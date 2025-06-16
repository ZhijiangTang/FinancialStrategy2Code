"""
金融策略强化学习包初始化
"""
import os
import sys

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 显式导入子模块
try:
    from .trainer import RLTrainer
except ImportError as e:
    print(f"无法导入RLTrainer模块: {str(e)}")
    raise