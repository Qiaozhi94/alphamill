import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

try:  # Package import is used by the host service; fallback keeps the legacy CLI usable.
    from .generator import clamp, generate_placeholder_signal
    from .lifecycle import UnloadFailed
except ImportError:  # pragma: no cover - direct script compatibility only.
    from generator import clamp, generate_placeholder_signal
    from lifecycle import UnloadFailed

# 上游 from_pretrained 认的权重文件名（Kronos / Tokenizer 目录内二选一）。
WEIGHT_FILE_NAMES = ("model.safetensors", "pytorch_model.bin")

# 数据不足的兜底信号 reason：未进模型，消费端据此不得标 source=kronos（F004-C002）。
NOT_ENOUGH_DATA_REASON = "not_enough_data"

# 显式 KRONOS_DEVICE 拿不到对应设备时的失败文案（F010 FR-004）：docker logs 可检索。
ERR_CPU_WHEEL = "torch is a CPU wheel (torch.version.cuda is empty)"
ERR_NO_CUDA_DEVICE = "no CUDA device visible in container (torch.cuda.is_available() is False)"
ERR_UNKNOWN_DEVICE = "unsupported KRONOS_DEVICE value"

# desired=stopped 期间的兜底信号 reason（F009 FR-003）：未进模型，消费端不得标 kronos。
LIFECYCLE_STOPPED_REASON = "lifecycle_stopped"

# 未进模型的全部 reason：/predict 据此拒绝标注 kronos 与权重路径。
FALLBACK_REASONS = (NOT_ENOUGH_DATA_REASON, LIFECYCLE_STOPPED_REASON)


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
        # 显式设置（编排给的）才走严格分支；未设置时保留开发机的宽松回落（F010 design §5）。
        self.device_explicit = "KRONOS_DEVICE" in os.environ
        self._predictor = None
        self._torch = None
        self._device = "cpu"
        self._load_error: str | None = None
        # 进程级锁：模型加载至多一次 + 推理互斥（spec FR-001 串行推理不变式）。
        self._lock = threading.Lock()
        # 推理准入（F009 FR-003）：由生命周期控制器注入；未接控制面时默认放行，
        # F004 既有行为与 mock 实例不受影响。
        self._allow_load = lambda: True

    def set_admission(self, allow_load) -> None:
        """接入生命周期控制器的准入判定（server 在注册控制面路由时调用）。"""
        self._allow_load = allow_load

    def allow_load(self) -> bool:
        return bool(self._allow_load())

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

    def unload(self) -> None:
        """卸载模型并释放 GPU 缓存（F009 FR-002，与 eager_load 对称）。

        幂等：未加载时为 no-op。失败以 `UnloadFailed(discarded=...)` 表达落点——
        `discarded=True` 表示模型引用已丢弃，该步不可逆，调用方不得假装回滚
        （architecture §7.1 / F009 design §5 表）。
        """
        with self._lock:
            torch = self._torch
            if self._predictor is None and torch is None:
                self._load_error = None
                return
            self._predictor = None  # 不可逆的一步
            self._load_error = None
            if torch is not None:
                try:
                    torch.cuda.empty_cache()
                except Exception as exc:
                    raise UnloadFailed(f"empty_cache failed: {exc}", discarded=True) from exc

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
        if not self.allow_load():
            # desired=stopped：走 F004 既有兜底路径，绝不触碰 _load_predictor——
            # 否则 stop 之后一次 /predict 就把显存吃回去（F009 FR-003）。
            signal = generate_placeholder_signal(rows)
            signal["reason"] = LIFECYCLE_STOPPED_REASON
            return signal

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
            self._device = self._resolve_device(torch)
            tokenizer = KronosTokenizer.from_pretrained(self.tokenizer_path)
            model = Kronos.from_pretrained(self.model_path)
            self._predictor = KronosPredictor(
                model, tokenizer, device=self._device, max_context=self.max_context
            )
            self._load_error = None
            # TR-001：实际设备 + torch CUDA 版本，"以为在 GPU、实际在 CPU"一眼可见。
            torch_cuda = getattr(getattr(torch, "version", None), "cuda", None)
            print(f"[kronos-real] model loaded: device={self._device} torch_cuda={torch_cuda}")
            return self._predictor
        except Exception as exc:
            self._load_error = str(exc)
            raise

    def _resolve_device(self, torch) -> str:
        """解析实际加载设备（F010 FR-004）；启动、restore 重载、惰性加载共用此闸。

        显式 `KRONOS_DEVICE=cuda*` 而拿不到 CUDA 时抛错，绝不静默回落 cpu——回落会让
        /health 报 cpu 而编排以为拿到了 GPU 实例。未设置时保留既有宽松语义。
        """
        request = self.device_request
        if not self.device_explicit:
            return "cuda:0" if request.startswith("cuda") and torch.cuda.is_available() else "cpu"
        if request == "cpu":
            return "cpu"
        # 只接受本 feature 真会用的那张卡的两种写法。`cuda:1` 之类**不得**被当成"以 cuda
        # 开头"而悄悄解析成 cuda:0——那与下面 ERR_UNKNOWN_DEVICE 的判断自相矛盾，且会让
        # 编排以为模型在别的卡上（单卡时段调度见架构 §7.1；代码检视 R1-005）。
        if request not in ("cuda", "cuda:0"):
            raise RuntimeError(
                f"{ERR_UNKNOWN_DEVICE}: KRONOS_DEVICE={request!r}"
                "（本 feature 只支持 cpu|cuda|cuda:0）"
            )
        if not getattr(getattr(torch, "version", None), "cuda", None):
            raise RuntimeError(f"KRONOS_DEVICE={request} but {ERR_CPU_WHEEL}")
        if not torch.cuda.is_available():
            raise RuntimeError(f"KRONOS_DEVICE={request} but {ERR_NO_CUDA_DEVICE}")
        return "cuda:0"

    @staticmethod
    def _rows_to_df(rows: list[dict]) -> pd.DataFrame:
        df = pd.DataFrame(rows)
        df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_convert(None)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        return df

    @staticmethod
    def _future_timestamps(last_timestamp: pd.Timestamp, pred_len: int) -> pd.Series:
        # 必须显式 unit：Timedelta(minutes=1) 与 Timedelta("1min") 都走 NumPy
        # generic-unit 换算，在 pandas 2.3 + numpy 2.5 触发 DeprecationWarning
        # （F004-Q005，未来版本升级为错误）。
        start = last_timestamp + pd.Timedelta(1, unit="min")
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
