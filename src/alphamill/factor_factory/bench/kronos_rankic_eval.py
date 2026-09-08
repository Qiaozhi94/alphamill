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


def latest_eval_end(pred_len: int) -> pd.Timestamp:
    sql = f"SELECT MAX(time) - INTERVAL '{int(pred_len)} minutes' AS eval_end FROM ohlcv_1m"
    df = psql_copy(sql)
    return pd.to_datetime(df["eval_end"].iloc[0], utc=True).tz_convert(None)


def make_eval_times(eval_end: pd.Timestamp, count: int, step_minutes: int) -> list[pd.Timestamp]:
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate Kronos cross-sectional RankIC on local OHLCV data."
    )
    parser.add_argument("--exchange", default="okx")
    parser.add_argument("--symbols", default=None)
    parser.add_argument("--lookback", type=int, default=256)
    parser.add_argument("--pred-len", type=int, default=20)
    parser.add_argument("--eval-count", type=int, default=12)
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
    model_id = args.model or str(PROJECT_ROOT / "models" / "Kronos-base")
    tokenizer_id = args.tokenizer or str(PROJECT_ROOT / "models" / "Kronos-Tokenizer-base")
    device_request = args.device or os.getenv("KRONOS_DEVICE", "cuda")
    device = "cuda:0" if device_request.startswith("cuda") and torch.cuda.is_available() else "cpu"

    eval_end = (
        pd.to_datetime(args.eval_end, utc=True).tz_convert(None)
        if args.eval_end
        else latest_eval_end(args.pred_len)
    )
    eval_times = make_eval_times(eval_end, args.eval_count, args.step_minutes)
    start = eval_times[0] - pd.Timedelta(minutes=args.lookback + 5)
    end = eval_times[-1] + pd.Timedelta(minutes=args.pred_len + 5)

    frames = {
        symbol: load_symbol_frame(args.exchange, symbol, start=start, end=end) for symbol in symbols
    }

    load_started = time.perf_counter()
    tokenizer = KronosTokenizer.from_pretrained(tokenizer_id)
    model = Kronos.from_pretrained(model_id)
    predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)
    load_seconds = time.perf_counter() - load_started

    eval_results = []
    all_rows = []
    inference_seconds = 0.0

    for eval_time in eval_times:
        df_list = []
        x_ts_list = []
        y_ts_list = []
        active_symbols = []
        current_close = {}
        realized_return = {}

        for symbol, frame in frames.items():
            history = frame.loc[:eval_time].tail(args.lookback)
            future_time = eval_time + pd.Timedelta(minutes=args.pred_len)
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
                        periods=args.pred_len,
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
            pred_len=args.pred_len,
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
                "eval_time": eval_time.isoformat(),
                "symbol": symbol,
                "predicted_return": predicted_return,
                "realized_return": realized_return[symbol],
            }
            rows.append(row)
            all_rows.append(row)

        ic = spearman_ic(rows)
        eval_results.append(
            {
                "eval_time": eval_time.isoformat(),
                "symbols": len(rows),
                "rank_ic": ic,
            }
        )

    valid_ics = [row["rank_ic"] for row in eval_results if row["rank_ic"] is not None]
    summary = {
        "status": "ok",
        "exchange": args.exchange,
        "symbols": symbols,
        "model": model_id,
        "tokenizer": tokenizer_id,
        "device": device,
        "lookback": args.lookback,
        "pred_len": args.pred_len,
        "eval_count_requested": args.eval_count,
        "eval_count_completed": len(eval_results),
        "mean_rank_ic": float(pd.Series(valid_ics).mean()) if valid_ics else None,
        "median_rank_ic": float(pd.Series(valid_ics).median()) if valid_ics else None,
        "positive_ic_ratio": float((pd.Series(valid_ics) > 0).mean()) if valid_ics else None,
        "load_seconds": round(load_seconds, 3),
        "inference_seconds": round(inference_seconds, 3),
        "results": eval_results,
    }

    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = pd.Timestamp.now(tz="Asia/Hong_Kong").strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"kronos-rankic-{stamp}.json"
    csv_path = output_dir / f"kronos-rankic-details-{stamp}.csv"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(all_rows).to_csv(csv_path, index=False)

    print(json.dumps({**summary, "json_path": str(json_path), "csv_path": str(csv_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
