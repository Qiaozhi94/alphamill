from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class DrawdownGuardState:
    blocked: bool
    reason: str
    max_drawdown_abs: float
    max_drawdown_ratio: float
    peak_equity: float
    trough_equity: float
    closed_trades: int


class DrawdownGuard:
    """Blocks trading once the realized equity curve exceeds max drawdown."""

    def __init__(
        self,
        max_drawdown_ratio: float = 0.20,
        lookback_days: int = 0,
        min_closed_trades: int = 3,
    ) -> None:
        self.max_drawdown_ratio = max_drawdown_ratio
        self.lookback_days = lookback_days
        self.min_closed_trades = min_closed_trades

    def evaluate(
        self,
        closed_trades: Iterable,
        current_equity: float,
        current_time: datetime | None = None,
    ) -> DrawdownGuardState:
        trades = self._closed_trades_in_scope(closed_trades, current_time)
        if current_equity <= 0 or len(trades) < self.min_closed_trades:
            return DrawdownGuardState(
                False, "insufficient_data", 0.0, 0.0, current_equity, current_equity, len(trades)
            )

        realized_profit = sum(self._profit_abs(trade) for trade in trades)
        equity = current_equity - realized_profit
        peak_equity = max(equity, 0.0)
        trough_equity = peak_equity
        max_drawdown_abs = 0.0

        for trade in trades:
            equity += self._profit_abs(trade)
            if equity > peak_equity:
                peak_equity = equity
                trough_equity = equity
                continue

            if equity < trough_equity:
                trough_equity = equity

            drawdown_abs = peak_equity - equity
            if drawdown_abs > max_drawdown_abs:
                max_drawdown_abs = drawdown_abs

        max_drawdown_ratio = max_drawdown_abs / peak_equity if peak_equity > 0 else 0.0
        if self.max_drawdown_ratio > 0 and max_drawdown_ratio >= self.max_drawdown_ratio:
            return DrawdownGuardState(
                True,
                "max_drawdown",
                max_drawdown_abs,
                max_drawdown_ratio,
                peak_equity,
                trough_equity,
                len(trades),
            )

        return DrawdownGuardState(
            False,
            "ok",
            max_drawdown_abs,
            max_drawdown_ratio,
            peak_equity,
            trough_equity,
            len(trades),
        )

    def _closed_trades_in_scope(
        self, closed_trades: Iterable, current_time: datetime | None
    ) -> list:
        trades = [trade for trade in closed_trades if self._closed_at(trade)]
        if self.lookback_days > 0:
            now = self._as_utc(current_time or datetime.now(UTC))
            cutoff = now - timedelta(days=self.lookback_days)
            trades = [trade for trade in trades if self._closed_at(trade) >= cutoff]

        return sorted(trades, key=self._closed_at)

    @staticmethod
    def _closed_at(trade) -> datetime | None:
        closed_at = getattr(trade, "close_date_utc", None) or getattr(trade, "close_date", None)
        if closed_at is None:
            return None
        if closed_at.tzinfo is None:
            return closed_at.replace(tzinfo=UTC)
        return closed_at.astimezone(UTC)

    @staticmethod
    def _profit_abs(trade) -> float:
        value = getattr(trade, "close_profit_abs", None)
        if value is None:
            value = getattr(trade, "realized_profit", 0.0)
        return float(value or 0.0)

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
