"""`AC-011` / `NFR-005`：扩容后容量与耗时实测证据门禁。

**为什么测的是"记录"而不是现场重跑**：`NFR-005` 要求的是「磁盘占用、单次全量导出
耗时、NAS 备份时长」三类实测值与 6 对基线对照，其中 NAS 备份依赖外部存储与凭据——
按 `docs/SOP.md` 的真实环境测试纪律，外部 NAS 传输不进 pytest 自动化范围（同
`tests/integration/test_f002_schedule_backup.py` 的处理），由执行机手工执行并把实测值
落盘。因此本套件对**落盘的实测记录**做可失败断言，而不是把导出/备份再跑一遍。

**判红阈值**（`docs/reviews/RETROSPECTIVE.md` `capacity-gate-not-quantified` 的裁决）：
「实测显著劣于外推必须报告」必须可断言，故取

- 全量导出耗时 > 外推值 **1.5 倍** → 判不可接受；
- 湖/NAS 分区文件数 > 外推值 **1.3 倍** → 判不可接受。

外推口径按 `NFR-005` 自身的线性缩放：40 对约 25min / 58,800 文件对应 6 对基线
（631 万行 / 全量 3m48s / NAS 8,823 分区文件），即 `基线 × 对数/6`——spec 里 40 对
的三个外推值正是这条公式的结果，故此处沿用同一口径（对数取实测记录里的 `admitted_pairs`）。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "reports" / "f008" / "capacity-report.json"

#: `NFR-005` 的 F002 6 对基线（不要改：spec/design 两处同源）
BASELINE_PAIRS = 6
BASELINE_ROWS = 6_310_000
BASELINE_EXPORT_SECONDS = 228.0  # 3m48s
BASELINE_NAS_FILES = 8_823

#: 回顾裁决的判红倍数
EXPORT_RATIO_MAX = 1.5
FILES_RATIO_MAX = 1.3

_REQUIRED_KEYS = (
    "schema_version",
    "measured_at",
    "hostname",
    "admitted_pairs",
    "lake_bytes",
    "lake_partition_files",
    "export_mode",
    "export_seconds",
    "nas_backup_seconds",
    "nas_file_count",
    "extrapolated",
)


def _require_report() -> dict:
    """读实测记录；缺失时开发机 skip、执行机（`ALPHAMILL_INTEGRATION=1`）判红。"""
    if not REPORT.is_file():
        message = f"容量实测记录缺失：{REPORT.relative_to(REPO)}（T023/T026 产出）"
        if os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}:
            pytest.fail(message)
        pytest.skip(message)
    return json.loads(REPORT.read_text(encoding="utf-8"))


def _extrapolated(pairs: int) -> dict[str, float]:
    scale = pairs / BASELINE_PAIRS
    return {
        "rows": BASELINE_ROWS * scale,
        "export_seconds": BASELINE_EXPORT_SECONDS * scale,
        "nas_files": BASELINE_NAS_FILES * scale,
    }


def test_report_is_complete_and_self_consistent() -> None:
    """记录必须自洽：字段齐全、对数与基线可比、外推值与 NFR-005 口径一致。"""
    report = _require_report()
    missing = [key for key in _REQUIRED_KEYS if key not in report]
    assert not missing, f"容量记录缺字段：{missing}"
    assert report["schema_version"] == 1

    pairs = int(report["admitted_pairs"])
    assert pairs > BASELINE_PAIRS, f"扩容后对数应大于基线 {BASELINE_PAIRS}，实为 {pairs}"
    assert report["hostname"], "记录必须带 hostname（NFR-004：执行机取证）"
    assert report["export_mode"] == "full", "NFR-005 的口径是**单次全量导出**"

    expected = _extrapolated(pairs)
    assert report["extrapolated"] == pytest.approx(expected, rel=0.02), (
        "记录里的外推值必须与 NFR-005 的线性缩放一致"
    )
    assert float(report["export_seconds"]) > 0
    assert int(report["lake_partition_files"]) > 0


def test_full_export_duration_is_within_threshold() -> None:
    """全量导出耗时不得超过外推值的 1.5 倍（回顾裁决的量化判红线）。"""
    report = _require_report()
    extrapolated = float(report["extrapolated"]["export_seconds"])
    measured = float(report["export_seconds"])
    assert measured <= extrapolated * EXPORT_RATIO_MAX, (
        f"全量导出耗时 {measured:.0f}s 超过外推 {extrapolated:.0f}s 的 {EXPORT_RATIO_MAX}×"
        f"（上限 {extrapolated * EXPORT_RATIO_MAX:.0f}s）"
    )


def test_partition_file_count_is_within_threshold() -> None:
    """湖分区文件数与 NAS 文件数都不得超过外推值的 1.3 倍。"""
    report = _require_report()
    extrapolated = float(report["extrapolated"]["nas_files"])

    lake_files = int(report["lake_partition_files"])
    assert lake_files <= extrapolated * FILES_RATIO_MAX, (
        f"湖分区文件数 {lake_files} 超过外推 {extrapolated:.0f} 的 {FILES_RATIO_MAX}×"
    )

    nas_files = int(report["nas_file_count"])
    assert nas_files <= extrapolated * FILES_RATIO_MAX, (
        f"NAS 文件数 {nas_files} 超过外推 {extrapolated:.0f} 的 {FILES_RATIO_MAX}×"
    )


def test_lake_on_execution_machine_matches_recorded_count() -> None:
    """执行机上，湖的**实际**分区文件数必须与记录一致（±5%）——记录不得是手写估值。

    开发机没有生产湖时跳过；执行机上湖存在即必须对齐，否则记录不可信。
    """
    report = _require_report()
    lake = Path(os.getenv("ALPHAMILL_LAKE_DIR", "/home/georg/projects/alphamill/lake"))
    if not lake.is_dir():
        pytest.skip(f"本机无湖目录 {lake}（开发机跳过属预期）")

    actual = sum(1 for _ in lake.rglob("*.parquet"))
    recorded = int(report["lake_partition_files"])
    assert actual == pytest.approx(recorded, rel=0.05), (
        f"实际分区文件数 {actual} 与记录 {recorded} 不一致（记录必须来自实测）"
    )
