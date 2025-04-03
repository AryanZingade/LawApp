import os
import json
from datetime import datetime, timedelta
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import AzureChatOpenAI

# Azure Configuration
AZURE_BLOB_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_BLOB_CONTAINER = os.getenv("AZURE_CONTAINER_NAME")
AZURE_BLOB_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
AZURE_FORM_RECOGNIZER_KEY = os.getenv("AZURE_DOC_INTELLIGENCE_KEY")

# Initialize Azure OpenAI GPT Model
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    azure_endpoint=os.getenv("OPENAI_GPT_ENDPOINT"),
    api_key=os.getenv("OPENAI_GPT_API_KEY"),
    api_version="2024-10-21",
    temperature=0.2
)

def upload_pdf_to_blob(file_path, file_name):
    """
    Uploads a PDF file to Azure Blob Storage.
    """
    blob_service_client = BlobServiceClient(
        account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
        credential=AZURE_BLOB_KEY
    )
    blob_client = blob_service_client.get_blob_client(container=AZURE_BLOB_CONTAINER, blob=file_name)

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type="application/pdf"))

    return f"File {file_name} uploaded successfully."

def get_latest_contract():
    """
    Fetches the latest uploaded contract file from Azure Blob Storage.
    """
    blob_service_client = BlobServiceClient(
        account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
        credential=AZURE_BLOB_KEY
    )
    container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)
    
    blobs = list(container_client.list_blobs())
    if not blobs:
        return None, "No contract files found in Azure Blob Storage."
    
    latest_blob = max(blobs, key=lambda x: x.last_modified)
    return latest_blob.name, None  # Return latest filename

def generate_sas_url(blob_name):
    """
    Generates a temporary SAS URL for a blob.
    """
    sas_token = generate_blob_sas(
        account_name=AZURE_BLOB_ACCOUNT,
        container_name=AZURE_BLOB_CONTAINER,
        blob_name=blob_name,
        account_key=AZURE_BLOB_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    return f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/{AZURE_BLOB_CONTAINER}/{blob_name}?{sas_token}"

def extract_summary(file_path, file_name):
    """
    Uploads a PDF, fetches the latest contract, extracts legal entities, and generates a summary.
    """
    # Step 1: Upload PDF first
    upload_pdf_to_blob(file_path, file_name)

    # Step 2: Fetch the latest uploaded contract
    latest_file, error = get_latest_contract()
    if error:
        return {"error": error}
    
    # Step 3: Generate SAS URL for latest file
    blob_url = generate_sas_url(latest_file)

    # Step 4: Initialize Document Intelligence client
    client = DocumentAnalysisClient(AZURE_FORM_RECOGNIZER_ENDPOINT, AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY))
    
    # Analyze document layout (text extraction)
    poller = client.begin_analyze_document_from_url("prebuilt-layout", blob_url)
    result = poller.result()
    extracted_text = "\n".join([line.content for page in result.pages for line in page.lines])

    # Step 5: Generate legal summary using GPT
    prompt = f"""
    Extract key legal details from the following contract text:
    
    **Contract Text:**
    {extracted_text}
    
    Return the result as a JSON object with keys: "parties", "dates", "financial_terms", "confidentiality", "termination", "governing_law".
    """
    messages = [
        SystemMessage(content="You are a legal document assistant."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    raw_response = response.content.strip()

    # Cleanup GPT response
    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]
    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]

    try:
        parsed_response = json.loads(raw_response)
        return parsed_response
    except json.JSONDecodeError:
        return {"error": "Failed to parse response from GPT."}

