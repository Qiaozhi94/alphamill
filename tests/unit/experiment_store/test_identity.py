"""T004 / `DR-002`·`AC-006`：ExperimentContext 规范化、两级内容 ID 与 supersedes 校验。

覆盖：语义相同 → 同一 `experiment_id`；`execution_tier` 与 `supersedes` 不参与身份；
方法/成本/窗口/种子/快照/代码摘要/upstream/cohort 任一变化必产生新 ID；两级结构（父级哈希
子摘要）；数值定标与时间 UTC 规范化；`supersedes` 的存在/同类/非自指/无环校验。
"""

from __future__ import annotations

import pytest

from alphamill.experiment_store.errors import SnapshotInputError
from alphamill.experiment_store.experiment_context import (
    CONTEXT_SCHEMA_VERSION,
    ExperimentContext,
    ExperimentIndex,
    validate_supersedes,
)
from alphamill.experiment_store.identity import (
    canonical_json,
    content_digest,
    decimal_text,
    normalize_numbers,
    normalize_utc_set,
)

DIGEST_A = "sha256:" + "1" * 64
DIGEST_B = "sha256:" + "2" * 64
DIGEST_C = "sha256:" + "3" * 64
DIGEST_D = "sha256:" + "4" * 64
REF_FACTOR = "factor_sha256:" + "a" * 64
COHORT = "cohort_sha256:" + "b" * 64
COHORT_OTHER = "cohort_sha256:" + "c" * 64


def make_context(**overrides) -> ExperimentContext:
    base = {
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "execution_tier": "canonical",
        "upstream": {"kind": "factor", "id": REF_FACTOR},
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


def with_method(normalized: dict) -> ExperimentContext:
    return make_context(method_config={"id": "method-v1", "normalized": normalized})


# ---------- 身份稳定性 ----------


def test_same_semantics_produce_same_id():
    assert make_context().experiment_id == make_context().experiment_id


def test_execution_tier_is_not_part_of_identity():
    canonical = make_context(execution_tier="canonical")
    preview = make_context(execution_tier="preview")
    assert canonical.experiment_id == preview.experiment_id
    assert canonical.normalized()["execution_tier"] != preview.normalized()["execution_tier"]


def test_supersedes_is_not_part_of_identity():
    plain = make_context()
    linked = make_context(supersedes=DIGEST_C)
    assert plain.experiment_id == linked.experiment_id


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seed", 8),
        ("research_snapshot_id", DIGEST_C),
        ("code_build_digest", DIGEST_C),
        ("cohort_id", COHORT_OTHER),
        ("upstream", {"kind": "pool", "id": REF_FACTOR}),
        ("upstream", {"kind": "factor", "id": "factor_sha256:" + "d" * 64}),
    ],
)
def test_semantic_field_change_produces_new_id(field: str, value):
    assert make_context().experiment_id != make_context(**{field: value}).experiment_id


def test_method_and_cost_normalized_change_produce_new_id():
    base = make_context()
    assert base.experiment_id != with_method({"fdr_alpha": 0.01, "hac_lag": 5}).experiment_id
    other_cost = make_context(
        cost_model={"id": "cm-v1", "normalized": {"maker_bps": 3, "taker_bps": 5}}
    )
    assert base.experiment_id != other_cost.experiment_id


def test_window_change_produces_new_id():
    other = make_context(
        window={
            "selection": ["2026-02-01T00:00:00Z", "2026-05-01T00:00:00Z"],
            "label_horizons": [1, 4, 24],
        }
    )
    assert make_context().experiment_id != other.experiment_id


def test_set_fields_are_order_and_duplicate_insensitive():
    shuffled = make_context(
        window={
            "selection": ["2026-04-01T00:00:00Z", "2026-01-01T00:00:00Z"],
            "label_horizons": [24, 1, 4, 1],
        }
    )
    assert make_context().experiment_id == shuffled.experiment_id


def test_timestamps_are_normalized_to_utc():
    offset = make_context(
        window={
            "selection": ["2026-01-01T00:00:00+00:00", "2026-04-01T08:00:00+08:00"],
            "label_horizons": [1, 4, 24],
        }
    )
    assert make_context().experiment_id == offset.experiment_id
    assert offset.normalized()["window"]["selection"] == [
        "2026-01-01T00:00:00Z",
        "2026-04-01T00:00:00Z",
    ]


# ---------- 两级内容 ID ----------


def test_identity_payload_hashes_component_digests_not_raw_configs():
    payload = make_context().identity_payload()
    assert set(payload) == {
        "schema_version",
        "upstream",
        "cohort_id",
        "method_config_digest",
        "window_digest",
        "cost_model_digest",
        "research_snapshot_id",
        "code_build_digest",
        "seed",
    }
    assert "method_config" not in payload and "cost_model" not in payload


def test_experiment_id_is_second_level_over_component_digests():
    context = make_context()
    digests = context.component_digests()
    expected = content_digest(canonical_json({**context.identity_payload()}).encode("utf-8"))
    assert context.experiment_id == expected
    assert context.experiment_id not in digests.values()
    for _name, value in digests.items():
        assert value.startswith("sha256:")
        assert len(value) == len("sha256:") + 64


def test_component_digest_change_moves_experiment_id():
    base = make_context()
    changed = with_method({"fdr_alpha": 0.05, "hac_lag": 6})
    assert (
        base.component_digests()["method_config_digest"]
        != changed.component_digests()["method_config_digest"]
    )
    assert base.experiment_id != changed.experiment_id


def test_roundtrip_preserves_identity_and_normalized_form():
    context = make_context()
    restored = ExperimentContext.from_dict(context.to_dict())
    assert restored.experiment_id == context.experiment_id
    assert restored.to_dict() == context.to_dict()


# ---------- 规范化原语 ----------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.05, "0.05"),
        (0.050, "0.05"),
        (5e-2, "0.05"),
        (100.0, "100"),
        (-0.0, "0"),
        (0.1, "0.1"),
        (5, "5"),
        (5.0, "5"),
    ],
)
def test_decimal_text_has_no_exponent_or_trailing_zeros(value: float, expected: str):
    assert decimal_text(value) == expected


def test_normalize_numbers_scales_ints_and_floats_alike_but_keeps_bools():
    """R1-115：`5` 与 `5.0` 必须落到同一身份文本；bool 仍保持原样。"""
    assert normalize_numbers({"a": 1, "b": 0.05, "c": True}) == {
        "a": "1",
        "b": "0.05",
        "c": True,
    }
    assert normalize_numbers({"hac_lag": 5}) == normalize_numbers({"hac_lag": 5.0})


def test_normalized_config_stores_decimal_text():
    context = make_context()
    assert context.normalized()["method_config"]["normalized"] == {
        "fdr_alpha": "0.05",
        "hac_lag": "5",
    }


def test_normalize_utc_set_dedupes_and_sorts():
    assert normalize_utc_set(
        ["2026-04-01T00:00:00Z", "2026-01-01T00:00:00Z", "2026-04-01T00:00:00Z"], "x"
    ) == [
        "2026-01-01T00:00:00Z",
        "2026-04-01T00:00:00Z",
    ]


# ---------- 校验 ----------


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"schema_version": 99}, "schema_version"),
        ({"execution_tier": "shadow"}, "执行层级"),
        ({"cohort_id": "not-a-ref"}, "cohort_id"),
        ({"research_snapshot_id": "latest"}, "research_snapshot_id"),
        ({"code_build_digest": "sha256:short"}, "code_build_digest"),
        ({"seed": "7"}, "seed"),
        ({"supersedes": "nope"}, "supersedes"),
        ({"window": {"selection": [], "label_horizons": [1]}}, "selection"),
        (
            {"window": {"selection": ["2026-01-01T00:00:00Z"], "label_horizons": [0]}},
            "label_horizons",
        ),
    ],
)
def test_invalid_context_is_rejected(overrides: dict, message: str):
    with pytest.raises(SnapshotInputError, match=message):
        make_context(**overrides)


def test_from_dict_requires_all_fields():
    payload = make_context().to_dict()
    del payload["seed"]
    with pytest.raises(SnapshotInputError, match="缺少字段"):
        ExperimentContext.from_dict(payload)


# ---------- supersedes 谱系 ----------


def test_valid_supersedes_chain_is_accepted():
    first = make_context(seed=1)
    second = make_context(seed=2, supersedes=first.experiment_id)
    index = ExperimentIndex.from_contexts([first, second])
    validate_supersedes(second, index)
    assert index.lineage(second.experiment_id) == (first.experiment_id,)


def test_supersedes_without_target_is_accepted():
    validate_supersedes(make_context(), ExperimentIndex.from_contexts([]))


def test_self_referencing_supersedes_is_rejected():
    context = make_context()
    index = ExperimentIndex.from_contexts([context])
    self_ref = make_context(supersedes=context.experiment_id)
    with pytest.raises(SnapshotInputError, match="自身"):
        validate_supersedes(make_context(supersedes=self_ref.experiment_id), index)


def test_unknown_supersedes_target_is_rejected():
    context = make_context(supersedes=DIGEST_D)
    with pytest.raises(SnapshotInputError, match="不存在"):
        validate_supersedes(context, ExperimentIndex.from_contexts([]))


def test_supersedes_across_upstream_or_cohort_is_rejected():
    first = make_context(seed=1)
    index = ExperimentIndex.from_contexts([first])
    other_cohort = make_context(seed=2, cohort_id=COHORT_OTHER, supersedes=first.experiment_id)
    with pytest.raises(SnapshotInputError, match="同一 upstream/cohort"):
        validate_supersedes(other_cohort, index)
    other_upstream = make_context(
        seed=2,
        upstream={"kind": "factor", "id": "factor_sha256:" + "e" * 64},
        supersedes=first.experiment_id,
    )
    with pytest.raises(SnapshotInputError, match="同一 upstream/cohort"):
        validate_supersedes(other_upstream, index)


def test_supersedes_cycle_is_rejected():
    first = make_context(seed=1)
    second = make_context(seed=2, supersedes=first.experiment_id)
    index = ExperimentIndex.from_contexts([first, second])
    cyclic = ExperimentContext(**{**first.to_dict(), "supersedes": second.experiment_id})
    assert cyclic.experiment_id == first.experiment_id
    with pytest.raises(SnapshotInputError, match="环"):
        validate_supersedes(cyclic, index)


def test_broken_supersedes_chain_is_rejected():
    dangling = make_context(seed=1, supersedes=DIGEST_D)
    context = make_context(seed=2, supersedes=dangling.experiment_id)
    with pytest.raises(SnapshotInputError, match="断裂"):
        validate_supersedes(context, ExperimentIndex.from_contexts([dangling]))
