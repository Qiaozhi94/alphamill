"""F003 NFR-003/AC-009：可复现性与运行身份（集合相等，不承诺逐位数值相同）。"""

from __future__ import annotations

import os
import random
from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from alphamill.factor_factory.factor import FactorDef
from alphamill.factor_factory.generators import alphagen_generation as gen
from alphamill.factor_factory.generators import reproducibility as rp
from alphamill.factor_factory.generators.base import GenerationRequest, Window
from alphamill.factor_factory.generators.binding import SnapshotRefBinding
from alphamill.factor_factory.generators.lake_tensor import TensorPanel
from alphamill.factor_factory.generators.manual import seeds
from alphamill.factor_factory.registry import run_store

pytestmark = pytest.mark.integration

FIXED_NOW = datetime(2026, 9, 19, 12, 0, 0, tzinfo=UTC)
VERDICT_FIELDS = {"ic", "rank_ic", "pnl", "verdict", "promoted", "cost_verdict"}


def _request(quota: int = 5) -> GenerationRequest:
    # ManualGenerator 只读取 generator 与 quota；binding 仅为构造完整请求而占位。
    return GenerationRequest(
        generator="manual",
        binding=object(),
        seed=7,
        window=Window(start=FIXED_NOW - timedelta(days=1), end=FIXED_NOW, resample="1h"),
        config={},
        quota=quota,
    )


def test_derive_seed_is_deterministic_and_component_sensitive() -> None:
    assert rp.derive_seed(11, "ppo") == rp.derive_seed(11, "ppo")
    assert rp.derive_seed(11, "ppo") != rp.derive_seed(11, "env")
    assert rp.derive_seed(11, "ppo") != rp.derive_seed(12, "ppo")


def test_derive_seed_does_not_read_global_random_state() -> None:
    first = rp.derive_seed(5, "x")
    random.seed(12345)
    random.random()
    assert rp.derive_seed(5, "x") == first


def test_run_identity_digest_is_stable_and_sensitive() -> None:
    base = dict(seed=1, binding_digest="sha256:a", config_digest="sha256:b", code_digest="sha256:c")
    identity = rp.RunIdentity(**base)
    assert identity.identity_digest == rp.RunIdentity(**base).identity_digest

    for field in base:
        changed = {**base, field: "sha256:zzz" if field != "seed" else 2}
        assert rp.RunIdentity(**changed).identity_digest != identity.identity_digest


def test_canonical_run_id_is_deterministic_safe_and_sensitive() -> None:
    kwargs = dict(
        generator="manual",
        seed=3,
        binding_digest="sha256:a",
        config_digest="sha256:b",
        code_digest="sha256:c",
        now=FIXED_NOW,
    )
    run_id = rp.canonical_run_id(**kwargs)
    assert run_id == rp.canonical_run_id(**kwargs)
    assert "/" not in run_id and ":" not in run_id and ".." not in run_id
    assert rp.canonical_run_id(**{**kwargs, "seed": 4}) != run_id


def test_torch_determinism_is_noop_when_torch_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rp, "_load_torch", lambda: None)
    with rp.torch_determinism():
        pass


def test_torch_determinism_sets_and_restores_state() -> None:
    torch = pytest.importorskip("torch")
    before_rng = torch.random.get_rng_state().clone()
    before_determinism = torch.are_deterministic_algorithms_enabled()

    with rp.torch_determinism():
        assert torch.are_deterministic_algorithms_enabled() is True
        assert torch.initial_seed() == rp.DEFAULT_TORCH_SEED

    assert bool(torch.equal(torch.random.get_rng_state(), before_rng))
    assert torch.are_deterministic_algorithms_enabled() is before_determinism


def test_manual_generation_is_reproducible_across_runs() -> None:
    first = seeds.ManualGenerator(run_id="run-a", clock=lambda: FIXED_NOW).produce(_request())
    second = seeds.ManualGenerator(
        run_id="run-b", clock=lambda: FIXED_NOW + timedelta(hours=5)
    ).produce(_request())

    assert rp.factor_id_set(first.factors) == rp.factor_id_set(second.factors)
    assert rp.factor_id_set(first.factors) != rp.factor_id_set(first.factors[:2])


def test_config_digest_is_key_order_stable(tmp_path) -> None:
    def write(run_id: str, config: dict) -> str:
        run_dir = run_store.generation_run_dir(run_id, reports_root=tmp_path)
        return run_store.write_config(run_dir, config)

    left = write("cfg-a", {"alpha": 1, "beta": [2, 3]})
    right = write("cfg-b", {"beta": [2, 3], "alpha": 1})
    changed = write("cfg-c", {"alpha": 1, "beta": [2, 4]})

    assert left == right
    assert changed != left


def test_pool_member_set_is_content_addressed() -> None:
    def pool(members: list[dict[str, object]]) -> FactorDef:
        return FactorDef(
            factor_id="pool_deadbeef0000",
            hypothesis_id="mechanism_unknown",
            name="pool",
            generator="pool",
            scope="cross_sectional",
            params={"members": members},
            compute=lambda frame: frame["x"],
            data_columns=["x"],
            meta={},
        )

    members = [{"factor_id": "manual_aaa", "weight": 0.5}]
    enlarged = [*members, {"factor_id": "manual_bbb", "weight": 0.5}]
    assert rp.pool_member_set(pool(members)) == frozenset({"manual_aaa"})
    assert rp.pool_member_set(pool(enlarged)) != rp.pool_member_set(pool(members))


def test_reproducibility_surface_exposes_no_verdict_fields() -> None:
    assert not VERDICT_FIELDS & set(rp.RunIdentity.__dataclass_fields__)
    assert not VERDICT_FIELDS & set(rp.derive_seed.__code__.co_names)


def _capacity_panel(days: int = 240, pair_count: int = 6) -> TensorPanel:
    timestamps = pd.date_range("2026-01-01", periods=days, freq="h", tz="UTC")
    pairs = tuple(f"PAIR-{index}" for index in range(pair_count))
    rows = [
        (t, p, 10 + d + i, 100 + d, 20 + d + i)
        for d, t in enumerate(timestamps)
        for i, p in enumerate(pairs)
    ]
    frame = pd.DataFrame(
        rows,
        columns=[
            "timestamp",
            "pair",
            "synthetic.close@1h",
            "synthetic.volume@1h",
            "synthetic.high@1h",
        ],
    ).set_index(["timestamp", "pair"])
    frame["__in_universe__"] = True
    return TensorPanel(
        datasets=("synthetic",),
        resample="1h",
        pairs=pairs,
        timestamps=timestamps,
        panel=frame,
        feature_map={"synthetic.volume@1h": 0, "synthetic.close@1h": 1, "synthetic.high@1h": 2},
        feature_map_digest="sha256:test",
        universe_source="test",
    )


def test_generation_outcome_exposes_no_verdict_fields() -> None:
    assert not VERDICT_FIELDS & set(gen.GenerationRunOutcome.__dataclass_fields__)


def test_write_generation_manifest_persists_counts_hostname_and_device(tmp_path) -> None:
    outcome = gen.GenerationRunOutcome(
        run_id="run-t029",
        hostname="host-t029",
        device="cpu",
        proposed=5,
        evaluations=4,
        rejected={"lookahead": 2},
        registered=3,
        candidates=(("feature:close",),) * 3,
    )
    run_dir = run_store.generation_run_dir(outcome.run_id, reports_root=tmp_path)
    path = gen.write_generation_manifest(
        outcome,
        run_dir=run_dir,
        binding=SnapshotRefBinding(mode="snapshot", research_snapshot_id="snapshot-t029"),
        window=Window(start=FIXED_NOW - timedelta(days=1), end=FIXED_NOW, resample="1h"),
        seed=7,
        config={"generator": "alphagen"},
        pair_count=6,
        symbol_map_digest="sha256:sm",
        universe_digest="sha256:universe",
        started_at=FIXED_NOW,
        finished_at=FIXED_NOW + timedelta(seconds=5),
    )

    run = run_store.load_run(path)
    assert run.status == "completed"
    assert run.hostname == "host-t029"
    assert run.device == "cpu"
    assert run.counts.proposed == 5
    assert run.counts.registered == 3
    assert run.counts.rejected.lookahead == 2
    assert run.universe is not None and run.universe.pair_count == 6


def test_generation_run_registers_fifty_candidates_when_integration_cuda_enabled() -> None:
    if os.environ.get("ALPHAMILL_INTEGRATION") != "1":
        pytest.skip("ALPHAMILL_INTEGRATION=1 is required")
    torch = pytest.importorskip("torch")
    if not torch.cuda.is_available():
        pytest.fail("ALPHAMILL_INTEGRATION=1 requires CUDA for the capacity run")

    from alphamill.factor_factory.generators.alphagen_runner import build_stock_data

    panel = _capacity_panel()
    stock_data, target, _ = build_stock_data(panel, feature_map=panel.feature_map)
    outcome = gen.run_generation(
        stock_data=stock_data,
        target=target,
        device="cuda",
        seed=11,
        total_timesteps=4096,
        pool_capacity=5,
    )

    assert outcome.device == "cuda"
    assert outcome.evaluations >= outcome.registered
    assert sum(outcome.rejected.values()) + outcome.registered == outcome.proposed
    assert outcome.registered >= 50, f"registered only {outcome.registered}"
