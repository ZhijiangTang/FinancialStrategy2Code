# 强化学习模块（Reinforcement Learning Module）

本模块实现了基于本地部署的 Qwen2.5-Coder-7B-Instruct 模型的金融策略描述到代码生成系统，结合了监督预训练（SFT）和近端策略优化（PPO）算法进行强化学习微调。

## 🧠 核心理念

- **本地大模型支持**：使用 `Qwen/Qwen2.5-Coder-7B-Instruct` 模型进行代码生成，从指定路径加载本地模型。
- **强化学习微调**：采用 SFT + PPO 的两阶段训练流程，使用 LoRA 进行参数高效微调。
- **多维度奖励函数**：构建涵盖策略一致性、代码质量、风险管理等多个维度的奖励函数。
- **动态提示词优化**：根据历史反馈动态调整提示词模板，提升代码生成质量。

## 🚀 使用方式

### 1. 安装依赖

```
pip install -r requirements.txt
```

### 2. 下载本地模型

请将 `Qwen/Qwen2.5-Coder-7B-Instruct` 模型下载到以下路径：
```
/root/autodl-tmp/FinancialStrategy2Code/rl/models/Qwen2.5-Coder-7B-Instruct
```

### 3. 训练模型

```
python train.py --model-path ./output/optimized_prompt_model.pth
```

### 4. 评估模型

```bash
python evaluate.py --model-path ./output/optimized_prompt_model.pth --sample-count 5
```

评估结果将包含详细的多维度评分，包括：
- 策略一致性 (0.4)
- 代码质量 (0.1)
- 风险管理 (0.15)
- 可执行性 (0.1)
- 性能表现 (0.1)
- 完整性 (0.1)
- 创新性 (0.05)
- 合规性 (0.05)

### 5. 训练流程说明

1. **监督预训练 (SFT)**
   - 使用 `merged_strategy_dataset.json` 数据集进行初始训练
   - 配置参数：batch_size=4, learning_rate=1e-5
   - 目标：建立基础的策略理解能力和代码生成能力

2. **强化学习微调 (PPO)**
   - 基于 SFT 模型继续训练
   - 配置参数：batch_size=4, ppo_epochs=4, learning_rate=1e-5
   - 目标：通过动态提示词优化提升代码生成质量

3. **提示词优化**
   - 根据历史评分结果动态调整提示词模板
   - 当平均奖励低于阈值（如 0.6）时触发优化逻辑

### 6. 评估指标

本项目采用多维度评分系统，包含以下核心指标：

| 指标               | 权重 | 说明                           |
|--------------------|------|--------------------------------|
| 策略一致性         | 0.4  | 生成代码与策略描述的语义匹配度 |
| 代码质量           | 0.1  | 代码规范性、可读性             |
| 风险管理           | 0.15 | 是否包含止损、仓位控制等机制   |
| 可执行性           | 0.1  | 代码是否能直接运行             |
| 性能表现           | 0.1  | 代码执行效率                   |
| 完整性             | 0.1  | 功能实现的完整性               |
| 创新性             | 0.05 | 是否包含创新性的实现方式       |
| 合规性             | 0.05 | 是否符合编码规范和行业标准     |

## 📁 项目结构

本项目遵循清晰的模块化设计，主要包含以下核心组件：

```
rl/
├── config.py                # 配置参数（模型路径、训练参数等）
├── strategy_rl.py           # 强化学习策略实现
├── model.py                 # 模型加载与基础接口
├── dataset.py               # 数据集加载与处理
├── environment.py           # 强化学习环境定义（状态空间、动作空间、奖励函数）
├── score.py                 # 多维度评分模块（策略一致性、代码质量等）
├── train.py                 # 训练入口
├── evaluate.py              # 评估入口
└── utils.py                 # 工具函数和全局变量
```

## 📦 依赖安装

在运行项目之前，请确保已安装所有依赖项，可以通过以下命令完成：

```
pip install -r requirements.txt
```

## 📦 依赖安装

在运行项目之前，请确保已安装所有依赖项，可以通过以下命令完成：

```
pip install -r requirements.txt
```

## 📦 磁盘空间要求

- **模型存储**：确保 `/root/autodl-tmp/FinancialStrategy2Code/rl/models` 路径至少有 **20GB** 可用空间以容纳 Qwen2.5-Coder-7B-Instruct 模型文件。
- **数据集存储**：训练数据集（如 `merged_strategy_dataset.json`）应存放在 `/root/autodl-tmp/FinancialStrategy2Code/rl/data_rl/` 目录下。

## 🧩 路径检查与配置

- **模型路径**：`/root/autodl-tmp/FinancialStrategy2Code/rl/models/Qwen2.5-Coder-7B-Instruct`
- **数据集路径**：`/root/autodl-tmp/FinancialStrategy2Code/rl/data_rl/merged_strategy_dataset.json`
- **输出路径**：生成的模型文件将保存在 `./output/` 目录下。

请确保以上路径存在且可访问。如果路径不存在，请提前创建相关目录以避免运行时错误。

## 📝 示例输出

运行评估后，你将得到以下输出：

- 生成的交易策略代码文件（如 `generated_strategy_1.py`）
- JSON 格式的详细评估报告（如 `evaluation_result.json`）
- 控制台输出的多维度评分信息

## 🧪 示例策略与输出

本项目提供了一个示例策略文件 `examples/sample_strategy.json`，包含以下内容：

```
{
    "strategy_id": "sample_001",
    "strategy_description": "基于50日和200日移动平均线的交易策略...",
    "code": "import pandas as pd\ndef calculate_moving_average(data, short_window=50, long_window=200):..."
}
```

生成的代码将保存在 `output/` 目录下，评估结果将输出到 `evaluation_result.json` 文件中。

## 📊 结果对比

你可以运行 `compare.py` 来对比原始提示词与优化后提示词生成的代码质量差异。

```bash
python compare.py
```

这将输出每条样本的评分变化，并保存生成的代码和对比结果。

## 📄 示例数据

示例策略描述文件位于 `examples/sample_strategy.json`，你可以将其作为测试输入。

## ✅ 总结

本模块实现了一种新颖的本地大模型与强化学习相结合的方法，适用于金融策略生成任务。通过结合 Qwen2.5-Coder-7B-Instruct 模型和 PPO 强化学习算法，我们能够在本地环境中显著提升代码生成质量。