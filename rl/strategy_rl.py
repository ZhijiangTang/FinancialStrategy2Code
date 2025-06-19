import torch
import logging
from model import StrategyModel
from environment import StrategyEnvironment
from utils import score_module

class StrategyRL:
    """
    金融策略生成的强化学习系统
    """
    def __init__(self, model_name="Qwen/Qwen2.5-Coder-7B-Instruct", local_files_only=True):
        """
        初始化强化学习系统
        
        参数:
            model_name: 模型名称
            local_files_only: 是否仅使用本地文件
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.local_files_only = local_files_only
        
        # 初始化模型和分词器
        self.tokenizer, self.model = self._load_local_model()
        
    def _load_local_model(self):
        """
        从本地路径加载模型和分词器
        
        返回:
            tokenizer, model: 加载后的 tokenizer 和模型
        """
        try:
            # 修改模型路径为实际路径
            model_path = "/root/autodl-tmp/FinancialStrategy2Code/rl/models/Qwen2.5-Coder-7B-Instruct"
            
            # 加载分词器
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            
            # 加载模型
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True
            )
            
            self.logger.info(f"成功加载本地模型 {model_path}")
            return tokenizer, model
    
        except Exception as e:
            self.logger.error(f"加载本地模型失败: {e}", exc_info=True)
            raise
    
    def fine_tune(self, dataset: Dataset, output_dir: str = "./output") -> None:
        try:
            # 创建 PPO 配置
            ppo_config = PPOConfig(
                model_name=self.model_name,
                batch_size=4,
                forward_batch_size=2,
                ppo_epochs=4,
                learning_rate=1e-5,
                ratio_clip=0.2,
                gae_lambda=0.9,
                gamma=0.99,
                entropy_coef=0.01,
                value_loss_coef=0.5,
                max_grad_norm=1.0
            )
            
            # 创建 PPO 训练器
            ppo_trainer = PPOTrainer(
                config=ppo_config,
                model=self.model,
                ref_model=None,  # 使用默认参考模型
                tokenizer=self.tokenizer
            )
            
            # 开始训练
            self.logger.info("开始使用 PPO 算法微调模型...")
            ppo_trainer.train(dataset)
            
            # 保存优化后的模型
            os.makedirs(output_dir, exist_ok=True)
            ppo_trainer.save_model(output_dir)
            self.logger.info(f"模型已保存到 {output_dir}")
        
        except Exception as e:
            self.logger.error(f"模型微调过程中发生错误: {e}", exc_info=True)
            raise

    def train(self, dataset: Dataset):
        """
        执行微调过程

        参数:
            dataset: 训练数据集
        """
        try:
            # 开始训练
            self.ppo_trainer.train(dataset)
            
            # 保存优化后的模型
            os.makedirs(self.config.output_dir, exist_ok=True)
            self.ppo_trainer.save_model(self.config.output_dir)
            self.logger.info(f"模型已保存到 {self.config.output_dir}")
        except Exception as e:
            self.logger.error(f"模型微调过程中发生错误: {e}", exc_info=True)
            raise

    def generate_code(self, strategy_description: str) -> str:
        """
        根据策略描述生成交易策略代码

        参数:
            strategy_description: 策略描述文本

        返回:
            generated_code: 生成的代码
        """
        try:
            # 构建输入提示
            prompt = (f"你是一个专业的金融量化交易系统开发者，请严格按照以下要求生成交易策略代码：\n"
                     f"- 使用标准 Python 编写\n"
                     f"- 函数命名规范（如 calculate_signal）\n"
                     f"- 包含必要的注释和文档字符串\n"
                     f"- 可执行性强、结构清晰\n"
                     f"- 避免使用不安全操作\n"
                     f"- 确保数值计算准确\n\n"
                     f"策略描述如下：\n{strategy_description}")
            
            # 编码输入
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            # 生成代码
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.95,
                do_sample=True
            )
            
            # 解码输出
            generated_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return generated_code
        
        except Exception as e:
            self.logger.error(f"代码生成过程中发生错误: {e}", exc_info=True)
            raise

    def _calculate_rewards(self, strategy_descriptions, generated_codes):
        """
        使用评估适配器生成奖励值
        
        参数:
            strategy_descriptions: 策略描述列表
            generated_codes: 生成的代码列表
        
        返回:
            rewards: 奖励值列表
        """
        # 初始化评分模块
        score_module = ScoreModule()
        
        # 执行批量评估
        scores = []
        for desc, code in zip(strategy_descriptions, generated_codes):
            score = score_module.score(code, desc)
            scores.append(score)
        
        return scores
