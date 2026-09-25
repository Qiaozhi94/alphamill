"""point-in-time 宇宙台账的读写面（`FR-005` / `AC-007` / `AC-008` / T007 / T008）。

**写入只有一条路径**：`append_membership()`（INSERT-only）；库侧另有触发器兜底——
`UPDATE`/`DELETE` 直接拒绝、同一 pair 的 `valid_from` 必须严格递增。

台账存的是**状态迁移行**（`listed` / `delisted` / `initial_seed`），可交易区间由行派生：

    第 i 行的区间 = [valid_from_i, valid_to_i ?? valid_from_{i+1} ?? ∞)
    `delisted` 行只终止前一行，本身不贡献区间

`universe_at(T)` 两个口径（库侧查询与 artifact 并集判定）必须逐点一致——两者都从同一批
行派生，一致性由 `materialize_intervals()` 保证。
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from alphamill.data_bridge.universe.errors import MembershipError

REASONS = ("listed", "delisted", "initial_seed")
_TRADABLE_REASONS = frozenset({"listed", "initial_seed"})
_INSERT_SQL = """
INSERT INTO universe_membership (
    exchange, market_type, db_symbol, lake_pair,
    valid_from, valid_to, reason, universe_id, ingested_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, NOW()))
"""
_SELECT_SQL = """
SELECT exchange, market_type, db_symbol, lake_pair,
       valid_from, valid_to, reason, universe_id, ingested_at
FROM universe_membership
{where}
ORDER BY lake_pair, valid_from, id
"""


@dataclass(frozen=True, kw_only=True)
class MembershipRow:
    """一条状态迁移；`valid_to` 非空时用于一次性表达已闭合的历史区间。"""

    exchange: str
    market_type: str
    db_symbol: str
    lake_pair: str
    valid_from: datetime
    reason: str
    universe_id: str
    valid_to: datetime | None = None
    ingested_at: datetime | None = None


@dataclass(frozen=True, kw_only=True)
class TradabilityInterval:
    """派生后的可交易区间（半开区间，`valid_to=None` 表示当前有效）。"""

    lake_pair: str
    valid_from: datetime
    valid_to: datetime | None


def append_membership(conn, rows: Iterable[MembershipRow], *, commit: bool = True) -> int:
    """只追加写入（幂等由调用方按 `(lake_pair, valid_from)` 去重保证）。"""
    payload = [_row_tuple(row) for row in rows]
    if not payload:
        return 0
    with conn.cursor() as cur:
        for values in payload:
            cur.execute(_INSERT_SQL, values)
    if commit:
        conn.commit()
    return len(payload)


def load_membership(
    conn, *, lake_pair: str | None = None, market_type: str | None = None
) -> list[MembershipRow]:
    clauses: list[str] = []
    params: list[Any] = []
    if lake_pair:
        clauses.append("lake_pair = %s")
        params.append(lake_pair)
    if market_type:
        clauses.append("market_type = %s")
        params.append(market_type)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with conn.cursor() as cur:
        cur.execute(_SELECT_SQL.format(where=where), tuple(params))
        fetched = cur.fetchall()
    return [_row_from_db(row) for row in fetched]


def known_lake_pairs(conn) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT lake_pair FROM universe_membership")
        return {str(row[0]) for row in cur.fetchall()}


def universe_at(conn, at: datetime, *, market_type: str | None = None) -> frozenset[str]:
    """T 时刻可交易的成员集合（库侧入口；判定逻辑与 `members_at` 同一实现）。"""
    return members_at(load_membership(conn, market_type=market_type), at)


def members_at(rows: Iterable[MembershipRow], at: datetime) -> frozenset[str]:
    """状态规则：`valid_from <= T` 的最后一个状态属于可交易状态即为成员。"""
    moment = _require_utc(at, "universe_at(T)")
    latest: dict[str, MembershipRow] = {}
    for row in rows:
        if row.valid_from > moment:
            continue
        if row.valid_to is not None and row.valid_to <= moment:
            continue
        current = latest.get(row.lake_pair)
        if current is None or row.valid_from >= current.valid_from:
            latest[row.lake_pair] = row
    return frozenset(
        lake_pair for lake_pair, row in latest.items() if row.reason in _TRADABLE_REASONS
    )


def materialize_intervals(rows: Sequence[MembershipRow]) -> tuple[TradabilityInterval, ...]:
    """状态迁移行 → 可交易区间（按 pair 派生并合并相邻区间）。"""
    grouped: dict[str, list[MembershipRow]] = {}
    for row in rows:
        grouped.setdefault(row.lake_pair, []).append(row)

    intervals: list[TradabilityInterval] = []
    for lake_pair, group in grouped.items():
        ordered = sorted(group, key=lambda item: (item.valid_from, item.reason))
        derived: list[TradabilityInterval] = []
        for index, row in enumerate(ordered):
            if row.reason not in _TRADABLE_REASONS:
                continue
            end = row.valid_to
            if end is None and index + 1 < len(ordered):
                end = ordered[index + 1].valid_from
            derived.append(
                TradabilityInterval(lake_pair=lake_pair, valid_from=row.valid_from, valid_to=end)
            )
        intervals.extend(_merge_adjacent(derived))
    intervals.sort(key=lambda item: (item.lake_pair, item.valid_from))
    return tuple(intervals)


def seed_initial_members(
    conn,
    *,
    universe_id: str,
    pairs: Sequence[str],
    exchange: str,
    market_type: str,
    commit: bool = True,
) -> list[MembershipRow]:
    """为既有 pair 补 `initial_seed`：`valid_from` 取各自**实际数据起点**。

    缺失数据的 pair 一律判红而不是静默跳过——「凭空全程存在」与「悄悄没有台账」
    都是 PIT 查询的错误来源。
    """
    if not pairs:
        return []
    starts = _data_starts(conn, exchange=exchange, pairs=pairs)
    missing = [pair for pair in pairs if pair not in starts]
    if missing:
        raise MembershipError(
            f"以下 pair 在 {exchange} 没有任何 ohlcv 数据，无法确定 valid_from: {missing}"
        )
    rows = [
        MembershipRow(
            exchange=exchange,
            market_type=market_type,
            db_symbol=pair,
            lake_pair=_lake_pair_for(pair, market_type),
            valid_from=starts[pair],
            reason="initial_seed",
            universe_id=universe_id,
        )
        for pair in pairs
    ]
    append_membership(conn, rows, commit=commit)
    return rows


def _data_starts(conn, *, exchange: str, pairs: Sequence[str]) -> dict[str, datetime]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT symbol, min(time) FROM ohlcv_1m
            WHERE exchange = %s AND symbol = ANY(%s)
            GROUP BY symbol
            """,
            (exchange, list(pairs)),
        )
        return {
            str(symbol): _require_utc(moment, f"{symbol}.min(time)")
            for symbol, moment in cur.fetchall()
            if moment is not None
        }


def _lake_pair_for(db_symbol: str, market_type: str) -> str:
    from alphamill.data_bridge import symbol_map

    lake_pair, _ = symbol_map.derive_pairs(db_symbol, market_type)
    return lake_pair


def _merge_adjacent(intervals: list[TradabilityInterval]) -> list[TradabilityInterval]:
    merged: list[TradabilityInterval] = []
    for interval in intervals:
        previous = merged[-1] if merged else None
        if (
            previous is not None
            and previous.valid_to is not None
            and (previous.valid_to == interval.valid_from)
        ):
            previous = merged.pop()
            merged.append(
                TradabilityInterval(
                    lake_pair=previous.lake_pair,
                    valid_from=previous.valid_from,
                    valid_to=interval.valid_to,
                )
            )
            continue
        merged.append(interval)
    return merged


def _row_tuple(row: MembershipRow) -> tuple[Any, ...]:
    error = validate_row(row)
    if error:
        raise MembershipError(error)
    return (
        row.exchange,
        row.market_type,
        row.db_symbol,
        row.lake_pair,
        row.valid_from.astimezone(UTC),
        None if row.valid_to is None else row.valid_to.astimezone(UTC),
        row.reason,
        row.universe_id,
        None if row.ingested_at is None else row.ingested_at.astimezone(UTC),
    )


def validate_row(row: MembershipRow) -> str | None:
    """应用层单写封装的第一道闸（库侧触发器是第二道）。"""
    if row.reason not in REASONS:
        return f"reason 非法: {row.reason!r}（合法: {REASONS}）——准入/隔离原因码归质量门判定记录"
    for field in ("exchange", "market_type", "db_symbol", "lake_pair", "universe_id"):
        if not str(getattr(row, field) or "").strip():
            return f"{field} 不能为空"
    if row.valid_from.tzinfo is None:
        return "valid_from 必须带时区（UTC）"
    if row.valid_to is not None:
        if row.valid_to.tzinfo is None:
            return "valid_to 必须带时区（UTC）"
        if row.valid_to <= row.valid_from:
            return f"valid_to({row.valid_to}) 必须晚于 valid_from({row.valid_from})"
    return None


def _row_from_db(row: Sequence[Any]) -> MembershipRow:
    return MembershipRow(
        exchange=str(row[0]),
        market_type=str(row[1]),
        db_symbol=str(row[2]),
        lake_pair=str(row[3]),
        valid_from=_require_utc(row[4], "valid_from"),
        valid_to=None if row[5] is None else _require_utc(row[5], "valid_to"),
        reason=str(row[6]),
        universe_id=str(row[7]),
        ingested_at=None if row[8] is None else _require_utc(row[8], "ingested_at"),
    )


def _require_utc(value: Any, field: str) -> datetime:
    """aware UTC 强制：naive 输入判红而不是猜时区（与 F003/F007 消费面同一纪律）。"""
    if not isinstance(value, datetime):
        raise MembershipError(f"{field} 必须是 datetime，得到 {value!r}")
    if value.tzinfo is None:
        raise MembershipError(f"{field} 必须带时区（UTC），得到 naive {value!r}")
    return value.astimezone(UTC)
