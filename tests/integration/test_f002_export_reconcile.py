"""F002 导出→对账→失效语义→中断恢复 集成测试（AC-001/002/010/014）。

需要本地 docker + quant-timescaledb 在线；使用一次性 f002_integration 库，
不触碰生产 quant 库与真实 lake/（见 conftest f002_db / f002_lake fixture）。
"""

from __future__ import annotations

import datetime as dt

import psycopg2
import pytest

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import paths, reconcile, registry
from alphamill.data_bridge.errors import InvalidVersionError, VersionNotFoundError
from alphamill.data_bridge.exporter import export_dataset
from alphamill.data_bridge.reader import read

from conftest import D1, D2, D3, D4, seed_f002_data

pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = __import__("os").getenv("ALPHAMILL_INTEGRATION", "").lower() in {
    "1", "true", "yes"
}

UTC = dt.UTC


def _require_or_skip(available: bool, reason: str) -> None:
    import os

    if available:
        return
    if INTEGRATION_REQUIRED:
        pytest.fail(reason)
    pytest.skip(reason)


@pytest.fixture()
def seeded(f002_conn, f002_lake):
    seed_f002_data(f002_conn)
    from conftest import export_symbol_map_for

    export_symbol_map_for(f002_conn, f002_lake)
    return f002_lake


def _db_count(conn, sql: str, params: tuple = ()) -> int:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return int(cur.fetchone()[0])


def test_ac001_full_export_all_datasets_reconciles(seeded, f002_conn):
    """AC-001：全量导出五 dataset，分区+manifest 齐备，DuckDB 行数与库一致。"""
    lake = seeded
    for dataset in registry.DATASETS:
        summary = export_dataset(dataset, mode="full", window_end=f"{D4}T00:00:00Z", conn=f002_conn)
        assert summary["status"] == "valid", (dataset, summary)
        manifest = mf.load_manifest(lake, dataset, summary["data_version"])
        assert manifest["reconcile"] == {"rows": "ok", "time_bounds": "ok", "row_digest": "ok"}
        assert manifest["source_snapshot"]["backend_xmin"] > 0
        assert manifest["caliber"] == {"close": "raw", "adjclose": "none_crypto"}
        for partition in manifest["partitions"]:
            assert (lake / partition["path"]).is_file()

    counts = {
        "ohlcv_1m": 11,  # BTC D1×5 + D3×1；ETH D1×5
        "derivatives_funding_rates": 3,
        "derivatives_open_interest": 2,
        "derivatives_mark_index_basis": 0,  # 空表 → 合法空快照
        "signals_log": 3,
    }
    for dataset, expected in counts.items():
        db_rows = _db_count(f002_conn, f"SELECT count(*) FROM {dataset}")
        assert db_rows == expected, dataset
        # BTC D1 带未解决质量旗 → 默认拒绝（详见 reader 测试），此处显式豁免
        result = read(dataset, lake_root=lake, allow_flagged=True)
        assert result.frame.empty if expected == 0 else len(result.frame) == expected
        assert result.data_version == mf.latest_valid_version(lake, dataset)

    flagged_result = read("ohlcv_1m", lake_root=lake, allow_flagged=True)
    assert flagged_result.flagged == [f"binance/BTC-USDT/{D1}"]

    basis = mf.load_manifest(lake, "derivatives_mark_index_basis",
                             mf.latest_valid_version(lake, "derivatives_mark_index_basis"))
    assert basis["partitions"] == [] and basis["rows"] == 0

    ohlcv = mf.load_manifest(lake, "ohlcv_1m", mf.latest_valid_version(lake, "ohlcv_1m"))
    assert ohlcv["quality"]["flagged_partitions"] == [f"binance/BTC-USDT/{D1}"]
    assert ohlcv["quality"]["unresolved_total"] == 1
    # BTC 跨度 D1..D3 内 D2 缺失 → skipped 完整逻辑键
    assert {"exchange": "binance", "pair": "BTC-USDT", "date": D2} in ohlcv["skipped"]
    assert ohlcv["pairs"] == ["BTC-USDT", "ETH-USDT"]


def test_ac002_reconcile_failure_marks_invalid(seeded, f002_conn, monkeypatch):
    """AC-002：构造对账不一致 → 版本发布为 invalid，取数拒绝，latest 跳过。"""
    lake = seeded
    real_stats = reconcile.source_partition_stats

    def corrupted_stats(conn, spec, key):
        stats = real_stats(conn, spec, key)
        stats["rows"] += 1  # 模拟湖侧少写一行的不一致
        return stats

    monkeypatch.setattr(reconcile, "source_partition_stats", corrupted_stats)
    summary = export_dataset("ohlcv_1m", mode="full", window_end=f"{D4}T00:00:00Z", conn=f002_conn)
    monkeypatch.undo()

    version = summary["data_version"]
    assert version is not None, "对账失败的版本仍须以 invalid 状态发布（审计证据）"
    assert summary["status"] == "invalid"
    manifest = mf.load_manifest(lake, "ohlcv_1m", version)
    assert manifest["status"] == "invalid"
    assert manifest["reconcile"]["rows"] == "mismatch"
    assert manifest["reconcile"]["failing_partitions"]

    with pytest.raises(InvalidVersionError):
        read("ohlcv_1m", data_version=version, lake_root=lake)
    with pytest.raises(VersionNotFoundError):
        mf.latest_valid_version(lake, "ohlcv_1m")  # 唯一版本 invalid → 无 latest
    with pytest.raises(VersionNotFoundError):
        read("ohlcv_1m", lake_root=lake)


def test_ac010_concurrent_upsert_no_false_valid(seeded, f002_conn):
    """AC-010：对账期间并发 upsert 历史行 → valid 且与导出快照一致（非伪 valid）。"""
    lake = seeded
    target = (f"{D1}T00:00:00Z",)
    upsert_conn = psycopg2.connect(**_conn_kwargs())

    def concurrent_upsert(_export_conn) -> None:
        # 与导出事务并发的第二连接：改写已导出窗口内的历史行
        with upsert_conn.cursor() as cur:
            cur.execute(
                "UPDATE ohlcv_1m SET close = 555.0 WHERE exchange='binance'"
                " AND symbol='BTC/USDT' AND time = %s",
                (dt.datetime.fromisoformat(f"{D1}T00:00:00+00:00"),),
            )
        upsert_conn.commit()

    try:
        summary = export_dataset(
            "ohlcv_1m", mode="full", window_end=f"{D4}T00:00:00Z",
            conn=f002_conn, post_export_hook=concurrent_upsert,
        )
        assert summary["status"] == "valid"
        assert summary["reconcile"]["row_digest"] == "ok"

        result = read("ohlcv_1m", start=f"{D1}T00:00:00Z", end=f"{D1}T00:01:00Z",
                      pairs=["BTC-USDT"], lake_root=lake, allow_flagged=True)
        assert len(result.frame) == 1
        lake_close = float(result.frame.iloc[0]["close"])
        assert lake_close == 100.0, "湖内必须与导出快照一致（REPEATABLE READ），不是并发新值"
        assert _db_count(
            f002_conn,
            "SELECT count(*) FROM ohlcv_1m WHERE close = 555.0 AND time = %s", target,
        ) == 1, "并发 upsert 必须已落在源库（证明竞态真实发生）"
    finally:
        with upsert_conn.cursor() as cur:
            cur.execute(
                "UPDATE ohlcv_1m SET close = 100.0 WHERE close = 555.0"
            )
        upsert_conn.commit()
        upsert_conn.close()


def _conn_kwargs() -> dict:
    import os

    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": __import__("conftest", fromlist=["F002_DB"]).F002_DB,
        "user": os.getenv("DB_USER", "quant"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def test_ac014_interrupted_run_resumes_without_hole(seeded, f002_conn):
    """AC-014：分区已 rename、manifest 未发布的中断态重跑 → 不漏日且 skipped 继承。"""
    lake = seeded

    v1 = export_dataset("ohlcv_1m", mode="full", window_end=f"{D2}T00:00:00Z", conn=f002_conn)
    assert v1["status"] == "valid" and v1["partitions"] == 2  # BTC D1 + ETH D1

    # 为 D2 准备新数据（BTC D2 ×2；测试末清理）
    with f002_conn.cursor() as cur:
        for minute in (0, 1):
            cur.execute(
                "INSERT INTO ohlcv_1m (time, exchange, symbol, open, high, low, close, volume)"
                " VALUES (%s,'binance','BTC/USDT',100,101,99,100,1)",
                (dt.datetime.fromisoformat(f"{D2}T00:0{minute}:00+00:00"),),
            )
    f002_conn.commit()

    def crash_after_rename(_conn) -> None:
        raise RuntimeError("模拟进程中断：分区已 rename，manifest 未发布")

    with pytest.raises(RuntimeError):
        export_dataset("ohlcv_1m", mode="incremental", window_end=f"{D3}T00:00:00Z",
                       conn=f002_conn, post_export_hook=crash_after_rename)
    # 中断态：D2 的 .r1 文件已在正式路径，但无任何新 manifest
    assert mf.list_versions(lake, "ohlcv_1m") == [v1["data_version"]]
    orphans = list((lake / "ohlcv_1m" / f"exchange=binance/pair=BTC-USDT").glob(f"date={D2}.*"))
    assert len(orphans) == 1

    # 重跑：窗口起点必须仍由 v1 推导（D1+1=D2），孤儿 .r1 不计入游标
    v2 = export_dataset("ohlcv_1m", mode="incremental", window_end=f"{D3}T00:00:00Z",
                        conn=f002_conn)
    assert v2["status"] == "valid"
    manifest = mf.load_manifest(lake, "ohlcv_1m", v2["data_version"])
    keys = [p["logical_partition_key"] for p in manifest["partitions"]]
    assert {"exchange": "binance", "pair": "BTC-USDT", "date": D2} in keys, \
        "中断当天必须回到新版本清单（防永久漏日）"
    d2_entry = next(p for p in manifest["partitions"]
                    if p["logical_partition_key"]["date"] == D2)
    assert d2_entry["path"].endswith(f"date={D2}.r2.parquet"), "重跑写 rN+1，不覆盖孤儿"
    # ETH 本轮无数据 → skipped 登记完整逻辑键
    assert {"exchange": "binance", "pair": "ETH-USDT", "date": D2} in manifest["skipped"]

    result = read("ohlcv_1m", data_version=v2["data_version"],
                  start=f"{D2}T00:00:00Z", end=f"{D2}T00:02:00Z", lake_root=lake)
    assert len(result.frame) == 2

    with f002_conn.cursor() as cur:
        cur.execute("DELETE FROM ohlcv_1m WHERE symbol='BTC/USDT' AND time >= %s AND time < %s",
                    (dt.datetime.fromisoformat(f"{D2}T00:00:00+00:00"),
                     dt.datetime.fromisoformat(f"{D3}T00:00:00+00:00")))
    f002_conn.commit()


def _conn_kwargs_shim():  # 供上文使用前定义顺序无碍
    return _conn_kwargs()
