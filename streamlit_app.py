import streamlit as st
import pandas as pd
import os
from services import YFinanceService, LohasService, EconomyService, SQLiteHandler
from view import AppView
from financial_scraper import FinancialScorer

# --- Initialize Services ---
yfinance_service = YFinanceService()
lohas_service = LohasService()
economy_service = EconomyService()
financial_scorer = FinancialScorer()
sqlite_handler = SQLiteHandler() # Uses default DB_PATH
app_view = AppView()

# --- Cached Data Fetching ---
@st.cache_data(ttl=3600)
def get_stock_info_cached(target: str) -> dict | None:
    return yfinance_service.get_stock_info(target)

@st.cache_data(ttl=3600)
def fetch_data_cached(ticker: str, market: str = None):
    return yfinance_service.fetch_data(ticker, market)

@st.cache_data(ttl=3600)
def get_financial_overview_cached():
    return sqlite_handler.get_financial_overview()

@st.cache_data(ttl=600)
def get_fear_greed_data_cached():
    return EconomyService.fetch_fear_greed_index()

# --- Routing Logic ---
# Read page from URL query parameters
query_params = st.query_params
current_page = query_params.get("page", "individual")

# --- UI Setup ---
AppView.setup_page()
AppView.render_apple_nav()

# --- Global Header Logic ---
if current_page not in ["economy", "financials_overview"]:
    subtitle = "Six-Index Analysis Tools" if current_page == "financials_six_index" else "Advanced LOHAS Analysis Tools"
    AppView.render_header(subtitle)

# --- Content Routing ---
if current_page == "individual":
    target = AppView.render_search_input()

    if target:
        with st.spinner('Computing Analysis...'):
            info = get_stock_info_cached(target)
            if info:
                sid = info['id']
                market = info['market']
                stock_data = fetch_data_cached(sid, market)
                
                if stock_data is not None:
                    stock_data = LohasService.prepare_data(stock_data)
                    five_lines_data = LohasService.calculate_five_lines(stock_data)
                    channel_data = LohasService.calculate_channel(stock_data)
                    
                    now_p = stock_data['close'].iloc[-1]
                    last_date = stock_data.index[-1].strftime('%Y-%m-%d')
                    
                    AppView.render_metrics(now_p, sid, last_date)
                    AppView.render_tabs(stock_data, five_lines_data, channel_data)
                else:
                    st.error("Data fetch failed.")
            else:
                AppView.render_not_found_message(target)
    else:
        st.markdown('<p style="text-align: center; color: #86868b; margin-top: 20px;">Enter a stock ticker or name to begin depth analysis.</p>', unsafe_allow_html=True)

elif current_page == "financials_overview":
    with st.spinner('Loading Financials Overview...'):
        df_ov = get_financial_overview_cached()
        AppView.render_financial_overview(df_ov)

elif current_page == "financials_six_index":
    target = AppView.render_search_input()

    if target:
        # Resolve Ticker and Name
        ticker = None
        stock_name = None
        
        info = get_stock_info_cached(target)
        if info:
            ticker = info['id']
            # Find name from CSV if available, otherwise use target if it's not the id, or just id
            if target == ticker: # User entered ID
                 # Try to look up name again or set default
                 match = yfinance_service.ticker_df[yfinance_service.ticker_df['代號'] == ticker]
                 if not match.empty:
                     stock_name = match.iloc[0]['名稱']
                 else:
                     stock_name = ticker
            else: # User entered Name
                stock_name = target
        elif target.isdigit():
             ticker = target
             stock_name = target

        if ticker:
            display_name = f"{stock_name} ({ticker})" if stock_name and stock_name != ticker else ticker
            with st.spinner(f'Analyzing Financial Data for {display_name}...'):
                try:
                    # 1. Real-time Analysis
                    results, raw_data = financial_scorer.analyze_stock_detailed(ticker)
                    
                    # 2. Historical Data from DB
                    history_df = sqlite_handler.get_financial_history(ticker)
                    
                    if results and results.get('總分') != "無法評分":
                        AppView.render_financial_dashboard(
                            ticker, 
                            stock_name if stock_name else ticker, 
                            results, 
                            raw_data, 
                            history_df
                        )
                    else:
                        st.error(f"Could not retrieve sufficient financial data for {display_name}. Please check if the stock is listed on TWSE/TPEx.")
                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")
        else:
            AppView.render_not_found_message(target)
    else:
        st.markdown('<p style="text-align: center; color: #86868b; margin-top: 20px;">Enter a stock ticker or name to view Six-Index Financial Scores.</p>', unsafe_allow_html=True)

elif current_page == "economy":
    with st.spinner('Fetching Market Sentiment...'):
        fg_data = get_fear_greed_data_cached()
        if fg_data:
            AppView.render_economy_page(fg_data)
        else:
            st.error("Failed to fetch CNN Fear & Greed Index. Please try again later.")
