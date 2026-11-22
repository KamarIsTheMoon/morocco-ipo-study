import math

import pandas as pd
import pytest

from src.returns import compute, latest


def data():
    ipos = pd.DataFrame({"ticker": ["A", "B", "C"], "company": ["A", "B", "C"], "sector": ["x"] * 3,
                         "ipo_date": ["2020-01-01", "2021-01-01", "2022-01-01"], "ipo_price_mad": [100, 200, None]})
    prices = pd.DataFrame({"ticker": ["A", "A", "B", "C", "B"],
                           "date": ["2022-01-01", "2024-01-01", "2021-07-01", "2023-01-01", "2020-06-01"],
                           "price_mad": [121, 150, 180, 10, 999]})
    return ipos, prices


def test_total_and_annualised_return():
    r = compute(*data())
    a = r[(r.ticker == "A") & (r.date == "2022-01-01")].iloc[0]
    assert a.total_return == pytest.approx(0.21)
    assert a.annualised_return == pytest.approx(0.10, abs=0.001)   # 1.21 over ~2 years


def test_short_periods_are_not_annualised():
    r = compute(*data())
    b = r[r.ticker == "B"].iloc[0]
    assert b.total_return == pytest.approx(-0.10)
    assert math.isnan(b.annualised_return)


def test_ignores_missing_ipo_price_and_prices_before_ipo():
    r = compute(*data())
    assert "C" not in r.ticker.values
    assert not ((r.ticker == "B") & (r.date == "2020-06-01")).any()


def test_latest_keeps_most_recent_snapshot():
    l = latest(compute(*data()))
    assert l[l.ticker == "A"].iloc[0].date == "2024-01-01"
