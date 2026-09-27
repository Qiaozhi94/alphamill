"""F012 AlphaGen 挖掘集成（AC-001/002/008）与取数辅助（T011）。

取数辅助不连库、不依赖 torch；真实训练用例在 `mining` extra 下运行，无 torch 环境按约定 skip。
"""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytest

from alphamill.factor_factory.errors import BindingValidationError
from alphamill.factor_factory.generators.lake_tensor import (
    pairs_during,
    require_universe_members,
    universe_pair_count,
)
from alphamill.factor_factory.generators.universe import UniverseLedger, UniverseMembership


def _utc(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


LEDGER = UniverseLedger(
    schema_version=1,
    digest="sha256:" + "0" * 64,
    memberships=(
        UniverseMembership(lake_pair="AAA-USDT", valid_from=_utc("2024-01-01"), valid_to=None),
        UniverseMembership(
            lake_pair="BBB-USDT", valid_from=_utc("2024-01-01"), valid_to=_utc("2025-06-01")
        ),
        UniverseMembership(lake_pair="CCC-USDT", valid_from=_utc("2026-12-01"), valid_to=None),
        UniverseMembership(
            lake_pair="DDD-USDT", valid_from=_utc("2023-01-01"), valid_to=_utc("2024-01-01")
        ),
    ),
)


def test_pairs_during_is_the_union_of_members_overlapping_the_window() -> None:
    """检视 D24：取窗口内曾在宇宙的成员并集——BBB 期间退出仍要读（不以终点成员筛历史）。"""
    pairs = pairs_during(LEDGER, _utc("2024-09-10"), _utc("2026-09-10"))

    assert pairs == ("AAA-USDT", "BBB-USDT")


def _panel(mask_by_pair: dict[str, list[bool]]) -> pd.DataFrame:
    hours = len(next(iter(mask_by_pair.values())))
    timestamps = pd.date_range("2026-01-01", periods=hours, freq="1h", tz=UTC)
    index = pd.MultiIndex.from_product(
        [timestamps, list(mask_by_pair)], names=["timestamp", "pair"]
    )
    mask = [mask_by_pair[pair][hour] for hour in range(hours) for pair in mask_by_pair]
    return pd.DataFrame({"__in_universe__": mask}, index=index)


def test_universe_pair_count_counts_pairs_ever_in_universe_not_lake_pairs() -> None:
    frame = _panel({"AAA": [True, True], "BBB": [False, True], "CCC": [False, False]})

    assert universe_pair_count(frame) == 2


def test_empty_universe_window_is_rejected_as_invalid_binding() -> None:
    """检视 D34：窗口内宇宙为空时 build_tensor 不抛错，须建后显式校验。"""
    with pytest.raises(BindingValidationError, match="universe"):
        require_universe_members(_panel({"AAA": [False, False]}))
