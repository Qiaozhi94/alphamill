"""F002 分区辅助函数边界测试。"""

import datetime as dt

import pytest

from alphamill.data_bridge import partitions, registry
from alphamill.data_bridge.errors import DataBridgeError
from alphamill.data_bridge.partitions import as_date


def test_naive_datetime_is_interpreted_as_utc():
    assert as_date(dt.datetime(2026, 9, 14, 0, 30)) == dt.date(2026, 9, 14)


class _Cursor:
    def __init__(self):
        self.sql = ""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params):
        self.sql = sql

    def fetchall(self):
        return [(dt.date(2026, 9, 14), 3)]


class _Conn:
    def __init__(self):
        self.cursor_obj = _Cursor()

    def cursor(self):
        return self.cursor_obj


def test_non_pair_dataset_discovers_one_cell_per_date():
    conn = _Conn()
    cells = partitions.discover_cells(
        conn,
        registry.require_dataset("signals_log"),
        dt.date(2026, 9, 14),
        dt.date(2026, 9, 15),
    )
    assert cells == {("2026-09-14",): 3}
    assert "GROUP BY d" in conn.cursor_obj.sql
    assert "exchange" not in conn.cursor_obj.sql.split("GROUP BY", 1)[1]


def test_non_pair_dataset_writes_one_logical_partition_per_date(monkeypatch, tmp_path):
    spec = registry.require_dataset("signals_log")
    key = {"date": "2026-09-14"}
    monkeypatch.setattr(partitions, "discover_cells", lambda *_args: {(key["date"],): 2})
    monkeypatch.setattr(partitions.reconcile, "fetch_cell_rows", lambda *_args: [["row"]])
    monkeypatch.setattr(partitions, "row_digest_of_rows", lambda *_args: "digest")
    monkeypatch.setattr(
        partitions,
        "write_partition",
        lambda _root, _spec, written_key, rows: {
            "logical_partition_key": written_key,
            "path": "signals_log/date=2026-09-14.r1.parquet",
            "rows": len(rows),
            "time_min": "2026-09-14T00:00:00Z",
            "time_max": "2026-09-14T00:00:00Z",
            "row_digest": "sha256:" + "a" * 64,
            "bytes": 1,
            "sha256": "0" * 64,
        },
    )

    produced, produced_keys, written = partitions.produce_partitions(
        tmp_path, spec, object(), dt.date(2026, 9, 14), dt.date(2026, 9, 15), [], {}
    )
    assert len(produced) == len(produced_keys) == len(written) == 1
    assert produced_keys == [key]
    assert "db_symbol" not in produced[0]["logical_partition_key"]


def test_non_pair_empty_cells_use_data_dates_not_an_unreachable_dimension():
    spec = registry.require_dataset("signals_log")
    present = [{"date": "2026-09-14"}, {"date": "2026-09-16"}]
    assert partitions.empty_cell_keys(
        spec, "full", present, ["2026-09-14", "2026-09-15", "2026-09-16"]
    ) == [{"date": "2026-09-15"}]


class _QualityCursor:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql):
        self.sql = sql

    def fetchall(self):
        return [("binanceusdm", "BTC/USDT", dt.date(2026, 9, 14), 1)]


class _QualityConn:
    def cursor(self):
        return _QualityCursor()


def test_quality_flag_without_symbol_mapping_fails_closed():
    with pytest.raises(DataBridgeError, match="质量标记无法映射"):
        partitions.quality_flags(_QualityConn(), {})
