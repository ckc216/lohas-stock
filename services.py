"""
Stock Analysis Services
"""
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.stats import norm
import os
import time


class YFinanceService:
    """Responsible for yfinance stock price fetching"""
    
    def __init__(self):
        self.ticker_df = None
        self._load_ticker_data()

    def _load_ticker_data(self):
        """Load stock ticker mapping from local CSV"""
        csv_path = os.path.join('data', 'stock_ticker.csv')
        if os.path.exists(csv_path):
            try:
                self.ticker_df = pd.read_csv(csv_path)
                self.ticker_df['代號'] = self.ticker_df['代號'].astype(str)
            except Exception as e:
                print(f"Error loading ticker data: {e}")
    
    def get_stock_info(self, target: str) -> dict | None:
        """
        Lookup stock ID and market info
        Returns: {'id': '2330', 'market': '上市'} or None
        """
        if self.ticker_df is None:
            return None
            
        # Try lookup by ID or Name
        if target.isdigit():
            match = self.ticker_df[self.ticker_df['代號'] == target]
        else:
            match = self.ticker_df[self.ticker_df['名稱'] == target]
            
        if not match.empty:
            return {
                'id': match.iloc[0]['代號'],
                'market': match.iloc[0]['market']
            }
        return None
    
    def fetch_data(self, ticker: str, market: str = None) -> pd.DataFrame | None:
        """
        Fetch historical stock data with smart suffix detection
        """
        start = (datetime.today() - timedelta(days=int(3.5 * 365))).strftime('%Y-%m-%d')
        max_retries = 3
        
        # Determine suffix based on market
        if market == '上市':
            suffixes = ['.TW']
        elif market == '上櫃':
            suffixes = ['.TWO']
        else:
            # Fallback if market unknown
            suffixes = ['.TW', '.TWO']
            
        for suffix in suffixes:
            full_ticker = f"{ticker}{suffix}"
            for attempt in range(max_retries):
                try:
                    # Fetching data
                    ticker_obj = yf.Ticker(full_ticker)
                    df = ticker_obj.history(start=start, auto_adjust=False)
                    
                    if not df.empty:
                        df = df.reset_index()
                        df.rename(columns={
                            'Date': 'date', 'Open': 'open', 'High': 'high', 
                            'Low': 'low', 'Close': 'close', 'Volume': 'Trading_Volume'
                        }, inplace=True)
                        
                        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                        df['stock_id'] = ticker
                        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].round(2)
                        return df[['date', 'stock_id', 'Trading_Volume', 'open', 'high', 'low', 'close']]
                    else:
                        break # Try next suffix or exit
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)
        return None


class LohasService:
    """Responsible for LOHAS 5-Lines and Channel analysis calculations"""
    
    @staticmethod
    def prepare_data(stock_data: pd.DataFrame) -> pd.DataFrame:
        df = stock_data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df[df['close'] != 0].dropna()
        df['Date_ordinal'] = df.index.map(datetime.toordinal)
        return df
    
    @staticmethod
    def calculate_five_lines(stock_data: pd.DataFrame) -> dict:
        X = stock_data['Date_ordinal'].values.reshape(-1, 1)
        Y = stock_data['close'].values
        model = LinearRegression().fit(X, Y)
        stock_data['LR'] = model.predict(X)
        std_lr = (stock_data['close'] - stock_data['LR']).std()
        z69, z95 = norm.ppf((1 + 0.69) / 2), norm.ppf((1 + 0.95) / 2)
        
        return {
            'data': stock_data, 'std': std_lr, 'z69': z69, 'z95': z95,
            'lines': {
                '+2SD': stock_data['LR'] + z95 * std_lr,
                '+1SD': stock_data['LR'] + z69 * std_lr,
                '-1SD': stock_data['LR'] - z69 * std_lr,
                '-2SD': stock_data['LR'] - z95 * std_lr,
                'Trend': stock_data['LR'],
            }
        }
    
    @staticmethod
    def calculate_channel(stock_data: pd.DataFrame) -> dict:
        stock_data['MA100'] = stock_data['close'].rolling(window=100).mean()
        stock_data['MA100_std'] = stock_data['close'].rolling(window=100).std()
        return {
            'data': stock_data,
            'lines': {
                'Top': stock_data['MA100'] + 2 * stock_data['MA100_std'],
                'Bottom': stock_data['MA100'] - 2 * stock_data['MA100_std'],
                '20W MA': stock_data['MA100'],
            }
        }
