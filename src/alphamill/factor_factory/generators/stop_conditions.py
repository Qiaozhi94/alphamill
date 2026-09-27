"""挖掘运行的停止判定（F012 `FR-002`/`FR-005`，design §1 第 5 行、§5）。

四种停止原因：`quota_reached`、`budget_exhausted`（由训练入口判定，不在这里）、`window_closed`、
`interrupted`。`StopController` 是唯一判定点，优先级 interrupted > window_closed > quota_reached，
一旦判定即固定（sticky）。信号处理器只置标志、不做 IO；在 `mine` 入口安装、退出时恢复原处理器。
"""

from __future__ import annotations

import signal
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Final

from alphamill.factor_factory.errors import FactorFactoryError
from alphamill.factor_factory.generators.gpu_slot import in_training_window

STOP_REASONS: Final = ("quota_reached", "budget_exhausted", "window_closed", "interrupted")
PARTIAL_REASONS: Final = frozenset({"window_closed", "interrupted"})


class RunInterrupted(FactorFactoryError):
    """检查点发现中断标志：调用方以 partial/interrupted 收尾（训练前被中断同样如此）。"""

    def __init__(self, stop_reason: str = "interrupted") -> None:
        self.stop_reason = stop_reason
        super().__init__(f"mining run stopped: {stop_reason}")


class SignalFlags:
    def __init__(self) -> None:
        self._event = threading.Event()

    def set(self, *_: object) -> None:
        self._event.set()

    def is_set(self) -> bool:
        return self._event.is_set()


@contextmanager
def install_signal_flags() -> Iterator[SignalFlags]:
    """SIGTERM/SIGINT 只置标志；退出时恢复原处理器（systemd 停止单元时走 partial 收尾）。"""
    flags = SignalFlags()
    previous = {sig: signal.signal(sig, flags.set) for sig in (signal.SIGTERM, signal.SIGINT)}
    try:
        yield flags
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


class StopController:
    def __init__(
        self,
        *,
        flags: SignalFlags,
        window_start: str,
        window_end: str,
        window_tz: str,
        ignore_window: bool,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._flags = flags
        self._window = (window_start, window_end, window_tz)
        self._ignore_window = ignore_window
        self._clock = clock or (lambda: datetime.now(UTC))
        self._quota = False
        self.reason: str | None = None

    def mark_quota(self) -> None:
        self._quota = True

    def check(self) -> str | None:
        """返回首个触发的停止原因；判定后固定不变。"""
        if self.reason is not None:
            return self.reason
        if self._flags.is_set():
            self.reason = "interrupted"
        elif not self._ignore_window and not in_training_window(
            self._clock(),
            window_start=self._window[0],
            window_end=self._window[1],
            window_tz=self._window[2],
        ):
            self.reason = "window_closed"
        elif self._quota:
            self.reason = "quota_reached"
        return self.reason

    def raise_if_interrupted(self) -> None:
        """训练前检查点：见中断标志即抛 `RunInterrupted`。"""
        if self._flags.is_set():
            self.reason = self.reason or "interrupted"
            raise RunInterrupted(self.reason)
