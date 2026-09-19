"""F003 纯度自检测试：FR-005、TR-002、AC-005。"""

from __future__ import annotations

import pytest

from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.factor import FactorScope
from alphamill.factor_factory.generators.manual import seeds as manual_seeds
from alphamill.factor_factory.generators.purity import PurityResult, check_expression


def test_all_manual_seed_expressions_are_accepted() -> None:
    for seed in manual_seeds._SEEDS.values():
        result = check_expression(
            seed.expression,
            scope=seed.scope,
            seen_definition_digests=frozenset(),
            definition_digest="new-definition",
        )

        assert result.accepted
        assert result.reason_code is None
        assert not result.detail


def test_unknown_operator_is_rejected_with_named_detail() -> None:
    result = check_expression(
        ("feature:close", "bogus_op:3"),
        scope="time_series",
        seen_definition_digests=frozenset(),
        definition_digest="new-definition",
    )

    assert not result.accepted
    assert result.reason_code == "unregistered_op"
    assert "bogus_op" in result.detail


@pytest.mark.parametrize("token", ("return:0", "return:-1", "return:abc", "return"))
def test_invalid_required_window_is_rejected_as_lookahead(token: str) -> None:
    result = check_expression(
        ("feature:close", token),
        scope="time_series",
        seen_definition_digests=frozenset(),
        definition_digest="new-definition",
    )

    assert not result.accepted
    assert result.reason_code == "lookahead"
    assert "return" in result.detail


def test_future_looking_denylisted_operator_is_rejected_as_lookahead() -> None:
    result = check_expression(
        ("feature:close", "lead"),
        scope="time_series",
        seen_definition_digests=frozenset(),
        definition_digest="new-definition",
    )

    assert not result.accepted
    assert result.reason_code == "lookahead"
    assert "lead" in result.detail


def test_malformed_non_window_operator_token_raises_schema_error() -> None:
    with pytest.raises(SchemaValidationError, match="neg"):
        check_expression(
            ("feature:close", "neg:1"),
            scope="time_series",
            seen_definition_digests=frozenset(),
            definition_digest="new-definition",
        )


def test_seen_definition_digest_is_rejected_as_duplicate() -> None:
    result = check_expression(
        ("feature:close", "neg"),
        scope="time_series",
        seen_definition_digests={"same-definition"},
        definition_digest="same-definition",
    )

    assert not result.accepted
    assert result.reason_code == "duplicate_definition"


def test_unseen_definition_digest_is_accepted() -> None:
    result = check_expression(
        ("feature:close", "neg"),
        scope="time_series",
        seen_definition_digests={"existing-definition"},
        definition_digest="new-definition",
    )

    assert result == PurityResult(accepted=True, reason_code=None, detail="")


def test_unregistered_operator_precedes_duplicate_definition() -> None:
    result = check_expression(
        ("feature:close", "bogus_op:3"),
        scope="time_series",
        seen_definition_digests={"same-definition"},
        definition_digest="same-definition",
    )

    assert not result.accepted
    assert result.reason_code == "unregistered_op"


def test_check_is_repeatable_and_does_not_mutate_seen_digests() -> None:
    seen = {"existing-definition"}
    inputs = {
        "scope": "time_series",
        "seen_definition_digests": seen,
        "definition_digest": "new-definition",
    }

    first = check_expression(("feature:close", "neg"), **inputs)
    second = check_expression(("feature:close", "neg"), **inputs)

    assert first == second
    assert seen == {"existing-definition"}


def test_empty_expression_raises_schema_error() -> None:
    with pytest.raises(SchemaValidationError, match="empty"):
        check_expression(
            (),
            scope="time_series",
            seen_definition_digests=frozenset(),
            definition_digest="new-definition",
        )


@pytest.mark.parametrize("scope", ("time_series", "cross_sectional"))
def test_scope_does_not_change_manual_seed_purity(scope: FactorScope) -> None:
    results = tuple(
        check_expression(
            seed.expression,
            scope=scope,
            seen_definition_digests=frozenset(),
            definition_digest=f"definition-{name}",
        )
        for name, seed in manual_seeds._SEEDS.items()
    )

    assert all(
        result == PurityResult(accepted=True, reason_code=None, detail="") for result in results
    )


@pytest.mark.parametrize(
    "expression",
    (
        ("feature:close", "delta:5"),
        ("feature:close", "sum:5"),
        ("constant:-10",),
        ("feature:close", "feature:volume", "corr:10"),
    ),
)
def test_alphagen_vendor_tokens_are_pure(expression: tuple[str, ...]) -> None:
    result = check_expression(
        expression,
        scope="cross_sectional",
        seen_definition_digests=frozenset(),
        definition_digest="vendor-definition",
    )

    assert result == PurityResult(accepted=True, reason_code=None, detail="")


def test_vendor_delta_rejects_a_window_outside_the_measured_set() -> None:
    result = check_expression(
        ("feature:close", "delta:7"),
        scope="time_series",
        seen_definition_digests=frozenset(),
        definition_digest="vendor-definition",
    )

    assert not result.accepted
    assert result.reason_code == "lookahead"


def test_vendor_pair_operator_requires_two_operands() -> None:
    with pytest.raises(SchemaValidationError, match="corr"):
        check_expression(
            ("feature:close", "corr:10"),
            scope="cross_sectional",
            seen_definition_digests=frozenset(),
            definition_digest="vendor-definition",
        )


def test_vendor_arity_follows_postfix_token_order() -> None:
    with pytest.raises(SchemaValidationError, match="add"):
        check_expression(
            ("feature:close", "add", "constant:1"),
            scope="time_series",
            seen_definition_digests=frozenset(),
            definition_digest="vendor-definition",
        )


@pytest.mark.parametrize("token", ("constant", "constant:nan", "constant:inf", "constant:1:2"))
def test_malformed_vendor_constant_raises_schema_error(token: str) -> None:
    with pytest.raises(SchemaValidationError, match="constant"):
        check_expression(
            (token,),
            scope="time_series",
            seen_definition_digests=frozenset(),
            definition_digest="vendor-definition",
        )
