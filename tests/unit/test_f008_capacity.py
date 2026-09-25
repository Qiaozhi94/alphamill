"""T002 / `AC-012` 的启动期磁盘闸门：`capacity` 的真实估算口径与「差 1 字节就拒绝」。

检视（变异测试）发现：`tests/unit/test_f008_cli_contract.py::test_backfill_rejects_insufficient_disk`
把 `cli.require_headroom` 整条猴补成「抛异常」，于是 `estimate_rows` / `required_bytes` /
`require_headroom`（含可注入的 `free=` 分支）零覆盖——把 `require_headroom` 换成恒不抛，
既有 16 个 CLI 契约用例仍全绿。本文件直接对这三个函数下断言，并让磁盘判定与真实磁盘解耦：
`free=` 与 `free_bytes` 猴补是仅有的余量来源，`shutil.disk_usage` 一次都不该被触达。

口径锚点（模块 docstring 的 F002 实测外推）：1 pair × 1 天 = 1440 行；6 pairs × 2 年 ≈ 631 万行。
"""

from __future__ import annotations

import pytest

from alphamill.data_bridge.universe import capacity
from alphamill.data_bridge.universe.capacity import (
    MARGIN,
    MINUTES_PER_DAY,
    estimate_rows,
    require_headroom,
    required_bytes,
)
from alphamill.data_bridge.universe.errors import InsufficientDiskError, UniverseError

FAKE_LAKE = "/nonexistent/alphamill-lake"  # 余量注入时绝不该被触碰：触碰即 OSError


# ---------- estimate_rows ----------


def test_estimate_rows_counts_pair_minutes_and_ratio() -> None:
    """行数 = pair 数 × 窗口分钟数 × 可得比例（缺省 1.0，即整窗都应有 K 线）。"""
    assert estimate_rows(pairs=1, window_days=1) == MINUTES_PER_DAY == 1440
    assert estimate_rows(pairs=2, window_days=3) == 2 * 3 * 1440
    assert estimate_rows(pairs=4, window_days=2, minutes_available_ratio=0.5) == 4 * 2 * 720
    assert estimate_rows(pairs=0, window_days=30) == 0


def test_estimate_rows_matches_f002_extrapolation_caliber() -> None:
    """docstring 里的实测外推（631 万行 / 约 6 对 / 2 年）必须是这个函数算出来的数。"""
    assert estimate_rows(pairs=6, window_days=730) == 6_307_200


def test_estimate_rows_is_monotonic_in_pairs_and_days() -> None:
    """多一对、多一天都不得让预估变少——保守口径是「宁可多留余量」的前提。"""
    by_pairs = [estimate_rows(pairs=n, window_days=30) for n in range(1, 9)]
    by_days = [estimate_rows(pairs=6, window_days=days) for days in (1, 2, 7, 30, 365, 730)]
    assert by_pairs == sorted(by_pairs) and len(set(by_pairs)) == len(by_pairs)
    assert by_days == sorted(by_days) and len(set(by_days)) == len(by_days)


@pytest.mark.parametrize(
    ("pairs", "window_days"),
    [(-1, 1), (1, -1), (-1, -1), (-6, 730)],
)
def test_estimate_rows_rejects_negative_parameters(pairs: int, window_days: float) -> None:
    with pytest.raises(InsufficientDiskError) as excinfo:
        estimate_rows(pairs=pairs, window_days=window_days)
    assert isinstance(excinfo.value, UniverseError)
    assert excinfo.value.code == "E_UNIVERSE_DISK"


# ---------- required_bytes ----------


def test_required_bytes_applies_margin_on_top_of_row_count() -> None:
    """字节数 = 行数 × 单行估值 × 余量系数；`MARGIN` 缺省 1.2（docstring 的 1.2 倍余量）。"""
    assert required_bytes(0) == 0
    assert required_bytes(1_000) == int(1_000 * capacity.BYTES_PER_ROW * MARGIN) == 264_000
    assert required_bytes(1_000, bytes_per_row=100, margin=2.0) == 200_000
    assert required_bytes(1_000, margin=1.0) == 220_000  # 恰好 1 倍余量是合法下界


def test_required_bytes_is_monotonic_in_rows() -> None:
    values = [required_bytes(rows) for rows in (0, 1, 1_440, 6_307_200, 10_000_000)]
    assert values == sorted(values) and len(set(values)) == len(values)


@pytest.mark.parametrize(
    ("rows", "bytes_per_row", "margin"),
    [(-1, 220, 1.2), (10, 0, 1.2), (10, -220, 1.2), (10, 220, 0.5), (10, 220, 0.0)],
)
def test_required_bytes_rejects_illegal_parameters(
    rows: int, bytes_per_row: int, margin: float
) -> None:
    with pytest.raises(InsufficientDiskError) as excinfo:
        required_bytes(rows, bytes_per_row=bytes_per_row, margin=margin)
    assert excinfo.value.code == "E_UNIVERSE_DISK"


# ---------- require_headroom ----------


def test_require_headroom_accepts_exactly_enough_free_space() -> None:
    """「刚好够」是放行边界：余量 == 本批预估时不得拒绝，且把可用量原样返回。"""
    needed = required_bytes(estimate_rows(pairs=6, window_days=730))
    assert needed == 1_665_100_800
    assert require_headroom(FAKE_LAKE, needed, free=needed) == needed


@pytest.mark.parametrize("short_by", [1, 2, 1000])
def test_require_headroom_rejects_shortfall_by_one_byte_or_more(short_by: int) -> None:
    """差 1 字节即拒绝：长跑写满盘的代价远大于多要求一点余量。"""
    needed = required_bytes(estimate_rows(pairs=6, window_days=730))
    available = needed - short_by
    with pytest.raises(InsufficientDiskError) as excinfo:
        require_headroom(FAKE_LAKE, needed, free=available)
    message = str(excinfo.value)
    assert excinfo.value.code == "E_UNIVERSE_DISK"
    assert str(available) in message and str(needed) in message
    assert FAKE_LAKE in message


def test_require_headroom_defaults_to_probing_free_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    """`free=None` 走真实探测分支：只在没有注入时读盘（猴补后同样不碰真实磁盘）。"""
    monkeypatch.setattr(capacity, "free_bytes", lambda path: 1_234)
    assert require_headroom(FAKE_LAKE, 1_000) == 1_234
    with pytest.raises(InsufficientDiskError):
        require_headroom(FAKE_LAKE, 4_321)
