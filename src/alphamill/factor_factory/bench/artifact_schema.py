"""产物 schema 读取与契约断言（`AC-005`/`AC-011`/`AC-012`/`NFR-005`；任务 T015）。

三类产物各自带 `schema_version`，reader 接受**当前版与前一版**、未知更高版本失败关闭
（`design.md` §7「兼容」）。发布前的互推与标注断言集中在这里，供 contract 测试与后续 consumer
（F005 只读 API、F006 晋级入口）共用：

- `curves.parquet` 的标量摘要必须能从侧车在容差内重算；
- `approximation` 标注**必须存在**；canonical 恒为 `is_approximate=false` 且无缩减维度；
- 产物路径只允许 **POSIX 逻辑路径/URI**：不得出现反斜杠或盘符（Windows/WSL 物理路径只进
  provenance，不进 manifest 的契约字段）。
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alphamill.factor_factory.bench.curves import (
    CurvesData,
    CurvesError,
    assert_scalars_match,
    read_curves,
)

SCHEMA_VERSION = 1
SUPPORTED_VERSIONS = (SCHEMA_VERSION,)
REPORT_REQUIRED = (
    "schema_version",
    "experiment_id",
    "approximation",
    "curves_summary",
    "stage_results",
)
SYNTHESIS_REQUIRED = (
    "schema_version",
    "synthesis_id",
    "cohort_id",
    "status",
    "funnel",
    "stage_funnel",
    "failures",
    "facts",
    "inferences",
    "recommendations",
)
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")


class ArtifactSchemaError(ValueError):
    """schema 版本不支持、缺必填字段、互推不符或路径不是 POSIX 逻辑路径。"""


@dataclass(frozen=True)
class ArtifactBundle:
    report: Mapping[str, Any]
    curves: CurvesData
    synthesis: Mapping[str, Any] | None = None


def is_logical_posix_path(value: str) -> bool:
    """POSIX 逻辑路径判据：无反斜杠、无盘符、无 Windows UNC 前缀。"""
    if not isinstance(value, str) or not value:
        return False
    if "\\" in value or value.startswith("//") or value.startswith("/"):
        return False
    return WINDOWS_DRIVE_RE.match(value) is None


def assert_logical_posix_paths(payload: Any, *, prefix: str = "") -> None:
    """递归断言所有以 `path`/`uri`/`ref` 结尾的字符串字段都是 POSIX 逻辑路径。"""
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key).lower() == "provenance":
                continue
            location = f"{prefix}.{key}" if prefix else str(key)
            if (
                isinstance(value, str)
                and any(token in str(key).lower() for token in ("path", "uri", "ref"))
                and not is_logical_posix_path(value)
            ):
                raise ArtifactSchemaError(f"{location} 不是 POSIX 逻辑路径: {value!r}")
            assert_logical_posix_paths(value, prefix=location)
    elif isinstance(payload, (list, tuple)):
        for index, item in enumerate(payload):
            assert_logical_posix_paths(item, prefix=f"{prefix}[{index}]")


def _check_version(payload: Mapping[str, Any], name: str) -> int:
    version = payload.get("schema_version")
    if version not in SUPPORTED_VERSIONS:
        raise ArtifactSchemaError(
            f"{name} 的 schema_version 不支持: {version!r}（支持 {list(SUPPORTED_VERSIONS)}，"
            "未知高版本失败关闭）"
        )
    return int(version)


def assert_approximation(payload: Mapping[str, Any], *, canonical: bool) -> None:
    """`approximation` 必须存在；canonical 恒为非近似且无缩减维度（`NFR-004`）。"""
    annotation = payload.get("approximation")
    if not isinstance(annotation, Mapping):
        raise ArtifactSchemaError("产物缺 approximation 标注")
    if "is_approximate" not in annotation:
        raise ArtifactSchemaError("approximation 缺 is_approximate")
    if canonical and annotation["is_approximate"]:
        raise ArtifactSchemaError("canonical 产物不得为近似（NFR-004）")
    if canonical and annotation.get("reduced_dimensions"):
        raise ArtifactSchemaError("canonical 产物不得声明 reduced_dimensions")


def read_report(path: Path, *, canonical: bool = False) -> dict[str, Any]:
    if not path.is_file():
        raise ArtifactSchemaError(f"report 不存在: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    _check_version(payload, "report")
    missing = [field for field in REPORT_REQUIRED if field not in payload]
    if missing:
        raise ArtifactSchemaError(f"report 缺必填字段: {missing}")
    assert_approximation(payload, canonical=canonical)
    assert_logical_posix_paths(payload)
    return payload


def read_synthesis(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ArtifactSchemaError(f"synthesis 不存在: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    _check_version(payload, "synthesis")
    missing = [field for field in SYNTHESIS_REQUIRED if field not in payload]
    if missing:
        raise ArtifactSchemaError(f"synthesis 缺必填字段: {missing}")
    for column in ("facts", "inferences", "recommendations"):
        if not isinstance(payload[column], list):
            raise ArtifactSchemaError(f"synthesis.{column} 必须是数组")
    assert_logical_posix_paths(payload)
    return payload


def read_artifact_dir(directory: Path, *, canonical: bool = False) -> ArtifactBundle:
    """读取一个已发布批次并做跨产物互推：report 的标量摘要必须与侧车重算一致。"""
    report = read_report(directory / "report.json", canonical=canonical)
    curves = read_curves(directory / "curves.parquet")
    try:
        assert_scalars_match(report["curves_summary"], curves.scalar_summary())
    except CurvesError as exc:
        raise ArtifactSchemaError(str(exc)) from exc
    synthesis_path = directory / "synthesis_report.json"
    synthesis = read_synthesis(synthesis_path) if synthesis_path.is_file() else None
    return ArtifactBundle(report=report, curves=curves, synthesis=synthesis)


def assert_stage_ids(payload: Mapping[str, Any]) -> None:
    """五阶段 ID 必须来自冻结清单（`AC-012`）。"""
    from alphamill.factor_factory.bench.stage_model import STAGE_IDS

    for entry in payload.get("stage_results", ()):
        if entry.get("stage") not in STAGE_IDS:
            raise ArtifactSchemaError(f"产物含未登记阶段: {entry.get('stage')!r}")


def assert_failure_taxonomy(payload: Mapping[str, Any]) -> None:
    """失败记录的 stage/owner/mechanism 必须来自冻结三维（`AC-012`）。"""
    from alphamill.factor_factory.bench.stage_model import (
        FAILURE_MECHANISMS,
        FAILURE_OWNERS,
        STAGE_IDS,
    )

    for entry in payload.get("stage_results", ()):
        for failure in entry.get("failures", ()):
            if failure.get("stage") not in STAGE_IDS:
                raise ArtifactSchemaError(f"失败记录 stage 未登记: {failure.get('stage')!r}")
            if failure.get("owner") not in FAILURE_OWNERS:
                raise ArtifactSchemaError(f"失败记录 owner 未登记: {failure.get('owner')!r}")
            if failure.get("mechanism") not in FAILURE_MECHANISMS:
                raise ArtifactSchemaError(
                    f"失败记录 mechanism 未登记: {failure.get('mechanism')!r}"
                )
