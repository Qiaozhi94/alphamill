"""Pure expression screening for F003 generation candidates."""

from __future__ import annotations

import re
from collections.abc import Mapping, Set
from dataclasses import dataclass
from typing import Final

from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.factor import FactorScope
from alphamill.factor_factory.generators.base import RejectionReason
from alphamill.factor_factory.generators.operator_registry import (
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
    ``lookahead``. Denylisted future-looking names are policy-recognized tokens,
    so they return ``lookahead`` even before a future registry adds them.

    ``scope`` is part of the stable generator API but does not change Phase-1
    token purity; scope-specific execution checks remain in the compiler.
    """
    if not expression:
        raise SchemaValidationError("expression must not be empty")

    operator_tokens: list[tuple[str, str | None, str]] = []
    for token in expression:
        if token.startswith(_FEATURE_PREFIX):
            if not token.removeprefix(_FEATURE_PREFIX).strip():
                raise SchemaValidationError(f"malformed feature token: {token!r}")
            continue

        name, separator, argument = token.partition(":")
        if _OPERATOR_NAME_PATTERN.fullmatch(name) is None or (separator and ":" in argument):
            raise SchemaValidationError(f"malformed operator token: {token!r}")
        operator_tokens.append((name, argument if separator else None, token))

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

    for name, argument, token in operator_tokens:
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
            continue
        if argument is not None:
            raise SchemaValidationError(f"operator does not accept a window: {token!r}")

    if definition_digest in seen_definition_digests:
        return PurityResult(
            accepted=False,
            reason_code="duplicate_definition",
            detail=f"definition digest already seen: {definition_digest}",
        )
    return PurityResult(accepted=True, reason_code=None, detail="")
