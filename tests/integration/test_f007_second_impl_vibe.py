"""T026 外部对照（可选依赖）：Vibe-Trading `quantlib_call` 独立取证。

依赖缺失按 SOP §3 skip，不进 unit 硬门（`NFR-002` 的可复现性由仓内第二实现对照承担）。
"""

from __future__ import annotations

import importlib.util

import pytest

pytestmark = pytest.mark.integration


def test_vibe_trading_quantlib_is_optional_and_skips_cleanly():
    available = importlib.util.find_spec("vibe_trading_ai") is not None
    if not available:
        pytest.skip("vibe-trading-ai 未安装（可选依赖，按 SOP §3 skip，不进 unit 硬门）")
    module = __import__("vibe_trading_ai")
    assert module is not None
