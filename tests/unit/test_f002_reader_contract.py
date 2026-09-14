"""F002 reader 的本地湖边界测试（不依赖 TimescaleDB）。"""

from datetime import UTC, datetime

import pyarrow.parquet as pq

from alphamill.data_bridge import digest, manifest, partitions, symbol_map
from alphamill.data_bridge.reader import read
from alphamill.data_bridge.registry import require_dataset


def test_pair_filter_uses_manifest_mapping_and_requested_lake(tmp_path, monkeypatch):
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
    table = partitions.rows_to_table(rows, spec)
    path = tmp_path / "signals_log/date=2026-09-11.r1.parquet"
    path.parent.mkdir(parents=True)
    pq.write_table(table, path)

    mapping = symbol_map.build_symbol_map([symbol_map.SymbolRow("binance", "spot", "BTC/USDT")])
    payload = symbol_map.canonical_csv_bytes(mapping)
    map_digest = symbol_map.content_digest(payload)
    map_path = symbol_map.paths.symbol_maps_dir(tmp_path) / f"{map_digest}.csv"
    map_path.parent.mkdir(parents=True)
    map_path.write_bytes(payload)

    entry = {
        "logical_partition_key": {"date": "2026-09-11"},
        "path": path.relative_to(tmp_path).as_posix(),
        "rows": 1,
        "time_min": "2026-09-11T09:00:00Z",
        "time_max": "2026-09-11T09:00:00Z",
        "row_digest": digest.row_digest(rows, spec.projection),
        "bytes": path.stat().st_size,
        "sha256": manifest.file_sha256(path),
    }
    unselected = {
        "logical_partition_key": {"date": "2026-09-12"},
        "path": "signals_log/date=2026-09-12.r1.parquet",
        "rows": 0,
        "time_min": "2026-09-12T00:00:00Z",
        "time_max": "2026-09-12T00:00:00Z",
        "row_digest": "sha256:" + "0" * 64,
        "bytes": 0,
        "sha256": "0" * 64,
    }
    lake_manifest = {
        "dataset": "signals_log",
        "source": manifest.SOURCE_TAG,
        "data_version": "v2026.09.11",
        "status": "valid",
        "rows": 1,
        "value_digest": manifest.compute_value_digest(spec, [entry, unselected]),
        "symbol_map_digest": map_digest,
        "partitions": [entry, unselected],
    }
    manifest.publish_manifest(tmp_path, lake_manifest)
    monkeypatch.delenv("ALPHAMILL_LAKE_DIR", raising=False)
    monkeypatch.delenv("ALPHAMILL_SYMBOL_MAP_CURRENT", raising=False)

    result = read(
        "signals_log",
        data_version="v2026.09.11",
        pairs=["BTC-USDT"],
        start="2026-09-11T00:00:00Z",
        end="2026-09-12T00:00:00Z",
        lake_root=tmp_path,
    )
    assert len(result.frame) == 1
    assert result.symbol_map_digest == map_digest
