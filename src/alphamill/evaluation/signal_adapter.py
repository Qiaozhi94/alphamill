"""信号型 `FactorDef` 适配契约（F007 `DR-007`，任务 T001）。

F004 交付真实 Kronos 推理实例与 `/predict` 契约，但**不**升级 `signals_log` 内容、也不切换
消费者路由；因此从信号到可评测 `FactorDef` 的适配由 F007 拥有：

- 适配器只做形状/语义映射，**不改变信号数值**（数值一致性由
  `tests/contract/test_f007_upstream_contracts.py` 的 fixture 固定）；
- `source=placeholder` 分层：**canonical 拒绝**（`E_INPUT_INVALID`，fail-closed）；
  **preview 允许**但必须标注 `signal_source=placeholder` 与 `approximation=true`，
  且不得据此产生任何晋级结论。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from alphamill.evaluation.contract_common import (
    EXECUTION_TIERS,
    SIGNAL_SOURCE_PLACEHOLDER,
    TIER_CANONICAL,
    UpstreamContractError,
)


@dataclass(frozen=True)
class SignalObservation:
    """形状映射后的信号观测；数值原样保留（适配器不改数值）。"""

    time: str
    symbol: str
    value: float
    label: float | None
    horizon: int


@dataclass(frozen=True)
class SignalFactorProvenance:
    dataset: str
    source_distribution: Mapping[str, int]
    adapter_version: str
    signal_columns: tuple[str, ...]
    label_horizons: Mapping[str, int]

    @property
    def has_placeholder(self) -> bool:
        return self.source_distribution.get(SIGNAL_SOURCE_PLACEHOLDER, 0) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "source_distribution": dict(self.source_distribution),
            "adapter_version": self.adapter_version,
            "signal_columns": list(self.signal_columns),
            "label_horizons": dict(self.label_horizons),
        }


def adapt_signal_records(
    records: Iterable[Mapping[str, Any]],
    *,
    dataset: str,
    adapter_version: str,
    signal_column: str,
    label_column: str | None = None,
    horizons: Mapping[str, int] | None = None,
) -> tuple[tuple[SignalObservation, ...], SignalFactorProvenance]:
    """`signals_log` 记录 → 可评测观测序列；只做形状/语义映射，不改变数值。"""
    horizon_by_source = dict(horizons or {})
    observations: list[SignalObservation] = []
    distribution: dict[str, int] = {}
    for index, record in enumerate(records):
        source = str(record.get("source", ""))
        distribution[source] = distribution.get(source, 0) + 1
        raw_value = record.get(signal_column)
        if not isinstance(raw_value, (int, float)) or isinstance(raw_value, bool):
            raise UpstreamContractError(f"第 {index} 条信号的 {signal_column} 不是数值")
        raw_label = record.get(label_column) if label_column else None
        if raw_label is not None and (
            not isinstance(raw_label, (int, float)) or isinstance(raw_label, bool)
        ):
            raise UpstreamContractError(f"第 {index} 条信号的 {label_column} 不是数值")
        observations.append(
            SignalObservation(
                time=str(record.get("time", "")),
                symbol=str(record.get("symbol", "")),
                value=float(raw_value),
                label=None if raw_label is None else float(raw_label),
                horizon=int(horizon_by_source.get(source, 0)),
            )
        )
    provenance = SignalFactorProvenance(
        dataset=dataset,
        source_distribution=distribution,
        adapter_version=adapter_version,
        signal_columns=(signal_column,),
        label_horizons=horizon_by_source,
    )
    return tuple(observations), provenance


def assert_signal_source_allowed(
    provenance: SignalFactorProvenance, execution_tier: str
) -> dict[str, Any]:
    """`source=placeholder` 分层：canonical 拒绝（`E_INPUT_INVALID`），preview 显式标注近似。"""
    if execution_tier not in EXECUTION_TIERS:
        raise UpstreamContractError(
            f"未知执行层级: {execution_tier!r}（合法: {list(EXECUTION_TIERS)}）"
        )
    if not provenance.has_placeholder:
        return {"signal_source": "real", "approximation": False}
    if execution_tier == TIER_CANONICAL:
        raise UpstreamContractError(
            "canonical 拒绝 source=placeholder 的信号源（fail-closed）",
            code="E_INPUT_INVALID",
        )
    return {"signal_source": SIGNAL_SOURCE_PLACEHOLDER, "approximation": True}
