import os
import pandas as pd
import random
from dotenv import load_dotenv
import google.generativeai as genai
from src.utils.chunking import DocumentProcessor
from src.utils.embed import generate_embeddings, add_documents,delete_collection

load_dotenv()

# def llm_completions(message: list) -> str:
#     return completion(
#         model=os.getenv("MODEL_AZ"),
#         messages=message,
#         api_base=os.getenv("AZURE_API_BASE"),
#         api_key=os.getenv("AZURE_API_KEY"),
#         api_version=os.getenv("AZURE_API_VERSION"),
#     ).choices[0].message.content.strip()

def quotation_re_embed(file_path):  # supplier quotation file path
    """
    Attach this function in streamlit- Trigger when quotations gets uploaded
    """
    # Chunking - DocumentProcessor class object creation
    processor = DocumentProcessor(chunk_size=50, chunk_overlap=5)

    file_paths_supplier = {'file3':file_path}
    ids = ["supplier_quotation"]
    json_file_path = processor.process(file_paths_supplier)

    # Embedding
    embeddings, documents = generate_embeddings()

    # Delete the existing/older embeddings po
    delete_collection("supplier_collection","supplier_quotation")

    # Add documents to chroma db collection
    add_documents(embeddings= embeddings, string_data=documents, ids=ids, collection_name = "supplier_collection")

    print("New Embeddings created for quotation file!")

def llm_completions(message: list) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name= os.getenv("MODEL")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    # print('message length',len(message))
    if len(message)==2:
        # print('enter if')
        prompt = f"SYSTEM PROMPT: {message[-2]['content']}\nUSER PROMPT: {message[-1]['content']}"
        response = model.generate_content(prompt)
        response = response.text
    elif len(message)==1:
        # print('enter elif')
        response = model.generate_content(message[-1]['content'])
        response = response.text

    return response

def build_prompt_with_context(convo_summary: str, user_query: str) -> str:    
    """
    Uses an LLM to extract relevant entities from convo_summary needed to process user_query.
    Returns a new query string with added context from history.
    """
    system_prompt = """
        You are an expert assistant. Given a summary of a conversation and a user's new query, analyze the user query if it contains needed context and attributes to execute the query if not then 
        extract all important entities from the summary that are required to precisely answer the new query. 
        Then, rewrite the user query by adding this necessary context (but do not add unrelated information). 
        The output should be a single, clear prompt for an LLM to answer.
        If the query already contains required context and is quite self-explanatory then do not alter the query.
    """

    #(such as product names, raw material IDs, or numbers) 

    user_prompt = f"Conversation history summary:\n{convo_summary}\n User query: {user_query}\n Extract the entities that are needed to perform action given by the query from the summary and rewrite the query with that context."
    

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


    return llm_completions(message)


def format_api_response(api_response) -> str:
    """
    Formats a raw API response into a user-friendly answer using LLM.
    Args:
        api_response (dict or str): The raw API response to format.
    Returns:
        str: The formatted, natural language response.
    """
    # Construct the prompt for the LLM
    message = [
        {
            "role": "system",
            "content": (
                "You are an assistant that summarizes API responses for the user. "
                "Given the following API response, write a clear and concise natural language explanation."
            )
        },
        {
            "role": "user",
            "content": f"API response: {api_response}"
        }
    ]
    return llm_completions(message)



def is_greeting(message):
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
    msg = message.strip().lower()
    return any(msg == g or msg.startswith(g + ' ') for g in greetings)


def greeting_response():
    responses = [
    "Hello! This is Stocksphere AI, your Supplier and Inventory Management Agentic System. How can I assist you today?",
    "Greetings from Stocksphere AI. How may I help you with your supplier or inventory management needs?",
    "Hi, you've reached Stocksphere AI. What can I do for you regarding suppliers or inventory?",
    "Welcome to Stocksphere AI, your partner in Supplier and Inventory Management. How can I be of service?",
    "Hello! Stocksphere AI is here to support your supplier and inventory management tasks. How can I help?"
]
    return random.choice(responses)



