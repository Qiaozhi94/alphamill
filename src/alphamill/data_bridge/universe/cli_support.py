"""CLI 的支撑函数（从 `cli.py` 拆出，行数治理）：窗口解析、湖路径、上市时间注入、
连续聚合刷新与冻结人解析——都是「参数/环境 → 运行期输入」的转换，与子命令编排无关。
"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from alphamill.data_bridge.universe.errors import WindowError


def refresh_aggregates(conn, start: datetime, end: datetime) -> None:
    """门禁前先把连续聚合刷到窗口内：跨周期对账是「视图 vs 1m 基表按桶重算」的精确相等，
    新回填的数据没进物化视图时会假红（F001 口径本身也以刷新后的视图为准）。"""
    from alphamill.data_bridge.collector import historical_backfill as backfill_mod

    print(
        f"refreshing continuous aggregates for {start.isoformat()}..{end.isoformat()}",
        file=sys.stderr,
    )
    backfill_mod.refresh_aggregates(conn, start, end)


def apply_listing_starts(definition, plans, window_start: datetime) -> None:
    """把定义里的真实上市时间交给回填层：新 pair 晚上线时，不说清「什么时候才有 K 线」，
    交易所会在窗口起点返回空批次并被 F001 的边界检查判成 stalled（是窗口起点问题，不是缺失）。"""
    from alphamill.data_bridge.collector import historical_backfill as backfill_mod

    listed = {item.db_symbol: item.listed_at for item in definition.selected}
    entries = []
    for plan in plans:
        value = listed.get(plan.db_symbol) or plan.listed_at
        if not value:
            continue
        moment = parse_moment(value)
        if moment > window_start:
            entries.append(f"{plan.db_symbol}={moment.isoformat()}")
    backfill_mod.LISTING_STARTS = ",".join(entries)


def lake_root_for(args) -> Path:
    value = getattr(args, "lake_root", None)
    if value:
        return Path(value)
    from alphamill.data_bridge import paths

    return paths.lake_root()


def split_pairs(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_moment(text: str) -> datetime:
    normalized = text.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise WindowError(f"时间必须带时区（UTC ISO8601）: {text!r}")
    return parsed.astimezone(UTC)


def window_from_args(args) -> tuple[datetime, datetime]:

    start_text = args.start or os.getenv("BACKFILL_WINDOW_START") or os.getenv("BACKFILL_START")
    end_text = args.end or os.getenv("BACKFILL_WINDOW_END") or os.getenv("BACKFILL_END")
    if not start_text or not end_text:
        raise WindowError(
            "回填/门禁窗口未给出：用 --start/--end 指定，或设 BACKFILL_WINDOW_START/END"
        )
    return parse_moment(start_text), parse_moment(end_text)


def default_frozen_by() -> str:
    import getpass

    try:
        return getpass.getuser()
    except Exception:  # noqa: BLE001 - 取不到用户时给出可追溯的占位
        return "unknown"
