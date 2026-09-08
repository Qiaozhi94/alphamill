import argparse
import json
import os
import subprocess
import sys
import time
from io import StringIO
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
KRONOS_ROOT = PROJECT_ROOT / "external" / "Kronos"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def psql_copy(sql: str) -> pd.DataFrame:
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "timescaledb",
            "psql",
            "-U",
            os.getenv("DB_USER", "quant"),
            "-d",
            os.getenv("DB_NAME", "quant"),
            "-c",
            f"COPY ({sql}) TO STDOUT WITH CSV HEADER",
        ],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return pd.read_csv(StringIO(result.stdout))


def load_symbol_frame(
    exchange: str, symbol: str, start: pd.Timestamp, end: pd.Timestamp
) -> pd.DataFrame:
    safe_exchange = exchange.replace("'", "''")
    safe_symbol = symbol.replace("'", "''")
    sql = f"""
SELECT time, open, high, low, close, volume
FROM ohlcv_1m
WHERE exchange = '{safe_exchange}'
  AND symbol = '{safe_symbol}'
  AND time >= '{start.isoformat()}'
  AND time <= '{end.isoformat()}'
ORDER BY time
"""
    df = psql_copy(sql)
    if df.empty:
        raise RuntimeError(f"No rows for {exchange} {symbol}")
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_convert(None)
    df = df.set_index("time")
    return df[["open", "high", "low", "close", "volume"]].astype(float)


def common_eval_end(max_horizon: int) -> pd.Timestamp:
    sql = f"""
SELECT MAX(time) - INTERVAL '{int(max_horizon)} minutes' AS eval_end
FROM ohlcv_1m
"""
    df = psql_copy(sql)
    return pd.to_datetime(df["eval_end"].iloc[0], utc=True).tz_convert(None)


def eval_times(eval_end: pd.Timestamp, days: int, step_minutes: int) -> list[pd.Timestamp]:
    count = int(days * 24 * 60 / step_minutes)
    times = [eval_end - pd.Timedelta(minutes=step_minutes * idx) for idx in range(count)]
    return list(reversed(times))


def spearman_ic(rows: list[dict]) -> float | None:
    df = pd.DataFrame(rows)
    if len(df) < 3:
        return None
    value = df["predicted_return"].corr(df["realized_return"], method="spearman")
    if pd.isna(value):
        return None
    return float(value)


def summarize_ics(ics: list[float]) -> dict:
    series = pd.Series(ics, dtype=float)
    if series.empty:
        return {
            "eval_count": 0,
            "mean_rank_ic": None,
            "median_rank_ic": None,
            "positive_ic_ratio": None,
            "ic_ir": None,
        }
    std = float(series.std(ddof=1)) if len(series) > 1 else 0.0
    return {
        "eval_count": int(len(series)),
        "mean_rank_ic": float(series.mean()),
        "median_rank_ic": float(series.median()),
        "positive_ic_ratio": float((series > 0).mean()),
        "ic_ir": float(series.mean() / std) if std else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate Kronos IC decay across multiple forward horizons."
    )
    parser.add_argument("--exchange", default="okx")
    parser.add_argument("--symbols", default=None)
    parser.add_argument("--lookback", type=int, default=256)
    parser.add_argument("--horizons", default="5,10,20,30,60")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--step-minutes", type=int, default=60)
    parser.add_argument("--eval-end", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--tokenizer", default=None)
    parser.add_argument("--device", default=None)
    parser.add_argument("--output-dir", default="reports")
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env")
    sys.path.insert(0, str(KRONOS_ROOT))

    import torch
    from model import Kronos, KronosPredictor, KronosTokenizer

    symbols = (
        [item.strip() for item in args.symbols.split(",")]
        if args.symbols
        else csv_env("SYMBOLS", "BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT,XRP/USDT,DOGE/USDT")
    )
    horizons = [int(item.strip()) for item in args.horizons.split(",") if item.strip()]
    max_horizon = max(horizons)
    model_id = args.model or str(PROJECT_ROOT / "models" / "Kronos-base")
    tokenizer_id = args.tokenizer or str(PROJECT_ROOT / "models" / "Kronos-Tokenizer-base")
    device_request = args.device or os.getenv("KRONOS_DEVICE", "cuda")
    device = "cuda:0" if device_request.startswith("cuda") and torch.cuda.is_available() else "cpu"

    end_time = (
        pd.to_datetime(args.eval_end, utc=True).tz_convert(None)
        if args.eval_end
        else common_eval_end(max_horizon)
    )
    times = eval_times(end_time, args.days, args.step_minutes)
    start = times[0] - pd.Timedelta(minutes=args.lookback + 5)
    end = times[-1] + pd.Timedelta(minutes=max_horizon + 5)

    frames = {
        symbol: load_symbol_frame(args.exchange, symbol, start=start, end=end) for symbol in symbols
    }

    load_started = time.perf_counter()
    tokenizer = KronosTokenizer.from_pretrained(tokenizer_id)
    model = Kronos.from_pretrained(model_id)
    predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)
    load_seconds = time.perf_counter() - load_started

    horizon_results: dict[int, list[dict]] = {horizon: [] for horizon in horizons}
    detail_rows = []
    inference_seconds = 0.0

    for horizon in horizons:
        for eval_time in times:
            df_list = []
            x_ts_list = []
            y_ts_list = []
            active_symbols = []
            current_close = {}
            realized_return = {}

            for symbol, frame in frames.items():
                history = frame.loc[:eval_time].tail(args.lookback)
                future_time = eval_time + pd.Timedelta(minutes=horizon)
                if len(history) < args.lookback or future_time not in frame.index:
                    continue

                current = float(history["close"].iloc[-1])
                future = float(frame.loc[future_time, "close"])
                current_close[symbol] = current
                realized_return[symbol] = (future / current) - 1 if current else 0.0
                df_list.append(history.reset_index()[["open", "high", "low", "close", "volume"]])
                x_ts_list.append(pd.Series(history.index))
                y_ts_list.append(
                    pd.Series(
                        pd.date_range(
                            start=eval_time + pd.Timedelta(minutes=1),
                            periods=horizon,
                            freq="1min",
                        )
                    )
                )
                active_symbols.append(symbol)

            if len(active_symbols) < 3:
                continue

            infer_started = time.perf_counter()
            pred_frames = predictor.predict_batch(
                df_list=df_list,
                x_timestamp_list=x_ts_list,
                y_timestamp_list=y_ts_list,
                pred_len=horizon,
                T=1.0,
                top_p=0.9,
                sample_count=1,
                verbose=False,
            )
            inference_seconds += time.perf_counter() - infer_started

            rows = []
            for symbol, pred_df in zip(active_symbols, pred_frames):
                predicted_close = float(pred_df["close"].iloc[-1])
                predicted_return = (
                    (predicted_close / current_close[symbol]) - 1 if current_close[symbol] else 0.0
                )
                row = {
                    "horizon": horizon,
                    "eval_time": eval_time.isoformat(),
                    "symbol": symbol,
                    "predicted_return": predicted_return,
                    "realized_return": realized_return[symbol],
                }
                rows.append(row)
                detail_rows.append(row)

            ic = spearman_ic(rows)
            horizon_results[horizon].append(
                {
                    "eval_time": eval_time.isoformat(),
                    "symbols": len(rows),
                    "rank_ic": ic,
                }
            )

    decay = []
    for horizon in horizons:
        ics = [row["rank_ic"] for row in horizon_results[horizon] if row["rank_ic"] is not None]
        decay.append({"horizon": horizon, **summarize_ics(ics)})

    summary = {
        "status": "ok",
        "exchange": args.exchange,
        "symbols": symbols,
        "model": model_id,
        "tokenizer": tokenizer_id,
        "device": device,
        "lookback": args.lookback,
        "days": args.days,
        "step_minutes": args.step_minutes,
        "eval_end": end_time.isoformat(),
        "horizons": horizons,
        "load_seconds": round(load_seconds, 3),
        "inference_seconds": round(inference_seconds, 3),
        "decay": decay,
        "results": horizon_results,
    }

    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = pd.Timestamp.now(tz="Asia/Hong_Kong").strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"kronos-ic-decay-{stamp}.json"
    csv_path = output_dir / f"kronos-ic-decay-details-{stamp}.csv"
    md_path = output_dir / f"kronos-ic-decay-{stamp}.md"

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(detail_rows).to_csv(csv_path, index=False)
    write_markdown(md_path, summary)

    print(
        json.dumps(
            {
                **{key: value for key, value in summary.items() if key not in {"results"}},
                "json_path": str(json_path),
                "csv_path": str(csv_path),
                "md_path": str(md_path),
            },
            indent=2,
        )
    )
    return 0


def write_markdown(path: Path, summary: dict) -> None:
    lines = [
        "# Kronos IC Decay Report",
        "",
        f"- Exchange: {summary['exchange']}",
        f"- Symbols: {', '.join(summary['symbols'])}",
        f"- Model: {summary['model']}",
        f"- Device: {summary['device']}",
        f"- Lookback: {summary['lookback']}",
        f"- Evaluation days: {summary['days']}",
        f"- Step minutes: {summary['step_minutes']}",
        f"- Inference seconds: {summary['inference_seconds']}",
        "",
        "| Horizon | Eval Count | Mean RankIC | Median RankIC | Positive IC Ratio | IC IR |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["decay"]:
        lines.append(
            "| {horizon} | {eval_count} | {mean} | {median} | {positive} | {ic_ir} |".format(
                horizon=row["horizon"],
                eval_count=row["eval_count"],
                mean=format_optional(row["mean_rank_ic"]),
                median=format_optional(row["median_rank_ic"]),
                positive=format_optional(row["positive_ic_ratio"]),
                ic_ir=format_optional(row["ic_ir"]),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_optional(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


if __name__ == "__main__":
    raise SystemExit(main())
