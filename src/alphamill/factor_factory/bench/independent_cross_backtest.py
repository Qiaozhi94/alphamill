from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


@dataclass
class Position:
    pair: str
    side: str
    open_time: pd.Timestamp
    open_rate: float
    amount: float


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independent candle-by-candle replay for KronosFusionStrategy signal logic."
    )
    parser.add_argument("--data-dir", default="freqtrade/user_data/data/okx")
    parser.add_argument("--config", default="freqtrade/user_data/config.json")
    parser.add_argument("--timerange", required=True, help="Format YYYYMMDD-YYYYMMDD")
    parser.add_argument("--output", required=True)
    parser.add_argument("--can-short", action="store_true")
    parser.add_argument(
        "--kronos-mode", choices=["neutral", "fixed-buy", "fixed-sell"], default="neutral"
    )
    parser.add_argument("--fee-rate", type=float, default=0.001)
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    start, end = parse_timerange(args.timerange)
    pairs = config["exchange"]["pair_whitelist"]
    stake_amount = float(config.get("stake_amount", 100))
    starting_balance = float(config.get("dry_run_wallet", 10000))
    max_open_trades = int(config.get("max_open_trades", 3))

    frames = load_frames(Path(args.data_dir), pairs, start, end)
    analyzed = {
        pair: add_signals(frame, kronos_mode=args.kronos_mode) for pair, frame in frames.items()
    }

    indexed = {pair: frame.set_index("date", drop=False) for pair, frame in analyzed.items()}
    all_dates = sorted(set().union(*(set(frame.index) for frame in indexed.values())))
    open_positions: list[Position] = []
    trades: list[dict] = []
    balance = starting_balance

    for current_time in all_dates:
        rows = {
            pair: frame.loc[current_time]
            for pair, frame in indexed.items()
            if current_time in frame.index
        }

        still_open: list[Position] = []
        for position in open_positions:
            row = rows.get(position.pair)
            if row is None:
                still_open.append(position)
                continue

            exit_reason = should_exit(position, row, current_time)
            if exit_reason:
                profit_abs, profit_ratio = close_profit(
                    position, float(row["close"]), args.fee_rate
                )
                balance += profit_abs
                trades.append(
                    {
                        "pair": position.pair,
                        "side": position.side,
                        "open_date": iso(position.open_time),
                        "close_date": iso(current_time),
                        "open_rate": position.open_rate,
                        "close_rate": float(row["close"]),
                        "profit_abs": profit_abs,
                        "profit_ratio": profit_ratio,
                        "exit_reason": exit_reason,
                    }
                )
            else:
                still_open.append(position)
        open_positions = still_open

        if len(open_positions) >= max_open_trades:
            continue

        open_pairs = {position.pair for position in open_positions}
        for pair in pairs:
            if len(open_positions) >= max_open_trades or pair in open_pairs:
                continue
            row = rows.get(pair)
            if row is None or not bool(row.get("startup_ready", False)):
                continue

            side = None
            if row.get("enter_long", 0) == 1:
                side = "long"
            elif args.can_short and row.get("enter_short", 0) == 1:
                side = "short"
            if side is None:
                continue

            rate = float(row["close"])
            amount = stake_amount / rate
            open_positions.append(
                Position(
                    pair=pair, side=side, open_time=current_time, open_rate=rate, amount=amount
                )
            )
            open_pairs.add(pair)

    if all_dates:
        final_time = all_dates[-1]
        for position in open_positions:
            frame = indexed[position.pair]
            row = frame.loc[frame["date"] <= final_time].iloc[-1]
            profit_abs, profit_ratio = close_profit(position, float(row["close"]), args.fee_rate)
            balance += profit_abs
            trades.append(
                {
                    "pair": position.pair,
                    "side": position.side,
                    "open_date": iso(position.open_time),
                    "close_date": iso(final_time),
                    "open_rate": position.open_rate,
                    "close_rate": float(row["close"]),
                    "profit_abs": profit_abs,
                    "profit_ratio": profit_ratio,
                    "exit_reason": "force_exit_end",
                }
            )

    summary = summarize(trades, starting_balance, balance, start, end, args)
    payload = {
        "summary": summary,
        "trades": trades,
        "lookahead_check": {
            "uses_future_columns": False,
            "rolling_windows_are_backward_looking": True,
            "freqtrade_kronos_backtest_warning": (
                "KronosFusionStrategy currently fetches one live Kronos signal per pair in populate_indicators; "
                "historical backtests therefore reuse the run-time signal across all historical candles unless "
                "precomputed timestamped Kronos signals are supplied."
            ),
            "independent_replay_kronos_mode": args.kronos_mode,
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {output}")
    return 0


def parse_timerange(value: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    start_text, end_text = value.split("-", 1)
    start = pd.Timestamp(datetime.strptime(start_text, "%Y%m%d"), tz="UTC")
    end = pd.Timestamp(datetime.strptime(end_text, "%Y%m%d"), tz="UTC")
    return start, end


def load_frames(
    data_dir: Path, pairs: list[str], start: pd.Timestamp, end: pd.Timestamp
) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for pair in pairs:
        name = pair.replace("/", "_").replace(":", "_")
        path = data_dir / f"{name}-5m.feather"
        if not path.exists():
            futures_path = data_dir / f"{name}-5m-futures.feather"
            path = (
                futures_path
                if futures_path.exists()
                else data_dir / "futures" / f"{name}-5m-futures.feather"
            )
        frame = pd.read_feather(path)
        if "date" not in frame:
            frame = frame.rename(columns={"time": "date"})
        frame["date"] = pd.to_datetime(frame["date"], utc=True)
        frame = frame[(frame["date"] >= start) & (frame["date"] < end)].copy()
        frame = frame.sort_values("date").reset_index(drop=True)
        frames[pair] = frame
    return frames


def add_signals(frame: pd.DataFrame, kronos_mode: str) -> pd.DataFrame:
    frame = frame.copy()
    frame["ema_fast"] = frame["close"].ewm(span=12, adjust=False).mean()
    frame["ema_slow"] = frame["close"].ewm(span=26, adjust=False).mean()
    frame["volume_mean"] = frame["volume"].rolling(24).mean()
    frame["momentum"] = frame["close"] / frame["close"].shift(12) - 1
    previous_close = frame["close"].shift(1)
    true_range = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - previous_close).abs(),
            (frame["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    frame["atr"] = true_range.rolling(14).mean()
    frame["atr_pct"] = frame["atr"] / frame["close"]
    if kronos_mode == "fixed-buy":
        frame["kronos_signal"] = "buy"
        frame["kronos_confidence"] = 0.6
        frame["kronos_expected_return"] = 0.001
        frame["kronos_direction_prob"] = 0.6
    elif kronos_mode == "fixed-sell":
        frame["kronos_signal"] = "sell"
        frame["kronos_confidence"] = 0.6
        frame["kronos_expected_return"] = -0.001
        frame["kronos_direction_prob"] = 0.4
    else:
        frame["kronos_signal"] = "neutral"
        frame["kronos_confidence"] = 0.0
        frame["kronos_expected_return"] = 0.0
        frame["kronos_direction_prob"] = 0.5

    trend = (frame["ema_fast"] / frame["ema_slow"] - 1).clip(-0.02, 0.02) / 0.02
    momentum = frame["momentum"].clip(-0.03, 0.03) / 0.03
    volume_ok = (frame["volume"] > frame["volume_mean"]).astype(float)
    volume_score = volume_ok.where(volume_ok == 1.0, -0.2)
    frame["ta_score"] = (trend * 0.45 + momentum * 0.40 + volume_score * 0.15).clip(-1.0, 1.0)

    signal_bias = frame["kronos_signal"].map({"buy": 1.0, "sell": -1.0}).fillna(0.0)
    expected = frame["kronos_expected_return"].clip(-0.01, 0.01) / 0.01
    direction = ((frame["kronos_direction_prob"].clip(0.0, 1.0) - 0.5) * 2.0).fillna(0.0)
    frame["kronos_score"] = (
        signal_bias * frame["kronos_confidence"].clip(0.0, 1.0) * 0.45
        + expected * 0.40
        + direction * 0.15
    ).clip(-1.0, 1.0)
    frame["freqai_score"] = 0.0
    frame["fusion_score"] = (frame["ta_score"] * 0.30 + frame["kronos_score"] * 0.45).clip(
        -1.0, 1.0
    )
    frame["fusion_signal"] = "neutral"
    frame.loc[frame["fusion_score"] >= 0.35, "fusion_signal"] = "buy"
    frame.loc[frame["fusion_score"] <= -0.25, "fusion_signal"] = "sell"
    frame["enter_long"] = (
        (frame["ema_fast"] > frame["ema_slow"])
        & (frame["momentum"] > 0)
        & (frame["volume"] > frame["volume_mean"])
        & (frame["volume"] > 0)
        & (frame["fusion_signal"] == "buy")
    ).astype(int)
    frame["enter_short"] = (
        (frame["ema_fast"] < frame["ema_slow"])
        & (frame["momentum"] < 0)
        & (frame["volume"] > frame["volume_mean"])
        & (frame["volume"] > 0)
        & (frame["fusion_signal"] == "sell")
    ).astype(int)
    frame["exit_long"] = (
        (
            (frame["ema_fast"] < frame["ema_slow"])
            | (frame["momentum"] < -0.02)
            | (frame["fusion_signal"] == "sell")
        )
        & (frame["volume"] > 0)
    ).astype(int)
    frame["exit_short"] = (
        (
            (frame["ema_fast"] > frame["ema_slow"])
            | (frame["momentum"] > 0.02)
            | (frame["fusion_signal"] == "buy")
        )
        & (frame["volume"] > 0)
    ).astype(int)
    frame["startup_ready"] = frame.index >= 60
    return frame


def should_exit(position: Position, row: pd.Series, current_time: pd.Timestamp) -> str | None:
    profit = raw_profit_ratio(position, float(row["close"]))
    minutes_open = (current_time - position.open_time).total_seconds() / 60
    if profit <= -0.10:
        return "stop_loss"
    if minutes_open >= 60 and profit >= 0.0:
        return "roi_60"
    if minutes_open >= 30 and profit >= 0.01:
        return "roi_30"
    if profit >= 0.02:
        return "roi_0"
    if position.side == "long" and row.get("exit_long", 0) == 1:
        return "exit_signal"
    if position.side == "short" and row.get("exit_short", 0) == 1:
        return "exit_signal"
    return None


def raw_profit_ratio(position: Position, close_rate: float) -> float:
    if position.side == "short":
        return position.open_rate / close_rate - 1
    return close_rate / position.open_rate - 1


def close_profit(position: Position, close_rate: float, fee_rate: float) -> tuple[float, float]:
    gross = raw_profit_ratio(position, close_rate)
    net = gross - fee_rate * 2
    profit_abs = position.open_rate * position.amount * net
    return profit_abs, net


def summarize(
    trades: list[dict],
    starting_balance: float,
    final_balance: float,
    start: pd.Timestamp,
    end: pd.Timestamp,
    args: argparse.Namespace,
) -> dict:
    profits = [float(trade["profit_abs"]) for trade in trades]
    wins = sum(1 for profit in profits if profit > 0)
    losses = sum(1 for profit in profits if profit < 0)
    draws = len(profits) - wins - losses
    long_count = sum(1 for trade in trades if trade["side"] == "long")
    short_count = sum(1 for trade in trades if trade["side"] == "short")
    total_profit = final_balance - starting_balance
    days = max(1.0, (end - start).total_seconds() / 86400)
    returns = [float(trade["profit_ratio"]) for trade in trades]
    sharpe = 0.0
    if len(returns) > 1:
        mean = sum(returns) / len(returns)
        variance = sum((item - mean) ** 2 for item in returns) / (len(returns) - 1)
        std = math.sqrt(variance)
        if std > 0:
            sharpe = mean / std * math.sqrt(len(returns))
    equity = starting_balance
    peak = starting_balance
    max_drawdown = 0.0
    for profit in profits:
        equity += profit
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return {
        "engine": "independent_event_replay",
        "timerange": args.timerange,
        "can_short": args.can_short,
        "kronos_mode": args.kronos_mode,
        "fee_rate": args.fee_rate,
        "total_trades": len(trades),
        "trade_count_long": long_count,
        "trade_count_short": short_count,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "winrate": wins / len(trades) if trades else 0.0,
        "starting_balance": starting_balance,
        "final_balance": final_balance,
        "profit_total_abs": total_profit,
        "profit_total": total_profit / starting_balance,
        "trades_per_day": len(trades) / days,
        "sharpe_trade_level": sharpe,
        "max_drawdown_abs": max_drawdown,
        "max_drawdown_ratio": max_drawdown / starting_balance,
    }


def iso(value: pd.Timestamp) -> str:
    return value.to_pydatetime().astimezone(UTC).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
