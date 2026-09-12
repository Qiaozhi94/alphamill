import logging
import os
from datetime import UTC, datetime, timedelta

import pandas as pd
import requests
from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy
from pandas import DataFrame
from alphamill.freqtrade_bridge.risk.circuit_breaker import CircuitBreaker
from alphamill.freqtrade_bridge.risk.correlation_guard import CorrelationGuard
from alphamill.freqtrade_bridge.risk.drawdown_guard import DrawdownGuard
from signal_fusion.lightgbm_meta import LightGBMFusionMetaModel
from signal_fusion.meta_model import FusionWeights, SignalFusionMetaModel

logger = logging.getLogger(__name__)


class KronosFusionStrategy(IStrategy):
    """Dry-run strategy with optional Kronos signal filtering."""

    INTERFACE_VERSION = 3

    timeframe = "5m"
    can_short = os.getenv("STRATEGY_CAN_SHORT", "false").lower() == "true"

    minimal_roi = {
        "60": 0.0,
        "30": 0.01,
        "0": 0.02,
    }
    stoploss = -0.10
    use_custom_stoploss = True
    startup_candle_count = 60
    process_only_new_candles = True
    kronos_url = os.getenv("KRONOS_SIGNAL_URL", "http://host.docker.internal:8002")
    kronos_timeout = float(os.getenv("KRONOS_SIGNAL_TIMEOUT", "8"))
    kronos_limit = int(os.getenv("KRONOS_SIGNAL_LIMIT", "256"))
    # 数据落库的交易所标签（F001 回填/采集源见 deployment/.env EXCHANGES），默认保持旧行为。
    kronos_exchange = os.getenv("KRONOS_SIGNAL_EXCHANGE", "okx")
    kronos_cache_minutes = int(os.getenv("KRONOS_SIGNAL_CACHE_MINUTES", "5"))
    kronos_disable_live_in_backtest = (
        os.getenv("KRONOS_DISABLE_LIVE_IN_BACKTEST", "true").lower() == "true"
    )
    kronos_historical_signal_path = os.getenv("KRONOS_HISTORICAL_SIGNAL_PATH", "")
    kronos_min_confidence = float(os.getenv("KRONOS_SIGNAL_MIN_CONFIDENCE", "0.55"))
    kronos_min_expected_return = float(os.getenv("KRONOS_SIGNAL_MIN_EXPECTED_RETURN", "0.0005"))
    kronos_min_short_expected_return = float(
        os.getenv("KRONOS_SIGNAL_MIN_SHORT_EXPECTED_RETURN", "-0.0005")
    )
    entry_long_enabled = os.getenv("STRATEGY_ENTRY_LONG_ENABLED", "true").lower() == "true"
    entry_short_enabled = os.getenv("STRATEGY_ENTRY_SHORT_ENABLED", "true").lower() == "true"
    freqai_min_expected_return = float(os.getenv("FREQAI_MIN_EXPECTED_RETURN", "0.002"))
    atr_period = int(os.getenv("STRATEGY_ATR_PERIOD", "14"))
    stoploss_atr_multiplier = float(os.getenv("STRATEGY_STOPLOSS_ATR_MULTIPLIER", "2.5"))
    min_dynamic_stoploss = float(os.getenv("STRATEGY_MIN_DYNAMIC_STOPLOSS", "0.025"))
    max_dynamic_stoploss = float(os.getenv("STRATEGY_MAX_DYNAMIC_STOPLOSS", "0.10"))
    max_entry_volatility = float(os.getenv("STRATEGY_MAX_ENTRY_VOLATILITY", "0.08"))
    trend_filter_enabled = os.getenv("STRATEGY_TREND_FILTER_ENABLED", "false").lower() == "true"
    trend_ema_fast_period = int(os.getenv("STRATEGY_TREND_EMA_FAST_PERIOD", "144"))
    trend_ema_slow_period = int(os.getenv("STRATEGY_TREND_EMA_SLOW_PERIOD", "312"))
    exit_momentum_threshold = float(os.getenv("STRATEGY_EXIT_MOMENTUM_THRESHOLD", "-0.02"))
    exit_on_ema_reversal = os.getenv("STRATEGY_EXIT_ON_EMA_REVERSAL", "true").lower() == "true"
    exit_on_fusion_sell = os.getenv("STRATEGY_EXIT_ON_FUSION_SELL", "true").lower() == "true"
    exit_min_hold_minutes = int(os.getenv("STRATEGY_EXIT_MIN_HOLD_MINUTES", "0"))
    exit_strong_confirmation_enabled = (
        os.getenv("STRATEGY_EXIT_STRONG_CONFIRMATION_ENABLED", "false").lower() == "true"
    )
    exit_confirmation_min_count = int(os.getenv("STRATEGY_EXIT_CONFIRMATION_MIN_COUNT", "2"))
    exit_kronos_expected_return_threshold = float(
        os.getenv("STRATEGY_EXIT_KRONOS_EXPECTED_RETURN_THRESHOLD", "-0.001")
    )
    exit_profit_guard_enabled = (
        os.getenv("STRATEGY_EXIT_PROFIT_GUARD_ENABLED", "false").lower() == "true"
    )
    exit_min_profit_ratio = float(os.getenv("STRATEGY_EXIT_MIN_PROFIT_RATIO", "0.0"))
    exit_max_hold_minutes = int(os.getenv("STRATEGY_EXIT_MAX_HOLD_MINUTES", "0"))
    fusion_buy_threshold = float(os.getenv("FUSION_BUY_THRESHOLD", "0.35"))
    fusion_sell_threshold = float(os.getenv("FUSION_SELL_THRESHOLD", "-0.25"))
    fusion_ta_weight = float(os.getenv("FUSION_TA_WEIGHT", "0.30"))
    fusion_kronos_weight = float(os.getenv("FUSION_KRONOS_WEIGHT", "0.45"))
    fusion_freqai_weight = float(os.getenv("FUSION_FREQAI_WEIGHT", "0.25"))
    fusion_meta_model_enabled = os.getenv("FUSION_META_MODEL_ENABLED", "false").lower() == "true"
    fusion_meta_model_path = os.getenv(
        "FUSION_META_MODEL_PATH", "/freqtrade/user_data/models/fusion_meta/latest"
    )
    fusion_meta_model_blend = float(os.getenv("FUSION_META_MODEL_BLEND", "0.35"))
    max_daily_loss_ratio = float(os.getenv("RISK_MAX_DAILY_LOSS_RATIO", "0.03"))
    max_daily_loss_abs = float(os.getenv("RISK_MAX_DAILY_LOSS_ABS", "0"))
    max_consecutive_losses = int(os.getenv("RISK_MAX_CONSECUTIVE_LOSSES", "3"))
    consecutive_loss_cooldown_hours = float(os.getenv("RISK_CONSECUTIVE_LOSS_COOLDOWN_HOURS", "24"))
    max_pair_correlation = float(os.getenv("RISK_MAX_PAIR_CORRELATION", "0.85"))
    correlation_lookback_candles = int(os.getenv("RISK_CORRELATION_LOOKBACK_CANDLES", "72"))
    correlation_min_periods = int(os.getenv("RISK_CORRELATION_MIN_PERIODS", "30"))
    max_drawdown_ratio = float(os.getenv("RISK_MAX_DRAWDOWN_RATIO", "0.20"))
    drawdown_lookback_days = int(os.getenv("RISK_DRAWDOWN_LOOKBACK_DAYS", "0"))
    drawdown_min_closed_trades = int(os.getenv("RISK_DRAWDOWN_MIN_CLOSED_TRADES", "3"))

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._kronos_cache: dict[str, tuple[datetime, dict]] = {}
        self._historical_signal_cache: dict[str, DataFrame] | None = None
        fusion_weights = FusionWeights(
            ta=self.fusion_ta_weight,
            kronos=self.fusion_kronos_weight,
            freqai=self.fusion_freqai_weight,
        )
        if any(
            os.getenv(name) is not None
            for name in ("FUSION_TA_IC", "FUSION_KRONOS_IC", "FUSION_FREQAI_IC")
        ):
            fusion_weights = FusionWeights.from_rank_ic_scores(
                ta_ic=self._optional_float_env("FUSION_TA_IC"),
                kronos_ic=self._optional_float_env("FUSION_KRONOS_IC"),
                freqai_ic=self._optional_float_env("FUSION_FREQAI_IC"),
            )
        learned_model = None
        if self.fusion_meta_model_enabled:
            learned_model = LightGBMFusionMetaModel(self.fusion_meta_model_path)
            if learned_model.available:
                logger.info(
                    "Loaded fusion LightGBM meta-model from %s", self.fusion_meta_model_path
                )
            else:
                logger.warning(
                    "Fusion LightGBM meta-model unavailable path=%s error=%s",
                    self.fusion_meta_model_path,
                    learned_model.load_error,
                )
        self._signal_fusion = SignalFusionMetaModel(
            weights=fusion_weights,
            buy_threshold=self.fusion_buy_threshold,
            sell_threshold=self.fusion_sell_threshold,
            learned_model=learned_model,
            learned_model_blend=self.fusion_meta_model_blend,
        )
        self._circuit_breaker = CircuitBreaker(
            max_daily_loss_ratio=self.max_daily_loss_ratio,
            max_daily_loss_abs=self.max_daily_loss_abs,
            max_consecutive_losses=self.max_consecutive_losses,
            consecutive_loss_cooldown_hours=self.consecutive_loss_cooldown_hours,
        )
        self._correlation_guard = CorrelationGuard(
            max_correlation=self.max_pair_correlation,
            lookback_candles=self.correlation_lookback_candles,
            min_periods=self.correlation_min_periods,
        )
        self._drawdown_guard = DrawdownGuard(
            max_drawdown_ratio=self.max_drawdown_ratio,
            lookback_days=self.drawdown_lookback_days,
            min_closed_trades=self.drawdown_min_closed_trades,
        )

    @staticmethod
    def _optional_float_env(name: str) -> float | None:
        value = os.getenv(name)
        if value is None or value == "":
            return None
        return float(value)

    def feature_engineering_expand_all(
        self, dataframe: DataFrame, period: int, metadata: dict, **kwargs
    ) -> DataFrame:
        dataframe["%-return-period"] = dataframe["close"].pct_change(period)
        dataframe["%-volume-ratio-period"] = (
            dataframe["volume"] / dataframe["volume"].rolling(period).mean()
        )
        dataframe["%-ema-ratio-period"] = (
            dataframe["close"].ewm(span=period, adjust=False).mean() / dataframe["close"] - 1
        )
        dataframe["%-range-pct-period"] = (dataframe["high"] - dataframe["low"]) / dataframe[
            "close"
        ]
        dataframe["%-volatility-period"] = dataframe["close"].pct_change().rolling(period).std()
        return dataframe

    def feature_engineering_expand_basic(
        self, dataframe: DataFrame, metadata: dict, **kwargs
    ) -> DataFrame:
        dataframe["%-pct-change"] = dataframe["close"].pct_change()
        dataframe["%-raw-volume"] = dataframe["volume"]
        dataframe["%-raw-close"] = dataframe["close"]
        dataframe["%-candle-body"] = (dataframe["close"] - dataframe["open"]) / dataframe["open"]
        dataframe["%-upper-shadow"] = (
            dataframe["high"] - dataframe[["open", "close"]].max(axis=1)
        ) / dataframe["close"]
        dataframe["%-lower-shadow"] = (
            dataframe[["open", "close"]].min(axis=1) - dataframe["low"]
        ) / dataframe["close"]
        return dataframe

    def feature_engineering_standard(
        self, dataframe: DataFrame, metadata: dict, **kwargs
    ) -> DataFrame:
        dataframe["%-day-of-week"] = dataframe["date"].dt.dayofweek
        dataframe["%-hour-of-day"] = dataframe["date"].dt.hour
        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        label_period = self.freqai_info["feature_parameters"]["label_period_candles"]
        dataframe["&-future_return"] = (
            dataframe["close"].shift(-label_period).rolling(label_period).mean()
            / dataframe["close"]
            - 1
        )
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if self.config.get("freqai", {}).get("enabled", False):
            dataframe = self.freqai.start(dataframe, metadata, self)

        dataframe["ema_fast"] = dataframe["close"].ewm(span=12, adjust=False).mean()
        dataframe["ema_slow"] = dataframe["close"].ewm(span=26, adjust=False).mean()
        dataframe["trend_ema_fast"] = (
            dataframe["close"].ewm(span=self.trend_ema_fast_period, adjust=False).mean()
        )
        dataframe["trend_ema_slow"] = (
            dataframe["close"].ewm(span=self.trend_ema_slow_period, adjust=False).mean()
        )
        dataframe["trend_long_ok"] = dataframe["trend_ema_fast"] > dataframe["trend_ema_slow"]
        dataframe["trend_short_ok"] = dataframe["trend_ema_fast"] < dataframe["trend_ema_slow"]
        dataframe["volume_mean"] = dataframe["volume"].rolling(24).mean()
        dataframe["momentum"] = dataframe["close"] / dataframe["close"].shift(12) - 1
        previous_close = dataframe["close"].shift(1)
        true_range = DataFrame(
            {
                "high_low": dataframe["high"] - dataframe["low"],
                "high_close": (dataframe["high"] - previous_close).abs(),
                "low_close": (dataframe["low"] - previous_close).abs(),
            }
        ).max(axis=1)
        dataframe["atr"] = true_range.rolling(self.atr_period).mean()
        dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"]
        historical_signals = self._historical_signals_for_pair(metadata["pair"])
        if self._is_backtesting_runmode() and historical_signals is not None:
            dataframe = self._merge_historical_signals(dataframe, historical_signals)
        else:
            signal = self._get_kronos_signal(metadata["pair"])
            dataframe["kronos_signal"] = signal["signal_type"]
            dataframe["kronos_confidence"] = signal["confidence"]
            dataframe["kronos_expected_return"] = signal["expected_return"]
            dataframe["kronos_direction_prob"] = signal["direction_prob"]
        dataframe = self._signal_fusion.add_signal_columns(dataframe)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        trend_long_ok = dataframe["trend_long_ok"] if self.trend_filter_enabled else True
        if self.entry_long_enabled:
            dataframe.loc[
                (
                    (dataframe["ema_fast"] > dataframe["ema_slow"])
                    & (dataframe["momentum"] > 0)
                    & (dataframe["volume"] > dataframe["volume_mean"])
                    & (dataframe["volume"] > 0)
                    & (dataframe["kronos_expected_return"] >= self.kronos_min_expected_return)
                    & (dataframe["fusion_signal"] == "buy")
                    & trend_long_ok
                ),
                "enter_long",
            ] = 1
        if self.can_short and self.entry_short_enabled:
            trend_short_ok = dataframe["trend_short_ok"] if self.trend_filter_enabled else True
            dataframe.loc[
                (
                    (dataframe["ema_fast"] < dataframe["ema_slow"])
                    & (dataframe["momentum"] < 0)
                    & (dataframe["volume"] > dataframe["volume_mean"])
                    & (dataframe["volume"] > 0)
                    & (dataframe["kronos_expected_return"] <= self.kronos_min_short_expected_return)
                    & (dataframe["fusion_signal"] == "sell")
                    & trend_short_ok
                ),
                "enter_short",
            ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        momentum_exit = dataframe["momentum"] < self.exit_momentum_threshold
        ema_exit = dataframe["ema_fast"] < dataframe["ema_slow"]
        fusion_exit = dataframe["fusion_signal"] == "sell"
        exit_long = momentum_exit
        if self.exit_on_ema_reversal:
            exit_long = exit_long | ema_exit
        if self.exit_on_fusion_sell:
            exit_long = exit_long | fusion_exit
        if self.exit_strong_confirmation_enabled:
            confirmation_count = momentum_exit.astype(int)
            if self.exit_on_ema_reversal:
                confirmation_count = confirmation_count + ema_exit.astype(int)
            if self.exit_on_fusion_sell:
                confirmation_count = confirmation_count + fusion_exit.astype(int)
            exit_long = (confirmation_count >= self.exit_confirmation_min_count) & (
                dataframe["kronos_expected_return"] <= self.exit_kronos_expected_return_threshold
            )
        dataframe["exit_long_candidate"] = exit_long & (dataframe["volume"] > 0)
        if self.exit_min_hold_minutes <= 0 and not self.exit_profit_guard_enabled:
            dataframe.loc[dataframe["exit_long_candidate"], "exit_long"] = 1
        if self.can_short:
            dataframe["exit_short_candidate"] = (
                (dataframe["ema_fast"] > dataframe["ema_slow"])
                | (dataframe["momentum"] > 0.02)
                | (dataframe["fusion_signal"] == "buy")
            ) & (dataframe["volume"] > 0)
            if self.exit_min_hold_minutes <= 0 and not self.exit_profit_guard_enabled:
                dataframe.loc[dataframe["exit_short_candidate"], "exit_short"] = 1
        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> float:
        if not self.dp:
            return self.stoploss

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty or "atr_pct" not in dataframe:
            return self.stoploss

        atr_pct = dataframe.iloc[-1]["atr_pct"]
        if atr_pct != atr_pct or atr_pct <= 0:
            return self.stoploss

        dynamic_stop = atr_pct * self.stoploss_atr_multiplier
        dynamic_stop = max(self.min_dynamic_stoploss, min(self.max_dynamic_stoploss, dynamic_stop))

        if current_profit > dynamic_stop * 2:
            dynamic_stop = max(self.min_dynamic_stoploss, dynamic_stop * 0.75)

        return -dynamic_stop

    def custom_exit(
        self,
        pair: str,
        trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ):
        drawdown_state = self._drawdown_guard.evaluate(
            Trade.get_trades_proxy(is_open=False),
            current_equity=self._current_equity(),
            current_time=current_time,
        )
        if drawdown_state.blocked:
            logger.warning(
                "Exit forced by drawdown guard pair=%s reason=%s max_drawdown_abs=%.4f "
                "max_drawdown_ratio=%.4f peak_equity=%.4f trough_equity=%.4f closed_trades=%s",
                pair,
                drawdown_state.reason,
                drawdown_state.max_drawdown_abs,
                drawdown_state.max_drawdown_ratio,
                drawdown_state.peak_equity,
                drawdown_state.trough_equity,
                drawdown_state.closed_trades,
            )
            return "max_drawdown_stop"

        if self.exit_profit_guard_enabled and self.dp:
            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if not dataframe.empty:
                last = dataframe.iloc[-1]
                column = (
                    "exit_short_candidate"
                    if getattr(trade, "is_short", False)
                    else "exit_long_candidate"
                )
                if bool(last.get(column, False)) and current_profit >= self.exit_min_profit_ratio:
                    return "profit_protected_exit_signal"

        if self.exit_max_hold_minutes > 0:
            open_time = getattr(trade, "open_date_utc", None) or getattr(trade, "open_date", None)
            if open_time is not None:
                if open_time.tzinfo is None:
                    open_time = open_time.replace(tzinfo=UTC)
                held_minutes = (
                    current_time.astimezone(UTC) - open_time.astimezone(UTC)
                ).total_seconds() / 60
                if held_minutes >= self.exit_max_hold_minutes:
                    return "timed_exit"

        if self.exit_min_hold_minutes > 0 and not self.exit_profit_guard_enabled and self.dp:
            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if not dataframe.empty:
                last = dataframe.iloc[-1]
                open_time = getattr(trade, "open_date_utc", None) or getattr(
                    trade, "open_date", None
                )
                if open_time is not None:
                    if open_time.tzinfo is None:
                        open_time = open_time.replace(tzinfo=UTC)
                    held_minutes = (
                        current_time.astimezone(UTC) - open_time.astimezone(UTC)
                    ).total_seconds() / 60
                    if held_minutes >= self.exit_min_hold_minutes:
                        column = (
                            "exit_short_candidate"
                            if getattr(trade, "is_short", False)
                            else "exit_long_candidate"
                        )
                        if bool(last.get(column, False)):
                            return "delayed_exit_signal"

        return None

    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time: datetime,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> bool:
        if side not in ("long", "short"):
            return False
        if side == "short" and not self.can_short:
            return False

        breaker_state = self._circuit_breaker.evaluate(
            Trade.get_trades_proxy(is_open=False),
            equity=self._current_equity(),
            current_time=current_time,
        )
        if breaker_state.blocked:
            logger.warning(
                "Entry blocked by circuit breaker pair=%s reason=%s daily_profit_abs=%.4f "
                "daily_profit_ratio=%.4f consecutive_losses=%s",
                pair,
                breaker_state.reason,
                breaker_state.daily_profit_abs,
                breaker_state.daily_profit_ratio,
                breaker_state.consecutive_losses,
            )
            return False

        drawdown_state = self._drawdown_guard.evaluate(
            Trade.get_trades_proxy(is_open=False),
            current_equity=self._current_equity(),
            current_time=current_time,
        )
        if drawdown_state.blocked:
            logger.warning(
                "Entry blocked by drawdown guard pair=%s reason=%s max_drawdown_abs=%.4f "
                "max_drawdown_ratio=%.4f peak_equity=%.4f trough_equity=%.4f closed_trades=%s",
                pair,
                drawdown_state.reason,
                drawdown_state.max_drawdown_abs,
                drawdown_state.max_drawdown_ratio,
                drawdown_state.peak_equity,
                drawdown_state.trough_equity,
                drawdown_state.closed_trades,
            )
            return False

        correlation_state = self._correlation_guard.evaluate(
            pair,
            Trade.get_trades_proxy(is_open=True),
            self._close_series_for_pair,
        )
        if correlation_state.blocked:
            logger.info(
                "Entry blocked by correlation guard pair=%s matched_pair=%s correlation=%.4f",
                pair,
                correlation_state.matched_pair,
                correlation_state.correlation,
            )
            return False

        signal = self._get_kronos_signal(pair)
        if (
            side == "long"
            and signal["signal_type"] == "sell"
            and signal["confidence"] >= self.kronos_min_confidence
        ):
            logger.info("Entry blocked by Kronos sell signal pair=%s signal=%s", pair, signal)
            return False

        if (
            side == "short"
            and signal["signal_type"] == "buy"
            and signal["confidence"] >= self.kronos_min_confidence
        ):
            logger.info("Short entry blocked by Kronos buy signal pair=%s signal=%s", pair, signal)
            return False

        if (
            side == "long"
            and signal["signal_type"] == "buy"
            and signal["confidence"] < self.kronos_min_confidence
            and signal["expected_return"] < self.kronos_min_expected_return
        ):
            logger.info("Entry blocked by weak Kronos buy signal pair=%s signal=%s", pair, signal)
            return False

        if (
            side == "short"
            and signal["signal_type"] == "sell"
            and signal["confidence"] < self.kronos_min_confidence
            and signal["expected_return"] > self.kronos_min_short_expected_return
        ):
            logger.info(
                "Short entry blocked by weak Kronos sell signal pair=%s signal=%s", pair, signal
            )
            return False

        if self.dp:
            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if not dataframe.empty and "atr_pct" in dataframe:
                atr_pct = dataframe.iloc[-1]["atr_pct"]
                if atr_pct == atr_pct and atr_pct > self.max_entry_volatility:
                    logger.info(
                        "Entry blocked by high volatility pair=%s atr_pct=%.4f max=%.4f",
                        pair,
                        atr_pct,
                        self.max_entry_volatility,
                    )
                    return False

        return True

    def _current_equity(self) -> float:
        try:
            return float(self.wallets.get_total_stake_amount())
        except Exception:
            return float(
                self.config.get("dry_run_wallet") or self.config.get("stake_amount") or 0.0
            )

    def _close_series_for_pair(self, pair: str):
        if not self.dp:
            return None

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty or "close" not in dataframe:
            return None

        return dataframe["close"]

    def _get_kronos_signal(self, pair: str) -> dict:
        now = datetime.now(UTC)
        signal_pair = self._spot_pair(pair)
        fallback = {
            "signal_type": "neutral",
            "confidence": 0.0,
            "expected_return": 0.0,
            "direction_prob": 0.5,
        }
        if self.kronos_disable_live_in_backtest and self._is_backtesting_runmode():
            return fallback

        cached = self._kronos_cache.get(signal_pair)
        if cached and now - cached[0] < timedelta(minutes=self.kronos_cache_minutes):
            return cached[1]

        try:
            response = requests.get(
                f"{self.kronos_url.rstrip('/')}/predict/{signal_pair}",
                params={"exchange": self.kronos_exchange, "limit": self.kronos_limit},
                timeout=self.kronos_timeout,
            )
            response.raise_for_status()
            payload = response.json()
            signal = {
                "signal_type": payload.get("signal_type", "neutral"),
                "confidence": float(payload.get("confidence", 0.0)),
                "expected_return": float(payload.get("expected_return", 0.0)),
                "direction_prob": float(payload.get("direction_prob", 0.5)),
            }
            logger.info(
                "Kronos signal pair=%s signal=%s confidence=%.4f expected_return=%.6f",
                signal_pair,
                signal["signal_type"],
                signal["confidence"],
                signal["expected_return"],
            )
        except Exception as exc:
            logger.warning("Kronos signal unavailable pair=%s error=%s", signal_pair, exc)
            signal = fallback

        self._kronos_cache[signal_pair] = (now, signal)
        return signal

    @staticmethod
    def _spot_pair(pair: str) -> str:
        return pair.split(":", 1)[0]

    def _is_backtesting_runmode(self) -> bool:
        runmode = self.config.get("runmode")
        value = getattr(runmode, "value", runmode)
        return str(value).lower() in {"backtest", "backtesting", "hyperopt"}

    def _historical_signals_for_pair(self, pair: str):
        if not self.kronos_historical_signal_path:
            return None
        if self._historical_signal_cache is None:
            self._historical_signal_cache = self._load_historical_signal_cache()
        return self._historical_signal_cache.get(self._spot_pair(pair))

    def _load_historical_signal_cache(self) -> dict[str, DataFrame]:
        path = self.kronos_historical_signal_path
        files = []
        if os.path.isdir(path):
            files = [
                os.path.join(path, name)
                for name in os.listdir(path)
                if name.endswith((".feather", ".csv"))
            ]
        elif os.path.exists(path):
            files = [path]
        else:
            logger.warning("Historical Kronos signal path does not exist: %s", path)
            return {}

        frames = []
        for file_path in files:
            try:
                if file_path.endswith(".csv"):
                    frames.append(pd.read_csv(file_path))
                else:
                    frames.append(pd.read_feather(file_path))
            except Exception as exc:
                logger.warning(
                    "Failed loading historical Kronos signals path=%s error=%s", file_path, exc
                )
        if not frames:
            return {}

        data = pd.concat(frames, ignore_index=True)
        data["date"] = pd.to_datetime(data["date"], utc=True).dt.tz_localize(None)
        data["pair"] = data["pair"].map(self._spot_pair)
        data = data.drop_duplicates(subset=["date", "pair"], keep="last")
        grouped = {
            pair_name: group.sort_values("date").reset_index(drop=True)
            for pair_name, group in data.groupby("pair")
        }
        logger.info(
            "Loaded historical Kronos signal cache path=%s rows=%s pairs=%s",
            path,
            len(data),
            sorted(grouped),
        )
        return grouped

    @staticmethod
    def _merge_historical_signals(dataframe: DataFrame, signals: DataFrame) -> DataFrame:
        work = dataframe.copy()
        work["_kronos_date"] = pd.to_datetime(work["date"], utc=True).dt.tz_localize(None)
        signal_cols = [
            "date",
            "kronos_signal",
            "kronos_confidence",
            "kronos_expected_return",
            "kronos_direction_prob",
        ]
        merged = work.merge(
            signals[signal_cols],
            how="left",
            left_on="_kronos_date",
            right_on="date",
            suffixes=("", "_kronos_cache"),
        )
        if "date_kronos_cache" in merged:
            merged = merged.drop(columns=["date_kronos_cache"])
        merged = merged.drop(columns=["_kronos_date"])
        merged["kronos_signal"] = merged["kronos_signal"].fillna("neutral")
        merged["kronos_confidence"] = merged["kronos_confidence"].fillna(0.0)
        merged["kronos_expected_return"] = merged["kronos_expected_return"].fillna(0.0)
        merged["kronos_direction_prob"] = merged["kronos_direction_prob"].fillna(0.5)
        return merged
