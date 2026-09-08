from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
ROUND_TRIP_FEE = 0.003
TARGETS = [("1h", 12), ("1h", 24), ("4h", 6), ("4h", 12)]
QUANTILES = [0.95, 0.98, 0.99]
EXCLUDED_COLUMNS = {"date", "pair", "timeframe"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Train low-frequency walk-forward baseline models."
    )
    parser.add_argument(
        "--dataset", default="reports/low-frequency-supervised-dataset-20260607.parquet"
    )
    parser.add_argument(
        "--output", default="reports/low-frequency-walk-forward-baselines-20260607.json"
    )
    parser.add_argument("--train-days", type=int, default=180)
    parser.add_argument("--test-days", type=int, default=45)
    parser.add_argument("--models", default="ridge,hgb")
    parser.add_argument("--stake", type=float, default=100.0)
    args = parser.parse_args()

    dataset = pd.read_parquet(PROJECT_ROOT / args.dataset)
    dataset["date"] = pd.to_datetime(dataset["date"], utc=True)
    model_names = [name.strip() for name in args.models.split(",") if name.strip()]
    sklearn_available, sklearn_error = sklearn_status()

    summaries = []
    all_trades = []
    for timeframe, horizon in TARGETS:
        frame = dataset[dataset["timeframe"] == timeframe].copy()
        target_column = f"target_return_{horizon}"
        frame = frame.dropna(subset=[target_column]).sort_values("date").reset_index(drop=True)
        feature_columns = infer_feature_columns(frame, horizon)
        windows = make_windows(frame, args.train_days, args.test_days)
        for model_name in model_names:
            if model_name == "hgb" and not sklearn_available:
                summaries.append(
                    {
                        "timeframe": timeframe,
                        "horizon": horizon,
                        "model": model_name,
                        "skipped": True,
                        "reason": sklearn_error,
                    }
                )
                continue
            predictions = []
            trades = []
            for window_index, (train, test, meta) in enumerate(windows, start=1):
                train_pred, test_pred = fit_predict(
                    model_name=model_name,
                    train=train,
                    test=test,
                    feature_columns=feature_columns,
                    target_column=target_column,
                )
                train_eval = train[["date", "pair", target_column]].copy()
                test_eval = test[["date", "pair", target_column]].copy()
                train_eval["prediction"] = train_pred
                test_eval["prediction"] = test_pred
                test_eval["window"] = window_index
                predictions.append(test_eval)
                trades.extend(
                    evaluate_window_trades(
                        train_eval=train_eval,
                        test_eval=test_eval,
                        timeframe=timeframe,
                        horizon=horizon,
                        model_name=model_name,
                        window_index=window_index,
                        meta=meta,
                        stake=args.stake,
                    )
                )
            prediction_frame = (
                pd.concat(predictions, ignore_index=True) if predictions else pd.DataFrame()
            )
            trade_frame = pd.DataFrame(trades)
            all_trades.append(trade_frame)
            summaries.append(
                summarize_model(
                    timeframe=timeframe,
                    horizon=horizon,
                    model_name=model_name,
                    frame=prediction_frame,
                    trades=trade_frame,
                    windows=len(windows),
                    feature_count=len(feature_columns),
                )
            )

    trades_frame = (
        pd.concat([frame for frame in all_trades if not frame.empty], ignore_index=True)
        if all_trades
        else pd.DataFrame()
    )
    result = {
        "dataset": args.dataset,
        "rows": int(len(dataset)),
        "train_days": args.train_days,
        "test_days": args.test_days,
        "round_trip_fee": ROUND_TRIP_FEE,
        "targets": [{"timeframe": timeframe, "horizon": horizon} for timeframe, horizon in TARGETS],
        "models": model_names,
        "sklearn_available": sklearn_available,
        "sklearn_error": sklearn_error,
        "summaries": sorted(
            summaries, key=lambda row: row.get("best_total_pnl", -1e18), reverse=True
        ),
        "recommendation": recommendation(summaries),
    }

    output = PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    trades_frame.to_csv(output.with_suffix(".csv"), index=False)
    write_markdown(output.with_suffix(".md"), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def sklearn_status() -> tuple[bool, str | None]:
    try:
        import sklearn  # noqa: F401

        return True, None
    except Exception as exc:
        return False, str(exc)


def infer_feature_columns(frame: pd.DataFrame, horizon: int) -> list[str]:
    columns = []
    for column in frame.columns:
        if column in EXCLUDED_COLUMNS or column.startswith("target_"):
            continue
        if pd.api.types.is_numeric_dtype(frame[column]) or pd.api.types.is_bool_dtype(
            frame[column]
        ):
            columns.append(column)
    for pair in sorted(frame["pair"].unique()):
        column = f"pair_{pair.replace('/', '_')}"
        frame[column] = (frame["pair"] == pair).astype(float)
        columns.append(column)
    return columns


def make_windows(
    frame: pd.DataFrame, train_days: int, test_days: int
) -> list[tuple[pd.DataFrame, pd.DataFrame, dict]]:
    start = frame["date"].min()
    end = frame["date"].max()
    current = start + pd.Timedelta(days=train_days)
    windows = []
    while current < end:
        train_start = current - pd.Timedelta(days=train_days)
        test_end = min(current + pd.Timedelta(days=test_days), end)
        train = frame[(frame["date"] >= train_start) & (frame["date"] < current)].copy()
        test = frame[(frame["date"] >= current) & (frame["date"] < test_end)].copy()
        if len(train) >= 1000 and len(test) > 0:
            windows.append(
                (
                    train,
                    test,
                    {
                        "train_start": str(train_start),
                        "train_end": str(current),
                        "test_end": str(test_end),
                    },
                )
            )
        current = test_end
    return windows


def fit_predict(
    model_name: str,
    train: pd.DataFrame,
    test: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
) -> tuple[np.ndarray, np.ndarray]:
    x_train, x_test = standardized_features(train, test, feature_columns)
    y_train = train[target_column].to_numpy(dtype=float)
    if model_name == "ridge":
        return ridge_predict(x_train, y_train, x_train), ridge_predict(x_train, y_train, x_test)
    if model_name == "hgb":
        from sklearn.ensemble import HistGradientBoostingRegressor

        model = HistGradientBoostingRegressor(
            max_iter=120,
            learning_rate=0.04,
            max_leaf_nodes=15,
            l2_regularization=0.05,
            random_state=42,
        )
        model.fit(x_train, y_train)
        return model.predict(x_train), model.predict(x_test)
    raise ValueError(f"Unknown model: {model_name}")


def standardized_features(
    train: pd.DataFrame, test: pd.DataFrame, feature_columns: list[str]
) -> tuple[np.ndarray, np.ndarray]:
    x_train = (
        train[feature_columns].replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy(dtype=float)
    )
    x_test = (
        test[feature_columns].replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy(dtype=float)
    )
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    std[std == 0] = 1.0
    return (x_train - mean) / std, (x_test - mean) / std


def ridge_predict(
    x_train: np.ndarray, y_train: np.ndarray, x_eval: np.ndarray, alpha: float = 10.0
) -> np.ndarray:
    x_train_i = np.column_stack([np.ones(len(x_train)), x_train])
    x_eval_i = np.column_stack([np.ones(len(x_eval)), x_eval])
    penalty = np.eye(x_train_i.shape[1]) * alpha
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(x_train_i.T @ x_train_i + penalty, x_train_i.T @ y_train)
    return x_eval_i @ beta


def evaluate_window_trades(
    train_eval: pd.DataFrame,
    test_eval: pd.DataFrame,
    timeframe: str,
    horizon: int,
    model_name: str,
    window_index: int,
    meta: dict,
    stake: float,
) -> list[dict]:
    rows = []
    target_column = f"target_return_{horizon}"
    for quantile in QUANTILES:
        high = float(train_eval["prediction"].quantile(quantile))
        low = float(train_eval["prediction"].quantile(1 - quantile))
        rows.extend(
            simulate_side(
                signals=test_eval[test_eval["prediction"] >= high],
                side="long",
                timeframe=timeframe,
                horizon=horizon,
                model_name=model_name,
                quantile=quantile,
                window_index=window_index,
                meta=meta,
                target_column=target_column,
                stake=stake,
            )
        )
        rows.extend(
            simulate_side(
                signals=test_eval[test_eval["prediction"] <= low],
                side="short",
                timeframe=timeframe,
                horizon=horizon,
                model_name=model_name,
                quantile=quantile,
                window_index=window_index,
                meta=meta,
                target_column=target_column,
                stake=stake,
            )
        )
    return rows


def simulate_side(
    signals: pd.DataFrame,
    side: str,
    timeframe: str,
    horizon: int,
    model_name: str,
    quantile: float,
    window_index: int,
    meta: dict,
    target_column: str,
    stake: float,
) -> list[dict]:
    trades = []
    next_available_by_pair: dict[str, pd.Timestamp] = {}
    hold = pd.Timedelta(hours=horizon if timeframe == "1h" else horizon * 4)
    for row in signals.sort_values("date").itertuples(index=False):
        next_available = next_available_by_pair.get(row.pair, pd.Timestamp.min.tz_localize("UTC"))
        if row.date < next_available:
            continue
        gross_return = float(getattr(row, target_column))
        if side == "short":
            gross_return = -gross_return
        net_return = gross_return - ROUND_TRIP_FEE
        label = f"{model_name}_{timeframe}_h{horizon}_{side}_top{int((1 - quantile) * 100)}"
        trades.append(
            {
                "candidate": label,
                "model": model_name,
                "timeframe": timeframe,
                "horizon": horizon,
                "side": side,
                "quantile": quantile,
                "window": window_index,
                "pair": row.pair,
                "entry_time": str(row.date),
                "exit_time": str(row.date + hold),
                "prediction": float(row.prediction),
                "gross_return": gross_return,
                "net_return": net_return,
                "pnl": net_return * stake,
                "train_start": meta["train_start"],
                "train_end": meta["train_end"],
                "test_end": meta["test_end"],
            }
        )
        next_available_by_pair[row.pair] = row.date + hold
    return trades


def summarize_model(
    timeframe: str,
    horizon: int,
    model_name: str,
    frame: pd.DataFrame,
    trades: pd.DataFrame,
    windows: int,
    feature_count: int,
) -> dict:
    target_column = f"target_return_{horizon}"
    base = {
        "timeframe": timeframe,
        "horizon": horizon,
        "model": model_name,
        "rows": int(len(frame)),
        "windows": int(windows),
        "feature_count": int(feature_count),
        "ic": optional_corr(frame["prediction"], frame[target_column]) if not frame.empty else None,
        "direction_accuracy": float(
            ((frame["prediction"] > 0) == (frame[target_column] > 0)).mean()
        )
        if not frame.empty
        else None,
        "trade_slices": [],
        "best_total_pnl": -1e18,
    }
    if trades.empty:
        return base
    slices = []
    for candidate, group in trades.groupby("candidate"):
        group = group.copy()
        group["entry_time"] = pd.to_datetime(group["entry_time"], utc=True)
        group["month"] = group["entry_time"].dt.strftime("%Y-%m")
        cumulative = group["pnl"].cumsum()
        drawdown = cumulative.cummax().clip(lower=0.0) - cumulative
        month_pnl = group.groupby("month")["pnl"].sum()
        slices.append(
            {
                "candidate": candidate,
                "trades": int(len(group)),
                "pairs": int(group["pair"].nunique()),
                "gross_mean": float(group["gross_return"].mean()),
                "net_mean": float(group["net_return"].mean()),
                "winrate": float((group["net_return"] > 0).mean()),
                "total_pnl": float(group["pnl"].sum()),
                "max_drawdown": float(drawdown.max()),
                "positive_month_ratio": float((month_pnl > 0).mean()),
                "decision": "PASS"
                if len(group) >= 30
                and group["net_return"].mean() > 0
                and (month_pnl > 0).mean() >= 0.5
                else "FAIL",
            }
        )
    slices.sort(key=lambda row: row["total_pnl"], reverse=True)
    base["trade_slices"] = slices
    base["best_total_pnl"] = slices[0]["total_pnl"] if slices else -1e18
    return base


def optional_corr(left: pd.Series, right: pd.Series) -> float | None:
    value = left.rank().corr(right.rank())
    return None if pd.isna(value) else float(value)


def recommendation(summaries: list[dict]) -> dict:
    candidates = []
    for summary in summaries:
        if summary.get("skipped"):
            continue
        for row in summary.get("trade_slices", []):
            if row["decision"] == "PASS":
                candidates.append(
                    {
                        "timeframe": summary["timeframe"],
                        "horizon": summary["horizon"],
                        "model": summary["model"],
                        **row,
                    }
                )
    candidates.sort(key=lambda row: row["total_pnl"], reverse=True)
    if candidates:
        return {
            "next_step": "freqtrade_low_frequency_candidate_backtest",
            "reason": "at least one low-frequency walk-forward candidate passed non-overlap checks",
            "best": candidates[0],
        }
    best = None
    for summary in sorted(
        summaries, key=lambda row: row.get("best_total_pnl", -1e18), reverse=True
    ):
        if summary.get("trade_slices"):
            best = {
                "timeframe": summary["timeframe"],
                "horizon": summary["horizon"],
                "model": summary["model"],
                **summary["trade_slices"][0],
            }
            break
    return {
        "next_step": "add_new_features_or_try_more_robust_models",
        "reason": "no low-frequency candidate passed positive expectancy and stability checks",
        "best": best,
    }


def write_markdown(path: Path, result: dict) -> None:
    lines = [
        "# 多交易对低频 Walk-forward Baseline",
        "",
        "日期：2026-06-07",
        "",
        "## 方法",
        "",
        f"- 数据集：`{result['dataset']}`",
        f"- 样本：{result['rows']}",
        f"- Walk-forward：过去 {result['train_days']} 天训练，未来 {result['test_days']} 天验证。",
        "- 模型：Ridge 与 sklearn Histogram Gradient Boosting。",
        "- 阈值：每个窗口只使用训练集预测分位数；执行为单交易对非重叠持仓。",
        f"- 往返成本：{result['round_trip_fee']:.2%}。",
        "",
        "## 模型汇总",
        "",
        "| 模型 | Timeframe | Horizon | 样本 | 窗口 | IC | 方向准确率 | 最佳切片 | 交易 | 净收益均值 | 总 PnL | 正收益月份 | 结论 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in result["summaries"]:
        if row.get("skipped"):
            lines.append(
                f"| {row['model']} | {row['timeframe']} | {row['horizon']} | - | - | - | - | skipped | - | - | - | - | FAIL |"
            )
            continue
        best = row["trade_slices"][0] if row["trade_slices"] else None
        lines.append(
            f"| {row['model']} | {row['timeframe']} | {row['horizon']} | {row['rows']} | {row['windows']} | "
            f"{fmt(row['ic'])} | {fmt_pct(row['direction_accuracy'])} | `{best['candidate'] if best else 'n/a'}` | "
            f"{best['trades'] if best else 0} | {fmt_pct(best['net_mean'] if best else None)} | "
            f"{best['total_pnl'] if best else 0:.4f} | {fmt_pct(best['positive_month_ratio'] if best else None)} | "
            f"{best['decision'] if best else 'FAIL'} |"
        )
    rec = result["recommendation"]
    lines.extend(
        ["", "## 结论", "", f"- 建议下一步：`{rec['next_step']}`。", f"- 原因：{rec['reason']}。"]
    )
    if rec.get("best"):
        best = rec["best"]
        lines.append(
            f"- 最佳候选：{best['model']} {best['timeframe']} horizon={best['horizon']} `{best['candidate']}`，"
            f"交易 {best['trades']} 笔，净收益均值 {fmt_pct(best['net_mean'])}，总 PnL {best['total_pnl']:.4f} USDT。"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4%}"


if __name__ == "__main__":
    raise SystemExit(main())
