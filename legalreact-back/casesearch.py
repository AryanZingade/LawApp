import os
import openai
import pinecone

# Azure OpenAI API Credentials
AZURE_OPENAI_ENDPOINT = os.getenv("EMBEDDING_API_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("EMBEDDING_API_KEY")
AZURE_OPENAI_MODEL = "text-embedding-ada-002"
AZURE_OPENAI_VERSION = os.getenv("EMBEDDING_API_VERSION")

# Pinecone API Credentials
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize OpenAI
openai_client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Initialize Pinecone
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is not set.")

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index2 = pc.Index(PINECONE_INDEX_NAME)

def search_cases(query):
    """
    Searches Pinecone for similar case documents based on a query.
    Groups chunks together under their original document name.
    """
    # Generate embedding from OpenAI
    response = openai_client.embeddings.create(
        model=AZURE_OPENAI_MODEL,
        input=query
    )

    print("Embedding Response:", response)  # 🔍 Debugging

    # Extract the embedding
    if hasattr(response, "data") and len(response.data) > 0:
        query_embedding = response.data[0].embedding
    else:
        print("❌ No embeddings found in OpenAI response!")
        return []
    
    search_results = index2.query(vector=query_embedding, top_k=5, include_metadata=True)

    if not search_results or "matches" not in search_results:
        print("⚠️ No search results returned from Pinecone!")
        return []

    print("Raw search results:", search_results)  # 🔍 Debugging

    # Dictionary to group chunks under a single document name
    grouped_results = {}

    matches = search_results.get("matches", [])

    if not matches:
        print("⚠️ No matches found in Pinecone search!")
        return []

    for match in matches:
        doc_chunk_name = match.get("id", "Unknown ID")  # e.g., partnershipA.pdf_chunk_0
        metadata = match.get("metadata", {})

        # Extract document name by removing "_chunk_X" suffix
        doc_name = doc_chunk_name.rsplit("_chunk_", 1)[0]
        chunk_summary = metadata.get("chunk", "No summary available")

        if doc_name not in grouped_results:
            grouped_results[doc_name] = []  # Initialize list for storing chunks
        
        grouped_results[doc_name].append(chunk_summary)

    # Convert grouped results into a formatted list
    final_results = [
        {"case_name": doc, "summary": " ".join(chunks)}
        for doc, chunks in grouped_results.items()
    ]

    print("Final Grouped Search Results:", final_results)  # 🔍 Debugging
    return final_results
