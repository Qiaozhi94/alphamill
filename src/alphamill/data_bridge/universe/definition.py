"""`UniverseDef` 的内容寻址、人工确认冻结与版本化（`FR-002` / `AC-002` / T005）。

三个不变量把「未冻结的宇宙不得驱动长跑」变成结构性质：

1. **id 只覆盖口径 + 快照时间 + 候选清单**（`design.md` §3 的公式）——同一口径同一快照
   必然同 id，冻结时间/冻结人不参与 id，因此冻结不改变身份；
2. **定义文件写一次**：`<universe_id>.json` 落 `<lake>/_metadata/universe_defs/`，
   同 id 内容不同即报错，没有 UPDATE 路径；
3. **冻结是独立的追加记录**：`<universe_id>.frozen.json`（`frozen_at` / `frozen_by`）。
   回填、门禁等长跑任务要求该记录存在；发现产出的草稿没有它，因此天然无法驱动长跑。
   成员增删会改变候选清单 → 产生新 `universe_id` → 新定义与新冻结记录，旧版本保持只读。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alphamill.data_bridge import paths
from alphamill.data_bridge.universe.canonical import (
    canonical_json_bytes,
    content_digest,
    parse_utc,
    utc_iso,
)
from alphamill.data_bridge.universe.criteria import Criteria, criteria_from_payload
from alphamill.data_bridge.universe.discover import Candidate, Evaluation
from alphamill.data_bridge.universe.errors import (
    UniverseAlreadyFrozenError,
    UniverseArtifactError,
    UniverseNotFoundError,
    UniverseNotFrozenError,
)
from alphamill.data_bridge.universe.storage import atomic_create, read_bytes

SCHEMA_VERSION = 1
DEF_SUFFIX = ".json"
FREEZE_SUFFIX = ".frozen.json"
_DEF_KEYS = frozenset({"schema_version", "universe_id", "criteria", "snapshot_at", "candidates"})
_FREEZE_KEYS = frozenset({"schema_version", "universe_id", "frozen_at", "frozen_by"})
_CANDIDATE_KEYS = frozenset(
    {
        "db_symbol",
        "lake_pair",
        "base",
        "quote",
        "listed_at",
        "listed_days",
        "turnover_usdt",
        "turnover_points",
        "rank",
        "excluded_reason",
    }
)


@dataclass(frozen=True, kw_only=True)
class UniverseDef:
    """不可变宇宙定义（定义文件的内容视图；冻结信息另存）。"""

    universe_id: str
    criteria: Criteria
    snapshot_at: str
    candidates: tuple[Candidate, ...]

    @property
    def selected(self) -> tuple[Candidate, ...]:
        return tuple(item for item in self.candidates if item.rank is not None)

    def selected_pairs(self) -> tuple[str, ...]:
        return tuple(item.db_symbol for item in self.selected)

    def db_symbols(self) -> tuple[str, ...]:
        return tuple(item.db_symbol for item in self.candidates)

    def payload(self) -> dict[str, Any]:
        """进入 `universe_id` 的字节（不含 id 自身与冻结信息）。"""
        return {
            "criteria": self.criteria.payload(),
            "snapshot_at": self.snapshot_at,
            "candidates": [item.payload() for item in self.candidates],
        }

    def document(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "universe_id": self.universe_id, **self.payload()}


@dataclass(frozen=True, kw_only=True)
class FreezeRecord:
    universe_id: str
    frozen_at: str
    frozen_by: str

    def document(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "universe_id": self.universe_id,
            "frozen_at": self.frozen_at,
            "frozen_by": self.frozen_by,
        }


def compute_universe_id(criteria: Criteria, evaluation: Evaluation) -> str:
    """`universe_id = sha256(canonical_json(criteria + snapshot_at + candidates))`。"""
    return content_digest({"criteria": criteria.payload(), **evaluation.payload()})


def build_definition(criteria: Criteria, evaluation: Evaluation) -> UniverseDef:
    return UniverseDef(
        universe_id=compute_universe_id(criteria, evaluation),
        criteria=criteria,
        snapshot_at=evaluation.snapshot_at,
        candidates=evaluation.candidates,
    )


def defs_dir(lake_root: Path | None = None) -> Path:
    root = Path(lake_root) if lake_root is not None else paths.lake_root()
    return root / "_metadata" / "universe_defs"


def definition_path(universe_id: str, lake_root: Path | None = None) -> Path:
    return defs_dir(lake_root) / f"{universe_id}{DEF_SUFFIX}"


def freeze_path(universe_id: str, lake_root: Path | None = None) -> Path:
    return defs_dir(lake_root) / f"{universe_id}{FREEZE_SUFFIX}"


def write_definition(definition: UniverseDef, lake_root: Path | None = None) -> Path:
    """写一次：同 id 内容不同即报错（定义不可原地改写）。"""
    target = definition_path(definition.universe_id, lake_root)
    atomic_create(target, canonical_json_bytes(definition.document()))
    return target


def load_definition(universe_id: str, lake_root: Path | None = None) -> UniverseDef:
    """按显式 id 载入定义；缺文件、键集合非法或 id 与内容不符一律 fail-closed。"""
    path = definition_path(universe_id, lake_root)
    document = _read_json(path, what="UniverseDef")
    unknown = sorted(set(document) - _DEF_KEYS)
    missing = sorted(_DEF_KEYS - set(document))
    if unknown or missing:
        raise UniverseArtifactError(
            f"UniverseDef 键集合非法（{path}）: missing={missing}, unknown={unknown}"
        )
    if document["schema_version"] != SCHEMA_VERSION:
        raise UniverseArtifactError(
            f"UniverseDef schema_version 不支持: {document['schema_version']!r}"
        )
    criteria = criteria_from_payload(_require_mapping(document["criteria"], "criteria"))
    snapshot_at = utc_iso(parse_utc(str(document["snapshot_at"]), field="snapshot_at"))
    candidates = tuple(
        _candidate_from_payload(item, index) for index, item in enumerate(document["candidates"])
    )
    evaluation = Evaluation(snapshot_at=snapshot_at, candidates=candidates)
    computed = compute_universe_id(criteria, evaluation)
    if computed != universe_id or document["universe_id"] != universe_id:
        raise UniverseArtifactError(
            f"UniverseDef 内容与 universe_id 不符（{path}）: 重算 {computed}"
        )
    return UniverseDef(
        universe_id=universe_id,
        criteria=criteria,
        snapshot_at=snapshot_at,
        candidates=candidates,
    )


def freeze_definition(
    universe_id: str,
    *,
    frozen_by: str,
    lake_root: Path | None = None,
    frozen_at: datetime | None = None,
) -> FreezeRecord:
    """人工确认后写入冻结记录；缺 `frozen_by` 判红，重复冻结内容不同判红。"""
    if not frozen_by or not frozen_by.strip():
        raise UniverseArtifactError("冻结必须记录 frozen_by（人工确认者）")
    load_definition(universe_id, lake_root)  # 定义不存在即 fail-closed
    record = FreezeRecord(
        universe_id=universe_id,
        frozen_at=utc_iso(frozen_at or datetime.now(UTC)),
        frozen_by=frozen_by.strip(),
    )
    atomic_create(freeze_path(universe_id, lake_root), canonical_json_bytes(record.document()))
    return record


def load_freeze(universe_id: str, lake_root: Path | None = None) -> FreezeRecord | None:
    """返回冻结记录；没有冻结记录返回 None（草稿状态）。"""
    path = freeze_path(universe_id, lake_root)
    if not path.is_file():
        return None
    document = _read_json(path, what="UniverseDef 冻结记录")
    unknown = sorted(set(document) - _FREEZE_KEYS)
    if unknown or _FREEZE_KEYS - set(document):
        raise UniverseArtifactError(f"冻结记录键集合非法（{path}）: unknown={unknown}")
    if document["schema_version"] != SCHEMA_VERSION:
        raise UniverseArtifactError(
            f"冻结记录 schema_version 不支持: {document['schema_version']!r}"
        )
    if document["universe_id"] != universe_id:
        raise UniverseArtifactError(f"冻结记录与 universe_id 不符（{path}）")
    return FreezeRecord(
        universe_id=universe_id,
        frozen_at=str(document["frozen_at"]),
        frozen_by=str(document["frozen_by"]),
    )


def is_frozen(universe_id: str, lake_root: Path | None = None) -> bool:
    return load_freeze(universe_id, lake_root) is not None


def require_frozen(universe_id: str, lake_root: Path | None = None) -> UniverseDef:
    """长跑任务（回填/门禁）的入口校验：未冻结的定义一律拒绝。"""
    if load_freeze(universe_id, lake_root) is None:
        raise UniverseNotFrozenError(
            f"universe {universe_id} 尚未人工确认冻结，拒绝驱动长跑任务（先 freeze --confirm）"
        )
    return load_definition(universe_id, lake_root)


def _read_json(path: Path, *, what: str) -> dict[str, Any]:
    if not path.is_file():
        raise UniverseNotFoundError(f"{what} 不存在: {path}")
    payload = read_bytes(path, what=what)
    try:
        document = json.loads(payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise UniverseArtifactError(f"{what} 不是合法 UTF-8 JSON: {path}: {exc}") from exc
    return _require_mapping(document, what)


def _require_mapping(value: Any, what: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise UniverseArtifactError(f"{what} 必须是 JSON object")
    return value


def _candidate_from_payload(value: Any, index: int) -> Candidate:
    item = _require_mapping(value, f"candidates[{index}]")
    unknown = sorted(set(item) - _CANDIDATE_KEYS)
    missing = sorted(_CANDIDATE_KEYS - set(item))
    if unknown or missing:
        raise UniverseArtifactError(
            f"candidates[{index}] 键集合非法: missing={missing}, unknown={unknown}"
        )
    return Candidate(
        db_symbol=str(item["db_symbol"]),
        lake_pair=str(item["lake_pair"]),
        base=str(item["base"]),
        quote=str(item["quote"]),
        listed_at=utc_iso(
            parse_utc(str(item["listed_at"]), field=f"candidates[{index}].listed_at")
        ),
        listed_days=int(item["listed_days"]),
        turnover_usdt=float(item["turnover_usdt"]),
        turnover_points=int(item["turnover_points"]),
        rank=None if item["rank"] is None else int(item["rank"]),
        excluded_reason=None if item["excluded_reason"] is None else str(item["excluded_reason"]),
    )


def ensure_unique_versions(ids: list[str]) -> None:
    """版本化自检：不同成员集合必须得到不同 id（供测试与冻结前复核使用）。"""
    if len(set(ids)) != len(ids):
        raise UniverseAlreadyFrozenError(f"不同成员集合产生了重复 universe_id: {ids}")
