"""生成运行记录的 schema：字段定义、严格解析与终态校验（F012 `DR-001`，design §1 第 8 行）。

自 `run_store.py` 迁出（SOP 350 行上限），`run_store` 以同名再导出，导入方零改动。
run.json 当前写入版本为 2（新增 `budget`、`stop_reason`、`evaluations` 与
`objective.position_rule`）；
读取同时接受 v1（缺省值补齐后严格校验）。事件信封版本 `EVENT_SCHEMA_VERSION` 与 run.json 解耦
（文档检视 D20/D40），本模块是叶子模块，不导入 run_store。
"""

from __future__ import annotations

import json
import types
from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Final, Literal, TypeAlias, TypeVar, get_args, get_origin, get_type_hints

from alphamill.factor_factory import canonical, errors
from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.generators import base, binding

RUN_SCHEMA_VERSION: Final = 2
RUN_SCHEMA_VERSIONS: Final = frozenset({1, 2})
EVENT_SCHEMA_VERSION: Final = 1
RunStatus: TypeAlias = Literal["completed", "rejected", "failed", "partial"]
TierLevel: TypeAlias = Literal["L0", "L1", "L2", "manual"]
StopReason: TypeAlias = Literal["quota_reached", "budget_exhausted", "window_closed", "interrupted"]
PositionRule: TypeAlias = Literal["sign", "cs_median"]
_COMPLETED_REASONS: Final = frozenset({"quota_reached", "budget_exhausted"})
_PARTIAL_REASONS: Final = frozenset({"window_closed", "interrupted"})
_V2_FIELDS: Final = ("budget", "stop_reason", "evaluations")
_T = TypeVar("_T")


@dataclass(frozen=True, kw_only=True)
class EngineInfo:
    vendor_commit: str | None
    code_digest: str
    dependencies: dict[str, str]


@dataclass(frozen=True, kw_only=True)
class UniverseSummary:
    pair_count: int
    symbol_map_digest: str
    universe_digest: str
    source: str


@dataclass(frozen=True, kw_only=True)
class ObjectiveInfo:
    turnover_penalty_lambda: float
    reachability_min_trades_90d: int
    cost_model: dict[str, JSONValue]
    min_after_cost_return: float
    position_rule: PositionRule = "sign"


@dataclass(frozen=True, kw_only=True)
class BudgetInfo:
    quota: int
    total_timesteps: int | None
    pool_capacity: int | None


@dataclass(frozen=True, kw_only=True)
class GenerationRun:
    schema_version: int
    run_id: str
    generator: str
    engine: EngineInfo
    binding: binding.SnapshotBinding | None
    seed: int | None
    config_digest: str
    device: str
    hostname: str
    vram_limit_gb: float | None
    kronos_offload: dict[str, JSONValue] | None
    universe: UniverseSummary | None
    tier_level: TierLevel
    window: base.Window | None
    objective: ObjectiveInfo
    counts: base.GenerationCounts
    pool: str | None
    started_at: datetime
    finished_at: datetime
    status: RunStatus
    termination: str
    reason: str | None
    budget: BudgetInfo | None = None
    stop_reason: StopReason | None = None
    evaluations: int | None = None


def load_run(path: Path) -> GenerationRun:
    """Strictly parse a persisted generation run manifest."""
    try:
        content = path.read_bytes()
        payload: JSONValue = json.loads(content)
    except OSError as exc:
        raise errors.RunStoreError(f"cannot read run manifest: {path}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise errors.SchemaValidationError(f"invalid run manifest JSON: {path}") from exc
    body = _mapping(payload, "run")
    version = body.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int):
        raise errors.SchemaValidationError("schema_version must be an integer")
    if version not in RUN_SCHEMA_VERSIONS:
        raise errors.UnknownSchemaVersionError(f"unsupported run schema_version: {version}")
    if version == 1:
        payload = _upgrade_v1(body)
    run = _parse_model(payload, GenerationRun, "run")
    _validate_terminal(run)
    return run


def _upgrade_v1(body: dict[str, JSONValue]) -> dict[str, JSONValue]:
    """v1 缺 v2 字段：补缺省值后仍走 v2 的严格字段集校验；v1 文件里出现 v2 字段即非法。"""
    if any(key in body for key in _V2_FIELDS):
        raise errors.SchemaValidationError("v1 run manifest must not carry v2 fields")
    objective = _mapping(body.get("objective"), "run.objective")
    if "position_rule" in objective:
        raise errors.SchemaValidationError("v1 objective must not carry position_rule")
    return {
        **body,
        **dict.fromkeys(_V2_FIELDS),
        "objective": {**objective, "position_rule": "sign"},
    }


def _validate_terminal(run: GenerationRun) -> None:
    if run.schema_version not in RUN_SCHEMA_VERSIONS or run.tier_level not in get_args(TierLevel):
        raise errors.SchemaValidationError("GenerationRun schema_version or tier_level is unknown")
    if run.stop_reason in _COMPLETED_REASONS and run.status != "completed":
        raise errors.SchemaValidationError(f"stop_reason {run.stop_reason!r} requires completed")
    if run.stop_reason in _PARTIAL_REASONS and run.status != "partial":
        raise errors.SchemaValidationError(f"stop_reason {run.stop_reason!r} requires partial")
    if _utc(run.finished_at, "finished_at") < _utc(run.started_at, "started_at"):
        raise errors.SchemaValidationError("finished_at must not precede started_at")
    match run.status:
        case "completed":
            if any(value is None for value in (run.binding, run.window, run.universe, run.seed)):
                raise errors.SchemaValidationError("completed run lacks required inputs")
            if run.reason is not None:
                raise errors.SchemaValidationError("completed run reason must be None")
        case "rejected" | "failed":
            if run.reason is None:
                raise errors.SchemaValidationError(f"{run.status} run requires reason")
        case "partial":
            if run.reason is None or run.pool is not None:
                raise errors.SchemaValidationError("partial run requires reason and forbids pool")
        case unknown:
            raise errors.SchemaValidationError(f"unknown run status: {unknown!r}")


def _payload(value) -> dict[str, JSONValue]:
    payload: JSONValue = json.loads(
        json.dumps(
            asdict(value),
            default=lambda item: (
                canonical.utc_iso(item) if isinstance(item, datetime) else item.as_posix()
            ),
            allow_nan=False,
        )
    )
    return _mapping(payload, "payload")


def _parse_model(value: JSONValue, model: type[_T], field: str) -> _T:
    body = _mapping(value, field, _field_names(model))
    annotations = get_type_hints(model)
    return model(
        **{
            item.name: _decode(body[item.name], annotations[item.name], f"{field}.{item.name}")
            for item in fields(model)
        }
    )


def _decode(value: JSONValue, annotation, field: str):
    if annotation is datetime:
        return canonical.parse_utc(_decode(value, str, field), field=field)
    if annotation in (str, int, float):
        accepted = (int, float) if annotation is float else (annotation,)
        if type(value) not in accepted:
            raise errors.SchemaValidationError(f"{field} has the wrong primitive type")
        return annotation(value)
    origin, arguments = get_origin(annotation), get_args(annotation)
    if origin is Literal:
        if value not in arguments:
            raise errors.SchemaValidationError(f"{field} has an unknown literal value")
        return value
    if origin is dict:
        return {
            key: _decode(item, arguments[1], f"{field}.{key}")
            for key, item in _mapping(value, field).items()
        }
    if origin is types.UnionType:
        if {str, int, float, bool, type(None)}.issubset(arguments):
            return value
        if value is None and type(None) in arguments:
            return None
        if {binding.SnapshotRefBinding, binding.ExplicitSnapshotBinding}.issubset(arguments):
            try:
                return binding.parse_binding(_mapping(value, field))
            except errors.BindingValidationError as exc:
                raise errors.SchemaValidationError(f"{field}: {exc}") from exc
        candidates = tuple(item for item in arguments if item is not type(None))
        if len(candidates) == 1:
            return _decode(value, candidates[0], field)
    if isinstance(annotation, type) and is_dataclass(annotation):
        return _parse_model(value, annotation, field)
    raise errors.SchemaValidationError(f"{field} has an unsupported schema type")


def _mapping(
    value: JSONValue, field: str, expected: frozenset[str] | None = None
) -> dict[str, JSONValue]:
    if not isinstance(value, dict):
        raise errors.SchemaValidationError(f"{field} must be a JSON object")
    if expected is not None and set(value) != expected:
        raise errors.SchemaValidationError(f"{field} fields do not match the schema")
    return value


def _field_names(model) -> frozenset[str]:
    return frozenset(item.name for item in fields(model))


def _utc(value: datetime, field: str) -> datetime:
    return canonical.parse_utc(canonical.utc_iso(value), field=field)
