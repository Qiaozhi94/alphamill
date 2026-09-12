"""F001 回填窗口配置的单一来源。

环境变量可显式覆盖仓库内的默认窗口；没有覆盖时从
``deployment/f001-backfill-window.env`` 读取。所有回填校验、测试和 supervisor
都应通过本模块或该 env 文件取值，避免跨层复制时间常量。
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from alphamill.data_bridge.collector.backfill_boundaries import (
    effective_derivative_window,
    listing_start_for,
    parse_unavailable_symbols,
)

WINDOW_FILE = Path(__file__).resolve().parents[1] / "deployment" / "f001-backfill-window.env"
DOTENV_FILE = WINDOW_FILE.parent / ".env"


def _file_values() -> dict[str, str]:
    if not WINDOW_FILE.is_file():
        return {}
    values: dict[str, str] = {}
    for raw_line in WINDOW_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _dotenv_values() -> dict[str, str]:
    if not DOTENV_FILE.is_file():
        return {}
    values: dict[str, str] = {}
    for raw_line in DOTENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _setting(name: str, default: str = "") -> str:
    return os.getenv(name, _file_values().get(name, _dotenv_values().get(name, default)))


def window_values() -> tuple[str, str]:
    defaults = _file_values()
    start = os.getenv("BACKFILL_WINDOW_START", defaults.get("BACKFILL_WINDOW_START", ""))
    end = os.getenv("BACKFILL_WINDOW_END", defaults.get("BACKFILL_WINDOW_END", ""))
    if not start or not end:
        raise RuntimeError("F001 回填窗口未配置 BACKFILL_WINDOW_START/BACKFILL_WINDOW_END")
    return start, end


def window_datetimes() -> tuple[datetime, datetime]:
    start_text, end_text = window_values()
    start = datetime.fromisoformat(start_text.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_text.replace("Z", "+00:00"))
    if start.tzinfo is None:
        start = start.replace(tzinfo=UTC)
    if end.tzinfo is None:
        end = end.replace(tzinfo=UTC)
    start = start.astimezone(UTC)
    end = end.astimezone(UTC)
    if start >= end:
        raise ValueError("F001 回填窗口必须满足 start < end")
    return start, end


def expected_minute_rows(start: datetime, end: datetime) -> int:
    """返回左闭右开分钟窗口应有的 K 线行数。"""
    seconds = (end - start).total_seconds()
    if seconds <= 0 or seconds % 60:
        raise ValueError("F001 回填窗口必须按整分钟对齐且 start < end")
    return int(seconds // 60)


def configured_symbols() -> list[str]:
    return [
        item.strip() for item in _setting("SYMBOLS", "BTC/USDT,ETH/USDT").split(",") if item.strip()
    ]


def configured_exchanges() -> list[str]:
    return [item.strip() for item in _setting("EXCHANGES", "binance").split(",") if item.strip()]


def listing_start(symbol: str, start: datetime) -> datetime:
    return listing_start_for(symbol, start, _setting("BACKFILL_SYMBOL_LISTING_STARTS"))


def unavailable_symbols() -> set[str]:
    return parse_unavailable_symbols(_setting("BACKFILL_UNAVAILABLE_SYMBOLS"))


def derivative_window(dataset: str, start: datetime, end: datetime) -> tuple[datetime, datetime]:
    max_days = int(_setting("DERIVATIVES_OPEN_INTEREST_MAX_DAYS", "0") or 0)
    return effective_derivative_window(dataset, start, end, max_days)
