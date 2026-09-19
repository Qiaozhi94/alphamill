"""信号质量阶段与近似/来源标注（`FR-003`/`NFR-004`/`DR-007`；任务 T007）。

- **最小信号质量**：Rank IC 与观测数。观测数为零记 `INCOMPLETE`（必需输入缺失），不足
  `min_observations` 记 `UNDERPOWERED`——两者都**不得**记为 `PASS`，也不得把空值当零
  （`design.md` §3.3 / `FR-003` 场景「指标样本不足」）。
- **近似标注**：`approximation.is_approximate` 与 `reduced_dimensions[]` 必须显式；canonical
  恒为 `is_approximate=false`，不因性能压力静默缩窗或采样（`NFR-004`）。
- **信号来源 provenance**：`source=placeholder` 在 canonical 失败关闭（`E_INPUT_INVALID`），
  preview 允许但必须标注 `signal_source=placeholder` 且 `approximation=true`（`DR-007`）。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import pandas as pd

from alphamill.evaluation.contract_common import (
    EXECUTION_TIERS,
    SIGNAL_SOURCE_PLACEHOLDER,
    TIER_CANONICAL,
)
from alphamill.evaluation.signal_adapter import assert_signal_source_allowed
from alphamill.factor_factory.bench.stage_model import (
    STAGE_SIGNAL_QUALITY,
    STATUS_INCOMPLETE,
    STATUS_PASS,
    STATUS_UNDERPOWERED,
    FailureRecord,
    StageModelError,
    StageResult,
)

ERROR_CODE = "E_REQUIRED_METRIC_FAILED"
MIN_OBSERVATIONS = 30


def rank_ic(signal: Sequence[float], label: Sequence[float]) -> float:
    """Spearman（rank）IC；缺失值或退化输入一律拒绝，不静默返回 0。"""
    values = list(signal)
    labels = list(label)
    if len(values) != len(labels):
        raise StageModelError(f"信号与标签长度不一致: {len(values)} vs {len(labels)}")
    if len(values) < 2:
        raise StageModelError("rank IC 至少需要 2 个观测")
    signal_series = pd.Series(values, dtype="float64")
    label_series = pd.Series(labels, dtype="float64")
    if signal_series.isna().any() or label_series.isna().any():
        raise StageModelError("rank IC 不接受缺失值（不得当作 0）")
    if signal_series.nunique() < 2 or label_series.nunique() < 2:
        raise StageModelError("rank IC 无法计算：信号或标签为常数")
    value = signal_series.rank().corr(label_series.rank())
    if pd.isna(value):
        raise StageModelError("rank IC 无法计算（退化输入）")
    return float(value)


@dataclass(frozen=True)
class SignalQualityResult:
    rank_ic: float | None
    n_observations: int
    min_observations: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "rank_ic": self.rank_ic,
            "n_observations": self.n_observations,
            "min_observations": self.min_observations,
        }


def evaluate_signal_quality(
    signal: Sequence[float],
    label: Sequence[float],
    *,
    observed_at: str,
    min_observations: int = MIN_OBSERVATIONS,
) -> tuple[SignalQualityResult, StageResult]:
    n_observations = len(list(signal))
    if n_observations == 0:
        failure = FailureRecord(
            stage=STAGE_SIGNAL_QUALITY,
            owner="signal",
            mechanism="missing_input",
            error_code=ERROR_CODE,
            first_seen=observed_at,
        )
        result = SignalQualityResult(None, 0, min_observations)
        return result, StageResult(
            stage_id=STAGE_SIGNAL_QUALITY,
            status=STATUS_INCOMPLETE,
            reason="无信号观测（必需输入缺失）",
            failures=(failure,),
        )
    if n_observations < min_observations:
        result = SignalQualityResult(None, n_observations, min_observations)
        return result, StageResult(
            stage_id=STAGE_SIGNAL_QUALITY,
            status=STATUS_UNDERPOWERED,
            reason=f"观测数 {n_observations} < 最小观测数 {min_observations}",
        )
    value = rank_ic(signal, label)
    return (
        SignalQualityResult(value, n_observations, min_observations),
        StageResult(stage_id=STAGE_SIGNAL_QUALITY, status=STATUS_PASS),
    )


@dataclass(frozen=True)
class Approximation:
    """报告 `approximation` 字段（`NFR-004`）；canonical 恒为非近似。"""

    is_approximate: bool = False
    reduced_dimensions: tuple[str, ...] = ()
    signal_source: str = "real"

    def __post_init__(self) -> None:
        if not self.is_approximate and self.reduced_dimensions:
            raise StageModelError("非近似结果不得声明 reduced_dimensions")
        if self.signal_source == SIGNAL_SOURCE_PLACEHOLDER and not self.is_approximate:
            raise StageModelError("source=placeholder 必须标记 approximation=true")

    def to_payload(self) -> dict[str, Any]:
        return {
            "is_approximate": self.is_approximate,
            "reduced_dimensions": list(self.reduced_dimensions),
            "signal_source": self.signal_source,
        }


def approximation_for(
    execution_tier: str,
    *,
    signal_source: str = "real",
    reduced_dimensions: Sequence[str] = (),
) -> Approximation:
    """canonical 拒绝任何近似；preview 的采样/缩窗与 placeholder 来源必须显式标注。"""
    if execution_tier not in EXECUTION_TIERS:
        raise StageModelError(f"未知执行层级: {execution_tier!r}")
    dimensions = tuple(sorted({str(item) for item in reduced_dimensions}))
    if execution_tier == TIER_CANONICAL:
        if dimensions or signal_source != "real":
            raise StageModelError(
                "canonical 不得近似：不接受缩窗/采样维度或非真实信号来源（NFR-004）"
            )
        return Approximation(is_approximate=False, reduced_dimensions=(), signal_source="real")
    return Approximation(
        is_approximate=bool(dimensions) or signal_source == SIGNAL_SOURCE_PLACEHOLDER,
        reduced_dimensions=dimensions,
        signal_source=signal_source,
    )


def signal_source_payload(
    provenance: Any,
    execution_tier: str,
    *,
    reduced_dimensions: Sequence[str] = (),
) -> dict[str, Any]:
    """信号来源 provenance + 近似标注；canonical 遇 placeholder 即失败关闭（`DR-007`）。"""
    decision = assert_signal_source_allowed(provenance, execution_tier)
    approximation = approximation_for(
        execution_tier,
        signal_source=decision["signal_source"],
        reduced_dimensions=reduced_dimensions,
    )
    return {
        "signal_provenance": provenance.to_dict(),
        "approximation": approximation.to_payload(),
    }
