import streamlit as st
import pandas as pd
from services import YFinanceService, LohasService, EconomyService
from view import AppView

# --- Initialize Services ---
yfinance_service = YFinanceService()
lohas_service = LohasService()
economy_service = EconomyService()
app_view = AppView()

# --- Cached Data Fetching ---
@st.cache_data(ttl=3600)
def get_stock_info_cached(target: str) -> dict | None:
    return yfinance_service.get_stock_info(target)

@st.cache_data(ttl=3600)
def fetch_data_cached(ticker: str, market: str = None):
    return yfinance_service.fetch_data(ticker, market)

@st.cache_data(ttl=3600)
def get_all_scores_cached():
    return yfinance_service.get_all_scores()

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
if current_page != "economy":
    AppView.render_header()

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

elif current_page == "dashboard":
    with st.spinner('Loading Market Overview...'):
        df_all = get_all_scores_cached()
        AppView.render_market_dashboard(df_all)

elif current_page == "economy":
    with st.spinner('Fetching Market Sentiment...'):
        fg_data = get_fear_greed_data_cached()
        if fg_data:
            AppView.render_economy_page(fg_data)
        else:
            st.error("Failed to fetch CNN Fear & Greed Index. Please try again later.")
