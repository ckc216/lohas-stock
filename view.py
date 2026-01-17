"""
Streamlit UI Components for Stock Analysis
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime


class AppView:
    """Responsible for Streamlit UI rendering and page switching"""
    
    # UI Color Scheme (Apple Classic White)
    COLORS = {
        'primary': '#0071e3',
        'text': '#1d1d1f',
        'secondary': '#86868b',
        'background': '#f5f5f7',
        'border': '#d2d2d7',
        'grid': '#e1e1e6',
        'line_dark': '#d1d1d6',
    }
    
    @staticmethod
    def setup_page():
        """Configure Streamlit page settings and styling"""
        st.set_page_config(page_title="Stock Intelligence", layout="centered")
        
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
            .stApp { background-color: #ffffff; color: #1d1d1f; }
            html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
            .main-title { font-size: 42px; font-weight: 600; letter-spacing: -1px; text-align: center; color: #1d1d1f; margin-bottom: 5px; }
            .sub-title { font-size: 18px; color: #86868b; text-align: center; margin-bottom: 30px; }
            [data-testid="stMetric"] { background-color: #f5f5f7; padding: 15px; border-radius: 12px; }
            [data-testid="stMetricLabel"] { color: #86868b !important; font-size: 12px !important; }
            [data-testid="stMetricValue"] { color: #1d1d1f !important; }
            .stTextInput input { background-color: #f5f5f7 !important; color: #1d1d1f !important; border: 1px solid #d2d2d7 !important; border-radius: 10px !important; text-align: center; }
            
            /* Tab 樣式美化 */
            .stTabs [data-baseweb="tab-list"] { gap: 24px; }
            .stTabs [data-baseweb="tab"] { 
                height: 50px; white-space: pre-wrap; background-color: transparent; 
                border-radius: 0px; color: #86868b; font-weight: 400;
            }
            .stTabs [aria-selected="true"] { color: #0071e3 !important; font-weight: 600 !important; }
            </style>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header():
        """Render the header section"""
        st.markdown('<p class="main-title">Stock Intelligence.</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">LOHAS 5-Lines Analysis</p>', unsafe_allow_html=True)
    
    @staticmethod
    def render_search_input() -> str:
        """Render stock search input field"""
        return st.text_input("Stock Search", placeholder="Search Stock Name or ID...", label_visibility="collapsed")
    
    @staticmethod
    def render_metrics(current_price: float, ticker: str, last_date: str):
        """Render metric cards (price, ticker, last update)"""
        c1, c2, c3 = st.columns(3)
        c1.metric("LATEST PRICE", f"{current_price:.1f} TWD")
        c2.metric("TICKER", ticker)
        c3.metric("LAST UPDATED", last_date)
    
    @staticmethod
    def render_five_lines_chart(stock_data, lines_data: dict):
        """Render 5-Lines (五線譜) chart"""
        custom_hover = "<b>%{fullData.name}</b>: %{y:.1f}<extra></extra>"
        
        fig = go.Figure()
        
        # Background fill for 2SD band
        fig.add_trace(go.Scatter(
            x=stock_data.index.tolist() + stock_data.index.tolist()[::-1],
            y=(lines_data['lines']['+2SD']).tolist() + (lines_data['lines']['-2SD']).tolist()[::-1],
            fill='toself', fillcolor='rgba(245, 245, 247, 0.5)',
            line=dict(color='rgba(0,0,0,0)'), hoverinfo='skip'
        ))
        
        # Add the 5 lines
        colors = ['#e1e1e6', '#d1d1d6', '#d1d1d6', '#e1e1e6']
        names = ['+2SD', '+1SD', '-1SD', '-2SD']
        vals = [
            lines_data['lines']['+2SD'],
            lines_data['lines']['+1SD'],
            lines_data['lines']['-1SD'],
            lines_data['lines']['-2SD'],
        ]
        
        for color, name, val in zip(colors, names, vals):
            fig.add_trace(go.Scatter(
                x=stock_data.index, y=val, name=name,
                line=dict(color=color, width=1),
                hovertemplate=custom_hover
            ))
        
        # Trend line
        fig.add_trace(go.Scatter(
            x=stock_data.index, y=lines_data['lines']['Trend'],
            name='Trend', line=dict(color='#86868b', width=1, dash='dot'),
            hovertemplate=custom_hover
        ))
        
        # Close price
        fig.add_trace(go.Scatter(
            x=stock_data.index, y=stock_data['close'],
            name='Close', line=dict(color='#1d1d1f', width=2),
            hovertemplate=custom_hover
        ))
        
        # Layout settings
        fig.update_layout(
            showlegend=False, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(color='#1d1d1f', size=11)),
            yaxis=dict(gridcolor='#f5f5f7', side='right', tickfont=dict(color='#1d1d1f', size=11)),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, width="stretch")
    
    @staticmethod
    def render_channel_chart(stock_data, channel_data: dict):
        """Render Channel (通道) chart"""
        custom_hover = "<b>%{fullData.name}</b>: %{y:.1f}<extra></extra>"
        
        fig = go.Figure()
        
        # Channel lines
        ch_style = dict(color='#0071e3', width=1.5)
        fig.add_trace(go.Scatter(
            x=stock_data.index, y=channel_data['lines']['Top'],
            name='Top', line=ch_style, hovertemplate=custom_hover
        ))
        fig.add_trace(go.Scatter(
            x=stock_data.index, y=channel_data['lines']['Bottom'],
            name='Bottom', line=ch_style, hovertemplate=custom_hover
        ))
        
        # 20W MA
        fig.add_trace(go.Scatter(
            x=stock_data.index, y=channel_data['lines']['20W MA'],
            name='20W MA', line=dict(color='#d2d2d7', width=1, dash='dash'),
            hovertemplate=custom_hover
        ))
        
        # Close price
        fig.add_trace(go.Scatter(
            x=stock_data.index, y=stock_data['close'],
            name='Close', line=dict(color='#1d1d1f', width=2),
            hovertemplate=custom_hover
        ))
        
        # Layout settings
        fig.update_layout(
            showlegend=False, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(color='#1d1d1f', size=11)),
            yaxis=dict(gridcolor='#f5f5f7', side='right', tickfont=dict(color='#1d1d1f', size=11)),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, width="stretch")
    
    @staticmethod
    def render_tabs(stock_data, five_lines_data: dict, channel_data: dict):
        """Render tabs and switch between analysis views"""
        tab1, tab2 = st.tabs(["Lohas 5-Lines", "Lohas Channel"])
        
        with tab1:
            AppView.render_five_lines_chart(stock_data, five_lines_data)
        
        with tab2:
            AppView.render_channel_chart(stock_data, channel_data)

    @staticmethod
    def render_not_found_message(search_term: str):
        """Render a high-contrast error message when stock is not found"""
        st.markdown(f"""
            <div style="
                padding: 16px;
                background-color: #fff2f2;
                border: 1px solid #ffcaca;
                border-radius: 12px;
                color: #d01b1b;
                text-align: center;
                margin-top: 20px;
                font-weight: 500;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">
                <p style="margin: 0; font-size: 16px;">Stock "{search_term}" not found.</p>
                <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.8;">Please check the ticker symbol (e.g., 2330) or company name.</p>
            </div>
        """, unsafe_allow_html=True)
