from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from pandas import DataFrame


class LightGBMFusionMetaModel:
    """Optional LightGBM meta-model wrapper for signal fusion inference."""

    def __init__(self, model_dir: str | Path, score_scale: float = 0.01) -> None:
        self.model_dir = Path(model_dir)
        self.score_scale = score_scale
        self.feature_columns: list[str] = []
        self.model = None
        self.available = False
        self.load_error: str | None = None
        self._load()

    def predict_score(self, dataframe: DataFrame):
        if not self.available or not self.feature_columns:
            return None

        features = self._feature_frame(dataframe)
        prediction = self.model.predict(features)
        return (prediction / self.score_scale).clip(-1.0, 1.0)

    def _load(self) -> None:
        try:
            import lightgbm as lgb

            metadata_path = self.model_dir / "metadata.json"
            model_path = self.model_dir / "model.txt"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.feature_columns = list(metadata["feature_columns"])
            self.score_scale = float(metadata.get("score_scale", self.score_scale))
            self.model = lgb.Booster(model_file=str(model_path))
            self.available = True
        except Exception as exc:
            self.load_error = str(exc)
            self.available = False

    def _feature_frame(self, dataframe: DataFrame) -> DataFrame:
        frame = DataFrame(index=dataframe.index)
        for column in self.feature_columns:
            if column in dataframe:
                frame[column] = dataframe[column]
            else:
                frame[column] = 0.0
        return frame.replace([float("inf"), float("-inf")], 0.0).fillna(0.0)


def build_meta_feature_frame(
    dataframe: DataFrame, feature_columns: Iterable[str] | None = None
) -> DataFrame:
    frame = DataFrame(index=dataframe.index)
    close = dataframe["close"]
    volume = dataframe["volume"]
    volume_mean = dataframe.get("volume_mean", volume.rolling(24).mean())
    ema_fast = dataframe.get("ema_fast", close.ewm(span=12, adjust=False).mean())
    ema_slow = dataframe.get("ema_slow", close.ewm(span=26, adjust=False).mean())
    momentum = dataframe.get("momentum", close / close.shift(12) - 1)
    atr_pct = dataframe.get(
        "atr_pct", (dataframe["high"] - dataframe["low"]).rolling(14).mean() / close
    )

    frame["ta_score"] = dataframe.get("ta_score", 0.0)
    frame["kronos_score"] = dataframe.get("kronos_score", 0.0)
    frame["freqai_score"] = dataframe.get("freqai_score", 0.0)
    frame["fusion_weighted_score"] = dataframe.get(
        "fusion_weighted_score", dataframe.get("fusion_score", 0.0)
    )
    frame["trend_score"] = (ema_fast / ema_slow - 1).clip(-0.02, 0.02) / 0.02
    frame["momentum_score"] = momentum.clip(-0.03, 0.03) / 0.03
    frame["volume_ratio"] = (volume / volume_mean).clip(0.0, 5.0)
    frame["atr_pct"] = atr_pct.clip(0.0, 0.2)
    frame["return_1"] = close.pct_change(1).clip(-0.05, 0.05)
    frame["return_3"] = close.pct_change(3).clip(-0.08, 0.08)
    frame["return_6"] = close.pct_change(6).clip(-0.12, 0.12)
    frame["volatility_12"] = close.pct_change().rolling(12).std().clip(0.0, 0.1)

    if feature_columns is not None:
        for column in feature_columns:
            if column not in frame:
                frame[column] = 0.0
        frame = frame[list(feature_columns)]

    return frame.replace([float("inf"), float("-inf")], 0.0).fillna(0.0)
