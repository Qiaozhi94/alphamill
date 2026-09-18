"""最小时序稳定性（`FR-005`；任务 T006，T010 扩展为 purged/embargoed rolling split）。

v0.2 preview 的最小切片：按时间顺序切成 `min_folds` 个连续折，逐折计算 Rank IC，要求各折
IC 与全样本 IC **同号**——即「选择期得出的方向在后续折仍然成立」。折内样本不足或退化时记
`INCOMPLETE`（估计器不可用，fail-closed），方向不一致记 `FAIL`（已评出、结论为负）。

T010 在此基础上补齐 purged/embargoed rolling split、三级样本量裁决与完整稳定性报告。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from alphamill.factor_factory.bench.signal_quality import rank_ic
from alphamill.factor_factory.bench.stage_model import (
    STAGE_TEMPORAL_STABILITY,
    STATUS_FAIL,
    STATUS_INCOMPLETE,
    STATUS_PASS,
    FailureRecord,
    StageModelError,
    StageResult,
)

ERROR_CODE = "E_REQUIRED_METRIC_FAILED"
DEFAULT_MIN_FOLDS = 2
MIN_FOLD_OBSERVATIONS = 2


@dataclass(frozen=True)
class StabilityResult:
    pooled_ic: float | None
    fold_ics: tuple[float, ...]

    @property
    def consistent(self) -> bool:
        if self.pooled_ic is None or not self.fold_ics:
            return False
        sign = 1.0 if self.pooled_ic > 0 else -1.0
        return all(ic * sign > 0 for ic in self.fold_ics)

    def to_payload(self) -> dict[str, Any]:
        return {
            "pooled_ic": self.pooled_ic,
            "fold_ics": list(self.fold_ics),
            "consistent": self.consistent,
        }


def split_folds(size: int, folds: int) -> tuple[tuple[int, int], ...]:
    if folds < 2:
        raise StageModelError(f"稳定性至少需要 2 折: {folds!r}")
    if size < folds * MIN_FOLD_OBSERVATIONS:
        raise StageModelError(
            f"样本量 {size} 不足以切成 {folds} 折（每折至少 {MIN_FOLD_OBSERVATIONS} 个观测）"
        )
    base, remainder = divmod(size, folds)
    bounds = []
    start = 0
    for index in range(folds):
        width = base + (1 if index < remainder else 0)
        bounds.append((start, start + width))
        start += width
    return tuple(bounds)


def evaluate_temporal_stability(
    signal: Sequence[float],
    label: Sequence[float],
    *,
    observed_at: str,
    min_folds: int = DEFAULT_MIN_FOLDS,
) -> tuple[StabilityResult, StageResult]:
    values = list(signal)
    labels = list(label)
    if len(values) != len(labels):
        raise StageModelError(f"信号与标签长度不一致: {len(values)} vs {len(labels)}")
    try:
        bounds = split_folds(len(values), min_folds)
        pooled = rank_ic(values, labels)
        fold_ics = tuple(rank_ic(values[a:b], labels[a:b]) for a, b in bounds)
    except StageModelError as exc:
        failure = FailureRecord(
            stage=STAGE_TEMPORAL_STABILITY,
            owner="statistics",
            mechanism="estimator_failure",
            error_code=ERROR_CODE,
            first_seen=observed_at,
        )
        return (
            StabilityResult(None, ()),
            StageResult(
                stage_id=STAGE_TEMPORAL_STABILITY,
                status=STATUS_INCOMPLETE,
                reason=f"稳定性估计器不可用: {exc}",
                failures=(failure,),
            ),
        )
    result = StabilityResult(pooled_ic=pooled, fold_ics=fold_ics)
    status = STATUS_PASS if result.consistent else STATUS_FAIL
    return result, StageResult(stage_id=STAGE_TEMPORAL_STABILITY, status=status)
