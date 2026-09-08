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
    )
except ImportError:  # pragma: no cover - direct legacy script compatibility.
    from alphamill.factor_factory.bench.train_low_frequency_walk_forward_baselines import (
        ROUND_TRIP_FEE,
        fit_predict,
        infer_feature_columns,
    )

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TIMEFRAME = "1h"
HORIZON = 12
MODEL = "ridge"
TARGET_COLUMN = f"target_return_{HORIZON}"
STAKE = 100.0
TRAIN_DAYS = 180
TEST_DAYS = 45
QUANTILE = 0.95
FILTERED_PAIRS = {"BNB/USDT", "DOGE/USDT", "ETH/USDT", "SOL/USDT"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate simple regime filters for the low-frequency Ridge candidate."
    )
    parser.add_argument(
        "--dataset", default="reports/low-frequency-supervised-dataset-20260607.parquet"
    )
    parser.add_argument(
        "--output", default="reports/low-frequency-candidate-regime-filters-20260617.json"
    )
    parser.add_argument("--holdout-days", type=int, default=90)
    args = parser.parse_args()

    dataset = pd.read_parquet(PROJECT_ROOT / args.dataset)
    dataset["date"] = pd.to_datetime(dataset["date"], utc=True)
    frame = dataset[dataset["timeframe"] == TIMEFRAME].copy()
    frame = frame.dropna(subset=[TARGET_COLUMN]).sort_values("date").reset_index(drop=True)
    feature_columns = infer_feature_columns(frame, HORIZON)
    end = frame["date"].max()
    holdout_start = end - pd.Timedelta(days=args.holdout_days)

    trades = generate_center_trades(frame, feature_columns, holdout_start, end)
    selection = trades[trades["stage"] == "selection"].copy()
    holdout = trades[trades["stage"] == "holdout"].copy()
    rules = build_rules(selection)

    rows = []
    for rule in rules:
        rows.append({"stage": "selection", **rule.meta, **summarize(rule.apply(selection))})
        rows.append({"stage": "holdout", **rule.meta, **summarize(rule.apply(holdout))})

    result_rows = pd.DataFrame(rows)
    chosen = choose_rule(result_rows)
    chosen_selection = lookup(result_rows, "selection", chosen)
    chosen_holdout = lookup(result_rows, "holdout", chosen)
    baseline_selection = lookup(result_rows, "selection", {"rule": "baseline_all_filtered_pairs"})
    baseline_holdout = lookup(result_rows, "holdout", {"rule": "baseline_all_filtered_pairs"})
    by_pair = pair_breakdown(trades)
    by_month = month_breakdown(trades)

    result = {
        "dataset": args.dataset,
        "date": "2026-06-17",
        "candidate": {
            "model": MODEL,
            "timeframe": TIMEFRAME,
            "horizon": HORIZON,
            "side": "short",
            "train_days": TRAIN_DAYS,
            "test_days": TEST_DAYS,
            "quantile": QUANTILE,
            "round_trip_fee": ROUND_TRIP_FEE,
            "stake": STAKE,
        },
        "holdout": {"days": args.holdout_days, "start": str(holdout_start), "end": str(end)},
        "rows": result_rows.to_dict(orient="records"),
        "pair_breakdown": by_pair,
        "month_breakdown": by_month,
        "summary": {
            "baseline_selection": baseline_selection,
            "baseline_holdout": baseline_holdout,
            "chosen_rule": chosen,
            "chosen_selection": chosen_selection,
            "chosen_holdout": chosen_holdout,
            "decision": decision(chosen_holdout, baseline_holdout),
        },
    }

    output = PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result_rows.to_csv(output.with_suffix(".csv"), index=False)
    write_markdown(output.with_suffix(".md"), result)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return 0


class Rule:
    def __init__(self, meta: dict, func):
        self.meta = meta
        self.func = func

    def apply(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return frame
        return frame[self.func(frame)].copy()


def generate_center_trades(
    frame: pd.DataFrame, feature_columns: list[str], holdout_start: pd.Timestamp, end: pd.Timestamp
) -> pd.DataFrame:
    trades = []
    stages = [
        ("selection", frame["date"].min() + pd.Timedelta(days=TRAIN_DAYS), holdout_start),
        ("holdout", holdout_start, end),
    ]
    for stage, start, stage_end in stages:
        current = start
        while current < stage_end:
            train_start = current - pd.Timedelta(days=TRAIN_DAYS)
            test_end = min(current + pd.Timedelta(days=TEST_DAYS), stage_end)
            train = frame[(frame["date"] >= train_start) & (frame["date"] < current)].copy()
            test = frame[(frame["date"] >= current) & (frame["date"] < test_end)].copy()
            if len(train) >= 1000 and len(test) > 0:
                train_pred, test_pred = fit_predict(
                    MODEL, train, test, feature_columns, TARGET_COLUMN
                )
                train_eval = train.copy()
                test_eval = test.copy()
                train_eval["prediction"] = train_pred
                test_eval["prediction"] = test_pred
                threshold = float(train_eval["prediction"].quantile(1 - QUANTILE))
                signals = test_eval[
                    (test_eval["prediction"] <= threshold)
                    & (test_eval["pair"].isin(FILTERED_PAIRS))
                ].copy()
                trades.extend(simulate(signals, stage, current, test_end))
            current = test_end
    return pd.DataFrame(trades)


def simulate(
    signals: pd.DataFrame, stage: str, window_start: pd.Timestamp, test_end: pd.Timestamp
) -> list[dict]:
    rows = []
    hold = pd.Timedelta(hours=HORIZON)
    next_available_by_pair: dict[str, pd.Timestamp] = {}
    for row in signals.sort_values("date").itertuples(index=False):
        next_available = next_available_by_pair.get(row.pair, pd.Timestamp.min.tz_localize("UTC"))
        if row.date < next_available:
            continue
        gross_return = -float(getattr(row, TARGET_COLUMN))
        net_return = gross_return - ROUND_TRIP_FEE
        rows.append(
            {
                "stage": stage,
                "window_start": window_start,
                "test_end": test_end,
                "pair": row.pair,
                "entry_time": row.date,
                "prediction": float(row.prediction),
                "gross_return": gross_return,
                "net_return": net_return,
                "pnl": net_return * STAKE,
                "trend_state": int(row.trend_state),
                "return_12": float(row.return_12),
                "return_24": float(row.return_24),
                "volatility_24": float(row.volatility_24),
                "volatility_72": float(row.volatility_72),
                "atr_pct_14": float(row.atr_pct_14),
                "volume_ratio_24": float(row.volume_ratio_24),
                "volume_z_72": float(row.volume_z_72),
                "ema_12_26_ratio": float(row.ema_12_26_ratio),
                "ema_26_50_ratio": float(row.ema_26_50_ratio),
            }
        )
        next_available_by_pair[row.pair] = row.date + hold
    return rows


def build_rules(selection: pd.DataFrame) -> list[Rule]:
    rules = [
        Rule(
            {"rule": "baseline_all_filtered_pairs", "family": "baseline"},
            lambda frame: pd.Series(True, index=frame.index),
        )
    ]
    for state in [-1, 0, 1]:
        rules.append(
            Rule(
                {"rule": f"trend_state_eq_{state}", "family": "trend"},
                lambda frame, state=state: frame["trend_state"] == state,
            )
        )
    rules.append(
        Rule(
            {"rule": "trend_state_not_bull", "family": "trend"},
            lambda frame: frame["trend_state"] != 1,
        )
    )
    rules.append(
        Rule(
            {"rule": "trend_state_not_bear", "family": "trend"},
            lambda frame: frame["trend_state"] != -1,
        )
    )

    for column in [
        "return_12",
        "return_24",
        "volatility_24",
        "volatility_72",
        "atr_pct_14",
        "volume_ratio_24",
        "volume_z_72",
        "ema_12_26_ratio",
    ]:
        values = selection[column].replace([np.inf, -np.inf], np.nan).dropna()
        if values.empty:
            continue
        for q in [0.25, 0.50, 0.75]:
            threshold = float(values.quantile(q))
            rules.append(
                Rule(
                    {
                        "rule": f"{column}_lte_q{int(q * 100)}",
                        "family": column,
                        "threshold": threshold,
                    },
                    lambda frame, column=column, threshold=threshold: frame[column] <= threshold,
                )
            )
            rules.append(
                Rule(
                    {
                        "rule": f"{column}_gte_q{int(q * 100)}",
                        "family": column,
                        "threshold": threshold,
                    },
                    lambda frame, column=column, threshold=threshold: frame[column] >= threshold,
                )
            )
    for pair in sorted(FILTERED_PAIRS):
        rules.append(
            Rule(
                {"rule": f"only_{pair.replace('/', '_')}", "family": "pair"},
                lambda frame, pair=pair: frame["pair"] == pair,
            )
        )
        rules.append(
            Rule(
                {"rule": f"exclude_{pair.replace('/', '_')}", "family": "pair"},
                lambda frame, pair=pair: frame["pair"] != pair,
            )
        )
    return rules


def summarize(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {
            "trades": 0,
            "pairs": 0,
            "net_mean": None,
            "winrate": None,
            "total_pnl": 0.0,
            "max_drawdown": 0.0,
            "positive_month_ratio": None,
            "positive_window_ratio": None,
            "decision": "FAIL",
        }
    data = frame.copy()
    data["entry_time"] = pd.to_datetime(data["entry_time"], utc=True)
    data["month"] = data["entry_time"].dt.strftime("%Y-%m")
    cumulative = data["pnl"].cumsum()
    drawdown = cumulative.cummax().clip(lower=0.0) - cumulative
    month_pnl = data.groupby("month")["pnl"].sum()
    window_pnl = data.groupby("window_start")["pnl"].sum()
    net_mean = float(data["net_return"].mean())
    positive_month_ratio = float((month_pnl > 0).mean())
    positive_window_ratio = float((window_pnl > 0).mean())
    return {
        "trades": int(len(data)),
        "pairs": int(data["pair"].nunique()),
        "net_mean": net_mean,
        "winrate": float((data["net_return"] > 0).mean()),
        "total_pnl": float(data["pnl"].sum()),
        "max_drawdown": float(drawdown.max()),
        "positive_month_ratio": positive_month_ratio,
        "positive_window_ratio": positive_window_ratio,
        "decision": "PASS"
        if len(data) >= 30
        and net_mean > 0
        and positive_month_ratio >= 0.5
        and positive_window_ratio >= 0.5
        else "FAIL",
    }


def choose_rule(rows: pd.DataFrame) -> dict | None:
    selection = rows[
        (rows["stage"] == "selection")
        & (rows["trades"] >= 30)
        & (rows["rule"] != "baseline_all_filtered_pairs")
    ].copy()
    passed = selection[selection["decision"] == "PASS"].copy()
    pool = passed if not passed.empty else selection
    if pool.empty:
        return None
    row = pool.sort_values(
        ["positive_window_ratio", "positive_month_ratio", "total_pnl"],
        ascending=[False, False, False],
    ).iloc[0]
    return {"rule": row["rule"]}


def lookup(rows: pd.DataFrame, stage: str, key: dict | None) -> dict | None:
    if key is None:
        return None
    matched = rows[(rows["stage"] == stage) & (rows["rule"] == key["rule"])]
    if matched.empty:
        return None
    return normalize(matched.iloc[0].to_dict())


def pair_breakdown(trades: pd.DataFrame) -> list[dict]:
    rows = []
    if trades.empty:
        return rows
    for (stage, pair), group in trades.groupby(["stage", "pair"]):
        item = summarize(group)
        rows.append({"stage": stage, "pair": pair, **item})
    return sorted(rows, key=lambda row: (row["stage"], row["total_pnl"]), reverse=True)


def month_breakdown(trades: pd.DataFrame) -> list[dict]:
    rows = []
    if trades.empty:
        return rows
    frame = trades.copy()
    frame["entry_time"] = pd.to_datetime(frame["entry_time"], utc=True)
    frame["month"] = frame["entry_time"].dt.strftime("%Y-%m")
    for (stage, month), group in frame.groupby(["stage", "month"]):
        item = summarize(group)
        rows.append({"stage": stage, "month": month, **item})
    return sorted(rows, key=lambda row: (row["stage"], row.get("month", "")))


def decision(chosen_holdout: dict | None, baseline_holdout: dict | None) -> str:
    if (
        chosen_holdout
        and chosen_holdout.get("decision") == "PASS"
        and chosen_holdout.get("total_pnl", 0)
        > max(0, (baseline_holdout or {}).get("total_pnl", 0))
    ):
        return "regime_filter_rescues_holdout_needs_freqtrade_backtest"
    if (
        chosen_holdout
        and chosen_holdout.get("total_pnl", 0)
        > max(0, (baseline_holdout or {}).get("total_pnl", 0))
        and chosen_holdout.get("net_mean", 0) > 0
        and chosen_holdout.get("trades", 0) < 30
    ):
        return "regime_filter_promising_but_underpowered"
    return "no_simple_regime_filter_rescued_holdout"


def normalize(row: dict | None) -> dict | None:
    if row is None:
        return None
    out = {}
    for key, value in row.items():
        if pd.isna(value):
            out[key] = None
        elif isinstance(value, np.generic):
            out[key] = value.item()
        else:
            out[key] = value
    return out


def write_markdown(path: Path, result: dict) -> None:
    summary = result["summary"]
    lines = [
        "# 低频 Ridge 候选市场状态过滤验证",
        "",
        "日期：2026-06-17",
        "",
        "## 方法",
        "",
        f"- 数据集：`{result['dataset']}`",
        "- 固定候选：Ridge，1h，horizon=12，short-only，180 天训练 / 45 天测试 / bottom 5%。",
        "- 交易对：过滤版 4 对 BNB/DOGE/ETH/SOL。",
        f"- 最终留出区间：{result['holdout']['start']} 至 {result['holdout']['end']}。",
        "- 过滤规则只使用选择期交易的特征分布定阈值，再直接应用到留出期。",
        "",
        "## 基线与选择规则",
        "",
    ]
    append_result(lines, "选择期基线", summary["baseline_selection"])
    append_result(lines, "留出期基线", summary["baseline_holdout"])
    if summary["chosen_rule"]:
        lines.append(f"- 选择期挑出的最佳过滤规则：`{summary['chosen_rule']['rule']}`。")
    append_result(lines, "选择规则的选择期表现", summary["chosen_selection"])
    append_result(lines, "选择规则的留出期表现", summary["chosen_holdout"])

    lines.extend(
        [
            "",
            "## 留出期基线分交易对",
            "",
            "| 交易对 | 交易 | 总 PnL | 净收益均值 | 胜率 | 判定 |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in [item for item in result["pair_breakdown"] if item["stage"] == "holdout"]:
        lines.append(
            f"| {row['pair']} | {row['trades']} | {row['total_pnl']:.4f} | {fmt_pct(row['net_mean'])} | {fmt_pct(row['winrate'])} | {row['decision']} |"
        )
    lines.extend(
        [
            "",
            "## 留出期基线分月份",
            "",
            "| 月份 | 交易 | 总 PnL | 净收益均值 | 胜率 |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in [item for item in result["month_breakdown"] if item["stage"] == "holdout"]:
        lines.append(
            f"| {row['month']} | {row['trades']} | {row['total_pnl']:.4f} | {fmt_pct(row['net_mean'])} | {fmt_pct(row['winrate'])} |"
        )
    lines.extend(
        [
            "",
            "## 结论",
            "",
            f"- 状态：`{summary['decision']}`。",
            "- 该验证不调整当前 dry-run 配置；若过滤规则只在小样本上改善，应转向新特征/模型并扩大验证，而不是直接包装该 Ridge 候选。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_result(lines: list[str], title: str, row: dict | None) -> None:
    if not row:
        lines.append(f"- {title}：无结果。")
        return
    lines.append(
        f"- {title}：`{row['rule']}`，{row['trades']} 笔，PnL {row['total_pnl']:.4f} USDT，"
        f"净均值 {fmt_pct(row['net_mean'])}，胜率 {fmt_pct(row['winrate'])}，"
        f"正收益月份 {fmt_pct(row['positive_month_ratio'])}，正收益窗口 {fmt_pct(row['positive_window_ratio'])}，"
        f"判定 `{row['decision']}`。"
    )


def fmt_pct(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.2%}"


if __name__ == "__main__":
    raise SystemExit(main())
