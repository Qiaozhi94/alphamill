"""manifest 契约读写、data_version 排序、完整性与增量合成（design §3/§4，架构 §4.4）。

关键不变量：
- `partitions` 是必填的版本身份；reader 只按清单构造输入路径，从不扫描目录
  （F002-R2-02）——完整性校验逐项验存在/字节数/sha256，任一不符即
  `ManifestIntegrityError`，不要求目录全集相等（`.rN` 共享模型）。
- `value_digest` 是 DatasetVersion 的语义根摘要：只含 dataset、registry 投影与
  分区级 (key, rows, bounds, row_digest)，不含物理 path/codec/bytes/sha256/
  exported_at（F002-D011）。
- manifest 合成是**累计完整快照**而非一日 delta：增量从上一 valid 清单继承基线，
  full 用基线复用未变文件但按当前源库组成版本；本轮分区按逻辑分区键替换/追加，
  `rows`/`pairs`/quality 重算，`skipped` 走同样的继承/替换（F002-R2-03/R3-03）。
"""

from __future__ import annotations

import errno
import hashlib
import json
import logging
import os
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from alphamill.data_bridge import paths
from alphamill.data_bridge.digest import DIGEST_PREFIX
from alphamill.data_bridge.errors import (
    ManifestIntegrityError,
    UnknownDatasetError,
    VersionNotFoundError,
)
from alphamill.data_bridge.manifest_validation import DATA_VERSION_RE
from alphamill.data_bridge.manifest_validation import safe_artifact_path as _safe_artifact_path
from alphamill.data_bridge.manifest_validation import (
    validate_manifest_shape as _validate_manifest_shape,
)
from alphamill.data_bridge.registry import DatasetSpec, require_dataset

logger = logging.getLogger(__name__)

SOURCE_TAG = "timescaledb@alphamill"

_REQUIRED_FIELDS = ("dataset", "data_version", "status", "rows", "value_digest", "partitions")


def parse_data_version(version: str) -> tuple[date, int]:
    if not isinstance(version, str):
        raise VersionNotFoundError(f"非法 data_version: {version!r}（期望 vYYYY.MM.DD[-rN]）")
    m = DATA_VERSION_RE.fullmatch(version)
    if m is None:
        raise VersionNotFoundError(f"非法 data_version: {version!r}（期望 vYYYY.MM.DD[-rN]）")
    try:
        day = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError as exc:
        raise VersionNotFoundError(f"非法 data_version: {version!r}（日期不存在）") from exc
    return day, int(m.group(4) or 1)


def format_data_version(day: date, revision: int = 1) -> str:
    if revision < 1:
        raise ValueError(f"revision 必须 >=1，收到 {revision}")
    base = f"v{day:%Y.%m.%d}"
    return base if revision == 1 else f"{base}-r{revision}"


def data_version_sort_key(version: str) -> tuple[date, int]:
    return parse_data_version(version)


def canonical_key(key: dict[str, str]) -> str:
    return json.dumps(key, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def iso_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def list_versions(root: Path, dataset: str) -> list[str]:
    require_dataset(dataset)
    directory = paths.manifests_dir(root, dataset)
    if not directory.is_dir():
        return []
    versions = [p.stem for p in directory.glob("*.json")]
    return sorted(versions, key=data_version_sort_key)


def load_manifest(root: Path, dataset: str, data_version: str) -> dict[str, Any]:
    # 先校验版本字符串，再拼路径；显式版本来自 API/CLI，不能让它成为路径入口。
    require_dataset(dataset)
    parse_data_version(data_version)
    path = paths.manifest_path(root, dataset, data_version)
    if not path.is_file():
        raise VersionNotFoundError(f"manifest 不存在: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ManifestIntegrityError(f"manifest JSON 损坏: {path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ManifestIntegrityError(f"manifest 顶层必须是 JSON object: {path}")
    for field in _REQUIRED_FIELDS:
        if field not in manifest:
            raise ManifestIntegrityError(f"manifest 缺少必填字段 {field!r}: {path}")
    if manifest["dataset"] != dataset or manifest["data_version"] != data_version:
        raise ManifestIntegrityError(
            f"manifest 身份不符: 文件位于 {dataset}/{data_version}，"
            f"内容为 {manifest['dataset']}/{manifest['data_version']}"
        )
    _validate_manifest_shape(Path(root), manifest)
    return manifest


def latest_valid_version(root: Path, dataset: str) -> str:
    for version in reversed(list_versions(root, dataset)):
        manifest = load_manifest(root, dataset, version)
        if manifest["status"] == "valid":
            return version
    raise VersionNotFoundError(f"{dataset} 无 valid 版本")


def next_data_version(root: Path, dataset: str, day: date) -> str:
    """同日重导追加序号；已被任何 manifest（含 invalid）占用的序号不复用。"""
    max_revision = 0
    for version in list_versions(root, dataset):
        seen_day, revision = parse_data_version(version)
        if seen_day == day:
            max_revision = max(max_revision, revision)
    return format_data_version(day, max_revision + 1)


def validate_manifest_integrity(
    root: Path,
    manifest: dict[str, Any],
    partitions: list[dict[str, Any]] | None = None,
) -> None:
    """校验清单结构，并按需校验选中的分区文件（只按清单，不扫目录）。

    `partitions=None` 用于基线/发布前的全量校验；reader 传入已筛选的条目，避免
    每个窄查询都重新读取并哈希整个湖。
    """
    root = Path(root)
    _validate_manifest_shape(root, manifest)
    selected = manifest.get("partitions", []) if partitions is None else partitions
    for partition in selected:
        rel = partition["path"]
        path = _safe_artifact_path(
            root, rel, manifest["dataset"], partition["logical_partition_key"]
        )
        if not path.is_file():
            raise ManifestIntegrityError(f"清单内文件缺失: {rel}")
        size = path.stat().st_size
        if size != partition["bytes"]:
            raise ManifestIntegrityError(
                f"清单内文件字节数不符: {rel}（清单 {partition['bytes']}，实际 {size}）"
            )
        actual = file_sha256(path)
        if actual != partition["sha256"]:
            raise ManifestIntegrityError(f"清单内文件 sha256 不符: {rel}")


def compute_value_digest(spec: DatasetSpec, partitions: list[dict[str, Any]]) -> str:
    """对 canonical JSON（dataset + registry 投影 + 排序后分区摘要）取 SHA-256。"""
    ordered = sorted(partitions, key=lambda p: canonical_key(p["logical_partition_key"]))
    payload = {
        "dataset": spec.name,
        "projection": [
            {"name": col.name, "logical_type": col.logical_type} for col in spec.projection
        ],
        "partitions": [
            {
                "logical_partition_key": p["logical_partition_key"],
                "rows": p["rows"],
                "time_min": p["time_min"],
                "time_max": p["time_max"],
                "row_digest": p["row_digest"],
            }
            for p in ordered
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return DIGEST_PREFIX + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def verify_value_digest(spec: DatasetSpec, manifest: dict[str, Any]) -> str:
    declared = manifest.get("value_digest")
    if not declared:
        raise ManifestIntegrityError(f"{manifest.get('data_version')}: value_digest 缺失")
    recomputed = compute_value_digest(spec, manifest.get("partitions", []))
    if declared != recomputed:
        raise ManifestIntegrityError(
            f"{manifest['data_version']}: value_digest 重算不符"
            f"（manifest {declared}，重算 {recomputed}）"
        )
    return declared


def synthesize_partitions(
    baseline: list[dict[str, Any]], produced: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """基线全量继承 + 本轮按逻辑分区键整项替换/追加，按规范化键排序。"""
    merged = {canonical_key(p["logical_partition_key"]): dict(p) for p in baseline}
    for partition in produced:
        merged[canonical_key(partition["logical_partition_key"])] = dict(partition)
    return sorted(merged.values(), key=lambda p: canonical_key(p["logical_partition_key"]))


def synthesize_skipped(
    baseline: list[dict[str, Any]],
    produced_keys: list[dict[str, str]],
    empty_keys: list[dict[str, str]],
) -> list[dict[str, str]]:
    """skipped 与 partitions 同一继承/替换（F002-R3-03）。

    本轮覆盖到的键（产出分区或判定为空）按本轮结果移除/加入；未碰的键原样
    继承。清单里只有存在的分区，「本该有却没有」的键无法从清单反推。
    """
    touched = {canonical_key(k) for k in (*produced_keys, *empty_keys)}
    merged = {canonical_key(k): dict(k) for k in baseline if canonical_key(k) not in touched}
    for key in empty_keys:
        merged[canonical_key(key)] = dict(key)
    return [merged[k] for k in sorted(merged)]


def partition_diff(
    baseline: list[dict[str, Any]], current: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """修订分区差异清单：changed / added / removed（仅全量校验模式填写）。"""
    baseline_by_key = {canonical_key(p["logical_partition_key"]): p for p in baseline}
    current_by_key = {canonical_key(p["logical_partition_key"]): p for p in current}
    diff: list[dict[str, Any]] = []
    for key, partition in current_by_key.items():
        entry = dict(partition["logical_partition_key"])
        if key not in baseline_by_key:
            diff.append({**entry, "reason": "added"})
        elif any(
            partition[f] != baseline_by_key[key].get(f)
            for f in ("rows", "time_min", "time_max", "row_digest")
        ):
            diff.append({**entry, "reason": "changed"})
    for key, partition in baseline_by_key.items():
        if key not in current_by_key:
            diff.append({**partition["logical_partition_key"], "reason": "removed"})
    diff.sort(key=lambda d: canonical_key({k: str(v) for k, v in d.items() if k != "reason"}))
    return diff


def partitions_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    fields = ("rows", "time_min", "time_max", "row_digest")
    return all(left[f] == right[f] for f in fields)


def metadata_changed(
    baseline: dict[str, Any] | None,
    symbol_map_digest: str,
    flagged: list[str],
    flagged_total: int,
    excluded_null: int,
) -> bool:
    """判断不属于 partitions 的版本元数据是否相对基线变化。"""
    if baseline is None:
        return False
    quality = baseline.get("quality", {})
    return (
        symbol_map_digest != baseline.get("symbol_map_digest")
        or flagged != quality.get("flagged_partitions", [])
        or flagged_total != quality.get("unresolved_total", 0)
        or excluded_null != baseline.get("excluded_null_event_time", 0)
    )


def publish_manifest(root: Path, manifest: dict[str, Any]) -> Path:
    """原子发布：优先 hard-link；不支持时用 O_EXCL，任何情况下不覆盖。"""
    try:
        require_dataset(manifest["dataset"])
        parse_data_version(manifest["data_version"])
    except (KeyError, TypeError, UnknownDatasetError, VersionNotFoundError) as exc:
        raise ManifestIntegrityError(f"无法发布非法 manifest 身份: {manifest!r}") from exc
    _validate_manifest_shape(Path(root), manifest)
    directory = paths.manifests_dir(root, manifest["dataset"])
    directory.mkdir(parents=True, exist_ok=True)
    final = paths.manifest_path(root, manifest["dataset"], manifest["data_version"])
    if final.exists():
        raise ManifestIntegrityError(f"manifest 已存在且不可覆盖: {final}")
    tmp = final.with_name(f"{final.name}.tmp-{os.getpid()}")
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        # 同目录 hard-link 是原子且不覆盖已有文件；防止重试/并发重写已发布版本。
        try:
            os.link(tmp, final)
        except FileExistsError as exc:
            raise ManifestIntegrityError(f"manifest 已存在且不可覆盖: {final}") from exc
        except OSError as exc:
            if exc.errno not in {errno.EXDEV, errno.EPERM, errno.EOPNOTSUPP}:
                raise
            fd = os.open(final, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(fd, "wb") as target, tmp.open("rb") as source:
                target.write(source.read())
                target.flush()
                os.fsync(target.fileno())
    except FileExistsError as exc:
        raise ManifestIntegrityError(f"manifest 已存在且不可覆盖: {final}") from exc
    finally:
        tmp.unlink(missing_ok=True)
    return final


def usable_baseline(root: Path, dataset: str) -> tuple[str | None, dict[str, Any] | None]:
    """取最新**可用**基线：`status=valid` 且清单内文件齐备。

    损坏版本（分区文件缺失/字节数或 sha256 不符）不能当继承来源，否则一次损坏就让
    此后所有导出都跑不动（2026-09-24 实测：`ohlcv_1m@v2026.09.21` 缺 12 个
    `date=2026-09-18/19` 分区文件 → 全量导出 `ManifestIntegrityError` 中断，缺失分区
    永无机会重建）。故从新到旧跳过损坏版本、回退到更早可用版本；损坏版本本身
    **对直读它的消费方仍 fail-closed**（`load_manifest`/校验语义未变）。
    """
    for version in reversed(list_versions(root, dataset)):
        try:
            manifest = load_manifest(root, dataset, version)
        except VersionNotFoundError:
            logger.warning("基线 %s@%s 的 manifest 读不到，跳过", dataset, version)
            continue
        if manifest["status"] != "valid":
            continue
        try:
            validate_manifest_integrity(root, manifest)
            verify_value_digest(require_dataset(dataset), manifest)
        except (ManifestIntegrityError, ValueError) as exc:
            logger.warning(
                "基线 %s@%s 完整性校验未通过（%s），回退到更早版本", dataset, version, exc
            )
            continue
        return version, manifest
    return None, None
