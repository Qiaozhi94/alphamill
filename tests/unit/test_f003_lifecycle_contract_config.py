"""F003-R4-002 锁：生命周期契约测试模块不得有 mock 默认地址。

契约目标是 `kronos-signal-real`（执行机 GPU 实例）；`KRONOS_CONTROL_URL` 未设时
模块级 `CONTROL_URL` 必须为空串并使用例 skip——绝不回落到 mock 的 8001（XPASS
转正警报因此只可能打在真实实例上）。直接以文件位置加载被测模块，避免受本进程
已导入副本或收集期环境的影响。
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

MODULE = (
    pathlib.Path(__file__).resolve().parents[1] / "integration" / "test_f003_kronos_lifecycle.py"
)


def _load_fresh():
    spec = importlib.util.spec_from_file_location("_f003_lifecycle_under_test", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_control_url_has_no_default(monkeypatch) -> None:
    monkeypatch.setenv("ALPHAMILL_INTEGRATION", "1")
    monkeypatch.delenv("KRONOS_CONTROL_URL", raising=False)
    mod = _load_fresh()
    assert mod.CONTROL_URL == "", "未设 KRONOS_CONTROL_URL 时不得有默认地址（不许打 mock）"


def test_require_ready_skips_without_url(monkeypatch) -> None:
    monkeypatch.setenv("ALPHAMILL_INTEGRATION", "1")
    monkeypatch.delenv("KRONOS_CONTROL_URL", raising=False)
    mod = _load_fresh()
    with pytest.raises(pytest.skip.Exception, match="KRONOS_CONTROL_URL"):
        mod._require_ready()
