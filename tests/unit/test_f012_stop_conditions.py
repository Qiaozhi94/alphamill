"""F012 停止条件（AC-005）：配额、夜槽、信号标志与 GPU 排队取消出队（文档检视 D11/D25）。"""

from __future__ import annotations

import os
import signal
from datetime import UTC, datetime

import pytest

from alphamill.factor_factory.generators import gpu_slot
from alphamill.factor_factory.generators.gpu_slot import AcquireCancelled, GpuSlot, GpuSlotConfig
from alphamill.factor_factory.generators.stop_conditions import (
    RunInterrupted,
    StopController,
    install_signal_flags,
)
from alphamill.factor_factory.generators.vram import VramReading

NIGHT = datetime(2026, 9, 27, 16, 0, tzinfo=UTC)  # 上海 00:00，在 22:00–06:30 夜槽内
DAY = datetime(2026, 9, 27, 4, 0, tzinfo=UTC)  # 上海 12:00，夜槽外


def _config(timeout: int = 5) -> GpuSlotConfig:
    return GpuSlotConfig(
        vram_limit_gb=4.0,
        window_start="22:00",
        window_end="06:30",
        window_tz="Asia/Shanghai",
        queue_timeout_s=timeout,
    )


def _controller(flags, *, now: datetime, ignore_window: bool = False) -> StopController:
    return StopController(
        flags=flags,
        window_start="22:00",
        window_end="06:30",
        window_tz="Asia/Shanghai",
        ignore_window=ignore_window,
        clock=lambda: now,
    )


def test_quota_reached_is_reported_after_mark() -> None:
    with install_signal_flags() as flags:
        stop = _controller(flags, now=NIGHT)
        assert stop.check() is None
        stop.mark_quota()
        assert stop.check() == "quota_reached"
        assert stop.reason == "quota_reached"


def test_window_closed_stops_training_unless_offhours_allowed() -> None:
    with install_signal_flags() as flags:
        assert _controller(flags, now=DAY).check() == "window_closed"
        assert _controller(flags, now=DAY, ignore_window=True).check() is None


def test_sigterm_sets_interrupted_and_outranks_other_reasons() -> None:
    previous = signal.getsignal(signal.SIGTERM)
    with install_signal_flags() as flags:
        stop = _controller(flags, now=DAY)
        stop.mark_quota()
        os.kill(os.getpid(), signal.SIGTERM)
        assert flags.is_set()
        assert stop.check() == "interrupted"
        with pytest.raises(RunInterrupted) as info:
            stop.raise_if_interrupted()
        assert info.value.stop_reason == "interrupted"
    assert signal.getsignal(signal.SIGTERM) == previous, "处理器须在退出时恢复"


def test_reason_is_sticky_once_decided() -> None:
    with install_signal_flags() as flags:
        clock = {"now": NIGHT}
        stop = StopController(
            flags=flags,
            window_start="22:00",
            window_end="06:30",
            window_tz="Asia/Shanghai",
            ignore_window=False,
            clock=lambda: clock["now"],
        )
        stop.mark_quota()
        assert stop.check() == "quota_reached"
        clock["now"] = DAY
        assert stop.check() == "quota_reached"


def test_cancelled_waiter_leaves_the_queue_and_next_run_acquires(tmp_path, monkeypatch) -> None:
    """检视 D25：取消须先写 cancelled 终态再抛，否则死 run 永远占住队头、后续每晚都排队超时。"""
    monkeypatch.setattr(gpu_slot, "query_vram", lambda: VramReading(total_gb=8, free_gb=8))
    slot = GpuSlot(locks_dir=tmp_path, config=_config())
    held = slot.acquire("run-holder", now=NIGHT)
    assert held.event == "acquired"

    with pytest.raises(AcquireCancelled) as info:
        slot.acquire("run-cancelled", now=NIGHT, cancel=lambda: True)
    assert info.value.record.event == "cancelled"
    slot.release("run-holder", now=NIGHT)

    record = slot.acquire("run-next", now=NIGHT)

    assert record.event == "acquired"
    events = [(r.run_id, r.event) for r in slot.queue_records()]
    assert ("run-cancelled", "cancelled") in events
