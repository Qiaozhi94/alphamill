"""F008 point-in-time 宇宙台账的只读消费面（F007 `IR-002`/`DR-006`，任务 T029）。

F007 只读、按显式 digest 加载 F008 的内容寻址台账，并提供 `universe_at(T)` 语义查询；
不实现宇宙扩容、不解析 latest、不把台账复制进 `reports/`。

台账 canonical 格式（F008 `IR-002`/`IR-003`）：

- 文件：`<lake_root>/_metadata/universes/<digest>.json`，digest 形如 `sha256:<64hex>`，
  前缀进文件名；
- 顶层键严格等于 `UNIVERSE_TOP_LEVEL_KEYS`，成员键严格等于 `UNIVERSE_MEMBER_KEYS`，
  多一个键即判非法，不做宽松忽略；
- `members` 按 `(lake_pair, valid_from)` 排序，对象键字典序；UTF-8、无多余空白、无尾随换行；
- `valid_from` 为 UTC ISO-8601 字符串，`valid_to` 为 UTC ISO-8601 字符串或 `null`
  （`null` = 当前有效，无上界）；
- canonical 字节 = `json.dumps(doc, sort_keys=True, separators=(",", ":"),
  ensure_ascii=False, allow_nan=False).encode("utf-8")`；`digest = "sha256:" +
  sha256(canonical 字节).hexdigest()`。

消费侧的规范化**独立实现**——不 import `alphamill.data_bridge.universe.canonical`（发布侧）：
两侧共用同一实现时，规范漂移会在两侧同时发生而无人发现。这里用 stdlib `json` 复算 canonical
字节，并按解析后的文档重算 digest 与显式引用比对；未知键、未知 `schema_version`、区间重叠
与非法时间一律经 `UpstreamContractError` 失败关闭。

成员区间为半开区间 `[valid_from, valid_to)`，`valid_to = None` 表示无上界。
"""

from __future__ import annotations

import errno
import json
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from alphamill.data_bridge import paths
from alphamill.evaluation.contract_common import (
    DIGEST_PREFIX,
    UNIVERSE_MEMBER_KEYS,
    UNIVERSE_SCHEMA_VERSION,
    UNIVERSE_TOP_LEVEL_KEYS,
    UpstreamContractError,
    content_digest,
    parse_utc,
)


@dataclass(frozen=True)
class UniverseMember:
    """`IR-002` 最小 PIT 投影的一条成员区间。

    只承载 `universe_at(T)` 判定所需的三个字段；`exchange` / `market_type` /
    `db_symbol` / `reason` / `universe_id` / `ingested_at` 等审计列留在联机库
    `universe_membership` 表，不进 artifact。
    """

    lake_pair: str
    valid_from: datetime
    valid_to: datetime | None  # None = 当前有效（无上界）

    def active_at(self, moment: datetime) -> bool:
        """半开区间 `[valid_from, valid_to)`；`valid_to` 为 None 表示无上界。"""
        if moment < self.valid_from:
            return False
        if self.valid_to is None:
            return True
        return moment < self.valid_to


@dataclass(frozen=True)
class UniverseLedger:
    """F008 内容寻址宇宙台账的只读视图。"""

    digest: str
    schema_version: int
    members: tuple[UniverseMember, ...]

    def members_at(self, moment: Any) -> tuple[UniverseMember, ...]:
        when = parse_utc(moment, "universe_at(T)")
        return tuple(member for member in self.members if member.active_at(when))

    def universe_at(self, moment: Any) -> tuple[str, ...]:
        """T 时刻的成员 `lake_pair` 集合（排序、去重）——`NFR-003` 无幸存者偏差。"""
        return tuple(sorted({member.lake_pair for member in self.members_at(moment)}))


def universe_artifact_dir(lake_root: Path | None = None) -> Path:
    root = Path(lake_root) if lake_root is not None else paths.lake_root()
    return root / "_metadata" / "universes"


def _utc_iso(value: datetime) -> str:
    """落盘时间戳：UTC ISO-8601 `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`，与发布侧同格式。"""
    return value.isoformat().replace("+00:00", "Z")


def _checked_times(
    valid_from: Any, valid_to: Any, field: str
) -> tuple[datetime, datetime | None]:
    """归一化并校验成员区间：`valid_to` 为 None 表示无上界，否则必须晚于 `valid_from`。"""
    start = parse_utc(valid_from, f"{field} valid_from")
    if valid_to is None:
        return start, None
    end = parse_utc(valid_to, f"{field} valid_to")
    if end <= start:
        raise UpstreamContractError(f"{field} valid_to 必须晚于 valid_from")
    return start, end


def _normalize_member(member: UniverseMember) -> UniverseMember:
    if not isinstance(member.lake_pair, str) or not member.lake_pair:
        raise UpstreamContractError("universe 成员 lake_pair 必须是非空字符串")
    valid_from, valid_to = _checked_times(member.valid_from, member.valid_to, "universe 成员")
    return UniverseMember(lake_pair=member.lake_pair, valid_from=valid_from, valid_to=valid_to)


def _member_document(member: UniverseMember) -> dict[str, Any]:
    valid_to = member.valid_to
    return {
        "lake_pair": member.lake_pair,
        "valid_from": _utc_iso(member.valid_from),
        "valid_to": None if valid_to is None else _utc_iso(valid_to),
    }


def _canonical_bytes(document: Mapping[str, Any]) -> bytes:
    """`IR-002` 冻结的 canonical 字节规则（本模块自实现，不 import 发布侧规范化模块）。"""
    try:
        text = json.dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise UpstreamContractError(f"universe 台账无法规范化为 canonical JSON: {exc}") from exc
    return text.encode("utf-8")


def canonical_universe_bytes(members: Iterable[UniverseMember]) -> bytes:
    """canonical 台账字节：顶层 `{schema_version, members}`、成员按 `(lake_pair, valid_from)` 排序。"""
    normalized = [_normalize_member(member) for member in members]
    _assert_no_overlap(normalized)
    documents = sorted(
        (_member_document(member) for member in normalized),
        key=lambda item: (item["lake_pair"], item["valid_from"]),
    )
    return _canonical_bytes({"schema_version": UNIVERSE_SCHEMA_VERSION, "members": documents})


def publish_universe(members: Iterable[UniverseMember], lake_root: Path | None = None) -> str:
    """按 canonical JSON 发布台账并返回 digest（**仅测试夹具构造器**）。

    生产发布者是 F008 的 `data_bridge/universe/artifact.py`（T009）——本函数只服务于
    F007 契约与集成测试的夹具构造，不参与生产路径。发布纪律与生产侧一致：原子创建、
    同 digest 必须逐字节一致、冲突即报错而非覆盖。
    """
    payload = canonical_universe_bytes(members)
    digest = content_digest(payload)
    target = universe_artifact_dir(lake_root) / f"{digest}.json"
    if target.is_file():
        if target.read_bytes() != payload:
            raise UpstreamContractError(f"同 digest universe artifact 内容不一致: {target}")
        return digest
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f"{target.name}.tmp-{os.getpid()}")
    tmp.write_bytes(payload)
    try:
        try:
            os.link(tmp, target)
        except FileExistsError as exc:
            raise UpstreamContractError(
                f"同 digest universe artifact 内容不一致: {target}"
            ) from exc
        except OSError as exc:
            if exc.errno not in {errno.EXDEV, errno.EPERM, errno.EOPNOTSUPP, errno.ENOTSUP}:
                raise
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
    finally:
        tmp.unlink(missing_ok=True)
    return digest


def load_universe(digest: str, lake_root: Path | None = None) -> UniverseLedger:
    """按显式 digest 只读加载；digest 缺失/不符、未知键或版本不符即失败关闭。"""
    if not isinstance(digest, str) or not digest.startswith(DIGEST_PREFIX):
        raise UpstreamContractError(f"universe digest 缺失或格式非法: {digest!r}")
    path = universe_artifact_dir(lake_root) / f"{digest}.json"
    if not path.is_file():
        raise UpstreamContractError(f"universe artifact 不存在: {path}")
    payload = path.read_bytes()
    if content_digest(payload) != digest:
        raise UpstreamContractError(f"universe digest 校验失败: {path}")
    document = _parse_document(payload, path)
    if _canonical_bytes(document) != payload:
        raise UpstreamContractError(f"universe 台账不是 canonical 形式（排序/字节）: {path}")
    members = _members_from_document(document)
    _assert_no_overlap(members)
    return UniverseLedger(
        digest=digest, schema_version=UNIVERSE_SCHEMA_VERSION, members=members
    )


def _parse_document(payload: bytes, path: Path) -> dict[str, Any]:
    """解析并做结构/版本校验：顶层与成员键集合必须严格相等，未知键即拒绝。"""
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UpstreamContractError(f"universe artifact 不是 UTF-8: {path}") from exc
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UpstreamContractError(f"universe artifact 不是合法 JSON: {path}") from exc
    if not isinstance(document, dict):
        raise UpstreamContractError(f"universe 台账顶层必须是对象: {path}")
    if set(document) != UNIVERSE_TOP_LEVEL_KEYS:
        raise UpstreamContractError(
            f"universe 台账顶层键非法: {sorted(document)}（期望 {sorted(UNIVERSE_TOP_LEVEL_KEYS)}）"
        )
    version = document["schema_version"]
    if isinstance(version, bool) or not isinstance(version, int):
        raise UpstreamContractError(f"universe schema_version 必须是整数: {version!r}")
    if version != UNIVERSE_SCHEMA_VERSION:
        raise UpstreamContractError(
            f"不支持的 universe schema_version: {version!r}（期望 {UNIVERSE_SCHEMA_VERSION}，"
            "未知版本失败关闭）"
        )
    if not isinstance(document["members"], list):
        raise UpstreamContractError(f"universe 台账 members 必须是数组: {path}")
    return document


def _members_from_document(document: Mapping[str, Any]) -> tuple[UniverseMember, ...]:
    return tuple(
        _member_from_document(index, item)
        for index, item in enumerate(document["members"])
    )


def _member_from_document(index: int, item: Any) -> UniverseMember:
    if not isinstance(item, dict):
        raise UpstreamContractError(f"universe 第 {index} 个成员必须是对象")
    if set(item) != UNIVERSE_MEMBER_KEYS:
        raise UpstreamContractError(
            f"universe 第 {index} 个成员键非法: {sorted(item)}"
            f"（期望 {sorted(UNIVERSE_MEMBER_KEYS)}）"
        )
    lake_pair = item["lake_pair"]
    if not isinstance(lake_pair, str) or not lake_pair:
        raise UpstreamContractError(f"universe 第 {index} 个成员 lake_pair 必须是非空字符串")
    valid_from, valid_to = _checked_times(
        item["valid_from"], item["valid_to"], f"universe 第 {index} 个成员"
    )
    return UniverseMember(lake_pair=lake_pair, valid_from=valid_from, valid_to=valid_to)


def _assert_no_overlap(members: Iterable[UniverseMember]) -> None:
    """同一 `lake_pair` 的区间不得重叠（端点相接合法）——design §3 消费方强制项。"""
    windows: dict[str, list[tuple[datetime, datetime | None]]] = {}
    for member in members:
        windows.setdefault(member.lake_pair, []).append((member.valid_from, member.valid_to))
    for lake_pair, spans in windows.items():
        spans.sort(key=lambda span: span[0])
        for index in range(1, len(spans)):
            previous_end = spans[index - 1][1]
            start = spans[index][0]
            if previous_end is None or previous_end > start:
                raise UpstreamContractError(
                    f"overlapping validity windows: {lake_pair} 的成员区间重叠"
                    f"（{spans[index - 1][0].isoformat()} 起的区间未在 {start.isoformat()} 前结束）"
                )
