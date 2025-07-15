""" This module chunks all the required files and save them to chunks.json 
    Provide file paths dictionary with all the required files that need to be embed together."""

import os
import json
import pandas as pd

class DocumentProcessor:
    def __init__(self, chunk_size=50, chunk_overlap=5):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_document(self, file_path: str) -> pd.DataFrame:
        extension = os.path.splitext(file_path)[1].lower()
        if extension == ".csv":
            return pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def chunk_dataframe(self, df: pd.DataFrame, chunks: list) -> list:
        """
        Chunk the DataFrame by rows, with optional overlap.
        Returns a list of DataFrame chunks.
        """
        # chunks = []
        n_rows = len(df)
        start = 0
        while start < n_rows:
            end = min(start + self.chunk_size, n_rows)
            chunk = df.iloc[start:end].to_dict(orient="records")
            # print(chunk)
            chunks.append(chunk)
            # Move start forward, with overlap
            start += self.chunk_size - self.chunk_overlap
            if start < 0:  # Avoid infinite loop if overlap >= chunk_size
                break
        return chunks

    def save_chunks_to_json(self, chunks: list) -> str:
        """
        Appends/ Saves all the chunks to the chunks.json file
        """
        # with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as json_file:
        with open("chunks.json", "w", encoding="utf-8") as json_file:
            json.dump(chunks, json_file, ensure_ascii=False, indent=2)
            return json_file.name

    def process(self, file_paths: dict):
        chunks = []
        for file_name, file_path in file_paths.items():
          if file_path and os.path.exists(file_path):
              df = self.load_document(file_path)
              combined_chunk= self.chunk_dataframe(df,chunks)
              chunks = combined_chunk
          else:
            raise FileNotFoundError("File path does not exist.")
        json_file_path = self.save_chunks_to_json(chunks)
        print(f"Chunks saved at: {json_file_path}")
        return json_file_path
        

# Usage
# if __name__ == "__main__":
#     processor = DocumentProcessor(chunk_size=50, chunk_overlap=5)
    
#     file_paths_inventory = {'file1':'demand_forecast.csv','file2':'inventory.csv'}
#     file_paths_supplier = {'file1':'supplier_historical.csv','file2':'purchase_order.csv','file3':'supplier_quotation.csv'}
#     ids = [id.split(".csv")[0] for id in file_paths_inventory.values()]
#     json_file_path = processor.process(file_paths_inventory)
#     # os.remove(json_file_path)