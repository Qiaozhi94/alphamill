import os

from KronosFusionStrategy import KronosFusionStrategy


class KronosFusion1hStrategy(KronosFusionStrategy):
    """Low-frequency experiment using hourly candles and timestamped Kronos cache."""

    timeframe = "1h"
    startup_candle_count = 60
    trend_ema_fast_period = int(os.getenv("STRATEGY_1H_TREND_EMA_FAST_PERIOD", "12"))
    trend_ema_slow_period = int(os.getenv("STRATEGY_1H_TREND_EMA_SLOW_PERIOD", "26"))
