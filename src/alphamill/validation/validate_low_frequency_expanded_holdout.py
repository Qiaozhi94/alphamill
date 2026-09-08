from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

try:  # Package import for AlphaMill; fallback preserves direct script execution.
    from ..factor_factory.bench.train_low_frequency_walk_forward_baselines import (
        ROUND_TRIP_FEE,
        fit_predict,
        infer_feature_columns,
        optional_corr,
    )
except ImportError:  # pragma: no cover - direct legacy script compatibility.
    from alphamill.factor_factory.bench.train_low_frequency_walk_forward_baselines import (
        ROUND_TRIP_FEE,
        fit_predict,
        infer_feature_columns,
        optional_corr,
    )

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TARGETS = [("1h", 12), ("1h", 24), ("4h", 6), ("4h", 12)]
MODEL = "ridge"
STAKE = 100.0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate expanded low-frequency Ridge candidates on a final holdout."
    )
    parser.add_argument(
        "--dataset",
        default="reports/low-frequency-expanded-12pair-supervised-dataset-20260628.parquet",
    )
    parser.add_argument(
        "--output", default="reports/low-frequency-expanded-12pair-holdout-ridge-20260628.json"
    )
    parser.add_argument("--holdout-days", type=int, default=90)
    parser.add_argument("--train-days", default="120,180,240")
    parser.add_argument("--test-days", default="30,45,60")
    parser.add_argument("--quantiles", default="0.95,0.98,0.99")
    args = parser.parse_args()

    train_days_values = parse_ints(args.train_days)
    test_days_values = parse_ints(args.test_days)
    quantiles = parse_floats(args.quantiles)

    dataset = pd.read_parquet(PROJECT_ROOT / args.dataset)
    dataset["date"] = pd.to_datetime(dataset["date"], utc=True)

    selection_rows = []
    holdout_rows = []
    all_trade_rows = []
    holdout_bounds = {}
    for timeframe, horizon in TARGETS:
        target_column = f"target_return_{horizon}"
        frame = dataset[dataset["timeframe"] == timeframe].copy()
        frame = frame.dropna(subset=[target_column]).sort_values("date").reset_index(drop=True)
        if frame.empty:
            continue
        feature_columns = infer_feature_columns(frame, horizon)
        end = frame["date"].max()
        holdout_start = end - pd.Timedelta(days=args.holdout_days)
        holdout_bounds[timeframe] = {"start": str(holdout_start), "end": str(end)}

        for train_days in train_days_values:
            for test_days in test_days_values:
                selection_predictions = run_walk_forward(
                    frame=frame,
                    feature_columns=feature_columns,
                    target_column=target_column,
                    train_days=train_days,
                    test_days=test_days,
                    start=frame["date"].min() + pd.Timedelta(days=train_days),
                    end=holdout_start,
                )
                holdout_predictions = run_walk_forward(
                    frame=frame,
                    feature_columns=feature_columns,
                    target_column=target_column,
                    train_days=train_days,
                    test_days=test_days,
                    start=holdout_start,
                    end=end,
                )
                for side in ("long", "short"):
                    for quantile in quantiles:
                        selection_trades = simulate_predictions(
                            predictions=selection_predictions,
                            timeframe=timeframe,
                            horizon=horizon,
                            target_column=target_column,
                            side=side,
                            quantile=quantile,
                        )
                        holdout_trades = simulate_predictions(
                            predictions=holdout_predictions,
                            timeframe=timeframe,
                            horizon=horizon,
                            target_column=target_column,
                            side=side,
                            quantile=quantile,
                        )
                        key = {
                            "model": MODEL,
                            "timeframe": timeframe,
                            "horizon": horizon,
                            "side": side,
                            "quantile": quantile,
                            "train_days": train_days,
                            "test_days": test_days,
                            "candidate": candidate_label(timeframe, horizon, side, quantile),
                        }
                        selection_rows.append(
                            {"stage": "selection", **key, **summarize_trades(selection_trades)}
                        )
                        holdout_rows.append(
                            {"stage": "holdout", **key, **summarize_trades(holdout_trades)}
                        )
                        all_trade_rows.extend(tag_trades(selection_trades, "selection", key))
                        all_trade_rows.extend(tag_trades(holdout_trades, "holdout", key))

    selection = pd.DataFrame(selection_rows)
    holdout = pd.DataFrame(holdout_rows)
    chosen = choose_config(selection)
    chosen_holdout = lookup(holdout, chosen)
    best_holdout = best_pass_or_best(holdout)
    result = {
        "dataset": args.dataset,
        "date": "2026-06-28",
        "model": MODEL,
        "stake": STAKE,
        "round_trip_fee": ROUND_TRIP_FEE,
        "holdout_days": args.holdout_days,
        "holdout_bounds": holdout_bounds,
        "candidate_family": {
            "targets": [
                {"timeframe": timeframe, "horizon": horizon} for timeframe, horizon in TARGETS
            ],
            "sides": ["long", "short"],
            "train_days": train_days_values,
            "test_days": test_days_values,
            "quantiles": quantiles,
        },
        "selection_rows": sorted_records(selection),
        "holdout_rows": sorted_records(holdout),
        "summary": {
            "chosen_from_selection": chosen,
            "chosen_holdout": chosen_holdout,
            "best_holdout_diagnostic": best_holdout,
            "decision": final_decision(chosen_holdout),
        },
    }

    output = PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.concat([selection, holdout], ignore_index=True).to_csv(
        output.with_suffix(".csv"), index=False
    )
    pd.DataFrame(all_trade_rows).to_csv(output.with_name(output.stem + "-trades.csv"), index=False)
    write_markdown(output.with_suffix(".md"), result)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return 0


def parse_ints(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_floats(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def run_walk_forward(
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    train_days: int,
    test_days: int,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> list[tuple[pd.DataFrame, pd.DataFrame, dict]]:
    current = start
    windows = []
    while current < end:
        train_start = current - pd.Timedelta(days=train_days)
        test_end = min(current + pd.Timedelta(days=test_days), end)
        train = frame[(frame["date"] >= train_start) & (frame["date"] < current)].copy()
        test = frame[(frame["date"] >= current) & (frame["date"] < test_end)].copy()
        if len(train) >= 1000 and len(test) > 0:
            train_pred, test_pred = fit_predict(
                model_name=MODEL,
                train=train,
                test=test,
                feature_columns=feature_columns,
                target_column=target_column,
            )
            train_eval = train[["date", "pair", target_column]].copy()
            test_eval = test[["date", "pair", target_column]].copy()
            train_eval["prediction"] = train_pred
            test_eval["prediction"] = test_pred
            windows.append(
                (
                    train_eval,
                    test_eval,
                    {
                        "train_start": str(train_start),
                        "train_end": str(current),
                        "test_end": str(test_end),
                    },
                )
            )
        current = test_end
    return windows


def simulate_predictions(
    predictions: list[tuple[pd.DataFrame, pd.DataFrame, dict]],
    timeframe: str,
    horizon: int,
    target_column: str,
    side: str,
    quantile: float,
) -> pd.DataFrame:
    trades = []
    hold = pd.Timedelta(hours=horizon if timeframe == "1h" else horizon * 4)
    for window_index, (train_eval, test_eval, meta) in enumerate(predictions, start=1):
        if side == "long":
            threshold = float(train_eval["prediction"].quantile(quantile))
            signals = test_eval[test_eval["prediction"] >= threshold].copy()
        else:
            threshold = float(train_eval["prediction"].quantile(1 - quantile))
            signals = test_eval[test_eval["prediction"] <= threshold].copy()
        next_available_by_pair: dict[str, pd.Timestamp] = {}
        for row in signals.sort_values("date").itertuples(index=False):
            next_available = next_available_by_pair.get(
                row.pair, pd.Timestamp.min.tz_localize("UTC")
            )
            if row.date < next_available:
                continue
            gross_return = float(getattr(row, target_column))
            if side == "short":
                gross_return = -gross_return
            net_return = gross_return - ROUND_TRIP_FEE
            trades.append(
                {
                    "window": window_index,
                    "pair": row.pair,
                    "entry_time": row.date,
                    "exit_time": row.date + hold,
                    "prediction": float(row.prediction),
                    "gross_return": gross_return,
                    "net_return": net_return,
                    "pnl": net_return * STAKE,
                    "train_start": meta["train_start"],
                    "train_end": meta["train_end"],
                    "test_end": meta["test_end"],
                }
            )
            next_available_by_pair[row.pair] = row.date + hold
    return pd.DataFrame(trades)


def summarize_trades(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return empty_summary()
    frame = trades.copy()
    frame["entry_time"] = pd.to_datetime(frame["entry_time"], utc=True)
    frame["month"] = frame["entry_time"].dt.strftime("%Y-%m")
    cumulative = frame["pnl"].cumsum()
    drawdown = cumulative.cummax().clip(lower=0.0) - cumulative
    month_pnl = frame.groupby("month")["pnl"].sum()
    window_pnl = frame.groupby("window")["pnl"].sum()
    net_mean = float(frame["net_return"].mean())
    positive_month_ratio = float((month_pnl > 0).mean())
    positive_window_ratio = float((window_pnl > 0).mean())
    return {
        "trades": int(len(frame)),
        "pairs": int(frame["pair"].nunique()),
        "gross_mean": float(frame["gross_return"].mean()),
        "net_mean": net_mean,
        "winrate": float((frame["net_return"] > 0).mean()),
        "total_pnl": float(frame["pnl"].sum()),
        "max_drawdown": float(drawdown.max()),
        "positive_month_ratio": positive_month_ratio,
        "positive_window_ratio": positive_window_ratio,
        "ic": optional_corr(frame["prediction"], frame["gross_return"]) if len(frame) > 2 else None,
        "decision": "PASS"
        if len(frame) >= 30
        and net_mean > 0
        and positive_month_ratio >= 0.5
        and positive_window_ratio >= 0.5
        else "FAIL",
    }


def empty_summary() -> dict:
    return {
        "trades": 0,
        "pairs": 0,
        "gross_mean": None,
        "net_mean": None,
        "winrate": None,
        "total_pnl": 0.0,
        "max_drawdown": 0.0,
        "positive_month_ratio": None,
        "positive_window_ratio": None,
        "ic": None,
        "decision": "FAIL",
    }


def choose_config(selection: pd.DataFrame) -> dict | None:
    candidates = selection[(selection["trades"] >= 30) & (selection["decision"] == "PASS")].copy()
    if candidates.empty:
        candidates = selection[selection["trades"] >= 30].copy()
    if candidates.empty:
        return None
    candidates["risk_score"] = candidates["total_pnl"] / candidates["max_drawdown"].replace(
        0, np.nan
    )
    candidates["risk_score"] = candidates["risk_score"].fillna(candidates["total_pnl"])
    row = candidates.sort_values(
        [
            "decision",
            "positive_window_ratio",
            "positive_month_ratio",
            "risk_score",
            "total_pnl",
            "trades",
        ],
        ascending=[True, False, False, False, False, False],
    ).iloc[0]
    return key_from_row(row)


def key_from_row(row: pd.Series | dict) -> dict:
    return {
        "model": row["model"],
        "timeframe": row["timeframe"],
        "horizon": int(row["horizon"]),
        "side": row["side"],
        "quantile": float(row["quantile"]),
        "train_days": int(row["train_days"]),
        "test_days": int(row["test_days"]),
        "candidate": row["candidate"],
    }


def lookup(rows: pd.DataFrame, key: dict | None) -> dict | None:
    if key is None or rows.empty:
        return None
    matched = rows[
        (rows["timeframe"] == key["timeframe"])
        & (rows["horizon"] == key["horizon"])
        & (rows["side"] == key["side"])
        & (np.isclose(rows["quantile"], key["quantile"]))
        & (rows["train_days"] == key["train_days"])
        & (rows["test_days"] == key["test_days"])
    ]
    if matched.empty:
        return None
    return normalize_dict(matched.iloc[0].to_dict())


def best_pass_or_best(rows: pd.DataFrame) -> dict | None:
    if rows.empty:
        return None
    pool = rows[rows["decision"] == "PASS"].copy()
    if pool.empty:
        pool = rows.copy()
    row = pool.sort_values(
        ["decision", "total_pnl", "trades"], ascending=[True, False, False]
    ).iloc[0]
    return normalize_dict(row.to_dict())


def final_decision(chosen_holdout: dict | None) -> str:
    if chosen_holdout and chosen_holdout.get("decision") == "PASS":
        return "selected_candidate_passed_holdout_next_freqtrade_backtest"
    if chosen_holdout:
        return "selected_candidate_failed_holdout_do_not_package"
    return "no_selectable_candidate_do_not_package"


def tag_trades(trades: pd.DataFrame, stage: str, key: dict) -> list[dict]:
    if trades.empty:
        return []
    rows = []
    for trade in trades.to_dict(orient="records"):
        rows.append(
            {
                "stage": stage,
                **key,
                **normalize_dict(trade),
            }
        )
    return rows


def sorted_records(rows: pd.DataFrame) -> list[dict]:
    if rows.empty:
        return []
    sorted_rows = rows.sort_values(
        ["stage", "decision", "total_pnl", "trades"], ascending=[True, True, False, False]
    )
    return [normalize_dict(row) for row in sorted_rows.to_dict(orient="records")]


def candidate_label(timeframe: str, horizon: int, side: str, quantile: float) -> str:
    top = int(round((1 - quantile) * 100))
    return f"{MODEL}_{timeframe}_h{horizon}_{side}_top{top}"


def normalize_dict(row: dict | None) -> dict | None:
    if row is None:
        return None
    normalized = {}
    for key, value in row.items():
        if pd.isna(value):
            normalized[key] = None
        elif isinstance(value, pd.Timestamp):
            normalized[key] = str(value)
        elif isinstance(value, np.generic):
            normalized[key] = value.item()
        else:
            normalized[key] = value
    return normalized


def write_markdown(path: Path, result: dict) -> None:
    summary = result["summary"]
    chosen = summary["chosen_from_selection"]
    chosen_holdout = summary["chosen_holdout"]
    diagnostic = summary["best_holdout_diagnostic"]
    lines = [
        "# 扩展 12 交易对低频 Ridge 最终留出验证",
        "",
        "日期：2026-06-28",
        "",
        "## 方法",
        "",
        f"- 数据集：`{result['dataset']}`",
        f"- 候选族：Ridge，{len(result['candidate_family']['targets'])} 个 timeframe/horizon 目标，long/short，训练窗口 {result['candidate_family']['train_days']} 天，验证窗口 {result['candidate_family']['test_days']} 天，阈值 {result['candidate_family']['quantiles']}。",
        f"- 留出窗口：最后 {result['holdout_days']} 天；各 timeframe 边界为 `{result['holdout_bounds']}`。",
        f"- 执行假设：单交易对非重叠持仓，stake={result['stake']:.2f} USDT，往返成本 {result['round_trip_fee']:.2%}。",
        "- 选择规则：只看 final holdout 之前的 selection 结果，优先选择 PASS 且窗口/月度稳定性更好的配置。",
        "",
        "## 选择期选中配置",
        "",
    ]
    if chosen:
        lines.extend(
            [
                f"- 候选：`{chosen['candidate']}`",
                f"- timeframe/horizon：{chosen['timeframe']} / {chosen['horizon']}",
                f"- 方向与阈值：{chosen['side']} / {chosen['quantile']}",
                f"- 训练/验证窗口：{chosen['train_days']}d / {chosen['test_days']}d",
            ]
        )
    else:
        lines.append("- 无可选候选。")
    lines.extend(["", "## Final Holdout", ""])
    if chosen_holdout:
        lines.extend(
            [
                f"- 交易：{chosen_holdout['trades']} 笔，覆盖 {chosen_holdout['pairs']} 个交易对。",
                f"- 净收益均值：{fmt_pct(chosen_holdout['net_mean'])}，胜率：{fmt_pct(chosen_holdout['winrate'])}。",
                f"- 总 PnL：{chosen_holdout['total_pnl']:.4f} USDT，最大回撤：{chosen_holdout['max_drawdown']:.4f} USDT。",
                f"- 正收益月份/窗口：{fmt_pct(chosen_holdout['positive_month_ratio'])} / {fmt_pct(chosen_holdout['positive_window_ratio'])}。",
                f"- 判定：`{chosen_holdout['decision']}`。",
            ]
        )
    else:
        lines.append("- 无对应留出结果。")
    lines.extend(["", "## 诊断信息", ""])
    if diagnostic:
        lines.append(
            f"- 留出期事后最佳诊断：`{diagnostic['candidate']}`，{diagnostic['trades']} 笔，"
            f"总 PnL {diagnostic['total_pnl']:.4f} USDT，判定 `{diagnostic['decision']}`。该项只用于诊断，不可作为部署选择。"
        )
    lines.extend(
        [
            "",
            "## 结论",
            "",
            f"- 状态：`{summary['decision']}`。",
        ]
    )
    if summary["decision"] == "selected_candidate_passed_holdout_next_freqtrade_backtest":
        lines.append(
            "- 选择期选中的配置通过 final holdout；下一步可生成候选信号缓存并做 Freqtrade 级回测，当前 dry-run 仍暂不调整。"
        )
    else:
        lines.append(
            "- 选择期选中的配置未通过 final holdout；不包装、不进入 paper/dry-run，后续继续扩样本或设计新特征。"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4%}"


if __name__ == "__main__":
    raise SystemExit(main())
