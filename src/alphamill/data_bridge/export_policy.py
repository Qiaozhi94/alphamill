"""全量导出的版本组成与收缩护栏（design §3）。

从 exporter 拆出的纯策略层：只对「基线清单 / 本轮清单 / 窗口上界」做判断，
不碰数据库、不碰湖文件，因此可以脱离 DB 单元测试（SOP 350 行上限）。
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge.errors import DataBridgeError


def merge_partitions(
    mode: str, baseline: list[dict[str, Any]], produced: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """增量继承全量基线；full 以本次源库全量结果为版本组成。"""
    inherited = baseline if mode == "incremental" else []
    return mf.synthesize_partitions(inherited, produced)


def guard_full_shrink(
    baseline: list[dict[str, Any]],
    current: list[dict[str, Any]],
    end: dt.date,
    *,
    allow_shrink: bool = False,
) -> None:
    """阻止全量导出因空库/错误窗口意外发布大幅缩水快照。

    `allow_shrink=True` 是「源库收缩确属有意」的人工确认通道（CLI `--allow-shrink`），
    放行空结果与大幅收缩，并由调用方在 manifest 记 `shrink_confirmed`（F002-R3-02）。
    窗口截断不在确认范围内——那是 `--window-end` 传错，不是源库收缩，任何情况下都拒绝。
    """
    if not baseline:
        return
    baseline_dates = [
        dt.date.fromisoformat(partition["logical_partition_key"]["date"]) for partition in baseline
    ]
    if max(baseline_dates) >= end:
        raise DataBridgeError(
            f"full window_end={end.isoformat()} 会截断已有基线，拒绝发布；"
            "请扩大窗口或明确处理历史快照（窗口错误不可用 --allow-shrink 绕过）"
        )
    if allow_shrink:
        return
    if not current:
        raise DataBridgeError(
            "full 导出得到空快照且已有非空基线，拒绝发布；"
            "确认源表清空确属有意后用 --allow-shrink 重跑"
        )
    if len(current) * 2 < len(baseline):
        raise DataBridgeError(
            f"full 导出分区数从 {len(baseline)} 大幅降至 {len(current)}，拒绝发布；"
            "确认源表收缩确属有意后用 --allow-shrink 重跑"
        )
