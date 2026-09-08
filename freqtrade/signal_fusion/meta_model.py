from __future__ import annotations

from dataclasses import dataclass

from pandas import DataFrame

from .lightgbm_meta import LightGBMFusionMetaModel, build_meta_feature_frame


@dataclass(frozen=True)
class FusionWeights:
    ta: float = 0.30
    kronos: float = 0.45
    freqai: float = 0.25

    def normalized(self) -> FusionWeights:
        total = self.ta + self.kronos + self.freqai
        if total <= 0:
            return FusionWeights()

        return FusionWeights(
            ta=self.ta / total,
            kronos=self.kronos / total,
            freqai=self.freqai / total,
        )

    @classmethod
    def from_rank_ic_scores(
        cls,
        ta_ic: float | None = None,
        kronos_ic: float | None = None,
        freqai_ic: float | None = None,
        floor: float = 0.05,
    ) -> FusionWeights:
        scores = {
            "ta": max(floor, abs(ta_ic or 0.0)),
            "kronos": max(floor, abs(kronos_ic or 0.0)),
            "freqai": max(floor, abs(freqai_ic or 0.0)),
        }
        return cls(
            ta=scores["ta"],
            kronos=scores["kronos"],
            freqai=scores["freqai"],
        ).normalized()


class SignalFusionMetaModel:
    """
    Lightweight signal fusion layer.

    It turns TA, Kronos, and FreqAI outputs into comparable [-1, 1] scores,
    then emits a unified weighted score and buy/sell/neutral label. The class is
    intentionally deterministic so it is safe for dry-run and backtesting.
    """

    def __init__(
        self,
        weights: FusionWeights | None = None,
        buy_threshold: float = 0.35,
        sell_threshold: float = -0.25,
        expected_return_scale: float = 0.01,
        freqai_return_scale: float = 0.01,
        learned_model: LightGBMFusionMetaModel | None = None,
        learned_model_blend: float = 0.0,
    ) -> None:
        self.weights = (weights or FusionWeights()).normalized()
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.expected_return_scale = expected_return_scale
        self.freqai_return_scale = freqai_return_scale
        self.learned_model = learned_model
        self.learned_model_blend = max(0.0, min(1.0, learned_model_blend))

    def add_signal_columns(self, dataframe: DataFrame) -> DataFrame:
        dataframe["ta_score"] = self._ta_score(dataframe)
        dataframe["kronos_score"] = self._kronos_score(dataframe)
        dataframe["freqai_score"] = self._freqai_score(dataframe)
        dataframe["fusion_weighted_score"] = (
            dataframe["ta_score"] * self.weights.ta
            + dataframe["kronos_score"] * self.weights.kronos
            + dataframe["freqai_score"] * self.weights.freqai
        ).clip(-1.0, 1.0)
        dataframe["fusion_meta_score"] = 0.0
        dataframe["fusion_score"] = dataframe["fusion_weighted_score"]

        if self.learned_model and self.learned_model.available and self.learned_model_blend > 0:
            meta_score = self.learned_model.predict_score(dataframe)
            if meta_score is not None:
                dataframe["fusion_meta_score"] = meta_score
                dataframe["fusion_score"] = (
                    dataframe["fusion_weighted_score"] * (1.0 - self.learned_model_blend)
                    + dataframe["fusion_meta_score"] * self.learned_model_blend
                ).clip(-1.0, 1.0)

        dataframe["fusion_signal"] = "neutral"
        dataframe.loc[dataframe["fusion_score"] >= self.buy_threshold, "fusion_signal"] = "buy"
        dataframe.loc[dataframe["fusion_score"] <= self.sell_threshold, "fusion_signal"] = "sell"
        return dataframe

    def meta_feature_frame(self, dataframe: DataFrame) -> DataFrame:
        return build_meta_feature_frame(dataframe)

    def _ta_score(self, dataframe: DataFrame):
        trend = (dataframe["ema_fast"] / dataframe["ema_slow"] - 1).clip(-0.02, 0.02) / 0.02
        momentum = dataframe["momentum"].clip(-0.03, 0.03) / 0.03
        volume_ok = (dataframe["volume"] > dataframe["volume_mean"]).astype(float)
        volume_score = volume_ok.where(volume_ok == 1.0, -0.2)
        return (trend * 0.45 + momentum * 0.40 + volume_score * 0.15).clip(-1.0, 1.0)

    def _kronos_score(self, dataframe: DataFrame):
        signal_bias = dataframe["kronos_signal"].map({"buy": 1.0, "sell": -1.0}).fillna(0.0)
        confidence = dataframe["kronos_confidence"].clip(0.0, 1.0)
        expected = (
            dataframe["kronos_expected_return"].clip(
                -self.expected_return_scale,
                self.expected_return_scale,
            )
            / self.expected_return_scale
        )
        direction = ((dataframe["kronos_direction_prob"].clip(0.0, 1.0) - 0.5) * 2.0).fillna(0.0)
        return (signal_bias * confidence * 0.45 + expected * 0.40 + direction * 0.15).clip(
            -1.0, 1.0
        )

    def _freqai_score(self, dataframe: DataFrame):
        if "do_predict" not in dataframe or "&-future_return" not in dataframe:
            return 0.0

        prediction_ok = (dataframe["do_predict"] == 1).astype(float)
        predicted_return = (
            dataframe["&-future_return"].clip(
                -self.freqai_return_scale,
                self.freqai_return_scale,
            )
            / self.freqai_return_scale
        )
        return (predicted_return * prediction_ok).clip(-1.0, 1.0)
