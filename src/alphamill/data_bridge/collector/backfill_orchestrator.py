"""回填编排层（从 `historical_backfill.py` 拆出，行数治理）：逐 pair 隔离、时间片与
`SymbolOutcome`。抓取细节仍在 `historical_backfill`，两者单向依赖（本模块 → 抓取层）。
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime

from alphamill.data_bridge.collector.backfill_progress import (
    current_cursor,
    ensure_progress_table,
)
from alphamill.data_bridge.collector.exchange_factory import build_exchange
from alphamill.data_bridge.collector.historical_backfill import (
    STATUS_COMPLETED,
    STATUS_DEFERRED,
    STATUS_FAILED,
    STATUS_UNAVAILABLE,
    BackfillDeadlineReached,
    fetch_symbol,
    logger,
)

__all__ = [
    "STATUS_COMPLETED",
    "STATUS_DEFERRED",
    "STATUS_FAILED",
    "STATUS_UNAVAILABLE",
    "BackfillDeadlineReached",
    "SymbolOutcome",
    "ensure_progress_table",
    "run_backfill",
]


@dataclass(frozen=True, kw_only=True)
class SymbolOutcome:
    """逐 pair 结果：失败也带断点位置与已完成行数（其他 pair 不受影响）。"""

    db_symbol: str
    status: str
    rows: int
    last_cursor: datetime | None
    error: str | None = None
    error_class: str | None = None


def run_backfill(
    *,
    exchange_id: str,
    symbols: Sequence[str],
    start: datetime,
    end: datetime,
    conn,
    exchange=None,
    limiter=None,
    should_stop: Callable[[], bool] | None = None,
    on_outcome: Callable[[SymbolOutcome], None] | None = None,
) -> list[SymbolOutcome]:
    """编排入口：逐 pair 执行、失败隔离、逐 pair 回调（进度事件与 `BackfillRun` 用）。"""
    ensure_progress_table(conn)
    owned = exchange is None
    client = exchange if exchange is not None else build_exchange(exchange_id)
    outcomes: list[SymbolOutcome] = []
    try:
        for symbol in symbols:
            if should_stop is not None and should_stop():
                # 时间片已到：剩余 pair 不再逐个进去（否则每个都要读一次进度、写一次 running），
                # 直接标 deferred 交给下一片
                cursor, _, done = current_cursor(conn, exchange_id, symbol, start, end)
                outcome = SymbolOutcome(
                    db_symbol=symbol,
                    status=STATUS_DEFERRED,
                    rows=done,
                    last_cursor=cursor,
                    error="deadline reached before start",
                )
                outcomes.append(outcome)
                if on_outcome is not None:
                    on_outcome(outcome)
                continue
            outcome = _run_one(
                exchange_id=exchange_id,
                exchange=client,
                conn=conn,
                symbol=symbol,
                start=start,
                end=end,
                limiter=limiter,
                should_stop=should_stop,
            )
            outcomes.append(outcome)
            if on_outcome is not None:
                on_outcome(outcome)
    finally:
        if owned:
            close = getattr(client, "close", None)
            if callable(close):
                close()
    return outcomes


def _run_one(
    *,
    exchange_id: str,
    exchange,
    conn,
    symbol: str,
    start: datetime,
    end: datetime,
    limiter,
    should_stop: Callable[[], bool] | None = None,
) -> SymbolOutcome:
    try:
        rows = fetch_symbol(
            exchange_id,
            exchange,
            conn,
            symbol,
            start,
            end,
            limiter=limiter,
            should_stop=should_stop,
        )
    except BackfillDeadlineReached as exc:
        cursor, _, done = current_cursor(conn, exchange_id, symbol, start, end)
        return SymbolOutcome(
            db_symbol=symbol, status=STATUS_DEFERRED, rows=done, last_cursor=cursor, error=str(exc)
        )
    except Exception as exc:  # noqa: BLE001 - 单 pair 失败必须隔离，其他 pair 继续
        logger.exception("symbol failed exchange=%s symbol=%s", exchange_id, symbol)
        conn.rollback()
        cursor, _, done = current_cursor(conn, exchange_id, symbol, start, end)
        return SymbolOutcome(
            db_symbol=symbol,
            status=STATUS_FAILED,
            rows=done,
            last_cursor=cursor,
            error=str(exc),
            error_class=type(exc).__name__,
        )
    cursor, status, done = current_cursor(conn, exchange_id, symbol, start, end)
    if status == "unavailable":
        return SymbolOutcome(
            db_symbol=symbol, status=STATUS_UNAVAILABLE, rows=done, last_cursor=cursor
        )
    return SymbolOutcome(
        db_symbol=symbol, status=STATUS_COMPLETED, rows=rows or done, last_cursor=cursor
    )
