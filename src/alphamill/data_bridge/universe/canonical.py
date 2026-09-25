"""canonical JSON 与摘要原语（F008 `IR-002`/`IR-003` 的字节规范，自包含实现）。

规范与 F003 的 `factor_factory/canonical.py` 一致，但本包**不 import 它**：该模块
当前只存在于未并入 main 的 `feat/F003-alphagen-vendor`（见 design §3 开工前检查补记）。

消费方（F003 `load_explicit_universe`、F007 `evaluation/universe_ledger.py`）加载
artifact 时会「解析文档 → 重新规范化 → 重算 digest」并与显式引用比对，因此两侧必须
逐字节同规范。规则：

- `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False,
  allow_nan=False)` 的 UTF-8 编码，**无尾随换行**；
- 值只允许 `str` / `int` / `bool` / `None` / 数组 / 对象——**不得出现浮点数**
  （浮点的文本表示不保证跨实现一致，`allow_nan=False` 同时挡掉 NaN/Inf）；
- `None` 在 JSON 里写作 `null`，由 schema 决定语义（例如 `valid_to` 为空串/None 表示当前有效）。
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from alphamill.data_bridge.universe.errors import UniverseArtifactError

DIGEST_PREFIX = "sha256:"


def canonical_json_bytes(value: Any) -> bytes:
    """键排序、紧凑分隔、禁止 NaN/Inf 的 UTF-8 编码；不含尾随换行。"""
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:  # 非 JSON 值或浮点无法规范编码
        raise UniverseArtifactError(f"无法规范化为 canonical JSON: {exc}") from exc
    return text.encode("utf-8")


def canonical_json_text(value: Any) -> str:
    return canonical_json_bytes(value).decode("utf-8")


def sha256_prefixed(payload: bytes) -> str:
    """外部 artifact / 内容地址统一带 `sha256:` 前缀。"""
    return DIGEST_PREFIX + hashlib.sha256(payload).hexdigest()


def content_digest(value: Any) -> str:
    """canonical JSON 字节的带前缀 SHA-256——内容寻址的唯一算法。"""
    return sha256_prefixed(canonical_json_bytes(value))


def utc_iso(value: datetime) -> str:
    """UTC 落盘时间戳：`YYYY-MM-DDTHH:MM:SS[.ffffff]Z`。"""
    if value.tzinfo is None:
        raise UniverseArtifactError("utc_iso: 需要带时区的 datetime")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_utc(text: str, *, field: str) -> datetime:
    """解析 ISO-8601 时间戳为 aware UTC；naive 输入判红而不是猜时区。"""
    if not isinstance(text, str):
        raise UniverseArtifactError(f"{field}: 必须是 ISO-8601 字符串")
    normalized = text.strip()
    if normalized.endswith(("Z", "z")):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise UniverseArtifactError(f"{field}: 非法 ISO-8601 时间戳 {text!r}") from exc
    if parsed.tzinfo is None:
        raise UniverseArtifactError(f"{field}: 时间戳必须带时区（{text!r}）")
    return parsed.astimezone(UTC)
