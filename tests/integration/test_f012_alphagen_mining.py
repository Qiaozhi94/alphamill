"""F012 AlphaGen 挖掘集成（AC-001/002/008）与取数辅助（T011）。

取数辅助不连库、不依赖 torch；真实训练用例在 `mining` extra 下运行，无 torch 环境按约定 skip。
"""

from __future__ import annotations

import signal
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
    """vendor 六个 FeatureType 通道齐全，候选不会因缺通道被整批拒掉。"""
    import numpy as np

    from alphamill.factor_factory.generators.lake_tensor import TensorPanel

    timestamps = pd.date_range("2026-01-01", periods=days, freq="h", tz="UTC")
    pairs = tuple(f"PAIR-{index}-USDT" for index in range(pair_count))
    index = pd.MultiIndex.from_product([timestamps, pairs], names=["timestamp", "pair"])
    rng = np.random.default_rng(7)
    close = 100.0 * np.exp(np.cumsum(rng.normal(0, 0.01, (days, pair_count)), axis=0)).ravel()
    names = ("open", "close", "high", "low", "volume", "vwap")
    columns = {
        "open": close * (1 + rng.normal(0, 0.002, close.size)),
        "close": close,
        "high": close * 1.004,
        "low": close * 0.996,
        "volume": rng.uniform(1e3, 1e4, close.size),
        "vwap": close * (1 + rng.normal(0, 0.001, close.size)),
    }
    frame = pd.DataFrame({f"ohlcv_1m.{n}@1h": columns[n] for n in names}, index=index)
    frame["__in_universe__"] = True
    return TensorPanel(
        datasets=("ohlcv_1m",),
        resample="1h",
        pairs=pairs,
        timestamps=timestamps,
        panel=frame,
        feature_map={f"ohlcv_1m.{n}@1h": i for i, n in enumerate(names)},
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


# ------------------------------------------------------------------ 生成器编排（T014）

_WINDOW = ("2026-01-01T00:00:00+00:00", "2026-01-11T00:00:00+00:00")
_LENIENT = {  # 预筛放宽到几乎全收：只验证编排与配额，不验证目标函数本身
    "reachability_min_trades_90d": 0,
    "min_after_cost_return": -1.0e9,
    "turnover_penalty_lambda": 0.0,
}


def _produce(tmp_path, *, quota: int, objective: dict, check=None, total_timesteps=512):
    pytest.importorskip("torch")
    pytest.importorskip("sb3_contrib")
    from alphamill.factor_factory import mine_dispatch
    from alphamill.factor_factory.generators.base import GenerationRequest, Window
    from alphamill.factor_factory.generators.stop_conditions import (
        StopController,
        install_signal_flags,
    )
    from alphamill.factor_factory.registry.default_compilers import full_registry
    from alphamill.factor_factory.registry.event_writer import RunEventWriter

    spec = mine_dispatch.resolve("alphagen")
    config = mine_dispatch.compose_config(
        spec,
        {"objective": objective, "total_timesteps": total_timesteps, "pool_capacity": 5},
        mining=True,
        quota=quota,
        window=list(_WINDOW),
    )
    run_id = "alphagen-test-run"
    with install_signal_flags() as flags:
        stop = StopController(
            flags=flags,
            window_start="22:00",
            window_end="06:30",
            window_tz="Asia/Shanghai",
            ignore_window=True,
        )
        if check is not None:
            stop.check = check(stop)
        writer = RunEventWriter(tmp_path, run_id=run_id)
        context = mine_dispatch.BuildContext(
            run_id=run_id, config=config, stop=stop, writer=writer, compilers=full_registry()
        )
        request = GenerationRequest(
            generator="alphagen",
            binding=object(),
            seed=11,
            window=Window(
                start=datetime.fromisoformat(_WINDOW[0]),
                end=datetime.fromisoformat(_WINDOW[1]),
                resample="1h",
            ),
            config=config,
            quota=quota,
            panel=_training_panel(),
        )
        result = mine_dispatch.build_generator(spec, context).produce(request)
        writer.close()
    return result


def _event_lines(path) -> list[dict]:
    import json

    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_generator_stops_at_quota_and_reports_v2_facts(tmp_path) -> None:
    result = _produce(tmp_path, quota=2, objective=_LENIENT, total_timesteps=2048)

    assert result.stop_reason == "quota_reached"
    assert len(result.factors) == result.counts.registered == 2
    assert result.pool is None and result.tier_level == "L0" and result.device == "cpu"
    assert result.budget == {"quota": 2, "total_timesteps": 2048, "pool_capacity": 5}
    assert result.evaluations is not None and result.evaluations > 0
    for factor in result.factors:
        assert factor.generator == "alphagen" and factor.meta["run_id"] == "alphagen-test-run"
        features = [s for s in factor.meta["expression"] if s.startswith("feature:")]
        assert features and all(s.startswith("feature:ohlcv_1m.") for s in features), "通道已绑定"


def test_generator_counts_are_conserved_against_the_event_files(tmp_path) -> None:
    strict = {"reachability_min_trades_90d": 10_000}  # 预筛全拒：跑满预算
    result = _produce(tmp_path, quota=5, objective=strict, total_timesteps=1024)

    rejected = _event_lines(tmp_path / "events.jsonl")
    counts = result.counts
    assert result.stop_reason == "budget_exhausted"
    assert counts.registered == 0
    assert counts.proposed == len(rejected) > 0
    by_code: dict[str, int] = {}
    for event in rejected:
        code = event["payload"]["reason_code"]
        by_code[code] = by_code.get(code, 0) + 1
    assert by_code == {k: v for k, v in vars(counts.rejected).items() if v}


def test_interrupted_training_reports_interrupted(tmp_path) -> None:
    def interrupt_after_five(stop):
        original, calls = stop.check, {"n": 0}

        def check():
            calls["n"] += 1
            if calls["n"] == 5:  # 第 5 个训练步收到 SIGTERM
                stop._flags.set(signal.SIGTERM, None)
            return original()

        return check

    result = _produce(tmp_path, quota=5, objective=_LENIENT, check=interrupt_after_five)

    assert result.stop_reason == "interrupted"
