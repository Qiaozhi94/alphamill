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
