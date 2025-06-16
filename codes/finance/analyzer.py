"""
金融策略分析器，用于评估生成代码与论文的一致性
"""
import os
import sys
import logging
from typing import Dict, Any, List
import json

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class FinancialStrategyAnalyzer:
    """金融策略分析器，用于评估生成代码与论文的一致性"""
    
    def __init__(self):
        """初始化金融策略分析器"""
        self.strategies = []
        self.loaded_dataset = False
        logger.info("FinancialStrategyAnalyzer initialized")
        
    def load_strategy_dataset(self, dataset_path: str):
        """
        加载策略数据集
        
        参数:
            dataset_path (str): 数据集文件路径
        """
        if not os.path.exists(dataset_path):
            logger.error(f"数据集文件不存在: {dataset_path}")
            raise FileNotFoundError(f"找不到数据集文件: {dataset_path}")
        
        try:
            with open(dataset_path, 'r') as f:
                self.strategies = json.load(f)
            self.loaded_dataset = True
            logger.info(f"成功加载数据集: {len(self.strategies)} 个策略")
        except Exception as e:
            logger.error(f"加载数据集失败: {str(e)}")
            raise
        
    def extract_strategy_patterns(self) -> Dict[str, Any]:
        """提取策略模式"""
        if not self.loaded_dataset:
            logger.warning("数据集未加载，无法提取策略模式")
            return {}
        
        # 提取所有策略的关键词
        patterns = {
            "terms": set(),
            "indicators": set(),
            "risk_management": set()
        }
        
        for strategy in self.strategies:
            # 提取术语
            if "strategy_description" in strategy:
                terms = self._extract_terms(strategy["strategy_description"])
                patterns["terms"].update(terms)
            
            # 提取技术指标
            if "technical_indicators" in strategy:
                patterns["indicators"].update(strategy["technical_indicators"])
            
            # 提取风险控制方法
            if "risk_management" in strategy:
                patterns["risk_management"].update(strategy["risk_management"])
            
        # 转换为列表以便序列化
        for key in patterns:
            patterns[key] = list(patterns[key])
        
        return patterns
        
    def _extract_terms(self, text: str) -> List[str]:
        """
        从文本中提取关键术语
        
        参数:
            text (str): 输入文本
            
        返回:
            list: 提取的关键术语列表
        """
        # 这里可以实现更复杂的NLP逻辑
        # 当前使用简单关键词匹配
        keywords = [
            "RSI", "MACD", "SMA", "EMA", "Bollinger", "ATR",
            "止损", "止盈", "仓位管理", "移动平均线", "布林带"
        ]
        
        found_terms = [term for term in keywords if term.lower() in text.lower()]
        return found_terms
        
    def compare_with_reference(self, reference_strategy: Dict, generated_strategy: str) -> Dict[str, Any]:
        """
        对比生成的策略与参考策略
        
        参数:
            reference_strategy (dict): 参考策略
            generated_strategy (str): 生成的策略
            
        返回:
            dict: 分析结果
        """
        result = {
            "term_match_score": 0.0,
            "logic_consistency": 0.0,
            "parameter_accuracy": 0.0,
            "missing_terms": [],
            "extra_terms": []
        }
        
        if not isinstance(reference_strategy, dict):
            logger.error("参考策略必须是字典类型")
            return result
        
        try:
            # 提取参考策略中的术语
            ref_terms = self._extract_terms(reference_strategy.get("strategy_description", ""))
            
            # 提取生成策略中的术语
            gen_terms = self._extract_terms(generated_strategy)
            
            # 计算术语匹配度
            if ref_terms:
                matched_terms = [term for term in ref_terms if term in gen_terms]
                result["term_match_score"] = len(matched_terms) / len(ref_terms)
                result["missing_terms"] = [term for term in ref_terms if term not in gen_terms]
                result["extra_terms"] = [term for term in gen_terms if term not in ref_terms]
            
            # 简单的逻辑一致性评估（可扩展）
            if "buy_condition" in reference_strategy:
                buy_condition = reference_strategy["buy_condition"]
                result["logic_consistency"] = 1.0 if buy_condition in generated_strategy else 0.5
            
            # 参数准确性评估（可扩展）
            if "parameters" in reference_strategy:
                param_count = len(reference_strategy["parameters"])
                matched_params = 0
                for param, value in reference_strategy["parameters"].items():
                    if f"{param}" in generated_strategy and f"{value}" in generated_strategy:
                        matched_params += 1
                result["parameter_accuracy"] = matched_params / param_count if param_count > 0 else 0
            
            logger.info(f"术语匹配度: {result['term_match_score']:.2f}, 缺失术语: {result['missing_terms']}")
            logger.info(f"逻辑一致性: {result['logic_consistency']:.2f}, 参数准确性: {result['parameter_accuracy']:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"策略对比失败: {str(e)}")
            return result