"""对账器（T004）——导出后逐分区与 TimescaleDB 对账（design §3 唯一权威口径）。

两侧由 digest.py 的同一个 Python 函数计算：源侧喂 psycopg2 游标值序列、湖侧
喂 PyArrow 读回的 `to_pylist()` 值序列。逐分区比较 rows / time 边界 / row_digest，
不一致 → 该 data_version 整体标记 invalid。**无降级分支**——不得退回
numeric/弱口径，性能不可接受走 spec 修订。

本模块还承载导出与对账共用的分区过滤 SQL 构造（`build_cell_filter`），
保证两侧查询的语义完全一致。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from alphamill.data_bridge import digest as digest_mod
from alphamill.data_bridge import registry
from alphamill.data_bridge.manifest import iso_utc


def partition_time_bounds(day: str) -> tuple[datetime, datetime]:
    """逻辑分区日期 → [day 00:00, day+1 00:00) UTC 时间窗。"""
    start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def build_cell_filter(spec: registry.DatasetSpec, key: dict[str, str]) -> tuple[str, list[Any]]:
    """逻辑分区键 → WHERE 片段与参数（event_time 半开区间）。

    `key` 为内部单元格键：除逻辑键成分外，pair 分区的 dataset 必须额外携带
    `"db_symbol"`（lake pair 无法直接进 SQL 谓词，列里存的是 db symbol）。
    """
    clauses: list[str] = []
    params: list[Any] = []
    if "exchange" in key:
        clauses.append("exchange = %s")
        params.append(key["exchange"])
    if "pair" in key:
        clauses.append("symbol = %s")
        params.append(key["db_symbol"])
    if "timeframe" in key:
        clauses.append("timeframe = %s")
        params.append(key["timeframe"])
    start, end = partition_time_bounds(key["date"])
    clauses.append(f"{spec.event_time} >= %s")
    params.append(start)
    clauses.append(f"{spec.event_time} < %s")
    params.append(end)
    clauses.append(f"{spec.event_time} IS NOT NULL")
    return " AND ".join(clauses), params


def projection_select(spec: registry.DatasetSpec) -> str:
    return ", ".join(col.name for col in spec.projection)


def fetch_cell_rows(conn, spec: registry.DatasetSpec, key: dict[str, str]) -> list[list[Any]]:
    """同一事务内取单个逻辑分区的全部行（投影顺序）。"""
    where, params = build_cell_filter(spec, key)
    sql = f"SELECT {projection_select(spec)} FROM {spec.source_table} WHERE {where}"
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return [list(row) for row in cur.fetchall()]


def source_partition_stats(
    conn, spec: registry.DatasetSpec, key: dict[str, str]
) -> dict[str, Any]:
    rows = fetch_cell_rows(conn, spec, key)
    return _stats_from_values(rows, spec)


def lake_partition_stats(
    path: Path, spec: registry.DatasetSpec
) -> dict[str, Any]:
    import pyarrow.parquet as pq

    table = pq.read_table(path)
    return _stats_from_values(digest_mod.iter_row_values(table), spec)


def _stats_from_values(
    rows: Any, spec: registry.DatasetSpec
) -> dict[str, Any]:
    materialized = list(rows)  # 源侧为列表、湖侧为生成器，统一物化
    row_digest = digest_mod.row_digest(materialized, spec.projection)
    event_idx = next(
        i for i, col in enumerate(spec.projection) if col.name == spec.event_time
    )
    times = [row[event_idx] for row in materialized]
    return {
        "rows": len(materialized),
        "time_min": iso_utc(min(times)) if times else None,
        "time_max": iso_utc(max(times)) if times else None,
        "row_digest": row_digest,
    }


def compare(source: dict[str, Any], lake: dict[str, Any]) -> dict[str, str]:
    """逐项对账结论；全 ok 才算通过（不降级）。"""
    return {
        "rows": "ok" if source["rows"] == lake["rows"] else "mismatch",
        "time_bounds": "ok"
        if (source["time_min"], source["time_max"]) == (lake["time_min"], lake["time_max"])
        else "mismatch",
        "row_digest": "ok" if source["row_digest"] == lake["row_digest"] else "mismatch",
    }
