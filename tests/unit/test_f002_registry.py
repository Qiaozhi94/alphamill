"""T015：dataset registry 白名单契约（design §3 表逐一核对）。"""

import pytest

from alphamill.data_bridge import registry
from alphamill.data_bridge.errors import UnknownDatasetError

EXPECTED_PROJECTIONS = {
    "ohlcv_1m": ["time", "exchange", "symbol", "open", "high", "low", "close", "volume"],
    "derivatives_funding_rates": [
        "time", "exchange", "symbol", "funding_rate", "next_funding_time",
        "mark_price", "index_price", "metadata", "ingested_at",
    ],
    "derivatives_open_interest": [
        "time", "exchange", "symbol", "timeframe", "open_interest",
        "open_interest_value", "base_volume", "quote_volume", "metadata", "ingested_at",
    ],
    "derivatives_mark_index_basis": [
        "time", "exchange", "symbol", "timeframe", "mark_open", "mark_high",
        "mark_low", "mark_close", "index_open", "index_high", "index_low",
        "index_close", "basis_close", "basis_pct", "metadata", "ingested_at",
    ],
    "signals_log": [
        "time", "exchange", "symbol", "source", "signal_type", "confidence",
        "metadata", "latest_candle", "expected_return", "volatility",
        "direction_prob", "realized_return_60m", "evaluated_at",
    ],
}

EXPECTED_PARTITIONS = {
    "ohlcv_1m": ("exchange", "pair", "date"),
    "derivatives_funding_rates": ("exchange", "pair", "date"),
    "derivatives_open_interest": ("exchange", "pair", "timeframe", "date"),
    "derivatives_mark_index_basis": ("exchange", "pair", "timeframe", "date"),
    "signals_log": ("date",),
}


def test_five_datasets_registered():
    assert sorted(registry.DATASETS) == sorted(EXPECTED_PROJECTIONS)


def test_unknown_dataset_rejected():
    with pytest.raises(UnknownDatasetError):
        registry.require_dataset("nope")
    with pytest.raises(UnknownDatasetError):
        registry.require_dataset("")


def test_projection_order_matches_design_table():
    for name, expected in EXPECTED_PROJECTIONS.items():
        spec = registry.require_dataset(name)
        assert [c.name for c in spec.projection] == expected, name
        # 投影列名不重复：编码顺序即身份，重复列会让摘要定义含糊
        assert len(set(expected)) == len(expected)


@pytest.mark.parametrize(
    ("dataset", "event_time", "available_at", "fidelity"),
    [
        ("ohlcv_1m", "time", None, "event_time_only"),
        ("derivatives_funding_rates", "time", "ingested_at", "bitemporal"),
        ("derivatives_open_interest", "time", "ingested_at", "bitemporal"),
        ("derivatives_mark_index_basis", "time", "ingested_at", "bitemporal"),
        ("signals_log", "latest_candle", "time", "bitemporal"),
    ],
)
def test_dual_time_axis_columns(dataset, event_time, available_at, fidelity):
    spec = registry.require_dataset(dataset)
    assert spec.event_time == event_time
    assert spec.available_at == available_at
    assert spec.as_of_fidelity == fidelity


def test_signals_log_event_time_is_latest_candle():
    spec = registry.require_dataset("signals_log")
    assert spec.event_time == "latest_candle"
    assert spec.deferred_labels == {"realized_return_60m": "evaluated_at"}


def test_partition_keys_and_market_type():
    for name, keys in EXPECTED_PARTITIONS.items():
        spec = registry.require_dataset(name)
        assert spec.partition_keys == keys, name
    assert registry.require_dataset("ohlcv_1m").market_type == "spot"
    assert registry.require_dataset("derivatives_open_interest").market_type == "perp"
    assert registry.pair_partitioned(registry.require_dataset("ohlcv_1m"))
    assert not registry.pair_partitioned(registry.require_dataset("signals_log"))
    assert registry.timeframe_partitioned(registry.require_dataset("derivatives_open_interest"))
    assert not registry.timeframe_partitioned(registry.require_dataset("ohlcv_1m"))


def test_filterable_columns_whitelist():
    assert registry.FILTERABLE_COLUMNS == frozenset(
        {"event_time", "available_at", "exchange", "symbol", "timeframe"}
    )


def test_logical_types_are_frozen_vocabulary():
    allowed = {"timestamptz", "text", "double", "jsonb"}
    for spec in registry.DATASETS.values():
        for col in spec.projection:
            assert col.logical_type in allowed, (spec.name, col.name)
