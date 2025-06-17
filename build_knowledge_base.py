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

# --- 1. 配置区域 ---
SILICONFLOW_API_KEY = "sk-"
API_URL = "https://api.siliconflow.cn/v1/embeddings"
BGE_MODEL_NAME = "BAAI/bge-m3"

CORPUS_DIRECTORY = "/home/sonata/FinancialStrategy2Code/corpus"
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".html"]

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

FAISS_INDEX_PATH = "knowledge_base.index"
CHUNKS_JSON_PATH = "chunks.json"


# --- 2. 文本提取模块 (已更新) ---

def read_file_with_fallbacks(file_path):
    """
    尝试用多种编码读取文件，以增加稳健性。
    首先尝试 UTF-8，然后是 GBK。如果都失败，则使用带错误忽略的 UTF-8。
    """
    try:
        # 首先，尝试最常见的 UTF-8 编码
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 如果 UTF-8 解码失败，记录一个警告并尝试 GBK 编码（在中文环境中常见）
        print(f"Warning: UTF-8 decoding failed for {file_path}. Trying 'gbk'.")
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except Exception as e:
            # 如果 GBK 也失败了，作为最后手段，使用 UTF-8 并忽略错误
            print(f"Warning: GBK decoding also failed for {file_path}. Reading with utf-8 and ignoring errors. Error: {e}")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception as final_e:
                # 如果连最后手段都失败了，打印错误并返回空字符串
                print(f"Error: Could not read file {file_path} even with fallbacks: {final_e}")
                return ""
    except Exception as e:
        print(f"Error: An unexpected error occurred while opening {file_path}: {e}")
        return ""


def extract_text_from_pdf(file_path):
    """使用 PyMuPDF 从 PDF 文件中提取文本"""
    try:
        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        # print(text[:1000])  # 打印前1000个字符以检查内容
        return text
    except Exception as e:
        print(f"Error processing PDF {file_path}: {e}")
        return ""

def extract_text_from_txt(file_path):
    """从 TXT 文件中提取文本"""
    try:
        return read_file_with_fallbacks(file_path)
    except Exception as e:
        print(f"Error processing TXT {file_path}: {e}")
        return ""

def extract_text_from_md(file_path):
    """从 Markdown 文件中提取纯文本"""
    try:
        raw_md = read_file_with_fallbacks(file_path)
        if raw_md:
            html = markdown(raw_md)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
        return ""
    except Exception as e:
        print(f"Error processing MD {file_path}: {e}")
        return ""

def extract_text_from_html(file_path):
    """从 HTML 文件中提取纯文本"""
    try:
        html_content = read_file_with_fallbacks(file_path)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            return soup.get_text()
        return ""
    except Exception as e:
        print(f"Error processing HTML {file_path}: {e}")
        return ""

# --- 3. 文本处理模块 ---

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """将长文本切分为带有重叠的块"""
    # 过滤掉文本中的空字节，这可能是导致API错误的另一个原因
    text = text.replace('\x00', '')
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

# --- 4. 向量化模块 ---

def get_embeddings(texts, model=BGE_MODEL_NAME):
    """通过 API 获取一批文本的嵌入向量。"""
    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json",
    }
    # 确保输入的文本不为空
    valid_texts = [text for text in texts if text.strip()]
    if not valid_texts:
        return np.array([])
        
    payload = {
        "model": model,
        "input": valid_texts
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
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return np.array([])
    except Exception as e:
        print(f"An unexpected error occurred during embedding generation: {e}")
        return np.array([])


# --- 5. 主执行逻辑 ---

def main():
    print("--- Step 1: Scanning and Extracting Text (Recursively) ---")
    
    all_files = []
    for root, _, files in os.walk(CORPUS_DIRECTORY):
        for file in files:
            if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                all_files.append(os.path.join(root, file))

    if not all_files:
        print(f"No documents with supported extensions {SUPPORTED_EXTENSIONS} found in '{CORPUS_DIRECTORY}' or its subdirectories.")
        return

    print(f"Found {len(all_files)} files to process.")
    all_chunks = []
    file_sources = [] 
    
    for file_path in tqdm(all_files, desc="Processing files"):
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

        if text and text.strip():
            chunks = chunk_text(text)
            if chunks:
                all_chunks.extend(chunks)
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
    print(f"\n--- Step 3: Building FAISS Index (Dimension: {embedding_dim}) ---")

    # 根据 faiss 版本决定使用 CPU 还是 GPU
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
    print(f"Text chunks saved to '{CHUNKS_JSON_PATH}'")
    
    print("\n✅ Knowledge base creation complete!")


if __name__ == "__main__":
    if not os.path.exists(CORPUS_DIRECTORY):
        os.makedirs(CORPUS_DIRECTORY)
        print(f"Created directory '{CORPUS_DIRECTORY}'. Please add your financial documents and subdirectories to it.")
    else:
        main()
