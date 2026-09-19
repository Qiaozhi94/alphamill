"""T003·T005 / `AC-001`·`AC-010`：执行层级边界与越权拒绝的集成夹具。

覆盖：preview 上下文对 canonical writer / 留出 reader / 最终确认窗 reader / 留出预算台账 writer
四项能力的**零持有**与逐项越权拒绝（稳定错误码 `E_CANONICAL_FORBIDDEN`）；canonical 上下文的
产物根与能力齐备；环境变量**不能**提权；preview 与 canonical 的物理命名空间互不重叠；
留出预算台账在 v0.2 保持零行（`DR-005`：不存在旁路写入者）。

本文件同时是 T019/T029 的载体：后续任务在此追加台账零行、越权写台账后 `evaluation.gate_rejected`
事件等断言。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alphamill.evaluation.capabilities import (
    CANONICAL_ONLY_CAPABILITIES,
    CAP_CANONICAL_WRITER,
    CAP_FINAL_WINDOW_READER,
    CAP_HOLDOUT_BUDGET_WRITER,
    CAP_HOLDOUT_READER,
    CapabilityError,
    TierRoots,
    assert_no_canonical_leak,
    canonical_capabilities,
    context_for,
    preview_capabilities,
)
from alphamill.evaluation.contract_common import (
    TIER_CANONICAL,
    TIER_PREVIEW,
    UpstreamContractError,
)

pytestmark = pytest.mark.integration

EXPERIMENT = "sha256:" + "e" * 64
SNAPSHOT = "sha256:" + "s" * 64
OBJECT = "factor_sha256:" + "o" * 64


def test_preview_context_holds_no_canonical_capability():
    context = context_for(TIER_PREVIEW, Path("/tmp/reports"))
    assert context.capabilities.granted_sorted() == ()
    assert not any(context.capabilities.has(cap) for cap in CANONICAL_ONLY_CAPABILITIES)


@pytest.mark.parametrize(
    "capability",
    [CAP_CANONICAL_WRITER, CAP_HOLDOUT_READER, CAP_FINAL_WINDOW_READER, CAP_HOLDOUT_BUDGET_WRITER],
)
def test_preview_require_raises_for_every_canonical_capability(capability: str):
    with pytest.raises(CapabilityError) as excinfo:
        context_for(TIER_PREVIEW, Path("/tmp/reports")).require(capability)
    assert excinfo.value.code == "E_CANONICAL_FORBIDDEN"


def test_preview_cannot_reach_canonical_artifact_root(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    with pytest.raises(CapabilityError, match="canonical_writer"):
        context.bench_dir(OBJECT, SNAPSHOT, EXPERIMENT)


def test_preview_cannot_obtain_holdout_budget_ledger_handle(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    with pytest.raises(CapabilityError, match="holdout_budget_writer"):
        context.holdout_ledger_path()


def test_preview_cannot_read_final_confirmation_window(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    with pytest.raises(CapabilityError, match="final_window_reader"):
        context.require_final_window_reader()


def test_preview_cannot_read_holdout(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    with pytest.raises(CapabilityError, match="holdout_reader"):
        context.require_holdout_reader()


def test_canonical_context_grants_all_four_capabilities(tmp_path):
    context = context_for(TIER_CANONICAL, tmp_path)
    assert context.capabilities.granted_sorted() == tuple(sorted(CANONICAL_ONLY_CAPABILITIES))
    assert context.is_canonical


def test_canonical_artifact_root_follows_design_layout(tmp_path):
    context = context_for(TIER_CANONICAL, tmp_path)
    assert context.bench_dir(OBJECT, SNAPSHOT, EXPERIMENT) == (
        tmp_path / "bench" / OBJECT / SNAPSHOT / EXPERIMENT
    )


def test_canonical_holds_holdout_ledger_handle(tmp_path):
    context = context_for(TIER_CANONICAL, tmp_path)
    assert context.holdout_ledger_path() == tmp_path / "holdout_budget" / "ledger.jsonl"


def test_preview_artifact_root_is_isolated_from_bench(tmp_path):
    preview = context_for(TIER_PREVIEW, tmp_path)
    assert preview.preview_attempt_dir(EXPERIMENT, "attempt-1") == (
        tmp_path / "preview" / EXPERIMENT / "attempt-1"
    )
    assert not str(preview.preview_attempt_dir(EXPERIMENT, "attempt-1")).startswith(
        str(tmp_path / "bench")
    )


def test_canonical_context_cannot_write_preview_namespace(tmp_path):
    with pytest.raises(CapabilityError, match="preview 命名空间"):
        context_for(TIER_CANONICAL, tmp_path).preview_attempt_dir(EXPERIMENT, "attempt-1")


def test_environment_variable_cannot_escalate_tier(tmp_path, monkeypatch):
    monkeypatch.setenv("ALPHAMILL_EXECUTION_TIER", TIER_CANONICAL)
    monkeypatch.setenv("ALPHAMILL_TIER", TIER_CANONICAL)
    context = context_for(TIER_PREVIEW, tmp_path)
    assert context.execution_tier == TIER_PREVIEW
    assert context.capabilities.granted_sorted() == ()


def test_unknown_execution_tier_is_rejected(tmp_path):
    with pytest.raises(UpstreamContractError, match="未知执行层级"):
        context_for("shadow", tmp_path)


def test_preview_and_canonical_capability_sets_are_disjoint():
    assert preview_capabilities().granted_sorted() == ()
    assert set(canonical_capabilities().granted) == set(CANONICAL_ONLY_CAPABILITIES)


def test_holdout_budget_ledger_is_empty_in_v0_2(tmp_path):
    """v0.2 无追加写入者：台账零行是锁定「不存在旁路写入者」的预期不变量（`DR-005`）。"""
    roots = TierRoots(reports=tmp_path)
    context = context_for(TIER_CANONICAL, tmp_path)
    assert context.holdout_ledger_path() == roots.holdout_ledger_path
    assert not roots.holdout_ledger_path.exists()


def test_agent_readable_payload_rejects_final_window_fields():
    with pytest.raises(CapabilityError, match="最终确认窗"):
        assert_no_canonical_leak({"final_window_ic": 0.9}, agent_readable=True)
    with pytest.raises(CapabilityError, match="最终确认窗"):
        assert_no_canonical_leak({"holdout_budget_rows": 3}, agent_readable=True)


def test_agent_readable_payload_rejects_nested_final_window_fields():
    """R1-106 回归：泄漏守卫必须递归扫描嵌套键，不能被顶层两键字典骗过。"""
    with pytest.raises(CapabilityError, match="最终确认窗"):
        assert_no_canonical_leak({"outer": [{"holdout_budget_rows": 3}]}, agent_readable=True)
    with pytest.raises(CapabilityError, match="最终确认窗"):
        assert_no_canonical_leak({"stages": {"final_window_ic": 0.9}}, agent_readable=True)


def test_agent_readable_payload_allows_ordinary_fields():
    assert_no_canonical_leak(
        {"experiment_id": EXPERIMENT, "stage": "signal_quality"}, agent_readable=True
    )
    assert_no_canonical_leak({"final_window_ic": 0.9}, agent_readable=False)
