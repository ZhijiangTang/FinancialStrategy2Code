import os
import sys
import json
import time
from tqdm import tqdm
from swift.llm import infer_main
from swift.utils import seed_everything
from swift.llm.utils.inference_utils import InferArguments
# 调用 infer_main() 并手动设置 eval_human=False
args, remaining_argv = InferArguments._parse_args()
args.eval_human = False  # 强制关闭交互模式
# 配置路径
CONFIG_PATH = "../config/infer_config.json"
DATASET_PATH = "../data/swift_format_dataset.jsonl"
OUTPUT_DIR = "../result/comparison_results1"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 读取配置文件
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    args_dict = json.load(f)

# 构建命令行参数
sys.argv = [
    'script',
    '--model', args_dict['model'],
    '--model_type', args_dict['model_type'],
    '--ckpt_dir', args_dict['ckpt_dir'],
    '--system', args_dict.get('system', ''),
    # '--eval_human', 'False'  # 固定关闭交互模式
]

seed_everything(42)  # 固定随机种子

# 初始化模型和 tokenizer（调用 infer_main）
tokenizer, base_model = infer_main()
_, lora_model = infer_main()

base_model = base_model.to('cuda')
lora_model = lora_model.to('cuda')

def generate_response(model, query):
    full_prompt = f"{args.system}\n\n{query}"
    inputs = tokenizer(full_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=2048,
        do_sample=True,
        temperature=0.9,
        top_p=0.95,
        repetition_penalty=1.1
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response[len(full_prompt):].strip()

# 读取数据集
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
        "strategy_name": item.get("strategy_name", f"id_{idx}"),
        "query": query,
        "base_model_response": base_response,
        "lora_model_response": lora_response
    })

# 保存结果
timestamp = int(time.time())
result_file = os.path.join(OUTPUT_DIR, f"comparison_{timestamp}.jsonl")
with open(result_file, "w", encoding="utf-8") as f:
    for line in results:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")

print(f"Comparison results saved to {result_file}")