import json
import os
from scores import CodeScore

# 输入输出文件路径
input_file = "../result/final_comparison_with_original.jsonl"
output_file = "../result/scores/eval_results.jsonl"

# 创建输出目录
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# 初始化评分器（ref_free 模式）
codescore = CodeScore(eval_type="ref_based", generated_n=3, model="Qwen/Qwen3-8B")

results = []

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line.strip())
        query = item.get("query", "")
        base_code = item.get("base_model_response", "")
        lora_code = item.get("lora_model_response", "")
        gold_code = item.get("original_response", "")

        print(f"Processing: {query[:50]}...")

        # 构造 paper_json（模拟论文内容为 query）
        paper_json = {"description": query}

        def score_response(name, code):
            if not code or code.strip() == "":
                return {
                    "score": 0,
                    "rationale": "Empty response"
                }
            try:
                result = codescore.score(
                    strategy_name=name,
                    paper_json=paper_json,
                    codes=code
                )
                return {
                    "score": result["eval_result"]["score"],
                    "rationale": result["eval_result"]["rationale_lst"][0]
                }
            except Exception as e:
                print(f"[ERROR] Failed to score {name}: {e}")
                return {
                    "score": 0,
                    "rationale": str(e)
                }

        # 分别评分
        base_score = score_response("Base Model", base_code)
        lora_score = score_response("LoRA Model", lora_code)
        gold_score = score_response("Original", gold_code)

        avg_score = (base_score["score"] + lora_score["score"] + gold_score["score"]) / 3

        results.append({
            "id": item.get("id", -1),
            "query": query,
            "base_score": base_score["score"],
            "base_rationale": base_score["rationale"],
            "lora_score": lora_score["score"],
            "lora_rationale": lora_score["rationale"],
            "gold_score": gold_score["score"],
            "gold_rationale": gold_score["rationale"],
            "avg_score": avg_score
        })

# 写入结果文件
with open(output_file, "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"\n✅ 所有样本已评分完成，结果保存至：{output_file}")