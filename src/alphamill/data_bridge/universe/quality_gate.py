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

import json
import socket
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from alphamill.data_bridge.universe.canonical import utc_iso
from alphamill.data_bridge.universe.errors import QualityGateError

VERDICT_ACTIVE = "ACTIVE"
VERDICT_QUARANTINED = "QUARANTINED"
VERDICT_INCOMPLETE = "INCOMPLETE"
VERDICTS = (VERDICT_ACTIVE, VERDICT_QUARANTINED, VERDICT_INCOMPLETE)

REASON_MISSING_RATIO = "missing_ratio_exceeded"
REASON_BOUNDARY = "boundary_not_closed"
REASON_DUPLICATE = "duplicate_primary_key"
REASON_AGGREGATE = "aggregate_mismatch"
REASON_INCOMPLETE = "backfill_incomplete"

DEFAULT_MISSING_RATIO = 0.01
AGGREGATES = {
    "ohlcv_5m": "5 minutes",
    "ohlcv_15m": "15 minutes",
    "ohlcv_1h": "1 hour",
    "ohlcv_4h": "4 hours",
    "ohlcv_1d": "1 day",
}
_INSERT_SQL = """
INSERT INTO universe_quality_verdicts (
    universe_id, exchange, market_type, db_symbol, lake_pair,
    verdict, reason_code, metrics, judged_at, hostname
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
_CURRENT_SQL = """
SELECT DISTINCT ON (lake_pair)
       universe_id, exchange, market_type, db_symbol, lake_pair,
       verdict, reason_code, metrics, judged_at, hostname
FROM universe_quality_verdicts
{where}
ORDER BY lake_pair, judged_at DESC, id DESC
"""


@dataclass(frozen=True, kw_only=True)
class GateThresholds:
    """阈值可配但默认不放宽（ADR-0003：换一套阈值会让新老数据不可比）。"""

    missing_ratio: float = DEFAULT_MISSING_RATIO

    def __post_init__(self) -> None:
        if not 0.0 <= self.missing_ratio <= 1.0:
            raise QualityGateError(f"missing_ratio 阈值非法: {self.missing_ratio!r}")


@dataclass(frozen=True, kw_only=True)
class PairGateResult:
    db_symbol: str
    lake_pair: str
    exchange: str
    market_type: str
    verdict: str
    reason_code: str | None
    metrics: dict[str, Any]

    def document(self) -> dict[str, Any]:
        return {
            "db_symbol": self.db_symbol,
            "lake_pair": self.lake_pair,
            "verdict": self.verdict,
            "reason_code": self.reason_code,
            "metrics": self.metrics,
        }


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
        status = _backfill_status(conn, exchange, db_symbol, window_start, window_end)
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

    rows, first, last = _row_bounds(conn, source_table, exchange, db_symbol, start, end)
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

    duplicates = _duplicate_keys(conn, source_table, exchange, db_symbol, start, end)
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

    aggregates = _aggregate_mismatch(conn, exchange, start, end)
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


def record_verdicts(
    conn,
    results: Iterable[PairGateResult],
    *,
    universe_id: str,
    hostname: str | None = None,
    judged_at: datetime | None = None,
    commit: bool = True,
) -> int:
    """只追加写判定记录（通过与失败同样保留）。"""
    host = hostname or socket.gethostname()
    moment = judged_at or datetime.now(UTC)
    payload = [
        (
            universe_id,
            result.exchange,
            result.market_type,
            result.db_symbol,
            result.lake_pair,
            result.verdict,
            result.reason_code,
            json.dumps(result.metrics, sort_keys=True, ensure_ascii=False),
            moment,
            host,
        )
        for result in results
    ]
    if not payload:
        return 0
    with conn.cursor() as cur:
        for values in payload:
            cur.execute(_INSERT_SQL, values)
    if commit:
        conn.commit()
    return len(payload)


def current_verdicts(conn, *, universe_id: str | None = None) -> dict[str, PairGateResult]:
    """每个 pair 的最新判定（准入状态真相源）。"""
    where = "WHERE universe_id = %s" if universe_id else ""
    params: tuple[Any, ...] = (universe_id,) if universe_id else ()
    with conn.cursor() as cur:
        cur.execute(_CURRENT_SQL.format(where=where), params)
        rows = cur.fetchall()
    out: dict[str, PairGateResult] = {}
    for row in rows:
        metrics = row[7]
        if isinstance(metrics, str):
            metrics = json.loads(metrics)
        out[str(row[4])] = PairGateResult(
            db_symbol=str(row[3]),
            lake_pair=str(row[4]),
            exchange=str(row[1]),
            market_type=str(row[2]),
            verdict=str(row[5]),
            reason_code=None if row[6] is None else str(row[6]),
            metrics=dict(metrics or {}),
        )
    return out


def admitted_pairs(conn, *, universe_id: str | None = None) -> frozenset[str]:
    """准入集合：判定为 ACTIVE 的 `lake_pair`（导出清单的交集之一）。"""
    return frozenset(
        pair
        for pair, result in current_verdicts(conn, universe_id=universe_id).items()
        if result.verdict == VERDICT_ACTIVE
    )


def export_admitted(conn, at: datetime, *, universe_id: str | None = None) -> frozenset[str]:
    """导出侧准入集合 = 台账可交易 ∩ 质量门 ACTIVE（`FR-006`）。"""
    from alphamill.data_bridge.universe.membership import universe_at

    return admitted_pairs(conn, universe_id=universe_id) & universe_at(conn, at)


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


def _backfill_status(
    conn, exchange: str, db_symbol: str, window_start: datetime, window_end: datetime
) -> str | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT status FROM backfill_progress
            WHERE exchange = %s AND symbol = %s AND timeframe = '1m'
              AND target_start = %s AND target_end = %s
            """,
            (exchange, db_symbol, window_start, window_end),
        )
        row = cur.fetchone()
    return None if not row else str(row[0])


def _row_bounds(conn, table: str, exchange: str, db_symbol: str, start: datetime, end: datetime):
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT count(*), min(time), max(time) FROM {table}"  # noqa: S608 - 表名来自受控参数
            " WHERE exchange = %s AND symbol = %s AND time >= %s AND time < %s",
            (exchange, db_symbol, start, end),
        )
        row = cur.fetchone()
    return int(row[0]), row[1], row[2]


def _duplicate_keys(
    conn, table: str, exchange: str, db_symbol: str, start: datetime, end: datetime
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT count(*) FROM (
                SELECT exchange, symbol, time FROM {table}
                WHERE exchange = %s AND symbol = %s AND time >= %s AND time < %s
                GROUP BY exchange, symbol, time HAVING count(*) > 1
            ) dup
            """,  # noqa: S608 - 表名来自受控参数
            (exchange, db_symbol, start, end),
        )
        return int(cur.fetchone()[0])


def _aggregate_mismatch(conn, exchange: str, start: datetime, end: datetime) -> dict[str, Any]:
    """连续聚合与 1m 基表按桶重算精确一致（差得不多也不放行）。"""
    out: dict[str, Any] = {}
    with conn.cursor() as cur:
        for view, bucket in AGGREGATES.items():
            cur.execute(
                f"SELECT count(*) FROM {view}"  # noqa: S608 - 视图名来自模块常量
                " WHERE exchange = %s AND bucket >= %s AND bucket < %s",
                (exchange, start, end),
            )
            view_rows = int(cur.fetchone()[0])
            cur.execute(
                f"""
                SELECT count(*) FROM (
                    SELECT symbol, time_bucket('{bucket}', time) AS b
                    FROM ohlcv_1m
                    WHERE exchange = %s AND time >= %s AND time < %s
                    GROUP BY symbol, b
                ) t
                """,  # noqa: S608 - 桶宽来自模块常量
                (exchange, start, end),
            )
            base_buckets = int(cur.fetchone()[0])
            out[view] = {
                "rows": view_rows,
                "base_buckets": base_buckets,
                "match": view_rows == base_buckets,
            }
    return out
