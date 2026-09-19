"""Bridge AlphaGen postfix tokens to executable factor computations.

The vendor preserves upstream top-level imports rooted at ``alphagen_vendor``. This
module exposes that root on ``sys.path`` in one place without importing optional vendor
modules, so importing the adapter remains safe without the mining dependency group.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from alphamill.factor_factory.errors import (
    FactorCompilationError,
    FeatureMapIntegrityError,
)
from alphamill.factor_factory.factor import FactorCompute, FactorDef, FactorScope
from alphamill.factor_factory.generators.expression_compiler import (
    compile_postfix,
    referenced_features,
)
from alphamill.factor_factory.generators.operator_registry import OPERATOR_REGISTRY
from alphamill.factor_factory.registry.compiler_registry import CompileContext, CompilerRegistry
from alphamill.factor_factory.registry.factor_store import feature_map_digest

__all__ = (
    "ALPHAGEN_GENERATOR",
    "compile_alphagen_expression",
    "data_columns_from_expression",
    "expression_from_factor",
    "register_alphagen_compiler",
)

_VENDOR_ROOT: Final = Path(__file__).with_name("alphagen_vendor").resolve()
_VENDOR_IMPORT_ROOT: Final = str(_VENDOR_ROOT)
if _VENDOR_IMPORT_ROOT not in sys.path:
    sys.path.insert(0, _VENDOR_IMPORT_ROOT)

ALPHAGEN_GENERATOR: Final = "alphagen"


def compile_alphagen_expression(
    expression: tuple[str, ...],
    *,
    scope: FactorScope,
    feature_map: Mapping[str, int],
) -> FactorCompute:
    """Compile AlphaGen tokens with the shared Phase-1 postfix compiler.

    Vendor ``Expression`` objects can later render into this stable token tuple without
    changing the adapter signature or the persisted expression representation.
    """
    features = dict(feature_map)
    data_columns = data_columns_from_expression(expression, feature_map=features)
    for token in expression:
        if token.startswith(("feature:", "constant:")):
            continue
        operator_name = token.partition(":")[0]
        if operator_name not in OPERATOR_REGISTRY:
            raise FactorCompilationError(
                f"operator is not registered for AlphaGen: {operator_name!r}"
            )
    return compile_postfix(
        CompileContext(
            generator=ALPHAGEN_GENERATOR,
            expression=expression,
            scope=scope,
            params={},
            data_columns=data_columns,
            feature_map=features,
            resolver=None,
        )
    )


def expression_from_factor(factor: FactorDef) -> tuple[str, ...]:
    """Recover an AlphaGen token expression from an executable factor."""
    raw_expression = factor.meta.get("expression")
    if not isinstance(raw_expression, list) or not raw_expression:
        raise FactorCompilationError(
            "FactorDef meta['expression'] must be a non-empty list of strings"
        )
    tokens = tuple(token for token in raw_expression if isinstance(token, str))
    if len(tokens) != len(raw_expression):
        raise FactorCompilationError(
            "FactorDef meta['expression'] must be a non-empty list of strings"
        )
    return tokens


def data_columns_from_expression(
    expression: tuple[str, ...], *, feature_map: Mapping[str, int]
) -> tuple[str, ...]:
    """Recover referenced data columns from an AlphaGen token expression."""
    features = dict(feature_map)
    feature_map_digest(features)
    data_columns = referenced_features(expression)
    missing = tuple(column for column in data_columns if column not in features)
    if missing:
        raise FeatureMapIntegrityError(f"expression features absent from feature_map: {missing!r}")
    return data_columns


def register_alphagen_compiler(registry: CompilerRegistry) -> None:
    """Register the AlphaGen compiler in a factor compiler registry."""
    registry.register(ALPHAGEN_GENERATOR, _compile_registered_expression)


def _compile_registered_expression(context: CompileContext) -> FactorCompute:
    return compile_alphagen_expression(
        context.expression,
        scope=context.scope,
        feature_map=context.feature_map,
    )
