"""T005 与 `AC-002`：`UniverseDef` 内容寻址、人工确认冻结与版本化。

覆盖：id 只覆盖口径+快照+候选（冻结不改身份）、定义写一次（同 id 内容不同即报错）、
草稿不得驱动长跑、冻结记录记人记时且不可原地改写、成员增删产生新版本且旧版本只读。
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from test_f008_discover import _criteria, _market, _snapshot

from alphamill.data_bridge.universe import definition as def_mod
from alphamill.data_bridge.universe.definition import (
    build_definition,
    freeze_definition,
    is_frozen,
    load_definition,
    load_freeze,
    require_frozen,
    write_definition,
)
from alphamill.data_bridge.universe.discover import evaluate
from alphamill.data_bridge.universe.errors import (
    UniverseAlreadyFrozenError,
    UniverseArtifactError,
    UniverseNotFoundError,
    UniverseNotFrozenError,
)

SNAPSHOT_AT = "2026-09-19T00:00:00Z"


def _definition(tmp_path, *records, criteria=None):
    chosen = criteria or _criteria(turnover_rank_top_n=5)
    snapshot = _snapshot(*records)
    return build_definition(chosen, evaluate(snapshot, chosen)), chosen


# ---------- 内容寻址 ----------


def test_universe_id_ignores_freeze_time_and_changes_with_content(tmp_path) -> None:
    definition, criteria = _definition(tmp_path, _market("BTC"), _market("ETH"))
    write_definition(definition, tmp_path)
    freeze_definition(definition.universe_id, frozen_by="georg", lake_root=tmp_path)
    # 冻结不改身份：同一 id 仍能载入同一内容
    reloaded = load_definition(definition.universe_id, tmp_path)
    assert reloaded.payload() == definition.payload()

    other_criteria = _criteria(turnover_rank_top_n=1)
    other = build_definition(
        other_criteria, evaluate(_snapshot(_market("BTC"), _market("ETH")), other_criteria)
    )
    assert other.universe_id != definition.universe_id


def test_universe_id_changes_when_snapshot_time_changes(tmp_path) -> None:
    criteria = _criteria()
    first = build_definition(
        criteria,
        evaluate(_snapshot(_market("BTC")), criteria),
    )
    from alphamill.data_bridge.universe.discover import MarketSnapshot

    later = MarketSnapshot(
        exchange="binance",
        market_type="perp",
        snapshot_at="2026-09-20T00:00:00Z",
        markets=_snapshot(_market("BTC")).markets,
    )
    second = build_definition(criteria, evaluate(later, criteria))
    assert first.universe_id != second.universe_id


def test_definition_path_is_lake_metadata(tmp_path) -> None:
    assert def_mod.defs_dir(tmp_path) == tmp_path / "_metadata" / "universe_defs"
    definition, _ = _definition(tmp_path, _market("BTC"))
    path = write_definition(definition, tmp_path)
    assert path.name == f"{definition.universe_id}.json"
    assert definition.universe_id.startswith("sha256:")


# ---------- 写一次与 fail-closed ----------


def test_definition_is_write_once(tmp_path) -> None:
    definition, _ = _definition(tmp_path, _market("BTC"))
    path = write_definition(definition, tmp_path)
    original = path.read_bytes()
    assert write_definition(definition, tmp_path) == path  # 幂等重写同内容
    path.write_bytes(original + b" ")
    with pytest.raises(UniverseArtifactError, match="内容不一致"):
        write_definition(definition, tmp_path)


def test_load_definition_rejects_tampered_content(tmp_path) -> None:
    definition, _ = _definition(tmp_path, _market("BTC"))
    path = write_definition(definition, tmp_path)
    path.write_bytes(path.read_bytes().replace(b"BTC/USDT", b"ETH/USDT"))
    with pytest.raises(UniverseArtifactError, match="universe_id 不符"):
        load_definition(definition.universe_id, tmp_path)


def test_load_definition_rejects_unknown_keys(tmp_path) -> None:
    definition, _ = _definition(tmp_path, _market("BTC"))
    path = write_definition(definition, tmp_path)
    payload = path.read_text(encoding="utf-8").replace(
        '"snapshot_at"', '"extra_field": 1, "snapshot_at"'
    )
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(UniverseArtifactError, match="键集合非法"):
        load_definition(definition.universe_id, tmp_path)


def test_load_definition_missing_file_is_not_found(tmp_path) -> None:
    with pytest.raises(UniverseNotFoundError):
        load_definition("sha256:" + "0" * 64, tmp_path)


# ---------- 冻结 ----------


def test_unfrozen_draft_cannot_drive_long_running_task(tmp_path) -> None:
    definition, _ = _definition(tmp_path, _market("BTC"))
    write_definition(definition, tmp_path)
    assert is_frozen(definition.universe_id, tmp_path) is False
    assert load_freeze(definition.universe_id, tmp_path) is None
    with pytest.raises(UniverseNotFrozenError) as excinfo:
        require_frozen(definition.universe_id, tmp_path)
    assert excinfo.value.code == "E_UNIVERSE_NOT_FROZEN"


def test_freeze_requires_human_and_is_recorded(tmp_path) -> None:
    definition, _ = _definition(tmp_path, _market("BTC"))
    write_definition(definition, tmp_path)
    with pytest.raises(UniverseArtifactError, match="frozen_by"):
        freeze_definition(definition.universe_id, frozen_by="  ", lake_root=tmp_path)

    record = freeze_definition(
        definition.universe_id,
        frozen_by="georg",
        lake_root=tmp_path,
        frozen_at=datetime(2026, 9, 19, 12, 0, tzinfo=UTC),
    )
    assert record.frozen_at == "2026-09-19T12:00:00Z"
    assert load_freeze(definition.universe_id, tmp_path) == record
    assert require_frozen(definition.universe_id, tmp_path).universe_id == definition.universe_id


def test_freeze_record_cannot_be_rewritten(tmp_path) -> None:
    definition, _ = _definition(tmp_path, _market("BTC"))
    write_definition(definition, tmp_path)
    freeze_definition(definition.universe_id, frozen_by="georg", lake_root=tmp_path)
    path = def_mod.freeze_path(definition.universe_id, tmp_path)
    path.write_bytes(path.read_bytes().replace(b"georg", b"other"))
    with pytest.raises(UniverseArtifactError, match="内容不一致"):
        freeze_definition(definition.universe_id, frozen_by="georg", lake_root=tmp_path)


def test_freezing_unknown_definition_fails_closed(tmp_path) -> None:
    with pytest.raises(UniverseNotFoundError):
        freeze_definition("sha256:" + "1" * 64, frozen_by="georg", lake_root=tmp_path)


# ---------- 版本化 ----------


def test_member_change_produces_new_version_and_old_version_is_readonly(tmp_path) -> None:
    first, criteria = _definition(tmp_path, _market("BTC"), _market("ETH"))
    write_definition(first, tmp_path)
    freeze_definition(first.universe_id, frozen_by="georg", lake_root=tmp_path)
    first_bytes = def_mod.definition_path(first.universe_id, tmp_path).read_bytes()

    second = build_definition(
        criteria,
        evaluate(_snapshot(_market("BTC"), _market("ETH"), _market("SOL")), criteria),
    )
    write_definition(second, tmp_path)
    freeze_definition(second.universe_id, frozen_by="georg", lake_root=tmp_path)

    assert second.universe_id != first.universe_id
    assert first.selected_pairs() == ("BTC/USDT", "ETH/USDT")
    assert second.selected_pairs() == ("BTC/USDT", "ETH/USDT", "SOL/USDT")
    # 旧版本字节未变，且仍可按显式 id 读取
    assert def_mod.definition_path(first.universe_id, tmp_path).read_bytes() == first_bytes
    assert load_definition(first.universe_id, tmp_path).selected_pairs() == (
        "BTC/USDT",
        "ETH/USDT",
    )


def test_duplicate_versions_are_rejected_by_self_check(tmp_path) -> None:
    definition, _ = _definition(tmp_path, _market("BTC"))
    with pytest.raises(UniverseAlreadyFrozenError):
        def_mod.ensure_unique_versions([definition.universe_id, definition.universe_id])
    def_mod.ensure_unique_versions([definition.universe_id, "sha256:" + "2" * 64])
