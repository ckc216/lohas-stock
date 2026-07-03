# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概觀

用 Streamlit 打造的互動式網頁應用,分析台股(上市 TWSE／上櫃 TPEx)。包含兩大功能:

- **LOHAS 技術面分析**(樂活五線譜 5-Lines 與樂活通道 Channel)——以線性迴歸畫出趨勢帶,以及 MA100 通道,涵蓋約 3.5 年的歷史股價。
- **六大指標基本面評分**——六項財務指標各評 0~4 分,再加總綜合分數。評分邏輯詳載於 `scoring_rules.md`(這是權威規格,務必與 `financial_scraper.py` 保持同步)。

所有資料都在請求／爬取當下取自公開來源,不需要任何 API 金鑰。

## 常用指令

```bash
pip install -r requirements.txt          # 安裝相依套件
streamlit run streamlit_app.py           # 本地端啟動網站

python ticker_scraper.py                 # 更新 data/stock_ticker.csv(TWSE/TPEx 股票清單)
python lohas_scraper.py                  # 計算所有股票的 LOHAS 位階 -> financial_scores.db
python financial_scraper.py              # 互動模式:單一股票或批次
python financial_scraper.py --auto --market ALL   # 非互動批次(ALL | TSE | OTC),CI 使用
```

沒有測試套件、linter 設定或建置步驟。`financial_scraper.py` 在不帶 `--auto` 啟動時,會以互動式 CLI 執行(模式 `[1]` 單一 /`[2]` 批次)。

## 架構

本專案採「控制器 → 服務 → 視圖」分層。資料流向:爬蟲填入 `data/`,Streamlit 網站再讀取這些檔案,並搭配即時的 yfinance 查詢。

- **`streamlit_app.py`** — 控制器/進入點。一次建立所有服務物件,用 `@st.cache_data` 包住資料抓取,並透過網址查詢參數 `?page=` 在四個頁面之間路由:`individual`(LOHAS 圖表)、`financials_six_index`(單股基本面)、`financials_overview`(從 DB 讀取的全股票表格)、`economy`(CNN 恐懼與貪婪指數)。要新增頁面 = 在此加一個 `elif current_page == ...` 分支 + 在 `AppView` 加一個 render 方法。
- **`services.py`** — 所有後端邏輯,不含 UI:
  - `YFinanceService` — 先用 `data/stock_ticker.csv` 解析名稱/代號,再抓取股價歷史。市場後綴自動推斷:`上市`→`.TW`、`上櫃`→`.TWO`、未知→兩者都試。失敗會退避重試。
  - `LohasService` — 純靜態方法的數學運算。`prepare_data` → `calculate_five_lines`(線性迴歸 + 用 69%/95% 的 z 分數畫出 ±1SD/±2SD 帶)/ `calculate_channel`(MA100 ±2SD)。`get_lohas_level` 把股價對應成 1~6 的整數位階。
  - `EconomyService` — 爬取 CNN 恐懼與貪婪指數的 JSON 端點。
  - `SQLiteHandler` — 掌管 DB schema 與所有讀寫。兩張表:`stock_price_trend_lines`(LOHAS 位階/線,以 `stock_id` 為鍵)與 `stock_financial_scores`(六大指標評分,`(stock_id, 營收月份)` 為唯一鍵)。
- **`view.py`** — `AppView`,所有 Streamlit/Plotly 的渲染,以及一大段自訂 CSS 打造類 Apple 的白色 UI。純呈現層;接收算好的資料並繪製。
- **`financial_scraper.py`** — `StockScraper` 爬取富邦財報頁面(Big5 編碼的 HTML);`FinancialScorer` 套用 `scoring_rules.md` 的邏輯。`analyze_stock_detailed(stock_id)` 驅動即時的六大指標頁面;`run_bulk_financial_analysis(market)` 驅動 CI 的批次執行。

### 資料檔(`data/`,已納入 git 版控)
- `stock_ticker.csv` — 名稱↔代號↔市場的對應表。欄位為中文(`代號`、`名稱`)加上 `market`。這是解析使用者輸入、以及爬蟲逐一遍歷所有股票的權威來源。
- `financial_scores.db` — SQLite;網站直接讀取它來顯示總覽頁與歷史趨勢。**由 CI 提交並更新**,所以 git 歷史大多是自動化的資料提交。

## 自動化(GitHub Actions,`.github/workflows/`)

爬蟲依排程執行(時間為 UTC;台灣為 UTC+8),算出結果後**把更新的資料檔提交回 repo**:
- `ticker_scraper.yml` — 每日 15:00 UTC → 提交 `stock_ticker.csv`。
- `lohas_scraper.yml` — 每日 14:00 UTC → 提交 `financial_scores.db`(LOHAS 位階)。
- `financial_scraper.yml` — 僅手動觸發(可選 ALL/TSE/OTC)→ 提交 `financial_scores.db`(六大指標評分)。

## 慣例

- DataFrame 與 DB 全程使用中文欄位名稱與評分鍵(例如 `代號`、`營收年增率`、`本期綜合評分`)。請完整保留這些字串——它們在 爬蟲 → DB → 視圖 之間是以字面比對的。
- 維持關注點分離:運算放在 `services.py`/`financial_scraper.py`,渲染放在 `view.py`,路由放在 `streamlit_app.py`。
- 爬蟲會用小幅隨機 sleep 節流並重試;編輯時小心別移除這些機制(避免對來源網站造成過度請求)。
- 分數 `"無法評分"`(字串)代表「無法評分」(網路/資料失敗),程式會明確檢查它——與數值 `0` 是不同的。
