"""生命周期控制面的配置契约（F009 FR-007）。

五个具名环境变量各有值域与默认值；非法值在**启动期判红**并点名变量，不静默回退默认——
静默回退会让"迁移执行机只改配置"变成"改了配置但没生效"，而这类缺陷只在夜槽出事时才暴露。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

PROBE_MODES = ("auto", "torch", "nvidia_smi")

ENV_PROBE_MODE = "KRONOS_VRAM_PROBE_MODE"
ENV_PROBE_TIMEOUT = "KRONOS_VRAM_PROBE_TIMEOUT_S"
ENV_STATUS_TIMEOUT = "KRONOS_LIFECYCLE_STATUS_TIMEOUT_S"
ENV_STOP_TIMEOUT = "KRONOS_LIFECYCLE_STOP_TIMEOUT_S"
ENV_RESTORE_TIMEOUT = "KRONOS_LIFECYCLE_RESTORE_TIMEOUT_S"


#: 服务端三个动作的 deadline 缺省值（架构 §7.1 动作表）。客户端 socket deadline 另算，
#: 且必须**严格更大**——两端同值时客户端先抛 OSError，服务端规范的 E_TIMEOUT 信封收不到
#: （F009 FR-009 / 检视 R4-002）。
SERVER_DEADLINES = {"status": 5.0, "stop": 60.0, "restore": 120.0}

#: 客户端 deadline 相对服务端的缺省余量（秒）。
CLIENT_DEADLINE_MARGIN_S = 5.0


class ConfigError(ValueError):
    """配置非法：启动期抛出，消息点名变量（FR-007）。"""


@dataclass(frozen=True)
class LifecycleConfig:
    probe_mode: str = "auto"
    probe_timeout_s: float = 2.0
    status_timeout_s: float = 5.0
    stop_timeout_s: float = 60.0
    restore_timeout_s: float = 120.0


def _positive(env: dict, name: str, default: float) -> float:
    raw = env.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{name} 必须是正数，实际为 {raw!r}") from exc
    if value <= 0:
        raise ConfigError(f"{name} 必须是正数，实际为 {raw!r}")
    return value


def load_config(env: dict | None = None) -> LifecycleConfig:
    """解析并校验配置；任何非法值抛 ConfigError（调用方在启动期让进程失败）。"""
    env = os.environ if env is None else env

    mode = env.get(ENV_PROBE_MODE, "auto")
    if mode not in PROBE_MODES:
        raise ConfigError(f"{ENV_PROBE_MODE} 取值须为 {'|'.join(PROBE_MODES)}，实际为 {mode!r}")

    status_timeout = _positive(env, ENV_STATUS_TIMEOUT, 5.0)
    probe_timeout = _positive(env, ENV_PROBE_TIMEOUT, 2.0)
    if probe_timeout > status_timeout:
        raise ConfigError(
            f"{ENV_PROBE_TIMEOUT}({probe_timeout}) 不得大于 "
            f"{ENV_STATUS_TIMEOUT}({status_timeout})——否则显存探测会把 status 拖过 deadline"
        )

    return LifecycleConfig(
        probe_mode=mode,
        probe_timeout_s=probe_timeout,
        status_timeout_s=status_timeout,
        stop_timeout_s=_positive(env, ENV_STOP_TIMEOUT, 60.0),
        restore_timeout_s=_positive(env, ENV_RESTORE_TIMEOUT, 120.0),
    )


def client_deadline_floor(
    action: str,
    *,
    server_deadline_s: float | None = None,
    margin_s: float = CLIENT_DEADLINE_MARGIN_S,
) -> float:
    """某个动作的**客户端** deadline 下限 = 服务端 deadline + 余量（FR-009）。

    服务端侧只负责给出这条下限；真正设置 socket 超时的是 F003 客户端
    （`kronos_offload.client_deadline`），其行为与变异判红在 F003 分支验收。
    """
    if action not in SERVER_DEADLINES:
        raise ConfigError(f"未知动作 {action!r}，取值须为 {'|'.join(SERVER_DEADLINES)}")
    if margin_s <= 0:
        raise ConfigError(
            f"客户端余量必须为正（实际 {margin_s}）：两端同值时客户端先超时，"
            "服务端的 E_TIMEOUT 信封收不到"
        )
    base = SERVER_DEADLINES[action] if server_deadline_s is None else server_deadline_s
    return base + margin_s
