"""Analyze an existing workbook into local HTML and CSV files (never modify input)."""

from __future__ import annotations

import argparse
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from price_viewer.analysis import filter_prices, summarize_prices, with_price_changes  # noqa: E402
from price_viewer.charts import price_line_chart  # noqa: E402
from price_viewer.io import load_price_workbook  # noqa: E402
from price_viewer.validation import WorkbookValidationError  # noqa: E402


def analyze_file(excel: Path, output_dir: Path) -> list[Path]:
    """Export plots and corresponding tables for each product in the xlsx file."""
    data = load_price_workbook(excel)
    output_dir.mkdir(parents=True, exist_ok=True)
    created = []
    for identifier in sorted(data["product_id"].unique()):
        rows = filter_prices(data, identifier)
        summary = summarize_prices(rows)
        if summary is None:
            continue
        # Product IDs can be arbitrary text; never trust them as filesystem paths.
        safe_id = sha256(identifier.encode("utf-8")).hexdigest()[:12]
        basename = f"product_{safe_id}"
        graph = price_line_chart(rows, f"{summary.product_name}（ID: {identifier}）")
        html_path = output_dir / f"{basename}.html"
        csv_path = output_dir / f"{basename}.csv"
        html_path.write_text(graph.to_html(full_html=True, include_plotlyjs=True), encoding="utf-8")
        with_price_changes(rows).to_csv(csv_path, index=False, encoding="utf-8-sig")
        created.extend([html_path, csv_path])
        print(
            f"商品ID={identifier}、{summary.observations}件、"
            f"変化率={'算出不可' if summary.change_pct is None else f'{summary.change_pct:+.2f}%'}"
        )
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Excelの商品価格を検証しHTML/CSVを出力")
    parser.add_argument("--excel", type=Path, default=ROOT / "product_prices.xlsx")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "analysis")
    args = parser.parse_args()
    try:
        files = analyze_file(args.excel, args.output_dir)
    except WorkbookValidationError as error:
        print("Excelの入力内容を修正してください:", file=sys.stderr)
        for issue in error.issues:
            print(f"- {issue.as_dict()}", file=sys.stderr)
        return 1
    print(f"{len(files)}ファイルを {args.output_dir} に保存しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())
