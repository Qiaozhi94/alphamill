"""T027 / `DR-001`·`DR-002`·`NFR-002`·`AC-006`：身份稳定性与快照敏感性属性测试。

按 `design.md` §8 的可复现约束执行：固定可复现 seed（`PROPERTY_SEED`，写进证据文件），
输入由**显式策略枚举**生成（集合重排、逐字段扰动），不依赖随机数据分布、不引入第三方
property-testing 框架。失败反例落 `reports/property/f007/<seed>/` 供复现。

两条性质：

1. **稳定性**：同一语义输入、任意构造路径/顺序 → 同一 `experiment_id` / `snapshot_id`；
2. **敏感性**：成员版本/value digest、cutoff、映射/日历摘要或其他实验语义变化 → 必须产生新 ID。
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from alphamill.experiment_store.experiment_context import (
    CONTEXT_SCHEMA_VERSION,
    ExperimentContext,
)
from alphamill.experiment_store.identity import (
    SCHEMA_VERSION,
    ResearchSnapshot,
    SnapshotMember,
    compute_snapshot_id,
    content_digest,
    universe_calendar_digest,
)

PROPERTY_SEED = 20260901
ARCHIVE_SUBDIR = ("property", "f007")
NOW = "2026-09-01T00:00:00Z"
FACTOR = "factor_sha256:" + "a" * 64
COHORT = "cohort_sha256:" + "b" * 64
DIGEST_A = "sha256:" + "1" * 64
DIGEST_B = "sha256:" + "2" * 64
UNIVERSE = "sha256:" + "3" * 64
CALENDAR = "sha256:" + "4" * 64


def _context(**overrides) -> ExperimentContext:
    base = {
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "execution_tier": "canonical",
        "upstream": {"kind": "factor", "id": FACTOR},
        "cohort_id": COHORT,
        "method_config": {"id": "method-v1", "normalized": {"fdr_alpha": 0.05, "hac_lag": 5}},
        "window": {
            "selection": ["2026-01-01T00:00:00Z", "2026-04-01T00:00:00Z"],
            "label_horizons": [1, 4, 24],
        },
        "cost_model": {"id": "cm-v1", "normalized": {"maker_bps": 2, "taker_bps": 5}},
        "research_snapshot_id": DIGEST_A,
        "code_build_digest": DIGEST_B,
        "seed": 7,
    }
    base.update(overrides)
    return ExperimentContext(**base)


def _members(**overrides) -> dict[str, SnapshotMember]:
    member = SnapshotMember(
        dataset="derivatives_funding_rates",
        data_version="v2026.09.01",
        value_digest=DIGEST_A,
        as_of_fidelity="bitemporal",
        event_time_min="2026-09-01T00:00:00Z",
        event_time_max="2026-09-01T23:59:00Z",
    )
    second = SnapshotMember(
        dataset="ohlcv_1m",
        data_version="v2026.09.01",
        value_digest=DIGEST_B,
        as_of_fidelity="bitemporal",
        event_time_min="2026-09-01T00:00:00Z",
        event_time_max="2026-09-01T23:59:00Z",
    )
    members = {"derivatives_funding_rates": member, "ohlcv_1m": second}
    members.update(overrides)
    return members


def _snapshot_id(
    members: dict[str, SnapshotMember], cutoff: str = NOW, combined: str | None = None
) -> str:
    return compute_snapshot_id(
        schema_version=SCHEMA_VERSION,
        cutoff_time=cutoff,
        members=members,
        symbol_map_digest=DIGEST_B,
        combined_digest=combined or universe_calendar_digest(UNIVERSE, CALENDAR),
    )


def archive_counterexample(payload: dict, *, root: Path) -> Path:
    """把失败反例按固定 seed 落盘，供复现（`design.md` §8）。"""
    directory = root.joinpath(*ARCHIVE_SUBDIR, str(PROPERTY_SEED))
    directory.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    name = content_digest(encoded).removeprefix("sha256:")[:16]
    path = directory / f"{name}.json"
    path.write_text(
        json.dumps({"seed": PROPERTY_SEED, **payload}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return path


# ---------- 稳定性 ----------


def test_experiment_id_is_invariant_under_set_permutations():
    canonical = _context().experiment_id
    for horizons in ([24, 1, 4], [4, 24, 1, 4], [1, 4, 24]):
        for selection in (
            ["2026-04-01T00:00:00Z", "2026-01-01T00:00:00Z"],
            ["2026-01-01T00:00:00Z", "2026-04-01T00:00:00Z"],
        ):
            variant = _context(
                window={"selection": selection, "label_horizons": horizons}
            ).experiment_id
            assert variant == canonical


def test_experiment_id_ignores_tier_and_supersedes():
    assert _context(execution_tier="preview").experiment_id == _context().experiment_id
    assert _context(supersedes=DIGEST_B).experiment_id == _context().experiment_id


def test_snapshot_id_is_invariant_under_member_insertion_order():
    forward = dict(_members())
    reverse = {name: _members()[name] for name in reversed(list(_members()))}
    assert _snapshot_id(forward) == _snapshot_id(reverse)


# ---------- 敏感性（显式策略枚举：逐字段扰动） ----------


def test_snapshot_id_depends_on_membership():
    base = _members()
    reduced = {"derivatives_funding_rates": base["derivatives_funding_rates"]}
    assert set(reduced) != set(base)
    assert _snapshot_id(reduced) != _snapshot_id(base)


def test_member_value_digest_change_moves_snapshot_id():
    base = _members()
    changed = {
        **base,
        "ohlcv_1m": SnapshotMember(
            dataset="ohlcv_1m",
            data_version="v2026.09.01",
            value_digest="sha256:" + "9" * 64,
            as_of_fidelity="bitemporal",
            event_time_min="2026-09-01T00:00:00Z",
            event_time_max="2026-09-01T23:59:00Z",
        ),
    }
    assert _snapshot_id(base) != _snapshot_id(changed)


def test_cutoff_change_moves_snapshot_id():
    later = (datetime.fromisoformat(NOW.replace("Z", "+00:00")) + timedelta(hours=1)).isoformat()
    assert _snapshot_id(_members()) != _snapshot_id(_members(), cutoff=later)


def test_universe_and_calendar_digests_move_snapshot_id():
    base = _snapshot_id(_members())
    other_universe = universe_calendar_digest("sha256:" + "8" * 64, CALENDAR)
    other_calendar = universe_calendar_digest(UNIVERSE, "sha256:" + "7" * 64)
    assert _snapshot_id(_members(), combined=other_universe) != base
    assert _snapshot_id(_members(), combined=other_calendar) != base


@pytest.mark.parametrize(
    "overrides",
    [
        {"seed": 8},
        {"research_snapshot_id": DIGEST_B},
        {"code_build_digest": DIGEST_A},
        {"method_config": {"id": "method-v1", "normalized": {"fdr_alpha": 0.01, "hac_lag": 5}}},
        {"cost_model": {"id": "cm-v1", "normalized": {"maker_bps": 3, "taker_bps": 5}}},
        {"upstream": {"kind": "factor", "id": "factor_sha256:" + "c" * 64}},
        {"cohort_id": "cohort_sha256:" + "d" * 64},
        {"execution_tier": "preview"},
    ],
)
def test_experiment_id_sensitivity_is_explicit_per_semantic_field(overrides: dict):
    changed = _context(**overrides).experiment_id
    if overrides.get("execution_tier"):
        assert changed == _context().experiment_id
    else:
        assert changed != _context().experiment_id


def test_snapshot_payload_roundtrip_preserves_identity():
    combined = universe_calendar_digest(UNIVERSE, CALENDAR)
    snapshot = ResearchSnapshot(
        schema_version=SCHEMA_VERSION,
        snapshot_id=_snapshot_id(_members(), combined=combined),
        cutoff_time=NOW,
        members=_members(),
        symbol_map_digest=DIGEST_B,
        universe_digest=UNIVERSE,
        calendar_digest=CALENDAR,
        universe_calendar_digest=combined,
        provenance={"created_at": NOW},
    )
    restored = ResearchSnapshot.from_dict(snapshot.to_dict())
    assert (
        _snapshot_id(
            restored.members,
            cutoff=restored.cutoff_time,
            combined=restored.universe_calendar_digest,
        )
        == snapshot.snapshot_id
    )


# ---------- 反例归档 ----------


def test_counterexample_archive_is_reproducible(tmp_path):
    payload = {"kind": "identity", "input": {"seed": 8}, "expected": _context().experiment_id}
    first = archive_counterexample(payload, root=tmp_path)
    second = archive_counterexample(payload, root=tmp_path)
    assert first == second
    stored = json.loads(first.read_text(encoding="utf-8"))
    assert stored["seed"] == PROPERTY_SEED
    assert first.parent.as_posix().endswith(f"property/f007/{PROPERTY_SEED}")
