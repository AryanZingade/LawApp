import os
import json
import openai
import pinecone
from langchain_openai import AzureChatOpenAI

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_GPT_API_KEY")
AZURE_ENDPOINT = os.getenv("OPENAI_GPT_ENDPOINT")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize OpenAI & Pinecone
openai_client = openai.AzureOpenAI(
    api_key=os.getenv("EMBEDDING_API_KEY"),
    api_version=os.getenv("EMBEDDING_API_VERSION"),
    azure_endpoint=os.getenv("EMBEDDING_API_ENDPOINT")
)

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    azure_endpoint=AZURE_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version="2024-10-21",
    temperature=0.2
)

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
knowledge_index = pc.Index("law-kb")
cases_index = pc.Index("past-cases")

import json
import re

def extract_case_details(case_input):
    """Extracts structured case details from input text using GPT."""
    print(f"📜 Extracting case details for: {case_input}")

    prompt = f"""
    Extract key details from the following legal case text:
    - Case Description
    - Involved Parties
    - Jurisdiction
    - Alleged Violations

    Respond in this JSON format:
    {{
        "case_description": "...",
        "involved_parties": "...",
        "jurisdiction": "...",
        "alleged_violations": "..."
    }}

    Case: "{case_input}"
    """
    
    response = llm.invoke(prompt)
    raw_text = response.content.strip()

    print(f"🧐 GPT Raw Response: {raw_text}")  # Debug print

    # Remove triple backticks if present
    raw_text = re.sub(r"^```json\n|\n```$", "", raw_text).strip()

    # Try parsing response as JSON
    try:
        structured_data = json.loads(raw_text)
        print(f"✅ Parsed Case Details: {structured_data}")  # Debug print
        return structured_data
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        return {"error": "Invalid JSON format returned by GPT"}

def generate_embeddings(text):
    """Generates an embedding for the given text."""
    response = openai_client.embeddings.create(model="text-embedding-ada-002", input=text)
    return response.data[0].embedding

def search_pinecone(index, query_embedding, top_k=5):
    """Searches Pinecone for similar cases or laws."""
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return results.matches if results.matches else []

def get_verdict(case_description, relevant_laws, similar_cases):
    """Predicts a verdict based on case details, laws, and past cases."""
    prompt = f"""
    A legal case was submitted with the following details:
    Case Description: {case_description}
    Relevant Laws:
    {relevant_laws}
    Similar Past Cases:
    {similar_cases}
    
    Based on the above, predict the most likely verdict and explain why.
    """
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating verdict: {e}"

def process_case(case_input):
    """Processes a legal case and returns structured insights."""
    print(f"🔍 Received case input: {case_input}")  

    # Step 1: Extract case details
    case_details = extract_case_details(case_input)
    if not case_details or "error" in case_details:
        print("❌ Error extracting case details:", case_details)
        return {"error": "Failed to extract case details"}

    case_description = case_details.get("case_description", "No description available")
    print(f"📜 Case Description: {case_description}")

    # Step 2: Generate embeddings
    case_embedding = generate_embeddings(case_input)
    if case_embedding is None:
        print("❌ Error: Failed to generate embeddings.")
        return {"error": "Failed to generate embeddings"}

    # Step 3: Search for relevant laws and similar cases
    relevant_laws = search_pinecone(knowledge_index, case_embedding)
    similar_cases = search_pinecone(cases_index, case_embedding)

    print(f"📚 Found {len(relevant_laws)} relevant laws.")
    print(f"⚖️ Found {len(similar_cases)} similar cases.")

    if not relevant_laws:
        return {"error": "No relevant laws found"}

    if not similar_cases:
        return {"error": "No similar cases found"}

    # Step 4: Format results
    laws_text = "\n".join([f"Title: {law['metadata'].get('title', 'No Title')}" for law in relevant_laws])
    cases_text = "\n".join([f"Title: {case['metadata'].get('title', 'No Title')}\nSummary: {case['metadata'].get('summary_chunk', 'No Summary')}" for case in similar_cases])

    # Step 5: Get verdict
    verdict = get_verdict(case_description, laws_text, cases_text)
    if verdict is None:
        print("❌ Error: Verdict generation failed.")
        return {"error": "Verdict generation failed"}

    # Step 6: Return final response
    result = {
        "case_description": case_description,
        "involved_parties": case_details.get("involved_parties", "Unknown parties"),
        "jurisdiction": case_details.get("jurisdiction", "Unknown jurisdiction"),
        "alleged_violations": case_details.get("alleged_violations", "Unknown violations"),
        "verdict": verdict,
        "relevant_laws": laws_text,
        "similar_cases": cases_text
    }

    print("✅ Final Processed Case:", result)  
    return result

