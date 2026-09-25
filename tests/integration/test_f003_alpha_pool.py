"""F003 协同池集成测试：FR-007 / DR-004 / AC-008。"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

from alphamill.factor_factory.errors import (
    CompilerNotRegisteredError,
    FactorDependencyError,
    FactorStoreError,
    SchemaValidationError,
)
from alphamill.factor_factory.factor import FactorDef
from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG
from alphamill.factor_factory.registry.compiler_registry import CompilerRegistry
from alphamill.factor_factory.registry.factor_store import FACTOR_DTO_FIELDS, build_factor
from alphamill.factor_factory.registry.pool_store import (
    POOL_GENERATOR,
    PoolMember,
    build_pool,
    load_pool,
    read_pool,
    write_pool,
)

pytestmark = pytest.mark.integration

CREATED_AT = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
FEATURE_MAP = {"alpha": 0, "beta": 1, "gamma": 2}


@dataclass(frozen=True, slots=True)
class PoolFixture:
    factors: Mapping[str, FactorDef]
    members: tuple[PoolMember, ...]
    panel: pd.DataFrame

    def resolve(self, factor_id: str) -> FactorDef:
        return self.factors[factor_id]


def _member(name: str, column: str) -> FactorDef:
    return build_factor(
        hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
        name=name,
        generator="manual",
        generator_version="1",
        scope="cross_sectional",
        expression=(f"feature:{column}",),
        params={},
        feature_map=FEATURE_MAP,
        run_id="member-run",
        created_at=CREATED_AT,
    )


@pytest.fixture
def pool_fixture() -> PoolFixture:
    factors = tuple(
        _member(name, column)
        for name, column in (("alpha", "alpha"), ("beta", "beta"), ("gamma", "gamma"))
    )
    by_id = {factor.factor_id: factor for factor in factors}
    timestamps = pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True)
    index = pd.MultiIndex.from_product(
        [timestamps, ["BTC", "ETH", "SOL"]], names=("timestamp", "pair")
    )
    panel = pd.DataFrame(
        {
            "alpha": [1.0, 2.0, 99.0, 4.0, 88.0, 6.0],
            "beta": [6.0, 5.0, 77.0, 3.0, 66.0, 1.0],
            "gamma": [2.0, 3.0, 55.0, 5.0, 44.0, 7.0],
            "__in_universe__": [True, True, False, True, False, True],
        },
        index=index,
    )
    members = (
        PoolMember(factor_id=factors[0].factor_id, weight=0.25),
        PoolMember(factor_id=factors[1].factor_id, weight=-1.5),
    )
    return PoolFixture(factors=by_id, members=members, panel=panel)


def _pool(fixture: PoolFixture, members: Sequence[PoolMember] | None = None) -> FactorDef:
    selected = fixture.members if members is None else members
    return build_pool(
        selected,
        run_id="pool-run",
        created_at=CREATED_AT,
        resolver=fixture.resolve,
        feature_map=FEATURE_MAP,
        pool_version="v1",
    )


def test_loaded_pool_recomputes_training_values_without_mutating_input(
    tmp_path: Path, pool_fixture: PoolFixture
) -> None:
    pool = _pool(pool_fixture)
    original_panel = pool_fixture.panel.copy(deep=True)
    recorded = pool.compute(pool_fixture.panel)
    path = write_pool(tmp_path / "pool-run", pool)

    loaded = load_pool(path, resolver=pool_fixture.resolve, feature_map=FEATURE_MAP)
    recomputed = loaded.compute(pool_fixture.panel)

    first, second = pool_fixture.members
    expected = first.weight * pool_fixture.resolve(first.factor_id).compute(
        pool_fixture.panel
    ) + second.weight * pool_fixture.resolve(second.factor_id).compute(pool_fixture.panel)
    pd.testing.assert_series_equal(recomputed, expected, check_names=False, rtol=1e-12, atol=1e-12)
    pd.testing.assert_series_equal(recomputed, recorded, check_names=False, rtol=1e-12, atol=1e-12)
    pd.testing.assert_index_equal(recomputed.index, pool_fixture.panel.index)
    pd.testing.assert_frame_equal(pool_fixture.panel, original_panel)
    assert recomputed[~pool_fixture.panel["__in_universe__"]].isna().all()


def test_persisted_pool_reverses_members_weights_and_definition_only(
    tmp_path: Path, pool_fixture: PoolFixture
) -> None:
    pool = _pool(pool_fixture)
    path = write_pool(tmp_path / "pool-run", pool)

    dto = read_pool(path)
    payload = json.loads(path.read_text(encoding="utf-8"))

    expected_members = [
        {"factor_id": member.factor_id, "weight": member.weight} for member in pool_fixture.members
    ]
    assert dto.params == {"members": expected_members, "pool_version": "v1"}
    assert dto.generator == POOL_GENERATOR
    assert dto.scope == "cross_sectional"
    assert set(payload) == FACTOR_DTO_FIELDS
    assert {"ic", "rank_ic", "pnl", "verdict", "promoted"}.isdisjoint(payload)


def test_member_or_weight_change_versions_pool_without_touching_old_file(
    tmp_path: Path, pool_fixture: PoolFixture
) -> None:
    original = _pool(pool_fixture)
    original_path = write_pool(tmp_path / "original", original)
    original_content = original_path.read_bytes()
    third = next(factor for factor in pool_fixture.factors.values() if factor.name == "gamma")
    variants = (
        _pool(
            pool_fixture,
            (*pool_fixture.members, PoolMember(factor_id=third.factor_id, weight=0.5)),
        ),
        _pool(pool_fixture, pool_fixture.members[:1]),
        _pool(
            pool_fixture,
            (
                PoolMember(
                    factor_id=pool_fixture.members[0].factor_id,
                    weight=0.5,
                ),
                pool_fixture.members[1],
            ),
        ),
    )

    for position, variant in enumerate(variants):
        write_pool(tmp_path / f"variant-{position}", variant)

    assert len({original.factor_id, *(variant.factor_id for variant in variants)}) == 4
    assert original_path.read_bytes() == original_content


@pytest.mark.parametrize(
    "members",
    (
        (),
        (
            PoolMember(factor_id="manual_duplicate", weight=1.0),
            PoolMember(factor_id="manual_duplicate", weight=2.0),
        ),
        (
            PoolMember(factor_id="manual_zero_a", weight=0.0),
            PoolMember(factor_id="manual_zero_b", weight=-0.0),
        ),
    ),
)
def test_build_pool_rejects_invalid_member_sets(
    pool_fixture: PoolFixture, members: Sequence[PoolMember]
) -> None:
    with pytest.raises(SchemaValidationError):
        _pool(pool_fixture, members)


@pytest.mark.parametrize("weight", (float("nan"), float("inf"), float("-inf")))
def test_build_pool_rejects_non_finite_weight(pool_fixture: PoolFixture, weight: float) -> None:
    with pytest.raises(SchemaValidationError):
        _pool(pool_fixture, (PoolMember(factor_id="manual_invalid", weight=weight),))


def test_compute_reports_unresolved_member_as_dependency_error(
    pool_fixture: PoolFixture,
) -> None:
    pool = _pool(
        pool_fixture,
        (PoolMember(factor_id="manual_missing", weight=1.0),),
    )

    with pytest.raises(FactorDependencyError, match="manual_missing"):
        pool.compute(pool_fixture.panel)


def test_build_pool_requires_registered_pool_compiler(pool_fixture: PoolFixture) -> None:
    with pytest.raises(CompilerNotRegisteredError):
        build_pool(
            pool_fixture.members,
            run_id="pool-run",
            created_at=CREATED_AT,
            resolver=pool_fixture.resolve,
            feature_map=FEATURE_MAP,
            pool_version="v1",
            compilers=CompilerRegistry(),
        )


def test_load_pool_requires_registered_pool_compiler(
    tmp_path: Path, pool_fixture: PoolFixture
) -> None:
    path = write_pool(tmp_path / "pool-run", _pool(pool_fixture))

    with pytest.raises(CompilerNotRegisteredError):
        load_pool(
            path,
            resolver=pool_fixture.resolve,
            feature_map=FEATURE_MAP,
            compilers=CompilerRegistry(),
        )


def test_write_pool_is_idempotent(tmp_path: Path, pool_fixture: PoolFixture) -> None:
    run_dir = tmp_path / "pool-run"
    pool = _pool(pool_fixture)

    first = write_pool(run_dir, pool)
    content = first.read_bytes()
    second = write_pool(run_dir, pool)

    assert first == second == run_dir / "pool.json"
    assert second.read_bytes() == content


def test_write_pool_rejects_conflicting_content(tmp_path: Path, pool_fixture: PoolFixture) -> None:
    run_dir = tmp_path / "pool-run"
    original = _pool(pool_fixture)
    changed = _pool(
        pool_fixture,
        (
            PoolMember(factor_id=pool_fixture.members[0].factor_id, weight=0.75),
            pool_fixture.members[1],
        ),
    )
    path = write_pool(run_dir, original)
    content = path.read_bytes()

    with pytest.raises(FactorStoreError):
        write_pool(run_dir, changed)

    assert path.read_bytes() == content
