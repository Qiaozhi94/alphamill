"""必需统计的生产接线（`FR-004`/`AC-003`；任务 T009，`R1-001`）。

T009 实现了估计器原语（HAC IC、block bootstrap、BH-FDR、有效独立数 DSR、MinTRL），但首轮检视
发现它们**没有任何生产调用者**——单元测试只证明函数本身正确，证明不了流程用了它。本模块把
两层统计接进出货路径：

- **成员级**（canonical/preview 评测阶段）：由信号与标签构造逐期 IC 序列，计算 HAC 稳健 IC 与
  block bootstrap 置信区间，异常由 `statistics_stage` 收敛为 `INCOMPLETE` + `estimator_failure`，
  不得伪装成 PASS（`design.md` §7）；
- **cohort 级**（finalize 阶段）：成员 p 值做 BH-FDR，成员两两相关性导出有效独立数，并以最好成员
  的收益序列计算 DSR 与 MinTRL；任一估计器异常把 cohort 统计标为 `INCOMPLETE`。
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from alphamill.factor_factory.bench.multiplicity import (
    benjamini_hochberg,
    deflated_sharpe_ratio,
    effective_trials,
    min_track_record_length,
    statistics_stage,
)
from alphamill.factor_factory.bench.stage_model import STAGE_TEMPORAL_STABILITY
from alphamill.factor_factory.bench.statistics import (
    StatisticsError,
    block_bootstrap_ci,
    fit_ic,
    normal_cdf,
    period_ic_series,
)

DEFAULT_HAC_LAG = 5
DEFAULT_BLOCK_SIZE = 5
DEFAULT_RESAMPLES = 1000
DEFAULT_SEED = 7
DEFAULT_FDR_ALPHA = 0.05


def statistics_parameters(method_config: Mapping[str, Any]) -> dict[str, Any]:
    """从预注册方法配置取统计参数（阈值不硬编码在评测函数，`FR-004`）。"""
    normalized = method_config.get("normalized", {}) if isinstance(method_config, Mapping) else {}
    ic = normalized.get("ic", {}) if isinstance(normalized, Mapping) else {}
    bootstrap = normalized.get("bootstrap", {}) if isinstance(normalized, Mapping) else {}
    multiplicity = normalized.get("multiplicity", {}) if isinstance(normalized, Mapping) else {}
    return {
        "hac_lag": int(ic.get("hac_lag", DEFAULT_HAC_LAG)),
        "block_size": int(bootstrap.get("block_size", DEFAULT_BLOCK_SIZE)),
        "n_resamples": int(bootstrap.get("n_resamples", DEFAULT_RESAMPLES)),
        "seed": int(bootstrap.get("seed", DEFAULT_SEED)),
        "fdr_alpha": float(multiplicity.get("fdr_alpha", DEFAULT_FDR_ALPHA)),
    }


def _cross_sectional_periods(
    times: Sequence[str], signals: Sequence[float], labels: Sequence[float]
) -> list[tuple[Sequence[float], Sequence[float]]]:
    groups: dict[str, list[int]] = {}
    for index, stamp in enumerate(times):
        groups.setdefault(str(stamp), []).append(index)
    return [
        ([signals[index] for index in indices], [labels[index] for index in indices])
        for indices in groups.values()
        if len(indices) >= 2
    ]


def _rolling_periods(
    signals: Sequence[float], labels: Sequence[float], window: int
) -> list[tuple[Sequence[float], Sequence[float]]]:
    size = len(signals)
    return [
        (tuple(signals[start : start + window]), tuple(labels[start : start + window]))
        for start in range(0, size - window + 1)
    ]


def build_period_ic_series(
    *,
    times: Sequence[str],
    signals: Sequence[float],
    labels: Sequence[float],
    block_size: int,
    symbols: Sequence[str] | None = None,
) -> tuple[tuple[float, ...], str]:
    """构造逐期 IC 序列：多标的按同一 timestamp 的横截面，单序列退回滚动窗。"""
    if symbols is not None:
        periods = _cross_sectional_periods(times, signals, labels)
        if len(periods) >= 2:
            return period_ic_series(periods), "cross_sectional"
    size = len(signals)
    window = max(2, min(block_size, max(2, size // 2)))
    return period_ic_series(_rolling_periods(signals, labels, window)), "rolling"


def member_statistics(
    *,
    times: Sequence[str],
    signals: Sequence[float],
    labels: Sequence[float],
    method_config: Mapping[str, Any],
    observed_at: str,
    symbols: Sequence[str] | None = None,
) -> tuple[dict[str, Any] | None, Any]:
    """成员级必需统计；异常统一失败关闭为 `INCOMPLETE`（`AC-003`）。"""
    parameters = statistics_parameters(method_config)

    def compute() -> dict[str, Any]:
        series, mode = build_period_ic_series(
            times=times,
            signals=signals,
            labels=labels,
            block_size=parameters["block_size"],
            symbols=symbols,
        )
        ic = fit_ic(series, hac_lag=parameters["hac_lag"])
        bootstrap = block_bootstrap_ci(
            series,
            block_size=parameters["block_size"],
            n_resamples=parameters["n_resamples"],
            seed=parameters["seed"],
        )
        return {
            "period_mode": mode,
            "periods": len(series),
            "ic": ic.to_payload(),
            "bootstrap": bootstrap.to_payload(),
            "p_value": 2.0 * (1.0 - normal_cdf(abs(ic.t_stat))),
            "method": parameters,
            "status": "PASS",
        }

    payload, stage = statistics_stage(STAGE_TEMPORAL_STABILITY, compute, observed_at=observed_at)
    return payload, stage


def _sharpe(series: Sequence[float]) -> float:
    values = [float(value) for value in series]
    size = len(values)
    if size < 2:
        raise StatisticsError(f"Sharpe 至少需要 2 期，收到 {size}")
    center = sum(values) / size
    variance = sum((value - center) ** 2 for value in values) / (size - 1)
    if variance <= 0:
        raise StatisticsError("收益序列方差非正，Sharpe 不可计算")
    return center / math.sqrt(variance)


def cohort_statistics(
    *,
    member_p_values: Mapping[str, float],
    member_returns: Mapping[str, Sequence[float]],
    correlations: Sequence[float],
    alpha: float = 0.05,
) -> dict[str, Any]:
    """cohort 级必需统计；任一必需估计器异常/缺失即整体 `INCOMPLETE`（不产出部分结论）。

    输入按 `candidate_id` 映射对齐（不再用并发列表），返回逐成员的 `bh_rejected` 与 `dsr`，
    供 finalize 把多重检验结论接进 `statistically_dead`。
    """
    if not member_p_values:
        return {
            "status": "INCOMPLETE",
            "fdr_alpha": alpha,
            "reason": "无成员 p 值，BH-FDR 不可判定",
        }
    candidates = list(member_p_values)
    try:
        bh = benjamini_hochberg([float(member_p_values[name]) for name in candidates], alpha=alpha)
    except StatisticsError as exc:
        return {"status": "INCOMPLETE", "fdr_alpha": alpha, "reason": f"BH-FDR 估计器异常: {exc}"}
    result: dict[str, Any] = {
        "status": "PASS",
        "fdr_alpha": alpha,
        "bh": bh.to_payload(),
        "bh_rejected": {
            name: bool(flag) for name, flag in zip(candidates, bh.rejected, strict=True)
        },
    }
    try:
        trials = effective_trials(correlations) if correlations else 1.0
    except StatisticsError as exc:
        return {**result, "status": "INCOMPLETE", "reason": f"有效独立数估计器异常: {exc}"}
    result["effective_trials"] = trials
    n_trials = max(1, math.ceil(trials))

    sharpes: dict[str, float] = {}
    for candidate, series in member_returns.items():
        try:
            sharpes[candidate] = _sharpe(series)
        except StatisticsError:
            continue
    if not sharpes:
        return {
            **result,
            "status": "INCOMPLETE",
            "reason": "无成员可计算 Sharpe，DSR/MinTRL 不可判定",
        }
    best_candidate = max(sharpes, key=lambda name: sharpes[name])
    best_sharpe = sharpes[best_candidate]
    result["best_candidate"] = best_candidate
    result["best_sharpe"] = best_sharpe
    if best_sharpe <= 0.0:
        return {
            **result,
            "status": "INCOMPLETE",
            "reason": f"最佳成员 Sharpe={best_sharpe:.6g} <= 0，DSR/MinTRL 无有限解",
        }
    dsr_map: dict[str, float | None] = {}
    for candidate, sharpe in sharpes.items():
        n_observations = len(member_returns[candidate])
        if n_observations < 2:
            dsr_map[candidate] = None
            continue
        sharpe_std = math.sqrt((1.0 + 0.5 * sharpe * sharpe) / n_observations)
        try:
            dsr_map[candidate] = deflated_sharpe_ratio(
                sharpe,
                n_trials=n_trials,
                sharpe_std=sharpe_std,
                n_observations=n_observations,
            )
        except StatisticsError:
            dsr_map[candidate] = None
    if dsr_map.get(best_candidate) is None:
        return {
            **result,
            "status": "INCOMPLETE",
            "dsr": dsr_map,
            "reason": "最佳成员 DSR 估计器异常",
        }
    result["dsr"] = dsr_map
    try:
        result["mintrl"] = min_track_record_length(best_sharpe, target_sharpe=0.0)
    except StatisticsError as exc:
        return {**result, "status": "INCOMPLETE", "reason": f"MinTRL 估计器异常: {exc}"}
    return result
