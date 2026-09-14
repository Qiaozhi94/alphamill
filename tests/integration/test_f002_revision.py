"""F002 修订检测与版本演进集成测试（AC-005/007/011）。

场景顺序敏感（同一模块级库）：
1. AC-011：full(D2)→v1，两次连续增量（插入 D2/D3 行）→ v2/v3 累计快照；
   用例结束时清理插入行。
2. AC-005/007：UPDATE 历史行 → 全量校验产生 v2+revision_diff，v1 字节不变、
   可读、并发读不串版。
"""

from __future__ import annotations

import datetime as dt

import pytest
from conftest import D1, D2, D3, D4, seed_f002_data

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge.exporter import export_dataset
from alphamill.data_bridge.reader import read

pytestmark = pytest.mark.integration


@pytest.fixture()
def exported(f002_conn, f002_lake):
    seed_f002_data(f002_conn)
    from conftest import export_symbol_map_for

    export_symbol_map_for(f002_conn, f002_lake)
    return f002_lake


def _insert_ohlcv(conn, day: str, symbol: str, count: int) -> None:
    with conn.cursor() as cur:
        for minute in range(count):
            cur.execute(
                "INSERT INTO ohlcv_1m (time, exchange, symbol, open, high, low, close, volume)"
                " VALUES (%s,'binance',%s,100,101,99,100,1)",
                (dt.datetime.fromisoformat(f"{day}T00:0{minute}:00+00:00"), symbol),
            )
    conn.commit()


def _delete_ohlcv(conn, day: str, symbol: str) -> None:
    start = dt.datetime.fromisoformat(f"{day}T00:00:00+00:00")
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM ohlcv_1m WHERE symbol=%s AND time >= %s AND time < %s",
            (
                symbol,
                start,
                start + dt.timedelta(days=1),
            ),
        )
    conn.commit()


def test_ac011_two_incrementals_build_cumulative_manifest(exported, f002_conn):
    """AC-011：连续两次增量后，第二版 partitions 覆盖第一版全部逻辑分区，
    rows 是累计总量而非单日 delta；显式读旧版本不被 latest 后移影响。"""
    lake = exported
    v1 = export_dataset("ohlcv_1m", mode="full", window_end=f"{D2}T00:00:00Z", conn=f002_conn)
    m1 = mf.load_manifest(lake, "ohlcv_1m", v1["data_version"])
    assert sum(p["rows"] for p in m1["partitions"]) == 10
    v1_keys = {mf.canonical_key(p["logical_partition_key"]) for p in m1["partitions"]}

    _insert_ohlcv(f002_conn, D2, "BTC/USDT", 2)
    v2 = export_dataset(
        "ohlcv_1m", mode="incremental", window_end=f"{D3}T00:00:00Z", conn=f002_conn
    )
    assert v2["status"] == "valid"

    _insert_ohlcv(f002_conn, D3, "ETH/USDT", 2)
    v3 = export_dataset(
        "ohlcv_1m", mode="incremental", window_end=f"{D4}T00:00:00Z", conn=f002_conn
    )
    assert v3["status"] == "valid"

    m2 = mf.load_manifest(lake, "ohlcv_1m", v2["data_version"])
    m3 = mf.load_manifest(lake, "ohlcv_1m", v3["data_version"])
    m2_keys = {mf.canonical_key(p["logical_partition_key"]) for p in m2["partitions"]}
    m3_keys = {mf.canonical_key(p["logical_partition_key"]) for p in m3["partitions"]}
    assert v1_keys <= m2_keys <= m3_keys, "未变分区必须逐版继承"
    # v2：v1(10) + BTC D2×2 = 12；v3：v2 + BTC D3(种子 1) + ETH D3×2 = 15（累计，非单日）
    assert m2["rows"] == 12
    assert m3["rows"] == 15
    # v2 判定 ETH D2 为空（完整逻辑键），v3 覆盖 D3 后该 skipped 原样继承
    assert {"exchange": "binance", "pair": "ETH-USDT", "date": D2} in m2["skipped"]
    assert {"exchange": "binance", "pair": "ETH-USDT", "date": D2} in m3["skipped"]

    # 显式版本读取互不串版
    r2 = read("ohlcv_1m", data_version=v2["data_version"], lake_root=lake, allow_flagged=True)
    r3 = read("ohlcv_1m", data_version=v3["data_version"], lake_root=lake, allow_flagged=True)
    assert len(r2.frame) == 12 and len(r3.frame) == 15

    _delete_ohlcv(f002_conn, D2, "BTC/USDT")
    _delete_ohlcv(f002_conn, D3, "ETH/USDT")


def test_ac005_ac007_revision_bumps_version_keeps_v1(exported, f002_conn):
    """AC-005/007：修订 → v2+差异清单；v1 分区字节不变、读回修订前值、并发不串版。"""
    lake = exported
    v1 = export_dataset("ohlcv_1m", mode="full", window_end=f"{D4}T00:00:00Z", conn=f002_conn)
    m1 = mf.load_manifest(lake, "ohlcv_1m", v1["data_version"])
    m1_bytes = (lake / "_manifests" / "ohlcv_1m" / f"{v1['data_version']}.json").read_bytes()

    # 修订历史行：BTC D1 00:00 close 100 → 999
    with f002_conn.cursor() as cur:
        cur.execute(
            "UPDATE ohlcv_1m SET close = 999.0 WHERE exchange='binance' AND symbol='BTC/USDT'"
            " AND time = %s",
            (dt.datetime.fromisoformat(f"{D1}T00:00:00+00:00"),),
        )
    f002_conn.commit()

    v2 = export_dataset("ohlcv_1m", mode="full", window_end=f"{D4}T00:00:00Z", conn=f002_conn)
    assert v2["status"] == "valid"
    assert v2["data_version"] != v1["data_version"]
    m2 = mf.load_manifest(lake, "ohlcv_1m", v2["data_version"])

    changed = [d for d in m2["revision_diff"] if d["reason"] == "changed"]
    assert changed and all(d["pair"] == "BTC-USDT" and d["date"] == D1 for d in changed)

    # v1 manifest 与其引用的每个分区文件字节不变
    assert (
        lake / "_manifests" / "ohlcv_1m" / f"{v1['data_version']}.json"
    ).read_bytes() == m1_bytes
    for partition in m1["partitions"]:
        path = lake / partition["path"]
        assert mf.file_sha256(path) == partition["sha256"]
        assert path.stat().st_size == partition["bytes"]

    # 并发读 v1/v2：各回各值，不串版
    r1 = read(
        "ohlcv_1m",
        data_version=v1["data_version"],
        start=f"{D1}T00:00:00Z",
        end=f"{D1}T00:01:00Z",
        pairs=["BTC-USDT"],
        lake_root=lake,
        allow_flagged=True,
    )
    r2 = read(
        "ohlcv_1m",
        data_version=v2["data_version"],
        start=f"{D1}T00:00:00Z",
        end=f"{D1}T00:01:00Z",
        pairs=["BTC-USDT"],
        lake_root=lake,
        allow_flagged=True,
    )
    assert float(r1.frame.iloc[0]["close"]) == 100.0, "v1 必须读回修订前的值"
    assert float(r2.frame.iloc[0]["close"]) == 999.0
    assert r1.data_version == v1["data_version"] and r2.data_version == v2["data_version"]
    assert r1.value_digest != r2.value_digest


def test_full_export_removes_source_partition_and_records_removed(exported, f002_conn):
    """全量重导反映源库删除，且 revision_diff 保留 removed 审计项。"""
    lake = exported
    v1 = export_dataset("ohlcv_1m", mode="full", window_end=f"{D4}T00:00:00Z", conn=f002_conn)
    before = mf.load_manifest(lake, "ohlcv_1m", v1["data_version"])
    assert any(
        p["logical_partition_key"]["pair"] == "ETH-USDT"
        and p["logical_partition_key"]["date"] == D1
        for p in before["partitions"]
    )

    _delete_ohlcv(f002_conn, D1, "ETH/USDT")
    v2 = export_dataset("ohlcv_1m", mode="full", window_end=f"{D4}T00:00:00Z", conn=f002_conn)
    assert v2["status"] == "valid"
    after = mf.load_manifest(lake, "ohlcv_1m", v2["data_version"])
    assert not any(
        p["logical_partition_key"]["pair"] == "ETH-USDT"
        and p["logical_partition_key"]["date"] == D1
        for p in after["partitions"]
    )
    assert any(
        item["reason"] == "removed" and item["pair"] == "ETH-USDT" and item["date"] == D1
        for item in after["revision_diff"]
    )
