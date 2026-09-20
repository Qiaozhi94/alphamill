"""挖掘运行的缺省配置与 --config 解析（自 cli.py 抽出，保持 CLI 薄壳）。"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Final

from alphamill.factor_factory import canonical, errors
from alphamill.factor_factory.generators import gpu_slot

DEFAULT_MINE_CONFIG: Final[Mapping[str, canonical.JSONValue]] = MappingProxyType(
    {
        "tier_level": "manual",
        "vram_limit_gb": 6.0,
        "queue_timeout_s": 1800,
        # 架构 §7.1 时段表按执行机本地时间表述；时区随执行机走（迁移只改配置）。
        "training_window_start": "22:00",
        "training_window_end": "06:30",
        "training_window_tz": gpu_slot.DEFAULT_WINDOW_TZ,
        # 夜槽卸载 Kronos 的控制面（架构 §7.1）。缺省 null = 本机未部署该服务；
        # 执行机必须显式配置，否则按观测→处置决策表 fail-closed，不抢卡。
        "kronos_control_url": None,
        "kronos_contract_version": "1",
        # 部署清单事实：True = 本机部署了 Kronos。为 True 而未配 control_url 即
        # fail-closed（漏配不等于没部署）；确未部署的机器显式置 False。
        "kronos_deployed": True,
    }
)


def load_config(path: Path | None) -> dict[str, canonical.JSONValue]:
    """读取 --config 指向的 JSON 对象；不可读或非对象即判红。"""
    if path is None:
        return {}
    try:
        payload: canonical.JSONValue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise errors.SchemaValidationError(f"config file cannot be read: {path}") from exc
    if not isinstance(payload, dict):
        raise errors.SchemaValidationError("config must be a JSON object")
    return payload


def _optional_text(value: canonical.JSONValue) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def resolve_kronos_offload(
    config: Mapping[str, canonical.JSONValue],
) -> gpu_slot.KronosOffloadOutcome:
    """按配置执行夜槽卸载决策（架构 §7.1 观测→处置决策表）。"""
    return gpu_slot.offload_kronos(
        control_url=_optional_text(config.get("kronos_control_url")),
        contract_version=str(config["kronos_contract_version"]),
        service_deployed=bool(config["kronos_deployed"]),
    )


def restore_kronos_if_stopped(
    config: Mapping[str, canonical.JSONValue],
    outcome: gpu_slot.KronosOffloadOutcome | None,
) -> bool | None:
    """夜槽结束后恢复常驻推理；未曾停过则无事可做（返回 None）。"""
    if outcome is None or outcome.action != "stopped":
        return None
    return gpu_slot.restore_kronos(
        control_url=_optional_text(config.get("kronos_control_url")),
        contract_version=str(config["kronos_contract_version"]),
    )
