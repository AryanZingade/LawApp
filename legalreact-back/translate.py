import os
import json
import tempfile
import requests
import logging
from datetime import datetime, timedelta
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.translation.text import TextTranslationClient
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from azure.core.credentials import AzureKeyCredential

AZURE_BLOB_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_BLOB_CONTAINER = os.getenv("AZURE_CONTAINER_NAME")
AZURE_BLOB_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
AZURE_FORM_RECOGNIZER_KEY = os.getenv("AZURE_DOC_INTELLIGENCE_KEY")
AZURE_TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION")
AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")

logging.basicConfig(level=logging.INFO)

blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
    credential=AZURE_BLOB_KEY
)

document_analysis_client = DocumentAnalysisClient(
    endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
)

translator_client = TextTranslationClient(
    endpoint="https://api.cognitive.microsofttranslator.com",
    credential=AzureKeyCredential(AZURE_TRANSLATOR_KEY)
)

def load_glossary(file_path="glossary.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Failed to load glossary: {str(e)}")
        return {}

GLOSSARY = load_glossary()

def upload_pdf_to_blob(file_path, original_filename):
    timestamped_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{original_filename}"
    blob_client = blob_service_client.get_blob_client(container=AZURE_BLOB_CONTAINER, blob=timestamped_filename)

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type="application/pdf"))

    return timestamped_filename

def get_latest_contract():
    container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)
    blobs = list(container_client.list_blobs())
    if not blobs:
        return None, "No contract files found in Azure Blob Storage."
    latest_blob = max(blobs, key=lambda x: x.last_modified)
    return latest_blob.name, None

def generate_sas_url(blob_name):
    sas_token = generate_blob_sas(
        account_name=AZURE_BLOB_ACCOUNT,
        container_name=AZURE_BLOB_CONTAINER,
        blob_name=blob_name,
        account_key=AZURE_BLOB_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    return f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/{AZURE_BLOB_CONTAINER}/{blob_name}?{sas_token}"

def extract_text_from_document(blob_name):
    document_url = generate_sas_url(blob_name)
    try:
        poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-read", document_url)
        result = poller.result()
        return "\n".join([line.content for page in result.pages for line in page.lines]) or None
    except Exception as e:
        logging.error(f"Document text extraction failed: {str(e)}")
        return None

def detect_language(text):
    url = "https://api.cognitive.microsofttranslator.com/detect?api-version=3.0"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
        "Content-Type": "application/json"
    }
    body = [{"text": text}]
    try:
        response = requests.post(url, headers=headers, json=body)
        return response.json()[0].get("language") if response.status_code == 200 else None
    except Exception as e:
        logging.error(f"Language detection failed: {str(e)}")
        return None

def apply_glossary_replacements(translated_text):
    for eng_term, hindi_term in GLOSSARY.items():
        translated_text = translated_text.replace(eng_term, hindi_term)
    return translated_text

def translate_text(text, target_language):
    url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
        "Content-Type": "application/json"
    }
    body = [{"text": text}]
    
    try:
        response = requests.post(url, headers=headers, json=body, params={"to": target_language})
        if response.status_code == 200:
            translated_text = response.json()[0]["translations"][0]["text"]
            return apply_glossary_replacements(translated_text)
        else:
            return None
    except Exception as e:
        logging.error(f"Translation failed: {str(e)}")
        return None

def process_uploaded_document(target_language):
    latest_contract, error = get_latest_contract()
    if error:
        return {"error": error}
    extracted_text = extract_text_from_document(latest_contract)
    if not extracted_text:
        return {"error": "Failed to extract text from document."}
    detected_lang = detect_language(extracted_text)
    if not detected_lang:
        return {"error": "Failed to detect source language."}
    if detected_lang == target_language:
        return {"message": "Document is already in the target language.", "translated_text": extracted_text}
    translated_text = translate_text(extracted_text, target_language)
    return {"source_language": detected_lang, "translated_text": translated_text} if translated_text else {"error": "Translation failed."}