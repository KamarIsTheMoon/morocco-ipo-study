"""Run the study.

    python -m src.run

Reads data/ipos.csv and data/prices.csv, writes output/results.md and charts.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .returns import compute, latest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
NAVY = "#1F3864"


def charts(ipos: pd.DataFrame, rets: pd.DataFrame) -> None:
    d = ipos.dropna(subset=["amount_raised_mad_m"]).sort_values("ipo_date")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(d["company"] + "\n" + d["ipo_date"].str[:4], d["amount_raised_mad_m"], color=NAVY)
    ax.set_ylabel("Amount raised (MAD m)")
    ax.set_title("Casablanca IPOs: amount raised")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    fig.tight_layout(); fig.savefig(OUT / "amount_raised.png", dpi=150); plt.close(fig)

    d = ipos.dropna(subset=["oversubscription_x"]).sort_values("ipo_date")
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.bar(d["company"] + "\n" + d["ipo_date"].str[:4], d["oversubscription_x"], color=NAVY)
    for i, v in enumerate(d["oversubscription_x"]):
        ax.text(i, v + 1, f"{v:g}x", ha="center", fontsize=9)
    ax.set_ylabel("Times oversubscribed")
    ax.set_title("How many times each IPO was oversubscribed")
    fig.tight_layout(); fig.savefig(OUT / "oversubscription.png", dpi=150); plt.close(fig)

    snap = rets[rets["date"] == "2022-12-14"]
    if not snap.empty:
        fig, ax = plt.subplots(figsize=(7, 3.8))
        colors = [NAVY if v >= 0 else "#C00000" for v in snap["total_return"]]
        ax.barh(snap["company"], snap["total_return"] * 100, color=colors)
        ax.axvline(0, color="grey", linewidth=0.8)
        ax.set_xlabel("Price return since IPO (%)")
        ax.set_title("Return since IPO, as of 14 December 2022")
        ax.invert_yaxis()
        fig.tight_layout(); fig.savefig(OUT / "returns_2022.png", dpi=150); plt.close(fig)


def table(df: pd.DataFrame) -> str:
    t = df[["company", "sector", "ipo_date", "ipo_price_mad", "date", "price_mad", "total_return", "annualised_return"]].copy()
    t["total_return"] = t["total_return"].map("{:+.1%}".format)
    t["annualised_return"] = t["annualised_return"].map(lambda v: f"{v:+.1%}" if pd.notna(v) else "")
    t.columns = ["Company", "Sector", "IPO date", "IPO price", "Price date", "Price", "Return since IPO", "Per year"]
    return t.to_markdown(index=False)


def main() -> pd.DataFrame:
    ipos = pd.read_csv(ROOT / "data" / "ipos.csv")
    prices = pd.read_csv(ROOT / "data" / "prices.csv")
    rets = compute(ipos, prices)
    OUT.mkdir(exist_ok=True)
    charts(ipos, rets)
    md = "\n".join([
        "# Results", "",
        f"{len(ipos)} IPOs since 2015, {ipos['amount_raised_mad_m'].sum():,.0f} MAD m offered in total (maximum amounts for SGTM and T2S).", "",
        "## Every price snapshot", "", table(rets), "",
        "## Latest snapshot per company", "", table(latest(rets)), "",
        "Price returns only, dividends not included.", ""])
    rets.to_csv(OUT / "returns.csv", index=False)
    (OUT / "results.md").write_text(md, encoding="utf-8")
    print(md)
    return rets


if __name__ == "__main__":
    main()
