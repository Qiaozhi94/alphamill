"""F012 run.json v2 与 v1 双读（AC-007 / DR-001，文档检视 D01/D22/D29）。"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from alphamill.factor_factory.errors import SchemaValidationError, UnknownSchemaVersionError
from alphamill.factor_factory.generators.base import (
    GenerationCounts,
    GenerationRequest,
    GenerationResult,
    RejectionCounts,
    Window,
)
from alphamill.factor_factory.generators.binding import SnapshotRefBinding
from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG
from alphamill.factor_factory.registry import factor_store, run_schema, run_store
from alphamill.factor_factory.registry.run_schema import (
    BudgetInfo,
    EngineInfo,
    GenerationRun,
    ObjectiveInfo,
    UniverseSummary,
)

STARTED = datetime(2026, 9, 27, 14, 0, tzinfo=UTC)
FINISHED = datetime(2026, 9, 27, 15, 0, tzinfo=UTC)


def _run(**overrides) -> GenerationRun:
    base = GenerationRun(
        schema_version=run_schema.RUN_SCHEMA_VERSION,
        run_id="alphagen-20260927T140000000000Z-1234abcd",
        generator="alphagen",
        engine=EngineInfo(
            vendor_commit="abc123", code_digest="sha256:" + "a" * 64, dependencies={}
        ),
        binding=SnapshotRefBinding(mode="snapshot", research_snapshot_id="snapshot-001"),
        seed=7,
        config_digest="sha256:" + "b" * 64,
        device="cuda",
        hostname="qiaozhi-lt",
        vram_limit_gb=6.0,
        kronos_offload={"action": "stopped"},
        universe=UniverseSummary(
            pair_count=26,
            symbol_map_digest="sha256:" + "c" * 64,
            universe_digest="sha256:" + "d" * 64,
            source="explicit",
        ),
        tier_level="L0",
        window=Window(
            start=datetime(2024, 9, 10, tzinfo=UTC),
            end=datetime(2026, 9, 10, tzinfo=UTC),
            resample="1h",
        ),
        objective=ObjectiveInfo(
            turnover_penalty_lambda=0.05,
            reachability_min_trades_90d=30,
            cost_model={"taker_fee_bps": 5.0},
            min_after_cost_return=0.0,
            position_rule="cs_median",
        ),
        counts=GenerationCounts(proposed=5, rejected=RejectionCounts(reachability=2), registered=3),
        pool=None,
        started_at=STARTED,
        finished_at=FINISHED,
        status="completed",
        termination="normal",
        reason=None,
        budget=BudgetInfo(quota=3, total_timesteps=8192, pool_capacity=10),
        stop_reason="quota_reached",
        evaluations=412,
    )
    return replace(base, **overrides)


def test_current_write_version_is_two_and_run_store_reexports_schema_names() -> None:
    assert run_schema.RUN_SCHEMA_VERSION == 2
    assert set(run_schema.RUN_SCHEMA_VERSIONS) == {1, 2}
    for name in ("RUN_SCHEMA_VERSION", "RunStatus", "TierLevel", "GenerationRun", "EngineInfo"):
        assert getattr(run_store, name) is getattr(run_schema, name)
    assert run_store.UniverseSummary is run_schema.UniverseSummary
    assert run_store.load_run is run_schema.load_run


def test_v2_manifest_round_trips_with_new_fields(tmp_path: Path) -> None:
    run = _run()
    run_store.finalize_run(tmp_path, run)

    on_disk = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    loaded = run_store.load_run(tmp_path / "run.json")

    assert on_disk["schema_version"] == 2
    assert on_disk["budget"] == {"quota": 3, "total_timesteps": 8192, "pool_capacity": 10}
    assert on_disk["stop_reason"] == "quota_reached"
    assert on_disk["objective"]["position_rule"] == "cs_median"
    assert loaded == run


def test_v1_manifest_is_still_readable_with_defaults(tmp_path: Path) -> None:
    payload = run_store._payload(_run(generator="manual", tier_level="manual"))
    for key in ("budget", "stop_reason", "evaluations"):
        payload.pop(key)
    payload["objective"].pop("position_rule")
    payload["schema_version"] = 1
    (tmp_path / "run.json").write_text(json.dumps(payload), encoding="utf-8")

    loaded = run_store.load_run(tmp_path / "run.json")

    assert loaded.schema_version == 1
    assert (loaded.budget, loaded.stop_reason, loaded.evaluations) == (None, None, None)
    assert loaded.objective.position_rule == "sign"


def test_v2_manifest_missing_new_fields_is_rejected(tmp_path: Path) -> None:
    payload = run_store._payload(_run())
    payload.pop("budget")
    (tmp_path / "run.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SchemaValidationError):
        run_store.load_run(tmp_path / "run.json")


def test_unknown_schema_version_is_rejected(tmp_path: Path) -> None:
    payload = run_store._payload(_run())
    payload["schema_version"] = 3
    (tmp_path / "run.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(UnknownSchemaVersionError):
        run_store.load_run(tmp_path / "run.json")


@pytest.mark.parametrize(
    ("status", "stop_reason", "reason"),
    [
        ("completed", "window_closed", None),
        ("completed", "interrupted", None),
        ("partial", "quota_reached", "已入册 3/3：quota_reached"),
        ("partial", "budget_exhausted", "已入册 1/3：budget_exhausted"),
    ],
)
def test_stop_reason_must_match_status(tmp_path, status, stop_reason, reason) -> None:
    with pytest.raises(SchemaValidationError, match="stop_reason"):
        run_store.finalize_run(
            tmp_path, _run(status=status, stop_reason=stop_reason, reason=reason)
        )


def test_partial_run_with_window_closed_is_valid(tmp_path: Path) -> None:
    run = _run(
        status="partial",
        stop_reason="window_closed",
        termination="window_closed",
        reason="已入册 2/3：window_closed",
    )
    run_store.finalize_run(tmp_path, run)
    assert run_store.load_run(tmp_path / "run.json").stop_reason == "window_closed"


def _manual_factor(run_dir: Path) -> Path:
    factor = factor_store.build_factor(
        hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
        name="unit-factor",
        generator="manual",
        generator_version="1",
        scope="time_series",
        expression=("feature:close", "neg"),
        params={},
        feature_map={"close": 0},
        run_id="run-a",
        created_at=STARTED,
    )
    return factor_store.write(run_dir, factor)


def test_factor_store_loads_factors_of_a_completed_v2_run(tmp_path: Path) -> None:
    """检视 D01：原先 load 要求 run.json schema_version == 1，v2 运行的全部因子都会被拒。"""
    path = _manual_factor(tmp_path)
    run_store.finalize_run(tmp_path, _run(generator="manual", tier_level="manual"))

    assert factor_store.load(path).generator == "manual"


def test_factor_store_still_refuses_a_partial_run(tmp_path: Path) -> None:
    from alphamill.factor_factory.errors import FactorStoreError

    path = _manual_factor(tmp_path)
    run_store.finalize_run(
        tmp_path,
        _run(status="partial", stop_reason="interrupted", reason="已入册 0/3：interrupted"),
    )
    with pytest.raises(FactorStoreError):
        factor_store.load(path)


def test_request_and_result_gain_optional_fields_with_defaults() -> None:
    fields_request = GenerationRequest.__dataclass_fields__
    fields_result = GenerationResult.__dataclass_fields__
    assert fields_request["panel"].default is None
    for name in ("stop_reason", "evaluations", "budget"):
        assert fields_result[name].default is None


# ------------------------------------------------------------------ 编译器组装（T010）


def _alphagen_factor(run_dir: Path, **kwargs) -> Path:
    factor = factor_store.build_factor(
        hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
        name="alphagen",
        generator="alphagen",
        generator_version="vendor-test",
        scope="time_series",
        expression=("feature:ohlcv_1m.close@1h", "mean:5"),
        params={},
        feature_map={"ohlcv_1m.close@1h": 0},
        run_id="alphagen-run",
        created_at=STARTED,
        **kwargs,
    )
    return factor_store.write(run_dir, factor)


def test_full_registry_compiles_manual_and_alphagen() -> None:
    from alphamill.factor_factory.registry.default_compilers import full_registry

    registry = full_registry()

    assert registry.require("manual") is not None
    assert registry.require("alphagen") is not None


def test_alphagen_factor_builds_and_loads_with_default_compilers(tmp_path: Path) -> None:
    """检视 D18/D28：缺省编译器只有 manual 时，alphagen 因子 build/load 都会报未注册。"""
    path = _alphagen_factor(tmp_path)
    run_store.finalize_run(tmp_path, _run())

    loaded = factor_store.load(path)

    assert loaded.generator == "alphagen"


def test_importing_factor_store_does_not_pull_in_the_alphagen_adapter() -> None:
    """惰性组装：factor_store 顶层不导入 adapter（否则三者成环）。"""
    import subprocess
    import sys

    probe = (
        "import sys; import alphamill.factor_factory.registry.factor_store; "
        "print('alphamill.factor_factory.generators.alphagen_adapter' in sys.modules)"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "False"
