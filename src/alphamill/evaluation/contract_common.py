"""F007 上游契约的共享错误、执行层级与编码基元（F007 design §2，任务 T001）。

被 `universe_ledger`（F008 消费面）、`generation_ingest`（F003 消费面）与
`signal_adapter`（信号型 FactorDef 适配）共用；`upstream_contracts` 只做门面再导出，
避免子模块互相 import 成环。
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

TIER_PREVIEW = "preview"
TIER_CANONICAL = "canonical"
EXECUTION_TIERS = (TIER_PREVIEW, TIER_CANONICAL)

DIGEST_PREFIX = "sha256:"

# --- F008 宇宙台账（canonical JSON，IR-002/IR-003）---
UNIVERSE_SCHEMA_VERSION = 1
UNIVERSE_TOP_LEVEL_KEYS = frozenset({"schema_version", "members"})
UNIVERSE_MEMBER_KEYS = frozenset({"lake_pair", "valid_from", "valid_to"})

# --- F003 生成侧 ---
EVENT_RUN_COMPLETED = "generation.run_completed"
EVENT_CANDIDATE_REJECTED = "generation.candidate_rejected"
RUN_COMPLETED_STATUS = "completed"

REASON_UNREGISTERED_OPERATOR = "unregistered_operator"
REASON_LOOKAHEAD = "lookahead"
REASON_INSUFFICIENT_REACHABILITY = "insufficient_reachability"
REASON_DUPLICATE_DEFINITION = "duplicate_definition"
REJECTION_REASONS = (
    REASON_UNREGISTERED_OPERATOR,
    REASON_LOOKAHEAD,
    REASON_INSUFFICIENT_REACHABILITY,
    REASON_DUPLICATE_DEFINITION,
)

OPERATOR_SCHEMA_VERSION = 1
OPERATOR_KINDS = ("time_series", "cross_sectional")

# --- 信号型 FactorDef 适配 ---
SIGNAL_SOURCE_PLACEHOLDER = "placeholder"


class UpstreamContractError(Exception):
    """上游契约不可解析或违反 fail-closed 规则；`code` 为稳定错误码。"""

    code = "E_INPUT_INVALID"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


def content_digest(payload: bytes) -> str:
    return DIGEST_PREFIX + hashlib.sha256(payload).hexdigest()


def parse_utc(value: Any, field: str) -> datetime:
    """把 ISO-8601 字符串或 datetime 归一为 aware UTC；无时区按 UTC 处理，非法即拒绝。"""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value:
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise UpstreamContractError(f"{field} 不是合法 ISO-8601 时间: {value!r}") from exc
    else:
        raise UpstreamContractError(f"{field} 必须是 ISO-8601 字符串或 datetime")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
