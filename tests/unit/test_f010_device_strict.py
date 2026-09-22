"""F010 设备解析严格分支（unit，CI 常绿，假 torch，不依赖 GPU）。

对应 spec FR-004 / NFR-004 / TR-001 与 AC-004 单元层、design §5：
- **显式** `KRONOS_DEVICE=cuda*` 而拿不到 CUDA（CPU wheel：`torch.version.cuda` 为空；
  或 `torch.cuda.is_available()` 为假）→ 加载入口抛错并点名原因，启动以非零码退出；
- 判断在 `_load_predictor()` 调用的 `_resolve_device()` 里：启动 eager load、F009 restore
  重载、`/predict` 惰性加载共用一个入口，任何路径都不得静默回落 cpu；
- `KRONOS_DEVICE` 未设置时保留既有宽松回落（开发机语义）；
- 加载成功后日志一行记录实际设备与 `torch.version.cuda`（TR-001）。
"""

from __future__ import annotations

import re
import sys
import types

import pytest

from alphamill.kronos_service import kronos_real


def _fake_assets(tmp_path):
    repo_dir = tmp_path / "Kronos"
    (repo_dir / "model").mkdir(parents=True)
    (repo_dir / "model" / "kronos.py").write_text("# fake upstream\n", encoding="utf-8")
    for base in (tmp_path / "Kronos-base", tmp_path / "Kronos-Tokenizer-base"):
        base.mkdir()
        (base / "config.json").write_text("{}", encoding="utf-8")
        (base / "model.safetensors").write_text("weights", encoding="utf-8")
    return repo_dir


class _Loader:
    calls: list[str]

    def __init__(self, calls: list[str]):
        self.calls = calls

    def from_pretrained(self, path: str) -> object:
        self.calls.append(path)
        return object()


def _install_fakes(monkeypatch, *, cuda_version, cuda_available, with_version=True):
    """装假 torch 与假 vendor model 模块；返回 from_pretrained 调用记录与 predictor 设备。"""
    cuda_ns = types.SimpleNamespace(is_available=lambda: cuda_available)
    torch_ns = types.SimpleNamespace(cuda=cuda_ns)
    if with_version:
        torch_ns.version = types.SimpleNamespace(cuda=cuda_version)
    monkeypatch.setitem(sys.modules, "torch", torch_ns)

    calls: list[str] = []
    predictor_devices: list[str] = []

    def _predictor(_model, _tokenizer, *, device, max_context):
        predictor_devices.append(device)
        return object()

    fake_model = types.SimpleNamespace(
        Kronos=_Loader(calls), KronosTokenizer=_Loader(calls), KronosPredictor=_predictor
    )
    monkeypatch.setitem(sys.modules, "model", fake_model)
    monkeypatch.setattr(sys, "path", [*sys.path])
    return calls, predictor_devices


def _make_signal(monkeypatch, tmp_path, device: str | None) -> kronos_real.KronosRealSignal:
    repo_dir = _fake_assets(tmp_path)
    monkeypatch.setenv("KRONOS_USE_REAL_MODEL", "true")
    monkeypatch.setenv("KRONOS_REPO_PATH", str(repo_dir))
    monkeypatch.setenv("KRONOS_MODEL_PATH", str(tmp_path / "Kronos-base"))
    monkeypatch.setenv("KRONOS_TOKENIZER_PATH", str(tmp_path / "Kronos-Tokenizer-base"))
    if device is None:
        monkeypatch.delenv("KRONOS_DEVICE", raising=False)
    else:
        monkeypatch.setenv("KRONOS_DEVICE", device)
    return kronos_real.KronosRealSignal()


def _load(signal: kronos_real.KronosRealSignal):
    with signal._lock:
        return signal._load_predictor()


@pytest.mark.parametrize(
    ("cuda_version", "cuda_available", "reason"),
    [
        (None, True, kronos_real.ERR_CPU_WHEEL),  # CPU wheel 镜像
        ("13.0", False, kronos_real.ERR_NO_CUDA_DEVICE),  # 容器内无设备
    ],
)
def test_explicit_cuda_without_cuda_raises(
    monkeypatch, tmp_path, cuda_version, cuda_available, reason
) -> None:
    signal = _make_signal(monkeypatch, tmp_path, "cuda")
    calls, _ = _install_fakes(monkeypatch, cuda_version=cuda_version, cuda_available=cuda_available)

    with pytest.raises(RuntimeError, match=re.escape(reason)):
        _load(signal)

    assert calls == [], "拿不到 CUDA 时不得开始加载权重"
    assert signal._predictor is None
    assert signal._device != "cuda:0"
    assert reason in (signal._load_error or ""), "失败原因须经 /health 的 error 字段可见"


def test_strict_branch_holds_on_every_reload(monkeypatch, tmp_path) -> None:
    """restore / 惰性加载再次进入加载入口时同样抛错，不因首次失败而回落 cpu。"""
    signal = _make_signal(monkeypatch, tmp_path, "cuda")
    calls, _ = _install_fakes(monkeypatch, cuda_version="13.0", cuda_available=False)

    for _ in range(2):
        with pytest.raises(RuntimeError, match=re.escape(kronos_real.ERR_NO_CUDA_DEVICE)):
            _load(signal)
    assert calls == []


def test_explicit_cuda_with_cuda_loads_on_gpu(monkeypatch, tmp_path, capsys) -> None:
    signal = _make_signal(monkeypatch, tmp_path, "cuda")
    _, devices = _install_fakes(monkeypatch, cuda_version="13.0", cuda_available=True)

    _load(signal)

    assert devices == ["cuda:0"]
    assert signal.status().device == "cuda:0"
    # TR-001：实际设备 + torch CUDA 版本进日志
    assert "[kronos-real] model loaded: device=cuda:0 torch_cuda=13.0" in capsys.readouterr().out


def test_explicit_cpu_stays_on_cpu_even_if_cuda_available(monkeypatch, tmp_path, capsys) -> None:
    signal = _make_signal(monkeypatch, tmp_path, "cpu")
    _, devices = _install_fakes(monkeypatch, cuda_version="13.0", cuda_available=True)

    _load(signal)

    assert devices == ["cpu"]
    assert "[kronos-real] model loaded: device=cpu torch_cuda=13.0" in capsys.readouterr().out


def test_explicit_unknown_device_is_rejected(monkeypatch, tmp_path) -> None:
    """显式给了既非 cpu 也非 cuda* 的值：拒绝而不是悄悄按 cpu 跑。"""
    signal = _make_signal(monkeypatch, tmp_path, "mps")
    calls, _ = _install_fakes(monkeypatch, cuda_version=None, cuda_available=False)

    with pytest.raises(RuntimeError, match=re.escape(kronos_real.ERR_UNKNOWN_DEVICE)):
        _load(signal)
    assert calls == []


@pytest.mark.parametrize(("cuda_available", "expected"), [(False, "cpu"), (True, "cuda:0")])
def test_unset_device_keeps_lenient_fallback(
    monkeypatch, tmp_path, cuda_available, expected
) -> None:
    """未设置 KRONOS_DEVICE：既有宽松语义（开发机），且不要求 torch.version 存在。"""
    signal = _make_signal(monkeypatch, tmp_path, None)
    _, devices = _install_fakes(
        monkeypatch, cuda_version=None, cuda_available=cuda_available, with_version=False
    )

    _load(signal)

    assert devices == [expected]


def test_startup_exits_nonzero_when_explicit_cuda_unavailable(
    monkeypatch, tmp_path, capsys
) -> None:
    """启动路径：严格分支抛错 → real_mode_startup 非零退出，stderr 点名原因。"""
    signal = _make_signal(monkeypatch, tmp_path, "cuda")
    _install_fakes(monkeypatch, cuda_version=None, cuda_available=False)

    with pytest.raises(SystemExit) as excinfo:
        kronos_real.real_mode_startup(signal)

    assert excinfo.value.code == 1
    err = capsys.readouterr().err
    assert "[kronos-real] model load failed" in err
    assert kronos_real.ERR_CPU_WHEEL in err
    assert signal.status().loaded is False
