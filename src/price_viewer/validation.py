"""Validate the existing Japanese Excel template without changing its contents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite
from numbers import Real

import pandas as pd

HISTORY_SHEET = "価格履歴"
PRODUCT_SHEET = "商品マスタ"
HISTORY_COLUMNS = ("確認日", "商品ID", "価格")
PRODUCT_COLUMNS = ("商品ID", "商品名")


@dataclass(frozen=True)
class ValidationIssue:
    sheet: str
    row: int | None
    column: str
    message: str

    def as_dict(self) -> dict[str, str | int | None]:
        return {
            "シート": self.sheet,
            "Excel行": self.row,
            "列": self.column,
            "問題": self.message,
        }


class WorkbookValidationError(ValueError):
    """User-correctable input failures, including precise spreadsheet locations."""

    def __init__(self, issues: list[ValidationIssue]):
        self.issues = issues
        super().__init__("; ".join(issue.message for issue in issues[:3]))


def _text_id(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return value.strip() or None


def _parse_date(value: object) -> pd.Timestamp | None:
    if isinstance(value, (datetime, date, pd.Timestamp)):
        try:
            parsed = pd.Timestamp(value)
            return parsed.normalize() if not pd.isna(parsed) else None
        except (ValueError, TypeError, OverflowError):
            return None
    if isinstance(value, str):
        raw = value.strip()
        if not raw or ("-" not in raw and "/" not in raw):
            return None
        try:
            parsed = pd.to_datetime(raw, errors="raise", format="mixed")
            if pd.isna(parsed) or isinstance(parsed, pd.DatetimeIndex):
                return None
            return pd.Timestamp(parsed).normalize()
        except (ValueError, TypeError, OverflowError):
            return None
    return None


def _price(value: object) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, Real):
        return None
    if not isfinite(float(value)) or value <= 0:
        return None
    return value


def _nonblank_rows(frame: pd.DataFrame) -> pd.DataFrame:
    # Do not reset indices: original Excel rows must remain traceable (header = row 1).
    return frame.dropna(how="all").copy()


def validate_frames(history: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Return normalized records or raise all actionable validation issues.

    The input uses the two-sheet format described in docs/plan.md. One record
    per calendar day and product ID is supported; no averaging or imputation.
    """
    issues: list[ValidationIssue] = []
    for sheet, frame, required in (
        (HISTORY_SHEET, history, HISTORY_COLUMNS),
        (PRODUCT_SHEET, products, PRODUCT_COLUMNS),
    ):
        for name in required:
            if name not in frame.columns:
                issues.append(ValidationIssue(sheet, 1, name, "必須列がありません"))
    if issues:
        raise WorkbookValidationError(issues)

    history = _nonblank_rows(history)
    products = _nonblank_rows(products)
    if history.empty:
        issues.append(ValidationIssue(HISTORY_SHEET, None, "確認日", "価格履歴が空です"))
    if products.empty:
        issues.append(ValidationIssue(PRODUCT_SHEET, None, "商品ID", "商品マスタが空です"))

    product_names: dict[str, str] = {}
    product_rows: dict[str, int] = {}
    for index, record in products.iterrows():
        excel_row = int(index) + 2
        identifier = _text_id(record["商品ID"])
        name = record["商品名"]
        if identifier is None:
            issues.append(
                ValidationIssue(PRODUCT_SHEET, excel_row, "商品ID", "文字列のIDが必要です（001など）")
            )
        if not isinstance(name, str) or not name.strip():
            issues.append(ValidationIssue(PRODUCT_SHEET, excel_row, "商品名", "商品名が空です"))
        if identifier:
            if identifier in product_rows:
                issues.append(
                    ValidationIssue(
                        PRODUCT_SHEET,
                        excel_row,
                        "商品ID",
                        f"商品ID {identifier} は{product_rows[identifier]}行目と重複します",
                    )
                )
            else:
                product_rows[identifier] = excel_row
                if isinstance(name, str) and name.strip():
                    product_names[identifier] = name.strip()

    rows: list[dict[str, object]] = []
    seen: dict[tuple[str, pd.Timestamp], int] = {}
    for index, record in history.iterrows():
        excel_row = int(index) + 2
        timestamp = _parse_date(record["確認日"])
        identifier = _text_id(record["商品ID"])
        amount = _price(record["価格"])
        if timestamp is None:
            issues.append(ValidationIssue(HISTORY_SHEET, excel_row, "確認日", "有効な日付ではありません"))
        if identifier is None:
            issues.append(
                ValidationIssue(HISTORY_SHEET, excel_row, "商品ID", "文字列のIDが必要です（001など）")
            )
        elif identifier not in product_rows:
            issues.append(
                ValidationIssue(HISTORY_SHEET, excel_row, "商品ID", f"商品ID {identifier} はマスタ未登録です")
            )
        if amount is None:
            issues.append(
                ValidationIssue(HISTORY_SHEET, excel_row, "価格", "0より大きい数値（日本円）を入力してください")
            )
        if identifier is not None and timestamp is not None:
            key = (identifier, timestamp)
            if key in seen:
                issues.append(
                    ValidationIssue(
                        HISTORY_SHEET,
                        excel_row,
                        "確認日・商品ID",
                        f"同一商品・同日の記録が{seen[key]}行目と重複します",
                    )
                )
            else:
                seen[key] = excel_row
        if timestamp is not None and identifier in product_names and amount is not None:
            note = record.get("備考", None)
            rows.append(
                {
                    "date": timestamp,
                    "product_id": identifier,
                    "product_name": product_names[identifier],
                    "price_jpy": amount,
                    "note": "" if pd.isna(note) else str(note),
                    "excel_row": excel_row,
                }
            )

    if issues:
        raise WorkbookValidationError(issues)
    return pd.DataFrame(rows).sort_values(["product_id", "date"]).reset_index(drop=True)
