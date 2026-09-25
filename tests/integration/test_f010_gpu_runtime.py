"""F010 GPU 运行时集成：`kronos-signal-real` 叠加 GPU override 在执行机真实推理（执行机取证）。

对应 spec AC-004 执行机层 / AC-006 / AC-007 / AC-008 与 T018 旅程轨、design §8：
- AC-006：容器内 `torch.cuda.is_available()` 为真、arch list 含 sm_120（NFR-002），当前卡
  （sm_89，不在 cu130 arch list 内，靠 CUDA 次版本二进制兼容）以实跑 GPU 运算为准，
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

# 只给「产镜像、不碰容器」的 CPU 构建用带 worktree 后缀的项目名：compose 项目名缺省取自
# compose 文件所在目录（deployment），所有 worktree 共用，生成的镜像名会被并行会话互相
# 覆盖（R1-001）。但**不能**把它套到整个 COMPOSE_BASE 上——那会让 rm/up 走另一个项目，
# 与运营容器 quant-kronos-signal-real 重名冲突，还会新建一套空的 TimescaleDB 卷
# （R2-001，第 1 轮修复引入）。
COMPOSE_PROJECT_BUILD = f"alphamill-{ROOT.name.removeprefix('alphamill-')}"
COMPOSE_CPU_BUILD = [
    "docker",
    "compose",
    "-p",
    COMPOSE_PROJECT_BUILD,
    "-f",
    "deployment/docker-compose.yml",
    "--profile",
    "kronos-real",
]
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
# cu130 wheel 的 arch list 实测为 sm_75/80/86/90/100/120：迁移目标 sm_120 在内，当前卡
# sm_89 不在内（跑 sm_86 cubin，CUDA 次版本二进制兼容）。当前卡的判据是实跑运算，不是列表。
REQUIRED_ARCHES = ("sm_120",)

# 实例与探测都在 127.0.0.1：一律绕开环境里的 HTTP(S)_PROXY，否则代理会替失败的连接
# 返回响应，让"/health 不可达"这类断言假绿（F010 T015 实测）。
SESSION = requests.Session()
SESSION.trust_env = False

pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}

POLL_SECONDS = 300
PEAK_SAMPLES = 5


def _require_integration(reason_unavailable: str | None = None) -> None:
    if not INTEGRATION_REQUIRED:
        pytest.skip("GPU 集成需 ALPHAMILL_INTEGRATION=1 并在执行机取证（SOP §3）")
    if reason_unavailable:
        pytest.fail(reason_unavailable)


def _run(
    cmd: list[str], timeout: int | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT, env=env)


def _build_env() -> dict[str, str]:
    """构建用环境：优先选 host 网络的 buildx builder。

    默认 builder 的 RUN 步骤走 bridge 网络，CUDA 依赖（cudnn 553MB 等）在执行机上连续
    三次读超时；host 网络实测 20MB/s vs 7MB/s，一次成功（F010 T008 实测）。builder 由
    `BUILDX_BUILDER` 指定时听调用者的；否则本机存在名为 hostnet 的 builder 就用它。
    """
    env = dict(os.environ)
    if "BUILDX_BUILDER" not in env:
        listed = subprocess.run(
            ["docker", "buildx", "ls", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if "hostnet" in listed.stdout.split():
            env["BUILDX_BUILDER"] = "hostnet"
    return env


def _inspect(container: str) -> dict:
    proc = _run(["docker", "inspect", container], timeout=60)
    assert proc.returncode == 0, f"容器不存在或 docker 不可达: {proc.stderr}"
    return json.loads(proc.stdout)[0]


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
            resp = SESSION.get(f"{BASE_URL}/health", timeout=5)
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
    resp = SESSION.get(f"{BASE_URL}/predict/BTC/USDT", params={"exchange": "binance"}, timeout=120)
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
    """以 GPU override 构建并拉起 real 实例；基线显存在实例起来之前读取。

    `KRONOS_REUSE_RUNNING=1` 时复用**已在跑**的 real 实例而不重建：9.7GB 的 GPU 镜像
    重建一次要几十分钟，且构建期需要能访问 registry（实测断网时 buildkit 解析
    `python:3.11-slim` 的 manifest 就失败）。复用不是默默省事——证据行会记下镜像
    tag / id / 创建时间，好让"这份证据是哪个镜像跑出来的"可追；复用时基线显存取的是
    **实例已在运行**时的读数，因此本模式下不断言"相对空载基线的上升"（见 AC-007 用例）。
    """
    _require_integration()
    _require_nvidia_runtime()

    if os.getenv("KRONOS_REUSE_RUNNING", "").lower() in {"1", "true", "yes"}:
        info = _inspect(REAL_CONTAINER)
        assert info["State"]["Running"] is True, "KRONOS_REUSE_RUNNING=1 但实例未在运行"
        image = info["Config"]["Image"]
        image_info = json.loads(
            _run(["docker", "image", "inspect", image], timeout=60).stdout or "[{}]"
        )[0]
        print(
            f"\n[evidence] reused image={image} id={image_info.get('Id', '?')[:19]} "
            f"created={image_info.get('Created', '?')[:19]}"
        )
        health = _wait_for_health("cuda")
        yield {"baseline_mib": None, "health": health, "reused": image}
        return

    _run([*COMPOSE_GPU, "rm", "-sf", "kronos-signal-real"], timeout=120)
    baseline = _used_mib()

    built = _run([*COMPOSE_GPU, "build", "kronos-signal-real"], timeout=3600, env=_build_env())
    assert built.returncode == 0, f"GPU 镜像构建失败: {built.stderr[-2000:]}"
    up = _run([*COMPOSE_GPU, "up", "-d", "kronos-signal-real"], timeout=300)
    assert up.returncode == 0, f"GPU 实例拉起失败: {up.stderr[-2000:]}"

    health = _wait_for_health("cuda")
    yield {"baseline_mib": baseline, "health": health, "reused": None}

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
            "import json,torch;"
            " a=torch.randn(512,512,device='cuda'); b=torch.randn(512,512,device='cuda');"
            " gpu=(a@b).sum().item(); cpu=(a.cpu()@b.cpu()).sum().item();"
            " print(json.dumps({'available': torch.cuda.is_available(),"
            " 'cuda': torch.version.cuda, 'torch': torch.__version__,"
            " 'arch': torch.cuda.get_arch_list(),"
            " 'capability': list(torch.cuda.get_device_capability(0)),"
            " 'matmul_ok': abs(gpu-cpu) < 1.0}))",
        ],
        timeout=120,
    )
    assert probe.returncode == 0, probe.stderr
    torch_info = json.loads(probe.stdout.strip().splitlines()[-1])
    assert torch_info["available"] is True, torch_info
    assert torch_info["cuda"], torch_info
    for arch in REQUIRED_ARCHES:
        assert arch in torch_info["arch"], f"arch list 缺 {arch}（NFR-002）: {torch_info['arch']}"
    # 当前卡（capability 8.9）不在 arch list 内，靠二进制兼容跑 sm_86 cubin：实算一次才算数
    assert torch_info["matmul_ok"] is True, f"GPU 运算结果与 CPU 不一致: {torch_info}"

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
        f" cuda={torch_info['cuda']} capability={torch_info['capability']}"
        f" arch={','.join(torch_info['arch'])} matmul_ok={torch_info['matmul_ok']}"
    )


def test_predict_real_signal_and_vram_rises(gpu_instance) -> None:
    """AC-007 / T009：真实信号（非兜底）且设备侧已用显存相对基线上升。"""
    payload = _predict()
    assert payload["source"] == "kronos", payload
    assert payload["rows_used"] >= 30, payload
    used = _used_mib()
    baseline = gpu_instance["baseline_mib"]
    if baseline is None:
        # 复用在跑实例：拿不到空载基线，退而断言"设备侧确实有显存被占用"，
        # 并如实说明这不是"相对空载的上升"（不得把弱断言说成强结论）。
        assert used > 0, f"复用实例但设备侧已用显存为 0: {used}"
        print(f"\n[evidence] reused-instance used_mib={used}（无空载基线，不断言上升量）")
    else:
        assert used > baseline, f"显存未上升: baseline={baseline} used={used}"
        print(f"\n[evidence] baseline_mib={baseline} after_predict_mib={used}")


def test_resident_vram_within_budget(gpu_instance) -> None:
    """AC-008 / T010：常驻显存峰值与架构 §7.1 白天行预算对照（整卡读数减基线）。"""
    samples = []
    for _ in range(PEAK_SAMPLES):
        _predict()
        samples.append(_used_mib())
    baseline = gpu_instance["baseline_mib"] or 0
    peak = max(samples) - baseline
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
    """构建（或按 `KRONOS_CPU_IMAGE` 指定）一个**当前代码的** CPU wheel real 镜像。

    不许拿本地任意同名镜像顶替：CPU wheel 分支断言的是 F010 的严格设备解析，旧镜像
    可能根本没有那段代码，用它取证等于测了别的东西。registry 不可达时宁可 skip——
    "构建不了"与"断言不成立"是两回事，不得混为一谈。
    """
    pinned = os.getenv("KRONOS_CPU_IMAGE", "").strip()
    # 说明：本机若已有「CPU wheel torch + 当前代码」的镜像，用 KRONOS_CPU_IMAGE 指定它比
    # 重新构建快得多（registry 不可达时是唯一可行路径）。构建方式见 tasks T015 证据行。
    if pinned:
        exists = _run(["docker", "image", "inspect", pinned], timeout=60)
        if exists.returncode != 0:
            pytest.skip(f"KRONOS_CPU_IMAGE={pinned} 在本机不存在")
        return pinned

    built = _run(
        [*COMPOSE_CPU_BUILD, "build", "kronos-signal-real"], timeout=3600, env=_build_env()
    )
    if built.returncode != 0:
        tail = built.stderr[-400:]
        if "registry-1.docker.io" in tail or "failed to resolve source metadata" in tail:
            pytest.skip(
                "无法构建当前代码的 CPU wheel 镜像（registry 不可达）：本用例的证据须用"
                "当前代码的镜像，旧镜像不算。网络恢复后重跑，或以 KRONOS_CPU_IMAGE 指定。"
            )
        pytest.fail(f"CPU real 镜像构建失败: {tail}")
    return _compose_image(COMPOSE_CPU_BUILD, "kronos-signal-real")


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
        # 后台起容器：前台 `docker run` 返回时容器已退出，"/health 不可达"那条断言恒真
        # （R1-007）。**不写 --restart=no**：那样"未重启"同样恒真（R2-004）——重启策略由
        # F004 的 compose 契约锁定（`restart: "no"`，见 test_f004_compose_profile_contract），
        # 这里不重复断言它，只断言"加载失败的实例始终没进入可服务状态"。
        started = _run(
            [
                "docker",
                "run",
                "-d",
                "--restart=no",
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
        assert started.returncode == 0, f"{case}: 容器未起来: {started.stderr[-500:]}"

        # 容器存活的**每一轮**都探 /health，而不是只探首轮——只探一次的话"不可达"多半只
        # 反映"服务还没开始监听"，而不是"它拒绝进入可服务状态"（R2-004）。重启策略不在这里
        # 断言：F004 的 compose 契约已锁 `restart: "no"`，这里断言它等于恒真。
        probes: list[object] = []
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            state = _run(
                ["docker", "inspect", "-f", "{{.State.Status}}|{{.State.ExitCode}}", container]
            )
            status_name, exit_code = state.stdout.strip().split("|")
            if status_name != "running":
                break
            try:
                probes.append(SESSION.get(f"http://127.0.0.1:{port}/health", timeout=2).status_code)
            except requests.RequestException:
                probes.append("unreachable")
            time.sleep(1)
        else:
            pytest.fail(f"{case}: 120s 内容器未退出（严格分支没拦住？status={status_name}）")

        logs = _run(["docker", "logs", container], timeout=60)
        output = logs.stdout + logs.stderr
        assert int(exit_code) != 0, f"{case}: 退出码为 0，显式 cuda 拿不到 CUDA 却未失败"
        assert status_name == "exited", f"{case}: 终态应为 exited，实际 {status_name}"
        assert "refusing to start" not in output, f"{case}: 预检未通过，严格分支未被执行"
        assert "[kronos-real] model load failed" in output, output[-1000:]
        assert reason in output, f"{case}: 日志缺失败文案 {reason!r}"
        assert "model loaded: device=cpu" not in output, f"{case}: 静默回落 cpu"
        assert all(p == "unreachable" for p in probes), (
            f"{case}: 容器存活期间 /health 曾可达（探测序列 {probes}）——"
            "加载失败的实例不得进入可服务状态"
        )
        with pytest.raises(requests.RequestException):
            SESSION.get(f"http://127.0.0.1:{port}/health", timeout=3)
        print(
            f"\n[evidence] case={case} hostname={socket.gethostname()} exit={exit_code} "
            f"health_probes_while_running={probes}（restart 策略由 F004 compose 契约锁定）"
        )
    finally:
        _run(["docker", "rm", "-f", container], timeout=60)


def _lifecycle(method: str, action: str) -> dict:
    resp = SESSION.request(
        method,
        f"{CONTROL_URL}/lifecycle/{action}",
        headers={"X-Contract-Version": "1"},
        json={} if method == "POST" else None,
        timeout=180,
    )
    assert resp.status_code == 200, f"/lifecycle/{action}: {resp.status_code} {resp.text[:300]}"
    return resp.json()


def test_night_slot_journey(gpu_instance) -> None:
    """T018 层 2 旅程：GPU 常驻 → stop → 显存真实下降且可用显存达训练预算 → restore → 真实信号。

    **先红态已解除**（2026-09-24，F010 T018）：该标记在 F009 控制面尚未合入主干时立起，
    合入并重建带 `/lifecycle/*` 的 GPU 镜像后取到真实证据（执行机 `qiaozhi-lt`）：

        常驻 563 MiB → stop 后 137 MiB → 卸载后整卡可用 7820 MiB ≥ 6GB 训练预算 → restore 恢复

    这是"夜槽卸载腾显存"这条链路第一次端到端在真实显存上跑通——此前 F009 只在 CPU 实例上
    验证过控制面语义，显存结论一律挂先红态。
    """
    resident = _used_mib()
    baseline = gpu_instance["baseline_mib"]
    if baseline is None:
        assert resident > 0, f"复用实例但设备侧已用显存为 0: {resident}"
    else:
        assert resident > baseline, f"GPU 常驻显存应高于空载基线: {baseline} -> {resident}"

    # try 的起点必须在 **stop 调用之前**（R2-005）：stop 本身失败时模型可能已被丢弃
    # （F009 的落点表：丢引用后保持 stopped），那种情况同样需要恢复。
    # 复用模式下这就是执行机的运营实例，留在 desired=stopped 会让白天 /predict 一直返回
    # 兜底信号而无人察觉，而 fixture 在复用模式下（有意）不做清理。
    try:
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
    finally:
        try:
            recovered = _lifecycle("POST", "restore")
        except Exception as exc:  # 不吞原始断言：恢复失败只打印，交由原异常继续冒泡
            print(f"\n[warn] 旅程收尾 restore 失败，实例可能仍处 stopped: {exc}")
        else:
            print(f"\n[cleanup] 旅程收尾 restore -> {recovered}")

    assert _lifecycle("GET", "status")["state"] == "running"
    assert _predict()["source"] == "kronos"
    print(
        f"\n[evidence] journey resident_mib={resident} after_stop_mib={after_stop} free_mib={free}"
    )
