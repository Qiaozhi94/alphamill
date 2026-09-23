"""F009 停机期间的推理准入（unit，CI 常绿）——本 feature 的真正增量。

对应 spec FR-003 与 AC-003、design §5：`desired=stopped` 期间 `generate_signal()`
**不触碰** `_load_predictor()`，走 F004 既有兜底路径且来源不标 `kronos`。

没有这一条，`stop` 之后任一 `/predict` 都会把模型加载回来、把显存吃回去——
`stopped` 不可能稳定存在（检视 R1-002）。变异证明：去掉准入分支，
`_load_predictor` 调用次数从 0 变正，本文件判红。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from alphamill.kronos_service import kronos_real, server


def _rows(count: int = 120) -> list[dict]:
    base = datetime(2026, 9, 1, tzinfo=UTC)
    return [
        {
            "time": base + timedelta(minutes=i),
            "open": 100.0 + i,
            "high": 101.0 + i,
            "low": 99.0 + i,
            "close": 100.5 + i,
            "volume": 10.0 + i,
        }
        for i in range(count)
    ]


@pytest.fixture
def stopped_signal(monkeypatch):
    """启用 real 模式但把期望态置为 stopped；记录 _load_predictor 是否被触碰。"""
    signal = kronos_real.KronosRealSignal()
    monkeypatch.setattr(signal, "enabled", True)
    calls: list[str] = []

    def _forbidden():
        calls.append("load")
        raise AssertionError("停机期间不得触碰 _load_predictor（FR-003）")

    monkeypatch.setattr(signal, "_load_predictor", _forbidden)
    signal.set_admission(lambda: False)
    return signal, calls


def test_generate_signal_never_loads_while_stopped(stopped_signal) -> None:
    signal, calls = stopped_signal

    payload = signal.generate_signal(_rows())

    assert calls == [], "停机期间模型不得被唤醒"
    assert payload["reason"] == kronos_real.LIFECYCLE_STOPPED_REASON
    assert set(payload) >= {"signal_type", "confidence", "expected_return", "reason"}


def test_repeated_requests_stay_on_fallback(stopped_signal) -> None:
    signal, calls = stopped_signal

    reasons = {signal.generate_signal(_rows())["reason"] for _ in range(5)}

    assert reasons == {kronos_real.LIFECYCLE_STOPPED_REASON}
    assert calls == []


def test_predict_endpoint_does_not_label_kronos_while_stopped(monkeypatch) -> None:
    """`/predict` 与 `/predict_batch` 共用 build_prediction：停机期间来源不标 kronos。"""
    monkeypatch.setattr(server.real_signal, "enabled", True)
    monkeypatch.setattr(server.real_signal, "_allow_load", lambda: False)
    monkeypatch.setattr(server, "latest_ohlcv", lambda **_: _rows())

    response = server.build_prediction(symbol="BTC/USDT", exchange="binance", limit=120)

    assert response.source == "placeholder", "停机期间不得虚标 kronos（F004 C002 同一纪律）"
    assert response.model == "placeholder", "未进模型不得回报权重路径"
    assert response.reason == kronos_real.LIFECYCLE_STOPPED_REASON


def test_admission_defaults_to_allowed() -> None:
    """未接控制面（mock / 裸用法）时准入默认放行，F004 既有行为不变。"""
    signal = kronos_real.KronosRealSignal()

    assert signal.allow_load() is True


def test_admission_follows_controller(monkeypatch) -> None:
    from _f009_fakes import FakeSignal

    from alphamill.kronos_service import lifecycle
    from alphamill.kronos_service.lifecycle_config import LifecycleConfig

    fake = FakeSignal()
    controller = lifecycle.LifecycleController(fake, LifecycleConfig(probe_mode="torch"))
    signal = kronos_real.KronosRealSignal()
    signal.set_admission(controller.allow_load)

    assert signal.allow_load() is True
    controller.stop()
    assert signal.allow_load() is False
    controller.restore()
    assert signal.allow_load() is True
