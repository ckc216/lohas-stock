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

    # Plotly 圖表字型堆疊（含中文字型，與主 CSS 一致）
    FONT = 'Inter, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif'

    @staticmethod
    def setup_page():
        st.set_page_config(page_title="股票智慧分析", layout="wide", initial_sidebar_state="collapsed")
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
                font-family: Inter, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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
                        <a class="nav-link" href="#"><span class="nav-kicker"></span>技術面</a>
                        <div class="dropdown-menu">
                            <a href="?page=individual" target="_self" class="dropdown-item">樂活五線譜</a>
                        </div>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#"><span class="nav-kicker"></span>財務面</a>
                        <div class="dropdown-menu">
                             <a href="?page=financials_six_index" target="_self" class="dropdown-item">六大指標評分</a>
                             <a href="?page=financials_overview" target="_self" class="dropdown-item">財務總覽</a>
                        </div>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#"><span class="nav-kicker"></span>總經面</a>
                        <div class="dropdown-menu">
                            <a href="?page=economy" target="_self" class="dropdown-item">Fear &amp; Greed Index</a>
                        </div>
                    </li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_header(title="股票智慧分析", subtitle=None):
        st.markdown(f'<h1 class="main-title">{html.escape(title)}</h1>', unsafe_allow_html=True)
        if subtitle:
            st.markdown(f'<p class="sub-title">{html.escape(subtitle)}</p>', unsafe_allow_html=True)

    @staticmethod
    def render_search_input() -> str:
        _, col, _ = st.columns([1, 2, 1])
        with col:
            return st.text_input(
                "股票搜尋",
                placeholder="輸入公司名稱或股票代號…",
                label_visibility="collapsed",
            )

    @staticmethod
    def render_metrics(current_price: float, ticker: str, last_date: str):
        c1, c2, c3 = st.columns(3)
        c1.metric("最新股價", f"{current_price:.2f} 元")
        c2.metric("股票代號", ticker)
        c3.metric("資料日期", last_date)

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
            font=dict(family=cls.FONT, color=cls.TEXT, size=12),
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
    def _add_price_marker(cls, fig, stock_data, ref_series):
        """在最新一點標出現價圓點；低於參考線(趨勢/均線)偏綠(相對便宜)、高於偏紅(相對昂貴)。"""
        last_x = stock_data.index[-1]
        last_close = stock_data["close"].iloc[-1]
        ref_last = ref_series.iloc[-1]
        color = cls.TEXT if pd.isna(ref_last) else (cls.GREEN if last_close < ref_last else cls.RED)
        fig.add_trace(
            go.Scatter(
                x=[last_x],
                y=[last_close],
                mode="markers",
                name="現價",
                marker=dict(size=11, color=color, line=dict(width=2, color="#ffffff")),
                hovertemplate=f"現價: {last_close:.2f}<extra></extra>",
                showlegend=False,
            )
        )

    @classmethod
    def _enable_legend(cls, fig):
        """開啟頂端水平圖例，讓各條線一目了然。"""
        fig.update_layout(
            showlegend=True,
            margin=dict(l=12, r=12, t=44, b=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color=cls.MUTED, size=11),
                bgcolor="rgba(0,0,0,0)",
            ),
        )
        return fig

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
                showlegend=False,
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
                name="趨勢線",
                line=dict(color=cls.BLUE, width=1.4, dash="dot"),
                hovertemplate=hover,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data["close"],
                name="收盤價",
                line=dict(color=cls.TEXT, width=2.4),
                hovertemplate=hover,
            )
        )
        cls._add_price_marker(fig, stock_data, lines_data["lines"]["Trend"])
        cls._plot(cls._enable_legend(cls._chart_layout(fig)))

    @classmethod
    def render_channel_chart(cls, stock_data, channel_data: dict):
        hover = "<b>%{fullData.name}</b>: %{y:.2f}<extra></extra>"
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=channel_data["lines"]["Top"],
                name="上通道",
                line=dict(color=cls.BLUE, width=1.4),
                hovertemplate=hover,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=channel_data["lines"]["Bottom"],
                name="下通道",
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
                name="20週均線",
                line=dict(color="#9b9ba5", width=1.2, dash="dash"),
                hovertemplate=hover,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data["close"],
                name="收盤價",
                line=dict(color=cls.TEXT, width=2.4),
                hovertemplate=hover,
            )
        )
        cls._add_price_marker(fig, stock_data, channel_data["lines"]["20W MA"])
        cls._plot(cls._enable_legend(cls._chart_layout(fig)))

    @staticmethod
    def render_tabs(stock_data, five_lines_data: dict, channel_data: dict):
        tab1, tab2 = st.tabs(["樂活五線譜", "樂活通道"])
        with tab1:
            AppView.render_five_lines_chart(stock_data, five_lines_data)
        with tab2:
            AppView.render_channel_chart(stock_data, channel_data)

    @classmethod
    def render_not_found_message(cls, search_term: str):
        st.markdown(
            f"""
            <div class="soft-message">
                <p class="soft-message-title">找不到「{cls._html(search_term)}」</p>
                <p class="soft-message-copy">請確認股票代號或公司名稱後再試一次。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @classmethod
    def render_financial_overview(cls, df: pd.DataFrame):
        st.markdown('<h1 class="main-title">財務總覽</h1>', unsafe_allow_html=True)

        if df.empty:
            st.info("目前沒有財務資料。")
            return

        _, col, _ = st.columns([1, 2, 1])
        with col:
            search_query = st.text_input(
                "搜尋總覽",
                placeholder="輸入公司名稱或股票代號…",
                label_visibility="collapsed",
            )

        display_df = df.copy()
        id_col = cls._first_existing(display_df, ["代號", "stock_id"])
        name_col = cls._first_existing(display_df, ["名稱", "stock_name"])
        level_col = cls._first_existing(display_df, ["樂活五線譜"])

        if search_query and id_col:
            mask = display_df[id_col].astype(str).str.contains(search_query, case=False, na=False)
            if name_col:
                mask = mask | display_df[name_col].astype(str).str.contains(search_query, case=False, na=False)
            display_df = display_df[mask]

        if level_col:
            display_df[level_col] = display_df[level_col].apply(lambda x: str(int(x)) if pd.notnull(x) else "-")

        rename_map = {
            "總分": "綜合評分",
            "樂活五線譜": "樂活位階",
            "月營收評分": "月營收",
            "營業利益率評分": "營業利益率",
            "淨利成長評分": "淨利成長",
            "EPS評分": "EPS",
            "存貨周轉率評分": "存貨周轉",
            "自由現金流量評分": "自由現金流",
        }
        display_df = display_df.rename(columns={k: v for k, v in rename_map.items() if k in display_df.columns})

        preferred = [
            "代號",
            "名稱",
            "產業",
            "綜合評分",
            "樂活位階",
            "月營收",
            "營業利益率",
            "淨利成長",
            "EPS",
            "存貨周轉",
            "自由現金流",
            "財報季度",
            "營收月份",
        ]
        cols = [c for c in preferred if c in display_df.columns] + [c for c in display_df.columns if c not in preferred]
        display_df = display_df[cols]

        numeric_score_cols = ["綜合評分", "月營收", "營業利益率", "淨利成長", "EPS", "自由現金流"]
        column_config = {
            "代號": st.column_config.TextColumn("代號", width="small"),
            "名稱": st.column_config.TextColumn("名稱", width="medium"),
            "產業": st.column_config.TextColumn("產業", width="medium"),
            "綜合評分": st.column_config.NumberColumn("綜合評分", format="%.2f", width="small"),
            "樂活位階": st.column_config.TextColumn("樂活位階", width="small"),
        }
        for col_name in numeric_score_cols:
            if col_name not in column_config:
                column_config[col_name] = st.column_config.NumberColumn(col_name, format="%.2f", width="small")

        cls._render_table(display_df, height=650, column_config=column_config)

    @classmethod
    def render_economy_page(cls, data: dict):
        st.markdown('<h1 class="main-title">市場情緒</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">CNN Fear &amp; Greed Index</p>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["總覽", "歷史走勢"])
        with tab1:
            col1, col2 = st.columns([2, 1])
            with col1:
                cls.render_fear_greed_gauge(data["current_score"], data["current_rating"])
                st.markdown(
                    f'<p style="color:#86868b;font-size:12px;text-align:center;">資料更新於 {cls._html(data["last_updated"])}</p>',
                    unsafe_allow_html=True,
                )
            with col2:
                cls._section_title("歷史數值")
                for label, value in [
                    ("前一交易日", data["previous_close"]),
                    ("一週前", data["previous_1_week"]),
                    ("一個月前", data["previous_1_month"]),
                    ("一年前", data["previous_1_year"]),
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
            font={"color": cls.TEXT, "family": cls.FONT},
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
                        <div class="meta-label">財報季度</div>
                        <div class="meta-value">{cls._html(quarter)}</div>
                    </div>
                    <div>
                        <div class="meta-label">營收月份</div>
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
                <div class="score-label">綜合評分</div>
                <div class="score-value" style="color:{score_color};">{cls._html(total_score)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metrics_map = [
            ("月營收", ["月營收評分", "營收年增率"]),
            ("營業利益率", ["營業利益率評分", "營業利益率"]),
            ("淨利成長", ["淨利成長評分", "稅後淨利年增率"]),
            ("EPS", ["EPS評分", "每股盈餘EPS"]),
            ("存貨周轉", ["存貨周轉率評分", "存貨周轉率"]),
            ("自由現金流", ["自由現金流量評分", "自由現金流量"]),
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
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if idx == 2:
                cols = st.columns(3)

        st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
        tabs = st.tabs(["月營收", "營業利益率", "淨利成長率", "EPS", "存貨周轉率", "自由現金流量"])

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
            config = {name: st.column_config.NumberColumn(name, format="%.2f") for name in names if name not in ["月份", "季度"]}
            cls._render_table(table, column_config=config)

        with tabs[0]:
            render_df(
                raw_data.get("revenue"),
                [["date"], ["revenue"], ["yoy"]],
                ["月份", "營收(千元)", "年增率(%)"],
                "查無營收資料。",
            )
        with tabs[1]:
            render_df(
                raw_data.get("profitability"),
                [["quarter"], ["營業利益率"]],
                ["季度", "營業利益率(%)"],
                "查無營業利益率資料。",
            )
        with tabs[2]:
            render_df(
                raw_data.get("profitability"),
                [["quarter"], ["稅後淨利成長率", "稅後淨利年增率"]],
                ["季度", "淨利成長率(%)"],
                "查無淨利成長資料。",
            )
        with tabs[3]:
            render_df(
                raw_data.get("profitability"),
                [["quarter"], ["每股盈餘", "每股盈餘EPS"]],
                ["季度", "EPS(元)"],
                "查無 EPS 資料。",
            )
        with tabs[4]:
            render_df(
                raw_data.get("profitability"),
                [["quarter"], ["存貨週轉率(次)", "存貨周轉率"]],
                ["季度", "存貨周轉率"],
                "查無存貨周轉率資料。",
            )
        with tabs[5]:
            render_df(
                raw_data.get("cashflow"),
                [["quarter"], ["fcf"]],
                ["季度", "自由現金流量"],
                "查無現金流量資料。",
            )

        if lohas_bundle:
            cls._section_title("樂活技術分析")
            l_tab1, l_tab2 = st.tabs(["樂活五線譜", "樂活通道"])
            with l_tab1:
                cls.render_five_lines_chart(lohas_bundle["stock_data"], lohas_bundle["five_lines_data"])
            with l_tab2:
                cls.render_channel_chart(lohas_bundle["stock_data"], lohas_bundle["channel_data"])

        if history_df is not None and not history_df.empty:
            cls._section_title("歷史評分走勢")
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
                        name="綜合評分",
                        line=dict(color=cls.BLUE, width=2.6),
                        marker=dict(size=7, color="#ffffff", line=dict(width=2, color=cls.BLUE)),
                        hovertemplate="評分: %{y:.2f}<extra></extra>",
                    )
                )
                fig = cls._chart_layout(fig, height=360, y_range=[0, 4.2])
                fig.update_xaxes(type="category")
                cls._plot(fig)

            rename_map = {
                "營收月份": "營收月份",
                "財報季度": "財報季度",
                "本期綜合評分": "綜合評分",
                "綜合評分變化": "評分變化",
                "營收年增率": "月營收",
                "營業利益率": "營業利益率",
                "稅後淨利年增率": "淨利成長",
                "每股盈餘EPS": "EPS",
                "存貨周轉率": "存貨周轉",
                "自由現金流量": "自由現金流",
            }
            final_hist_df = history_df.rename(columns={k: v for k, v in rename_map.items() if k in history_df.columns})
            preferred = ["營收月份", "財報季度", "綜合評分", "評分變化", "月營收", "營業利益率", "淨利成長", "EPS", "存貨周轉", "自由現金流"]
            cols = [c for c in preferred if c in final_hist_df.columns]
            cls._render_table(
                final_hist_df[cols] if cols else final_hist_df,
                column_config={
                    "綜合評分": st.column_config.NumberColumn("綜合評分", format="%.2f", width="small"),
                    "評分變化": st.column_config.NumberColumn("評分變化", format="%+.2f"),
                },
            )
