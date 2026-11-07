"""Read-only loading of the existing two-sheet Excel workbook."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO
from zipfile import BadZipFile

import pandas as pd

from price_viewer.validation import (
    HISTORY_SHEET,
    PRODUCT_SHEET,
    ValidationIssue,
    WorkbookValidationError,
    validate_frames,
)

MAX_BYTES = 20 * 1024 * 1024


def load_price_workbook(source: str | Path | BinaryIO) -> pd.DataFrame:
    """Read/validate xlsx; never write to source or silently repair bad rows."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.is_file():
            raise WorkbookValidationError(
                [ValidationIssue("ファイル", None, "パス", f"Excelが見つかりません: {path}")]
            )
        if path.suffix.lower() != ".xlsx":
            raise WorkbookValidationError(
                [ValidationIssue("ファイル", None, "形式", ".xlsxファイルを選んでください")]
            )
        size = path.stat().st_size
    else:
        position = source.tell()
        source.seek(0, 2)
        size = source.tell()
        source.seek(position)
    if size > MAX_BYTES:
        raise WorkbookValidationError(
            [ValidationIssue("ファイル", None, "容量", "Excelは20MB以下にしてください")]
        )

    try:
        if not isinstance(source, (str, Path)):
            source.seek(0)
        with pd.ExcelFile(source, engine="openpyxl") as book:
            missing = [name for name in (HISTORY_SHEET, PRODUCT_SHEET) if name not in book.sheet_names]
            if missing:
                raise WorkbookValidationError(
                    [ValidationIssue(name, None, "シート名", "指定されたシートがありません") for name in missing]
                )
            # dtype=object keeps text IDs such as '001' and lets validation reject numeric IDs.
            history = pd.read_excel(book, sheet_name=HISTORY_SHEET, dtype=object)
            products = pd.read_excel(book, sheet_name=PRODUCT_SHEET, dtype=object)
    except WorkbookValidationError:
        raise
    except (ValueError, OSError, KeyError, TypeError, ImportError, BadZipFile) as error:
        raise WorkbookValidationError(
            [ValidationIssue("ファイル", None, "Excel", f"読み込めません: {type(error).__name__}")]
        ) from error
    return validate_frames(history, products)
