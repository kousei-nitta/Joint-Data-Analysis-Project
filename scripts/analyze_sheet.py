"""Export price charts from a private Google Sheet without modifying its contents."""

from __future__ import annotations

import argparse
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from price_viewer.analysis import filter_prices, summarize_prices, with_price_changes  # noqa: E402
from price_viewer.charts import price_line_chart  # noqa: E402
from price_viewer.sheets import SheetAccessError, load_price_sheet  # noqa: E402
from price_viewer.validation import WorkbookValidationError  # noqa: E402


def analyze_sheet(spreadsheet_id: str | None, output_dir: Path) -> list[Path]:
    """One live read, then export all product series as local HTML/CSV."""
    records = load_price_sheet(spreadsheet_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for product_id in sorted(records["product_id"].unique()):
        rows = filter_prices(records, product_id)
        summary = summarize_prices(rows)
        if summary is None:
            continue
        safe_id = sha256(product_id.encode("utf-8")).hexdigest()[:12]
        stem = f"product_{safe_id}"
        graph = price_line_chart(rows, f"{summary.product_name}（ID: {product_id}）")
        html = output_dir / f"{stem}.html"
        csv = output_dir / f"{stem}.csv"
        html.write_text(graph.to_html(include_plotlyjs=True, full_html=True), encoding="utf-8")
        with_price_changes(rows).to_csv(csv, encoding="utf-8-sig", index=False)
        created.extend((html, csv))
        print(f"{product_id}: {summary.observations}件、変化率={summary.change_pct:+.2f}%")
    return created


def main() -> int:
    parser = argparse.ArgumentParser(
        description="非公開Googleスプレッドシートから価格推移HTMLとCSVを作成"
    )
    parser.add_argument("--spreadsheet-id", default=None, help="省略時は環境変数GOOGLE_SHEET_ID")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "analysis")
    args = parser.parse_args()
    try:
        paths = analyze_sheet(args.spreadsheet_id, args.output_dir)
    except (SheetAccessError, WorkbookValidationError) as error:
        print(f"読み込み/入力エラー: {error}", file=sys.stderr)
        if isinstance(error, WorkbookValidationError):
            for issue in error.issues:
                print(issue.as_dict(), file=sys.stderr)
        return 1
    print(f"{len(paths)}ファイルを {args.output_dir} に保存しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())
