"""统一列集面板装载的确定性（`R1-103`）：结果不得依赖 CSV 原始行序。"""

from __future__ import annotations

from pathlib import Path

import pytest

from alphamill.evaluation.contract_common import UpstreamContractError
from alphamill.evaluation.run_config import load_unified_panel

HEADER = "time,symbol,close,signal,forward_return\n"
GROUPED = (
    "2026-01-01T00:00:00Z,BTC-USDT,100,1.0,0.01\n"
    "2026-01-01T01:00:00Z,BTC-USDT,101,2.0,0.02\n"
    "2026-01-01T00:00:00Z,ETH-USDT,50,3.0,0.03\n"
    "2026-01-01T01:00:00Z,ETH-USDT,51,4.0,0.04\n"
)
SHUFFLED = (
    "2026-01-01T01:00:00Z,ETH-USDT,51,4.0,0.04\n"
    "2026-01-01T00:00:00Z,BTC-USDT,100,1.0,0.01\n"
    "2026-01-01T01:00:00Z,BTC-USDT,101,2.0,0.02\n"
    "2026-01-01T00:00:00Z,ETH-USDT,50,3.0,0.03\n"
)


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "panel.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + body, encoding="utf-8")
    return path


def test_panel_loading_is_independent_of_csv_row_order(tmp_path):
    grouped = load_unified_panel(_write(tmp_path / "a", GROUPED))
    shuffled = load_unified_panel(_write(tmp_path / "b", SHUFFLED))
    assert grouped == shuffled
    assert grouped[0] == (
        "2026-01-01T00:00:00Z",
        "2026-01-01T01:00:00Z",
        "2026-01-01T00:00:00Z",
        "2026-01-01T01:00:00Z",
    )
    assert grouped[1] == ("BTC-USDT", "BTC-USDT", "ETH-USDT", "ETH-USDT")


def test_duplicate_time_symbol_is_rejected(tmp_path):
    duplicated = GROUPED + "2026-01-01T00:00:00Z,BTC-USDT,100,9.0,9.0\n"
    with pytest.raises(UpstreamContractError, match="重复"):
        load_unified_panel(_write(tmp_path, duplicated))


def test_curve_rejects_non_monotonic_times():
    """R2-209：曲线时间轴必须严格递增，多标的面板不得回跳。"""
    from datetime import UTC, datetime

    from alphamill.factor_factory.bench.curves import CurvesError, build_equity_curves

    times = (
        datetime(2026, 1, 1, 0, tzinfo=UTC),
        datetime(2026, 1, 1, 1, tzinfo=UTC),
        datetime(2026, 1, 1, 0, 30, tzinfo=UTC),
    )
    with pytest.raises(CurvesError, match="严格递增"):
        build_equity_curves((0.1, 0.2, 0.3), times=times)


def test_panel_evaluation_groups_by_symbol_and_has_monotonic_times(tmp_path):
    """R2-209：多标的面板按 symbol 分组算交易摘要，时间轴单调、无跨标的边界换手。"""
    from alphamill.evaluation.pipeline import evaluate_fixture
    from alphamill.evaluation.run_config import load_run_config

    body = (
        "2026-01-01T02:00:00Z,BTC,100,1.0,0.01\n"
        "2026-01-01T00:00:00Z,BTC,100,1.0,0.01\n"
        "2026-01-01T01:00:00Z,BTC,100,1.0,0.02\n"
        "2026-01-01T02:00:00Z,ETH,50,1.0,0.02\n"
        "2026-01-01T01:00:00Z,ETH,50,1.0,0.01\n"
        "2026-01-01T00:00:00Z,ETH,50,1.0,0.03\n"
    )
    path = _write(tmp_path, body)
    config = load_run_config(
        Path(__file__).resolve().parents[2] / "fixtures" / "f007" / "method-v1.json"
    )
    times, symbols, signals, labels = load_unified_panel(path)
    evaluation = evaluate_fixture(
        config=config,
        times=times,
        signals=signals,
        labels=labels,
        execution_tier="canonical",
        observed_at="2026-01-01T00:00:00Z",
        symbols=symbols,
    )
    assert evaluation.curve_times == (
        "2026-01-01T00:00:00Z",
        "2026-01-01T01:00:00Z",
        "2026-01-01T02:00:00Z",
    )
    assert len(evaluation.period_returns) == 3
    assert evaluation.trade_summary["round_trips"] == 2
