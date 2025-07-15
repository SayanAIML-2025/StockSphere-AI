"""
This module embeds the chunks provided from chunks.json and store it to the vector db collection
inventory_collection - collection name for querying inventory and forecast data
supplier_collection - collection name for querying suppliers
"""

from dotenv import load_dotenv
import google.generativeai as genai
import json
import os
import chromadb
import numpy as np

load_dotenv()

# Convert the list of dictionaries into a list of strings
def chunk_to_text(chunk):
    return "\n".join(" ".join(str(v) for v in row.values()) for row in chunk)

# generate embeddings
def generate_embeddings():
    """
    Converts chunks (list of json objects) to string and embeds them.
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # load chunks
    with open('chunks.json', 'r') as f:
        data = json.load(f)

    # convert to string data
    string_data = [chunk_to_text(chunk) for chunk in data]

    # create embeddings using Gemini embedding model
    result = genai.embed_content(
            model="models/gemini-embedding-exp-03-07",
            content=string_data, # Use the list of strings here aka chunks
            task_type="retrieval_document"
    )   
    embeddings = result['embedding']
    embeddings = np.array(embeddings).astype(np.float32)
    print("Embeddings generated:",embeddings)
    return embeddings, string_data

def add_documents(embeddings: list, string_data: list, ids: list, collection_name: str):
    """
    Add documents, embeddings, and ids to chroma db collection
    """
    # 1. Set up ChromaDB persistent client (change path accordingly)
    client = chromadb.PersistentClient(path="chroma_db_dir")
    collection_name = collection_name

    # 2. Check if the collection exists
    existing_collections = [c.name for c in client.list_collections()]

    if collection_name in existing_collections:
        if collection_name == "inventory_collection":
            print("Inventory collection already exists ")
            return 
        else:
            collection = client.get_collection(collection_name)
            print(f"Collection '{collection_name}' exists. Using it.")
    else:
        collection = client.create_collection(collection_name)
        print(f"Collection '{collection_name}' does not exist. Creating it.")

    # Adding documents
    embeddings = embeddings
    ids = ids #["demand_forecast","inventory_data"]
    documents = string_data

    # Store embeddings into ChromaDB
    try:
        collection.add(
            embeddings=embeddings,
            ids=ids,
            documents=documents,
        ) #,,documents=documents,metadatas=metadatas  # optional
    except Exception as e:
        print("Exception:",e)

    print(f"Embeddings stored successfully to {collection_name}!")

    # print("Documents:", documents)
    # print("collection read:",collection.get())
    # result = collection.get(
    #     include=["embeddings", "documents"]
    # )
    return 


def delete_collection(collection_name: str, doc_id: str):

    # 1. Set up ChromaDB persistent client (change path accordingly)
    client = chromadb.PersistentClient(path="chroma_db_dir")
    collection_name = collection_name

    # 2. Check if the collection exists
    existing_collections = [c.name for c in client.list_collections()]

    if collection_name in existing_collections:
        collection = client.get_collection(collection_name)
        print(f"Collection '{collection_name}' exists. Using it.")
    else:
        print(f"Collection '{collection_name}' does not exist. Cannot process with deletion")
        return

    try:
        # Delete the existing entry
        collection.delete(ids=[doc_id])
    except Exception as e:
        print("Error while deleting embeddings", e)

    print("Deleted Embeddings for document id",doc_id)

    read_id = collection.get(ids=[doc_id],
    include=["embeddings", "documents"]
    )
    print("Documents after deletion for id",doc_id,":",read_id)

    return

    

