"""导出器——TimescaleDB → 分区 Parquet + manifest（design §3，NFR-001 唯一写湖方）。

核心规则：
- 单个 REPEATABLE READ 只读事务内完成查询与源侧对账（F002-D004）；事务内记录
  `txid_current_snapshot()` 的 xmin 与时刻到 manifest `source_snapshot`；
- 分区写入先 staging 后 rename、永不覆盖、孤儿不阻塞（partitions.py）；
- 增量游标只从上一 valid manifest 推导，绝不看磁盘分区（F002-R3-02）；
- 内容与基线一致的分区**跨版本共享同一物理文件**（直接继承基线条目），只有
  修订分区写新 `.rN`——全量校验不为未变数据产生副本；
- 全量校验只在内容相对基线变化时发布新版本（FR-005：发现修订才递增），
  `revision_diff` 登记 changed/added/removed；无差异 → no-op 不发布；
- 每个 manifest 都是累计完整快照（F002-R2-03）：基线全量继承 + 本轮替换/追加；
- 对账失败时版本照常发布但 `status: invalid`（失败审计证据保留）；
- 回收：全量模式清 staging 与无引用孤儿 `.rN`；invalid 版本及其引用文件保留。

CLI 入口见底部 `main()`（退出码契约 0/1/2，design §5，实现在 cli.py）。
"""

from __future__ import annotations

import datetime as dt
import logging
import shutil
import time
from pathlib import Path
from typing import Any

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import partitions, paths, reconcile, registry
from alphamill.data_bridge.collector.db_writer import db_connect
from alphamill.data_bridge.errors import DataBridgeError, VersionNotFoundError

logger = logging.getLogger(__name__)

# 测试注入点（AC-010 并发 upsert）：签名 (conn) -> None，生产路径恒为 None。
PostExportHook = Any


def _begin_snapshot_tx(conn) -> tuple[str, str]:
    """进入 REPEATABLE READ 只读事务，返回 (xmin, taken_at)（F002-D004）。"""
    conn.rollback()
    with conn.cursor() as cur:
        cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        cur.execute("SELECT txid_current_snapshot(), current_timestamp")
        snapshot, taken_at = cur.fetchone()
    return snapshot.split(":")[0], mf.iso_utc(taken_at)


def _table_span(conn, spec: registry.DatasetSpec) -> tuple[str, str] | None:
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT min({spec.event_time}), max({spec.event_time}) "
            f"FROM {spec.source_table} WHERE {spec.event_time} IS NOT NULL"
        )
        row = cur.fetchone()
    if row is None or row[0] is None:
        return None
    return (
        row[0].astimezone(dt.UTC).date().isoformat(),
        row[1].astimezone(dt.UTC).date().isoformat(),
    )


def _count_null_event_time(conn, spec: registry.DatasetSpec) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {spec.source_table} WHERE {spec.event_time} IS NULL")
        return int(cur.fetchone()[0])


def _baseline(root: Path, dataset: str) -> tuple[str | None, dict[str, Any] | None]:
    try:
        version = mf.latest_valid_version(root, dataset)
        return version, mf.load_manifest(root, dataset, version)
    except VersionNotFoundError:
        return None, None


def _resolve_window(
    conn, spec: registry.DatasetSpec, mode: str, window_end: Any,
    baseline_partitions: list[dict[str, Any]],
) -> tuple[dt.date, dt.date]:
    """窗口 = [start, end)：分区日期 date ∈ [start, end)。end 缺省 = 今日。"""
    end = partitions.as_date(window_end) if window_end is not None else dt.datetime.now(dt.UTC).date()
    span = _table_span(conn, spec)
    if mode == "full":
        return (dt.date.fromisoformat(span[0]) if span else end), end
    if baseline_partitions:
        start = max(
            dt.date.fromisoformat(p["logical_partition_key"]["date"])
            for p in baseline_partitions
        ) + dt.timedelta(days=1)
    else:
        start = dt.date.fromisoformat(span[0]) if span else end
    return start, end


def _reconcile_key(
    spec: registry.DatasetSpec, entry: dict[str, Any],
    lake_pairs: dict[tuple[str, str], str],
) -> dict[str, str]:
    """从 manifest 条目重建对账查询键；db_symbol 由同事务的 pair 映射求逆。"""
    key = dict(entry["logical_partition_key"])
    if "pair" in key:
        pairs_to_symbols = {
            pair: db_symbol
            for (exchange, db_symbol), pair in lake_pairs.items()
            if exchange == key.get("exchange", "")
        }
        if key["pair"] not in pairs_to_symbols:
            raise DataBridgeError(f"对账键反查失败: {key['pair']!r} 不在导出映射中")
        key["db_symbol"] = pairs_to_symbols[key["pair"]]
    return key


def _reconcile_partitions(
    conn, spec: registry.DatasetSpec, root: Path,
    produced: list[dict[str, Any]], written: list[bool],
    lake_pairs: dict[tuple[str, str], str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """逐新写分区与源库对账（同一事务）；继承分区跳过（不可变且读取前会再验）。"""
    report: dict[str, Any] = {"rows": "ok", "time_bounds": "ok", "row_digest": "ok"}
    failures: list[dict[str, Any]] = []
    for entry, is_written in zip(produced, written):
        if not is_written:
            continue
        key = _reconcile_key(spec, entry, lake_pairs)
        source = reconcile.source_partition_stats(conn, spec, key)
        lake = reconcile.lake_partition_stats(root / entry["path"], spec)
        verdict = reconcile.compare(source, lake)
        for field, outcome in verdict.items():
            if outcome != "ok":
                report[field] = "mismatch"
        if any(v != "ok" for v in verdict.values()):
            failures.append({"partition": entry["logical_partition_key"], "verdict": verdict})
    if failures:
        report["failing_partitions"] = [mf.canonical_key(f["partition"]) for f in failures]
    return report, failures


def _cleanup_orphans(root: Path) -> int:
    """全量模式回收：staging 与无任何 manifest 引用的孤儿 `.rN`；invalid 审计证据保留。"""
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


def _summary(
    spec: registry.DatasetSpec, mode: str, data_version: str | None,
    baseline_version: str | None, merged: list[dict[str, Any]],
    failures: list[dict[str, Any]], skipped: list[dict[str, str]],
    reconcile_field: dict[str, Any], *, excluded: int, started: float,
    no_op: bool, reason: str | None, revision_diff: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "dataset": spec.name,
        "mode": mode,
        "data_version": data_version,
        "baseline_version": baseline_version,
        "status": "invalid" if failures else ("no-op" if no_op else "valid"),
        "no_op": no_op,
        "reason": reason,
        "rows": sum(p["rows"] for p in merged),
        "partitions": len(merged),
        "skipped": len(skipped),
        "reconcile": reconcile_field,
        "revision_diff": len(revision_diff),
        "excluded_null_event_time": excluded,
        "elapsed_seconds": round(time.monotonic() - started, 2),
    }


def export_dataset(
    dataset: str,
    mode: str = "incremental",
    window_end: Any | None = None,
    conn=None,
    lake_root: Path | None = None,
    post_export_hook: PostExportHook = None,
) -> dict[str, Any]:
    """导出单个 dataset（design §4 契约）；返回 manifest 摘要 dict。

    mode: incremental（默认，窗口 = 上一 valid manifest 最大日期 +1 ~ window_end）
          | full（全 span 重导 + 分区级 diff，仅在内容变化时发布新版本）。
    window_end: 窗口开区间上界；缺省导到「昨天」。
    """
    if mode not in ("incremental", "full"):
        raise ValueError(f"未知 mode: {mode!r}")
    spec = registry.require_dataset(dataset)
    root = Path(lake_root) if lake_root is not None else paths.lake_root()
    own_conn = conn is None
    conn = conn if conn is not None else db_connect()
    started = time.monotonic()
    try:
        return _export_one(conn, spec, mode, window_end, root, post_export_hook, started)
    finally:
        if own_conn:
            conn.close()


def _export_one(
    conn, spec: registry.DatasetSpec, mode: str, window_end: Any,
    root: Path, post_export_hook: PostExportHook, started: float,
) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    baseline_version, baseline = _baseline(root, spec.name)
    baseline_partitions = baseline["partitions"] if baseline else []

    xmin, taken_at = _begin_snapshot_tx(conn)
    start, end = _resolve_window(conn, spec, mode, window_end, baseline_partitions)
    ok_reconcile = {"rows": "ok", "time_bounds": "ok", "row_digest": "ok"}
    if start >= end:
        conn.rollback()
        return _summary(spec, mode, None, baseline_version, [], [], [], ok_reconcile,
                        excluded=0, started=started, no_op=True,
                        reason="window-empty", revision_diff=[])

    data_version = mf.next_data_version(root, spec.name, dt.datetime.now(dt.UTC).date())
    lake_pairs = partitions.lake_pairs_map(conn)
    excluded_null = _count_null_event_time(conn, spec)
    flagged, flagged_total = (
        partitions.quality_flags(conn, lake_pairs)
        if spec.source_table == "ohlcv_1m" else ([], 0)
    )

    produced, produced_keys, written = partitions.produce_partitions(
        root, spec, conn, start, end, baseline_partitions, lake_pairs
    )
    window_dates = partitions.date_span(
        start.isoformat(), (end - dt.timedelta(days=1)).isoformat()
    )
    empty_keys = partitions.empty_cell_keys(spec, mode, produced_keys, window_dates)
    skipped = mf.synthesize_skipped(
        baseline["skipped"] if baseline else [], produced_keys, empty_keys
    )

    # AC-010 注入点：对账与导出共享同一 REPEATABLE READ 快照
    if post_export_hook is not None:
        post_export_hook(conn)

    reconcile_field, failures = _reconcile_partitions(
        conn, spec, root, produced, written, lake_pairs
    )
    merged = mf.synthesize_partitions(baseline_partitions, produced)
    value_digest = mf.compute_value_digest(spec, merged)
    baseline_quality = (baseline or {}).get("quality", {})
    content_changed = bool(failures) or baseline is None or (
        value_digest != baseline.get("value_digest")
        or skipped != baseline.get("skipped", [])
        or flagged != baseline_quality.get("flagged_partitions", [])
        or excluded_null != baseline.get("excluded_null_event_time", 0)
    )
    if not content_changed:
        conn.rollback()
        partitions.remove_staging(root, spec.name)
        return _summary(spec, mode, None, baseline_version, merged, [], skipped,
                        reconcile_field, excluded=excluded_null, started=started,
                        no_op=True, reason="content-unchanged", revision_diff=[])

    manifest = {
        "dataset": spec.name,
        "source": mf.SOURCE_TAG,
        "source_snapshot": {"backend_xmin": int(xmin), "taken_at": taken_at},
        "as_of_fidelity": spec.as_of_fidelity,
        "exported_at": mf.iso_utc(dt.datetime.now(dt.UTC)),
        "rows": sum(p["rows"] for p in merged),
        "pairs": sorted({
            p["logical_partition_key"]["pair"]
            for p in merged if "pair" in p["logical_partition_key"]
        }),
        "caliber": {"close": "raw", "adjclose": "none_crypto"},
        "data_version": data_version,
        "value_digest": value_digest,
        "status": "invalid" if failures else "valid",
        "partitions": merged,
        "reconcile": reconcile_field,
        "quality": {"flagged_partitions": flagged, "unresolved_total": flagged_total},
        "skipped": skipped,
        "excluded_null_event_time": excluded_null,
        "revision_diff": mf.partition_diff(baseline_partitions, merged) if mode == "full" else [],
    }
    mf.publish_manifest(root, manifest)
    if failures:
        logger.error("对账失败（%s/%s）: %s", spec.name, data_version, failures)
    if mode == "full":
        removed = _cleanup_orphans(root)
        logger.info("全量模式回收孤儿/staging 文件 %d 个", removed)
    else:
        partitions.remove_staging(root, spec.name)
    conn.rollback()
    return _summary(spec, mode, data_version, baseline_version, merged, failures,
                    skipped, reconcile_field, excluded=excluded_null, started=started,
                    no_op=False, reason=None, revision_diff=manifest["revision_diff"])


def main(argv: list[str] | None = None) -> int:
    """`python -m alphamill.data_bridge.exporter` 入口；退出码契约见 cli 模块。"""
    from alphamill.data_bridge.cli import main as cli_main

    return cli_main(argv)


if __name__ == "__main__":
    import sys

    sys.exit(main())
