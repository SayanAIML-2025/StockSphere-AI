from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from datetime import datetime
from src.utils.similarity_search import similarity_search

from src.utils.functions import build_prompt_with_context
from dotenv import load_dotenv

load_dotenv()


class SupplierRecommendationInput(BaseModel):
    """Input schema for KnowledgeGraph."""
    user_query: str = Field(..., description="User query to process.")
    convo_summary: str = Field(..., description="Conversations history summary for context.")


class SupplierRecommendationTool(BaseTool):
    name: str = "Supplier recommendation"
    description: str = (
        "Process queries to get supplier recommendations processed out of the supplier data and provide insights on the response."
    )
    args_schema: Type[BaseModel] = SupplierRecommendationInput

    def _run(self, user_query: str,convo_summary: str) -> str:
        try:
            print("Into the Supplier Recommendation Tool")

            # Build user query in reference with conversation history
            updated_query = build_prompt_with_context(convo_summary,user_query)
            
            # Write logic here

            # Getting Similar Searches and response for query
            result = similarity_search(updated_query,"supplier_collection")

            print("Response from Supplier Knowledge Graph:",result)
            return result

        except Exception as e:
            return f"Error in retrieving Dynamic KG API query response: {str(e)}"


