import sys
import os
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from finance.strategy_processor import FinanceStrategyProcessor
from finance.data_utils import FinancialDataProcessor
from finance.rl_optimizer import RLOptimizer, StrategyValidator

class FinanceStrategyAdapter:
    """适配器类，用于将金融策略功能集成到现有的paper2code系统中"""
    
    def __init__(self, strategy_dataset_path: str, config: Dict[str, Any]):
        self.strategy_processor = FinanceStrategyProcessor(strategy_dataset_path)
        self.data_processor = FinancialDataProcessor()
        self.rl_optimizer = RLOptimizer(config)
        self.validator = StrategyValidator(config)
        
    def enhance_planning(self, paper_content: str) -> Dict[str, Any]:
        """增强规划阶段，添加金融策略特定的分析"""
        # 使用金融策略处理器分析论文
        strategy_analysis = self.strategy_processor.enhance_paper_analysis(paper_content)
        
        # 提取交易需求
        backtest_requirements = strategy_analysis['backtest_requirements']
        
        # 获取回测数据
        market_data = self.data_processor.fetch_market_data(
            symbol=backtest_requirements['markets'][0],
            timeframe=backtest_requirements['timeframe'],
            start_date=backtest_requirements['start_date'],
            end_date=backtest_requirements['end_date']
        )
        
        # 计算技术指标
        indicators = [{'type': ind} for ind in strategy_analysis.get('trading_components', [])]
        processed_data = self.data_processor.calculate_indicators(market_data, indicators)
        
        # 使用强化学习优化策略参数
        env = self.rl_optimizer.create_env({'close': processed_data['close'].values})
        self.rl_optimizer.train(env)
        
        return {
            'strategy_analysis': strategy_analysis,
            'market_data': processed_data,
            'optimized_params': self.rl_optimizer.optimize_strategy({
                'stop_loss': 0.02,
                'take_profit': 0.04
            })
        }
        
    def enhance_analysis(self, paper_content: str, planning_output: Dict[str, Any]) -> Dict[str, Any]:
        """增强分析阶段，添加金融策略特定的分析"""
        strategy_info = self.strategy_processor.preprocess_strategy(paper_content)
        
        return {
            'trading_type': strategy_info['trading_type'],
            'market': strategy_info['market'],
            'timeframe': strategy_info['timeframe'],
            'indicators': strategy_info['indicators'],
            'risk_management': planning_output['strategy_analysis']['risk_management'],
            'optimized_params': planning_output['optimized_params']
        }
        
    def enhance_coding(self, analysis_output: Dict[str, Any]) -> str:
        """增强代码生成阶段，生成金融策略特定的代码"""
        strategy_template = """
import ccxt
import pandas as pd
import numpy as np
from typing import Dict, Any

class TradingStrategy:
    def __init__(self, config: Dict[str, Any]):
        self.exchange = getattr(ccxt, config['exchange'])({
            'apiKey': config['api_key'],
            'secret': config['api_secret']
        })
        self.symbol = config['symbol']
        self.timeframe = config['timeframe']
        self.stop_loss = config['stop_loss']
        self.take_profit = config['take_profit']
        
    def setup_indicators(self):
        \"\"\"设置技术指标\"\"\"
        {indicator_setup}
        
    def get_position(self) -> float:
        \"\"\"获取当前持仓\"\"\"
        try:
            position = self.exchange.fetch_position(self.symbol)
            return float(position['size'])
        except:
            return 0.0
            
    def place_order(self, side: str, amount: float):
        \"\"\"下单\"\"\"
        try:
            order = self.exchange.create_order(
                symbol=self.symbol,
                type='market',
                side=side,
                amount=amount
            )
            return order
        except Exception as e:
            print(f"下单失败: {e}")
            return None
            
    def on_bar(self, data: pd.DataFrame) -> Dict[str, Any]:
        \"\"\"策略主逻辑\"\"\"
        {strategy_logic}
        
    def run(self):
        \"\"\"运行策略\"\"\"
        while True:
            try:
                # 获取市场数据
                ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # 运行策略
                signals = self.on_bar(df)
                
                # 执行交易
                current_position = self.get_position()
                if signals['action'] == 'buy' and current_position <= 0:
                    self.place_order('buy', signals['amount'])
                elif signals['action'] == 'sell' and current_position >= 0:
                    self.place_order('sell', signals['amount'])
                    
            except Exception as e:
                print(f"策略运行错误: {e}")
                continue
"""
        
        # 生成指标设置代码
        indicator_setup = self._generate_indicator_setup(analysis_output['indicators'])
        
        # 生成策略逻辑代码
        strategy_logic = self._generate_strategy_logic(
            analysis_output['trading_type'],
            analysis_output['optimized_params']
        )
        
        return strategy_template.format(
            indicator_setup=indicator_setup,
            strategy_logic=strategy_logic
        )
        
    def _generate_indicator_setup(self, indicators: List[str]) -> str:
        """生成指标设置代码"""
        setup_code = []
        for indicator in indicators:
            if indicator == 'MA':
                setup_code.append("""
        self.ma_period = 20
        df['MA'] = df['close'].rolling(window=self.ma_period).mean()""")
            elif indicator == 'RSI':
                setup_code.append("""
        self.rsi_period = 14
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))""")
                
        return '\n'.join(setup_code)
        
    def _generate_strategy_logic(self, trading_type: str, params: Dict[str, Any]) -> str:
        """生成策略逻辑代码"""
        return f"""
        # 获取当前价格和指标值
        current_price = data['close'].iloc[-1]
        
        # 计算信号
        signal = {{'action': None, 'amount': 0.0}}
        
        # 执行风险管理
        position = self.get_position()
        if position > 0:
            if current_price <= position_price * (1 - {params['stop_loss']}):
                signal['action'] = 'sell'
                signal['amount'] = abs(position)
            elif current_price >= position_price * (1 + {params['take_profit']}):
                signal['action'] = 'sell'
                signal['amount'] = abs(position)
        
        return signal"""
