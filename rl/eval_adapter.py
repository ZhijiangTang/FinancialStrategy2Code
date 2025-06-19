import json
import logging
from typing import Dict, Any
from score import ScoreModule

class EvalAdapter:
    """
    评估适配器，用于多维度评分生成代码的质量
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def evaluate(self, strategy_description: str, generated_code: str) -> float:
        """
        评估生成的代码质量
        
        参数:
            strategy_description: 策略描述文本
            generated_code: 生成的代码
        
        返回:
            score: 综合评分
        """
        try:
            # 计算综合评分
            score = score_module.score(generated_code, strategy_description)
            
            return score
        except Exception as e:
            self.logger.error(f"评估过程中发生错误: {e}", exc_info=True)
            raise
    
    def batch_evaluate(self, strategy_descriptions: List[str], generated_codes: List[str]) -> List[float]:
        """
        批量评估生成的代码质量
        
        参数:
            strategy_descriptions: 策略描述列表
            generated_codes: 生成的代码列表
        
        返回:
            scores: 评分列表
        """
        if len(strategy_descriptions) != len(generated_codes):
            raise ValueError("策略描述和生成代码的数量必须相同")
        
        scores = []
        for desc, code in zip(strategy_descriptions, generated_codes):
            score = self.evaluate(desc, code)
            scores.append(score)
        
        return scores