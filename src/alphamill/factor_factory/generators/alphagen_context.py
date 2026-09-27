"""AlphaGen 生成器的构造上下文与 objective 参数解析（F012，检视 R-C6）。

放在 generators 层：生成器只依赖本模块，不反向导入 CLI 层的 `mine_dispatch`；
`mine_dispatch` 再导出这些名字供 CLI 使用。
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from alphamill.factor_factory import errors
from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.generators.objective import CostModel, ObjectiveParams

if TYPE_CHECKING:
    from alphamill.factor_factory.generators.stop_conditions import StopController
    from alphamill.factor_factory.registry.compiler_registry import CompilerRegistry
    from alphamill.factor_factory.registry.event_writer import RunEventWriter

ALPHAGEN_GENERATOR_VERSION: Final = "alphagen-f012-v1"


@dataclass(frozen=True, kw_only=True)
class BuildContext:
    run_id: str
    config: Mapping[str, JSONValue]
    stop: StopController | None
    writer: RunEventWriter | None
    compilers: CompilerRegistry
    device: str = "cpu"


def objective_params(config: Mapping[str, JSONValue]) -> ObjectiveParams:
    objective = _mapping(config["objective"])
    cost = _mapping(objective["cost_model"])
    return ObjectiveParams(
        turnover_penalty_lambda=float(objective["turnover_penalty_lambda"]),
        reachability_min_trades_90d=int(objective["reachability_min_trades_90d"]),
        cost_model=CostModel(
            taker_fee_bps=float(cost["taker_fee_bps"]),
            maker_fee_bps=float(cost["maker_fee_bps"]),
            slippage_bps=float(cost["slippage_bps"]),
            funding_8h_bps=float(cost.get("funding_8h_bps", 0.0)),
        ),
        min_after_cost_return=float(objective["min_after_cost_return"]),
    )


def _mapping(value: object) -> Mapping[str, JSONValue]:
    if not isinstance(value, Mapping):
        raise errors.SchemaValidationError("config section must be a JSON object")
    return value
