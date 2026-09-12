"""F001 回填完整性校验与报告生成（design §3 口径的唯一实现）。

用法：
    .venv/bin/python tools/f001_backfill_report.py [--report reports/f001-backfill-<date>.json]

口径（F001 design §3，唯一权威定义）：
- ohlcv_1m 逐交易对：count vs 期望行数（(max-min)/60s+1）的缺失率 ≤ 阈值；
  时间轴用 lag 扫描缺口，缺口区间记入报告。
- 连续聚合：行数与 1m 基表按桶重算精确一致。
- signals/trades/quality/dryrun：不可重建资产，报告显式记录损失（空表起步）。

退出码 0 = 校验通过；非 0 = 存在判红项。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from f001_backfill_config import (  # noqa: E402
    configured_symbols,
    derivative_window,
    expected_minute_rows,
    listing_start,
    unavailable_symbols,
    window_datetimes,
    window_values,
)

from alphamill.data_bridge.collector.db_writer import db_connect  # noqa: E402
from alphamill.data_bridge.collector.derivatives_market_backfill import (  # noqa: E402
    BASIS_UNSUPPORTED_EXCHANGES,
)

GAP_RATIO_THRESHOLD = 0.01  # 缺失率 1%：容忍交易所偶发缺失
WINDOW_START_TEXT, WINDOW_END_TEXT = window_values()
WINDOW_START, WINDOW_END = window_datetimes()
AGGREGATES = {
    "ohlcv_5m": "5 minutes",
    "ohlcv_15m": "15 minutes",
    "ohlcv_1h": "1 hour",
    "ohlcv_4h": "4 hours",
    "ohlcv_1d": "1 day",
}
LOSING_TABLES = [
    "signals_log",
    "trades_log",
    "ohlcv_quality_flags",
    "dryrun_open_positions",
    "dryrun_runtime_snapshots",
]
DERIVATIVES_TABLES = [
    "derivatives_funding_rates",
    "derivatives_open_interest",
    "derivatives_mark_index_basis",
]
DERIVATIVE_DATASETS = {
    "derivatives_funding_rates": ("funding", timedelta(hours=8)),
    "derivatives_open_interest": ("open_interest", timedelta(hours=6)),
    "derivatives_mark_index_basis": ("basis", timedelta(hours=1)),
}
DERIVATIVES_EXCHANGE = os.getenv("DERIVATIVES_EXCHANGE", "binanceusdm")
MAX_REPORTED_GAPS = 20


def fetch_one(conn, sql: str, params: tuple = ()) -> tuple:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def symbol_stats(conn, exchange: str, symbol: str) -> dict:
    effective_start = listing_start(symbol, WINDOW_START)
    row = fetch_one(
        conn,
        """SELECT
            count(*) FILTER (WHERE time >= %s AND time < %s),
            min(time), max(time)
        FROM ohlcv_1m
        WHERE exchange = %s AND symbol = %s""",
        (effective_start, WINDOW_END, exchange, symbol),
    )
    count, first, last = int(row[0]), row[1], row[2]
    expected = expected_minute_rows(effective_start, WINDOW_END)
    if count == 0:
        if symbol in unavailable_symbols():
            return {
                "rows": 0,
                "expected_rows_in_window": 0,
                "availability_start": effective_start.isoformat(),
                "status": "unavailable",
                "verdict": "PASS",
            }
        return {
            "rows": 0,
            "expected_rows_in_window": expected,
            "availability_start": effective_start.isoformat(),
            "verdict": "FAIL",
            "reason": "no rows in authoritative window",
        }
    missing = expected - count
    gaps = fetch_one(
        conn,
        """
            WITH ordered AS (
                SELECT time, lag(time) OVER (ORDER BY time) AS prev FROM ohlcv_1m
                WHERE exchange = %s AND symbol = %s AND time >= %s AND time < %s
            )
            SELECT count(*) FILTER (WHERE time - prev > interval '1 minute'),
                   max(time - prev)
            FROM ordered
        """,
        (exchange, symbol, effective_start, WINDOW_END),
    )
    gap_count, max_gap = int(gaps[0]), gaps[1]
    gap_ratio = missing / expected
    boundary_ok = first <= effective_start and last >= WINDOW_END - timedelta(minutes=1)
    return {
        "rows": count,
        "first": first.isoformat(),
        "last": last.isoformat(),
        "expected_rows_in_window": expected,
        "missing_rows": missing,
        "missing_ratio": round(gap_ratio, 6),
        "gap_jumps_gt_1m": gap_count,
        "max_gap": str(max_gap),
        "window_start": effective_start.isoformat(),
        "window_end": WINDOW_END.isoformat(),
        "boundary_ok": boundary_ok,
        "verdict": "PASS" if gap_ratio <= GAP_RATIO_THRESHOLD and boundary_ok else "FAIL",
    }


def top_gaps(conn, exchange: str, symbol: str) -> list[dict]:
    effective_start = listing_start(symbol, WINDOW_START)
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH ordered AS (
                SELECT time, lag(time) OVER (ORDER BY time) AS prev FROM ohlcv_1m
                WHERE exchange = %s AND symbol = %s AND time >= %s AND time < %s
            )
            SELECT prev, time, time - prev FROM ordered
            WHERE time - prev > interval '5 minutes'
            ORDER BY time - prev DESC
            LIMIT %s
            """,
            (exchange, symbol, effective_start, WINDOW_END, MAX_REPORTED_GAPS),
        )
        return [
            {"from": r[0].isoformat(), "to": r[1].isoformat(), "gap": str(r[2])}
            for r in cur.fetchall()
        ]


def aggregate_stats(conn, exchange: str) -> dict:
    stats = {}
    for view, bucket in AGGREGATES.items():
        view_count = int(
            fetch_one(
                conn,
                f"SELECT count(*) FROM {view} WHERE exchange = %s AND bucket >= %s AND bucket < %s",
                (exchange, WINDOW_START, WINDOW_END),
            )[0]
        )
        # 连续聚合保留 symbol 维度：基表侧按 (symbol, bucket) 去重后对齐。
        bucket_count = int(
            fetch_one(
                conn,
                f"""
                SELECT count(*) FROM (
                    SELECT symbol, time_bucket('{bucket}', time) AS b
                    FROM ohlcv_1m
                    WHERE exchange = %s
                      AND time >= %s AND time < %s
                    GROUP BY symbol, b
                ) t
                """,
                (exchange, WINDOW_START, WINDOW_END),
            )[0]
        )
        stats[view] = {
            "rows": view_count,
            "distinct_symbol_buckets_in_base": bucket_count,
            "verdict": "PASS" if view_count == bucket_count else "FAIL",
        }
    return stats


def table_counts(conn, tables: list[str]) -> dict:
    return {t: int(fetch_one(conn, f"SELECT count(*) FROM {t}")[0]) for t in tables}


def derivative_verdict(
    *,
    dataset: str,
    exchange: str,
    actual_rows: int,
    populated_symbols: int,
    expected_symbols: int,
    effective_start: datetime,
    effective_end: datetime,
    failed_progress: int,
    progress_window_covers_authoritative_window: bool = True,
    progress_window_start: datetime | None = None,
    progress_window_end: datetime | None = None,
) -> dict:
    if dataset == "basis" and exchange in BASIS_UNSUPPORTED_EXCHANGES:
        return {
            "status": "unsupported",
            "actual_rows": actual_rows,
            "expected_min_rows": 0,
            "effective_start": effective_start.isoformat(),
            "effective_end": effective_end.isoformat(),
            "progress_window_covers_authoritative_window": (
                progress_window_covers_authoritative_window
            ),
            "boundary": "exchange_mark_index_ohlcv_unavailable",
            "verdict": "PASS",
        }

    interval = DERIVATIVE_DATASETS[
        {
            "funding": "derivatives_funding_rates",
            "open_interest": "derivatives_open_interest",
            "basis": "derivatives_mark_index_basis",
        }[dataset]
    ][1]
    duration = effective_end - effective_start
    expected_per_symbol = max(1, int(duration.total_seconds() // interval.total_seconds()))
    expected_min_rows = expected_per_symbol * expected_symbols
    status = "failed" if failed_progress else "complete"
    passed = (
        status == "complete"
        and progress_window_covers_authoritative_window
        and populated_symbols == expected_symbols
        and actual_rows >= expected_min_rows
    )
    return {
        "status": status,
        "actual_rows": actual_rows,
        "expected_min_rows": expected_min_rows,
        "effective_start": effective_start.isoformat(),
        "effective_end": effective_end.isoformat(),
        "populated_symbols": populated_symbols,
        "expected_symbols": expected_symbols,
        "progress_window_covers_authoritative_window": progress_window_covers_authoritative_window,
        "progress_window_start": progress_window_start.isoformat()
        if progress_window_start
        else None,
        "progress_window_end": progress_window_end.isoformat() if progress_window_end else None,
        "verdict": "PASS" if passed else "FAIL",
    }


def derivative_stats(conn, exchange: str, symbols: list[str]) -> dict:
    stats = {}
    for table, (dataset, interval) in DERIVATIVE_DATASETS.items():
        progress = fetch_one(
            conn,
            """SELECT min(target_start), max(target_end),
                      count(*) FILTER (WHERE status = 'failed')
               FROM derivatives_backfill_progress
               WHERE exchange = %s AND dataset = %s""",
            (exchange, dataset),
        )
        progress_start, progress_end, failed_progress = progress
        progress_covers_window = bool(
            progress_start
            and progress_end
            and progress_start <= WINDOW_START
            and progress_end >= WINDOW_END
        )
        effective_start, effective_end = derivative_window(dataset, WINDOW_START, WINDOW_END)
        data = fetch_one(
            conn,
            f"""SELECT count(*), count(DISTINCT symbol)
                FROM {table}
                WHERE exchange = %s AND time >= %s AND time < %s""",
            (exchange, WINDOW_START, WINDOW_END),
        )
        stats[table] = derivative_verdict(
            dataset=dataset,
            exchange=exchange,
            actual_rows=int(data[0]),
            populated_symbols=int(data[1]),
            expected_symbols=len(symbols),
            effective_start=effective_start,
            effective_end=effective_end,
            failed_progress=int(failed_progress or 0),
            progress_window_covers_authoritative_window=progress_covers_window,
            progress_window_start=progress_start,
            progress_window_end=progress_end,
        )
        stats[table]["interval"] = str(interval)
    return stats


def build_report(conn, exchange: str, symbols: list[str]) -> dict:
    per_symbol = {s: symbol_stats(conn, exchange, s) for s in symbols}
    gaps = {s: top_gaps(conn, exchange, s) for s in symbols}
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "feature": "F001",
        "check_spec": "F001 design §3 / spec FR-001 AC-001",
        "exchange": exchange,
        "missing_ratio_threshold": GAP_RATIO_THRESHOLD,
        "ohlcv_1m": per_symbol,
        "ohlcv_1m_top_gaps": gaps,
        "backfill_window": {
            "start": WINDOW_START_TEXT,
            "end": WINDOW_END_TEXT,
            "timezone": "UTC",
            "end_is_exclusive": True,
        },
        "continuous_aggregates": aggregate_stats(conn, exchange),
        "derivatives_exchange": DERIVATIVES_EXCHANGE,
        "derivatives": derivative_stats(conn, DERIVATIVES_EXCHANGE, symbols),
        "derivatives_rows": table_counts(conn, DERIVATIVES_TABLES),
        "unrecoverable_history_rows": table_counts(conn, LOSING_TABLES),
        "unrecoverable_note": (
            "signals/trades/quality 历史随数据源灭失，空表起步（migration-plan §八）"
        ),
    }
    checks = (
        [v["verdict"] for v in per_symbol.values()]
        + [v["verdict"] for v in report["continuous_aggregates"].values()]
        + [v["verdict"] for v in report["derivatives"].values()]
    )
    report["verdict"] = "PASS" if checks and all(v == "PASS" for v in checks) else "FAIL"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--exchange", default=os.getenv("EXCHANGES", "binance").split(",")[0])
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    conn = db_connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT symbol FROM ohlcv_1m WHERE exchange = %s ORDER BY 1",
                (args.exchange,),
            )
            symbols = configured_symbols()
        if not symbols:
            print(f"no rows for exchange={args.exchange}; nothing to verify")
            return 2
        report = build_report(conn, args.exchange, symbols)
    finally:
        conn.close()

    path = args.report or f"reports/f001-backfill-{datetime.now(UTC):%Y%m%d}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"report -> {path}")
    print(f"verdict: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
