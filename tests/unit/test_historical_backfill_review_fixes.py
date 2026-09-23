"""historical_backfill review regression tests."""

from datetime import UTC, datetime, timedelta

import pytest

from alphamill.data_bridge.collector import historical_backfill as backfill
from alphamill.data_bridge.collector.backfill_progress import ensure_progress_table


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
        ensure_progress_table(_SchemaConnection(None))

    ensure_progress_table(_SchemaConnection("backfill_progress"))


def test_env_entrypoint_imports_after_orchestrator_split() -> None:
    """环境层必须能导入：`python -m ...historical_backfill` 是 F001 缺口补齐的入口。

    回归（2026-09-23）：编排层拆到 `backfill_orchestrator` 后，`backfill_cli` 仍从
    `historical_backfill` 导入 `run_backfill`，`main()` 里的延迟导入于是必炸——
    `deployment/f001-backfill-supervisor.sh` 一调就 ImportError，且没有测试覆盖。
    """
    from alphamill.data_bridge.collector import backfill_cli, backfill_orchestrator

    assert callable(backfill_cli.run_from_env)
    assert backfill_cli.run_backfill is backfill_orchestrator.run_backfill


def test_env_entrypoint_passes_window_and_symbols(monkeypatch) -> None:
    """环境层：窗口与 symbols 解析后原样交给编排层，成功后刷新连续聚合。"""
    from alphamill.data_bridge.collector import backfill_cli

    seen: dict = {}

    class _Outcome:
        status = "completed"
        rows = 7

    class _Conn:
        def close(self):
            seen["closed"] = True

    def _run_backfill(**kwargs):
        seen.update(kwargs)
        return [_Outcome()]

    monkeypatch.setenv("EXCHANGES", "binance")
    monkeypatch.setenv("SYMBOLS", "BTC/USDT")
    monkeypatch.setenv("BACKFILL_START", "2024-09-10T00:00:00Z")
    monkeypatch.setenv("BACKFILL_END", "2024-09-11T00:00:00Z")
    monkeypatch.setattr(backfill_cli, "db_connect", _Conn)
    monkeypatch.setattr(backfill_cli, "run_backfill", _run_backfill)

    def _refresh(_conn, start, end):
        seen["refreshed"] = (start, end)

    monkeypatch.setattr(backfill_cli, "refresh_aggregates", _refresh)

    assert backfill_cli.run_from_env() == 0
    assert seen["symbols"] == ["BTC/USDT"]
    assert seen["start"].isoformat() == "2024-09-10T00:00:00+00:00"
    assert seen["end"].isoformat() == "2024-09-11T00:00:00+00:00"
    assert "refreshed" in seen
    assert seen["closed"] is True


def test_refresh_aggregates_ends_open_transaction_first(monkeypatch) -> None:
    """回归（2026-09-23）：连接上残留只读事务时，切 autocommit 前必须先收尾。

    psycopg2 对「事务开着就 set_session」直接抛 `ProgrammingError`，而调用方
    （`run_from_env` 写完缺口后）手上正是一个刚做完只读查询的连接。
    """

    class _Cursor:
        def __init__(self, calls):
            self.calls = calls

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def execute(self, sql, params=None):
            self.calls.append(("execute", sql, params))

    class _Conn:
        autocommit = False

        def __init__(self):
            self.calls = []

        def cursor(self):
            return _Cursor(self.calls)

        def commit(self):
            self.calls.append(("commit",))

    conn = _Conn()
    monkeypatch.setattr(backfill, "REFRESH_AGGREGATES", True)

    end = datetime(2024, 9, 11, tzinfo=UTC)
    backfill.refresh_aggregates(conn, datetime(2024, 9, 10, tzinfo=UTC), end)

    assert conn.calls[0] == ("commit",)
    calls = {c[2][0]: c[2] for c in conn.calls if c[0] == "execute"}
    assert list(calls) == ["ohlcv_5m", "ohlcv_15m", "ohlcv_1h", "ohlcv_4h", "ohlcv_1d"]
    # 窗口短于两个桶时必须放宽，否则 TimescaleDB 报 `refresh window too small`
    assert calls["ohlcv_1d"][1] == end - timedelta(days=2)
    assert calls["ohlcv_5m"][1] == datetime(2024, 9, 10, tzinfo=UTC)
    assert conn.autocommit is False  # 恢复原值
