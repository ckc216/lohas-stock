import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import numpy as np
import urllib3

# 關閉 SSL 警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class StockScraper:
    """
    負責抓取並解析富邦證券的財報數據。
    實作了快取機制，避免對同一頁面重複請求。
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self._soup_cache = {}

    def _fetch_soup(self, url, max_retries=3):
        """通用請求函式，含重試與快取"""
        if url in self._soup_cache:
            return self._soup_cache[url]

        for i in range(max_retries):
            try:
                time.sleep(random.uniform(0.2, 0.5)) # 禮貌性延遲
                response = requests.get(url, headers=self.headers, timeout=10, verify=False)
                response.encoding = 'big5'
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    self._soup_cache[url] = soup
                    return soup
                else:
                    print(f"嘗試 {i+1}: 狀態碼 {response.status_code} ({url})")
            except Exception as e:
                print(f"嘗試 {i+1}: 錯誤 {e} ({url})")
            
            if i < max_retries - 1:
                time.sleep(1)
        return None

    def _parse_row_data(self, soup, target_names):
        """
        從 soup 中解析特定名稱的列數據。
        target_names 可以是字串或列表。
        回傳: {name: [values...]}
        """
        if not soup: return {}
        if isinstance(target_names, str): target_names = [target_names]
        
        results = {}
        for name in target_names:
            # 模糊搜尋
            target = soup.find(['span', 'td'], string=lambda x: x and name in x)
            if target:
                row = target.find_parent(['div', 'tr'])
                if row:
                    cells = row.find_all(['span', 'td'])
                    # 跳過第一個 cell (標題)，取後面的數值
                    vals = []
                    for c in cells[1:]:
                        txt = c.get_text(strip=True).replace(',', '').replace('%', '')
                        try: vals.append(float(txt))
                        except: vals.append(np.nan)
                    results[name] = vals
        return results

    def _parse_periods(self, soup):
        """解析期別 (季度)"""
        if not soup: return []
        period_span = soup.find(['span', 'td'], string=lambda x: x and '期別' in x)
        if period_span:
            row = period_span.find_parent(['div', 'tr'])
            if row:
                return [c.get_text(strip=True) for c in row.find_all(['span', 'td'])[1:]]
        return []

    def get_profitability_data(self, stock_id):
        """
        抓取獲利能力頁面 (zcr) 的所有數據
        包含: 營業利益率, 稅後淨利成長率, 每股盈餘, 存貨週轉率
        """
        url = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcr/zcr_{stock_id}.djhtm"
        soup = self._fetch_soup(url) 
        if soup is None: return None
        
        periods = self._parse_periods(soup)
        targets = ['營業利益率', '稅後淨利成長率', '每股盈餘', '存貨週轉率(次)']
        data_map = self._parse_row_data(soup, targets)
        
        # 整理成 DataFrame
        if periods and data_map:
            min_len = min(len(periods), *[len(v) for v in data_map.values()])
            df_data = {'quarter': periods[:min_len]}
            for k, v in data_map.items():
                df_data[k] = v[:min_len]
            return pd.DataFrame(df_data)
        return pd.DataFrame()

    def get_monthly_revenue(self, stock_id):
        """抓取月營收 (zch)"""
        url = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zch/zch_{stock_id}.djhtm"
        soup = self._fetch_soup(url)
        if soup is None: return None

        # 這裡結構比較特殊，手動解析
        header_td = soup.find('td', string='年/月')
        if not header_td: return pd.DataFrame()
        
        header_tr = header_td.parent
        headers = [td.get_text(strip=True) for td in header_tr.find_all('td')]
        try:
            idx_date = headers.index('年/月')
            idx_rev = headers.index('營收')
            idx_yoy = headers.index('年增率')
        except:
            return pd.DataFrame()

        data = []
        for tr in header_tr.find_next_siblings('tr'):
            cols = tr.find_all('td')
            if len(cols) > max(idx_date, idx_rev, idx_yoy):
                d_str = cols[idx_date].get_text(strip=True)
                rev_str = cols[idx_rev].get_text(strip=True).replace(',', '')
                yoy_str = cols[idx_yoy].get_text(strip=True).replace('%', '').replace(',', '')
                
                if '/' in d_str:
                    try:
                        y, m = map(int, d_str.split('/'))
                        full_date = f"{y+1911}-{m:02d}"
                        rev = float(rev_str) if rev_str not in ['-', ''] else 0.0
                        yoy = float(yoy_str) if yoy_str not in ['-', ''] else 0.0
                        data.append({'date': full_date, 'year': y+1911, 'month': m, 'revenue': rev, 'yoy': yoy})
                    except:
                        continue
        return pd.DataFrame(data)

    def get_cashflow_data(self, stock_id):
        """抓取現金流量 (zc3)"""
        url = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zc3/zc3_{stock_id}.djhtm"
        soup = self._fetch_soup(url)
        if soup is None: return None
        
        periods = self._parse_periods(soup)
        targets = ['來自營運之現金流量', '投資活動之現金流量']
        data_map = self._parse_row_data(soup, targets)
        
        if periods and data_map:
            min_len = min(len(periods), *[len(v) for v in data_map.values()])
            df_data = {'quarter': periods[:min_len]}
            # 計算 FCF
            op = data_map.get('來自營運之現金流量', [0]*min_len)
            inv = data_map.get('投資活動之現金流量', [0]*min_len)
            fcf = [(op[i] if not np.isnan(op[i]) else 0) + (inv[i] if not np.isnan(inv[i]) else 0) for i in range(min_len)]
            df_data['fcf'] = fcf
            return pd.DataFrame(df_data)
        return pd.DataFrame()

    def get_inventory_check_data(self, stock_id):
        """抓取存貨與營收數據 (用於低庫存檢查)"""
        # 1. 季營收 (zcq)
        url_zcq = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcq_{stock_id}.djhtm"
        soup_zcq = self._fetch_soup(url_zcq)
        if soup_zcq is None: return None

        # 2. 年營收 (zcqa)
        url_zcqa = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcq/zcqa/zcqa_{stock_id}.djhtm"
        soup_zcqa = self._fetch_soup(url_zcqa)
        if soup_zcqa is None: return None

        # 3. 季存貨 (zcpa)
        url_zcpa = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpa/zcpa_{stock_id}.djhtm"
        soup_zcpa = self._fetch_soup(url_zcpa)
        if soup_zcpa is None: return None

        # 4. 年存貨 (zcpb)
        url_zcpb = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcp/zcpb/zcpb_{stock_id}.djhtm"
        soup_zcpb = self._fetch_soup(url_zcpb)
        if soup_zcpb is None: return None

        metrics = {}
        rev_map = self._parse_row_data(soup_zcq, '營業收入')
        metrics['rev_q'] = rev_map['營業收入'][0] if rev_map.get('營業收入') else None

        rev0_map = self._parse_row_data(soup_zcqa, '營業收入')
        metrics['rev_y'] = rev0_map['營業收入'][0] if rev0_map.get('營業收入') else None

        inv_map = self._parse_row_data(soup_zcpa, '存貨')
        metrics['inv_q'] = inv_map['存貨'][0] if inv_map.get('存貨') else None

        inv0_map = self._parse_row_data(soup_zcpb, '存貨')
        metrics['inv_y'] = inv0_map['存貨'][0] if inv0_map.get('存貨') else None
        
        return metrics


class FinancialScorer:
    """
    負責計算評分邏輯 (不處理爬蟲)
    """
    def __init__(self):
        self.scraper = StockScraper()

    def analyze_stock(self, stock_id):
        """主入口：分析一檔股票的所有指標"""
        results = {}
        
        # 1. 抓取所有數據
        print("Scraping Profitability Data (zcr)...")
        df_zcr = self.scraper.get_profitability_data(stock_id)
        
        print("Scraping Monthly Revenue (zch)...")
        df_rev = self.scraper.get_monthly_revenue(stock_id)
        
        print("Scraping Cashflow (zc3)...")
        df_cf = self.scraper.get_cashflow_data(stock_id)
        
        print("Scraping Inventory Metrics (zcq/zcp)...")
        inv_check = self.scraper.get_inventory_check_data(stock_id)

        # 2. 計算各項分數
        results['月營收評分'] = self.score_revenue(df_rev)
        
        if df_zcr is None:
            results['營業利益率評分'] = "無法評分"
            results['淨利成長評分'] = "無法評分"
            results['EPS評分'] = "無法評分"
            results['存貨周轉率評分'] = "無法評分"
        elif df_zcr.empty:
            results['營業利益率評分'] = 0
            results['淨利成長評分'] = 0
            results['EPS評分'] = 0
            results['存貨周轉率評分'] = "不評分"
        else:
            results['營業利益率評分'] = self.score_operating_profit_margin(df_zcr['營業利益率'].tolist() if '營業利益率' in df_zcr else [])
            results['淨利成長評分'] = self.score_net_profit_growth(df_zcr['稅後淨利成長率'].tolist() if '稅後淨利成長率' in df_zcr else [])
            results['EPS評分'] = self.score_eps(df_zcr['每股盈餘'].tolist() if '每股盈餘' in df_zcr else [])
            
            # 存貨評分需要周轉率 + 存貨金額檢查
            turnover_list = df_zcr['存貨週轉率(次)'].tolist() if '存貨週轉率(次)' in df_zcr else []
            results['存貨周轉率評分'] = self.score_inventory(turnover_list, inv_check)

        if df_cf is None:
            results['自由現金流評分'] = "無法評分"
        else:
            results['自由現金流評分'] = self.score_fcf(df_cf['fcf'].tolist() if not df_cf.empty else [])

        return results

    # --- 以下為純邏輯評分函式 ---

    def score_revenue(self, df):
        if df is None: return "無法評分"
        if df.empty or len(df) < 6: return 0
        
        latest = df.iloc[0]
        yoy_series = []
        is_cny = (latest['month'] == 2)
        
        if is_cny:
            try:
                curr_jan = df[df['month']==1]['revenue'].iloc[0]
                curr_feb = df[df['month']==2]['revenue'].iloc[0]
                prev_jan = df[(df['year']==latest['year']-1) & (df['month']==1)]['revenue'].iloc[0]
                prev_feb = df[(df['year']==latest['year']-1) & (df['month']==2)]['revenue'].iloc[0]
                
                merged_yoy = ((curr_jan+curr_feb) - (prev_jan+prev_feb)) / (prev_jan+prev_feb) * 100 if (prev_jan+prev_feb)!=0 else 0
                yoy_series.append(merged_yoy)
                
                needed = 4
                for _, row in df.iterrows():
                    if needed == 0: break
                    if row['year'] == latest['year'] and row['month'] >= 1: continue
                    yoy_series.append(row['yoy'])
                    needed -= 1
            except:
                return 0
        else:
            yoy_series = df['yoy'].head(6).tolist()

        if len(yoy_series) < (5 if is_cny else 6): return 0
        
        m0, m1, m2 = yoy_series[0], yoy_series[1], yoy_series[2]
        avg = sum(yoy_series) / len(yoy_series)
        
        if avg < 0 or m0 < 0: return 0
        if m2 > m1 > m0: return 1
        if any(y < 0 for y in yoy_series): return 2
        
        m0_up = (m0 >= m1)
        if avg > 25:
            return 4 if m0_up else 3
        if 10 <= avg <= 25 and m0_up: return 3
        if avg > 25 and not m0_up:
            if abs(m1) > 0 and (m1-m0)/abs(m1) < 0.5: return 3
            
        return 2

    def score_operating_profit_margin(self, margins):
        if not margins or len(margins) < 4: return 0
        q0, q1, q2, q3 = margins[:4]
        avg = sum(margins[:4]) / 4
        
        def drop(p, c): return (p-c)/abs(p) if abs(p)>0 else 0
        
        is_stable = (drop(q1,q0)<0.2 and drop(q2,q1)<0.2 and drop(q3,q2)<0.2)
        is_uptrend = (q0 > q1)
        history_stable = (drop(q2,q1)<0.2 and drop(q3,q2)<0.2)
        
        if avg < 0 or q0 < 0: return 0
        if drop(q1, q0) >= 0.2 or avg < 5: return 1
        
        if is_stable:
            if avg >= 15: return 4
            if 10 <= avg < 15 and is_uptrend: return 4
            if 10 <= avg < 15: return 3
            if 5 <= avg < 10 and is_uptrend: return 3
            
        return 2 if not history_stable else 2

    def score_net_profit_growth(self, rates):
        if not rates or len(rates) < 3: return 0
        q0, q1, q2 = rates[:3]
        q3 = rates[3] if len(rates)>=4 else 0
        
        neg_count = sum(1 for x in [q0,q1,q2,q3] if x < 0)
        is_big_drop = (q1 > 0 and (q1-q0)/q1 > 0.5)
        
        if q0 < 0 and q1 < 0: return 0
        if q0 < 0 or neg_count >= 2: return 1
        if (q2 > q1 > q0) and (q0 < 50): return 1
        if q1 < 0 or is_big_drop: return 2
        
        if q0 >= 50 and q1 >= 50 and q2 >= 50: return 4
        if q0 > 0 and q1 > 0 and q2 > 0 and q0 > q1: return 4
        
        return 3

    def score_eps(self, eps_list):
        if not eps_list or len(eps_list) < 4: return 0
        q0 = eps_list[0]
        sum4q = sum(eps_list[:4])
        
        if sum4q < 0: return 0
        if q0 < 0 or (0 <= sum4q <= 1): return 1
        if sum4q > 5: return 4
        if 3 < sum4q <= 5: return 3
        if 1 < sum4q <= 3: return 2
        return 1

    def score_inventory(self, turnover_list, metrics):
        # 網路錯誤處理
        if metrics is None: return "無法評分"
        
        # 低庫存產業檢查 (不評分)
        inv_q, rev_q = metrics.get('inv_q'), metrics.get('rev_q')
        inv_y, rev_y = metrics.get('inv_y'), metrics.get('rev_y')
        
        if inv_q is not None and rev_q and (inv_q/rev_q < 0.04): return "不評分"
        if inv_y is not None and rev_y and (inv_y/rev_y < 0.01): return "不評分"
        
        # 抓不到資料 (不評分)
        if not turnover_list: return "不評分"
        
        # 資料不足 (0分)
        if len(turnover_list) < 4: return 0
        
        q0, q1, q2, q3 = turnover_list[:4]
        avg = sum(turnover_list[:4]) / 4
        
        def drop(p, c): return (p-c)/p if p>0 else 0
        
        if drop(q1, q0) > 0.2: return 0
        if drop(q2, q1) > 0.2 or drop(q3, q2) > 0.2: return 1
        if (q2 > q1 > q0) and drop(q2, q0) > 0.2: return 2
        
        return 4 if avg >= 1.5 else 3

    def score_fcf(self, fcf_list):
        if not fcf_list or len(fcf_list) < 6: return 0
        sum6q = sum(fcf_list[:6])
        sum4q = sum(fcf_list[:4])
        
        if all(x > 0 for x in fcf_list[:6]): return 4
        if sum6q > 0 and sum4q > 0: return 3
        if sum6q <= 0 and sum4q > 0: return 2
        if sum6q > 0 and sum4q <= 0: return 1
        return 0

if __name__ == "__main__":
    stock_id = input("請輸入台股股票代號 (例如 2330): ")
    scorer = FinancialScorer()
    
    print(f"\n開始分析 {stock_id} ...")
    start_time = time.time()
    
    results = scorer.analyze_stock(stock_id)
    
    print(f"\n--- {stock_id} 分析結果 (耗時: {time.time()-start_time:.2f}秒) ---")
    for k, v in results.items():
        if isinstance(v, (int, float)):
            score_str = f"{v} 分"
        else:
            score_str = str(v)
        print(f"{k}: {score_str}")
