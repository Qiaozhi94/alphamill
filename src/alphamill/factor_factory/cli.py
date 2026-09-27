from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from alphamill.factor_factory import canonical, errors, mine_dispatch
from alphamill.factor_factory.generators import base, binding, gpu_slot
from alphamill.factor_factory.generators.egress_guard import install_egress_guard
from alphamill.factor_factory.generators.manual import (
    seeds as manual_seeds,  # noqa: F401 测试打桩入口
)
from alphamill.factor_factory.generators.mining_capability import require_mining_capabilities
from alphamill.factor_factory.generators.stop_conditions import (
    PARTIAL_REASONS,
    RunInterrupted,
    StopController,
    install_signal_flags,
)
from alphamill.factor_factory.generators.write_guard import install_write_path_guard
from alphamill.factor_factory.manifest_builder import (
    EXIT_FAILED,
    EXIT_OK,
    EXIT_REJECTED,
    RunState,
    budget_for,
    build_manifest,
    finish_error,
    finish_partial,
    partial_outcome,
    print_summary,
    reject,
)
from alphamill.factor_factory.mine_config import (
    DEFAULT_ALPHAGEN_CONFIG,
    load_config,
    resolve_kronos_offload,
    restore_kronos_if_needed,
)
from alphamill.factor_factory.registry import factor_store, run_store
from alphamill.factor_factory.registry.default_compilers import full_registry
from alphamill.factor_factory.registry.event_writer import RunEventWriter

__all__ = ("EXIT_FAILED", "EXIT_OK", "EXIT_REJECTED", "build_parser", "main")
_GENERATORS: Final = tuple(mine_dispatch.SPECS)


def build_parser() -> argparse.ArgumentParser:
    """Build the generation CLI parser."""
    parser = argparse.ArgumentParser(prog="alphamill-generate")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("seed", "mine"):
        command = commands.add_parser(name)
        choices = _GENERATORS if name == "mine" else ("manual",)
        command.add_argument("--generator", choices=choices, required=True)
        command.add_argument("--binding", type=Path)
        command.add_argument("--seed", type=int, required=True)
        command.add_argument(
            "--window", choices=(base.DEFAULT_WINDOW_PRESET,), default=base.DEFAULT_WINDOW_PRESET
        )
        command.add_argument("--config", type=Path)
        if name == "mine":
            command.add_argument("--quota", type=int, default=base.DEFAULT_SEED_QUOTA)
            command.add_argument("--allow-cpu", action="store_true")
            command.add_argument("--allow-offhours", action="store_true")
    show = commands.add_parser("show")
    selector = show.add_mutually_exclusive_group(required=True)
    selector.add_argument("--run")
    selector.add_argument("--factor")
    return parser


def _run_generation(args: argparse.Namespace, reports_root: Path, lake_root: Path | None) -> int:
    with install_signal_flags() as flags:
        return _generate(args, reports_root, lake_root, flags)


def _generate(args, reports_root: Path, lake_root: Path | None, flags) -> int:
    spec = mine_dispatch.resolve(args.generator)
    mining = args.command == "mine"
    run_id = run_store.new_run_id(spec.name)
    state = RunState(
        run_id=run_id,
        run_dir=run_store.generation_run_dir(run_id, reports_root=reports_root),
        started_at=datetime.now(UTC),
        seed=args.seed,
        generator=spec.name,
        tier_level=spec.tier_level,
        engine=mine_dispatch.engine_info(spec),
        objective=mine_dispatch.objective_info(spec, DEFAULT_ALPHAGEN_CONFIG),
    )
    slot: gpu_slot.GpuSlot | None = None
    kronos_offload_attempt: gpu_slot.KronosOffloadOutcome | None = None
    writer: RunEventWriter | None = None
    config: dict[str, canonical.JSONValue] = {}
    quota = args.quota if mining else base.DEFAULT_SEED_QUOTA
    binding_path: Path | None = args.binding
    if binding_path is None:
        return reject(state, "missing_binding", "--binding is required")
    try:
        validated = binding.validate_binding(
            binding.load_binding_file(binding_path), lake_root=lake_root
        )
        window = base.Window.from_preset(args.window, cutoff_time=validated.resolved.cutoff_time)
        window_config: canonical.JSONValue = {
            "preset": args.window,
            "start": canonical.utc_iso(window.start),
            "end": canonical.utc_iso(window.end),
            "resample": window.resample,
        }
        supplied_config = load_config(args.config)
        if (
            mining
            and spec.tier_required_in_config
            and args.config is not None
            and "tier_level" not in supplied_config
        ):
            return reject(state, "unknown_tier", "tier_level is required in --config")
        config = mine_dispatch.compose_config(
            spec, supplied_config, mining=mining, quota=quota, window=window_config
        )
        state = replace(
            state,
            binding=validated.source,
            config_digest=canonical.sha256_prefixed_bytes(canonical.canonical_json_bytes(config)),
            window=window,
            universe=mine_dispatch.universe_summary(spec, validated, None),
            objective=mine_dispatch.objective_info(spec, config),
            budget=budget_for(spec, config, quota) if mining else None,
        )
        if mining and config.get("tier_level") != spec.tier_level:
            return reject(state, "unknown_tier", "tier_level is missing or unknown")
        panel, stop = None, None
        if mining:
            slot_config = mine_dispatch.slot_config(config)
            require_mining_capabilities(require_cuda=not args.allow_cpu)
            stop = StopController(
                flags=flags,
                window_start=slot_config.window_start,
                window_end=slot_config.window_end,
                window_tz=slot_config.window_tz,
                ignore_window=args.allow_offhours,
                clock=None,
            )
            stop.raise_if_interrupted()
            if spec.needs_panel:  # 先建张量：坏张量不白卸载 Kronos（检视 D21）
                panel = mine_dispatch.prepare_panel(validated, window, config, lake_root)
                universe = mine_dispatch.universe_summary(spec, validated, panel)
                state = replace(state, universe=universe)
                mine_dispatch.warm_training_runtime()  # 导入期缓存目录须在写护栏外建好
                stop.raise_if_interrupted()
            window_open = gpu_slot.in_training_window(
                datetime.now(UTC),
                window_start=slot_config.window_start,
                window_end=slot_config.window_end,
                window_tz=slot_config.window_tz,
            )
            if not window_open and not args.allow_offhours:
                return reject(
                    state, "outside_training_window", "outside configured training window"
                )
            if not args.allow_cpu:
                # 先卸载 Kronos 再量显存：白天 Kronos 常驻 ≤3GB，8GB 卡上剩余不足夜槽
                # 需要的 ≤6GB 独占——这正是卸载要解决的主场景（架构 §7.1 时段表）。
                offload = resolve_kronos_offload(config)
                kronos_offload_attempt = offload
                state = replace(state, kronos_offload=asdict(offload))
                if offload.action == "fail_closed":
                    return reject(state, "kronos_offload_failed", offload.reason)
                reading = gpu_slot.query_vram()
                if not gpu_slot.vram_is_sufficient(reading, limit_gb=slot_config.vram_limit_gb):
                    return reject(
                        state, "cuda_unavailable", "CUDA VRAM is unavailable or insufficient"
                    )
                # device 只在确认显存可用后才写成 cuda——被拒的运行不该自称跑在 GPU 上。
                state = replace(state, device="cuda", vram_limit_gb=slot_config.vram_limit_gb)
                candidate_slot = gpu_slot.GpuSlot(
                    locks_dir=reports_root / ".locks", config=slot_config
                )
                candidate_slot.acquire(
                    state.run_id, ignore_window=args.allow_offhours, cancel=flags.is_set
                )
                slot = candidate_slot
        request = base.GenerationRequest(
            generator=spec.name,
            binding=validated.source,
            seed=state.seed,
            window=window,
            config=config,
            quota=quota,
            panel=panel,
        )
        with (
            install_egress_guard(),
            install_write_path_guard(state.run_dir, reports_root=reports_root),
        ):
            writer = (
                RunEventWriter(state.run_dir, run_id=state.run_id) if spec.needs_panel else None
            )
            context = mine_dispatch.BuildContext(
                run_id=state.run_id,
                config=config,
                stop=stop,
                writer=writer,
                compilers=full_registry(),
                device=state.device,
            )
            result = mine_dispatch.build_generator(spec, context).produce(request)
            state = replace(
                state,
                counts=result.counts,
                stop_reason=result.stop_reason,
                evaluations=result.evaluations,
                budget=run_store.BudgetInfo(**result.budget) if result.budget else state.budget,
            )
            for factor in result.factors:
                factor_store.write(state.run_dir, factor)
            if writer is not None:
                writer.close()  # 先于 finalize：run.json 发布时事件已落盘（检视 D30）
            state = replace(state, config_digest=run_store.write_config(state.run_dir, config))
            partial = result.stop_reason in PARTIAL_REASONS
            outcome = (
                partial_outcome(state, str(result.stop_reason), quota)
                if partial
                else ("completed", "normal", None)
            )
            run_store.finalize_run(state.run_dir, build_manifest(state, outcome))
        print_summary(state, outcome[0], spec)
        return EXIT_OK
    except (errors.FactorFactoryError, OSError, RuntimeError, TypeError, ValueError) as exc:
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
            case errors.SchemaValidationError() | TypeError() | ValueError() if mining:
                return reject(state, "invalid_config", str(exc), writer)
            case _:
                return finish_error(state, ("failed", type(exc).__name__, str(exc)), writer)
    finally:
        if writer is not None:
            writer.close()  # 幂等兜底
        if slot is not None:
            slot.release(state.run_id)
        if (
            kronos_offload_attempt is not None
            and restore_kronos_if_needed(config, kronos_offload_attempt) is False
        ):
            print(
                f"WARNING: kronos restore failed after run {state.run_id}; "
                "daytime dry-run has no live signal until it is restored",
                file=sys.stderr,
            )


def _safe_identifier(value: str) -> bool:
    return bool(value) and ".." not in value and all(c.isalnum() or c in "._-" for c in value)


def _show_run(reports_root: Path, run_id: str) -> int:
    if not _safe_identifier(run_id):
        return EXIT_REJECTED
    path = reports_root / "generation" / run_id / "run.json"
    if not path.is_file():
        return EXIT_REJECTED
    run_store.load_run(path)
    payload: canonical.JSONValue = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return EXIT_OK


def _show_factor(reports_root: Path, factor_id: str) -> int:
    generation_root = reports_root / "generation"
    if not generation_root.is_dir() or not _safe_identifier(factor_id):
        return EXIT_REJECTED
    occurrences = []
    for run_dir in sorted(generation_root.iterdir()):
        factor_path = run_dir / "factors" / f"{factor_id}.json"
        run_path = run_dir / "run.json"
        if factor_path.is_file() and run_path.is_file():
            run = run_store.load_run(run_path)
            dto = factor_store.read(factor_path)
            occurrences.append((factor_path, run, dto.definition_digest))
    if not occurrences:
        return EXIT_REJECTED
    occurrences.sort(key=lambda item: (item[1].finished_at, item[1].run_id))
    if len({item[2] for item in occurrences}) != 1:
        raise errors.FactorStoreError(
            f"factor occurrences disagree on definition_digest: {factor_id}"
        )
    selected_path, _, _ = occurrences[-1]
    payload = json.loads(selected_path.read_text(encoding="utf-8"))
    payload["occurrences"] = [
        {
            "finished_at": canonical.utc_iso(run.finished_at),
            "run_id": run.run_id,
            "status": run.status,
        }
        for _, run, _ in occurrences
    ]
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return EXIT_OK


def main(
    argv: Sequence[str] | None = None,
    *,
    reports_root: Path | None = None,
    lake_root: Path | None = None,
) -> int:
    """Run the Phase-1 CLI and return a stable process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    selected_reports_root = reports_root or Path(__file__).resolve().parents[3] / "reports"
    try:
        match args.command:
            case "seed" | "mine":
                return _run_generation(args, selected_reports_root, lake_root)
            case "show":
                return (
                    _show_run(selected_reports_root, args.run)
                    if args.run is not None
                    else _show_factor(selected_reports_root, args.factor)
                )
            case unknown:
                parser.error(f"unknown command: {unknown}")
    except errors.UnknownSchemaVersionError as exc:
        print(exc, file=sys.stderr)
        return EXIT_REJECTED
    except (errors.FactorFactoryError, OSError, ValueError, UnicodeError) as exc:
        print(exc, file=sys.stderr)
        return EXIT_FAILED
