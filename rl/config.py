import os
import argparse

class RLConfig:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "Qwen2.5-Coder-7B-Instruct"  # 确认模型名称
        self.learning_rate = 5e-5
        self.max_grad_norm = 1.0
        self.num_training_steps = 1000
        self.warmup_steps = 100
        self.logging_interval = 10
        self.evaluation_interval = 50
        self.checkpoint_interval = 100
        self.batch_size = 16
        self.gamma = 0.99  # 折扣因子
        self.epsilon = 0.1  # 探索率
        
        # PPO 强化学习参数
        self.ppo_config = {
            'batch_size': 4,                # 批次大小
            'forward_batch_size': 2,          # 前向传播批次大小
            'ppo_epochs': 4,                # PPO 训练轮数
            'learning_rate': 1e-5,           # 学习率
            'ratio_clip': 0.2,               # PPO ratio clip 参数
            'gae_lambda': 0.9,               # GAE lambda 参数
            'gamma': 0.99,                   # 折扣因子
            'entropy_coef': 0.01,             # 熵系数
            'value_loss_coef': 0.5,           # 价值损失系数
            'max_grad_norm': 1.0              # 最大梯度范数
        }
        
        # 数据集相关配置
        self.dataset_path = "./data_rl/merged_strategy_dataset.json"
        self.example_data_path = "./FinancialStrategy/example_paper.json"
        
        # 提示词模板（可被 GRPO 优化）
        self.prompt_template = (f"你是一个专业的金融量化交易系统开发者，请严格按照以下要求生成交易策略代码：\n"
                             f"- 使用标准 Python 编写\n"
                             f"- 函数命名规范（如 calculate_signal）\n"
                             f"- 包含必要的注释和文档字符串\n"
                             f"- 可执行性强、结构清晰\n"
                             f"- 避免使用不安全操作\n"
                             f"- 确保数值计算准确\n\n"
                             f"策略描述如下：\n{{strategy_description}}")
        
        # 日志路径
        self.log_dir = os.path.join("/root/autodl-tmp/FinancialStrategy2Code/rl/logs")
        
        # 输出与评估配置
        self.output_dir = "./output"
        self.eval_output_dir = "./evaluation_results"
        self.max_code_length = 2048  # 最大代码长度
        
        # 环境参数
        self.max_steps = 100  # 每个回合的最大步数
        
        # 设备配置
        self.device = "cuda" if torch.cuda.is_available() else "cpu"  # 使用的设备
        
        # 随机种子
        self.seed = 42  # 随机种子，确保实验可重复
        
        # 创建必要的目录
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.model_save_path), exist_ok=True)
    
    @classmethod
    def from_args(cls, args):
        """
        从命令行参数创建配置
        
        参数:
            args: 命令行参数
        """
        config = cls()
        
        # 如果提供了参数，覆盖配置中的相应值
        if hasattr(args, 'dataset_path') and args.dataset_path:
            config.dataset_path = args.dataset_path
        if hasattr(args, 'model_save_path') and args.model_save_path:
            config.model_save_path = args.model_save_path
        if hasattr(args, 'local_model_path') and args.local_model_path:
            config.local_model_path = args.local_model_path
        if hasattr(args, 'epochs') and args.epochs is not None:
            config.epochs = args.epochs
        if hasattr(args, 'model_name') and args.model_name:
            config.model_name = args.model_name
            config.model_save_path = os.path.join(config.model_base_path, config.model_name, "optimized_model.pth")
            config.local_model_path = os.path.join(config.model_base_path, config.model_name, "local_model.pth")
        if hasattr(args, 'batch_size') and args.batch_size is not None:
            config.batch_size = args.batch_size
        if hasattr(args, 'learning_rate') and args.learning_rate is not None:
            config.learning_rate = args.learning_rate
        if hasattr(args, 'beta') and args.beta is not None:
            config.beta = args.beta
        if hasattr(args, 'loss_type') and args.loss_type:
            config.loss_type = args.loss_type
        if hasattr(args, 'steps_per_epoch') and args.steps_per_epoch:
            config.steps_per_epoch = args.steps_per_epoch
        if hasattr(args, 'max_steps') and args.max_steps is not None:
            config.max_steps = args.max_steps
        if hasattr(args, 'epsilon_start') and args.epsilon_start is not None:
            config.epsilon_start = args.epsilon_start
        if hasattr(args, 'epsilon_end') and args.epsilon_end is not None:
            config.epsilon_end = args.epsilon_end
        if hasattr(args, 'epsilon_decay') and args.epsilon_decay is not None:
            config.epsilon_decay = args.epsilon_decay
        
        # 再次确保必要目录存在
        os.makedirs(config.log_dir, exist_ok=True)
        os.makedirs(os.path.dirname(config.model_save_path), exist_ok=True)
        
        return config
    
    @classmethod
    def get_parser(cls):
        """
        获取RL相关的命令行参数解析器
        """
        parser = argparse.ArgumentParser(description='强化学习配置参数')
        parser.add_argument('--dataset-path', type=str, default=None,
                          help=f'数据集路径（默认：{cls().dataset_path}）')
        parser.add_argument('--model-save-path', type=str, default=None,
                          help=f'模型保存路径（默认：{cls().model_save_path}）')
        parser.add_argument('--local-model-path', type=str, default=None,
                          help=f'本地模型路径（默认：{cls().local_model_path}）')
        parser.add_argument('--epochs', type=int, default=None,
                          help=f'训练轮数（默认：{cls().epochs}）')
        parser.add_argument('--batch-size', type=int, default=None,
                          help=f'批次大小（默认：{cls().batch_size}）')
        parser.add_argument('--learning-rate', '--lr', type=float, default=None,
                          help=f'学习率（默认：{cls().learning_rate}）')
        parser.add_argument('--beta', type=float, default=None,
                          help=f'KL 散度系数（默认：{cls().beta}）')
        parser.add_argument('--loss-type', type=str, default=None,
                          help=f'损失函数类型（默认：{cls().loss_type}）')
        parser.add_argument('--steps-per-epoch', type=int, default=None,
                          help=f'每个 epoch 的训练步数（默认：{cls().steps_per_epoch}）')
        parser.add_argument('--max-steps', type=int, default=None,
                          help=f'每个回合的最大步数（默认：{cls().max_steps}）')
        parser.add_argument('--epsilon-start', type=float, default=None,
                          help=f'初始探索率（默认：{cls().epsilon_start}）')
        parser.add_argument('--epsilon-end', type=float, default=None,
                          help=f'最终探索率（默认：{cls().epsilon_end}）')
        parser.add_argument('--epsilon-decay', type=float, default=None,
                          help=f'探索率衰减（默认：{cls().epsilon_decay}）')
        
        return parser