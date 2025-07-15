from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from src.utils.similarity_search import similarity_search

from src.utils.functions import build_prompt_with_context
from dotenv import load_dotenv

load_dotenv()



class QueryInventoryInput(BaseModel):
    """Input schema for KnowledgeGraph."""
    user_query: str = Field(..., description="User query to process.")
    convo_summary: str = Field(..., description="Conversations history summary for context.")


class QueryInventoryTool(BaseTool):
    name: str = "Query Inventory"
    description: str = (
        "Answers queries related to all inventory details and provides insights on inventory and forecast data"
    )
    args_schema: Type[BaseModel] = QueryInventoryInput

    def _run(self, user_query: str,convo_summary: str) -> str:
        try:
            print("Into the Query tool")

            # Build user query in reference with conversation history
            updated_query = build_prompt_with_context(convo_summary,user_query)
            print('updated prompt:',updated_query)
            # Write logic here- start RAG processing

            # Getting Similar Searches and response for query
            result = similarity_search(updated_query,"inventory_collection")

            print("Response from Inventory RAG:",result)
            return result

        except Exception as e:
            return f"Error in retrieving response: {str(e)}"


