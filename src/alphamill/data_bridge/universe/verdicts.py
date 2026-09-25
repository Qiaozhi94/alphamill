"""准入判定记录与导出准入集合（`DR-004` / `FR-006` / T015 / T017）。

判定记录**只追加**（库侧触发器拒绝 UPDATE/DELETE），最新一条（`judged_at, id`）是准入状态
真相源；它与台账的可交易期区间相互独立——准入按**贸易符号**（`db_symbol`）判定，台账按
湖内命名空间（`lake_pair`）记录，`export_admitted` 是两者之间的桥。
"""

from __future__ import annotations

import json
import socket
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

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
    conn, at: datetime, *, market_type: str | None = None, universe_id: str | None = None
) -> frozenset[str]:
    """导出侧准入集合 = 台账可交易 ∩ 质量门 ACTIVE（`FR-006`）。

    准入记录按贸易符号（`db_symbol`）判定，而台账里同一个符号有 spot / perp 两条湖内
    命名空间，因此过滤要落到**被导出 dataset 的 market_type** 上：`market_type` 给定时
    只在台账里该命名空间的成员上取交集，缺省（None）等价于 `universe_at` 的直接交集。
    """
    from alphamill.data_bridge.universe.membership import load_membership, members_at

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
    return frozenset(row.lake_pair for row in rows if row.lake_pair in members_at(rows, at))
