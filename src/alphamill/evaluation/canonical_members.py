"""finalize 的成员证据读取（从 `canonical_ops` 拆出以守住单文件上限）。

- `resolve_reference`：把成员 `evidence_ref` 解析为物理路径（POSIX 逻辑 ref 相对 reports 根）；
- `load_member_curves` / `load_member_report`：读取成员曲线与报告，读不到即返回 `None`（由调用方
  写 `gate_rejected` 并把 cohort 统计标 `INCOMPLETE`，不得静默剔除）；
- `load_registry`：读取评测面既有记录，但**排除当前 cohort**，避免 finalize 读到自己刚写的结论。
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from alphamill.experiment_store import population
from alphamill.experiment_store.dedup import DedupCandidate, DedupRecord
from alphamill.factor_factory.bench.curves import CurvesError, read_curves


def resolve_reference(root: Path, reference: str | None) -> Path | None:
    if not reference:
        return None
    path = Path(reference)
    if path.is_absolute():
        return path
    candidate = root / path
    if candidate.exists():
        return candidate
    if path.parts and path.parts[0] == "reports":
        return root / Path(*path.parts[1:])
    return candidate


def load_member_curves(root: Path, entry: population.MemberRegistration) -> Any:
    path = resolve_reference(root, entry.evidence_ref)
    if path is None:
        return None
    try:
        return read_curves(path)
    except CurvesError:
        return None


def load_member_report(root: Path, entry: population.MemberRegistration) -> dict[str, Any] | None:
    path = resolve_reference(root, entry.evidence_ref)
    if path is None:
        return None
    report_path = path.parent / "report.json"
    if not report_path.is_file():
        return None
    return json.loads(report_path.read_text(encoding="utf-8"))


def load_registry(
    root: Path, horizon: int, exclude_cohort_id: str
) -> tuple[tuple[DedupRecord, ...], dict[str, DedupCandidate]]:
    """评测面既有记录，排除当前 cohort（否则 finalize 会读到自己刚写下的结论）。"""
    from alphamill.evaluation.registry_writeback import read_evaluation_face

    records: list[DedupRecord] = []
    candidates: dict[str, DedupCandidate] = {}
    for row in read_evaluation_face(root):
        if str(row.get("cohort_id")) == exclude_cohort_id:
            continue
        dedup = row.get("dedup") or {}
        verdict = str(dedup.get("verdict", "none"))
        factor_id = str(row["factor_id"])
        records.append(DedupRecord(factor_id=factor_id, verdict=verdict))
        if verdict == "rejected":
            continue
        path = resolve_reference(root, row.get("evidence_ref"))
        if path is None:
            continue
        try:
            curves = read_curves(path)
        except CurvesError:
            continue
        candidates[factor_id] = DedupCandidate.from_curves(
            factor_id, curves, horizon, evidence_ref=row.get("evidence_ref")
        )
    return tuple(records), candidates


def horizon_of(definition: Mapping[str, Any]) -> int:
    horizons = (definition.get("window") or {}).get("label_horizons") or [1]
    return max(int(horizon) for horizon in horizons)
