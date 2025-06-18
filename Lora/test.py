# from transformers import AutoModelForCausalLM, AutoTokenizer
# from peft import PeftModel

# # 原始模型路径
# base_model = "/home/lihang/.cache/modelscope/hub/models/Qwen/Qwen1.5-0.5B-Chat"
# # LoRA 模型路径（注意指向具体的 checkpoint 目录）
# lora_model = "/home/lihang/FinancialStrategy2Code/output/lora/financial_strategy/v3-20250617-150831/checkpoint-32"


# # 加载原始模型
# model = AutoModelForCausalLM.from_pretrained(base_model)

# # 尝试加载 LoRA 权重
# try:
#     model = PeftModel.from_pretrained(model, lora_model)
#     print("✅ LoRA 模型加载成功！")
# except Exception as e:
#     print("❌ 加载失败:", str(e))
from transformers import AutoTokenizer, AutoModelForCausalLM
LOCAL_MODEL_PATH = "/home/lihang/.cache/modelscope/hub/models/Qwen/Qwen1.5-0.5B-Chat"
tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH, local_files_only=True, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL_PATH, local_files_only=True, trust_remote_code=True).to("cuda")

query = """
请根据以下描述生成一个 BTC-V反策略 的 Python 量化交易策略代码：
该策略基于价格反转原理，在 BTC/USDT 行情出现超卖或超买信号后，进行逆势开仓操作。
使用双均线交叉作为趋势判断依据，结合 RSI 指标识别超买超卖区域。
要求包含初始化函数、定时任务、下单逻辑和止损逻辑。
"""
inputs = tokenizer(query, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=512, do_sample=True, temperature=0.7)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(response[len(query):].strip())