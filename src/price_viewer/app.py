"""Local Streamlit price-history viewer (Excel is always read-only)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# The existing pyproject intentionally uses tool.uv.package=false.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from price_viewer.analysis import filter_prices, summarize_prices, with_price_changes  # noqa: E402
from price_viewer.charts import price_line_chart  # noqa: E402
from price_viewer.demo_data import make_demo_workbook  # noqa: E402
from price_viewer.io import load_price_workbook  # noqa: E402
from price_viewer.validation import WorkbookValidationError  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    st.set_page_config(page_title="商品価格分析デモ", page_icon="📈", layout="wide")
    st.title("Excel商品価格の推移分析")
    st.caption("中国景気との関連性は未検証。ここでは価格の観測・集計のみを行います。")

    source = st.radio(
        "データの入力元",
        ["架空デモデータ", "Excelをアップロード", "リポジトリのExcel"],
        horizontal=True,
    )
    if source == "架空デモデータ":
        st.warning("この画面のデータはすべて架空です。実際の市場価格ではありません。")
        workbook = make_demo_workbook()
    elif source == "Excelをアップロード":
        workbook = st.file_uploader("product_prices.xlsx形式のファイル", type=["xlsx"])
        if workbook is None:
            st.info("2シートのExcelファイルを選んでください。")
            st.stop()
    else:
        workbook = ROOT / "product_prices.xlsx"
        st.info("リポジトリのExcelを読み取り専用で開きます。内容は保存・変更しません。")

    try:
        records = load_price_workbook(workbook)
    except WorkbookValidationError as error:
        st.error("Excelを分析できません。以下の入力内容を修正してください。")
        st.dataframe(pd.DataFrame([item.as_dict() for item in error.issues]))
        st.stop()

    choices = records[["product_id", "product_name"]].drop_duplicates().sort_values("product_id")
    labels = {
        str(row.product_id): f"{row.product_name}（ID: {row.product_id}）"
        for row in choices.itertuples(index=False)
    }
    selected_id = st.selectbox("商品を選択", list(labels), format_func=lambda key: labels[key])
    product_records = filter_prices(records, selected_id)
    lower = product_records["date"].min().date()
    upper = product_records["date"].max().date()
    left, right = st.columns(2)
    with left:
        start = st.date_input("開始日", value=lower, min_value=lower, max_value=upper)
    with right:
        end = st.date_input("終了日", value=upper, min_value=lower, max_value=upper)
    if start > end:
        st.error("開始日は終了日以前にしてください。")
        st.stop()

    selected = filter_prices(records, selected_id, start, end)
    summary = summarize_prices(selected)
    if summary is None:
        st.info("指定期間に価格記録がありません。")
        st.stop()

    first, last, change = st.columns(3)
    first.metric("期間内の最初の観測価格", f"¥{summary.first_price_jpy:,.0f}")
    last.metric("期間内の最後の観測価格", f"¥{summary.last_price_jpy:,.0f}")
    change.metric(
        "期間内の変化率",
        "算出不可" if summary.change_pct is None else f"{summary.change_pct:+.2f}%",
    )
    st.caption(
        f"観測 {summary.observations}件 / {summary.start_date} 〜 {summary.end_date}。"
        " 指定期間内の最初と最後の観測値を比較し、欠測日の補完はしません。"
        " 金額単位は日本円です。"
    )
    figure = price_line_chart(selected, labels[selected_id])
    st.plotly_chart(figure, use_container_width=True)
    table = with_price_changes(selected)[
        ["date", "product_id", "product_name", "price_jpy", "change_jpy", "change_pct", "note"]
    ].rename(
        columns={
            "date": "確認日",
            "product_id": "商品ID",
            "product_name": "商品名",
            "price_jpy": "価格（円）",
            "change_jpy": "前回比（円）",
            "change_pct": "前回比（%）",
            "note": "備考",
        }
    )
    st.subheader("分析に使った観測データ")
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button(
        "グラフをHTMLで保存",
        data=figure.to_html(full_html=True, include_plotlyjs=True).encode("utf-8"),
        file_name="price_chart_demo.html" if source == "架空デモデータ" else "price_chart.html",
        mime="text/html",
    )
    st.download_button(
        "数表をCSVで保存",
        data=table.to_csv(index=False).encode("utf-8-sig"),
        file_name="prices_demo.csv" if source == "架空デモデータ" else "prices.csv",
        mime="text/csv",
    )
    st.caption("出力を公開する前に、価格の出典・利用許諾・実測/架空区分を確認してください。")


if __name__ == "__main__":
    main()
