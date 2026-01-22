"""
Stock Analysis Services
"""
import requests
import pandas as pd
import yfinance as yf
import sqlite3
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
        Lookup stock ID and market info.
        If not in CSV but input is numeric, returns ID with None market.
        """
        if self.ticker_df is not None:
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
        
        # Fallback: If input is numeric but not in CSV, allow it with unknown market
        if target.isdigit():
            return {
                'id': target,
                'market': None
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

    def get_all_scores(self) -> pd.DataFrame:
        """Fetch all calculated scores from SQLite database"""
        db_path = os.path.join('data', 'financial_scores.db')
        if not os.path.exists(db_path):
            return pd.DataFrame()
            
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM stock_price_trend_lines", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error reading database: {e}")
            return pd.DataFrame()


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

    @staticmethod
    def get_lohas_level(price: float, lines: dict) -> int:
        """
        Calculate Lohas Score (1-6) based on current price relative to bands:
        1: < -2SD
        2: [-2SD, -1SD)
        3: [-1SD, Trend)
        4: [Trend, +1SD)
        5: [+1SD, +2SD)
        6: >= +2SD
        """
        trend = lines['Trend'].iloc[-1]
        p1sd = lines['+1SD'].iloc[-1]
        p2sd = lines['+2SD'].iloc[-1]
        m1sd = lines['-1SD'].iloc[-1]
        m2sd = lines['-2SD'].iloc[-1]

        if price < m2sd:
            return 1
        elif price < m1sd:
            return 2
        elif price < trend:
            return 3
        elif price < p1sd:
            return 4
        elif price < p2sd:
            return 5
        else:
            return 6


class EconomyService:
    """Service to fetch global economic indicators like CNN Fear & Greed Index"""
    
    # Updated working endpoint for graph and current data
    CNN_GRAPH_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.cnn.com/markets/fear-and-greed'
    }

    @staticmethod
    def fetch_fear_greed_index() -> dict | None:
        """Fetch CNN Fear & Greed Index data"""
        try:
            # Fetch data from roughly 1 year ago
            start_date = (datetime.today() - timedelta(days=366)).strftime('%Y-%m-%d')
            url = f"{EconomyService.CNN_GRAPH_URL}{start_date}"
            
            response = requests.get(url, headers=EconomyService.HEADERS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Extract main components
                fear_greed = data.get('fear_and_greed', {})
                historical = data.get('fear_and_greed_historical', {}).get('data', [])
                
                # Format historical data for Plotly
                df_history = pd.DataFrame(historical)
                if not df_history.empty:
                    df_history['x'] = pd.to_datetime(df_history['x'], unit='ms')
                    df_history.rename(columns={'x': 'date', 'y': 'score'}, inplace=True)
                    df_history = df_history.sort_values('date')

                return {
                    'current_score': fear_greed.get('score', 0),
                    'current_rating': fear_greed.get('rating', 'Neutral').title(),
                    'last_updated': fear_greed.get('timestamp', ''),
                    'previous_close': fear_greed.get('previous_close', 0),
                    'previous_1_week': fear_greed.get('previous_1_week', 0),
                    'previous_1_month': fear_greed.get('previous_1_month', 0),
                    'previous_1_year': fear_greed.get('previous_1_year', 0),
                    'historical_data': df_history
                }
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
        return None
