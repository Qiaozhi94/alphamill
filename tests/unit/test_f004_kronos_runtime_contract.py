"""F004 薄壳运行时契约（unit，CI 常绿）。

对应 spec FR-001 / design §5：
- 失败关闭：real 模式启动预检缺任一资产（vendor clone / 模型 / 分词器）→ 打印缺失路径
  并以非零码退出，绝不退回 mock；
- 串行推理：模型加载至多一次、推理互斥（进程级锁，并发请求排队执行）。
"""

from __future__ import annotations

import asyncio
import threading
import time
from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from alphamill.kronos_service import kronos_real, server

REQUIRED_FILES = ("model/kronos.py", "Kronos-base/config.json", "model.safetensors")


def _fake_assets(
    tmp_path, *, repo=True, model_cfg=True, model_weights=True, tok_cfg=True, tok_weights=True
):
    """按开关缺件的 fake 资产树：repo clone + 模型 + 分词器目录。"""
    repo_dir = tmp_path / "Kronos"
    (repo_dir / "model").mkdir(parents=True)
    if repo:
        (repo_dir / "model" / "kronos.py").write_text("# fake upstream\n", encoding="utf-8")
    for base, cfg, weights in (
        (tmp_path / "Kronos-base", model_cfg, model_weights),
        (tmp_path / "Kronos-Tokenizer-base", tok_cfg, tok_weights),
    ):
        base.mkdir()
        if cfg:
            (base / "config.json").write_text("{}", encoding="utf-8")
        if weights:
            (base / "model.safetensors").write_text("weights", encoding="utf-8")
    return repo_dir


def _make_signal(monkeypatch, tmp_path, **asset_flags) -> kronos_real.KronosRealSignal:
    repo_dir = _fake_assets(tmp_path, **asset_flags)
    monkeypatch.setenv("KRONOS_USE_REAL_MODEL", "true")
    monkeypatch.setenv("KRONOS_REPO_PATH", str(repo_dir))
    monkeypatch.setenv("KRONOS_MODEL_PATH", str(tmp_path / "Kronos-base"))
    monkeypatch.setenv("KRONOS_TOKENIZER_PATH", str(tmp_path / "Kronos-Tokenizer-base"))
    return kronos_real.KronosRealSignal()


def test_real_mode_preflight_fails_closed_without_assets(monkeypatch, tmp_path, capsys) -> None:
    """缺权重：预检报告缺失路径，startup 非零退出，实例保持未加载（不退回 mock）。"""
    signal = _make_signal(monkeypatch, tmp_path, model_weights=False)

    missing = signal.preflight()
    assert missing == [str(tmp_path / "Kronos-base" / "model.safetensors")]

    with pytest.raises(SystemExit) as excinfo:
        kronos_real.real_mode_startup(signal)
    assert excinfo.value.code != 0
    assert "model.safetensors" in capsys.readouterr().err
    assert signal.status().loaded is False


def test_real_mode_preflight_reports_each_missing_asset_kind(monkeypatch, tmp_path) -> None:
    """repo clone、模型与分词器的目录/必需文件缺失都要逐项报出。"""
    signal = _make_signal(
        monkeypatch, tmp_path, repo=False, model_cfg=False, tok_cfg=False, tok_weights=False
    )

    missing = signal.preflight()

    assert str(tmp_path / "Kronos" / "model" / "kronos.py") in missing
    assert str(tmp_path / "Kronos-base" / "config.json") in missing
    assert str(tmp_path / "Kronos-Tokenizer-base" / "config.json") in missing
    assert str(tmp_path / "Kronos-Tokenizer-base" / "model.safetensors") in missing


def test_real_mode_preflight_passes_with_complete_assets(monkeypatch, tmp_path) -> None:
    signal = _make_signal(monkeypatch, tmp_path)
    assert signal.preflight() == []


def test_real_mode_startup_exits_when_model_load_fails(monkeypatch, tmp_path, capsys) -> None:
    """预检通过但加载失败：同样非零退出并打印错误，不留可用中间态。"""
    signal = _make_signal(monkeypatch, tmp_path)

    def broken_load() -> None:
        raise RuntimeError("torchbroken")

    monkeypatch.setattr(signal, "_load_predictor", broken_load)
    with pytest.raises(SystemExit):
        kronos_real.real_mode_startup(signal)
    assert "torchbroken" in capsys.readouterr().err


def test_real_mode_startup_is_noop_for_mock(monkeypatch) -> None:
    """mock 模式（默认编排）启动钩子必须零接触：不触发预检与加载（NFR-001）。"""

    def _boom() -> None:
        raise AssertionError("mock 模式不应触发预检")

    monkeypatch.setattr(kronos_real.real_signal, "enabled", False)
    monkeypatch.setattr(kronos_real.KronosRealSignal, "preflight", _boom)
    monkeypatch.setattr(kronos_real.KronosRealSignal, "eager_load", _boom)
    kronos_real.real_mode_startup()


class _FakePredictor:
    """记录并发度的假 predictor：predict 慢执行并统计峰值并发。"""

    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0

    def predict(self, **_kwargs) -> pd.DataFrame:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        time.sleep(0.05)
        self.active -= 1
        return pd.DataFrame({"close": [100.0, 101.0, 102.0]})


def _rows(count: int) -> list[dict]:
    start = datetime(2026, 9, 1, tzinfo=UTC)
    return [
        {
            "time": start + timedelta(minutes=idx),
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0 + idx,
            "volume": 1.0,
        }
        for idx in range(count)
    ]


def test_predictor_loads_once_and_inference_serializes(monkeypatch) -> None:
    """并发推理：模型加载至多一次、推理互斥（请求排队，无并发进入 predictor）。"""
    signal = kronos_real.KronosRealSignal()
    fake = _FakePredictor()
    load_calls: list[int] = []
    errors: list[Exception] = []

    def slow_load():
        # 复刻真实 _load_predictor 的记忆化契约：登记 self._predictor 后复用。
        # 无锁时并发首请求会同时看到 None → 多次加载；有锁时只有首个请求真正加载。
        if signal._predictor is None:
            load_calls.append(1)
            time.sleep(0.05)  # 拉长加载窗口，放大并发首请求的加载竞态
            signal._predictor = fake
        return signal._predictor

    def run() -> None:
        try:
            signal.generate_signal(_rows(40))
        except Exception as exc:  # 收集线程内异常，不让断言被静默吞掉
            errors.append(exc)

    monkeypatch.setattr(signal, "_load_predictor", slow_load)
    threads = [threading.Thread(target=run) for _ in range(6)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert len(load_calls) == 1, f"模型被加载了 {len(load_calls)} 次"
    assert fake.max_active == 1, f"predictor 峰值并发 {fake.max_active}"


def _drive_lifespan() -> None:
    """直接驱动 server 的 lifespan（不经 TestClient——CI 不装 httpx；HTTP 层
    由容器集成测试覆盖）。"""
    asyncio.run(_consume_lifespan())


async def _consume_lifespan() -> None:
    async with server.lifespan(server.app):
        pass


def test_server_lifespan_invokes_startup_hook_in_real_mode(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(server, "healthcheck", lambda: {"total_rows": 1})
    monkeypatch.setattr(server.real_signal, "enabled", True)
    monkeypatch.setattr(kronos_real, "real_mode_startup", lambda: calls.append("startup"))

    _drive_lifespan()
    assert calls == ["startup"]  # 启动恰好一次，关停阶段不重复触发


def test_server_lifespan_skips_startup_in_mock_mode(monkeypatch) -> None:
    """mock 模式（默认编排）下 lifespan 全程不触发预检/加载——缺资产也不影响启动。

    门控在 real_mode_startup 内部（enabled 才动作），这里验证端到端可观察行为。
    """

    def _boom() -> None:
        raise AssertionError("mock 模式不应触发预检/加载")

    monkeypatch.setattr(server, "healthcheck", lambda: {"total_rows": 1})
    monkeypatch.setattr(server.real_signal, "enabled", False)
    monkeypatch.setattr(kronos_real.KronosRealSignal, "preflight", _boom)
    monkeypatch.setattr(kronos_real.KronosRealSignal, "eager_load", _boom)

    _drive_lifespan()
    assert server.health()["status"] == "ok"
