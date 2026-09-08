from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import ccxt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-28"
DEFAULT_EXISTING = {"BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover OKX USDT swap universe and compare it with local futures data."
    )
    parser.add_argument("--data-dir", default="freqtrade/user_data/data/okx/futures")
    parser.add_argument("--top", type=int, default=40)
    parser.add_argument(
        "--output", default=f"reports/okx-swap-universe-discovery-{DATE.replace('-', '')}.json"
    )
    args = parser.parse_args()

    exchange = ccxt.okx(
        {"enableRateLimit": True, "timeout": 30_000, "options": {"defaultType": "swap"}}
    )
    markets = exchange.load_markets()
    tickers = exchange.fetch_tickers()
    local_pairs = discover_local_pairs(PROJECT_ROOT / args.data_dir)

    rows = []
    for symbol, market in markets.items():
        if not is_usdt_swap(market):
            continue
        pair = normalized_pair(market)
        ticker = tickers.get(symbol) or tickers.get(market.get("symbol")) or {}
        quote_volume = (
            numeric(ticker.get("quoteVolume"))
            or numeric((ticker.get("info") or {}).get("volCcy24h"))
            or 0.0
        )
        base_volume = (
            numeric(ticker.get("baseVolume"))
            or numeric((ticker.get("info") or {}).get("vol24h"))
            or 0.0
        )
        rows.append(
            {
                "pair": pair,
                "market_symbol": symbol,
                "market_id": market.get("id"),
                "active": bool(market.get("active", True)),
                "quote_volume_24h": quote_volume,
                "base_volume_24h": base_volume,
                "local_1h_exists": pair in local_pairs,
                "already_in_core_six": pair in DEFAULT_EXISTING,
            }
        )
    rows.sort(key=lambda row: (row["active"], row["quote_volume_24h"]), reverse=True)
    ranked = []
    for rank, row in enumerate(rows, start=1):
        row = dict(row)
        row["rank_by_quote_volume"] = rank
        ranked.append(row)

    candidates = [row for row in ranked if row["active"] and not row["local_1h_exists"]][: args.top]
    result = {
        "date": DATE,
        "generated_at": datetime.now(UTC).isoformat(),
        "exchange": "okx",
        "market_type": "USDT swap",
        "local_data_dir": args.data_dir,
        "local_pairs": sorted(local_pairs),
        "active_usdt_swap_markets": sum(1 for row in ranked if row["active"]),
        "ranked_markets": ranked,
        "top_missing_candidates": candidates,
        "recommendation": {
            "next_step": "download_1h_futures_for_top_missing_candidates",
            "candidate_count": len(candidates),
            "suggested_initial_batch": [row["pair"] for row in candidates[:12]],
            "rule": (
                "Start with the highest quote-volume missing USDT swaps, then rebuild "
                "the supervised dataset and repeat sealed validation."
            ),
        },
    }

    output = PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(output.with_suffix(".md"), result)
    print(json.dumps(result["recommendation"], ensure_ascii=False, indent=2))
    return 0


def discover_local_pairs(data_dir: Path) -> set[str]:
    pairs = set()
    if not data_dir.exists():
        return pairs
    for path in data_dir.glob("*_USDT-1h-futures.feather"):
        stem = path.name.removesuffix("-1h-futures.feather")
        if stem.endswith("_USDT"):
            stem = stem[: -len("_USDT")]
        parts = stem.split("_")
        if len(parts) >= 2:
            pairs.add(f"{parts[0]}/{parts[1]}")
    return pairs


def is_usdt_swap(market: dict) -> bool:
    return bool(
        market.get("swap")
        and market.get("linear", True)
        and market.get("quote") == "USDT"
        and market.get("settle") == "USDT"
    )


def normalized_pair(market: dict) -> str:
    return f"{market.get('base')}/{market.get('quote')}"


def numeric(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def write_markdown(path: Path, result: dict) -> None:
    rec = result["recommendation"]
    lines = [
        "# OKX USDT 永续交易对扩展发现",
        "",
        f"日期：{result['date']}",
        "",
        "## 概览",
        "",
        f"- 活跃 USDT 永续市场数：{result['active_usdt_swap_markets']}",
        f"- 本地已有 1h futures 交易对：{', '.join(result['local_pairs'])}",
        f"- 建议下一步：`{rec['next_step']}`",
        "",
        "## 建议首批下载",
        "",
        "| 优先级 | 交易对 | OKX 市场 | 24h Quote Volume |",
        "| ---: | --- | --- | ---: |",
    ]
    for index, pair in enumerate(rec["suggested_initial_batch"], start=1):
        row = next(item for item in result["top_missing_candidates"] if item["pair"] == pair)
        lines.append(
            f"| {index} | {pair} | `{row['market_symbol']}` | {row['quote_volume_24h']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Top 缺失候选",
            "",
            "| 市场排名 | 交易对 | OKX 市场 | 24h Quote Volume |",
            "| ---: | --- | --- | ---: |",
        ]
    )
    for row in result["top_missing_candidates"][:30]:
        lines.append(
            f"| {row['rank_by_quote_volume']} | {row['pair']} | `{row['market_symbol']}` | "
            f"{row['quote_volume_24h']:.2f} |"
        )
    lines.extend(["", "## 规则", "", f"- {rec['rule']}", "- 本报告只做市场发现，不调整 dry-run。"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
