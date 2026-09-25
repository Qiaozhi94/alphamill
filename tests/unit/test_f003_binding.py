"""F003 T001/T002/T009 的快照绑定与宇宙台账契约（FR-003 / DR-001 / AC-003）。"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from alphamill.data_bridge import digest as lake_digest
from alphamill.data_bridge import manifest, partitions, symbol_map
from alphamill.data_bridge import paths as lake_paths
from alphamill.data_bridge.registry import require_dataset
from alphamill.factor_factory.canonical import (
    JSONValue,
    canonical_json_bytes,
    sha256_prefixed_bytes,
)
from alphamill.factor_factory.errors import (
    BindingValidationError,
    SchemaValidationError,
    SnapshotResolverUnavailableError,
)
from alphamill.factor_factory.generators.binding import (
    ArtifactRef,
    BindingProvenance,
    DatasetBinding,
    ExplicitSnapshotBinding,
    SnapshotRefBinding,
    ValidatedBinding,
    binding_to_dict,
    load_binding_file,
    parse_binding,
    validate_binding,
)
from alphamill.factor_factory.generators.universe import (
    UniverseLedger,
    UniverseMembership,
    load_explicit_universe,
)


def _write_payload(tmp_path: Path, payload: JSONValue, *, indent: int | None = None) -> Path:
    path = tmp_path / "universe.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=indent), encoding="utf-8")
    return path


def _digest(payload: JSONValue) -> str:
    return sha256_prefixed_bytes(canonical_json_bytes(payload))


def test_valid_ledger_loads_with_canonical_digest(tmp_path: Path) -> None:
    payload: JSONValue = {
        "members": [
            {
                "valid_to": None,
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-01T00:00:00Z",
            }
        ],
        "schema_version": 1,
    }
    expected_digest = _digest(payload)
    path = _write_payload(tmp_path, payload, indent=2)

    ledger = load_explicit_universe(
        path,
        expected_digest=expected_digest,
        expected_schema_version=1,
    )

    assert ledger.digest == expected_digest
    assert ledger.schema_version == 1
    assert ledger.memberships == (
        UniverseMembership(
            lake_pair="BTC-USDT",
            valid_from=datetime(2026, 1, 1, tzinfo=UTC),
            valid_to=None,
        ),
    )


def test_schema_version_mismatch_is_rejected(tmp_path: Path) -> None:
    payload: JSONValue = {"schema_version": 1, "members": []}
    path = _write_payload(tmp_path, payload)

    with pytest.raises(SchemaValidationError, match="schema_version"):
        load_explicit_universe(
            path,
            expected_digest=_digest(payload),
            expected_schema_version=2,
        )


def test_unknown_top_level_key_is_rejected(tmp_path: Path) -> None:
    payload: JSONValue = {"schema_version": 1, "members": [], "current_members": []}
    path = _write_payload(tmp_path, payload)

    with pytest.raises(SchemaValidationError, match="top-level"):
        load_explicit_universe(
            path,
            expected_digest=_digest(payload),
            expected_schema_version=1,
        )


def test_tampered_members_are_rejected_by_stale_digest(tmp_path: Path) -> None:
    original: JSONValue = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_to": None,
            }
        ],
    }
    tampered: JSONValue = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_to": "2026-02-01T00:00:00Z",
            }
        ],
    }
    path = _write_payload(tmp_path, tampered)

    with pytest.raises(BindingValidationError, match="digest"):
        load_explicit_universe(
            path,
            expected_digest=_digest(original),
            expected_schema_version=1,
        )


def test_universe_at_uses_half_open_pit_boundaries(tmp_path: Path) -> None:
    payload: JSONValue = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-02T00:00:00Z",
                "valid_to": "2026-01-04T00:00:00Z",
            },
            {
                "lake_pair": "ETH-USDT",
                "valid_from": "2026-01-03T00:00:00Z",
                "valid_to": None,
            },
        ],
    }
    path = _write_payload(tmp_path, payload)
    ledger = load_explicit_universe(
        path,
        expected_digest=_digest(payload),
        expected_schema_version=1,
    )

    assert ledger.universe_at(datetime(2026, 1, 1, tzinfo=UTC)) == frozenset()
    assert ledger.universe_at(datetime(2026, 1, 2, tzinfo=UTC)) == frozenset({"BTC-USDT"})
    assert ledger.universe_at(datetime(2026, 1, 3, tzinfo=UTC)) == frozenset(
        {"BTC-USDT", "ETH-USDT"}
    )
    assert ledger.universe_at(datetime(2026, 1, 4, tzinfo=UTC)) == frozenset({"ETH-USDT"})
    assert ledger.universe_at(datetime(2030, 1, 1, tzinfo=UTC)) == frozenset({"ETH-USDT"})


def test_pair_can_leave_and_reenter_in_non_overlapping_windows(tmp_path: Path) -> None:
    payload: JSONValue = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_to": "2026-01-02T00:00:00Z",
            },
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-03T00:00:00Z",
                "valid_to": "2026-01-04T00:00:00Z",
            },
        ],
    }
    path = _write_payload(tmp_path, payload)
    ledger = load_explicit_universe(
        path,
        expected_digest=_digest(payload),
        expected_schema_version=1,
    )

    assert ledger.universe_at(datetime(2026, 1, 1, 12, tzinfo=UTC)) == frozenset({"BTC-USDT"})
    assert ledger.universe_at(datetime(2026, 1, 2, 12, tzinfo=UTC)) == frozenset()
    assert ledger.universe_at(datetime(2026, 1, 3, 12, tzinfo=UTC)) == frozenset({"BTC-USDT"})


def test_duplicate_overlapping_membership_is_rejected(tmp_path: Path) -> None:
    payload: JSONValue = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_to": "2026-01-04T00:00:00Z",
            },
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-03T00:00:00Z",
                "valid_to": None,
            },
        ],
    }
    path = _write_payload(tmp_path, payload)

    with pytest.raises(SchemaValidationError, match="overlapping"):
        load_explicit_universe(
            path,
            expected_digest=_digest(payload),
            expected_schema_version=1,
        )


def test_valid_from_after_valid_to_is_rejected(tmp_path: Path) -> None:
    payload: JSONValue = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-03T00:00:00Z",
                "valid_to": "2026-01-02T00:00:00Z",
            }
        ],
    }
    path = _write_payload(tmp_path, payload)

    with pytest.raises(SchemaValidationError, match="valid_from"):
        load_explicit_universe(
            path,
            expected_digest=_digest(payload),
            expected_schema_version=1,
        )


def test_naive_membership_timestamp_is_rejected(tmp_path: Path) -> None:
    payload: JSONValue = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-01T00:00:00",
                "valid_to": None,
            }
        ],
    }
    path = _write_payload(tmp_path, payload)

    with pytest.raises(SchemaValidationError, match="必须带时区"):
        load_explicit_universe(
            path,
            expected_digest=_digest(payload),
            expected_schema_version=1,
        )


def test_universe_at_rejects_naive_timestamp(tmp_path: Path) -> None:
    payload: JSONValue = {"schema_version": 1, "members": []}
    path = _write_payload(tmp_path, payload)
    ledger = load_explicit_universe(
        path,
        expected_digest=_digest(payload),
        expected_schema_version=1,
    )

    with pytest.raises(SchemaValidationError, match="UTC"):
        ledger.universe_at(datetime(2026, 1, 1))


def test_empty_members_yields_empty_universe(tmp_path: Path) -> None:
    payload: JSONValue = {"schema_version": 1, "members": []}
    path = _write_payload(tmp_path, payload)
    ledger = load_explicit_universe(
        path,
        expected_digest=_digest(payload),
        expected_schema_version=1,
    )

    assert ledger.universe_at(datetime(2026, 1, 1, tzinfo=UTC)) == frozenset()


def _build_explicit_binding(tmp_path: Path) -> ExplicitSnapshotBinding:
    lake_root = tmp_path / "lake"
    spec = require_dataset("signals_log")
    event_time = datetime(2026, 9, 11, 9, tzinfo=UTC)
    rows = [
        [
            event_time,
            "binance",
            "BTC/USDT",
            "placeholder",
            "buy",
            0.9,
            {},
            event_time,
            0.01,
            0.2,
            0.6,
            None,
            None,
        ]
    ]
    partition_path = lake_root / "signals_log/date=2026-09-11.r1.parquet"
    partition_path.parent.mkdir(parents=True)
    pq.write_table(partitions.rows_to_table(rows, spec), partition_path)

    mapping = symbol_map.build_symbol_map([symbol_map.SymbolRow("binance", "spot", "BTC/USDT")])
    mapping_payload = symbol_map.canonical_csv_bytes(mapping)
    symbol_digest = symbol_map.content_digest(mapping_payload)
    symbol_path = lake_paths.symbol_maps_dir(lake_root) / f"{symbol_digest}.csv"
    symbol_path.parent.mkdir(parents=True)
    symbol_path.write_bytes(mapping_payload)

    partition_entry = {
        "logical_partition_key": {"date": "2026-09-11"},
        "path": partition_path.relative_to(lake_root).as_posix(),
        "rows": 1,
        "time_min": "2026-09-11T09:00:00Z",
        "time_max": "2026-09-11T09:00:00Z",
        "row_digest": lake_digest.row_digest(rows, spec.projection),
        "bytes": partition_path.stat().st_size,
        "sha256": manifest.file_sha256(partition_path),
    }
    value_digest = manifest.compute_value_digest(spec, [partition_entry])
    manifest_path = manifest.publish_manifest(
        lake_root,
        {
            "dataset": "signals_log",
            "source": manifest.SOURCE_TAG,
            "data_version": "v2026.09.11",
            "status": "valid",
            "rows": 1,
            "value_digest": value_digest,
            "symbol_map_digest": symbol_digest,
            "partitions": [partition_entry],
        },
    )

    universe_payload: JSONValue = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_to": None,
            },
            {
                "lake_pair": "ETH-USDT",
                "valid_from": "2026-09-13T00:00:00Z",
                "valid_to": None,
            },
        ],
    }
    universe_digest = _digest(universe_payload)
    universe_path = tmp_path / "artifacts/universe" / f"{universe_digest}.json"
    universe_path.parent.mkdir(parents=True)
    universe_path.write_bytes(canonical_json_bytes(universe_payload))

    calendar_payload: JSONValue = {
        "schema_version": 1,
        "kind": "continuous_24_7",
        "timezone": "UTC",
    }
    calendar_digest = _digest(calendar_payload)
    calendar_path = tmp_path / "artifacts/calendar" / f"{calendar_digest}.json"
    calendar_path.parent.mkdir(parents=True)
    calendar_path.write_bytes(canonical_json_bytes(calendar_payload))

    universe_calendar_digest = _digest({"universe": universe_digest, "calendar": calendar_digest})
    artifact_path = tmp_path / "artifacts/bindings" / f"{universe_calendar_digest}.json"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text("{}", encoding="utf-8")
    return ExplicitSnapshotBinding(
        mode="explicit_tuples",
        schema_version=1,
        cutoff_time=datetime(2026, 9, 12, tzinfo=UTC),
        members={
            "signals_log": DatasetBinding(
                data_version="v2026.09.11",
                value_digest=value_digest,
                as_of_fidelity="bitemporal",
                event_time_min=event_time,
                event_time_max=event_time,
            )
        },
        symbol_map_digest=symbol_digest,
        universe=ArtifactRef(digest=universe_digest, path=universe_path, schema_version=1),
        calendar=ArtifactRef(digest=calendar_digest, path=calendar_path, schema_version=1),
        universe_calendar_digest=universe_calendar_digest,
        provenance=BindingProvenance(
            created_at=datetime(2026, 9, 12, 1, tzinfo=UTC),
            artifact_path=artifact_path,
            member_manifest_paths={"signals_log": manifest_path},
            symbol_map_path=symbol_path,
            universe_path=universe_path,
            calendar_path=calendar_path,
        ),
    )


def test_explicit_binding_validates_against_real_fake_lake(tmp_path: Path) -> None:
    binding = _build_explicit_binding(tmp_path)

    validated = validate_binding(binding, lake_root=tmp_path / "lake")

    assert validated == ValidatedBinding(
        source=binding,
        resolved=binding,
        universe_ledger=validated.universe_ledger,
    )
    assert isinstance(validated.universe_ledger, UniverseLedger)


def test_validated_binding_exposes_pit_universe_for_pair_detection(tmp_path: Path) -> None:
    binding = _build_explicit_binding(tmp_path)

    validated = validate_binding(binding, lake_root=tmp_path / "lake")

    universe = validated.universe_ledger.universe_at(binding.cutoff_time)
    assert "BTC-USDT" in universe
    assert "ETH-USDT" not in universe


def test_binding_to_dict_round_trips_both_modes(tmp_path: Path) -> None:
    explicit = _build_explicit_binding(tmp_path)
    snapshot = SnapshotRefBinding(mode="snapshot", research_snapshot_id="snapshot-001")

    assert parse_binding(binding_to_dict(explicit)) == explicit
    assert parse_binding(binding_to_dict(snapshot)) == snapshot


def test_load_binding_file_uses_frozen_explicit_format(tmp_path: Path) -> None:
    binding = _build_explicit_binding(tmp_path)
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(binding_to_dict(binding)), encoding="utf-8")

    assert load_binding_file(path) == binding


def test_missing_dataset_version_is_rejected(tmp_path: Path) -> None:
    payload = binding_to_dict(_build_explicit_binding(tmp_path))
    members = payload["members"]
    assert isinstance(members, dict)
    member = members["signals_log"]
    assert isinstance(member, dict)
    del member["data_version"]

    with pytest.raises(BindingValidationError):
        parse_binding(payload)


def test_wrong_member_value_digest_is_rejected(tmp_path: Path) -> None:
    binding = _build_explicit_binding(tmp_path)
    member = binding.members["signals_log"]
    wrong = replace(
        binding,
        members={
            "signals_log": replace(member, value_digest="sha256:" + "f" * 64),
        },
    )

    with pytest.raises(BindingValidationError, match="value_digest"):
        validate_binding(wrong, lake_root=tmp_path / "lake")


def test_wrong_symbol_map_digest_is_rejected(tmp_path: Path) -> None:
    binding = _build_explicit_binding(tmp_path)
    wrong = replace(binding, symbol_map_digest="sha256:" + "f" * 64)

    with pytest.raises(BindingValidationError, match="symbol_map_digest"):
        validate_binding(wrong, lake_root=tmp_path / "lake")


def test_invalid_dataset_version_is_wrapped_with_cause(tmp_path: Path) -> None:
    binding = _build_explicit_binding(tmp_path)
    lake_root = tmp_path / "lake"
    source_manifest = manifest.load_manifest(lake_root, "signals_log", "v2026.09.11")
    invalid_manifest = dict(source_manifest)
    invalid_manifest["data_version"] = "v2026.09.12"
    invalid_manifest["status"] = "invalid"
    invalid_path = manifest.publish_manifest(lake_root, invalid_manifest)
    member = binding.members["signals_log"]
    wrong = replace(
        binding,
        members={"signals_log": replace(member, data_version="v2026.09.12")},
        provenance=replace(
            binding.provenance,
            member_manifest_paths={"signals_log": invalid_path},
        ),
    )

    with pytest.raises(BindingValidationError) as captured:
        validate_binding(wrong, lake_root=lake_root)

    assert captured.value.__cause__ is not None


def test_nonexistent_dataset_version_is_rejected(tmp_path: Path) -> None:
    binding = _build_explicit_binding(tmp_path)
    member = binding.members["signals_log"]
    wrong = replace(
        binding,
        members={"signals_log": replace(member, data_version="v2026.09.13")},
    )

    with pytest.raises(BindingValidationError):
        validate_binding(wrong, lake_root=tmp_path / "lake")


@pytest.mark.parametrize("artifact_name", ["universe", "calendar"])
def test_missing_semantic_artifact_is_rejected(tmp_path: Path, artifact_name: str) -> None:
    binding = _build_explicit_binding(tmp_path)
    artifact = binding.universe if artifact_name == "universe" else binding.calendar
    artifact.path.unlink()

    with pytest.raises(BindingValidationError):
        validate_binding(binding, lake_root=tmp_path / "lake")


@pytest.mark.parametrize(
    "calendar_payload",
    [
        {"schema_version": 1, "kind": "session", "timezone": "UTC"},
        {"schema_version": 1, "kind": "continuous_24_7", "timezone": "Asia/Shanghai"},
        {
            "schema_version": 1,
            "kind": "continuous_24_7",
            "timezone": "UTC",
            "weekends": True,
        },
    ],
)
def test_invalid_calendar_contract_is_rejected(
    tmp_path: Path, calendar_payload: dict[str, JSONValue]
) -> None:
    binding = _build_explicit_binding(tmp_path)
    binding.calendar.path.write_bytes(canonical_json_bytes(calendar_payload))

    with pytest.raises(BindingValidationError):
        validate_binding(binding, lake_root=tmp_path / "lake")


def test_wrong_universe_calendar_digest_is_rejected(tmp_path: Path) -> None:
    binding = _build_explicit_binding(tmp_path)
    wrong = replace(binding, universe_calendar_digest="sha256:" + "f" * 64)

    with pytest.raises(BindingValidationError, match="universe_calendar_digest"):
        validate_binding(wrong, lake_root=tmp_path / "lake")


@pytest.mark.parametrize(
    "payload",
    [
        {"mode": "snapshot", "research_snapshot_id": "snapshot-001", "latest": True},
        {"mode": "unsupported"},
    ],
)
def test_unknown_mode_or_top_level_key_is_rejected(payload: dict[str, object]) -> None:
    with pytest.raises(BindingValidationError):
        parse_binding(payload)


def test_unknown_explicit_top_level_key_is_rejected(tmp_path: Path) -> None:
    payload = binding_to_dict(_build_explicit_binding(tmp_path))
    payload["latest"] = True

    with pytest.raises(BindingValidationError):
        parse_binding(payload)


def test_unknown_binding_schema_version_is_rejected(tmp_path: Path) -> None:
    payload = binding_to_dict(_build_explicit_binding(tmp_path))
    payload["schema_version"] = 2

    with pytest.raises(BindingValidationError, match="schema_version"):
        parse_binding(payload)


def test_snapshot_binding_requires_resolver() -> None:
    binding = SnapshotRefBinding(mode="snapshot", research_snapshot_id="snapshot-001")

    with pytest.raises(SnapshotResolverUnavailableError):
        validate_binding(binding)


def test_snapshot_binding_resolves_and_validates(tmp_path: Path) -> None:
    explicit = _build_explicit_binding(tmp_path)
    source = SnapshotRefBinding(mode="snapshot", research_snapshot_id="snapshot-001")

    def resolve_snapshot(research_snapshot_id: str) -> ExplicitSnapshotBinding:
        assert research_snapshot_id == "snapshot-001"
        return explicit

    validated = validate_binding(
        source,
        lake_root=tmp_path / "lake",
        snapshot_resolver=resolve_snapshot,
    )

    assert validated.source == source
    assert validated.resolved == explicit
