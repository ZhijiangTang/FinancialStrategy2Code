import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class LocalQwenModelLoader:
    """
    本地 Qwen2.5-Coder-7B-Instruct 模型加载器
    """
    def __init__(self, model_path="/root/autodl-tmp/FinancialStrategy2Code/models/qwen2.5-coder-7b-instruct"):
        """
        初始化模型加载器
        
        参数:
            model_path: 本地模型路径
        """
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        
    def load_model(self):
        """
        加载本地模型和 tokenizer
        
        返回:
            tokenizer, model: 加载后的 tokenizer 和模型
        """
        print(f"正在从 {self.model_path} 加载模型...")
        
        # 加载 tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True
        )
        
        # 加载模型并启用混合精度（如果支持）
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        
        print("模型加载完成")
        return self.tokenizer, self.model
    
    def get_tokenizer_and_model(self):
        """
        获取 tokenizer 和模型实例
        
        返回:
            tokenizer, model: tokenizer 和模型
        """
        if self.tokenizer is None or self.model is None:
            return self.load_model()
        return self.tokenizer, self.model