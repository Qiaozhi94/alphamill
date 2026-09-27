"""全生成器编译器注册表的惰性组装（F012 `FR-001`，design §1 第 11 行，文档检视 D18/D28）。

`compiler_registry.DEFAULT_COMPILERS` 只含 manual；alphagen 编译器在 `alphagen_adapter`，而 adapter
又依赖 `factor_store` → `compiler_registry`，顶层互相导入会成环。这里在函数内导入 adapter，
`factor_store.build_factor` / `load` 的缺省编译器取本函数的结果。
"""

from __future__ import annotations

from alphamill.factor_factory.generators.expression_compiler import compile_postfix
from alphamill.factor_factory.registry.compiler_registry import CompilerRegistry


def full_registry() -> CompilerRegistry:
    """manual + alphagen 两类编译器（每次返回新实例，调用方可再注册而不污染全局）。"""
    from alphamill.factor_factory.generators.alphagen_adapter import register_alphagen_compiler

    registry = CompilerRegistry({"manual": compile_postfix})
    register_alphagen_compiler(registry)
    return registry
