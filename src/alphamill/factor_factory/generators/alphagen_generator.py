"""AlphaGen 生成器编排（F012 `FR-001`/`FR-002`/`FR-008`，design §1 第 3 行、§2）。

`request.panel`（CLI 已在卸载 Kronos、取 GPU 槽之前建好）→ vendor 布局张量 → 回调式训练；
训练中每个被评估的表达式立即交给 `CandidatePipeline` 自检入册。停止判定、事件写者与编译器
注册表都由构造器注入（检视 D31），本类只做串联，不做判定。

层级固定 L0、不产出线性池（`pool=None`）：池权重是 vendor 的训练内部状态，不是登记事实。
"""

from __future__ import annotations

import logging
import statistics
import time
from datetime import UTC, datetime
from typing import Final

from alphamill.factor_factory import mine_dispatch
from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.generators.alphagen_runner import build_stock_data
from alphamill.factor_factory.generators.alphagen_training import train_with_callbacks
from alphamill.factor_factory.generators.base import GenerationRequest, GenerationResult
from alphamill.factor_factory.generators.candidate_pipeline import CandidatePipeline

LOGGER = logging.getLogger(__name__)
TIER_LEVEL: Final = "L0"
_LOG_EVERY: Final = 500  # 每 500 次评估一条进度日志（design §6）


class AlphaGenGenerator:
    name = "alphagen"

    def __init__(self, ctx: mine_dispatch.BuildContext) -> None:
        self._ctx = ctx

    def produce(self, request: GenerationRequest) -> GenerationResult:
        ctx = self._ctx
        _ensure_log_handler()
        panel = request.panel
        if panel is None:
            raise SchemaValidationError("alphagen needs the tensor panel built by the CLI")
        total_timesteps = int(ctx.config["total_timesteps"])
        pool_capacity = int(ctx.config["pool_capacity"])
        stock_data, target, _ = build_stock_data(panel, feature_map=panel.feature_map)
        pipeline = CandidatePipeline(
            panel=panel,
            objective_params=mine_dispatch.objective_params(ctx.config),
            run_id=ctx.run_id,
            writer=ctx.writer,
            compilers=ctx.compilers,
            quota=request.quota,
            generator_version=mine_dispatch.ALPHAGEN_GENERATOR_VERSION,
            created_at=datetime.now(UTC),
            on_quota=ctx.stop.mark_quota,
        )

        def offer(tokens: tuple[str, ...]) -> None:
            pipeline.offer(tokens)
            proposed = pipeline.counts().proposed
            if proposed and proposed % _LOG_EVERY == 0 and not pipeline.stopped:
                _log_progress(pipeline)

        started = time.perf_counter()
        outcome = train_with_callbacks(
            stock_data=stock_data,
            target=target,
            device=ctx.device,
            seed=request.seed,
            total_timesteps=total_timesteps,
            pool_capacity=pool_capacity,
            on_expression=offer,
            should_stop=ctx.stop.check,
        )
        stop_reason = _stop_reason(outcome.stopped, ctx.stop.reason, pipeline.stopped)
        LOGGER.info(
            "alphagen stopped: stop_reason=%s elapsed_s=%.1f evaluations=%d%s",
            stop_reason,
            time.perf_counter() - started,
            outcome.evaluations,
            _vram_peak(ctx.device),
        )
        return GenerationResult(
            run_id=ctx.run_id,
            factors=list(pipeline.registered),
            pool=None,
            counts=pipeline.counts(),
            device=ctx.device,
            tier_level=TIER_LEVEL,
            stop_reason=stop_reason,
            evaluations=outcome.evaluations,
            budget={
                "quota": request.quota,
                "total_timesteps": total_timesteps,
                "pool_capacity": pool_capacity,
            },
        )


def _stop_reason(stopped: bool, decided: str | None, quota_hit: bool) -> str:
    """回调叫停取判定点的原因；未叫停但配额恰在最后一步达成，仍如实记 quota_reached。"""
    if stopped and decided is not None:
        return decided
    return "quota_reached" if quota_hit else "budget_exhausted"


def _ensure_log_handler() -> None:
    """CLI 进程未配置 logging 时，进度/停止日志仍须到 stderr（design §6，运维可见）。"""
    if LOGGER.handlers or logging.getLogger().handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)


def _log_progress(pipeline: CandidatePipeline) -> None:
    counts = pipeline.counts()
    timings = pipeline.prefilter_ms
    p95 = statistics.quantiles(timings, n=20)[18] if len(timings) >= 2 else None
    LOGGER.info(
        "alphagen progress: proposed=%d registered=%d rejected=%s prefilter_ms_p95=%s",
        counts.proposed,
        counts.registered,
        vars(counts.rejected),
        p95,
    )


def _vram_peak(device: str) -> str:
    if device != "cuda":
        return ""
    import torch

    return f" vram_peak_gb={torch.cuda.max_memory_allocated() / 2**30:.2f}"
