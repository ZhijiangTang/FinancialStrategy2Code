"""
强化学习评分适配器，用于将代码评分转换为强化学习奖励信号。
"""
import os
import sys
import logging
from typing import Dict, Any

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 确保finance目录在Python路径中
finance_dir = os.path.join(project_root, 'codes', 'finance')
if finance_dir not in sys.path:
    sys.path.insert(0, finance_dir)

# 导入金融策略分析模块
try:
    from finance.analyze_financial_strategy import FinancialStrategyAnalyzer
except ImportError as e:
    logger.error(f"无法导入FinancialStrategyAnalyzer模块: {str(e)}")
    raise

class ScoreAdapter:
    """将CodeScore评分结果适配为强化学习奖励信号的适配器类"""
    
    def __init__(self, eval_type="ref_free", strategy_name="default"):
        """
        初始化评分适配器
        
        参数:
            eval_type (str): 评估类型，可选"ref_free"或"ref_based"
            strategy_name (str): 策略名称
        """
        # 使用FinancialStrategyAnalyzer进行论文一致性评估
        self.analyzer = FinancialStrategyAnalyzer()
        self.strategy_name = strategy_name
        
        # 加载策略数据集
        dataset_path = os.path.join(project_root, 'datasets', 'merged_strategy_dataset.json')
        if not os.path.exists(dataset_path):
            logger.error(f"数据集文件不存在: {dataset_path}")
            raise FileNotFoundError(f"找不到数据集文件: {dataset_path}")
        
        self.analyzer.load_strategy_dataset(dataset_path)
        logger.info("ScoreAdapter initialized successfully")
        
    def calculate_reward(self, paper_json: Dict, generated_code: str) -> float:
        """
        计算强化学习奖励信号（基于论文一致性的评分）
        
        参数:
            paper_json (dict): 论文内容
            generated_code (str): 生成的策略代码
            
        返回:
            float: 强化学习奖励值
        """
        try:
            # 找到最相似的策略样本
            sample_strategy = self._find_similar_strategy(paper_json)
            
            # 进行详细对比分析
            analysis_result = self.analyzer.compare_with_reference(
                reference_strategy=sample_strategy,
                generated_strategy=generated_code
            )
            
            # 提取关键指标
            term_match_score = analysis_result["term_match_score"]
            logic_consistency = analysis_result["logic_consistency"]
            parameter_accuracy = analysis_result["parameter_accuracy"]
            
            # 计算加权奖励（专注于论文一致性）
            reward = (
                0.4 * term_match_score +
                0.3 * logic_consistency +
                0.3 * parameter_accuracy
            )
            
            logger.info(f"术语匹配度: {term_match_score:.2f}, 逻辑一致性: {logic_consistency:.2f}, 参数准确性: {parameter_accuracy:.2f}")
            logger.info(f"计算出的奖励值: {reward:.2f}")
            return reward
            
        except Exception as e:
            logger.error(f"评分计算失败: {str(e)}")
            return -1.0  # 返回默认负奖励表示失败
            
    def _find_similar_strategy(self, paper_json: Dict) -> Dict:
        """
        根据论文内容找到最相似的参考策略
        
        参数:
            paper_json (dict): 论文内容
            
        返回:
            dict: 最相似的参考策略
        """
        # 这里可以实现更复杂的相似度计算
        # 当前简单返回第一个策略作为示例
        return self.analyzer.strategies[0]
        
    def get_missing_terms(self, paper_json: Dict, generated_code: str) -> list:
        """
        获取论文中提到但未在代码中实现的术语列表
        
        参数:
            paper_json (dict): 论文内容
            generated_code (str): 生成的策略代码
            
        返回:
            list: 缺失的术语列表
        """
        analysis_result = self.analyzer.compare_with_reference(
            reference_strategy=self._find_similar_strategy(paper_json),
            generated_strategy=generated_code
        )
        return analysis_result.get("missing_terms", [])