import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import numpy as np
import urllib3
import os
from datetime import datetime, timedelta
from tqdm import tqdm
from services import SQLiteHandler, DB_PATH

# 關閉 SSL 警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class StockScraper:
    """負責抓取並解析富邦證券的財報數據。"""
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self._soup_cache = {}

    def _fetch_soup(self, url, max_retries=3):
        if url in self._soup_cache: return self._soup_cache[url]
        for i in range(max_retries):
            try:
                time.sleep(random.uniform(0.1, 0.3))
                response = requests.get(url, headers=self.headers, timeout=10, verify=False)
                response.encoding = 'big5'
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    self._soup_cache[url] = soup
                    return soup
            except: pass
            time.sleep(1)
        return None

    def _parse_row_data(self, soup, target_names):
        if not soup: return {}
        if isinstance(target_names, str): target_names = [target_names]
        results = {}
        for name in target_names:
            target = soup.find(['span', 'td'], string=lambda x: x and name in x)
            if target:
                row = target.find_parent(['div', 'tr'])
                if row:
                    cells = row.find_all(['span', 'td'])
                    vals = []
                    for c in cells[1:]:
                        txt = c.get_text(strip=True).replace(',', '').replace('%', '')
                        try: vals.append(float(txt))
                        except: vals.append(np.nan)
                    results[name] = vals
        return results

    def _parse_periods(self, soup):
        if not soup: return []
        period_span = soup.find(['span', 'td'], string=lambda x: x and '期別' in x)
        if period_span:
            row = period_span.find_parent(['div', 'tr'])
            if row: return [c.get_text(strip=True) for c in row.find_all(['span', 'td'])[1:]]
        return []

    def get_profitability_data(self, stock_id):
        url = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcr/zcr_{stock_id}.djhtm"
        soup = self._fetch_soup(url) 
        if soup is None: return pd.DataFrame()
        periods = self._parse_periods(soup)
        targets = ['營業利益率', '稅後淨利成長率', '每股盈餘', '存貨週轉率(次)']
        data_map = self._parse_row_data(soup, targets)
        if periods and data_map:
            min_len = min(len(periods), *[len(v) for v in data_map.values()])
            df_data = {'quarter': periods[:min_len]}
            for k, v in data_map.items(): df_data[k] = v[:min_len]
            return pd.DataFrame(df_data)
        return pd.DataFrame()

    def get_monthly_revenue(self, stock_id):
        url = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zch/zch_{stock_id}.djhtm"
        soup = self._fetch_soup(url)
        if soup is None: return pd.DataFrame()
        header_td = soup.find('td', string='年/月')
        if not header_td: return pd.DataFrame()
        header_tr = header_td.parent
        headers = [td.get_text(strip=True) for td in header_tr.find_all('td')]
        try:
            idx_date, idx_rev, idx_yoy = headers.index('年/月'), headers.index('營收'), headers.index('年增率')
        except: return pd.DataFrame()
        data = []
        for tr in header_tr.find_next_siblings('tr'):
            cols = tr.find_all('td')
            if len(cols) > max(idx_date, idx_rev, idx_yoy):
                d_str, rev_str, yoy_str = cols[idx_date].get_text(strip=True), cols[idx_rev].get_text(strip=True).replace(',', ''), cols[idx_yoy].get_text(strip=True).replace('%', '')
                if '/' in d_str:
                    try:
                        y, m = map(int, d_str.split('/'))
                        data.append({'date': f"{y+1911}-{m:02d}", 'year': y+1911, 'month': m, 'revenue': float(rev_str or 0), 'yoy': float(yoy_str or 0)})
                    except: continue
        return pd.DataFrame(data)

    def get_cashflow_data(self, stock_id):
        url = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zc3/zc3_{stock_id}.djhtm"
        soup = self._fetch_soup(url)
        if soup is None: return pd.DataFrame()
        periods = self._parse_periods(soup)
        targets = ['來自營運之現金流量', '投資活動之現金流量']
        data_map = self._parse_row_data(soup, targets)
        if periods and data_map:
            min_len = min(len(periods), *[len(v) for v in data_map.values()])
            df_data = {'quarter': periods[:min_len]}
            op, inv = data_map.get('來自營運之現金流量', [0]*min_len), data_map.get('投資活動之現金流量', [0]*min_len)
            df_data['fcf'] = [(op[i] if not np.isnan(op[i]) else 0) + (inv[i] if not np.isnan(inv[i]) else 0) for i in range(min_len)]
            return pd.DataFrame(df_data)
        return pd.DataFrame()

    def get_inventory_check_data(self, stock_id):
        urls = {
            'rev_q': f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcq_{stock_id}.djhtm",
            'rev_y': f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcqa/zcqa_{stock_id}.djhtm",
            'inv_q': f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpa/zcpa_{stock_id}.djhtm",
            'inv_y': f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpb/zcpb_{stock_id}.djhtm"
        }
        metrics = {}
        for k, url in urls.items():
            soup = self._fetch_soup(url)
            target = '營業收入' if 'rev' in k else '存貨'
            res = self._parse_row_data(soup, target)
            metrics[k] = res[target][0] if res.get(target) else None
        return metrics


class FinancialScorer:
    """負責計算評分邏輯。"""
    def __init__(self):
        self.scraper = StockScraper()

    def _analyze_core(self, stock_id):
        """核心分析邏輯：抓取數據並計算分數。"""
        df_zcr = self.scraper.get_profitability_data(stock_id)
        df_rev = self.scraper.get_monthly_revenue(stock_id)
        df_cf = self.scraper.get_cashflow_data(stock_id)
        inv_check = self.scraper.get_inventory_check_data(stock_id)

        results = {}
        results['月營收評分'] = self.score_revenue(df_rev)
        
        # Metadata
        if not df_rev.empty:
            results['營收月份'] = f"{int(df_rev.iloc[0]['year'])}-{int(df_rev.iloc[0]['month']):02d}"
        else: results['營收月份'] = None

        if not df_zcr.empty and 'quarter' in df_zcr:
            q_str = df_zcr.iloc[0]['quarter']
            try:
                if '.' in q_str:
                    y, q = q_str.split('.')
                    results['財報季度'] = f"{int(y)+1911 if int(y)<1000 else y}.{q}"
                else: results['財報季度'] = q_str
            except: results['財報季度'] = q_str
        else: results['財報季度'] = None

        # Scores
        if df_zcr.empty:
            results.update({'營業利益率評分': 0, '淨利成長評分': 0, 'EPS評分': 0, '存貨周轉率評分': "不評分"})
        else:
            results['營業利益率評分'] = self.score_operating_profit_margin(df_zcr['營業利益率'].tolist())
            results['淨利成長評分'] = self.score_net_profit_growth(df_zcr['稅後淨利成長率'].tolist())
            results['EPS評分'] = self.score_eps(df_zcr['每股盈餘'].tolist())
            results['存貨周轉率評分'] = self.score_inventory(df_zcr['存貨週轉率(次)'].tolist(), inv_check)

        results['自由現金流評分'] = self.score_fcf(df_cf['fcf'].tolist() if not df_cf.empty else [])

        # Total
        keys = ['月營收評分', '營業利益率評分', '淨利成長評分', 'EPS評分', '存貨周轉率評分', '自由現金流評分']
        raw_scores = [results.get(k) for k in keys]
        if any(s == "無法評分" for s in raw_scores): results['總分'] = "無法評分"
        else:
            valid = [s for s in raw_scores if isinstance(s, (int, float))]
            results['總分'] = round(sum(valid)/len(valid), 2) if valid else "不評分"

        return results, {'revenue': df_rev, 'profitability': df_zcr, 'cashflow': df_cf}

    def analyze_stock(self, stock_id):
        results, _ = self._analyze_core(stock_id)
        return results

    def analyze_stock_detailed(self, stock_id):
        return self._analyze_core(stock_id)

    # --- 評分函式 ---
    def score_revenue(self, df):
        if df.empty or len(df) < 6: return 0
        latest = df.iloc[0]
        yoy_series = []
        if latest['month'] == 2:
            try:
                c1, c2 = df[df['month']==1]['revenue'].iloc[0], df[df['month']==2]['revenue'].iloc[0]
                p1, p2 = df[(df['year']==latest['year']-1) & (df['month']==1)]['revenue'].iloc[0], df[(df['year']==latest['year']-1) & (df['month']==2)]['revenue'].iloc[0]
                yoy_series.append(((c1+c2)-(p1+p2))/(p1+p2)*100 if (p1+p2)!=0 else 0)
                needed = 4
                for _, r in df.iterrows():
                    if needed == 0: break
                    if r['year'] == latest['year'] and r['month'] >= 1: continue
                    yoy_series.append(r['yoy']); needed -= 1
            except: return 0
        else: yoy_series = df['yoy'].head(6).tolist()
        if len(yoy_series) < (5 if latest['month']==2 else 6): return 0
        m0, m1, m2 = yoy_series[0], yoy_series[1], yoy_series[2]
        avg = sum(yoy_series)/len(yoy_series)
        if avg < 0 or m0 < 0: return 0
        if m2 > m1 > m0: return 1
        if any(y < 0 for y in yoy_series): return 2
        if avg > 25: return 4 if m0 >= m1 else 3
        if 10 <= avg <= 25 and m0 >= m1: return 3
        return 2

    def score_operating_profit_margin(self, margins):
        if len(margins) < 4 or any(np.isnan(margins[:4])): return 0
        q0, q1, q2, q3 = margins[:4]
        avg = sum(margins[:4])/4
        def drop(p, c): return (p-c)/abs(p) if abs(p)>0 else 0
        if avg < 0 or q0 < 0: return 0
        if drop(q1, q0) >= 0.2 or avg < 5: return 1
        if (drop(q1,q0)<0.2 and drop(q2,q1)<0.2 and drop(q3,q2)<0.2):
            if avg >= 15 or (10 <= avg < 15 and q0 > q1) or (5 <= avg < 10 and q0 > q1): return 4 if avg >= 10 else 3
            return 3 if avg >= 10 else 2
        return 2

    def score_net_profit_growth(self, rates):
        if len(rates) < 4 or any(np.isnan(rates[:4])): return 0
        q0, q1, q2, q3 = rates[:4]
        if q0 < 0 and q1 < 0: return 0
        if q0 < 0 or sum(1 for x in rates[:4] if x < 0) >= 2: return 1
        if (rates[2] > rates[1] > rates[0]) and (q0 < 50): return 1
        if q1 < 0 or (q1 > 0 and (q1-q0)/q1 > 0.5): return 2
        if all(x >= 50 for x in rates[:3]) or (q0 > 0 and q1 > 0 and q2 > 0 and q0 > q1): return 4
        return 3

    def score_eps(self, eps_list):
        if len(eps_list) < 4 or any(np.isnan(eps_list[:4])): return 0
        q0, sum4q = eps_list[0], sum(eps_list[:4])
        if sum4q < 0: return 0
        if q0 < 0 or sum4q <= 1: return 1
        return 4 if sum4q > 5 else 3 if sum4q > 3 else 2

    def score_inventory(self, turnover_list, metrics):
        if metrics is None: return "無法評分"
        iq, rq = metrics.get('inv_q'), metrics.get('rev_q')
        iy, ry = metrics.get('inv_y'), metrics.get('rev_y')
        if (iq and rq and iq/rq < 0.04) or (iy and ry and iy/ry < 0.01): return "不評分"
        if len(turnover_list) < 4 or any(np.isnan(turnover_list[:4])): return 0
        q0, q1, q2, q3 = turnover_list[:4]
        avg = sum(turnover_list[:4])/4
        def drop(p, c): return (p-c)/p if p>0 else 0
        if drop(q1, q0) > 0.2: return 0
        if drop(q2, q1) > 0.2 or drop(q3, q2) > 0.2: return 1
        if (turnover_list[2] > turnover_list[1] > turnover_list[0]) and drop(turnover_list[2], turnover_list[0]) > 0.2: return 2
        return 4 if avg >= 1.5 else 3

    def score_fcf(self, fcf_list):
        if len(fcf_list) < 6 or any(np.isnan(fcf_list[:6])): return 0
        s6, s4 = sum(fcf_list[:6]), sum(fcf_list[:4])
        if all(x > 0 for x in fcf_list[:6]): return 4
        return 3 if s6 > 0 and s4 > 0 else 2 if s6 <= 0 and s4 > 0 else 1 if s6 > 0 and s4 <= 0 else 0


def run_bulk_financial_analysis(market_filter='ALL'):
    ticker_csv = os.path.join('data', 'stock_ticker.csv')
    if not os.path.exists(ticker_csv): return
    df = pd.read_csv(ticker_csv)
    df['代號'] = df['代號'].astype(str)
    if market_filter == 'TSE': df = df[df['market'] == '上市']
    elif market_filter == 'OTC': df = df[df['market'] == '上櫃']
    
    scorer = FinancialScorer()
    handler = SQLiteHandler() # Use default DB_PATH
    results = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Financial Scoring"):
        sid, sname, ldate, ind = row['代號'], row['名稱'], row['list_date'], row['industry']
        if ind == '金融保險業': continue
        time.sleep(random.uniform(0.1, 0.3))
        try:
            analysis = scorer.analyze_stock(sid)
            keys = ['月營收評分', '營業利益率評分', '淨利成長評分', 'EPS評分', '存貨周轉率評分', '自由現金流評分']
            if any(analysis.get(k) == "無法評分" for k in keys) or not analysis.get('營收月份'): continue
            
            score_diff = None
            current_score = analysis.get('總分')
            current_month_str = analysis.get('營收月份')

            if current_month_str and isinstance(current_score, (int, float)):
                try:
                    # Calculate previous month string (e.g., '2026-01' -> '2025-12')
                    y, m = map(int, current_month_str.split('-'))
                    prev_date = datetime(y, m, 1) - timedelta(days=1)
                    prev_month_str = f"{prev_date.year}-{prev_date.month:02d}"

                    # Fetch history to find previous score
                    history = handler.get_financial_history(sid)
                    if not history.empty:
                        prev_record = history[history['營收月份'] == prev_month_str]
                        if not prev_record.empty:
                            prev_score = prev_record.iloc[0]['本期綜合評分']
                            if isinstance(prev_score, (int, float)):
                                score_diff = round(current_score - float(prev_score), 2)
                except Exception:
                    pass

            results.append((sid, sname, ldate, ind, analysis.get('財報季度'), analysis.get('營收月份'), 
                            analysis.get('月營收評分'), analysis.get('營業利益率評分'), analysis.get('淨利成長評分'), 
                            analysis.get('EPS評分'), analysis.get('存貨周轉率評分'), analysis.get('自由現金流評分'), 
                            current_score, score_diff))
            
            if len(results) >= 20:
                handler.save_financial_scores(results); results = []
        except: continue
    if results: handler.save_financial_scores(results)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true')
    parser.add_argument('--market', default='ALL')
    args = parser.parse_args()
    if args.auto: run_bulk_financial_analysis(args.market)
    else:
        choice = input("選擇模式: [1] 單一 [2] 批次: ")
        if choice == '1':
            sid = input("代號: ")
            res, _ = FinancialScorer()._analyze_core(sid)
            for k, v in res.items(): print(f"{k}: {v}")
        else:
            m = input("市場: [1] 全部 [2] 上市 [3] 上櫃: ")
            run_bulk_financial_analysis('ALL' if m=='1' else 'TSE' if m=='2' else 'OTC')
