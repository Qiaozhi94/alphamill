"""F008 宇宙台账的 Phase-1 显式 artifact 消费契约。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from alphamill.factor_factory.canonical import (
    JSONValue,
    canonical_json_bytes,
    parse_utc,
    sha256_prefixed_bytes,
    utc_iso,
)
from alphamill.factor_factory.errors import BindingValidationError, SchemaValidationError

_TOP_LEVEL_KEYS: Final = frozenset({"schema_version", "members"})
_MEMBERSHIP_KEYS: Final = frozenset({"lake_pair", "valid_from", "valid_to"})


@dataclass(frozen=True, kw_only=True)
class UniverseMembership:
    """一个 lake pair 的半开有效期成员记录。"""

    lake_pair: str
    valid_from: datetime
    valid_to: datetime | None


@dataclass(frozen=True, kw_only=True)
class UniverseLedger:
    """已校验 schema 与内容摘要的不可变宇宙台账。"""

    schema_version: int
    digest: str
    memberships: tuple[UniverseMembership, ...]

    def universe_at(self, at: datetime) -> frozenset[str]:
        """返回 UTC 时点 `at` 上有效的 lake pair 集合。"""
        if at.tzinfo is None or at.utcoffset() != UTC.utcoffset(at):
            raise SchemaValidationError("universe_at.at: 必须是带时区的 UTC datetime")
        return frozenset(
            membership.lake_pair
            for membership in self.memberships
            if membership.valid_from <= at
            and (membership.valid_to is None or at < membership.valid_to)
        )


def _parse_membership(value: JSONValue, *, index: int) -> UniverseMembership:
    if not isinstance(value, dict):
        raise SchemaValidationError(f"members[{index}]: 必须是 JSON object")
    if set(value) != _MEMBERSHIP_KEYS:
        missing = sorted(_MEMBERSHIP_KEYS - set(value))
        unknown = sorted(set(value) - _MEMBERSHIP_KEYS)
        raise SchemaValidationError(
            f"members[{index}]: keys invalid; missing={missing}, unknown={unknown}"
        )

    lake_pair = value["lake_pair"]
    valid_from_text = value["valid_from"]
    valid_to_text = value["valid_to"]
    if not isinstance(lake_pair, str):
        raise SchemaValidationError(f"members[{index}].lake_pair: 必须是 string")
    if not isinstance(valid_from_text, str):
        raise SchemaValidationError(f"members[{index}].valid_from: 必须是 string")

    valid_from = parse_utc(valid_from_text, field=f"members[{index}].valid_from")
    if valid_to_text is None:
        valid_to = None
    else:
        if not isinstance(valid_to_text, str):
            raise SchemaValidationError(f"members[{index}].valid_to: 必须是 string 或 null")
        valid_to = parse_utc(valid_to_text, field=f"members[{index}].valid_to")

    if valid_to is not None and valid_from > valid_to:
        raise SchemaValidationError(
            f"members[{index}]: valid_from {utc_iso(valid_from)} 晚于 valid_to {utc_iso(valid_to)}"
        )
    return UniverseMembership(
        lake_pair=lake_pair,
        valid_from=valid_from,
        valid_to=valid_to,
    )


def load_explicit_universe(
    path: Path,
    *,
    expected_digest: str,
    expected_schema_version: int,
) -> UniverseLedger:
    """加载并校验 Phase-1 显式宇宙台账 artifact。"""
    try:
        document: JSONValue = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SchemaValidationError(f"universe artifact 不是有效 UTF-8 JSON: {path}") from exc

    if not isinstance(document, dict):
        raise SchemaValidationError("universe artifact top-level 必须是 JSON object")
    if set(document) != _TOP_LEVEL_KEYS:
        missing = sorted(_TOP_LEVEL_KEYS - set(document))
        unknown = sorted(set(document) - _TOP_LEVEL_KEYS)
        raise SchemaValidationError(
            f"universe artifact top-level keys invalid; missing={missing}, unknown={unknown}"
        )

    schema_version = document["schema_version"]
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise SchemaValidationError("universe.schema_version: 必须是 integer")
    if schema_version != expected_schema_version:
        raise SchemaValidationError(
            f"universe.schema_version: expected {expected_schema_version}, got {schema_version}"
        )

    member_values = document["members"]
    if not isinstance(member_values, list):
        raise SchemaValidationError("universe.members: 必须是 array")

    try:
        actual_digest = sha256_prefixed_bytes(canonical_json_bytes(document))
    except ValueError as exc:
        raise SchemaValidationError("universe artifact 含非规范 JSON 数值") from exc
    if actual_digest != expected_digest:
        raise BindingValidationError(
            f"universe digest mismatch: expected {expected_digest}, got {actual_digest}"
        )

    memberships: list[UniverseMembership] = []
    for index, value in enumerate(member_values):
        membership = _parse_membership(value, index=index)
        for previous in memberships:
            has_overlap = (
                previous.lake_pair == membership.lake_pair
                and previous.valid_from != previous.valid_to
                and membership.valid_from != membership.valid_to
                and (membership.valid_to is None or previous.valid_from < membership.valid_to)
                and (previous.valid_to is None or membership.valid_from < previous.valid_to)
            )
            if has_overlap:
                raise SchemaValidationError(
                    f"members[{index}]: overlapping validity windows for "
                    f"{membership.lake_pair!r} at {utc_iso(membership.valid_from)}"
                )
        memberships.append(membership)

    return UniverseLedger(
        schema_version=schema_version,
        digest=actual_digest,
        memberships=tuple(memberships),
    )
