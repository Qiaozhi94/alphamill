"""规范化 JSON 与摘要原语（F003 内容寻址身份的唯一入口）。

摘要规则是身份契约：任何调用方都必须经由本模块，不得自行 json.dumps + sha256。
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import TypeAlias

from alphamill.factor_factory.errors import SchemaValidationError

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


def canonical_json_bytes(value: JSONValue) -> bytes:
    """键排序、紧凑分隔、禁止 NaN/Inf 的 UTF-8 编码；不含尾随换行。"""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_json_text(value: JSONValue) -> str:
    return canonical_json_bytes(value).decode("utf-8")


def sha256_hex(value: JSONValue) -> str:
    """无前缀 64 位小写十六进制摘要（factor_id 公式要求无前缀）。"""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_prefixed_bytes(payload: bytes) -> str:
    """外部 artifact 摘要统一带 `sha256:` 前缀。"""
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def utc_iso(value: datetime) -> str:
    """UTC 落盘时间戳：`YYYY-MM-DDTHH:MM:SS[.ffffff]Z`。"""
    if value.tzinfo is None:
        raise SchemaValidationError("utc_iso: 需要带时区的 datetime")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_utc(value: str, *, field: str) -> datetime:
    """解析 ISO-8601 时间戳为 aware UTC；naive 输入判红而不是猜测时区。"""
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SchemaValidationError(f"{field}: 非法 ISO-8601 时间戳 {value!r}") from exc
    if parsed.tzinfo is None:
        raise SchemaValidationError(f"{field}: 时间戳必须带时区（{value!r}）")
    return parsed.astimezone(UTC)
