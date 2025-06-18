import numpy as np
import json
import faiss
from openai import OpenAI, OpenAIError
import re 

# *******************************************************************# 配置 OpenAI API 密钥
# 请确保在环境变量中设置 SILICONFLOW
API_KEY = "sk-cjnnfcatihrikdywnbebqofrrhfyzmzoturkcyyagrnlrjud"
# *******************************************************************

BASE_URL = "https://api.siliconflow.cn/v1"

# --- 模型与文件路径配置 ---
BGE_MODEL_NAME = "BAAI/bge-m3"
FAISS_INDEX_PATH = "../knowledge_base.index"
CHUNKS_JSON_PATH = "../chunks.json"

# 用于重写、重排和生成的LLM模型
REWRITER_MODEL = "Qwen/Qwen3-30B-A3B"
GENERATOR_MODEL = "Qwen/Qwen3-30B-A3B"

class RAGHandler:
    def __init__(self, top_k_retrieve=10, top_k_rerank=3):
        self.top_k_retrieve = top_k_retrieve
        self.top_k_rerank = top_k_rerank
        
        print(">> 步骤 1: 初始化API客户端并加载知识库...")
        if not API_KEY:
            print("!! 严重错误: API Key 未设置。请在环境变量或.env文件中设置 SILICONFLOW_API_KEY。")
            self.client = None
            self.index = None
            return

        try:
            self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            with open(CHUNKS_JSON_PATH, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            print(f">> 知识库准备就绪，索引中包含 {self.index.ntotal} 条向量。")
        except FileNotFoundError as e:
            print(f"!! 严重错误: 知识库文件未找到: {e}")
            self.index = None
        except Exception as e:
            print(f"!! 严重错误: 初始化失败: {e}")
            self.index = None

    def _get_embedding_via_api(self, text):
        try:
            response = self.client.embeddings.create(
                model=BGE_MODEL_NAME,
                input=[text]
            )
            return np.array([response.data[0].embedding], dtype='float32')
        except OpenAIError as e:
            print(f"!! BGE embedding API 请求失败: {e}")
            return None

    def _call_llm(self, model, messages, max_tokens=None, temperature=0.7, json_mode=False): # --- OPTIMIZATION ---
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
            # --- OPTIMIZATION: Use JSON mode for structured output ---
            if json_mode:
                payload["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**payload)
            return response.choices[0].message.content
        except OpenAIError as e:
            print(f"!! LLM ({model}) API 调用失败: {e}")
            return None
        except (KeyError, IndexError):
            print(f"!! 从LLM响应中解析内容失败。")
            return None

    def _rewrite_query(self, query):
        print(f"\n>> 步骤 2: 重写查询...")
        prompt = f"请根据用户输入，判断可以需要的知识，生成简短的问题供RAG在金融知识库中进行向量检索，使其更严谨清晰丰富。请直接返回改写后的查询，不要额外解释。\n原始查询: \"{query}\""
        rewritten_query = self._call_llm(
            model=REWRITER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.0
        )
        if rewritten_query:
            # print(f"   - 原始查询: '{query}'")
            print(f"   - 重写后查询: '{rewritten_query.strip()}'")
            return rewritten_query.strip()
        print("   - 查询重写失败，使用原始查询。")
        return query

    # --- OPTIMIZATION: Replaced the entire reranking logic ---
    def retrieve_and_rerank(self, original_query, rewritten_query):
        """
        执行“FAISS检索”与“LLM重排序”。
        【修改点】此版本不依赖json_mode，通过优化提示词和解析逻辑来提高稳定性。
        """
        # 1. FAISS Vector Retrieval
        print("\n>> 步骤 3: FAISS向量检索...")
        query_embedding = self._get_embedding_via_api(rewritten_query)
        if query_embedding is None:
            print("   - 因无法获取查询向量，检索失败。")
            return []
            
        distances, indices = self.index.search(query_embedding, self.top_k_retrieve)
        retrieved_contexts = [self.chunks[i] for i in indices[0] if i < len(self.chunks)]
        print(f"   - 成功从FAISS召回 {len(retrieved_contexts)} 条候选知识。")
        
        if not retrieved_contexts:
            return []

        # 2. Rerank with a Single LLM Call
        print("\n>> 步骤 4: 大模型重排序 (单次API调用)...")
        
        context_texts = [chunk.get('text', str(chunk)) for chunk in retrieved_contexts]
        prompt_documents = "\n\n".join([f'--- 文档【{i}】---\n"{text}"' for i, text in enumerate(context_texts)])
        
        # --- 优化的提示词：更明确地要求输出格式 ---
        prompt = (
            f"你是一个排序助手。请根据用户查询，从下面的多个文档中，选出与查询最相关的 Top {self.top_k_rerank} 个文档。"
            f"请严格按照相关性从高到低的顺序列出这些文档的索引号。\n\n"
            f"--- 用户查询 ---\n{rewritten_query}\n\n"
            f"--- 文档列表 ---\n{prompt_documents}\n\n"
            f"--- 你的任务 ---\n"
            f"你的回答必须且只能是一个JSON数组，其中包含你选择的文档索引。例如：[2, 0, 5]。不要包含任何其他文字、解释或代码块标记。"
        )

        rerank_result_str = self._call_llm(
            model=REWRITER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.0
        )
        
        final_contexts = []
        # --- 更稳健的解析逻辑 ---
        if not rerank_result_str:
            print("   - LLM重排序未返回任何内容，将按原始检索顺序选择。")
        else:
            try:
                # 使用正则表达式从可能的答复中提取出JSON列表
                # 例如，从 "好的，这是给您的列表: [2, 0, 1]" 中提取 "[2, 0, 1]"
                match = re.search(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', rerank_result_str)
                if not match:
                    raise ValueError("在LLM的返回结果中未找到格式正确的列表。")
                
                reranked_indices = json.loads(match.group())
                
                if isinstance(reranked_indices, list):
                    final_contexts = [context_texts[i] for i in reranked_indices if i < len(context_texts)]
                    print(f"   - 重排序完成，模型选出的最佳索引: {reranked_indices}")
                else:
                    raise ValueError("JSON输出不是一个列表。")

            except (json.JSONDecodeError, ValueError, TypeError, IndexError) as e:
                print(f"   - LLM重排序结果解析失败 ({e})，将按原始检索顺序选择Top {self.top_k_rerank}。")
                print(f"   - 模型原始返回: '{rerank_result_str}'")


        if not final_contexts:
             # 如果解析失败或LLM返回空，执行回退逻辑
            final_contexts = context_texts[:self.top_k_rerank]

        print(f"   - 最终选出 Top {len(final_contexts)} 条知识。")
        for i, context in enumerate(final_contexts, 1):
            print(f"     {i}. {context[:50]}...")
        return final_contexts

    # ... (generate_answer and other methods remain the same) ...
    def generate_answer(self, query, context):
        """
        【修改点】使用最相关的上下文生成最终答案，并带有流式打印效果。
        """
        print("\n>> 步骤 5: 生成最终答案...")
        prompt_context = "\n\n".join(context) if context else "知识库中没有找到相关信息。"
        prompt = (
            f"请严格根据下面提供的“上下文信息”，清晰并简洁地回答“用户查询”。不要回答多余的东西，如果上下文不足以回答，请谨慎补充并标记\n\n"
            f"--- 上下文信息 ---\n{prompt_context}\n\n"
            f"--- 用户查询 ---\n{query}"
        )
        
        payload = {
            "model": GENERATOR_MODEL,
            "messages": [
                {"role": "system", "content": "你是一个严谨的金融交易助手，作为RAG的一个模块，你的回答基于用户提供的上下文信息，不要回答多余的东西，如果信息不足，请谨慎补充"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "stream": True # 开启流式传输以实现打字机效果
        }

        try:
            response_stream = self.client.chat.completions.create(**payload)
            
            full_response = []
            print("\n" + "="*20 + " 模型回复中... " + "="*20)
            for chunk in response_stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response.append(content)
            
            print("\n" + "="*55)
            return "".join(full_response)

        except OpenAIError as e:
            print(f"\n!! LLM ({GENERATOR_MODEL}) API 调用失败: {e}")
            return "抱歉，生成答案时发生错误。"

    def answer(self, query):
        """执行完整的 RAG 流程。"""
        if not self.index or not self.client:
            return "错误：RAG处理器未成功初始化，无法处理查询。"
        
        rewritten_query = self._rewrite_query(query)
        final_context = self.retrieve_and_rerank(original_query=query, rewritten_query=rewritten_query)
        response = self.generate_answer(rewritten_query, final_context)
        return response

# --- Main execution block remains the same ---
if __name__ == '__main__':
    rag = RAGHandler()
    if rag.index: 
        test_query = "什么是海龟交易？"
        print(f"\n\n==================== 开始处理查询 ====================")
        print(f"用户查询: {test_query}")
        final_answer = rag.answer(test_query)