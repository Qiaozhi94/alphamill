"""磁盘余量启动期校验（`FR-003` / `AC-012` / T002 的代码侧闸门）。

回填是 1~2 周的长跑：跑到一半写满盘会让整批 pair 停在半途，因此**启动期**就要拒绝。
估算口径保守（按 F002 实测：631 万行 / 约 6 对 / 2 年窗口外推），宁可多留余量。
"""

from __future__ import annotations

import shutil
from pathlib import Path

from alphamill.data_bridge.universe.errors import InsufficientDiskError

BYTES_PER_ROW = 220  # 含 Parquet 压缩与副本的保守估值（F002 实测外推）
MINUTES_PER_DAY = 1440
MARGIN = 1.2


def estimate_rows(*, pairs: int, window_days: float, minutes_available_ratio: float = 1.0) -> int:
    """预估本批写入行数：pair 数 × 窗口分钟数 × 实际可得比例。"""
    if pairs < 0 or window_days < 0:
        raise InsufficientDiskError("pairs/window_days 不能为负")
    return int(pairs * window_days * MINUTES_PER_DAY * minutes_available_ratio)


def required_bytes(rows: int, *, bytes_per_row: int = BYTES_PER_ROW, margin: float = MARGIN) -> int:
    if rows < 0 or bytes_per_row <= 0 or margin < 1:
        raise InsufficientDiskError("required_bytes 参数非法")
    return int(rows * bytes_per_row * margin)


def free_bytes(path: str | Path) -> int:
    return shutil.disk_usage(str(Path(path))).free


def require_headroom(path: str | Path, needed_bytes: int, *, free: int | None = None) -> int:
    """余量不足即抛 `InsufficientDiskError`（启动期拒绝，绝不跑到一半再说）。"""
    available = free_bytes(path) if free is None else free
    if available < needed_bytes:
        raise InsufficientDiskError(
            f"磁盘余量不足：{Path(path)} 可用 {available} 字节 < 本批预估 {needed_bytes} 字节"
            "（含 1.2 倍余量）；先扩容或缩小批次再回填"
        )
    return available
