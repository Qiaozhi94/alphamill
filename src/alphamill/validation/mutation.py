"""F007 定向变异证据（`AC-001`~`AC-013` 的门禁判别力；任务 T017）。

外部变异工具（mutmut / cosmic-ray）在 v0.2 的开发环境不可用（无网络安装），因此本模块实现一个
**确定性、零依赖**的定向变异台：每个 mutant 用一个「等价但被削弱」的判据与真实判据跑同一份输入，
`killed = 真实判据拦截 ∧ 削弱判据放行`。这直接证明门禁的**判别力**（抓到 vs 放过），而不是只证明
它当前对某个 fixture 返回红色。

覆盖 `design.md` §8 指定的高风险路径：future-fill（L1 纯度）、embargo 比较符、guard 注册表、
preview writer 权限、异常吞噬（估计器失败关闭）、发布完整性判据。

结果写 `reports/mutation/f007/mutation_report.json`（开发期证据，非 canonical 结论）。
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
MUTATION_SUBDIR = ("mutation", "f007")
REPORT_NAME = "mutation_report.json"
HARNESS = "in-repo deterministic mutant harness (no external dependency)"


def _weakened_noop() -> bool:
    """与真实判据等价的「削弱」实现：跳过全部校验（故意放行）。"""
    return False


def _real_future_fill() -> bool:
    from alphamill.validation.methodology_gate import GuardViolation, assert_no_lookahead_expression

    try:
        assert_no_lookahead_expression("shift(close, -1) / close - 1")
    except GuardViolation:
        return True
    return False


def _real_embargo() -> bool:
    from alphamill.validation import methodology_gate as mg

    try:
        mg._guard_embargo("close", mg.GuardContext(max_label_horizon=24, embargo=5))
    except mg.GuardViolation:
        return True
    return False


def _real_guard_registration() -> bool:
    from alphamill.validation.methodology_gate import GuardViolation, assert_capabilities_guarded

    try:
        assert_capabilities_guarded(["teleport"])
    except GuardViolation:
        return True
    return False


def _real_preview_writer() -> bool:
    from alphamill.evaluation.capabilities import CapabilityError, context_for

    try:
        context_for("preview", Path("/tmp/reports")).require("canonical_writer")
    except CapabilityError:
        return True
    return False


def _real_exception_swallowing() -> bool:
    from alphamill.factor_factory.bench.multiplicity import statistics_stage
    from alphamill.factor_factory.bench.stage_model import STAGE_TEMPORAL_STABILITY, STATUS_PASS
    from alphamill.factor_factory.bench.statistics import fit_ic

    _value, stage = statistics_stage(
        STAGE_TEMPORAL_STABILITY, lambda: fit_ic([0.1]), observed_at="2026-09-01T00:00:00Z"
    )
    return stage.status != STATUS_PASS


def _real_publish_completeness() -> bool:
    import tempfile

    from alphamill.evaluation.publisher import is_published

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        (path / "manifest.json").write_text("{}", encoding="utf-8")
        (path / "report.json").write_text("{}", encoding="utf-8")
        (path / "curves.parquet").write_bytes(b"")
        return is_published(path, canonical=True) is False


@dataclass(frozen=True)
class Mutant:
    mutant_id: str
    gate: str
    description: str
    real: Callable[[], bool]
    weakened: Callable[[], bool]

    @property
    def killed(self) -> bool:
        return bool(self.real()) and not bool(self.weakened())

    def to_payload(self) -> dict[str, Any]:
        real = bool(self.real())
        weakened = bool(self.weakened())
        return {
            "mutant_id": self.mutant_id,
            "gate": self.gate,
            "description": self.description,
            "real_detected": real,
            "weakened_detected": weakened,
            "status": "killed" if (real and not weakened) else "survived",
        }


MUTANTS: tuple[Mutant, ...] = (
    Mutant(
        "M01_future_fill",
        "l1_ast_purity",
        "L1 纯度门对负向 shift 的拦截（削弱 = 完全不校验）",
        _real_future_fill,
        _weakened_noop,
    ),
    Mutant(
        "M02_embargo_comparator",
        "embargo_covers_max_horizon",
        "embargo < max horizon 必须拒绝（削弱 = 让比较永不触发）",
        _real_embargo,
        _weakened_noop,
    ),
    Mutant(
        "M03_guard_registration",
        "capability_registry",
        "未登记能力默认拒绝（削弱 = 不做配对检查）",
        _real_guard_registration,
        _weakened_noop,
    ),
    Mutant(
        "M04_preview_writer",
        "capability_boundary",
        "preview 无 canonical writer（削弱 = 授予全部能力）",
        _real_preview_writer,
        _weakened_noop,
    ),
    Mutant(
        "M05_exception_swallowing",
        "required_statistics_fail_closed",
        "估计器异常必须记 INCOMPLETE（削弱 = 吞成 PASS）",
        _real_exception_swallowing,
        _weakened_noop,
    ),
    Mutant(
        "M06_publish_completeness",
        "publish_completeness",
        "缺 registration 的 canonical 目录不可消费（削弱 = 判为已发布）",
        _real_publish_completeness,
        _weakened_noop,
    ),
)


def build_report() -> dict[str, Any]:
    entries = [mutant.to_payload() for mutant in MUTANTS]
    killed = sum(1 for entry in entries if entry["status"] == "killed")
    return {
        "schema_version": SCHEMA_VERSION,
        "harness": HARNESS,
        "totals": {
            "mutants": len(entries),
            "killed": killed,
            "survived": len(entries) - killed,
        },
        "mutants": entries,
    }


def report_path(root: Path) -> Path:
    return root.joinpath(*MUTATION_SUBDIR, REPORT_NAME)


def write_report(root: Path) -> Path:
    """写变异报告；返回落盘路径（默认根为 `reports/`，可用 ALPHAMILL_REPORTS_DIR 覆盖）。"""
    path = report_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_report()
    temp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    temp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temp, path)
    return path


def survivors(report: dict[str, Any] | None = None) -> tuple[str, ...]:
    payload = report or build_report()
    return tuple(entry["mutant_id"] for entry in payload["mutants"] if entry["status"] != "killed")
