"""曲线侧车（`curves.parquet`）的最小列集与标量互推（`FR-006`/`AC-005`/`AC-011`；任务 T011）。

架构 §4.2 的最小列集：UTC 时间、成本后权益、回撤、q1~q5 与 long-short 累计收益、各 horizon 的
rolling IC。**标量摘要必须能从侧车在容差内重算**——publisher 在发布前做这项互推校验，失败即
`E_PUBLISH_INCOMPLETE`（不出现半个 PASS）。列 metadata 记录 schema/return convention。
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

SCHEMA_VERSION = 1
RETURN_CONVENTION = "simple_return_net_of_cost"
TOLERANCE = 1e-9
QUANTILE_COLUMNS = ("q1", "q2", "q3", "q4", "q5")
BASE_COLUMNS = ("time", "equity_net", "drawdown")
SCALAR_FIELDS = (
    "final_equity",
    "total_return",
    "max_drawdown",
    "long_short_total",
    "quantile_spread",
)


class CurvesError(ValueError):
    """曲线缺失、长度不一致或标量互推不符。"""


def rolling_ic_column(horizon: int) -> str:
    return f"rolling_ic_h{horizon}"


@dataclass(frozen=True)
class CurvesData:
    times: tuple[datetime, ...]
    equity_net: tuple[float, ...]
    drawdown: tuple[float, ...]
    quantiles: Mapping[str, tuple[float, ...]]
    long_short: tuple[float, ...]
    rolling_ic: Mapping[int, tuple[float, ...]]

    def __post_init__(self) -> None:
        size = len(self.times)
        if size == 0:
            raise CurvesError("曲线不能为空")
        missing = [name for name in QUANTILE_COLUMNS if name not in self.quantiles]
        if missing:
            raise CurvesError(f"曲线缺分位列: {missing}")
        for name, column in [
            ("equity_net", self.equity_net),
            ("drawdown", self.drawdown),
            ("long_short", self.long_short),
            *self.quantiles.items(),
            *((rolling_ic_column(h), c) for h, c in self.rolling_ic.items()),
        ]:
            if len(column) != size:
                raise CurvesError(f"列 {name} 长度 {len(column)} 与时间轴 {size} 不一致")

    def columns(self) -> dict[str, tuple[Any, ...]]:
        payload: dict[str, tuple[Any, ...]] = {
            "time": self.times,
            "equity_net": self.equity_net,
            "drawdown": self.drawdown,
        }
        payload.update(self.quantiles)
        payload["long_short"] = self.long_short
        for horizon in sorted(self.rolling_ic):
            payload[rolling_ic_column(horizon)] = self.rolling_ic[horizon]
        return payload

    def scalar_summary(self) -> dict[str, float]:
        final_equity = self.equity_net[-1]
        return {
            "final_equity": final_equity,
            "total_return": final_equity - self.equity_net[0],
            "max_drawdown": max(self.drawdown),
            "long_short_total": self.long_short[-1],
            "quantile_spread": self.quantiles["q5"][-1] - self.quantiles["q1"][-1],
        }


def write_curves(path: Path, data: CurvesData) -> None:
    columns = data.columns()
    columns["time"] = [stamp.astimezone(UTC) for stamp in data.times]
    metadata = {
        b"schema_version": str(SCHEMA_VERSION).encode(),
        b"return_convention": RETURN_CONVENTION.encode(),
    }
    table = pa.table(
        {name: pa.array(values) for name, values in columns.items()},
        metadata=metadata,
    )
    pq.write_table(table, path)


def read_curves(path: Path) -> CurvesData:
    if not path.is_file():
        raise CurvesError(f"曲线不存在: {path}")
    table = pq.read_table(path)
    metadata = {
        key.decode(): value.decode() for key, value in (table.schema.metadata or {}).items()
    }
    if metadata.get("schema_version") != str(SCHEMA_VERSION):
        raise CurvesError(f"不支持的 curves schema_version: {metadata.get('schema_version')!r}")
    if metadata.get("return_convention") != RETURN_CONVENTION:
        raise CurvesError(f"未知收益口径: {metadata.get('return_convention')!r}")
    payload = {name: table.column(name).to_pylist() for name in table.column_names}
    rolling_ic = {
        int(name.removeprefix("rolling_ic_h")): tuple(payload[name])
        for name in table.column_names
        if name.startswith("rolling_ic_h")
    }
    return CurvesData(
        times=tuple(payload["time"]),
        equity_net=tuple(payload["equity_net"]),
        drawdown=tuple(payload["drawdown"]),
        quantiles={name: tuple(payload[name]) for name in QUANTILE_COLUMNS},
        long_short=tuple(payload["long_short"]),
        rolling_ic=rolling_ic,
    )


def assert_scalars_match(declared: Mapping[str, Any], recomputed: Mapping[str, float]) -> None:
    """报告中的标量摘要必须与侧车重算一致（容差内），否则拒绝发布。"""
    for field in SCALAR_FIELDS:
        if field not in declared:
            raise CurvesError(f"报告缺曲线标量 {field!r}")
        value = declared[field]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise CurvesError(f"曲线标量 {field!r} 必须是数值: {value!r}")
        expected = recomputed[field]
        if abs(float(value) - expected) > TOLERANCE:
            raise CurvesError(
                f"曲线标量互推不符 {field}: 报告 {value} vs 重算 {expected}（容差 {TOLERANCE}）"
            )


def build_equity_curves(
    periods: Sequence[float],
    *,
    times: Sequence[datetime],
    quantiles: Mapping[str, Sequence[float]] | None = None,
    rolling_ic: Mapping[int, Sequence[float]] | None = None,
) -> CurvesData:
    """由逐期成本后收益构造标准曲线（权益、回撤与分位/IC 侧车）。"""
    if len(periods) != len(times):
        raise CurvesError(f"收益与时间轴长度不一致: {len(periods)} vs {len(times)}")
    for index in range(1, len(times)):
        if times[index] <= times[index - 1]:
            raise CurvesError(
                "时间轴必须严格递增（多标的面板需先按 timestamp 聚合，不得回跳）: "
                f"{times[index - 1]} -> {times[index]}"
            )
    equity: list[float] = []
    running = 1.0
    peak = 1.0
    drawdown: list[float] = []
    for value in periods:
        running *= 1.0 + value
        peak = max(peak, running)
        equity.append(running)
        drawdown.append(running / peak - 1.0)
    quantile_columns = {
        name: tuple(quantiles[name])
        if quantiles and name in quantiles
        else tuple([0.0] * len(periods))
        for name in QUANTILE_COLUMNS
    }
    return CurvesData(
        times=tuple(times),
        equity_net=tuple(equity),
        drawdown=tuple(drawdown),
        quantiles=quantile_columns,
        long_short=tuple(float(value) for value in periods),
        rolling_ic=(
            {horizon: tuple(values) for horizon, values in rolling_ic.items()} if rolling_ic else {}
        ),
    )
