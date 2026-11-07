"""Exportable local Plotly charts."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def price_line_chart(frame: pd.DataFrame, title: str) -> go.Figure:
    """Plot one comparable product series, using actual observed dates."""
    if frame.empty:
        raise ValueError("グラフに表示できる記録がありません")
    ordered = frame.sort_values("date")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ordered["date"],
            y=ordered["price_jpy"],
            mode="lines+markers",
            name="買取価格（円）",
            hovertemplate="%{x|%Y-%m-%d}<br>¥%{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="確認日",
        yaxis_title="価格（日本円）",
        yaxis_tickformat=",.0f",
        hovermode="x unified",
    )
    return fig
