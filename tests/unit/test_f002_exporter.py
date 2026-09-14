"""F002 导出窗口边界测试。"""

import datetime as dt

import pytest

from alphamill.data_bridge import exporter, registry
from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge.errors import DataBridgeError


def _partition(pair: str) -> dict:
    return {
        "logical_partition_key": {"exchange": "binance", "pair": pair, "date": "2026-09-14"},
        "path": f"ohlcv_1m/exchange=binance/pair={pair}/date=2026-09-14.r1.parquet",
        "rows": 1,
        "time_min": "2026-09-14T00:00:00Z",
        "time_max": "2026-09-14T00:00:00Z",
        "row_digest": "sha256:" + pair.replace("-", "") * 64,
        "bytes": 1,
        "sha256": "0" * 64,
    }


def test_default_window_end_excludes_current_partial_day(monkeypatch):
    monkeypatch.setattr(exporter.reconcile, "table_span", lambda _conn, _spec: None)
    _, end = exporter._resolve_window(
        object(), registry.require_dataset("ohlcv_1m"), "incremental", None, []
    )
    assert end == dt.datetime.now(dt.UTC).date()


def test_full_merge_drops_source_partitions_that_disappeared():
    baseline = [_partition("BTC-USDT"), _partition("ETH-USDT")]
    produced = [_partition("BTC-USDT")]
    merged = exporter._merge_partitions("full", baseline, produced)
    assert [entry["logical_partition_key"]["pair"] for entry in merged] == ["BTC-USDT"]


def test_full_shrink_guard_rejects_empty_result_with_nonempty_baseline():
    with pytest.raises(DataBridgeError, match="空快照"):
        exporter._guard_full_shrink([_partition("BTC-USDT")], [], dt.date(2026, 9, 15))


def test_full_shrink_guard_rejects_large_shrink_and_truncated_window():
    baseline = [_partition("BTC-USDT"), _partition("ETH-USDT"), _partition("SOL-USDT")]
    with pytest.raises(DataBridgeError, match="大幅降至"):
        exporter._guard_full_shrink(baseline, [_partition("BTC-USDT")], dt.date(2026, 9, 15))

    baseline = [_partition("BTC-USDT"), _partition("ETH-USDT")]
    current = [_partition("BTC-USDT")]
    with pytest.raises(DataBridgeError, match="截断"):
        exporter._guard_full_shrink(baseline, current, dt.date(2026, 9, 14))


def test_quality_flag_count_change_is_not_a_noop():
    baseline = {
        "symbol_map_digest": "sha256:" + "a" * 64,
        "quality": {"flagged_partitions": ["binance/BTC-USDT/2026-09-14"], "unresolved_total": 1},
        "excluded_null_event_time": 0,
    }
    assert mf.metadata_changed(
        baseline,
        "sha256:" + "a" * 64,
        ["binance/BTC-USDT/2026-09-14"],
        2,
        0,
    )
