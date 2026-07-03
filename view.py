"""
Streamlit UI components for the stock analysis dashboard.
"""
from __future__ import annotations

import html
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


class AppView:
    """Render Streamlit screens with a restrained, consistent visual system."""

    TEXT = "#1d1d1f"
    MUTED = "#6e6e73"
    SUBTLE = "#86868b"
    BORDER = "#d8d8de"
    PANEL = "#f5f5f7"
    BLUE = "#0071e3"
    GREEN = "#16a34a"
    RED = "#d92d20"
    AMBER = "#b7791f"

    @staticmethod
    def setup_page():
        st.set_page_config(page_title="Stock Intelligence", layout="wide", initial_sidebar_state="collapsed")
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            :root {
                --text: #1d1d1f;
                --muted: #6e6e73;
                --subtle: #86868b;
                --border: #d8d8de;
                --panel: #f5f5f7;
                --panel-strong: #ececf1;
                --blue: #0071e3;
            }

            html, body, [class*="css"], .stApp {
                font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                color: var(--text);
                background: #ffffff;
            }

            header, [data-testid="stHeader"], .stAppHeader { display: none; }
            .block-container {
                max-width: 1120px;
                padding: 76px 32px 56px !important;
            }

            .apple-nav {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 52px;
                background: rgba(255, 255, 255, 0.92);
                border-bottom: 1px solid rgba(0, 0, 0, 0.08);
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                z-index: 999999;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .nav-list {
                display: flex;
                gap: 10px;
                list-style: none;
                margin: 0;
                padding: 0;
            }

            .nav-item { position: relative; }
            .nav-link {
                display: flex;
                align-items: center;
                gap: 8px;
                min-height: 36px;
                padding: 0 14px;
                border-radius: 10px;
                color: var(--text) !important;
                text-decoration: none !important;
                font-size: 14px;
                font-weight: 600;
                transition: background 0.16s ease, color 0.16s ease;
            }

            .nav-item:hover .nav-link { background: var(--panel); color: #000 !important; }
            .nav-kicker {
                width: 7px;
                height: 7px;
                border-radius: 50%;
                background: var(--blue);
                opacity: 0.8;
            }

            .dropdown-menu {
                position: absolute;
                top: 43px;
                left: 50%;
                min-width: 220px;
                padding: 8px;
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.98);
                box-shadow: 0 18px 45px rgba(0, 0, 0, 0.11);
                opacity: 0;
                visibility: hidden;
                transform: translate(-50%, -6px);
                transition: opacity 0.16s ease, transform 0.16s ease, visibility 0.16s ease;
            }

            .nav-item:hover .dropdown-menu {
                opacity: 1;
                visibility: visible;
                transform: translate(-50%, 0);
            }

            .dropdown-item {
                display: block;
                padding: 11px 12px;
                border-radius: 8px;
                color: var(--text) !important;
                text-decoration: none !important;
                font-size: 14px;
                font-weight: 500;
            }

            .dropdown-item:hover { background: var(--panel); }

            .main-title {
                margin: 14px 0 8px;
                color: var(--text);
                text-align: center;
                font-size: 44px;
                font-weight: 700;
                line-height: 1.08;
            }

            .sub-title {
                margin: 0 auto 34px;
                max-width: 680px;
                color: var(--muted);
                text-align: center;
                font-size: 18px;
                font-weight: 400;
                line-height: 1.45;
            }

            .section-title {
                margin: 28px 0 12px;
                color: var(--text);
                font-size: 20px;
                font-weight: 700;
            }

            .panel {
                padding: 20px;
                border: 1px solid var(--border);
                border-radius: 8px;
                background: #fff;
            }

            .split-header {
                display: flex;
                justify-content: space-between;
                gap: 24px;
                align-items: flex-end;
                padding-bottom: 20px;
                margin-bottom: 22px;
                border-bottom: 1px solid var(--border);
            }

            .stock-title {
                margin: 0;
                color: var(--text);
                font-size: 38px;
                font-weight: 700;
                line-height: 1.1;
            }

            .meta-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(120px, 1fr));
                gap: 12px;
                text-align: right;
            }

            .meta-label {
                color: var(--subtle);
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }

            .meta-value {
                margin-top: 4px;
                color: var(--text);
                font-size: 18px;
                font-weight: 700;
            }

            .score-hero {
                display: grid;
                place-items: center;
                margin: 4px 0 28px;
                padding: 26px 16px;
                border: 1px solid var(--border);
                border-radius: 8px;
                background: linear-gradient(180deg, #fff 0%, #f8f8fa 100%);
            }

            .score-label {
                color: var(--subtle);
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .score-value {
                margin-top: 4px;
                font-size: 64px;
                font-weight: 700;
                line-height: 1;
            }

            .score-note {
                margin-top: 8px;
                color: var(--muted);
                font-size: 13px;
                font-weight: 500;
            }

            .metric-card {
                min-height: 112px;
                padding: 18px;
                border: 1px solid var(--border);
                border-radius: 8px;
                background: #fff;
            }

            .metric-card-label {
                color: var(--muted);
                font-size: 13px;
                font-weight: 600;
            }

            .metric-card-value {
                margin-top: 8px;
                color: var(--text);
                font-size: 28px;
                font-weight: 700;
                line-height: 1;
            }

            .metric-card-scale {
                margin-top: 6px;
                color: var(--subtle);
                font-size: 12px;
                font-weight: 500;
            }

            [data-testid="stMetric"] {
                padding: 18px;
                border: 1px solid var(--border);
                border-radius: 8px;
                background: #fff;
            }

            [data-testid="stMetricLabel"] p {
                color: var(--muted) !important;
                font-size: 12px !important;
                font-weight: 700 !important;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }

            [data-testid="stMetricValue"] {
                color: var(--text) !important;
                font-size: 26px !important;
                font-weight: 700 !important;
            }

            .stTextInput input {
                height: 46px;
                border: 1px solid var(--border) !important;
                border-radius: 8px !important;
                background: #fff !important;
                color: var(--text) !important;
                box-shadow: none !important;
                text-align: center;
                font-weight: 500;
            }

            .stTextInput input:focus {
                border-color: var(--blue) !important;
                box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.12) !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
                border-bottom: 1px solid var(--border);
            }

            .stTabs [data-baseweb="tab"] {
                height: 42px;
                border-radius: 8px 8px 0 0;
                padding: 0 12px;
            }

            .stTabs [aria-selected="true"] {
                background: var(--panel);
            }

            .stTabs [data-baseweb="tab"] p {
                color: var(--text) !important;
                font-size: 14px;
                font-weight: 600 !important;
            }

            [data-testid="stDataFrame"] {
                overflow: hidden;
                border: 1px solid var(--border);
                border-radius: 8px;
                background: #fff;
            }

            [data-testid="stDataFrame"] div[role="grid"] {
                border: none !important;
            }

            .soft-message {
                margin-top: 20px;
                padding: 22px;
                border: 1px solid var(--border);
                border-radius: 8px;
                background: var(--panel);
                text-align: center;
            }

            .soft-message-title {
                margin: 0;
                color: var(--text);
                font-size: 17px;
                font-weight: 700;
            }

            .soft-message-copy {
                margin: 7px 0 0;
                color: var(--muted);
                font-size: 14px;
            }

            @media (max-width: 760px) {
                .block-container { padding: 70px 18px 36px !important; }
                .nav-list { gap: 2px; }
                .nav-link { padding: 0 9px; font-size: 12px; }
                .main-title { font-size: 34px; }
                .sub-title { font-size: 16px; margin-bottom: 24px; }
                .split-header { display: block; }
                .stock-title { font-size: 30px; margin-bottom: 18px; }
                .meta-grid { text-align: left; }
                .score-value { font-size: 52px; }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_apple_nav():
        st.markdown(
            """
            <div class="apple-nav">
                <ul class="nav-list">
                    <li class="nav-item">
                        <a class="nav-link" href="#"><span class="nav-kicker"></span>Technical</a>
                        <div class="dropdown-menu">
                            <a href="?page=individual" target="_self" class="dropdown-item">LOHAS Five-Line</a>
                        </div>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#"><span class="nav-kicker"></span>Financials</a>
                        <div class="dropdown-menu">
                             <a href="?page=financials_six_index" target="_self" class="dropdown-item">Six-Index Scores</a>
                             <a href="?page=financials_overview" target="_self" class="dropdown-item">Financials Overview</a>
                        </div>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#"><span class="nav-kicker"></span>Economy</a>
                        <div class="dropdown-menu">
                            <a href="?page=economy" target="_self" class="dropdown-item">Fear and Greed</a>
                        </div>
                    </li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_header(subtitle="Advanced LOHAS Analysis Tools"):
        st.markdown('<h1 class="main-title">Stock Intelligence</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-title">{html.escape(subtitle)}</p>', unsafe_allow_html=True)

    @staticmethod
    def render_search_input() -> str:
        _, col, _ = st.columns([1, 2, 1])
        with col:
            return st.text_input(
                "Stock Search",
                placeholder="Search company name or ticker...",
                label_visibility="collapsed",
            )

    @staticmethod
    def render_metrics(current_price: float, ticker: str, last_date: str):
        c1, c2, c3 = st.columns(3)
        c1.metric("Latest Price", f"{current_price:.2f} TWD")
        c2.metric("Ticker", ticker)
        c3.metric("Last Updated", last_date)

    @classmethod
    def _score_color(cls, value: Any) -> str:
        if not isinstance(value, (int, float)):
            return cls.TEXT
        if value >= 3.5:
            return cls.GREEN
        if value < 2:
            return cls.RED
        return cls.AMBER

    @classmethod
    def _section_title(cls, title: str):
        st.markdown(f'<h2 class="section-title">{html.escape(title)}</h2>', unsafe_allow_html=True)

    @classmethod
    def _chart_layout(cls, fig: go.Figure, height: int = 430, y_range: list[int] | None = None):
        fig.update_layout(
            height=height,
            showlegend=False,
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            margin=dict(l=12, r=12, t=24, b=12),
            font=dict(family="Inter, sans-serif", color=cls.TEXT, size=12),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="#ffffff", bordercolor=cls.BORDER, font_size=12, font_color=cls.TEXT),
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=cls.MUTED, size=11)),
            yaxis=dict(
                side="right",
                gridcolor="#ececf1",
                zeroline=False,
                tickfont=dict(color=cls.MUTED, size=11),
                range=y_range,
            ),
        )
        return fig

    @classmethod
    def _plot(cls, fig: go.Figure):
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    @classmethod
    def _render_table(
        cls,
        df: pd.DataFrame,
        *,
        height: int | None = None,
        column_config: dict[str, Any] | None = None,
    ):
        kwargs: dict[str, Any] = {
            "use_container_width": True,
            "hide_index": True,
            "column_config": column_config,
        }
        if height is not None:
            kwargs["height"] = height
        st.dataframe(df, **kwargs)

    @staticmethod
    def _first_existing(df: pd.DataFrame, candidates: list[str]) -> str | None:
        for col in candidates:
            if col in df.columns:
                return col
        return None

    @staticmethod
    def _safe_get(mapping: dict[str, Any], candidates: list[str], default: Any = "N/A") -> Any:
        for key in candidates:
            if key in mapping:
                return mapping.get(key, default)
        return default

    @staticmethod
    def _html(value: Any) -> str:
        return html.escape(str(value))

    @classmethod
    def render_five_lines_chart(cls, stock_data, lines_data: dict):
        hover = "<b>%{fullData.name}</b>: %{y:.2f}<extra></extra>"
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=stock_data.index.tolist() + stock_data.index.tolist()[::-1],
                y=lines_data["lines"]["+2SD"].tolist() + lines_data["lines"]["-2SD"].tolist()[::-1],
                fill="toself",
                fillcolor="rgba(0, 113, 227, 0.06)",
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
            )
        )
        for color, name in [("#c7c7cc", "+2SD"), ("#b6b6bf", "+1SD"), ("#b6b6bf", "-1SD"), ("#c7c7cc", "-2SD")]:
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=lines_data["lines"][name],
                    name=name,
                    line=dict(color=color, width=1.1),
                    hovertemplate=hover,
                )
            )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=lines_data["lines"]["Trend"],
                name="Trend",
                line=dict(color=cls.BLUE, width=1.4, dash="dot"),
                hovertemplate=hover,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data["close"],
                name="Close",
                line=dict(color=cls.TEXT, width=2.4),
                hovertemplate=hover,
            )
        )
        cls._plot(cls._chart_layout(fig))

    @classmethod
    def render_channel_chart(cls, stock_data, channel_data: dict):
        hover = "<b>%{fullData.name}</b>: %{y:.2f}<extra></extra>"
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=channel_data["lines"]["Top"],
                name="Top",
                line=dict(color=cls.BLUE, width=1.4),
                hovertemplate=hover,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=channel_data["lines"]["Bottom"],
                name="Bottom",
                fill="tonexty",
                fillcolor="rgba(0, 113, 227, 0.06)",
                line=dict(color=cls.BLUE, width=1.4),
                hovertemplate=hover,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=channel_data["lines"]["20W MA"],
                name="20W MA",
                line=dict(color="#9b9ba5", width=1.2, dash="dash"),
                hovertemplate=hover,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data["close"],
                name="Close",
                line=dict(color=cls.TEXT, width=2.4),
                hovertemplate=hover,
            )
        )
        cls._plot(cls._chart_layout(fig))

    @staticmethod
    def render_tabs(stock_data, five_lines_data: dict, channel_data: dict):
        tab1, tab2 = st.tabs(["Lohas 5-Lines", "Lohas Channel"])
        with tab1:
            AppView.render_five_lines_chart(stock_data, five_lines_data)
        with tab2:
            AppView.render_channel_chart(stock_data, channel_data)

    @classmethod
    def render_not_found_message(cls, search_term: str):
        st.markdown(
            f"""
            <div class="soft-message">
                <p class="soft-message-title">No match for "{cls._html(search_term)}"</p>
                <p class="soft-message-copy">Check the ticker symbol or company name and try again.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @classmethod
    def render_financial_overview(cls, df: pd.DataFrame):
        st.markdown('<h1 class="main-title">Financials Overview</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Latest financial scores and LOHAS levels</p>', unsafe_allow_html=True)

        if df.empty:
            st.info("No financial data available.")
            return

        _, col, _ = st.columns([1, 2, 1])
        with col:
            search_query = st.text_input(
                "Search Overview",
                placeholder="Search company name or ticker...",
                label_visibility="collapsed",
            )

        display_df = df.copy()
        id_col = cls._first_existing(display_df, ["Ticker", "stock_id", "代號"])
        name_col = cls._first_existing(display_df, ["Name", "stock_name", "名稱"])
        level_col = cls._first_existing(display_df, ["LOHAS Level", "樂活五線譜"])

        if search_query and id_col:
            mask = display_df[id_col].astype(str).str.contains(search_query, case=False, na=False)
            if name_col:
                mask = mask | display_df[name_col].astype(str).str.contains(search_query, case=False, na=False)
            display_df = display_df[mask]

        if level_col:
            display_df[level_col] = display_df[level_col].apply(lambda x: str(int(x)) if pd.notnull(x) else "-")

        rename_map = {
            "代號": "Ticker",
            "名稱": "Name",
            "產業": "Industry",
            "上市日期": "Listed",
            "財報季度": "Quarter",
            "營收月份": "Month",
            "總分": "Average Score",
            "樂活五線譜": "LOHAS Level",
            "月營收評分": "Revenue",
            "營業利益率評分": "OP Margin",
            "淨利成長評分": "Net Profit",
            "EPS評分": "EPS",
            "存貨周轉率評分": "Inventory",
            "自由現金流量評分": "Cash Flow",
        }
        display_df = display_df.rename(columns={k: v for k, v in rename_map.items() if k in display_df.columns})

        preferred = [
            "Ticker",
            "Name",
            "Industry",
            "Average Score",
            "LOHAS Level",
            "Revenue",
            "OP Margin",
            "Net Profit",
            "EPS",
            "Inventory",
            "Cash Flow",
            "Quarter",
            "Month",
        ]
        cols = [c for c in preferred if c in display_df.columns] + [c for c in display_df.columns if c not in preferred]
        display_df = display_df[cols]

        numeric_score_cols = ["Average Score", "Revenue", "OP Margin", "Net Profit", "EPS", "Cash Flow"]
        column_config = {
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Industry": st.column_config.TextColumn("Industry", width="medium"),
            "Average Score": st.column_config.ProgressColumn("Average Score", min_value=0, max_value=4, format="%.2f"),
            "LOHAS Level": st.column_config.TextColumn("LOHAS Level", width="small"),
        }
        for col_name in numeric_score_cols:
            if col_name not in column_config:
                column_config[col_name] = st.column_config.NumberColumn(col_name, format="%.2f", width="small")

        cls._render_table(display_df, height=650, column_config=column_config)

    @classmethod
    def render_economy_page(cls, data: dict):
        st.markdown('<h1 class="main-title">Market Sentiment</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">CNN Fear & Greed Index</p>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Overview", "Timeline"])
        with tab1:
            col1, col2 = st.columns([2, 1])
            with col1:
                cls.render_fear_greed_gauge(data["current_score"], data["current_rating"])
                st.markdown(
                    f'<p style="color:#86868b;font-size:12px;text-align:center;">Last updated {cls._html(data["last_updated"])}</p>',
                    unsafe_allow_html=True,
                )
            with col2:
                cls._section_title("Previous Readings")
                for label, value in [
                    ("Previous close", data["previous_close"]),
                    ("1 week ago", data["previous_1_week"]),
                    ("1 month ago", data["previous_1_month"]),
                    ("1 year ago", data["previous_1_year"]),
                ]:
                    rating = "Neutral"
                    if value <= 25:
                        rating = "Extreme Fear"
                    elif value <= 45:
                        rating = "Fear"
                    elif value <= 55:
                        rating = "Neutral"
                    elif value <= 75:
                        rating = "Greed"
                    else:
                        rating = "Extreme Greed"
                    color = cls.GREEN if "Greed" in rating else cls.RED if "Fear" in rating else cls.TEXT
                    st.markdown(
                        f"""
                        <div class="metric-card" style="min-height:auto;margin-bottom:10px;">
                            <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;">
                                <div>
                                    <div class="metric-card-label">{cls._html(label)}</div>
                                    <div style="margin-top:4px;font-weight:700;color:{color};">{rating}</div>
                                </div>
                                <div style="font-size:24px;font-weight:700;color:{color};">{int(value)}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with tab2:
            cls.render_fear_greed_timeline(data["historical_data"])

    @classmethod
    def render_fear_greed_gauge(cls, score: float, rating: str):
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=score,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": rating.upper(), "font": {"size": 20, "color": cls.TEXT}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": cls.SUBTLE},
                    "bar": {"color": cls.TEXT, "thickness": 0.16},
                    "bgcolor": "white",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 25], "color": "#fdecec"},
                        {"range": [25, 45], "color": "#fff4de"},
                        {"range": [45, 55], "color": "#ececf1"},
                        {"range": [55, 75], "color": "#e9f7ef"},
                        {"range": [75, 100], "color": "#dff3e7"},
                    ],
                    "threshold": {
                        "line": {"color": cls.TEXT, "width": 4},
                        "thickness": 0.74,
                        "value": score,
                    },
                },
            )
        )
        fig.update_layout(
            height=390,
            paper_bgcolor="white",
            font={"color": cls.TEXT, "family": "Inter, sans-serif"},
            margin=dict(l=16, r=16, t=50, b=12),
        )
        cls._plot(fig)

    @classmethod
    def render_fear_greed_timeline(cls, df: pd.DataFrame):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["score"],
                name="Fear & Greed Index",
                line=dict(color=cls.BLUE, width=2.4),
                hovertemplate="Score: %{y:.0f}<extra></extra>",
            )
        )
        for val, label in [(25, "Extreme Fear"), (75, "Extreme Greed")]:
            fig.add_hline(y=val, line_dash="dot", line_color=cls.BORDER, annotation_text=label)

        fig = cls._chart_layout(fig, height=430, y_range=[0, 100])
        fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.06))
        cls._plot(fig)

    @classmethod
    def render_financial_dashboard(
        cls,
        ticker: str,
        stock_name: str,
        results: dict,
        raw_data: dict,
        history_df: pd.DataFrame | None = None,
        lohas_bundle: dict | None = None,
    ):
        display_title = f"{ticker} {stock_name}" if stock_name and stock_name != ticker else ticker
        quarter = cls._safe_get(results, ["財報季度"])
        revenue_month = cls._safe_get(results, ["營收月份"])

        st.markdown(
            f"""
            <div class="split-header">
                <h1 class="stock-title">{cls._html(display_title)}</h1>
                <div class="meta-grid">
                    <div>
                        <div class="meta-label">Fiscal Quarter</div>
                        <div class="meta-value">{cls._html(quarter)}</div>
                    </div>
                    <div>
                        <div class="meta-label">Revenue Month</div>
                        <div class="meta-value">{cls._html(revenue_month)}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        total_score = cls._safe_get(results, ["總分", "本期綜合評分"])
        score_color = cls._score_color(total_score)
        st.markdown(
            f"""
            <div class="score-hero">
                <div class="score-label">Average Score</div>
                <div class="score-value" style="color:{score_color};">{cls._html(total_score)}</div>
                <div class="score-note">Six-index financial quality score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metrics_map = [
            ("Revenue", ["月營收評分", "營收年增率"]),
            ("OP Margin", ["營業利益率評分", "營業利益率"]),
            ("Net Profit", ["淨利成長評分", "稅後淨利年增率"]),
            ("EPS", ["EPS評分", "每股盈餘EPS"]),
            ("Inventory", ["存貨周轉率評分", "存貨周轉率"]),
            ("Cash Flow", ["自由現金流量評分", "自由現金流量"]),
        ]
        cols = st.columns(3)
        for idx, (label, keys) in enumerate(metrics_map):
            val = cls._safe_get(results, keys)
            color = cls._score_color(val)
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-card-label">{label}</div>
                        <div class="metric-card-value" style="color:{color};">{cls._html(val)}</div>
                        <div class="metric-card-scale">Score out of 4</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if idx == 2:
                cols = st.columns(3)

        st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
        tabs = st.tabs(["Monthly Revenue", "Operating Margin", "Net Profit Growth", "EPS", "Inventory Turnover", "Free Cash Flow"])

        def render_df(df: pd.DataFrame | None, candidates: list[list[str]], names: list[str], empty_msg: str):
            if df is None or df.empty:
                st.info(empty_msg)
                return
            selected = [cls._first_existing(df, group) for group in candidates]
            if any(col is None for col in selected):
                st.info(empty_msg)
                return
            table = df[selected].copy()
            table.columns = names
            config = {name: st.column_config.NumberColumn(name, format="%.2f") for name in names if name not in ["Month", "Quarter"]}
            cls._render_table(table, column_config=config)

        with tabs[0]:
            render_df(
                raw_data.get("revenue"),
                [["date"], ["revenue"], ["yoy"]],
                ["Month", "Revenue (Thousand TWD)", "YoY (%)"],
                "No revenue data available.",
            )
        with tabs[1]:
            render_df(
                raw_data.get("profitability"),
                [["quarter"], ["營業利益率"]],
                ["Quarter", "Operating Margin (%)"],
                "No operating margin data available.",
            )
        with tabs[2]:
            render_df(
                raw_data.get("profitability"),
                [["quarter"], ["稅後淨利成長率", "稅後淨利年增率"]],
                ["Quarter", "Net Profit Growth (%)"],
                "No net profit growth data available.",
            )
        with tabs[3]:
            render_df(
                raw_data.get("profitability"),
                [["quarter"], ["每股盈餘", "每股盈餘EPS"]],
                ["Quarter", "EPS (TWD)"],
                "No EPS data available.",
            )
        with tabs[4]:
            render_df(
                raw_data.get("profitability"),
                [["quarter"], ["存貨週轉率(次)", "存貨周轉率"]],
                ["Quarter", "Inventory Turnover"],
                "No inventory turnover data available.",
            )
        with tabs[5]:
            render_df(
                raw_data.get("cashflow"),
                [["quarter"], ["fcf"]],
                ["Quarter", "Free Cash Flow"],
                "No cash flow data available.",
            )

        if lohas_bundle:
            cls._section_title("LOHAS Technical Analysis")
            l_tab1, l_tab2 = st.tabs(["Lohas 5-Lines", "Lohas Channel"])
            with l_tab1:
                cls.render_five_lines_chart(lohas_bundle["stock_data"], lohas_bundle["five_lines_data"])
            with l_tab2:
                cls.render_channel_chart(lohas_bundle["stock_data"], lohas_bundle["channel_data"])

        if history_df is not None and not history_df.empty:
            cls._section_title("Historical Performance")
            month_col = cls._first_existing(history_df, ["營收月份", "Month"])
            score_col = cls._first_existing(history_df, ["本期綜合評分", "總分", "Total Score"])
            if month_col and score_col:
                hist_plot = history_df.sort_values(month_col)
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=hist_plot[month_col],
                        y=hist_plot[score_col],
                        mode="lines+markers",
                        name="Total Score",
                        line=dict(color=cls.BLUE, width=2.6),
                        marker=dict(size=7, color="#ffffff", line=dict(width=2, color=cls.BLUE)),
                        hovertemplate="Score: %{y:.2f}<extra></extra>",
                    )
                )
                fig = cls._chart_layout(fig, height=360, y_range=[0, 4.2])
                fig.update_xaxes(type="category")
                cls._plot(fig)

            rename_map = {
                "營收月份": "Month",
                "財報季度": "Quarter",
                "本期綜合評分": "Total Score",
                "綜合評分變化": "Change",
                "營收年增率": "Revenue",
                "營業利益率": "OP Margin",
                "稅後淨利年增率": "Net Profit",
                "每股盈餘EPS": "EPS",
                "存貨周轉率": "Inventory",
                "自由現金流量": "Cash Flow",
            }
            final_hist_df = history_df.rename(columns={k: v for k, v in rename_map.items() if k in history_df.columns})
            preferred = ["Month", "Quarter", "Total Score", "Change", "Revenue", "OP Margin", "Net Profit", "EPS", "Inventory", "Cash Flow"]
            cols = [c for c in preferred if c in final_hist_df.columns]
            cls._render_table(
                final_hist_df[cols] if cols else final_hist_df,
                column_config={
                    "Total Score": st.column_config.ProgressColumn("Total Score", min_value=0, max_value=4, format="%.2f"),
                    "Change": st.column_config.NumberColumn("Change", format="%+.2f"),
                },
            )
