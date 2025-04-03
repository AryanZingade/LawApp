import os
from flask import Flask, request, jsonify, render_template
from langgraph.graph import Graph
from langchain_openai import AzureChatOpenAI
from casesearch import search_cases 
from verdict import process_case
from formatter import classify_document_type, fetch_template_from_blob, extract_placeholders, extract_json_from_response, fill_document_with_gpt, generate_extraction_prompt
from summarisation import extract_summary  # Import summarization logic
from translate import upload_pdf_to_blob, process_uploaded_document  # Import translation functions
from flask_cors import CORS 

OPENAI_API_KEY = os.getenv("OPENAI_GPT_API_KEY")
AZURE_ENDPOINT = os.getenv("OPENAI_GPT_ENDPOINT")

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    azure_endpoint=AZURE_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version="2024-10-21",
    temperature=0.2
)

app = Flask(__name__)
CORS(app)

def classify_query(data):
    user_input = data.get("user_input", "").strip() if isinstance(data, dict) else str(data).strip()

    if not user_input:
        return "unknown", data  # Ensure it always returns a tuple (classification, data)

    prompt = f"""
    Classify the following user query:
    - "case_search" if searching for similar legal cases.
    - "verdict_prediction" if seeking a verdict prediction.
    - "document_generation" if query is regarding any kind of drafting or creation of a document.

    Query: "{user_input}"
    Output (case_search or verdict_prediction or document_generation):
    """

    response = llm.invoke(prompt)
    classification = response.content.strip().lower()

    return (classification if classification in ["case_search", "verdict_prediction", "document_generation"] else "unknown", data)


def case_search_agent(data):
    query = data.get("user_input", "") if isinstance(data, dict) else str(data)
    if not query:
        return {"error": "No query provided."}
    result = search_cases(query)
    return {"result": result}


def verdict_agent(data):
    case_input = data.get("user_input", "") if isinstance(data, dict) else str(data)
    if not case_input:
        return {"error": "No case input provided."}
    return process_case(case_input)


def document_generation(inputs):
    if isinstance(inputs, tuple):  # Unpack if it's a tuple
        _, data = inputs  
    else:
        data = inputs

    if not isinstance(data, dict):
        return {"error": "Invalid input format."}

    user_query = data.get("user_input", "").strip()
    if not user_query:
        return {"error": "User input is missing or empty."}

    document_type = classify_document_type(user_query)
    if not document_type:
        return {"error": "Could not determine document type."}

    template_path = fetch_template_from_blob(document_type)
    if not template_path:
        print("Error: Template fetching failed, stopping execution.")
        return  # Stop execution if template fetching fails

    placeholders = extract_placeholders(template_path)
    if not placeholders:
        return {"error": "No placeholders found in the template."}

    extraction_prompt = generate_extraction_prompt(user_query, document_type, placeholders)
    response = llm.invoke([{ "role": "user", "content": extraction_prompt }])
    extracted_data = extract_json_from_response(response.content.strip())

    if not extracted_data:
        return {"error": "GPT response format is incorrect."}

    final_doc_path = fill_document_with_gpt(template_path, extracted_data)
    if not final_doc_path:
        return {"error": "Failed to generate document."}

    return {"document_path": final_doc_path}


def summarization_agent():
    result = extract_summary()
    return result

workflow = Graph()
workflow.add_node("classifier", classify_query)
workflow.add_node("case_search_agent", case_search_agent)
workflow.add_node("verdict_agent", verdict_agent)
workflow.add_node("document_generation", document_generation)

def route_decision(inputs):
    classification, data = inputs  # Extract classification and data
    if not isinstance(data, dict):
        return None  # Fail safely if data is not a dictionary

    data["classification"] = classification

    if classification == "case_search":
        return "case_search_agent"
    elif classification == "verdict_prediction":
        return "verdict_agent"
    elif classification == "document_generation":
        return "document_generation"
    else:
        return None

workflow.add_conditional_edges("classifier", route_decision)
workflow.set_finish_point("case_search_agent")
workflow.set_finish_point("verdict_agent")
workflow.set_finish_point("document_generation")
workflow.set_entry_point("classifier")
app_workflow = workflow.compile()

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/invoke", methods=["POST"])
def invoke_workflow():
    data = request.json
    if not data or "user_input" not in data:
        return jsonify({"error": "user_input is required"}), 400

    result = app_workflow.invoke(data)
    return jsonify(result)

@app.route('/summarize', methods=['POST'])
def summarize():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    file_path = f"/tmp/{file.filename}"
    file.save(file_path)

    result = extract_summary(file_path, file.filename)  # Call your function
    return jsonify(result)

@app.route('/translatedoc', methods=['POST'])
def translate_document():
    file = request.files.get("file")
    target_language = request.form.get("target_language")
    if not file or not target_language:
        return jsonify({"error": "File and target language are required."}), 400

    file_path = f"/tmp/{file.filename}"
    file.save(file_path)
    uploaded_filename = upload_pdf_to_blob(file_path, file.filename)
    os.remove(file_path)

    result = process_uploaded_document(target_language)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
