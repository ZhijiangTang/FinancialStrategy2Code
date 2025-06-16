import numpy as np
from typing import Tuple

def prepare_data(data: np.ndarray) -> Tuple[np.ndarray, int, int]:
    """
    准备强化学习所需的数据

    Args:
        data: 原始数据，形状为 (n_samples, n_features)

    Returns:
        features: 处理后的特征数据，形状为 (n_samples, lookback, n_features)
        state_size: 状态空间大小
        action_size: 动作空间大小
    """
    # 确保数据为numpy数组
    data = np.array(data, dtype=np.float32)
    
    # 标准化数据
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0) + 1e-8
    normalized_data = (data - mean) / std
    
    # 创建固定大小的时间窗口特征
    lookback = 10
    n_samples = len(normalized_data) - lookback
    n_features = normalized_data.shape[1]
    
    features = np.zeros((n_samples, lookback, n_features))
    for i in range(n_samples):
        features[i] = normalized_data[i:i+lookback]
    
    # 设置状态空间和动作空间大小
    state_size = lookback * n_features
    action_size = 3  # 买入、卖出、持有
    
    return features, state_size, action_size
