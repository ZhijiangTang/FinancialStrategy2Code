# Financial Strategy Code Generator

这是一个基于人工智能的金融策略代码生成系统，能够自动生成、分析和优化金融交易策略。

## 项目结构

```
FinancialStrategy2Code/
├── api_key/          # API密钥配置目录
├── assets/           # 静态资源文件
├── codes/            # 核心代码实现
│   ├── 1_planning.py     # 策略规划模块
│   ├── 1.1_extract_config.py  # 配置提取模块
│   ├── 2_analyzing.py    # 策略分析模块
│   ├── 3_coding.py       # 代码生成模块
│   └── utils.py          # 工具函数
├── data/             # 数据文件目录
├── datasets/         # 数据集目录
├── examples/         # 示例代码
├── myquant_dataset/  # MyQuant数据集
├── outputs/          # 输出结果目录
├── prompts/          # 提示词模板
├── score/            # 评分相关文件
├── scripts/          # 脚本文件
└── utils/            # 通用工具函数
```

## 环境要求

- Python 3.8+
- OpenAI API密钥
- 其他依赖包（见requirements.txt）

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/ZhijiangTang/FinancialStrategy2Code
cd FinancialStrategy2Code
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置API密钥：
在`api_key`目录下配置必要的API密钥。

## 主要功能

1. **策略规划**：通过`1_planning.py`进行策略的初始规划和设计
2. **策略分析**：使用`2_analyzing.py`对策略进行深入分析
3. **代码生成**：通过`3_coding.py`自动生成可执行的策略代码
4. **配置管理**：使用`1.1_extract_config.py`处理策略配置

## 使用方法

1. 准备数据：
   - 将数据文件放置在`data`或`datasets`目录下
   - 确保数据格式符合要求

2. 运行策略生成：
```bash
cd scripts
bash run.sh
```

3. 查看结果：
   - 生成的策略代码将保存在`outputs`目录

## 注意事项

- 请确保API密钥配置正确
- 建议在运行前备份重要数据
- 注意遵守相关金融法规和API使用限制
