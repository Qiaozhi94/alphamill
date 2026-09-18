"""purged/embargoed rolling split 与稳定性报告（`FR-005`/`AC-004`；任务 T010）。

切分纪律（`design.md` §5、ADR-0006「证据边界不变量」）：

- 切分以 outcome/label endpoint 为边界，**不是**信号起点：`label_horizon` 期内的训练观测被 purge，
  因为它们的标签落进了测试折；
- embargo 是额外的序列相关缓冲，覆盖测试折开始前 `embargo` 期（`embargo ≥ max label horizon`
  由 T008 的守卫另行断言）；
- 训练折只包含测试折**之前**的观测（rolling/expanding），有效训练集 = 训练区间 − purge − embargo。

稳定性报告逐折给出 IC、有效训练/测试规模与一致性；折内退化（常数信号或样本不足）记
`INCOMPLETE` + `estimator_failure`（fail-closed），方向不一致记 `FAIL`（已评出、结论为负）。
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
DEFAULT_N_FOLDS = 3
DEFAULT_LABEL_HORIZON = 1
DEFAULT_EMBARGO = 1
MIN_FOLD_OBSERVATIONS = 2


@dataclass(frozen=True)
class Fold:
    index: int
    test_start: int
    test_end: int
    train_indices: tuple[int, ...]
    purged: tuple[int, ...]
    embargoed: tuple[int, ...]

    @property
    def train_size(self) -> int:
        return len(self.train_indices)

    @property
    def test_size(self) -> int:
        return self.test_end - self.test_start

    def to_payload(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "train_indices": list(self.train_indices),
            "test_start": self.test_start,
            "test_end": self.test_end,
            "purged": list(self.purged),
            "embargoed": list(self.embargoed),
        }


def split_segments(size: int, segments: int) -> tuple[tuple[int, int], ...]:
    if segments < 2:
        raise StageModelError(f"切分至少需要 2 段: {segments!r}")
    if size < segments * MIN_FOLD_OBSERVATIONS:
        raise StageModelError(
            f"样本量 {size} 不足以切成 {segments} 段（每段至少 {MIN_FOLD_OBSERVATIONS} 个观测）"
        )
    base, remainder = divmod(size, segments)
    bounds = []
    start = 0
    for index in range(segments):
        width = base + (1 if index < remainder else 0)
        bounds.append((start, start + width))
        start += width
    return tuple(bounds)


def make_purged_rolling_folds(
    size: int,
    *,
    n_folds: int = DEFAULT_N_FOLDS,
    label_horizon: int = DEFAULT_LABEL_HORIZON,
    embargo: int = DEFAULT_EMBARGO,
) -> tuple[Fold, ...]:
    """`n_folds` 个 rolling 折：第 k 折测试第 k 段，训练集为更早各段减去 purge 与 embargo。"""
    if label_horizon < 0 or embargo < 0:
        raise StageModelError(f"label_horizon/embargo 不得为负: {label_horizon}/{embargo}")
    segments = split_segments(size, n_folds + 1)
    folds = []
    for index in range(1, n_folds + 1):
        test_start, test_end = segments[index]
        purged = tuple(
            position for position in range(test_start) if position + label_horizon >= test_start
        )
        embargoed = tuple(position for position in range(max(0, test_start - embargo), test_start))
        removed = set(purged) | set(embargoed)
        folds.append(
            Fold(
                index=index,
                test_start=test_start,
                test_end=test_end,
                train_indices=tuple(
                    position for position in range(test_start) if position not in removed
                ),
                purged=purged,
                embargoed=embargoed,
            )
        )
    return tuple(folds)


@dataclass(frozen=True)
class StabilityReport:
    pooled_ic: float | None
    fold_ics: tuple[float, ...]
    fold_train_sizes: tuple[int, ...]
    fold_test_sizes: tuple[int, ...]
    n_folds: int
    label_horizon: int
    embargo: int

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
            "fold_train_sizes": list(self.fold_train_sizes),
            "fold_test_sizes": list(self.fold_test_sizes),
            "n_folds": self.n_folds,
            "label_horizon": self.label_horizon,
            "embargo": self.embargo,
            "consistent": self.consistent,
        }


def evaluate_temporal_stability(
    signal: Sequence[float],
    label: Sequence[float],
    *,
    observed_at: str,
    n_folds: int = DEFAULT_N_FOLDS,
    label_horizon: int = DEFAULT_LABEL_HORIZON,
    embargo: int = DEFAULT_EMBARGO,
) -> tuple[StabilityReport, StageResult]:
    values = list(signal)
    labels = list(label)
    if len(values) != len(labels):
        raise StageModelError(f"信号与标签长度不一致: {len(values)} vs {len(labels)}")
    empty = StabilityReport(None, (), (), (), n_folds, label_horizon, embargo)
    try:
        folds = make_purged_rolling_folds(
            len(values), n_folds=n_folds, label_horizon=label_horizon, embargo=embargo
        )
        if any(fold.train_size < MIN_FOLD_OBSERVATIONS for fold in folds):
            raise StageModelError(f"存在有效训练集不足 {MIN_FOLD_OBSERVATIONS} 的折")
        pooled = rank_ic(values, labels)
        fold_ics = tuple(
            rank_ic(
                [values[position] for position in fold.train_indices],
                [labels[position] for position in fold.train_indices],
            )
            for fold in folds
        )
    except StageModelError as exc:
        failure = FailureRecord(
            stage=STAGE_TEMPORAL_STABILITY,
            owner="statistics",
            mechanism="estimator_failure",
            error_code=ERROR_CODE,
            first_seen=observed_at,
        )
        return empty, StageResult(
            stage_id=STAGE_TEMPORAL_STABILITY,
            status=STATUS_INCOMPLETE,
            reason=f"稳定性估计器不可用: {exc}",
            failures=(failure,),
        )
    report = StabilityReport(
        pooled_ic=pooled,
        fold_ics=fold_ics,
        fold_train_sizes=tuple(fold.train_size for fold in folds),
        fold_test_sizes=tuple(fold.test_size for fold in folds),
        n_folds=n_folds,
        label_horizon=label_horizon,
        embargo=embargo,
    )
    status = STATUS_PASS if report.consistent else STATUS_FAIL
    return report, StageResult(stage_id=STAGE_TEMPORAL_STABILITY, status=status)
