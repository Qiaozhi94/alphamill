"""导出摘要构造；与数据库/湖文件编排解耦。"""

from __future__ import annotations

import time
from typing import Any

from alphamill.data_bridge import registry


def build_summary(
    spec: registry.DatasetSpec,
    mode: str,
    data_version: str | None,
    baseline_version: str | None,
    merged: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    skipped: list[dict[str, str]],
    reconcile_field: dict[str, Any],
    *,
    excluded: int,
    started: float,
    no_op: bool,
    reason: str | None,
    revision_diff: list[dict[str, Any]],
    universe_id: str | None = None,
    dropped_by_universe: tuple[str, ...] | list[str] = (),
) -> dict[str, Any]:
    return {
        "dataset": spec.name,
        "mode": mode,
        "data_version": data_version,
        "baseline_version": baseline_version,
        "status": "invalid" if failures else ("no-op" if no_op else "valid"),
        "no_op": no_op,
        "reason": reason,
        "rows": sum(p["rows"] for p in merged),
        "partitions": len(merged),
        "skipped": len(skipped),
        "reconcile": reconcile_field,
        "revision_diff": len(revision_diff),
        "excluded_null_event_time": excluded,
        "elapsed_seconds": round(time.monotonic() - started, 2),
        # F011 IR-002：键始终存在；未开过滤或未给绑定时为 null / []
        "universe_id": universe_id,
        "dropped_by_universe": list(dropped_by_universe),
    }
