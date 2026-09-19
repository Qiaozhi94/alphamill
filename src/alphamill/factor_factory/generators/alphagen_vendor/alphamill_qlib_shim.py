# [alphamill] Define only the qlib-free type surface consumed by the vendored core.
from enum import IntEnum
from typing import Protocol

from torch import Tensor


class FeatureType(IntEnum):
    OPEN = 0
    CLOSE = 1
    HIGH = 2
    LOW = 3
    VOLUME = 4
    VWAP = 5


class StockData(Protocol):
    data: Tensor
    max_backtrack_days: int
    max_future_days: int

    @property
    def n_days(self) -> int: ...

    @property
    def n_stocks(self) -> int: ...
