"""分区文件层操作：单元格发现、`.rN` 写入、空单元格判定、质量标记（design §3）。

本模块只做「源行集 → 湖分区文件」的机械转换与窗口内的网格判定；导出编排
（事务、基线继承、manifest 合成与发布）在 exporter.py。分区写入永不覆盖：
内容变化写 `.rN+1`，序号由盘上现有最大值推导，孤儿文件不阻塞重跑。
"""

from __future__ import annotations

import datetime as dt
import hashlib
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import paths, reconcile, registry, symbol_map
from alphamill.data_bridge.digest import canonical_json_text, canonical_row_bytes
from alphamill.data_bridge.errors import DataBridgeError

logger = logging.getLogger(__name__)

_PARQUET_RE = re.compile(r"^date=(\d{4}-\d{2}-\d{2})\.r(\d+)\.parquet$")
_DIM_NAMES = ("exchange", "pair", "timeframe")

_ARROW_TYPES = {
    registry.TIMESTAMPTZ: pa.timestamp("us", tz="UTC"),
    registry.TEXT: pa.string(),
    registry.DOUBLE: pa.float64(),
    registry.JSONB: pa.string(),  # canonical JSON 文本（两侧摘要等价，见 digest.py）
}

Dim = tuple[str | None, ...]  # 按 _DIM_NAMES 顺序的维度键；signals_log 为 ()


def as_date(value: Any) -> dt.date:
    """窗口上界 → UTC 日期；接受 date、datetime（含 ISO 字符串，naive 视为 UTC）。"""
    if isinstance(value, dt.datetime):
        return value.astimezone(dt.UTC).date()
    if isinstance(value, dt.date):
        return value
    text = str(value).strip()
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.UTC)
        return parsed.astimezone(dt.UTC).date()


def date_span(start: str, end_inclusive: str) -> list[str]:
    start_d, end_d = dt.date.fromisoformat(start), dt.date.fromisoformat(end_inclusive)
    days = (end_d - start_d).days
    return [(start_d + dt.timedelta(days=i)).isoformat() for i in range(max(days + 1, 0))]


def dim_of(logical_key: dict[str, str]) -> Dim:
    return tuple(logical_key.get(name) for name in _DIM_NAMES)


def dim_logical_key(dim: Dim, day: str) -> dict[str, str]:
    key = {name: value for name, value in zip(_DIM_NAMES, dim, strict=False) if value is not None}
    key["date"] = day
    return key


def lake_pairs_map(conn) -> dict[tuple[str, str], str]:
    """(exchange, db_symbol) → lake pair；按内容推导并显式做碰撞检查。"""
    seen: dict[str, tuple[str, str]] = {}
    out: dict[tuple[str, str], str] = {}
    for row in symbol_map._rows_from_conn(conn):
        lake_pair, _ = symbol_map.derive_pairs(row.db_symbol, row.market_type)
        key = (row.exchange, row.db_symbol)
        if lake_pair in seen:
            raise DataBridgeError(f"lake_pair 碰撞: {lake_pair!r}（{seen[lake_pair]} 与 {key}）")
        seen[lake_pair] = key
        out[key] = lake_pair
    return out


def arrow_schema(spec: registry.DatasetSpec) -> pa.Schema:
    return pa.schema([(col.name, _ARROW_TYPES[col.logical_type]) for col in spec.projection])


def rows_to_table(rows: list[list[Any]], spec: registry.DatasetSpec) -> pa.Table:
    arrays = []
    for idx, col in enumerate(spec.projection):
        values = [row[idx] for row in rows]
        if col.logical_type == registry.JSONB:
            values = [None if v is None else canonical_json_text(v) for v in values]
        arrays.append(pa.array(values, type=_ARROW_TYPES[col.logical_type]))
    return pa.Table.from_arrays(arrays, schema=arrow_schema(spec))


def discover_cells(
    conn, spec: registry.DatasetSpec, start: dt.date, end: dt.date
) -> dict[tuple, int]:
    """窗口内 (exchange, symbol[, timeframe], date_iso) → 行数（单一聚合查询）。"""
    group_cols = ["exchange", "symbol"]
    if registry.timeframe_partitioned(spec):
        group_cols.append("timeframe")
    utc_date = f"({spec.event_time} AT TIME ZONE 'UTC')::date"
    sql = (
        f"SELECT {', '.join(group_cols)}, {utc_date} AS d, count(*) "
        f"FROM {spec.source_table} WHERE {spec.event_time} IS NOT NULL "
        f"AND {spec.event_time} >= %s AND {spec.event_time} < %s "
        f"GROUP BY {', '.join(group_cols)}, d"
    )
    start_ts = dt.datetime.combine(start, dt.time.min, tzinfo=dt.UTC)
    end_ts = dt.datetime.combine(end, dt.time.min, tzinfo=dt.UTC)
    cells: dict[tuple, int] = {}
    with conn.cursor() as cur:
        cur.execute(sql, (start_ts, end_ts))
        for row in cur.fetchall():
            dims, day, count = row[:-2], row[-2], int(row[-1])
            cells[tuple(dims) + (day.isoformat(),)] = count
    return cells


def quality_flags(conn, lake_pairs: dict[tuple[str, str], str]) -> tuple[list[str], int]:
    """ohlcv 未解决质量标记 → 分区级键串与总数（design §3 质量裁决表）。"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT exchange, symbol, (time AT TIME ZONE 'UTC')::date AS d, count(*) "
            "FROM ohlcv_quality_flags WHERE resolved_at IS NULL GROUP BY exchange, symbol, d"
        )
        rows = cur.fetchall()
    flagged: list[str] = []
    total = 0
    for exchange, symbol, day, count in rows:
        total += int(count)
        lake_pair = lake_pairs.get((exchange, symbol))
        if lake_pair is None:
            logger.warning("质量标记无法映射 lake pair，跳过分区标注: %s %s", exchange, symbol)
            continue
        flagged.append(f"{exchange}/{lake_pair}/{day.isoformat()}")
    return sorted(flagged), total


def row_digest_of_rows(rows: list[list[Any]], spec: registry.DatasetSpec) -> str:
    encoded = sorted(canonical_row_bytes(row, spec.projection) for row in rows)
    hasher = hashlib.sha256()
    for chunk in encoded:
        hasher.update(chunk)
    return f"sha256:{hasher.hexdigest()}"


def write_partition(
    root: Path, spec: registry.DatasetSpec, key: dict[str, str], rows: list[list[Any]]
) -> dict[str, Any]:
    """规范化排序 → row_digest → staging 写 Parquet → rename 到 `.rN` 正式路径。

    `key` 是内部单元格键（含 db_symbol）；manifest 条目只含逻辑分区键。
    """
    encoded = sorted((canonical_row_bytes(row, spec.projection), row) for row in rows)
    row_digest = row_digest_of_rows(rows, spec)
    sorted_rows = [row for _, row in encoded]

    logical_key = {k: v for k, v in key.items() if k != "db_symbol"}
    partition_dir = paths.partition_dir(root, spec.name, logical_key)
    partition_dir.mkdir(parents=True, exist_ok=True)
    max_rev = 0
    for existing in partition_dir.iterdir():
        m = _PARQUET_RE.match(existing.name)
        if m and m.group(1) == key["date"]:
            max_rev = max(max_rev, int(m.group(2)))
    final = partition_dir / f"date={key['date']}.r{max_rev + 1}.parquet"

    staging = paths.staging_dir(root, spec.name, "current") / final.name
    staging.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(rows_to_table(sorted_rows, spec), staging)
    file_sha = mf.file_sha256(staging)
    file_bytes = staging.stat().st_size
    staging.replace(final)

    event_idx = next(i for i, c in enumerate(spec.projection) if c.name == spec.event_time)
    times = [row[event_idx] for row in sorted_rows]
    return {
        "logical_partition_key": logical_key,
        "path": final.relative_to(root).as_posix(),
        "rows": len(rows),
        "time_min": mf.iso_utc(min(times)),
        "time_max": mf.iso_utc(max(times)),
        "row_digest": row_digest,
        "bytes": file_bytes,
        "sha256": file_sha,
    }


def cell_logical_key(spec: registry.DatasetSpec, cell: tuple, lake_pair: str) -> dict[str, str]:
    key: dict[str, str] = {}
    values = cell[:-1]  # 末位是 date_iso
    idx = 0
    if "exchange" in spec.partition_keys:
        key["exchange"] = values[idx]
        idx += 1
    if "pair" in spec.partition_keys:
        key["pair"] = lake_pair
        idx += 1
    if "timeframe" in spec.partition_keys:
        key["timeframe"] = values[idx]
    key["date"] = cell[-1]
    return key


def produce_partitions(
    root: Path,
    spec: registry.DatasetSpec,
    conn,
    start: dt.date,
    end: dt.date,
    baseline_partitions: list[dict[str, Any]],
    lake_pairs: dict[tuple[str, str], str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[bool]]:
    """导出窗口内全部单元格 → (produced 条目, 产出逻辑键, 是否新写文件)。"""
    cells = discover_cells(conn, spec, start, end)
    baseline_by_key = {mf.canonical_key(p["logical_partition_key"]): p for p in baseline_partitions}
    produced: list[dict[str, Any]] = []
    produced_keys: list[dict[str, str]] = []
    written: list[bool] = []
    for cell in sorted(cells):
        lake_pair = lake_pairs.get((cell[0], cell[1]))
        if lake_pair is None:
            raise DataBridgeError(f"symbol 无法映射 lake pair: {(cell[0], cell[1])}")
        logical = cell_logical_key(spec, cell, lake_pair)
        key = {**logical, "db_symbol": cell[1]}
        rows = reconcile.fetch_cell_rows(conn, spec, key)
        row_digest = row_digest_of_rows(rows, spec)
        inherited = baseline_by_key.get(mf.canonical_key(logical))
        if inherited is not None and inherited["row_digest"] == row_digest:
            produced.append(dict(inherited))  # 未变分区跨版本共享同一物理文件
            written.append(False)
        else:
            produced.append(write_partition(root, spec, key, rows))
            written.append(True)
        produced_keys.append(logical)
    return produced, produced_keys, written


def empty_cell_keys(
    spec: registry.DatasetSpec,
    mode: str,
    present_keys: list[dict[str, str]],
    window_dates: list[str],
    baseline_partitions: list[dict[str, Any]] | None = None,
    baseline_skipped: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """本轮空单元格（本该有分区却没有）的完整逻辑键。

    - full：每个有数据的维度只在自己「首个数据日 ~ 末个数据日」的活跃跨度内
      判缺——跨度外的日期不属于「本该有」，否则新 pair 的历史之前全是空洞；
    - incremental：**基线维度 ∪ 本轮维度** × 窗口日期判缺（spec 边界场景：
      「导出窗口内某 pair 无新数据 → 跳过该分区且 manifest 记录 skipped」）。
      基线 skipped 键的继承/移除由 manifest.synthesize_skipped 负责。
    """
    present_by_dim: dict[Dim, set[str]] = defaultdict(set)
    for key in present_keys:
        present_by_dim[dim_of(key)].add(key["date"])

    empty: list[dict[str, str]] = []
    if not registry.pair_partitioned(spec):
        dates = sorted(present_by_dim.get((), set()))
        check = date_span(dates[0], dates[-1]) if mode == "full" and dates else window_dates
        present = present_by_dim.get((), set())
        return [{"date": day} for day in check if day not in present]

    if mode == "full":
        for dim, dates in sorted(present_by_dim.items(), key=repr):
            for day in date_span(min(dates), max(dates)):
                if day not in dates:
                    empty.append(dim_logical_key(dim, day))
    else:
        universe = set(present_by_dim)
        for part in baseline_partitions or []:
            universe.add(dim_of(part["logical_partition_key"]))
        for key in baseline_skipped or []:
            universe.add(dim_of(key))
        for dim in sorted(universe, key=repr):
            for day in window_dates:
                if day not in present_by_dim[dim]:
                    empty.append(dim_logical_key(dim, day))
    return sorted(empty, key=mf.canonical_key)


def remove_staging(root: Path, dataset: str) -> None:
    staging = paths.staging_dir(root, dataset, "current")
    if staging.is_dir():
        import shutil

        shutil.rmtree(staging, ignore_errors=True)


def cleanup_orphans(root: Path) -> int:
    """全量模式回收：staging 与无任何 manifest 引用的孤儿 `.rN`（design §3 回收边界）。

    invalid manifest 及其引用 `.rN` 作为完整失败审计证据一并保留，不得只删分区
    使 manifest 的 partitions/sha256 失效。
    """
    import shutil

    referenced: set[str] = set()
    for dataset in registry.DATASETS:
        for version in mf.list_versions(root, dataset):
            manifest = mf.load_manifest(root, dataset, version)
            referenced.update(p["path"] for p in manifest.get("partitions", []))
    removed = 0
    for dataset in registry.DATASETS:
        dataset_dir = root / dataset
        if not dataset_dir.is_dir():
            continue
        for file in dataset_dir.rglob("*.parquet"):
            if file.relative_to(root).as_posix() not in referenced:
                file.unlink()
                removed += 1
    staging = root / "_staging"
    if staging.is_dir():
        shutil.rmtree(staging, ignore_errors=True)
    return removed
