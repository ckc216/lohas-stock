import sqlite3
import pandas as pd
import os
import time
import random
from datetime import datetime
from tqdm import tqdm
from services import YFinanceService, LohasService, SQLiteHandler

def run_score_scraper():
    # Configuration
    db_path = os.path.join('data', 'financial_scores.db')
    ticker_csv = os.path.join('data', 'stock_ticker.csv')
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    if not os.path.exists(ticker_csv):
        print(f"Error: {ticker_csv} not found.")
        return

    # Load tickers
    tickers_df = pd.read_csv(ticker_csv)
    tickers_df['代號'] = tickers_df['代號'].astype(str)
    
    yf_service = YFinanceService()
    db_handler = SQLiteHandler(db_path)
    
    results = []
    failed_stocks = []
    
    print(f"Starting score calculation for {len(tickers_df)} stocks...")
    
    # Process stocks with progress bar
    for _, row in tqdm(tickers_df.iterrows(), total=len(tickers_df), desc="Processing"):
        sid = row['代號']
        sname = row['名稱']
        market = row['market']
        
        # Add a small random delay to prevent rate limiting
        time.sleep(random.uniform(0.2, 0.5))
        
        try:
            # Fetch data (YFinanceService has internal retry)
            df = yf_service.fetch_data(sid, market)
            
            if df is not None and len(df) > 100: # Need enough data for regression
                # Calculate Five Lines
                clean_df = LohasService.prepare_data(df)
                analysis = LohasService.calculate_five_lines(clean_df)
                
                # Get latest price and score
                latest_price = clean_df['close'].iloc[-1]
                level = LohasService.get_lohas_level(latest_price, analysis['lines'])
                
                # Prepare row for DB
                # Schema: stock_id, date, stock_name, level, close_price, u2sd, u1sd, trend, l1sd, l2sd
                lines = analysis['lines']
                results.append((
                    sid, today_str, sname, level, latest_price,
                    round(lines['+2SD'].iloc[-1], 2), 
                    round(lines['+1SD'].iloc[-1], 2),
                    round(lines['Trend'].iloc[-1], 2), 
                    round(lines['-1SD'].iloc[-1], 2),
                    round(lines['-2SD'].iloc[-1], 2)
                ))
                
                # Batch save every 50 records
                if len(results) >= 50:
                    db_handler.save_scores(results)
                    results = []
            else:
                failed_stocks.append(f"{sid} {sname}: Insufficient data or fetch failed")
                
        except Exception as e:
            failed_stocks.append(f"{sid} {sname}: Error {str(e)}")

    # Final save for remaining records
    if results:
        db_handler.save_scores(results)

    # Logging
    print("\n" + "="*30)
    print(f"Scraping completed on {today_str}")
    print(f"Successfully processed: {len(tickers_df) - len(failed_stocks)}")
    print(f"Failed: {len(failed_stocks)}")
    
    if failed_stocks:
        print("\nFailed Stocks Log:")
        for log in failed_stocks:
            print(log)
    print("="*30)

if __name__ == "__main__":
    run_score_scraper()
