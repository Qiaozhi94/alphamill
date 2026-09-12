from __future__ import annotations

import argparse
import json
import logging
import os
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import ccxt
from psycopg2.extras import Json, execute_values

try:  # Support both package imports and the legacy standalone container entrypoint.
    from .db_writer import db_connect
except ImportError:  # pragma: no cover - exercised only by direct script execution.
    from db_writer import db_connect


PROJECT_ROOT = next(
    (
        root
        for root in [
            Path(__file__).resolve().parents[1],
            Path.cwd(),
            Path(__file__).resolve().parent,
        ]
        if (root / "db" / "migrations" / "003_derivatives_market_data.sql").exists()
    ),
    Path(__file__).resolve().parents[1],
)
MIGRATION = PROJECT_ROOT / "db" / "migrations" / "003_derivatives_market_data.sql"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
DEFAULT_PAIRS = "BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT,XRP/USDT,DOGE/USDT"
DEFAULT_DATASETS = "funding,open_interest,basis"

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("derivatives-market-backfill")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Backfill derivatives funding/open-interest/mark-index basis data."
    )
    parser.add_argument("--exchange", default=os.getenv("DERIVATIVES_EXCHANGE", "binanceusdm"))
    parser.add_argument(
        "--symbols", default=os.getenv("DERIVATIVES_SYMBOLS", os.getenv("SYMBOLS", DEFAULT_PAIRS))
    )
    parser.add_argument("--datasets", default=os.getenv("DERIVATIVES_DATASETS", DEFAULT_DATASETS))
    parser.add_argument("--start", default=os.getenv("DERIVATIVES_START"))
    parser.add_argument("--end", default=os.getenv("DERIVATIVES_END"))
    parser.add_argument("--days", type=int, default=int(os.getenv("DERIVATIVES_DAYS", "30")))
    parser.add_argument("--timeframe", default=os.getenv("DERIVATIVES_TIMEFRAME", "1h"))
    parser.add_argument(
        "--limit", type=int, default=int(os.getenv("DERIVATIVES_FETCH_LIMIT", "100"))
    )
    parser.add_argument("--retries", type=int, default=int(os.getenv("DERIVATIVES_RETRIES", "3")))
    parser.add_argument("--schema-only", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    start, end = date_range(args.start, args.end, args.days)
    symbols = csv(args.symbols)
    datasets = csv(args.datasets)
    report_path = PROJECT_ROOT / (
        args.output
        or "reports/derivatives-market-data-backfill-"
        f"{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.json"
    )

    conn = db_connect()
    try:
        ensure_schema(conn)
        if args.schema_only:
            result = {
                "status": "schema_ready",
                "exchange": args.exchange,
                "symbols": symbols,
                "datasets": datasets,
                "start": str(start),
                "end": str(end),
            }
        else:
            exchange = build_exchange(args.exchange)
            try:
                result = run_backfill(
                    conn,
                    exchange,
                    args.exchange,
                    symbols,
                    datasets,
                    start,
                    end,
                    args.timeframe,
                    args.limit,
                    args.retries,
                )
            finally:
                close = getattr(exchange, "close", None)
                if callable(close):
                    close()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        write_markdown(report_path.with_suffix(".md"), result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get("status") == "failed" else 0
    finally:
        conn.close()


def csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


BASIS_UNSUPPORTED_EXCHANGES = set(
    csv(os.getenv("DERIVATIVES_BASIS_UNSUPPORTED_EXCHANGES", "binanceusdm"))
)


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def date_range(
    start_value: str | None, end_value: str | None, days: int
) -> tuple[datetime, datetime]:
    end = parse_utc(end_value) if end_value else datetime.now(UTC)
    start = parse_utc(start_value) if start_value else end - timedelta(days=days)
    start = start.replace(second=0, microsecond=0)
    end = end.replace(second=0, microsecond=0)
    if start >= end:
        raise ValueError("start must be before end")
    return start, end


def ensure_schema(conn) -> None:
    sql = MIGRATION.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def build_exchange(exchange_id: str):
    exchange_class = getattr(ccxt, exchange_id)
    config = {
        "enableRateLimit": True,
        "timeout": 30_000,
        "options": {"defaultType": "swap"},
    }
    api_key = os.getenv(f"{exchange_id.upper()}_API_KEY", "")
    secret = os.getenv(f"{exchange_id.upper()}_SECRET", "")
    password = os.getenv(f"{exchange_id.upper()}_PASSPHRASE", "")
    if api_key and secret:
        config["apiKey"] = api_key
        config["secret"] = secret
    if password:
        config["password"] = password
    # 本机 DNS 对部分交易所域名存在污染时，经内网代理出网（默认关闭，不影响直连行为）。
    exchange_proxy = os.getenv(f"{exchange_id.upper()}_HTTPS_PROXY", "")
    if exchange_proxy:
        config["httpsProxy"] = exchange_proxy
    exchange = exchange_class(config)
    exchange.load_markets()
    return exchange


def derivative_symbol(exchange, symbol: str) -> str:
    if symbol in exchange.markets and exchange.markets[symbol].get("swap"):
        return symbol
    if "/" in symbol and ":" not in symbol:
        base, quote = symbol.split("/", 1)
        candidate = f"{base}/{quote}:{quote}"
        if candidate in exchange.markets:
            return candidate
    return symbol


def run_backfill(
    conn,
    exchange,
    exchange_id: str,
    symbols: list[str],
    datasets: list[str],
    start: datetime,
    end: datetime,
    timeframe: str,
    limit: int,
    retries: int,
) -> dict:
    rows = []
    for symbol in symbols:
        market_symbol = derivative_symbol(exchange, symbol)
        item = {"symbol": symbol, "market_symbol": market_symbol, "datasets": {}}
        if "funding" in datasets:
            item["datasets"]["funding"] = run_dataset(
                conn,
                exchange_id,
                symbol,
                "funding",
                "none",
                start,
                end,
                lambda symbol=symbol, market_symbol=market_symbol: fetch_and_store_funding(
                    conn, exchange, exchange_id, symbol, market_symbol, start, end, limit, retries
                ),
            )
        if "open_interest" in datasets:
            item["datasets"]["open_interest"] = run_dataset(
                conn,
                exchange_id,
                symbol,
                "open_interest",
                timeframe,
                start,
                end,
                lambda symbol=symbol, market_symbol=market_symbol: fetch_and_store_open_interest(
                    conn,
                    exchange,
                    exchange_id,
                    symbol,
                    market_symbol,
                    start,
                    end,
                    timeframe,
                    limit,
                    retries,
                ),
            )
        if "basis" in datasets:
            item["datasets"]["basis"] = run_dataset(
                conn,
                exchange_id,
                symbol,
                "basis",
                timeframe,
                start,
                end,
                lambda symbol=symbol, market_symbol=market_symbol: fetch_and_store_basis(
                    conn,
                    exchange,
                    exchange_id,
                    symbol,
                    market_symbol,
                    start,
                    end,
                    timeframe,
                    limit,
                    retries,
                ),
            )
        rows.append(item)
    return {
        "status": overall_backfill_status(rows),
        "exchange": exchange_id,
        "start": str(start),
        "end": str(end),
        "timeframe": timeframe,
        "symbols": rows,
        "totals": summarize_totals(rows),
    }


def run_dataset(
    conn,
    exchange_id: str,
    symbol: str,
    dataset: str,
    timeframe: str,
    start: datetime,
    end: datetime,
    fetcher,
) -> dict:
    try:
        return fetcher()
    except Exception as exc:
        logger.exception(
            "dataset failed exchange=%s symbol=%s dataset=%s", exchange_id, symbol, dataset
        )
        conn.rollback()
        save_progress(
            conn, exchange_id, symbol, dataset, timeframe, start, end, start, "failed", 0, str(exc)
        )
        return {"rows_fetched": 0, "rows_upserted": 0, "status": "failed", "error": str(exc)}


def fetch_and_store_funding(
    conn,
    exchange,
    exchange_id: str,
    symbol: str,
    market_symbol: str,
    start: datetime,
    end: datetime,
    limit: int,
    retries: int,
) -> dict:
    raw_rows = fetch_paginated(
        lambda since: exchange.fetch_funding_rate_history(market_symbol, since=since, limit=limit),
        start,
        end,
        retries,
        exchange.rateLimit,
    )
    rows = []
    for row in raw_rows:
        ts = row.get("timestamp")
        if ts is None:
            continue
        at = dt_from_ms(ts)
        if not (start <= at < end):
            continue
        info = row.get("info") or {}
        next_funding = row.get("nextFundingTimestamp") or numeric(info.get("nextFundingTime"))
        rows.append(
            (
                at,
                exchange_id,
                symbol,
                numeric(row.get("fundingRate")),
                dt_from_ms(next_funding) if next_funding else None,
                numeric(row.get("markPrice") or info.get("markPx")),
                numeric(row.get("indexPrice") or info.get("indexPx")),
                Json(info),
            )
        )
    count = upsert_funding(conn, rows)
    save_progress(
        conn, exchange_id, symbol, "funding", "none", start, end, end, "complete", count, None
    )
    return {"rows_fetched": len(raw_rows), "rows_upserted": count, "status": "complete"}


def fetch_and_store_open_interest(
    conn,
    exchange,
    exchange_id: str,
    symbol: str,
    market_symbol: str,
    start: datetime,
    end: datetime,
    timeframe: str,
    limit: int,
    retries: int,
) -> dict:
    if not getattr(exchange, "has", {}).get("fetchOpenInterestHistory"):
        save_progress(
            conn,
            exchange_id,
            symbol,
            "open_interest",
            timeframe,
            start,
            end,
            start,
            "unsupported",
            0,
            "fetchOpenInterestHistory unsupported",
        )
        return {"rows_fetched": 0, "rows_upserted": 0, "status": "unsupported"}
    requested_start = start
    configured_days = int(os.getenv("DERIVATIVES_OPEN_INTEREST_MAX_DAYS", "0") or 0)
    if configured_days > 0:
        # This is an explicit exchange-availability boundary, not an observed-data fallback.
        start = max(start, end - timedelta(days=configured_days))
    elif exchange_id == "okx":
        # OKX rejects old open-interest history windows with 50030 Illegal time range.
        start = max(start, end - timedelta(days=29))
    effective_start = start
    raw_rows = []
    chunk_start = start
    while chunk_start < end:
        chunk_end = min(chunk_start + timedelta(days=29), end)
        chunk_end_ms = int(chunk_end.timestamp() * 1000)
        raw_rows.extend(
            fetch_paginated(
                lambda since, until=chunk_end_ms: exchange.fetch_open_interest_history(
                    market_symbol,
                    timeframe=timeframe,
                    since=since,
                    limit=limit,
                    params={"until": until},
                ),
                chunk_start,
                chunk_end,
                retries,
                exchange.rateLimit,
            )
        )
        chunk_start = chunk_end
    rows = []
    for row in raw_rows:
        ts = row.get("timestamp")
        if ts is None:
            continue
        at = dt_from_ms(ts)
        if not (start <= at < end):
            continue
        info = row.get("info") or {}
        rows.append(
            (
                at,
                exchange_id,
                symbol,
                timeframe,
                numeric(row.get("openInterestAmount") or row.get("openInterest")),
                numeric(row.get("openInterestValue")),
                numeric(row.get("baseVolume")),
                numeric(row.get("quoteVolume")),
                Json(info),
            )
        )
    count = upsert_open_interest(conn, rows)
    save_progress(
        conn,
        exchange_id,
        symbol,
        "open_interest",
        timeframe,
        requested_start,
        end,
        end,
        "complete",
        count,
        None,
    )
    status = "partial_recent_window" if start > requested_start else "complete"
    return {
        "rows_fetched": len(raw_rows),
        "rows_upserted": count,
        "status": status,
        "effective_start": str(effective_start),
    }


def fetch_and_store_basis(
    conn,
    exchange,
    exchange_id: str,
    symbol: str,
    market_symbol: str,
    start: datetime,
    end: datetime,
    timeframe: str,
    limit: int,
    retries: int,
) -> dict:
    if exchange_id in BASIS_UNSUPPORTED_EXCHANGES:
        save_progress(
            conn,
            exchange_id,
            symbol,
            "basis",
            timeframe,
            start,
            end,
            start,
            "unsupported",
            0,
            "exchange is explicitly allowlisted as lacking mark/index OHLCV",
        )
        return {
            "mark_rows": 0,
            "index_rows": 0,
            "rows_upserted": 0,
            "status": "unsupported",
            "boundary": "exchange_mark_index_ohlcv_unavailable",
        }

    mark_rows = fetch_price_ohlcv(
        exchange, market_symbol, timeframe, start, end, limit, retries, "mark"
    )
    index_rows = fetch_price_ohlcv(
        exchange, market_symbol, timeframe, start, end, limit, retries, "index"
    )
    by_index = {row[0]: row for row in index_rows}
    rows = []
    for mark in mark_rows:
        idx = by_index.get(mark[0])
        if not idx:
            continue
        at = dt_from_ms(mark[0])
        if not (start <= at < end):
            continue
        basis_close = (
            numeric(mark[4]) - numeric(idx[4])
            if numeric(mark[4]) is not None and numeric(idx[4]) not in {None, 0.0}
            else None
        )
        index_close = numeric(idx[4])
        rows.append(
            (
                at,
                exchange_id,
                symbol,
                timeframe,
                numeric(mark[1]),
                numeric(mark[2]),
                numeric(mark[3]),
                numeric(mark[4]),
                numeric(idx[1]),
                numeric(idx[2]),
                numeric(idx[3]),
                index_close,
                basis_close,
                basis_close / index_close if basis_close is not None and index_close else None,
                Json({"market_symbol": market_symbol}),
            )
        )
    count = upsert_basis(conn, rows)
    save_progress(
        conn, exchange_id, symbol, "basis", timeframe, start, end, end, "complete", count, None
    )
    return {
        "mark_rows": len(mark_rows),
        "index_rows": len(index_rows),
        "rows_upserted": count,
        "status": "complete",
    }


def fetch_paginated(
    fetcher, start: datetime, end: datetime, retries: int, rate_limit_ms: int | None
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    since = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    while since < end_ms:
        batch = retry_fetch(lambda since=since: fetcher(since), retries)
        batch = [
            row for row in batch if row.get("timestamp") is not None and row["timestamp"] < end_ms
        ]
        if not batch:
            break
        rows.extend(batch)
        next_since = max(int(row["timestamp"]) for row in batch) + 1
        if next_since <= since:
            break
        since = next_since
        time.sleep((rate_limit_ms or 200) / 1000)
    return rows


def fetch_price_ohlcv(
    exchange,
    market_symbol: str,
    timeframe: str,
    start: datetime,
    end: datetime,
    limit: int,
    retries: int,
    price_type: str,
) -> list[list]:
    rows = []
    since = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    while since < end_ms:
        if price_type == "mark" and getattr(exchange, "has", {}).get("fetchMarkOHLCV"):
            batch = retry_fetch(
                lambda since=since: exchange.fetch_mark_ohlcv(
                    market_symbol, timeframe=timeframe, since=since, limit=limit
                ),
                retries,
            )
        elif price_type == "index" and getattr(exchange, "has", {}).get("fetchIndexOHLCV"):
            batch = retry_fetch(
                lambda since=since: exchange.fetch_index_ohlcv(
                    market_symbol, timeframe=timeframe, since=since, limit=limit
                ),
                retries,
            )
        else:
            batch = retry_fetch(
                lambda since=since: exchange.fetch_ohlcv(
                    market_symbol,
                    timeframe=timeframe,
                    since=since,
                    limit=limit,
                    params={"price": price_type},
                ),
                retries,
            )
        batch = [row for row in batch if row[0] < end_ms]
        if not batch:
            break
        rows.extend(batch)
        next_since = int(batch[-1][0]) + timeframe_ms(timeframe)
        if next_since <= since:
            break
        since = next_since
        time.sleep((exchange.rateLimit or 200) / 1000)
    return rows


def retry_fetch(fetcher, retries: int):
    for attempt in range(1, retries + 1):
        try:
            return fetcher()
        except Exception as exc:
            if attempt >= retries:
                raise
            sleep_for = min(2**attempt, 10)
            logger.warning(
                "fetch failed attempt=%s/%s retry_in=%ss error=%s", attempt, retries, sleep_for, exc
            )
            time.sleep(sleep_for)
    return []


def upsert_funding(conn, rows: list[tuple]) -> int:
    if not rows:
        return 0
    sql = """
        INSERT INTO derivatives_funding_rates
            (
                time, exchange, symbol, funding_rate, next_funding_time,
                mark_price, index_price, metadata
            )
        VALUES %s
        ON CONFLICT (exchange, symbol, time) DO UPDATE SET
            funding_rate = EXCLUDED.funding_rate,
            next_funding_time = EXCLUDED.next_funding_time,
            mark_price = EXCLUDED.mark_price,
            index_price = EXCLUDED.index_price,
            metadata = EXCLUDED.metadata,
            ingested_at = NOW()
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows)
    conn.commit()
    return len(rows)


def upsert_open_interest(conn, rows: list[tuple]) -> int:
    if not rows:
        return 0
    sql = """
        INSERT INTO derivatives_open_interest
            (
                time, exchange, symbol, timeframe, open_interest, open_interest_value,
                base_volume, quote_volume, metadata
            )
        VALUES %s
        ON CONFLICT (exchange, symbol, timeframe, time) DO UPDATE SET
            open_interest = EXCLUDED.open_interest,
            open_interest_value = EXCLUDED.open_interest_value,
            base_volume = EXCLUDED.base_volume,
            quote_volume = EXCLUDED.quote_volume,
            metadata = EXCLUDED.metadata,
            ingested_at = NOW()
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows)
    conn.commit()
    return len(rows)


def upsert_basis(conn, rows: list[tuple]) -> int:
    if not rows:
        return 0
    sql = """
        INSERT INTO derivatives_mark_index_basis
            (time, exchange, symbol, timeframe, mark_open, mark_high, mark_low, mark_close,
             index_open, index_high, index_low, index_close, basis_close, basis_pct, metadata)
        VALUES %s
        ON CONFLICT (exchange, symbol, timeframe, time) DO UPDATE SET
            mark_open = EXCLUDED.mark_open,
            mark_high = EXCLUDED.mark_high,
            mark_low = EXCLUDED.mark_low,
            mark_close = EXCLUDED.mark_close,
            index_open = EXCLUDED.index_open,
            index_high = EXCLUDED.index_high,
            index_low = EXCLUDED.index_low,
            index_close = EXCLUDED.index_close,
            basis_close = EXCLUDED.basis_close,
            basis_pct = EXCLUDED.basis_pct,
            metadata = EXCLUDED.metadata,
            ingested_at = NOW()
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows)
    conn.commit()
    return len(rows)


def save_progress(
    conn,
    exchange_id: str,
    symbol: str,
    dataset: str,
    timeframe: str,
    start: datetime,
    end: datetime,
    next_since: datetime,
    status: str,
    rows_upserted: int,
    last_error: str | None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO derivatives_backfill_progress (
                exchange, symbol, dataset, timeframe, target_start, target_end,
                next_since, status, rows_upserted, last_error, updated_at, completed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(),
                    CASE WHEN %s IN ('complete', 'unsupported') THEN NOW() ELSE NULL END)
            ON CONFLICT (exchange, symbol, dataset, timeframe, target_start, target_end)
            DO UPDATE SET
                next_since = EXCLUDED.next_since,
                status = EXCLUDED.status,
                rows_upserted = EXCLUDED.rows_upserted,
                last_error = EXCLUDED.last_error,
                updated_at = NOW(),
                completed_at = CASE
                    WHEN EXCLUDED.status IN ('complete', 'unsupported') THEN NOW()
                    ELSE derivatives_backfill_progress.completed_at
                END
            """,
            (
                exchange_id,
                symbol,
                dataset,
                timeframe,
                start,
                end,
                next_since,
                status,
                rows_upserted,
                last_error,
                status,
            ),
        )
    conn.commit()


def summarize_totals(rows: list[dict]) -> dict:
    totals: dict[str, int] = {}
    for symbol in rows:
        for name, stats in symbol["datasets"].items():
            totals[name] = totals.get(name, 0) + int(stats.get("rows_upserted", 0))
    return totals


def overall_backfill_status(rows: list[dict]) -> str:
    """Any failed dataset makes the batch fail; unsupported is an explicit boundary."""
    statuses = [stats.get("status") for symbol in rows for stats in symbol["datasets"].values()]
    return "failed" if "failed" in statuses else "complete"


def dt_from_ms(value: Any) -> datetime:
    return datetime.fromtimestamp(int(value) / 1000, tz=UTC)


def numeric(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def timeframe_ms(timeframe: str) -> int:
    unit = timeframe[-1]
    value = int(timeframe[:-1])
    if unit == "m":
        return value * 60_000
    if unit == "h":
        return value * 3_600_000
    if unit == "d":
        return value * 86_400_000
    raise ValueError(f"Unsupported timeframe: {timeframe}")


def write_markdown(path: Path, result: dict) -> None:
    lines = [
        "# 衍生品微观结构数据回补报告",
        "",
        f"生成时间：{datetime.now(UTC).isoformat()}",
        "",
        "## 结果",
        "",
        f"- 状态：`{result['status']}`",
        f"- 交易所：`{result['exchange']}`",
        f"- 时间范围：{result['start']} 至 {result['end']}",
    ]
    if result["status"] == "schema_ready":
        lines.extend(["- 本次仅验证/创建 schema，未请求交易所数据。", ""])
    else:
        lines.extend(["", "| 数据集 | 写入行数 |", "| --- | ---: |"])
        for dataset, count in result["totals"].items():
            lines.append(f"| {dataset} | {count} |")
        lines.extend(
            [
                "",
                "## 分交易对",
                "",
                "| 交易对 | 市场符号 | Funding | Open Interest | Basis |",
                "| --- | --- | ---: | ---: | ---: |",
            ]
        )
        for item in result["symbols"]:
            stats = item["datasets"]
            lines.append(
                f"| {item['symbol']} | `{item['market_symbol']}` | "
                f"{stats.get('funding', {}).get('rows_upserted', 0)} | "
                f"{stats.get('open_interest', {}).get('rows_upserted', 0)} | "
                f"{stats.get('basis', {}).get('rows_upserted', 0)} |"
            )
    lines.extend(
        [
            "## 后续",
            "",
            "- 数据写入后，下一步是生成衍生品特征数据集并与 1h 低频监督学习数据按时间对齐。",
            "- 当前脚本只采集数据，不调整 dry-run 或策略配置。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
