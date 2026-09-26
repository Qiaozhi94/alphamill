"""F003 IC 口径对齐回归（FR-006 / AC-007 冒烟第 2 天判据）。

**只做数值一致性回归**：把「张量世界」与「pandas 世界」对同一表达式算出的横截面 IC
做容差内比对，用于尽早发现两套口径漂移。本模块**不产 verdict、不写台账、不产证据**；
评测权唯一属 F007（ADR-0003）。

范围说明：vendor 的具体张量计算器随被丢弃的 `alphagen_qlib/calculator.py` 一同移除，
因此张量侧以独立的 numpy/torch 参考实现承载；若未来扩展 shim 提供具体计算器，可把
`tensor_ic` 的输入换成 vendor `Expression.evaluate` 的输出而不改本模块接口。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd

IC_PARITY_TOLERANCE: Final = 1e-6


@dataclass(frozen=True, kw_only=True)
class IcParityResult:
    """两个口径的 IC 差异；字段只描述数值一致性，不含任何裁决。"""

    matched: bool
    max_abs_diff: float
    points: int
    detail: str


def _as_2d(array: object) -> np.ndarray:
    if hasattr(array, "detach"):
        array = array.detach().cpu().numpy()
    values = np.asarray(array, dtype=float)
    if values.ndim != 2:
        raise ValueError(f"IC 输入必须是二维 (timestamps x pairs)，实际 {values.ndim} 维")
    return values


def _average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(values.size, dtype=float)
    ranks[order] = np.arange(1, values.size + 1, dtype=float)
    sorted_values = values[order]
    start = 0
    while start < sorted_values.size:
        stop = start + 1
        while stop < sorted_values.size and sorted_values[stop] == sorted_values[start]:
            stop += 1
        if stop - start > 1:
            ranks[order[start:stop]] = ranks[order[start:stop]].mean()
        start = stop
    return ranks


def _row_spearman(left: np.ndarray, right: np.ndarray) -> float | None:
    if left.size < 2:
        return None
    ranked_left, ranked_right = _average_ranks(left), _average_ranks(right)
    if ranked_left.std() == 0 or ranked_right.std() == 0:
        return None
    return float(np.corrcoef(ranked_left, ranked_right)[0, 1])


def tensor_ic(
    values: object,
    forward_returns: object,
    *,
    universe_mask: object | None = None,
) -> float:
    """张量世界的横截面 Spearman IC：逐 timestamp 排名相关，再对 timestamp 取均值。"""
    rows = _as_2d(values)
    returns = _as_2d(forward_returns)
    if rows.shape != returns.shape:
        raise ValueError("signal 与 forward_returns 形状必须一致")
    mask = np.ones_like(rows, dtype=bool) if universe_mask is None else _as_2d(universe_mask) > 0

    per_timestamp: list[float] = []
    for index in range(rows.shape[0]):
        keep = mask[index] & np.isfinite(rows[index]) & np.isfinite(returns[index])
        ic = _row_spearman(rows[index][keep], returns[index][keep])
        if ic is not None:
            per_timestamp.append(ic)
    return float(np.mean(per_timestamp)) if per_timestamp else 0.0


def pandas_ic(
    values: pd.Series,
    forward_returns: pd.Series,
    *,
    universe_mask: pd.Series | None = None,
) -> float:
    """pandas 世界的同一口径；与 tensor_ic 逐 timestamp 排名相关 + 取均值完全一致。"""
    frame = pd.DataFrame({"signal": values, "forward": forward_returns})
    if universe_mask is not None:
        frame = frame[universe_mask.reindex(frame.index).fillna(False).astype(bool)]
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()

    per_timestamp: list[float] = []
    for _, group in frame.groupby(level=0):
        if len(group) < 2:
            continue
        ranked_signal = group["signal"].rank()
        ranked_forward = group["forward"].rank()
        if ranked_signal.std() == 0 or ranked_forward.std() == 0:
            continue
        per_timestamp.append(float(np.corrcoef(ranked_signal, ranked_forward)[0, 1]))
    return float(np.mean(per_timestamp)) if per_timestamp else 0.0


def compare_ic(
    expression: tuple[str, ...],
    panel: pd.DataFrame,
    forward_returns: pd.Series,
    *,
    feature_map: dict[str, int],
    tolerance: float = IC_PARITY_TOLERANCE,
) -> IcParityResult:
    """编译表达式得到信号，比较张量侧与 pandas 侧 IC 的差异。"""
    from alphamill.factor_factory.generators.alphagen_adapter import compile_alphagen_expression

    compute = compile_alphagen_expression(
        expression, scope="cross_sectional", feature_map=feature_map
    )
    signal = compute(panel)

    mask = panel["__in_universe__"].astype(bool)
    timestamps = panel.index.get_level_values("timestamp").unique()
    pairs = panel.index.get_level_values("pair").unique()
    matrix = signal.unstack("pair").reindex(index=timestamps, columns=pairs)
    returns = forward_returns.unstack("pair").reindex(index=timestamps, columns=pairs)
    mask_matrix = mask.unstack("pair").reindex(index=timestamps, columns=pairs).fillna(False)

    tensor_value = tensor_ic(
        matrix.to_numpy(), returns.to_numpy(), universe_mask=mask_matrix.to_numpy()
    )
    pandas_value = pandas_ic(signal, forward_returns, universe_mask=mask)
    diff = abs(tensor_value - pandas_value)
    return IcParityResult(
        matched=diff <= tolerance,
        max_abs_diff=diff,
        points=int(mask_matrix.to_numpy().sum()),
        detail=f"tensor={tensor_value:.12f} pandas={pandas_value:.12f}",
    )
