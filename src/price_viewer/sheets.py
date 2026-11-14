"""Read a private Google Sheet via the read-only Sheets API (one batch request)."""

from __future__ import annotations

import os
import re
import time
from collections.abc import Callable, Mapping
from typing import Any

import pandas as pd

from price_viewer.validation import (
    HISTORY_SHEET,
    PRODUCT_SHEET,
    ValidationIssue,
    WorkbookValidationError,
    validate_frames,
)

READ_ONLY_SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"
API_ENDPOINT = "https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values:batchGet"
RANGES = ("'価格履歴'!A:D", "'商品マスタ'!A:B")
MAX_RETRIES = 2
RETRYABLE = {429, 500, 502, 503, 504}


class SheetAccessError(RuntimeError):
    """Configuration, authentication, permissions or remote API failure."""


def _authorized_session() -> Any:
    """Use Application Default Credentials; secrets never enter the source tree."""
    try:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError
        from google.auth.transport.requests import AuthorizedSession
    except ImportError as error:
        raise SheetAccessError(
            "google-authが不足しています。uv sync --lockedを実行してください"
        ) from error

    try:
        credentials, _ = google.auth.default(scopes=[READ_ONLY_SCOPE])
    except DefaultCredentialsError as error:
        raise SheetAccessError(
            "Google認証情報が見つかりません。GOOGLE_APPLICATION_CREDENTIALSの設定を確認してください"
        ) from error
    return AuthorizedSession(credentials)


def _rows_to_frame(payload: Mapping[str, Any], sheet: str) -> pd.DataFrame:
    rows = payload.get("values", [])
    if not isinstance(rows, list) or not rows:
        raise WorkbookValidationError([ValidationIssue(sheet, 1, "見出し", "シートが空です")])
    if not isinstance(rows[0], list):
        raise WorkbookValidationError(
            [ValidationIssue(sheet, 1, "見出し", "表形式を確認してください")]
        )
    headers = rows[0]
    if any(not isinstance(name, str) or not name.strip() for name in headers):
        raise WorkbookValidationError([ValidationIssue(sheet, 1, "見出し", "列名が空です")])
    if len(headers) != len(set(headers)):
        raise WorkbookValidationError([ValidationIssue(sheet, 1, "見出し", "列名が重複しています")])
    if any(not isinstance(row, list) or len(row) > len(headers) for row in rows[1:]):
        raise WorkbookValidationError(
            [ValidationIssue(sheet, None, "行", "見出しと行の列数が一致しません")]
        )
    # Preserve the original 1-based spreadsheet row through DataFrame indices.
    padded = [row + [None] * (len(headers) - len(row)) for row in rows[1:]]
    return pd.DataFrame(padded, columns=headers, dtype=object)


def parse_batch_values(payload: Mapping[str, Any]) -> pd.DataFrame:
    """Validate two batchGet ranges; keep numeric prices and string IDs unchanged."""
    ranges = payload.get("valueRanges")
    if not isinstance(ranges, list) or len(ranges) != 2:
        raise SheetAccessError("Google Sheets APIから2つのシートの値を取得できませんでした")
    history = _rows_to_frame(ranges[0], HISTORY_SHEET)
    products = _rows_to_frame(ranges[1], PRODUCT_SHEET)
    return validate_frames(history, products)


def load_price_sheet(
    spreadsheet_id: str | None = None,
    *,
    session: Any | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> pd.DataFrame:
    """Fetch both tables with one read request, never write to Google Sheets.

    session injection keeps offline tests fully independent from credentials/network.
    """
    sheet_id = (spreadsheet_id or os.getenv("GOOGLE_SHEET_ID", "")).strip()
    if not sheet_id:
        raise SheetAccessError(
            "GOOGLE_SHEET_IDが未設定です。共有シートのURLからIDを確認してください"
        )
    if not re.fullmatch(r"[A-Za-z0-9_-]{15,200}", sheet_id):
        raise SheetAccessError("GOOGLE_SHEET_IDの形式が不正です（URLではなくIDのみ指定）")

    client = session if session is not None else _authorized_session()
    params = [
        ("ranges", RANGES[0]),
        ("ranges", RANGES[1]),
        ("majorDimension", "ROWS"),
        ("valueRenderOption", "UNFORMATTED_VALUE"),
        ("dateTimeRenderOption", "FORMATTED_STRING"),
    ]
    url = API_ENDPOINT.format(spreadsheet_id=sheet_id)
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.get(url, params=params, timeout=20)
        except Exception as error:
            # Do not include a secret-bearing exception's request headers/body.
            raise SheetAccessError(
                "Google Sheets APIへの接続に失敗しました。ネットワークを確認してください"
            ) from error
        status = response.status_code
        if status == 200:
            try:
                payload = response.json()
            except ValueError as error:
                raise SheetAccessError("Google Sheets APIの応答がJSONではありません") from error
            if not isinstance(payload, dict):
                raise SheetAccessError("Google Sheets APIの応答形式が不正です")
            return parse_batch_values(payload)
        if status in RETRYABLE and attempt < MAX_RETRIES:
            sleep(2**attempt)
            continue
        if status in (401, 403):
            raise SheetAccessError(
                "Google認証または閲覧権限が不足しています。サービスアカウントを閲覧者として共有してください"
            )
        if status == 404:
            raise SheetAccessError(
                "スプレッドシートが見つかりません。IDと閲覧権限を確認してください"
            )
        if status == 400:
            raise SheetAccessError(
                "Google Sheets APIがシート名・範囲を認識できません。『価格履歴』『商品マスタ』を確認してください"
            )
        if status == 429:
            raise SheetAccessError(
                "Google Sheets APIの読み取り上限に達しました。時間をおいて実行してください"
            )
        raise SheetAccessError(f"Google Sheets APIがエラーを返しました（HTTP {status}）")
    raise AssertionError("unreachable")
