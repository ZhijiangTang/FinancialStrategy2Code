import numpy as np
from typing import Dict, List, Optional
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from collections import defaultdict

class FinancialStrategyAnalyzer:
    def __init__(self):
        self.strategy_patterns = defaultdict(list)
        self.risk_metrics = {}
        
    def load_strategy_dataset(self, dataset_path: str) -> None:
        """加载金融策略数据集"""
        with open(dataset_path) as f:
            self.strategies = json.load(f)
            
    def extract_strategy_patterns(self) -> Dict:
        """提取策略模式和特征"""
        for strategy in self.strategies:
            code = strategy['strategy_code']
            # 分析交易模式
            if 'while' in code:
                self.strategy_patterns['loop_trading'].append(strategy['strategy_id'])
            if 'RSI' in code or 'MACD' in code:
                self.strategy_patterns['technical_indicator'].append(strategy['strategy_id'])
            if 'ATR' in code:
                self.strategy_patterns['volatility_based'].append(strategy['strategy_id'])
                
        return self.strategy_patterns
        
    def analyze_risk_management(self, strategy_code: str) -> Dict:
        """分析策略的风险管理机制"""
        try:
            risk_features = {
                'has_stop_loss': False,
                'has_position_sizing': False,
                'has_leverage_control': False,
                'has_risk_metrics': False
            }
            
            if isinstance(strategy_code, str):
                # 检查止损机制
                if 'stop' in strategy_code.lower() or 'stoploss' in strategy_code.lower():
                    risk_features['has_stop_loss'] = True
                    
                # 检查仓位管理
                if 'position' in strategy_code.lower() or 'amount' in strategy_code.lower():
                    risk_features['has_position_sizing'] = True
                    
                # 检查杠杆控制
                if 'leverage' in strategy_code.lower():
                    risk_features['has_leverage_control'] = True
                    
                # 检查风险指标
                if 'risk' in strategy_code.lower() or 'drawdown' in strategy_code.lower():
                    risk_features['has_risk_metrics'] = True
            
            return risk_features
        except Exception as e:
            print(f"Error in analyze_risk_management: {str(e)}")
            return {
                'has_stop_loss': False,
                'has_position_sizing': False,
                'has_leverage_control': False,
                'has_risk_metrics': False,
                'error': str(e)
            }
        
    def detect_anomalies(self, returns: np.array) -> np.array:
        """检测策略回报中的异常值"""
        scaler = StandardScaler()
        normalized_returns = scaler.fit_transform(returns.reshape(-1, 1))
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        return iso_forest.fit_predict(normalized_returns)
        
    def calculate_risk_metrics(self, returns: np.array) -> Dict:
        """计算风险指标"""
        metrics = {
            'sharpe_ratio': None,
            'max_drawdown': None,
            'volatility': None,
            'var_95': None  # 95% Value at Risk
        }
        
        if len(returns) > 0:
            # 夏普比率
            risk_free_rate = 0.02  # 假设无风险利率为2%
            excess_returns = returns - risk_free_rate
            metrics['sharpe_ratio'] = np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0
            
            # 最大回撤
            cumulative_returns = np.cumsum(returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = cumulative_returns - running_max
            metrics['max_drawdown'] = np.min(drawdown)
            
            # 波动率
            metrics['volatility'] = np.std(returns)
            
            # 95% VaR
            metrics['var_95'] = np.percentile(returns, 5)
            
        return metrics
        
    def optimize_parameters(self, strategy_code: str, historical_data: pd.DataFrame) -> Dict:
        """优化策略参数"""
        # 这里使用简单的网格搜索示例
        param_grid = {
            'stop_loss': [0.01, 0.02, 0.03],
            'take_profit': [0.02, 0.03, 0.04],
            'position_size': [0.1, 0.2, 0.3]
        }
        
        best_params = {}
        best_sharpe = -np.inf
        
        for sl in param_grid['stop_loss']:
            for tp in param_grid['take_profit']:
                for ps in param_grid['position_size']:
                    # 在这里实现回测逻辑
                    returns = self._backtest(strategy_code, historical_data, sl, tp, ps)
                    if returns is not None:
                        sharpe = self.calculate_risk_metrics(returns)['sharpe_ratio']
                        if sharpe > best_sharpe:
                            best_sharpe = sharpe
                            best_params = {'stop_loss': sl, 'take_profit': tp, 'position_size': ps}
                            
        return best_params
        
    def _backtest(self, strategy_code: str, data: pd.DataFrame, sl: float, tp: float, ps: float) -> Optional[np.array]:
        """简单的回测框架"""
        try:
            returns = []
            position = 0
            for i in range(1, len(data)):
                # 简单的策略逻辑示例
                if position == 0:
                    if data['close'][i] > data['close'][i-1]:  # 上涨趋势
                        position = ps
                        entry_price = data['close'][i]
                elif position > 0:
                    # 检查止损和止盈
                    if data['close'][i] <= entry_price * (1 - sl):  # 止损
                        returns.append((data['close'][i] / entry_price - 1) * position)
                        position = 0
                    elif data['close'][i] >= entry_price * (1 + tp):  # 止盈
                        returns.append((data['close'][i] / entry_price - 1) * position)
                        position = 0
                        
            return np.array(returns)
        except Exception as e:
            print(f"Backtest error: {str(e)}")
            return None
            
    def generate_reinforcement_learning_features(self, strategy_code: str) -> Dict:
        """生成强化学习特征"""
        features = {
            'state_space': [],
            'action_space': [],
            'reward_signals': []
        }
        
        # 分析状态空间
        if 'price' in strategy_code.lower():
            features['state_space'].append('price')
        if 'volume' in strategy_code.lower():
            features['state_space'].append('volume')
        if 'volatility' in strategy_code.lower() or 'atr' in strategy_code.lower():
            features['state_space'].append('volatility')
            
        # 分析动作空间
        if 'buy' in strategy_code.lower() or 'long' in strategy_code.lower():
            features['action_space'].append('long')
        if 'sell' in strategy_code.lower() or 'short' in strategy_code.lower():
            features['action_space'].append('short')
            
        # 分析奖励信号
        if 'profit' in strategy_code.lower():
            features['reward_signals'].append('profit')
        if 'drawdown' in strategy_code.lower():
            features['reward_signals'].append('drawdown')
            
        return features
