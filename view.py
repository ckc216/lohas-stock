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
                gap: 60px; /* 增加間距 */
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
            
            /* 讓導覽列圖示變黑白並調整大小 */
            .nav-link span {
                filter: grayscale(100%);
                font-size: 20px;
                line-height: 1;
            }
            
            /* 下拉選單 (Dropdown) */
            .dropdown-menu {
                position: absolute;
                top: 85%;
                left: 50%;
                transform: translateX(-50%) translateY(-10px);
                background: rgba(255, 255, 255, 0.98);
                border: 0.5px solid rgba(0,0,0,0.1);
                border-radius: 12px;
                padding: 8px;
                padding-top: 8px;
                min-width: 240px; /* 選單寬度同步增加 */
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                opacity: 0;
                visibility: hidden;
                transition: all 0.2s ease-in-out;
                z-index: 1000000;
                display: block;
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
                transition: background 0.1s;
                cursor: pointer;
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
                        <a class="nav-link" href="#"><span>📊</span> Technical</a>
                        <div class="dropdown-menu">
                            <a href="?page=individual" target="_self" class="dropdown-item">LOHAS Five-Line</a>
                        </div>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#"><span>💰</span> Financials</a>
                        <div class="dropdown-menu">
                             <a href="?page=financials_six_index" target="_self" class="dropdown-item">Six-Index Scores</a>
                             <a href="?page=financials_overview" target="_self" class="dropdown-item">Financials Overview</a>
                        </div>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#"><span>📈</span> Economy</a>
                        <div class="dropdown-menu">
                            <a href="?page=economy" target="_self" class="dropdown-item">Fear and Greed</a>
                        </div>
                    </li>
                </ul>
            </div>
            <div style="margin-top: 48px;"></div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_header(subtitle="Advanced LOHAS Analysis Tools"):
        """Render the hero section"""
        st.markdown('<p class="main-title">Stock Intelligence.</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-title">{subtitle}</p>', unsafe_allow_html=True)
    
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
    def render_financial_overview(df: pd.DataFrame):
        """Render the Financials Overview table"""
        st.markdown('<p class="main-title">Financials Overview.</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Latest Financial Scores & Lohas Levels</p>', unsafe_allow_html=True)
        
        if df.empty:
            st.info("No financial data available.")
            return

        # 搜尋功能
        _, col, _ = st.columns([1, 2, 1])
        with col:
            search_query = st.text_input("Search Overview", placeholder="Search Company Name or ID...", label_visibility="collapsed")
        
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df['代號'].astype(str).str.contains(search_query) | 
                filtered_df['名稱'].str.contains(search_query)
            ]

        # 處理 樂活五線譜 (Level) 轉為整數並處理缺失值
        # 我們使用 map 來處理顯示，這不會改變原始資料類型，但會讓渲染更漂亮
        display_df = filtered_df.copy()
        
        # 處理 Level 的顯示
        display_df['樂活五線譜'] = display_df['樂活五線譜'].apply(
            lambda x: str(int(x)) if pd.notnull(x) else "-"
        )

        column_config = {
            "代號": st.column_config.TextColumn("代號"),
            "名稱": st.column_config.TextColumn("名稱"),
            "總分": st.column_config.NumberColumn("總分", format="%.2f"),
            "月營收評分": st.column_config.NumberColumn("月營收評分"),
            "營業利益率評分": st.column_config.NumberColumn("營業利益率評分"),
            "淨利成長評分": st.column_config.NumberColumn("淨利成長評分"),
            "EPS評分": st.column_config.NumberColumn("EPS評分"),
            "存貨周轉率評分": st.column_config.TextColumn("存貨周轉率評分"),
            "自由現金流評分": st.column_config.NumberColumn("自由現金流評分"),
        }

        st.dataframe(
            display_df, 
            width='stretch', 
            height=650, 
            hide_index=True, 
            column_config=column_config
        )

    @staticmethod
    def render_economy_page(data: dict):
        """Render the Economy page with CNN Fear & Greed Index"""
        st.markdown('<p class="main-title">Market Sentiment.</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">CNN Fear & Greed Index</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Overview", "Timeline"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            with col1:
                AppView.render_fear_greed_gauge(data['current_score'], data['current_rating'])
                st.markdown(f'<p style="color: #86868b; font-size: 12px; text-align: center;">Last updated {data["last_updated"]}</p>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div style="padding-top: 40px;"></div>', unsafe_allow_html=True)
                metrics = [
                    ("Previous close", data['previous_close']),
                    ("1 week ago", data['previous_1_week']),
                    ("1 month ago", data['previous_1_month']),
                    ("1 year ago", data['previous_1_year'])
                ]
                
                for label, value in metrics:
                    rating = "Neutral"
                    if value <= 25: rating = "Extreme Fear"
                    elif value <= 45: rating = "Fear"
                    elif value <= 55: rating = "Neutral"
                    elif value <= 75: rating = "Greed"
                    else: rating = "Extreme Greed"
                    
                    color = "#1d1d1f"
                    if "Greed" in rating: color = "#00c805"
                    elif "Fear" in rating: color = "#ff3b30"
                    
                    st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 0.5px solid #d2d2d7;">
                            <div>
                                <div style="font-size: 14px; color: #424245;">{label}</div>
                                <div style="font-size: 16px; font-weight: 600; color: {color};">{rating}</div>
                            </div>
                            <div style="width: 32px; height: 32px; border-radius: 50%; border: 1.5px solid #d2d2d7; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600;">
                                {int(value)}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        with tab2:
            AppView.render_fear_greed_timeline(data['historical_data'])

    @staticmethod
    def render_fear_greed_gauge(score: float, rating: str):
        """Render the Gauge chart for Fear & Greed Index"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': rating.upper(), 'font': {'size': 24, 'color': '#1d1d1f'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#86868b"},
                'bar': {'color': "#1d1d1f", 'thickness': 0.15},
                'bgcolor': "white",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 25], 'color': '#f5f5f7'},
                    {'range': [25, 45], 'color': '#e5e5e7'},
                    {'range': [45, 55], 'color': '#d2d2d7'},
                    {'range': [55, 75], 'color': '#e5e5e7'},
                    {'range': [75, 100], 'color': '#f5f5f7'},
                ],
                'threshold': {
                    'line': {'color': "#1d1d1f", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        
        fig.update_layout(
            paper_bgcolor='white',
            font={'color': "#1d1d1f", 'family': "sans-serif"},
            margin=dict(l=20, r=20, t=50, b=20),
            height=400
        )
        st.plotly_chart(fig, width='stretch')

    @staticmethod
    def render_fear_greed_timeline(df: pd.DataFrame):
        """Render the historical timeline for Fear & Greed Index"""
        fig = go.Figure()
        
        # Add historical line
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['score'],
            name='Fear & Greed Index',
            line=dict(color='#0071e3', width=2),
            hovertemplate="Score: %{y:.0f}<extra></extra>"
        ))
        
        # Add reference lines
        for val, label in [(25, "Extreme Fear"), (75, "Extreme Greed")]:
            fig.add_hline(y=val, line_dash="dot", line_color="#d2d2d7", annotation_text=label)

        fig.update_layout(
            showlegend=False, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(color='#424245', size=11), rangeslider=dict(visible=True)),
            yaxis=dict(gridcolor='#f5f5f7', side='right', tickfont=dict(color='#424245', size=11), range=[0, 100]),
            hovermode="x unified"
        )
        st.plotly_chart(fig, width='stretch')

    @staticmethod
    def render_financial_dashboard(ticker: str, stock_name: str, results: dict, raw_data: dict, history_df: pd.DataFrame = None, lohas_bundle: dict = None):
        """Render the Six-Index Scores dashboard"""
        
        # 1. Info Header (Ticker & Dates)
        display_title = f"{ticker} {stock_name}" if stock_name and stock_name != ticker else ticker
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; padding: 0 10px;">
                <div>
                    <div style="font-size: 42px; font-weight: 700; color: #1d1d1f;">{display_title}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 14px; color: #86868b; margin-bottom: 2px;">FISCAL QUARTER</div>
                    <div style="font-size: 24px; font-weight: 600; color: #1d1d1f; margin-bottom: 8px;">{results.get('財報季度', 'N/A')}</div>
                    <div style="font-size: 14px; color: #86868b; margin-bottom: 2px;">REVENUE MONTH</div>
                    <div style="font-size: 24px; font-weight: 600; color: #1d1d1f;">{results.get('營收月份', 'N/A')}</div>
                </div>
            </div>
            <hr style="border: 0; border-top: 0.5px solid #d2d2d7; margin-bottom: 30px;">
        """, unsafe_allow_html=True)
        
        # 2. Total Score
        total_score = results.get('總分', 'N/A')
        score_color = "#1d1d1f"
        if isinstance(total_score, (int, float)):
            if total_score >= 3.5: score_color = "#00c805"
            elif total_score < 2: score_color = "#ff3b30"
            
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 40px;">
                <div style="font-size: 16px; color: #86868b; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Average Score</div>
                <div style="font-size: 72px; font-weight: 700; color: {score_color}; line-height: 1.1;">{total_score}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # 3. Six Metrics Grid
        c1, c2, c3 = st.columns(3)
        c4, c5, c6 = st.columns(3)
        
        metrics_map = [
            ("Revenue", "月營收評分", c1),
            ("OP Margin", "營業利益率評分", c2),
            ("Net Profit", "淨利成長評分", c3),
            ("EPS", "EPS評分", c4),
            ("Inventory", "存貨周轉率評分", c5),
            ("Cash Flow", "自由現金流評分", c6)
        ]
        
        for label, key, col in metrics_map:
            val = results.get(key, 'N/A')
            col.metric(label, f"{val} / 4" if isinstance(val, (int, float)) else val)
            
        st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)

        # 4. Raw Data Tables (Split into 6 Tabs)
        tabs = st.tabs(["Monthly Revenue", "Operating Margin", "Net Profit Growth", "EPS", "Inventory Turnover", "Free Cash Flow"])
        
        # Helper to format and display
        def render_df(df, cols, rename_map, empty_msg):
            if df is not None and not df.empty and all(c in df.columns for c in cols):
                sub_df = df[cols].rename(columns=rename_map)
                st.dataframe(sub_df, width='stretch', hide_index=True)
            else:
                st.info(empty_msg)

        with tabs[0]: # Monthly Revenue
            render_df(
                raw_data.get('revenue'), 
                ['date', 'revenue', 'yoy'], 
                {'date': 'Month', 'revenue': 'Revenue (Thousand TWD)', 'yoy': 'YoY (%)'}, 
                "No revenue data available."
            )
                
        with tabs[1]: # Operating Margin
            render_df(
                raw_data.get('profitability'), 
                ['quarter', '營業利益率'], 
                {'quarter': 'Quarter', '營業利益率': 'Operating Margin (%)'}, 
                "No operating margin data available."
            )

        with tabs[2]: # Net Profit Growth
            render_df(
                raw_data.get('profitability'), 
                ['quarter', '稅後淨利成長率'], 
                {'quarter': 'Quarter', '稅後淨利成長率': 'Net Profit Growth (%)'}, 
                "No net profit growth data available."
            )

        with tabs[3]: # EPS
            render_df(
                raw_data.get('profitability'), 
                ['quarter', '每股盈餘'], 
                {'quarter': 'Quarter', '每股盈餘': 'EPS (TWD)'}, 
                "No EPS data available."
            )

        with tabs[4]: # Inventory Turnover
            render_df(
                raw_data.get('profitability'), 
                ['quarter', '存貨週轉率(次)'], 
                {'quarter': 'Quarter', '存貨週轉率(次)': 'Inventory Turnover (Times)'}, 
                "No inventory turnover data available."
            )

        with tabs[5]: # Free Cash Flow
            render_df(
                raw_data.get('cashflow'), 
                ['quarter', 'fcf'], 
                {'quarter': 'Quarter', 'fcf': 'Free Cash Flow (Million TWD)'}, 
                "No cash flow data available."
            )

        # 5. Integrated LOHAS Charts
        if lohas_bundle:
            st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
            st.markdown('<p class="sub-title">Lohas Technical Analysis</p>', unsafe_allow_html=True)
            l_tab1, l_tab2 = st.tabs(["Lohas 5-Lines", "Lohas Channel"])
            with l_tab1:
                AppView.render_five_lines_chart(lohas_bundle['stock_data'], lohas_bundle['five_lines_data'])
            with l_tab2:
                AppView.render_channel_chart(lohas_bundle['stock_data'], lohas_bundle['channel_data'])

        # 5. Historical Analysis Section
        if history_df is not None and not history_df.empty:
            st.markdown('<div style="margin-top: 60px;"></div>', unsafe_allow_html=True)
            st.markdown('<p class="sub-title">Historical Performance Analysis</p>', unsafe_allow_html=True)
            
            # 確保日期排序正確 (舊 -> 新) 供繪圖
            hist_plot = history_df.sort_values('營收月份')
            
            # Trend Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist_plot['營收月份'], 
                y=hist_plot['本期綜合評分'],
                mode='lines+markers',
                name='Total Score',
                line=dict(color='#0071e3', width=3),
                marker=dict(size=8, color='#ffffff', line=dict(width=2, color='#0071e3')),
                hovertemplate="Score: %{y:.2f}<extra></extra>"
            ))
            
            fig.update_layout(
                title={'text': 'Total Score Trend', 'font': {'size': 18, 'color': '#1d1d1f'}},
                showlegend=False, 
                plot_bgcolor='white', 
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    type='category', # 強制使用類別型，只顯示字串日期
                    showgrid=False, 
                    tickfont=dict(color='#86868b')
                ),
                yaxis=dict(showgrid=True, gridcolor='#f5f5f7', range=[0, 4.2], tickfont=dict(color='#86868b')),
                hovermode="x unified"
            )
            st.plotly_chart(fig, width='stretch')
            
            # Historical Data Table
            st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 18px; font-weight: bold; color: #1d1d1f; margin-bottom: 10px;">Historical Data Table</p>', unsafe_allow_html=True)
            
            # 選擇並重新命名欄位以供顯示
            display_cols = [
                '營收月份', '財報季度', '本期綜合評分', '綜合評分變化',
                '營收年增率', '營業利益率', '稅後淨利年增率', 
                '每股盈餘EPS', '存貨周轉率', '自由現金流量'
            ]
            rename_map = {
                '營收月份': 'Month', 
                '財報季度': 'Quarter',
                '本期綜合評分': 'Total Score',
                '綜合評分變化': 'Change',
                '營收年增率': 'Rev Score', 
                '營業利益率': 'OP Margin Score',
                '稅後淨利年增率': 'Net Profit Score', 
                '每股盈餘EPS': 'EPS Score',
                '存貨周轉率': 'Inv Score',
                '自由現金流量': 'FCF Score'
            }
            
            # 處理欄位可能不存在的情況 (防禦性程式設計)
            avail_cols = [c for c in display_cols if c in history_df.columns]
            final_hist_df = history_df[avail_cols].rename(columns=rename_map)
            
            # 使用 column_config 調整對齊與格式
            column_config = {
                "Month": st.column_config.TextColumn("Month"),
                "Quarter": st.column_config.TextColumn("Quarter"),
                "Total Score": st.column_config.NumberColumn("Total Score", format="%.2f"),
                "Change": st.column_config.NumberColumn("Change", format="%+.2f"),
                "Rev Score": st.column_config.NumberColumn("Rev Score"),
                "OP Margin Score": st.column_config.NumberColumn("OP Margin Score"),
                "Net Profit Score": st.column_config.NumberColumn("Net Profit Score"),
                "EPS Score": st.column_config.NumberColumn("EPS Score"),
                "Inv Score": st.column_config.NumberColumn("Inv Score", help="Inventory Score"),
                "FCF Score": st.column_config.NumberColumn("FCF Score"),
            }
            
            st.dataframe(final_hist_df, width='stretch', hide_index=True, column_config=column_config)