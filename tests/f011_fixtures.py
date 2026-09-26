"""F011 测试共享构造器：在 scratch 湖里写一版（可冻结的）宇宙定义。

放在 `tests/` 根下：unit 与 integration 都用，跨目录 `from test_xxx import ...` 会 ImportError。
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from alphamill.data_bridge.universe.definition import (
    UniverseDef,
    build_definition,
    freeze_definition,
    write_definition,
)
from alphamill.data_bridge.universe.discover import MarketSnapshot, evaluate
from tests.f008_fixtures import criteria_for, market


def utc(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


def define_universe(
    lake: Path,
    *,
    selected: tuple[str, ...],
    dropped: tuple[str, ...] = (),
    snapshot_at: str,
    frozen_at: str | None,
    market_type: str = "perp",
) -> UniverseDef:
    """`selected` 按成交额排前，`dropped` 垫底被 top_n 截掉（仍是候选）；无 `frozen_at` 即草稿。"""
    criteria = criteria_for(turnover_rank_top_n=len(selected), market_type=market_type)
    records = [market(base, turnover=10_000_000.0 - index) for index, base in enumerate(selected)]
    records += [market(base, turnover=1_000.0 + index) for index, base in enumerate(dropped)]
    snap = MarketSnapshot(
        exchange=criteria.exchange,
        market_type=market_type,
        snapshot_at=snapshot_at,
        markets=tuple(records),
    )
    definition = build_definition(criteria, evaluate(snap, criteria))
    assert {c.db_symbol.split("/")[0] for c in definition.selected} == set(selected)
    write_definition(definition, lake)
    if frozen_at is not None:
        freeze_definition(
            definition.universe_id, frozen_by="tester", lake_root=lake, frozen_at=utc(frozen_at)
        )
    return definition
