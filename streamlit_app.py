import streamlit as st
from services import YFinanceService, LohasService
from view import AppView

# --- Initialize Services ---
yfinance_service = YFinanceService()
lohas_service = LohasService()
app_view = AppView()

# --- Cached Data Fetching ---
@st.cache_data(ttl=3600)
def get_stock_info_cached(target: str) -> dict | None:
    """Cached wrapper for stock info lookup"""
    return yfinance_service.get_stock_info(target)

@st.cache_data(ttl=3600)
def fetch_data_cached(ticker: str, market: str):
    """Cached wrapper for data fetching"""
    return yfinance_service.fetch_data(ticker, market)

# --- Main App ---
AppView.setup_page()
AppView.render_header()

target = AppView.render_search_input()

if target:
    with st.spinner('Computing Analysis...'):
        # Get stock info (ID and Market)
        info = get_stock_info_cached(target)
        if info:
            sid = info['id']
            market = info['market']
            
            # Fetch stock data with specific market suffix
            stock_data = fetch_data_cached(sid, market)
            
            if stock_data is not None:
                # Prepare and calculate analysis
                stock_data = LohasService.prepare_data(stock_data)
                five_lines_data = LohasService.calculate_five_lines(stock_data)
                channel_data = LohasService.calculate_channel(stock_data)
                
                # Render metrics
                now_p = stock_data['close'].iloc[-1]
                last_date = stock_data.index[-1].strftime('%Y-%m-%d')
                AppView.render_metrics(now_p, sid, last_date)
                
                # Render tabs and charts
                AppView.render_tabs(stock_data, five_lines_data, channel_data)
            else:
                st.error("Data fetch failed.")
        else:
            AppView.render_not_found_message(target)
