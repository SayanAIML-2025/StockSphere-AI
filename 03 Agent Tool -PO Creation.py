import pandas as pd
import datetime
import random
# import pyodbc
import re

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from src.utils.functions import build_prompt_with_context
from dotenv import load_dotenv
from src.utils.chunking import DocumentProcessor
from src.utils.embed import generate_embeddings, add_documents,delete_collection

load_dotenv()

def re_embed_po(file_path):
    # Chunking - DocumentProcessor class object creation
    processor = DocumentProcessor(chunk_size=50, chunk_overlap=5)

    file_paths_supplier = {'file2':file_path}
    ids = ["purchase_order"]
    json_file_path = processor.process(file_paths_supplier)

    # Embedding
    embeddings, documents = generate_embeddings()

    # Delete the existing/older embeddings po
    delete_collection("supplier_collection","purchase_order")

    # Add documents to chroma db collection
    add_documents(embeddings= embeddings, string_data=documents, ids=ids, collection_name = "supplier_collection")

    print("New Embeddings created for PO file!")


def find_matching_names(item_names, user_query):
    user_query_lower = user_query.lower()
    found = []
    # Sort names descending by length, so "corn syrup" is checked before "corn"
    for name in sorted(item_names, key=lambda x: -len(x)):
        pattern = r'\b' + re.escape(name.lower()) + r'\b'
        if re.search(pattern, user_query_lower):
            found.append(name)
            # Remove the matched name from user_query_lower to prevent substrings from matching
            user_query_lower = re.sub(pattern, ' ', user_query_lower)
    print("Founded names inside func:", found)
    return found


class CompareInventoryInput(BaseModel):
    """Input schema for CompareInventory."""
    forecast_path: str = Field(..., description="Path to the demand forecast CSV file.")
    inventory_path: str = Field(..., description="Path to the current inventory CSV file.")
    user_query: str = Field(..., description="User query to process.")
    convo_summary: str = Field(..., description="Conversations history summary for context.")


class CompareInventoryTool(BaseTool):
    name: str = "Compare Inventory"
    description: str = (
        "Compares demand forecast with current inventory and identifies raw materials that need restocking."
    )
    args_schema: Type[BaseModel] = CompareInventoryInput

    def _run(self, forecast_path: str, inventory_path: str, user_query: str,convo_summary: str) -> str:
        try:
            
            print(f"Reading forecast from: {forecast_path}")
            print(f"Reading inventory from: {inventory_path}")
            
            forecast_df = pd.read_csv(forecast_path)
            inventory_df = pd.read_csv(inventory_path)

            item_ids = inventory_df['RawMaterial_ID'].unique().tolist()
            item_names = inventory_df['RawMaterial_Name'].unique().tolist()

            
            # Merge dataframes on RawMaterial_ID
            merged_df = pd.merge(
                forecast_df, 
                inventory_df, 
                on='RawMaterial_ID', 
                suffixes=('_forecast', '')
            )
            
            # Identify raw materials that need restocking
            merged_df['required_quantity'] = merged_df['RawMaterial_QuantityRequired'] - merged_df['RawMaterial_CurrentQuantity']
            
            shortage_df = merged_df[merged_df['required_quantity'] > 0]

            print("Materials with shortage inventory")
            print(shortage_df)

            #code to get entities from user query imp for PO creation
            updated_user_query = build_prompt_with_context(convo_summary, user_query)

            # Check and return the matching item
            find_ids = [x for x in item_ids if x.lower() in updated_user_query.lower()]

            find_names = find_matching_names(item_names, updated_user_query)

            print("Item Names list: ", item_names)
            print("Founded names:",find_names)

            # find_names = [x for x in item_names if x.lower() in updated_user_query.lower()]

            print(f"Raw materials identified for restocking: ID/s: {find_ids}, Name/s: {find_names}")

            # Filter shortage_df for all mentioned IDs or Names
            filtered_shortage_df = pd.DataFrame()

            if not find_ids and not find_names:
                filtered_shortage_df = shortage_df

            if find_ids:
                filtered_shortage_df = shortage_df[shortage_df['RawMaterial_ID'].isin(find_ids)]
                
            if find_names:
                filtered_shortage_df = pd.concat([
                    filtered_shortage_df,
                    shortage_df[shortage_df['RawMaterial_Name'].isin(find_names)]
                ]).drop_duplicates()
            
            print("Filtered data frame",filtered_shortage_df)

            if filtered_shortage_df.empty:
                result= "No raw materials need restocking. All current inventory levels are sufficient for forecast."
                return result, filtered_shortage_df
            else:
                result = "Raw materials that need restocking:\n\n"
                result += filtered_shortage_df[['RawMaterial_ID', 'RawMaterial_Name', 'RawMaterial_QuantityRequired', 
                                      'RawMaterial_CurrentQuantity', 'required_quantity']].to_string()
                return result, filtered_shortage_df
        except Exception as e:
            return f"Error comparing inventory: {str(e)}"



class CreatePurchaseOrderInput(BaseModel):
    """Input schema for CreatePurchaseOrder."""
    forecast_path: str = Field(..., description="Path to the demand forecast CSV file.")
    inventory_path: str = Field(..., description="Path to the current inventory CSV file.")
    user_query: str = Field(..., description="User query to process.")
    convo_summary: str = Field(..., description="Conversations history summary for context.")


#output_path: str = Field(..., description="Path to save the purchase order CSV file.")


class CreatePurchaseOrderTool(BaseTool):
    name: str = "Create Purchase Order"
    description: str = (
        "Returns a purchase order summary for raw materials where forecasted quantity exceeds current inventory."
    )
    args_schema: Type[BaseModel] = CreatePurchaseOrderInput

    def _run(self, forecast_path: str, inventory_path: str, user_query: str, convo_summary: str) -> str:      #output_path: str, 
        try:
            res,df = CompareInventoryTool._run(self,forecast_path,inventory_path,user_query,convo_summary)

            if "No raw materials need restocking." in res and df.empty:
                return "Restocking not required. No purchase order created. All current inventory levels are sufficient for forecast."

            elif "Raw materials that need restocking:" in res and df.empty == False:     

                # Create purchase order dataframe
                po_df = df[['RawMaterial_ID', 'RawMaterial_Name', 'required_quantity']].copy()
                po_df = po_df.rename(columns={'required_quantity': 'RawMaterial_Quantity'})
                
                # Generate a single Purchase_Order_ID for the entire order
                # Format: PO-YYYYMMDD-XXXX where XXXX is a random 4-digit number
                
                today = datetime.datetime.utcnow()
                po_id = f"PO-{today.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                
                # Add the same Purchase_Order_ID to all rows
                po_df['Purchase_Order_ID'] = po_id
                po_df['Supplier_ID'] = 'Not Applicable'
                po_df['Fulfilment_Status'] = 'open'
                po_df['Create_Timestamp'] = today.strftime("%Y-%m-%d %H:%M:%S") #.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "0000"  # Format to match SQL datetime
                po_df['Update_Timestamp'] = today.strftime("%Y-%m-%d %H:%M:%S") #.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "0000"

                print("Updated timezone:",po_df)

                # Write code here for po update insert in purchase_order.csv
                
                # Append DataFrame to existing CSV (without writing header)
                po_df.to_csv("purchase_order.csv", mode='a', header=False, index=False)

                # print(f"Purchase order {po_id} created at {output_path} with {len(po_df)} raw materials.")
                
                summary = f"Purchase order {po_id} created with {len(po_df)} raw materials.\n\n"
                summary += "Summary of purchase order:\n"
                summary += po_df.to_string()

                print("Purchase order created")

                # Re-embedding po file to supplier_collection
                re_embed_po("purchase_order.csv")
                
                return summary
        except Exception as e:
            return f"Error creating purchase order: {str(e)}"



