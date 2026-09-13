"""DuckDB 研究只读取数入口（FR-003，NFR-001 零写路径）。

- 只按 manifest `partitions` 清单构造输入路径，**从不扫描目录**（F002-R2-02）；
- 返回数据前先跑清单完整性校验（存在/字节数/sha256）与 `value_digest` 重算，
  任一不符抛 `ManifestIntegrityError`（fail-closed，NFR-002 的技术保证）；
- `as_of=T` 同时施加 `event_time <= T` **与** `available_at <= T`（双时间轴，
  design §3）；`as_of_fidelity=event_time_only` 的 dataset 默认抛
  `InsufficientAsOfFidelityError`，显式 `allow_event_time_only=True` 才放行；
- 事后回填标签（`realized_return_60m`）在其可用时间（`evaluated_at`）晚于 T
  时**置 NULL 而非丢行**——丢行会让样本集随 T 变化；
- 带未解决质量旗的分区默认拒绝，`allow_flagged=True` 显式豁免并随附清单；
- 时间过滤语义：`start` 含、`end` 含（半开区间 [start, end)）。
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import partitions, paths, registry, symbol_map
from alphamill.data_bridge.errors import (
    FlaggedPartitionError,
    InsufficientAsOfFidelityError,
    InvalidVersionError,
    VersionNotFoundError,
)

FilterValue = Any


@dataclass(frozen=True)
class ReadResult:
    frame: pd.DataFrame
    dataset: str
    data_version: str  # 即使调用方传 None，也回报实际解析版本
    value_digest: str  # 来自已校验 manifest 的语义根摘要
    as_of: dt.datetime | None  # None = 纯历史切片，不得用于回测/门禁判定
    as_of_fidelity: str | None  # "bitemporal" | "event_time_only"；as_of=None 时为 None
    flagged: list[str]  # 被显式豁免放行的带旗分区


def latest_valid_version(dataset: str, lake_root: Path | None = None) -> str:
    spec = registry.require_dataset(dataset)
    root = lake_root or paths.lake_root()
    return mf.latest_valid_version(root, spec.name)


def _utc(value: FilterValue, name: str) -> dt.datetime:
    if isinstance(value, str):
        try:
            value = dt.datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{name} 不是合法 ISO8601 时间: {value!r}") from exc
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if not isinstance(value, dt.datetime):
        raise ValueError(f"{name} 需要 datetime/ISO 字符串，收到 {type(value).__name__}")
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.UTC)
    return value.astimezone(dt.UTC)


def _partition_covers(key_date: str, start: dt.datetime | None, end: dt.datetime | None) -> bool:
    """分区日 [D 00:00, D+1) 与查询窗有交集才读该文件。"""
    day = dt.date.fromisoformat(key_date)
    if start is not None and day < start.date():
        return False
    if end is not None and day > end.date():
        return False
    if end is not None and day == end.date() and end.time() == dt.time.min:
        return False  # end 恰为当日 00:00：该日分区全部行 >= end
    return True


def _empty_frame(spec: registry.DatasetSpec) -> pd.DataFrame:
    table = partitions.rows_to_table([], spec)
    return table.to_pandas()


def _selected_flagged(manifest: dict[str, Any], selected: list[dict[str, Any]]) -> list[str]:
    flagged = set(manifest.get("quality", {}).get("flagged_partitions", []))
    hits = []
    for partition in selected:
        key = partition["logical_partition_key"]
        label = "/".join(
            str(key[name]) for name in ("exchange", "pair", "date") if name in key
        )
        if label in flagged:
            hits.append(label)
    return sorted(set(hits))


def read(
    dataset: str,
    data_version: str | None = None,
    start: FilterValue | None = None,
    end: FilterValue | None = None,
    pairs: list[str] | None = None,
    as_of: FilterValue | None = None,
    allow_flagged: bool = False,
    allow_event_time_only: bool = False,
    lake_root: Path | None = None,
) -> ReadResult:
    spec = registry.require_dataset(dataset)
    root = Path(lake_root) if lake_root is not None else paths.lake_root()

    version = data_version or mf.latest_valid_version(root, spec.name)
    manifest = mf.load_manifest(root, spec.name, version)
    if manifest["status"] == "invalid":
        raise InvalidVersionError(
            f"{dataset}/{version} 已标记 invalid（对账或完整性失败），拒绝读取"
        )
    mf.validate_manifest_integrity(root, manifest)
    value_digest = mf.verify_value_digest(spec, manifest)

    start_dt = _utc(start, "start") if start is not None else None
    end_dt = _utc(end, "end") if end is not None else None
    as_of_dt = _utc(as_of, "as_of") if as_of is not None else None

    as_of_fidelity: str | None = None
    if as_of_dt is not None:
        fidelity = manifest.get("as_of_fidelity", spec.as_of_fidelity)
        if fidelity == registry.AS_OF_EVENT_TIME_ONLY and not allow_event_time_only:
            raise InsufficientAsOfFidelityError(
                f"{dataset} 无采集时间列（as_of_fidelity=event_time_only），"
                "as-of 只能退化为 event_time<=T；显式 allow_event_time_only=True 才放行"
            )
        as_of_fidelity = fidelity

    selected = []
    for partition in manifest.get("partitions", []):
        key = partition["logical_partition_key"]
        if pairs is not None and "pair" in key and key["pair"] not in pairs:
            continue
        if not _partition_covers(key["date"], start_dt, end_dt):
            continue
        selected.append(partition)

    flagged_hits = _selected_flagged(manifest, selected)
    if flagged_hits and not allow_flagged:
        raise FlaggedPartitionError(
            f"查询命中带未解决质量旗的分区且未显式豁免: {flagged_hits}"
        )

    frame = _query(spec, root, selected, start_dt, end_dt, as_of_dt, pairs)
    if as_of_dt is not None:
        _nullify_deferred_labels(spec, frame, as_of_dt)
    return ReadResult(
        frame=frame,
        dataset=spec.name,
        data_version=version,
        value_digest=value_digest,
        as_of=as_of_dt,
        as_of_fidelity=as_of_fidelity,
        flagged=flagged_hits,
    )


def _query(
    spec: registry.DatasetSpec,
    root: Path,
    selected: list[dict[str, Any]],
    start_dt: dt.datetime | None,
    end_dt: dt.datetime | None,
    as_of_dt: dt.datetime | None,
    pairs: list[str] | None,
) -> pd.DataFrame:
    if not selected:
        return _empty_frame(spec)
    import duckdb

    files = [str(root / p["path"]) for p in selected]
    clauses: list[str] = []
    params: list[Any] = []
    if start_dt is not None:
        clauses.append(f"{spec.event_time} >= CAST(? AS TIMESTAMPTZ)")
        params.append(start_dt)
    if end_dt is not None:
        clauses.append(f"{spec.event_time} < CAST(? AS TIMESTAMPTZ)")
        params.append(end_dt)
    if as_of_dt is not None:
        clauses.append(f"{spec.event_time} <= CAST(? AS TIMESTAMPTZ)")
        params.append(as_of_dt)
        if spec.available_at is not None:
            clauses.append(f"{spec.available_at} <= CAST(? AS TIMESTAMPTZ)")
            params.append(as_of_dt)
    if pairs is not None and not registry.pair_partitioned(spec):
        db_symbols = symbol_map.to_db_symbols(pairs, spec.market_type)
        placeholders = ", ".join("?" for _ in db_symbols)
        clauses.append(f"symbol IN ({placeholders})")
        params.extend(db_symbols)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    order_cols = [
        name for name in (spec.event_time, "symbol", "exchange", "timeframe")
        if name in {c.name for c in spec.projection}
    ]
    sql = (
        f"SELECT * FROM read_parquet(?::VARCHAR[]) {where} "
        f"ORDER BY {', '.join(order_cols)}"
    )
    con = duckdb.connect(":memory:")
    try:
        return con.execute(sql, [files, *params]).df()
    finally:
        con.close()


def _nullify_deferred_labels(
    spec: registry.DatasetSpec, frame: pd.DataFrame, as_of_dt: dt.datetime
) -> None:
    """事后回填标签在可用时间晚于 T（或未知）时置 NULL 而非丢行（design §3）。"""
    for label_col, available_col in spec.deferred_labels.items():
        if label_col not in frame.columns:
            continue
        available = pd.to_datetime(frame[available_col], utc=True)
        unknown = available.isna() | (available > pd.Timestamp(as_of_dt))
        frame.loc[unknown, label_col] = None
