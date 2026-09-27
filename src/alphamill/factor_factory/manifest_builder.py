"""挖掘/种子运行的唯一 run.json 构建器（F012 `FR-007`，design §1 第 12 行，检视 D14）。

自 `cli.py` 迁出 `_SeedState` / `_manifest` / 失败收尾：生成器、层级、引擎与 objective 不再写死，
由 `mine_dispatch` 按生成器给出；v2 字段（budget / stop_reason / evaluations）在这里落笔。
事件写者必须先于 finalize 关闭（检视 D30）——失败与 partial 收尾同样遵守。
"""

from __future__ import annotations

import json
import socket
import statistics
import sys
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, TypeAlias

from alphamill.factor_factory import canonical, errors
from alphamill.factor_factory.generators import base, binding, gpu_slot
from alphamill.factor_factory.generators.stop_conditions import RunInterrupted
from alphamill.factor_factory.registry import run_store

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_REJECTED = 2
EMPTY_CONFIG_DIGEST = canonical.sha256_prefixed_bytes(canonical.canonical_json_bytes({}))
Outcome: TypeAlias = tuple[Literal["completed", "rejected", "failed", "partial"], str, str | None]


@dataclass(frozen=True, slots=True, kw_only=True)
class RunState:
    run_id: str
    run_dir: Path
    started_at: datetime
    seed: int
    generator: str
    tier_level: str
    engine: run_store.EngineInfo
    objective: run_store.ObjectiveInfo
    binding: binding.SnapshotBinding | None = None
    config_digest: str = EMPTY_CONFIG_DIGEST
    window: base.Window | None = None
    universe: run_store.UniverseSummary | None = None
    counts: base.GenerationCounts = base.GenerationCounts(0, base.RejectionCounts(), 0)
    device: Literal["cpu", "cuda"] = "cpu"
    vram_limit_gb: float | None = None
    kronos_offload: dict[str, canonical.JSONValue] | None = None
    budget: run_store.BudgetInfo | None = None
    stop_reason: str | None = None
    evaluations: int | None = None


def build_manifest(state: RunState, outcome: Outcome) -> run_store.GenerationRun:
    status, termination, reason = outcome
    return run_store.GenerationRun(
        schema_version=run_store.RUN_SCHEMA_VERSION,
        run_id=state.run_id,
        generator=state.generator,
        engine=state.engine,
        binding=state.binding,
        seed=state.seed,
        config_digest=state.config_digest,
        device=state.device,
        hostname=socket.gethostname(),
        vram_limit_gb=state.vram_limit_gb,
        kronos_offload=state.kronos_offload,
        universe=state.universe,
        tier_level=state.tier_level,
        window=state.window,
        objective=state.objective,
        counts=state.counts,
        pool=None,
        started_at=state.started_at,
        finished_at=datetime.now(UTC),
        status=status,
        termination=termination,
        reason=reason,
        budget=state.budget,
        stop_reason=state.stop_reason,
        evaluations=state.evaluations,
    )


def finish_error(state: RunState, outcome: Outcome, writer: Any = None) -> int:
    if writer is not None:
        writer.close()
    try:
        run_store.finalize_run(state.run_dir, build_manifest(state, outcome))
    except (errors.FactorFactoryError, OSError) as exc:
        print(f"cannot publish terminal run: {exc}", file=sys.stderr)
    print(outcome[2], file=sys.stderr)
    return EXIT_REJECTED if outcome[0] == "rejected" else EXIT_FAILED


def reject(state: RunState, termination: str, reason: str, writer: Any = None) -> int:
    return finish_error(state, ("rejected", termination, reason), writer)


def finish_exception(state: RunState, exc: Exception, writer, quota: int, spec, *, config_phase):
    """异常 → 终态（design §7）。

    仅 `config_phase`（进入生成器之前）时配置类异常才记 invalid_config；训练期一律 failed。
    """
    match exc:
        case RunInterrupted() | gpu_slot.AcquireCancelled():
            return finish_partial(state, writer, quota, spec)
        case gpu_slot.GpuQueueTimeoutError():
            return reject(state, "queue_timeout", str(exc), writer)
        case errors.MiningCapabilityError():
            return reject(state, "capability_unavailable", str(exc), writer)
        case errors.BindingValidationError():
            return reject(state, "invalid_binding", str(exc), writer)
        case errors.UnknownSchemaVersionError():
            return reject(state, "unknown_schema_version", str(exc), writer)
        case errors.SchemaValidationError() | TypeError() | ValueError() if config_phase:
            return reject(state, "invalid_config", str(exc), writer)
        case _:
            return finish_error(state, ("failed", type(exc).__name__, str(exc)), writer)


def partial_outcome(state: RunState, stop_reason: str, quota: int) -> Outcome:
    """partial 的 termination 取停止原因，reason 写明「已入册 k/quota」（spec FR-005）。"""
    return ("partial", stop_reason, f"已入册 {state.counts.registered}/{quota}：{stop_reason}")


def budget_for(spec, config, quota: int) -> run_store.BudgetInfo:
    if not spec.needs_panel:
        return run_store.BudgetInfo(quota=quota, total_timesteps=None, pool_capacity=None)
    return run_store.BudgetInfo(
        quota=quota,
        total_timesteps=int(config["total_timesteps"]),
        pool_capacity=int(config["pool_capacity"]),
    )


def finish_partial(state: RunState, writer, quota: int, spec) -> int:
    """训练前或排队时被中断：partial/interrupted，入册 0，照常写 run.json（FR-005）。"""
    if writer is not None:
        writer.close()
    state = replace(state, stop_reason="interrupted")
    run_store.finalize_run(
        state.run_dir, build_manifest(state, partial_outcome(state, "interrupted", quota))
    )
    print_summary(state, "partial", spec)
    return EXIT_OK


def print_summary(state: RunState, status: str, spec) -> None:
    """运维可见的单行摘要（IR-003）；只对 alphagen 打印，manual 输出保持与改动前一致。

    run.json 已发布后才调用：摘要失败只告警，不改退出码、不再走异常收尾（检视 R-A5）。
    """
    if not spec.needs_panel:
        return
    try:
        _print_summary(state, status)
    except Exception as exc:  # noqa: BLE001 — run.json 已发布，任何摘要失败都只告警（R2-2）
        print(f"WARNING: run {state.run_id} summary unavailable: {exc}", file=sys.stderr)


def _print_summary(state: RunState, status: str) -> None:
    elapsed = _prefilter_elapsed(state.run_dir / "prefilter.jsonl")
    quantiles = statistics.quantiles(elapsed, n=20) if len(elapsed) >= 2 else elapsed * 19
    summary = {
        "run_id": state.run_id,
        "generator": state.generator,
        "status": status,
        "stop_reason": state.stop_reason,
        "counts": asdict(state.counts),
        "budget": asdict(state.budget) if state.budget else None,
        "prefilter_ms_p50": statistics.median(elapsed) if elapsed else None,
        "prefilter_ms_p95": quantiles[18] if quantiles else None,
        "vram_peak_gb": _vram_peak_gb(state.device),  # 产能取证（AC-009）
    }
    print(json.dumps(summary, ensure_ascii=False))


def _prefilter_elapsed(path: Path) -> list[float]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [float(json.loads(line)["elapsed_ms"]) for line in lines if line.strip()]


def _vram_peak_gb(device: str) -> float | None:
    if device != "cuda":
        return None
    import torch

    return round(torch.cuda.max_memory_allocated() / 2**30, 3)
