"""Full AlphaGen generation run: collect candidates, self-check, count, persist.

This is the T029 capacity path: while PPO trains, every expression the vendor builder
hands to the environment is recorded, rendered to postfix tokens, passed through the
generation-side self-check (`purity`), and counted. Only definition-level facts are
persisted — no verdict, no IC-driven decision (evaluation authority is F007).
"""

from __future__ import annotations

import socket
from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.errors import FactorFactoryError
from alphamill.factor_factory.generators.alphagen_runner import (
    LakeStockData,
    LakeTensorCalculator,
    render_expression,
)
from alphamill.factor_factory.generators.base import (
    GenerationCounts,
    RejectionCounts,
    Window,
)
from alphamill.factor_factory.generators.binding import SnapshotBinding
from alphamill.factor_factory.generators.purity import check_expression
from alphamill.factor_factory.registry import run_store

if TYPE_CHECKING:
    import torch

GENERATION_GENERATOR = "alphagen"
_RENDER_ERRORS = (FactorFactoryError, AttributeError, TypeError, ValueError, IndexError)


@dataclass(frozen=True, kw_only=True)
class GenerationRunOutcome:
    """Raw facts from one mining run; carries definitions and counts only."""

    run_id: str
    hostname: str
    device: str
    proposed: int
    evaluations: int
    rejected: dict[str, int]
    registered: int
    candidates: tuple[tuple[str, ...], ...]


def run_generation(
    *,
    stock_data: LakeStockData,
    target: torch.Tensor,
    device: str,
    seed: int,
    total_timesteps: int,
    pool_capacity: int = 10,
) -> GenerationRunOutcome:
    """Train briefly and self-check every expression the agent proposed."""
    import torch
    from alphagen.models.linear_alpha_pool import MseAlphaPool
    from alphagen.rl.env.core import AlphaEnvCore
    from alphagen.rl.env.wrapper import AlphaEnvWrapper
    from alphagen.utils import reseed_everything
    from sb3_contrib import MaskablePPO

    collected: list[object] = []

    class _CollectingEnvCore(AlphaEnvCore):
        def _evaluate(self):
            with suppress(_RENDER_ERRORS):
                collected.append(self._builder.get_tree())
            return super()._evaluate()

    reseed_everything(seed)
    run_id = run_store.new_run_id(GENERATION_GENERATOR)
    torch_device = torch.device(device)
    run_stock_data = LakeStockData(
        data=stock_data.data.to(torch_device),
        max_backtrack_days=stock_data.max_backtrack_days,
        max_future_days=stock_data.max_future_days,
    )
    calculator = LakeTensorCalculator(run_stock_data, target.to(torch_device))
    pool = MseAlphaPool(capacity=pool_capacity, calculator=calculator, device=torch_device)
    core = _CollectingEnvCore(pool=pool, device=torch_device)
    env = AlphaEnvWrapper(core)
    env.reset(seed=seed)
    MaskablePPO(
        "MlpPolicy", env, n_steps=64, batch_size=64, seed=seed, device=device, verbose=0
    ).learn(total_timesteps=total_timesteps)

    seen: set[str] = set()
    rejected: dict[str, int] = {}
    accepted: list[tuple[str, ...]] = []
    for expression in collected:
        try:
            tokens = render_expression(expression)
            verdict = check_expression(
                tokens,
                scope="cross_sectional",
                seen_definition_digests=seen,
                definition_digest=repr(tokens),
            )
        except _RENDER_ERRORS:
            rejected["unregistered_op"] = rejected.get("unregistered_op", 0) + 1
            continue
        if verdict.accepted:
            accepted.append(tokens)
            seen.add(repr(tokens))
        else:
            code = verdict.reason_code or "unregistered_op"
            rejected[code] = rejected.get(code, 0) + 1

    return GenerationRunOutcome(
        run_id=run_id,
        hostname=socket.gethostname(),
        device=device,
        proposed=len(collected),
        evaluations=core.eval_cnt,
        rejected=rejected,
        registered=len(accepted),
        candidates=tuple(accepted),
    )


def build_counts(outcome: GenerationRunOutcome) -> GenerationCounts:
    """Project the run outcome onto the manifest's graded funnel counts."""
    return GenerationCounts(
        proposed=outcome.proposed,
        rejected=RejectionCounts(
            unregistered_op=outcome.rejected.get("unregistered_op", 0),
            lookahead=outcome.rejected.get("lookahead", 0),
            reachability=outcome.rejected.get("reachability", 0),
            duplicate_definition=outcome.rejected.get("duplicate_definition", 0),
        ),
        registered=outcome.registered,
    )


def write_generation_manifest(
    outcome: GenerationRunOutcome,
    *,
    run_dir: Path,
    binding: SnapshotBinding,
    window: Window,
    seed: int,
    config: Mapping[str, JSONValue],
    pair_count: int,
    symbol_map_digest: str,
    universe_digest: str,
    started_at: datetime,
    finished_at: datetime,
) -> Path:
    """Persist the terminal `completed` manifest for a generation run."""
    config_digest = run_store.write_config(run_dir, config)
    run = run_store.GenerationRun(
        schema_version=run_store.RUN_SCHEMA_VERSION,
        run_id=outcome.run_id,
        generator=GENERATION_GENERATOR,
        engine=run_store.EngineInfo(vendor_commit=None, code_digest=config_digest, dependencies={}),
        binding=binding,
        seed=seed,
        config_digest=config_digest,
        device=outcome.device,
        hostname=outcome.hostname,
        vram_limit_gb=None,
        universe=run_store.UniverseSummary(
            pair_count=pair_count,
            symbol_map_digest=symbol_map_digest,
            universe_digest=universe_digest,
            source="explicit",
        ),
        tier_level="L0",
        window=window,
        objective=run_store.ObjectiveInfo(
            turnover_penalty_lambda=0.0,
            reachability_min_trades_90d=30,
            cost_model={},
            min_after_cost_return=0.0,
        ),
        counts=build_counts(outcome),
        pool=None,
        started_at=started_at,
        finished_at=finished_at,
        status="completed",
        termination="normal",
        reason=None,
    )
    return run_store.finalize_run(run_dir, run)
