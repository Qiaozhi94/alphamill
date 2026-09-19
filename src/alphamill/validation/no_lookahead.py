"""无前视三层状态与晋级阻断（`FR-007`/`AC-009`；任务 T008）。

三层防线归属**冻结**（`spec.md` `FR-007`、`design.md` §7）：

| 层 | 内容 | owner | F007 的行为 |
|---|---|---|---|
| L1 | AST 纯度与未来算子门 | **F007** | 在评测入口 fail-closed 复检 |
| L2 | 独立逐 K 线重放审计 | F006/M3 | 不实现审计器，只消费证据 |
| L3 | 信号缓存 merge/join 时间戳与陈旧度对齐 | F006/M3 | 不实现审计器，只消费证据 |

缺失层必须显式记 `not_yet_available` 并携带 `owner`，**不得记为 `PASS`、也不得静默省略**；任一层
非 `PASS` 时证据达标的成员也只能是 `blocked_pending_audit`，由 F006 晋级入口消费后 fail-closed
（`E_PROMOTION_BLOCKED`）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

LAYER_L1 = "L1"
LAYER_L2 = "L2"
LAYER_L3 = "L3"
LAYERS = (LAYER_L1, LAYER_L2, LAYER_L3)

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_NOT_YET_AVAILABLE = "not_yet_available"
LAYER_STATUSES = (STATUS_PASS, STATUS_FAIL, STATUS_NOT_YET_AVAILABLE)

OWNER_F007 = "F007"
OWNER_F006_M3 = "F006/M3"
LAYER_OWNERS = {LAYER_L1: OWNER_F007, LAYER_L2: OWNER_F006_M3, LAYER_L3: OWNER_F006_M3}
LAYER_KINDS = {
    LAYER_L1: "ast_purity_and_future_operators",
    LAYER_L2: "per_candle_replay_audit",
    LAYER_L3: "signal_cache_merge_join_alignment",
}


class NoLookaheadError(ValueError):
    """违反三层状态契约（未知层、错误 owner、把缺失层记为 PASS）。"""


@dataclass(frozen=True)
class NoLookaheadLayer:
    layer: str
    status: str
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.layer not in LAYERS:
            raise NoLookaheadError(f"未登记的无前视层: {self.layer!r}")
        if self.status not in LAYER_STATUSES:
            raise NoLookaheadError(f"未登记的无前视层状态: {self.status!r}")
        if self.status == STATUS_PASS and not self.evidence_refs:
            raise NoLookaheadError(f"{self.layer} 记为 PASS 必须携带证据引用")

    @property
    def owner(self) -> str:
        return LAYER_OWNERS[self.layer]

    @property
    def kind(self) -> str:
        return LAYER_KINDS[self.layer]

    def to_payload(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "owner": self.owner,
            "kind": self.kind,
            "status": self.status,
            "evidence_refs": list(self.evidence_refs),
        }


@dataclass(frozen=True)
class NoLookahead:
    layers: tuple[NoLookaheadLayer, ...]

    def __post_init__(self) -> None:
        present = [layer.layer for layer in self.layers]
        missing = [layer for layer in LAYERS if layer not in present]
        if missing:
            raise NoLookaheadError(f"三层必须逐层显式记录，缺失: {missing}（不得静默省略）")
        if len(set(present)) != len(present):
            raise NoLookaheadError(f"无前视层重复记录: {present}")

    def get(self, layer: str) -> NoLookaheadLayer:
        return next(entry for entry in self.layers if entry.layer == layer)

    @property
    def non_pass_layers(self) -> tuple[str, ...]:
        return tuple(entry.layer for entry in self.layers if entry.status != STATUS_PASS)

    @property
    def blocks_promotion(self) -> bool:
        return bool(self.non_pass_layers)

    def to_payload(self) -> dict[str, Any]:
        return {
            "layers": [self.get(layer).to_payload() for layer in LAYERS],
            "blocks_promotion": self.blocks_promotion,
        }


def build_no_lookahead(
    *,
    l1_status: str,
    l1_evidence_refs: tuple[str, ...] = (),
    l2_status: str = STATUS_NOT_YET_AVAILABLE,
    l3_status: str = STATUS_NOT_YET_AVAILABLE,
    l2_evidence_refs: tuple[str, ...] = (),
    l3_evidence_refs: tuple[str, ...] = (),
) -> NoLookahead:
    """构造三层状态；L1 由本 Feature 写，L2/L3 默认 `not_yet_available`（owner=F006/M3）。"""
    return NoLookahead(
        layers=(
            NoLookaheadLayer(LAYER_L1, l1_status, l1_evidence_refs),
            NoLookaheadLayer(LAYER_L2, l2_status, l2_evidence_refs),
            NoLookaheadLayer(LAYER_L3, l3_status, l3_evidence_refs),
        )
    )
