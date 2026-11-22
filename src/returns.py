"""Price returns of each IPO since its listing, for every price snapshot available."""
import numpy as np
import pandas as pd


def years_between(start: pd.Series, end: pd.Series) -> pd.Series:
    return (pd.to_datetime(end) - pd.to_datetime(start)).dt.days / 365.25


def compute(ipos: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    """One row per (IPO, price date): total price return and annualised return."""
    df = prices.merge(ipos[["ticker", "company", "sector", "ipo_date", "ipo_price_mad"]], on="ticker", how="inner")
    df = df[df["ipo_price_mad"].notna() & (pd.to_datetime(df["date"]) > pd.to_datetime(df["ipo_date"]))].copy()
    df["years_since_ipo"] = years_between(df["ipo_date"], df["date"])
    df["total_return"] = df["price_mad"] / df["ipo_price_mad"] - 1
    with np.errstate(invalid="ignore"):
        df["annualised_return"] = np.where(df["years_since_ipo"] >= 1,
                                           (1 + df["total_return"]) ** (1 / df["years_since_ipo"]) - 1, np.nan)
    return df.sort_values(["date", "total_return"], ascending=[True, False]).reset_index(drop=True)


def latest(returns: pd.DataFrame) -> pd.DataFrame:
    """Most recent snapshot for each IPO."""
    return returns.sort_values("date").groupby("ticker").tail(1).sort_values("total_return", ascending=False)
