from __future__ import annotations

import argparse
import io
import json
import os
import platform
import socket
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal, TypeAlias

from alphamill.factor_factory import canonical, errors
from alphamill.factor_factory.generators import base, binding
from alphamill.factor_factory.generators.egress_guard import install_egress_guard
from alphamill.factor_factory.generators.manual.seeds import (
    MANUAL_GENERATOR_VERSION,
    ManualGenerator,
)
from alphamill.factor_factory.generators.write_guard import install_write_path_guard
from alphamill.factor_factory.registry import factor_store, run_store

EXIT_OK: Final = 0
EXIT_FAILED: Final = 1
EXIT_REJECTED: Final = 2

_DEFAULT_CONFIG: Final[Mapping[str, canonical.JSONValue]] = MappingProxyType({})
_EMPTY_CONFIG_DIGEST: Final = canonical.sha256_prefixed_bytes(canonical.canonical_json_bytes({}))
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


def build_parser() -> argparse.ArgumentParser:
    """Build the Phase-1 parser containing only ``seed`` and ``show``."""
    parser = argparse.ArgumentParser(prog="alphamill-generate")
    commands = parser.add_subparsers(dest="command", required=True)
    seed = commands.add_parser("seed")
    seed.add_argument("--generator", choices=("manual",), required=True)
    seed.add_argument("--binding", type=Path)
    seed.add_argument("--seed", type=int, required=True)
    seed.add_argument(
        "--window", choices=(base.DEFAULT_WINDOW_PRESET,), default=base.DEFAULT_WINDOW_PRESET
    )
    seed.add_argument("--config", type=Path)
    show = commands.add_parser("show")
    selector = show.add_mutually_exclusive_group(required=True)
    selector.add_argument("--run")
    selector.add_argument("--factor")
    return parser


def _load_config(path: Path | None) -> dict[str, canonical.JSONValue]:
    if path is None:
        return dict(_DEFAULT_CONFIG)
    try:
        payload: canonical.JSONValue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise errors.SchemaValidationError(f"config file cannot be read: {path}") from exc
    if not isinstance(payload, dict):
        raise errors.SchemaValidationError("config must be a JSON object")
    return payload


def _manifest(state: _SeedState, outcome: _Outcome) -> run_store.GenerationRun:
    status, termination, reason = outcome
    return run_store.GenerationRun(
        schema_version=run_store.RUN_SCHEMA_VERSION,
        run_id=state.run_id,
        generator="manual",
        engine=run_store.EngineInfo(
            vendor_commit=None,
            code_digest=canonical.sha256_prefixed_bytes(
                canonical.canonical_json_bytes(
                    {"generator": "manual", "version": MANUAL_GENERATOR_VERSION}
                )
            ),
            dependencies={"alphamill": "0.1.0", "python": platform.python_version()},
        ),
        binding=state.binding,
        seed=state.seed,
        config_digest=state.config_digest,
        device="cpu",
        hostname=socket.gethostname(),
        vram_limit_gb=None,
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


def _finish_error(state: _SeedState, outcome: _Outcome, exit_code: int) -> int:
    try:
        run_store.finalize_run(state.run_dir, _manifest(state, outcome))
    except (errors.FactorFactoryError, OSError) as exc:
        print(f"cannot publish terminal run: {exc}", file=sys.stderr)
    print(outcome[2], file=sys.stderr)
    return exit_code


def _event_stream(descriptor: int, mode: str, buffering: int = -1) -> io.FileIO:
    return io.FileIO(descriptor, mode=mode, closefd=True)


def _run_seed(args: argparse.Namespace, reports_root: Path, lake_root: Path | None) -> int:
    run_id = run_store.new_run_id("manual")
    state = _SeedState(
        run_id,
        run_store.generation_run_dir(run_id, reports_root=reports_root),
        datetime.now(UTC),
        args.seed,
    )
    binding_path: Path | None = args.binding
    if binding_path is None:
        return _finish_error(
            state, ("rejected", "missing_binding", "--binding is required"), EXIT_REJECTED
        )
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
        config = {
            **_load_config(args.config),
            "generator": "manual",
            "quota": base.DEFAULT_SEED_QUOTA,
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
        request = base.GenerationRequest(
            generator="manual",
            binding=validated.source,
            seed=state.seed,
            window=window,
            config=config,
            quota=base.DEFAULT_SEED_QUOTA,
        )
        with (
            install_egress_guard(),
            install_write_path_guard(state.run_dir, reports_root=reports_root),
        ):
            result = ManualGenerator(run_id=state.run_id).produce(request)
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
            case errors.BindingValidationError():
                outcome = ("rejected", "invalid_binding", str(exc))
                exit_code = EXIT_REJECTED
            case errors.UnknownSchemaVersionError():
                outcome = ("rejected", "unknown_schema_version", str(exc))
                exit_code = EXIT_REJECTED
            case _:
                outcome = ("failed", type(exc).__name__, str(exc))
                exit_code = EXIT_FAILED
        return _finish_error(state, outcome, exit_code)


def _safe_identifier(value: str) -> bool:
    characters_are_safe = all(character.isalnum() or character in "._-" for character in value)
    return bool(value) and ".." not in value and characters_are_safe


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
            case "seed":
                return _run_seed(args, selected_reports_root, lake_root)
            case "show":
                if args.run is not None:
                    return _show_run(selected_reports_root, args.run)
                return _show_factor(selected_reports_root, args.factor)
            case unknown:
                parser.error(f"unknown command: {unknown}")
    except errors.UnknownSchemaVersionError as exc:
        print(exc, file=sys.stderr)
        return EXIT_REJECTED
    except (errors.FactorFactoryError, OSError, ValueError, UnicodeError) as exc:
        print(exc, file=sys.stderr)
        return EXIT_FAILED
