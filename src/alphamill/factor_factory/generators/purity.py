"""Pure expression screening for F003 generation candidates."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Set
from dataclasses import dataclass
from typing import Final

from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.factor import FactorScope
from alphamill.factor_factory.generators.base import RejectionReason
from alphamill.factor_factory.generators.operator_registry import (
    DELTAS,
    OPERATOR_ARITIES,
    OPERATOR_REGISTRY,
    OperatorSpec,
)

_FEATURE_PREFIX: Final = "feature:"
_OPERATOR_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"[a-z][a-z0-9_]*\Z")
_FUTURE_LOOKING_TOKENS: Final[frozenset[str]] = frozenset(
    {"future_return", "lead", "shift_forward"}
)


@dataclass(frozen=True, kw_only=True)
class PurityResult:
    accepted: bool
    reason_code: RejectionReason | None
    detail: str


def check_expression(
    expression: tuple[str, ...],
    *,
    scope: FactorScope,
    seen_definition_digests: Set[str],
    definition_digest: str,
    registry: Mapping[str, OperatorSpec] = OPERATOR_REGISTRY,
) -> PurityResult:
    """Apply deterministic token-purity checks without I/O or state mutation.

    This module owns ``unregistered_op``, ``lookahead``, and
    ``duplicate_definition``. ``reachability`` belongs to T024's objective
    pre-filter and is intentionally absent here. Checks run in that ownership
    order: unknown operators first, lookahead second, duplicate definitions last.

    A well-formed token with an unknown operator name returns
    ``unregistered_op``. Invalid token shapes raise ``SchemaValidationError``;
    registered operators that require a window are the deliberate exception:
    missing, non-numeric, or non-positive windows are structurally classified as
    ``lookahead``. ``delta`` windows outside the vendor's measured ``DELTAS``
    set use the same ``lookahead`` classification. Denylisted future-looking
    names are policy-recognized tokens, so they return ``lookahead`` even before
    a future registry adds them.

    ``scope`` is part of the stable generator API but does not change Phase-1
    token purity; scope-specific execution checks remain in the compiler.
    """
    if not expression:
        raise SchemaValidationError("expression must not be empty")

    operator_tokens: list[tuple[str, str | None, str]] = []
    parsed_tokens: list[tuple[str, str | None, str] | None] = []
    for token in expression:
        if not isinstance(token, str):
            raise SchemaValidationError(f"expression token must be a string: {token!r}")
        if token.startswith(_FEATURE_PREFIX):
            if not token.removeprefix(_FEATURE_PREFIX).strip():
                raise SchemaValidationError(f"malformed feature token: {token!r}")
            parsed_tokens.append(None)
            continue

        if token.startswith("constant:"):
            literal = token.removeprefix("constant:")
            if ":" in literal or not _is_finite_float(literal):
                raise SchemaValidationError(f"malformed constant token: {token!r}")
            parsed_tokens.append(None)
            continue
        if token == "constant":
            raise SchemaValidationError(f"malformed constant token: {token!r}")

        name, separator, argument = token.partition(":")
        if _OPERATOR_NAME_PATTERN.fullmatch(name) is None or (separator and ":" in argument):
            raise SchemaValidationError(f"malformed operator token: {token!r}")
        parsed_operator = (name, argument if separator else None, token)
        operator_tokens.append(parsed_operator)
        parsed_tokens.append(parsed_operator)

    for name, argument, token in operator_tokens:
        if name in _FUTURE_LOOKING_TOKENS:
            continue
        if registry.get(name) is None:
            argument_is_valid = argument is None or (
                argument.isascii() and argument.isdecimal() and int(argument) > 0
            )
            if not argument_is_valid:
                raise SchemaValidationError(f"malformed operator token: {token!r}")
            return PurityResult(
                accepted=False,
                reason_code="unregistered_op",
                detail=f"operator is not registered: {name!r}",
            )

    stack_depth = 0
    for parsed_token in parsed_tokens:
        if parsed_token is None:
            stack_depth += 1
            continue
        name, argument, token = parsed_token
        if name in _FUTURE_LOOKING_TOKENS:
            return PurityResult(
                accepted=False,
                reason_code="lookahead",
                detail=f"future-looking operator is forbidden: {name!r}",
            )

        spec = registry[name]
        if spec.window_parameter is not None:
            window_is_valid = argument is not None and (
                argument.isascii() and argument.isdecimal() and int(argument) > 0
            )
            if not window_is_valid:
                return PurityResult(
                    accepted=False,
                    reason_code="lookahead",
                    detail=(
                        f"operator {name!r} requires a strictly positive integer window: {token!r}"
                    ),
                )
            if name == "delta" and int(argument) not in DELTAS:
                return PurityResult(
                    accepted=False,
                    reason_code="lookahead",
                    detail=f"delta window is not enabled by the vendor contract: {token!r}",
                )
        elif argument is not None:
            raise SchemaValidationError(f"operator does not accept a window: {token!r}")

        arity = OPERATOR_ARITIES.get(name)
        if arity is not None:
            if stack_depth < arity:
                raise SchemaValidationError(f"operator has insufficient operands: {token!r}")
            stack_depth = stack_depth - arity + 1

    if stack_depth != 1:
        raise SchemaValidationError("expression must leave exactly one value on the stack")

    if definition_digest in seen_definition_digests:
        return PurityResult(
            accepted=False,
            reason_code="duplicate_definition",
            detail=f"definition digest already seen: {definition_digest}",
        )
    return PurityResult(accepted=True, reason_code=None, detail="")


def _is_finite_float(value: str) -> bool:
    try:
        return math.isfinite(float(value))
    except ValueError:
        return False
