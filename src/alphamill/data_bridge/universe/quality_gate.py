"""新 pair 准入门与准入记录（`FR-004` / `DR-004` / `AC-005` / `AC-006` / T015 / T016）。

四项检查（`FR-004`）与原因码一一对应：

| 检查 | 失败原因码 |
|---|---|
| 缺失率 | `missing_ratio_exceeded` |
| 时间边界闭合 | `boundary_not_closed` |
| 重复主键 | `duplicate_primary_key` |
| 跨周期对账 | `aggregate_mismatch` |

口径细节：

- **缺失率**按该 pair 的**实际可得窗口**算（`max(窗口起点, 真实上市时间)`），默认阈值 1%；
  上线晚不算缺失（`AC-006`）；
- **边界闭合**：首行 ≤ 窗口起点 且 末行 ≥ 窗口终点 − 1 分钟；
- **重复主键**：同一 `(exchange, symbol, time)` 多行——参考表有主键，检测路径由无主键
  scratch 表 fixture 真实触发，不写成恒真的空转断言；
- **跨周期对账**：连续聚合行数与 1m 基表按桶重算**精确相等**，差得不多也不放行。

判定结论三态：`ACTIVE`（全过）/ `QUARANTINED`（任一失败）/ `INCOMPLETE`（回填未完成，
不判 PASS）。判定记录只追加，最新一条（`judged_at, id`）是准入状态真相源（`DR-004`）；
它与台账的可交易期区间相互独立（spec §5 不变量）。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from alphamill.data_bridge.universe.canonical import utc_iso
from alphamill.data_bridge.universe.errors import QualityGateError
from alphamill.data_bridge.universe.gate_sql import (
    AGGREGATES,
    aggregate_mismatch,
    backfill_status,
    duplicate_keys,
    row_bounds,
)
from alphamill.data_bridge.universe.verdicts import (
    VERDICT_ACTIVE,
    VERDICT_INCOMPLETE,
    VERDICT_QUARANTINED,
    VERDICTS,
    PairGateResult,
    admitted_pairs,
    current_verdicts,
    export_admitted,
    record_verdicts,
)

# 判定记录与导出准入集合的实现搬到了 `verdicts.py`（文件行数治理）；这里保留同名
# re-export，调用方（含 `admission.py` 与测试）的导入路径不变。
__all__ = [
    "AGGREGATES",
    "DEFAULT_MISSING_RATIO",
    "GateThresholds",
    "PairGateResult",
    "REASON_AGGREGATE",
    "REASON_BOUNDARY",
    "REASON_DUPLICATE",
    "REASON_INCOMPLETE",
    "REASON_MISSING_RATIO",
    "VERDICT_ACTIVE",
    "VERDICT_INCOMPLETE",
    "VERDICT_QUARANTINED",
    "VERDICTS",
    "admitted_pairs",
    "check_pair",
    "current_verdicts",
    "effective_window",
    "expected_minutes",
    "export_admitted",
    "gate_pairs",
    "record_verdicts",
]

REASON_MISSING_RATIO = "missing_ratio_exceeded"
REASON_BOUNDARY = "boundary_not_closed"
REASON_DUPLICATE = "duplicate_primary_key"
REASON_AGGREGATE = "aggregate_mismatch"
REASON_INCOMPLETE = "backfill_incomplete"

DEFAULT_MISSING_RATIO = 0.01


@dataclass(frozen=True, kw_only=True)
class GateThresholds:
    """阈值可配但默认不放宽（ADR-0003：换一套阈值会让新老数据不可比）。"""

    missing_ratio: float = DEFAULT_MISSING_RATIO

    def __post_init__(self) -> None:
        if not 0.0 <= self.missing_ratio <= 1.0:
            raise QualityGateError(f"missing_ratio 阈值非法: {self.missing_ratio!r}")


def effective_window(
    *,
    window_start: datetime,
    window_end: datetime,
    listed_at: datetime | None = None,
    delisting_end: datetime | None = None,
) -> tuple[datetime, datetime]:
    """实际可得窗口：上线晚于窗口起点不算缺失（`AC-006`）。"""
    start = window_start if listed_at is None else max(window_start, listed_at)
    end = window_end if delisting_end is None else min(window_end, delisting_end)
    return start, end


def expected_minutes(start: datetime, end: datetime) -> int:
    seconds = (end - start).total_seconds()
    if seconds <= 0:
        return 0
    return int(seconds // 60)


def check_pair(
    conn,
    *,
    exchange: str,
    market_type: str,
    db_symbol: str,
    lake_pair: str,
    window_start: datetime,
    window_end: datetime,
    listed_at: datetime | None = None,
    delisting_end: datetime | None = None,
    source_table: str = "ohlcv_1m",
    thresholds: GateThresholds | None = None,
    require_backfill_complete: bool = True,
) -> PairGateResult:
    """对单个 pair 跑四项检查；返回判定（不写库，写库由 `record_verdicts` 负责）。"""
    limits = thresholds or GateThresholds()
    start, end = effective_window(
        window_start=window_start,
        window_end=window_end,
        listed_at=listed_at,
        delisting_end=delisting_end,
    )
    expected = expected_minutes(start, end)
    metrics: dict[str, Any] = {
        "window_start": utc_iso(start),
        "window_end": utc_iso(end),
        "expected_minutes": expected,
        "thresholds": {"missing_ratio": limits.missing_ratio},
        "source_table": source_table,
    }

    if require_backfill_complete:
        status = backfill_status(conn, exchange, db_symbol, window_start, window_end)
        metrics["backfill_status"] = status
        if status != "complete":
            return _result(
                db_symbol,
                lake_pair,
                exchange,
                market_type,
                VERDICT_INCOMPLETE,
                REASON_INCOMPLETE,
                metrics,
            )

    rows, first, last = row_bounds(conn, source_table, exchange, db_symbol, start, end)
    metrics.update(
        {
            "rows": rows,
            "first": None if first is None else utc_iso(first),
            "last": None if last is None else utc_iso(last),
        }
    )
    if rows == 0:
        return _result(
            db_symbol,
            lake_pair,
            exchange,
            market_type,
            VERDICT_INCOMPLETE,
            REASON_INCOMPLETE,
            metrics,
        )

    missing = max(expected - rows, 0)
    ratio = (missing / expected) if expected else 1.0
    metrics["missing_rows"] = missing
    metrics["missing_ratio"] = round(ratio, 6)
    if ratio > limits.missing_ratio:
        return _result(
            db_symbol,
            lake_pair,
            exchange,
            market_type,
            VERDICT_QUARANTINED,
            REASON_MISSING_RATIO,
            metrics,
        )

    boundary_ok = (
        first is not None
        and last is not None
        and (first <= start and last >= end - timedelta(minutes=1))
    )
    metrics["boundary_ok"] = boundary_ok
    if not boundary_ok:
        return _result(
            db_symbol,
            lake_pair,
            exchange,
            market_type,
            VERDICT_QUARANTINED,
            REASON_BOUNDARY,
            metrics,
        )

    duplicates = duplicate_keys(conn, source_table, exchange, db_symbol, start, end)
    metrics["duplicate_keys"] = duplicates
    if duplicates:
        return _result(
            db_symbol,
            lake_pair,
            exchange,
            market_type,
            VERDICT_QUARANTINED,
            REASON_DUPLICATE,
            metrics,
        )

    aggregates = aggregate_mismatch(conn, exchange, start, end)
    metrics["aggregates"] = aggregates
    if any(not item["match"] for item in aggregates.values()):
        return _result(
            db_symbol,
            lake_pair,
            exchange,
            market_type,
            VERDICT_QUARANTINED,
            REASON_AGGREGATE,
            metrics,
        )

    return _result(db_symbol, lake_pair, exchange, market_type, VERDICT_ACTIVE, None, metrics)


def gate_pairs(
    conn,
    *,
    pairs: Sequence[tuple[str, str, str]],
    exchange: str,
    market_type: str,
    window_start: datetime,
    window_end: datetime,
    listed_at: dict[str, datetime] | None = None,
    thresholds: GateThresholds | None = None,
    require_backfill_complete: bool = True,
) -> list[PairGateResult]:
    """逐 pair 跑门禁；`pairs` 为 `(db_symbol, lake_pair, reason)` 三元组序列。"""
    listed = listed_at or {}
    return [
        check_pair(
            conn,
            exchange=exchange,
            market_type=market_type,
            db_symbol=db_symbol,
            lake_pair=lake_pair,
            window_start=window_start,
            window_end=window_end,
            listed_at=listed.get(db_symbol),
            thresholds=thresholds,
            require_backfill_complete=require_backfill_complete,
        )
        for db_symbol, lake_pair, _reason in pairs
    ]


def _result(
    db_symbol: str,
    lake_pair: str,
    exchange: str,
    market_type: str,
    verdict: str,
    reason_code: str | None,
    metrics: dict[str, Any],
) -> PairGateResult:
    return PairGateResult(
        db_symbol=db_symbol,
        lake_pair=lake_pair,
        exchange=exchange,
        market_type=market_type,
        verdict=verdict,
        reason_code=reason_code,
        metrics=metrics,
    )
