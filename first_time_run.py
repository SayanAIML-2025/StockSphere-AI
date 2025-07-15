from src.utils.chunking import DocumentProcessor
from src.utils.embed import generate_embeddings, add_documents
from src.utils.similarity_search import similarity_search

# Chunking - DocumentProcessor class object creation
processor = DocumentProcessor(chunk_size=50, chunk_overlap=5)

def supplier_documents():
    # One time embedding creation code for supplier and purcahse order files- vectors stored in supplier_collection for future queries
    # Note: For next iterations/ updation only purchase_order and supplier_quotation files will be re-embedded and stored in supplier_collection - Trigger, when new po gets created and when quotation gets uploaded.
#**************************************************#
    # Chunking
    file_paths_supplier = {'file1':'supplier_historical.csv','file2':'purchase_order.csv','file3':'supplier_quotation.csv'}
    ids = [id.split(".csv")[0] for id in file_paths_supplier.values()]
    # json_file_path = processor.process(file_paths_supplier)

    # Embedding
    embeddings, documents = generate_embeddings()

    # Add documents to chroma db collection
    add_documents(embeddings= embeddings, string_data=documents, ids=ids, collection_name = "supplier_collection")
#**************************************************#


def inventory_documents():
    # One time embedding creation code for inventory and forecast files- vectors stored in inventory_collection for future queries
#**************************************************#
    # Chunking
    file_paths_inventory = {'file1':'demand_forecast.csv','file2':'inventory.csv'}
    ids = [id.split(".csv")[0] for id in file_paths_inventory.values()]
    # json_file_path = processor.process(file_paths_inventory)

    # Embedding
    embeddings, documents = generate_embeddings()

    # Add documents to chroma db collection
    add_documents(embeddings= embeddings, string_data=documents, ids=ids, collection_name = "inventory_collection")
#**************************************************#


# To check on successful storing of vectors in chromadb use below funtion

def get_resp(user_query, collection_name):
    # Getting Similar Searches and response for query
    if collection_name == "supplier_collection":
        result = similarity_search(user_query,"supplier_collection")
    elif collection_name == "inventory_collection":
        result = similarity_search(user_query,"inventory_collection")
    print("Response from RAG:",result)
    return result


if __name__ == "__main__":
    # call functions here
    # supplier_documents()
    # inventory_documents()
    # print(get_resp('do we have enough salt?','inventory_collection'))
    pass