"""回调式 AlphaGen 训练入口（F012 `FR-002`，design §1 第 2 行、§5）。

只管训练与回调时机：环境每评估一个表达式，就渲染成 postfix token 交给 `on_expression`；
每个训练步边界问一次 `should_stop()`，非 None 即叫停。停止判定本身在 `StopController`，
候选处理在 `CandidatePipeline`，这里都不做。

SB3 回调叫停时 `learn()` 同样正常返回，所以以 `stopped` 标志区分「被叫停」与「预算耗尽」，
不把「正常返回」当作耗尽（检视 D33）。F003 的 `alphagen_generation.run_generation` 原样保留
（检视 D19）。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from alphamill.factor_factory.errors import FactorFactoryError
from alphamill.factor_factory.generators.alphagen_runner import LakeStockData, render_expression

if TYPE_CHECKING:
    import torch

_RENDER_ERRORS = (FactorFactoryError, AttributeError, TypeError, ValueError, IndexError)
_ROLLOUT_STEPS = 64  # 与 run_generation 一致


@dataclass(frozen=True, kw_only=True)
class TrainingOutcome:
    evaluations: int
    stopped: bool
    timesteps: int


def train_with_callbacks(
    *,
    stock_data: LakeStockData,
    target: torch.Tensor,
    device: str,
    seed: int,
    total_timesteps: int,
    on_expression: Callable[[tuple[str, ...]], object],
    should_stop: Callable[[], str | None],
    pool_capacity: int = 10,
) -> TrainingOutcome:
    import torch
    from alphagen.models.linear_alpha_pool import MseAlphaPool
    from alphagen.rl.env.core import AlphaEnvCore
    from alphagen.rl.env.wrapper import AlphaEnvWrapper
    from alphagen.utils import reseed_everything
    from sb3_contrib import MaskablePPO
    from stable_baselines3.common.callbacks import BaseCallback

    from alphamill.factor_factory.generators.alphagen_runner import LakeTensorCalculator

    class _HookedEnvCore(AlphaEnvCore):
        def _evaluate(self):
            on_expression(_render(self._builder.get_tree()))
            return super()._evaluate()

    class _StopCallback(BaseCallback):
        stopped = False

        def _on_step(self) -> bool:
            if should_stop() is None:
                return True
            self.stopped = True
            return False

    reseed_everything(seed)
    torch_device = torch.device(device)
    run_stock_data = LakeStockData(
        data=stock_data.data.to(torch_device),
        max_backtrack_days=stock_data.max_backtrack_days,
        max_future_days=stock_data.max_future_days,
    )
    calculator = LakeTensorCalculator(run_stock_data, target.to(torch_device))
    pool = MseAlphaPool(capacity=pool_capacity, calculator=calculator, device=torch_device)
    core = _HookedEnvCore(pool=pool, device=torch_device)
    env = AlphaEnvWrapper(core)
    env.reset(seed=seed)
    model = MaskablePPO(
        "MlpPolicy",
        env,
        n_steps=_ROLLOUT_STEPS,
        batch_size=_ROLLOUT_STEPS,
        seed=seed,
        device=device,
        verbose=0,
    )
    callback = _StopCallback()
    model.learn(total_timesteps=total_timesteps, callback=callback)
    return TrainingOutcome(
        evaluations=core.eval_cnt, stopped=callback.stopped, timesteps=model.num_timesteps
    )


def _render(expression: object) -> tuple[str, ...]:
    """渲染失败的表达式仍要进漏斗计数：给一个不可编译的 token，由流水线判 unregistered_op。"""
    try:
        return render_expression(expression)
    except _RENDER_ERRORS as exc:
        return (f"unrenderable:{type(exc).__name__}",)
