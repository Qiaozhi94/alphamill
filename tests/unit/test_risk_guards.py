"""F001 risk guard unit and batch-scenario regression tests."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from alphamill.freqtrade_bridge.risk.circuit_breaker import CircuitBreaker
from alphamill.freqtrade_bridge.risk.correlation_guard import CorrelationGuard
from alphamill.freqtrade_bridge.risk.drawdown_guard import DrawdownGuard


def _trade(closed_at: datetime, profit: float, pair: str = "BTC/USDT"):
    return SimpleNamespace(close_date_utc=closed_at, close_profit_abs=profit, pair=pair)


def test_circuit_breaker_enforces_daily_loss_and_ignores_previous_day() -> None:
    now = datetime(2026, 1, 2, 12, tzinfo=UTC)
    trades = [_trade(now.replace(hour=1), -4), _trade(now - timedelta(days=1), -100)]

    state = CircuitBreaker(max_daily_loss_ratio=0.03).evaluate(trades, equity=100, current_time=now)

    assert state.blocked is True
    assert state.reason == "daily_loss_ratio"
    assert state.daily_profit_abs == -4


def test_circuit_breaker_cooldown_counts_only_latest_loss_streak() -> None:
    now = datetime(2026, 1, 2, 12, tzinfo=UTC)
    trades = [
        _trade(now - timedelta(hours=1), -1),
        _trade(now - timedelta(hours=2), -1),
        _trade(now - timedelta(hours=3), -1),
        _trade(now - timedelta(hours=25), -1),
    ]

    state = CircuitBreaker(max_daily_loss_ratio=0, consecutive_loss_cooldown_hours=24).evaluate(
        trades, equity=100, current_time=now
    )

    assert state.blocked is True
    assert state.consecutive_losses == 3


def test_correlation_guard_checks_multiple_open_trades_as_a_batch() -> None:
    close = pd.Series(range(1, 80), dtype=float)
    trades = [_trade(datetime.now(UTC), 0, "ETH/USDT"), _trade(datetime.now(UTC), 0, "SOL/USDT")]

    state = CorrelationGuard(min_periods=30).evaluate(
        "BTC/USDT",
        trades,
        lambda pair: close if pair in {"BTC/USDT", "ETH/USDT"} else pd.Series(range(80)),
    )

    assert state.blocked is True
    assert state.reason == "high_correlation"
    assert state.matched_pair == "ETH/USDT"


def test_drawdown_guard_positive_and_negative_paths() -> None:
    now = datetime(2026, 1, 2, tzinfo=UTC)
    trades = [
        _trade(now - timedelta(minutes=3), 10),
        _trade(now - timedelta(minutes=2), -30),
        _trade(now - timedelta(minutes=1), 5),
    ]

    blocked = DrawdownGuard(max_drawdown_ratio=0.2, min_closed_trades=3).evaluate(
        trades, current_equity=85, current_time=now
    )
    allowed = DrawdownGuard(max_drawdown_ratio=0.5, min_closed_trades=3).evaluate(
        trades, current_equity=85, current_time=now
    )

    assert blocked.blocked is True
    assert allowed.blocked is False


def test_drawdown_lookback_uses_explicit_window_start_equity() -> None:
    now = datetime(2026, 1, 2, tzinfo=UTC)
    trades = [
        _trade(now - timedelta(days=3), 100),
        _trade(now - timedelta(hours=3), -20),
        _trade(now - timedelta(hours=2), 5),
        _trade(now - timedelta(hours=1), 5),
    ]

    state = DrawdownGuard(max_drawdown_ratio=0.2, lookback_days=1, min_closed_trades=3).evaluate(
        trades,
        current_equity=90,
        current_time=now,
        starting_equity=100,
    )

    assert state.closed_trades == 3
    assert state.peak_equity == 100
    assert state.trough_equity == 80
    assert state.blocked is True


def test_strategy_passes_drawdown_baseline_at_both_runtime_hooks() -> None:
    root = Path(__file__).resolve().parents[2]
    strategy = (root / "freqtrade/user_data/strategies/KronosFusionStrategy.py").read_text(
        encoding="utf-8"
    )

    assert strategy.count("starting_equity=self._drawdown_starting_equity()") == 2
    assert "RISK_DRAWDOWN_LOOKBACK_DAYS requires" in strategy
