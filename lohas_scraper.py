import sqlite3
import pandas as pd
import os
import time
import random
from datetime import datetime
from tqdm import tqdm
from services import YFinanceService, LohasService, SQLiteHandler, DB_PATH

def run_score_scraper():
    # Configuration
    ticker_csv = os.path.join('data', 'stock_ticker.csv')
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    if not os.path.exists(ticker_csv):
        print(f"Error: {ticker_csv} not found.")
        return

    # Load tickers
    tickers_df = pd.read_csv(ticker_csv)
    tickers_df['代號'] = tickers_df['代號'].astype(str)
    
    yf_service = YFinanceService()
    db_handler = SQLiteHandler(DB_PATH)
    
    results = []
    failed_stocks = []
    
    print(f"Starting score calculation for {len(tickers_df)} stocks...")
    
    for _, row in tqdm(tickers_df.iterrows(), total=len(tickers_df), desc="Processing"):
        sid = row['代號']
        sname = row['名稱']
        market = row['market']
        time.sleep(random.uniform(0.1, 0.3))
        
        try:
            df = yf_service.fetch_data(sid, market)
            if df is not None and len(df) > 100:
                clean_df = LohasService.prepare_data(df)
                analysis = LohasService.calculate_five_lines(clean_df)
                latest_price = clean_df['close'].iloc[-1]
                level = LohasService.get_lohas_level(latest_price, analysis['lines'])
                lines = analysis['lines']
                results.append((
                    sid, today_str, sname, level, latest_price,
                    round(lines['+2SD'].iloc[-1], 2), round(lines['+1SD'].iloc[-1], 2),
                    round(lines['Trend'].iloc[-1], 2), round(lines['-1SD'].iloc[-1], 2),
                    round(lines['-2SD'].iloc[-1], 2)
                ))
                if len(results) >= 50:
                    db_handler.save_scores(results); results = []
            else: failed_stocks.append(f"{sid} {sname}: Insufficient data or fetch failed")
        except Exception as e: failed_stocks.append(f"{sid} {sname}: Error {str(e)}")

    if results: db_handler.save_scores(results)
    print("\n" + "="*30)
    print(f"Scraping completed on {today_str}")
    print(f"Successfully processed: {len(tickers_df) - len(failed_stocks)}")
    print(f"Failed: {len(failed_stocks)}")
    print("="*30)

if __name__ == "__main__":
    run_score_scraper()