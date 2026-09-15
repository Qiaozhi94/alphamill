import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

try:  # Package import is used by the host service; fallback keeps the legacy CLI usable.
    from .generator import clamp
except ImportError:  # pragma: no cover - direct script compatibility only.
    from generator import clamp

# 上游 from_pretrained 认的权重文件名（Kronos / Tokenizer 目录内二选一）。
WEIGHT_FILE_NAMES = ("model.safetensors", "pytorch_model.bin")

# 数据不足的兜底信号 reason：未进模型，消费端据此不得标 source=kronos（F004-C002）。
NOT_ENOUGH_DATA_REASON = "not_enough_data"


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
        self.kronos_root = os.getenv("KRONOS_REPO_PATH", "vendor/Kronos")
        self.max_context = int(os.getenv("KRONOS_MAX_CONTEXT", "512"))
        self.pred_len = int(os.getenv("KRONOS_PRED_LEN", "12"))
        self.device_request = os.getenv("KRONOS_DEVICE", "cuda")
        self._predictor = None
        self._torch = None
        self._device = "cpu"
        self._load_error: str | None = None
        # 进程级锁：模型加载至多一次 + 推理互斥（spec FR-001 串行推理不变式）。
        self._lock = threading.Lock()

    def preflight(self) -> list[str]:
        """启动预检：返回缺失资产的路径清单，空清单即通过（design §5）。

        校验 vendor clone（以 `model/kronos.py` 存在为准）、模型与分词器目录及
        必需文件（config.json + 权重文件）。
        """
        missing: list[str] = []
        kronos_module = Path(self.kronos_root) / "model" / "kronos.py"
        if not kronos_module.is_file():
            missing.append(str(kronos_module))
        for asset_dir in (Path(self.model_path), Path(self.tokenizer_path)):
            if not asset_dir.is_dir():
                missing.append(str(asset_dir))
                continue
            if not (asset_dir / "config.json").is_file():
                missing.append(str(asset_dir / "config.json"))
            if not any((asset_dir / name).is_file() for name in WEIGHT_FILE_NAMES):
                missing.append(str(asset_dir / WEIGHT_FILE_NAMES[0]))
        return missing

    def eager_load(self) -> None:
        """启动期一次性加载模型，先于接收流量（design §5）。"""
        with self._lock:
            self._load_predictor()

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
        if len(rows) < 30:
            return {
                "signal_type": "neutral",
                "confidence": 0.0,
                "expected_return": 0.0,
                "volatility": 0.0,
                "direction_prob": 0.5,
                "reason": NOT_ENOUGH_DATA_REASON,
            }

        # 进程级锁包住加载与推理：并发请求排队执行，加载至多一次、
        # predictor 无并发进入（spec FR-001 串行推理不变式 / design §5）。
        with self._lock:
            predictor = self._load_predictor()

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
        """加载 Kronos + Tokenizer（调用方须已持有 self._lock，保证至多一次）。"""
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


def real_mode_startup(signal: KronosRealSignal | None = None) -> None:
    """real 模式启动钩子（server lifespan 调用）：预检 → eager load，先于接收流量。

    预检或加载任一失败即打印缺失路径/错误并以非零码退出——失败关闭，绝不退回
    mock（spec FR-001 / design §7：退回会让 AC-006 假绿）。mock 模式为 no-op，
    默认编排行为不变（NFR-001）。
    """
    signal = signal if signal is not None else real_signal
    if not signal.enabled:
        return

    missing = signal.preflight()
    if missing:
        for path in missing:
            print(f"[kronos-real] missing asset: {path}", file=sys.stderr)
        raise SystemExit(
            f"[kronos-real] preflight failed: {len(missing)} asset(s) missing, refusing to start"
        )
    try:
        signal.eager_load()
    except Exception as exc:
        print(f"[kronos-real] model load failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
