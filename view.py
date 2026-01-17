"""
Streamlit UI Components for Stock Analysis - Apple Premium Style
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


class AppView:
    """Responsible for Streamlit UI rendering with Apple Design Language"""
    
    @staticmethod
    def setup_page():
        """Configure Streamlit page settings and premium styling"""
        st.set_page_config(page_title="Stock Intelligence", layout="wide", initial_sidebar_state="collapsed")
        
        # Apple Global CSS
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
            
            /* 全域背景與字體 */
            .stApp { background-color: #ffffff; color: #1d1d1f; }
            html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
            
            /* 隱藏 Streamlit 預設標頭 */
            header { visibility: hidden; height: 0px; }
            [data-testid="stHeader"] { display: none; }
            .stAppHeader { display: none; }
            
            /* Apple Style Global Nav Bar */
            .apple-nav {
                position: fixed;
                top: 0; left: 0; right: 0;
                height: 48px;
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                z-index: 999999;
                border-bottom: 0.5px solid rgba(0,0,0,0.1);
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .nav-list {
                list-style: none;
                display: flex;
                gap: 40px;
                margin: 0;
                padding: 0;
            }
            
            .nav-item {
                position: relative;
                padding: 14px 0;
            }
            
            .nav-link {
                text-decoration: none !important; /* 移除底線 */
                color: #1d1d1f !important; /* 加深文字顏色 */
                font-size: 18px; /* 進一步放大字體 */
                font-weight: 600; /* 加粗到 semi-bold */
                opacity: 0.8;
                transition: opacity 0.2s;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .nav-item:hover .nav-link { opacity: 1; text-decoration: none !important; }
            
            /* 下拉選單 (Dropdown) */
            .dropdown-menu {
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%) translateY(-10px);
                background: rgba(255, 255, 255, 0.98);
                border: 0.5px solid rgba(0,0,0,0.1);
                border-radius: 12px;
                padding: 12px;
                min-width: 240px; /* 選單寬度同步增加 */
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                z-index: 1000000;
            }
            
            .nav-item:hover .dropdown-menu {
                opacity: 1;
                visibility: visible;
                transform: translateX(-50%) translateY(0);
            }
            
            .dropdown-item {
                display: block;
                padding: 12px 16px;
                color: #1d1d1f !important;
                text-decoration: none !important; /* 移除底線 */
                font-size: 16px; /* 放大選單字體 */
                border-radius: 8px;
                transition: background 0.2s;
            }
            
            .dropdown-item:hover {
                background: #f5f5f7;
                text-decoration: none !important;
            }
            
            /* 內容佈局控制 */
            .block-container {
                padding-top: 2rem !important;
                max-width: 1000px !important;
            }
            
            /* 標題樣式 - 加強對比 */
            .main-title { 
                font-size: 48px; font-weight: 600; letter-spacing: -1.2px; 
                text-align: center; color: #1d1d1f; margin-top: 60px; margin-bottom: 5px; 
            }
            .sub-title { 
                font-size: 21px; color: #424245; text-align: center; /* 加深副標題 */
                margin-bottom: 40px; font-weight: 400; 
            }
            
            /* Metric 卡片美化 - 解決截圖中文字看不見的問題 */
            [data-testid="stMetric"] { 
                background-color: #f5f5f7; 
                padding: 20px; 
                border-radius: 18px; 
                border: none; 
            }
            [data-testid="stMetricLabel"] { 
                color: #424245 !important; /* 加深標籤 */
                font-weight: 500 !important;
            }
            [data-testid="stMetricValue"] { 
                color: #1d1d1f !important; /* 確保數值是黑色的 */
            }
            
            /* 搜尋框加深 */
            .stTextInput input { 
                background-color: #f5f5f7 !important; 
                color: #1d1d1f !important;
                border-radius: 12px !important; 
                border: 1px solid #d2d2d7 !important; /* 增加極細邊框提升輪廓感 */
                padding: 12px !important; 
                text-align: center;
            }
            
            /* Tab 加深 */
            .stTabs [data-baseweb="tab"] p {
                color: #424245 !important;
                font-weight: 500 !important;
            }

            /* Dataframe 容器美化 */
            [data-testid="stDataFrame"] {
                background-color: #f5f5f7;
                border-radius: 18px;
                padding: 12px;
                border: none;
            }
            
            /* 讓表格內部的捲軸與背景更協調 (選用) */
            [data-testid="stDataFrame"] > div {
                background-color: transparent !important;
            }
            </style>
            """, unsafe_allow_html=True)

    @staticmethod
    def render_apple_nav():
        """Render the custom HTML/CSS Apple-style navigation"""
        st.markdown("""
            <div class="apple-nav">
                <ul class="nav-list">
                    <li class="nav-item">
                        <a class="nav-link" href="#"><span>♫</span> LOHAS Five-Line</a>
                        <div class="dropdown-menu">
                            <a href="/?page=individual" target="_self" class="dropdown-item">Stock Insights</a>
                            <a href="/?page=dashboard" target="_self" class="dropdown-item">Market Overview</a>
                        </div>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" style="opacity: 0.2; cursor: default;">Financials</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" style="opacity: 0.2; cursor: default;">Economy</a>
                    </li>
                </ul>
            </div>
            <div style="margin-top: 48px;"></div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_header():
        """Render the hero section"""
        st.markdown('<p class="main-title">Stock Intelligence.</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Advanced LOHAS Analysis Tools</p>', unsafe_allow_html=True)
    
    @staticmethod
    def render_search_input() -> str:
        """Render stock search input field"""
        _, col, _ = st.columns([1, 2, 1])
        with col:
            val = st.text_input("Stock Search", placeholder="Search Company Name or ID...", label_visibility="collapsed")
        return val

    @staticmethod
    def render_metrics(current_price: float, ticker: str, last_date: str):
        c1, c2, c3 = st.columns(3)
        c1.metric("LATEST PRICE", f"{current_price:.2f} TWD")
        c2.metric("TICKER", ticker)
        c3.metric("LAST UPDATED", last_date)

    @staticmethod
    def render_five_lines_chart(stock_data, lines_data: dict):
        custom_hover = "<b>%{fullData.name}</b>: %{y:.2f}<extra></extra>"
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=stock_data.index.tolist() + stock_data.index.tolist()[::-1],
            y=(lines_data['lines']['+2SD']).tolist() + (lines_data['lines']['-2SD']).tolist()[::-1],
            fill='toself', fillcolor='rgba(245, 245, 247, 0.4)',
            line=dict(color='rgba(0,0,0,0)'), hoverinfo='skip'
        ))
        colors = ['#e1e1e6', '#d1d1d6', '#d1d1d6', '#e1e1e6']
        names = ['+2SD', '+1SD', '-1SD', '-2SD']
        for color, name in zip(colors, names):
            fig.add_trace(go.Scatter(x=stock_data.index, y=lines_data['lines'][name], name=name, line=dict(color=color, width=1), hovertemplate=custom_hover))
        fig.add_trace(go.Scatter(x=stock_data.index, y=lines_data['lines']['Trend'], name='Trend', line=dict(color='#86868b', width=1, dash='dot'), hovertemplate=custom_hover))
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['close'], name='Close', line=dict(color='#1d1d1f', width=2.5), hovertemplate=custom_hover))
        fig.update_layout(
            showlegend=False, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(color='#424245', size=11)),
            yaxis=dict(gridcolor='#f5f5f7', side='right', tickfont=dict(color='#424245', size=11)),
            hovermode="x unified"
        )
        st.plotly_chart(fig, width='stretch')

    @staticmethod
    def render_channel_chart(stock_data, channel_data: dict):
        custom_hover = "<b>%{fullData.name}</b>: %{y:.2f}<extra></extra>"
        fig = go.Figure()
        ch_style = dict(color='#0071e3', width=1.5)
        fig.add_trace(go.Scatter(x=stock_data.index, y=channel_data['lines']['Top'], name='Top', line=ch_style, hovertemplate=custom_hover))
        fig.add_trace(go.Scatter(x=stock_data.index, y=channel_data['lines']['Bottom'], name='Bottom', line=ch_style, hovertemplate=custom_hover))
        fig.add_trace(go.Scatter(x=stock_data.index, y=channel_data['lines']['20W MA'], name='20W MA', line=dict(color='#d2d2d7', width=1, dash='dash'), hovertemplate=custom_hover))
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['close'], name='Close', line=dict(color='#1d1d1f', width=2.5), hovertemplate=custom_hover))
        fig.update_layout(
            showlegend=False, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(color='#424245', size=11)),
            yaxis=dict(gridcolor='#f5f5f7', side='right', tickfont=dict(color='#424245', size=11)),
            hovermode="x unified"
        )
        st.plotly_chart(fig, width='stretch')

    @staticmethod
    def render_tabs(stock_data, five_lines_data: dict, channel_data: dict):
        tab1, tab2 = st.tabs(["Lohas 5-Lines", "Lohas Channel"])
        with tab1: AppView.render_five_lines_chart(stock_data, five_lines_data)
        with tab2: AppView.render_channel_chart(stock_data, channel_data)

    @staticmethod
    def render_not_found_message(search_term: str):
        st.markdown(f"""
            <div style="padding: 24px; background-color: #f5f5f7; border-radius: 18px; text-align: center; margin-top: 20px;">
                <p style="margin: 0; font-size: 18px; color: #1d1d1f; font-weight: 500;">We couldn't find "{search_term}".</p>
                <p style="margin: 8px 0 0 0; font-size: 14px; color: #86868b;">Check the ticker symbol or company name.</p>
            </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_market_dashboard(df: pd.DataFrame):
        if df.empty:
            st.info("No data available in the dashboard.")
            return
        last_date = df['date'].iloc[0] if 'date' in df.columns else "Unknown"
        st.markdown(f'<p style="text-align: right; color: #86868b; font-size: 12px; margin-bottom: 5px;">Global Snapshot: {last_date}</p>', unsafe_allow_html=True)
        search_query = st.text_input("Search...", placeholder="Search company name or ID...", label_visibility="collapsed")
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df['stock_id'].astype(str).str.contains(search_query) | filtered_df['stock_name'].str.contains(search_query)]
        
        display_cols = ['stock_id', 'stock_name', 'level', 'close_price', 'lower_2sd', 'lower_1sd', 'trend_line', 'upper_1sd', 'upper_2sd']
        
        # 使用 Pandas Styler 設定風格
        styled_df = filtered_df[display_cols].style.set_properties(**{
            'background-color': '#f5f5f7',
            'color': '#1d1d1f',
            'border-color': '#d2d2d7'
        })
        
        st.dataframe(styled_df, use_container_width=True, height=600, hide_index=True)