"""证据批次原子发布与恢复（`FR-006`/`AC-005`/`NFR-001`；任务 T011）。

发布协议（design §3.2）：

1. 在**同一文件系统**的 sibling temp 目录内写全部文件并完成校验（schema、摘要、曲线-标量互推）；
   跨盘拒绝——只有 rename 才提供可见性边界；
2. `manifest.json` / `report.json` / `curves.parquet` / `events.jsonl` 就位后，**最后**生成
   `registration.json`；
3. 原子 `rename` temp → 目标目录；目标已存在时按**语义**判幂等，语义冲突即
   `E_PUBLISH_INCOMPLETE`；
4. 任一步失败：temp 清理或移入 quarantine，目标目录**不可见**——消费者只认带完整
   manifest + registration 的目录，因此失败注入不会产生「半个 PASS」。
"""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alphamill.evaluation.capabilities import TierContext
from alphamill.evaluation.contract_common import TIER_CANONICAL
from alphamill.evaluation.events import EVENTS_FILENAME, RunEvent, append_events, read_events
from alphamill.factor_factory.bench.curves import (
    CurvesData,
    CurvesError,
    assert_scalars_match,
    read_curves,
    write_curves,
)

MANIFEST_NAME = "manifest.json"
REPORT_NAME = "report.json"
CURVES_NAME = "curves.parquet"
REGISTRATION_NAME = "registration.json"
QUARANTINE_SUBDIR = "_quarantine"
MANIFEST_REQUIRED = ("schema_version", "execution_tier", "experiment_id", "state", "events_digest")
CANONICAL_MANIFEST_REQUIRED = ("research_snapshot_id", "object_id")


class PublishError(Exception):
    """发布不完整或语义冲突；映射到稳定错误码 `E_PUBLISH_INCOMPLETE`。"""

    code = "E_PUBLISH_INCOMPLETE"


@dataclass(frozen=True)
class PublishRequest:
    experiment_id: str
    manifest: Mapping[str, Any]
    report: Mapping[str, Any]
    curves: CurvesData
    events: tuple[RunEvent, ...] = ()
    registration: Mapping[str, Any] | None = None
    attempt_id: str = "attempt-1"
    object_id: str | None = None
    snapshot_id: str | None = None


def target_dir(context: TierContext, request: PublishRequest) -> Path:
    """按 tier 解析发布目录；canonical 需 `object_id`/`snapshot_id` 且触发能力校验。"""
    if context.execution_tier == TIER_CANONICAL:
        missing = [
            name
            for name, value in (
                ("object_id", request.object_id),
                ("snapshot_id", request.snapshot_id),
            )
            if not value
        ]
        if missing:
            raise PublishError(f"canonical 发布缺 {missing}")
        return context.bench_dir(
            str(request.object_id), str(request.snapshot_id), request.experiment_id
        )
    return context.preview_attempt_dir(request.experiment_id, request.attempt_id)


def assert_same_filesystem(temp: Path, root: Path) -> None:
    """temp 与目标必须同盘：跨盘 rename 退化为复制，失去原子可见性。"""
    try:
        if temp.stat().st_dev != root.stat().st_dev:
            raise PublishError(f"temp 与目标不在同一文件系统（跨盘发布拒绝）: {temp} vs {root}")
    except FileNotFoundError as exc:
        raise PublishError(f"发布路径不存在: {exc}") from exc


def _write_payload(temp: Path, request: PublishRequest, *, canonical: bool) -> None:
    manifest = dict(request.manifest)
    missing = [key for key in MANIFEST_REQUIRED if key not in manifest]
    if canonical:
        missing.extend(key for key in CANONICAL_MANIFEST_REQUIRED if key not in manifest)
    if missing:
        raise PublishError(f"manifest 缺必填字段: {sorted(set(missing))}")
    if manifest["execution_tier"] != (TIER_CANONICAL if canonical else "preview"):
        raise PublishError(f"manifest execution_tier 与请求不符: {manifest['execution_tier']!r}")
    (temp / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    (temp / REPORT_NAME).write_text(
        json.dumps(dict(request.report), ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_curves(temp / CURVES_NAME, request.curves)
    append_events(temp / EVENTS_FILENAME, request.events)


def _write_registration(temp: Path, request: PublishRequest, *, canonical: bool) -> None:
    """`registration.json` 在校验通过后**最后**写：目录可见时最后一块拼图即注册凭据。"""
    if canonical and request.registration is None:
        raise PublishError("canonical 发布必须提供 registration.json 内容")
    if request.registration is not None:
        (temp / REGISTRATION_NAME).write_text(
            json.dumps(dict(request.registration), ensure_ascii=False, indent=1, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )


def _validate_batch(temp: Path, request: PublishRequest) -> None:
    """发布前校验：曲线可读、标量互推一致、事件可回读。"""
    try:
        sidecar = read_curves(temp / CURVES_NAME)
    except CurvesError as exc:
        raise PublishError(f"曲线侧车不可读: {exc}") from exc
    declared = request.report.get("curves_summary")
    if not isinstance(declared, Mapping):
        raise PublishError("report 缺 curves_summary")
    try:
        assert_scalars_match(declared, sidecar.scalar_summary())
    except CurvesError as exc:
        raise PublishError(str(exc)) from exc
    stored = read_events(temp / EVENTS_FILENAME)
    if len(stored) != len(request.events):
        raise PublishError("events.jsonl 回读条数与请求不一致")


def _semantic_signature(directory: Path, *, canonical: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for name in (MANIFEST_NAME, REPORT_NAME, REGISTRATION_NAME):
        path = directory / name
        payload[name] = path.read_text(encoding="utf-8") if path.is_file() else None
    curves = directory / CURVES_NAME
    payload[CURVES_NAME] = read_curves(curves).scalar_summary() if curves.is_file() else None
    payload["canonical"] = canonical
    return payload


def publish(
    context: TierContext, request: PublishRequest, *, quarantine_on_failure: bool = False
) -> Path:
    """原子发布一个证据批次；失败不留可见半成品。"""
    canonical = context.execution_tier == TIER_CANONICAL
    target = target_dir(context, request)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f"{target.name}.tmp-{os.getpid()}")
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True)
    try:
        assert_same_filesystem(temp, target.parent)
        _write_payload(temp, request, canonical=canonical)
        _validate_batch(temp, request)
        _write_registration(temp, request, canonical=canonical)
        if target.exists():
            existing = _semantic_signature(target, canonical=canonical)
            if existing != _semantic_signature(temp, canonical=canonical):
                raise PublishError(f"目标已存在且语义不一致，拒绝覆盖: {target}")
            shutil.rmtree(temp)
            return target
        os.rename(temp, target)
    except Exception as exc:  # noqa: BLE001 - 失败路径必须清理/隔离 temp 后重抛
        if temp.exists():
            if quarantine_on_failure:
                tier_root = context.roots.bench_root if canonical else context.roots.preview_root
                quarantine = tier_root / QUARANTINE_SUBDIR / temp.name
                quarantine.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(temp), str(quarantine))
            else:
                shutil.rmtree(temp)
        if isinstance(exc, PublishError):
            raise
        raise PublishError(f"发布失败: {type(exc).__name__}: {exc}") from exc
    return target


def is_published(directory: Path, *, canonical: bool) -> bool:
    """消费者判据：只有带完整 manifest（canonical 还需 registration）的目录才算已发布。"""
    if not (directory / MANIFEST_NAME).is_file():
        return False
    if any(not (directory / name).is_file() for name in (REPORT_NAME, CURVES_NAME)):
        return False
    if canonical:
        return (directory / REGISTRATION_NAME).is_file()
    return True


def list_published(root: Path, *, canonical: bool) -> tuple[Path, ...]:
    if not root.is_dir():
        return ()
    return tuple(
        sorted(
            path
            for path in root.rglob("*")
            if path.is_dir() and is_published(path, canonical=canonical)
        )
    )
