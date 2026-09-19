"""F003 NFR-003/AC-009：可复现性与运行身份（集合相等，不承诺逐位数值相同）。"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

import pytest

from alphamill.factor_factory.factor import FactorDef
from alphamill.factor_factory.generators import reproducibility as rp
from alphamill.factor_factory.generators.base import GenerationRequest, Window
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
