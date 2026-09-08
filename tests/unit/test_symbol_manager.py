"""Collector symbol parsing contract tests (F001/T006)."""

import pytest

from alphamill.data_bridge.collector.symbol_manager import parse_symbols


def test_parse_symbols_deduplicates_preserving_order() -> None:
    assert parse_symbols(" btc/usdt,ETH/USDT,BTC/USDT, ") == ["BTC/USDT", "ETH/USDT"]


def test_parse_symbols_uses_safe_defaults() -> None:
    assert parse_symbols(None) == ["BTC/USDT", "ETH/USDT"]


@pytest.mark.parametrize("value", ["", "BTC-USDT", "/USDT", "BTC/"])
def test_parse_symbols_rejects_invalid_or_empty_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_symbols(value)
