"""上游只读摄入契入门面（F007 design §2，任务 T001）。

design §2 把「F003 `generation.*` 事件、算子能力登记表、协同池 `FactorDef`」与
「F008 universe artifact 的 digest 加载及 `universe_at(T)` 语义校验」统一归到本模块。
实现按关注点拆成三个子模块（SOP 350 行硬上限），本模块只做再导出与文档锚点：

- `universe_ledger`：F008 point-in-time 台账的只读消费（`IR-002`/`IR-003`）；
- `generation_ingest`：F003 漏斗第一级、算子能力登记表与协同池 meta-factor（`TR-001`/`TR-002`）；
- `signal_adapter`：信号型 `FactorDef` 适配与 `source=placeholder` 分层（`DR-007`）。

F003/F008 尚在开发中：这里冻结的是**消费者侧**契约（字段名与枚举），差异由
`tests/contract/test_f007_upstream_contracts.py` 的 fixture 固定。
"""

from __future__ import annotations

from alphamill.evaluation.contract_common import (
    DIGEST_PREFIX,
    EVENT_CANDIDATE_REJECTED,
    EVENT_RUN_COMPLETED,
    EXECUTION_TIERS,
    OPERATOR_KINDS,
    OPERATOR_SCHEMA_VERSION,
    REASON_DUPLICATE_DEFINITION,
    REASON_INSUFFICIENT_REACHABILITY,
    REASON_LOOKAHEAD,
    REASON_UNREGISTERED_OPERATOR,
    REJECTION_REASONS,
    RUN_COMPLETED_STATUS,
    SIGNAL_SOURCE_PLACEHOLDER,
    TIER_CANONICAL,
    TIER_PREVIEW,
    UNIVERSE_COLUMNS,
    UNIVERSE_SCHEMA_VERSION,
    UpstreamContractError,
    content_digest,
    parse_utc,
)
from alphamill.evaluation.generation_ingest import (
    CandidateRejected,
    FunnelFirstLevel,
    GenerationRunCompleted,
    OperatorCapability,
    OperatorRegistry,
    PoolFactor,
    PoolMember,
    ingest_generation_events,
    load_operator_capabilities,
    load_pool_factor,
)
from alphamill.evaluation.signal_adapter import (
    SignalFactorProvenance,
    SignalObservation,
    adapt_signal_records,
    assert_signal_source_allowed,
)
from alphamill.evaluation.universe_ledger import (
    UniverseLedger,
    UniverseMember,
    canonical_universe_bytes,
    load_universe,
    publish_universe,
    universe_artifact_dir,
)

__all__ = [
    "DIGEST_PREFIX",
    "EVENT_CANDIDATE_REJECTED",
    "EVENT_RUN_COMPLETED",
    "EXECUTION_TIERS",
    "OPERATOR_KINDS",
    "OPERATOR_SCHEMA_VERSION",
    "REASON_DUPLICATE_DEFINITION",
    "REASON_INSUFFICIENT_REACHABILITY",
    "REASON_LOOKAHEAD",
    "REASON_UNREGISTERED_OPERATOR",
    "REJECTION_REASONS",
    "RUN_COMPLETED_STATUS",
    "SIGNAL_SOURCE_PLACEHOLDER",
    "TIER_CANONICAL",
    "TIER_PREVIEW",
    "UNIVERSE_COLUMNS",
    "UNIVERSE_SCHEMA_VERSION",
    "CandidateRejected",
    "FunnelFirstLevel",
    "GenerationRunCompleted",
    "OperatorCapability",
    "OperatorRegistry",
    "PoolFactor",
    "PoolMember",
    "SignalFactorProvenance",
    "SignalObservation",
    "UniverseLedger",
    "UniverseMember",
    "UpstreamContractError",
    "adapt_signal_records",
    "assert_signal_source_allowed",
    "canonical_universe_bytes",
    "content_digest",
    "ingest_generation_events",
    "load_operator_capabilities",
    "load_pool_factor",
    "load_universe",
    "parse_utc",
    "publish_universe",
    "universe_artifact_dir",
]
