"""manifest 结构、版本绑定与分区路径的 fail-closed 校验。"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path, PureWindowsPath
from typing import Any

from alphamill.data_bridge import paths
from alphamill.data_bridge.errors import (
    DataBridgeError,
    ManifestIntegrityError,
    UnknownDatasetError,
)
from alphamill.data_bridge.registry import require_dataset

DATA_VERSION_RE = re.compile(r"^v(\d{4})\.(\d{2})\.(\d{2})(?:-r([1-9]\d*))?$")
PARTITION_FILE_RE = re.compile(r"^date=(\d{4}-\d{2}-\d{2})\.r([1-9]\d*)\.parquet$")
SHA256_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _canonical_key(key: dict[str, str]) -> str:
    return json.dumps(key, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def safe_artifact_path(
    root: Path,
    rel: str,
    dataset: str,
    logical_key: dict[str, str] | None = None,
    *,
    expected_dir: Path | None = None,
) -> Path:
    """把 manifest 相对路径限制在 lake/<dataset>/ 内（含 symlink 防逃逸）。"""
    if not isinstance(rel, str) or not rel:
        raise ManifestIntegrityError(f"manifest 分区 path 非法: {rel!r}")
    rel_path = Path(rel)
    if (
        rel_path.is_absolute()
        or PureWindowsPath(rel).is_absolute()
        or PureWindowsPath(rel).drive
        or any(part in {"", ".", ".."} for part in rel_path.parts)
        or not rel_path.parts
        or rel_path.parts[0] != dataset
        or rel_path.suffix != ".parquet"
    ):
        raise ManifestIntegrityError(f"manifest 分区 path 越界或格式非法: {rel!r}")
    lake_root = root.resolve()
    candidate = (lake_root / rel_path).resolve(strict=False)
    try:
        candidate.relative_to(lake_root)
    except ValueError as exc:
        raise ManifestIntegrityError(f"manifest 分区 path 越界: {rel!r}") from exc
    if logical_key is not None:
        filename_match = PARTITION_FILE_RE.fullmatch(candidate.name)
        if filename_match is None or filename_match.group(1) != logical_key.get("date"):
            raise ManifestIntegrityError(f"manifest 分区 path 与逻辑日期不符: {rel!r}")
        if expected_dir is None:
            try:
                expected_dir = paths.partition_dir(root, dataset, logical_key).resolve()
            except DataBridgeError as exc:
                raise ManifestIntegrityError(
                    f"manifest 逻辑分区键包含非法路径组件: {logical_key!r}"
                ) from exc
        if candidate.parent != expected_dir:
            raise ManifestIntegrityError(f"manifest 分区 path 与逻辑键不符: {rel!r}")
    return candidate


def _validate_data_version(value: Any) -> None:
    if not isinstance(value, str):
        raise ManifestIntegrityError("manifest data_version 必须是字符串")
    match = DATA_VERSION_RE.fullmatch(value)
    if match is None:
        raise ManifestIntegrityError("manifest data_version 格式非法")
    try:
        date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError as exc:
        raise ManifestIntegrityError("manifest data_version 日期非法") from exc


def validate_manifest_shape(root: Path, manifest: dict[str, Any]) -> None:
    """验证 reader/exporter 依赖的清单结构，避免篡改后以 KeyError 收场。"""
    if not isinstance(manifest, dict):
        raise ManifestIntegrityError("manifest 顶层必须是 JSON object")
    try:
        spec = require_dataset(manifest["dataset"])
    except (KeyError, UnknownDatasetError, TypeError) as exc:
        raise ManifestIntegrityError("manifest dataset 非法或未登记") from exc
    if manifest.get("status") not in {"valid", "invalid"}:
        raise ManifestIntegrityError(
            f"manifest status 非法: {manifest.get('status')!r}（期望 valid|invalid）"
        )
    _validate_data_version(manifest.get("data_version"))
    rows = manifest.get("rows")
    if not isinstance(rows, int) or isinstance(rows, bool) or rows < 0:
        raise ManifestIntegrityError("manifest rows 必须是非负整数")
    value_digest = manifest.get("value_digest")
    if not isinstance(value_digest, str) or not SHA256_DIGEST_RE.fullmatch(value_digest):
        raise ManifestIntegrityError("manifest value_digest 格式非法")
    symbol_map_digest = manifest.get("symbol_map_digest")
    if symbol_map_digest is not None and (
        not isinstance(symbol_map_digest, str) or not SHA256_DIGEST_RE.fullmatch(symbol_map_digest)
    ):
        raise ManifestIntegrityError("manifest symbol_map_digest 格式非法")
    partitions = manifest.get("partitions")
    if not isinstance(partitions, list):
        raise ManifestIntegrityError("manifest partitions 必须是数组")

    seen_keys: set[str] = set()
    seen_paths: set[str] = set()
    expected_dirs: dict[str, Path] = {}
    required = {
        "logical_partition_key",
        "path",
        "rows",
        "time_min",
        "time_max",
        "row_digest",
        "bytes",
        "sha256",
    }
    for index, partition in enumerate(partitions):
        if not isinstance(partition, dict) or not required <= partition.keys():
            raise ManifestIntegrityError(f"manifest partitions[{index}] 字段不完整")
        logical_key = partition["logical_partition_key"]
        if not isinstance(logical_key, dict) or set(logical_key) != set(spec.partition_keys):
            raise ManifestIntegrityError(f"manifest partitions[{index}] 逻辑分区键不符合 registry")
        if any(not isinstance(value, str) or not value for value in logical_key.values()):
            raise ManifestIntegrityError(f"manifest partitions[{index}] 逻辑分区键值非法")
        try:
            date.fromisoformat(logical_key["date"])
        except ValueError as exc:
            raise ManifestIntegrityError(f"manifest partitions[{index}] date 非法") from exc
        key = _canonical_key(logical_key)
        if key in seen_keys:
            raise ManifestIntegrityError(f"manifest partitions[{index}] 逻辑分区键重复")
        seen_keys.add(key)
        rel = partition["path"]
        directory_key = _canonical_key(
            {name: value for name, value in logical_key.items() if name != "date"}
        )
        if directory_key not in expected_dirs:
            try:
                expected_dirs[directory_key] = paths.partition_dir(
                    root, spec.name, logical_key
                ).resolve()
            except DataBridgeError as exc:
                raise ManifestIntegrityError(
                    f"manifest 逻辑分区键包含非法路径组件: {logical_key!r}"
                ) from exc
        safe_artifact_path(
            root, rel, spec.name, logical_key, expected_dir=expected_dirs[directory_key]
        )
        if rel in seen_paths:
            raise ManifestIntegrityError(f"manifest partitions[{index}] path 重复")
        seen_paths.add(rel)
        partition_rows = partition["rows"]
        if (
            not isinstance(partition_rows, int)
            or isinstance(partition_rows, bool)
            or partition_rows < 0
        ):
            raise ManifestIntegrityError(f"manifest partitions[{index}] rows 非法")
        partition_bytes = partition["bytes"]
        if (
            not isinstance(partition_bytes, int)
            or isinstance(partition_bytes, bool)
            or partition_bytes < 0
        ):
            raise ManifestIntegrityError(f"manifest partitions[{index}] bytes 非法")
        if not isinstance(partition["time_min"], str) or not isinstance(partition["time_max"], str):
            raise ManifestIntegrityError(f"manifest partitions[{index}] 时间边界非法")
        if not isinstance(partition["row_digest"], str) or not isinstance(partition["sha256"], str):
            raise ManifestIntegrityError(f"manifest partitions[{index}] 摘要字段非法")

    if rows != sum(partition["rows"] for partition in partitions):
        raise ManifestIntegrityError("manifest rows 与 partitions 汇总不符")
    quality = manifest.get("quality")
    if quality is not None:
        if not isinstance(quality, dict):
            raise ManifestIntegrityError("manifest quality 必须是 object")
        flagged = quality.get("flagged_partitions", [])
        unresolved = quality.get("unresolved_total", 0)
        if not isinstance(flagged, list) or any(not isinstance(item, str) for item in flagged):
            raise ManifestIntegrityError("manifest quality.flagged_partitions 必须是字符串数组")
        if not isinstance(unresolved, int) or isinstance(unresolved, bool) or unresolved < 0:
            raise ManifestIntegrityError("manifest quality.unresolved_total 必须是非负整数")
    skipped = manifest.get("skipped")
    if skipped is not None:
        if not isinstance(skipped, list):
            raise ManifestIntegrityError("manifest skipped 必须是数组")
        for index, key in enumerate(skipped):
            if not isinstance(key, dict) or set(key) != set(spec.partition_keys):
                raise ManifestIntegrityError(f"manifest skipped[{index}] 逻辑分区键非法")
            if any(not isinstance(value, str) or not value for value in key.values()):
                raise ManifestIntegrityError(f"manifest skipped[{index}] 逻辑分区键值非法")
            try:
                date.fromisoformat(key["date"])
            except ValueError as exc:
                raise ManifestIntegrityError(f"manifest skipped[{index}] date 非法") from exc
