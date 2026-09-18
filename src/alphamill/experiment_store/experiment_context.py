"""`ExperimentContext`：实验语义上下文的规范化、两级内容 ID 与 supersedes 谱系（`DR-002`）。

`experiment_id` **只**哈希语义字段（ADR-0006 决策 3）：

```text
level 1  method_config_digest / window_digest / cost_model_digest   （子对象内容摘要）
level 2  experiment_id = sha256(canonical_json({
           schema_version, upstream, cohort_id,
           method_config_digest, window_digest, cost_model_digest,
           research_snapshot_id, code_build_digest, seed }))
```

父级哈希**子摘要**而不是重复哈希子对象的输入（与 ADR-0007 的
`universe_calendar_digest → snapshot_id` 同一条规则）。`execution_tier` 与 `supersedes` 明确
**不参与身份**：层级由 capability 强制，`supersedes` 只表达谱系（design §3.1）；物理路径、
Parquet codec、created_at、host、duration 与 file SHA 同样不入身份。

规范化口径（design §3.1）：UTF-8 canonical JSON、键排序、时间统一 UTC ISO-8601、数值用十进制
定标文本、集合字段先去重再排序。因此语义相同的输入必须得到同一个 `experiment_id`（`NFR-002`）。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from alphamill.evaluation.contract_common import EXECUTION_TIERS
from alphamill.experiment_store.errors import SnapshotInputError
from alphamill.experiment_store.identity import (
    DIGEST_RE,
    REF_RE,
    canonical_json,
    content_digest,
    normalize_numbers,
    normalize_utc_set,
)

CONTEXT_SCHEMA_VERSION = 1
CONFIG_FIELDS = ("method_config", "cost_model")


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise SnapshotInputError(f"{field} 必须是非空字符串")
    return value


def _ref(value: Any, field: str) -> str:
    text = _text(value, field)
    if not REF_RE.fullmatch(text):
        raise SnapshotInputError(f"{field} 必须是内容寻址引用（sha256:<hex>）: {text!r}")
    return text


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SnapshotInputError(f"{field} 必须是 object")
    return value


def _positive_ints(value: Any, field: str) -> tuple[int, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple, set, frozenset)):
        raise SnapshotInputError(f"{field} 必须是数组")
    horizons = set()
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool) or item < 1:
            raise SnapshotInputError(f"{field} 必须是正整数集合: {item!r}")
        horizons.add(item)
    if not horizons:
        raise SnapshotInputError(f"{field} 不能为空")
    return tuple(sorted(horizons))


@dataclass(frozen=True)
class ExperimentContext:
    schema_version: int
    execution_tier: str
    upstream: Mapping[str, str]
    cohort_id: str
    method_config: Mapping[str, Any]
    window: Mapping[str, Any]
    cost_model: Mapping[str, Any]
    research_snapshot_id: str
    code_build_digest: str
    seed: int
    supersedes: str | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.schema_version != CONTEXT_SCHEMA_VERSION:
            raise SnapshotInputError(f"不支持的 experiment schema_version: {self.schema_version!r}")
        if self.execution_tier not in EXECUTION_TIERS:
            raise SnapshotInputError(
                f"未知执行层级: {self.execution_tier!r}（合法: {list(EXECUTION_TIERS)}）"
            )
        upstream = _mapping(self.upstream, "upstream")
        _text(upstream.get("kind"), "upstream.kind")
        _text(upstream.get("id"), "upstream.id")
        _ref(self.cohort_id, "cohort_id")
        _ref(self.research_snapshot_id, "research_snapshot_id")
        if not isinstance(self.code_build_digest, str) or not DIGEST_RE.fullmatch(
            self.code_build_digest
        ):
            raise SnapshotInputError(
                f"code_build_digest 必须是 sha256:<hex>: {self.code_build_digest!r}"
            )
        if not isinstance(self.seed, int) or isinstance(self.seed, bool):
            raise SnapshotInputError(f"seed 必须是整数: {self.seed!r}")
        if self.supersedes is not None:
            _ref(self.supersedes, "supersedes")
        for field in CONFIG_FIELDS:
            config = _mapping(getattr(self, field), field)
            _text(config.get("id"), f"{field}.id")
            _mapping(config.get("normalized"), f"{field}.normalized")
        window = _mapping(self.window, "window")
        normalize_utc_set(window.get("selection"), "window.selection")
        _positive_ints(window.get("label_horizons"), "window.label_horizons")

    def normalized(self) -> dict[str, Any]:
        upstream = _mapping(self.upstream, "upstream")
        return {
            "execution_tier": self.execution_tier,
            "upstream": {
                "kind": _text(upstream["kind"], "upstream.kind"),
                "id": _text(upstream["id"], "upstream.id"),
            },
            "cohort_id": self.cohort_id,
            "method_config": _normalized_config(self.method_config, "method_config"),
            "window": {
                "selection": normalize_utc_set(self.window["selection"], "window.selection"),
                "label_horizons": list(
                    _positive_ints(self.window["label_horizons"], "window.label_horizons")
                ),
            },
            "cost_model": _normalized_config(self.cost_model, "cost_model"),
            "research_snapshot_id": self.research_snapshot_id,
            "code_build_digest": self.code_build_digest,
            "seed": self.seed,
            "supersedes": self.supersedes,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, **self.normalized()}

    def component_digests(self) -> dict[str, str]:
        normalized = self.normalized()
        return {
            "method_config_digest": content_digest(
                canonical_json(normalized["method_config"]).encode("utf-8")
            ),
            "window_digest": content_digest(canonical_json(normalized["window"]).encode("utf-8")),
            "cost_model_digest": content_digest(
                canonical_json(normalized["cost_model"]).encode("utf-8")
            ),
        }

    def identity_payload(self) -> dict[str, Any]:
        normalized = self.normalized()
        return {
            "schema_version": self.schema_version,
            "upstream": normalized["upstream"],
            "cohort_id": normalized["cohort_id"],
            **self.component_digests(),
            "research_snapshot_id": normalized["research_snapshot_id"],
            "code_build_digest": normalized["code_build_digest"],
            "seed": normalized["seed"],
        }

    @property
    def experiment_id(self) -> str:
        return content_digest(canonical_json(self.identity_payload()).encode("utf-8"))

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ExperimentContext:
        fields = {"schema_version", *cls.__dataclass_fields__}
        missing = sorted(f for f in fields if f not in payload)
        if missing:
            raise SnapshotInputError(f"experiment context 缺少字段: {missing}")
        return cls(**{key: payload[key] for key in fields})


def _normalized_config(config: Mapping[str, Any], field: str) -> dict[str, Any]:
    body = _mapping(config, field)
    return {
        "id": _text(body.get("id"), f"{field}.id"),
        "normalized": normalize_numbers(_mapping(body.get("normalized"), f"{field}.normalized")),
    }


@dataclass(frozen=True)
class ExperimentIndex:
    """已发布实验的只读索引，供 `supersedes` 校验与谱系回溯。"""

    entries: Mapping[str, ExperimentContext]

    @classmethod
    def from_contexts(cls, contexts: Iterable[ExperimentContext]) -> ExperimentIndex:
        return cls(entries={context.experiment_id: context for context in contexts})

    def get(self, experiment_id: str) -> ExperimentContext | None:
        return self.entries.get(experiment_id)

    def lineage(self, experiment_id: str) -> tuple[str, ...]:
        chain: list[str] = []
        cursor = self.get(experiment_id)
        while cursor is not None and cursor.supersedes is not None:
            chain.append(cursor.supersedes)
            cursor = self.get(cursor.supersedes)
        return tuple(chain)


def validate_supersedes(context: ExperimentContext, index: ExperimentIndex) -> None:
    """`supersedes` 只表达谱系：存在、同类（upstream+cohort 相同）、非自指、无环、链不断。"""
    target = context.supersedes
    if target is None:
        return
    if target == context.experiment_id:
        raise SnapshotInputError("supersedes 不能指向自身")
    previous = index.get(target)
    if previous is None:
        raise SnapshotInputError(f"supersedes 目标不存在: {target}")
    if (
        previous.normalized()["upstream"] != context.normalized()["upstream"]
        or previous.cohort_id != context.cohort_id
    ):
        raise SnapshotInputError("supersedes 只能替代同一 upstream/cohort 的历史实验")
    seen = {context.experiment_id, target}
    cursor: ExperimentContext = previous
    while cursor.supersedes is not None:
        if cursor.supersedes in seen:
            raise SnapshotInputError("supersedes 链存在环")
        seen.add(cursor.supersedes)
        next_cursor = index.get(cursor.supersedes)
        if next_cursor is None:
            raise SnapshotInputError("supersedes 链断裂：中间节点不存在")
        cursor = next_cursor
