"""可执行 FactorDef 契约（唯一拥有者；对应架构 §4.1）。

磁盘 DTO 与可执行对象是同一对象的两种形态，转换归 registry/factor_store.py；
本模块只定义可执行形态，不依赖任何存储或后端模块。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypeAlias

import pandas as pd

from alphamill.factor_factory.canonical import JSONValue

FactorScope: TypeAlias = Literal["time_series", "cross_sectional"]
FactorInput: TypeAlias = pd.DataFrame
FactorOutput: TypeAlias = pd.Series
FactorCompute: TypeAlias = Callable[[FactorInput], FactorOutput]
FactorResolver: TypeAlias = Callable[[str], "FactorDef"]


@dataclass(frozen=True)
class FactorDef:
    """只含定义、不含任何评测结论的可执行因子。

    `time_series` 的输入输出索引为 UTC DatetimeIndex；`cross_sectional` 为命名为
    `("timestamp", "pair")` 的 MultiIndex，并以保留列 `__in_universe__` 承载 PIT
    掩码——掩码外的行输出 NaN（no-signal 的唯一表示）。表达式原文只存在于
    `meta["expression"]`，不得成为顶层字段。
    """

    factor_id: str
    hypothesis_id: str
    name: str
    generator: str
    scope: FactorScope
    params: dict[str, JSONValue]
    compute: FactorCompute
    data_columns: list[str]
    meta: dict[str, JSONValue]
