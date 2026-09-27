"""F012 AC-010：AlphaGen 表达式渲染器逐算子往返（文档检视 D23/D37）。

vendor 默认动作空间（`alphagen/config.py` 的 `OPERATORS`）里的每个算子构造一个表达式，
渲染成 token 后必须能被纯度门接受；滚动与成对滚动算子必须带窗口（`name:N`），
否则纯度门会把它们判成 lookahead（F003 既有缺陷：`Mean(c,10)` 渲染成 `('feature:close','mean')`）。
"""

from __future__ import annotations

import pytest

pytest.importorskip("torch")

from alphamill.factor_factory.generators.alphagen_runner import (  # noqa: E402
    _add_vendor_root,
    render_expression,
)
from alphamill.factor_factory.generators.purity import check_expression  # noqa: E402

_add_vendor_root()

from alphagen.config import OPERATORS  # noqa: E402
from alphagen.data.expression import (  # noqa: E402
    BinaryOperator,
    CSRank,
    Feature,
    FeatureType,
    Mean,
    PairRollingOperator,
    Rank,
    RollingOperator,
    UnaryOperator,
)

CLOSE = Feature(FeatureType.CLOSE)
VOLUME = Feature(FeatureType.VOLUME)
WINDOW = 10


def _check(tokens: tuple[str, ...]):
    return check_expression(
        tokens,
        scope="cross_sectional",
        seen_definition_digests=frozenset(),
        definition_digest="",
    )


def _build(operator: type) -> object:
    if issubclass(operator, PairRollingOperator):
        return operator(CLOSE, VOLUME, WINDOW)
    if issubclass(operator, RollingOperator):
        return operator(CLOSE, WINDOW)
    if issubclass(operator, BinaryOperator):
        return operator(CLOSE, VOLUME)
    if issubclass(operator, UnaryOperator):
        return operator(CLOSE)
    raise AssertionError(f"unexpected operator category: {operator.__name__}")


@pytest.mark.parametrize("operator", OPERATORS, ids=lambda op: op.__name__)
def test_every_vendor_operator_renders_to_an_accepted_expression(operator) -> None:
    tokens = render_expression(_build(operator))

    verdict = _check(tokens)

    assert verdict.accepted, (tokens, verdict)
    if issubclass(operator, (RollingOperator, PairRollingOperator)):
        assert tokens[-1] == f"{operator.__name__.lower()}:{WINDOW}", tokens
        assert not any(token.startswith("delta:") for token in tokens[:-1]), tokens


def test_rolling_window_is_kept_in_the_operator_token() -> None:
    assert render_expression(Mean(CLOSE, WINDOW)) == ("feature:close", f"mean:{WINDOW}")


def test_cross_sectional_rank_maps_to_the_registered_operator() -> None:
    tokens = render_expression(CSRank(CLOSE))

    assert tokens == ("feature:close", "cs_rank")
    assert _check(tokens).accepted


def test_time_series_rank_is_rendered_honestly_and_rejected_as_unregistered() -> None:
    """时序 Rank 不得再被错译成截面 cs_rank；登记表没有 ts_rank，如实以 unregistered_op 拒绝。"""
    tokens = render_expression(Rank(CLOSE, 20))

    assert tokens == ("feature:close", "ts_rank:20")
    verdict = _check(tokens)
    assert not verdict.accepted
    assert verdict.reason_code == "unregistered_op"
