"""
金融策略模块初始化文件
"""
import os
import sys

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 显式导入子模块
try:
    from .analyze_financial_strategy import FinancialStrategyAnalyzer
except ImportError as e:
    print(f"无法导入金融策略分析器: {str(e)}")
    raise