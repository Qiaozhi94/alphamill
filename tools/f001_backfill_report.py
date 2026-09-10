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
from datetime import UTC, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from alphamill.data_bridge.collector.db_writer import db_connect  # noqa: E402

GAP_RATIO_THRESHOLD = 0.01  # 缺失率 1%：容忍交易所偶发缺失
# 权威回填窗口（supervisor 与 AC-001 钉死的 BACKFILL_START/END）：聚合一致性对比
# 只在窗口内进行——实时采集会在窗口外持续写入，不属于回填校验范畴。
WINDOW_START = os.getenv("BACKFILL_WINDOW_START", "2024-09-10 00:00:00+00:00")
WINDOW_END = os.getenv("BACKFILL_WINDOW_END", "2026-09-10 15:52:00+00:00")
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
MAX_REPORTED_GAPS = 20


def fetch_one(conn, sql: str, params: tuple = ()) -> tuple:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def symbol_stats(conn, exchange: str, symbol: str) -> dict:
    row = fetch_one(
        conn,
        """
        SELECT count(*), min(time), max(time) FROM ohlcv_1m
        WHERE exchange = %s AND symbol = %s
        """,
        (exchange, symbol),
    )
    count, first, last = int(row[0]), row[1], row[2]
    if count == 0:
        return {"rows": 0, "verdict": "FAIL", "reason": "no rows"}
    expected = int((last - first).total_seconds() // 60) + 1
    missing = expected - count
    gaps = fetch_one(
        conn,
        """
        WITH ordered AS (
            SELECT time, lag(time) OVER (ORDER BY time) AS prev FROM ohlcv_1m
            WHERE exchange = %s AND symbol = %s
        )
        SELECT count(*) FILTER (WHERE time - prev > interval '1 minute'),
               max(time - prev)
        FROM ordered
        """,
        (exchange, symbol),
    )
    gap_count, max_gap = int(gaps[0]), gaps[1]
    gap_ratio = missing / expected
    return {
        "rows": count,
        "first": first.isoformat(),
        "last": last.isoformat(),
        "expected_rows_in_span": expected,
        "missing_rows": missing,
        "missing_ratio": round(gap_ratio, 6),
        "gap_jumps_gt_1m": gap_count,
        "max_gap": str(max_gap),
        "verdict": "PASS" if gap_ratio <= GAP_RATIO_THRESHOLD else "FAIL",
    }


def top_gaps(conn, exchange: str, symbol: str) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH ordered AS (
                SELECT time, lag(time) OVER (ORDER BY time) AS prev FROM ohlcv_1m
                WHERE exchange = %s AND symbol = %s
            )
            SELECT prev, time, time - prev FROM ordered
            WHERE time - prev > interval '5 minutes'
            ORDER BY time - prev DESC
            LIMIT %s
            """,
            (exchange, symbol, MAX_REPORTED_GAPS),
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
                f"SELECT count(*) FROM {view} WHERE bucket >= %s AND bucket < %s",
                (WINDOW_START, WINDOW_END),
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
        "continuous_aggregates": aggregate_stats(conn, exchange),
        "derivatives_rows": table_counts(conn, DERIVATIVES_TABLES),
        "unrecoverable_history_rows": table_counts(conn, LOSING_TABLES),
        "unrecoverable_note": (
            "signals/trades/quality 历史随数据源灭失，空表起步（migration-plan §八）"
        ),
    }
    checks = [v["verdict"] for v in per_symbol.values()] + [
        v["verdict"] for v in report["continuous_aggregates"].values()
    ]
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
            symbols = [r[0] for r in cur.fetchall()]
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
