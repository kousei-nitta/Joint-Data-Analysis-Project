"""実データを使わず、Excel→データ加工→グラフ生成の依存関係を確認する。"""

import sys
from importlib.metadata import version
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit  # noqa: F401
from openpyxl import Workbook


def main() -> None:
    if sys.version_info[:3] != (3, 12, 11):
        raise RuntimeError(f"Python 3.12.11が必要です: {sys.version}")

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "価格履歴"
    sheet.append(["確認日", "商品ID", "価格", "備考"])
    sheet.append(["2026-01-01", "001", 100, None])
    sheet.append(["2026-01-02", "001", 120, None])
    buffer = BytesIO()
    workbook.save(buffer)
    workbook.close()
    buffer.seek(0)
    frame = pd.read_excel(
        buffer, sheet_name="価格履歴", engine="openpyxl", dtype={"商品ID": "string"}
    )
    if frame["商品ID"].tolist() != ["001", "001"]:
        raise RuntimeError("Excelの商品IDの先頭ゼロが失われました")
    if frame["価格"].tolist() != [100, 120]:
        raise RuntimeError("Excelの価格を読み取れませんでした")
    frame["確認日"] = pd.to_datetime(frame["確認日"])
    figure = px.line(frame, x="確認日", y="価格", color="商品ID")
    if len(figure.data) != 1 or list(figure.data[0].y) != [100, 120]:
        raise RuntimeError("グラフのデータが読み取り結果と一致しません")
    html = figure.to_html(include_plotlyjs=True, full_html=True)
    if "Plotly.newPlot" not in html:
        raise RuntimeError("グラフをHTMLに変換できませんでした")

    print(f"Python {sys.version.split()[0]}")
    for package in ("pandas", "openpyxl", "plotly", "streamlit", "ruff", "pytest"):
        print(f"{package}: {version(package)}")
    print("OK: Excel読み込み、商品IDの保持、グラフとHTMLの生成")


if __name__ == "__main__":
    main()
