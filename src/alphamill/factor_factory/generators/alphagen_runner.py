"""Run the vendored AlphaGen PPO smoke path on an F003 tensor panel."""

from __future__ import annotations

import re
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

import pandas as pd

from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.generators.lake_tensor import TensorPanel

if TYPE_CHECKING:
    import torch
    from alphagen.data.expression import Expression
    from alphagen.models.alpha_pool import AlphaPoolBase

ALPHAGEN_RUNNER_VERSION: Final = "1"
_VENDOR_ROOT = Path(__file__).with_name("alphagen_vendor").resolve()
_VENDOR_IMPORT_ROOT = str(_VENDOR_ROOT)
if _VENDOR_IMPORT_ROOT not in sys.path:
    sys.path.insert(0, _VENDOR_IMPORT_ROOT)


@dataclass(frozen=True, slots=True)
class LakeStockData:
    """Feature-first stock data supplied to the AlphaGen compatibility boundary."""

    data: torch.Tensor
    max_backtrack_days: int = 0
    max_future_days: int = 0

    @property
    def n_days(self) -> int:
        """Return the number of observations in the panel."""
        return int(self.data.shape[1])

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
                data=stock_data.data.permute(1, 0, 2),
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
        return int(self.data.shape[0])

    @property
    def n_stocks(self) -> int:
        return int(self.data.shape[2])


def __getattr__(name: str) -> type:
    if name == "LakeTensorCalculator":
        return _lake_tensor_calculator_class()
    raise AttributeError(name)


def build_stock_data(
    panel: TensorPanel,
    *,
    feature_map: Mapping[str, int],
    target_horizon: int = 1,
) -> tuple[LakeStockData, torch.Tensor, tuple[str, ...]]:
    """Build feature-first tensors and a forward close-return target.

    Missing or out-of-universe cells remain NaN. The returned pair order is the
    panel order, so callers can reproduce the same stock axis on another run.
    """
    import torch

    if target_horizon < 1:
        raise SchemaValidationError("target_horizon must be at least one bar")
    ordered_features = tuple(
        name for name, _ in sorted(feature_map.items(), key=lambda item: item[1])
    )
    if not ordered_features or set(feature_map.values()) != set(range(len(feature_map))):
        raise SchemaValidationError("feature_map channels must be contiguous from zero")

    pairs = tuple(panel.pairs)
    timestamps = pd.DatetimeIndex(panel.timestamps)
    index = pd.MultiIndex.from_product([timestamps, pairs], names=["timestamp", "pair"])
    panel_frame = panel.panel.reindex(index)
    out_of_universe = ~panel_frame["__in_universe__"].eq(True)
    panel_frame.loc[out_of_universe, list(ordered_features)] = float("nan")
    values = panel_frame[list(ordered_features)].to_numpy(dtype="float32")
    days, stocks = len(timestamps), len(pairs)
    data = torch.from_numpy(values.reshape(days, stocks, len(ordered_features))).permute(2, 0, 1)

    close_channel = next(
        (
            channel
            for name, channel in feature_map.items()
            if name.split(".", maxsplit=1)[-1].split("@", maxsplit=1)[0].lower() == "close"
        ),
        None,
    )
    if close_channel is None:
        raise SchemaValidationError("feature_map must contain a close feature for the target")
    close = data[close_channel]
    target = torch.full_like(close, float("nan"))
    if target_horizon < days:
        target[:-target_horizon] = close[target_horizon:] / close[:-target_horizon] - 1.0
    target[~torch.isfinite(target)] = float("nan")
    return LakeStockData(data=data), target, pairs


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
