import json

# 数据路径
DATASET_PATH = "../data/swift_format_dataset.jsonl"
COMPARISON_PATH = "../result/comparison_results.jsonl"
OUTPUT_PATH = "../result/final_comparison_with_original.jsonl"

# 读取原始 dataset 的 query -> response 映射
dataset_map = {}
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line.strip())
        query = item["query"]
        response = item.get("response", "")
        dataset_map[query] = response

# 读取 comparison_results 并合并 original response
results = []
with open(COMPARISON_PATH, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line.strip())
        query = item["query"]
        base_resp = item["base_model_response"]
        lora_resp = item["lora_model_response"]

        # 获取原始 response
        original_response = dataset_map.get(query, "")

        results.append({
            "query": query,
            "base_model_response": base_resp,
            "lora_model_response": lora_resp,
            "original_response": original_response
        })

# 写入新文件
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for line in results:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")

print(f"已合并至 {OUTPUT_PATH}")