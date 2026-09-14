"""湖根路径与目录布局约定（design §3）。

唯一入口 `lake_root()`：默认仓库根 `lake/`，可用环境变量 `ALPHAMILL_LAKE_DIR`
覆盖（测试与多环境部署用）。所有模块经此处取湖路径，不各自硬编码。
"""

from __future__ import annotations

import os
from pathlib import Path, PureWindowsPath

from alphamill.data_bridge.errors import DataBridgeError

REPO_ROOT = Path(__file__).resolve().parents[3]


def lake_root() -> Path:
    override = os.getenv("ALPHAMILL_LAKE_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (REPO_ROOT / "lake").resolve()


def manifests_dir(root: Path, dataset: str) -> Path:
    return root / "_manifests" / dataset


def manifest_path(root: Path, dataset: str, data_version: str) -> Path:
    return manifests_dir(root, dataset) / f"{data_version}.json"


def staging_dir(root: Path, dataset: str, data_version: str) -> Path:
    return root / "_staging" / dataset / data_version


def symbol_maps_dir(root: Path) -> Path:
    return root / "_metadata" / "symbol_maps"


def partition_dir(root: Path, dataset: str, logical_key: dict[str, str]) -> Path:
    """分区目录：lake/<dataset>/exchange=<ex>/[pair=<pair>/][timeframe=<tf>/]。"""
    _validate_component(dataset, "dataset")
    parts = [dataset]
    if "exchange" in logical_key:
        parts.append(f"exchange={_validate_component(logical_key['exchange'], 'exchange')}")
    if "pair" in logical_key:
        parts.append(f"pair={_validate_component(logical_key['pair'], 'pair')}")
    if "timeframe" in logical_key:
        parts.append(f"timeframe={_validate_component(logical_key['timeframe'], 'timeframe')}")
    return root.joinpath(*parts)


def _validate_component(value: str, name: str) -> str:
    """拒绝会改变湖目录层级或逃逸根目录的外部维度值。"""
    if (
        not isinstance(value, str)
        or not value
        or value in {".", ".."}
        or "\x00" in value
        or "/" in value
        or "\\" in value
        or PureWindowsPath(value).is_absolute()
        or PureWindowsPath(value).drive
    ):
        raise DataBridgeError(f"非法分区路径组件 {name}: {value!r}")
    return value


def partition_filename(logical_key: dict[str, str], revision: int) -> str:
    return f"date={logical_key['date']}.r{revision}.parquet"
