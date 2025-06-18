import os
import sys
import json
from swift.llm import ModelType, InferArguments, infer_main
import time

def main():
    # 从配置文件加载参数
    config_path = '../config/infer_config.json'
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file {config_path} not found.")

    with open(config_path, 'r') as f:
        args_dict = json.load(f)

     # 确保 output_dir 是目录，然后生成唯一文件名
    output_dir = args_dict['output_dir']
    os.makedirs(output_dir, exist_ok=True)  # 确保目录存在
    timestamp = int(time.time())  # 获取当前时间戳
    result_file = os.path.join(output_dir, f"{timestamp}.jsonl")  # 构造文件路径

    # 构建命令行参数
    args = [
        '--model', args_dict['model'],
        '--model_type', args_dict['model_type'],
        '--ckpt_dir', args_dict['ckpt_dir'],
        '--system', args_dict.get('system', ''),
        '--result_path',result_file,
    ]

    print("Starting inference with model:", args_dict['model'])
    sys.argv = [sys.argv[0]] + args  # 替换 sys.argv
    infer_main()

if __name__ == "__main__":
    main()