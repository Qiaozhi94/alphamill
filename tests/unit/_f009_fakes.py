"""F009 单元测试共用替身（不是测试文件，故以 `_` 前缀避免被 pytest 收集）。"""

from __future__ import annotations

import time


class FakeSignal:
    """最小 KronosRealSignal 替身：只暴露控制器依赖的三个面。"""

    def __init__(self, *, loaded=True, device="cpu"):
        self.loaded = loaded
        self.device = device
        self.load_calls = 0
        self.unload_calls = 0
        self.load_error: Exception | None = None
        self.unload_error: Exception | None = None
        self.load_delay = 0.0
        self.unload_delay = 0.0

    # --- 控制器依赖面 ---
    def status(self):
        return type("S", (), {"loaded": self.loaded, "device": self.device})()

    def eager_load(self) -> None:
        if self.loaded:
            return  # 复刻 _load_predictor 的早返回：已加载即幂等，不重复 from_pretrained
        self.load_calls += 1
        if self.load_delay:
            time.sleep(self.load_delay)
        if self.load_error is not None:
            raise self.load_error
        self.loaded = True

    def unload(self) -> None:
        self.unload_calls += 1
        if self.unload_delay:
            time.sleep(self.unload_delay)
        if self.unload_error is not None:
            self.loaded = getattr(self.unload_error, "discarded", False) is False
            raise self.unload_error
        self.loaded = False
