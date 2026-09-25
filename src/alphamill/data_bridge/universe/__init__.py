"""F008 宇宙扩容与 point-in-time 宇宙台账（`docs/features/0.2/F008-universe-expansion/`）。

四段式流水线：**发现 → 冻结 → 回填 → 质量门 → 台账发布**。

- `criteria`：筛选口径的载入与校验（T001，`DR-001`）；
- `discover`：按成交额排名 + 上线天数 + 排除规则筛候选（T004，`FR-001`）；
- `definition`：`UniverseDef` 内容寻址、人工确认冻结与版本化（T005，`FR-002`）；
- `membership`：只追加台账与 `universe_at(T)`（T007/T008，`FR-005`）；
- `artifact`：台账 canonical JSON 内容寻址发布（T009，`IR-002`）；
- `events`：`universe.member_changed` / `backfill.*` 事件（T010/T014，`TR-001`/`TR-002`）；
- `rate_limit` / `backfill_runner`：长跑编排的限速、退避、断点（T012/T013，`FR-003`）；
- `quality_gate`：新 pair 准入门与准入记录（T015/T016/T017，`FR-004`/`FR-006`）；
- `cli` / `__main__`：`python -m alphamill.data_bridge.universe`（T018，`IR-001`）。
"""

from __future__ import annotations

__all__ = ["__doc__"]
