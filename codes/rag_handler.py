# FinancialStrategy2Code/codes/rag_handler.py

import numpy as np
import json
import faiss
from openai import OpenAI, OpenAIError

# --- 配置信息 (请在此处直接修改) ---
# *******************************************************************
# ** 重要：请在这里填入您的 SiliconFlow API Key **
API_KEY = "sk-" 
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
    """
    适配FAISS索引的RAG处理器，所有API请求均通过 OpenAI SDK 调用。
    """
    def __init__(self, top_k_retrieve=10, top_k_rerank=5):
        self.top_k_retrieve = top_k_retrieve
        self.top_k_rerank = top_k_rerank
        
        print(">> 步骤 1: 初始化API客户端并加载知识库...")
        try:
            # 初始化一个可复用的OpenAI客户端
            self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
            
            # 加载FAISS索引和文本块
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            with open(CHUNKS_JSON_PATH, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            print(f">> 知识库准备就绪，索引中包含 {self.index.ntotal} 条向量。")
        except FileNotFoundError as e:
            print(f"!! 严重错误: 知识库文件未找到: {e}")
            print("!! 请确保您已经运行 build_knowledge_base.py 并正确生成了索引文件。")
            self.index = None
        except Exception as e:
            print(f"!! 严重错误: 初始化失败: {e}")
            self.index = None

    def _get_embedding_via_api(self, text):
        """
        通过 OpenAI SDK 获取单个文本的BGE embedding。
        """
        try:
            response = self.client.embeddings.create(
                model=BGE_MODEL_NAME,
                input=[text] # API需要一个列表
            )
            embedding = response.data[0].embedding
            return np.array([embedding], dtype='float32')
        except OpenAIError as e:
            print(f"!! BGE embedding API 请求失败: {e}")
            return None

    def _call_llm(self, model, messages, max_tokens=None, temperature=0.7):
        """
        通过 OpenAI SDK 统一调用LLM（非流式）。
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": False # 关闭流式传输以获取完整响应
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**payload)
            return response.choices[0].message.content
        except OpenAIError as e:
            print(f"!! LLM ({model}) API 调用失败: {e}")
            return None
        except (KeyError, IndexError):
            print(f"!! 从LLM响应中解析内容失败。")
            return None


    def _rewrite_query(self, query):
        """使用LLM重写查询。"""
        print(f"\n>> 步骤 2: 重写查询...")
        prompt = f"请将以下用户查询改写得更适合在金融知识库中进行向量检索，使其更严谨清晰丰富。请直接返回改写后的查询，不要额外解释。\n原始查询: \"{query}\""
        
        rewritten_query = self._call_llm(
            model=REWRITER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.0 # 重写需要确定性
        )

        if rewritten_query:
            print(f"   - 原始查询: '{query}'")
            print(f"   - 重写后查询: '{rewritten_query.strip()}'")
            return rewritten_query.strip()
        
        print("   - 查询重写失败，使用原始查询。")
        return query

    def retrieve_and_rerank(self, original_query, rewritten_query):
        """执行“FAISS检索”与“LLM重排序”。"""
        # 阶段一：使用FAISS进行高效向量检索
        print("\n>> 步骤 3: FAISS向量检索...")
        query_embedding = self._get_embedding_via_api(rewritten_query)
        
        if query_embedding is None:
            print("   - 因无法获取查询向量，检索失败。")
            return []
            
        distances, indices = self.index.search(query_embedding, self.top_k_retrieve)
        retrieved_contexts = [self.chunks[i] for i in indices[0] if i < len(self.chunks)]
        print(f"   - 成功从FAISS召回 {len(retrieved_contexts)} 条候选知识。")
        
        # 阶段二：使用LLM对检索结果进行重排序
        print("\n>> 步骤 4: 大模型重排序...")
        if not retrieved_contexts: return []

        scored_contexts = []
        for context_chunk in retrieved_contexts:
            context_text = context_chunk.get('text', str(context_chunk))
            prompt = f"对用户查询和上下文的相关性进行打分（0-100分）。请只返回分数。\n\n用户查询: \"{original_query}\"\n\n上下文: \"{context_text}\""
            
            score_text = self._call_llm(
                model=REWRITER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.0 # 打分需要确定性
            )
            
            score = 0
            if score_text:
                try: score = int(score_text.strip())
                except (ValueError, TypeError): pass
            scored_contexts.append((score, context_text))

        scored_contexts.sort(key=lambda x: x[0], reverse=True)
        final_contexts = [context for score, context in scored_contexts[:self.top_k_rerank]]
        
        print(f"   - 重排序完成，最终选出 Top {self.top_k_rerank} 条知识。")
        print("   - 相关性分数（从高到低）:", [score for score, _ in scored_contexts[:self.top_k_rerank]])
        print("   - 最终选出的上下文片段:")
        for i, context in enumerate(final_contexts, 1):
            print(f"     {i}. {context[:50]}...")
        return final_contexts

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
                # 检查块中是否有内容
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    # print(content, end="", flush=True) # 立即打印，不换行
                    full_response.append(content)
            
            print("\n" + "="*55) # 打印一个结束符
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
        response = self.generate_answer(query, final_context)
        return response

# --- 主程序入口 ---
if __name__ == '__main__':
    rag = RAGHandler()
    if rag.index: 
        test_query = "什么是动量策略？"
        
        print(f"\n\n==================== 开始处理查询 ====================")
        print(f"用户查询: {test_query}")
        
        # 【修改点】现在答案会在 answer 方法内部以流式效果打印，无需在这里再次打印
        final_answer = rag.answer(test_query)

