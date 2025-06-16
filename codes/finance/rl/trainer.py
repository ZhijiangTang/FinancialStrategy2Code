"""
金融策略强化学习训练器
"""
import os
import sys
import logging
from typing import Dict, Any

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 确保utils目录在Python路径中
utils_dir = os.path.join(project_root, 'utils')
if utils_dir not in sys.path:
    sys.path.insert(0, utils_dir)

# 导入所需模块
try:
    from utils.score_adapter import ScoreAdapter
except ImportError as e:
    logger.error(f"无法导入ScoreAdapter模块: {str(e)}")
    raise

class RLTrainer:
    """金融策略强化学习训练器"""
    
    def __init__(self, strategy_name: str, paper_json: Dict):
        """
        初始化强化学习训练器
        
        参数:
            strategy_name (str): 策略名称
            paper_json (dict): 论文内容
        """
        self.strategy_name = strategy_name
        self.paper_json = paper_json
        # 创建评分适配器
        self.reward_calculator = ScoreAdapter(strategy_name=strategy_name)
        logger.info("RLTrainer initialized successfully")
        
    def train_step(self, generated_code: str) -> float:
        """
        执行一个训练步骤，返回奖励值（基于论文一致性）
        
        参数:
            generated_code (str): 生成的策略代码
            
        返回:
            float: 强化学习奖励值
        """
        logger.info("Executing training step")
        # 计算奖励
        reward = self.reward_calculator.calculate_reward(
            paper_json=self.paper_json,
            generated_code=generated_code
        )
        logger.info(f"Training step completed. Reward: {reward:.2f}")
        return reward
        
    def get_missing_terms(self, generated_code: str) -> list:
        """
        获取论文中提到但未在代码中实现的术语列表
        
        参数:
            generated_code (str): 生成的策略代码
            
        返回:
            list: 缺失的术语列表
        """
        missing_terms = self.reward_calculator.get_missing_terms(
            paper_json=self.paper_json,
            generated_code=generated_code
        )
        logger.info(f"检测到缺失的术语: {missing_terms}")
        return missing_terms
        
    def suggest_improvements(self, generated_code: str) -> str:
        """
        根据缺失术语建议改进代码
        
        参数:
            generated_code (str): 生成的策略代码
            
        返回:
            str: 改进后的策略代码
        """
        missing_terms = self.get_missing_terms(generated_code)
        if not missing_terms:
            logger.info("没有发现缺失术语，无需改进")
            return generated_code
        
        logger.info(f"尝试补充缺失术语: {missing_terms}")
        
        # 简单的代码改进建议（可扩展为更复杂的逻辑）
        improvements = "\n# 补充缺失的技术指标\n" + "\n".join([
            f"def calculate_{term.lower().replace(' ', '_')}():\n    pass\n" 
            for term in missing_terms if term.isalpha()
        ])
        
        improved_code = generated_code + "\n" + improvements
        logger.info("代码已改进，新增以下内容:")
        logger.info(improvements)
        return improved_code