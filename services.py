"""
Stock Analysis Services
"""
import requests
import pandas as pd
from FinMind.data import DataLoader
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.stats import norm


class FinMindService:
    """Responsible for FinMind API stock price fetching"""
    
    def __init__(self, token: str):
        self.token = token
        self.finmind = DataLoader()
        self.finmind.login_by_token(api_token=token)
    
    def get_stock_id(self, stock_name: str) -> str | None:
        """
        Convert stock name to stock ID
        Returns stock_id directly if input is numeric
        """
        if stock_name.isdigit():
            return stock_name
        
        url = "https://api.finmindtrade.com/api/v4/data"
        payload = {"dataset": "TaiwanStockInfo", "token": self.token}
        try:
            data = requests.get(url, params=payload).json()
            for stock in data["data"]:
                if stock["stock_name"] == stock_name:
                    return stock["stock_id"]
        except:
            return None
        return None
    
    def fetch_data(self, ticker: str) -> pd.DataFrame | None:
        """
        Fetch historical stock data from FinMind API
        Returns last 3.5 years of daily data
        """
        end = datetime.today().strftime('%Y-%m-%d')
        start = (datetime.today() - timedelta(days=int(3.5 * 365))).strftime('%Y-%m-%d')
        try:
            df = self.finmind.taiwan_stock_daily(stock_id=ticker, start_date=start, end_date=end)
            return df if not df.empty else None
        except:
            return None


class LohasService:
    """Responsible for LOHAS 5-Lines and Channel analysis calculations"""
    
    @staticmethod
    def prepare_data(stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare and clean stock data
        Converts date to datetime index and adds ordinal column for regression
        """
        df = stock_data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df[df['close'] != 0].dropna()
        df['Date_ordinal'] = df.index.map(datetime.toordinal)
        return df
    
    @staticmethod
    def calculate_five_lines(stock_data: pd.DataFrame) -> dict:
        """
        Calculate 5-Lines (五線譜) analysis
        Uses Linear Regression with standard deviation bands (±1SD, ±2SD)
        """
        X = stock_data['Date_ordinal'].values.reshape(-1, 1)
        Y = stock_data['close'].values
        model = LinearRegression().fit(X, Y)
        stock_data['LR'] = model.predict(X)
        std_lr = (stock_data['close'] - stock_data['LR']).std()
        z69, z95 = norm.ppf((1 + 0.69) / 2), norm.ppf((1 + 0.95) / 2)
        
        return {
            'data': stock_data,
            'std': std_lr,
            'z69': z69,
            'z95': z95,
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
        """
        Calculate LOHAS Channel (通道) analysis
        Uses 100-day moving average with 2 standard deviation bands
        """
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
