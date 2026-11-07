"""Deterministic price calculations; no AI-invented numeric results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True)
class PriceSummary:
    product_id: str
    product_name: str
    start_date: date
    end_date: date
    first_price_jpy: float
    last_price_jpy: float
    change_jpy: float | None
    change_pct: float | None
    observations: int


def filter_prices(
    frame: pd.DataFrame,
    product_id: str,
    start: date | None = None,
    end: date | None = None,
) -> pd.DataFrame:
    """Use observed records inside selected bounds; do not interpolate missing days."""
    selected = frame.loc[frame["product_id"] == product_id].copy()
    if start is not None:
        selected = selected.loc[selected["date"] >= pd.Timestamp(start)]
    if end is not None:
        selected = selected.loc[selected["date"] <= pd.Timestamp(end)]
    return selected.sort_values("date").reset_index(drop=True)


def with_price_changes(frame: pd.DataFrame) -> pd.DataFrame:
    """Previous *observed* price, not yesterday's inferred price."""
    result = frame.sort_values(["product_id", "date"]).copy()
    result["previous_price_jpy"] = result.groupby("product_id")["price_jpy"].shift()
    result["change_jpy"] = result["price_jpy"] - result["previous_price_jpy"]
    result["change_pct"] = 100 * result["change_jpy"] / result["previous_price_jpy"]
    return result.reset_index(drop=True)


def summarize_prices(frame: pd.DataFrame) -> PriceSummary | None:
    if frame.empty:
        return None
    ordered = frame.sort_values("date")
    first, last = ordered.iloc[0], ordered.iloc[-1]
    if first["product_id"] != last["product_id"]:
        raise ValueError("1商品ずつ集計してください")
    count = len(ordered)
    first_price, last_price = float(first["price_jpy"]), float(last["price_jpy"])
    change = last_price - first_price if count > 1 else None
    ratio = 100 * change / first_price if change is not None and first_price > 0 else None
    return PriceSummary(
        product_id=str(first["product_id"]),
        product_name=str(first["product_name"]),
        start_date=first["date"].date(),
        end_date=last["date"].date(),
        first_price_jpy=first_price,
        last_price_jpy=last_price,
        change_jpy=change,
        change_pct=ratio,
        observations=count,
    )
