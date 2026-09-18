#!/usr/bin/env python3
"""文档一致性门禁（doc review F003 契约断言回归门）。

把 F003 检视闭环中被修复的每一处契约写成**可红的断言**：要求项缺失、或旧矛盾
文本回归时即判红。每条 check 对应一个 finding id，便于检视方逐条独立核对。

覆盖范围：
  - 声明式文本断言（`TEXT_CHECKS`）：要求/禁止的字面量，按 finding 分组；
  - 解析式断言：F007 是否声明 F003 上游（D014）、AC 断言是否覆盖其引用的子句
    （D017）、活跃 feature 索引三处是否一致（D022）、三件套测试文件引用的存在性
    与白名单台账（R2-002/R4-005）。

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
TEST_LIFECYCLE = "tests/integration/test_f003_kronos_lifecycle.py"

# F003-R5-002/R6-001：404 回落探测的规范子句，AC-010 / design / T025 逐字共用。
OFFLOAD_FALLBACK_CLAUSE = (
    "404/`E_UNSUPPORTED_VERSION` 回落探测：`/health.device=cpu` 或设备侧 `memory.used` "
    "低于阈值 → `offload_not_needed`；达到阈值或读数不可得 → fail-closed（不依赖 GPU 进程列表）"
)
ADR7 = "docs/decisions/0007-research-snapshot-binding.md"


@dataclasses.dataclass(frozen=True)
class TextCheck:
    check_id: str
    finding: str
    requires: tuple[tuple[str, str], ...] = ()
    forbids: tuple[tuple[str, str], ...] = ()


TEXT_CHECKS: tuple[TextCheck, ...] = (
    TextCheck(
        "architecture_universe_calendar_split_aligned",
        "F007-D045",
        requires=(
            (ARCH, '"universe_digest"'),
            (ARCH, '"calendar_digest"'),
            (ARCH, "lake/_metadata/universes/<digest>.csv"),
            (ARCH, 'sha256(canonical_json({"universe": <universe_digest>,'),
            (ARCH, '"calendar": <calendar_digest>}))'),
            (ARCH, "`universe_path` / `calendar_path`"),
        ),
        forbids=((ARCH, "显式 universe/calendar JSON 由构造器规范化后保存于"),),
    ),
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
            (F007_TASKS, "T029 [TEST]"),
            (F007_TASKS, "T031 [TEST]"),
            (F007_TASKS, "T032: 回写 spec"),
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
            # R2 批注（D003 保持 open 的证据）：design 只钉正文字样漏掉了 frontmatter，
            # 现在两侧都钉。
            (F007_DESIGN, "related_features: [F002, F003, F004, F008]"),
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
            (F007_DESIGN, "三级（ADR-0003 样本量门槛；半开区间"),
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
            # F007-D028（operator 裁决#1）拆分后：摘要回写+查重归 F007，
            # lifecycle 状态判定 v0.2 无 owner、后移 M3/F006。
            (SPEC, "评测摘要回写与 `|ρ|`"),
            (SPEC, "owner = `F007`"),
            (SPEC, "lifecycle 状态判定** v0.2 无 owner"),
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
            # R4-002：契约目标是真实推理服务，不是 mock（mock 无 GPU 显存可释放）。
            (ARCH, "真实推理服务 `kronos-signal-real`"),
            # R4-003：status 行错误码必须含 E_UNSUPPORTED_VERSION（wire 绑定对所有
            # 动作生效，契约测试正是打 GET /lifecycle/status 做版本拒绝）。
            (ARCH, "`E_UNAVAILABLE` / `E_UNSUPPORTED_VERSION`"),
            (DESIGN, "Kronos 生命周期 Contract"),
            (TASKS, "test_f003_kronos_lifecycle.py"),
            (F004_SPEC, "Kronos 服务生命周期控制面"),
            (F004_TASKS, "tests/integration/test_f003_kronos_lifecycle.py"),
        ),
    ),
    TextCheck(
        "kronos_offload_classification_defined",
        "F003-R4-004",
        requires=(
            # 架构侧决策表本体由解析式检查 check_offload_decision_table 逐行锁定（R4-004）。
            (ARCH, "观测 → 处置决策表"),
            # 客户端侧：AC-010 验收、design 客户端契约、T025 单测断言；404 回落探测判据
            # 三处用同一规范子句（R5-002 裁决#3 + R6-001），片段级改写即判红。
            (SPEC, "观测→处置决策表记 `offload_not_needed`"),
            (SPEC, OFFLOAD_FALLBACK_CLAUSE),
            (DESIGN, "逐行实现并在单测中断言"),
            (DESIGN, OFFLOAD_FALLBACK_CLAUSE),
            (TASKS, "观测→处置决策表逐行断言"),
            (TASKS, OFFLOAD_FALLBACK_CLAUSE),
            (TASKS, "进程列表为空但 `memory.used` 达到阈值 → fail-closed"),
        ),
        forbids=(
            # 旧的无判定方法表述（「确未部署」没有操作化定义）不得回归。
            (ARCH, "控制面不可达且该服务确实未部署"),
            (DESIGN, "服务确未部署记 `offload_not_needed`"),
            # R5-001：mock 探测括注（决策表推不出来）不得回归。
            (ARCH, "对其探测按下方决策表归"),
            # R6-001：WSL2 下 nvidia-smi 不列 GPU 进程，进程判据恒真，不得回归。
            (ARCH, "卡上无 Kronos 进程"),
            (SPEC, "卡上无 Kronos 进程"),
            (DESIGN, "卡上无 Kronos 进程"),
            (TASKS, "卡上无 Kronos 进程"),
        ),
    ),
    TextCheck(
        "kronos_t033_zero_xfail_gate",
        "F003-R4-001",
        requires=(
            # T033 的 0 xfailed 硬要求与机器门禁参数（--runxfail 使先红态按真失败计）。
            (TASKS, "必须以 **0 xfailed** 通过"),
            # R4-001：钉命令整串，避免被说明文字里的同名串满足。
            (TASKS, "pytest -q --runxfail tests/integration/test_f003_generation_run.py"),
            (TASKS, "KRONOS_CONTROL_URL=http://127.0.0.1:8002"),
            # 端点 feature -> T033 前置边。
            (TASKS, "BACKLOG「Kronos 服务生命周期端点」feature 落地并部署于执行机 -> T033"),
            # BACKLOG 行不得回退为「F003 开工前落地」矛盾表述。
            (BACKLOG, "T033 要求 `test_f003_kronos_lifecycle.py` 以 0 xfailed 通过"),
        ),
        forbids=((BACKLOG, "F003 开工前落地"),),
    ),
    TextCheck(
        "lifecycle_test_no_mock_default",
        "F003-R4-002",
        requires=(
            # 契约测试模块：URL 必须显式（无默认值），缺失即 skip；
            # 配套行为单测 tests/unit/test_f003_lifecycle_contract_config.py。
            (TEST_LIFECYCLE, 'os.getenv("KRONOS_CONTROL_URL", "")'),
            (TEST_LIFECYCLE, "必须显式指定"),
        ),
        forbids=((TEST_LIFECYCLE, "127.0.0.1:8001"),),
    ),
    TextCheck(
        "kronos_owner_wording_unified",
        "F003-R5-003",
        requires=(
            (DESIGN, "经**架构 §7.1 服务生命周期契约**"),
            (SPEC, "经架构 §7.1 服务生命周期契约"),
        ),
        forbids=(
            (DESIGN, "经 F004 交付的服务生命周期"),
            (SPEC, "经 F004 交付的容器编排控制"),
        ),
    ),
    # ---- F007 文档检视 Round 2 修复断言（finding id 前缀 F007-D026..D040）----
    TextCheck(
        "adr0007_universe_calendar_split_aligned",
        "F007-D030",
        requires=(
            (ADR7, "universe_path"),
            (ADR7, "calendar_path"),
            (ADR7, 'sha256(canonical_json({"universe"'),
            (F007_SPEC, 'sha256(canonical_json({"universe"'),
            (F007_DESIGN, 'sha256(canonical_json({"universe"'),
            (DESIGN, "sha256(canonical_json"),
            (DESIGN, "冻结公式"),
        ),
        forbids=(
            (ADR7, "universe_calendar_path"),
            (DESIGN, "<combine(universe.digest, calendar.digest)>"),
        ),
    ),
    TextCheck(
        "sample_tier_boundaries_frozen",
        "F007-D031",
        requires=(
            (F007_SPEC, "`[0, 30)`"),
            (F007_SPEC, "`[30, 69)`"),
            (F007_SPEC, "`[69, ∞)`"),
            (F007_SPEC, "`sample_unit`"),
            (F007_SPEC, "29/30/68/69"),
            (F007_DESIGN, "`[0, 30)`"),
            (F007_DESIGN, "`[30, 69)`"),
            (F007_DESIGN, "`[69, ∞)`"),
            (F007_DESIGN, "导出优先级"),
        ),
        forbids=(
            (F007_SPEC, "≈≥69"),
            (F007_SPEC, "`<30`"),
            (F007_SPEC, "`30~69`"),
            (F007_DESIGN, "≈≥69"),
        ),
    ),
    TextCheck(
        "holdout_ledger_writer_deferred",
        "F007-D032",
        requires=(
            (F007_SPEC, "**v0.2 写入者边界**"),
            (F007_SPEC, "追加写入者后移 FR4/M3"),
            (F007_SPEC, "`holdout_window`"),
            (F007_SPEC, "`regime`"),
            (F007_DESIGN, "v0.2 无追加写入者"),
            (F007_DESIGN, "周度 top-k 配额"),
            (F007_TASKS, "留出预算台账的追加写入者"),
        ),
    ),
    TextCheck(
        "second_impl_tolerance_by_estimator",
        "F007-D034",
        requires=(
            (F007_TASKS, "确定性量（BH-FDR 临界值、HAC 稳健 SE）相对差 ≤1e-6"),
            (F007_TASKS, "固定 seed 同实现复算一致"),
            (F007_TASKS, "test_f007_second_impl_vibe.py"),
            (F007_DESIGN, "第二实现对照（本仓）"),
            (F007_DESIGN, "第二实现对照（外部）"),
            (F007_DESIGN, "test_f007_second_impl_vibe.py"),
        ),
        forbids=((F007_TASKS, "估计量相对差 ≤1e-6"),),
    ),
    TextCheck(
        "deferred_owner_has_carrier",
        "F007-D036",
        requires=(
            (BACKLOG, "无前视 L2（逐 K 线重放）"),
            (BACKLOG, "lifecycle 状态判定"),
            (F007_TASKS, "无前视 L2（独立逐 K 线重放审计）与 L3"),
            (F007_TASKS, "BACKLOG「规划中」行已登记"),
        ),
    ),
    TextCheck(
        "code_digest_runner_computed",
        "F007-D037",
        requires=(
            (F007_SPEC, "只作**期望值**"),
            (F007_SPEC, "工作树脏时拒绝 canonical"),
            (F007_SPEC, "`E_INPUT_INVALID`"),
            (F007_DESIGN, "只作**期望值**"),
            (F007_DESIGN, "回退 git tree"),
            (F007_DESIGN, "不接受调用方自报值"),
        ),
    ),
    TextCheck(
        "cost_model_version_published",
        "F007-D038",
        requires=(
            (F007_DESIGN, "对外即 **`cost_model_version`**"),
            (F007_DESIGN, "F003 只读消费"),
            (F007_SPEC, "`cost_model_version`"),
        ),
    ),
    TextCheck(
        "evidence_dirs_in_design_tree",
        "F007-D040",
        requires=(
            (F007_DESIGN, "f007/real_env/<run_id>/"),
            (F007_DESIGN, "mutation/f007/mutation_report.json"),
            (F007_DESIGN, "property/f007/<seed>/"),
            (F007_DESIGN, "second_impl/<experiment_id>/"),
            (F007_DESIGN, "开发期证据"),
        ),
    ),
    TextCheck(
        "f007_requirement_refs_disambiguated",
        "F007-D039",
        requires=(
            (F007_SPEC, "F008 `IR-003`"),
            (F007_TASKS, "`AC-012`, `AC-013`"),
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


TEST_REF_RE = re.compile(r"tests/[A-Za-z0-9_/.-]+\.py")

# F003-R4-005：三件套声明了但尚未落盘的测试文件白名单（载体台账）。
# 条目 = 文件路径 → 首个声明它的未开工任务。文件落盘后必须移除条目（转为存在性
# 校验，防止过期豁免把「删除已落盘载体」盖住）；引用未登记的幽灵文件同样判红。
DECLARED_TEST_ALLOWLIST: dict[str, str] = {
    "tests/integration/test_f003_alpha_pool.py": "T026",
    "tests/integration/test_f003_generation_run.py": "T028",
    "tests/integration/test_f003_lake_tensor.py": "T020",
    "tests/integration/test_f003_smoke_gate.py": "T016",
    "tests/unit/test_f003_alphagen_adapter.py": "T021",
    "tests/unit/test_f003_gpu_slot.py": "T004",
    "tests/unit/test_f003_ic_parity.py": "T018",
    "tests/unit/test_f003_objective.py": "T024",
    "tests/unit/test_f003_operator_registry.py": "T022",
    "tests/unit/test_f003_vendor_hygiene.py": "T013",
}


# F003-R4-004/R6-001：架构 §7.1「观测 → 处置决策表」的期望内容（逐行、按序）。
# 片段级 require 连续两轮锁不住行级改写，因此改为解析整张表逐格比对；
# 改表必须同步改这里，这正是有意的摩擦。
OFFLOAD_TABLE_ANCHOR = "**观测 → 处置决策表**"
EXPECTED_OFFLOAD_TABLE: tuple[tuple[str, str, str], ...] = (
    (
        "连接拒绝，且部署清单中无该服务",
        "确未部署",
        "记 `offload_not_needed`，继续夜槽",
    ),
    (
        "`status` 可达且 `device=cpu`（非 GPU 实例）",
        "无显存可释放",
        "记 `offload_not_needed`，继续夜槽",
    ),
    (
        "HTTP 404 / `E_UNSUPPORTED_VERSION`",
        "端点未实现，**回落探测** `/health` 的 `device` 与设备侧显存读数"
        "（`nvidia-smi --query-gpu=memory.used`），**不依赖 GPU 进程列表**"
        "（WSL2 下 `nvidia-smi` 不列出 GPU 进程）",
        "`/health.device=cpu`，或设备侧 `memory.used` 低于可配阈值 "
        "`kronos_vram_idle_threshold` → 记 `offload_not_needed`"
        "（`reason=endpoint_absent_no_gpu_tenant`，读数写入 `kronos_offload`），继续夜槽；"
        "`memory.used` 达到阈值或任一读数不可得 → **fail-closed** 留在单槽队列",
    ),
    (
        "`stop` 返回 `E_BUSY` / `E_TIMEOUT`，或 `status.vram_bytes` 确认未释放",
        "停止失败",
        "**fail-closed** 留在单槽队列",
    ),
    (
        "控制面不可达（连接拒绝/超时），但部署清单中存在该服务",
        "状态未知",
        "**fail-closed** 留在单槽队列",
    ),
)


def parse_offload_table(text: str) -> list[tuple[str, ...]] | None:
    """取锚点之后第一张 Markdown 表的数据行（跳过表头与分隔行）；无锚点返回 None。"""
    idx = text.find(OFFLOAD_TABLE_ANCHOR)
    if idx < 0:
        return None
    rows: list[tuple[str, ...]] = []
    started = False
    for line in text[idx:].splitlines()[1:]:
        s = line.strip()
        if s.startswith("|"):
            started = True
            rows.append(tuple(c.strip() for c in s.strip("|").split("|")))
        elif started:
            break
    return rows[2:]  # 去掉表头与 |---| 分隔行


def check_offload_decision_table(root: pathlib.Path) -> list[tuple[str, str]]:
    """F003-R4-004：夜槽卸载决策表逐行逐格与期望一致（增删改行、改处置均判红）。"""
    check_id = "offload_decision_table_rows"
    rows = parse_offload_table(read(root, ARCH))
    if rows is None:
        return [(check_id, f"{ARCH} 缺少锚点 {OFFLOAD_TABLE_ANCHOR}")]
    expected = [tuple(r) for r in EXPECTED_OFFLOAD_TABLE]
    if rows == expected:
        return []
    errors: list[tuple[str, str]] = []
    if len(rows) != len(expected):
        errors.append((check_id, f"决策表行数 {len(rows)} ≠ 期望 {len(expected)}"))
    for i, (got, want) in enumerate(zip(rows, expected, strict=False), start=1):
        if got != want:
            errors.append((check_id, f"决策表第 {i} 行与期望不一致：{' | '.join(got)[:80]}"))
    return errors


def check_declared_test_carriers(root: pathlib.Path) -> list[tuple[str, str]]:
    """F003-R2-002/R4-005：三件套引用的测试文件必须落盘，未开工的须显式登记白名单。

    「声明的载体不存在」正是 Round 3/4 的失败模式——fix_summary 宣称由契约测试
    闭合，但文件从未创建。本检查扫描 spec/design/tasks 中全部 `tests/**.py` 引用：
    文件必须存在，或在 `DECLARED_TEST_ALLOWLIST` 显式登记（附首个声明任务）。
    """
    check_id = "declared_test_carrier_exists"
    errors: list[tuple[str, str]] = []
    refs: set[str] = set()
    for rel in (SPEC, DESIGN, TASKS):
        refs.update(TEST_REF_RE.findall(read(root, rel)))
    for path in sorted(refs):
        if (root / path).is_file():
            if path in DECLARED_TEST_ALLOWLIST:
                errors.append((check_id, f"白名单条目已落盘，请移除以纳入存在性校验：{path}"))
            continue
        if path in DECLARED_TEST_ALLOWLIST:
            continue
        errors.append((check_id, f"引用的测试文件不存在且未登记白名单：{path}"))
    # R5-004：文档已不再引用的白名单条目必须移除，过期豁免不得静默残留。
    for path in sorted(DECLARED_TEST_ALLOWLIST):
        if path not in refs:
            errors.append((check_id, f"白名单条目未被三件套引用（孤儿条目，请移除）：{path}"))
    return errors


# ---- F007 Round 2 解析式门禁（D026/D027/D028/D029/D035/D039：结构闭合，非子串存在）----
# 动因：TEXT_CHECKS 的子串针脚只能证明「文字没被删」，D026/D027/D029 在全部门禁绿的情况下
# 仍然成立（见 CURRENT-doc-F007.md Round 2 变异核对）。这一组改为解析文档结构后断言闭合性。


def _md_section(text: str, title: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    start = None
    for i, line in enumerate(lines):
        m = re.match(r"^##\s+(.+)$", line)
        if m and m.group(1).strip() == title:
            start = i + 1
            break
    if start is None:
        return ""
    body: list[str] = []
    for line in lines[start:]:
        if re.match(r"^##\s", line):
            break
        body.append(line)
    return "\n".join(body)


def _fenced_text_block(section_text: str) -> str:
    m = re.search(r"```text\n([\s\S]*?)```", section_text)
    return m.group(1) if m else ""


F007_LIFECYCLE_STATES = {
    "CREATED",
    "VALIDATING",
    "RUNNING",
    "EVIDENCE_READY",
    "REJECTED",
    "INCOMPLETE",
    "REGISTERED",
    "PREVIEW_DONE",
    "OPEN",
    "FINALIZED",
}
LIFECYCLE_TRANSITION_RE = re.compile(r"^\s*(?:\w+ )?([A-Z][A-Z_]+)\s*->\s*([A-Z][A-Z_]+)", re.M)


def check_f007_lifecycle_closure(root: pathlib.Path) -> list[tuple[str, str]]:
    """F007-D026：生命周期状态机闭合——失败成员必须有终态登记路径。

    解析 spec §5 的 text 代码块为迁移边，校验：状态都在冻结枚举内；REJECTED /
    INCOMPLETE 都能到达 REGISTERED；finalize 条件写明「全部终态且已 REGISTERED」；
    INCOMPLETE 的终态条件（重试上限/显式 abandon）有定义。
    """
    check_id = "f007_lifecycle_closure"
    block = _fenced_text_block(_md_section(read(root, F007_SPEC), "5. 生命周期与不变量"))
    if not block:
        return [(check_id, "spec §5 未找到生命周期 text 代码块")]
    errors: list[tuple[str, str]] = []
    edge_set: set[tuple[str, str]] = set()
    for m in LIFECYCLE_TRANSITION_RE.finditer(block):
        src, dst = m.group(1), m.group(2)
        edge_set.add((src, dst))
        for state in (src, dst):
            if state not in F007_LIFECYCLE_STATES:
                errors.append((check_id, f"未知生命周期状态 {state!r}（枚举外取值）"))
    for need, why in (
        (("CREATED", "INCOMPLETE"), "身份/输入不可解析缺少失败路径"),
        (("VALIDATING", "REJECTED"), "方法论门失败缺少 REJECTED 终态路径"),
        (("VALIDATING", "INCOMPLETE"), "snapshot/输入校验失败缺少可重试路径"),
        (("RUNNING", "REJECTED"), "运行时守卫拒绝缺少 REJECTED 终态路径"),
        (("REJECTED", "REGISTERED"), "拒绝成员缺少终态登记路径（cohort 将无法 finalize）"),
        (("INCOMPLETE", "VALIDATING"), "INCOMPLETE 缺少重试路径"),
        (("INCOMPLETE", "REGISTERED"), "INCOMPLETE 终态缺少登记路径"),
    ):
        if need not in edge_set:
            errors.append((check_id, f"缺少迁移 {need[0]} -> {need[1]}：{why}"))
    finalize = " ".join(ln for ln in block.split("\n") if "OPEN -> FINALIZED" in ln)
    if "REGISTERED" not in finalize:
        errors.append((check_id, "finalize 条件未写明「全部终态且已 REGISTERED」"))
    if "重试上限" not in block or "abandon" not in block:
        errors.append((check_id, "INCOMPLETE 终态条件未定义（重试上限/显式 abandon）"))
    # D044：design §7 的每条失败映射都必须落在 spec §5 的迁移上，且 abandon 必须有 CLI 入口。
    mapping = _md_section(read(root, F007_DESIGN), "7. 失败、恢复、安全与兼容")
    for src, dst in set(LIFECYCLE_TRANSITION_RE.findall(mapping)):
        if (src, dst) not in edge_set:
            errors.append(
                (check_id, f"design §7 失败映射 {src} -> {dst} 在 spec §5 状态机中没有对应迁移")
            )
    if "abandon" not in read(root, F007_SPEC).split("## 5.")[0]:
        errors.append((check_id, "spec §4 IR-001 未提供 abandon 入口（INCOMPLETE 终态无法收口）"))
    if "alphamill.evaluation abandon" not in read(root, F007_DESIGN):
        errors.append((check_id, "design §4 CLI 契约缺 abandon 子命令"))
    return errors


# D041/D043：枚举不再硬编码在门禁里（硬编码把「旧答案」当成正确答案，Round 3 因此漏检
# 优先级表输出 provisional 而枚举没有它）。这里只锁两条不变量：枚举 == 优先级表输出集合、
# spec FR-005 的优先级串 == 表的行序；另加 D027 的必须取值 blocked_pending_audit。
F007_PROMOTION_REQUIRED = {"blocked_pending_audit"}
UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")


def _split_md_row(line: str) -> list[str]:
    r"""按未转义的 `|` 切分表格行；`\|`（如 `\|ρ\|`）是单元格内容，不是分隔符。"""
    return [c.strip() for c in UNESCAPED_PIPE_RE.split(line.strip())[1:-1]]


def _f007_promotion_priority_rows(design: str) -> list[tuple[int, str, str]]:
    section = _md_section(design, "3. 数据模型与 Migration")
    anchor = section.find("导出优先级")
    if anchor < 0:
        return []
    rows = []
    for line in section[anchor:].split("\n"):
        if not line.strip().startswith("|"):
            if rows:
                break
            continue
        cells = _split_md_row(line)
        if len(cells) != 3 or not cells[0].isdigit():
            continue
        values = re.findall(r"`([a-z_]+)`", cells[2])
        if values:
            rows.append((int(cells[0]), cells[1], values[0]))
    return rows


def check_f007_promotion_blocked_state_defined(root: pathlib.Path) -> list[tuple[str, str]]:
    """F007-D027/D041/D043：promotion_verdict 枚举、优先级表与 spec 顺序三者闭合（解析式）。"""
    check_id = "f007_promotion_blocked_state_defined"
    errors: list[tuple[str, str]] = []
    design = read(root, F007_DESIGN)
    spec = read(root, F007_SPEC)
    enums: set[str] = set()
    m = re.search(r"\|\s*成员晋升裁决\s*\|\s*`promotion_verdict`\s*\|((?:[^|\\]|\\\|)+)\|", design)
    if not m:
        errors.append((check_id, "design §3.3 术语表缺 promotion_verdict 枚举行"))
    else:
        enums = {t.strip(" `\\") for t in m.group(1).split("\\|") if t.strip(" `\\")}
        for needed in sorted(F007_PROMOTION_REQUIRED - enums):
            errors.append((check_id, f"promotion_verdict 枚举缺必需取值 {needed!r}"))
    rows = _f007_promotion_priority_rows(design)
    if not rows:
        errors.append((check_id, "design §3.3 缺 promotion_verdict 导出优先级表"))
    else:
        if [r[0] for r in rows] != list(range(1, len(rows) + 1)):
            errors.append((check_id, f"导出优先级表级别不连续：{[r[0] for r in rows]}"))
        outputs = [r[2] for r in rows]
        if enums and set(outputs) != enums:
            errors.append(
                (
                    check_id,
                    "优先级表输出集合与术语表枚举不一致："
                    f"表多出 {sorted(set(outputs) - enums)}、"
                    f"枚举多出 {sorted(enums - set(outputs))}",
                )
            )
        conditions = " ".join(r[1] for r in rows)
        for needle, why in (
            ("REJECTED", "未覆盖 run 终态 REJECTED"),
            ("dedup", "未覆盖查重结论"),
            ("INCOMPLETE", "未覆盖 INCOMPLETE 终态"),
            ("no_lookahead", "未覆盖无前视三层状态"),
        ):
            if needle not in conditions:
                errors.append((check_id, f"导出优先级表条件{why}（缺 {needle}）"))
        m2 = re.search(r"冻结优先级表取值（`([^`]+)`）", spec)
        if not m2:
            errors.append((check_id, "spec FR-005 缺 promotion_verdict 优先级串"))
        else:
            spec_order = [t.strip() for t in m2.group(1).split(">")]
            table_order = list(dict.fromkeys(outputs))
            if spec_order != table_order:
                errors.append(
                    (check_id, f"spec 优先级串 {spec_order} 与 design 表行序 {table_order} 不一致")
                )
    if "E_PROMOTION_BLOCKED" not in design:
        errors.append((check_id, "design 未定义专用错误码 E_PROMOTION_BLOCKED"))
    if "blocked_pending_audit" not in spec or "F006 晋级入口" not in spec:
        errors.append((check_id, "spec FR-007 未写明 blocked_pending_audit 与 F006 晋级入口消费"))
    return errors


def check_f007_dedup_precedes_verdict(root: pathlib.Path) -> list[tuple[str, str]]:
    """F007-D042：查重必须在 finalize 内、先于 promotion_verdict 导出，回写只搬运结论。"""
    check_id = "f007_dedup_precedes_verdict"
    errors: list[tuple[str, str]] = []
    design = read(root, F007_DESIGN)
    spec = read(root, F007_SPEC)
    tasks = read(root, F007_TASKS)
    finalize = next(
        (
            para.replace("\n", " ")
            for para in _md_section(design, "3. 数据模型与 Migration").split("\n\n")
            if "finalize-cohort" in para
        ),
        "",
    )
    if "查重" not in finalize or "promotion_verdict" not in finalize:
        errors.append((check_id, "design §3.2 未写明 finalize 内先查重、再导出 promotion_verdict"))
    elif finalize.index("查重") > finalize.index("promotion_verdict"):
        errors.append((check_id, "design §3.2 把查重写在 promotion_verdict 导出之后"))
    if "同一次原子写" not in finalize:
        errors.append((check_id, "design §3.2 未锁定查重结论与 verdict 同一次原子写"))
    for rel, text, needles in (
        (F007_SPEC, spec, ("之前", "evidence_ref", "承诺顺序")),
        (F007_DESIGN, design, ("不重算", "evidence_ref", "承诺顺序")),
    ):
        for needle in needles:
            if needle not in text:
                errors.append((check_id, f"{rel} 缺查重契约要素 {needle!r}"))
    t012 = [ln for ln in tasks.split("\n") if ln.strip().startswith("- [ ] T012")]
    if not t012 or "查重" not in t012[0]:
        errors.append((check_id, "tasks T012（finalize）未承接查重实现"))
    t018 = [ln for ln in tasks.split("\n") if ln.strip().startswith("- [ ] T018")]
    if not t018 or "不重算" not in t018[0]:
        errors.append((check_id, "tasks T018（回写）未写明只搬运结论、不重算查重"))
    return errors


def check_f007_registry_writeback_carrier(root: pathlib.Path) -> list[tuple[str, str]]:
    """F007-D028：注册表评测面回写必须具备 FR/DR/AC/design/tasks 全载体（解析式）。"""
    check_id = "f007_registry_writeback_carrier"
    errors: list[tuple[str, str]] = []
    spec = read(root, F007_SPEC)
    design = read(root, F007_DESIGN)
    tasks = read(root, F007_TASKS)
    fr8 = re.search(r"###\s+Requirement:[^\n]*`FR-008`[\s\S]*?(?=\n### )", spec)
    if not fr8:
        errors.append((check_id, "spec §4 缺 FR-008 需求块"))
    else:
        for needle in ("0.99", "评测面", "append-only", "不写注册表**定义面**"):
            if needle not in fr8.group(0):
                errors.append((check_id, f"FR-008 正文缺关键约束 {needle!r}"))
    if "**DR-008**" not in spec:
        errors.append((check_id, "spec 缺 DR-008 实体（RegistryEvaluationSummary）"))
    ac13 = None
    for line in spec.replace("\r\n", "\n").split("\n"):
        m = AC_LINE_RE.match(line.strip())
        if m and m.group(1) == "013":
            ac13 = m
    if ac13 is None:
        errors.append((check_id, "spec 缺 AC-013 验收项"))
    else:
        refs = set(re.findall(r"\b(?:FR|DR|TR|IR|UX|NFR)-\d+\b", ac13.group(2)))
        if not {"FR-008", "DR-008"} <= refs:
            errors.append((check_id, f"AC-013 未同时引用 FR-008/DR-008（现引用 {sorted(refs)}）"))
    if "registry_writeback" not in design:
        errors.append((check_id, "design 缺 registry_writeback 模块"))
    if "下游 Contract（F003 注册表评测面）" not in design:
        errors.append((check_id, "design 缺 F003 注册表评测面下游契约段"))
    if "FR-008" not in tasks:
        errors.append((check_id, "tasks 无 FR-008 承载任务"))
    return errors


def _f007_design_ac_file_map(design_text: str) -> dict[str, set[str]]:
    """解析 design §8 表：验收项单元格中的 AC-x → 该行计划文件集合。

    「真实环境」行是执行机证据（SOP §3），不纳入开发机旅程验收的覆盖要求。
    """
    ac_files: dict[str, set[str]] = {}
    for line in _md_section(design_text, "8. 测试策略与验收映射").split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 5:
            continue
        head = cells[1]
        if "验收项" in head or set(head) <= {"-", " "}:
            continue
        if "真实环境" in head:
            continue
        files = set(TEST_FILE_RE.findall(cells[3]))
        for ac in re.findall(r"\bAC-(\d+)\b", head):
            ac_files.setdefault(ac, set()).update(files)
    return ac_files


def check_f007_design_covers_all_spec_acs(root: pathlib.Path) -> list[tuple[str, str]]:
    """F007-D035：spec §6 的每个 AC 必须在 design §8 有映射行。"""
    check_id = "f007_design_covers_all_spec_acs"
    errors: list[tuple[str, str]] = []
    spec = read(root, F007_SPEC)
    ac_ids = {
        m.group(1)
        for m in (AC_LINE_RE.match(ln.strip()) for ln in spec.replace("\r\n", "\n").split("\n"))
        if m
    }
    ac_files = _f007_design_ac_file_map(read(root, F007_DESIGN))
    for ac in sorted(ac_ids):
        if ac not in ac_files:
            errors.append((check_id, f"design §8 缺 AC-{ac} 映射行"))
    return errors


def check_f007_test_group_verify_covers_ac_map(root: pathlib.Path) -> list[tuple[str, str]]:
    """F007-D029：[TEST] 条目引用的 AC 所映射的测试文件必须出现在其 verify 命令内。"""
    check_id = "f007_test_group_verify_covers_ac_map"
    errors: list[tuple[str, str]] = []
    ac_files = _f007_design_ac_file_map(read(root, F007_DESIGN))
    s3 = _md_section(read(root, F007_TASKS), "3. 验证与验收任务")
    for line in s3.split("\n"):
        if "[TEST]" not in line:
            continue
        m = TASK_LINE_RE.match(line.strip())
        if not m:
            continue
        tid = m.group(1)
        paren = REF_PAREN_RE.search(m.group(2))
        refs = re.findall(r"\bAC-(\d+)\b", paren.group(1)) if paren else []
        verify_part = line.split("verify:")[-1] if "verify:" in line else ""
        verify_files = set(TEST_FILE_RE.findall(verify_part))
        for ac in refs:
            for f in sorted(ac_files.get(ac, ())):
                if f not in verify_files:
                    errors.append((check_id, f"{tid} 引用 AC-{ac} 但 verify 未运行其载体 {f}"))
    return errors


def check_f007_requirement_id_order(root: pathlib.Path) -> list[tuple[str, str]]:
    """F007-D039：spec §4 的 FR/DR 需求 ID 必须按编号升序且不重复。"""
    check_id = "f007_requirement_id_order"
    errors: list[tuple[str, str]] = []
    section = _md_section(read(root, F007_SPEC), "4. 需求")
    fr_ids = re.findall(r"^###\s+Requirement:[^\n]*`FR-(\d+)`", section, re.M)
    dr_ids = re.findall(r"^- \*\*DR-(\d+)\*\*", section, re.M)
    for label, seq in (("FR", fr_ids), ("DR", dr_ids)):
        nums = [int(x) for x in seq]
        if nums != sorted(nums):
            errors.append((check_id, f"spec §4 {label} 需求 ID 未按编号升序：{seq}"))
        if len(set(nums)) != len(nums):
            errors.append((check_id, f"spec §4 {label} 需求 ID 重复：{seq}"))
    return errors


CUSTOM_CHECKS = (
    check_f007_declares_f003,
    check_ac_body_covers_clauses,
    check_active_feature_indexes,
    check_f007_design_test_map_covers_tasks,
    check_no_stale_closed_question_task,
    check_declared_test_carriers,
    check_f007_lifecycle_closure,
    check_f007_promotion_blocked_state_defined,
    check_f007_dedup_precedes_verdict,
    check_f007_registry_writeback_carrier,
    check_f007_design_covers_all_spec_acs,
    check_f007_test_group_verify_covers_ac_map,
    check_f007_requirement_id_order,
    check_offload_decision_table,
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
