"""Generate HTML/CSV from fictional rows, without Google credentials or network access."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from price_viewer.analysis import filter_prices, summarize_prices, with_price_changes  # noqa: E402
from price_viewer.charts import price_line_chart  # noqa: E402
from price_viewer.demo_data import make_demo_records  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="架空のGoogle Sheets相当データで分析する")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "demo")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data = make_demo_records()
    for product_id in sorted(data["product_id"].unique()):
        selected = filter_prices(data, product_id)
        summary = summarize_prices(selected)
        if summary is None:
            continue
        stem = f"demo_{product_id}"
        graph = price_line_chart(selected, f"{summary.product_name}（架空データ）")
        (args.output_dir / f"{stem}.html").write_text(
            graph.to_html(full_html=True, include_plotlyjs=True), encoding="utf-8"
        )
        with_price_changes(selected).to_csv(args.output_dir / f"{stem}.csv", index=False)
        print(f"{product_id}: {summary.observations}件、変化率={summary.change_pct:+.2f}%（架空）")
    print(f"出力先: {args.output_dir}")


if __name__ == "__main__":
    main()
