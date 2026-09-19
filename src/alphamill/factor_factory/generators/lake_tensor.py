"""Build deterministic factor panels from validated immutable lake bindings."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, assert_never

import pandas as pd
from pandas.tseries.frequencies import to_offset

from alphamill.data_bridge import reader, registry, symbol_map
from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.generators.binding import (
    ExplicitSnapshotBinding,
    SnapshotRefBinding,
    ValidatedBinding,
)
from alphamill.factor_factory.registry.factor_store import (
    feature_map_digest as digest_feature_map,
)

_OHLCV_AGGREGATIONS: Final[dict[str, str]] = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
}


@dataclass(frozen=True, kw_only=True)
class TensorPanel:
    """A cross-sectional feature panel with immutable snapshot provenance."""

    datasets: tuple[str, ...]
    resample: str
    pairs: tuple[str, ...]
    timestamps: pd.DatetimeIndex
    panel: pd.DataFrame
    feature_map: dict[str, int]
    feature_map_digest: str
    universe_source: str


def _aggregate(frame: pd.DataFrame, resample: str) -> pd.DataFrame:
    feature_columns = tuple(
        column for column in frame.columns if column not in {"timestamp", "pair"}
    )
    if resample == "1m":
        result = frame.set_index(["timestamp", "pair"])[list(feature_columns)]
        if result.index.has_duplicates:
            raise SchemaValidationError("1m tensor input has duplicate (timestamp, pair) rows")
        return result.sort_index()

    aggregations = {column: _OHLCV_AGGREGATIONS.get(column, "last") for column in feature_columns}
    result = (
        frame.set_index("timestamp")
        .groupby("pair", sort=True)
        .resample(resample, closed="right", label="right")
        .agg(aggregations)
    )
    result.index.names = ["pair", "timestamp"]
    return result.reorder_levels(["timestamp", "pair"]).sort_index()


def build_tensor(
    binding: ValidatedBinding,
    *,
    datasets: Sequence[str],
    resample: str = "1h",
    start: object | None = None,
    end: object | None = None,
    pairs: Sequence[str] | None = None,
    lake_root: Path | None = None,
) -> TensorPanel:
    """Build a PIT-masked panel through the F002 reader only.

    Feature channels use ``<dataset>.<column>@<resample>`` names in dataset input order,
    then registry projection order. This keeps dataset and resampling identity inside the
    canonical feature-map digest. A requested dataset returning zero rows raises
    ``SchemaValidationError`` instead of silently disappearing from the tensor.
    """
    dataset_names = tuple(datasets)
    if not dataset_names:
        raise SchemaValidationError("datasets must contain at least one dataset")
    if len(set(dataset_names)) != len(dataset_names):
        raise SchemaValidationError("datasets must not contain duplicates")
    if resample != "1m":
        try:
            interval_ns = to_offset(resample).nanos
        except (TypeError, ValueError) as exc:
            raise SchemaValidationError(f"unsupported resample: {resample!r}") from exc
        if interval_ns <= 0:
            raise SchemaValidationError(f"unsupported resample: {resample!r}")

    requested_pairs = list(pairs) if pairs is not None else None
    resolved = binding.resolved
    mapping = symbol_map.load_symbol_map(
        digest=resolved.symbol_map_digest,
        lake_root=lake_root,
    )
    dataset_panels: list[pd.DataFrame] = []
    ordered_features: list[str] = []
    for dataset in dataset_names:
        member = resolved.members.get(dataset)
        if member is None:
            raise SchemaValidationError(f"dataset absent from validated binding: {dataset!r}")
        spec = registry.require_dataset(dataset)
        result = reader.read(
            dataset,
            data_version=member.data_version,
            start=start,
            end=end,
            pairs=requested_pairs,
            as_of=resolved.cutoff_time,
            allow_event_time_only=member.as_of_fidelity == "event_time_only",
            lake_root=lake_root,
        )
        expected_columns = tuple(column.name for column in spec.projection)
        actual_columns = tuple(result.frame.columns)
        missing = tuple(column for column in expected_columns if column not in actual_columns)
        extra = tuple(column for column in actual_columns if column not in expected_columns)
        if missing or extra:
            raise SchemaValidationError(
                f"{dataset}: reader schema mismatch; missing={missing!r}, extra={extra!r}"
            )
        if result.frame.empty:
            raise SchemaValidationError(f"{dataset} returned 0 rows for the requested window")

        lookup = mapping.loc[
            mapping["market_type"].eq(spec.market_type),
            ["exchange", "db_symbol", "lake_pair"],
        ]
        mapped = result.frame.merge(
            lookup,
            how="left",
            left_on=["exchange", "symbol"],
            right_on=["exchange", "db_symbol"],
            validate="many_to_one",
        )
        if mapped["lake_pair"].isna().any():
            missing_symbols = tuple(
                sorted(mapped.loc[mapped["lake_pair"].isna(), "symbol"].astype(str).unique())
            )
            raise SchemaValidationError(
                f"{dataset}: symbol_map missing db symbols {missing_symbols!r}"
            )
        if requested_pairs is not None:
            mapped = mapped.loc[mapped["lake_pair"].isin(requested_pairs)]
        if mapped.empty:
            raise SchemaValidationError(f"{dataset} returned 0 rows for the requested pairs")

        raw_features = tuple(
            column.name for column in spec.projection if column.logical_type == registry.DOUBLE
        )
        prepared = mapped.loc[:, [spec.event_time, "lake_pair", *raw_features]].rename(
            columns={spec.event_time: "timestamp", "lake_pair": "pair"}
        )
        prepared["timestamp"] = pd.to_datetime(prepared["timestamp"], utc=True)
        aggregated = _aggregate(prepared, resample)
        channel_names = tuple(f"{dataset}.{column}@{resample}" for column in raw_features)
        dataset_panels.append(
            aggregated.rename(columns=dict(zip(raw_features, channel_names, strict=True)))
        )
        ordered_features.extend(channel_names)

    panel = pd.concat(dataset_panels, axis="columns", join="outer").sort_index()
    panel.index = panel.index.set_names(["timestamp", "pair"])
    timestamps = pd.DatetimeIndex(panel.index.get_level_values("timestamp").unique()).sort_values()
    memberships = {
        timestamp: binding.universe_ledger.universe_at(timestamp.to_pydatetime())
        for timestamp in timestamps
    }
    row_timestamps = pd.DatetimeIndex(panel.index.get_level_values("timestamp"))
    row_pairs = panel.index.get_level_values("pair")
    mask = pd.Series(
        [
            str(pair) in memberships[timestamp]
            for timestamp, pair in zip(row_timestamps, row_pairs, strict=True)
        ],
        index=panel.index,
        dtype=bool,
    )
    panel.loc[~mask, ordered_features] = float("nan")
    panel["__in_universe__"] = mask
    feature_map = {feature: channel for channel, feature in enumerate(ordered_features)}

    match binding.source:
        case ExplicitSnapshotBinding():
            universe_source = (
                f"explicit:{resolved.universe.path.as_posix()}@{resolved.universe.digest}"
            )
        case SnapshotRefBinding():
            universe_source = f"f008:{resolved.universe.digest}"
        case unreachable:
            assert_never(unreachable)

    return TensorPanel(
        datasets=dataset_names,
        resample=resample,
        pairs=tuple(sorted({str(pair) for pair in row_pairs})),
        timestamps=timestamps,
        panel=panel,
        feature_map=feature_map,
        feature_map_digest=digest_feature_map(feature_map),
        universe_source=universe_source,
    )
