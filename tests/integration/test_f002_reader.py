"""F002 DuckDB 取数入口集成测试（AC-003/008/009/013）。

复用 conftest 的一次性 f002_integration 库与种子数据；真实 TimescaleDB
在线时运行，否则按 SOP 约定跳过（ALPHAMILL_INTEGRATION=1 下判红）。
"""

from __future__ import annotations

import datetime as dt
import json

import pytest

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge.errors import (
    FlaggedPartitionError,
    InsufficientAsOfFidelityError,
    ManifestIntegrityError,
)
from alphamill.data_bridge.exporter import export_dataset
from alphamill.data_bridge.reader import read

from conftest import D1, D2, D3, D4, seed_f002_data

pytestmark = pytest.mark.integration


@pytest.fixture()
def exported(f002_conn, f002_lake):
    seed_f002_data(f002_conn)
    from conftest import export_symbol_map_for

    export_symbol_map_for(f002_conn, f002_lake)
    for dataset in ("ohlcv_1m", "signals_log"):
        summary = export_dataset(dataset, mode="full", window_end=f"{D4}T00:00:00Z",
                                 conn=f002_conn)
        assert summary["status"] == "valid", (dataset, summary)
    return f002_lake


def test_ac003_read_by_version_time_pairs_reports_identity(exported):
    """AC-003：dataset+version+时间范围+pair 过滤正确，且回报解析身份。"""
    lake = exported
    version = mf.latest_valid_version(lake, "ohlcv_1m")

    result = read("ohlcv_1m", data_version=version,
                  start=f"{D1}T00:00:00Z", end=f"{D1}T00:03:00Z",
                  pairs=["BTC-USDT"], lake_root=lake, allow_flagged=True)
    manifest = mf.load_manifest(lake, "ohlcv_1m", version)
    assert len(result.frame) == 3  # BTC D1 00:00..00:02
    assert set(result.frame["symbol"]) == {"BTC/USDT"}
    assert result.dataset == "ohlcv_1m"
    assert result.data_version == version
    assert result.value_digest == manifest["value_digest"]
    assert result.as_of is None and result.as_of_fidelity is None

    # pair 过滤排除另一 pair
    both = read("ohlcv_1m", start=f"{D1}T00:00:00Z", end=f"{D1}T00:01:00Z",
                lake_root=lake, allow_flagged=True)
    assert len(both.frame) == 2


def test_ac003_explicit_version_immune_to_latest_shift(exported, f002_conn):
    """AC-003：显式版本读取不受后来 latest 变化影响。"""
    lake = exported
    v1 = mf.latest_valid_version(lake, "ohlcv_1m")
    v1_rows = len(read("ohlcv_1m", data_version=v1, lake_root=lake, allow_flagged=True).frame)

    with f002_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ohlcv_1m (time, exchange, symbol, open, high, low, close, volume)"
            " VALUES (%s,'binance','ETH/USDT',100,101,99,100,1)",
            (dt.datetime.fromisoformat(f"{D4}T00:00:00+00:00"),),
        )
    f002_conn.commit()
    v2_summary = export_dataset("ohlcv_1m", mode="incremental",
                                window_end="2026-09-05T00:00:00Z", conn=f002_conn)
    assert v2_summary["data_version"] not in (None, v1)

    assert len(read("ohlcv_1m", data_version=v1, lake_root=lake, allow_flagged=True).frame) == v1_rows
    latest = read("ohlcv_1m", lake_root=lake, allow_flagged=True)
    assert latest.data_version == v2_summary["data_version"]
    assert len(latest.frame) == v1_rows + 1


def test_ac008_integrity_fail_closed_but_unreferenced_files_ok(exported):
    """AC-008：删清单内文件/改一字节 → ManifestIntegrityError；他版本 .rN 不判红。"""
    lake = exported
    version = mf.latest_valid_version(lake, "signals_log")  # signals 无质量旗干扰
    manifest = mf.load_manifest(lake, "signals_log", version)
    target = lake / manifest["partitions"][0]["path"]

    backup = target.read_bytes()
    try:
        target.unlink()
        with pytest.raises(ManifestIntegrityError, match="缺失"):
            read("signals_log", data_version=version, lake_root=lake)

        target.write_bytes(backup[:-1] + bytes([backup[-1] ^ 0xFF]))
        with pytest.raises(ManifestIntegrityError, match="sha256"):
            read("signals_log", data_version=version, lake_root=lake)

        target.write_bytes(backup)
        # 目录里出现本版本未引用的 .r2（其他版本的合法分区）→ reader 不扫目录，正常返回
        ghost = target.with_name(target.name.replace(".r1.", ".r2."))
        ghost.write_bytes(backup)
        result = read("signals_log", data_version=version, lake_root=lake)
        assert len(result.frame) == 3
    finally:
        if not target.is_file():
            target.write_bytes(backup)


def test_ac009_as_of_bitemporal_semantics(exported):
    """AC-009：无前视双时间轴；晚评估的标签置 NULL 而非丢行。"""
    lake = exported
    as_of_10 = dt.datetime.fromisoformat(f"{D1}T10:00:00+00:00")
    as_of_1230 = dt.datetime.fromisoformat(f"{D1}T12:30:00+00:00")
    as_of_13 = dt.datetime.fromisoformat(f"{D1}T13:00:00+00:00")

    # s1/s2 的 available_at（time）= D1 12:00：as_of=10:00 时根本还不存在
    early = read("signals_log", as_of=as_of_10, lake_root=lake)
    assert len(early.frame) == 0
    assert early.as_of_fidelity == "bitemporal"

    # as_of=12:30：两行可见，但 s2 的 realized_return_60m（13:00 才评估）必须置 NULL
    mid = read("signals_log", as_of=as_of_1230, lake_root=lake)
    assert len(mid.frame) == 2
    assert mid.frame["realized_return_60m"].isna().all()

    # as_of=13:00：s2 的标签可见
    late = read("signals_log", as_of=as_of_13, lake_root=lake)
    assert len(late.frame) == 2
    values = late.frame["realized_return_60m"].tolist()
    assert 0.05 in [v for v in values if v == v]  # s2 标签出现（NaN 之外）
    # s1 无评估 → 标签保持 NULL
    s1_row = late.frame[late.frame["expected_return"].isna()]
    assert len(late.frame) - s1_row.shape[0] >= 1

    # 不传 as_of：纯历史切片，as_of_fidelity=None，不得用于回测判定
    plain = read("signals_log", lake_root=lake)
    assert len(plain.frame) == 3 and plain.as_of is None and plain.as_of_fidelity is None


def test_ac013_as_of_on_ohlcv_fail_closed(exported):
    """AC-013：ohlcv_1m 传 as_of 默认抛错；显式豁免后如实回报 event_time_only。"""
    lake = exported
    as_of = dt.datetime.fromisoformat(f"{D1}T12:00:00+00:00")

    with pytest.raises(InsufficientAsOfFidelityError):
        read("ohlcv_1m", as_of=as_of, lake_root=lake, allow_flagged=True)

    result = read("ohlcv_1m", as_of=as_of, lake_root=lake,
                  allow_flagged=True, allow_event_time_only=True)
    assert result.as_of_fidelity == "event_time_only"
    assert len(result.frame) == 10  # D1 全部 10 行（BTC+ETH 各 5），event_time<=T 全可见

    manifest = mf.load_manifest(lake, "ohlcv_1m", result.data_version)
    assert manifest["as_of_fidelity"] == "event_time_only"


def test_flagged_partition_default_refusal(exported):
    """质量旗裁决：默认拒绝被标记分区；allow_flagged 豁免并回报清单。"""
    lake = exported
    with pytest.raises(FlaggedPartitionError, match="BTC-USDT"):
        read("ohlcv_1m", start=f"{D1}T00:00:00Z", end=f"{D1}T00:01:00Z", lake_root=lake)

    allowed = read("ohlcv_1m", start=f"{D1}T00:00:00Z", end=f"{D1}T00:01:00Z",
                   lake_root=lake, allow_flagged=True)
    assert allowed.flagged == [f"binance/BTC-USDT/{D1}"]
    assert len(allowed.frame) == 2

    # 查询未命中被标记分区 → 无需豁免
    clean = read("ohlcv_1m", start=f"{D3}T00:00:00Z", end=f"{D3}T00:01:00Z", lake_root=lake)
    assert len(clean.frame) == 1 and clean.flagged == []
