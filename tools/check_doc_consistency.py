#!/usr/bin/env python3
"""文档一致性门禁（doc review F003 契约断言回归门）。

把 F003 检视闭环中被修复的每一处契约写成**可红的断言**：要求项缺失、或旧矛盾
文本回归时即判红。每条 check 对应一个 finding id，便于检视方逐条独立核对。

覆盖范围：
  - 声明式文本断言（`TEXT_CHECKS`）：要求/禁止的字面量，按 finding 分组；
  - 解析式断言：F007 是否声明 F003 上游（D014）、AC 断言是否覆盖其引用的子句
    （D017）、活跃 feature 索引三处是否一致（D022）。

用法：python tools/check_doc_consistency.py
退出码 0 = 全部通过；1 = 存在违规。
"""

from __future__ import annotations

import dataclasses
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

SPEC = "docs/features/0.2/F003-alphagen-vendor/spec.md"
DESIGN = "docs/features/0.2/F003-alphagen-vendor/design.md"
TASKS = "docs/features/0.2/F003-alphagen-vendor/tasks.md"
F007_SPEC = "docs/features/0.2/F007-evaluation-gates/spec.md"
F007_DESIGN = "docs/features/0.2/F007-evaluation-gates/design.md"
F007_TASKS = "docs/features/0.2/F007-evaluation-gates/tasks.md"


@dataclasses.dataclass(frozen=True)
class TextCheck:
    check_id: str
    finding: str
    requires: tuple[tuple[str, str], ...] = ()
    forbids: tuple[tuple[str, str], ...] = ()


TEXT_CHECKS: tuple[TextCheck, ...] = (
    TextCheck(
        "factor_id_no_run_seq",
        "F003-D001",
        requires=(
            (DESIGN, "factor_id = <generator>_<definition_digest[:12]>"),
            (SPEC, "不含 run 序号"),
        ),
        forbids=((DESIGN, "run_seq"), (DESIGN, "_r<run_seq>")),
    ),
    TextCheck(
        "terminal_run_facts",
        "F003-D002",
        requires=(
            (DESIGN, "四种终态"),
            (DESIGN, "只有 `status=completed` 的运行可被下游消费"),
            (SPEC, "写终态 run.json"),
        ),
        forbids=((DESIGN, "run.json 不写出"), (DESIGN, "原因入日志")),
    ),
    TextCheck(
        "tier_ladder_matches_adr0001",
        "F003-D003",
        requires=((SPEC, "L1→L2 不在 time-box 内"), (SPEC, "L1 连续 2 周")),
        forbids=((SPEC, "降级到 L1/L2"), (SPEC, "四条判据")),
    ),
    TextCheck(
        "smoke_obligations_linked",
        "F003-D004",
        requires=(
            (SPEC, "not_yet_available"),
            (SPEC, "奖励频率维度抽查"),
            (TASKS, "not_yet_available"),
        ),
    ),
    TextCheck(
        "explicit_tuple_fields_match_adr0007",
        "F003-D005",
        requires=(
            (DESIGN, '"mode": "explicit_tuples"'),
            (DESIGN, "as_of_fidelity"),
            (DESIGN, "universe_calendar_digest"),
            (DESIGN, "provenance"),
            (DESIGN, "created_at"),
        ),
        forbids=((DESIGN, "[{dataset, data_version, value_digest}]"),),
    ),
    TextCheck(
        "pit_mask_depends_on_f008",
        "F003-D006",
        requires=((DESIGN, "universe_at(T)"), (SPEC, "universe_at(T)")),
    ),
    TextCheck(
        "egress_claim_matches_guard_strength",
        "F003-D007",
        requires=((SPEC, "进程级"), (DESIGN, "不等于内核级网络隔离")),
        forbids=((SPEC, "生成运行在无网络出口下完成"),),
    ),
    TextCheck(
        "sigterm_not_completed",
        "F003-D008",
        requires=((DESIGN, "status=partial"), (DESIGN, "不发")),
        forbids=((DESIGN, "status=completed` + `termination=early"),),
    ),
    TextCheck(
        "objective_includes_after_cost",
        "F003-D009",
        requires=((DESIGN, "min_after_cost_return"), (SPEC, "成本后收益")),
    ),
    TextCheck(
        "pool_is_executable_factordef",
        "F003-D010",
        requires=(
            (DESIGN, 'generator="pool"'),
            (SPEC, 'generator="pool"'),
        ),
        forbids=((DESIGN, "AlphaPoolDef**："), (DESIGN, "pool_id"), (SPEC, "pool_id")),
    ),
    TextCheck(
        "gpu_schedule_protocol_and_owner",
        "F003-D013",
        requires=(
            (DESIGN, "queue_seq"),
            (DESIGN, "kronos_offload"),
            (SPEC, "queue_timeout"),
            (TASKS, "live owner = F003"),
        ),
    ),
    TextCheck(
        "factordef_dto_matches_architecture",
        "F003-D015",
        requires=((DESIGN, "加载契约（可执行恢复）"), (DESIGN, "factor_store.load()")),
    ),
    TextCheck(
        "ir003_schema_version_has_carrier",
        "F003-D016",
        requires=(
            (DESIGN, "**GenerationRun**：`schema_version`"),
            (SPEC, "AC-012"),
            (SPEC, "IR-003"),
            (TASKS, "schema_version"),
        ),
    ),
    TextCheck(
        "reproducibility_config_digest",
        "F003-D018",
        requires=(
            (DESIGN, "canonical config artifact"),
            (DESIGN, "config_digest"),
            (SPEC, "config_digest"),
        ),
    ),
    TextCheck(
        "cli_builds_generation_request",
        "F003-D019",
        requires=((DESIGN, "强制字段的构造"), (DESIGN, "--window"), (DESIGN, "--config")),
    ),
    TextCheck(
        "hypothesis_has_applicable_state",
        "F003-D020",
        requires=((DESIGN, "applicable_state"), (SPEC, "applicable_state")),
    ),
    TextCheck(
        "vendor_hygiene_has_upstream_baseline",
        "F003-D021",
        requires=((SPEC, "上游基线"), (TASKS, "_upstream_baseline.json")),
    ),
    # ---- F007 文档检视 Round 1 修复断言（finding id 前缀 F007-D）----
    TextCheck(
        "f007_test_group_present",
        "F007-D001",
        requires=(
            (F007_TASKS, "### [TEST] 组：层 2 旅程验收轨"),
            (F007_TASKS, "T027 [TEST]"),
            (F007_TASKS, "T029 [TEST]"),
            (F007_TASKS, "T030: 回写 spec"),
        ),
        forbids=((F007_TASKS, "- [ ] T024: 回写 spec"),),
    ),
)

AC_LINE_RE = re.compile(r"^-\s+\[[ xX]\]\s+\*\*AC-(\d+)\*\*\s*\(([^)]*)\)\s*:\s*(.*)$")
AC_BODY_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "003": ("DR-001 运行字段",),
    "005": ("可按 run 查询",),
    "009": ("DR-002", "DR-003", "TR-001", "池成员"),
    "010": ("hostname", "queue_seq"),
    "011": ("cli_contract",),
}
AC_FINDING = "F003-D017"

FEATURE_DIR_RE = re.compile(r"^F\d{3}-")
CLAUDE_ACTIVE_RE = re.compile(r"^-\s+(F\d{3})\b")
README_ACTIVE_RE = re.compile(r"当前\s*((?:F\d{3}\s*/\s*)+F\d{3})")
BACKLOG_ROW_RE = re.compile(r"^\|\s*(F\d{3}-[^|]+)\s*\|")


def read(root: pathlib.Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict:
    norm = text.replace("\r\n", "\n")
    m = re.match(r"^---\n([\s\S]*?)\n---", norm)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).split("\n"):
        kv = re.match(r"^([A-Za-z_]\w*):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return fm


def check_text_checks(root: pathlib.Path) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    cache: dict[str, str] = {}
    for chk in TEXT_CHECKS:
        for rel, needle in chk.requires:
            cache.setdefault(rel, read(root, rel))
            if needle not in cache[rel]:
                errors.append((chk.check_id, f"缺少要求文本 {needle!r}（{rel}）"))
        for rel, needle in chk.forbids:
            cache.setdefault(rel, read(root, rel))
            if needle in cache[rel]:
                errors.append((chk.check_id, f"出现已废弃文本 {needle!r}（{rel}）"))
    return errors


def active_features(root: pathlib.Path) -> dict[str, str]:
    """非 done feature 目录名 → id。"""
    out: dict[str, str] = {}
    features_dir = root / "docs" / "features"
    if not features_dir.is_dir():
        return out
    for ver in features_dir.iterdir():
        if not ver.is_dir() or ver.name in ("TEMPLATE", "releases"):
            continue
        for f in ver.iterdir():
            if not f.is_dir() or not FEATURE_DIR_RE.match(f.name):
                continue
            spec = f / "spec.md"
            if not spec.is_file():
                continue
            if parse_frontmatter(spec.read_text(encoding="utf-8")).get("status") != "done":
                out[f.name] = f.name[:4]
    return out


def check_f007_declares_f003(root: pathlib.Path) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    text = read(root, F007_SPEC)
    fm = parse_frontmatter(text)
    related = fm.get("related_features", "")
    if not re.search(r"\bF003\b", related):
        errors.append(("f007_declares_f003_upstream", "F007 related_features 未声明 F003"))
    if "**F003**" not in text:
        errors.append(("f007_declares_f003_upstream", "F007 上游 Contract 未显式列出 F003"))
    return errors


def check_ac_body_covers_clauses(root: pathlib.Path) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    bodies: dict[str, str] = {}
    for line in read(root, SPEC).replace("\r\n", "\n").split("\n"):
        m = AC_LINE_RE.match(line.strip())
        if m:
            bodies[m.group(1)] = m.group(3)
    for ac_num, needles in AC_BODY_REQUIREMENTS.items():
        body = bodies.get(ac_num)
        if body is None:
            errors.append((AC_FINDING, f"spec 未找到 AC-{ac_num}"))
            continue
        for needle in needles:
            if needle not in body:
                errors.append((AC_FINDING, f"AC-{ac_num} 断言未覆盖其引用的子句 {needle!r}"))
    return errors


def check_active_feature_indexes(root: pathlib.Path) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    expected = set(active_features(root))

    backlog_rows: set[str] = set()
    for line in read(root, "BACKLOG.md").replace("\r\n", "\n").split("\n"):
        if line.lstrip().startswith("## "):
            break
        m = BACKLOG_ROW_RE.match(line.strip())
        if m:
            backlog_rows.add(m.group(1).strip())
    if backlog_rows != expected:
        errors.append(
            (
                "active_feature_indexes_aligned",
                f"BACKLOG 活跃集合 {sorted(backlog_rows)} != 非 done 集合 {sorted(expected)}",
            )
        )

    claude = read(root, "CLAUDE.md").replace("\r\n", "\n")
    section = claude.split("## 当前活跃 Feature", 1)[-1]
    claude_ids = {
        m.group(1) for m in (CLAUDE_ACTIVE_RE.match(ln.strip()) for ln in section.split("\n")) if m
    }
    expected_ids = {name[:4] for name in expected}
    if claude_ids != expected_ids:
        errors.append(
            (
                "active_feature_indexes_aligned",
                f"CLAUDE 活跃集合 {sorted(claude_ids)} != 非 done 集合 {sorted(expected_ids)}",
            )
        )

    readme = read(root, "docs/README.md")
    m = README_ACTIVE_RE.search(readme)
    readme_ids = set(re.findall(r"F\d{3}", m.group(1))) if m else set()
    if readme_ids != expected_ids:
        errors.append(
            (
                "active_feature_indexes_aligned",
                f"docs/README 活跃集合 {sorted(readme_ids)} != 非 done 集合 {sorted(expected_ids)}",
            )
        )
    return errors


CUSTOM_CHECKS = (
    check_f007_declares_f003,
    check_ac_body_covers_clauses,
    check_active_feature_indexes,
)


def run_checks(root: pathlib.Path = ROOT) -> list[tuple[str, str]]:
    errors = check_text_checks(root)
    for fn in CUSTOM_CHECKS:
        errors.extend(fn(root))
    return errors


def main() -> int:
    errors = run_checks()
    if not errors:
        print("check_doc_consistency: 全部通过")
        return 0
    print("check_doc_consistency: 失败", file=sys.stderr)
    for check_id, msg in errors:
        print(f"  - [{check_id}] {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
