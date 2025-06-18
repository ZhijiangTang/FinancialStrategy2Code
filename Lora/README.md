FinancialStrategy2Code/
├── codes/                  # 核心代码目录
│   ├── *.py                 # 各阶段处理脚本（PDF解析、提取配置、规划、分析、编码）
│   ├── eval.py              # 评估脚本
│   ├── infer.py             # 推理脚本
│   ├── train.py             # 训练入口脚本
│   └── utils.py             # 工具函数
│   └──codes/comparison.py-- # 对比脚本,生成对比数据集
│   └──codes/scores.py---#评分
│   └──codes/merge.py---#合并
│   └──codes/convert_dataset.py----#转换数据集


│
├── data/                   # 数据目录
│   └── merged_strategy_dataset.json  # 合并后的策略数据集
│
├── output/                 # 输出目录
│   └── lora/
│       └── financial_strategy/  # LoRA 微调模型输出路径
│           └── v1/v2/v3...        # 不同版本的训练结果
│
├── scripts/                # 运行脚本
│   └── run.sh               # LoRA 微调启动脚本
│
├── score/                  # 评估结果目录
│   └── id_*_eval_ref_based_Qwen/  # 不同ID的评估结果
│       └── Qwen3-8B_YYYYMMDD_HHMMSS/
│           └── score.json         # 单次运行评分结果
│
└── README.md               # 项目说明文档（见下方模板）

markdown

# Financial Strategy to Code Generation Project

This project aims to generate executable financial strategies based on user input using a fine-tuned language model (Qwen). The system is built with a pipeline that includes dataset preparation, model training (LoRA), inference, and evaluation.

---

## 📁 Project Structure

FinancialStrategy2Code/ ├── codes/ # Core scripts for processing, inference, and evaluation ├── data/ # Dataset files ├── output/ # Model checkpoints and outputs ├── scripts/ # Shell scripts for training/inference ├── score/ # Evaluation scores └── README.md # This file


---

## 🔧 Setup & Usage

### 1. Install Dependencies

Make sure you have the following installed:

- Python 3.x
- PyTorch
- Transformers
- Swift (for LoRA training)

```bash
!git clone git@github.com:modelscope/ms-swift.git
%cd ms-swift
!pip install -e .
!pip install transformers --upgrade
2. Train the Model
Run the training script:

bash
cd scripts
bash run.sh
The trained models will be saved in ../output/lora/financial_strategy.

3. Run Inference
Use infer.py with a checkpoint:

bash
python ../codes/infer.py --ckpt_dir ../output/lora/financial_strategy/v1
4. Evaluate Results
Evaluation results are stored under the score/ directory. Each subfolder corresponds to a different test case or experiment.

📊 Evaluation Metrics
Each score.json file contains metrics such as accuracy, fluency, and domain relevance of the generated strategy compared to reference texts.

📝 License
[MIT License]
```
