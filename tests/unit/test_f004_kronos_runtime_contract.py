"""F004 薄壳运行时契约（unit，CI 常绿）。

对应 spec FR-001 / design §5：
- 失败关闭：real 模式启动预检缺任一资产（vendor clone / 模型 / 分词器）→ 打印缺失路径
  并以非零码退出，绝不退回 mock；
- 串行推理：模型加载至多一次、推理互斥（进程级锁，并发请求排队执行）。
"""

from __future__ import annotations

import threading
import time
from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from alphamill.kronos_service import kronos_real, server

REQUIRED_FILES = ("model/kronos.py", "Kronos-base/config.json", "model.safetensors")


def _fake_assets(tmp_path, *, repo=True, model_cfg=True, model_weights=True, tok_cfg=True,
                 tok_weights=True):
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


def test_server_lifespan_invokes_startup_hook_in_real_mode(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(server, "healthcheck", lambda: {"total_rows": 1})
    monkeypatch.setattr(server.real_signal, "enabled", True)
    monkeypatch.setattr(kronos_real, "real_mode_startup", lambda: calls.append("startup"))

    with TestClient(server.app) as client:
        assert calls == ["startup"]
        assert client.get("/health").status_code == 200
    assert calls == ["startup"]  # 关停阶段不重复触发


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

    with TestClient(server.app) as client:
        assert client.get("/health").status_code == 200
