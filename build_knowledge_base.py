import os
import glob
import json
import fitz  # PyMuPDF
import requests
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from markdown import markdown
import faiss  # Make sure you have faiss-gpu or faiss-cpu installed
import time  # 增加了 time 模块的导入

# --- 1. 配置区域 ---
SILICONFLOW_API_KEY = "sk-cjnnfcatihrikdywnbebqofrrhfyzmzoturkcyyagrnlrjud"
API_URL = "https://api.siliconflow.cn/v1/embeddings"
BGE_MODEL_NAME = "BAAI/bge-m3"

CORPUS_DIRECTORY = "/home/sonata/FinancialStrategy2Code/corpus"
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".html"]

CHUNK_SIZE = 512  # 每个文本块的大小（字符数）
CHUNK_OVERLAP = 50 # 块之间的重叠大小（字符数）

FAISS_INDEX_PATH = "knowledge_base1.index"
CHUNKS_JSON_PATH = "chunks1.json"


# --- 2. 文本提取模块 (已更新) ---

def read_file_with_fallbacks(file_path):
    """
    尝试用多种编码读取文件，以增加稳健性。
    首先尝试 UTF-8，然后是 GBK。如果都失败，则使用带错误忽略的 UTF-8。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except UnicodeDecodeError:
            print(f"Warning: Could not decode {file_path} with utf-8 or gbk. Falling back to utf-8 with error handling.")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

def extract_text_from_pdf(file_path):
    """从 PDF 文件中提取文本。"""
    try:
        doc = fitz.open(file_path)
        text = "".join([page.get_text() for page in doc])
        return text
    except Exception as e:
        print(f"Error processing PDF file {file_path}: {e}")
        return ""

def extract_text_from_html(file_path):
    """从 HTML 文件中提取文本。"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            return soup.get_text()
    except Exception as e:
        print(f"Error processing HTML file {file_path}: {e}")
        return ""

def extract_text_from_markdown(file_path):
    """从 Markdown 文件中提取文本。"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = markdown(f.read())
            return ''.join(BeautifulSoup(html, "html.parser").findAll(text=True))
    except Exception as e:
        print(f"Error processing Markdown file {file_path}: {e}")
        return ""
        
# --- 3. 核心处理流程 ---
def get_embedding(text_or_texts, api_key, model_name):
    """
    获取单个文本或文本列表的嵌入。
    为了提高效率，此函数设计为可以处理批量请求。
    """
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json",
    }
    data = {
        "model": model_name,
        "input": text_or_texts,
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status() # This will raise an exception for HTTP error codes
        embeddings = [item['embedding'] for item in response.json()['data']]
        return embeddings
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 429:
            print("Rate limit exceeded. Consider adding a delay between requests.")
            raise
        return None


if __name__ == "__main__":
    print("--- Step 1: Reading and Parsing Files ---")
    all_chunks = []
    file_sources = []
    
    for extension in SUPPORTED_EXTENSIONS:
        for file_path in glob.glob(os.path.join(CORPUS_DIRECTORY, f"**/*{extension}"), recursive=True):
            print(f"Processing file: {file_path}")
            content = ""
            if extension == '.pdf':
                content = extract_text_from_pdf(file_path)
            elif extension == '.txt':
                content = read_file_with_fallbacks(file_path)
            elif extension == '.md':
                content = extract_text_from_markdown(file_path)
            elif extension == '.html':
                content = extract_text_from_html(file_path)

            if content:
                for i in range(0, len(content), CHUNK_SIZE - CHUNK_OVERLAP):
                    chunk = content[i:i + CHUNK_SIZE]
                    all_chunks.append(chunk)
                    file_sources.append(os.path.basename(file_path))

    print(f"Total chunks created: {len(all_chunks)}")

    # --- Step 2: Getting Embeddings from API (已修复) ---
    print("\n--- Step 2: Getting Embeddings from API ---")
    
    all_embeddings = []
    # 以批次方式处理，更高效且能避免超出 API 限制
    batch_size = 32  # 你可以根据需要调整这个批次大小
    for i in tqdm(range(0, len(all_chunks), batch_size), desc="Getting Embeddings"):
        batch_chunks = all_chunks[i:i + batch_size]
        
        # 获取当前批次的嵌入
        batch_embeddings = get_embedding(batch_chunks, SILICONFLOW_API_KEY, BGE_MODEL_NAME)

        if batch_embeddings:
            all_embeddings.extend(batch_embeddings)

        # 增加 1 秒的延迟以避免达到速率限制
        time.sleep(1)

    if not all_embeddings:
        print("Could not retrieve any embeddings. Exiting.")
        exit()

    print(f"Successfully retrieved {len(all_embeddings)} embeddings.")

    # --- Step 3: Building FAISS Index ---
    print("\n--- Step 3: Building FAISS Index ---")
    
    embeddings_matrix = np.array(all_embeddings).astype('float32')
    embedding_dim = embeddings_matrix.shape[1]
    
    if hasattr(faiss, 'StandardGpuResources'):
        print("FAISS-GPU available, building index on GPU.")
        res = faiss.StandardGpuResources()
        cpu_index = faiss.IndexFlatL2(embedding_dim)
        index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
    else:
        print("FAISS-GPU not available, building index on CPU.")
        index = faiss.IndexFlatL2(embedding_dim)
        
    index.add(embeddings_matrix)
    print(f"Index built successfully. Total vectors in index: {index.ntotal}")

    # --- Step 4: Saving Index and Chunks ---
    print("\n--- Step 4: Saving Index and Chunks ---")
    
    if hasattr(faiss, 'index_gpu_to_cpu'):
        cpu_index_to_save = faiss.index_gpu_to_cpu(index)
        faiss.write_index(cpu_index_to_save, FAISS_INDEX_PATH)
    else:
        faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"FAISS index saved to '{FAISS_INDEX_PATH}'")

    chunk_data_with_source = [{"text": text, "source": source} for text, source in zip(all_chunks, file_sources)]
    with open(CHUNKS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunk_data_with_source, f, ensure_ascii=False, indent=4)
    print(f"Chunk data and sources saved to '{CHUNKS_JSON_PATH}'")