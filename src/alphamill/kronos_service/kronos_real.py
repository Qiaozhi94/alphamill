import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

try:  # Package import is used by the host service; fallback keeps the legacy CLI usable.
    from .generator import clamp
except ImportError:  # pragma: no cover - direct script compatibility only.
    from generator import clamp


@dataclass
class ModelStatus:
    enabled: bool
    available: bool
    loaded: bool
    model: str
    tokenizer: str
    device: str
    error: str | None = None


class KronosRealSignal:
    def __init__(self):
        self.enabled = os.getenv("KRONOS_USE_REAL_MODEL", "false").lower() in {"1", "true", "yes"}
        self.model_path = os.getenv(
            "KRONOS_MODEL_PATH", os.getenv("KRONOS_MODEL", "models/Kronos-base")
        )
        self.tokenizer_path = os.getenv(
            "KRONOS_TOKENIZER_PATH",
            os.getenv("KRONOS_TOKENIZER", "models/Kronos-Tokenizer-base"),
        )
        self.kronos_root = os.getenv("KRONOS_REPO_PATH", "external/Kronos")
        self.max_context = int(os.getenv("KRONOS_MAX_CONTEXT", "512"))
        self.pred_len = int(os.getenv("KRONOS_PRED_LEN", "12"))
        self.device_request = os.getenv("KRONOS_DEVICE", "cuda")
        self._predictor = None
        self._torch = None
        self._device = "cpu"
        self._load_error: str | None = None

    def status(self) -> ModelStatus:
        available = self._dependencies_available()
        return ModelStatus(
            enabled=self.enabled,
            available=available,
            loaded=self._predictor is not None,
            model=self.model_path,
            tokenizer=self.tokenizer_path,
            device=self._device,
            error=self._load_error,
        )

    def generate_signal(self, rows: list[dict]) -> dict:
        predictor = self._load_predictor()
        if len(rows) < 30:
            return {
                "signal_type": "neutral",
                "confidence": 0.0,
                "expected_return": 0.0,
                "volatility": 0.0,
                "direction_prob": 0.5,
                "reason": "not_enough_data",
            }

        df = self._rows_to_df(rows[-self.max_context :])
        x_df = df[["open", "high", "low", "close", "volume"]]
        x_timestamp = df["time"]
        y_timestamp = self._future_timestamps(x_timestamp.iloc[-1], self.pred_len)

        started = time.perf_counter()
        pred_df = predictor.predict(
            df=x_df,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=self.pred_len,
            T=float(os.getenv("KRONOS_TEMPERATURE", "1.0")),
            top_p=float(os.getenv("KRONOS_TOP_P", "0.9")),
            sample_count=int(os.getenv("KRONOS_SAMPLE_COUNT", "1")),
            verbose=False,
        )
        infer_seconds = time.perf_counter() - started

        latest_close = float(x_df["close"].iloc[-1])
        predicted_close = float(pred_df["close"].iloc[-1])
        expected_return = (predicted_close / latest_close) - 1 if latest_close else 0.0
        pred_returns = pred_df["close"].pct_change().dropna().abs()
        volatility = float(pred_returns.mean()) if not pred_returns.empty else abs(expected_return)
        confidence = clamp(abs(expected_return) / max(volatility, 1e-8))
        direction_prob = clamp(0.5 + (expected_return / max(volatility, 1e-8)) * 0.25)

        threshold = float(os.getenv("KRONOS_SIGNAL_THRESHOLD", "0.001"))
        if expected_return > threshold:
            signal_type = "buy"
        elif expected_return < -threshold:
            signal_type = "sell"
        else:
            signal_type = "neutral"

        return {
            "signal_type": signal_type,
            "confidence": round(confidence, 6),
            "expected_return": round(expected_return, 8),
            "volatility": round(volatility, 8),
            "direction_prob": round(direction_prob, 6),
            "reason": f"kronos_base_pred_len_{self.pred_len}_infer_{infer_seconds:.3f}s",
        }

    def _dependencies_available(self) -> bool:
        try:
            import torch  # noqa: F401

            kronos_root = Path(self.kronos_root)
            return kronos_root.exists()
        except Exception:
            return False

    def _load_predictor(self):
        if not self.enabled:
            raise RuntimeError("KRONOS_USE_REAL_MODEL is not enabled")
        if self._predictor is not None:
            return self._predictor

        try:
            kronos_root = Path(self.kronos_root).resolve()
            if str(kronos_root) not in sys.path:
                sys.path.insert(0, str(kronos_root))

            import torch
            from model import Kronos, KronosPredictor, KronosTokenizer

            self._torch = torch
            self._device = (
                "cuda:0"
                if self.device_request.startswith("cuda") and torch.cuda.is_available()
                else "cpu"
            )
            tokenizer = KronosTokenizer.from_pretrained(self.tokenizer_path)
            model = Kronos.from_pretrained(self.model_path)
            self._predictor = KronosPredictor(
                model, tokenizer, device=self._device, max_context=self.max_context
            )
            self._load_error = None
            return self._predictor
        except Exception as exc:
            self._load_error = str(exc)
            raise

    @staticmethod
    def _rows_to_df(rows: list[dict]) -> pd.DataFrame:
        df = pd.DataFrame(rows)
        df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_convert(None)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        return df

    @staticmethod
    def _future_timestamps(last_timestamp: pd.Timestamp, pred_len: int) -> pd.Series:
        start = last_timestamp + pd.Timedelta(minutes=1)
        return pd.Series(pd.date_range(start=start, periods=pred_len, freq="1min"))


real_signal = KronosRealSignal()
