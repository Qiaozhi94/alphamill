"""F003 因子存储测试：DR-002 / AC-009 / AC-012。"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from alphamill.factor_factory.errors import (
    CompilerNotRegisteredError,
    FactorCompilationError,
    FactorStoreError,
    FeatureMapIntegrityError,
    SchemaValidationError,
    UnknownSchemaVersionError,
)
from alphamill.factor_factory.factor import FactorDef, FactorScope
from alphamill.factor_factory.generators.expression_compiler import (
    compile_postfix,
    referenced_features,
)
from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG
from alphamill.factor_factory.registry.compiler_registry import DEFAULT_COMPILERS, CompilerRegistry
from alphamill.factor_factory.registry.factor_store import (
    FACTOR_DTO_FIELDS,
    build_factor,
    feature_map_digest,
    load,
    read,
    write,
)

CREATED_AT = datetime(2026, 9, 18, 12, 0, tzinfo=UTC)
FEATURE_MAP = {"close": 0}
META_FIELDS = {
    "schema_version",
    "expression",
    "definition_digest",
    "generator_version",
    "feature_map",
    "feature_map_digest",
    "run_id",
    "created_at",
    "hypothesis_source",
}


def _build(expression: tuple[str, ...], scope: FactorScope = "time_series") -> FactorDef:
    return build_factor(
        hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
        name="unit-factor",
        generator="manual",
        generator_version="1",
        scope=scope,
        expression=expression,
        params={},
        feature_map=FEATURE_MAP,
        run_id="run-a",
        created_at=CREATED_AT,
    )


def _round_trip(run_dir: Path, expression: tuple[str, ...], scope: FactorScope) -> FactorDef:
    factor = _build(expression, scope)
    path = write(run_dir, factor)
    dto = read(path)

    assert set(vars(dto)) == FACTOR_DTO_FIELDS
    loaded = load(path, require_completed=False)
    assert set(loaded.meta) == META_FIELDS
    return loaded


def _persisted_factor(tmp_path: Path) -> Path:
    return write(tmp_path / "run-a", _build(("feature:close", "neg")))


def _identity_factor(name: str, params: dict[str, int], feature_map: dict[str, int]) -> FactorDef:
    return build_factor(
        hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
        name=name,
        generator="manual",
        generator_version="1",
        scope="time_series",
        expression=("feature:close", "neg"),
        params=params,
        feature_map=feature_map,
        run_id="run-a",
        created_at=CREATED_AT,
    )


def test_round_trip_neg_returns_executable_factor(tmp_path: Path) -> None:
    factor = _round_trip(tmp_path / "run-a", ("feature:close", "neg"), "time_series")
    index = pd.date_range("2026-01-01", periods=3, tz="UTC")
    frame = pd.DataFrame({"close": [1.0, -2.0, 3.0]}, index=index)

    result = factor.compute(frame)

    expected = pd.Series([-1.0, 2.0, -3.0], index=index, name="close")
    pd.testing.assert_series_equal(result, expected)
    assert factor.data_columns == ["close"]


def test_round_trip_pct_change_groups_cross_section_by_pair(tmp_path: Path) -> None:
    factor = _round_trip(
        tmp_path / "run-a",
        ("feature:close", "pct_change:1"),
        "cross_sectional",
    )
    timestamps = pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True)
    index = pd.MultiIndex.from_product([timestamps, ["BTC", "ETH"]], names=("timestamp", "pair"))
    frame = pd.DataFrame(
        {"close": [10.0, 20.0, 15.0, 10.0], "__in_universe__": True},
        index=index,
    )

    result = factor.compute(frame)

    expected = pd.Series([float("nan"), float("nan"), 0.5, -0.5], index=index, name="close")
    pd.testing.assert_series_equal(result, expected)


def test_round_trip_cs_rank_masks_rows_outside_pit_universe(tmp_path: Path) -> None:
    factor = _round_trip(tmp_path / "run-a", ("feature:close", "cs_rank"), "cross_sectional")
    timestamps = pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True)
    index = pd.MultiIndex.from_product(
        [timestamps, ["BTC", "ETH", "SOL"]], names=("timestamp", "pair")
    )
    frame = pd.DataFrame(
        {
            "close": [10.0, 20.0, 1000.0, 30.0, 10.0, -1000.0],
            "__in_universe__": [True, True, False, True, True, False],
        },
        index=index,
    )

    result = factor.compute(frame)

    expected = pd.Series(
        [0.5, 1.0, float("nan"), 1.0, 0.5, float("nan")], index=index, name="close"
    )
    pd.testing.assert_series_equal(result, expected)


@pytest.mark.parametrize(
    ("token", "expected"),
    (
        ("return:1", [float("nan"), 1.0, 1.0]),
        ("rolling_std:2", [float("nan"), 2**-0.5, 2**0.5]),
    ),
)
def test_time_series_window_operators(token: str, expected: list[float]) -> None:
    factor = _build(("feature:close", token))
    index = pd.date_range("2026-01-01", periods=3, tz="UTC")
    frame = pd.DataFrame({"close": [1.0, 2.0, 4.0]}, index=index)

    result = factor.compute(frame)

    pd.testing.assert_series_equal(result, pd.Series(expected, index=index, name="close"))


def test_referenced_features_preserves_first_appearance_without_duplicates() -> None:
    expression = ("feature:volume", "neg", "feature:close", "feature:volume")

    result = referenced_features(expression)

    assert result == ("volume", "close")


def test_time_series_compute_rejects_non_utc_index() -> None:
    factor = _build(("feature:close",))
    frame = pd.DataFrame(
        {"close": [1.0]}, index=pd.date_range("2026-01-01", periods=1, tz="Europe/Berlin")
    )

    with pytest.raises(FactorCompilationError, match="UTC"):
        factor.compute(frame)


def test_identity_ignores_run_and_created_at_but_tracks_definition() -> None:
    first = _identity_factor("stable", {}, {"close": 0})
    second = build_factor(
        hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
        name="stable",
        generator="manual",
        generator_version="1",
        scope="time_series",
        expression=("feature:close", "neg"),
        params={},
        feature_map={"close": 0},
        run_id="run-b",
        created_at=CREATED_AT + timedelta(days=1),
    )

    assert first.meta["definition_digest"] == second.meta["definition_digest"]
    assert first.factor_id == second.factor_id

    variants = (
        _identity_factor("renamed", {}, {"close": 0}),
        _identity_factor("stable", {"lag": 1}, {"close": 0}),
        _identity_factor("stable", {}, {"volume": 0, "close": 1}),
    )
    assert all(
        item.meta["definition_digest"] != first.meta["definition_digest"] for item in variants
    )
    assert all(item.factor_id != first.factor_id for item in variants)


def test_read_rejects_extra_dto_key(tmp_path: Path) -> None:
    path = _persisted_factor(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["verdict"] = "pass"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SchemaValidationError):
        read(path)


def test_read_rejects_unknown_schema_version(tmp_path: Path) -> None:
    path = _persisted_factor(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["schema_version"] = 2
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(UnknownSchemaVersionError):
        read(path)


def test_read_rejects_factor_id_inconsistent_with_digest(tmp_path: Path) -> None:
    path = _persisted_factor(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["factor_id"] = "manual_deadbeefdead"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="factor_id"):
        read(path)


@pytest.mark.parametrize(
    "feature_map",
    ({"close": 1}, {"close": 0, "volume": 0}),
)
def test_feature_map_rejects_non_contiguous_or_duplicate_channels(
    feature_map: dict[str, int],
) -> None:
    with pytest.raises(FeatureMapIntegrityError):
        feature_map_digest(feature_map)


def test_feature_map_digest_is_stable_under_key_order() -> None:
    assert feature_map_digest({"close": 0, "volume": 1}) == feature_map_digest(
        {"volume": 1, "close": 0}
    )


def test_write_rejects_conflicting_feature_map_content(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-a"
    factor = _build(("feature:close", "neg"))
    digest = str(factor.meta["feature_map_digest"])
    feature_map_path = run_dir / "feature_maps" / f"{digest.removeprefix('sha256:')}.json"
    feature_map_path.parent.mkdir(parents=True)
    feature_map_path.write_text("{}", encoding="utf-8")

    with pytest.raises(FactorStoreError):
        write(run_dir, factor)

    assert not (run_dir / "factors" / f"{factor.factor_id}.json").exists()


def test_write_is_idempotent_and_uses_content_addressed_paths(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-a"
    factor = _build(("feature:close", "neg"))

    first = write(run_dir, factor)
    second = write(run_dir, factor)

    digest = str(factor.meta["feature_map_digest"]).removeprefix("sha256:")
    assert first == second == run_dir / "factors" / f"{factor.factor_id}.json"
    assert (run_dir / "feature_maps" / f"{digest}.json").is_file()


def test_load_accepts_completed_run_manifest(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-a"
    path = write(run_dir, _build(("feature:close", "neg")))
    (run_dir / "run.json").write_text(
        json.dumps({"schema_version": 1, "status": "completed"}), encoding="utf-8"
    )

    factor = load(path)

    assert factor.factor_id == read(path).factor_id


def test_load_rejects_feature_map_content_at_wrong_digest_path(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-a"
    factor = _build(("feature:close", "neg"))
    path = write(run_dir, factor)
    digest = str(factor.meta["feature_map_digest"]).removeprefix("sha256:")
    feature_path = run_dir / "feature_maps" / f"{digest}.json"
    feature_path.write_text(
        json.dumps({"schema_version": 1, "features": {"volume": 0}}), encoding="utf-8"
    )

    with pytest.raises(FeatureMapIntegrityError):
        load(path, require_completed=False)


def test_default_compiler_registry_contains_only_manual_phase_one_compiler() -> None:
    assert callable(DEFAULT_COMPILERS.require("manual"))
    with pytest.raises(CompilerNotRegisteredError):
        DEFAULT_COMPILERS.require("alphagen")


def test_build_factor_rejects_unknown_generator() -> None:
    with pytest.raises(CompilerNotRegisteredError):
        build_factor(
            hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
            name="unknown-generator",
            generator="alphagen",
            generator_version="1",
            scope="time_series",
            expression=("feature:close",),
            params={},
            feature_map=FEATURE_MAP,
            run_id="run-a",
            created_at=CREATED_AT,
        )


@pytest.mark.parametrize(
    "expression",
    (
        ("feature:close", "unknown"),
        ("feature:close", "rolling_std:0"),
        ("feature:close", "return:not-an-int"),
        ("neg",),
        ("feature:close", "feature:close"),
        ("feature:",),
    ),
)
def test_build_factor_rejects_malformed_postfix_expression(
    expression: tuple[str, ...],
) -> None:
    with pytest.raises(FactorCompilationError):
        _build(expression)


def test_build_factor_rejects_feature_missing_from_feature_map() -> None:
    with pytest.raises(FeatureMapIntegrityError):
        _build(("feature:volume",))


def test_load_requires_completed_run_by_default(tmp_path: Path) -> None:
    path = _persisted_factor(tmp_path)

    with pytest.raises(FactorStoreError, match="run.json"):
        load(path)


def test_compiler_registry_rejects_duplicate_registration() -> None:
    """注册表必须拒绝重复注册，而不是静默覆盖（否则后注册者悄悄换掉编译器）。"""
    registry = CompilerRegistry({"manual": compile_postfix})

    with pytest.raises(SchemaValidationError, match="already registered"):
        registry.register("manual", compile_postfix)

    assert registry.require("manual") is compile_postfix
