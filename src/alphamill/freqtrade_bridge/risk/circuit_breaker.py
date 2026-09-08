from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta


@dataclass(frozen=True)
class CircuitBreakerState:
    blocked: bool
    reason: str
    daily_profit_abs: float
    daily_profit_ratio: float
    consecutive_losses: int


class CircuitBreaker:
    """Daily loss and losing-streak entry gate."""

    def __init__(
        self,
        max_daily_loss_ratio: float = 0.03,
        max_daily_loss_abs: float = 0.0,
        max_consecutive_losses: int = 3,
        consecutive_loss_cooldown_hours: float = 24.0,
    ) -> None:
        self.max_daily_loss_ratio = max_daily_loss_ratio
        self.max_daily_loss_abs = max_daily_loss_abs
        self.max_consecutive_losses = max_consecutive_losses
        self.consecutive_loss_cooldown_hours = consecutive_loss_cooldown_hours

    def evaluate(
        self,
        closed_trades: Iterable,
        equity: float,
        current_time: datetime | None = None,
    ) -> CircuitBreakerState:
        now = self._as_utc(current_time or datetime.now(UTC))
        today_start = datetime.combine(now.date(), time.min, tzinfo=UTC)
        todays_trades = [
            trade
            for trade in closed_trades
            if self._closed_at(trade) and self._closed_at(trade) >= today_start
        ]
        daily_profit_abs = sum(self._profit_abs(trade) for trade in todays_trades)
        daily_profit_ratio = daily_profit_abs / equity if equity > 0 else 0.0
        consecutive_losses = self._count_consecutive_losses(closed_trades, now)

        if self.max_daily_loss_abs > 0 and daily_profit_abs <= -self.max_daily_loss_abs:
            return CircuitBreakerState(
                blocked=True,
                reason="daily_loss_abs",
                daily_profit_abs=daily_profit_abs,
                daily_profit_ratio=daily_profit_ratio,
                consecutive_losses=consecutive_losses,
            )

        if self.max_daily_loss_ratio > 0 and daily_profit_ratio <= -self.max_daily_loss_ratio:
            return CircuitBreakerState(
                blocked=True,
                reason="daily_loss_ratio",
                daily_profit_abs=daily_profit_abs,
                daily_profit_ratio=daily_profit_ratio,
                consecutive_losses=consecutive_losses,
            )

        if self.max_consecutive_losses > 0 and consecutive_losses >= self.max_consecutive_losses:
            return CircuitBreakerState(
                blocked=True,
                reason="consecutive_losses",
                daily_profit_abs=daily_profit_abs,
                daily_profit_ratio=daily_profit_ratio,
                consecutive_losses=consecutive_losses,
            )

        return CircuitBreakerState(
            blocked=False,
            reason="ok",
            daily_profit_abs=daily_profit_abs,
            daily_profit_ratio=daily_profit_ratio,
            consecutive_losses=consecutive_losses,
        )

    def _count_consecutive_losses(self, closed_trades: Iterable, now: datetime) -> int:
        losses = 0
        cooldown_start = (
            now - timedelta(hours=self.consecutive_loss_cooldown_hours)
            if self.consecutive_loss_cooldown_hours > 0
            else None
        )
        ordered = sorted(
            [trade for trade in closed_trades if self._closed_at(trade)],
            key=self._closed_at,
            reverse=True,
        )
        for trade in ordered:
            if cooldown_start and self._closed_at(trade) < cooldown_start:
                break
            if self._profit_abs(trade) < 0:
                losses += 1
                continue
            break
        return losses

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
