"""F008 point-in-time 宇宙台账的只读消费面（F007 `IR-002`/`DR-006`，任务 T001）。

F007 只读、按显式 digest 加载 F008 的内容寻址台账，并提供 `universe_at(T)` 语义查询；
不实现宇宙扩容、不解析 latest、不把台账复制进 `reports/`。

台账 canonical 格式（对齐 F008 `IR-002`/`IR-003` 与 `DR-002`）：UTF-8、LF、固定列序
`UNIVERSE_COLUMNS`、按全列排序；digest = canonical 字节的 SHA-256。成员区间为半开区间
`[valid_from, valid_to)`，`valid_to` 为空表示当前有效（无上界）。
"""

from __future__ import annotations

import csv
import errno
import io
import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from alphamill.data_bridge import paths
from alphamill.evaluation.contract_common import (
    DIGEST_PREFIX,
    UNIVERSE_COLUMNS,
    UNIVERSE_SCHEMA_VERSION,
    UpstreamContractError,
    content_digest,
    parse_utc,
)


@dataclass(frozen=True)
class UniverseMember:
    exchange: str
    market_type: str
    db_symbol: str
    lake_pair: str
    valid_from: str
    valid_to: str  # 空串 = 当前有效
    reason: str
    universe_id: str

    def active_at(self, moment: datetime) -> bool:
        """半开区间 `[valid_from, valid_to)`；`valid_to` 为空表示无上界。"""
        if moment < parse_utc(self.valid_from, "valid_from"):
            return False
        if not self.valid_to:
            return True
        return moment < parse_utc(self.valid_to, "valid_to")


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


def _sort_key(member: UniverseMember) -> tuple[str, ...]:
    return (
        member.exchange,
        member.market_type,
        member.db_symbol,
        member.lake_pair,
        member.valid_from,
        member.valid_to,
        member.reason,
        member.universe_id,
    )


def canonical_universe_bytes(members: Iterable[UniverseMember]) -> bytes:
    """canonical 台账字节：固定列序 + 全列排序 + UTF-8/LF。"""
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(UNIVERSE_COLUMNS)
    for member in sorted(members, key=_sort_key):
        writer.writerow(
            [
                member.exchange,
                member.market_type,
                member.db_symbol,
                member.lake_pair,
                member.valid_from,
                member.valid_to,
                member.reason,
                member.universe_id,
                str(UNIVERSE_SCHEMA_VERSION),
            ]
        )
    return buffer.getvalue().encode("utf-8")


def publish_universe(members: Iterable[UniverseMember], lake_root: Path | None = None) -> str:
    """内容寻址发布台账并返回 digest；同 digest 必须逐字节一致，否则拒绝。"""
    rows = tuple(members)
    payload = canonical_universe_bytes(rows)
    digest = content_digest(payload)
    target = universe_artifact_dir(lake_root) / f"{digest}.csv"
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
    """按显式 digest 只读加载；digest 缺失/不符、列序非法或 schema 未知高版本即失败关闭。"""
    if not isinstance(digest, str) or not digest.startswith(DIGEST_PREFIX):
        raise UpstreamContractError(f"universe digest 缺失或格式非法: {digest!r}")
    path = universe_artifact_dir(lake_root) / f"{digest}.csv"
    if not path.is_file():
        raise UpstreamContractError(f"universe artifact 不存在: {path}")
    payload = path.read_bytes()
    if content_digest(payload) != digest:
        raise UpstreamContractError(f"universe digest 校验失败: {path}")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UpstreamContractError(f"universe artifact 不是 UTF-8: {path}") from exc
    rows = list(csv.reader(io.StringIO(text, newline="")))
    if not rows or tuple(rows[0]) != UNIVERSE_COLUMNS:
        raise UpstreamContractError(f"universe 台账列序非法: {rows[0] if rows else None}")
    members = []
    for index, row in enumerate(rows[1:], start=1):
        member, schema_version = _member_from_row(index, row)
        if schema_version != str(UNIVERSE_SCHEMA_VERSION):
            raise UpstreamContractError(
                f"不支持的 universe schema_version: {schema_version!r}（期望 "
                f"{UNIVERSE_SCHEMA_VERSION}，未知高版本失败关闭）"
            )
        members.append(member)
    if canonical_universe_bytes(members) != payload:
        raise UpstreamContractError(f"universe 台账不是 canonical 形式（排序/字节）: {path}")
    return UniverseLedger(
        digest=digest, schema_version=UNIVERSE_SCHEMA_VERSION, members=tuple(members)
    )


def _member_from_row(index: int, row: list[str]) -> tuple[UniverseMember, str]:
    if len(row) != len(UNIVERSE_COLUMNS):
        raise UpstreamContractError(f"universe 第 {index} 行列数 {len(row)} 不符合契约")
    values = dict(zip(UNIVERSE_COLUMNS, row, strict=True))
    member = UniverseMember(
        exchange=values["exchange"],
        market_type=values["market_type"],
        db_symbol=values["db_symbol"],
        lake_pair=values["lake_pair"],
        valid_from=values["valid_from"],
        valid_to=values["valid_to"],
        reason=values["reason"],
        universe_id=values["universe_id"],
    )
    parse_utc(member.valid_from, f"universe 第 {index} 行 valid_from")
    if member.valid_to:
        end = parse_utc(member.valid_to, f"universe 第 {index} 行 valid_to")
        if end <= parse_utc(member.valid_from, "valid_from"):
            raise UpstreamContractError(f"universe 第 {index} 行 valid_to 必须晚于 valid_from")
    return member, values["schema_version"]
