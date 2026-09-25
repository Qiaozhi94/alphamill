"""TimescaleDB → Parquet 导出编排：快照读取、分区写入、对账与 manifest 发布。

增量继承未变分区；full 以源库全量结果为组成但复用未变文件；对账失败保留 invalid 版本。
"""

from __future__ import annotations

import datetime as dt
import logging
import time
from pathlib import Path
from typing import Any

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import partitions, paths, reconcile, registry, symbol_map
from alphamill.data_bridge.collector.db_writer import db_connect
from alphamill.data_bridge.errors import DataBridgeError
from alphamill.data_bridge.export_policy import guard_full_shrink as _guard_full_shrink
from alphamill.data_bridge.export_policy import merge_partitions as _merge_partitions
from alphamill.data_bridge.export_summary import build_summary as _summary

logger = logging.getLogger(__name__)

# 测试注入点（AC-010 并发 upsert）：签名 (conn) -> None，生产路径恒为 None。
PostExportHook = Any


def _resolve_window(
    conn,
    spec: registry.DatasetSpec,
    mode: str,
    window_end: Any,
    baseline_partitions: list[dict[str, Any]],
) -> tuple[dt.date, dt.date]:
    """窗口 = [start, end)：分区日期 date ∈ [start, end)。end 缺省 = 今日。"""
    end = (
        partitions.as_date(window_end) if window_end is not None else dt.datetime.now(dt.UTC).date()
    )
    span = reconcile.table_span(conn, spec)
    if mode == "full":
        return (dt.date.fromisoformat(span[0]) if span else end), end
    if baseline_partitions:
        start = max(
            dt.date.fromisoformat(p["logical_partition_key"]["date"]) for p in baseline_partitions
        ) + dt.timedelta(days=1)
    else:
        start = dt.date.fromisoformat(span[0]) if span else end
    return start, end


def _reconcile_key(
    spec: registry.DatasetSpec,
    entry: dict[str, Any],
    lake_pairs: dict[tuple[str, str, str], str],
) -> dict[str, str]:
    """从 manifest 条目重建对账查询键；db_symbol 由同事务的 pair 映射求逆。"""
    key = dict(entry["logical_partition_key"])
    if "pair" in key:
        pairs_to_symbols = {
            pair: db_symbol
            for (exchange, market_type, db_symbol), pair in lake_pairs.items()
            if exchange == key.get("exchange", "") and market_type == spec.market_type
        }
        if key["pair"] not in pairs_to_symbols:
            raise DataBridgeError(f"对账键反查失败: {key['pair']!r} 不在导出映射中")
        key["db_symbol"] = pairs_to_symbols[key["pair"]]
    return key


def _reconcile_partitions(
    conn,
    spec: registry.DatasetSpec,
    root: Path,
    produced: list[dict[str, Any]],
    written: list[bool],
    lake_pairs: dict[tuple[str, str, str], str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """逐新写分区与源库对账（同一事务）；继承分区跳过（不可变且读取前会再验）。"""
    report: dict[str, Any] = {"rows": "ok", "time_bounds": "ok", "row_digest": "ok"}
    failures: list[dict[str, Any]] = []
    for entry, is_written in zip(produced, written, strict=True):
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


def export_dataset(
    dataset: str,
    mode: str = "incremental",
    window_end: Any | None = None,
    conn=None,
    lake_root: Path | None = None,
    post_export_hook: PostExportHook = None,
    allow_shrink: bool = False,
    admitted: set[str] | None = None,
    universe_filter: bool = False,
) -> dict[str, Any]:
    """导出单个 dataset（design §4 契约）；返回 manifest 摘要 dict。

    mode: incremental（默认，窗口 = 上一 valid manifest 最大日期 +1 ~ window_end）| full
          （全 span 重导 + 分区级 diff，仅在内容变化时发布新版本）；`window_end` 缺省为今日 00:00Z。
    `allow_shrink`: full 模式下确认源库收缩确属有意（见 `_guard_full_shrink`）。
    `admitted`: F008 导出准入集合（`lake_pair`）；`None`（默认）与 F002 现状逐字节一致。
    `universe_filter`: 按「台账可交易 ∩ 质量门 ACTIVE」在本 dataset 的窗口终点上现算准入集合
        （F008 `FR-006`）；与显式 `admitted` 互斥，只在本参数为真且未显式给出集合时生效。
    """
    if mode not in ("incremental", "full"):
        raise ValueError(f"未知 mode: {mode!r}")
    spec = registry.require_dataset(dataset)
    root = Path(lake_root) if lake_root is not None else paths.lake_root()
    own_conn = conn is None
    conn = conn if conn is not None else db_connect()
    started = time.monotonic()
    try:
        return _export_one(
            conn,
            spec,
            mode,
            window_end,
            root,
            post_export_hook,
            started,
            allow_shrink,
            admitted,
            universe_filter,
        )
    finally:
        reconcile.reset_snapshot_session(conn)
        if own_conn:
            conn.close()


def _admitted_only(
    entries: list[dict[str, Any]], admitted: set[str] | None
) -> list[dict[str, Any]]:
    """按准入集合收窄基线条目：未准入 pair 的日期是策略排除，不是数据缺口（检视 R1-005）。

    没有 `pair` 键的条目（非 pair 分区数据集如 `signals_log`）不参与裁剪，否则整片缺口账被清掉
    （检视第 2 轮 N1）；与 `produce_partitions` 的 `pair_partitioned` 守卫同类。
    """
    if admitted is None:
        return entries
    keys = [(e.get("logical_partition_key") or e).get("pair") for e in entries]
    return [e for e, key in zip(entries, keys, strict=True) if key is None or key in admitted]


def _export_one(
    conn,
    spec: registry.DatasetSpec,
    mode: str,
    window_end: Any,
    root: Path,
    post_export_hook: PostExportHook,
    started: float,
    allow_shrink: bool = False,
    admitted: set[str] | None = None,
    universe_filter: bool = False,
) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    # 回退只允许全量模式（检视 R1-001）：增量把回退版当继承基线会丢中间版本的分区
    baseline_version, baseline = mf.usable_baseline(root, spec.name, allow_fallback=mode == "full")
    baseline_partitions = baseline["partitions"] if baseline else []

    xmin, taken_at = reconcile.begin_snapshot_tx(conn)
    start, end = _resolve_window(conn, spec, mode, window_end, baseline_partitions)
    if universe_filter and admitted is None:
        # F008 导出清单：台账可交易 ∩ 质量门 ACTIVE，取本次导出的窗口终点作为 PIT 时点
        from alphamill.data_bridge.universe.quality_gate import export_admitted

        admitted = export_admitted(
            conn,
            dt.datetime.combine(end, dt.time.min, tzinfo=dt.UTC),
            market_type=spec.market_type,
        )
    symbol_map_ref = symbol_map.export_symbol_map(conn=conn, lake_root=root)
    # 未收窄映射用于质量标记记账（检视 R1-002）：未准入 pair 的标记不该让整轮导出 FATAL
    all_lake_pairs = partitions.lake_pairs_map(conn, market_type=spec.market_type)
    lake_pairs = (
        all_lake_pairs
        if admitted is None
        else {key: pair for key, pair in all_lake_pairs.items() if pair in admitted}
    )
    excluded_null = reconcile.count_null_event_time(conn, spec)
    flagged, flagged_total = (
        partitions.quality_flags(conn, all_lake_pairs)
        if spec.source_table == "ohlcv_1m"
        else ([], 0)
    )
    metadata_changed = mf.metadata_changed(
        baseline, symbol_map_ref.digest, flagged, flagged_total, excluded_null
    )
    ok_reconcile = {"rows": "ok", "time_bounds": "ok", "row_digest": "ok"}
    if (
        start >= end
        and baseline is not None
        and not metadata_changed
        and not (mode == "full" and baseline_partitions)
    ):
        # 窗口为空且已有基线：无新内容可发布（首次导出即使是空表也要发布合法空快照）
        conn.rollback()
        return _summary(
            spec,
            mode,
            None,
            baseline_version,
            [],
            [],
            [],
            ok_reconcile,
            excluded=excluded_null,
            started=started,
            no_op=True,
            reason="window-empty",
            revision_diff=[],
        )

    data_version = mf.next_data_version(root, spec.name, dt.datetime.now(dt.UTC).date())

    produced, produced_keys, written = partitions.produce_partitions(
        root, spec, conn, start, end, baseline_partitions, lake_pairs, admitted
    )
    window_dates = partitions.date_span(start.isoformat(), (end - dt.timedelta(days=1)).isoformat())
    empty_keys = partitions.empty_cell_keys(
        spec,
        mode,
        produced_keys,
        window_dates,
        baseline_partitions=_admitted_only(baseline_partitions, admitted),
        baseline_skipped=_admitted_only(baseline["skipped"] if baseline else [], admitted),
    )
    skipped = mf.synthesize_skipped(
        _admitted_only(baseline["skipped"], admitted) if baseline and mode == "incremental" else [],
        produced_keys,
        empty_keys,
    )

    # AC-010 注入点：对账与导出共享同一 REPEATABLE READ 快照
    if post_export_hook is not None:
        post_export_hook(conn)

    reconcile_field, failures = _reconcile_partitions(
        conn, spec, root, produced, written, lake_pairs
    )
    merged = _merge_partitions(mode, baseline_partitions, produced)
    if mode == "full":
        _guard_full_shrink(baseline_partitions, merged, end, allow_shrink=allow_shrink)
    value_digest = mf.compute_value_digest(spec, merged)
    content_changed = (
        bool(failures)
        or baseline is None
        or (
            value_digest != baseline.get("value_digest")
            or skipped != baseline.get("skipped", [])
            or metadata_changed
        )
    )
    if not content_changed:
        conn.rollback()
        partitions.remove_staging(root, spec.name)
        return _summary(
            spec,
            mode,
            None,
            baseline_version,
            merged,
            [],
            skipped,
            reconcile_field,
            excluded=excluded_null,
            started=started,
            no_op=True,
            reason="content-unchanged",
            revision_diff=[],
        )

    manifest = {
        "dataset": spec.name,
        "source": mf.SOURCE_TAG,
        "source_snapshot": {"backend_xmin": int(xmin), "taken_at": taken_at},
        "symbol_map_digest": symbol_map_ref.digest,
        # 人工确认过的源库收缩留痕，使「为什么这一版分区变少了」事后可查（F002-R3-02）。
        "shrink_confirmed": bool(allow_shrink and mode == "full"),
        "as_of_fidelity": spec.as_of_fidelity,
        "exported_at": mf.iso_utc(dt.datetime.now(dt.UTC)),
        "rows": sum(p["rows"] for p in merged),
        "pairs": sorted(
            {
                p["logical_partition_key"]["pair"]
                for p in merged
                if "pair" in p["logical_partition_key"]
            }
        ),
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
        removed = partitions.cleanup_orphans(root)
        logger.info("全量模式回收孤儿/staging 文件 %d 个", removed)
    else:
        partitions.remove_staging(root, spec.name)
    conn.rollback()
    return _summary(
        spec,
        mode,
        data_version,
        baseline_version,
        merged,
        failures,
        skipped,
        reconcile_field,
        excluded=excluded_null,
        started=started,
        no_op=False,
        reason=None,
        revision_diff=manifest["revision_diff"],
    )


def main(argv: list[str] | None = None) -> int:
    from alphamill.data_bridge.cli import main as cli_main

    return cli_main(argv)


if __name__ == "__main__":
    import sys

    sys.exit(main())
