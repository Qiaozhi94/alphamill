"""Run the vendored AlphaGen PPO smoke path on an F003 tensor panel."""

from __future__ import annotations

import re
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

import numpy as np
import pandas as pd

from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.generators.lake_tensor import TensorPanel

if TYPE_CHECKING:
    import torch
    from alphagen.data.expression import Expression
    from alphagen.models.alpha_pool import AlphaPoolBase

ALPHAGEN_RUNNER_VERSION: Final = "1"
# 顺序必须与 vendor 的 FeatureType 枚举一致（OPEN/CLOSE/HIGH/LOW/VOLUME/VWAP）——
# vendor 用 int(FeatureType) 直接索引张量的 feature 轴。
_FEATURE_TYPE_NAMES: Final = ("open", "close", "high", "low", "volume", "vwap")
_CLOSE_SLOT: Final = _FEATURE_TYPE_NAMES.index("close")
_VENDOR_ROOT = Path(__file__).with_name("alphagen_vendor").resolve()
_VENDOR_IMPORT_ROOT = str(_VENDOR_ROOT)
if _VENDOR_IMPORT_ROOT not in sys.path:
    sys.path.insert(0, _VENDOR_IMPORT_ROOT)


@dataclass(frozen=True, slots=True)
class LakeStockData:
    """Vendor-layout stock data: ``(n_days, n_features, n_stocks)``.

    The vendor derives its evaluation window as
    ``data[period.start + backtrack : period.stop + backtrack + n_days - 1, feature, :]``,
    so axis 0 must be days and the feature axis is indexed by ``FeatureType``.
    """

    data: torch.Tensor
    max_backtrack_days: int = 0
    max_future_days: int = 0

    @property
    def n_days(self) -> int:
        """Evaluation window length: rows minus the backtrack/future margins."""
        return int(self.data.shape[0]) - self.max_backtrack_days - self.max_future_days

    @property
    def n_stocks(self) -> int:
        """Return the number of pairs in the panel."""
        return int(self.data.shape[2])


@dataclass(frozen=True, slots=True)
class PpoEpochResult:
    """Raw PPO smoke-run facts; evaluation decisions belong to F007."""

    steps: int
    device: str
    pool_size: int
    evaluations: int
    duration_s: float
    pool: AlphaPoolBase


def _lake_tensor_calculator_class() -> type:
    _add_vendor_root()
    from alphagen.data.calculator import TensorAlphaCalculator

    class LakeTensorCalculator(TensorAlphaCalculator):
        """Evaluate vendored expressions against an F003 lake tensor."""

        def __init__(self, stock_data: LakeStockData, target: torch.Tensor) -> None:
            super().__init__(target)
            self._lake_stock_data = stock_data
            self._stock_data = _VendorStockData(
                data=stock_data.data,
                max_backtrack_days=stock_data.max_backtrack_days,
                max_future_days=stock_data.max_future_days,
            )

        @property
        def n_days(self) -> int:
            """Return the calculator window length."""
            return self._lake_stock_data.n_days

        def evaluate_alpha(self, expr: Expression) -> torch.Tensor:
            """Evaluate an expression and align its returned window to ``n_days``."""
            import torch

            values = expr.evaluate(self._stock_data)
            if values.shape[0] == self.n_days:
                return values
            if values.shape[0] > self.n_days:
                return values[-self.n_days :]
            aligned = torch.full(
                (self.n_days, self._lake_stock_data.n_stocks),
                float("nan"),
                dtype=values.dtype,
                device=values.device,
            )
            aligned[-values.shape[0] :] = values
            return aligned

    globals()["LakeTensorCalculator"] = LakeTensorCalculator
    return LakeTensorCalculator


@dataclass(frozen=True, slots=True)
class _VendorStockData:
    data: torch.Tensor
    max_backtrack_days: int
    max_future_days: int

    @property
    def n_days(self) -> int:
        return int(self.data.shape[0]) - self.max_backtrack_days - self.max_future_days

    @property
    def n_stocks(self) -> int:
        return int(self.data.shape[2])


def __getattr__(name: str) -> type:
    if name == "LakeTensorCalculator":
        return _lake_tensor_calculator_class()
    raise AttributeError(name)


def _operator_margin() -> int:
    """Vendor operators look back/forward by at most the largest delta time."""
    _add_vendor_root()
    from alphagen.config import DELTA_TIMES

    return max(DELTA_TIMES)


def build_stock_data(
    panel: TensorPanel,
    *,
    feature_map: Mapping[str, int],
    target_horizon: int = 1,
) -> tuple[LakeStockData, torch.Tensor, tuple[str, ...]]:
    """Build a vendor-layout tensor and a forward close-return target.

    The vendor reads ``data[start:stop, <FeatureType>, :]``, so the tensor MUST be
    ``(n_days, n_features, n_stocks)`` with the feature axis indexed by ``FeatureType``
    (open/close/high/low/volume/vwap) — an arbitrary lake ``feature_map`` channel order
    is not addressable by the vendor's expression language. Absent FeatureTypes and
    out-of-universe cells stay NaN. The returned pair order is the panel order.
    """
    import torch

    if target_horizon < 1:
        raise SchemaValidationError("target_horizon must be at least one bar")

    slots = {
        name: _FEATURE_TYPE_NAMES.index(basename)
        for name in feature_map
        if (basename := name.split(".")[-1].split("@")[0].lower()) in _FEATURE_TYPE_NAMES
    }
    if not slots:
        raise SchemaValidationError(
            "panel exposes none of the vendor FeatureType columns "
            f"({', '.join(_FEATURE_TYPE_NAMES)})"
        )
    close_columns = [name for name, slot in slots.items() if slot == _CLOSE_SLOT]
    if not close_columns:
        raise SchemaValidationError("panel must expose a close column for the target")

    pairs = tuple(panel.pairs)
    timestamps = pd.DatetimeIndex(panel.timestamps)
    index = pd.MultiIndex.from_product([timestamps, pairs], names=["timestamp", "pair"])
    frame = panel.panel.reindex(index)
    out_of_universe = ~frame["__in_universe__"].eq(True)
    masked = frame[list(slots)].mask(out_of_universe, other=float("nan"))

    days, stocks = len(timestamps), len(pairs)
    width = len(_FEATURE_TYPE_NAMES)
    margin = _operator_margin()
    if days <= margin + target_horizon:
        raise SchemaValidationError(
            f"panel has {days} days but the vendor operator set needs more than "
            f"{margin + target_horizon}"
        )
    values = np.full((days * stocks, width), np.nan, dtype="float32")
    for name, slot in slots.items():
        values[:, slot] = masked[name].to_numpy(dtype="float32")
    data = torch.from_numpy(
        np.ascontiguousarray(values.reshape(days, stocks, -1).transpose(0, 2, 1))
    )

    span = days - margin - target_horizon
    close = data[margin : margin + span, _CLOSE_SLOT, :]
    forward = data[margin + target_horizon : margin + target_horizon + span, _CLOSE_SLOT, :]
    target = forward / close - 1.0
    target[~torch.isfinite(target)] = float("nan")
    return (
        LakeStockData(data=data, max_backtrack_days=margin, max_future_days=target_horizon),
        target,
        pairs,
    )


def run_ppo_epoch(
    *,
    stock_data: LakeStockData,
    target: torch.Tensor,
    device: str,
    seed: int,
    pool_capacity: int = 5,
    total_timesteps: int = 64,
) -> PpoEpochResult:
    """Run one bounded PPO smoke epoch and return raw execution facts."""
    import torch
    from alphagen.models.linear_alpha_pool import MseAlphaPool
    from alphagen.rl.env.core import AlphaEnvCore
    from alphagen.rl.env.wrapper import AlphaEnvWrapper
    from alphagen.utils import reseed_everything
    from sb3_contrib import MaskablePPO

    reseed_everything(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    run_stock_data = LakeStockData(
        data=stock_data.data.to(device),
        max_backtrack_days=stock_data.max_backtrack_days,
        max_future_days=stock_data.max_future_days,
    )
    calculator_class = _lake_tensor_calculator_class()
    calculator = calculator_class(run_stock_data, target.to(device))
    pool = MseAlphaPool(
        capacity=pool_capacity,
        calculator=calculator,
        device=torch.device(device),
    )
    core = AlphaEnvCore(pool=pool, device=torch.device(device))
    env = AlphaEnvWrapper(core)
    env.reset(seed=seed)
    n_steps = min(total_timesteps, 64)
    start = time.perf_counter()
    model = MaskablePPO(
        "MlpPolicy",
        env,
        n_steps=n_steps,
        batch_size=n_steps,
        seed=seed,
        device=device,
        verbose=0,
    )
    model.learn(total_timesteps=total_timesteps)
    return PpoEpochResult(
        steps=total_timesteps,
        device=device,
        pool_size=pool.size,
        evaluations=core.eval_cnt,
        duration_s=time.perf_counter() - start,
        pool=pool,
    )


def extract_candidates(pool: AlphaPoolBase) -> list[tuple[str, ...]]:
    """Render accepted vendor expressions as compiler-compatible postfix tokens."""
    _add_vendor_root()
    from alphagen.data.expression import Constant, DeltaTime, Feature, Operator

    def render(expr: Expression) -> tuple[str, ...]:
        if isinstance(expr, Feature):
            return (f"feature:{expr._feature.name.lower()}",)
        if isinstance(expr, Constant):
            return (f"constant:{expr.value:g}",)
        if isinstance(expr, DeltaTime):
            return (f"delta:{expr._delta_time}",)
        if isinstance(expr, Operator):
            tokens: list[str] = []
            operands = expr.operands
            render_operands = operands
            if operands and hasattr(operands[-1], "_delta_time"):
                render_operands = operands[:-1]
            for operand in render_operands:
                tokens.extend(render(operand))
            name = _operator_token(type(expr).__name__, operands)
            return (*tokens, name)
        return (str(expr),)

    return [render(expr) for expr in pool.exprs[: pool.size] if expr is not None]


def _add_vendor_root() -> None:
    if _VENDOR_IMPORT_ROOT not in sys.path:
        sys.path.insert(0, _VENDOR_IMPORT_ROOT)


def _operator_token(name: str, operands: tuple[Expression, ...]) -> str:
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    if snake in {"rank", "cs_rank", "cross_sectional_rank"}:
        return "cs_rank"
    if operands and name.lower() in {"return", "pctchange", "pct_change", "rollingstd"}:
        last = operands[-1]
        if hasattr(last, "_delta_time"):
            operator = snake.replace("pctchange", "pct_change").replace("rollingstd", "rolling_std")
            return f"{operator}:{last._delta_time}"
    return snake
