import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import pylint.lint
from pylint.reporters.text import TextReporter
import tempfile
import os
import logging

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScoreModule:
    """
    评分模块，用于评估生成代码的质量
    """
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer()
        
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本之间的相似度（使用 TF-IDF + 余弦相似度）
        
        参数:
            text1: 文本1
            text2: 文本2
        
        返回:
            similarity: 相似度评分（0-1）
        """
        tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    def _calculate_code_quality(self, code: str) -> float:
        """
        计算代码质量评分（基于 Pylint）
        
        参数:
            code: 代码字符串
        
        返回:
            quality_score: 质量评分（0-1）
        """
        try:
            # 创建临时文件并写入代码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmpfile:
                tmpfile.write(code)
                tmpfile_path = tmpfile.name
            
            # 运行 Pylint
            pylint_opts = ['--output-format=text', '--disable=all', '--enable=F,E,warning-category', tmpfile_path]
            reporter = TextReporter()
            result = pylint.lint.Run(plint_opts, reporter=reporter, exit=False)
            
            # 解析结果
            score = (result.linter.stats['info'] + result.linter.stats['convention']) / 10.0  # 归一化为 0-1 分
            
            # 清理临时文件
            os.unlink(tmpfile_path)
            
            return score
        except Exception as e:
            logger.error(f"代码质量评估失败: {e}")
            return 0.0
    
    def _calculate_risk_management(self, code: str) -> float:
        """
        检查代码中的风险控制机制
        
        参数:
            code: 代码字符串
        
        返回:
            risk_score: 风险评分（0-1）
        """
        # 实际应用中应实现更复杂的逻辑来检测风险控制机制
        risk_keywords = ['stop_loss', 'position_size', 'risk_ratio', 'max_drawdown']
        found_keywords = sum(1 for keyword in risk_keywords if keyword in code)
        return min(found_keywords / len(risk_keywords), 1.0)
    
    def score(self, generated_code: str, strategy_description: str) -> float:
        """
        评估生成的代码质量
        
        参数:
            generated_code: 生成的代码
            strategy_description: 策略描述
        
        返回:
            score: 综合评分
        """
        # 各维度权重
        weights = {
            'strategy_consistency': 0.4,
            'code_quality': 0.1,
            'risk_management': 0.15,
            'executability': 0.1,
            'performance': 0.1,
            'completeness': 0.1,
            'innovation': 0.05,
            'compliance': 0.05
        }
        
        # 计算各维度评分
        scores = {
            'strategy_consistency': self._calculate_text_similarity(generated_code, strategy_description),
            'code_quality': self._calculate_code_quality(generated_code),
            'risk_management': self._calculate_risk_management(generated_code),
            'executability': 1.0 if self._is_executable(generated_code) else 0.0,
            'performance': self._calculate_performance(generated_code),
            'completeness': self._calculate_completeness(generated_code, strategy_description),
            'innovation': self._detect_innovation(generated_code),
            'compliance': self._check_compliance(generated_code)
        }
        
        # 计算综合评分
        total_score = sum(score * weights[key] for key, score in scores.items())
        
        return total_score
    
    def _is_executable(self, code: str) -> bool:
        """
        检查代码是否可执行
        
        参数:
            code: 代码字符串
        
        返回:
            executable: 是否可执行
        """
        try:
            # 尝试解析语法
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def _calculate_performance(self, code: str) -> float:
        """
        评估性能表现（简化版）
        
        参数:
            code: 代码字符串
        
        返回:
            performance_score: 性能评分（0-1）
        """
        # 实际应用中应运行基准测试
        return np.random.uniform(0.6, 1.0)
    
    def _calculate_completeness(self, code: str, description: str) -> float:
        """
        评估代码完整性（简化版）
        
        参数:
            code: 代码字符串
            description: 策略描述
        
        返回:
            completeness_score: 完整性评分（0-1）
        """
        # 实际应用中应分析代码与描述的匹配程度
        return np.random.uniform(0.7, 1.0)
    
    def _detect_innovation(self, code: str) -> float:
        """
        检测创新性（简化版）
        
        参数:
            code: 代码字符串
        
        返回:
            innovation_score: 创新性评分（0-1）
        """
        # 实际应用中应比较现有策略库
        return np.random.uniform(0.5, 1.0)
    
    def _check_compliance(self, code: str) -> float:
        """
        检查合规性（简化版）
        
        参数:
            code: 代码字符串
        
        返回:
            compliance_score: 合规性评分（0-1）
        """
        # 实际应用中应检查是否符合编码规范
        return np.random.uniform(0.8, 1.0)