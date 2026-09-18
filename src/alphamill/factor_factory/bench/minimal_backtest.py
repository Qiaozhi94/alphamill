"""最小回测摘要：把信号序列折算成成本模型需要的四个量（任务 T006/T007）。

v0.2 preview 的最小切片：方向仓位 `sign(signal)`，逐期收益 `position × forward_return`。
成本前收益与换手都取**累计**口径（不是均值），否则与一次性扣成本不可比：

```text
gross_return = Σ position_i × forward_return_i
turnover     = Σ |position_i − position_{i−1}|      （position_0 = 0）
round_trips  = position 发生变化的次数（每次变化 = 平旧仓 + 开新仓）
```

「一「笔」= 一次完整往返交易（同一仓位周期开平合为一笔）」（`FR-005`）：无成交时按独立信号
观测数计，并以 `sample_unit` 显式记录计数口径。purged/embargoed rolling split 与稳定性报告由
任务 T010 在此基础上扩展。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from alphamill.evaluation.contract_common import parse_utc
from alphamill.factor_factory.bench.stage_model import (
    SAMPLE_UNIT_OBSERVATIONS,
    SAMPLE_UNIT_ROUND_TRIPS,
    StageModelError,
)


@dataclass(frozen=True)
class TradeSummary:
    gross_return: float
    turnover: float
    round_trips: int
    holding_period_hours: float
    sample_unit: str
    trade_count: int
    n_observations: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "gross_return": self.gross_return,
            "turnover": self.turnover,
            "round_trips": self.round_trips,
            "holding_period_hours": self.holding_period_hours,
            "sample_unit": self.sample_unit,
            "trade_count": self.trade_count,
            "n_observations": self.n_observations,
        }


def sign_positions(signal: Sequence[float]) -> tuple[float, ...]:
    positions = []
    for value in signal:
        if value != value:
            raise StageModelError("信号含缺失值，无法建立仓位")
        positions.append(1.0 if value > 0 else (-1.0 if value < 0 else 0.0))
    return tuple(positions)


def _window_hours(times: Sequence[str]) -> float:
    if len(times) < 2:
        return 0.0
    start = parse_utc(times[0], "signals[0].time")
    end = parse_utc(times[-1], "signals[-1].time")
    return max(0.0, (end - start).total_seconds() / 3600.0)


def summarize(
    signal: Sequence[float],
    label: Sequence[float],
    times: Sequence[str],
) -> TradeSummary:
    values = list(signal)
    labels = list(label)
    stamps = list(times)
    if not (len(values) == len(labels) == len(stamps)):
        raise StageModelError(
            f"signal/label/time 长度不一致: {len(values)}/{len(labels)}/{len(stamps)}"
        )
    n_observations = len(values)
    if n_observations == 0:
        raise StageModelError("空序列无法建立回测摘要")
    positions = sign_positions(values)
    gross_return = sum(position * value for position, value in zip(positions, labels, strict=True))
    previous = 0.0
    turnover = 0.0
    transitions = 0
    for position in positions:
        delta = abs(position - previous)
        turnover += delta
        transitions += 1 if delta > 0 else 0
        previous = position
    round_trips = transitions
    if round_trips > 0:
        sample_unit = SAMPLE_UNIT_ROUND_TRIPS
        trade_count = round_trips
    else:
        sample_unit = SAMPLE_UNIT_OBSERVATIONS
        trade_count = n_observations
    holding = _window_hours(stamps) / max(round_trips, 1)
    return TradeSummary(
        gross_return=gross_return,
        turnover=turnover,
        round_trips=round_trips,
        holding_period_hours=holding,
        sample_unit=sample_unit,
        trade_count=trade_count,
        n_observations=n_observations,
    )
