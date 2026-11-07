"""Generate offline demo HTML/CSV from an in-memory xlsx; no real data used."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from price_viewer.analysis import filter_prices, summarize_prices, with_price_changes  # noqa: E402
from price_viewer.charts import price_line_chart  # noqa: E402
from price_viewer.demo_data import make_demo_workbook  # noqa: E402
from price_viewer.io import load_price_workbook  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="架空データでExcel→分析→HTML/CSVを検証")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "demo")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    data = load_price_workbook(make_demo_workbook())
    for product_id in sorted(data["product_id"].unique()):
        selected = filter_prices(data, product_id)
        summary = summarize_prices(selected)
        if summary is None:
            continue
        name = f"demo_{product_id}"
        graph = price_line_chart(selected, f"{summary.product_name}（架空データ）")
        (args.output_dir / f"{name}.html").write_text(
            graph.to_html(full_html=True, include_plotlyjs=True), encoding="utf-8"
        )
        with_price_changes(selected).to_csv(args.output_dir / f"{name}.csv", index=False)
        print(
            f"{product_id}: {summary.observations}件、"
            f"{summary.first_price_jpy:,.0f}円→{summary.last_price_jpy:,.0f}円、"
            f"変化率={summary.change_pct:+.2f}%（架空データ）"
        )
    print(f"保存先: {args.output_dir}")


if __name__ == "__main__":
    main()
