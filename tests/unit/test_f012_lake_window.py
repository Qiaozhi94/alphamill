"""F012 检视 R2-1：ohlcv 的 `time` 是 K 线开盘时间，小时标签只能含已收盘的 1m K 线（无前视）。"""

from __future__ import annotations

import pandas as pd

from alphamill.factor_factory.generators.lake_tensor import _aggregate


def test_hour_label_contains_only_candles_closed_by_the_label_time() -> None:
    opens = pd.to_datetime(
        ["2026-01-01T00:00Z", "2026-01-01T00:59Z", "2026-01-01T01:00Z"], utc=True
    )
    frame = pd.DataFrame(
        {"timestamp": opens, "pair": "AAA-USDT", "close": [1.0, 2.0, 99.0], "volume": 1.0}
    )

    hourly = _aggregate(frame, "1h")

    # 00:00、00:59 开盘的在 01:00 前收盘 → 标签 01:00；01:00 开盘的 01:01 才收盘 → 标签 02:00
    assert hourly.loc[(pd.Timestamp("2026-01-01T01:00Z"), "AAA-USDT"), "close"] == 2.0
    assert hourly.loc[(pd.Timestamp("2026-01-01T01:00Z"), "AAA-USDT"), "volume"] == 2.0
    assert hourly.loc[(pd.Timestamp("2026-01-01T02:00Z"), "AAA-USDT"), "close"] == 99.0
