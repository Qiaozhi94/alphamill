"""执行层级 capability 边界（F007 `FR-001`/`NFR-003`；design §3.2/§7，任务 T003/T005）。

执行层级必须**显式提供**，并由「物理根目录 + capability 双重隔离」强制：

- preview 落 `reports/preview/<experiment_id>/<attempt_id>/`，canonical 落
  `reports/bench/<object_id>/<research_snapshot_id>/<experiment_id>/`；
- `canonical writer`、`holdout reader`、**最终确认窗 reader**、`holdout budget ledger writer`
  是**显式注入**的 capability；preview / Agent 构造器**没有**这些接口，越权即 fail-closed
  并返回稳定错误码 `E_CANONICAL_FORBIDDEN`；
- 任何环境变量只能提供普通路径默认值，**不能升级 tier 或权限**——层级只从显式参数来，
  因此本模块不读取任何 tier 相关的环境变量。

标签单隔离（只靠目录名）不足以防误写，故 capability 与路径同时强制（design §9 决策表）。
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from alphamill.evaluation.contract_common import (
    EXECUTION_TIERS,
    TIER_CANONICAL,
    TIER_PREVIEW,
    UpstreamContractError,
)

CAP_CANONICAL_WRITER = "canonical_writer"
CAP_HOLDOUT_READER = "holdout_reader"
CAP_FINAL_WINDOW_READER = "final_window_reader"
CAP_HOLDOUT_BUDGET_WRITER = "holdout_budget_writer"

CANONICAL_ONLY_CAPABILITIES = (
    CAP_CANONICAL_WRITER,
    CAP_HOLDOUT_READER,
    CAP_FINAL_WINDOW_READER,
    CAP_HOLDOUT_BUDGET_WRITER,
)

PREVIEW_SUBDIR = "preview"
BENCH_SUBDIR = "bench"
COHORTS_SUBDIR = "cohorts"
HOLDOUT_LEDGER_SUBDIR = "holdout_budget"
HOLDOUT_LEDGER_NAME = "ledger.jsonl"


class CapabilityError(UpstreamContractError):
    """越权访问 canonical 能力（写正式总体 / 读留出或最终确认窗 / 追加留出预算）。"""

    code = "E_CANONICAL_FORBIDDEN"


@dataclass(frozen=True)
class TierRoots:
    """tier 物理根目录（design §3.2）；只承载路径，不承载权限。"""

    reports: Path

    @property
    def preview_root(self) -> Path:
        return self.reports / PREVIEW_SUBDIR

    @property
    def bench_root(self) -> Path:
        return self.reports / BENCH_SUBDIR

    @property
    def cohorts_root(self) -> Path:
        return self.reports / COHORTS_SUBDIR

    @property
    def holdout_ledger_path(self) -> Path:
        return self.reports / HOLDOUT_LEDGER_SUBDIR / HOLDOUT_LEDGER_NAME

    def preview_attempt_dir(self, experiment_id: str, attempt_id: str) -> Path:
        return self.preview_root / experiment_id / attempt_id

    def bench_dir(self, object_id: str, snapshot_id: str, experiment_id: str) -> Path:
        return self.bench_root / object_id / snapshot_id / experiment_id


@dataclass(frozen=True)
class CapabilitySet:
    """显式注入的能力集合；preview 与 canonical 的差别只在这里。"""

    execution_tier: str
    granted: frozenset[str] = frozenset()

    def has(self, capability: str) -> bool:
        return capability in self.granted

    def require(self, capability: str) -> None:
        if not self.has(capability):
            raise CapabilityError(
                f"{self.execution_tier} 上下文没有 {capability} 能力（fail-closed）"
            )

    def granted_sorted(self) -> tuple[str, ...]:
        return tuple(sorted(self.granted))


def preview_capabilities() -> CapabilitySet:
    """preview / Agent 构造器：零 canonical 能力。"""
    return CapabilitySet(execution_tier=TIER_PREVIEW, granted=frozenset())


def canonical_capabilities() -> CapabilitySet:
    return CapabilitySet(
        execution_tier=TIER_CANONICAL, granted=frozenset(CANONICAL_ONLY_CAPABILITIES)
    )


@dataclass(frozen=True)
class TierContext:
    """一次运行的显式上下文：层级 + 物理根 + 能力。

    层级只能由 `context_for` 的显式参数决定；本模块不读环境变量，避免「env 提权」。
    """

    execution_tier: str
    roots: TierRoots
    capabilities: CapabilitySet

    @property
    def is_canonical(self) -> bool:
        return self.execution_tier == TIER_CANONICAL

    def require(self, capability: str) -> None:
        self.capabilities.require(capability)

    def preview_attempt_dir(self, experiment_id: str, attempt_id: str) -> Path:
        """preview 产物目录；canonical 上下文调用即越权。"""
        if self.is_canonical:
            raise CapabilityError("canonical 上下文不得写 preview 命名空间")
        return self.roots.preview_attempt_dir(experiment_id, attempt_id)

    def bench_dir(self, object_id: str, snapshot_id: str, experiment_id: str) -> Path:
        """canonical 产物目录；必须持有 canonical writer 能力。"""
        self.require(CAP_CANONICAL_WRITER)
        return self.roots.bench_dir(object_id, snapshot_id, experiment_id)

    def holdout_ledger_path(self) -> Path:
        """留出预算台账句柄；只有 canonical 持有 append 能力时才可取得。"""
        self.require(CAP_HOLDOUT_BUDGET_WRITER)
        return self.roots.holdout_ledger_path

    def require_holdout_reader(self) -> None:
        self.require(CAP_HOLDOUT_READER)

    def require_final_window_reader(self) -> None:
        """最终确认窗统计量的读取口；preview/Agent 一律拒绝（`AC-010`）。"""
        self.require(CAP_FINAL_WINDOW_READER)


def context_for(execution_tier: str, reports: Path) -> TierContext:
    """按显式 tier 构造上下文；未知 tier 或缺失能力一律 fail-closed。"""
    if execution_tier not in EXECUTION_TIERS:
        raise UpstreamContractError(
            f"未知执行层级: {execution_tier!r}（合法: {list(EXECUTION_TIERS)}）"
        )
    capabilities = (
        canonical_capabilities() if execution_tier == TIER_CANONICAL else preview_capabilities()
    )
    return TierContext(
        execution_tier=execution_tier,
        roots=TierRoots(reports=Path(reports)),
        capabilities=capabilities,
    )


FORBIDDEN_AGENT_KEY_TOKENS = ("final_window", "holdout")


def assert_no_canonical_leak(payload: Mapping[str, object], *, agent_readable: bool) -> None:
    """Agent/preview 可读产物不得含最终确认窗统计量；违规即失败关闭（`NFR-003`）。

    递归扫描嵌套 dict/list 的**键名**（只扫顶层会让嵌套泄漏静默通过，`R1-106`）。
    """
    if not agent_readable:
        return
    forbidden: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                text = str(key)
                if any(token in text for token in FORBIDDEN_AGENT_KEY_TOKENS):
                    forbidden.append(text)
                walk(value)
        elif isinstance(node, (list, tuple)):
            for item in node:
                walk(item)

    walk(payload)
    if forbidden:
        raise CapabilityError(
            f"Agent/preview 可读产物含最终确认窗/留出字段: {sorted(set(forbidden))}（fail-closed）"
        )
