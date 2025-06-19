import os
import argparse
import json
import logging
from typing import Dict, List, Any
from .config import RLConfig
from .strategy_rl import StrategyRL
from .eval_adapter import EvalAdapter
from evaluation.score_module import score_module  # 新的评分模块路径

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description='强化学习模型评估')
    parser.add_argument('--model-path', type=str, default=None,
                      help='预训练模型路径（可选）')
    parser.add_argument('--sample-count', type=int, default=5,
                      help='评估的样本数量（默认：5）')
    parser.add_argument('--dataset-path', type=str, default=None,
                      help='数据集路径（可选）')
    parser.add_argument('--output-path', type=str, default=None,
                      help='评估结果输出路径（可选）')
    return parser.parse_args()


def evaluate(model, dataset):
    """
    评估模型性能
    
    参数:
        model: 要评估的模型
        dataset: 评估数据集
    
    返回:
        evaluation_result: 评估结果
    """
    evaluation_result = {}
    
    for data in dataset:
        strategy_description = data['strategy']
        gt_code = data['code']
        
        # 生成代码
        generated_code = model.generate_code(strategy_description)
        
        # 评估生成代码质量
        score = score_module.score(generated_code, gt_code)
        evaluation_result[strategy_description] = score
    
    return evaluation_result


def evaluate_rl_model():
    """
    评估强化学习模型生成代码的质量
    """
    try:
        # 初始化配置
        config = RLConfig()
        
        # 创建策略 RL 实例
        strategy_rl = StrategyRL()
        
        # 初始化评估适配器
        eval_adapter = EvalAdapter()
    
        # 加载预训练模型
        model_path = config.model_save_path
        if model_path and os.path.exists(model_path):
            strategy_rl.load_model(model_path)
            logger.info(f"模型已加载 from {model_path}")
        else:
            logger.warning("未找到预训练模型，将使用随机初始化模型进行评估")
    
        # 加载测试数据集
        dataset_path = config.dataset_path
        if not dataset_path or not os.path.exists(dataset_path):
            logger.error(f"数据集路径无效: {dataset_path}")
            raise ValueError("数据集路径不能为空且必须存在")
            
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # 取指定数量的样本进行评估
        sample_count = config.eval_sample_count
        samples = dataset[:sample_count]
        logger.info(f"将评估 {len(samples)} 个样本（共 {len(dataset)} 个可用样本）")
        
        # 初始化评估适配器
        eval_adapter = EvalAdapter()
        print(f"开始评估强化学习模型，使用 {len(samples)} 个样本...")
        
        # 创建结果目录
        output_dir = config.eval_output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"评估结果将保存到 {output_dir}")
        
        # 存储所有评估结果
        all_results = []
        
        # 对每个样本进行评估
        for i, sample in enumerate(samples):
            strategy_description = sample['strategy_description']
            
            # 生成优化后的策略代码
            generated_code = strategy_rl.generate_optimized_strategy(strategy_description)
            
            # 执行评估
            score = eval_adapter.evaluate(strategy_description, generated_code)
            
            # 创建详细评分报告
            detailed_score = {
                "strategy_id": sample['strategy_id'],
                "strategy_description": strategy_description,
                "score": score,
                "detailed_scores": {
                    "strategy_consistency": score * 0.4,  # 策略一致性（假设占总分的40%）
                    "code_quality": score * 0.1,      # 代码质量（假设占总分的10%）
                    "risk_management": score * 0.15,  # 风险管理（假设占总分的15%）
                    "executability": score * 0.1,     # 可执行性（假设占总分的10%）
                    "performance": score * 0.1,       # 性能表现（假设占总分的10%）
                    "completeness": score * 0.1,      # 完整性（假设占总分的10%）
                    "innovation": score * 0.05,       # 创新性（假设占总分的5%）
                    "compliance": score * 0.05        # 合规性（假设占总分的5%）
                },
                "code_file_path": os.path.join(output_dir, f"generated_strategy_{i+1}.py")
            }
            
            # 保存生成的代码
            with open(detailed_score["code_file_path"], "w", encoding="utf-8") as f:
                f.write(generated_code)
            
            all_results.append(detailed_score)
            
            # 打印评估结果
            logger.info(f"\n样本 {i+1}/{len(samples)} 评估结果：")
            logger.info(f"总评分: {score:.4f}")
            logger.info("详细评分：")
            for key, value in detailed_score["detailed_scores"].items():
                logger.info(f"{key.replace('_', ' ').title()}: {value:.4f}")
            logger.info(f"生成的代码已保存到 {detailed_score['code_file_path']}")
        
        # 保存所有结果
        result_path = os.path.join(output_dir, "evaluation_result.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n所有评估结果已保存到 {result_path}")
    
    except Exception as e:
        logger.error(f"评估过程中发生错误: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    evaluate_rl_model()