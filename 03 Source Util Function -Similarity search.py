import chromadb
import numpy as np
from google.generativeai import GenerativeModel
import google.generativeai as genai
from src.utils.constants import RAG_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()

def similarity_search(user_query,collection_name):
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)

    llm = GenerativeModel("models/gemini-2.0-flash")

    # ---- ChromaDB Client Setup ----
    client = chromadb.PersistentClient(path="chroma_db_dir")  # Change path as needed
    collection = client.get_collection(collection_name)

    result = genai.embed_content(
            model="models/gemini-embedding-exp-03-07",
            content=user_query,
            task_type="retrieval_document"
    )
    query_embedding = result['embedding']
    query_embedding = np.array(query_embedding).astype(np.float32)

    # ---- Perform Similarity Search in ChromaDB ----
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    # ---- View Retrieved Documents ----
    for i, doc in enumerate(results["documents"][0]):
        print(f"Result {i+1}: {doc}")

    # Compose context for LLM
    retrieved_texts = "\n".join(results["documents"][0])
    prompt = f"{RAG_PROMPT}\n\nContext: {retrieved_texts}\n\nUser query: {user_query}"

    response = llm.generate_content(prompt)
    print("Gemini 2.0 Flash Response:\n", response.text)
    return response