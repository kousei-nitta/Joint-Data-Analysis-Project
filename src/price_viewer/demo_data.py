"""Deterministic *fictional* rows, matching private Google Sheets response values."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from price_viewer.validation import validate_frames


def make_demo_records() -> pd.DataFrame:
    products = (
        ("001", "架空商品A", (100000, 96000, 90000, 92000, 88000)),
        ("002", "架空商品B", (85000, 87000, 89000, 86000, 91000)),
        ("003", "架空商品C", (50000, 49500, 48000, 45000, 47000)),
    )
    master = pd.DataFrame(
        [[product_id, name] for product_id, name, _ in products],
        columns=["商品ID", "商品名"],
    )
    rows = []
    for product_id, _, amounts in products:
        for i, amount in enumerate(amounts):
            rows.append(
                [
                    (date(2026, 1, 1) + timedelta(days=7 * i)).isoformat(),
                    product_id,
                    amount,
                    "デモ用の架空価格",
                ]
            )
    # The real API may return unordered observations; validation sorts them.
    rows.reverse()
    history = pd.DataFrame(rows, columns=["確認日", "商品ID", "価格", "備考"])
    return validate_frames(history, master)
