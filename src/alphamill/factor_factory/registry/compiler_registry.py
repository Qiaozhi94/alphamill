from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TypeAlias

from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.errors import CompilerNotRegisteredError, SchemaValidationError
from alphamill.factor_factory.factor import FactorCompute, FactorResolver, FactorScope
from alphamill.factor_factory.generators.expression_compiler import compile_postfix


@dataclass(frozen=True, kw_only=True)
class CompileContext:
    generator: str
    expression: tuple[str, ...]
    scope: FactorScope
    params: Mapping[str, JSONValue]
    data_columns: tuple[str, ...]
    feature_map: Mapping[str, int]
    resolver: FactorResolver | None


FactorCompiler: TypeAlias = Callable[[CompileContext], FactorCompute]


class CompilerRegistry:
    """Map generator names to their expression compilers."""

    def __init__(self, compilers: Mapping[str, FactorCompiler] | None = None) -> None:
        self._compilers = dict(compilers or {})

    def register(self, generator: str, compiler: FactorCompiler) -> None:
        if generator in self._compilers:
            raise SchemaValidationError(f"compiler already registered: {generator!r}")
        self._compilers[generator] = compiler

    def require(self, generator: str) -> FactorCompiler:
        if generator not in self._compilers:
            raise CompilerNotRegisteredError(f"compiler not registered: {generator!r}")
        return self._compilers[generator]

    def compile(self, context: CompileContext) -> FactorCompute:
        return self.require(context.generator)(context)


DEFAULT_COMPILERS: CompilerRegistry = CompilerRegistry({"manual": compile_postfix})
