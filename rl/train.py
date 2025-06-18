import os
import argparse
import logging
from config import RLConfig
from strategy_rl import StrategyRL
from dataset import StrategyDataset


def main():
    try:
        # 解析命令行参数
        args = parse_args()
        
        # 初始化配置
        config = RLConfig()
        
        # 创建策略 RL 实例
        strategy_rl = StrategyRL(model_name=config.model_name)
        
        # 如果指定了预训练模型路径，则加载模型
        if args.model_path and os.path.exists(args.model_path):
            strategy_rl.load_model(args.model_path)
            print(f"模型已加载 from {args.model_path}")
        
        # 加载数据集
        dataset_loader = StrategyDataset()
        raw_dataset = dataset_loader.load_dataset()
        
        # 开始训练
        print("开始训练...")
        strategy_rl.train(raw_dataset)
        
        # 保存最终模型
        strategy_rl.save_model(config.model_save_path)
        print(f"训练完成，模型已保存到 {config.model_save_path}")
    
    except Exception as e:
        logging.error(f"训练过程中发生错误: {e}", exc_info=True)


def train_rl_model():
    """
    训练强化学习模型（实际上是提示词优化）
    """
    # 初始化日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # 创建输出目录
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化配置
        config = RLConfig()
        
        # 加载数据集
        dataset_loader = StrategyDataset()
        raw_dataset = dataset_loader.load_dataset()
        
        # 初始化策略 RL 系统
        strategy_rl = StrategyRL()
        
        logger.info("开始使用 PPO 算法微调模型...")
        
        # 执行微调
        strategy_rl.fine_tune(raw_dataset, output_dir)
        
        logger.info(f"训练完成，最佳模型已保存到 {output_dir}")
    
    except Exception as e:
        logger.error(f"训练过程中发生错误: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    train_rl_model()