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
TIMEFRAME = "1h"
HORIZON = 12
MODEL = "ridge"
TARGET_COLUMN = f"target_return_{HORIZON}"
STAKE = 100.0
FILTERED_PAIRS = {"BNB/USDT", "DOGE/USDT", "ETH/USDT", "SOL/USDT"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate low-frequency Ridge candidate on a final time holdout."
    )
    parser.add_argument(
        "--dataset", default="reports/low-frequency-supervised-dataset-20260607.parquet"
    )
    parser.add_argument("--output", default="reports/low-frequency-candidate-holdout-20260617.json")
    parser.add_argument("--holdout-days", type=int, default=90)
    parser.add_argument("--train-days", default="120,180,240")
    parser.add_argument("--test-days", default="30,45,60")
    parser.add_argument("--quantiles", default="0.90,0.95,0.97,0.98,0.99")
    args = parser.parse_args()

    train_days_values = parse_ints(args.train_days)
    test_days_values = parse_ints(args.test_days)
    quantiles = parse_floats(args.quantiles)

    dataset = pd.read_parquet(PROJECT_ROOT / args.dataset)
    dataset["date"] = pd.to_datetime(dataset["date"], utc=True)
    frame = dataset[dataset["timeframe"] == TIMEFRAME].copy()
    frame = frame.dropna(subset=[TARGET_COLUMN]).sort_values("date").reset_index(drop=True)
    feature_columns = infer_feature_columns(frame, HORIZON)

    end = frame["date"].max()
    holdout_start = end - pd.Timedelta(days=args.holdout_days)

    selection_rows = []
    holdout_rows = []
    for train_days in train_days_values:
        for test_days in test_days_values:
            selection_predictions = run_walk_forward(
                frame=frame,
                feature_columns=feature_columns,
                train_days=train_days,
                test_days=test_days,
                start=frame["date"].min() + pd.Timedelta(days=train_days),
                end=holdout_start,
            )
            holdout_predictions = run_walk_forward(
                frame=frame,
                feature_columns=feature_columns,
                train_days=train_days,
                test_days=test_days,
                start=holdout_start,
                end=end,
            )
            for quantile in quantiles:
                selection_trades = simulate_predictions(selection_predictions, quantile)
                holdout_trades = simulate_predictions(holdout_predictions, quantile)
                selection_rows.extend(
                    score_scopes(selection_trades, "selection", train_days, test_days, quantile)
                )
                holdout_rows.extend(
                    score_scopes(holdout_trades, "holdout", train_days, test_days, quantile)
                )

    selection = pd.DataFrame(selection_rows)
    holdout = pd.DataFrame(holdout_rows)
    chosen = choose_config(selection)
    center = {"train_days": 180, "test_days": 45, "quantile": 0.95, "scope": "filtered_no_btc_xrp"}
    chosen_holdout = lookup(holdout, chosen) if chosen else None
    center_selection = lookup(selection, center)
    center_holdout = lookup(holdout, center)

    result = {
        "dataset": args.dataset,
        "date": "2026-06-17",
        "candidate": {
            "model": MODEL,
            "timeframe": TIMEFRAME,
            "horizon": HORIZON,
            "side": "short",
            "round_trip_fee": ROUND_TRIP_FEE,
            "stake": STAKE,
        },
        "holdout": {
            "days": args.holdout_days,
            "start": str(holdout_start),
            "end": str(end),
        },
        "selection_rows": selection.to_dict(orient="records"),
        "holdout_rows": holdout.to_dict(orient="records"),
        "summary": {
            "chosen_from_selection": chosen,
            "chosen_holdout": chosen_holdout,
            "center_selection": center_selection,
            "center_holdout": center_holdout,
            "decision": decision(chosen_holdout, center_holdout),
        },
    }

    output = PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.concat([selection, holdout], ignore_index=True).to_csv(
        output.with_suffix(".csv"), index=False
    )
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
                target_column=TARGET_COLUMN,
            )
            train_eval = train[["date", "pair", TARGET_COLUMN]].copy()
            test_eval = test[["date", "pair", TARGET_COLUMN]].copy()
            train_eval["prediction"] = train_pred
            test_eval["prediction"] = test_pred
            test_eval["window_start"] = str(current)
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
    predictions: list[tuple[pd.DataFrame, pd.DataFrame, dict]], quantile: float
) -> pd.DataFrame:
    trades = []
    hold = pd.Timedelta(hours=HORIZON)
    for window_index, (train_eval, test_eval, meta) in enumerate(predictions, start=1):
        threshold = float(train_eval["prediction"].quantile(1 - quantile))
        signals = test_eval[test_eval["prediction"] <= threshold].copy()
        next_available_by_pair: dict[str, pd.Timestamp] = {}
        for row in signals.sort_values("date").itertuples(index=False):
            next_available = next_available_by_pair.get(
                row.pair, pd.Timestamp.min.tz_localize("UTC")
            )
            if row.date < next_available:
                continue
            gross_return = -float(getattr(row, TARGET_COLUMN))
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


def score_scopes(
    trades: pd.DataFrame, stage: str, train_days: int, test_days: int, quantile: float
) -> list[dict]:
    return [
        {
            "stage": stage,
            "scope": "all_pairs",
            "train_days": train_days,
            "test_days": test_days,
            "quantile": quantile,
            **summarize_trades(trades),
        },
        {
            "stage": stage,
            "scope": "filtered_no_btc_xrp",
            "train_days": train_days,
            "test_days": test_days,
            "quantile": quantile,
            **summarize_trades(
                trades[trades["pair"].isin(FILTERED_PAIRS)].copy() if not trades.empty else trades
            ),
        },
    ]


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
    return {
        "trades": int(len(frame)),
        "pairs": int(frame["pair"].nunique()),
        "net_mean": net_mean,
        "winrate": float((frame["net_return"] > 0).mean()),
        "total_pnl": float(frame["pnl"].sum()),
        "max_drawdown": float(drawdown.max()),
        "positive_month_ratio": float((month_pnl > 0).mean()),
        "positive_window_ratio": float((window_pnl > 0).mean()),
        "ic": optional_corr(frame["prediction"], frame["gross_return"]) if len(frame) > 2 else None,
        "decision": "PASS"
        if len(frame) >= 30
        and net_mean > 0
        and float((month_pnl > 0).mean()) >= 0.5
        and float((window_pnl > 0).mean()) >= 0.5
        else "FAIL",
    }


def empty_summary() -> dict:
    return {
        "trades": 0,
        "pairs": 0,
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
    filtered = selection[
        (selection["scope"] == "filtered_no_btc_xrp") & (selection["trades"] >= 30)
    ].copy()
    passed = filtered[filtered["decision"] == "PASS"].copy()
    pool = passed if not passed.empty else filtered
    if pool.empty:
        return None
    row = pool.sort_values(
        ["positive_month_ratio", "total_pnl", "trades"], ascending=[False, False, False]
    ).iloc[0]
    return key_from_row(row)


def key_from_row(row: pd.Series | dict) -> dict:
    return {
        "scope": row["scope"],
        "train_days": int(row["train_days"]),
        "test_days": int(row["test_days"]),
        "quantile": float(row["quantile"]),
    }


def lookup(rows: pd.DataFrame, key: dict | None) -> dict | None:
    if key is None:
        return None
    matched = rows[
        (rows["scope"] == key["scope"])
        & (rows["train_days"] == key["train_days"])
        & (rows["test_days"] == key["test_days"])
        & (np.isclose(rows["quantile"], key["quantile"]))
    ]
    if matched.empty:
        return None
    return normalize_dict(matched.iloc[0].to_dict())


def decision(chosen_holdout: dict | None, center_holdout: dict | None) -> str:
    chosen_pass = chosen_holdout and chosen_holdout.get("decision") == "PASS"
    center_pass = center_holdout and center_holdout.get("decision") == "PASS"
    if chosen_pass and center_pass:
        return "holdout_pass_but_requires_paper_sizing_design"
    if chosen_pass or center_pass:
        return "mixed_holdout_needs_one_more_validation"
    return "holdout_failed_do_not_paper"


def normalize_dict(row: dict | None) -> dict | None:
    if row is None:
        return None
    normalized = {}
    for key, value in row.items():
        if pd.isna(value):
            normalized[key] = None
        elif isinstance(value, np.generic):
            normalized[key] = value.item()
        else:
            normalized[key] = value
    return normalized


def write_markdown(path: Path, result: dict) -> None:
    summary = result["summary"]
    lines = [
        "# 低频 Ridge 候选最终留出验证",
        "",
        "日期：2026-06-17",
        "",
        "## 方法",
        "",
        f"- 数据集：`{result['dataset']}`",
        "- 候选族：Ridge，1h，horizon=12，short-only。",
        f"- 最终留出区间：{result['holdout']['start']} 至 {result['holdout']['end']}，共 {result['holdout']['days']} 天。",
        "- 参数选择只使用留出区间之前的数据；留出区间只做最后验证。",
        "- 每个窗口只使用训练集标准化参数和训练集预测分位数；执行为单交易对非重叠持仓。",
        "",
        "## 选择配置",
        "",
    ]
    chosen = summary["chosen_from_selection"]
    chosen_holdout = summary["chosen_holdout"]
    center_selection = summary["center_selection"]
    center_holdout = summary["center_holdout"]
    if chosen:
        lines.append(
            f"- 选择期最优过滤版配置：训练 {chosen['train_days']} 天，测试 {chosen['test_days']} 天，bottom {(1 - chosen['quantile']):.0%}。"
        )
    append_result(lines, "选择期最优配置留出表现", chosen_holdout)
    append_result(lines, "中心配置选择期表现", center_selection)
    append_result(lines, "中心配置留出表现", center_holdout)
    lines.extend(
        [
            "",
            "## 结论",
            "",
            f"- 状态：`{summary['decision']}`。",
            "- 当前不进入 paper/dry-run；若后续新证据支持重新考虑，必须先设计独立 paper 配置、仓位上限和熔断条件。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_result(lines: list[str], title: str, row: dict | None) -> None:
    lines.extend(["", f"### {title}", ""])
    if not row:
        lines.append("- 无可用结果。")
        return
    lines.extend(
        [
            f"- 配置：训练 {row['train_days']} 天，测试 {row['test_days']} 天，bottom {(1 - row['quantile']):.0%}，范围 `{row['scope']}`。",
            f"- 交易：{row['trades']} 笔，覆盖 {row['pairs']} 个交易对。",
            f"- 收益：净收益均值 {fmt_pct(row['net_mean'])}，总 PnL {row['total_pnl']:.4f} USDT，最大回撤 {row['max_drawdown']:.4f} USDT。",
            f"- 稳定性：胜率 {fmt_pct(row['winrate'])}，正收益月份 {fmt_pct(row['positive_month_ratio'])}，正收益窗口 {fmt_pct(row['positive_window_ratio'])}。",
            f"- 判定：`{row['decision']}`。",
        ]
    )


def fmt_pct(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.2%}"


if __name__ == "__main__":
    raise SystemExit(main())
