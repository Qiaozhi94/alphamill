"""F012 集成用 scratch 湖：ohlcv_1m 小时级合成行情 + 符号映射 + manifest + 显式绑定。

走 data_bridge 真实写路径（`write_partition` / `publish_manifest`），CLI 由此经 F002 reader
与绑定校验读数——与执行机真实湖同一条取数链，只是规模小。同一份数据可按不同宇宙成员
生成多个显式绑定（AC-008：数据版本相同、宇宙不同）。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np

from alphamill.data_bridge import manifest, partitions, symbol_map
from alphamill.data_bridge import paths as lake_paths
from alphamill.data_bridge.registry import require_dataset
from alphamill.factor_factory.canonical import (
    JSONValue,
    canonical_json_bytes,
    sha256_prefixed_bytes,
)

DATASET = "ohlcv_1m"
DATA_VERSION = "v2026.09.11"
EXCHANGE = "binance"
BASES = ("AAA", "BBB", "CCC", "DDD", "EEE", "FFF")
DATA_START = datetime(2026, 9, 1, tzinfo=UTC)
HOURS = 240
DATA_END = DATA_START + timedelta(hours=HOURS - 1)
CUTOFF = DATA_START + timedelta(hours=HOURS)


@dataclass(frozen=True)
class ScratchLake:
    lake_root: Path
    reports_root: Path
    bindings: dict[str, Path]


def lake_pair(base: str) -> str:
    return f"{base}-USDT"


def build_scratch_lake(
    tmp_path: Path, universes: dict[str, list[dict[str, str | None]]]
) -> ScratchLake:
    """`universes`：绑定名 → 宇宙成员（`lake_pair`/`valid_from`/`valid_to`，ISO UTC）。"""
    lake_root = tmp_path / "lake"
    spec = require_dataset(DATASET)
    rng = np.random.default_rng(20260911)
    entries = []
    for index, base in enumerate(BASES):
        close = 10.0 * (index + 1) * np.exp(np.cumsum(rng.normal(0.0, 0.01, HOURS)))
        by_day: dict[str, list[list[object]]] = {}
        for hour in range(HOURS):
            ts = DATA_START + timedelta(hours=hour)
            c = float(close[hour])
            o = c * (1 + float(rng.normal(0.0, 0.002)))
            row = [ts, EXCHANGE, f"{base}/USDT", o, max(o, c) * 1.002, min(o, c) * 0.998, c]
            row.append(float(rng.uniform(1e3, 1e4)))
            by_day.setdefault(ts.date().isoformat(), []).append(row)
        for day, rows in by_day.items():
            key = {"exchange": EXCHANGE, "pair": lake_pair(base), "date": day}
            entries.append(
                partitions.write_partition(
                    lake_root, spec, {**key, "db_symbol": f"{base}/USDT"}, rows
                )
            )

    mapping = symbol_map.build_symbol_map(
        [symbol_map.SymbolRow(EXCHANGE, "spot", f"{base}/USDT") for base in BASES]
    )
    mapping_payload = symbol_map.canonical_csv_bytes(mapping)
    symbol_digest = symbol_map.content_digest(mapping_payload)
    symbol_path = lake_paths.symbol_maps_dir(lake_root) / f"{symbol_digest}.csv"
    symbol_path.parent.mkdir(parents=True, exist_ok=True)
    symbol_path.write_bytes(mapping_payload)

    value_digest = manifest.compute_value_digest(spec, entries)
    manifest_path = manifest.publish_manifest(
        lake_root,
        {
            "dataset": DATASET,
            "source": manifest.SOURCE_TAG,
            "data_version": DATA_VERSION,
            "status": "valid",
            "rows": HOURS * len(BASES),
            "value_digest": value_digest,
            "symbol_map_digest": symbol_digest,
            "partitions": entries,
        },
    )
    bindings = {
        name: _write_binding(
            tmp_path / "bindings" / name,
            members,
            value_digest=value_digest,
            symbol_digest=symbol_digest,
            symbol_path=symbol_path,
            manifest_path=manifest_path,
        )
        for name, members in universes.items()
    }
    return ScratchLake(lake_root=lake_root, reports_root=tmp_path / "reports", bindings=bindings)


def _digest(payload: JSONValue) -> str:
    return sha256_prefixed_bytes(canonical_json_bytes(payload))


def _artifact(root: Path, kind: str, payload: JSONValue) -> tuple[str, Path]:
    digest = _digest(payload)
    path = root / "artifacts" / kind / f"{digest}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(payload))
    return digest, path


def _write_binding(
    root: Path,
    members: list[dict[str, str | None]],
    *,
    value_digest: str,
    symbol_digest: str,
    symbol_path: Path,
    manifest_path: Path,
) -> Path:
    universe_digest, universe_path = _artifact(
        root, "universe", {"schema_version": 1, "members": members}
    )
    calendar_digest, calendar_path = _artifact(
        root,
        "calendar",
        {"schema_version": 1, "kind": "continuous_24_7", "timezone": "UTC"},
    )
    combined = _digest({"universe": universe_digest, "calendar": calendar_digest})
    artifact_path = root / "artifacts/bindings" / f"{combined}.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text("{}", encoding="utf-8")
    binding_path = root / "binding.json"
    binding_path.write_bytes(
        canonical_json_bytes(
            {
                "mode": "explicit_tuples",
                "schema_version": 1,
                "cutoff_time": manifest.iso_utc(CUTOFF),
                "members": {
                    DATASET: {
                        "data_version": DATA_VERSION,
                        "value_digest": value_digest,
                        "as_of_fidelity": "event_time_only",
                        "event_time_min": manifest.iso_utc(DATA_START),
                        "event_time_max": manifest.iso_utc(DATA_END),
                    }
                },
                "symbol_map_digest": symbol_digest,
                "universe": {
                    "digest": universe_digest,
                    "path": universe_path.as_posix(),
                    "schema_version": 1,
                },
                "calendar": {
                    "digest": calendar_digest,
                    "path": calendar_path.as_posix(),
                    "schema_version": 1,
                },
                "universe_calendar_digest": combined,
                "provenance": {
                    "created_at": manifest.iso_utc(CUTOFF),
                    "artifact_path": artifact_path.as_posix(),
                    "member_manifest_paths": {DATASET: manifest_path.as_posix()},
                    "symbol_map_path": symbol_path.as_posix(),
                    "universe_path": universe_path.as_posix(),
                    "calendar_path": calendar_path.as_posix(),
                },
            }
        )
    )
    return binding_path
