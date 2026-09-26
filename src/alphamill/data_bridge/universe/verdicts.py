"""准入判定记录与导出准入集合（`DR-004` / `FR-006` / T015 / T017）。

判定记录**只追加**（库侧触发器拒绝 UPDATE/DELETE），最新一条（`judged_at, id`）是准入状态
真相源；它与台账的可交易期区间相互独立——准入按**贸易符号**（`db_symbol`）判定，台账按
湖内命名空间（`lake_pair`）记录，`export_admitted` 是两者之间的桥。
"""

from __future__ import annotations

import json
import logging
import socket
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from alphamill.data_bridge.universe.binding import Binding

logger = logging.getLogger(__name__)

VERDICT_ACTIVE = "ACTIVE"
VERDICT_QUARANTINED = "QUARANTINED"
VERDICT_INCOMPLETE = "INCOMPLETE"
VERDICTS = (VERDICT_ACTIVE, VERDICT_QUARANTINED, VERDICT_INCOMPLETE)

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


def export_admitted(
    conn,
    at: datetime,
    *,
    market_type: str | None = None,
    universe_id: str | None = None,
    bound_universe: Binding | None = None,
) -> frozenset[str]:
    """导出侧准入集合 = 台账可交易 ∩ 质量门 ACTIVE（`FR-006`）[∩ 被绑定宇宙入选集，F011]。

    准入记录按贸易符号（`db_symbol`）判定，而台账里同一个符号有 spot / perp 两条湖内
    命名空间，因此过滤要落到**被导出 dataset 的 market_type** 上：`market_type` 给定时
    只在台账里该命名空间的成员上取交集，缺省（None）等价于 `universe_at` 的直接交集。
    `bound_universe=None` 保持 F008 原语义；薄包装，口径见 `export_admission`。
    """
    return export_admission(
        conn, at, market_type=market_type, universe_id=universe_id, bound_universe=bound_universe
    ).admitted


@dataclass(frozen=True, kw_only=True)
class Admission:
    """导出准入（F011 `FR-001`/`FR-004`/`FR-005`）。

    `admitted`：不限日期产出分区的 `lake_pair`；`cutoffs`：已离开准入集合、判定 ACTIVE 的
    `lake_pair` → 截止日（含当日，之后不产出）；`dropped`：因绑定而剔除的 `db_symbol`；
    `universe_id`：被绑定版本（未绑定为 None）。
    """

    admitted: frozenset[str]
    cutoffs: dict[str, date] = field(default_factory=dict)
    dropped: tuple[str, ...] = ()
    universe_id: str | None = None

    def summary_fields(self, *, pair_scoped: bool = True) -> dict[str, Any]:
        """运行摘要的绑定留痕（`IR-002`）：被绑定版本 + 因绑定剔除的 db_symbol。

        非 pair 分区的 dataset（`pair_scoped=False`）没有单元格会因绑定被剔除，只记绑定（检视 R4）。
        """
        dropped = self.dropped if pair_scoped else ()
        return {"universe_id": self.universe_id, "dropped_by_universe": dropped}

    def covers(self, pair: str | None) -> bool:
        """该 pair 在本轮是否可能产出分区（准入或有截止日）。"""
        return pair in self.admitted or pair in self.cutoffs

    def allows(self, pair: str | None, day: str | date) -> bool:
        """单元格 `(pair, day)` 是否产出——增量与全量同一判据。"""
        if pair in self.admitted:
            return True
        cutoff = self.cutoffs.get(pair) if pair is not None else None
        if cutoff is None:
            return False
        return (date.fromisoformat(day) if isinstance(day, str) else day) <= cutoff


def export_admission(
    conn,
    at: datetime,
    *,
    market_type: str | None = None,
    universe_id: str | None = None,
    bound_universe: Binding | None = None,
) -> Admission:
    """唯一交集点：判定与台账各读一次，同一 `at`、同一 market_type 下同时产出三件结果。"""
    from alphamill.data_bridge.universe.membership import (
        load_membership,
        materialize_intervals,
        members_at,
    )

    active_symbols = {
        result.db_symbol
        for result in current_verdicts(conn, universe_id=universe_id).values()
        if result.verdict == VERDICT_ACTIVE
    }
    rows = [
        row
        for row in load_membership(conn)
        if row.db_symbol in active_symbols
        and (market_type is None or row.market_type == market_type)
    ]
    tradable = members_at(rows, at)
    if bound_universe is None:
        return Admission(
            admitted=frozenset(row.lake_pair for row in rows if row.lake_pair in tradable)
        )
    selected = bound_universe.selected_symbols()
    symbol_of = {row.lake_pair: row.db_symbol for row in rows}
    admitted = frozenset(pair for pair in tradable if symbol_of[pair] in selected)
    dropped = tuple(sorted({symbol_of[pair] for pair in tradable - admitted}))
    ended = _delisting_cutoffs(materialize_intervals(rows), tradable, at)
    cutoffs: dict[str, date] = {}
    for pair in sorted((tradable - admitted) | ended.keys()):
        found = [bound_universe.drop_cutoff(symbol_of[pair]), ended.get(pair)]
        cutoffs[pair] = min(item for item in found if item is not None)
    for symbol in dropped:
        logger.info(
            "绑定 %s 剔除 %s: not_in_universe_selection", bound_universe.universe_id, symbol
        )
    return Admission(
        admitted=admitted, cutoffs=cutoffs, dropped=dropped, universe_id=bound_universe.universe_id
    )


def exporter_admission(
    conn,
    end: date,
    market_type: str | None,
    admitted: set[str] | None,
    universe_filter: bool,
    bound_universe: Binding | None,
) -> Admission | None:
    """导出编排入口：显式集合优先（F008 `admitted=`），否则按过滤开关在窗口终点现算；
    都没有 ⇒ 不过滤。"""
    if admitted is not None:
        return Admission(admitted=frozenset(admitted))
    if not universe_filter:
        return None
    at = datetime.combine(end, datetime.min.time(), tzinfo=UTC)
    return export_admission(conn, at, market_type=market_type, bound_universe=bound_universe)


def _delisting_cutoffs(intervals, tradable: frozenset[str], at: datetime) -> dict[str, date]:
    """退市截止日：`at` 时已不可交易者，其最后一个已终止区间终点所在日（恰为 00:00 取前一日）。"""
    out: dict[str, date] = {}
    for interval in intervals:
        end = interval.valid_to
        if interval.lake_pair in tradable or end is None or end > at:
            continue
        day = (end - timedelta(microseconds=1)).date()
        out[interval.lake_pair] = max(day, out.get(interval.lake_pair, day))
    return out
