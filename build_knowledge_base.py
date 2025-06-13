import os
import glob
import json
import fitz  # PyMuPDF
import requests
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from markdown import markdown
import faiss  # Make sure you have faiss-gpu installed

# --- 1. 配置区域 (与之前相同) ---
SILICONFLOW_API_KEY = "sk-cjnnfcatihrikdywnbebqofrrhfyzmzoturkcyyagrnlrjud"
API_URL = "https://api.siliconflow.cn/v1/embeddings"
BGE_MODEL_NAME = "BAAI/bge-m3"

CORPUS_DIRECTORY = "corpus"
# 注意：这里的文件扩展名现在用于过滤，而不是用于构建搜索模式
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".html"]

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

FAISS_INDEX_PATH = "knowledge_base.index"
CHUNKS_JSON_PATH = "chunks.json"


# --- 2. 文本提取模块 (与之前相同) ---

def extract_text_from_pdf(file_path):
    """使用 PyMuPDF 从 PDF 文件中提取文本"""
    try:
        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        print(f"Error processing PDF {file_path}: {e}")
        return ""

def extract_text_from_txt(file_path):
    """从 TXT 文件中提取文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error processing TXT {file_path}: {e}")
        return ""

def extract_text_from_md(file_path):
    """从 Markdown 文件中提取纯文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = markdown(f.read())
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
    except Exception as e:
        print(f"Error processing MD {file_path}: {e}")
        return ""

def extract_text_from_html(file_path):
    """从 HTML 文件中提取纯文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            return soup.get_text()
    except Exception as e:
        print(f"Error processing HTML {file_path}: {e}")
        return ""

# --- 3. 文本处理模块 (与之前相同) ---

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """将长文本切分为带有重叠的块"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

# --- 4. 向量化模块 (与之前相同) ---

def get_embeddings(texts, model=BGE_MODEL_NAME):
    """通过 API 获取一批文本的嵌入向量。"""
    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "input": texts
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        embeddings_data = response.json().get('data', [])
        embeddings = [item['embedding'] for item in embeddings_data]
        return np.array(embeddings, dtype='float32')
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        if e.response is not None:
            print(f"Response body: {e.response.text}")
        return np.array([])


# --- 5. 主执行逻辑 (已更新) ---

def main():
    print("--- Step 1: Scanning and Extracting Text (Recursively) ---")
    
    # --- 主要改动在这里 ---
    all_files = []
    # os.walk 会递归遍历所有子目录
    for root, _, files in os.walk(CORPUS_DIRECTORY):
        for file in files:
            # 检查文件扩展名是否是我们支持的类型
            if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                all_files.append(os.path.join(root, file))
    # --- 改动结束 ---

    if not all_files:
        print(f"No documents with supported extensions {SUPPORTED_EXTENSIONS} found in '{CORPUS_DIRECTORY}' or its subdirectories.")
        return

    print(f"Found {len(all_files)} files to process.")
    all_chunks = []
    file_sources = [] 
    
    for file_path in tqdm(all_files, desc="Processing files"):
        # 使用相对路径作为来源标识，更清晰
        relative_path = os.path.relpath(file_path, CORPUS_DIRECTORY)
        ext = os.path.splitext(relative_path)[1].lower()
        text = ""
        
        if ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif ext == '.txt':
            text = extract_text_from_txt(file_path)
        elif ext == '.md':
            text = extract_text_from_md(file_path)
        elif ext == '.html':
            text = extract_text_from_html(file_path)

        if text:
            chunks = chunk_text(text)
            all_chunks.extend(chunks)
            # 记录来源，使用包含子目录的相对路径
            file_sources.extend([relative_path] * len(chunks)) 

    if not all_chunks:
        print("No text could be extracted from the documents.")
        return

    print(f"\n--- Step 2: Generating Embeddings for {len(all_chunks)} Chunks ---")
    
    batch_size = 32
    all_embeddings = []
    
    for i in tqdm(range(0, len(all_chunks), batch_size), desc="Generating Embeddings"):
        batch_texts = all_chunks[i:i+batch_size]
        batch_embeddings = get_embeddings(batch_texts)
        if batch_embeddings.size > 0:
            all_embeddings.append(batch_embeddings)

    if not all_embeddings:
        print("Embedding generation failed. Aborting.")
        return

    embeddings_matrix = np.vstack(all_embeddings)
    embedding_dim = embeddings_matrix.shape[1]
    print(f"\n--- Step 3: Building FAISS-GPU Index (Dimension: {embedding_dim}) ---")

    if not faiss.get_num_gpus():
        print("FAISS-GPU not available. Falling back to CPU.")
        index = faiss.IndexFlatL2(embedding_dim)
    else:
        print("Found GPU, building FAISS index on GPU.")
        res = faiss.StandardGpuResources()
        cpu_index = faiss.IndexFlatL2(embedding_dim)
        index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
        
    index.add(embeddings_matrix)
    print(f"Index built successfully. Total vectors in index: {index.ntotal}")

    print("\n--- Step 4: Saving Index and Chunks ---")
    
    if faiss.get_num_gpus() > 0:
        cpu_index_to_save = faiss.index_gpu_to_cpu(index)
        faiss.write_index(cpu_index_to_save, FAISS_INDEX_PATH)
    else:
        faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"FAISS index saved to '{FAISS_INDEX_PATH}'")

    chunk_data_with_source = [{"text": text, "source": source} for text, source in zip(all_chunks, file_sources)]
    with open(CHUNKS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunk_data_with_source, f, ensure_ascii=False, indent=4)
    print(f"Text chunks saved to '{CHUNKS_JSON_PATH}'")
    
    print("\n✅ Knowledge base creation complete!")


if __name__ == "__main__":
    if not os.path.exists(CORPUS_DIRECTORY):
        os.makedirs(CORPUS_DIRECTORY)
        print(f"Created directory '{CORPUS_DIRECTORY}'. Please add your financial documents and subdirectories to it.")
    else:
        main()