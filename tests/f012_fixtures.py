"""F012 集成夹具：scratch 湖（ohlcv_1m 小时级合成行情 + 符号映射 + manifest + 显式绑定）
与训练/生成器/CLI 驱动。

走 data_bridge 真实写路径（`write_partition` / `publish_manifest`），CLI 由此经 F002 reader
与绑定校验读数——与执行机真实湖同一条取数链，只是规模小。同一份数据可按不同宇宙成员
生成多个显式绑定（AC-008：数据版本相同、宇宙不同）。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

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
WINDOW_START = CUTOFF - timedelta(days=730)  # default_1h_2y 预设


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
    # 窗口边界探针（检视 R-C1/R2-1），`time` 是 1m K 线开盘时间：window.start 前 1 分钟开盘的
    # 须排除；cutoff 前 1 分钟开盘（cutoff 收盘，close=2.0）的归入 cutoff 标签；cutoff 开盘的
    # （close=99.0）cutoff 之后才收盘，须排除——否则即前视
    minute = timedelta(minutes=1)
    probes: dict[str, list[list[object]]] = {}
    for ts, value in ((WINDOW_START - minute, 1.0), (CUTOFF - minute, 2.0), (CUTOFF, 99.0)):
        row = [ts, EXCHANGE, f"{BASES[0]}/USDT", value, value, value, value, 1.0]
        probes.setdefault(ts.date().isoformat(), []).append(row)
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
        if index == 0:
            for day, rows in probes.items():
                by_day.setdefault(day, []).extend(rows)
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
            "rows": sum(entry["rows"] for entry in entries),
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


# ------------------------------------------------------------------ 训练/生成器/CLI 驱动


def _training_panel(days: int = 240, pair_count: int = 6):
    """vendor 六个 FeatureType 通道齐全，候选不会因缺通道被整批拒掉。"""
    from alphamill.factor_factory.generators.lake_tensor import TensorPanel

    timestamps = pd.date_range("2026-01-01", periods=days, freq="h", tz="UTC")
    pairs = tuple(f"PAIR-{index}-USDT" for index in range(pair_count))
    index = pd.MultiIndex.from_product([timestamps, pairs], names=["timestamp", "pair"])
    rng = np.random.default_rng(7)
    close = 100.0 * np.exp(np.cumsum(rng.normal(0, 0.01, (days, pair_count)), axis=0)).ravel()
    names = ("open", "close", "high", "low", "volume", "vwap")
    columns = {
        "open": close * (1 + rng.normal(0, 0.002, close.size)),
        "close": close,
        "high": close * 1.004,
        "low": close * 0.996,
        "volume": rng.uniform(1e3, 1e4, close.size),
        "vwap": close * (1 + rng.normal(0, 0.001, close.size)),
    }
    frame = pd.DataFrame({f"ohlcv_1m.{n}@1h": columns[n] for n in names}, index=index)
    frame["__in_universe__"] = True
    return TensorPanel(
        datasets=("ohlcv_1m",),
        resample="1h",
        pairs=pairs,
        timestamps=timestamps,
        panel=frame,
        feature_map={f"ohlcv_1m.{n}@1h": i for i, n in enumerate(names)},
        feature_map_digest="sha256:test",
        universe_source="test",
    )


_WINDOW = ("2026-01-01T00:00:00+00:00", "2026-01-11T00:00:00+00:00")


_LENIENT = {  # 预筛放宽到几乎全收：只验证编排与配额，不验证目标函数本身
    "reachability_min_trades_90d": 0,
    "min_after_cost_return": -1.0e9,
    "turnover_penalty_lambda": 0.0,
}


def _produce(tmp_path, *, quota: int, objective: dict, check=None, total_timesteps=512):
    pytest.importorskip("torch")
    pytest.importorskip("sb3_contrib")
    from alphamill.factor_factory import mine_dispatch
    from alphamill.factor_factory.generators.base import GenerationRequest, Window
    from alphamill.factor_factory.generators.stop_conditions import (
        StopController,
        install_signal_flags,
    )
    from alphamill.factor_factory.registry.default_compilers import full_registry
    from alphamill.factor_factory.registry.event_writer import RunEventWriter

    spec = mine_dispatch.resolve("alphagen")
    config = mine_dispatch.compose_config(
        spec,
        {"objective": objective, "total_timesteps": total_timesteps, "pool_capacity": 5},
        mining=True,
        quota=quota,
        window=list(_WINDOW),
    )
    run_id = "alphagen-test-run"
    with install_signal_flags() as flags:
        stop = StopController(
            flags=flags,
            window_start="22:00",
            window_end="06:30",
            window_tz="Asia/Shanghai",
            ignore_window=True,
        )
        if check is not None:
            stop.check = check(stop)
        writer = RunEventWriter(tmp_path, run_id=run_id)
        context = mine_dispatch.BuildContext(
            run_id=run_id, config=config, stop=stop, writer=writer, compilers=full_registry()
        )
        request = GenerationRequest(
            generator="alphagen",
            binding=object(),
            seed=11,
            window=Window(
                start=datetime.fromisoformat(_WINDOW[0]),
                end=datetime.fromisoformat(_WINDOW[1]),
                resample="1h",
            ),
            config=config,
            quota=quota,
            panel=_training_panel(),
        )
        result = mine_dispatch.build_generator(spec, context).produce(request)
        writer.close()
    return result


def _event_lines(path) -> list[dict]:
    import json

    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


FULL = [
    {"lake_pair": f"{base}-USDT", "valid_from": "2026-01-01T00:00:00Z", "valid_to": None}
    for base in ("AAA", "BBB", "CCC", "DDD", "EEE", "FFF")
]


PARTIAL_UNIVERSE = [
    {"lake_pair": "AAA-USDT", "valid_from": "2026-01-01T00:00:00Z", "valid_to": None},
    {"lake_pair": "BBB-USDT", "valid_from": "2026-01-01T00:00:00Z", "valid_to": None},
    # 窗口内中途退出者仍计入「曾在宇宙」
    {
        "lake_pair": "CCC-USDT",
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_to": "2026-09-05T00:00:00Z",
    },
]


def _cli_mine(lake, binding: str, tmp_path, *, quota: int, total_timesteps: int, objective=None):
    import json

    pytest.importorskip("torch")
    pytest.importorskip("sb3_contrib")
    from alphamill.factor_factory import mine_dispatch
    from alphamill.factor_factory.cli import main
    from alphamill.factor_factory.registry import factor_store

    panels = []
    original = mine_dispatch.build_tensor

    def recording(*args, **kwargs):
        panels.append(original(*args, **kwargs))
        return panels[-1]

    config = tmp_path / f"config-{binding}.json"
    body = {"total_timesteps": total_timesteps, "pool_capacity": 5}
    if objective is not None:
        body["objective"] = objective
    config.write_text(json.dumps(body), encoding="utf-8")
    argv = ["mine", "--generator", "alphagen", "--binding", str(lake.bindings[binding])]
    argv += ["--seed", "11", "--quota", str(quota), "--config", str(config)]
    argv += ["--allow-cpu", "--allow-offhours"]
    written = []  # 运行内入册的 FactorDef（即预筛所用的那一份，检视 R-C2）
    original_write = factor_store.write

    def recording_write(run_dir, factor):
        written.append(factor)
        return original_write(run_dir, factor)

    before = set((lake.reports_root / "generation").glob("*/run.json"))
    mp = pytest.MonkeyPatch()
    mp.setattr(mine_dispatch, "build_tensor", recording)
    mp.setattr(factor_store, "write", recording_write)
    # 训练中 torch 惰性导入 torch._inductor.test_operators，名字命中 pytest 的断言改写钩子，
    # 钩子用 os.makedirs 写 pyc 缓存而被进程级写护栏拦下；生产进程无此钩子（importlib 走 posix）。
    mp.setattr(sys, "dont_write_bytecode", True)
    try:
        code = main(argv, reports_root=lake.reports_root, lake_root=lake.lake_root)
    finally:
        mp.undo()
    # 本次新增的那一个 run（不按 mtime 猜，检视 R-C10）
    [run_path] = set((lake.reports_root / "generation").glob("*/run.json")) - before
    run = json.loads(run_path.read_text(encoding="utf-8"))
    return code, run_path, run, panels[-1], written
