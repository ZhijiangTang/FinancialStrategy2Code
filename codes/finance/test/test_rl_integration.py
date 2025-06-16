"""
强化学习与评分系统集成测试（专注于论文一致性）
"""
import os
import sys
import json
import numpy as np
import importlib

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 确保codes目录在Python路径中 - 修正双斜杠问题
codes_dir = os.path.normpath(project_root)
if codes_dir not in sys.path:
    sys.path.insert(0, codes_dir)

print(f"调试信息 - project_root: {project_root}")
print(f"调试信息 - codes_dir: {codes_dir}")
print(f"调试信息 - sys.path: {sys.path}")

# 尝试导入RLTrainer
try:
    from codes.finance.rl.trainer import RLTrainer
except ImportError:
    # 动态加载模块作为备选方案
    try:
        import importlib.util
        
        # 构建模块路径
        module_name = "codes.finance.rl.trainer"
        module_path = os.path.normpath(os.path.join(codes_dir, "finance", "rl", "trainer.py"))
        
        print(f"调试信息 - 模块文件存在: {os.path.exists(module_path)}")
        print(f"调试信息 - 模块文件路径: {module_path}")
        
        # 检查模块文件是否存在
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"找不到模块文件: {module_path}")
        
        # 动态加载模块
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            raise ImportError(f"无法创建模块spec，请检查文件路径和模块名称: {module_path}")
            
        trainer_module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = trainer_module
        spec.loader.exec_module(trainer_module)
        
        # 获取RLTrainer类
        RLTrainer = trainer_module.RLTrainer
        
    except Exception as e:
        raise ImportError("无法动态加载RLTrainer模块，请确保代码文件存在且路径正确") from e

# 导入金融策略分析器
try:
    from codes.finance.analyzer import FinancialStrategyAnalyzer
except ImportError:
    # 如果标准导入失败，尝试使用相对导入
    try:
        from ..analyzer import FinancialStrategyAnalyzer
    except Exception as e:
        raise ImportError("无法导入FinancialStrategyAnalyzer模块，请确保codes目录在Python路径中") from e

# 导入数据工具
try:
    from finance.data_utils import prepare_data
except ImportError:
    # 如果标准导入失败，尝试使用相对导入
    try:
        from ..data_utils import prepare_data
    except Exception as e:
        raise ImportError("无法导入data_utils模块，请确保codes目录在Python路径中") from e

def test_rl_score_integration():
    """测试强化学习与评分系统的集成"""
    print("\n=== 测试强化学习与评分系统集成 ===")
    try:
        # 准备测试数据
        dataset_path = os.path.join(project_root, 'datasets', 'merged_strategy_dataset.json')
        
        # 加载策略数据集
        analyzer = FinancialStrategyAnalyzer()
        analyzer.load_strategy_dataset(dataset_path)
        
        # 取第一个策略作为测试样本
        sample_strategy = analyzer.strategies[0]
        paper_json = {
            "strategy_description": sample_strategy['strategy_description'],
            "strategy_code": sample_strategy['strategy_code']
        }
        
        # 初始化强化学习训练器
        trainer = RLTrainer(strategy_name="test_strategy", paper_json=paper_json)
        
        # 模拟生成的策略代码（这里使用数据集中的代码作为测试）
        generated_code = sample_strategy['strategy_code']
        
        # 执行训练步骤并获取奖励
        reward = trainer.train_step(generated_code)
        print(f"✓ 基础奖励计算成功: {reward:.2f}")
        
        # 测试自定义奖励计算
        # 模拟生成新策略代码（简单修改原始代码）
        modified_code = generated_code.replace("stop_loss = 0.05", "stop_loss = 0.03")
        reward = trainer.train_step(modified_code)
        print(f"✓ 修改后的策略奖励计算成功: {reward:.2f}")
        
        # 测试缺失术语检测
        missing_terms = trainer.get_missing_terms(generated_code)
        print(f"✓ 检测到缺失术语: {missing_terms}")
        
        # 测试代码改进建议
        improved_code = trainer.suggest_improvements(generated_code)
        reward = trainer.train_step(improved_code)
        print(f"✓ 改进后策略奖励: {reward:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"调试信息 - 当前工作目录: {os.getcwd()}")
    test_result = test_rl_score_integration()
    print(f"\n整体测试结果: {'✓ 成功' if test_result else '✗ 失败'}")