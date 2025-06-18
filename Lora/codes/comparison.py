import json
import os
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# 模型路径配置（⚠️ 改成你自己的本地路径！）
LOCAL_MODEL_PATH = "/home/lihang/.cache/modelscope/hub/models/Qwen/Qwen1.5-0.5B-Chat"
LORA_CHECKPOINT = "../output/lora/financial_strategy/v3-20250617-150831/checkpoint-32"


# 数据集路径
DATASET_PATH = "../data/swift_format_dataset.jsonl"
OUTPUT_PATH = "../result/comparison_results.jsonl"


# 加载 tokenizer 和模型
print("Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH, local_files_only=True, trust_remote_code=True)
base_model = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL_PATH, local_files_only=True, trust_remote_code=True).to("cuda")

print("Loading LoRA model...")
lora_model = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL_PATH, local_files_only=True, trust_remote_code=True)
lora_model = PeftModel.from_pretrained(lora_model, LORA_CHECKPOINT).to("cuda")

def generate_response(model, query):
    inputs = tokenizer(query, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=2048,
        do_sample=True,
        temperature=0.9,     # 提高创造性
        top_p=0.95,          # nucleus sampling
        repetition_penalty=1.1  # 防止重复
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response[len(query):].strip()

# 读取数据集并推理
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    lines = [json.loads(line) for line in f]

results = []

for idx, item in enumerate(tqdm(lines, desc="Processing queries")):
    query = item["query"]

    # 原始模型生成
    base_response = generate_response(base_model, query)

    # LoRA 微调模型生成
    lora_response = generate_response(lora_model, query)

    results.append({
        "id": idx,
        "query": query,
        "base_model_response": base_response,
        "lora_model_response": lora_response
    })

# 保存结果
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for line in results:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")

print(f"Results saved to {OUTPUT_PATH}")