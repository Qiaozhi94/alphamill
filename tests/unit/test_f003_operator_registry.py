"""F003 算子能力登记表测试：FR-005、TR-002、AC-005。"""

from __future__ import annotations

import json
import operator

import pytest

from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.generators import operator_registry
from alphamill.factor_factory.generators.manual import seeds as manual_seeds
from alphamill.factor_factory.generators.operator_registry import (
    OPERATOR_REGISTRY,
    REGISTRY_SCHEMA_VERSION,
    capability_manifest,
    enabled_operators,
    manifest_digest,
    require_operator,
    window_to_duration,
)


def test_registry_covers_exact_phase_one_dsl_operators() -> None:
    expected_metadata = {
        "cs_rank": ("cross_sectional", None, None),
        "neg": ("time_series", None, None),
        "pct_change": ("time_series", 1, "bars"),
        "return": ("time_series", 1, "bars"),
        "rolling_std": ("time_series", 1, "bars"),
    }

    actual_metadata = {
        name: (spec.kind, spec.window_bars, spec.window_parameter)
        for name, spec in OPERATOR_REGISTRY.items()
    }

    assert actual_metadata == expected_metadata
    assert tuple(spec.name for spec in enabled_operators()) == tuple(expected_metadata)
    assert all(spec.description for spec in enabled_operators())
    assert "feature" not in OPERATOR_REGISTRY
    assert "feature:close" not in OPERATOR_REGISTRY


def test_require_operator_returns_known_spec() -> None:
    spec = require_operator("neg")

    assert spec is OPERATOR_REGISTRY["neg"]


def test_require_operator_rejects_unknown_name() -> None:
    with pytest.raises(SchemaValidationError, match="future_mean"):
        require_operator("future_mean")


def test_manual_seed_operator_tokens_resolve_in_registry() -> None:
    operator_names = {
        token.partition(":")[0]
        for seed in manual_seeds._SEEDS.values()
        for token in seed.expression
        if not token.startswith("feature:")
    }

    resolved_names = {require_operator(name).name for name in operator_names}

    assert resolved_names == operator_names


def test_window_to_duration_uses_exact_hour_or_minute_units() -> None:
    assert window_to_duration(24, "1h") == "24h"
    assert window_to_duration(7, "1d") == "168h"
    assert window_to_duration(12, "5m") == "1h"
    assert window_to_duration(1, "1m") == "1m"


def test_window_to_duration_rejects_non_positive_bars() -> None:
    with pytest.raises(SchemaValidationError, match="bars"):
        window_to_duration(0, "1h")


def test_window_to_duration_rejects_unsupported_resample() -> None:
    with pytest.raises(SchemaValidationError, match="2h"):
        window_to_duration(1, "2h")


def test_capability_manifest_is_versioned_and_deterministic() -> None:
    expected_operators: list[JSONValue] = [
        {
            "name": spec.name,
            "kind": spec.kind,
            "window_bars": spec.window_bars,
            "window_parameter": spec.window_parameter,
            "description": spec.description,
        }
        for spec in enabled_operators()
    ]
    first = capability_manifest()
    second = capability_manifest()

    assert first == second
    assert first == {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "operators": expected_operators,
    }
    assert manifest_digest() == manifest_digest()


def test_capability_manifest_round_trips_through_json() -> None:
    manifest = capability_manifest()

    assert json.loads(json.dumps(manifest)) == manifest


def test_operator_registry_rejects_mutation() -> None:
    with pytest.raises(TypeError):
        operator.setitem(
            OPERATOR_REGISTRY,
            "extra",
            operator_registry.OperatorSpec(
                name="extra",
                kind="time_series",
                window_bars=None,
                window_parameter=None,
                description="Not enabled.",
            ),
        )
