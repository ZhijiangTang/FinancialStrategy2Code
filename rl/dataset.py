import json
import os
from .config import RLConfig
from datasets import Dataset

class StrategyDataset:
    """
    策略数据集加载和处理
    """
    def __init__(self, dataset_path=None):
        """
        初始化数据集处理器
        
        参数:
            dataset_path: 数据集路径
        """
        self.config = RLConfig()
        self.dataset_path = dataset_path or self.config.dataset_path
    
    def load_dataset(self):
        """
        加载并返回训练数据集
        
        返回:
            raw_dataset: 原始数据集
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"数据集文件不存在: {self.dataset_path}")
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        // 确保数据格式正确
        for item in data:
            if 'strategy_description' not in item:
                item['strategy_description'] = item.get('strategy', '')
            if 'code' not in item:
                item['code'] = item.get('code', '')
        
        return Dataset.from_list(data)
