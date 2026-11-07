"""Smoke-test the default demo UI on CI, where Streamlit is installed."""

from pathlib import Path

import pytest


def test_demo_mode_renders_without_exception():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parents[1] / "src" / "price_viewer" / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=20).run()
    assert not app.exception
    assert any("Excel商品価格" in title.value for title in app.title)
    assert len(app.metric) == 3
