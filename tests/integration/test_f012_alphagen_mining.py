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
from tests.f012_fixtures import (
    _LENIENT,
    FULL,
    PARTIAL_UNIVERSE,
    _cli_mine,
    _event_lines,
    _produce,
    _training_panel,
)


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


# ------------------------------------------------------------------ CLI × scratch 湖（T017）


@pytest.fixture(scope="module")
def scratch(tmp_path_factory):
    from tests.f012_fixtures import build_scratch_lake

    root = tmp_path_factory.mktemp("f012-lake")
    return build_scratch_lake(root, {"full": FULL, "partial": PARTIAL_UNIVERSE}), root


def test_quota_run_registers_loadable_factors_with_pointwise_equal_signals(scratch) -> None:
    """AC-001/AC-002：--quota 3 恰入册 3；因子通道已绑定；load 反解后在同一面板逐点一致。"""
    from alphamill.factor_factory.registry import factor_store

    lake, root = scratch
    code, run_path, run, panel, written = _cli_mine(
        lake, "full", root, quota=3, total_timesteps=4096, objective=_LENIENT
    )

    assert code == 0, run
    assert (run["schema_version"], run["status"], run["stop_reason"]) == (
        2,
        "completed",
        "quota_reached",
    )
    assert run["counts"]["registered"] == 3 and run["tier_level"] == "L0"
    window_start = datetime.fromisoformat(run["window"]["start"].replace("Z", "+00:00"))
    window_end = datetime.fromisoformat(run["window"]["end"].replace("Z", "+00:00"))
    assert window_start < panel.timestamps[0], "恰在 window.start 的探针 bar 须排除（开区间）"
    assert panel.timestamps[-1] == window_end, "恰在 window.end 的探针 bar 须保留、其后的须排除"
    in_run = {factor.factor_id: factor for factor in written}  # 预筛所用的那一份 FactorDef
    paths = sorted((run_path.parent / "factors").glob("*.json"))
    assert len(paths) == 3 and {path.stem for path in paths} == set(in_run)
    for path in paths:
        dto = factor_store.read(path)
        loaded = factor_store.load(path)
        assert loaded.generator == "alphagen" and loaded.hypothesis_id == "mechanism_unknown"
        features = [t for t in dto.expression if t.startswith("feature:")]
        assert features and all(t.startswith("feature:ohlcv_1m.") for t in features)
        pd.testing.assert_series_equal(
            loaded.compute(panel.panel),
            in_run[path.stem].compute(panel.panel),
            check_names=False,
        )


def test_tiny_budget_ends_with_budget_exhausted_below_quota(scratch) -> None:
    lake, root = scratch
    code, _, run, _, _ = _cli_mine(lake, "full", root, quota=50, total_timesteps=64)

    assert code == 0, run
    assert run["status"] == "completed" and run["stop_reason"] == "budget_exhausted"
    assert run["counts"]["registered"] < 50
    assert run["budget"] == {"quota": 50, "total_timesteps": 64, "pool_capacity": 5}


def test_pair_count_follows_the_bound_universe_not_the_lake(scratch) -> None:
    """AC-008：同数据版本、宇宙不同的两个显式绑定 → pair_count 不同且等于窗口内曾在宇宙数。"""
    from alphamill.factor_factory.generators.lake_tensor import universe_pair_count

    lake, root = scratch
    _, _, full, full_panel, _ = _cli_mine(lake, "full", root, quota=50, total_timesteps=64)
    _, _, part, part_panel, _ = _cli_mine(lake, "partial", root, quota=50, total_timesteps=64)

    assert full["universe"]["pair_count"] == 6 == universe_pair_count(full_panel.panel)
    assert part["universe"]["pair_count"] == 3 == universe_pair_count(part_panel.panel)
    assert full["binding"]["members"] == part["binding"]["members"], "数据版本相同"


def test_factors_of_a_v1_manual_run_still_load(tmp_path) -> None:
    """AC-001：v2 落地后，改动前写下的 v1 manual 运行的因子仍可 load。"""
    import json

    from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG
    from alphamill.factor_factory.registry import factor_store, run_store
    from tests.unit.test_f012_run_schema import _run

    factor = factor_store.build_factor(
        hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
        name="legacy",
        generator="manual",
        generator_version="1",
        scope="time_series",
        expression=("feature:close", "neg"),
        params={},
        feature_map={"close": 0},
        run_id="run-v1",
        created_at=datetime(2026, 9, 1, tzinfo=UTC),
    )
    path = factor_store.write(tmp_path, factor)
    payload = run_store._payload(_run(generator="manual", tier_level="manual"))
    for key in ("budget", "stop_reason", "evaluations"):
        payload.pop(key)
    payload["objective"].pop("position_rule")
    payload["schema_version"] = 1
    (tmp_path / "run.json").write_text(json.dumps(payload), encoding="utf-8")

    assert factor_store.load(path).generator == "manual"
