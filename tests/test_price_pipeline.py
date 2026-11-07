"""Tests use fictional, memory-only workbooks; never open product_prices.xlsx."""

from datetime import datetime
from io import BytesIO

import pandas as pd
import pytest
from openpyxl import Workbook

from price_viewer.analysis import filter_prices, summarize_prices, with_price_changes
from price_viewer.charts import price_line_chart
from price_viewer.demo_data import make_demo_workbook
from price_viewer.io import load_price_workbook
from price_viewer.validation import WorkbookValidationError


def workbook_bytes(
    history=None,
    products=None,
    history_header=None,
    include_master=True,
):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "価格履歴"
    sheet.append(history_header or ["確認日", "商品ID", "価格", "備考"])
    for row in history if history is not None else [
        [datetime(2026, 1, 8), "001", 90000, None],
        [datetime(2026, 1, 1), "001", 100000, "架空"],
    ]:
        sheet.append(row)
    if include_master:
        master = workbook.create_sheet("商品マスタ")
        master.append(["商品ID", "商品名"])
        for row in products if products is not None else [["001", "架空商品A"]]:
            master.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    workbook.close()
    buffer.seek(0)
    return buffer


def issues_from(buffer):
    with pytest.raises(WorkbookValidationError) as caught:
        load_price_workbook(buffer)
    return caught.value.issues


def test_end_to_end_sort_percent_and_html():
    data = load_price_workbook(workbook_bytes())
    assert data["date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-01-01", "2026-01-08"]
    assert data["product_id"].tolist() == ["001", "001"]
    summary = summarize_prices(data)
    assert summary is not None
    assert summary.change_pct == pytest.approx(-10.0)
    changes = with_price_changes(data)
    assert pd.isna(changes.loc[0, "change_pct"])
    assert changes.loc[1, "change_jpy"] == -10000
    chart = price_line_chart(data, "架空データ")
    assert list(chart.data[0].y) == [100000, 90000]
    assert "Plotly.newPlot" in chart.to_html(include_plotlyjs=True)


def test_demo_workbook_is_repeatable():
    first = load_price_workbook(make_demo_workbook())
    second = load_price_workbook(make_demo_workbook())
    pd.testing.assert_frame_equal(first, second)
    assert first["product_id"].nunique() == 3
    assert (first["price_jpy"] > 0).all()


def test_original_buffer_is_read_only():
    buffer = workbook_bytes()
    before = buffer.getvalue()
    load_price_workbook(buffer)
    assert buffer.getvalue() == before


@pytest.mark.parametrize(
    "kwargs,expected_column",
    [
        ({"include_master": False}, "シート名"),
        ({"history_header": ["確認日", "商品ID", "備考"]}, "価格"),
        ({"history": [["not-a-date", "001", 100, None]]}, "確認日"),
        ({"history": [[datetime(2026, 1, 1), "999", 100, None]]}, "商品ID"),
        ({"history": [[datetime(2026, 1, 1), "001", "10,000", None]]}, "価格"),
        ({"history": [[datetime(2026, 1, 1), "001", 0, None]]}, "価格"),
        ({"history": [[datetime(2026, 1, 1), "001", -10, None]]}, "価格"),
        ({"history": [[datetime(2026, 1, 1), 1, 100, None]]}, "商品ID"),
        ({"products": [["001", "A"], ["001", "B"]]}, "商品ID"),
        (
            {
                "history": [
                    [datetime(2026, 1, 1), "001", 100, None],
                    [datetime(2026, 1, 1), "001", 200, None],
                ]
            },
            "確認日・商品ID",
        ),
    ],
)
def test_invalid_workbook_reports_excel_location(kwargs, expected_column):
    issues = issues_from(workbook_bytes(**kwargs))
    assert any(issue.column == expected_column for issue in issues)
    assert all(issue.row is None or issue.row >= 1 for issue in issues)


def test_blank_row_ignored_but_missing_value_is_error():
    history = [
        [datetime(2026, 1, 1), "001", 100000, None],
        [None, None, None, None],
        [datetime(2026, 1, 8), "001", 95000, None],
    ]
    records = load_price_workbook(workbook_bytes(history=history))
    assert len(records) == 2
    assert records["excel_row"].tolist() == [2, 4]
    history[1] = [datetime(2026, 1, 7), "001", None, None]
    issues = issues_from(workbook_bytes(history=history))
    assert any(issue.row == 3 and issue.column == "価格" for issue in issues)


def test_filter_period_and_one_observation():
    records = load_price_workbook(workbook_bytes())
    single = filter_prices(records, "001", start=datetime(2026, 1, 8).date())
    assert len(single) == 1
    summary = summarize_prices(single)
    assert summary is not None and summary.change_pct is None
    assert summarize_prices(filter_prices(records, "does-not-exist")) is None


def test_bad_workbook_file_and_oversize():
    issues = issues_from(BytesIO(b"invalid zip"))
    assert issues[0].column == "Excel"
    oversized = BytesIO(b"a" * (20 * 1024 * 1024 + 1))
    issues = issues_from(oversized)
    assert issues[0].column == "容量"


def test_batch_analysis_real_excel_path_is_not_modified(tmp_path):
    from scripts.analyze_workbook import analyze_file

    excel = tmp_path / "fixture.xlsx"
    excel.write_bytes(workbook_bytes().getvalue())
    before = excel.read_bytes()
    paths = analyze_file(excel, tmp_path / "reports")
    assert len(paths) == 2
    assert any(path.suffix == ".html" for path in paths)
    assert any(path.suffix == ".csv" for path in paths)
    assert excel.read_bytes() == before
