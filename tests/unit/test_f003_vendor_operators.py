from __future__ import annotations

from collections.abc import Callable
from datetime import UTC

import numpy as np
import pandas as pd
import pytest

from alphamill.factor_factory.generators.alphagen_adapter import compile_alphagen_expression
from alphamill.factor_factory.generators.expression_compiler import compile_postfix
from alphamill.factor_factory.registry.compiler_registry import CompileContext

FEATURE_MAP = {"left": 0, "right": 1}


def _panel() -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=4, tz=UTC)
    index = pd.MultiIndex.from_product([timestamps, ["A", "B", "C"]], names=("timestamp", "pair"))
    return pd.DataFrame(
        {
            "left": [1.0, 2.0, 5.0, 2.0, 4.0, 5.0, 3.0, 6.0, 5.0, 4.0, 8.0, 5.0],
            "right": [2.0, 1.0, 5.0, 4.0, 2.0, 5.0, 6.0, 3.0, 5.0, 8.0, 4.0, 5.0],
            "__in_universe__": [
                True,
                True,
                False,
                True,
                True,
                True,
                True,
                False,
                True,
                True,
                True,
                False,
            ],
        },
        index=index,
    )


def _compute(expression: tuple[str, ...]) -> pd.Series:
    context = CompileContext(
        generator="alphagen",
        expression=expression,
        scope="cross_sectional",
        params={},
        data_columns=("left", "right"),
        feature_map=FEATURE_MAP,
        resolver=None,
    )
    return compile_postfix(context)(_panel())


@pytest.mark.parametrize(
    ("expression", "expected"),
    (
        (("feature:left", "delta:1"), lambda values: values.groupby(level="pair").diff()),
        (
            ("feature:left", "sum:2"),
            lambda values: values.groupby(level="pair", sort=False, group_keys=False).transform(
                lambda group: group.rolling(2).sum()
            ),
        ),
        (
            ("feature:left", "mean:2"),
            lambda values: values.groupby(level="pair", sort=False, group_keys=False).transform(
                lambda group: group.rolling(2).mean()
            ),
        ),
        (
            ("feature:left", "std:2"),
            lambda values: values.groupby(level="pair", sort=False, group_keys=False).transform(
                lambda group: group.rolling(2).std()
            ),
        ),
        (("feature:left", "ref:1"), lambda values: values.groupby(level="pair").shift(1)),
        (("feature:left", "abs"), lambda values: values.abs()),
        (
            ("feature:left", "feature:right", "less"),
            lambda values: np.minimum(values, _panel()["right"]),
        ),
    ),
)
def test_vendor_operator_matches_hand_computed_pandas(
    expression: tuple[str, ...], expected: Callable[[pd.Series], pd.Series]
) -> None:
    panel = _panel()
    source = panel["left"]
    actual = _compute(expression)
    expected_series = expected(source)

    pd.testing.assert_series_equal(
        actual,
        expected_series.where(panel["__in_universe__"]),
        check_names=False,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_vendor_corr_is_pair_rolling_and_masks_non_members() -> None:
    panel = _panel()
    actual = _compute(("feature:left", "feature:right", "corr:2"))
    pieces: list[pd.Series] = []
    for _, left_values in panel["left"].groupby(level="pair", sort=False):
        right_values = panel["right"].loc[left_values.index]
        members = panel["__in_universe__"].loc[left_values.index]
        pieces.append(left_values.where(members).rolling(2).corr(right_values.where(members)))
    expected = pd.concat(pieces).reindex(panel.index)
    expected.loc[(pd.Timestamp("2026-01-03", tz="UTC"), "C")] = 0.0

    pd.testing.assert_series_equal(
        actual,
        expected.where(panel["__in_universe__"]),
        check_names=False,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_vendor_expression_round_trips_through_alphagen_adapter() -> None:
    panel = _panel()
    compute = compile_alphagen_expression(
        ("feature:left", "constant:-10", "add", "abs"),
        scope="cross_sectional",
        feature_map=FEATURE_MAP,
    )

    actual = compute(panel)

    assert (
        actual.loc[panel["__in_universe__"]]
        .eq((panel["left"] - 10).abs())
        .loc[panel["__in_universe__"]]
        .all()
    )
    assert actual.loc[~panel["__in_universe__"]].isna().all()


def test_every_registered_vendor_operator_executes_on_a_panel() -> None:
    unary = ("abs", "log")
    binary = ("add", "sub", "mul", "div", "greater", "less")
    rolling = (
        "delta",
        "ema",
        "mad",
        "max",
        "mean",
        "med",
        "min",
        "ref",
        "std",
        "sum",
        "var",
        "wma",
    )
    expressions = (
        *(("feature:left", name) for name in unary),
        *(("feature:left", "feature:right", name) for name in binary),
        *(("feature:left", f"{name}:2") for name in rolling),
        ("feature:left", "feature:right", "corr:2"),
        ("feature:left", "feature:right", "cov:2"),
    )

    for expression in expressions:
        result = _compute(expression)

        assert result.index.equals(_panel().index)
        assert result.loc[~_panel()["__in_universe__"]].isna().all()


def test_vendor_time_series_window_uses_a_utc_datetime_index() -> None:
    index = pd.date_range("2026-01-01", periods=3, tz=UTC)
    frame = pd.DataFrame({"left": [1.0, 3.0, 5.0]}, index=index)
    compute = compile_alphagen_expression(
        ("feature:left", "mean:2"),
        scope="time_series",
        feature_map={"left": 0},
    )

    result = compute(frame)

    pd.testing.assert_series_equal(
        result,
        frame["left"].rolling(2).mean(),
        check_names=False,
    )


def test_existing_phase_one_tokens_still_compile() -> None:
    panel = _panel()
    expressions: tuple[tuple[str, ...], ...] = (
        ("feature:left", "neg"),
        ("feature:left", "return:1"),
        ("feature:left", "rolling_std:2"),
        ("feature:left", "cs_rank"),
    )

    for expression in expressions:
        result = _compute(expression)

        assert result.index.equals(panel.index)
        assert result.loc[~panel["__in_universe__"]].isna().all()


def test_delta_never_reads_a_future_bar() -> None:
    panel = _panel()
    actual = _compute(("feature:left", "delta:1"))
    expected = panel["left"].groupby(level="pair").diff(1)

    pd.testing.assert_series_equal(
        actual,
        expected.where(panel["__in_universe__"]),
        check_names=False,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )
