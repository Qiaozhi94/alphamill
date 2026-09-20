from __future__ import annotations

import argparse
import io
import json
import os
import platform
import socket
import sys
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Literal, TypeAlias

from alphamill.factor_factory import canonical, errors
from alphamill.factor_factory.generators import base, binding, gpu_slot
from alphamill.factor_factory.generators.egress_guard import install_egress_guard
from alphamill.factor_factory.generators.manual import seeds as manual_seeds
from alphamill.factor_factory.generators.mining_capability import require_mining_capabilities
from alphamill.factor_factory.generators.write_guard import install_write_path_guard
from alphamill.factor_factory.mine_config import DEFAULT_MINE_CONFIG, load_config
from alphamill.factor_factory.registry import factor_store, run_store

EXIT_OK: Final = 0
EXIT_FAILED: Final = 1
EXIT_REJECTED: Final = 2
_EMPTY_CONFIG_DIGEST: Final = canonical.sha256_prefixed_bytes(canonical.canonical_json_bytes({}))
_MANUAL_CODE_DIGEST: Final = canonical.sha256_prefixed_bytes(
    canonical.canonical_json_bytes(
        {"generator": "manual", "version": manual_seeds.MANUAL_GENERATOR_VERSION}
    )
)
_Outcome: TypeAlias = tuple[Literal["completed", "rejected", "failed"], str, str | None]


@dataclass(frozen=True, slots=True)
class _SeedState:
    run_id: str
    run_dir: Path
    started_at: datetime
    seed: int
    binding: binding.SnapshotBinding | None = None
    config_digest: str = _EMPTY_CONFIG_DIGEST
    window: base.Window | None = None
    universe: run_store.UniverseSummary | None = None
    counts: base.GenerationCounts = base.GenerationCounts(0, base.RejectionCounts(), 0)
    device: Literal["cpu", "cuda"] = "cpu"
    vram_limit_gb: float | None = None


def build_parser() -> argparse.ArgumentParser:
    """Build the generation CLI parser."""
    parser = argparse.ArgumentParser(prog="alphamill-generate")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("seed", "mine"):
        command = commands.add_parser(name)
        command.add_argument("--generator", choices=("manual",), required=True)
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


def _manifest(state: _SeedState, outcome: _Outcome) -> run_store.GenerationRun:
    status, termination, reason = outcome
    return run_store.GenerationRun(
        schema_version=run_store.RUN_SCHEMA_VERSION,
        run_id=state.run_id,
        generator="manual",
        engine=run_store.EngineInfo(
            vendor_commit=None,
            code_digest=_MANUAL_CODE_DIGEST,
            dependencies={"alphamill": "0.1.0", "python": platform.python_version()},
        ),
        binding=state.binding,
        seed=state.seed,
        config_digest=state.config_digest,
        device=state.device,
        hostname=socket.gethostname(),
        vram_limit_gb=state.vram_limit_gb,
        universe=state.universe,
        tier_level="manual",
        window=state.window,
        objective=run_store.ObjectiveInfo(
            turnover_penalty_lambda=0.0,
            reachability_min_trades_90d=30,
            cost_model={},
            min_after_cost_return=0.0,
        ),
        counts=state.counts,
        pool=None,
        started_at=state.started_at,
        finished_at=datetime.now(UTC),
        status=status,
        termination=termination,
        reason=reason,
    )


def _finish_error(state: _SeedState, outcome: _Outcome) -> int:
    try:
        run_store.finalize_run(state.run_dir, _manifest(state, outcome))
    except (errors.FactorFactoryError, OSError) as exc:
        print(f"cannot publish terminal run: {exc}", file=sys.stderr)
    print(outcome[2], file=sys.stderr)
    return EXIT_REJECTED if outcome[0] == "rejected" else EXIT_FAILED


def _reject(state: _SeedState, termination: str, reason: str) -> int:
    return _finish_error(state, ("rejected", termination, reason))


def _event_stream(descriptor: int, mode: str, buffering: int = -1) -> io.FileIO:
    return io.FileIO(descriptor, mode=mode, closefd=True)


def _run_generation(args: argparse.Namespace, reports_root: Path, lake_root: Path | None) -> int:
    mining = args.command == "mine"
    run_id = run_store.new_run_id("manual")
    run_dir = run_store.generation_run_dir(run_id, reports_root=reports_root)
    state = _SeedState(run_id, run_dir, datetime.now(UTC), args.seed)
    slot: gpu_slot.GpuSlot | None = None
    binding_path: Path | None = args.binding
    if binding_path is None:
        return _reject(state, "missing_binding", "--binding is required")
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
        if mining and args.config is not None and "tier_level" not in supplied_config:
            return _reject(state, "unknown_tier", "tier_level is required in --config")
        quota = args.quota if mining else base.DEFAULT_SEED_QUOTA
        config = {
            **(DEFAULT_MINE_CONFIG if mining else {}),
            **supplied_config,
            "generator": "manual",
            "quota": quota,
            "window": window_config,
        }
        universe = run_store.UniverseSummary(
            pair_count=len(validated.universe_ledger.universe_at(validated.resolved.cutoff_time)),
            symbol_map_digest=validated.resolved.symbol_map_digest,
            universe_digest=validated.resolved.universe.digest,
            source=validated.source.mode,
        )
        state = replace(
            state,
            binding=validated.source,
            config_digest=canonical.sha256_prefixed_bytes(canonical.canonical_json_bytes(config)),
            window=window,
            universe=universe,
        )
        if mining and config.get("tier_level") != "manual":
            return _reject(state, "unknown_tier", "tier_level is missing or unknown")
        if mining:
            slot_config = gpu_slot.GpuSlotConfig(
                vram_limit_gb=float(config["vram_limit_gb"]),
                window_start=str(config["training_window_start"]),
                window_end=str(config["training_window_end"]),
                window_tz=str(config["training_window_tz"]),
                queue_timeout_s=int(config["queue_timeout_s"]),
            )
            require_mining_capabilities(require_cuda=not args.allow_cpu)
            now = datetime.now(UTC)
            window_open = gpu_slot.in_training_window(
                now,
                window_start=slot_config.window_start,
                window_end=slot_config.window_end,
                window_tz=slot_config.window_tz,
            )
            if not window_open and not args.allow_offhours:
                return _reject(
                    state, "outside_training_window", "outside configured training window"
                )
            if not args.allow_cpu:
                reading = gpu_slot.query_vram()
                if not gpu_slot.vram_is_sufficient(reading, limit_gb=slot_config.vram_limit_gb):
                    return _reject(
                        state, "cuda_unavailable", "CUDA VRAM is unavailable or insufficient"
                    )
                state = replace(state, device="cuda", vram_limit_gb=slot_config.vram_limit_gb)
                candidate_slot = gpu_slot.GpuSlot(
                    locks_dir=reports_root / ".locks", config=slot_config
                )
                candidate_slot.acquire(state.run_id, ignore_window=args.allow_offhours)
                slot = candidate_slot
        request = base.GenerationRequest(
            generator="manual",
            binding=validated.source,
            seed=state.seed,
            window=window,
            config=config,
            quota=quota,
        )
        with (
            install_egress_guard(),
            install_write_path_guard(state.run_dir, reports_root=reports_root),
        ):
            result = manual_seeds.ManualGenerator(run_id=state.run_id).produce(request)
            state = replace(state, counts=result.counts)
            for factor in result.factors:
                factor_store.write(state.run_dir, factor)
            state = replace(state, config_digest=run_store.write_config(state.run_dir, config))
            original_fdopen = os.fdopen
            os.fdopen = _event_stream
            try:
                run_store.finalize_run(
                    state.run_dir, _manifest(state, ("completed", "normal", None))
                )
            finally:
                os.fdopen = original_fdopen
        return EXIT_OK
    except (errors.FactorFactoryError, OSError, RuntimeError, TypeError, ValueError) as exc:
        match exc:
            case gpu_slot.GpuQueueTimeoutError():
                return _reject(state, "queue_timeout", str(exc))
            case errors.MiningCapabilityError():
                return _reject(state, "capability_unavailable", str(exc))
            case errors.BindingValidationError():
                return _reject(state, "invalid_binding", str(exc))
            case errors.UnknownSchemaVersionError():
                return _reject(state, "unknown_schema_version", str(exc))
            case errors.SchemaValidationError() | TypeError() | ValueError() if mining:
                return _reject(state, "invalid_config", str(exc))
            case _:
                return _finish_error(state, ("failed", type(exc).__name__, str(exc)))
    finally:
        if slot is not None:
            slot.release(state.run_id)


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
