"""成员级必需统计：HAC 稳健 IC 与 block bootstrap 置信区间（`FR-004`；任务 T009）。

自研最小协议（不依赖 ml4t 配套包，ADR-0003）：逐期 Rank IC 序列 → 均值 IC 的 Newey-West(Bartlett)
稳健标准误 → block bootstrap 置信区间。所有估计器**失败即抛错**，绝不 `except → warning/null`：
异常由调用方映射为 `INCOMPLETE` + `estimator_failure`，不得伪装成 PASS（`design.md` §7）。

周期 IC 序列的输入是「按时间排序的每期 (signal 向量, label 向量)」；纯 Python 实现（只用标准库），
避免引入未声明依赖，也保证同一 seed 的 bootstrap 可复算（`NFR-002`）。
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

MIN_PERIODS = 2
MIN_OBSERVATIONS = 30
DEFAULT_HAC_LAG = 5
DEFAULT_BLOCK_SIZE = 5
DEFAULT_RESAMPLES = 1000
DEFAULT_SEED = 7
SQRT_TWO = math.sqrt(2.0)


class StatisticsError(ValueError):
    """必需统计不可计算；调用方必须映射为 `INCOMPLETE`/`estimator_failure`（失败关闭）。"""


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / SQRT_TWO))


def normal_ppf(probability: float) -> float:
    """标准正态分位数（Acklam 有理逼近，绝对误差 < 1.2e-9）。"""
    if not 0.0 < probability < 1.0:
        raise StatisticsError(f"分位数概率必须在 (0,1) 内: {probability!r}")
    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00, 3.754408661907416e00)
    low, high = 0.02425, 1 - 0.02425
    if probability < low:
        q = math.sqrt(-2 * math.log(probability))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    if probability > high:
        q = math.sqrt(-2 * math.log(1 - probability))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    q = probability - 0.5
    r = q * q
    return (
        (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5])
        * q
        / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    )


def _spearman(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise StatisticsError(f"维度不一致: {len(left)} vs {len(right)}")
    if len(left) < MIN_PERIODS:
        raise StatisticsError(f"每期至少 {MIN_PERIODS} 个观测，收到 {len(left)}")
    ranks_left = _ranks(left)
    ranks_right = _ranks(right)
    mean_left = sum(ranks_left) / len(ranks_left)
    mean_right = sum(ranks_right) / len(ranks_right)
    cov = sum(
        (a - mean_left) * (b - mean_right) for a, b in zip(ranks_left, ranks_right, strict=True)
    )
    var_left = sum((a - mean_left) ** 2 for a in ranks_left)
    var_right = sum((b - mean_right) ** 2 for b in ranks_right)
    if var_left <= 0 or var_right <= 0:
        raise StatisticsError("秩为常数，IC 不可计算")
    return cov / math.sqrt(var_left * var_right)


def _ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(order):
        end = position
        while end + 1 < len(order) and values[order[end + 1]] == values[order[position]]:
            end += 1
        average = (position + end) / 2.0 + 1.0
        for index in range(position, end + 1):
            ranks[order[index]] = average
        position = end + 1
    return ranks


def period_ic_series(
    periods: Sequence[tuple[Sequence[float], Sequence[float]]],
) -> tuple[float, ...]:
    """逐期 Rank IC 序列；任一期退化即抛错（不跳过、不补零）。"""
    if len(periods) < MIN_PERIODS:
        raise StatisticsError(f"至少需要 {MIN_PERIODS} 期，收到 {len(periods)}")
    return tuple(_spearman(signal, label) for signal, label in periods)


def mean(series: Sequence[float]) -> float:
    if not series:
        raise StatisticsError("空序列没有均值")
    return sum(series) / len(series)


def hac_se(series: Sequence[float], *, lag: int = DEFAULT_HAC_LAG) -> float:
    """Newey-West(Bartlett) 稳健标准误；`lag` 超过序列长度时自动收紧。"""
    if len(series) < MIN_PERIODS:
        raise StatisticsError(f"HAC 至少需要 {MIN_PERIODS} 期")
    if lag < 0:
        raise StatisticsError(f"HAC lag 不得为负: {lag!r}")
    effective_lag = min(lag, len(series) - 1)
    center = mean(series)
    deviations = [value - center for value in series]
    size = len(series)
    gamma0 = sum(value * value for value in deviations) / size
    total = gamma0
    for offset in range(1, effective_lag + 1):
        weight = 1.0 - offset / (effective_lag + 1.0)
        gamma = (
            sum(deviations[index] * deviations[index - offset] for index in range(offset, size))
            / size
        )
        total += 2.0 * weight * gamma
    if total <= 0:
        raise StatisticsError("HAC 方差非正，样本退化")
    return math.sqrt(total / size)


@dataclass(frozen=True)
class ICFit:
    ic: float
    hac_se: float
    t_stat: float
    n_periods: int
    hac_lag: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "ic": self.ic,
            "hac_se": self.hac_se,
            "t_stat": self.t_stat,
            "n_periods": self.n_periods,
            "hac_lag": self.hac_lag,
        }


def fit_ic(series: Sequence[float], *, hac_lag: int = DEFAULT_HAC_LAG) -> ICFit:
    point = mean(series)
    se = hac_se(series, lag=hac_lag)
    return ICFit(ic=point, hac_se=se, t_stat=point / se, n_periods=len(series), hac_lag=hac_lag)


@dataclass(frozen=True)
class BootstrapCI:
    point: float
    lower: float
    upper: float
    n_resamples: int
    block_size: int
    seed: int
    alpha: float

    @property
    def excludes_zero(self) -> bool:
        return self.lower > 0.0 or self.upper < 0.0

    def to_payload(self) -> dict[str, Any]:
        return {
            "point": self.point,
            "lower": self.lower,
            "upper": self.upper,
            "n_resamples": self.n_resamples,
            "block_size": self.block_size,
            "seed": self.seed,
            "alpha": self.alpha,
            "excludes_zero": self.excludes_zero,
        }


def block_bootstrap_ci(
    series: Sequence[float],
    *,
    block_size: int = DEFAULT_BLOCK_SIZE,
    n_resamples: int = DEFAULT_RESAMPLES,
    seed: int = DEFAULT_SEED,
    alpha: float = 0.05,
) -> BootstrapCI:
    """固定 seed 的移动块 bootstrap；同 seed 必须逐位复算一致（`NFR-002`）。"""
    size = len(series)
    if size < MIN_PERIODS:
        raise StatisticsError(f"bootstrap 至少需要 {MIN_PERIODS} 期")
    if block_size < 1 or block_size >= size:
        raise StatisticsError(
            f"block_size 必须落在 [1, {size - 1}]（等于序列长度会退化为零宽区间）: {block_size!r}"
        )
    if n_resamples < 1:
        raise StatisticsError(f"重采样次数必须为正: {n_resamples!r}")
    if not 0.0 < alpha < 1.0:
        raise StatisticsError(f"alpha 必须在 (0,1) 内: {alpha!r}")
    rng = random.Random(seed)
    blocks_needed = math.ceil(size / block_size)
    starts_limit = size - block_size
    means = []
    for _ in range(n_resamples):
        sample: list[float] = []
        for _ in range(blocks_needed):
            start = rng.randint(0, starts_limit)
            sample.extend(series[start : start + block_size])
        means.append(sum(sample[:size]) / size)
    means.sort()
    lower_index = max(0, min(n_resamples - 1, int(math.floor(alpha / 2 * n_resamples))))
    upper_index = max(0, min(n_resamples - 1, int(math.ceil((1 - alpha / 2) * n_resamples)) - 1))
    return BootstrapCI(
        point=mean(series),
        lower=means[lower_index],
        upper=means[upper_index],
        n_resamples=n_resamples,
        block_size=block_size,
        seed=seed,
        alpha=alpha,
    )
