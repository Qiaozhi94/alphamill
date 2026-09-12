"""F001 回填报告回归门禁。"""

from __future__ import annotations

from datetime import UTC, datetime

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
