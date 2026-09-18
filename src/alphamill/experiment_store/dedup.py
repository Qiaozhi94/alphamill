"""`|ρ|` 查重判定（`FR-008`/`AC-013`；任务 T012）。

在 `finalize-cohort` **内部、导出 `promotion_verdict` 之前**执行。相关性口径按 PRD FR2.5：

- 取两个序列——**OOS PnL（成本后权益收益）**与 **rolling IC 序列**，均来自各成员的 `curves.parquet`；
- 取两个口径绝对相关的较大值为 `max_abs_rho`；
- `|ρ| > 0.99` → `dedup.verdict=rejected`；`0.90 ~ 0.99` → `variant`；否则 `none`。

比较集合 = 注册表评测面中 `dedup.verdict≠rejected` 的既有记录 ∪ **按承诺顺序排在候选之前**的同
cohort 成员。只把「在先者」计入比较集合，正是「cohort 内重复对按承诺顺序保留在先者、拒绝在后者，
不按结果择优」的实现。被拒者仍计入 cohort 试验总数与漏斗分母（`FR-004`）。
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

REJECT_ABOVE = 0.99
VARIANT_ABOVE = 0.90
MIN_POINTS = 2


class DedupError(ValueError):
    """序列过短、退化或取值非法。"""


def pearson(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise DedupError(f"序列长度不一致: {len(left)} vs {len(right)}")
    if len(left) < MIN_POINTS:
        raise DedupError(f"相关性至少需要 {MIN_POINTS} 个点")
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    cov = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right, strict=True))
    var_left = sum((a - mean_left) ** 2 for a in left)
    var_right = sum((b - mean_right) ** 2 for b in right)
    if var_left <= 0 or var_right <= 0:
        raise DedupError("序列为常数，相关性不可计算")
    return cov / math.sqrt(var_left * var_right)


def max_abs_rho(left: DedupCandidate, right: DedupCandidate) -> float:
    """两个成员在 OOS PnL 与 rolling IC 两个口径上的绝对相关最大值。"""
    scores = []
    for name, first, second in (
        ("oos_pnl", left.oos_pnl, right.oos_pnl),
        ("rolling_ic", left.rolling_ic, right.rolling_ic),
    ):
        if not first or not second:
            continue
        if len(first) != len(second):
            raise DedupError(f"{name} 序列长度不一致: {len(first)} vs {len(second)}")
        scores.append(abs(pearson(first, second)))
    if not scores:
        raise DedupError("两个口径都缺序列，查重不可判定")
    return max(scores)


@dataclass(frozen=True)
class DedupCandidate:
    """成员用于查重的两个序列；`evidence_ref` 供回写载荷定位曲线。"""

    factor_id: str
    oos_pnl: tuple[float, ...] = ()
    rolling_ic: tuple[float, ...] = ()
    evidence_ref: str | None = None

    @classmethod
    def from_curves(
        cls, factor_id: str, curves: Any, horizon: int, *, evidence_ref: str | None = None
    ) -> DedupCandidate:
        """从 `CurvesData` 取 OOS PnL（long/short 累计收益）与某 horizon 的 rolling IC。"""
        from alphamill.factor_factory.bench.curves import rolling_ic_column

        columns = curves.columns()
        return cls(
            factor_id=factor_id,
            oos_pnl=tuple(float(value) for value in curves.long_short),
            rolling_ic=tuple(float(value) for value in columns.get(rolling_ic_column(horizon), ())),
            evidence_ref=evidence_ref,
        )


@dataclass(frozen=True)
class DedupRecord:
    """注册表评测面的既有记录（只读）。"""

    factor_id: str
    verdict: str = "none"


@dataclass(frozen=True)
class DedupOutcome:
    max_abs_rho: float
    verdict: str
    against_factor_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "max_abs_rho": self.max_abs_rho,
            "verdict": self.verdict,
            "against_factor_id": self.against_factor_id,
        }


def decide_verdict(rho: float) -> str:
    if rho > REJECT_ABOVE:
        return "rejected"
    if rho >= VARIANT_ABOVE:
        return "variant"
    return "none"


def decide_dedup(
    candidate: DedupCandidate,
    *,
    earlier_members: Iterable[DedupCandidate] = (),
    registry_records: Iterable[DedupRecord] = (),
    registry_candidates: Mapping[str, DedupCandidate] | None = None,
) -> DedupOutcome:
    """对候选做两两查重并取最大相关；无比较对象时 `verdict=none`、`max_abs_rho=0`。"""
    comparators: list[DedupCandidate] = [member for member in earlier_members]
    known = registry_candidates or {}
    for record in registry_records:
        if record.verdict == "rejected":
            continue
        counterpart = known.get(record.factor_id)
        if counterpart is not None and counterpart.factor_id != candidate.factor_id:
            comparators.append(counterpart)
    best_rho = -1.0
    best_against: str | None = None
    for counterpart in comparators:
        rho = max_abs_rho(candidate, counterpart)
        if best_against is None or rho > best_rho:
            best_rho = rho
            best_against = counterpart.factor_id
    if best_against is None:
        return DedupOutcome(max_abs_rho=0.0, verdict="none", against_factor_id=None)
    return DedupOutcome(
        max_abs_rho=best_rho, verdict=decide_verdict(best_rho), against_factor_id=best_against
    )


def resolve_cohort_dedup(
    members_in_commitment_order: Sequence[DedupCandidate],
    *,
    registry_records: Iterable[DedupRecord] = (),
    registry_candidates: Mapping[str, DedupCandidate] | None = None,
) -> dict[str, DedupOutcome]:
    """按承诺顺序逐个裁决：在先者不被后来者影响，在后者对在先者查重（`FR-008` 场景 2）。"""
    outcomes: dict[str, DedupOutcome] = {}
    earlier: list[DedupCandidate] = []
    for member in members_in_commitment_order:
        outcome = decide_dedup(
            member,
            earlier_members=earlier,
            registry_records=registry_records,
            registry_candidates=registry_candidates,
        )
        outcomes[member.factor_id] = outcome
        earlier.append(member)
    return outcomes
