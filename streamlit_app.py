import streamlit as st
from services import FinMindService, LohasService
from view import AppView

# --- Configuration ---
API_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyNC0wOS0yMSAyMzo0NToxMSIsInVzZXJfaWQiOiJja2MyMTYiLCJpcCI6IjEyNS4yMjQuMTM0LjIyMSJ9.SDy5B6g5uZZ7R5KYyetxf4UW7U5HBW6-0Em1q9vnzC4'

# --- Initialize Services ---
finmind_service = FinMindService(API_TOKEN)
lohas_service = LohasService()
app_view = AppView()

# --- Cached Data Fetching ---
@st.cache_data(ttl=3600)
def get_stock_id_cached(stock_name: str) -> str | None:
    """Cached wrapper for stock ID lookup"""
    return finmind_service.get_stock_id(stock_name)

@st.cache_data(ttl=3600)
def fetch_data_cached(ticker: str):
    """Cached wrapper for data fetching"""
    return finmind_service.fetch_data(ticker)

# --- Main App ---
AppView.setup_page()
AppView.render_header()

target = AppView.render_search_input()

if target:
    with st.spinner('Computing Analysis...'):
        # Get stock ID
        sid = get_stock_id_cached(target)
        if sid:
            # Fetch stock data
            stock_data = fetch_data_cached(sid)
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
            st.warning("Stock not found.")
