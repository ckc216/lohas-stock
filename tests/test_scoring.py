"""
Unit tests for FinancialScorer's six scoring functions.

Each test maps to a scoring tier documented in `scoring_rules.md` (the
authoritative spec). Score lists are ordered newest-first: index 0 == Q0/M0
(most recent), matching the scrapers' output.

Run:  pytest tests/test_scoring.py -v
"""
import numpy as np
import pandas as pd
import pytest

from financial_scraper import FinancialScorer


@pytest.fixture(scope="module")
def scorer():
    return FinancialScorer()


# --- Helper for the revenue scorer (takes a DataFrame, not a list) ---
def rev_df(yoy_newest_first, latest_year=2025, latest_month=6):
    """Build a monthly-revenue DataFrame (newest-first) for the non-CNY path.

    latest_month must not be 2, otherwise the Lunar-New-Year branch triggers.
    """
    assert latest_month != 2, "use a non-Feb latest month for the standard path"
    rows = []
    y, m = latest_year, latest_month
    for yoy in yoy_newest_first:
        rows.append({"date": f"{y}-{m:02d}", "year": y, "month": m,
                     "revenue": 1000.0, "yoy": float(yoy)})
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    return pd.DataFrame(rows)


# =====================================================================
# 1. Monthly Revenue YoY  (scoring_rules.md §1)
# =====================================================================
class TestRevenue:
    def test_insufficient_rows_is_zero(self, scorer):
        assert scorer.score_revenue(rev_df([30, 30, 30, 30, 30])) == 0  # 5 rows

    def test_empty_is_zero(self, scorer):
        assert scorer.score_revenue(pd.DataFrame()) == 0

    def test_negative_average_is_zero(self, scorer):
        assert scorer.score_revenue(rev_df([5, -10, -10, -10, -10, -10])) == 0

    def test_latest_month_negative_is_zero(self, scorer):
        assert scorer.score_revenue(rev_df([-1, 30, 30, 30, 30, 30])) == 0

    def test_recent_three_month_decline_is_one(self, scorer):
        # avg > 0 but M2 > M1 > M0 (strictly decreasing) -> 1
        assert scorer.score_revenue(rev_df([10, 20, 30, 40, 40, 40])) == 1

    def test_had_negative_month_is_two(self, scorer):
        # avg positive, not decreasing, but a historical month was negative -> 2
        assert scorer.score_revenue(rev_df([30, 20, 25, -5, 40, 40])) == 2

    def test_high_growth_rising_is_four(self, scorer):
        # all > 0, avg > 25, M0 >= M1 -> 4
        assert scorer.score_revenue(rev_df([40, 30, 30, 30, 30, 30])) == 4

    def test_mid_growth_rising_is_three(self, scorer):
        # all > 0, 10 <= avg <= 25, M0 >= M1 -> 3
        assert scorer.score_revenue(rev_df([20, 15, 15, 12, 12, 12])) == 3

    def test_mid_growth_not_rising_is_two(self, scorer):
        # all > 0, avg in band but M0 < M1 and not decreasing-3 -> 2 (其他)
        assert scorer.score_revenue(rev_df([10, 15, 10, 12, 13, 14])) == 2

    def test_cny_branch_combines_jan_feb(self, scorer):
        # Latest month == 2: M0 = combined Jan+Feb YoY vs prior-year Jan+Feb.
        # c1=c2=130, p1=p2=100 -> M0 = (260-200)/200*100 = 30; prior yoy all 30
        # -> avg 30 (>25), M0 >= M1 -> 4
        rows = [
            {"year": 2025, "month": 2, "revenue": 130.0, "yoy": 99.0},
            {"year": 2025, "month": 1, "revenue": 130.0, "yoy": 99.0},
            {"year": 2024, "month": 12, "revenue": 900.0, "yoy": 30.0},
            {"year": 2024, "month": 11, "revenue": 900.0, "yoy": 30.0},
            {"year": 2024, "month": 10, "revenue": 900.0, "yoy": 30.0},
            {"year": 2024, "month": 9, "revenue": 900.0, "yoy": 30.0},
            {"year": 2024, "month": 2, "revenue": 100.0, "yoy": 30.0},
            {"year": 2024, "month": 1, "revenue": 100.0, "yoy": 30.0},
        ]
        df = pd.DataFrame([{**r, "date": f"{r['year']}-{r['month']:02d}"} for r in rows])
        assert scorer.score_revenue(df) == 4

    def test_cny_branch_missing_prior_year_is_zero(self, scorer):
        # Latest month == 2 but prior-year Jan/Feb rows absent -> except -> 0
        rows = [
            {"year": 2025, "month": 2, "revenue": 130.0, "yoy": 30.0},
            {"year": 2025, "month": 1, "revenue": 130.0, "yoy": 30.0},
            {"year": 2024, "month": 12, "revenue": 900.0, "yoy": 30.0},
            {"year": 2024, "month": 11, "revenue": 900.0, "yoy": 30.0},
            {"year": 2024, "month": 10, "revenue": 900.0, "yoy": 30.0},
            {"year": 2024, "month": 9, "revenue": 900.0, "yoy": 30.0},
        ]
        df = pd.DataFrame([{**r, "date": f"{r['year']}-{r['month']:02d}"} for r in rows])
        assert scorer.score_revenue(df) == 0

    @pytest.mark.xfail(reason="Code returns 3 for any M0<M1 when avg>25; "
                              "scoring_rules.md §1 restricts the 3-point 微回檔 "
                              "tier to drops <50% (else 2). Known code/spec gap.")
    def test_high_growth_large_recent_drop_should_be_two(self, scorer):
        # all>0, avg>25, M0<M1 with drop (40->10) = 75% >= 50%.
        # Not caught by decreasing-3 (M2=30 not > M1=40). Spec -> 2, code -> 3.
        assert scorer.score_revenue(rev_df([10, 40, 30, 40, 40, 40])) == 2


# =====================================================================
# 2. Operating Profit Margin  (scoring_rules.md §2)
# =====================================================================
class TestOperatingMargin:
    @pytest.mark.parametrize("margins,expected", [
        ([10, 10, 10],            0),   # < 4 quarters
        ([-1, 20, 20, 20],        0),   # Q0 < 0
        ([-5, -5, -5, -5],        0),   # avg < 0
        ([8, 20, 20, 20],         1),   # recent drop (20->8) >= 20%
        ([4, 4, 4, 4],            1),   # avg < 5
        ([20, 20, 20, 20],        4),   # stable, avg >= 15
        ([14, 12, 12, 12],        4),   # stable, 10<=avg<15, Q0 > Q1
        ([11, 12, 12, 13],        3),   # stable, 10<=avg<15, Q0 <= Q1
        ([9, 7, 7, 7],            3),   # stable, 5<=avg<10, Q0 > Q1
        ([7, 7, 7, 7],            2),   # stable, 5<=avg<10, no growth
        ([20, 20, 20, 30],        2),   # historical drop (30->20)=33% -> unstable
    ])
    def test_tiers(self, scorer, margins, expected):
        assert scorer.score_operating_profit_margin(margins) == expected

    def test_nan_is_zero(self, scorer):
        assert scorer.score_operating_profit_margin([np.nan, 10, 10, 10]) == 0


# =====================================================================
# 3. Net Profit YoY Growth  (scoring_rules.md §3)
# =====================================================================
class TestNetProfitGrowth:
    @pytest.mark.parametrize("rates,expected", [
        ([10, 10],                0),   # insufficient
        ([-5, -10, 20, 20],       0),   # two most recent negative
        ([-5, 10, 10, 10],        1),   # Q0 negative
        ([10, -5, -5, 10],        1),   # >= 2 negatives
        ([10, 20, 30, 5],         1),   # decreasing 3q and Q0 < 50
        ([10, -5, 10, 10],        2),   # turnaround: Q1 < 0, Q0 > 0
        ([10, 30, 20, 20],        2),   # sharp drop (30->10) > 50%
        ([60, 55, 70, 10],        4),   # super growth: last 3 >= 50
        ([30, 20, 10, 5],         4),   # accelerating: all>0, Q0 > Q1
        ([15, 20, 10, 10],        3),   # steady: two positive, no big drop
    ])
    def test_tiers(self, scorer, rates, expected):
        assert scorer.score_net_profit_growth(rates) == expected

    def test_nan_is_zero(self, scorer):
        assert scorer.score_net_profit_growth([np.nan, 10, 10, 10]) == 0


# =====================================================================
# 4. EPS (TTM)  (scoring_rules.md §4)
# =====================================================================
class TestEps:
    @pytest.mark.parametrize("eps,expected", [
        ([1, 1, 1],               0),   # insufficient
        ([-1, -1, -1, -1],        0),   # cumulative loss
        ([-0.5, 2, 2, 2],         1),   # latest quarter loss
        ([0.2, 0.2, 0.2, 0.2],    1),   # 0 <= sum <= 1
        ([0.25, 0.25, 0.25, 0.25],1),   # boundary sum == 1
        ([2, 2, 2, 2],            4),   # sum 8 > 5
        ([1, 1, 1, 1],            3),   # sum 4 in (3, 5]
        ([1.25, 1.25, 1.25, 1.25],3),   # boundary sum == 5
        ([0.5, 0.5, 0.5, 0.5],    2),   # sum 2 in (1, 3]
        ([0.75, 0.75, 0.75, 0.75],2),   # boundary sum == 3
    ])
    def test_tiers(self, scorer, eps, expected):
        assert scorer.score_eps(eps) == expected

    def test_nan_is_zero(self, scorer):
        assert scorer.score_eps([np.nan, 2, 2, 2]) == 0


# =====================================================================
# 5. Inventory Turnover  (scoring_rules.md §5)
# =====================================================================
# A metrics dict that passes the low-inventory-industry gate.
NORMAL_METRICS = {"inv_q": 10, "rev_q": 100, "inv_y": 10, "rev_y": 100}


class TestInventory:
    def test_metrics_none_is_unscorable(self, scorer):
        assert scorer.score_inventory([2, 2, 2, 2], None) == "無法評分"

    def test_low_inventory_quarter_is_skipped(self, scorer):
        m = {"inv_q": 1, "rev_q": 100, "inv_y": 10, "rev_y": 100}  # iq/rq = 1% < 4%
        assert scorer.score_inventory([2, 2, 2, 2], m) == "不評分"

    def test_low_inventory_year_is_skipped(self, scorer):
        m = {"inv_q": 10, "rev_q": 100, "inv_y": 0.5, "rev_y": 100}  # iy/ry = 0.5% < 1%
        assert scorer.score_inventory([2, 2, 2, 2], m) == "不評分"

    @pytest.mark.parametrize("turnover,expected", [
        ([2, 2, 2],               0),   # insufficient
        ([0.7, 1.0, 1.0, 1.0],    0),   # recent drop (1.0->0.7)=30% > 20%
        ([1.0, 1.0, 1.3, 1.0],    1),   # historical drop (1.3->1.0)=23% > 20%
        ([0.8, 0.9, 1.1, 1.1],    2),   # slow 2q decline, cumulative > 20%
        ([2, 2, 2, 2],            4),   # stable, avg >= 1.5
        ([1, 1, 1, 1],            3),   # stable, avg < 1.5
    ])
    def test_tiers(self, scorer, turnover, expected):
        assert scorer.score_inventory(turnover, NORMAL_METRICS) == expected

    def test_nan_is_zero(self, scorer):
        assert scorer.score_inventory([np.nan, 2, 2, 2], NORMAL_METRICS) == 0


# =====================================================================
# 6. Free Cash Flow  (scoring_rules.md §6)
# =====================================================================
class TestFreeCashFlow:
    @pytest.mark.parametrize("fcf,expected", [
        ([1, 1, 1, 1, 1],             0),   # insufficient (< 6)
        ([-1, -1, -1, -1, -1, -1],    0),   # Sum6 <= 0 and Sum4 <= 0
        ([1, 1, 1, 1, 1, 1],          4),   # all six positive
        ([1, 1, 1, 1, -0.5, 1],       3),   # Sum6 > 0 and Sum4 > 0
        ([2, 2, 2, 2, -5, -5],        2),   # Sum6 <= 0 but Sum4 > 0
        ([-3, -3, 2, 2, 5, 5],        1),   # Sum6 > 0 but Sum4 <= 0
    ])
    def test_tiers(self, scorer, fcf, expected):
        assert scorer.score_fcf(fcf) == expected

    def test_nan_is_zero(self, scorer):
        assert scorer.score_fcf([np.nan, 1, 1, 1, 1, 1]) == 0
