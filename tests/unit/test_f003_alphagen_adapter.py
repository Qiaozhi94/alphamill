"""F003 AlphaGen 适配器测试：FR-004 / AC-004。"""

from __future__ import annotations

import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.errors import (
    FactorCompilationError,
    FeatureMapIntegrityError,
    SchemaValidationError,
)
from alphamill.factor_factory.factor import FactorDef, FactorScope
from alphamill.factor_factory.generators import alphagen_adapter
from alphamill.factor_factory.generators.alphagen_adapter import (
    ALPHAGEN_GENERATOR,
    compile_alphagen_expression,
    data_columns_from_expression,
    expression_from_factor,
    register_alphagen_compiler,
)
from alphamill.factor_factory.generators.expression_compiler import compile_postfix
from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG
from alphamill.factor_factory.registry.compiler_registry import CompileContext, CompilerRegistry
from alphamill.factor_factory.registry.factor_store import build_factor, load, write

CREATED_AT = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
FEATURE_MAP = {"close": 0}
RANKED_RETURN = ("feature:close", "return:1", "cs_rank")


def _registry() -> CompilerRegistry:
    registry = CompilerRegistry()
    register_alphagen_compiler(registry)
    return registry


def _factor(
    expression: tuple[str, ...] = RANKED_RETURN,
    scope: FactorScope = "cross_sectional",
) -> FactorDef:
    return build_factor(
        hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
        name="alphagen-unit-factor",
        generator=ALPHAGEN_GENERATOR,
        generator_version="vendor-259687e",
        scope=scope,
        expression=expression,
        params={},
        feature_map=FEATURE_MAP,
        run_id="run-alphagen",
        created_at=CREATED_AT,
        compilers=_registry(),
    )


def _panel() -> pd.DataFrame:
    timestamps = pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True)
    index = pd.MultiIndex.from_product(
        [timestamps, ["BTC", "ETH", "SOL"]], names=("timestamp", "pair")
    )
    return pd.DataFrame(
        {
            "close": [10.0, 20.0, 30.0, 20.0, 10.0, 60.0],
            "__in_universe__": [True, True, False, True, True, False],
        },
        index=index,
    )


def test_adapter_matches_postfix_compiler_on_same_panel() -> None:
    panel = _panel()
    adapter_compute = compile_alphagen_expression(
        RANKED_RETURN,
        scope="cross_sectional",
        feature_map=FEATURE_MAP,
    )
    postfix_compute = compile_postfix(
        CompileContext(
            generator=ALPHAGEN_GENERATOR,
            expression=RANKED_RETURN,
            scope="cross_sectional",
            params={},
            data_columns=("close",),
            feature_map=FEATURE_MAP,
            resolver=None,
        )
    )

    actual = adapter_compute(panel)
    expected = postfix_compute(panel)

    pd.testing.assert_series_equal(actual, expected, check_exact=False, rtol=1e-12, atol=1e-12)


def test_expression_from_factor_round_trips_build_factor() -> None:
    factor = _factor()

    assert expression_from_factor(factor) == RANKED_RETURN


def test_data_columns_preserve_first_appearance_and_reject_unknown_feature() -> None:
    expression = ("feature:volume", "neg", "feature:close", "feature:volume")

    assert data_columns_from_expression(expression, feature_map={"close": 0, "volume": 1}) == (
        "volume",
        "close",
    )
    with pytest.raises(FeatureMapIntegrityError, match="volume"):
        data_columns_from_expression(("feature:volume",), feature_map=FEATURE_MAP)


def test_compile_rejects_feature_absent_from_feature_map() -> None:
    with pytest.raises(FeatureMapIntegrityError, match="volume"):
        compile_alphagen_expression(
            ("feature:volume",), scope="time_series", feature_map=FEATURE_MAP
        )


def test_cross_sectional_rows_without_membership_are_no_signal() -> None:
    timestamps = pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True)
    index = pd.MultiIndex.from_product(
        [timestamps, ["BTC", "ETH", "SOL"]], names=("timestamp", "pair")
    )
    panel = pd.DataFrame(
        {
            "close": [10.0, 20.0, 30.0, 30.0, 10.0, 20.0],
            "__in_universe__": pd.array([True, False, pd.NA, True, False, pd.NA], dtype="boolean"),
        },
        index=index,
    )
    compute = compile_alphagen_expression(
        ("feature:close", "cs_rank"),
        scope="cross_sectional",
        feature_map=FEATURE_MAP,
    )

    result = compute(panel)

    members = panel["__in_universe__"].fillna(False).astype(bool)
    assert np.isfinite(result[members]).all()
    assert result[~members].isna().all()
    assert not result[members].eq(0.0).any()


def test_time_series_compute_preserves_index_and_input_frame() -> None:
    index = pd.date_range("2026-01-01", periods=3, tz="UTC")
    frame = pd.DataFrame({"close": [1.0, 2.0, 4.0]}, index=index)
    original = frame.copy(deep=True)
    compute = compile_alphagen_expression(
        ("feature:close", "return:1"),
        scope="time_series",
        feature_map=FEATURE_MAP,
    )

    result = compute(frame)

    assert result.index.identical(frame.index)
    assert result.iloc[1] == pytest.approx(1.0)
    pd.testing.assert_frame_equal(frame, original)


def test_registered_compiler_restores_executable_persisted_factor(tmp_path: Path) -> None:
    registry = _registry()
    factor = _factor(("feature:close", "neg"), "time_series")
    path = write(tmp_path / "run-alphagen", factor)
    frame = pd.DataFrame(
        {"close": [1.0, -2.0]},
        index=pd.date_range("2026-01-01", periods=2, tz="UTC"),
    )

    restored = load(
        path,
        compilers=registry,
        require_completed=False,
    )

    pd.testing.assert_series_equal(restored.compute(frame), factor.compute(frame))
    assert restored.generator == ALPHAGEN_GENERATOR


def test_register_alphagen_compiler_rejects_duplicate_registration() -> None:
    registry = CompilerRegistry()
    register_alphagen_compiler(registry)

    with pytest.raises(SchemaValidationError, match="alphagen"):
        register_alphagen_compiler(registry)


def test_compile_rejects_operator_absent_from_registry() -> None:
    with pytest.raises(FactorCompilationError, match="future_mean"):
        compile_alphagen_expression(
            ("feature:close", "future_mean"),
            scope="time_series",
            feature_map=FEATURE_MAP,
        )


@pytest.mark.parametrize(
    "meta",
    (
        {},
        {"expression": "feature:close"},
        {"expression": []},
        {"expression": ["feature:close", 1]},
    ),
)
def test_expression_from_factor_rejects_missing_or_malformed_meta(
    meta: dict[str, JSONValue],
) -> None:
    factor = replace(_factor(("feature:close",), "time_series"), meta=meta)

    with pytest.raises(FactorCompilationError, match="meta.*expression"):
        expression_from_factor(factor)


def test_adapter_exposes_vendor_root_without_importing_vendor_modules() -> None:
    vendor_root = str(Path(alphagen_adapter.__file__).with_name("alphagen_vendor").resolve())

    assert vendor_root in sys.path
