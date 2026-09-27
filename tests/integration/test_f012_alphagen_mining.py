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


# ------------------------------------------------------------------ 回调式训练（T013）


def _training_panel(days: int = 240, pair_count: int = 6):
    from alphamill.factor_factory.generators.lake_tensor import TensorPanel

    timestamps = pd.date_range("2026-01-01", periods=days, freq="h", tz="UTC")
    pairs = tuple(f"PAIR-{index}-USDT" for index in range(pair_count))
    rows = [
        (t, p, 10 + d + i + (d % 7) * i, 100 + d * (i + 1), 20 + d + i)
        for d, t in enumerate(timestamps)
        for i, p in enumerate(pairs)
    ]
    frame = pd.DataFrame(
        rows,
        columns=[
            "timestamp",
            "pair",
            "ohlcv_1m.close@1h",
            "ohlcv_1m.volume@1h",
            "ohlcv_1m.high@1h",
        ],
    ).set_index(["timestamp", "pair"])
    frame["__in_universe__"] = True
    return TensorPanel(
        datasets=("ohlcv_1m",),
        resample="1h",
        pairs=pairs,
        timestamps=timestamps,
        panel=frame,
        feature_map={"ohlcv_1m.close@1h": 0, "ohlcv_1m.volume@1h": 1, "ohlcv_1m.high@1h": 2},
        feature_map_digest="sha256:test",
        universe_source="test",
    )


def _train(**overrides):
    pytest.importorskip("torch")
    pytest.importorskip("sb3_contrib")
    from alphamill.factor_factory.generators.alphagen_runner import build_stock_data
    from alphamill.factor_factory.generators.alphagen_training import train_with_callbacks

    panel = _training_panel()
    stock_data, target, _ = build_stock_data(panel, feature_map=panel.feature_map)
    kwargs = dict(
        stock_data=stock_data,
        target=target,
        device="cpu",
        seed=11,
        total_timesteps=256,
        pool_capacity=5,
        on_expression=lambda tokens: None,
        should_stop=lambda: None,
    )
    return train_with_callbacks(**{**kwargs, **overrides})


def test_every_evaluated_expression_reaches_the_hook_as_tokens() -> None:
    offered: list[tuple[str, ...]] = []

    outcome = _train(on_expression=offered.append)

    assert outcome.stopped is False, "未叫停时正常耗尽预算"
    assert offered, "训练期间必须有表达式被评估"
    assert all(isinstance(t, tuple) and all(isinstance(s, str) for s in t) for t in offered)
    assert 0 < outcome.evaluations <= len(offered)
    assert outcome.timesteps >= 256


def test_should_stop_ends_training_at_a_step_boundary_and_reports_stopped() -> None:
    """检视 D33：回调叫停时 learn() 同样正常返回，必须以 stopped 区分而非「返回即耗尽」。"""
    steps = {"n": 0}

    def should_stop() -> str | None:
        steps["n"] += 1
        return "quota_reached" if steps["n"] >= 10 else None

    outcome = _train(should_stop=should_stop, total_timesteps=4096)

    assert outcome.stopped is True
    assert outcome.timesteps < 4096
    assert steps["n"] == 10, "叫停后不再推进训练步"
