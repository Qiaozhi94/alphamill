from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from pandas import Series


@dataclass(frozen=True)
class CorrelationGuardState:
    blocked: bool
    reason: str
    matched_pair: str | None
    correlation: float


class CorrelationGuard:
    """Blocks new entries that duplicate highly correlated open exposure."""

    def __init__(
        self,
        max_correlation: float = 0.85,
        lookback_candles: int = 72,
        min_periods: int = 30,
    ) -> None:
        self.max_correlation = max_correlation
        self.lookback_candles = lookback_candles
        self.min_periods = min_periods

    def evaluate(
        self,
        pair: str,
        open_trades: Iterable,
        close_series_provider: Callable[[str], Series | None],
    ) -> CorrelationGuardState:
        candidate_returns = self._returns(close_series_provider(pair))
        if candidate_returns is None:
            return CorrelationGuardState(False, "insufficient_candidate_data", None, 0.0)

        for trade in open_trades:
            open_pair = getattr(trade, "pair", None)
            if not open_pair or open_pair == pair:
                continue

            open_returns = self._returns(close_series_provider(open_pair))
            if open_returns is None:
                continue

            correlation = candidate_returns.corr(open_returns)
            if correlation != correlation:
                continue

            if abs(float(correlation)) >= self.max_correlation:
                return CorrelationGuardState(
                    blocked=True,
                    reason="high_correlation",
                    matched_pair=open_pair,
                    correlation=float(correlation),
                )

        return CorrelationGuardState(False, "ok", None, 0.0)

    def _returns(self, close: Series | None) -> Series | None:
        if close is None or len(close) < self.min_periods:
            return None

        returns = close.tail(self.lookback_candles).pct_change().dropna()
        if len(returns) < self.min_periods:
            return None

        return returns
