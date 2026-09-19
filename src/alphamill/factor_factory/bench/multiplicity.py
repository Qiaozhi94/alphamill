"""多重检验与按有效独立数校正的显著性（`FR-004`；任务 T009）。

自研最小协议：cohort 级 Benjamini-Hochberg FDR、由相关性导出的**有效独立试验数**、按有效独立数
校正的 Deflated Sharpe Ratio（DSR）与最小 track-record length（MinTRL）。

口径与冻结来源：`method-v1.json` 的 `multiplicity` 段（`fdr_method=benjamini_hochberg`、
`fdr_alpha`、`effective_independent=deflated_sharpe_ratio`、`min_track_record_years`）。阈值由
预注册配置持有，不硬编码（`FR-004`）。

失败语义：估计器异常一律抛 `StatisticsError`，由 `statistics_stage` 映射为 `INCOMPLETE` +
`estimator_failure`——stage 不得为 `PASS`（`AC-003` 场景「必需估计器异常」）。
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, TypeVar

from alphamill.factor_factory.bench.stage_model import (
    STATUS_INCOMPLETE,
    STATUS_PASS,
    FailureRecord,
    StageResult,
)
from alphamill.factor_factory.bench.statistics import (
    StatisticsError,
    mean,
    normal_cdf,
    normal_ppf,
)

ERROR_CODE = "E_REQUIRED_METRIC_FAILED"
EULER_MASCHERONI = 0.5772156649015329
T = TypeVar("T")


def benjamini_hochberg(p_values: Sequence[float], *, alpha: float) -> BHResult:
    """BH step-up：返回 q 值、逐项是否拒绝与临界名次（无拒绝时为 0）。"""
    if not p_values:
        raise StatisticsError("BH-FDR 需要至少一个 p 值")
    if not 0.0 < alpha < 1.0:
        raise StatisticsError(f"alpha 必须在 (0,1) 内: {alpha!r}")
    for value in p_values:
        if not 0.0 <= value <= 1.0:
            raise StatisticsError(f"p 值必须落在 [0,1]: {value!r}")
    size = len(p_values)
    order = sorted(range(size), key=lambda index: p_values[index])
    q_values = [1.0] * size
    running = 1.0
    for rank in range(size, 0, -1):
        index = order[rank - 1]
        candidate = p_values[index] * size / rank
        running = min(running, candidate)
        q_values[index] = min(1.0, running)
    critical_rank = 0
    for rank in range(1, size + 1):
        if p_values[order[rank - 1]] <= rank / size * alpha:
            critical_rank = rank
    rejected = [False] * size
    for rank in range(1, critical_rank + 1):
        rejected[order[rank - 1]] = True
    return BHResult(
        q_values=tuple(q_values),
        rejected=tuple(rejected),
        critical_rank=critical_rank,
        alpha=alpha,
    )


@dataclass(frozen=True)
class BHResult:
    q_values: tuple[float, ...]
    rejected: tuple[bool, ...]
    critical_rank: int
    alpha: float

    @property
    def rejected_count(self) -> int:
        return sum(1 for flag in self.rejected if flag)

    def to_payload(self) -> dict[str, Any]:
        return {
            "q_values": list(self.q_values),
            "rejected": list(self.rejected),
            "critical_rank": self.critical_rank,
            "rejected_count": self.rejected_count,
            "alpha": self.alpha,
        }


def effective_trials(correlations: Sequence[float]) -> float:
    """由平均相关性导出的有效独立试验数 `N / (1 + (N-1)·ρ̄)`，ρ̄ 取绝对相关均值。"""
    if not correlations:
        raise StatisticsError("有效独立数需要至少一个相关系数")
    for value in correlations:
        if not -1.0 <= value <= 1.0:
            raise StatisticsError(f"相关系数必须落在 [-1,1]: {value!r}")
    rho = mean([abs(value) for value in correlations])
    count = len(correlations) + 1
    denominator = 1.0 + (count - 1) * rho
    if denominator <= 0:
        raise StatisticsError("有效独立数分母非正")
    return count / denominator


def expected_max_sharpe(n_trials: int) -> float:
    """iid 正态下 M 次试验最大 Sharpe 的期望（以 SR 标准差为单位）。"""
    if not isinstance(n_trials, int) or isinstance(n_trials, bool) or n_trials < 1:
        raise StatisticsError(f"试验数必须为正整数: {n_trials!r}")
    if n_trials == 1:
        return 0.0
    first = normal_ppf(1.0 - 1.0 / n_trials)
    second = normal_ppf(1.0 - 1.0 / (n_trials * math.e))
    return (1.0 - EULER_MASCHERONI) * first + EULER_MASCHERONI * second


def deflated_sharpe_ratio(
    sharpe: float,
    *,
    n_trials: int,
    sharpe_std: float,
    n_observations: int,
    skew: float = 0.0,
    kurtosis: float = 3.0,
) -> float:
    """DSR = Φ(z)；`kurtosis` 用非超额峰度（正态=3），`sharpe` 与 `sharpe_std` 为同频率口径。"""
    if n_observations < 2:
        raise StatisticsError(f"DSR 至少需要 2 个观测: {n_observations!r}")
    if sharpe_std < 0:
        raise StatisticsError(f"SR 标准差不得为负: {sharpe_std!r}")
    if kurtosis < 1.0:
        raise StatisticsError(f"峰度必须 >= 1（非超额峰度）: {kurtosis!r}")
    threshold = sharpe_std * expected_max_sharpe(n_trials)
    variance_term = 1.0 - skew * sharpe + (kurtosis - 1.0) / 4.0 * sharpe * sharpe
    if variance_term <= 0:
        raise StatisticsError("DSR 方差项非正，样本退化")
    z_score = (sharpe - threshold) * math.sqrt(n_observations - 1) / math.sqrt(variance_term)
    return normal_cdf(z_score)


def min_track_record_length(
    sharpe: float,
    *,
    target_sharpe: float,
    skew: float = 0.0,
    kurtosis: float = 3.0,
    alpha: float = 0.05,
) -> float:
    """达到 `target_sharpe` 显著性所需的最小观测数；`sharpe <= target_sharpe` 时无有限解。"""
    if not 0.0 < alpha < 1.0:
        raise StatisticsError(f"alpha 必须在 (0,1) 内: {alpha!r}")
    if kurtosis < 1.0:
        raise StatisticsError(f"峰度必须 >= 1（非超额峰度）: {kurtosis!r}")
    edge = sharpe - target_sharpe
    if edge <= 0:
        raise StatisticsError("SR 未超过目标 SR，MinTRL 无有限解")
    variance_term = 1.0 - skew * sharpe + (kurtosis - 1.0) / 4.0 * sharpe * sharpe
    if variance_term <= 0:
        raise StatisticsError("MinTRL 方差项非正，样本退化")
    z_alpha = normal_ppf(1.0 - alpha)
    return 1.0 + variance_term * (z_alpha / edge) ** 2


def statistics_stage(
    stage_id: str,
    compute: Callable[[], T],
    *,
    observed_at: str,
) -> tuple[T | None, StageResult]:
    """把估计器异常收敛为 `INCOMPLETE` + `estimator_failure`（`AC-003` 的失败关闭口径）。"""
    try:
        return compute(), StageResult(stage_id=stage_id, status=STATUS_PASS)
    except StatisticsError as exc:
        failure = FailureRecord(
            stage=stage_id,
            owner="statistics",
            mechanism="estimator_failure",
            error_code=ERROR_CODE,
            first_seen=observed_at,
        )
        return None, StageResult(
            stage_id=stage_id,
            status=STATUS_INCOMPLETE,
            reason=f"必需统计估计器异常: {exc}",
            failures=(failure,),
        )
