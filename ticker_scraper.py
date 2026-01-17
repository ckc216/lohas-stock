import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import os

def run_scraper():
    """
    抓取所有上市/上櫃股票代碼及其相關資訊，並儲存到 CSV 檔案中。
    """
    output_dir = 'data'
    output_file = os.path.join(output_dir, 'stock_ticker.csv')

    # 確保 data 目錄存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Fetching stock list from TWSE website...")
    urls = [
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2",  # 上市
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"   # 上櫃
    ]

    combined_df = pd.DataFrame()

    for url in urls:
        try:
            response = requests.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'lxml')
            table = soup.find_all('table')[1]
            df = pd.read_html(StringIO(str(table)), header=0)[0]

            # 清理 DataFrame
            df.rename(columns={'有價證券代號及名稱': 'code_and_name', '市場別': 'market', '產業別': 'industry', '上市日': 'list_date'}, inplace=True)
            df = df.drop(columns=['國際證券辨識號碼(ISIN Code)', 'CFICode', '備註'], errors='ignore').dropna()
            df = df[df['market'].isin(['上市', '上櫃'])]
            
            # 分割代號和名稱
            df['代號'] = df['code_and_name'].apply(lambda x: x.split()[0] if len(x.split()) > 0 else '')
            df['名稱'] = df['code_and_name'].apply(lambda x: " ".join(x.split()[1:]) if len(x.split()) > 1 else '')
            
            df = df[df['代號'].apply(lambda x: str(x).isdigit())]
            df = df.drop(columns=['code_and_name'])
            df['list_date'] = pd.to_datetime(df['list_date'], format='%Y/%m/%d', errors='coerce').dt.strftime('%Y-%m-%d')
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except Exception as e:
            print(f"Failed to process url {url}. Error: {e}")
            continue

    if not combined_df.empty:
        combined_df = combined_df.reset_index(drop=True)
        print(f"Scraping complete. Saving to {output_file}...")
        combined_df.to_csv(output_file, encoding='utf-8-sig', index=False)
        print("File saved successfully.")
    else:
        print("No data was scraped. The output file was not created.")

if __name__ == '__main__':
    run_scraper()
