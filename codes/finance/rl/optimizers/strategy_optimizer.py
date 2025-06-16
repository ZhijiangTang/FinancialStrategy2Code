"""
策略优化器接口
"""
import os
import sys
from typing import List, Dict, Any
import numpy as np
from ..agents.dqn_agent import DQNAgent
from ..environments.strategy_env import StrategyEnv

# Add codes directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from codes.finance.utils.strategy_scorer import calculate_strategy_score

class StrategyOptimizer:
    """策略优化器，使用强化学习优化金融策略"""
    
    def __init__(self, data: np.ndarray, action_size: int, initial_balance: float = 10000):
        self.env = StrategyEnv(data, {"initial_balance": initial_balance})
        state_example = self.env.reset()
        self.state_size = len(np.asarray(state_example, dtype=np.float32).flatten())
        self.agent = DQNAgent(self.state_size, action_size)
        self.batch_size = 32
        self.episodes = 100