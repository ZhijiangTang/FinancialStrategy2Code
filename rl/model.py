import torch
import logging
from config import RLConfig
from utils import score_module
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM

class RLConfig:
    """
    强化学习模型配置参数
    """
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.learning_rate = 5e-5
        self.max_grad_norm = 1.0
        self.num_training_steps = 1000
        self.warmup_steps = 100
        self.logging_interval = 10
        self.evaluation_interval = 50
        self.checkpoint_interval = 100
        self.batch_size = 16
        self.gamma = 0.99  # 折扣因子
        self.epsilon = 0.1  # 探索率

class StrategyModel:
    """
    强化学习策略模型，作为基础模型的适配器
    """
    def __init__(self, config=None):
        """
        初始化模型
        
        参数:
            config: 模型配置
        """
        self.config = config or RLConfig()
        
        # 替换为本地模型路径
        try:
            model_path = "/root/autodl-tmp/FinancialStrategy2Code/rl/models/Qwen2.5-Coder-7B-Instruct"
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        except Exception as e:
            raise RuntimeError(f"加载分词器失败: {e}")
    
    def load_model(self, model_path):
        """
        加载预训练模型

        参数:
            model_path: 模型路径
        """
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True
            )
            print(f"模型已加载 from {model_path}")
        except Exception as e:
            raise RuntimeError(f"加载模型失败: {e}")

    def train_step(self, states, actions, rewards):
        """
        执行一个训练步骤（对于本地模型，执行实际的训练逻辑）
        
        参数:
            states: 当前状态
            actions: 执行的动作
            rewards: 获得的奖励
        
        返回:
            loss: 训练损失
            outputs: 模型输出
        """
        if not hasattr(self, 'model'):
            raise RuntimeError("模型未加载，请先调用 load_model 方法")
        
        # 将状态转换为模型输入格式
        inputs = self.tokenizer(states, return_tensors="pt", padding=True, truncation=True).to(self.config.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # 计算损失（简化版）
        # 实际应用中应使用更复杂的损失计算方式
        loss = torch.tensor(0.0, device=self.config.device)  # 占位符，实际应根据奖励计算损失
        
        # 这里可以添加更复杂的提示词调整和优化逻辑
        avg_reward = np.mean(rewards)
        if avg_reward < 0.6:  # 假设0.6是阈值
            print("检测到生成代码质量较低，建议调整提示词模板")
        
        return loss.item(), outputs
    
    def _prepare_inputs(self, states, actions):
        """
        准备模型输入
        
        参数:
            states: 当前状态
            actions: 执行的动作
        
        返回:
            inputs: 模型输入
        """
        # 将状态和动作编码为文本
        texts = []
        for state, action in zip(states, actions):
            state_text = self._state_to_text(state)
            action_text = self._action_to_text(action)
            text = f"{state_text} {action_text}"
            texts.append(text)
        
        # 使用tokenizer进行编码
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)
        
        return inputs
    
    def _state_to_text(self, state):
        """
        将状态转换为文本表示
        
        参数:
            state: 当前状态
        
        返回:
            state_text: 状态的文本表示
        """
        # 提取状态特征
        cash_ratio, position_ratio, *features = state
        returns = features[:5]
        volatility = features[5:10]
        rsi = features[10]
        
        # 创建状态描述
        state_text = (
            f"当前资金比例：{cash_ratio:.2f}，"
            f"持仓比例：{position_ratio:.2f}，"
            f"最近5天收益率：{np.mean(returns):.4f}，"
            f"最近5天波动率：{np.mean(volatility):.4f}，"
            f"行业指数相对强度：{rsi:.4f}。"
        )
        
        return state_text
    
    def _action_to_text(self, action):
        """
        将动作转换为文本表示
        
        参数:
            action: 动作编号
        
        返回:
            action_text: 动作的文本表示
        """
        # 动作映射
        actions = {
            0: "增加仓位",
            1: "减少仓位",
            2: "保持仓位",
            3: "买入",
            4: "卖出"
        }
        
        return f"执行动作：{actions[action]}。"