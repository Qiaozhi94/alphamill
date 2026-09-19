"""ResearchSnapshot builder/reader（ADR-0007；F007 `DR-001`/`DR-006`，任务 T001）。

契约（ADR-0007「决策」第 2/3 条，字段名冻结）：

```text
ResearchSnapshot = {
  schema_version, snapshot_id, cutoff_time,
  members: {<dataset>: {data_version, value_digest, as_of_fidelity,
                        event_time_min, event_time_max}},
  symbol_map_digest, universe_digest, calendar_digest, universe_calendar_digest,
  provenance: {created_at, artifact_path, member_manifest_paths,
               symbol_map_path, universe_path, calendar_path}
}
```

本模块负责**冻结与持久化**；身份规则见 `identity`，calendar 契约见 `universe_calendar`，
F008 universe 消费面见 `evaluation.universe_ledger`。

不变量：

- canonical 禁止动态 latest：`allow_latest=False`（默认）时任何 `None` 版本成员即拒绝；
  preview 的 `--latest` 必须先在**构造输入阶段**解析并冻结成快照，再开始计算（ADR-0007 决策 5）。
- universe 与 calendar **分别**校验内容摘要，不合并成单一输入文件（`DR-006`）。
- 失败关闭：成员缺失、版本 invalid、`value_digest` 重算不符、分区文件完整性不符、覆盖范围
  不足、as-of 保真度不满足声明用途、symbol/universe/calendar 摘要缺失，均不得发布快照。
- 已发布对象不原地修改；同 ID 重复发布必须逐字节幂等。
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import registry, symbol_map
from alphamill.data_bridge.manifest import iso_utc
from alphamill.experiment_store.errors import (
    SnapshotError,
    SnapshotInputError,
    SnapshotIntegrityError,
    SnapshotNotFoundError,
)
from alphamill.experiment_store.identity import (
    DIGEST_RE,
    SCHEMA_VERSION,
    ResearchSnapshot,
    SnapshotMember,
    canonical_json,
    compute_snapshot_id,
    content_digest,
    members_payload,
    parse_utc,
    universe_calendar_digest,
)
from alphamill.experiment_store.paths import (
    MANIFEST_NAME,
    atomic_create,
    calendar_artifact_path,
    reports_root,
    snapshot_dir,
)
from alphamill.experiment_store.universe_calendar import (
    CALENDAR_SCHEMA_VERSION,
    calendar_covers,
    freeze_calendar,
    validate_calendar,
)

__all__ = [
    "CALENDAR_SCHEMA_VERSION",
    "DIGEST_RE",
    "MANIFEST_NAME",
    "SCHEMA_VERSION",
    "ResearchSnapshot",
    "SnapshotError",
    "SnapshotInputError",
    "SnapshotIntegrityError",
    "SnapshotMember",
    "SnapshotNotFoundError",
    "build_snapshot",
    "calendar_artifact_path",
    "calendar_covers",
    "canonical_json",
    "compute_snapshot_id",
    "content_digest",
    "freeze_calendar",
    "freeze_member",
    "freeze_members",
    "load_snapshot",
    "members_payload",
    "parse_utc",
    "publish_snapshot",
    "reports_root",
    "snapshot_dir",
    "universe_calendar_digest",
    "validate_calendar",
]


def freeze_member(
    lake_root: Path,
    dataset: str,
    data_version: str | None,
    *,
    cutoff: datetime,
    require_bitemporal: bool,
    allow_latest: bool,
) -> SnapshotMember:
    """把一个 dataset 冻结成不可变成员引用；`data_version=None` 仅在 allow_latest 时解析 latest。"""
    spec = registry.require_dataset(dataset)
    if data_version is None:
        if not allow_latest:
            raise SnapshotInputError(
                f"canonical/显式快照禁止动态 latest：{dataset} 必须给出 data_version"
            )
        try:
            data_version = mf.latest_valid_version(lake_root, dataset)
        except Exception as exc:  # noqa: BLE001 - 统一映射为输入不可解析
            raise SnapshotInputError(f"{dataset} 无 valid 版本可冻结: {exc}") from exc

    try:
        manifest = mf.load_manifest(lake_root, dataset, data_version)
    except Exception as exc:  # noqa: BLE001 - 版本缺失/清单损坏都是输入不可解析
        raise SnapshotInputError(f"{dataset}/{data_version} manifest 不可解析: {exc}") from exc
    if manifest.get("status") != "valid":
        raise SnapshotInputError(f"{dataset}/{data_version} 不是 valid 版本，拒绝冻结")

    try:
        value_digest = mf.verify_value_digest(spec, manifest)
        mf.validate_manifest_integrity(lake_root, manifest)
    except Exception as exc:  # noqa: BLE001 - 摘要/完整性不符一律 fail-closed
        raise SnapshotInputError(f"{dataset}/{data_version} 完整性校验失败: {exc}") from exc

    fidelity = manifest.get("as_of_fidelity", spec.as_of_fidelity)
    if require_bitemporal and fidelity != registry.AS_OF_BITEMPORAL:
        raise SnapshotInputError(
            f"{dataset}/{data_version} as_of_fidelity={fidelity}，不满足双时间轴用途"
        )

    populated = [p for p in manifest.get("partitions", []) if p.get("rows", 0) > 0]
    if not populated:
        raise SnapshotInputError(f"{dataset}/{data_version} 无有效分区，覆盖范围不足")
    event_min = min(parse_utc(p["time_min"], "time_min") for p in populated)
    event_max = max(parse_utc(p["time_max"], "time_max") for p in populated)
    if not (event_min <= cutoff <= event_max):
        raise SnapshotInputError(
            f"{dataset}/{data_version} 未覆盖 cutoff（数据 [{event_min.isoformat()}, "
            f"{event_max.isoformat()}] vs cutoff {cutoff.isoformat()}）"
        )
    return SnapshotMember(
        dataset=dataset,
        data_version=data_version,
        value_digest=value_digest,
        as_of_fidelity=fidelity,
        event_time_min=iso_utc(event_min),
        event_time_max=iso_utc(event_max),
    )


def freeze_members(
    lake_root: Path,
    datasets: Mapping[str, str | None],
    *,
    cutoff: datetime,
    require_bitemporal: bool = True,
    allow_latest: bool = False,
) -> dict[str, SnapshotMember]:
    if not datasets:
        raise SnapshotInputError("快照至少需要一个成员 dataset")
    return {
        name: freeze_member(
            lake_root,
            name,
            version,
            cutoff=cutoff,
            require_bitemporal=require_bitemporal,
            allow_latest=allow_latest,
        )
        for name, version in datasets.items()
    }


def build_snapshot(
    *,
    lake_root: Path,
    root: Path,
    cutoff: datetime,
    datasets: Mapping[str, str | None],
    universe_digest: str,
    calendar: Mapping[str, Any],
    symbol_map_digest: str,
    require_bitemporal: bool = True,
    allow_latest: bool = False,
    created_at: datetime | None = None,
) -> ResearchSnapshot:
    """构造（不发布）一个 ResearchSnapshot；任何校验失败均 fail-closed。"""
    from alphamill.evaluation.upstream_contracts import load_universe

    if cutoff.tzinfo is None:
        raise SnapshotInputError("cutoff 必须带时区（UTC）")
    cutoff_utc = cutoff.astimezone(UTC)

    if not DIGEST_RE.fullmatch(symbol_map_digest or ""):
        raise SnapshotInputError(f"symbol_map digest 缺失或格式非法: {symbol_map_digest!r}")
    try:
        symbol_map.load_symbol_map(symbol_map_digest, lake_root)
    except Exception as exc:  # noqa: BLE001 - 摘要不符即失败关闭
        raise SnapshotInputError(f"symbol_map artifact 校验失败: {exc}") from exc

    try:
        universe = load_universe(universe_digest, lake_root)
    except Exception as exc:  # noqa: BLE001 - F008 台账缺失/digest 不符即失败关闭
        raise SnapshotInputError(f"universe artifact 校验失败: {exc}") from exc

    members = freeze_members(
        lake_root,
        datasets,
        cutoff=cutoff_utc,
        require_bitemporal=require_bitemporal,
        allow_latest=allow_latest,
    )
    calendar_digest, calendar_logical = freeze_calendar(root, calendar)
    combined = universe_calendar_digest(universe.digest, calendar_digest)
    cutoff_text = iso_utc(cutoff_utc)
    snapshot_id = compute_snapshot_id(
        schema_version=SCHEMA_VERSION,
        cutoff_time=cutoff_text,
        members=members,
        symbol_map_digest=symbol_map_digest,
        combined_digest=combined,
    )
    provenance = {
        "created_at": iso_utc(created_at or datetime.now(UTC)),
        "artifact_path": f"reports/research_snapshots/{snapshot_id}/{MANIFEST_NAME}",
        "member_manifest_paths": {
            name: f"lake/_manifests/{name}/{members[name].data_version}.json"
            for name in sorted(members)
        },
        "symbol_map_path": f"lake/_metadata/symbol_maps/{symbol_map_digest}.csv",
        "universe_path": f"lake/_metadata/universes/{universe.digest}.json",
        "calendar_path": calendar_logical,
    }
    return ResearchSnapshot(
        schema_version=SCHEMA_VERSION,
        snapshot_id=snapshot_id,
        cutoff_time=cutoff_text,
        members=members,
        symbol_map_digest=symbol_map_digest,
        universe_digest=universe.digest,
        calendar_digest=calendar_digest,
        universe_calendar_digest=combined,
        provenance=provenance,
    )


def _semantic_fields(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "provenance"}


def publish_snapshot(root: Path, snapshot: ResearchSnapshot) -> Path:
    """原子发布快照 manifest；同 ID 幂等（**语义**一致即成功，先写者胜），语义冲突即拒绝。

    `provenance.created_at` 是墙钟时间，不参与身份，因此不能作为幂等判据——否则同一语义的
    快照每次重跑都会「冲突」。判据取除 provenance 外的语义字段。
    """
    candidate = snapshot.to_dict()
    payload = (json.dumps(candidate, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    final = snapshot_dir(root, snapshot.snapshot_id) / MANIFEST_NAME
    if final.is_file():
        try:
            existing = json.loads(final.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise SnapshotIntegrityError(f"同 snapshot_id 已有产物损坏: {final}: {exc}") from exc
        if _semantic_fields(existing) != _semantic_fields(candidate):
            raise SnapshotIntegrityError(f"同 snapshot_id 语义不一致，拒绝覆盖: {final}")
        return final
    atomic_create(final, payload)
    return final


def load_snapshot(root: Path, snapshot_id: str) -> ResearchSnapshot:
    """按已发布 snapshot_id 读取并重算身份；canonical 只走这条路径（不接受 latest）。"""
    if not DIGEST_RE.fullmatch(snapshot_id or ""):
        raise SnapshotInputError(
            f"snapshot_id 格式非法（canonical 只接受已发布 ID）: {snapshot_id!r}"
        )
    path = snapshot_dir(root, snapshot_id) / MANIFEST_NAME
    if not path.is_file():
        raise SnapshotNotFoundError(f"ResearchSnapshot 不存在: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SnapshotIntegrityError(f"snapshot manifest JSON 损坏: {path}: {exc}") from exc
    snapshot = ResearchSnapshot.from_dict(payload)
    if snapshot.snapshot_id != snapshot_id:
        raise SnapshotIntegrityError(
            f"snapshot_id 与目录不符: 目录 {snapshot_id}，内容 {snapshot.snapshot_id}"
        )
    recomputed = compute_snapshot_id(
        schema_version=snapshot.schema_version,
        cutoff_time=snapshot.cutoff_time,
        members=snapshot.members,
        symbol_map_digest=snapshot.symbol_map_digest,
        combined_digest=snapshot.universe_calendar_digest,
    )
    if recomputed != snapshot_id:
        raise SnapshotIntegrityError(f"snapshot 语义摘要重算不符: {snapshot_id}")
    combined = universe_calendar_digest(snapshot.universe_digest, snapshot.calendar_digest)
    if combined != snapshot.universe_calendar_digest:
        raise SnapshotIntegrityError(f"universe_calendar_digest 组合公式校验失败: {snapshot_id}")
    return snapshot
