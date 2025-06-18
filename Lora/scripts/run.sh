#!/bin/bash

# 设置环境变量
export OPENAI_API_KEY="sk-ovbcsfjpkvyabqgnpypnrbgnxkvincjikogjdaketsqgwgmw"
export MODEL_NAME="Qwen/Qwen1.5-0.5B-Chat"
export DATASET_PATH="../data/swift_format_dataset.jsonl"
export OUTPUT_DIR="../output/lora/financial_strategy"
export CONFIG_PATH="../config/training_config.yaml"

mkdir -p $OUTPUT_DIR

echo "------- Training -------"

# 启动 LoRA 微调
swift sft \
    --model $MODEL_NAME \
    --train_type lora \
    --dataset=$DATASET_PATH \
    --torch_dtype bfloat16 \
    --output_dir $OUTPUT_DIR \
    --num_train_epochs=8 \
    --max_length=2048 \
    --lora_rank=8 \
    --lora_alpha=32 \
    --lora_dropout=0.05 \
    --target_modules all-linear \
    --gradient_checkpointing=true \
    --per_device_train_batch_size 4 \
    --weight_decay=0.1 \
    --learning_rate=5e-5 \
    --gradient_accumulation_steps=8 \
    --max_grad_norm=0.5 \
    --warmup_ratio=0.03 \
    --eval_steps=100 \
    --save_steps=100 \
    --save_total_limit=2 \
    --logging_steps=10 \
    --dataloader_num_workers 0

echo "------- Inference -------"

# 推理脚本（可选）
python ../codes/infer.py \
    --ckpt_dir $OUTPUT_DIR \
    --system "You are a financial strategy expert."
