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


class SQLiteHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 建立股價趨勢線資料表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_price_trend_lines (
            stock_id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            stock_name TEXT,
            level REAL,
            close_price REAL,
            upper_2sd REAL,
            upper_1sd REAL,
            trend_line REAL,
            lower_1sd REAL,
            lower_2sd REAL
        );
        """)
        
        # 建立財務評價資料表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_financial_scores (
            stock_id TEXT NOT NULL,
            stock_name TEXT,
            上市櫃日期 TEXT,
            產業類別 TEXT,
            財報季度 TEXT,
            營收月份 TEXT,
            營收年增率 REAL,
            營業利益率 REAL,
            稅後淨利年增率 REAL,
            每股盈餘EPS REAL,
            存貨周轉率 TEXT,
            自由現金流量 REAL,
            本期綜合評分 REAL,
            綜合評分變化 REAL,
            UNIQUE (stock_id, 營收月份)
        );
        """)
        conn.commit()
        conn.close()

    def save_scores(self, data_list):
        """Batch save scores to database using REPLACE (Upsert)"""
        if not data_list: return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        sql = "REPLACE INTO stock_price_trend_lines VALUES (?,?,?,?,?,?,?,?,?,?)"
        try:
            cursor.executemany(sql, data_list)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def save_financial_scores(self, data_list):
        """Batch save financial scores using INSERT OR IGNORE"""
        if not data_list: return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        sql = """
        REPLACE INTO stock_financial_scores (
            stock_id, stock_name, 上市櫃日期, 產業類別, 財報季度, 營收月份,
            營收年增率, 營業利益率, 稅後淨利年增率, 每股盈餘EPS,
            存貨周轉率, 自由現金流量, 本期綜合評分, 綜合評分變化
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor.executemany(sql, data_list)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error (Financial Scores): {e}")
        finally:
            conn.close()

    def get_financial_history(self, stock_id: str) -> pd.DataFrame:
        """Fetch historical financial scores for a specific stock"""
        conn = sqlite3.connect(self.db_path)
        try:
            query = "SELECT * FROM stock_financial_scores WHERE stock_id = ? ORDER BY 營收月份 DESC"
            df = pd.read_sql_query(query, conn, params=(str(stock_id),))
            return df
        except Exception as e:
            print(f"Error fetching financial history: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def get_financial_overview(self) -> pd.DataFrame:
        """Fetch the latest financial scores and lohas levels for all stocks"""
        conn = sqlite3.connect(self.db_path)
        try:
            # 使用 ROW_NUMBER() 取得每檔股票最新的一筆財報資料，並 JOIN 樂活等級
            query = """
            WITH LatestFinancials AS (
                SELECT *,
                       ROW_NUMBER() OVER (PARTITION BY stock_id ORDER BY 營收月份 DESC) as rn
                FROM stock_financial_scores
            )
            SELECT 
                f.stock_id AS 代號,
                f.stock_name AS 名稱,
                f.產業類別 AS 產業,
                f.上市櫃日期 AS 上市日期,
                f.財報季度 AS 財報季度,
                f.營收月份 AS 營收月份,
                f.本期綜合評分 AS 總分,
                l.level AS 樂活五線譜,
                f.營收年增率 AS 月營收評分,
                f.營業利益率 AS 營業利益率評分,
                f.稅後淨利年增率 AS 淨利成長評分,
                f.每股盈餘EPS AS EPS評分,
                f.存貨周轉率 AS 存貨周轉率評分,
                f.自由現金流量 AS 自由現金流量評分
            FROM LatestFinancials f
            LEFT JOIN stock_price_trend_lines l ON f.stock_id = l.stock_id
            WHERE f.rn = 1
            ORDER BY f.stock_id ASC
            """
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            print(f"Error fetching financial overview: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

