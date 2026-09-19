"""`promotion_verdict` 导出优先级表（`design.md` §3.3 冻结；`FR-005`/`FR-008`；任务 T012）。

该表是 `promotion_verdict` 的**唯一**取值来源：输出值集合与枚举行完全相等，条件覆盖全部 run
终态（`EVIDENCE_READY`/`REJECTED`/`INCOMPLETE`）与全部 `dedup.verdict` 取值（`variant` 与 `none`
不改变取值）。成员级结论按优先级取**首个命中**：

| 优先级 | 条件 | 取值 |
|---|---|---|
| 1 | 终态 `REJECTED` 或 `dedup.verdict=rejected` | `rejected` |
| 2 | 必需阶段/估计器失败或证据不完整（含 INCOMPLETE 终态） | `incomplete` |
| 3 | `sample_tier=underpowered` 或必需阶段 `UNDERPOWERED` | `underpowered` |
| 4 | `cost_verdict=cost_negative` 或统计判死 | `dead` |
| 5 | 证据达标但 `no_lookahead` 存在非 `PASS` 层 | `blocked_pending_audit` |
| 6 | `sample_tier=provisional` | `provisional` |
| 7 | 其余 | `promising` |

优先级 2 只覆盖「证据没能产出」类失败：`INCOMPLETE` 阶段，或失败机制属于缺输入/无效输入/能力未
守卫/估计器失败/发布失败。`cost_negative` 与 `underpowered` 是**已评出的结论**，分别走优先级 4 与
3——若把「任何 FAIL」都当成优先级 2，`FR-005` 的「成本不存活 → `dead`」会被提前吞成 `incomplete`。
"""

from __future__ import annotations

from dataclasses import dataclass

from alphamill.evaluation.run_state import STATE_REJECTED
from alphamill.factor_factory.bench.stage_model import (
    COST_NEGATIVE,
    PROMOTION_VERDICTS,
    TIER_PROVISIONAL,
    TIER_UNDERPOWERED,
    StageResults,
)
from alphamill.validation.no_lookahead import NoLookahead

VERDICT_REJECTED = "rejected"
VERDICT_INCOMPLETE = "incomplete"
VERDICT_UNDERPOWERED = TIER_UNDERPOWERED
VERDICT_DEAD = "dead"
VERDICT_BLOCKED = "blocked_pending_audit"
VERDICT_PROVISIONAL = TIER_PROVISIONAL
VERDICT_PROMISING = "promising"

DEDUP_REJECTED = "rejected"
DEDUP_VARIANT = "variant"
DEDUP_NONE = "none"
DEDUP_VERDICTS = (DEDUP_NONE, DEDUP_VARIANT, DEDUP_REJECTED)
EVIDENCE_FAILURE_MECHANISMS = (
    "missing_input",
    "invalid_input",
    "capability_unguarded",
    "estimator_failure",
    "publish_failure",
)


class PromotionError(ValueError):
    """未知终态、未知 dedup 取值或未知样本量档位。"""


@dataclass(frozen=True)
class PromotionInputs:
    run_state: str
    stage_results: StageResults
    sample_tier: str
    cost_verdict: str
    no_lookahead: NoLookahead
    dedup_verdict: str = DEDUP_NONE
    statistically_dead: bool = False

    def __post_init__(self) -> None:
        if self.dedup_verdict not in DEDUP_VERDICTS:
            raise PromotionError(f"未登记的 dedup 取值: {self.dedup_verdict!r}")
        if self.sample_tier not in (TIER_UNDERPOWERED, TIER_PROVISIONAL, "trustworthy"):
            raise PromotionError(f"未登记的样本量档位: {self.sample_tier!r}")


def derive_promotion_verdict(inputs: PromotionInputs) -> str:
    """按冻结优先级表导出成员级 `promotion_verdict`（首个命中即返回）。"""
    if inputs.run_state == STATE_REJECTED or inputs.dedup_verdict == DEDUP_REJECTED:
        return VERDICT_REJECTED
    stages = inputs.stage_results
    evidence_failure = any(
        failure.mechanism in EVIDENCE_FAILURE_MECHANISMS for failure in stages.failures()
    )
    if stages.incomplete_stages or evidence_failure:
        return VERDICT_INCOMPLETE
    if inputs.sample_tier == TIER_UNDERPOWERED or stages.underpowered_stages:
        return VERDICT_UNDERPOWERED
    if inputs.cost_verdict == COST_NEGATIVE or inputs.statistically_dead:
        return VERDICT_DEAD
    if inputs.no_lookahead.blocks_promotion:
        return VERDICT_BLOCKED
    if inputs.sample_tier == TIER_PROVISIONAL:
        return VERDICT_PROVISIONAL
    return VERDICT_PROMISING


def assert_verdict_is_frozen(verdict: str) -> str:
    if verdict not in PROMOTION_VERDICTS:
        raise PromotionError(f"promotion_verdict 不在冻结枚举内: {verdict!r}")
    return verdict
