from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path
from typing import TypeAlias

import pandas as pd
import pyarrow.parquet as pq
import pytest

from alphamill.data_bridge import digest, manifest, partitions, symbol_map
from alphamill.data_bridge import paths as lake_paths
from alphamill.data_bridge.reader import read
from alphamill.data_bridge.registry import require_dataset
from alphamill.factor_factory.canonical import (
    JSONValue,
    canonical_json_bytes,
    sha256_prefixed_bytes,
)
from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.generators.binding import (
    ArtifactRef,
    BindingProvenance,
    DatasetBinding,
    ExplicitSnapshotBinding,
    ValidatedBinding,
    validate_binding,
)
from alphamill.factor_factory.generators.lake_tensor import build_tensor
from alphamill.factor_factory.registry.factor_store import feature_map_digest

pytestmark = pytest.mark.integration

_VERSION = "v2026.01.01"
_START = datetime(2026, 1, 1, tzinfo=UTC)
RowValue: TypeAlias = datetime | JSONValue


@dataclass(frozen=True, slots=True)
class _PartitionData:
    key: dict[str, str]
    rows: tuple[tuple[RowValue, ...], ...]
    time_min: datetime
    time_max: datetime


@dataclass(frozen=True, slots=True)
class _FakeLake:
    root: Path
    binding: ValidatedBinding


def _candles(symbol: str, base: float) -> tuple[tuple[RowValue, ...], ...]:
    return tuple(
        (
            _START + timedelta(minutes=minute),
            "binance",
            symbol,
            base + minute,
            base + minute + 2,
            base + minute - 1,
            base + minute + 1,
            float(minute),
        )
        for minute in range(1, 121)
    )


def _write_artifact(root: Path, kind: str, payload: JSONValue) -> ArtifactRef:
    encoded = canonical_json_bytes(payload)
    artifact_digest = sha256_prefixed_bytes(encoded)
    path = root / "_metadata" / kind / f"{artifact_digest}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return ArtifactRef(digest=artifact_digest, path=path, schema_version=1)


@pytest.fixture
def fake_lake(tmp_path: Path) -> _FakeLake:
    mapping = symbol_map.build_symbol_map(
        [
            symbol_map.SymbolRow("binance", "spot", "BTC/USDT"),
            symbol_map.SymbolRow("binance", "spot", "ETH/USDT"),
        ]
    )
    map_payload = symbol_map.canonical_csv_bytes(mapping)
    map_digest = symbol_map.content_digest(map_payload)
    map_path = lake_paths.symbol_maps_dir(tmp_path) / f"{map_digest}.csv"
    map_path.parent.mkdir(parents=True)
    map_path.write_bytes(map_payload)

    ohlcv = [
        _PartitionData(
            key={"exchange": "binance", "pair": pair, "date": "2026-01-01"},
            rows=_candles(symbol, base),
            time_min=_START + timedelta(minutes=1),
            time_max=_START + timedelta(hours=2),
        )
        for pair, symbol, base in (
            ("BTC-USDT", "BTC/USDT", 100.0),
            ("ETH-USDT", "ETH/USDT", 200.0),
        )
    ]
    signal_rows: tuple[tuple[RowValue, ...], ...] = tuple(
        (
            at + timedelta(minutes=1),
            "binance",
            symbol,
            "fixture",
            "buy",
            confidence,
            {},
            at,
            confidence / 10,
            0.2,
            0.6,
            confidence / 20,
            at + timedelta(minutes=30),
        )
        for at, symbol, confidence in (
            (_START + timedelta(hours=1), "BTC/USDT", 0.8),
            (_START + timedelta(hours=1), "ETH/USDT", 0.7),
            (_START + timedelta(hours=2), "BTC/USDT", 0.9),
            (_START + timedelta(hours=2), "ETH/USDT", 0.6),
        )
    )
    signals = [
        _PartitionData(
            key={"date": "2026-01-01"},
            rows=signal_rows,
            time_min=_START + timedelta(hours=1),
            time_max=_START + timedelta(hours=2),
        )
    ]

    def publish(dataset: str, source: list[_PartitionData]) -> DatasetBinding:
        spec = require_dataset(dataset)
        entries: list[dict[str, JSONValue]] = []
        for item in source:
            rows = [list(row) for row in item.rows]
            path = lake_paths.partition_dir(tmp_path, dataset, item.key) / (
                f"date={item.key['date']}.r1.parquet"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            pq.write_table(partitions.rows_to_table(rows, spec), path)
            entries.append(
                {
                    "logical_partition_key": item.key,
                    "path": path.relative_to(tmp_path).as_posix(),
                    "rows": len(rows),
                    "time_min": manifest.iso_utc(item.time_min),
                    "time_max": manifest.iso_utc(item.time_max),
                    "row_digest": digest.row_digest(rows, spec.projection),
                    "bytes": path.stat().st_size,
                    "sha256": manifest.file_sha256(path),
                }
            )
        lake_manifest: dict[str, JSONValue] = {
            "dataset": dataset,
            "source": manifest.SOURCE_TAG,
            "data_version": _VERSION,
            "status": "valid",
            "rows": sum(entry["rows"] for entry in entries),
            "value_digest": manifest.compute_value_digest(spec, entries),
            "symbol_map_digest": map_digest,
            "partitions": entries,
        }
        manifest.publish_manifest(tmp_path, lake_manifest)
        return DatasetBinding(
            data_version=_VERSION,
            value_digest=str(lake_manifest["value_digest"]),
            as_of_fidelity=spec.as_of_fidelity,
            event_time_min=min(item.time_min for item in source),
            event_time_max=max(item.time_max for item in source),
        )

    members = {
        "ohlcv_1m": publish("ohlcv_1m", ohlcv),
        "signals_log": publish("signals_log", signals),
    }
    universe = _write_artifact(
        tmp_path,
        "universes",
        {
            "schema_version": 1,
            "members": [
                {"lake_pair": "BTC-USDT", "valid_from": "2026-01-01T00:00:00Z", "valid_to": None},
                {"lake_pair": "ETH-USDT", "valid_from": "2026-01-01T01:30:00Z", "valid_to": None},
            ],
        },
    )
    calendar = _write_artifact(
        tmp_path,
        "calendars",
        {"schema_version": 1, "kind": "continuous_24_7", "timezone": "UTC"},
    )
    identity = sha256_prefixed_bytes(
        canonical_json_bytes({"universe": universe.digest, "calendar": calendar.digest})
    )
    binding_path = tmp_path / "_metadata" / "bindings" / f"{identity}.json"
    binding_path.parent.mkdir(parents=True)
    binding_path.write_bytes(canonical_json_bytes({"schema_version": 1}))
    cutoff = _START + timedelta(hours=3)
    explicit = ExplicitSnapshotBinding(
        mode="explicit_tuples",
        schema_version=1,
        cutoff_time=cutoff,
        members=members,
        symbol_map_digest=map_digest,
        universe=universe,
        calendar=calendar,
        universe_calendar_digest=identity,
        provenance=BindingProvenance(
            created_at=cutoff,
            artifact_path=binding_path,
            member_manifest_paths={
                name: lake_paths.manifest_path(tmp_path, name, _VERSION) for name in members
            },
            symbol_map_path=map_path,
            universe_path=universe.path,
            calendar_path=calendar.path,
        ),
    )
    return _FakeLake(root=tmp_path, binding=validate_binding(explicit, lake_root=tmp_path))


def test_tensor_matches_reader_and_applies_pit_mask(fake_lake: _FakeLake) -> None:
    """FR-003/AC-003：抽样值与 reader 一致，且 PIT 掩码随台账变化。"""
    make_tensor = partial(build_tensor, fake_lake.binding, lake_root=fake_lake.root)
    tensor = make_tensor(datasets=("ohlcv_1m", "signals_log"), resample="1m")
    sampled_at = _START + timedelta(hours=1)
    raw = read(
        "ohlcv_1m",
        data_version=_VERSION,
        start=sampled_at,
        end=sampled_at + timedelta(minutes=1),
        pairs=["BTC-USDT"],
        as_of=fake_lake.binding.resolved.cutoff_time,
        allow_event_time_only=True,
        lake_root=fake_lake.root,
    ).frame

    value = tensor.panel.loc[(sampled_at, "BTC-USDT"), "ohlcv_1m.close@1m"]
    assert value == pytest.approx(raw.iloc[0]["close"])
    assert not bool(tensor.panel.loc[(sampled_at, "ETH-USDT"), "__in_universe__"])
    assert tensor.panel.loc[(sampled_at, "ETH-USDT"), list(tensor.feature_map)].isna().all()
    later = _START + timedelta(hours=2)
    assert bool(tensor.panel.loc[(later, "ETH-USDT"), "__in_universe__"])
    assert pd.notna(tensor.panel.loc[(later, "ETH-USDT"), "ohlcv_1m.close@1m"])
    assert tensor.universe_source.startswith("explicit:")
    assert tensor.universe_source.endswith(f"@{fake_lake.binding.resolved.universe.digest}")


def test_right_closed_hourly_ohlcv_aggregation(fake_lake: _FakeLake) -> None:
    """FR-003/AC-003：1m→1h 使用右闭右标 OHLCV 聚合。"""
    make_tensor = partial(build_tensor, fake_lake.binding, lake_root=fake_lake.root)
    minute = make_tensor(datasets=("ohlcv_1m", "signals_log"), resample="1m")
    tensor = make_tensor(
        datasets=("ohlcv_1m",),
        resample="1h",
        start=_START + timedelta(minutes=1),
        end=_START + timedelta(hours=2, minutes=1),
    )
    reversed_order = make_tensor(datasets=("signals_log", "ohlcv_1m"), resample="1m")
    first = tensor.panel.loc[(_START + timedelta(hours=1), "BTC-USDT")]

    assert len(tensor.timestamps) == 2
    assert first["ohlcv_1m.open@1h"] == pytest.approx(101.0)
    assert first["ohlcv_1m.high@1h"] == pytest.approx(162.0)
    assert first["ohlcv_1m.low@1h"] == pytest.approx(100.0)
    assert first["ohlcv_1m.close@1h"] == pytest.approx(161.0)
    assert first["ohlcv_1m.volume@1h"] == pytest.approx(1830.0)
    assert list(minute.feature_map.values()) == list(range(len(minute.feature_map)))
    assert minute.feature_map_digest == feature_map_digest(minute.feature_map)
    assert minute.feature_map_digest != tensor.feature_map_digest
    assert minute.feature_map_digest != reversed_order.feature_map_digest


def test_empty_dataset_is_rejected_explicitly(fake_lake: _FakeLake) -> None:
    """FR-003/AC-003：窗口内零行的数据集以具名 schema 错误显式暴露。"""
    make_tensor = partial(build_tensor, fake_lake.binding, lake_root=fake_lake.root)
    with pytest.raises(SchemaValidationError, match="signals_log.*0 rows"):
        make_tensor(
            datasets=("signals_log",),
            resample="1m",
            start=_START + timedelta(minutes=1),
            end=_START + timedelta(minutes=30),
        )


def test_end_boundary_is_exclusive(fake_lake: _FakeLake) -> None:
    """FR-003/AC-003：读取窗口保持 start 包含、end 排除的半开语义。"""
    end = _START + timedelta(minutes=3)
    make_tensor = partial(build_tensor, fake_lake.binding, lake_root=fake_lake.root)
    tensor = make_tensor(
        datasets=("ohlcv_1m",),
        resample="1m",
        start=_START + timedelta(minutes=1),
        end=end,
    )

    assert len(tensor.timestamps) == 2
    assert end not in tensor.timestamps
