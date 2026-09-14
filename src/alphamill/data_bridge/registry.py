"""Dataset registry——F002-D007 / R2-04 冻结的只读白名单（design §3）。

`export_dataset()` 与 `read()` 的 `dataset` 参数只接受 `DATASETS` 中的键，
其余一律抛 `UnknownDatasetError`。投影列逐一枚举、顺序即编码顺序——摘要的
稳定性取决于输入是否被完全规范化，禁止用「等」占位。

类型只有五种：`timestamptz` / `text` / `double` / `jsonb` / NULL（NULL 的
哨兵编码见 digest.py）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType

from alphamill.data_bridge.errors import UnknownDatasetError

TIMESTAMPTZ = "timestamptz"
TEXT = "text"
DOUBLE = "double"
JSONB = "jsonb"

AS_OF_BITEMPORAL = "bitemporal"
AS_OF_EVENT_TIME_ONLY = "event_time_only"


@dataclass(frozen=True)
class Column:
    name: str
    logical_type: str


@dataclass(frozen=True)
class DatasetSpec:
    """单个 dataset 的投影与分区契约。

    - `projection`：导出/编码列，顺序即 digest 编码顺序（design §3 表）。
    - `event_time` / `available_at`：双时间轴；`available_at=None` 表示该表
      无采集时间列，as-of 退化为 event_time_only（fail-closed，见 reader）。
    - `partition_keys`：逻辑分区键成分；`pair` 指经 symbol_map 换算的湖内
      pair，`date` 指 event_time 的 UTC 日期。
    - `market_type`：symbol_map 消歧用（lake pair 过滤 → db symbol）。
    - `symbol_map_enabled`：是否将该源表的 symbol 纳入全局映射；无 pair 分区的
      混合来源不能仅凭 registry 的单一 market_type 推导映射，默认不参与。
    - `deferred_labels`：事后回填的结果列 → 其可用时间列。`read(as_of=T)`
      时可用时间 > T 的标签置 NULL 而非丢行（design §3）。
    """

    name: str
    source_table: str
    projection: tuple[Column, ...]
    event_time: str
    available_at: str | None
    partition_keys: tuple[str, ...]
    primary_key: tuple[str, ...]
    as_of_fidelity: str
    market_type: str
    deferred_labels: dict[str, str] = field(default_factory=dict)
    symbol_map_enabled: bool = True


_OHLCV_PROJECTION = (
    Column("time", TIMESTAMPTZ),
    Column("exchange", TEXT),
    Column("symbol", TEXT),
    Column("open", DOUBLE),
    Column("high", DOUBLE),
    Column("low", DOUBLE),
    Column("close", DOUBLE),
    Column("volume", DOUBLE),
)

_FUNDING_PROJECTION = (
    Column("time", TIMESTAMPTZ),
    Column("exchange", TEXT),
    Column("symbol", TEXT),
    Column("funding_rate", DOUBLE),
    Column("next_funding_time", TIMESTAMPTZ),
    Column("mark_price", DOUBLE),
    Column("index_price", DOUBLE),
    Column("metadata", JSONB),
    Column("ingested_at", TIMESTAMPTZ),
)

_OI_PROJECTION = (
    Column("time", TIMESTAMPTZ),
    Column("exchange", TEXT),
    Column("symbol", TEXT),
    Column("timeframe", TEXT),
    Column("open_interest", DOUBLE),
    Column("open_interest_value", DOUBLE),
    Column("base_volume", DOUBLE),
    Column("quote_volume", DOUBLE),
    Column("metadata", JSONB),
    Column("ingested_at", TIMESTAMPTZ),
)

_BASIS_PROJECTION = (
    Column("time", TIMESTAMPTZ),
    Column("exchange", TEXT),
    Column("symbol", TEXT),
    Column("timeframe", TEXT),
    Column("mark_open", DOUBLE),
    Column("mark_high", DOUBLE),
    Column("mark_low", DOUBLE),
    Column("mark_close", DOUBLE),
    Column("index_open", DOUBLE),
    Column("index_high", DOUBLE),
    Column("index_low", DOUBLE),
    Column("index_close", DOUBLE),
    Column("basis_close", DOUBLE),
    Column("basis_pct", DOUBLE),
    Column("metadata", JSONB),
    Column("ingested_at", TIMESTAMPTZ),
)

_SIGNALS_PROJECTION = (
    Column("time", TIMESTAMPTZ),
    Column("exchange", TEXT),
    Column("symbol", TEXT),
    Column("source", TEXT),
    Column("signal_type", TEXT),
    Column("confidence", DOUBLE),
    Column("metadata", JSONB),
    Column("latest_candle", TIMESTAMPTZ),
    Column("expected_return", DOUBLE),
    Column("volatility", DOUBLE),
    Column("direction_prob", DOUBLE),
    Column("realized_return_60m", DOUBLE),
    Column("evaluated_at", TIMESTAMPTZ),
)

_DATASETS: dict[str, DatasetSpec] = {
    "ohlcv_1m": DatasetSpec(
        name="ohlcv_1m",
        source_table="ohlcv_1m",
        projection=_OHLCV_PROJECTION,
        event_time="time",
        available_at=None,  # 无采集时间列：as-of 只能退化，见 design §3 已知缺口
        partition_keys=("exchange", "pair", "date"),
        primary_key=("exchange", "symbol", "time"),
        as_of_fidelity=AS_OF_EVENT_TIME_ONLY,
        market_type="spot",
    ),
    "derivatives_funding_rates": DatasetSpec(
        name="derivatives_funding_rates",
        source_table="derivatives_funding_rates",
        projection=_FUNDING_PROJECTION,
        event_time="time",
        available_at="ingested_at",
        partition_keys=("exchange", "pair", "date"),
        primary_key=("exchange", "symbol", "time"),
        as_of_fidelity=AS_OF_BITEMPORAL,
        market_type="perp",
    ),
    "derivatives_open_interest": DatasetSpec(
        name="derivatives_open_interest",
        source_table="derivatives_open_interest",
        projection=_OI_PROJECTION,
        event_time="time",
        available_at="ingested_at",
        partition_keys=("exchange", "pair", "timeframe", "date"),
        primary_key=("exchange", "symbol", "timeframe", "time"),
        as_of_fidelity=AS_OF_BITEMPORAL,
        market_type="perp",
    ),
    "derivatives_mark_index_basis": DatasetSpec(
        name="derivatives_mark_index_basis",
        source_table="derivatives_mark_index_basis",
        projection=_BASIS_PROJECTION,
        event_time="time",
        available_at="ingested_at",
        partition_keys=("exchange", "pair", "timeframe", "date"),
        primary_key=("exchange", "symbol", "timeframe", "time"),
        as_of_fidelity=AS_OF_BITEMPORAL,
        market_type="perp",
    ),
    "signals_log": DatasetSpec(
        name="signals_log",
        source_table="signals_log",
        projection=_SIGNALS_PROJECTION,
        event_time="latest_candle",
        available_at="time",
        partition_keys=("date",),  # 无 exchange 维度，按事件日分区（DQ-001）
        primary_key=(),  # 库内无主键（design §3：摘要排序因此用编码字节串）
        as_of_fidelity=AS_OF_BITEMPORAL,
        market_type="spot",
        deferred_labels={"realized_return_60m": "evaluated_at"},
        symbol_map_enabled=False,
    ),
}

DATASETS: MappingProxyType[str, DatasetSpec] = MappingProxyType(_DATASETS)

# 允许进入 read() SQL 谓词的列仅此五者；其余列读出来由调用方自筛（design §3）。
FILTERABLE_COLUMNS = frozenset({"event_time", "available_at", "exchange", "symbol", "timeframe"})


def require_dataset(name: str) -> DatasetSpec:
    try:
        return _DATASETS[name]
    except KeyError:
        raise UnknownDatasetError(
            f"未知 dataset: {name!r}；合法取值: {sorted(_DATASETS)}"
        ) from None


def pair_partitioned(spec: DatasetSpec) -> bool:
    return "pair" in spec.partition_keys


def timeframe_partitioned(spec: DatasetSpec) -> bool:
    return "timeframe" in spec.partition_keys
