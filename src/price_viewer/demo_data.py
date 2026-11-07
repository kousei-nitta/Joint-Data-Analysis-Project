"""Clearly fictional, deterministic .xlsx input for end-to-end demonstrations."""

from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO

from openpyxl import Workbook


def make_demo_workbook() -> BytesIO:
    """Create a workbook in memory; never touch product_prices.xlsx."""
    workbook = Workbook()
    history = workbook.active
    history.title = "価格履歴"
    history.append(["確認日", "商品ID", "価格", "備考"])
    master = workbook.create_sheet("商品マスタ")
    master.append(["商品ID", "商品名"])
    products = (
        ("001", "架空商品A", (100000, 96000, 90000, 92000, 88000)),
        ("002", "架空商品B", (85000, 87000, 89000, 86000, 91000)),
        ("003", "架空商品C", (50000, 49500, 48000, 45000, 47000)),
    )
    for product_id, name, prices in products:
        master.append([product_id, name])
        master.cell(row=master.max_row, column=1).number_format = "@"
        for index, price in enumerate(prices):
            when = datetime(2026, 1, 1) + timedelta(days=7 * index)
            history.append([when, product_id, price, "デモ用の架空価格"])
            history.cell(row=history.max_row, column=1).number_format = "yyyy-mm-dd"
            history.cell(row=history.max_row, column=2).number_format = "@"
    # Deliberately out of date order to exercise sorting on import.
    history.move_range("A2:D2", rows=history.max_row + 1)
    buffer = BytesIO()
    workbook.save(buffer)
    workbook.close()
    buffer.seek(0)
    return buffer
