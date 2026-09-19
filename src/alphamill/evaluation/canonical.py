"""canonical 运行编排（`FR-001`/`IR-001`/`IR-002`/`TR-003`；任务 T013）。

canonical 与 preview 的差别是**门禁强度**，不是流程分支：

- 必须显式给出冻结 cohort、已发布 ResearchSnapshot、规则版本与 `--code-build-digest` 期望值；
  digest 由 runner 自行计算（不接受调用方自报），工作树脏或无法判定即拒绝（`IR-001`）；
- 入口先跑方法论门 L1 静态纯度 fail-closed（`FR-002`/`FR-007`）；canonical 恒为非近似
  （`NFR-004`），`source=placeholder` 一律拒绝（`DR-007`）；
- 产物发布到 `reports/bench/`，必须带 `registration.json`，随后写 `evaluation.registered`；
- **整个 canonical 事务以 `<experiment_id>.claim` 原子创建取得单写权**（`design.md` §5、
  `NFR-001`）；已有完整 canonical 直接幂等返回，在飞冲突拒绝（`E_COHORT_FROZEN`）；
- 同语义重跑**幂等返回既有实验**（同一 `experiment_id`，不重复计数）。

执行体见 `canonical_execute`；登记与复用恢复见 `canonical_registration`。
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from alphamill.evaluation import claim, publisher
from alphamill.evaluation.canonical_execute import execute_canonical
from alphamill.evaluation.canonical_registration import (
    CANONICAL_STATE_MANIFEST,
    ensure_member_registered,
    stage_results_from_manifest,
)
from alphamill.evaluation.canonical_result import CanonicalResult
from alphamill.evaluation.capabilities import context_for
from alphamill.evaluation.code_build import (
    assert_expected_code_build_digest,
    assert_worktree_clean_for_canonical,
)
from alphamill.evaluation.code_build import code_build_digest as compute_code_build_digest
from alphamill.evaluation.contract_common import (
    TIER_CANONICAL,
    UpstreamContractError,
    content_digest,
)
from alphamill.evaluation.run_config import load_run_config
from alphamill.evaluation.run_state import STATE_EVIDENCE_READY
from alphamill.experiment_store import population
from alphamill.experiment_store import research_snapshot as rs
from alphamill.experiment_store.experiment_context import (
    CONTEXT_SCHEMA_VERSION,
    ExperimentContext,
)

CLAIMS_SUBDIR = "_claims"


class CanonicalError(UpstreamContractError):
    """canonical 前置条件不满足或输入不可解析；`E_INPUT_INVALID`。"""

    code = "E_INPUT_INVALID"


def run_canonical(
    *,
    config_path: Path,
    factor_ref: str,
    candidate_id: str,
    cohort_id: str,
    seed: int,
    signals_path: Path,
    snapshot_id: str,
    expression: str,
    object_id: str | None = None,
    expected_code_build_digest: str | None = None,
    observed_at: str | None = None,
    require_clean_worktree: bool = True,
) -> CanonicalResult:
    config = load_run_config(config_path)
    if require_clean_worktree:
        assert_worktree_clean_for_canonical()
    code_digest = compute_code_build_digest()
    assert_expected_code_build_digest(expected_code_build_digest, code_digest)

    reports = rs.reports_root()
    definition = population.load_cohort(reports, cohort_id)
    if candidate_id not in population.commitment_ids(definition):
        raise CanonicalError(f"候选 {candidate_id} 不在 cohort {cohort_id} 的承诺内")
    snapshot = rs.load_snapshot(reports, snapshot_id)
    context = ExperimentContext(
        schema_version=CONTEXT_SCHEMA_VERSION,
        execution_tier=TIER_CANONICAL,
        upstream={"kind": "factor", "id": factor_ref},
        cohort_id=cohort_id,
        method_config=config.method_config,
        window=config.window,
        cost_model=config.cost_model,
        research_snapshot_id=snapshot.snapshot_id,
        code_build_digest=code_digest,
        seed=seed,
    )
    experiment_id = context.experiment_id
    tier_context = context_for(TIER_CANONICAL, reports)
    target = tier_context.bench_dir(object_id or factor_ref, snapshot.snapshot_id, experiment_id)
    if publisher.is_published(target, canonical=True):
        manifest = json.loads((target / CANONICAL_STATE_MANIFEST).read_text(encoding="utf-8"))
        recorded_digest = manifest.get("signal_digest")
        if recorded_digest and recorded_digest != content_digest(signals_path.read_bytes()):
            raise CanonicalError(
                "已发布结论与本次信号输入不一致（signal_digest 不符）；语义变化必须新建实验"
            )
        ensure_member_registered(
            reports=reports,
            cohort_id=cohort_id,
            candidate_id=candidate_id,
            experiment_id=experiment_id,
            target=target,
            config=config,
        )
        return CanonicalResult(
            experiment_id=experiment_id,
            cohort_id=cohort_id,
            candidate_id=candidate_id,
            snapshot_id=snapshot.snapshot_id,
            code_build_digest=code_digest,
            state=str(manifest.get("state", STATE_EVIDENCE_READY)),
            cost_verdict=str(manifest.get("cost_verdict", "cost_undetermined")),
            sample_tier=str(manifest.get("sample_tier", "underpowered")),
            stage_results=stage_results_from_manifest(manifest),
            approximation=manifest.get("approximation", {}),
            promotion_verdict=None,
            artifact_dir=str(target),
            reused=True,
        )

    claim_token = f"canonical-{os.getpid()}-{uuid.uuid4().hex}"
    claim.recover(reports / CLAIMS_SUBDIR, experiment_id, owner_token=claim_token)
    try:
        return execute_canonical(
            reports=reports,
            tier_context=tier_context,
            config=config,
            experiment_id=experiment_id,
            cohort_id=cohort_id,
            candidate_id=candidate_id,
            factor_ref=factor_ref,
            object_id=object_id,
            signals_path=signals_path,
            snapshot=snapshot,
            expression=expression,
            code_digest=code_digest,
            observed_at=observed_at,
        )
    finally:
        claim.release(reports / CLAIMS_SUBDIR, experiment_id, owner_token=claim_token)
