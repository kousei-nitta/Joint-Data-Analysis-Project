"""Local Streamlit viewer for private Google Sheets price observations."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from price_viewer.analysis import filter_prices, summarize_prices, with_price_changes  # noqa: E402
from price_viewer.charts import price_line_chart  # noqa: E402
from price_viewer.demo_data import make_demo_records  # noqa: E402
from price_viewer.sheets import SheetAccessError, load_price_sheet  # noqa: E402
from price_viewer.validation import WorkbookValidationError  # noqa: E402


@st.cache_data(ttl=300, show_spinner="Google Sheetsからデータを取得中...")
def _cached_sheet(spreadsheet_id: str) -> pd.DataFrame:
    """One batch read per cache miss, capped to a 5-minute refresh interval."""
    return load_price_sheet(spreadsheet_id)


def main() -> None:
    st.set_page_config(page_title="商品価格分析", page_icon="📈", layout="wide")
    st.title("商品価格の推移分析")
    st.caption("価格は日本円。中国景気との因果性・先行性は未検証です。")

    source = st.radio("入力元", ["架空デモデータ", "非公開Googleスプレッドシート"], horizontal=True)
    if source == "架空デモデータ":
        st.warning("ここに表示する商品・価格はすべて架空です。実際の買取相場ではありません。")
        records = make_demo_records()
    else:
        spreadsheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()
        st.info("シートは読み取り専用です。共有されたGoogleアカウント以外には公開しません。")
        if st.button("最新のデータを再取得"):
            _cached_sheet.clear()
        try:
            records = _cached_sheet(spreadsheet_id)
        except SheetAccessError as error:
            st.error(str(error))
            st.stop()
        except WorkbookValidationError as error:
            st.error("スプレッドシートに入力エラーがあります。該当する行・列を修正してください。")
            st.dataframe(pd.DataFrame([issue.as_dict() for issue in error.issues]))
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
        st.info("指定期間に観測データがありません。")
        st.stop()

    first, last, change = st.columns(3)
    first.metric("期間の最初の観測値", f"¥{summary.first_price_jpy:,.0f}")
    last.metric("期間の最後の観測値", f"¥{summary.last_price_jpy:,.0f}")
    change.metric(
        "期間内の変化率",
        "算出不可" if summary.change_pct is None else f"{summary.change_pct:+.2f}%",
    )
    st.caption(
        f"観測 {summary.observations}件 / {summary.start_date}〜{summary.end_date}。"
        " 欠測日は補完しません。表示金額は日本円です。"
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
    st.subheader("集計に使用した観測データ")
    st.dataframe(table, use_container_width=True, hide_index=True)
    suffix = "_demo" if source == "架空デモデータ" else ""
    st.download_button(
        "グラフをHTMLで保存",
        data=figure.to_html(full_html=True, include_plotlyjs=True).encode("utf-8"),
        file_name=f"price_chart{suffix}.html",
        mime="text/html",
    )
    st.download_button(
        "数表をCSVで保存",
        data=table.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"prices{suffix}.csv",
        mime="text/csv",
    )
    st.caption("ローカル専用。外部公開前に出典と商用利用条件を確認してください。")


if __name__ == "__main__":
    main()
