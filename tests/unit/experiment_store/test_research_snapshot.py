"""T001 / `DR-001`·`DR-006`·`AC-006`：ResearchSnapshot 身份、冻结与发布的正反两面测试。

覆盖：路径/创建时间无关的身份稳定、成员变化必产生新 ID、universe 与 calendar 两个独立
artifact 的冻结组合公式、canonical 禁止动态 latest、preview latest 先冻结、invalid/覆盖不足/
保真度不足的失败关闭、同 ID 幂等发布与篡改检测。
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import registry, symbol_map
from alphamill.evaluation.universe_ledger import UniverseMember, publish_universe
from alphamill.experiment_store import research_snapshot as rs
from alphamill.experiment_store.errors import (
    SnapshotInputError,
    SnapshotIntegrityError,
    SnapshotNotFoundError,
)
from alphamill.experiment_store.identity import (
    canonical_json,
    content_digest,
    universe_calendar_digest,
)

DAY = "2026-09-01"
DAY2 = "2026-09-02"
VERSION = "v2026.09.01"
VERSION2 = "v2026.09.02"
CUTOFF = datetime(2026, 9, 1, 6, 0, tzinfo=UTC)
CUTOFF_LATE = datetime(2026, 9, 1, 18, 0, tzinfo=UTC)
CUTOFF_DAY2 = datetime(2026, 9, 2, 12, 0, tzinfo=UTC)
DATASET = "derivatives_funding_rates"
CALENDAR = {
    "schema_version": 1,
    "timezone": "UTC",
    "windows": [{"start": "2026-09-01T00:00:00Z", "end": "2026-09-30T00:00:00Z"}],
}


def _add_version(root: Path, dataset: str, version: str, day: str, rows: int) -> None:
    spec = registry.require_dataset(dataset)
    payload = b"x" * 10
    rel = f"{dataset}/exchange=binance/pair=BTC-USDT/date={day}.r1.parquet"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    partition = {
        "logical_partition_key": {"exchange": "binance", "pair": "BTC-USDT", "date": day},
        "path": rel,
        "rows": rows,
        "time_min": f"{day}T00:00:00Z",
        "time_max": f"{day}T23:59:00Z",
        "row_digest": "sha256:" + "a" * 64,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    mf.publish_manifest(
        root,
        {
            "dataset": dataset,
            "data_version": version,
            "status": "valid",
            "rows": rows,
            "value_digest": mf.compute_value_digest(spec, [partition]),
            "partitions": [partition],
        },
    )


def make_lake(
    tmp_path: Path, *, dataset: str = DATASET, rows: int = 10, status: str = "valid"
) -> Path:
    root = tmp_path / "lake"
    _add_version(root, dataset, VERSION, DAY, rows)
    if status != "valid":
        manifest = mf.load_manifest(root, dataset, VERSION)
        manifest["status"] = status
        (root / "_manifests" / dataset / f"{VERSION}.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
    return root


def make_symbol_map(root: Path) -> str:
    frame = symbol_map.build_symbol_map([symbol_map.SymbolRow("binance", "perp", "BTC/USDT")])
    payload = symbol_map.canonical_csv_bytes(frame)
    digest = symbol_map.content_digest(payload)
    target = root / "_metadata" / "symbol_maps" / f"{digest}.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return digest


def make_universe(root: Path) -> str:
    return publish_universe(
        [
            UniverseMember(
                lake_pair="BTC-USDT-PERP",
                valid_from=datetime(2026, 8, 1, tzinfo=UTC),
                valid_to=None,
            )
        ],
        root,
    )


def build(
    tmp_path: Path,
    *,
    dataset: str = DATASET,
    rows: int = 10,
    status: str = "valid",
    cutoff: datetime = CUTOFF,
    calendar: dict | None = None,
    universe_digest: str | None = None,
    symbol_map_digest: str | None = None,
    require_bitemporal: bool = True,
    allow_latest: bool = False,
    datasets: dict | None = None,
):
    lake = make_lake(tmp_path, dataset=dataset, rows=rows, status=status)
    return rs.build_snapshot(
        lake_root=lake,
        root=tmp_path / "reports",
        cutoff=cutoff,
        datasets=datasets if datasets is not None else {dataset: VERSION},
        universe_digest=universe_digest or make_universe(lake),
        calendar=CALENDAR if calendar is None else calendar,
        symbol_map_digest=symbol_map_digest or make_symbol_map(lake),
        require_bitemporal=require_bitemporal,
        allow_latest=allow_latest,
    )


# ---------- 身份 ----------


def test_snapshot_id_is_stable_across_paths(tmp_path):
    first = build(tmp_path / "a")
    second = build(tmp_path / "b")
    assert first.snapshot_id == second.snapshot_id
    assert first.members == second.members


def test_member_change_produces_new_id(tmp_path):
    base = build(tmp_path / "a", rows=10)
    changed = build(tmp_path / "b", rows=11)
    assert base.snapshot_id != changed.snapshot_id


def test_cutoff_change_produces_new_id(tmp_path):
    early = build(tmp_path / "a", cutoff=CUTOFF)
    late = build(tmp_path / "b", cutoff=CUTOFF_LATE)
    assert early.snapshot_id != late.snapshot_id


def test_universe_calendar_digest_uses_frozen_combination_formula(tmp_path):
    snapshot = build(tmp_path)
    expected = content_digest(
        canonical_json(
            {"universe": snapshot.universe_digest, "calendar": snapshot.calendar_digest}
        ).encode("utf-8")
    )
    assert (
        snapshot.universe_calendar_digest
        == expected
        == universe_calendar_digest(snapshot.universe_digest, snapshot.calendar_digest)
    )


def test_identity_payload_is_only_semantic_fields(tmp_path):
    snapshot = build(tmp_path)
    payload = {
        "schema_version": snapshot.schema_version,
        "cutoff_time": snapshot.cutoff_time,
        "members": rs.members_payload(snapshot.members),
        "symbol_map_digest": snapshot.symbol_map_digest,
        "universe_calendar_digest": snapshot.universe_calendar_digest,
    }
    assert set(payload) == {
        "schema_version",
        "cutoff_time",
        "members",
        "symbol_map_digest",
        "universe_calendar_digest",
    }
    assert (
        rs.compute_snapshot_id(
            schema_version=snapshot.schema_version,
            cutoff_time=snapshot.cutoff_time,
            members=snapshot.members,
            symbol_map_digest=snapshot.symbol_map_digest,
            combined_digest=snapshot.universe_calendar_digest,
        )
        == snapshot.snapshot_id
    )


# ---------- latest 与失败关闭 ----------


def test_canonical_forbids_dynamic_latest(tmp_path):
    lake = make_lake(tmp_path)
    with pytest.raises(SnapshotInputError, match="latest"):
        rs.freeze_members(lake, {DATASET: None}, cutoff=CUTOFF, allow_latest=False)


def test_preview_latest_freezes_resolved_version(tmp_path):
    lake = make_lake(tmp_path)
    _add_version(lake, DATASET, VERSION2, DAY2, rows=11)
    frozen = rs.freeze_members(lake, {DATASET: None}, cutoff=CUTOFF_DAY2, allow_latest=True)
    assert frozen[DATASET].data_version == VERSION2


def test_invalid_member_is_rejected(tmp_path):
    with pytest.raises(SnapshotInputError, match="valid 版本"):
        build(tmp_path, status="invalid")


def test_coverage_insufficient_is_rejected(tmp_path):
    lake = make_lake(tmp_path)
    with pytest.raises(SnapshotInputError, match="覆盖"):
        rs.freeze_members(
            lake,
            {DATASET: VERSION},
            cutoff=datetime(2026, 10, 1, tzinfo=UTC),
            allow_latest=False,
        )


def test_bitemporal_fidelity_required(tmp_path):
    lake = make_lake(tmp_path, dataset="ohlcv_1m")
    with pytest.raises(SnapshotInputError, match="as_of_fidelity"):
        rs.freeze_members(lake, {"ohlcv_1m": VERSION}, cutoff=CUTOFF, require_bitemporal=True)


def test_missing_universe_artifact_is_rejected(tmp_path):
    with pytest.raises(SnapshotInputError, match="universe"):
        build(tmp_path, universe_digest="sha256:" + "9" * 64)


def test_symbol_map_digest_mismatch_is_rejected(tmp_path):
    with pytest.raises(SnapshotInputError, match="symbol_map"):
        build(tmp_path, symbol_map_digest="sha256:" + "9" * 64)


def test_calendar_schema_is_validated(tmp_path):
    broken = {"schema_version": 1, "timezone": "UTC", "windows": []}
    with pytest.raises(SnapshotInputError, match="windows"):
        build(tmp_path, calendar=broken)


def test_calendar_missing_digest_fields_rejected(tmp_path):
    with pytest.raises(SnapshotInputError):
        universe_calendar_digest("", "sha256:" + "b" * 64)


# ---------- 发布与读取 ----------


def test_publish_is_idempotent_and_load_roundtrips(tmp_path):
    snapshot = build(tmp_path)
    root = tmp_path / "reports"
    assert rs.publish_snapshot(root, snapshot) == rs.publish_snapshot(root, snapshot)
    assert rs.load_snapshot(root, snapshot.snapshot_id).to_dict() == snapshot.to_dict()


def test_republish_with_different_created_at_is_idempotent(tmp_path):
    """provenance.created_at 是墙钟时间、不参与身份，因此不能作为幂等判据。"""
    lake = make_lake(tmp_path)
    root = tmp_path / "reports"
    kwargs = {
        "lake_root": lake,
        "root": root,
        "cutoff": CUTOFF,
        "datasets": {DATASET: VERSION},
        "universe_digest": make_universe(lake),
        "calendar": CALENDAR,
        "symbol_map_digest": make_symbol_map(lake),
    }
    first = rs.build_snapshot(**kwargs, created_at=datetime(2026, 1, 1, tzinfo=UTC))
    second = rs.build_snapshot(**kwargs, created_at=datetime(2026, 6, 1, tzinfo=UTC))
    assert first.snapshot_id == second.snapshot_id
    path = rs.publish_snapshot(root, first)
    assert rs.publish_snapshot(root, second) == path
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["provenance"]["created_at"] == first.provenance["created_at"]
    assert rs.load_snapshot(root, first.snapshot_id).to_dict() == first.to_dict()


def test_semantically_conflicting_republish_is_rejected(tmp_path):
    snapshot = build(tmp_path)
    root = tmp_path / "reports"
    path = rs.publish_snapshot(root, snapshot)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["members"][DATASET]["value_digest"] = "sha256:" + "e" * 64
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError, match="语义不一致"):
        rs.publish_snapshot(root, snapshot)


def test_tampered_snapshot_is_detected(tmp_path):
    snapshot = build(tmp_path)
    root = tmp_path / "reports"
    path = rs.publish_snapshot(root, snapshot)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["cutoff_time"] = "2027-01-01T00:00:00Z"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError, match="重算不符"):
        rs.load_snapshot(root, snapshot.snapshot_id)


def test_unknown_snapshot_id_is_not_found(tmp_path):
    with pytest.raises(SnapshotNotFoundError):
        rs.load_snapshot(tmp_path / "reports", "sha256:" + "0" * 64)


def test_load_rejects_non_digest_id(tmp_path):
    with pytest.raises(SnapshotInputError, match="格式非法"):
        rs.load_snapshot(tmp_path / "reports", "latest")
