import os
import json
from swift.llm import ModelType, InferArguments, infer_main

def main():
    # 加载配置
    with open("../config/training_config.yaml", 'r') as f:
        config = json.load(f)

    # 微调参数设置
    args = {
        "model": config["model"],
        "train_type": config["train_type"],
        "dataset": config["dataset"],
        "torch_dtype": config["torch_dtype"],
        "output_dir": config["output_dir"],
        "num_train_epochs": config["num_train_epochs"],
        "max_length": config["max_length"],
        "lora_rank": config["lora_rank"],
        "lora_alpha": config["lora_alpha"],
        "lora_dropout": config["lora_dropout"],
        "target_modules": config["target_modules"],
        "gradient_checkpointing": config["gradient_checkpointing"],
        "per_device_train_batch_size": config["per_device_train_batch_size"],
        "weight_decay": config["weight_decay"],
        "learning_rate": config["learning_rate"],
        "gradient_accumulation_steps": config["gradient_accumulation_steps"],
        "max_grad_norm": config["max_grad_norm"],
        "warmup_ratio": config["warmup_ratio"],
        "eval_steps": config["eval_steps"],
        "save_steps": config["save_steps"],
        "save_total_limit": config["save_total_limit"],
        "logging_steps": config["logging_steps"],
        "dataloader_num_workers": config["dataloader_num_workers"]
    }

    # 执行微调
    print("Starting LoRA fine-tuning...")
    # 这里可以调用具体的训练逻辑或 Swift 的 API
    # 示例：swift.sft(**args)

if __name__ == "__main__":
    main()