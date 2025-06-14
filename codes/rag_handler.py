import json
import faiss
import numpy as np
import requests

# --- Configuration (same as in build_knowledge_base.py) ---
# Make sure to use the same model and API details
SILICONFLOW_API_KEY = "sk-cjnnfcatihrikdywnbebqofrrhfyzmzoturkcyyagrnlrjud"
API_URL = "https://api.siliconflow.cn/v1/embeddings"
BGE_MODEL_NAME = "BAAI/bge-m3"

FAISS_INDEX_PATH = "../knowledge_base.index"
CHUNKS_JSON_PATH = "../chunks.json"

class RAGHandler:
    def __init__(self):
        print("Initializing RAGHandler...")
        try:
            # Load the FAISS index
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            
            # Move index to GPU if available
            if faiss.get_num_gpus() > 0:
                print("Moving FAISS index to GPU.")
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

            # Load the text chunks
            with open(CHUNKS_JSON_PATH, 'r', encoding='utf-8') as f:
                self.chunks_data = json.load(f)
            
            print(f"Successfully loaded FAISS index with {self.index.ntotal} vectors and {len(self.chunks_data)} chunks.")

        except Exception as e:
            print(f"Error initializing RAGHandler: {e}")
            print("Please ensure 'knowledge_base.index' and 'chunks.json' exist and are in the correct path.")
            self.index = None
            self.chunks_data = None

    def _get_embedding(self, text):
        """Gets a single embedding for a query text."""
        headers = {
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = { "model": BGE_MODEL_NAME, "input": [text] }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            embedding = response.json()['data'][0]['embedding']
            return np.array([embedding], dtype='float32')
        except requests.exceptions.RequestException as e:
            print(f"API request for query embedding failed: {e}")
            return None

    def retrieve(self, query, k=5):
        """
        Retrieves the top_k most relevant text chunks for a given query.
        """
        top_k = k
        if not self.index or not self.chunks_data:
            print("RAG Handler is not initialized. Cannot retrieve.")
            return []

        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return []

        # Search the FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Retrieve the corresponding chunks
        retrieved_chunks = []
        for i in indices[0]:
            if i != -1: # FAISS returns -1 for no result
                retrieved_chunks.append(self.chunks_data[i])
        
        return retrieved_chunks

# Optional: For testing the handler directly
if __name__ == '__main__':
    rag_handler = RAGHandler()
    if rag_handler.index:
        query = "How to implement a Simple Moving Average (SMA) crossover strategy in backtrader?"
        print(f"\nTesting RAG with query: '{query}'")
        results = rag_handler.retrieve(query, top_k=3)
        
        if results:
            for i, result in enumerate(results):
                print(f"\n--- Result {i+1} (from: {result['source']}) ---")
                # Print first 200 chars for brevity
                print(result['text'][:200] + "...")
        else:
            print("No results found.")