"""台账 artifact 的 canonical JSON 序列化与内容寻址发布（`IR-002`/`IR-003` / T009）。

冻结的 schema（多一个键即判非法，不做宽松忽略）：

```json
{"schema_version": 1, "members": [
  {"lake_pair": "BTC-USDT-PERP", "valid_from": "2024-09-10T00:00:00Z", "valid_to": null}]}
```

- 只承载**最小 PIT 投影**：`reason`/`universe_id`/`ingested_at`/`exchange`/`market_type`/`db_symbol`
  留在联机库（它们不参与 `universe_at(T)`，放进来只会让 digest 随审计噪声漂移）；
- canonical 字节规则见 `canonical.py`（键排序、紧凑分隔、UTF-8、无尾随换行、**不得出现浮点数**）；
- `digest = "sha256:" + sha256(canonical_bytes)`，前缀进文件名；
- 发布写一次：同 digest 已存在则必须逐字节一致，否则报错而不是覆盖；
- 载入侧独立重算 digest 并与显式引用比对，`schema_version` 不符或出现未知键即拒绝加载。
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from alphamill.data_bridge import paths
from alphamill.data_bridge.universe.canonical import (
    canonical_json_bytes,
    parse_utc,
    sha256_prefixed,
    utc_iso,
)
from alphamill.data_bridge.universe.errors import UniverseArtifactError
from alphamill.data_bridge.universe.membership import TradabilityInterval
from alphamill.data_bridge.universe.storage import atomic_create, read_bytes

SCHEMA_VERSION = 1
TOP_LEVEL_KEYS = frozenset({"schema_version", "members"})
MEMBER_KEYS = frozenset({"lake_pair", "valid_from", "valid_to"})
SUFFIX = ".json"
_DIGEST_HEX_LEN = 64


@dataclass(frozen=True, kw_only=True)
class ArtifactMember:
    lake_pair: str
    valid_from: datetime
    valid_to: datetime | None


@dataclass(frozen=True, kw_only=True)
class ArtifactLedger:
    """已校验 schema 与 digest 的不可变台账视图。"""

    digest: str
    schema_version: int
    members: tuple[ArtifactMember, ...]

    def universe_at(self, at: datetime) -> frozenset[str]:
        """T 时刻成员集合：半开区间并集（`valid_from <= T < valid_to`）。"""
        if not isinstance(at, datetime) or at.tzinfo is None:
            raise UniverseArtifactError("universe_at(T) 需要带时区的 datetime")
        return frozenset(
            member.lake_pair
            for member in self.members
            if member.valid_from <= at and (member.valid_to is None or at < member.valid_to)
        )


def artifact_dir(lake_root: Path | None = None) -> Path:
    root = Path(lake_root) if lake_root is not None else paths.lake_root()
    return root / "_metadata" / "universes"


def artifact_path(digest: str, lake_root: Path | None = None) -> Path:
    if not is_digest(digest):
        raise UniverseArtifactError(f"非法 universe digest: {digest!r}（期望 sha256:<64hex>）")
    return artifact_dir(lake_root) / f"{digest}{SUFFIX}"


def is_digest(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    body = value[len("sha256:") :]
    return len(body) == _DIGEST_HEX_LEN and all(char in "0123456789abcdef" for char in body)


def build_document(
    intervals: Iterable[TradabilityInterval], *, schema_version: int = SCHEMA_VERSION
) -> dict[str, Any]:
    """区间 → canonical 文档（排序由本函数负责，载入侧只校验）。"""
    members = [
        {
            "lake_pair": interval.lake_pair,
            "valid_from": utc_iso(interval.valid_from),
            "valid_to": None if interval.valid_to is None else utc_iso(interval.valid_to),
        }
        for interval in intervals
    ]
    members.sort(key=lambda item: (item["lake_pair"], item["valid_from"]))
    return {"schema_version": schema_version, "members": members}


def canonical_artifact_bytes(document: dict[str, Any]) -> bytes:
    """校验 schema 后再编码；任何未知键/未知类型/乱序都在这里判红。"""
    validate_document(document)
    return canonical_json_bytes(document)


def validate_document(document: Any, *, expected_schema_version: int | None = None) -> None:
    if not isinstance(document, dict):
        raise UniverseArtifactError("artifact 顶层必须是 JSON object")
    top_unknown = sorted(set(document) - TOP_LEVEL_KEYS)
    top_missing = sorted(TOP_LEVEL_KEYS - set(document))
    if top_unknown or top_missing:
        raise UniverseArtifactError(
            f"artifact 顶层键集合非法: missing={top_missing}, unknown={top_unknown}"
        )
    schema_version = document["schema_version"]
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise UniverseArtifactError("artifact schema_version 必须是整数")
    if expected_schema_version is not None and schema_version != expected_schema_version:
        raise UniverseArtifactError(
            f"artifact schema_version 不支持: {schema_version}（期望 {expected_schema_version}）"
        )
    members = document["members"]
    if not isinstance(members, list):
        raise UniverseArtifactError("artifact members 必须是数组")
    previous: tuple[str, str] | None = None
    for index, member in enumerate(members):
        if not isinstance(member, dict):
            raise UniverseArtifactError(f"members[{index}] 必须是 JSON object")
        unknown = sorted(set(member) - MEMBER_KEYS)
        missing = sorted(MEMBER_KEYS - set(member))
        if unknown or missing:
            raise UniverseArtifactError(
                f"members[{index}] 键集合非法: missing={missing}, unknown={unknown}"
            )
        lake_pair = member["lake_pair"]
        if not isinstance(lake_pair, str) or not lake_pair:
            raise UniverseArtifactError(f"members[{index}].lake_pair 必须是非空字符串")
        start_text = member["valid_from"]
        if not isinstance(start_text, str):
            raise UniverseArtifactError(f"members[{index}].valid_from 必须是字符串")
        end_text = member["valid_to"]
        if end_text is not None and not isinstance(end_text, str):
            raise UniverseArtifactError(f"members[{index}].valid_to 必须是字符串或 null")
        start = parse_utc(start_text, field=f"members[{index}].valid_from")
        if end_text is not None:
            end = parse_utc(end_text, field=f"members[{index}].valid_to")
            if end <= start:
                raise UniverseArtifactError(
                    f"members[{index}] valid_to 必须晚于 valid_from: {start_text} → {end_text}"
                )
        key = (lake_pair, utc_iso(start))
        if previous is not None and key < previous:
            raise UniverseArtifactError(
                f"members 未按 (lake_pair, valid_from) 排序: {previous} → {key}"
            )
        if previous is not None and key == previous:
            raise UniverseArtifactError(f"members 出现重复键: {key}")
        previous = key


def digest_for(document: dict[str, Any]) -> str:
    return sha256_prefixed(canonical_artifact_bytes(document))


def publish_artifact(
    intervals: Iterable[TradabilityInterval], lake_root: Path | None = None
) -> tuple[str, Path]:
    """原子发布（写一次）：返回 `(digest, path)`；同 digest 内容不同即报错。"""
    document = build_document(intervals)
    payload = canonical_artifact_bytes(document)
    digest = sha256_prefixed(payload)
    target = artifact_path(digest, lake_root)
    atomic_create(target, payload)
    return digest, target


def load_artifact(
    digest: str,
    lake_root: Path | None = None,
    *,
    expected_schema_version: int = SCHEMA_VERSION,
) -> ArtifactLedger:
    """按显式 digest 载入：digest 不符、版本不符、未知键或非 canonical 一律拒绝。"""
    path = artifact_path(digest, lake_root)
    payload = read_bytes(path, what="universe artifact")
    try:
        document = json.loads(payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise UniverseArtifactError(f"universe artifact 不是合法 UTF-8 JSON: {path}") from exc
    validate_document(document, expected_schema_version=expected_schema_version)
    recomputed = sha256_prefixed(canonical_json_bytes(document))
    if recomputed != digest:
        raise UniverseArtifactError(
            f"universe artifact digest 不符: 期望 {digest}，重算 {recomputed}（{path}）"
        )
    members = tuple(
        ArtifactMember(
            lake_pair=str(item["lake_pair"]),
            valid_from=parse_utc(str(item["valid_from"]), field="valid_from"),
            valid_to=None
            if item["valid_to"] is None
            else parse_utc(str(item["valid_to"]), field="valid_to"),
        )
        for item in document["members"]
    )
    return ArtifactLedger(
        digest=digest, schema_version=int(document["schema_version"]), members=members
    )


def members_for_intervals(intervals: Sequence[TradabilityInterval]) -> tuple[ArtifactMember, ...]:
    """测试友好的视图转换（与 `build_document` 同源，避免两处排序规则漂移）。"""
    document = build_document(intervals)
    return tuple(
        ArtifactMember(
            lake_pair=str(item["lake_pair"]),
            valid_from=parse_utc(str(item["valid_from"]), field="valid_from"),
            valid_to=None
            if item["valid_to"] is None
            else parse_utc(str(item["valid_to"]), field="valid_to"),
        )
        for item in document["members"]
    )
