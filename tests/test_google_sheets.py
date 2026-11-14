"""No real Google account, network, or private data is used in tests."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from price_viewer.analysis import summarize_prices
from price_viewer.sheets import SheetAccessError, load_price_sheet, parse_batch_values
from price_viewer.validation import WorkbookValidationError

ID = "example_private_spreadsheet_id_123456789"


def payload(history=None, products=None):
    return {
        "valueRanges": [
            {
                "values": history
                if history is not None
                else [
                    ["確認日", "商品ID", "価格", "備考"],
                    ["2026/01/08", "001", 90000, "架空"],
                    ["2026/01/01", "001", 100000, "架空"],
                ]
            },
            {
                "values": products
                if products is not None
                else [["商品ID", "商品名"], ["001", "架空商品A"]]
            },
        ]
    }


@dataclass
class Response:
    status_code: int = 200
    data: object = None

    def json(self):
        return self.data


class FakeSession:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def get(self, url, *, params, timeout):
        self.calls.append((url, params, timeout))
        return next(self.responses)


def test_one_batch_request_preserves_ids_and_jpy():
    client = FakeSession([Response(200, payload())])
    frame = load_price_sheet(ID, session=client)
    assert frame["product_id"].tolist() == ["001", "001"]
    assert frame["price_jpy"].tolist() == [100000, 90000]
    summary = summarize_prices(frame)
    assert summary is not None and summary.change_pct == pytest.approx(-10.0)
    assert len(client.calls) == 1
    url, params, timeout = client.calls[0]
    assert "/values:batchGet" in url
    assert [v for k, v in params if k == "ranges"] == ["'価格履歴'!A:D", "'商品マスタ'!A:B"]
    assert ("valueRenderOption", "UNFORMATTED_VALUE") in params
    assert timeout == 20


def test_trailing_api_cells_are_padded_and_empty_rows_skipped():
    history = [
        ["確認日", "商品ID", "価格", "備考"],
        ["2026/01/01", "001", 100],
        [],
        ["2026/01/08", "001", 90],
    ]
    result = parse_batch_values(payload(history=history))
    assert result["excel_row"].tolist() == [2, 4]


@pytest.mark.parametrize(
    "history,products,bad_column,bad_row",
    [
        ([["確認日", "商品ID", "備考"], ["2026/01/01", "001", "memo"]], None, "価格", None),
        ([["確認日", "商品ID", "価格"], ["2026/01/01", 1, 10]], None, "商品ID", 2),
        ([["確認日", "商品ID", "価格"], ["2026/01/01", "001", "10,000"]], None, "価格", 2),
        ([["確認日", "商品ID", "価格"], ["2026/01/01", "001", 0]], None, "価格", 2),
        (
            [["確認日", "商品ID", "価格"], ["2026/01/01", "001", 10], ["2026/01/01", "001", 11]],
            None,
            "確認日・商品ID",
            3,
        ),
        ([["確認日", "商品ID", "価格"], ["wrong date", "001", 10]], None, "確認日", 2),
        (None, [["商品ID", "商品名"], ["001", "A"], ["001", "B"]], "商品ID", 3),
    ],
)
def test_bad_data_fails_without_silent_discard(history, products, bad_column, bad_row):
    # Note: missing '備考' is permitted, because it is optional.
    with pytest.raises(WorkbookValidationError) as caught:
        parse_batch_values(payload(history=history, products=products))
    assert any(
        i.column == bad_column and (bad_row is None or i.row == bad_row)
        for i in caught.value.issues
    )


def test_blank_or_duplicate_headers_caught():
    with pytest.raises(WorkbookValidationError):
        parse_batch_values(payload(history=[["確認日", "商品ID", "", "備考"]]))
    with pytest.raises(WorkbookValidationError):
        parse_batch_values(payload(products=[["商品ID", "商品ID"], ["001", "A"]]))


def test_unavailable_or_wrong_auth_gives_actionable_error(monkeypatch):
    monkeypatch.delenv("GOOGLE_SHEET_ID", raising=False)
    with pytest.raises(SheetAccessError, match="GOOGLE_SHEET_ID"):
        load_price_sheet(session=FakeSession([]))
    with pytest.raises(SheetAccessError, match="形式"):
        load_price_sheet("invalid id!", session=FakeSession([]))
    with pytest.raises(SheetAccessError, match="閲覧権限"):
        load_price_sheet(ID, session=FakeSession([Response(403)]))
    with pytest.raises(SheetAccessError, match="シート名"):
        load_price_sheet(ID, session=FakeSession([Response(400)]))


def test_transient_quota_retries_are_bounded():
    sleeps = []
    client = FakeSession([Response(429), Response(503), Response(200, payload())])
    frame = load_price_sheet(ID, session=client, sleep=sleeps.append)
    assert len(frame) == 2
    assert sleeps == [1, 2]
    assert len(client.calls) == 3
    with pytest.raises(SheetAccessError, match="上限"):
        load_price_sheet(ID, session=FakeSession([Response(429)] * 3), sleep=lambda _: None)


def test_bad_api_payload_raises_clear_error():
    with pytest.raises(SheetAccessError):
        parse_batch_values({"valueRanges": []})
    with pytest.raises(SheetAccessError):
        load_price_sheet(ID, session=FakeSession([Response(200, [])]))
