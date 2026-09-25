"""批次切分与窗口校验（从 `backfill_runner.py` 拆出，行数治理）。

批次只影响回填与准入的**时序**，不影响 `universe_id`——冻结的是完整的 40 对定义；
批 1 取成交额排名前 `batch_split`（含现有 6 对），批 2 取其余。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from alphamill.data_bridge.collector.backfill_progress import current_cursor
from alphamill.data_bridge.universe.canonical import utc_iso
from alphamill.data_bridge.universe.definition import UniverseDef
from alphamill.data_bridge.universe.errors import WindowError

DEFAULT_BATCH_SPLIT = 30


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


def plan_batch(
    definition: UniverseDef,
    *,
    batch: int | None = None,
    pairs: Sequence[str] | None = None,
    batch_split: int = DEFAULT_BATCH_SPLIT,
) -> tuple[PairPlan, ...]:
    """按成交额排名切分批次：批 1 = 前 `batch_split`（含现有 6 对），批 2 = 其余。

    `pairs` 只接受**入选**（`definition.selected`）的 pair：候选里被排除者（稳定币对、杠杆
    代币、跌出前 N……）此前能通过校验却在过滤后得到空批次，`gate` 会以「空列表 all() 为真」
    退出 0 报成功（检视 R1-015，fail-open）。排除原因随错误一并给出。
    """
    selected = definition.selected
    if pairs is not None:
        wanted = {pair.strip() for pair in pairs if pair.strip()}
        chosen = {item.db_symbol for item in selected}
        unknown = sorted(wanted - chosen)
        if unknown:
            reasons = {
                item.db_symbol: item.excluded_reason
                for item in definition.candidates
                if item.db_symbol in set(unknown)
            }
            raise WindowError(f"以下 pair 不在本宇宙的入选集内: {unknown}（排除原因: {reasons}）")
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


def resume_mismatch(run, universe_id: str, start: datetime, end: datetime, selected) -> str | None:
    """续跑参数与运行记录不一致时的说明（检视 R1-009）；一致返回 `None`。

    原先 `--resume-run-id` 只用 run 记录里的 pairs：换窗口/换批次续跑时已完成的 pair 不在
    pending → 一行不取 → `remaining` 为空直接 `finished()`，CLI 退出 0、分片脚本打印
    「本批全部完成」——把「参数打错」报成「跑完了」。`run` 按鸭子类型使用（避免与
    `backfill_runner` 形成循环依赖）。
    """
    if run.universe_id != universe_id:
        return f"universe_id {run.universe_id} != {universe_id}"
    if (run.window_start, run.window_end) != (utc_iso(start), utc_iso(end)):
        return f"窗口 {run.window_start}~{run.window_end} != {utc_iso(start)}~{utc_iso(end)}"
    wanted = {plan.db_symbol for plan in selected}
    have = {plan.db_symbol for plan in run.plans()}
    if wanted != have:
        return f"目标集合不一致：请求 {sorted(wanted)} vs 记录 {sorted(have)}"
    return None


def _plan(item) -> PairPlan:
    return PairPlan(
        db_symbol=item.db_symbol,
        lake_pair=item.lake_pair,
        rank=item.rank,
        listed_at=item.listed_at,
    )


def split_already_complete(
    conn, exchange_id: str, plans: list[PairPlan], start: datetime, end: datetime
):
    """库侧进度已 `complete` 的 pair 直接记为完成：数据已在库里（进度账本是断点续跑的
    存储契约），重拉 2 年窗口等于白跑几小时；真实覆盖仍由质量门逐项复核。"""
    done: list[tuple[PairPlan, Any, int, int]] = []
    todo: list[PairPlan] = []
    for plan in plans:
        cursor, status, ledger_rows = current_cursor(conn, exchange_id, plan.db_symbol, start, end)
        if status == "complete":
            rows = _count_window_rows(conn, exchange_id, plan.db_symbol, start, end)
            done.append((plan, cursor, rows, ledger_rows))
        else:
            todo.append(plan)
    return done, todo


def _count_window_rows(conn, exchange_id: str, symbol: str, start: datetime, end: datetime) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM ohlcv_1m"
            " WHERE exchange = %s AND symbol = %s AND time >= %s AND time < %s",
            (exchange_id, symbol, start, end),
        )
        return int(cur.fetchone()[0])
