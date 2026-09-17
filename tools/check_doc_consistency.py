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
ARCH = "docs/alphamill-architecture.md"
BACKLOG = "BACKLOG.md"
CLAUDE = "CLAUDE.md"
README = "docs/README.md"
F007_DESIGN = "docs/features/0.2/F007-evaluation-gates/design.md"
F007_TASKS = "docs/features/0.2/F007-evaluation-gates/tasks.md"
F004_SPEC = "docs/features/0.2/F004-kronos-inference-runtime/spec.md"
F004_TASKS = "docs/features/0.2/F004-kronos-inference-runtime/tasks.md"


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
    TextCheck(
        "f007_ingests_f003_contracts",
        "F007-D002",
        requires=(
            (F007_DESIGN, "generation.run_completed"),
            (F007_DESIGN, "generation.candidate_rejected"),
            (F007_DESIGN, "算子能力登记表"),
            (F007_TASKS, "generation.candidate_rejected"),
        ),
        forbids=((F007_DESIGN, "related_features: [F002, F004]"),),
    ),
    TextCheck(
        "f007_declares_f008_universe",
        "F007-D003",
        requires=(
            (F007_SPEC, "related_features: [F002, F003, F004, F008]"),
            (F007_SPEC, "universe_at(T)"),
            (F007_SPEC, "F008"),
            (F007_DESIGN, "F008 上游 Contract"),
            (F007_TASKS, "universe_at(T)"),
        ),
    ),
    TextCheck(
        "universe_calendar_artifacts_split",
        "F007-D004",
        requires=(
            (F007_SPEC, "DR-006"),
            (F007_DESIGN, "lake/_metadata/universes/"),
            (F007_DESIGN, "--calendar <path>"),
            (F007_DESIGN, "--universe <digest|ref>"),
        ),
        forbids=(
            (F007_DESIGN, "--universe-calendar"),
            (F007_TASKS, "--universe-calendar"),
        ),
    ),
    TextCheck(
        "no_lookahead_three_layers_owned",
        "F007-D005",
        requires=(
            (F007_SPEC, "FR-007"),
            (F007_SPEC, "独立逐 K 线重放"),
            (F007_SPEC, "信号缓存"),
            (F007_DESIGN, "owner=F006"),
            (F007_TASKS, "三层无前视状态"),
        ),
    ),
    TextCheck(
        "sample_size_three_tiers",
        "F007-D006",
        requires=(
            (F007_SPEC, "sample_tier=underpowered"),
            (F007_SPEC, "provisional"),
            (F007_SPEC, "trustworthy"),
            (F007_DESIGN, "三级（ADR-0003 样本量门槛）"),
            (F007_TASKS, "三级样本量"),
        ),
    ),
    TextCheck(
        "task_graph_missing_edges_f007",
        "F007-D007",
        requires=(
            (F007_TASKS, "`T009 -> T012`"),
            (F007_TASKS, "`T012 -> T013`"),
        ),
    ),
    TextCheck(
        "full_chain_controls_have_predecessors",
        "F007-D008",
        requires=(
            (F007_TASKS, "`T007 -> T010/T011`"),
            (F007_TASKS, "`T012/T014 -> T016`"),
        ),
    ),
    TextCheck(
        "real_env_task_has_distinct_evidence",
        "F007-D009",
        requires=(
            (F007_TASKS, "ALPHAMILL_INTEGRATION=1"),
            (F007_TASKS, "test_f007_controls_real.py"),
            (F007_SPEC, "ALPHAMILL_INTEGRATION=1"),
            (F007_DESIGN, "test_f007_controls_real.py"),
        ),
    ),
    TextCheck(
        "holdout_budget_ledger_exists",
        "F007-D010",
        requires=(
            (F007_SPEC, "**DR-005**：`HoldoutBudgetLedger`"),
            (F007_DESIGN, "holdout_budget/ledger.jsonl"),
            (F007_TASKS, "DR-005"),
            (F007_TASKS, "留出预算台账"),
        ),
    ),
    TextCheck(
        "verdict_vocabulary_frozen",
        "F007-D011",
        requires=(
            (F007_DESIGN, "术语表（冻结"),
            (F007_DESIGN, "promotion_verdict"),
            (F007_DESIGN, "cost_verdict"),
            (F007_SPEC, "promotion_verdict"),
            (F007_SPEC, "两层独立枚举"),
            (F007_TASKS, "术语表"),
        ),
    ),
    TextCheck(
        "sc002_concurrency_has_task",
        "F007-D012",
        requires=(
            (F007_TASKS, "SC-002"),
            (F007_TASKS, "故障注入"),
            (F007_TASKS, "test_f007_concurrency.py"),
            (F007_DESIGN, "SC-002"),
        ),
    ),
    TextCheck(
        "ac003_multi_member_batch",
        "F007-D013",
        requires=(
            (F007_SPEC, "多成员 cohort 批量夹具"),
            (F007_DESIGN, "多成员 cohort 批量 fixture"),
            (F007_TASKS, "多成员 cohort 批量夹具"),
        ),
    ),
    TextCheck(
        "nfr004_approximation_covered",
        "F007-D014",
        requires=(
            (F007_SPEC, "NFR-004"),
            (F007_SPEC, "`approximation`"),
            (F007_DESIGN, "`approximation`"),
            (F007_TASKS, "`approximation`"),
        ),
    ),
    TextCheck(
        "mutation_targets_labels_aligned",
        "F007-D015",
        requires=(
            (F007_TASKS, "变异工具版本 pin"),
            (F007_TASKS, "mutation_report.json"),
            (F007_DESIGN, "mutation_report.json"),
            (F007_TASKS, "`AC-001`, `AC-002`, `AC-003`, `AC-005`"),
        ),
    ),
    TextCheck(
        "second_implementation_has_task",
        "F007-D016",
        requires=(
            (F007_TASKS, "第二实现对照抽查"),
            (F007_TASKS, "time-box 1 周"),
            (F007_TASKS, "test_second_implementation.py"),
            (F007_SPEC, "第二实现抽查"),
        ),
    ),
    TextCheck(
        "f004_to_f007_factor_source_contract",
        "F007-D017",
        requires=(
            (F007_SPEC, "DR-007"),
            (F007_SPEC, "source=placeholder"),
            (F007_DESIGN, "signals_log"),
            (F007_DESIGN, "`source=placeholder` 的处理分层"),
            (F007_TASKS, "placeholder"),
        ),
    ),
    TextCheck(
        "f005_frontend_does_not_bypass_api",
        "F007-D018",
        requires=(
            (F007_DESIGN, "src/alphamill/api/"),
            (F007_DESIGN, "不得成为前端直读路径"),
        ),
    ),
    TextCheck(
        "final_confirmation_window_hidden",
        "F007-D019",
        requires=(
            (F007_SPEC, "**AC-010** (`NFR-003`, `IR-003`)"),
            (F007_SPEC, "最终确认窗"),
            (F007_SPEC, "fail-closed"),
            (F007_DESIGN, "最终确认窗"),
            (F007_TASKS, "最终确认窗"),
        ),
    ),
    TextCheck(
        "stage_ids_and_failure_dimensions_frozen",
        "F007-D021",
        requires=(
            (F007_SPEC, "`signal_quality`"),
            (F007_SPEC, "**AC-012**"),
            (F007_DESIGN, "`execution_implementation`"),
            (F007_DESIGN, "failure_taxonomy"),
            (F007_TASKS, "failure_taxonomy"),
        ),
    ),
    TextCheck(
        "nfr005_ux001_traceable",
        "F007-D022",
        requires=(
            (F007_SPEC, "**AC-011** (`NFR-004`, `NFR-005`, `UX-001`)"),
            (F007_SPEC, "POSIX 逻辑路径"),
            (F007_TASKS, "POSIX 逻辑路径断言"),
            (F007_TASKS, "首个失败原因（快照测试锁定）"),
            (F007_DESIGN, "POSIX"),
        ),
    ),
    TextCheck(
        "design_no_task_directives",
        "F007-D023",
        requires=(
            (F007_DESIGN, "约束的落地形态与执行规则见 `tasks.md`"),
            (F007_TASKS, "编写早"),
            (F007_TASKS, "组（§3）是开发前置门"),
        ),
        forbids=((F007_DESIGN, "开工门禁（SDD Flow T3）会拒绝缺失该组的流转"),),
    ),
    TextCheck(
        "state_vocab_and_bench_mapping_aligned",
        "F007-D024",
        requires=(
            (F007_SPEC, "`evaluation.registered`"),
            (F007_SPEC, "`reports/bench/`"),
            (F007_SPEC, "`PREVIEW_DONE`"),
            (F007_DESIGN, "`reports/bench/`"),
            (F007_DESIGN, "`evaluation.registered`"),
        ),
    ),
    TextCheck(
        "property_strategy_has_execution_task",
        "F007-D025",
        requires=(
            (F007_TASKS, "属性测试轨"),
            (F007_TASKS, "显式策略枚举"),
            (F007_DESIGN, "固定可复现 seed"),
            (F007_DESIGN, "`tests/property/test_f007_identity_properties.py`"),
        ),
    ),
    # ---- F003 文档检视 Round 2 修复断言（finding id 前缀 F003-R2）----
    TextCheck(
        "explicit_binding_splits_universe_calendar",
        "F003-R2-003",
        requires=(
            (DESIGN, '"universe": {"digest"'),
            (DESIGN, '"calendar": {"digest"'),
            (DESIGN, "universe_path"),
            (DESIGN, "calendar_path"),
            (DESIGN, "组合导出"),
        ),
        forbids=((DESIGN, "universe_calendar_path"),),
    ),
    TextCheck(
        "factordef_expression_dto_shape",
        "F003-R2-004",
        requires=(
            (DESIGN, "`expression` 的唯一形态"),
            (DESIGN, "**不新增**"),
            (DESIGN, 'meta["expression"]'),
            (ARCH, "不进入可执行对象顶层"),
        ),
    ),
    TextCheck(
        "factor_registry_owner_declared",
        "F003-R2-005",
        requires=(
            (SPEC, "查重判定与 lifecycle 状态判定"),
            (SPEC, "owner = `F007`"),
            (SPEC, "lifecycle 动作执行"),
            (F007_SPEC, "唯一写入 owner"),
        ),
    ),
    TextCheck(
        "kronos_lifecycle_contract_defined",
        "F003-R2-002",
        requires=(
            (ARCH, "Kronos 服务生命周期契约"),
            (ARCH, "contract_version"),
            (ARCH, "E_UNSUPPORTED_VERSION"),
            (ARCH, "`GET /lifecycle/status`"),
            (DESIGN, "Kronos 生命周期 Contract"),
            (TASKS, "test_f003_kronos_lifecycle.py"),
            (F004_SPEC, "Kronos 服务生命周期控制面"),
            (F004_TASKS, "tests/integration/test_f003_kronos_lifecycle.py"),
        ),
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


TEST_FILE_RE = re.compile(r"tests/[A-Za-z0-9_./-]+\.py")


def check_f007_design_test_map_covers_tasks(root: pathlib.Path) -> list[tuple[str, str]]:
    """F007-D020：tasks 声明的测试文件必须能在 design §8 映射表里找到。

    单向校验（tasks ⊆ design）：design 允许比 tasks 多列后备方案，反之则说明
    tasks 的 verify 载体没有落进设计映射，测试面无人负责。
    """
    errors: list[tuple[str, str]] = []
    design_map = set(TEST_FILE_RE.findall(read(root, F007_DESIGN)))
    for path in sorted(set(TEST_FILE_RE.findall(read(root, F007_TASKS)))):
        if path not in design_map:
            errors.append(
                (
                    "f007_design_test_map_covers_tasks",
                    f"design §8 未映射 tasks 使用的测试文件 {path}",
                )
            )
    return errors


TASK_LINE_RE = re.compile(r"^-\s+\[[ xX]\]\s+(T\d{3})\b(.*)$")
REF_PAREN_RE = re.compile(r"\(([^)]*)\)")
TASK_REF_RE = re.compile(r"\b(?:FR|DR|TR|IR|UX|NFR)-\d+\b|Q-\d+")


def check_no_stale_closed_question_task(root: pathlib.Path) -> list[tuple[str, str]]:
    """F003-R2-006：前置任务不得只引用已关闭的 Q（已关闭问题不是开发前动作）。"""
    errors: list[tuple[str, str]] = []
    closed = {m.group(1) for m in re.finditer(r"^-\s+\[[xX]\]\s+(Q-\d+)", read(root, SPEC), re.M)}
    for line in read(root, TASKS).replace("\r\n", "\n").split("\n"):
        task = TASK_LINE_RE.match(line.strip())
        if not task:
            continue
        paren = REF_PAREN_RE.search(task.group(2))
        if not paren:
            continue
        refs = TASK_REF_RE.findall(paren.group(1))
        if refs and all(ref in closed for ref in refs):
            errors.append(
                (
                    "no_stale_closed_question_task",
                    f"{task.group(1)} 只引用已关闭的 Q（{', '.join(refs)}）",
                )
            )
    return errors


LIFECYCLE_CONTRACT_TEST = "tests/integration/test_f003_kronos_lifecycle.py"


def check_declared_contract_test_carrier(root: pathlib.Path) -> list[tuple[str, str]]:
    """F003-R2-002：文档声明的生命周期契约测试必须真实落盘。

    本轮 finding 的失败模式正是「声明的载体不存在」——fix_summary 宣称由契约测试
    闭合，但文件从未创建。按文件存在性校验，防止再次用不存在的证据收口。
    """
    if not (root / LIFECYCLE_CONTRACT_TEST).is_file():
        return [
            (
                "declared_contract_test_carrier",
                f"声明的契约测试文件不存在：{LIFECYCLE_CONTRACT_TEST}",
            )
        ]
    return []


CUSTOM_CHECKS = (
    check_f007_declares_f003,
    check_ac_body_covers_clauses,
    check_active_feature_indexes,
    check_f007_design_test_map_covers_tasks,
    check_no_stale_closed_question_task,
    check_declared_contract_test_carrier,
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
