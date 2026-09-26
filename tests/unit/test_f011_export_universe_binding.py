"""F011：导出准入绑定当前宇宙版本——解析规则、准入与截止日、摘要、确定性（单元层）。

绑定解析（`binding.resolve_binding`）是纯文件计算：在 scratch 湖里写定义与冻结记录
（冻结时刻可注入），不连库。准入计算（`verdicts.export_admission`）把判定与台账两次
读库替换成内存桩，只验集合语义与查询次数。
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from alphamill.data_bridge.universe import binding as binding_mod
from alphamill.data_bridge.universe.definition import (
    UniverseDef,
    build_definition,
    freeze_definition,
    freeze_path,
    write_definition,
)
from alphamill.data_bridge.universe.discover import MarketSnapshot, evaluate
from alphamill.data_bridge.universe.errors import (
    UniverseAmbiguousError,
    UniverseArtifactError,
    UniverseLookaheadError,
    UniverseNotFoundError,
    UniverseNotFrozenError,
)
from tests.f008_fixtures import criteria_for, market


def _utc(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


def _define(
    lake: Path,
    *,
    selected: tuple[str, ...],
    dropped: tuple[str, ...] = (),
    snapshot_at: str,
    frozen_at: str | None,
    market_type: str = "perp",
) -> UniverseDef:
    """写一版定义：`selected` 按成交额排前、`dropped` 垫底并被 top_n 截掉（仍是候选）。"""
    criteria = criteria_for(turnover_rank_top_n=len(selected), market_type=market_type)
    records = [market(base, turnover=10_000_000.0 - index) for index, base in enumerate(selected)]
    records += [market(base, turnover=1_000.0 + index) for index, base in enumerate(dropped)]
    snap = MarketSnapshot(
        exchange=criteria.exchange,
        market_type=market_type,
        snapshot_at=snapshot_at,
        markets=tuple(records),
    )
    definition = build_definition(criteria, evaluate(snap, criteria))
    assert {c.db_symbol.split("/")[0] for c in definition.selected} == set(selected)
    write_definition(definition, lake)
    if frozen_at is not None:
        freeze_definition(
            definition.universe_id, frozen_by="tester", lake_root=lake, frozen_at=_utc(frozen_at)
        )
    return definition


@pytest.fixture()
def lake(tmp_path: Path) -> Path:
    return tmp_path / "lake"


# ------------------------------------------------------------------ 解析：默认 / 显式


def test_default_binds_latest_snapshot_among_versions_already_frozen(lake) -> None:
    """AC-003：候选 = `frozen_at ≤ at`；候选内按 `snapshot_at` 取最新——晚冻结的旧快照不胜出。"""
    _define(lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31")
    newer = _define(
        lake, selected=("BTC", "ETH"), snapshot_at="2026-09-02T00:00:00Z", frozen_at="2026-09-03"
    )
    _define(  # 旧快照、晚冻结：不得覆盖更新的快照
        lake, selected=("ETH",), snapshot_at="2026-09-01T00:00:00Z", frozen_at="2026-09-04"
    )

    bound = binding_mod.resolve_binding(_utc("2026-09-05"), lake_root=lake)

    assert bound.universe_id == newer.universe_id
    assert bound.resolution == "default"


def test_historical_window_does_not_bind_a_version_frozen_later(lake) -> None:
    """AC-003 / D12：`snapshot_at ≤ t < frozen_at` 的版本在 t 时尚未生效，不得被绑定。"""
    old = _define(
        lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31"
    )
    _define(
        lake,
        selected=("BTC", "ETH"),
        snapshot_at="2026-09-02T00:00:00Z",
        frozen_at="2026-09-03T10:00:00",
    )

    assert binding_mod.resolve_binding(_utc("2026-09-03"), lake_root=lake).universe_id == (
        old.universe_id
    )


def test_explicit_id_overrides_default_and_gives_a_different_version(lake) -> None:
    older = _define(
        lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31"
    )
    newer = _define(
        lake, selected=("BTC", "ETH"), snapshot_at="2026-09-02T00:00:00Z", frozen_at="2026-09-03"
    )
    at = _utc("2026-09-05")

    explicit = binding_mod.resolve_binding(at, universe_id=older.universe_id, lake_root=lake)

    assert explicit.universe_id == older.universe_id
    assert explicit.resolution == "explicit"
    assert binding_mod.resolve_binding(at, lake_root=lake).universe_id == newer.universe_id
    # 显式回绑较早版本时，版本链止于被绑定版本，不含之后的版本
    assert [d.universe_id for d, _ in explicit.chain] == [older.universe_id]


# ------------------------------------------------------------------ 解析：拒绝分支（IR-003）


def test_no_definition_at_all_is_not_frozen(lake) -> None:
    with pytest.raises(UniverseNotFrozenError) as info:
        binding_mod.resolve_binding(_utc("2026-09-05"), lake_root=lake)
    assert info.value.code == "E_UNIVERSE_NOT_FROZEN"


def test_only_drafts_or_future_versions_is_not_frozen(lake) -> None:
    _define(lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at=None)
    _define(lake, selected=("ETH",), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-09-10")
    with pytest.raises(UniverseNotFrozenError):
        binding_mod.resolve_binding(_utc("2026-09-05"), lake_root=lake)


def test_explicit_unknown_id_is_not_found(lake) -> None:
    _define(lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31")
    with pytest.raises(UniverseNotFoundError) as info:
        binding_mod.resolve_binding(
            _utc("2026-09-05"), universe_id="sha256:" + "0" * 64, lake_root=lake
        )
    assert info.value.code == "E_UNIVERSE_NOT_FOUND"


def test_explicit_draft_is_not_frozen(lake) -> None:
    draft = _define(lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at=None)
    with pytest.raises(UniverseNotFrozenError):
        binding_mod.resolve_binding(
            _utc("2026-09-05"), universe_id=draft.universe_id, lake_root=lake
        )


def test_explicit_version_frozen_after_window_is_lookahead(lake) -> None:
    later = _define(
        lake, selected=("BTC",), snapshot_at="2026-09-02T00:00:00Z", frozen_at="2026-09-06"
    )
    with pytest.raises(UniverseLookaheadError) as info:
        binding_mod.resolve_binding(
            _utc("2026-09-05"), universe_id=later.universe_id, lake_root=lake
        )
    assert info.value.code == "E_UNIVERSE_LOOKAHEAD"


def test_explicit_snapshot_after_window_is_lookahead_even_if_frozen_at_is_injected_early(
    lake,
) -> None:
    """`freeze_definition(frozen_at=...)` 可注入早于求值的冻结时刻，两个条件都要检查。"""
    odd = _define(
        lake, selected=("BTC",), snapshot_at="2026-09-08T00:00:00Z", frozen_at="2026-09-01"
    )
    with pytest.raises(UniverseLookaheadError):
        binding_mod.resolve_binding(_utc("2026-09-05"), universe_id=odd.universe_id, lake_root=lake)


def test_default_rejects_multiple_criteria_scopes(lake) -> None:
    perp = _define(
        lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31"
    )
    _define(
        lake,
        selected=("ETH",),
        snapshot_at="2026-08-30T00:00:00Z",
        frozen_at="2026-08-31",
        market_type="spot",
    )
    at = _utc("2026-09-05")
    with pytest.raises(UniverseAmbiguousError) as info:
        binding_mod.resolve_binding(at, lake_root=lake)
    assert info.value.code == "E_UNIVERSE_AMBIGUOUS"
    # 显式指定可以消歧，版本链只含同口径版本
    explicit = binding_mod.resolve_binding(at, universe_id=perp.universe_id, lake_root=lake)
    assert [d.universe_id for d, _ in explicit.chain] == [perp.universe_id]


def test_corrupt_freeze_record_is_artifact_error(lake) -> None:
    good = _define(
        lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31"
    )
    freeze_path(good.universe_id, lake).write_text("{not json", encoding="utf-8")
    with pytest.raises(UniverseArtifactError):
        binding_mod.resolve_binding(_utc("2026-09-05"), lake_root=lake)


# ------------------------------------------------------------------ 落选截止日（spec §1 术语）


def test_drop_cutoff_is_none_for_pairs_selected_by_the_bound_version(lake) -> None:
    _define(
        lake, selected=("BTC", "ETH"), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31"
    )
    bound = binding_mod.resolve_binding(_utc("2026-09-05"), lake_root=lake)
    assert bound.drop_cutoff("ETH/USDT") is None


def test_drop_cutoff_is_the_freeze_day_of_the_first_dropping_version(lake) -> None:
    _define(
        lake, selected=("BTC", "ETH"), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31"
    )
    _define(
        lake,
        selected=("BTC",),
        dropped=("ETH",),
        snapshot_at="2026-09-02T12:00:00Z",
        frozen_at="2026-09-03T10:00:00",
    )
    bound = binding_mod.resolve_binding(_utc("2026-09-05"), lake_root=lake)
    assert bound.drop_cutoff("ETH/USDT") == date(2026, 9, 3)
    assert bound.drop_cutoff("BTC/USDT") is None


def test_drop_cutoff_does_not_move_when_a_later_version_still_drops_the_pair(lake) -> None:
    """D01 解释点：连续落选段 U2→U2b 取段内最早冻结日，绑定 U2b 也不后移。"""
    _define(
        lake, selected=("BTC", "ETH"), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31"
    )
    _define(
        lake,
        selected=("BTC",),
        dropped=("ETH",),
        snapshot_at="2026-09-02T12:00:00Z",
        frozen_at="2026-09-03",
    )
    later = _define(
        lake,
        selected=("BTC", "SOL"),
        dropped=("ETH",),
        snapshot_at="2026-09-03T12:00:00Z",
        frozen_at="2026-09-04",
    )
    bound = binding_mod.resolve_binding(_utc("2026-09-05"), lake_root=lake)
    assert bound.universe_id == later.universe_id
    assert bound.drop_cutoff("ETH/USDT") == date(2026, 9, 3)


def test_drop_cutoff_resets_after_reentry_and_a_new_drop(lake) -> None:
    _define(
        lake, selected=("BTC", "ETH"), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31"
    )
    _define(
        lake,
        selected=("BTC",),
        dropped=("ETH",),
        snapshot_at="2026-09-01T00:00:00Z",
        frozen_at="2026-09-01",
    )
    reentry = _define(
        lake, selected=("BTC", "ETH"), snapshot_at="2026-09-02T00:00:00Z", frozen_at="2026-09-02"
    )
    at = _utc("2026-09-05")
    assert (
        binding_mod.resolve_binding(
            at, universe_id=reentry.universe_id, lake_root=lake
        ).drop_cutoff("ETH/USDT")
        is None
    )
    _define(
        lake,
        selected=("BTC", "SOL"),
        dropped=("ETH",),
        snapshot_at="2026-09-03T00:00:00Z",
        frozen_at="2026-09-04",
    )
    assert binding_mod.resolve_binding(at, lake_root=lake).drop_cutoff("ETH/USDT") == date(
        2026, 9, 4
    )


def test_drop_cutoff_for_never_selected_pair_is_the_earliest_freeze_in_chain(lake) -> None:
    _define(lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31")
    _define(
        lake, selected=("BTC", "SOL"), snapshot_at="2026-09-02T00:00:00Z", frozen_at="2026-09-03"
    )
    bound = binding_mod.resolve_binding(_utc("2026-09-05"), lake_root=lake)
    assert bound.drop_cutoff("DOGE/USDT") == date(2026, 8, 31)


def test_resolution_is_deterministic(lake) -> None:
    """AC-007：同一湖 + 同一 at ⇒ 同一绑定与同一版本链（与目录枚举顺序无关）。"""
    for day, sel in (
        ("2026-08-30", ("BTC",)),
        ("2026-09-01", ("BTC", "ETH")),
        ("2026-09-02", ("ETH",)),
    ):
        _define(lake, selected=sel, snapshot_at=f"{day}T00:00:00Z", frozen_at=day)
    at = _utc("2026-09-05")
    first = binding_mod.resolve_binding(at, lake_root=lake)
    second = binding_mod.resolve_binding(at, lake_root=lake)
    assert first.universe_id == second.universe_id
    assert [d.universe_id for d, _ in first.chain] == [d.universe_id for d, _ in second.chain]
    assert [f.frozen_at for _, f in first.chain] == sorted(f.frozen_at for _, f in first.chain)
