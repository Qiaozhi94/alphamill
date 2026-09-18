"""方法论门：能力/守卫配对 + L1 无前视 fail-closed（`FR-002`/`FR-007`；任务 T008）。

「能力声明 + 守卫注册」配对是硬约束：新增标签/变换/join/forward-fill/跨 pair/算子能力时，
必须有覆盖该能力的守卫；**未知能力默认拒绝**（`FR-002`）。守卫分两类：

- **静态（L1）**：因子表达式 AST 纯度与未来算子——引用未来算子/前视记号即 `FAIL`（fail-closed）；
- **运行时**：label endpoint 不跨折、embargo ≥ 最大 horizon、拟合型变换只在训练折拟合、
  as-of join 方向为 backward 且陈旧度有上限、forward-fill 有界、跨 pair 与算子均已登记。

任何守卫失败 ⇒ 方法论门 `FAIL`，运行进 `REJECTED` 终态并**照常登记**（`spec.md` §5：被拒者仍计入
漏斗分母，不携带任何 PASS-like 结论）。
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from alphamill.evaluation.contract_common import DIGEST_PREFIX
from alphamill.validation.no_lookahead import (
    STATUS_FAIL,
    STATUS_PASS,
    NoLookahead,
    build_no_lookahead,
)

CAPABILITY_LABEL = "label"
CAPABILITY_TRANSFORM = "transform"
CAPABILITY_JOIN = "join"
CAPABILITY_FORWARD_FILL = "forward_fill"
CAPABILITY_CROSS_PAIR = "cross_pair"
CAPABILITY_OPERATOR = "operator"
CAPABILITIES = (
    CAPABILITY_LABEL,
    CAPABILITY_TRANSFORM,
    CAPABILITY_JOIN,
    CAPABILITY_FORWARD_FILL,
    CAPABILITY_CROSS_PAIR,
    CAPABILITY_OPERATOR,
)

ERROR_CODE = "E_METHODOLOGY_REJECTED"
FUTURE_TOKENS = ("future_", "lookahead", "peek(", "lead(")
NEGATIVE_SHIFT_RE = re.compile(r"shift\s*\(\s*[^,]+,\s*-\s*\d")
JOIN_FORWARD = "forward"


class GuardViolation(Exception):
    """运行时或静态守卫失败；映射到稳定错误码 `E_METHODOLOGY_REJECTED`。"""

    code = ERROR_CODE

    def __init__(self, guard: str, message: str) -> None:
        super().__init__(f"{guard}: {message}")
        self.guard = guard
        self.message = message


@dataclass(frozen=True)
class GuardContext:
    signal_times: tuple[datetime, ...] = ()
    label_endpoints: tuple[datetime, ...] = ()
    fold_bounds: tuple[tuple[datetime, datetime], ...] = ()
    max_label_horizon: int = 0
    embargo: int = 0
    fit_indices: frozenset[int] = frozenset()
    train_indices: frozenset[int] = frozenset()
    join_direction: str = "backward"
    join_staleness_seconds: float = 0.0
    join_max_staleness_seconds: float = 0.0
    forward_fill_seconds: float = 0.0
    forward_fill_max_seconds: float = 0.0
    used_operators: tuple[str, ...] = ()
    cross_pair_operators: tuple[str, ...] = ()
    registered_operators: frozenset[str] = frozenset()


def assert_no_lookahead_expression(expression: str) -> None:
    """L1 静态纯度：未来算子/前视记号即拒绝。"""
    guard = "l1_ast_purity"
    if not expression.strip():
        raise GuardViolation(guard, "因子表达式为空")
    lowered = expression.lower()
    hit = next((token for token in FUTURE_TOKENS if token in lowered), None)
    if hit is not None:
        raise GuardViolation(guard, f"表达式引用前视记号 {hit!r}")
    if NEGATIVE_SHIFT_RE.search(expression):
        raise GuardViolation(guard, "表达式含负向 shift（future-fill）")


def _guard_label_endpoint(expression: str, context: GuardContext) -> None:
    guard = "label_endpoint_within_fold"
    if not context.fold_bounds:
        return
    for index, signal_time in enumerate(context.signal_times):
        fold = next(
            (bounds for bounds in context.fold_bounds if bounds[0] <= signal_time < bounds[1]),
            None,
        )
        if fold is None:
            continue
        endpoint = context.label_endpoints[index]
        if endpoint >= fold[1]:
            raise GuardViolation(
                guard, f"第 {index} 个观测的 label endpoint 跨越切分边界（{endpoint} >= {fold[1]}）"
            )


def _guard_embargo(expression: str, context: GuardContext) -> None:
    if context.embargo < context.max_label_horizon:
        raise GuardViolation(
            "embargo_covers_max_horizon",
            f"embargo={context.embargo} < 最大标签 horizon={context.max_label_horizon}",
        )


def _guard_transform_fit(expression: str, context: GuardContext) -> None:
    leaked = sorted(context.fit_indices - context.train_indices)
    if leaked:
        raise GuardViolation("transform_fit_subset_of_train", f"拟合索引越出训练折: {leaked[:5]}")


def _guard_asof_join(expression: str, context: GuardContext) -> None:
    if context.join_direction == JOIN_FORWARD:
        raise GuardViolation("asof_join_backward", "as-of join 方向必须为 backward")
    if context.join_staleness_seconds > context.join_max_staleness_seconds:
        raise GuardViolation(
            "asof_join_backward",
            f"join 陈旧度 {context.join_staleness_seconds}s 超过上限 "
            f"{context.join_max_staleness_seconds}s",
        )


def _guard_forward_fill(expression: str, context: GuardContext) -> None:
    if context.forward_fill_seconds > context.forward_fill_max_seconds:
        raise GuardViolation(
            "forward_fill_bounded",
            f"forward-fill 跨度 {context.forward_fill_seconds}s 超过上限 "
            f"{context.forward_fill_max_seconds}s",
        )


def _guard_cross_pair(expression: str, context: GuardContext) -> None:
    unregistered = sorted(set(context.cross_pair_operators) - context.registered_operators)
    if unregistered:
        raise GuardViolation("cross_pair_registered", f"跨 pair 算子未登记: {unregistered}")


def _guard_operator(expression: str, context: GuardContext) -> None:
    unregistered = sorted(set(context.used_operators) - context.registered_operators)
    if unregistered:
        raise GuardViolation("operator_registered", f"算子未登记: {unregistered}")


@dataclass(frozen=True)
class GuardSpec:
    name: str
    capability: str
    check: Callable[[str, GuardContext], None]


GUARDS: tuple[GuardSpec, ...] = (
    GuardSpec("label_endpoint_within_fold", CAPABILITY_LABEL, _guard_label_endpoint),
    GuardSpec("embargo_covers_max_horizon", CAPABILITY_LABEL, _guard_embargo),
    GuardSpec("transform_fit_subset_of_train", CAPABILITY_TRANSFORM, _guard_transform_fit),
    GuardSpec("asof_join_backward", CAPABILITY_JOIN, _guard_asof_join),
    GuardSpec("forward_fill_bounded", CAPABILITY_FORWARD_FILL, _guard_forward_fill),
    GuardSpec("cross_pair_registered", CAPABILITY_CROSS_PAIR, _guard_cross_pair),
    GuardSpec("operator_registered", CAPABILITY_OPERATOR, _guard_operator),
)
GUARDS_BY_NAME = {spec.name: spec for spec in GUARDS}


def guards_for(capability: str) -> tuple[GuardSpec, ...]:
    return tuple(spec for spec in GUARDS if spec.capability == capability)


def assert_capabilities_guarded(declared: Iterable[str]) -> None:
    """声明的每种能力都必须有守卫；未登记的能力默认拒绝（`FR-002`）。"""
    for capability in declared:
        if capability not in CAPABILITIES:
            raise GuardViolation("capability_registry", f"未知能力: {capability!r}（默认拒绝）")
        if not guards_for(capability):
            raise GuardViolation("capability_registry", f"能力 {capability!r} 没有对应的守卫")


def run_guards(expression: str, context: GuardContext) -> tuple[GuardViolation, ...]:
    violations = []
    for spec in GUARDS:
        try:
            spec.check(expression, context)
        except GuardViolation as violation:
            violations.append(violation)
    return tuple(violations)


@dataclass(frozen=True)
class MethodologyVerdict:
    passed: bool
    violations: tuple[GuardViolation, ...]
    no_lookahead: NoLookahead
    declared_capabilities: tuple[str, ...] = field(default_factory=tuple)

    @property
    def failure_mechanism(self) -> str:
        return "lookahead" if self.l1_failed else "capability_unguarded"

    @property
    def l1_failed(self) -> bool:
        return self.no_lookahead.get("L1").status == STATUS_FAIL

    def to_payload(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "error_code": None if self.passed else ERROR_CODE,
            "mechanism": None if self.passed else self.failure_mechanism,
            "declared_capabilities": list(self.declared_capabilities),
            "violations": [
                {"guard": item.guard, "message": item.message} for item in self.violations
            ],
            "no_lookahead": self.no_lookahead.to_payload(),
        }


def evaluate_methodology(
    *,
    expression: str,
    declared_capabilities: Iterable[str],
    context: GuardContext,
    l1_evidence_refs: tuple[str, ...] = (),
) -> MethodologyVerdict:
    """L1 静态纯度 + 能力覆盖 + 运行时守卫；任一步失败即 `passed=False`（fail-closed）。"""
    declared = tuple(sorted(set(declared_capabilities)))
    violations: list[GuardViolation] = []
    l1_status = STATUS_PASS
    try:
        assert_no_lookahead_expression(expression)
    except GuardViolation as violation:
        violations.append(violation)
        l1_status = STATUS_FAIL
    try:
        assert_capabilities_guarded(declared)
    except GuardViolation as violation:
        violations.append(violation)
    violations.extend(run_guards(expression, context))
    evidence = l1_evidence_refs
    if l1_status == STATUS_PASS and not evidence:
        evidence = (DIGEST_PREFIX + hashlib.sha256(expression.encode("utf-8")).hexdigest(),)
    no_lookahead = build_no_lookahead(
        l1_status=l1_status, l1_evidence_refs=evidence if l1_status == STATUS_PASS else ()
    )
    return MethodologyVerdict(
        passed=not violations,
        violations=tuple(violations),
        no_lookahead=no_lookahead,
        declared_capabilities=declared,
    )


def guard_registry_payload() -> Mapping[str, Any]:
    """守卫登记表的可发布视图（供测试证明「每种能力都有守卫」）。"""
    return {
        "capabilities": list(CAPABILITIES),
        "guards": [{"name": spec.name, "capability": spec.capability} for spec in GUARDS],
    }
