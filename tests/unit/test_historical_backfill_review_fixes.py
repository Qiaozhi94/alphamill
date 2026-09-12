"""historical_backfill review regression tests."""

from datetime import UTC, datetime

import pytest

from alphamill.data_bridge.collector import historical_backfill as backfill


class _Exchange:
    rateLimit = 0

    def fetch_ohlcv(self, *_args, **_kwargs):
        return []


class _RecordingExchange(_Exchange):
    def __init__(self):
        self.calls = []

    def fetch_ohlcv(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return []


class _SchemaCursor:
    def __init__(self, table_name):
        self.table_name = table_name

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, *_args):
        return None

    def fetchone(self):
        return (self.table_name,)


class _SchemaConnection:
    def __init__(self, table_name):
        self.cursor_obj = _SchemaCursor(table_name)

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        return None


def test_empty_batch_before_end_is_stalled_not_complete(monkeypatch) -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 2, tzinfo=UTC)
    progress = []
    monkeypatch.setattr(backfill, "load_progress", lambda *_args: (start, 0))
    monkeypatch.setattr(backfill, "save_progress", lambda *args: progress.append(args))

    with pytest.raises(RuntimeError, match="empty OHLCV batch"):
        backfill.fetch_symbol("binance", _Exchange(), object(), "BTC/USDT", start, end)

    assert progress[-1][6] == "stalled"
    assert not any(item[6] == "complete" for item in progress)


def test_retry_count_has_safe_lower_bound() -> None:
    assert backfill.retry_count(0) == 1
    assert backfill.retry_count("-2") == 1
    assert backfill.retry_count(3) == 3


def test_listing_boundary_is_used_before_fetch(monkeypatch) -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    listing_start = datetime(2024, 1, 1, 0, 2, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 3, tzinfo=UTC)
    exchange = _RecordingExchange()
    monkeypatch.setattr(backfill, "LISTING_STARTS", f"BTC/USDT={listing_start.isoformat()}")
    monkeypatch.setattr(backfill, "load_progress", lambda *_args: (start, 0))
    monkeypatch.setattr(backfill, "save_progress", lambda *_args: None)

    with pytest.raises(RuntimeError, match="empty OHLCV batch"):
        backfill.fetch_symbol("binance", exchange, object(), "BTC/USDT", start, end)

    assert exchange.calls[0][1]["since"] == int(listing_start.timestamp() * 1000)


def test_explicitly_unavailable_symbol_is_terminal(monkeypatch) -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 3, tzinfo=UTC)
    progress = []
    monkeypatch.setattr(backfill, "UNAVAILABLE_SYMBOLS", {"DELISTED/USDT"})
    monkeypatch.setattr(backfill, "save_progress", lambda *args: progress.append(args))

    rows = backfill.fetch_symbol("binance", _Exchange(), object(), "DELISTED/USDT", start, end)

    assert rows == 0
    assert progress[-1][6] == "unavailable"


def test_delisting_boundary_stops_before_exchange_empty_batch(monkeypatch) -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    delisting_end = datetime(2024, 1, 1, 0, 2, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 4, tzinfo=UTC)
    progress = []

    class _BoundaryExchange(_RecordingExchange):
        def fetch_ohlcv(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            since = kwargs["since"]
            if since >= int(delisting_end.timestamp() * 1000):
                return []
            return [[since, 1, 1, 1, 1, 1]]

    exchange = _BoundaryExchange()
    monkeypatch.setattr(backfill, "DELISTING_ENDS", f"DELISTED/USDT={delisting_end.isoformat()}")
    monkeypatch.setattr(backfill, "load_progress", lambda *_args: (start, 0))
    monkeypatch.setattr(backfill, "save_progress", lambda *args: progress.append(args))
    monkeypatch.setattr(backfill, "upsert_ohlcv", lambda *_args: 1)

    rows = backfill.fetch_symbol("binance", exchange, object(), "DELISTED/USDT", start, end)

    assert rows == 2
    assert exchange.calls[-1][1]["since"] < int(delisting_end.timestamp() * 1000)
    assert progress[-1][6] == "complete"
    assert "delisting boundary" in progress[-1][8]


def test_progress_schema_is_required_from_init_sql() -> None:
    with pytest.raises(RuntimeError, match="backfill_progress is missing"):
        backfill.ensure_progress_table(_SchemaConnection(None))

    backfill.ensure_progress_table(_SchemaConnection("backfill_progress"))
