"""Price analysis uses synthetic Google Sheets-style rows, never real data."""

from datetime import date

import pandas as pd
import pytest

from price_viewer.analysis import filter_prices, summarize_prices, with_price_changes
from price_viewer.charts import price_line_chart
from price_viewer.demo_data import make_demo_records


def test_demo_is_repeatable_and_sorted():
    first = make_demo_records()
    second = make_demo_records()
    pd.testing.assert_frame_equal(first, second)
    assert first["product_id"].nunique() == 3
    assert len(first) == 15
    assert (first["price_jpy"] > 0).all()


def test_change_and_chart():
    data = make_demo_records()
    series = filter_prices(data, "001")
    summary = summarize_prices(series)
    assert summary is not None
    assert summary.change_pct == pytest.approx(-12.0)
    changes = with_price_changes(series)
    assert pd.isna(changes.loc[0, "change_pct"])
    assert changes.iloc[-1]["change_jpy"] == -4000
    chart = price_line_chart(series, "架空データ")
    assert list(chart.data[0].y) == [100000, 96000, 90000, 92000, 88000]
    assert "Plotly.newPlot" in chart.to_html(include_plotlyjs=True)


def test_period_filter_and_single_observation():
    data = make_demo_records()
    one = filter_prices(data, "001", start=date(2026, 1, 29))
    assert len(one) == 1
    summary = summarize_prices(one)
    assert summary is not None and summary.change_pct is None
    assert summarize_prices(filter_prices(data, "not-here")) is None
