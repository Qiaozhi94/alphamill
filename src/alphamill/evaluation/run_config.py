"""preview 的输入装载与快照解析（任务 T006）。

- `load_run_config`：预注册 method/cost/window 配置（阈值不硬编码在评测函数，`FR-004`）；
- `load_unified_frame`：统一列集的信号夹具（T002 冻结的列契约）；
- `resolve_snapshot`：显式 `--snapshot` 直接读取；`--latest` **先解析并冻结**成 ResearchSnapshot
  再返回（ADR-0007 决策 5——canonical 禁止动态 latest，preview 也必须先冻结）；
- `preview_cohort_id`：未显式给 cohort 时的确定性 preview 专属引用（永不登记）。
"""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from alphamill.data_bridge import paths
from alphamill.evaluation.contract_common import UpstreamContractError
from alphamill.experiment_store import research_snapshot as rs
from alphamill.experiment_store.identity import canonical_json, content_digest

SIGNAL_COLUMN = "signal"
LABEL_COLUMN = "forward_return"
TIME_COLUMN = "time"
SYMBOL_COLUMN = "symbol"
CLOSE_COLUMN = "close"
REQUIRED_COLUMNS = (TIME_COLUMN, SYMBOL_COLUMN, CLOSE_COLUMN, SIGNAL_COLUMN, LABEL_COLUMN)


@dataclass(frozen=True)
class RunConfig:
    method_config: Mapping[str, Any]
    cost_model: Mapping[str, Any]
    window: Mapping[str, Any]

    @property
    def min_observations(self) -> int:
        ic = self.method_config.get("normalized", {}).get("ic", {})
        return int(ic.get("min_observations", 30))

    @property
    def max_label_horizon(self) -> int:
        return max(int(horizon) for horizon in self.window["label_horizons"])


def load_run_config(path: Path) -> RunConfig:
    """装载预注册配置；字段缺失或 JSON 非法即 `E_INPUT_INVALID`。"""
    if not path.is_file():
        raise UpstreamContractError(f"配置不存在: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise UpstreamContractError(f"配置不是合法 JSON: {path}: {exc}") from exc
    missing = [key for key in ("method_config", "cost_model", "window") if key not in payload]
    if missing:
        raise UpstreamContractError(f"配置缺少字段: {missing}")
    return RunConfig(
        method_config=payload["method_config"],
        cost_model=payload["cost_model"],
        window=payload["window"],
    )


def load_unified_panel(
    path: Path,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[float, ...], tuple[float, ...]]:
    """读取统一列集的信号夹具，保留 `symbol` 列以支持横截面逐期 IC。

    强制 `(time, symbol)` 唯一，并按 `(symbol, time)` 规范化排序：结果不得依赖 CSV 原始行序，
    否则同一面板换个行序会改变成本换手与样本量档位（`R1-103`）。按 symbol 分组排序保留了
    「每标的时序」的既有夹具语义（冻结控制期望以此为准），只消除行序不确定性。
    """
    if not path.is_file():
        raise UpstreamContractError(f"信号文件不存在: {path}")
    rows: list[tuple[str, str, float, float]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REQUIRED_COLUMNS:
            raise UpstreamContractError(
                f"信号文件列集不符（期望 {list(REQUIRED_COLUMNS)}）: {reader.fieldnames}"
            )
        for index, row in enumerate(reader, start=2):
            try:
                signal = float(row[SIGNAL_COLUMN])
                label = float(row[LABEL_COLUMN])
            except (TypeError, ValueError) as exc:
                raise UpstreamContractError(f"信号文件第 {index} 行数值非法: {exc}") from exc
            rows.append((row[TIME_COLUMN], row[SYMBOL_COLUMN], signal, label))
    if not rows:
        raise UpstreamContractError(f"信号文件为空: {path}")
    seen: set[tuple[str, str]] = set()
    for time, symbol, _signal, _label in rows:
        key = (time, symbol)
        if key in seen:
            raise UpstreamContractError(f"信号文件存在重复 (time,symbol): {key}")
        seen.add(key)
    rows.sort(key=lambda item: (item[1], item[0]))
    return (
        tuple(row[0] for row in rows),
        tuple(row[1] for row in rows),
        tuple(row[2] for row in rows),
        tuple(row[3] for row in rows),
    )


def load_unified_frame(path: Path) -> tuple[tuple[str, ...], tuple[float, ...], tuple[float, ...]]:
    """读取统一列集的信号夹具（不保留 symbol）。"""
    times, _symbols, signals, labels = load_unified_panel(path)
    return times, signals, labels


def preview_cohort_id(upstream_id: str, snapshot_id: str) -> str:
    payload = canonical_json({"preview": True, "upstream": upstream_id, "snapshot": snapshot_id})
    return "cohort_sha256:" + content_digest(payload.encode("utf-8")).removeprefix("sha256:")


def resolve_snapshot(
    *,
    snapshot_id: str | None,
    latest: Sequence[str] | None,
    cutoff: str | None,
    symbol_map_digest: str | None,
    universe_digest: str | None,
    calendar_path: Path | None,
) -> rs.ResearchSnapshot:
    """显式 ID 直接读取；latest 先解析、校验、冻结并发布成快照。"""
    root = rs.reports_root()
    if snapshot_id is not None:
        return rs.load_snapshot(root, snapshot_id)
    if not latest:
        raise UpstreamContractError("preview 需要 --snapshot 或 --latest")
    missing = [
        name
        for name, value in (
            ("--cutoff", cutoff),
            ("--symbol-map", symbol_map_digest),
            ("--universe", universe_digest),
            ("--calendar", calendar_path),
        )
        if value is None
    ]
    if missing:
        raise UpstreamContractError(f"--latest 模式必须同时给出 {missing}")
    try:
        calendar = json.loads(Path(calendar_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UpstreamContractError(f"calendar 读取失败: {calendar_path}: {exc}") from exc
    try:
        cutoff_time = datetime.fromisoformat(str(cutoff))
    except ValueError as exc:
        raise UpstreamContractError(f"--cutoff 不是合法 ISO-8601: {cutoff!r}") from exc
    snapshot = rs.build_snapshot(
        lake_root=paths.lake_root(),
        root=root,
        cutoff=cutoff_time,
        datasets={name: None for name in latest},
        universe_digest=str(universe_digest),
        calendar=calendar,
        symbol_map_digest=str(symbol_map_digest),
        require_bitemporal=False,
        allow_latest=True,
    )
    rs.publish_snapshot(root, snapshot)
    return snapshot
