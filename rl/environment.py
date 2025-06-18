import numpy as np
import logging
from gym import Env
from gym.spaces import Discrete, Box
from transformers import AutoTokenizer
import torch
from rl.config import RLConfig
from score import ScoreModule

class RLConfig:
    """强化学习环境的配置类"""
    def __init__(self, 
                 max_steps=1000,
                 initial_cash_ratio=1.0,
                 initial_position_ratio=0.0,
                 trade_fee=0.001,
                 risk_free_rate=0.02,
                 window_size=5):
        """
        初始化配置参数
        
        参数:
            max_steps: 每个训练回合的最大步数
            initial_cash_ratio: 初始资金比例（0~1）
            initial_position_ratio: 初始持仓比例（0~1）
            trade_fee: 交易手续费率
            risk_free_rate: 无风险利率
            window_size: 用于计算收益率和波动率的时间窗口大小
        """
        self.max_steps = max_steps
        self.initial_cash_ratio = initial_cash_ratio
        self.initial_position_ratio = initial_position_ratio
        self.trade_fee = trade_fee
        self.risk_free_rate = risk_free_rate
        self.window_size = window_size

class StrategyEnvironment(Env):
    """
    金融策略生成的强化学习环境
    """
    def __init__(self, config=None):
        """
        初始化环境
        
        参数:
            config: 环境配置
        """
        super(StrategyEnvironment, self).__init__()
        
        self.config = config or RLConfig()
        
        # 加载基础模型分词器
        try:
            model_path = self.config.local_model_path
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        except Exception as e:
            raise RuntimeError(f"加载分词器失败: {e}")

        # 定义动作空间（token ID 的范围）
        self.action_space = Discrete(len(self.tokenizer))  # 动作对应 token ID
        
        # 定义状态空间（使用向量表示编码后的策略描述）
        self.observation_space = Box(
            low=0,
            high=len(self.tokenizer),
            shape=(1024,),  # 假设最大序列长度为 1024
            dtype=np.float32
        )
        
        # 存储当前状态（策略描述）
        self.state = None
        
        # 当前策略描述索引
        self.current_index = 0
        
        # 加载数据集
        self.dataset = self._load_dataset()
    
    def reset(self, seed=None, options=None):
        """
        重置环境到初始状态
        
        参数:
            seed: 随机种子
            options: 其他选项
        
        返回:
            state: 初始状态
        """
        super().reset(seed=seed)
        
        # 从数据集中获取一个策略描述
        self.current_index = 0
        strategy_description = self.dataset[self.current_index]['strategy_description']
        
        # 编码策略描述作为初始状态
        inputs = self.tokenizer(strategy_description, return_tensors="pt", padding=True, truncation=True)
        self.state = inputs['input_ids'].squeeze().numpy()[:1024]  # 截断或填充至最大长度
        
        return self.state, {}
    
    def _get_observation(self):
        """
        获取当前状态
        
        返回:
            observation: 当前状态
        """
        # 固定使用5天的历史数据
        window_size = 5
        
        # 计算最近5天的收益率
        recent_returns = np.zeros(window_size) if len(self.history_returns) < window_size else self.history_returns[-window_size:]
        
        # 计算最近5天的波动率
        recent_volatility = np.zeros(window_size) if len(self.history_volatility) < window_size else self.history_volatility[-window_size:]
        
        # 使用最新的RSI值
        rsi = 0.5 if len(self.history_rsi) < 1 else self.history_rsi[-1]
        
        # 构建状态向量
        state = np.array([
            self.cash_ratio,  # 当前资金比例
            self.position_ratio,  # 当前持仓比例
            *recent_returns,  # 最近5天的收益率
            *recent_volatility,  # 最近5天的波动率
            rsi  # 行业指数相对强度
        ])
        
        return state
    
    def step(self, action):
        """
        执行一个动作并返回新状态、奖励、是否结束等信息
        
        参数:
            action: 要执行的动作（token ID）
        
        返回:
            next_state: 下一个状态
            reward: 奖励值
            terminated: 是否终止
            truncated: 是否截断
            info: 其他信息
        """
        # 将动作转换为 token 并构建提示词
        generated_prompt = self.tokenizer.decode([action], skip_special_tokens=True)
        
        # 生成交易策略代码
        generated_code = self._generate_code(generated_prompt)
        
        # 获取参考代码
        reference_code = self.dataset[self.current_index]['code']
        
        # 计算奖励（基于生成代码与参考代码的匹配程度）
        reward = self._calculate_reward(generated_code, reference_code)
        
        # 更新步骤计数器
        self.current_index += 1
        self.state = self._get_next_state()
        
        # 判断是否结束
        terminated = (self.current_index >= len(self.dataset))
        
        return self.state, reward, terminated, False, {}
    
    def _execute_action(self, action):
        """
        执行交易操作并返回奖励
        
        参数:
            action: 要执行的动作
        
        返回:
            reward: 奖励值
        """
        # 根据动作调整仓位
        if action == 0:  # 增加仓位
            trade_amount = min(0.1, self.cash_ratio)  # 增加10%仓位，但不超过可用资金
            self.cash_ratio -= trade_amount
            self.position_ratio += trade_amount
            reward = 0.1  # 给予一个小奖励
        elif action == 1:  # 减少仓位
            trade_amount = min(0.1, self.position_ratio)  # 减少10%仓位
            self.position_ratio -= trade_amount
            self.cash_ratio += trade_amount
            reward = 0.05  # 给予一个小奖励
        elif action == 2:  # 保持仓位
            reward = 0.01  # 给予小奖励以鼓励稳定
        elif action == 3:  # 买入
            trade_amount = min(0.2, self.cash_ratio)  # 买入20%仓位
            self.cash_ratio -= trade_amount
            self.position_ratio += trade_amount
            reward = 0.2  # 给予较大奖励
        elif action == 4:  # 卖出
            trade_amount = min(0.2, self.position_ratio)  # 卖出20%仓位
            self.position_ratio -= trade_amount
            self.cash_ratio += trade_amount
            reward = 0.2  # 给予较大奖励
        
        # 简单的市场影响模型
        market_impact = np.random.normal(0, 0.01)  # 固定使用基础波动率
        
        # 统一处理交易成本
        trade_cost = 0
        if action in [0, 1, 3, 4]:  # 如果是买卖或增减仓操作
            trade_amount = 0.1 if action in [0, 1] else 0.2  # 小幅调整仓位时使用较小交易量
            trade_cost = trade_amount * self.config.trade_fee
            
        # 简化的奖励计算
        reward += market_impact - trade_cost  # 扣除交易成本
        
        # 记录历史数据
        self.history_returns.append(market_impact)
        self.history_volatility.append(abs(market_impact))
        self.history_rsi.append(np.random.rand())  # 在实际应用中应替换为真实RSI计算
        
        return reward
    
    def render(self, mode='human'):
        """
        渲染环境状态
        """
        print(f"Step: {self.current_step}")
        print(f"Cash ratio: {self.cash_ratio:.2f}")
        print(f"Position ratio: {self.position_ratio:.2f}")
        print(f"Current reward: {self._execute_action(2):.2f}")  # 使用保持仓位的奖励作为当前收益估计
    
    def close(self):
        """
        关闭环境
        """
        pass