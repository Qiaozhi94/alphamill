"""T017 与 `AC-009`：准入联动（库追加 → artifact 发布 → 写准入记录）与导出清单过滤。

三步顺序是硬约束（design §5）：任一步失败就不进入下一步——顺序反了会出现「导出清单里
有、台账里没有」的 pair。导出清单本身没有独立实体：它就是「台账可交易 ∩ 质量门 ACTIVE」
的联合查询结果，由导出侧在 pair 选择处过滤（`admitted=` / `universe_filter=True`）。
"""

from __future__ import annotations

import socket
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from alphamill.data_bridge.universe import artifact as artifact_mod
from alphamill.data_bridge.universe.canonical import parse_utc
from alphamill.data_bridge.universe.definition import UniverseDef
from alphamill.data_bridge.universe.errors import QualityGateError
from alphamill.data_bridge.universe.membership import (
    MembershipRow,
    append_membership,
    load_membership,
    materialize_intervals,
)
from alphamill.data_bridge.universe.quality_gate import (
    VERDICT_ACTIVE,
    PairGateResult,
    gate_pairs,
    record_verdicts,
)

STEP_LEDGER = "ledger_appended"
STEP_ARTIFACT = "artifact_published"
STEP_ADMISSION = "admission_recorded"


@dataclass(frozen=True, kw_only=True)
class AdmissionOutcome:
    """一个 pair 的准入结果：三步各自的痕迹（`artifact_digest` 为空表示未发布）。"""

    db_symbol: str
    lake_pair: str
    verdict: str
    reason_code: str | None
    steps: tuple[str, ...]
    artifact_digest: str | None
    listed_at: datetime | None


def admit_pair(
    conn,
    *,
    definition: UniverseDef,
    result: PairGateResult,
    lake_root: Path | None = None,
    hostname: str | None = None,
    listed_at: datetime | None = None,
    start: datetime | None = None,
) -> AdmissionOutcome:
    """单 pair 准入：库追加 → artifact 发布 → 写准入记录；QUARANTINED 只记判定。"""
    steps: list[str] = []
    if result.verdict != VERDICT_ACTIVE:
        record_verdicts(conn, [result], universe_id=definition.universe_id, hostname=hostname)
        steps.append(STEP_ADMISSION)
        return AdmissionOutcome(
            db_symbol=result.db_symbol,
            lake_pair=result.lake_pair,
            verdict=result.verdict,
            reason_code=result.reason_code,
            steps=tuple(steps),
            artifact_digest=None,
            listed_at=listed_at,
        )

    valid_from = listed_at or _candidate_listed_at(definition, result.db_symbol) or start
    if valid_from is None:
        raise QualityGateError(
            f"无法确定 {result.db_symbol} 的 valid_from（既无上市时间也无窗口起点）"
        )

    # 步骤 1：库追加（可交易期事实；退出用追加 delisted 行表达，不改写历史）。
    # 同一 db_symbol 写**两条湖内命名空间**：研究数据集 ohlcv_1m 是 spot（`BTC-USDT`），
    # derivatives_* 是 perp（`BTC-USDT-PERP`）；F003 的张量掩码按 lake_pair 过滤，
    # 少一条就会让对应数据集的分区被整片掩掉。
    pending = _pending_membership_rows(
        conn, _membership_rows(result, valid_from, definition.universe_id)
    )
    if pending:
        append_membership(conn, pending)
    steps.append(STEP_LEDGER)

    # 步骤 2：artifact 发布（库是真相源，湖内是它的内容寻址快照）
    digest, _path = artifact_mod.publish_artifact(
        materialize_intervals(load_membership(conn)), lake_root
    )
    steps.append(STEP_ARTIFACT)

    # 步骤 3：写准入记录（准入状态真相源，与台账区间相互独立）
    record_verdicts(conn, [result], universe_id=definition.universe_id, hostname=hostname)
    steps.append(STEP_ADMISSION)
    return AdmissionOutcome(
        db_symbol=result.db_symbol,
        lake_pair=result.lake_pair,
        verdict=result.verdict,
        reason_code=result.reason_code,
        steps=tuple(steps),
        artifact_digest=digest,
        listed_at=valid_from,
    )


def gate_and_admit(
    conn,
    *,
    definition: UniverseDef,
    window_start: datetime,
    window_end: datetime,
    pairs: Sequence[str] | None = None,
    lake_root: Path | None = None,
    hostname: str | None = None,
    thresholds=None,
    require_backfill_complete: bool = True,
) -> list[AdmissionOutcome]:
    """对目标 pair 跑门禁并逐 pair 准入（通过者走三步，失败者只记判定）。"""
    chosen = _selected(definition, pairs)
    listed = {item.db_symbol: _parse_listed(item.listed_at) for item in definition.selected}
    results = gate_pairs(
        conn,
        pairs=chosen,
        exchange=definition.criteria.exchange,
        market_type=definition.criteria.market_type,
        window_start=window_start,
        window_end=window_end,
        listed_at={k: v for k, v in listed.items() if v is not None},
        thresholds=thresholds,
        require_backfill_complete=require_backfill_complete,
    )
    return [
        admit_pair(
            conn,
            definition=definition,
            result=result,
            lake_root=lake_root,
            hostname=hostname or socket.gethostname(),
            listed_at=listed.get(result.db_symbol),
            start=window_start,
        )
        for result in results
    ]


def _membership_rows(
    result: PairGateResult, valid_from: datetime, universe_id: str
) -> list[MembershipRow]:
    from alphamill.data_bridge import symbol_map

    rows: list[MembershipRow] = []
    for market_type in ("spot", "perp"):
        lake_pair, _ = symbol_map.derive_pairs(result.db_symbol, market_type)
        rows.append(
            MembershipRow(
                exchange=result.exchange,
                market_type=market_type,
                db_symbol=result.db_symbol,
                lake_pair=lake_pair,
                valid_from=valid_from,
                reason="listed",
                universe_id=universe_id,
            )
        )
    return rows


def _selected(
    definition: UniverseDef, pairs: Sequence[str] | None
) -> tuple[tuple[str, str, str], ...]:
    rows = [
        (item.db_symbol, item.lake_pair, item.excluded_reason or "selected")
        for item in definition.selected
    ]
    if pairs is None:
        return tuple(rows)
    wanted = {pair.strip() for pair in pairs if pair.strip()}
    unknown = sorted(wanted - {item.db_symbol for item in definition.candidates})
    if unknown:
        raise QualityGateError(f"以下 pair 不在宇宙定义内: {unknown}")
    return tuple(row for row in rows if row[0] in wanted)


def _candidate_listed_at(definition: UniverseDef, db_symbol: str) -> datetime | None:
    for item in definition.candidates:
        if item.db_symbol == db_symbol:
            return _parse_listed(item.listed_at)
    return None


def _parse_listed(value: str | None) -> datetime | None:
    if not value:
        return None
    return parse_utc(value, field="candidate.listed_at")


def all_admitted(results: Iterable[AdmissionOutcome]) -> tuple[str, ...]:
    return tuple(item.db_symbol for item in results if item.verdict == VERDICT_ACTIVE)

def _pending_membership_rows(conn, rows: list[MembershipRow]) -> list[MembershipRow]:
    """与台账对账，去掉 `(lake_pair, market_type, valid_from)` 已存在的行。

    `append_membership` 的幂等**由调用方负责**（见其 docstring），而库侧触发器会拒绝
    同一 pair 的重复/回填 `valid_from`：门禁复跑（同一 pair 同一上市日）会在第二步
    追加时被拒（2026-09-24 实测：第二次 `gate` 在 BTC 上报「追加序非法」而整轮中断）。
    已存在的成员关系本就是同一个事实，跳过追加即可；真正的变更（退市、改上市日）
    走新区间。
    """
    existing: set[tuple[str, str, datetime]] = set()
    for lake_pair in {row.lake_pair for row in rows}:
        existing.update(
            (row.lake_pair, row.market_type, row.valid_from)
            for row in load_membership(conn, lake_pair=lake_pair)
        )
    return [row for row in rows if (row.lake_pair, row.market_type, row.valid_from) not in existing]
