"""导出准入绑定的宇宙版本解析（F011 `FR-002` / `IR-003` / T003）。

纯文件计算，不连库：枚举 `<lake>/_metadata/universe_defs/*.frozen.json`，按两条规则选版：

- **过滤**看生效：`frozen_at ≤ at ∧ snapshot_at ≤ at`（当时已人工确认、且不反映未来市场）。
  `frozen_at` 保证历史回放与当时实际绑定一致；`snapshot_at` 另查一次，因为
  `freeze_definition(frozen_at=...)` 允许注入早于求值的冻结时刻。
- **定序**看市场时点：`(snapshot_at, frozen_at, universe_id)`，晚冻结的旧快照不覆盖新快照。

同一次解析还给出**版本链**（同口径、生效、定序不晚于被绑定版本），供落选截止日计算：
截止日 = 本次连续落选段内各版本 `frozen_at` 的最早 UTC 日期（spec §1 术语）。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from alphamill.data_bridge.universe.canonical import parse_utc
from alphamill.data_bridge.universe.definition import (
    FREEZE_SUFFIX,
    FreezeRecord,
    UniverseDef,
    defs_dir,
    load_definition,
    load_freeze,
)
from alphamill.data_bridge.universe.errors import (
    UniverseAmbiguousError,
    UniverseArtifactError,
    UniverseLookaheadError,
    UniverseNotFoundError,
    UniverseNotFrozenError,
)

RESOLUTION_DEFAULT = "default"
RESOLUTION_EXPLICIT = "explicit"

Version = tuple[UniverseDef, FreezeRecord]


@dataclass(frozen=True, kw_only=True)
class Binding:
    """被绑定的宇宙版本 + 版本链（升序，末项即被绑定版本）。"""

    definition: UniverseDef
    freeze: FreezeRecord
    chain: tuple[Version, ...]
    resolution: str

    @property
    def universe_id(self) -> str:
        return self.definition.universe_id

    def selected_symbols(self) -> frozenset[str]:
        return frozenset(self.definition.selected_pairs())

    def drop_cutoff(self, db_symbol: str) -> date | None:
        """落选截止日；被绑定版本选中 ⇒ None。

        从链尾向前收集「未选中该 pair」的版本，遇到最近一个选中它的版本即停（不含）；
        取这一段里最早的冻结日。从未被选中过的 pair，这一段就是整条链。
        """
        if db_symbol in self.selected_symbols():
            return None
        segment: list[FreezeRecord] = []
        for definition, freeze in reversed(self.chain):
            if db_symbol in definition.selected_pairs():
                break
            segment.append(freeze)
        return min(_moment(item.frozen_at, "frozen_at").date() for item in segment)


def resolve_binding(
    at: datetime, *, universe_id: str | None = None, lake_root: Path | None = None
) -> Binding:
    """按 spec `FR-002` 解析被绑定版本；拒绝分支抛 `IR-003` 表中的 `UniverseError` 子类。"""
    if universe_id is not None:
        definition = load_definition(universe_id, lake_root)  # 不存在 → E_UNIVERSE_NOT_FOUND
        freeze = load_freeze(universe_id, lake_root)
        if freeze is None:
            raise UniverseNotFrozenError(
                f"universe {universe_id} 尚未人工确认冻结，不能绑定导出（先 freeze --confirm）"
            )
        if not _effective((definition, freeze), at):
            raise UniverseLookaheadError(
                f"universe {universe_id} 在窗口终点 {at.isoformat()} 时尚未生效"
                f"（snapshot_at={definition.snapshot_at}, frozen_at={freeze.frozen_at}），不许前视"
            )
        bound: Version = (definition, freeze)
        versions = [item for item in _frozen_versions(lake_root) if _effective(item, at)]
        resolution = RESOLUTION_EXPLICIT
    else:
        versions = [item for item in _frozen_versions(lake_root) if _effective(item, at)]
        if not versions:
            raise UniverseNotFrozenError(
                f"没有在窗口终点 {at.isoformat()} 前生效的冻结宇宙定义，拒绝导出（不静默放行全集）"
            )
        scopes = {_scope(item) for item in versions}
        if len(scopes) > 1:
            raise UniverseAmbiguousError(
                f"冻结定义存在多种口径 {sorted(scopes)}，默认解析拒绝串线；"
                "请用 --universe-id 显式指定"
            )
        bound = max(versions, key=_order_key)
        resolution = RESOLUTION_DEFAULT
    chain = sorted(
        (
            item
            for item in versions
            if _scope(item) == _scope(bound) and _order_key(item) <= _order_key(bound)
        ),
        key=_order_key,
    )
    if not chain or chain[-1][0].universe_id != bound[0].universe_id:
        chain.append(bound)
    return Binding(definition=bound[0], freeze=bound[1], chain=tuple(chain), resolution=resolution)


def _frozen_versions(lake_root: Path | None) -> list[Version]:
    """全部已冻结版本；冻结记录或定义损坏一律 fail-closed（`E_UNIVERSE_ARTIFACT`）。"""
    root = defs_dir(lake_root)
    if not root.is_dir():
        return []
    out: list[Version] = []
    for path in sorted(root.glob(f"*{FREEZE_SUFFIX}")):
        universe_id = path.name[: -len(FREEZE_SUFFIX)]
        freeze = load_freeze(universe_id, lake_root)
        if freeze is None:
            continue
        try:
            definition = load_definition(universe_id, lake_root)
        except UniverseNotFoundError as exc:  # 有冻结记录无定义：湖内产物损坏（检视 R3）
            raise UniverseArtifactError(f"冻结记录 {path.name} 没有对应的定义文件") from exc
        out.append((definition, freeze))
    return out


def _effective(version: Version, at: datetime) -> bool:
    definition, freeze = version
    return (
        _moment(freeze.frozen_at, "frozen_at") <= at
        and _moment(definition.snapshot_at, "snapshot_at") <= at
    )


def _order_key(version: Version) -> tuple[datetime, datetime, str]:
    definition, freeze = version
    return (
        _moment(definition.snapshot_at, "snapshot_at"),
        _moment(freeze.frozen_at, "frozen_at"),
        definition.universe_id,
    )


def _scope(version: Version) -> tuple[str, str]:
    criteria = version[0].criteria
    return (criteria.exchange, criteria.market_type)


def _moment(text: str, field: str) -> datetime:
    return parse_utc(text, field=field)
