"""F011 集成旅程：真实 scratch 库 + 临时湖上的「三版宇宙」导出（AC-001/002/006/009）。

时间线（全部 UTC）：
- 源库：BTC / ETH / SOL 在 09-01 ~ 09-06 每天各一行 1m；
- `U1`（快照 08-30，冻结 08-31）选 BTC/ETH/SOL；
- `U2`（快照 09-02 12:00，冻结 09-03 10:00）选 BTC/SOL，ETH 落选 → 截止日 09-03；
- `U3`（快照 09-04 12:00，冻结 09-05 10:00）三者全选，ETH 重新入选；
- SOL 于 09-02 12:00 退市（台账追加 `delisted` 行）→ 截止日 09-02。

绑定一律按窗口终点解析（`resolve_binding(at)`），与导出 CLI 的生产路径同口径。
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest
from conftest import export_symbol_map_for

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge.exporter import export_dataset
from alphamill.data_bridge.universe.admission import admit_pair
from alphamill.data_bridge.universe.binding import resolve_binding
from alphamill.data_bridge.universe.definition import load_definition
from alphamill.data_bridge.universe.membership import (
    MembershipRow,
    append_membership,
    load_membership,
)
from alphamill.data_bridge.universe.quality_gate import VERDICT_ACTIVE, PairGateResult
from tests.f011_fixtures import define_universe, utc

pytestmark = pytest.mark.integration

SYMBOLS = ("BTC/USDT", "ETH/USDT", "SOL/USDT")
DAYS = [date(2026, 9, 1) + timedelta(days=offset) for offset in range(6)]


_utc = utc


def _define(lake, *, selected, dropped=(), snapshot_at, frozen_at) -> str:
    return define_universe(
        lake,
        selected=selected,
        dropped=dropped,
        snapshot_at=snapshot_at,
        frozen_at=frozen_at,
    ).universe_id


def _seed_ohlcv(conn) -> None:
    with conn.cursor() as cur:
        for day in DAYS:
            for symbol in SYMBOLS:
                cur.execute(
                    "INSERT INTO ohlcv_1m (time, exchange, symbol, open, high, low, close, volume)"
                    " VALUES (%s,'binance',%s,100,101,99,100,1)",
                    (datetime.combine(day, datetime.min.time(), tzinfo=UTC), symbol),
                )
    conn.commit()


@pytest.fixture()
def world(f008_conn, f002_lake):
    """三版冻结定义 + 三对准入（ACTIVE、台账 09-01 上市）+ SOL 退市。"""
    lake = f002_lake
    _seed_ohlcv(f008_conn)
    export_symbol_map_for(f008_conn, lake)
    ids = {
        "U1": _define(
            lake,
            selected=("BTC", "ETH", "SOL"),
            snapshot_at="2026-08-30T00:00:00Z",
            frozen_at="2026-08-31",
        ),
        "U2": _define(
            lake,
            selected=("BTC", "SOL"),
            dropped=("ETH",),
            snapshot_at="2026-09-02T12:00:00Z",
            frozen_at="2026-09-03T10:00:00",
        ),
        "U3": _define(
            lake,
            selected=("BTC", "ETH", "SOL"),
            snapshot_at="2026-09-04T12:00:00Z",
            frozen_at="2026-09-05T10:00:00",
        ),
    }
    definition = load_definition(ids["U1"], lake)
    for symbol in SYMBOLS:
        base = symbol.split("/")[0]
        admit_pair(
            f008_conn,
            definition=definition,
            result=PairGateResult(
                db_symbol=symbol,
                lake_pair=f"{base}-USDT",
                exchange="binance",
                market_type="spot",
                verdict=VERDICT_ACTIVE,
                reason_code=None,
                metrics={"synthetic": True},
            ),
            lake_root=lake,
            hostname="qiaozhi-lt",
            listed_at=_utc("2026-09-01"),
        )
    append_membership(
        f008_conn,
        [
            MembershipRow(
                exchange="binance",
                market_type=market_type,
                db_symbol="SOL/USDT",
                lake_pair=lake_pair,
                valid_from=_utc("2026-09-02T12:00:00"),
                reason="delisted",
                universe_id=ids["U1"],
            )
            for market_type, lake_pair in (("spot", "SOL-USDT"), ("perp", "SOL-USDT-PERP"))
        ],
    )
    return {"lake": lake, "conn": f008_conn, "ids": ids}


def _export(world, mode: str, end: str, *, lake_root=None, bound: bool = True) -> dict:
    at = _utc(end)
    return export_dataset(
        "ohlcv_1m",
        mode=mode,
        window_end=f"{end}T00:00:00Z",
        conn=world["conn"],
        lake_root=lake_root or world["lake"],
        universe_filter=True,
        bound_universe=resolve_binding(at, lake_root=world["lake"]) if bound else None,
    )


def _cells(lake, summary) -> set[tuple[str, str]]:
    version = summary["data_version"] or summary["baseline_version"]
    manifest = mf.load_manifest(lake, "ohlcv_1m", version)
    return {
        (p["logical_partition_key"]["pair"], p["logical_partition_key"]["date"])
        for p in manifest["partitions"]
    }


def _grid(pair: str, *days: int) -> set[tuple[str, str]]:
    return {(pair, f"2026-09-{day:02d}") for day in days}


def _ledger(conn) -> list[tuple]:
    return sorted(
        (r.market_type, r.lake_pair, r.valid_from.isoformat(), r.reason)
        for r in load_membership(conn)
    )


def test_journey_drop_cutoff_reentry_and_mode_consistency(world) -> None:
    """AC-001 / AC-002 / D13 / D15：落选即移出、截止日前历史不丢、两种 mode 同判据。"""
    lake, conn, ids = world["lake"], world["conn"], world["ids"]
    ledger_before = _ledger(conn)

    first = _export(world, "incremental", "2026-09-03")  # 绑定 U1（U2 当时尚未冻结）
    assert first["universe_id"] == ids["U1"]
    assert first["dropped_by_universe"] == []
    assert _cells(lake, first) == (
        _grid("BTC-USDT", 1, 2) | _grid("ETH-USDT", 1, 2) | _grid("SOL-USDT", 1, 2)
    ), "SOL 退市截止 09-02：之前照常产出"

    dropped = _export(world, "incremental", "2026-09-05")  # 绑定 U2：ETH 落选，截止 09-03
    assert dropped["status"] == "valid", "截止日前的 ETH/SOL 分区照常与源库对账"
    assert dropped["universe_id"] == ids["U2"]
    assert dropped["dropped_by_universe"] == ["ETH/USDT"]
    expected_u2 = (
        _grid("BTC-USDT", 1, 2, 3, 4) | _grid("ETH-USDT", 1, 2, 3) | _grid("SOL-USDT", 1, 2)
    )
    assert _cells(lake, dropped) == expected_u2
    manifest = mf.load_manifest(lake, "ohlcv_1m", dropped["data_version"])
    assert "ETH-USDT" in manifest["pairs"], "manifest pairs 保留落选 pair 截止日前的历史"
    assert manifest["skipped"] == [], "截止日后的日期是策略排除，不记缺口"

    full = _export(world, "full", "2026-09-05")
    assert full["no_op"] is True, f"全量与增量同一判据，内容不应变化: {full}"
    again = _export(world, "incremental", "2026-09-05")
    assert again["no_op"] is True, "增量→全量→增量：skipped 不翻转、不发布新版本"

    reentry = _export(world, "incremental", "2026-09-06")  # 绑定 U3：ETH 重新入选
    assert reentry["universe_id"] == ids["U3"]
    assert reentry["dropped_by_universe"] == []
    assert ("ETH-USDT", "2026-09-05") in _cells(lake, reentry)
    assert ("ETH-USDT", "2026-09-04") not in _cells(lake, reentry), "增量不回填落选期"

    backfill = _export(world, "full", "2026-09-06")
    assert backfill["no_op"] is False and backfill["status"] == "valid", backfill
    assert ("ETH-USDT", "2026-09-04") in _cells(lake, backfill), "首次全量补回落选期"
    assert _export(world, "incremental", "2026-09-06")["no_op"] is True
    assert _export(world, "full", "2026-09-06")["no_op"] is True, "补回后两种 mode 重新一致"

    assert _ledger(conn) == ledger_before, "落选/重新入选全程不写台账"


def test_empty_lake_full_export_rebuilds_history_up_to_each_cutoff(world, tmp_path) -> None:
    """AC-002 空湖首导：历史从源库产出，不依赖湖里已有内容。"""
    fresh = tmp_path / "fresh-lake"
    export_symbol_map_for(world["conn"], fresh)
    summary = _export(world, "full", "2026-09-05", lake_root=fresh)
    assert summary["status"] == "valid", summary
    assert _cells(fresh, summary) == (
        _grid("BTC-USDT", 1, 2, 3, 4) | _grid("ETH-USDT", 1, 2, 3) | _grid("SOL-USDT", 1, 2)
    )


def test_full_export_absorbs_source_revision_before_cutoff(world) -> None:
    lake, conn = world["lake"], world["conn"]
    _export(world, "full", "2026-09-05")
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE ohlcv_1m SET close = 123 WHERE symbol = 'ETH/USDT' AND time = %s",
            (_utc("2026-09-02"),),
        )
    conn.commit()

    revised = _export(world, "full", "2026-09-05")

    assert revised["status"] == "valid", revised
    manifest = mf.load_manifest(lake, "ohlcv_1m", revised["data_version"])
    changed = {(item["pair"], item["date"]) for item in manifest["revision_diff"] if "pair" in item}
    assert ("ETH-USDT", "2026-09-02") in changed, manifest["revision_diff"]


def test_default_off_path_exports_everything_with_null_binding_keys(world) -> None:
    """AC-006：不开过滤时与现状可观察等价——全部 pair × 全部日期；摘要两键为 null/[]。"""
    summary = export_dataset(
        "ohlcv_1m",
        mode="full",
        window_end="2026-09-07T00:00:00Z",
        conn=world["conn"],
        lake_root=world["lake"],
    )
    assert summary["universe_id"] is None
    assert summary["dropped_by_universe"] == []
    all_days = range(1, 7)
    assert _cells(world["lake"], summary) == (
        _grid("BTC-USDT", *all_days) | _grid("ETH-USDT", *all_days) | _grid("SOL-USDT", *all_days)
    )


def test_library_filter_without_binding_keeps_f008_semantics(world) -> None:
    """AC-009：库 API 开过滤但不给绑定 ⇒ F008 原语义（台账 ∩ ACTIVE，无宇宙交集、无截止日）。"""
    summary = _export(world, "full", "2026-09-05", bound=False)
    assert summary["universe_id"] is None
    assert summary["dropped_by_universe"] == []
    assert _cells(world["lake"], summary) == _grid("BTC-USDT", 1, 2, 3, 4) | _grid(
        "ETH-USDT", 1, 2, 3, 4
    )


def test_explicit_binding_replays_an_earlier_version(world, tmp_path) -> None:
    """US-002 / AC-003：显式回绑 `U1` 可复现当时的清单（ETH 不落选），摘要记被绑定版本。"""
    replay_lake = tmp_path / "replay-lake"
    export_symbol_map_for(world["conn"], replay_lake)
    at = _utc("2026-09-05")
    explicit = resolve_binding(at, universe_id=world["ids"]["U1"], lake_root=world["lake"])

    summary = export_dataset(
        "ohlcv_1m",
        mode="full",
        window_end="2026-09-05T00:00:00Z",
        conn=world["conn"],
        lake_root=replay_lake,
        universe_filter=True,
        bound_universe=explicit,
    )

    assert summary["universe_id"] == world["ids"]["U1"]
    assert summary["dropped_by_universe"] == []
    assert _cells(replay_lake, summary) == (
        _grid("BTC-USDT", 1, 2, 3, 4) | _grid("ETH-USDT", 1, 2, 3, 4) | _grid("SOL-USDT", 1, 2)
    )


def test_non_pair_dataset_records_binding_but_drops_nothing(world) -> None:
    """检视 R4：`signals_log` 无 pair 维度，绑定照记，但没有任何单元格因绑定被剔除。"""
    summary = export_dataset(
        "signals_log",
        mode="full",
        window_end="2026-09-05T00:00:00Z",
        conn=world["conn"],
        lake_root=world["lake"],
        universe_filter=True,
        bound_universe=resolve_binding(_utc("2026-09-05"), lake_root=world["lake"]),
    )
    assert summary["universe_id"] == world["ids"]["U2"]
    assert summary["dropped_by_universe"] == []
