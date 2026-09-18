"""DR-003/AC-009：假设定义、目录与显式默认值契约。"""

from dataclasses import replace

import pytest

from alphamill.factor_factory.errors import SchemaValidationError, UnknownHypothesisError
from alphamill.factor_factory.hypotheses.catalog import (
    DEFAULT_CATALOG,
    MECHANISM_UNKNOWN_ID,
    HypothesisCatalog,
    builtin_catalog,
)
from alphamill.factor_factory.hypotheses.schema import HypothesisDef


def _hypothesis(*, hypothesis_id: str = "test_hypothesis") -> HypothesisDef:
    return HypothesisDef(
        hypothesis_id=hypothesis_id,
        mechanism="A persistent imbalance should predict subsequent returns.",
        data_columns=("close",),
        expected_holding_period="1-3 days",
        cost_sensitivity="medium",
        source="unit_test",
        generation=1,
    )


def test_hypothesis_def_constructs_with_unspecified_applicable_state() -> None:
    hypothesis = _hypothesis()

    assert hypothesis.applicable_state == "unspecified"


@pytest.mark.parametrize(
    "field_name",
    ("hypothesis_id", "mechanism", "expected_holding_period", "source", "applicable_state"),
)
def test_hypothesis_def_rejects_empty_string_field(field_name: str) -> None:
    with pytest.raises(SchemaValidationError):
        replace(_hypothesis(), **{field_name: ""})


def test_hypothesis_def_rejects_empty_data_column() -> None:
    with pytest.raises(SchemaValidationError):
        replace(_hypothesis(), data_columns=("close", ""))


def test_hypothesis_def_rejects_duplicate_data_columns() -> None:
    with pytest.raises(SchemaValidationError):
        replace(_hypothesis(), data_columns=("close", "close"))


def test_hypothesis_def_rejects_negative_generation() -> None:
    with pytest.raises(SchemaValidationError):
        replace(_hypothesis(), generation=-1)


def test_hypothesis_def_rejects_invalid_cost_sensitivity() -> None:
    with pytest.raises(SchemaValidationError):
        replace(_hypothesis(), cost_sensitivity="invalid")


def test_catalog_rejects_duplicate_hypothesis_id() -> None:
    catalog = HypothesisCatalog((_hypothesis(),))

    with pytest.raises(SchemaValidationError):
        catalog.register(_hypothesis())


def test_catalog_require_unknown_raises_with_missing_id() -> None:
    catalog = HypothesisCatalog()

    with pytest.raises(UnknownHypothesisError, match="missing_hypothesis"):
        catalog.require("missing_hypothesis")


def test_catalog_require_known_returns_same_object() -> None:
    hypothesis = _hypothesis()
    catalog = HypothesisCatalog((hypothesis,))

    assert catalog.require(hypothesis.hypothesis_id) is hypothesis


def test_catalog_all_preserves_insertion_order() -> None:
    first = _hypothesis(hypothesis_id="first")
    second = _hypothesis(hypothesis_id="second")
    catalog = HypothesisCatalog((first, second))

    assert catalog.all() == (first, second)


def test_builtin_catalog_contains_exactly_six_unique_hypotheses() -> None:
    entries = builtin_catalog().all()
    hypothesis_ids = tuple(entry.hypothesis_id for entry in entries)

    assert hypothesis_ids == (
        MECHANISM_UNKNOWN_ID,
        "funding_carry",
        "basis_reversion",
        "open_interest_change",
        "cross_sectional_momentum",
        "realized_volatility",
    )
    assert len(hypothesis_ids) == len(set(hypothesis_ids))
    assert all(entry.mechanism for entry in entries)


def test_builtin_mechanism_unknown_uses_explicit_unknown_defaults() -> None:
    hypothesis = builtin_catalog().require(MECHANISM_UNKNOWN_ID)

    assert hypothesis.applicable_state == "unspecified"
    assert hypothesis.cost_sensitivity == "unknown"


def test_builtin_economic_hypotheses_match_seed_dependencies() -> None:
    entries = builtin_catalog().all()[1:]

    assert {entry.hypothesis_id: entry.data_columns for entry in entries} == {
        "funding_carry": ("funding_rate",),
        "basis_reversion": ("basis_pct",),
        "open_interest_change": ("open_interest",),
        "cross_sectional_momentum": ("close",),
        "realized_volatility": ("close",),
    }
    assert all(entry.generation == 1 for entry in entries)
    assert all(entry.cost_sensitivity in {"low", "medium", "high"} for entry in entries)


def test_default_catalog_contains_same_six_hypotheses() -> None:
    assert isinstance(DEFAULT_CATALOG, HypothesisCatalog)
    assert tuple(entry.hypothesis_id for entry in DEFAULT_CATALOG.all()) == tuple(
        entry.hypothesis_id for entry in builtin_catalog().all()
    )
