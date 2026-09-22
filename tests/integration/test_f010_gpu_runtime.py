"""F010 GPU 运行时集成：`kronos-signal-real` 叠加 GPU override 在执行机真实推理（执行机取证）。

对应 spec AC-004 执行机层 / AC-006 / AC-007 / AC-008 与 T018 旅程轨、design §8：
- AC-006：容器内 `torch.cuda.is_available()` 为真、arch list 覆盖 sm_89 与 sm_120（NFR-002），
  `/health` 报 `device=cuda:<n>`、`model_loaded=true`，启动日志含实际设备与 torch CUDA 版本；
- AC-007：`/predict` 返回 `source=kronos`，设备侧已用显存相对基线上升；
- AC-008：常驻显存峰值与架构 §7.1 白天行预算对照，证据记录 hostname / GPU 型号 / 读数；
- AC-004：显式 `KRONOS_DEVICE=cuda` 的两种拿不到 CUDA 情形（GPU 镜像不挂设备 / CPU 镜像）
  均非零退出、不重启、日志含对应文案、`/health` 不可达——预检须通过（挂真实资产），否则
  严格分支根本没执行；守护进程拒绝设备请求**不算**本条证据（R1-003）。

开关语义与 F004 一致：未设 `ALPHAMILL_INTEGRATION` 时 skip；设了而 docker / nvidia 运行时
不可达判红，不以 skip 代替证据。显存读数用 `nvidia-smi --query-gpu`（WSL2 下不列 GPU 进程，
NFR-005），是整卡读数：取证期间执行机不得有其他 GPU 负载（夜槽训练、bench 等）。

GPU 实例常驻时 `tests/integration/test_f004_real_profile.py`（断言 CPU 配置）会判红，属预期：
本文件 teardown 移除 real 容器，跑 F004 前按 `docs/alphamill-integration.md` §七 切回 CPU。
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
import requests

from alphamill.kronos_service.kronos_real import ERR_CPU_WHEEL, ERR_NO_CUDA_DEVICE

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_BASE = ["docker", "compose", "-f", "deployment/docker-compose.yml"]
COMPOSE_CPU = [*COMPOSE_BASE, "--profile", "kronos-real"]
COMPOSE_GPU = [
    *COMPOSE_BASE,
    "-f",
    "deployment/docker-compose.gpu.yml",
    "--profile",
    "kronos-real",
]
REAL_CONTAINER = "quant-kronos-signal-real"
GPU_IMAGE = "alphamill/kronos-signal-real:gpu"
BASE_URL = "http://127.0.0.1:8002"
CONTROL_URL = os.getenv("KRONOS_CONTROL_URL", BASE_URL)

# 架构 §7.1 白天行：Kronos 常驻显存预算。实测超出 → 在 §7.1 显式重标并同步此常量（AC-008），
# 不得只改这里。与 F003 `vram_limit_gb` 训练预算不是同一量（spec §7 R1-006）。
RESIDENT_VRAM_BUDGET_MIB = 3 * 1024
# 架构 §7.1 夜槽行 / F003 `vram_limit_gb` 缺省 6.0：卸载后整卡可用显存须达到的训练预算。
TRAINING_VRAM_BUDGET_MIB = 6 * 1024
REQUIRED_ARCHES = ("sm_89", "sm_120")  # 当前 RTX 4060 Laptop / 迁移目标 Blackwell

pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}

POLL_SECONDS = 300
PEAK_SAMPLES = 5


def _require_integration(reason_unavailable: str | None = None) -> None:
    if not INTEGRATION_REQUIRED:
        pytest.skip("GPU 集成需 ALPHAMILL_INTEGRATION=1 并在执行机取证（SOP §3）")
    if reason_unavailable:
        pytest.fail(reason_unavailable)


def _run(cmd: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)


def _nvidia_query(field: str) -> str:
    proc = _run(["nvidia-smi", f"--query-gpu={field}", "--format=csv,noheader,nounits"], 30)
    assert proc.returncode == 0, f"nvidia-smi 不可用: {proc.stderr}"
    return proc.stdout.strip().splitlines()[0].strip()


def _used_mib() -> int:
    return int(_nvidia_query("memory.used"))


def _free_mib() -> int:
    return int(_nvidia_query("memory.free"))


def _wait_for_health(prefix: str = "cuda") -> dict:
    deadline = time.monotonic() + POLL_SECONDS
    last_error: str | None = None
    while time.monotonic() < deadline:
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=5)
            if resp.status_code == 200:
                health = resp.json()
                if health.get("model_loaded") and str(health.get("device")).startswith(prefix):
                    return health
                last_error = f"health={health}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(5)
    pytest.fail(f"GPU 实例 {POLL_SECONDS}s 内未就绪: {last_error}")


def _predict() -> dict:
    resp = requests.get(f"{BASE_URL}/predict/BTC/USDT", params={"exchange": "binance"}, timeout=120)
    assert resp.status_code == 200, resp.text[:300]
    return resp.json()


def _compose_image(compose_cmd: list[str], service: str) -> str:
    """默认 CPU 构建的镜像名（<project>-<service>:latest），与 F004 同口径。"""
    cfg = _run([*compose_cmd, "config", "--format", "json"], timeout=60)
    assert cfg.returncode == 0, cfg.stderr
    return f"{json.loads(cfg.stdout)['name']}-{service}:latest"


def _require_nvidia_runtime() -> None:
    info = _run(["docker", "info", "--format", "{{json .Runtimes}}"], timeout=30)
    if info.returncode != 0:
        _require_integration(f"ALPHAMILL_INTEGRATION=1 但 docker 不可达: {info.stderr}")
    runtimes = sorted(json.loads(info.stdout or "{}"))
    if "nvidia" not in runtimes:
        _require_integration(f"docker 无 nvidia 运行时（Runtimes={runtimes}）：先完成 F010 T002")


@pytest.fixture(scope="module")
def gpu_instance() -> Iterator[dict]:
    """以 GPU override 构建并拉起 real 实例；基线显存在实例起来之前读取。"""
    _require_integration()
    _require_nvidia_runtime()

    _run([*COMPOSE_GPU, "rm", "-sf", "kronos-signal-real"], timeout=120)
    baseline = _used_mib()

    built = _run([*COMPOSE_GPU, "build", "kronos-signal-real"], timeout=3600)
    assert built.returncode == 0, f"GPU 镜像构建失败: {built.stderr[-2000:]}"
    up = _run([*COMPOSE_GPU, "up", "-d", "kronos-signal-real"], timeout=300)
    assert up.returncode == 0, f"GPU 实例拉起失败: {up.stderr[-2000:]}"

    health = _wait_for_health("cuda")
    yield {"baseline_mib": baseline, "health": health}

    _run([*COMPOSE_GPU, "rm", "-sf", "kronos-signal-real"], timeout=120)


def test_gpu_instance_loads_on_cuda(gpu_instance) -> None:
    """AC-006 / T008：CUDA 可用、arch 覆盖、/health 报 cuda、启动日志含设备与 CUDA 版本。"""
    probe = _run(
        [
            "docker",
            "exec",
            REAL_CONTAINER,
            "python",
            "-c",
            "import json,torch; print(json.dumps({'available': torch.cuda.is_available(),"
            " 'cuda': torch.version.cuda, 'torch': torch.__version__,"
            " 'arch': torch.cuda.get_arch_list()}))",
        ],
        timeout=120,
    )
    assert probe.returncode == 0, probe.stderr
    torch_info = json.loads(probe.stdout.strip().splitlines()[-1])
    assert torch_info["available"] is True, torch_info
    assert torch_info["cuda"], torch_info
    for arch in REQUIRED_ARCHES:
        assert arch in torch_info["arch"], f"arch list 缺 {arch}（NFR-002）: {torch_info['arch']}"

    health = gpu_instance["health"]
    assert health["model_loaded"] is True
    assert str(health["device"]).startswith("cuda:"), health

    logs = _run(["docker", "logs", REAL_CONTAINER], timeout=60)
    expected = (
        f"[kronos-real] model loaded: device={health['device']} torch_cuda={torch_info['cuda']}"
    )
    assert expected in logs.stdout + logs.stderr, "启动日志缺 TR-001 设备行"
    print(
        f"\n[evidence] hostname={socket.gethostname()} gpu={_nvidia_query('name')}"
        f" driver={_nvidia_query('driver_version')} torch={torch_info['torch']}"
        f" cuda={torch_info['cuda']} arch={','.join(torch_info['arch'])}"
    )


def test_predict_real_signal_and_vram_rises(gpu_instance) -> None:
    """AC-007 / T009：真实信号（非兜底）且设备侧已用显存相对基线上升。"""
    payload = _predict()
    assert payload["source"] == "kronos", payload
    assert payload["rows_used"] >= 30, payload
    used = _used_mib()
    assert used > gpu_instance["baseline_mib"], (
        f"显存未上升: baseline={gpu_instance['baseline_mib']} used={used}"
    )
    print(f"\n[evidence] baseline_mib={gpu_instance['baseline_mib']} after_predict_mib={used}")


def test_resident_vram_within_budget(gpu_instance) -> None:
    """AC-008 / T010：常驻显存峰值与架构 §7.1 白天行预算对照（整卡读数减基线）。"""
    samples = []
    for _ in range(PEAK_SAMPLES):
        _predict()
        samples.append(_used_mib())
    peak = max(samples) - gpu_instance["baseline_mib"]
    print(
        f"\n[evidence] hostname={socket.gethostname()} gpu={_nvidia_query('name')}"
        f" baseline_mib={gpu_instance['baseline_mib']} samples_mib={samples}"
        f" resident_peak_mib={peak} budget_mib={RESIDENT_VRAM_BUDGET_MIB}"
    )
    assert peak <= RESIDENT_VRAM_BUDGET_MIB, (
        f"常驻峰值 {peak} MiB 超出 §7.1 预算 {RESIDENT_VRAM_BUDGET_MIB} MiB："
        "须在架构 §7.1 白天行显式重标并同步 RESIDENT_VRAM_BUDGET_MIB（spec US-003 场景 2）"
    )


def _cpu_image() -> str:
    built = _run([*COMPOSE_CPU, "build", "kronos-signal-real"], timeout=3600)
    assert built.returncode == 0, f"CPU real 镜像构建失败: {built.stderr[-2000:]}"
    return _compose_image(COMPOSE_CPU, "kronos-signal-real")


@pytest.mark.parametrize(
    ("case", "reason"),
    [("gpu-image-no-device", ERR_NO_CUDA_DEVICE), ("cpu-image", ERR_CPU_WHEEL)],
)
def test_explicit_cuda_without_cuda_fails_visible(gpu_instance, case: str, reason: str) -> None:
    """AC-004 执行机层 / T015：预检通过（挂真实资产）后严格分支拒绝，失败态可见。

    依赖 gpu_instance：GPU 镜像由其构建（T008 -> T015）。不加 `--gpus`，守护进程不参与
    设备分配——失败只能来自加载入口的严格分支。
    """
    image = GPU_IMAGE if case == "gpu-image-no-device" else _cpu_image()
    container = f"f010-strict-{case}"
    port = "18012"
    _run(["docker", "rm", "-f", container], timeout=60)
    try:
        proc = _run(
            [
                "docker",
                "run",
                "--name",
                container,
                "-p",
                f"127.0.0.1:{port}:8001",
                "-v",
                f"{ROOT / 'vendor/Kronos'}:/app/vendor/Kronos:ro",
                "-v",
                f"{ROOT / 'models'}:/app/models:ro",
                "-e",
                "KRONOS_USE_REAL_MODEL=true",
                "-e",
                "KRONOS_REPO_PATH=/app/vendor/Kronos",
                "-e",
                "KRONOS_MODEL_PATH=/app/models/Kronos-base",
                "-e",
                "KRONOS_TOKENIZER_PATH=/app/models/Kronos-Tokenizer-base",
                "-e",
                "KRONOS_DEVICE=cuda",
                image,
            ],
            timeout=300,
        )
        output = proc.stdout + proc.stderr
        assert proc.returncode != 0, f"{case}: 显式 cuda 拿不到 CUDA 却未失败: {output[-1000:]}"
        assert "refusing to start" not in output, f"{case}: 预检未通过，严格分支未被执行"
        assert "[kronos-real] model load failed" in output, output[-1000:]
        assert reason in output, f"{case}: 日志缺失败文案 {reason!r}"
        assert "model loaded: device=cpu" not in output, f"{case}: 静默回落 cpu"

        state = _run(
            [
                "docker",
                "inspect",
                "-f",
                "{{.State.Status}}|{{.State.ExitCode}}|{{.RestartCount}}",
                container,
            ]
        )
        status_name, exit_code, restarts = state.stdout.strip().split("|")
        assert status_name == "exited" and int(exit_code) != 0, state.stdout
        assert int(restarts) == 0, f"{case}: 失败实例不得重启: {state.stdout}"
        with pytest.raises(requests.RequestException):
            requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
        print(f"\n[evidence] case={case} hostname={socket.gethostname()} exit={exit_code}")
    finally:
        _run(["docker", "rm", "-f", container], timeout=60)


def _lifecycle(method: str, action: str) -> dict:
    resp = requests.request(
        method,
        f"{CONTROL_URL}/lifecycle/{action}",
        headers={"X-Contract-Version": "1"},
        json={} if method == "POST" else None,
        timeout=180,
    )
    assert resp.status_code == 200, f"/lifecycle/{action}: {resp.status_code} {resp.text[:300]}"
    return resp.json()


@pytest.mark.xfail(
    strict=True,
    reason="T018 旅程红灯：待 F009 控制面合入主干（/lifecycle/*）且 T002 GPU 运行时就绪；"
    "转绿即 XPASS 判红，须在 F010 T018 显式移除本标记",
)
def test_night_slot_journey(gpu_instance) -> None:
    """T018 层 2 旅程：GPU 常驻 → stop → 显存真实下降且可用显存达训练预算 → restore → 真实信号。"""
    resident = _used_mib()
    assert resident > gpu_instance["baseline_mib"], "GPU 常驻显存应 >0"

    stopped = _lifecycle("POST", "stop")
    assert stopped["state"] == "stopped", stopped
    after_stop = _used_mib()
    assert after_stop < resident, f"stop 后显存未下降: {resident} -> {after_stop}"
    free = _free_mib()
    assert free >= TRAINING_VRAM_BUDGET_MIB, (
        f"卸载后可用显存 {free} MiB < 训练预算 {TRAINING_VRAM_BUDGET_MIB} MiB"
    )
    # 模拟夜槽取锁：卸载态下推理走兜底，不得重新加载模型
    assert _predict()["source"] != "kronos"

    restored = _lifecycle("POST", "restore")
    assert restored["state"] == "running", restored
    assert _predict()["source"] == "kronos"
    print(
        f"\n[evidence] journey resident_mib={resident} after_stop_mib={after_stop} free_mib={free}"
    )
