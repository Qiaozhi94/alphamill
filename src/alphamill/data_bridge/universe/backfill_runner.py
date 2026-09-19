"""分批回填编排：批次切分、断点续跑、逐 pair 隔离与 `BackfillRun` 落盘。

（`FR-003` / `DR-003` / `NFR-002` / `AC-003` / `AC-010` / T013 / T014）

三条结构性保证：

1. **未冻结不得驱动**：编排入口先 `require_frozen()`（`FR-002` 场景：未冻结即非零拒绝）；
2. **断点续跑**：每写完一个 pair 就把 `BackfillRun` 落盘；重跑同一 run 时**跳过已完成
   （completed/unavailable）的 pair**，未完成的 pair 由 `backfill_progress` 表的
   `next_since` 继续（幂等 upsert，重跑不产生重复行）；
3. **失败隔离**：单 pair 失败只记该 pair 的 `status=failed`、断点位置与错误分类，
   其他 pair 继续跑完。
"""

from __future__ import annotations

import json
import socket
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alphamill.data_bridge import paths
from alphamill.data_bridge.collector import historical_backfill as backfill
from alphamill.data_bridge.collector.backfill_progress import current_cursor
from alphamill.data_bridge.universe.canonical import utc_iso
from alphamill.data_bridge.universe.definition import UniverseDef, require_frozen
from alphamill.data_bridge.universe.errors import BackfillIncompleteError, WindowError
from alphamill.data_bridge.universe.storage import atomic_create

SCHEMA_VERSION = 1
DEFAULT_BATCH_SPLIT = 30
_RUN_FILE = "run.json"
_DONE_STATUSES = frozenset({backfill.STATUS_COMPLETED, backfill.STATUS_UNAVAILABLE})
EventSink = Callable[[str, dict[str, Any]], None]


@dataclass(frozen=True, kw_only=True)
class PairPlan:
    """一个待回填 pair 的计划：批次只影响时序，不影响 `universe_id`。"""

    db_symbol: str
    lake_pair: str
    rank: int | None
    listed_at: str | None

    def payload(self) -> dict[str, Any]:
        return {
            "db_symbol": self.db_symbol,
            "lake_pair": self.lake_pair,
            "rank": self.rank,
            "listed_at": self.listed_at,
        }


@dataclass(frozen=True, kw_only=True)
class BackfillRun:
    """`DR-003` 的运行记录：目标集合、窗口、限速参数、逐 pair 结果、hostname、起止。"""

    run_id: str
    universe_id: str
    batch: int | None
    window_start: str
    window_end: str
    rate_limit: dict[str, Any]
    hostname: str
    started_at: str
    pairs: tuple[dict[str, Any], ...]
    finished_at: str | None = None

    def document(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_id,
            "universe_id": self.universe_id,
            "batch": self.batch,
            "window": {"start": self.window_start, "end": self.window_end},
            "rate_limit": self.rate_limit,
            "hostname": self.hostname,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "pairs": list(self.pairs),
        }

    def with_outcome(self, outcome: dict[str, Any]) -> BackfillRun:
        merged = [item for item in self.pairs if item["db_symbol"] != outcome["db_symbol"]]
        merged.append(outcome)
        merged.sort(key=lambda item: str(item["db_symbol"]))
        return _replace(self, pairs=tuple(merged))

    def finished(self) -> BackfillRun:
        return _replace(self, finished_at=utc_iso(datetime.now(UTC)))

    def pending(self) -> tuple[str, ...]:
        return tuple(
            item["db_symbol"] for item in self.pairs if item.get("status") not in _DONE_STATUSES
        )

    def plans(self) -> tuple[PairPlan, ...]:
        return tuple(
            PairPlan(
                db_symbol=str(item["db_symbol"]),
                lake_pair=str(item["lake_pair"]),
                rank=None if item.get("rank") is None else int(item["rank"]),
                listed_at=None if item.get("listed_at") is None else str(item["listed_at"]),
            )
            for item in self.pairs
        )

    def failed_pairs(self) -> tuple[str, ...]:
        return tuple(
            item["db_symbol"] for item in self.pairs if item.get("status") == backfill.STATUS_FAILED
        )


def _replace(run: BackfillRun, **changes: Any) -> BackfillRun:
    payload = {
        "run_id": run.run_id,
        "universe_id": run.universe_id,
        "batch": run.batch,
        "window_start": run.window_start,
        "window_end": run.window_end,
        "rate_limit": run.rate_limit,
        "hostname": run.hostname,
        "started_at": run.started_at,
        "pairs": run.pairs,
        "finished_at": run.finished_at,
    }
    payload.update(changes)
    return BackfillRun(**payload)


def plan_batch(
    definition: UniverseDef,
    *,
    batch: int | None = None,
    pairs: Sequence[str] | None = None,
    batch_split: int = DEFAULT_BATCH_SPLIT,
) -> tuple[PairPlan, ...]:
    """按成交额排名切分批次：批 1 = 前 `batch_split`（含现有 6 对），批 2 = 其余。"""
    selected = definition.selected
    if pairs is not None:
        wanted = {pair.strip() for pair in pairs if pair.strip()}
        unknown = sorted(wanted - {item.db_symbol for item in definition.candidates})
        if unknown:
            raise WindowError(f"以下 pair 不在宇宙定义内: {unknown}")
        return tuple(_plan(item) for item in selected if item.db_symbol in wanted)
    if batch is None:
        return tuple(_plan(item) for item in selected)
    if batch == 1:
        chosen = selected[:batch_split]
    elif batch == 2:
        chosen = selected[batch_split:]
    else:
        raise WindowError(f"批次只能是 1 或 2，得到 {batch!r}")
    return tuple(_plan(item) for item in chosen)


def run_window_check(start: datetime, end: datetime) -> None:
    if start.tzinfo is None or end.tzinfo is None:
        raise WindowError("回填窗口必须带时区（UTC）")
    if start >= end:
        raise WindowError(f"回填窗口非法：start({start}) 必须早于 end({end})")


def run_backfill_batch(
    *,
    universe_id: str,
    plans: Iterable[PairPlan],
    start: datetime,
    end: datetime,
    conn,
    lake_root: Path | None = None,
    reports_dir: Path | None = None,
    exchange_id: str | None = None,
    exchange=None,
    limiter=None,
    event_sink: EventSink | None = None,
    hostname: str | None = None,
    batch: int | None = None,
    resume_run_id: str | None = None,
) -> BackfillRun:
    """执行一批 pair；未冻结的宇宙、非法窗口与空批次都在启动期拒绝。"""
    run_window_check(start, end)
    definition = require_frozen(universe_id, lake_root)
    selected = tuple(plans)
    if not selected and resume_run_id is None:
        raise BackfillIncompleteError(f"universe {universe_id} 的本批目标为空，拒绝启动空跑")

    exchange_id = exchange_id or definition.criteria.exchange
    state: dict[str, BackfillRun] = {
        "run": load_run(resume_run_id, reports_dir)
        if resume_run_id
        else _initial_run(
            definition=definition,
            selected=selected,
            start=start,
            end=end,
            limiter=limiter,
            hostname=hostname or socket.gethostname(),
            batch=batch,
            now=datetime.now(UTC),
        )
    }
    _write_run(state["run"], reports_dir)

    pending = set(state["run"].pending())
    remaining = [plan for plan in state["run"].plans() if plan.db_symbol in pending]
    if not remaining:
        finished = state["run"].finished()
        _write_run(finished, reports_dir)
        return finished

    def on_outcome(outcome) -> None:
        payload = _outcome_payload(outcome, conn, exchange_id, start, end, remaining)
        state["run"] = state["run"].with_outcome(payload)
        _write_run(state["run"], reports_dir)
        _emit(event_sink, state["run"], payload)

    backfill.run_backfill(
        exchange_id=exchange_id,
        symbols=[plan.db_symbol for plan in remaining],
        start=start,
        end=end,
        conn=conn,
        exchange=exchange,
        limiter=limiter,
        on_outcome=on_outcome,
    )
    finished = state["run"].finished()
    _write_run(finished, reports_dir)
    return finished


def _emit(event_sink: EventSink | None, run: BackfillRun, payload: dict[str, Any]) -> None:
    if event_sink is None:
        return
    common = {
        "run_id": run.run_id,
        "lake_pair": payload.get("lake_pair"),
        "hostname": run.hostname,
    }
    if payload.get("status") == backfill.STATUS_FAILED:
        event_sink(
            "backfill.failed",
            {
                **common,
                "error_class": payload.get("error_class"),
                "retries": None,
                "last_cursor": payload.get("last_cursor"),
                "error": payload.get("error"),
            },
        )
        return
    event_sink(
        "backfill.progress",
        {
            **common,
            "rows": payload.get("rows"),
            "cursor": payload.get("last_cursor"),
            "status": payload.get("status"),
        },
    )


def _outcome_payload(
    outcome, conn, exchange_id: str, start: datetime, end: datetime, plans: Sequence[PairPlan]
) -> dict[str, Any]:
    plan = next((item for item in plans if item.db_symbol == outcome.db_symbol), None)
    cursor = outcome.last_cursor
    if cursor is None:
        cursor, _, _ = current_cursor(conn, exchange_id, outcome.db_symbol, start, end)
    return {
        "db_symbol": outcome.db_symbol,
        "lake_pair": plan.lake_pair if plan else None,
        "rank": plan.rank if plan else None,
        "status": outcome.status,
        "rows": outcome.rows,
        "last_cursor": None if cursor is None else utc_iso(cursor),
        "error": outcome.error,
        "error_class": outcome.error_class,
    }


def _initial_run(
    *,
    definition: UniverseDef,
    selected: Sequence[PairPlan],
    start: datetime,
    end: datetime,
    limiter,
    hostname: str,
    batch: int | None,
    now: datetime,
) -> BackfillRun:
    rate_limit: dict[str, Any] = {}
    if limiter is not None:
        policy = limiter.policy
        rate_limit = {
            "min_interval_seconds": policy.min_interval_seconds,
            "max_retries": policy.max_retries,
            "base_backoff_seconds": policy.base_backoff_seconds,
            "max_backoff_seconds": policy.max_backoff_seconds,
        }
    return BackfillRun(
        run_id=_run_id(definition.universe_id, batch, now),
        universe_id=definition.universe_id,
        batch=batch,
        window_start=utc_iso(start),
        window_end=utc_iso(end),
        rate_limit=rate_limit,
        hostname=hostname,
        started_at=utc_iso(now),
        pairs=tuple(
            {
                **plan.payload(),
                "status": "pending",
                "rows": 0,
                "last_cursor": None,
                "error": None,
                "error_class": None,
            }
            for plan in selected
        ),
    )


def _run_id(universe_id: str, batch: int | None, now: datetime) -> str:
    short = universe_id.split(":", 1)[-1][:12]
    return f"{short}-b{batch or 0}-{now.strftime('%Y%m%dT%H%M%SZ')}"


def run_dir(run_id: str, reports_dir: Path | None = None) -> Path:
    root = (
        Path(reports_dir) if reports_dir is not None else paths.REPO_ROOT / "reports" / "backfill"
    )
    return root / run_id


def load_run(run_id: str, reports_dir: Path | None = None) -> BackfillRun:
    """按 run_id 载入运行记录（断点续跑的入口）。"""
    path = run_dir(run_id, reports_dir) / _RUN_FILE
    document = json.loads(path.read_text(encoding="utf-8"))
    window = document["window"]
    return BackfillRun(
        run_id=str(document["run_id"]),
        universe_id=str(document["universe_id"]),
        batch=document["batch"],
        window_start=str(window["start"]),
        window_end=str(window["end"]),
        rate_limit=dict(document["rate_limit"]),
        hostname=str(document["hostname"]),
        started_at=str(document["started_at"]),
        pairs=tuple(document["pairs"]),
        finished_at=document.get("finished_at"),
    )


def _write_run(run: BackfillRun, reports_dir: Path | None) -> None:
    """运行记录是**可更新的运行态**（不是内容寻址 artifact）：逐 pair 落盘以保留断点。"""
    target = run_dir(run.run_id, reports_dir) / _RUN_FILE
    payload = json.dumps(run.document(), sort_keys=True, indent=2, ensure_ascii=False).encode()
    if target.is_file():
        target.write_bytes(payload)
        return
    atomic_create(target, payload)


def _plan(item) -> PairPlan:
    return PairPlan(
        db_symbol=item.db_symbol,
        lake_pair=item.lake_pair,
        rank=item.rank,
        listed_at=item.listed_at,
    )
