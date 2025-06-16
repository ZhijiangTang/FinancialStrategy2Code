import pandas as pd
import numpy as np
from typing import List, Dict, Any
import yfinance as yf
import ccxt

class FinancialDataProcessor:
    """金融数据处理器，用于处理和准备金融数据"""
    
    def __init__(self):
        self.supported_exchanges = {
            'binance': ccxt.binance(),
            'okex': ccxt.okex()
        }
        
    def fetch_market_data(self, 
                         symbol: str,
                         timeframe: str,
                         start_date: str,
                         end_date: str,
                         source: str = 'binance') -> pd.DataFrame:
        """获取市场数据"""
        if source.lower() in self.supported_exchanges:
            return self._fetch_crypto_data(symbol, timeframe, start_date, end_date, source)
        else:
            return self._fetch_stock_data(symbol, start_date, end_date)
            
    def _fetch_crypto_data(self,
                          symbol: str,
                          timeframe: str,
                          start_date: str,
                          end_date: str,
                          exchange: str) -> pd.DataFrame:
        """获取加密货币市场数据"""
        exchange = self.supported_exchanges[exchange.lower()]
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
        
    def _fetch_stock_data(self,
                         symbol: str,
                         start_date: str,
                         end_date: str) -> pd.DataFrame:
        """获取股票市场数据"""
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        return df
        
    def calculate_indicators(self, df: pd.DataFrame, indicators: List[Dict[str, Any]]) -> pd.DataFrame:
        """计算技术指标"""
        for indicator in indicators:
            indicator_type = indicator['type']
            params = indicator.get('params', {})
            
            if indicator_type == 'MA':
                period = params.get('period', 20)
                df[f'MA_{period}'] = df['close'].rolling(window=period).mean()
                
            elif indicator_type == 'RSI':
                period = params.get('period', 14)
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
                
            elif indicator_type == 'MACD':
                fast = params.get('fast', 12)
                slow = params.get('slow', 26)
                signal = params.get('signal', 9)
                
                exp1 = df['close'].ewm(span=fast, adjust=False).mean()
                exp2 = df['close'].ewm(span=slow, adjust=False).mean()
                macd = exp1 - exp2
                signal_line = macd.ewm(span=signal, adjust=False).mean()
                
                df[f'MACD_{fast}_{slow}'] = macd
                df[f'MACD_Signal_{signal}'] = signal_line
                df[f'MACD_Histogram'] = macd - signal_line
                
        return df
        
    def prepare_backtest_data(self,
                             df: pd.DataFrame,
                             features: List[str],
                             target: str,
                             train_ratio: float = 0.8) -> tuple:
        """准备回测数据"""
        X = df[features]
        y = df[target]
        
        train_size = int(len(df) * train_ratio)
        
        X_train = X[:train_size]
        X_test = X[train_size:]
        y_train = y[:train_size]
        y_test = y[train_size:]
        
        return (X_train, X_test, y_train, y_test)
        
    def normalize_data(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """数据标准化"""
        for col in columns:
            mean = df[col].mean()
            std = df[col].std()
            df[f'{col}_normalized'] = (df[col] - mean) / std
        return df
