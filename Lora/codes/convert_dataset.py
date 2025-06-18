# convert_dataset.py

import json
import os

# 输入路径
input_path = "../data/merged_strategy_dataset.json"
# 输出路径
output_path = "../data/swift_format_dataset.jsonl"

# 提示词模板
prompt_template = "请生成一个{strategy_name}策略代码"

def convert():
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(output_path, 'w', encoding='utf-8') as out_f:
        for item in data:
            strategy_id = item['strategy_id']
            strategy_code = item['strategy_code'].strip()
            strategy_desc = item['strategy_description'].strip()

            # 提取策略名称
            strategy_name = strategy_desc.split('\n')[0].replace("策略名称: ", "").strip()

            # 构造 query 和 response
            query = prompt_template.format(strategy_name=strategy_name)
            response = strategy_code

            # 写入 JSONL 文件
            out_f.write(json.dumps({
                "query": query,
                "response": response
            }, ensure_ascii=False) + '\n')

    print(f"✅ 数据已成功转换并保存至 {output_path}")

if __name__ == "__main__":
    convert()


# 当前的数据是这样的：

# json
# [
#   {
#     "strategy_id": "strategy_1",
#     "strategy_code": "python...",
#     "strategy_description": "策略名称: BSC-Transaction\n..."
#   },
#   ...
# ]
# 转化为：

# Swift 需要的是问答对格式（默认字段名）：

# json
# {
#   "query": "用户提问内容",
#   "response": "模型应该输出的内容"
# }