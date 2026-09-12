"""F001 回填报告回归门禁。"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from alphamill.data_bridge.collector import derivatives_market_backfill as derivatives
from tools import f001_backfill_report as report


class _Cursor:
    def __init__(self, rows: list[tuple]) -> None:
        self.rows = iter(rows)
        self.statements: list[tuple[str, tuple]] = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql: str, params: tuple = ()) -> None:
        self.statements.append((sql, params))

    def fetchone(self):
        return next(self.rows)


class _Connection:
    def __init__(self, rows: list[tuple]) -> None:
        self.cursor_obj = _Cursor(rows)

    def cursor(self):
        return self.cursor_obj


def test_symbol_stats_uses_authoritative_window_not_observed_span(monkeypatch) -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 3, tzinfo=UTC)
    monkeypatch.setattr(report, "WINDOW_START", start)
    monkeypatch.setattr(report, "WINDOW_END", end)

    # The observed rows cover only minutes 1 and 2. An observed-span check would
    # incorrectly pass with expected=2; the configured left-closed window expects 3.
    conn = _Connection([(2, start.replace(minute=1), start.replace(minute=2)), (1, None)])
    stats = report.symbol_stats(conn, "binance", "BTC/USDT")

    assert stats["expected_rows_in_window"] == 3
    assert stats["missing_rows"] == 1
    assert stats["verdict"] == "FAIL"
    assert all(start in params and end in params for _, params in conn.cursor_obj.statements)


def test_symbol_stats_uses_explicit_listing_boundary(monkeypatch) -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    effective_start = datetime(2024, 1, 1, 0, 1, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 3, tzinfo=UTC)
    monkeypatch.setattr(report, "WINDOW_START", start)
    monkeypatch.setattr(report, "WINDOW_END", end)
    monkeypatch.setattr(report, "listing_start", lambda *_args: effective_start)
    monkeypatch.setattr(report, "unavailable_symbols", lambda: set())

    conn = _Connection(
        [
            (2, effective_start, end - report.timedelta(minutes=1)),
            (0, None),
        ]
    )
    stats = report.symbol_stats(conn, "binance", "NEW/USDT")

    assert stats["expected_rows_in_window"] == 2
    assert stats["boundary_ok"] is True
    assert stats["verdict"] == "PASS"


def test_derivative_verdict_fails_failed_progress() -> None:
    stats = report.derivative_verdict(
        dataset="funding",
        exchange="binanceusdm",
        actual_rows=10_000,
        populated_symbols=6,
        expected_symbols=6,
        effective_start=datetime(2024, 1, 1, tzinfo=UTC),
        effective_end=datetime(2024, 1, 2, tzinfo=UTC),
        failed_progress=1,
    )
    assert stats["verdict"] == "FAIL"


def test_derivative_verdict_fails_when_progress_does_not_cover_target_window() -> None:
    stats = report.derivative_verdict(
        dataset="open_interest",
        exchange="binanceusdm",
        actual_rows=10_000,
        populated_symbols=6,
        expected_symbols=6,
        effective_start=datetime(2024, 1, 1, tzinfo=UTC),
        effective_end=datetime(2024, 1, 2, tzinfo=UTC),
        failed_progress=0,
        progress_window_covers_authoritative_window=False,
    )
    assert stats["verdict"] == "FAIL"


def test_basis_boundary_is_explicitly_allowlisted() -> None:
    stats = report.derivative_verdict(
        dataset="basis",
        exchange="binanceusdm",
        actual_rows=0,
        populated_symbols=0,
        expected_symbols=6,
        effective_start=datetime(2024, 1, 1, tzinfo=UTC),
        effective_end=datetime(2024, 1, 2, tzinfo=UTC),
        failed_progress=0,
    )
    assert "binanceusdm" in derivatives.BASIS_UNSUPPORTED_EXCHANGES
    assert stats["status"] == "unsupported"
    assert stats["verdict"] == "PASS"
    assert stats["expected_min_rows"] == 0


def test_aggregate_view_query_filters_exchange() -> None:
    conn = _Connection([(1,), (1,)] * len(report.AGGREGATES))
    report.aggregate_stats(conn, "binance")

    view_queries = conn.cursor_obj.statements[::2]
    assert len(view_queries) == len(report.AGGREGATES)
    assert all("WHERE exchange = %s" in sql for sql, _ in view_queries)
    assert all(params[0] == "binance" for _, params in view_queries)


def test_powershell_completeness_uses_configured_window() -> None:
    script = (Path(__file__).resolve().parents[2] / "deployment/verify.ps1").read_text(
        encoding="utf-8"
    )

    assert "$backfillWindowStart" in script
    assert "$backfillWindowEnd" in script
    assert "EXTRACT(EPOCH FROM ('$backfillWindowEnd'::timestamptz" in script
    assert "EXTRACT(EPOCH FROM (t1 - t0))" not in script
