"""F003 生成侧只读摄入契约（F007 `FR-002`/`DR-004`，任务 T001）。

F007 不写 F003 运行记录、不解析 vendor 内部结构；本模块只消费三样东西：

- `generation.run_completed`（`TR-001`）：**只有 `status=completed` 的运行**才被消费，
  `rejected`/`failed`/`partial` 不产生该事件、也不得被下游当成绩效证据；
- `generation.candidate_rejected`（`TR-002`）：按冻结原因码计数，与完成运行共同构成漏斗
  第一级，**拒绝者仍计入分母**（`FR-004`）；
- 算子能力登记表与协同池 meta-factor：登记表是方法论门的已登记能力白名单（未登记默认拒绝），
  协同池（`generator="pool"`）与普通因子走同一评测路径，不因来源或聚合形态获得豁免。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from alphamill.evaluation.contract_common import (
    EVENT_CANDIDATE_REJECTED,
    EVENT_RUN_COMPLETED,
    OPERATOR_KINDS,
    OPERATOR_SCHEMA_VERSION,
    REJECTION_REASONS,
    RUN_COMPLETED_STATUS,
    UpstreamContractError,
)


@dataclass(frozen=True)
class GenerationRunCompleted:
    run_id: str
    generator: str
    counts: Mapping[str, int]
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class CandidateRejected:
    run_id: str
    expression: str
    reason_code: str


@dataclass(frozen=True)
class FunnelFirstLevel:
    """生成侧漏斗第一级：只有 completed 运行被消费，拒绝者仍入分母。"""

    completed_runs: tuple[GenerationRunCompleted, ...]
    rejections: tuple[CandidateRejected, ...]

    @property
    def rejected_by_reason(self) -> dict[str, int]:
        counts = {reason: 0 for reason in REJECTION_REASONS}
        for rejection in self.rejections:
            counts[rejection.reason_code] += 1
        return counts

    @property
    def rejected_total(self) -> int:
        return len(self.rejections)

    @property
    def registered_candidates(self) -> int:
        return sum(int(run.counts.get("registered", 0)) for run in self.completed_runs)

    @property
    def denominator(self) -> int:
        """漏斗分母 = 入册候选 + 被拒候选（`FR-004`：拒绝者不得缺席）。"""
        return self.registered_candidates + self.rejected_total


def ingest_generation_events(events: Iterable[Mapping[str, Any]]) -> FunnelFirstLevel:
    """只读摄入 `generation.*` 事件；非 completed 运行忽略，未知类型/原因码失败关闭。"""
    completed: list[GenerationRunCompleted] = []
    rejections: list[CandidateRejected] = []
    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            raise UpstreamContractError(f"第 {index} 条 generation 事件不是 object")
        kind = event.get("type")
        if kind == EVENT_RUN_COMPLETED:
            if event.get("status") != RUN_COMPLETED_STATUS:
                continue  # rejected/failed/partial 不发完成事件，不得被消费
            run_id = str(event.get("run_id", ""))
            if not run_id:
                raise UpstreamContractError(f"第 {index} 条 run_completed 缺 run_id")
            counts = event.get("counts") or {}
            if not isinstance(counts, Mapping):
                raise UpstreamContractError(f"第 {index} 条 run_completed counts 必须是 object")
            completed.append(
                GenerationRunCompleted(
                    run_id=run_id,
                    generator=str(event.get("generator", "")),
                    counts={str(key): int(value) for key, value in counts.items()},
                    payload=dict(event),
                )
            )
        elif kind == EVENT_CANDIDATE_REJECTED:
            reason = str(event.get("reason_code", ""))
            if reason not in REJECTION_REASONS:
                raise UpstreamContractError(
                    f"第 {index} 条 candidate_rejected 原因码未登记: {reason!r}"
                    f"（合法: {list(REJECTION_REASONS)}）"
                )
            rejections.append(
                CandidateRejected(
                    run_id=str(event.get("run_id", "")),
                    expression=str(event.get("expression", "")),
                    reason_code=reason,
                )
            )
        else:
            raise UpstreamContractError(f"第 {index} 条事件类型未登记: {kind!r}")
    return FunnelFirstLevel(completed_runs=tuple(completed), rejections=tuple(rejections))


@dataclass(frozen=True)
class OperatorCapability:
    name: str
    kind: str
    window_semantics: str


@dataclass(frozen=True)
class OperatorRegistry:
    """算子能力登记表——方法论门的已登记能力白名单；未登记默认拒绝（`FR-002`）。"""

    capabilities: Mapping[str, OperatorCapability]

    def require(self, name: str) -> OperatorCapability:
        try:
            return self.capabilities[name]
        except KeyError:
            raise UpstreamContractError(f"算子能力未登记: {name!r}（默认拒绝）") from None


def load_operator_capabilities(payload: Mapping[str, Any]) -> OperatorRegistry:
    if payload.get("schema_version") != OPERATOR_SCHEMA_VERSION:
        raise UpstreamContractError(
            f"算子能力登记表 schema_version 需为 {OPERATOR_SCHEMA_VERSION}，"
            f"收到 {payload.get('schema_version')!r}"
        )
    entries = payload.get("operators")
    if not isinstance(entries, list) or not entries:
        raise UpstreamContractError("算子能力登记表 operators 必须是非空数组")
    capabilities: dict[str, OperatorCapability] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise UpstreamContractError(f"operators[{index}] 必须是 object")
        name = str(entry.get("name", ""))
        kind = str(entry.get("kind", ""))
        if not name:
            raise UpstreamContractError(f"operators[{index}] 缺 name")
        if kind not in OPERATOR_KINDS:
            raise UpstreamContractError(
                f"operators[{index}] kind 未登记: {kind!r}（合法: {list(OPERATOR_KINDS)}）"
            )
        capabilities[name] = OperatorCapability(
            name=name, kind=kind, window_semantics=str(entry.get("window_semantics", ""))
        )
    return OperatorRegistry(capabilities=capabilities)


@dataclass(frozen=True)
class PoolMember:
    factor_id: str
    weight: float


@dataclass(frozen=True)
class PoolFactor:
    factor_id: str
    members: tuple[PoolMember, ...]

    def provenance(self) -> dict[str, Any]:
        """成员 `factor_id` 与权重随定义进入 manifest provenance（design §4）。"""
        return {
            "generator": "pool",
            "pool_factor_id": self.factor_id,
            "members": [
                {"factor_id": member.factor_id, "weight": member.weight}
                for member in sorted(self.members, key=lambda item: item.factor_id)
            ],
        }


def load_pool_factor(payload: Mapping[str, Any]) -> PoolFactor:
    """协同池 meta-factor（`generator="pool"`）；与普通因子同一评测路径，无豁免。"""
    if payload.get("generator") != "pool":
        raise UpstreamContractError(
            f"协同池 FactorDef 的 generator 必须是 'pool'，收到 {payload.get('generator')!r}"
        )
    factor_id = str(payload.get("factor_id", ""))
    if not factor_id:
        raise UpstreamContractError("协同池 FactorDef 缺 factor_id")
    raw = payload.get("members")
    if not isinstance(raw, list) or not raw:
        raise UpstreamContractError("协同池 FactorDef members 必须是非空数组")
    members = []
    for index, entry in enumerate(raw):
        if not isinstance(entry, Mapping) or not entry.get("factor_id"):
            raise UpstreamContractError(f"pool members[{index}] 缺 factor_id")
        weight = entry.get("weight")
        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            raise UpstreamContractError(f"pool members[{index}] weight 必须是数值")
        members.append(PoolMember(factor_id=str(entry["factor_id"]), weight=float(weight)))
    return PoolFactor(factor_id=factor_id, members=tuple(members))
