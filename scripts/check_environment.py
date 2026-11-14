"""Offline smoke check for Google Sheets-shaped rows -> plots, without credentials."""

import sys
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from price_viewer.analysis import summarize_prices  # noqa: E402
from price_viewer.demo_data import make_demo_records  # noqa: E402
from price_viewer.charts import price_line_chart  # noqa: E402


def main() -> None:
    if sys.version_info[:3] != (3, 12, 11):
        raise RuntimeError(f"Python 3.12.11が必要です: {sys.version}")
    data = make_demo_records()
    first = data.loc[data["product_id"] == "001"]
    summary = summarize_prices(first)
    if summary is None or round(summary.change_pct or 0, 2) != -12:
        raise RuntimeError("架空価格の変化率が正しくありません")
    html = price_line_chart(first, "架空データ").to_html(include_plotlyjs=True)
    if "Plotly.newPlot" not in html:
        raise RuntimeError("グラフHTMLを生成できません")
    print(f"Python {sys.version.split()[0]}")
    for package in ("pandas", "plotly", "streamlit", "google-auth", "requests", "ruff", "pytest"):
        print(f"{package}: {version(package)}")
    print("OK: 2シート形式の架空データ→価格変化率→グラフ（API呼び出しなし）")


if __name__ == "__main__":
    main()
