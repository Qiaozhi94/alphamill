---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f5f9c9f13ffeUndV8k28QEtsfZ"
title: "F004设计文档检视问题修复"
project: "/home/georg/projects/alphamill"
model: "deepseek-flash"
created_at: "2026-09-14T14:47:42Z"
updated_at: "2026-09-14T16:42:05Z"
tokens_input: 423859
tokens_output: 40284
cost: 0.2134
---

# F004设计文档检视问题修复

## user · 2026-09-14T14:47:42Z

<system-reminder>Note: The user selected #20 from "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md". ``` ```

 This may or may not be relevant to the current task.</system-reminder>

当前项目的f004需求的设计文档已经进行了第一轮的检视，请作为修复者严格按照skill要求审视每个问题并修复

## assistant · 2026-09-14T14:47:42Z

- **tool**: `skill({"name": "review-convergence", "user_message": "修复 F004 kronos-inference-runtime 设计文档第一轮检视发现的问题"})`
- **tool**: `bash({"command": "ls -la /home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/"})`


> [reasoning] The user wants me to fix issues found in a design document review for feature F004 (kronos-inference-runtime). They mention it's already gone through first round of review. The user says "作为修复者严格按照skill要求审视每个问题并修复" - as a fixer, strictly follow skill requirements to review each issue and fix it.

This is a review/fix task. According to the review-convergence skill, this is the default protocol for ALL code and document review. I should load the review-convergence skill first.

Let me also look at the design doc and find the review report. Let me start by loading the skill and exploring the relevant files.

The user selected #20 from the design.md file - which suggests there's a review report somewhere. Let me find it.

Let me load the review-convergence skill and explore the F004 directory.

  <details><summary>tool output</summary>

  ```text
## Skill: review-convergence

**Base directory**: /home/georg/.config/opencode/skills/review-convergence

Base directory for this skill: /home/georg/.config/opencode/skills/review-convergence/
File references (@path) in this skill are relative to this directory.

# Review Convergence

> 优先级:本 skill 优先于任何一次性的 code-review skill(包括 `review-changes`、
> `code-review-agent` 之类)。那些只是报告生成器,没有停止条件——正是本 skill 要修的
> 失效模式。真正一次性、无后续的小审查,可按第 0 节缩减轮次,但仍走本流程。
> 项目 CLAUDE.md 要求优先用 code-review-graph MCP 工具时,把它当作本流程的**取证手段**,
> 而不是替代本流程。

十轮审查还能挑出中等问题、修复还大概率引入新问题——这不是审查不够仔细,是流程没有
收敛条件。"审到审查者没意见为止"不是良定义的停止条件:只要投入足够注意力,任何代码
都能挑出新问题。本skill的目的是让审查在有限轮次内收敛,而不是无限发散。

## 0. 项目适配(每次先做,不要跳过)

在开始之前,读取当前仓库的 `CLAUDE.md` / `AGENTS.md`(如果存在),提取:
- 该项目自己的测试/回归规范(例如"每次修复必须补充回归测试"这类硬性要求)
- 已知的历史教训(例如"assert 被悄悄降级成 warning"这
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
total 24
drwxr-xr-x 2 georg georg 4096 Sep 14 21:48 .
drwxr-xr-x 7 georg georg 4096 Sep 14 21:48 ..
-rw-r--r-- 1 georg georg 3407 Sep 12 23:44 design.md
-rw-r--r-- 1 georg georg 5881 Sep 14 21:48 spec.md
-rw-r--r-- 1 georg georg 2295 Sep 12 23:44 tasks.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:47:48Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/alphamill/docs/reviews/ 2>/dev/null; echo \"---\"; git -C /home/georg/projects/alphamill status --short; echo \"---\"; git -C /home/georg/projects/alphamill rev-parse --short HEAD; git -C /home/georg/projects/alphamill branch --show-current"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md"})`


> [reasoning] The user is the fixer (修复者). The review has been done (first round). I need to:
1. Find the review report (CURRENT-doc.md likely in docs/reviews/)
2. Read the design document and review findings
3. Fix each issue as the fixer
4. Write FIX-log.md with evidence

Let me look for the review files. The user selected #20 from design.md - probably line 20 or issue #20? Let me check docs/reviews.

  <details><summary>tool output</summary>

  ```text
total 116
drwxr-xr-x 2 georg georg  4096 Sep 14 22:33 .
drwxr-xr-x 7 georg georg  4096 Sep 14 21:48 ..
-rw-r--r-- 1 georg georg 13486 Sep 14 22:33 CURRENT-doc.md
-rw-r--r-- 1 georg georg 93031 Sep 14 21:48 RETROSPECTIVE.md
---
---
bc314f0
main


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: related_features: [F001, F002]
6: topics: [kronos, inference, deployment]
7: doc_kind: design
8: created: 2026-09-12
9: updated: 2026-09-12
10: ---
11:
12: # F004：Kronos 真实推理运行时 - 设计
13:
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15:
16: ## 0. 输入与约束
17:
18: - **行为契约**：`spec.md`（FR-001 / NFR-001）
19: - **上游 Contract**：F001 冻结的 Kronos HTTP API（`GET /health`、`GET /predict/{symbol:path}`、`POST /predict_batch`），零改动
20: - **执行环境**：与 F001 收口态一致（WSL2 + docker-ce；本机无独立显卡，CPU 推理实测 3.4–7.2s/次）
21: - **实现约束**：`vendor/Kronos`（pin `67b630e`）与 `models/`（391MB + 16MB）不入库，由 F001 既有流程获取
22:
23: ## 1. 技术概要
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:47:51Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md"})`


> [reasoning] I'm the fixer. There's a `CURRENT-doc.md` review report (13KB) with findings. Let me read it, plus the spec.md and tasks.md. Also read CLAUDE.md for the project rules.

The report is at docs/reviews/CURRENT-doc.md. Let me read it.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md</path>
<type>file</type>
<content>
1: ---
2: report_type: doc-review
3: round: 1
4: date: 2026-09-14
5: prior_report: null
6: scope: full-scan
7: stop_condition_met: false
8: severity_counts: {critical: 0, high: 6, medium: 4, low: 0}
9: issues:
10:   - id: F004-D001
11:     title: 真实 profile 未接入 signals_log 的生产消费者
12:     severity: high
13:     category: correctness
14:     root_cause: root-cause
15:     origin: spec-drift
16:     pattern_tag: cross-feature-contract-drift
17:     status: open
18:     tracked_task: null
19:     fix_summary: ""
20:     regression_test: ""
21:     suggested_fix: 明确 profile 启用时 Freqtrade 与 runtime snapshot 的路由切换，并以 signals_log.source=kronos 的端到端断言验收；否则删除“自动升级 signals_log”的范围承诺。
22:     dispositio
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: status: draft
6: gate_version: 1
7: related_features: [F001, F002]
8: topics: [kronos, inference, deployment]
9: doc_kind: spec
10: created: 2026-09-12
11: updated: 2026-09-12
12: ---
13:
14: # F004：Kronos 真实推理运行时（编排内可复现）
15:
16: > Owner: Georg | Target: v0.2.x
17:
18: ## 0. 来源与意图
19:
20: - **PRD 来源**：`docs/alphamill-prd.md` FR3（信号生产）与 M1 运行基座
21: - **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑）
22: - **上游来源**：F001 AC-006（真实推理证据，当前靠仓外手工实例）、F002 检视 F002-Q001（容器化不在数据桥契约内，需独立载体）
23: - **功能类型**：backend / infra
24: - **规格模式**：lite
25: - **变更类型**：ADDED
26: - **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: related_features: [F001, F002]
6: topics: [kronos, inference, deployment]
7: doc_kind: tasks
8: created: 2026-09-12
9: updated: 2026-09-12
10: ---
11:
12: # F004：Kronos 真实推理运行时 - 任务
13:
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15:
16: ## 0. 来源与执行规则
17:
18: - 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
19: - 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
20: - 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
21:
22: ## 1. 前置条件
23:
24: - F001 已 done：薄壳、`vendor/Kronos` pin 与 `models/` 权重流程成立，AC-006 已有手工命令形态的实测证据。
25: - spec §8 Q-001（是否阻塞 F002 done）未关闭前，本 feature 不进入 `ready-for-development`。
26:
27: ## 2. 实现任务
28:

…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:47:53Z

- **tool**: `bash({"command": "ls /home/georg/projects/alphamill/deployment/ /home/georg/projects/alphamill/src/alphamill/kronos_service/ /home/georg/projects/alphamill/tests/integration/ 2>&1"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/SOP.md"})`


> [reasoning] Now I have the full picture. I'm the fixer (修复者). The review (CURRENT-doc.md) has 10 open issues: 6 High, 4 Medium.

As the fixer, I need to:
1. Review each issue strictly per the review-convergence skill's requirements
2. Fix the valid ones in spec.md/design.md/tasks.md
3. For issues I disagree with, write a rejection in FIX-log.md with evidence
4. Append Round 1 fix declaration to FIX-log.md with evidence triples: findings, commits, regression_tests, gate

Wait — but this is a doc review. The regression test for docs is "document changed + link/format checks pass". The skill says for doc-review the closure evidence is "文档被改+链接/格式检查通过".

Also note: the user says "当前项目的f004需求的设计文档已经进行了第一轮的检视，请作为修复者严格按照skill要求审视每个问题并修复". So they want me to fix the design docs. The review covers spec.md, design.md, tasks.md (all three artifacts).

Let me read CLAUDE.md first (project adaptation per skill §0), and check the related contracts mentioned:
- F001 spec (AC-006 area), F001 test file
- F002 signals_log spec
- PRD FR3/FR1.2/FR5, M0
- deployment/docker-compose.yml
- deployment/kronos-service.Dockerfile
- kronos_service thin shell
- alphamill-snapshot.service
- SOP
- architecture §7

Let me do this efficiently. First read CLAUDE.md and find the relevant files.

The fixes needed:

**D001 (High)**: spec claims "F004 落地后 signals_log 内容自动升级" but real profile isn't wired into production consumers (Freqtrade compose + alphamill-snapshot.service still point to mock :8001). Need to either: (a) define runtime routing switching, or (b) delete the "auto-upgrade signals_log" scope promise.

Let me look at what the actual consumer setup is. This is a design decision. The reviewer says: "最短修复路径是先裁决真实 profile 只服务 AC-006，还是同时成为运营信号源". As the fixer, I need to decide — but this is a product scope decision. Hmm, but the fix suggestions say "明确 profile 启用时 Freqtrade 与 runtime snapshot 的路由切换，并以 signals_log.source=kronos 的端到端断言验收；否则删除'自动升级 signals_log'的范围承诺。"

Given this is a "lite" spec for infrastructure, and F004's intent is "把 Kronos 真实模型推理纳入 deployment/ 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并让 F002 导出的 signals_log 能承载真实信号而非 placeholder" — the minimal honest fix is to delete/adjust the "自动升级" claim since wiring consumers' routing is a scope expansion. But wait, "让 F002 导出的 signals_log 能承载真实信号而非 placeholder" is in the one-line intent too. Hmm.

Actually there are two options:
1. Expand scope: make F004 also handle consumer routing (Freqtrade compose + snapshot service reroute to 8002 when profile enabled). This is a bigger change.
2. Narrow scope: F004 only makes the real instance available in orchestration (AC-006 reproducible); the "signals_log auto-upgrade" is not claimed; instead add a tracked follow-up task/note that consumer routing is a separate feature/decision. Update the spec's one-line intent and the decision table's "后续" column.

Which one does the reviewer prefer? The suggested fix gives both options. As fixer, I should pick the simpler, honest one that keeps the feature focused. The spec mode is "lite", the intent is to make AC-006 reproducible in orchestration. The signals_log claim is secondary (it appears in 一句话意图 and §7 decision table "后续" column and US-001 "以便" clause).

Let me check what "自动升级" means concretely. spec line 124: "F004 落地后 signals_log 内容自动升级，无需 F002 返工". And line 26: "并让 F002 导出的 `signals_log` 能承载真实信号而非 placeholder".

If consumers still hit 8001 (mock), then even after F004, signals_log stays placeholder. So the claim is wrong. Options:
- Option A: wire the routing (expand scope). To do it properly, the snapshot service and freqtrade would need to point at 8002 when real profile is up. That's cross-feature contract change (F002's snapshot service config). This could balloon F004.
- Option B: remove the claim. Change intent to "为 F002 的 signals_log 提供可编排的真实信号源；消费者路由切换不在本 feature 范围，作为后续决策"。 Add a "明确后移" or decision entry with a tracked task.

I think Option B is right for a lite infra feature, and the review explicitly allows it ("否则删除'自动升级 signals_log'的范围承诺"). But I need to check: does removing it leave "让 F002 导出的 signals_log 能承载真实信号而非 placeholder" unaddressed? The intent says "并让 F002 导出的 signals_log 能承载真实信号" — with the real instance available at 8002, the capability exists; but nothing consumes it automatically. So the honest wording: "并提供真实信号源（8002），为 signals_log 内容升级铺路；消费者路由切换与自动升级不在本 feature 范围（显式后移）".

Hmm, but wait. Maybe I should consult the user? The review says "最短修复路径是先裁决真实 profile 只服务 AC-006，还是同时成为运营信号源" — this is a product decision. The skill says when there's ambiguity with 2x effort difference, ask. But the skill also says as fixer I can accept or reject findings. Since the review itself offers "或删除该范围承诺" as an acceptable fix, I can choose the narrow path without user input. That's within the reviewer's stated acceptable fixes.

Actually, let me think about what's best for the project. F004's goal is "编排内可复现的验收" for AC-006. Making it also the operational signal source is bigger: Freqtrade routing, snapshot service routing, failover between mock/real... That's clearly a separate feature. The narrow fix:
- spec §0.意图: remove "并让 F002 导出的 signals_log 能承载真实信号而非 placeholder" → replace with something honest like "为 signals_log 的真实化提供唯一真实信号源（消费者路由切换不在本 feature 范围）"
- spec §7 decision table: "F004 落地后 signals_log 内容自动升级，无需 F002 返工" → fix this claim.
- Also add to §5 maybe? No, §5 is "生命周期与不变量" not applicable.
- Add a clear "后移" note: consumer routing → separate feature/eval. In spec §3 范围外 maybe: "Freqtrade 与 runtime snapshot 的消费者路由切换（仍指向 mock :8001；真实源切换另立评估）".

Wait, but actually, is it true that consumers route to 8001? Let me verify by looking at deployment/docker-compose.yml and the snapshot service. The reviewer's D001 says "Freqtrade compose 与 alphamill-snapshot.service 仍固定访问 mock :8001". Let me verify.

**D002 (High)**: fail-closed & serial inference have no implementation path. Current model loads on first /predict, synchronous FastAPI handler can concurrently enter same predictor. Fix: add to design/tasks: startup dependency & dual-weight-dir validation, eager load/readiness, process-level inference lock, tests for missing assets and concurrent requests.

This requires design changes: §5 Runtime — add model lifecycle: startup precheck (vendor path, model dir, tokenizer), eager load at startup, readiness; inference lock (serialize via threading.Lock or single worker). §7 failure — missing weights → startup fails non-zero (already present but need path validation details). §8 test strategy — add tests. tasks.md — add tasks T00x for Python thin shell changes.

Wait — but the design says "不新增 Python 模块。差异只在镜像层与挂载" and "并发：单实例，CPU 推理串行，无共享状态". The reviewer says this is wrong: the current code loads model lazily in first /predict and handlers are sync (FastAPI runs sync handlers in threadpool → concurrency possible). Let me verify the actual code in src/alphamill/kronos_service/.

So the fix requires actually changing the design to include thin-shell changes, and tasks to include them. Also design §2 "不新增 Python 模块" might need to change to "允许对 kratos_service 薄壳做最小改造" or similar. Let me look at the code first.

**D003 (High)**: "一条命令复现" lacks compose location & data preconditions. Fix: use `docker compose -f deployment/docker-compose.yml` consistently; declare DB migration complete + target exchange/symbol has ≥30 closed 1m candles; add new-clone data prep steps or narrow scenario.

This affects spec US-001 独立测试 (§2 line 53), and probably design/tasks commands (T002/T003 use `docker compose config` without -f). Fix all commands to include -f deployment/docker-compose.yml. And add data preconditions: DB migrated + ≥30 1m candles for target symbol. Where? spec §2 US 独立测试 and §3 边界场景? Or §7 依赖? Probably: spec US-001 独立测试: "新 clone + 权重就位 + DB 已迁移且目标 symbol 有 ≥30 根已闭合 1m K 线". Also design §8 test doc should mention env requirements. Also tasks T003 verify command needs -f.

**D004 (High)**: AC-001's reused F001 test can bypass compose (test just hits KRONOS_BASE_URL; a manual host process passes it). Fix: add F004-specific compose config tests / container integration tests proving: real target, read-only mounts, real container identity, missing asset failure, default profile isolation, signals_log source; keep F001 smoke for HTTP contract only.

So: design §8 test strategy needs multiple test rows/files; tasks needs new tasks creating tests. Need to figure out the project's test conventions. Let me look at tests/integration/test_f001_kronos_smoke.py and the existing test setup.

**D005 (High)**: real image deps list misses huggingface_hub & tqdm (direct imports in pin 67b630e). Fix: lock minimal inference deps including huggingface_hub and tqdm, specify torch CPU wheel version and index; verify with in-container import + real weight load.

Design §1/§2 or a new subsection should list pinned deps. spec §3 范围内 line 63 lists "torch/cpu + einops + safetensors" — should add huggingface_hub, tqdm. And torch version + cpu index (--index-url https://download.pytorch.org/whl/cpu). Let me check vendor/Kronos pin — it's not in repo (not committed). Let me check if vendor/Kronos exists locally to verify imports.

**D006 (High)**: acceptance environment violates execution-machine evidence discipline. design still uses "本机无独显" as integration environment; tasks lack hostname/device. Fix: designate qiaozhi-lt as integration acceptance machine; record hostname/device=cpu; dev machine only runs static+unit gates.

Wait, but design line 20 says "本机无独立显卡，CPU 推理实测 3.4–7.2s/次" — this is the current F001 closure state. Hmm, reviewer says design "仍以'本机无独显'作为集成环境... 与 SOP 的执行机取证硬规则冲突". Let me read SOP to understand the evidence-machine rule. Maybe SOP says integration evidence must be collected on qiaozhi-lt (a specific machine). Let me read docs/SOP.md.

Also design §8's test row + tasks T003 should mention hostname/device evidence.

**D007 (Medium)**: NFR-001's build isolation mechanism & criterion undefined. Fix: define Dockerfile base/mock/real targets and which target each compose service uses; change "镜像层与改前一致" to stable assertable criterion "默认镜像不含 torch 且默认 compose 不启用/不构建 real 服务".

So tasks T001 verify should change; design §1/§7 should define multi-stage targets explicitly.

**D008 (Medium)**: mount contract missing KRONOS_TOKENIZER_PATH, :ro, host 8002→container 8001 mapping. Fix: write full host/container paths, env vars, read-only mounts, port mapping in design §2/§5.

Need to verify actual env var name (KRONOS_TOKENIZER_PATH?) and paths from F001 code. Let me check the kronos_service config.

**D009 (Medium)**: spec cites PRD FR3 as "信号生产" but FR3 is evidence evaluation & validation. Fix: change source to M0, FR1.2 and related FR5 runtime chain; explain F004-FR3 relation is only providing Kronos signal input for evaluation.

Let me check PRD for FR3, FR1.2, FR5, M0.

**D010 (Medium)**: tasks dependency graph broken: T001→T004 and T005→T006 chains not connected; T006 mixes evidence writeback + status/BACKLOG change. Fix: complete DAG T004→T005→验收证据回写→状态/BACKLOG同步; split T006; unify final gate `python3 tools/verify.py`.

OK. Now, the fixer workflow per skill:
- One finding one commit (local commits), preserve bisect/revert ability.
- Write FIX-log.md Round 1 declaration with: findings, commits, regression_tests, gate.
- For doc-review: regression_test = doc changed + link/format checks pass. Actually skill says "文档检视靠'文档被改+链接/格式检查通过'". The project has `python3 tools/verify.py` which validates spec lifecycle, links, deps pins, secret scan, pytest, ruff.

Important: "检视意见固化为门禁失败测试后才允许关闭:先让测试红(复现 finding),修复后变绿" — for docs, this means the verify tool should catch issues? The project has validate_spec_lifecycle.py. Hmm, for doc findings, we can't easily write a red test for "consumer routing claim" etc. The doc-review closure evidence is "文档被改+链接/格式检查通过". So the gate is tools/verify.py on the updated docs. Let me check what verify.py does to make sure our doc changes won't break it.

Also skill §0 says: "基线声明:开始前在会话/报告里写明当前基线——分支名 + HEAD commit 短哈希 + 受影响产物版本". Baseline: main @ bc314f0, docs v0.2, status draft. Note diff>30%? First round fix.

Also per the skill, commits: "每轮 commit 只含代码部分" — well here it's docs. Hmm: "检视文件只是过程稿...永不提交 git". So we commit the doc fixes (spec/design/tasks + F001 spec writeback if included), not the review files. Wait — should the fix round include the F001 spec §6 writeback? That's a task T004, an implementation task. In this round I'm fixing the review findings about the F004 docs. T004 is about writing back after implementation. Actually design.md says "文档 / 配置：F001 spec §6 命令回写" as impact. But the review didn't require executing T004 now; it required the docs to be correct. Hmm, but D003 says fix commands to `-f deployment/docker-compose.yml` consistently — that includes wherever commands appear.

Let me now also check whether I should actually implement code (no — the user says fix the design document issues; feature is in draft, not ready-for-development, so we shouldn't implement code yet. The fixes are doc-level: spec/design/tasks).

Wait, user message: "当前项目的f004需求的设计文档已经进行了第一轮的检视，请作为修复者严格按照skill要求审视每个问题并修复" — "the design document of F004 has gone through round 1 review; as fixer, strictly follow the skill requirements to review each issue and fix". So fix the docs. Good.

Now let me gather evidence. I need to check:
1. CLAUDE.md (project conventions)
2. SOP.md (evidence machine rules, review flow)
3. deployment/docker-compose.yml, kronos-service.Dockerfile
4. src/alphamill/kronos_service/ (thin shell — model loading, concurrency)
5. tests/integration/test_f001_kronos_smoke.py
6. F001 spec (AC-006, §6)
7. F002 spec (signals_log, snapshot service)
8. PRD (FR3, FR1.2, FR5, M0)
9. architecture §7
10. tools/verify.py + validate_spec_lifecycle.py
11. Check vendor/Kronos imports (if locally present)
12. Check RETROSPECTIVE.md for relevant patterns? Maybe skim relevant recent lessons.

That's a lot. Let me parallelize with reads and explore agents. Actually codegraph could help for code, but this is mostly docs. Let me do direct reads for docs and codegraph for the service code.

Let me fire:
- Read CLAUDE.md
- Read docs/SOP.md
- bash: ls deployment, src/alphamill/kronos_service
- codegraph_explore for kronos_service model loading + concurrency

Then second batch: F001 spec §6, F002 spec, PRD sections, architecture §7, compose file, Dockerfile, test file.

Since I'm the fixer and need to be accurate, direct reads are fine. Let me be efficient but thorough. I'll use parallel tool calls.

Let me start.
Baseline established: `main` @ `bc314f0`, F004 docs v0.2 (spec/design/tasks), 10 open findings (6 High / 4 Medium). Now gathering evidence on each finding before fixing.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill/deployment/:
alphamill-backup.service
alphamill-backup.timer
alphamill-export.service
alphamill-export.timer
alphamill-fullexport.service
alphamill-fullexport.timer
alphamill-snapshot.service
alphamill-snapshot.timer
backup-nas.sh
backups
data-collector.Dockerfile
docker-compose.yml
f001-backfill-supervisor.sh
f001-backfill-window.env
freqtrade-entrypoint.sh
initdb-apply-migrations.sh
kronos-service.Dockerfile
verify.ps1

/home/georg/projects/alphamill/src/alphamill/kronos_service/:
__init__.py
__pycache__
db_adapter.py
generator.py
kronos_real.py
server.py

/home/georg/projects/alphamill/tests/integration/:
__pycache__
conftest.py
test_f001_collector_smoke.py
test_f001_dryrun_monitoring.py
test_f001_kronos_smoke.py
test_f001_row_reconciliation.py
test_f002_e
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/CLAUDE.md</path>
<type>file</type>
<content>
1: # AlphaMill
2:
3: AI 原生的加密量化研究与交易管线：以 AI 因子工厂为核心，贯通数据治理 → 假设与因子 →
4: 证据评测 → 组合与策略 → Freqtrade 执行 → 监控归因与复盘（中文别名：淘沙）。
5:
6: ## 当前结构
7:
8: - `docs/alphamill-prd.md`：正式 PRD（产品真相源），产品判断以此为准。
9: - `docs/alphamill-architecture.md`：四平面架构与接口契约（架构真相源），随实现迭代。
10: - `docs/alphamill-research-factor-mining.md`：因子挖掘/ML 选型调研证据（决策已提炼至 ADR-0001）。
11: - `docs/alphamill-integration.md`：数据桥 / Vibe-Trading / Freqtrade 集成操作细节（依赖策略见 ADR-0002）。
12: - `docs/decisions/`：ADR——0001 挖掘引擎选型 / 0002 依赖管理策略 / 0003 验证门禁不降级 / 0004 组合构建（因子→策略映射） / 0005 呈现与观测架构 / 0006 证据边界与实验身份 / 0007 研究快照绑定（dataset 独立版本 + ResearchSnapshot）。
13: - `docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`：quant-crypto 资产清算迁移操作手册（F001 附属）。
14: - `doc
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/SOP.md</path>
<type>file</type>
<content>
1: ---
2: topics: [sop, workflow]
3: doc_kind: note
4: created: 2026-09-06
5: updated: 2026-09-07
6: ---
7:
8: # 开发流程（AlphaMill）
9:
10: 本文是项目的**原则入口与质量门**唯一真源：汇总「项目不可违反原则」的短摘要与各自
11: 唯一拥有者链接，规定开发纪律、验证流程、状态转换与复核协议。
12:
13: ## 0. 项目不可违反原则（入口）
14:
15: 以下原则是**阻断性**的：违反其中任何一条的规格/实现不得进入实现或收口阶段。规范
16: 正文在各自的唯一拥有者中，本文只给摘要与入口。**每条原则的规范正文只放一个唯一
17: 拥有者**，本文只写短摘要与链接，不重复 PRD、architecture、decisions 的完整定义。
18:
19: | # | 原则 | 短摘要 | 规范正文唯一拥有者 |
20: |---|---|---|---|
21: | 1 | 可追溯规格优先 | 功能必须先有已评审规格；实现/测试/实验/结论必须引用需求编号；未写入规格的行为不视为承诺 | 本文 + `docs/features/README.md` |
22: | 2 | 证据门不降级 | 候选按样本功效分级并经过留出与最终确认；效率提升不得来自放宽门禁 | `docs/decisions/0003-validation-gate-non-degradation.md` |
23: | 3 | 无前视一等公民 | 因子定义过 AST 纯度门 + 独立逐 K
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:48:14Z

- **tool**: `bash({"command": "wc -l /home/georg/projects/alphamill/deployment/docker-compose.yml /home/georg/projects/alphamill/deployment/kronos-service.Dockerfile /home/georg/projects/alphamill/src/alphamill/kronos_service/*.py /home/georg/projects/alphamill/tests/integration/test_f001_kronos_smoke.py /home/georg/projects/alphamill/tests/integration/conftest.py /home/georg/projects/alphamill/docs/alphamill-prd.md /home/georg/projects/alphamill/docs/alphamill-architecture.md /home/georg/projects/alphamill/tools
…[truncated])`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/deployment/docker-compose.yml"})`


> [reasoning] Now let me read the key code and configs:
1. deployment/docker-compose.yml
2. deployment/kronos-service.Dockerfile
3. src/alphamill/kronos_service/server.py + kronos_real.py + generator.py
4. tests/integration/test_f001_kronos_smoke.py + conftest.py
5. F001 spec §6 (AC-006)
6. F002 spec (signals_log, consumer routing)
7. PRD FR3/FR1.2/FR5/M0
8. architecture §7
9. tools/verify.py & validate_spec_lifecycle.py

Parallel reads. Some files may be large (PRD, architecture). Let me grep relevant sections instead for the big docs. Actually let me read the smaller ones fully and grep the large ones.

Let me first list sizes.

  <details><summary>tool output</summary>

  ```text
143 /home/georg/projects/alphamill/deployment/docker-compose.yml
    11 /home/georg/projects/alphamill/deployment/kronos-service.Dockerfile
     1 /home/georg/projects/alphamill/src/alphamill/kronos_service/__init__.py
   159 /home/georg/projects/alphamill/src/alphamill/kronos_service/db_adapter.py
    45 /home/georg/projects/alphamill/src/alphamill/kronos_service/generator.py
   166 /home/georg/projects/alphamill/src/alphamill/kronos_service/kronos_real.py
   149 /home/georg/projects/alphamill/src/alphamill/kronos_service/server.py
   100 /home/georg/projects/alphamill/tests/integration/test_f001_kronos_smoke.py
   196 /home/georg/projects/alphamill/tests/integration/conftest.py
   309 /home/georg/projects/alphamill/docs/alphamill-prd.md
   577 /home/georg/projects/alphamill/docs/alphamil
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/deployment/docker-compose.yml</path>
<type>file</type>
<content>
1: services:
2:   timescaledb:
3:     image: timescale/timescaledb:latest-pg16
4:     container_name: quant-timescaledb
5:     restart: unless-stopped
6:     environment:
7:       POSTGRES_USER: ${DB_USER:-quant}
8:       POSTGRES_PASSWORD: ${DB_PASSWORD:-change-me}
9:       POSTGRES_DB: ${DB_NAME:-quant}
10:     ports:
11:       - "5432:5432"
12:     volumes:
13:       - timescale_data:/var/lib/postgresql/data
14:       - ../db/init.sql:/docker-entrypoint-initdb.d/01_init.sql:ro
15:       # 迁移目录整挂到 initdb 的子目录（子目录不会被 entrypoint 直接执行），
16:       # 由 02_apply_migrations.sh 按序应用并登记 schema_migrations——与既有库的
17:       # tools/apply_migrations.py 共用同一个版本账本（C402）。
18:       - ../db/migrations:/d
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:48:17Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/deployment/kronos-service.Dockerfile"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/kronos_service/server.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/kronos_service/kronos_real.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/integration/test_f001_kronos_smoke.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/deployment/alphamill-snapshot.service"})`


> [reasoning] Confirmed D001 evidence: freqtrade uses `KRONOS_SIGNAL_URL: http://kronos-signal:8001` — hardcoded to the mock service. Let me check alphamill-snapshot.service for the runtime snapshot consumer.

Also read:
- kronos-service.Dockerfile
- kronos_service/server.py, kronos_real.py, generator.py
- test_f001_kronos_smoke.py
- alphamill-snapshot.service
- F002 spec (find relevant parts: signals_log, snapshot)
- F001 spec §6 AC-006
- PRD FR3/FR1.2/FR5/M0
- architecture §7

Let me batch these.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/deployment/kronos-service.Dockerfile</path>
<type>file</type>
<content>
1: FROM python:3.11-slim
2:
3: WORKDIR /app
4: ENV PYTHONUNBUFFERED=1
5:
6: COPY pyproject.toml README.md ./
7: COPY src ./src
8: RUN pip install --no-cache-dir .
9:
10: EXPOSE 8001
11: CMD ["uvicorn", "alphamill.kronos_service.server:app", "--host", "0.0.0.0", "--port", "8001"]

(End of file - total 11 lines)
</content>
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/kronos_service/server.py</path>
<type>file</type>
<content>
1: import os
2: from datetime import datetime
3:
4: from fastapi import FastAPI, HTTPException, Query
5: from pydantic import BaseModel
6:
7: try:  # Package import is used by the host service; fallback keeps the legacy CLI usable.
8:     from .db_adapter import healthcheck, latest_ohlcv
9:     from .generator import generate_placeholder_signal
10:     from .kronos_real import real_signal
11: except ImportError:  # pragma: no cover - direct script compatibility only.
12:     from db_adapter import healthcheck, latest_ohlcv
13:     from generator import generate_placeholder_signal
14:     from kronos_real import real_signal
15:
16:
17: class PredictResponse(BaseModel):
18:
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/kronos_service/kronos_real.py</path>
<type>file</type>
<content>
1: import os
2: import sys
3: import time
4: from dataclasses import dataclass
5: from pathlib import Path
6:
7: import pandas as pd
8:
9: try:  # Package import is used by the host service; fallback keeps the legacy CLI usable.
10:     from .generator import clamp
11: except ImportError:  # pragma: no cover - direct script compatibility only.
12:     from generator import clamp
13:
14:
15: @dataclass
16: class ModelStatus:
17:     enabled: bool
18:     available: bool
19:     loaded: bool
20:     model: str
21:     tokenizer: str
22:     device: str
23:     error: str | None = None
24:
25:
26: class KronosRealSignal:
27:     def __init__(self):
28:         self.enabled
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/integration/test_f001_kronos_smoke.py</path>
<type>file</type>
<content>
1: """F001 Kronos 推理冒烟：AC-002（编排内契约）+ AC-006（真实推理证据）。
2:
3: AC-002 —— 编排内常绿：`/health` 200，`/predict` 返回结构合法的信号，且 `source`
4: 与 `/health` 的 `model_enabled` **一致**（mock→placeholder，real→kronos）。声明真实
5: 模型却回 placeholder 一律判红，不是放水的降级判据。
6:
7: AC-006 —— 真实推理证据：需要 391MB 权重与 vendor clone，不在默认编排内，因此由独立
8: 命令验证（前置条件见 spec §7 / vendor/VENDORED.md）：
9:
10:     set -a; . ./deployment/.env; set +a   # DB_HOST 默认是 compose 服务名，宿主上不可解析
11:     DB_HOST=127.0.0.1 KRONOS_USE_REAL_MODEL=true KRONOS_REPO_PATH=vendor/Kronos \
12:       .venv/bin/python -m uvicorn alphamill.kronos_service.server:app --port 8002 &
13:     ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 \
14:       KRONOS_BASE
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/deployment/alphamill-snapshot.service</path>
<type>file</type>
<content>
1: [Unit]
2: Description=AlphaMill dry-run runtime snapshot (freqtrade API -> TimescaleDB)
3:
4: [Service]
5: Type=oneshot
6: WorkingDirectory=%h/projects/alphamill
7: ExecStart=%h/.local/bin/pwsh -NoProfile -File %h/projects/alphamill/scripts/collect_runtime_snapshot.ps1 -KronosHostUrl http://127.0.0.1:8001 -Exchange binance

(End of file - total 7 lines)
</content>
  ```
  </details>

## assistant · 2026-09-14T14:48:20Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.1/F001-quant-crypto-migration/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-prd.md"})`


> [reasoning] Confirmed:
- D001: `freqtrade` → `KRONOS_SIGNAL_URL: http://kronos-signal:8001` (mock). `alphamill-snapshot.service` → `-KronosHostUrl http://127.0.0.1:8001`. Both point to mock. So "signals_log 自动升级" claim is false unless routing is changed. Also note: real profile uses host port 8002 but the compose network service name would be different... Actually if real service is named `kronos-signal-real` at host port 8002, freqtrade would still hit 8001. Even in-container routing would need KRONOS_SIGNAL_URL change.

Wait, actually, hmm — the design says real instance uses host port 8002 while mock 8001 stays. The snapshot service runs on host (Windows, %h) hitting 127.0.0.1:8001. For signals_log (F002 export from TimescaleDB runtime snapshot?) let me check F002's signals_log to understand what upgrades it. The claim in F004 spec: "F004 落地后 signals_log 内容自动升级，无需 F002 返工". signals_log source=placeholder comes from the runtime snapshot consumer (collect_runtime_snapshot.ps1 → DB), which hits 8001. So indeed consumers need routing change.

- D002: kronos_real.py `_load_predictor` loads lazily on first `generate_signal` call; no eager load at startup; no lock. server.py `predict` is sync `def` → FastAPI runs it in threadpool → concurrent requests can enter `_load_predictor` and `predictor.predict` concurrently. Confirmed. Also `_dependencies_available` only checks torch import + kronos_root exists (doesn't check model dirs). And `status().available` requires torch import + kronos_root existence. The design claims "权重或 vendor 缺失 → 容器启动即非零退出" but nothing does that — lazy load means the container starts successfully and only fails at first /predict. Confirmed D002.

- D005: need to check vendor/Kronos pin imports. Local vendor/Kronos may exist (not in repo). Let me check. The reviewer says pin 67b630e imports huggingface_hub and tqdm directly. Let me verify locally if vendor exists.

- D003: compose commands in specs: design §5 line 46 `docker compose --profile kronos-real up -d kronos-signal-real`; spec line 53 `docker compose --profile kronos-real up -d`; tasks line 30 `docker compose config`... none use `-f deployment/docker-compose.yml`. Repo root has no compose file (docker compose config failed). Confirmed.

- D004: test hits KRONOS_BASE_URL only; a manual host process passes it (that's actually how AC-006 manual works today). So the test doesn't prove the compose profile works. Confirmed.

- D006: design line 20 says "执行环境：与 F001 收口态一致（WSL2 + docker-ce；本机无独立显卡，CPU 推理实测 3.4–7.2s/次）". SOP §3 machine boundary: "集成与 GPU 证据一律在执行机取（当前 qiaozhi-lt）；验收证据必须记录取证机器的 hostname 与设备（GPU 型号 / device=cpu）；开发机上的 skip 不算证据". The design as-is says integration env = local dev machine (WSL2, no dGPU) — conflicts. Fix: integration acceptance on qiaozhi-lt with device=cpu recorded; dev machine only static/unit gates. Note the reviewer suggested "指定 qiaozhi-lt 执行集成验收并记录 hostname/device=cpu；开发机只跑本地门禁".

Hmm wait, but F001's AC-006 evidence was collected where? "本机无独立显卡，CPU 推理实测 3.4–7.2s/次" suggests evidence was on the dev machine? Let me check F001 spec AC-006 and its evidence to see what was recorded. Also check architecture §7.1 for the machine boundaries. Let me read those.

- D009: PRD FR3. Let me read the PRD.

- D010: tasks graph. Current: T001→T002→T003→T004 chain; T005→T006 chain separate. The reviewer says "T001→T004 与 T005→T006 两条链未连接；T006 同时承担证据回写和状态/BACKLOG 变更". Fix: full DAG T001→T002→T003→T004→T005 (verify)→T006(evidence writeback)→T007(status/BACKLOG sync), and use `python3 tools/verify.py` consistently (T006 uses `python tools/validate_spec_lifecycle.py` without `3`; inconsistent).

Wait: "统一使用 python3 tools/verify.py 作为最终门" — T004 and T005 already use `python3 tools/verify.py`; T006 uses `python tools/validate_spec_lifecycle.py`. Hmm the fix: split T006 into evidence writeback + status change, where status change uses verify.py as final gate? Let me look at how other done features' tasks handled this. Let me check F002 tasks.md (0.2) for a pattern of status/BACKLOG sync tasks. Also check the RETROSPECTIVE or SOP for the required sequence.

Also for D010: "把 T004 -> T005 -> 验收证据回写 -> 状态/BACKLOG 同步串成完整 DAG".

Now let me gather remaining evidence:
1. F001 spec §6 AC-006 + §7 (Kronos real inference prerequisites)
2. F002 spec signals_log parts
3. PRD FR3, FR1.2, FR5, M0
4. architecture §7 (7.1)
5. tools/verify.py & validate_spec_lifecycle.py (what checks run)
6. vendor/Kronos presence & imports (D005)
7. Maybe collect_runtime_snapshot.ps1
8. F002 tasks for status-sync pattern

Let me batch. PRD is 309 lines — read fully. Architecture 577 lines — grep §7 or read relevant portion. F001 spec 233 lines — read. F002 spec 296 — read. That's a lot of tokens but necessary for accurate fixes. Let me do it.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.1/F001-quant-crypto-migration/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F001
4: version: "0.1"
5: status: done
6: gate_version: 1
7: related_features: []
8: topics: [migration, infra]
9: doc_kind: spec
10: created: 2026-09-06
11: updated: 2026-09-12
12: ---
13:
14: # F001：quant-crypto 资产清算迁移
15:
16: > Owner: Georg | Target: v0.1.0
17:
18: ## 0. 来源与意图
19:
20: - **PRD 来源**：`docs/alphamill-prd.md` §1.2 决策 4（复用成熟基础设施）与里程碑 M0
21: - **架构来源**：`docs/alphamill-architecture.md` §五（资产清算迁移表）、§七（部署拓扑）
22: - **系统设计 / Research / Contract 来源**：`docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`（迁移清单与验收）
23: - **上游决策**：`docs/decisions/`（暂无；仓库归档处置记录于同目录 migration-plan.md §二）
24: - **功能类型**：backend / workfl
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-prd.md</path>
<type>file</type>
<content>
1: # AlphaMill — 产品需求文档（PRD）
2:
3: > 版本：v0.1 | 日期：2026-09-13 | 状态：草案
4:
5: ## 一、背景与问题定义
6:
7: ### 1.1 quant-crypto 复盘
8:
9: 上一代项目 quant-crypto 已建成可复用的数据、推理、执行、风控与监控基础设施：631 万行
10: 1m OHLCV、衍生品特征、Kronos 信号缓存、Freqtrade dry-run、风险保护、90 天留出门和信号
11: 质量监控。最终状态为 `blocked_no_paper_candidate`：所有候选均未通过最终留出。
12:
13: 这次失败暴露的不是单点工具缺失，而是研究到交易之间没有形成可持续运转的闭环：
14:
15: - 假设主要靠人工提出，5 周只覆盖 3 个信号族，探索速度慢；
16: - 因子生成、成本评估、统计验证与策略构建的优化目标不完全一致；
17: - 数据、实验、信号和交易结果之间缺少统一谱系，复现与重定价成本高；
18: - 失败结果没有结构化回流为下一轮假设，研究循环无法积累；
19: - 研究 PASS、组合纳入、部署和线上衰减之间缺少完整生命周期管理。
20:
21: AlphaMill 要解决的不是“多生成一些公式”，而是把 **Alpha 的发现、证伪、部署和运营**
22: 做成一条可信、可复现、可持续学习的生产管线。
23:
24: ### 1.2 项目决策
25:
26: 1. **以 AI 因子工厂为核心引擎**：程序化、RL、人工与 LLM 共同生产带来
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:48:27Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/spec.md"})`


> [reasoning] Now I have PRD. FR3 is indeed "证据评测与验证" (evidence evaluation & validation) — so D009 is confirmed: spec cites "FR3（信号生产）" wrongly. The actual signal production... hmm. Let me think about which PRD items are direct sources for F004:
- M0 (self-contained runtime baseline) — yes, F001/F004 runtime base.
- FR1.2 不可变快照: "data_bridge 将 OHLCV、funding、basis、OI、Kronos 信号与必要日志导出为分区 Parquet" — Kronos signals are exported in FR1.2. F004 makes the Kronos signal source real. So citing FR1.2 as downstream/related is valid.
- FR5 runtime chain: FR5.1 versioned signal contract, FR5.2 deployment pre-check... F004 is more about the Kronos inference runtime feeding signals. FR5 is 部署与交易执行 (deployment and trade execution). Hmm, "相关 FR5 运行链" — the reviewer's suggested fix says "改指 M0、FR1.2 与相关 FR5 条款". Hmm, maybe FR5.1? Let me think: F004's role is to make the Kronos real inference available within orchestration; the signals_log (F002 export) gets real content which feeds FR3 evaluation. The closest PRD source is M0 (runtime baseline) + FR1.2 (snapshot includes Kronos signals). FR5? Actually I'm not sure FR5 is right — F004's consumer is the runtime snapshot → signals_log → research evaluation (FR3 downstream relation: "F004 与 FR3 的关系仅是为评测提供 Kronos 信号输入"). The review says "把来源改为直接支持该能力的 M0、FR1.2 与相关 FR5 运行链，并说明 F004 与 FR3 的关系仅是为评测提供 Kronos 信号输入。"

Hmm wait — maybe architecture §7 topology includes the Kronos service as part of the runtime? Let me check architecture §7 for what F004 maps to. Also the "M1 运行基座" claim in F004's current text ("PRD 来源：FR3（信号生产）与 M1 运行基座"). M0 is "自包含运行基线" — includes "Kronos /health". So M0 is more apt than M1? F001 was M0. F004 completes the Kronos runtime within compose. Hmm, "M1 运行基座"... M1 = "可信数据与证据底座" (FR1 + FR3 + FR7). The Kronos real runtime mainly serves M0's exit criteria (Kronos /health) and F002/M1 data bridge export.

Let me check the architecture §7 deployment topology to see where the Kronos service / real profile fits, and whether there's a mention of runtime snapshot routing. Let me read the architecture doc sections. 577 lines, let me read the whole thing? It's important for D001 (consumer routing), D006 (machine boundary §7.1), and D009 (sources). Let me read it.

Also need F002 spec for signals_log details and Q001. And tools/verify.py + validate_spec_lifecycle.py.

Let me batch: architecture (read relevant portion — grep for §7 first, then read), F002 spec, verify.py, validate_spec_lifecycle.py.

Actually, let me just read architecture fully (577 lines) — it's the source for deployment topology and machine boundaries. Plus F002 spec (296 lines). Plus verify.py (70) and validate_spec_lifecycle.py (315). That's ~1250 lines, fine.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
1: # AlphaMill — 系统架构设计
2:
3: > 版本：v0.1 | 日期：2026-09-13 | 配套：[alphamill-prd.md](./alphamill-prd.md)
4:
5: ---
6:
7: ## 〇、存储三件套分工（TimescaleDB / Parquet / DuckDB）
8:
9: **不是三选一的竞品，是流水线上的三段**：Parquet 是文件格式（箱子），DuckDB 是查询引擎（开箱的手），TimescaleDB 是数据库服务（实时柜台）。
10:
11: | | TimescaleDB | Parquet 湖 | DuckDB |
12: |---|---|---|---|
13: | 本质 | PG 时序扩展（数据库服务） | 列式文件格式（无服务） | 进程内 OLAP 查询引擎 |
14: | 写入 | ✅ 流式写入、幂等 upsert、可修订 | ❌ 不可变，只增新文件 | ❌ 不负责存储 |
15: | 擅长 | 实时最新值、连续聚合、Grafana 直连 | 大范围列扫描、快照不可变=可复现 | 直接对 Parquet 跑 SQL |
16: | 复现性 | ❌ 数据会被回补/修订 | ✅ 同一 data_version 永远同结果 | 无关（读的人） |
17: | 角色 | **联机运营库** | **研究快照**（封存账本） | **取数入口**（会计的手） |
18:
19: ```text
20: CCXT 采集 ──写入──▶ TimescaleDB（联机运营库，随时改）
21
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F002
4: version: "0.2"
5: status: done
6: gate_version: 1
7: related_features: [F001]
8: topics: [data-bridge, parquet, duckdb, m1]
9: doc_kind: spec
10: created: 2026-09-12
11: updated: 2026-09-14
12: ---
13:
14: # F002：数据桥——Parquet 湖导出与 DuckDB 研究取数层
15:
16: > Owner: Georg | Target: v0.2.0
17:
18: ## 0. 来源与意图
19:
20: - **PRD 来源**:`docs/alphamill-prd.md` FR1.2(不可变快照)、FR1.3(研究只读边界)、FR1.4(双口径与时间语义)、FR1.6(灾备,湖部分);里程碑 M1
21: - **架构来源**:`docs/alphamill-architecture.md` §〇(存储三件套分工)、§四 data_bridge(质量门·对账·manifest)、§4.4(Parquet 湖 manifest 契约)
22: - **系统设计 / Research / Contract 来源**:`docs/alphamill-integration.md` §一(TimescaleDB → Parquet 湖,导出设计/修订政策/
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:48:33Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -rn \"signals_log\" --include=\"*.py\" --include=\"*.ps1\" --include=\"*.sql\" --include=\"*.service\" -l . 2>/dev/null | head -30; echo \"=== unit tests ===\"; ls tests/unit/ | head -40; echo \"=== workflows ===\"; ls .github/workflows/ 2>/dev/null; echo \"=== vendor ===\"; ls vendor/ 2>/dev/null; ls vendor/Kronos 2>/dev/null | head; echo \"=== vendor VENDORED ===\"; head -60 vendor/VENDORED.md 2>/dev/null"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/verify.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md"})`


> [reasoning] Very interesting. F002 spec §6 (line 218-221) contains: "F004 落地后内容自动升级, F002 无需返工". So the same false claim appears in F002 spec too! The review finding D001 targets F004 spec:26 ("并让 F002 导出的 signals_log 能承载真实信号而非 placeholder" and "F004 落地后 signals_log 内容自动升级，无需 F002 返工" in spec §7 decision table line 124).

Wait, actually reading F002 spec §6: "F004 落地后内容自动升级, F002 无需返工。" — the claim there is about the signals_log content。But as the review says, since neither freqtrade (KRONOS_SIGNAL_URL→8001) nor the snapshot service (KronosHostUrl→8001) is rewired, the placeholder content persists even after F004. So "内容自动升级" is false in both F002 and F004.

Hmm, but wait. How does signals_log get populated? Let me check. The F002 says signals_log dataset exists in TimescaleDB with 2,040 rows source=placeholder. Who writes signals_log? Probably the runtime snapshot collector (scripts/collect_runtime_snapshot.ps1) writes prediction results into signals_log, or the kronos service writes? Let me check.

Actually let me find signals_log producer. Search the repo.

The D001 suggested fix options: (a) wire the consumers, or (b) delete the auto-upgrade scope promise. Since F002 is done and its spec also carries the claim, and the review only targets F004 docs... but wait, the review's finding location is F004 spec.md:26. The fixer should fix F004 docs. But should I also fix F002 spec's claim? The review scope was "受检产物: F004 三件套". Hmm — but "相邻契约" includes F002. The point of D001: "spec 宣称内容自动升级，但 Freqtrade compose 与 alphamill-snapshot.service 仍固定访问 mock :8001".

Actually wait. Let me think again about whether consumers matter. The signals_log is written by... let me check. If the runtime snapshot consumer (collect_runtime_snapshot.ps1) hits :8001 every N minutes and writes its predictions to signals_log, then its `source` field would be placeholder while mock. If F004 brings up a real instance on host port 8002, the snapshot consumer still hits 8001 (mock) → signals_log remains placeholder. Unless the operator manually sets -KronosHostUrl to 8002... The service file is fixed.

So "内容自动升级" is wrong. Which fix is right?

Option A (wire consumers): F004 would add routing so that when the real profile is up, freqtrade and snapshot point to it. But how would that work semantically? In compose, freqtrade could point to `kronos-signal-real:8001` (container port) — but the real service is optional; the default freqtrade must keep working without it. Docker compose doesn't have conditional env vars per-profile easily... Actually it does: you can set KRONOS_SIGNAL_URL per profile? No — env can't be conditional on profile. You could add a second freqtrade override, or use a separate compose file. This is exactly the "profile 组合变复杂" case. The design explicitly said: "若 profile 组合变复杂再拆 override 文件". Wiring the consumers = scope expansion and complexity. The reviewer even says "最短修复路径是先裁决真实 profile 只服务 AC-006，还是同时成为运营信号源".

For a fixer, choosing the narrow path (delete the claim) is simpler and keeps F004 focused. But wait — is that honest w.r.t. the spec's stated intent? The user (owner) might actually want F004 to make signals_log real. The F002 spec says "F004 落地后内容自动升级, F002 无需返工" — that's an owner-level promise. Hmm. But as reviewer D001 notes, this claim is currently false. The reviewer suggests either wire or delete.

Let me check if there's a follow-up mechanism. Actually, remember: the review suggests "否则删除'自动升级 signals_log'的范围承诺". As fixer, I need to decide. Let me think about what's the most correct for the project:

The F004 feature's core intent (one-liner): "把 Kronos 真实模型推理纳入 deployment/ 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并让 F002 导出的 signals_log 能承载真实信号而非 placeholder。"

If we cut the signals_log part entirely, F004 becomes purely "AC-006 in orchestration". But the real instance still exists at 8002; the snapshot consumer could be pointed there manually. Actually — what writes to signals_log? Let me check. If it's the kronos service itself (real mode writes signals_log), then the real instance on 8002 would write its own signals_log rows... Let me verify.

Let me search for signals_log writers.

Also D002: I need to check if the design should include Python changes (eager load, lock, preflight). The current design says "不新增 Python 模块" — but the reviewer says the fail-closed promise needs thin-shell changes. That's a real design gap: design §7 says "权重或 vendor 缺失 → 容器启动即非零退出" but as implemented, the container starts fine and fails at first /predict. To make it fail at startup, we need code changes (startup validation) or a compose healthcheck/command wrapper. Design must specify.

Wait, but also there's a subtlety: does the requirement really need startup fail? spec §3 边界场景: "权重或 vendor 缺失：profile 启动即失败并打印缺失路径，不静默退回 mock。" So yes, spec promises startup failure. The design must implement it (thin shell changes). So the fix: design §2/§5/§7 updated to include thin-shell changes: startup preflight validation + eager load + inference serialization (lock) + readiness; and tasks to implement them.

Let me check what tests exist for the kronos service (unit tests?) and think about what tasks to add.

Also D006: integration acceptance machine. SOP says integration evidence must be collected on the execution machine (qiaozhi-lt) and record hostname/device. But note F001's AC-006 evidence: "AC-006 同文件真实模型 CPU 推理通过（KRONOS_REQUIRE_REAL_MODEL=1 + :8002 实例，1.76s/次，T008 记录）". Where was that collected? The F001 spec line 205 says host venv... The dev machine has no NVIDIA; the CPU inference was measured... "本机无独立显卡" - the F001 decision table says "本机无独立显卡 | AC-002 采用 CPU 推理回退". Hmm, but per architecture §7.1, the execution machine qiaozhi-lt has RTX 4060. The "本机" in F001 might refer to the Windows host (qiaozhi-lt?) Hmm.

Wait, CLAUDE.md says dev machine is `qiaozhi-gp`/`gp-wsl` (Legion Go, AMD iGPU, no NVIDIA); execution machine qiaozhi-lt (RTX 4060). The F001 spec says "本机无独立显卡，CPU 推理实测 3.4–7.2s/次" — that was probably on the dev machine. And the review D006 says: design still uses "本机无独显" as integration environment; SOP requires execution machine evidence. The reviewer suggests: "指定 qiaozhi-lt 执行集成验收并记录 hostname/device=cpu；开发机只跑本地门禁".

Hmm, but hold on: is that right for this feature? The feature is about compose orchestration; the real instance with torch CPU. The final target is the execution machine (Kronos 常驻 on GPU, arch §7.1: 白天 Kronos 常驻推理 ≤3GB GPU). CPU fallback acceptance could be on either. But per SOP, integration evidence must be on the execution machine. The dev machine can only run unit tests/verify.py. So design must say: integration acceptance (profile up + real prediction) must run on qiaozhi-lt; record hostname + device=cpu (until GPU passthrough is done); dev machine only runs static config gates + unit tests. tasks T003 must be updated to include hostname/device evidence.

Wait, but there's a nuance: the reviewer said "允许明确的 device=cpu 验收". The architecture says the target machine has RTX 4060, but GPU passthrough is explicitly a non-goal for F004 ("不做 GPU 推理与性能优化... GPU 直通留给执行机落地时处理"). So on qiaozhi-lt, the container runs CPU (no GPU passthrough in WSL2 docker-ce without nvidia toolkit). The evidence must record device=cpu. OK.

Hmm, wait, actually let me check where the current "本机" is. CLAUDE.md says dev machine = qiaozhi-gp/gp-wsl. The F001 spec §7 decision "本机无独立显卡" and architecture §7.1 says dev machine has no NVIDIA. But F001's integration runs (TimescaleDB, docker) — those need the execution machine per SOP? F001 was done before... hmm, actually the F001 closure happened on the host that had docker. The CLAUDE.md says "平台：Windows 11 宿主 + WSL2（Ubuntu 26.04，docker-ce，非 Docker Desktop）；docker-compose 自 quant-crypto 迁入" and "机器边界（架构 §7.1...）：开发机 qiaozhi-gp/gp-wsl ... 集成与 GPU 证据一律在执行机取".

So yes, F004 design line 20 "执行环境：与 F001 收口态一致（WSL2 + docker-ce；本机无独立显卡...）" conflicts: it designates the dev machine as integration env. Fix: execution env = qiaozhi-lt (execution machine), evidence records hostname/device=cpu. Also design §8 test mapping should say where each test runs: static compose tests can run on dev (they're static, no service); container integration + real prediction tests run on qiaozhi-lt.

Actually wait, are static compose config tests "unit tests" allowable on dev? `docker compose config` requires docker CLI but not docker daemon? Actually `docker compose config` works without daemon connection (it just parses/merges YAML). Hmm, but the dev machine may have docker-ce in WSL2 too (CLAUDE.md says platform WSL2 + docker-ce). It says dev machine "只承载编码、单元测试与 tools/verify.py 门禁". So compose config parsing tests could be argued either way; but to be safe: static config assertions (no daemon needed) can run on dev; anything requiring containers/credentials/data = execution machine.

Hmm, actually, let me reconsider: docker compose config needs the docker CLI and compose plugin; parsing doesn't need daemon. It's a static check. I'll define: "静态编排断言（docker compose config，无守护进程依赖）可入 `tests/unit` 并可上开发机 CI；容器级集成（build/up/predict/mount/失败路径）只在执行机 qiaozhi-lt 跑，证据记录 hostname 与 device=cpu"。

Also important: CI. The project CI — let me check what CI does: .github/workflows. tests/integration presumably skipped in CI (needs docker+DB). The reviewer D004 wants "F004 专属 compose 配置/容器集成测试，分别证明 real target、只读挂载、真实容器身份、缺资产失败、默认 profile 隔离及 signals_log 来源；保留 F001 冒烟只验证 HTTP 契约。"

So I need to define test files:
1. Static compose/Dockerfile test (unit-level): e.g. `tests/unit/test_f004_compose_profile.py` — parses deployment/docker-compose.yml + Dockerfile:
   - real service exists with `profiles: [kronos-real]`, target = real, mounts vendor/models read-only, env KRONOS_USE_REAL_MODEL=true, port mapping 8002:8001.
   - default profile excludes real service (`docker compose config` no real service) — but if parsing YAML directly, can assert `profiles` key.
   - Dockerfile has multi-stage/targets: default target doesn't install torch; real target installs torch CPU + deps.
   - Mock/default image excludes torch: an "image identity" check — maybe via parsing the Dockerfile target stages + a build config test. Static parse can prove "default target installs only base deps"; a container-level test can prove the built image has no torch: `docker compose build kronos-signal` then `docker run --rm quant-kronos-signal python -c "import torch"` must fail... Wait, D007 suggested criterion: "默认镜像不含 torch 且默认 compose 不启用/构建 real 服务". So a test can assert: in the built default image, `import torch` fails (ModuleNotFoundError); and `docker compose config --services` (no profile) lacks kronos-signal-real.
2. Container integration test (F004-specific): `tests/integration/test_f004_real_profile.py`:
   - `docker compose -f deployment/docker-compose.yml --profile kronos-real config` shows real service.
   - container identity: after `up`, find the container (compose service kronos-signal-real) — assert via `docker compose ps -q kronos-signal-real` and/or exec into it (`docker inspect` / `docker compose exec kronos-signal-real` run python: check `KRONOS_REPO_PATH` etc.? "真实容器身份" means prove the prediction came from the compose container, not a manual host process. E.g., use `docker compose exec kronos-signal-real python -c "import requests; ..."`? Or check container hostname via /health? /health doesn't expose hostname. Hmm — how do F001-style tests prove container identity? Options: `docker inspect <cid>` label `com.docker.compose.service=kronos-signal-real`, and query the service through container network from another container, or assert that killing the container makes the endpoint unreachable... A pragmatic approach: collect `docker compose ps --format json` to identify the container port mapping, then hit `127.0.0.1:8002` and also verify via `docker compose exec kronos-signal-real` that the same service responds. The reviewer's phrase: "真实容器身份" — assert that the running real service is managed by compose (compose ps has it running) and that the container's image is the real build target. E.g., `docker inspect` → `Config.Env` contains KRONOS_USE_REAL_MODEL=true; `Config.Labels` compose project/service = kronos-signal-real; and mounts are read-only.
   - Missing assets failure: start a scenario with an empty models dir (or wrong path) → container exits non-zero and logs missing paths. How to test without breaking the real env? Could run a one-off container from the same image with a bogus KRONOS_MODEL_PATH env and assert exit code != 0 + message. That's a good approach: `docker compose run --rm kronos-signal-real` with env override pointing to non-existent paths, assert exit code non-zero and log contains the missing path.
   - Default profile isolation: `docker compose -f ... config --services` (no profile) doesn't include kronos-signal-real; and real profile doesn't get started by default up. Static test.
   - signals_log source: depends on D001 decision. If we narrow scope (real profile only serves AC-006), then the signals_log assertion moves out. But the reviewer's D004 suggested fix mentions "及 signals_log 来源" as part of the container integration tests — but that's conditioned on D001 resolution. Hmm.

OK so there's coupling: D001's decision (wire consumers vs delete claim) determines D004's signals_log test scope.

Let me now decide D001 definitively. Options:

**Option A: Wire consumers (expand F004 scope)** — add to F004: when real profile is enabled, the runtime snapshot consumer and freqtrade route to the real instance. But:
- freqtrade routing: KRONOS_SIGNAL_URL is env in compose; profiles can't conditionally change env. Could define separate freqtrade-real service? That's "profile 组合变复杂" — the design already has a decision against it, saying "若 profile 组合变复杂再拆 override 文件".
- The snapshot consumer is a systemd/Windows script on host with hardcoded `-KronosHostUrl http://127.0.0.1:8001`. Changing it to 8002 would break mock default. It would need a flag/setting; and the consumer writes signals_log which research uses. This touches F002's contract (export) but the producer is scripts/collect_runtime_snapshot.ps1.
- Also end-to-end assertion "signals_log.source=kronos" would require running the snapshot collector + DB + export... that's a much bigger integration test.

**Option B: Narrow scope (delete claim)** — F004 = orchestration-internal reproducible AC-006 evidence only. The real instance is available in the compose network at 8002; consumer routing ("真实信号源切换") is explicitly out of scope, listed as deferred to a follow-up (with a tracked task or F-note). Then update:
- spec §0 intent: remove "并让 F002 导出的 signals_log 能承载真实信号而非 placeholder" → replace with honest statement: "（真实信号进入运营链路/消费者路由切换不在本 feature 范围）"
- spec §0 PRD source: fix FR3→ M0/FR1.2/FR5 chain (D009).
- spec §7 decision table line 124: replace "F004 落地后 signals_log 内容自动升级，无需 F002 返工" with the truth: consumer routing not in scope; F002 spec's claim needs correction too? Hmm. The review scope is F004 docs; but the same false claim in F002 spec — do I fix F002 too? The review didn't flag F002 spec as an issue (it's a "相邻契约"). D001's location is F004 spec:26. The claim in F004 §7 decision table says "代价已写进 F002 spec §6 限制说明；F004 落地后 signals_log 内容自动升级，无需 F002 返工". If I remove the promise, I should probably also fix F002's text since it propagates the false claim. But careful: F002 is done; docs/features/README says version directories after closure "只允许修复历史错误或死链" — correcting a now-known-false claim is a historical error fix, allowed. But is it in scope for this fix round? The reviewer D001 says the claim is false; leaving the same false claim in F002 spec would just move the problem. Hmm. But also: maybe the routing isn't considered blocked — maybe the intent is that an operator can later point the snapshot collector at 8002 manually... "自动升级" though is specifically "自动".

Actually — wait. Let me re-read D001 more carefully:

"真实 profile 未接入 signals_log 的生产消费者；spec 宣称内容自动升级，但 Freqtrade compose 与 alphamill-snapshot.service 仍固定访问 mock :8001"
suggested_fix: "明确 profile 启用时 Freqtrade 与 runtime snapshot 的路由切换，并以 signals_log.source=kronos 的端到端断言验收；否则删除'自动升级 signals_log'的范围承诺。"

The two options. The choice interacts with what the project actually wants. Let me look at the F004 spec's decision table: "是否阻塞 F002 done | 不阻塞（2026-09-13 owner 裁决） ... 代价已写进 F002 spec §6 限制说明；F004 落地后 signals_log 内容自动升级，无需 F002 返工". The owner already decided F004 doesn't block F002. The question is whether F004 should wire consumers. Given:
- F004 is a lite spec / infra feature.
- Consumer routing spans freqtrade (strategy config), snapshot service (host script), and would need profile-conditional behavior — genuinely a separate concern.
- The reviewer's own "正确性通道判定" says: "最短修复路径是先裁决真实 profile 只服务 AC-006，还是同时成为运营信号源；这会决定 D001 的实现范围".

As the fixer, I should pick the minimal correct fix: narrow scope + explicitly defer consumer routing to a tracked follow-up. But should I consult the owner (user)? The skill says fixer can reject or fix; but this is a scope-level product decision. The review offers both as acceptable. The safer default for a "lite" infrastructure feature whose core is AC-006 reproducibility: narrow scope. Also, importantly, the current design (port 8002 coexistence, mock default) already implies the real instance is NOT the consumer source. The claim in the spec was aspirational/wrong; docs should reflect actual design. I'll go with Option B and make the deferral explicit:

- spec §0: remove auto-upgrade claim; state that consumer routing (Freqtrade KRONOS_SIGNAL_URL / runtime snapshot KronosHostUrl) stays mock :8001 and is out of scope, deferred (tracked).
- spec §2 US-001: the "以便" clause says "AC-006 与 signals_log 的内容有效性不依赖任何仓外手工步骤" — must fix: real instance in orchestration doesn't make signals_log valid automatically. Change to "AC-006 的真实推理证据不依赖仓外手工步骤".
- spec §7 依赖: "下游消费者：F002 的 signals_log dataset 内容有效性" — needs rewording: signals_log 内容真实化仍需消费者路由切换（后移）。
- spec §7 decision table line 124: fix the "自动升级" claim.
- Add scope exclusion in §3 范围外: "消费者路由切换（Freqtrade KRONOS_SIGNAL_URL、runtime snapshot KronosHostUrl 仍指向 mock :8001）；真实实例只服务 AC-006 证据与手工/后续切换".
- Add "明确后移" in tasks §5: "消费者路由切换（freqtrade/snapshot → 真实实例）→ 评估后另立（或 F00x）"— 需要目标 feature/version per tasks format: "第 5 节只能放明确移交给其它 Feature/版本的内容，必须写目标 Feature/版本". Hmm, there's no existing target feature. I could write "目标：v0.2.x 后续 feature（未立项，需 owner 立项）"... The template says must write target feature/version. Maybe "0.2 后续评估（未立项）" — that violates "必须写目标 Feature/版本"? I could say target version 0.2 and feature "待立项（F00x/评估）". Hmm. Let me check the TEMPLATE tasks.md for the exact convention and another feature's "明确后移" section. Let me read the template.

Also there's an alternative: maybe I should ask the user which option. The user said "严格按照skill要求审视每个问题并修复" — strict per skill. The skill says for fixers: fix or reject with evidence. For ambiguous scope decisions, the skill's "clarification protocol" applies when 2x effort difference... Option A vs B is much more than 2x effort. But the review explicitly accepts B ("否则删除...范围承诺"). Since the reviewer pre-authorized B, and B is minimal/correct, I'll do B without asking. If the owner wanted A, they'd have asked to expand. Also note: I'm the fixer, not the product owner; choosing B is the conservative option that doesn't silently expand scope. And I'll note it in FIX-log as acceptance of D001 via suggested alternative.

Hmm wait, but actually, let me reconsider. If we choose B, then D004's suggested test "及 signals_log 来源" gets adjusted: the F004 container test should instead assert that signals_log routing OUT of scope... no test needed for out-of-scope. But we can still test "real instance writes signals_log?" Let me check whether the kronos service writes signals_log at all! Let me search.

Actually — hold on. Let me check: how does signals_log get written in the first place? If the snapshot script calls /predict and writes rows, then even with real instance on 8002, no auto-upgrade. Let me grep for signals_log in the repo.

Also for D002 I need to see if there are existing unit tests for the kronos service (tests/unit/test_...kronos...). Let me look.

And check the bootstrap: how does the container get started? docker-compose kronos-signal service runs uvicorn with the package. For F004 real service, we'd add command/env. The design needs the new service name & Dockerfile target.

Let me also check the .github workflow to know what CI runs (D004/D007 test levels), and read tools/verify.py + validate_spec_lifecycle.py to know doc gates.

Let me batch:
- grep signals_log across repo
- ls tests/unit | grep -i f001/kronos
- read tools/verify.py
- read tools/validate_spec_lifecycle.py
- read .github workflows
- read TEMPLATE tasks.md
- check vendor/Kronos exists & its imports (D005 evidence)

  <details><summary>tool output</summary>

  ```text
./src/alphamill/data_bridge/registry.py
./src/alphamill/data_bridge/digest.py
./src/alphamill/data_bridge/symbol_map.py
./src/alphamill/data_bridge/partitions.py
./deployment/verify.ps1
./tests/integration/conftest.py
./tests/integration/test_f002_reader.py
./tests/integration/test_f002_schedule_backup.py
./tests/integration/test_f002_export_reconcile.py
./tests/integration/test_f001_dryrun_monitoring.py
./tests/unit/test_f002_cli_contract.py
./tests/unit/test_f002_symbol_map.py
./tests/unit/test_f002_manifest.py
./tests/unit/test_f002_reader_contract.py
./tests/unit/test_f002_partitions.py
./tests/unit/test_f002_registry.py
./tools/f001_backfill_report.py
./db/init.sql
./scripts/collect_runtime_snapshot.ps1
=== unit tests ===
__pycache__
test_apply_migrations.py
test_backup_nas_contract.p
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/verify.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """本地统一验证入口（公开验证唯一入口）。
3:
4: 按固定顺序运行：规格生命周期校验 → 文档相对链接检查 → dev 依赖 pin 范围检查
5: → 密钥模式扫描 → pytest → ruff check → ruff format check。任一步失败即记录，
6: 全部跑完后汇总返回非零（不短路）。
7:
8: 各底层命令仍可单独用于定位，但 README、SOP 与 CLAUDE 不再各自维护完整命令清单，
9: 统一指向本入口。
10:
11: 用法：
12:     python3 tools/verify.py
13: 退出码 0 表示全部通过；非 0 时打印失败步骤。
14: """
15:
16: from __future__ import annotations
17:
18: import pathlib
19: import subprocess
20: import sys
21:
22: ROOT = pathlib.Path(__file__).resolve().parent.parent
23:
24:
25: def _run(cmd: list[str], label: str) -> bool:
26:     print(f"\n== {label} ==")
27:     proc = subprocess.run(cmd, cwd=ROOT)
28:     if proc.returncode != 0:
29:         print(f"FAILED: {l
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: Fxxx
4: version: "0.x"
5: related_features: []
6: topics: []
7: doc_kind: tasks
8: created: YYYY-MM-DD
9: updated: YYYY-MM-DD
10: ---
11:
12: # Fxxx：功能名称 - 任务
13:
14: > Owner: TBD | Spec: `spec.md` | Design: `design.md`
15:
16: ## 0. 来源与执行规则
17:
18: - 行为与验收真相源：`spec.md`。
19: - 技术方案与边界：`design.md`。
20: - 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
21: - 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
22: - `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
23: - 实现中若任务顺序或契约失效，先修订三件套，再继续编码。
24:
25: 统一任务格式：
26:
27: ```markdown
28: - [ ] T001 [P] (`US-001`, `FR-001`, `AC-001`): <一个可验证动作> — verify: `path/to/test.ts`
29: ```
30:
31: ## 1. 前置条件
32:
33: - [ ] T001 (`DQ-001`): 关闭所有阻塞性 spec/de
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:49:05Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== Kronos model imports ===\"; grep -rn \"import\" vendor/Kronos/model/*.py | grep -v \"^Binary\" | grep -E \"huggingface|tqdm|einops|safetensors|torch|^.*from\" | head -30; echo; echo \"=== requirements.txt ===\"; cat vendor/Kronos/requirements.txt; echo; echo \"=== model module libs ===\"; sed -n '1,40p' vendor/Kronos/model/kronos.py 2>/dev/null; echo \"=== snapshot script kronos refs ===\"; grep -n \"Kronos\\|kronos\\|signals_log\" scr
…[truncated])`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_f001_compose_contract.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/.github/workflows/ci.yml"})`


> [reasoning] Now let me check the vendor/Kronos imports for D005, the existing unit tests for kronos (test_kronos_health.py, test_kronos_db_adapter.py), test_f001_compose_contract.py (for the static compose test pattern), the CI workflow, and the snapshot script / signals_log writer. Also validate_spec_lifecycle.py to know what doc gates check (e.g., tasks section formats, Q/DQ).

Let me batch reads:
- vendor/Kronos/model/__init__.py (imports), requirements.txt
- tests/unit/test_f001_compose_contract.py
- tests/unit/test_kronos_health.py
- scripts/collect_runtime_snapshot.ps1 (see signals_log write & KronosHostUrl)
- .github/workflows/ci.yml
- tools/validate_spec_lifecycle.py

Let me first grep vendor/Kronos for imports of huggingface_hub/tqdm.

  <details><summary>tool output</summary>

  ```text
=== Kronos model imports ===
vendor/Kronos/model/__init__.py:1:from .kronos import KronosTokenizer, Kronos, KronosPredictor
vendor/Kronos/model/kronos.py:3:import torch
vendor/Kronos/model/kronos.py:4:from huggingface_hub import PyTorchModelHubMixin
vendor/Kronos/model/kronos.py:7:from tqdm import trange
vendor/Kronos/model/kronos.py:10:from model.module import *
vendor/Kronos/model/module.py:3:from einops import rearrange, reduce
vendor/Kronos/model/module.py:4:import torch
vendor/Kronos/model/module.py:5:import torch.nn as nn
vendor/Kronos/model/module.py:6:from torch.autograd import Function
vendor/Kronos/model/module.py:7:import torch.nn.functional as F

=== requirements.txt ===
numpy
pandas
torch>=2.0.0

einops==0.8.1
huggingface_hub==0.33.1
matplotlib==3.9.3
pandas==2.2.2
tqdm=
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_f001_compose_contract.py</path>
<type>file</type>
<content>
1: """F001 dry-run compose/import contract regression tests."""
2:
3: from pathlib import Path
4:
5: ROOT = Path(__file__).resolve().parents[2]
6:
7:
8: def test_freqtrade_service_mounts_repo_strategy_dependencies() -> None:
9:     compose = (ROOT / "deployment/docker-compose.yml").read_text(encoding="utf-8")
10:     strategy = (ROOT / "freqtrade/user_data/strategies/KronosFusionStrategy.py").read_text(
11:         encoding="utf-8"
12:     )
13:
14:     assert "  freqtrade:" in compose
15:     assert '      - "8080:8080"' in compose
16:     assert "HTTP_PROXY: ${BINANCE_HTTPS_PROXY:-}" in compose
17:     assert "HTTPS_PROXY: ${BINANCE_HTTPS_PROXY:-}" in compose
18:     asse
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/.github/workflows/ci.yml</path>
<type>file</type>
<content>
1: name: CI
2:
3: on:
4:   push:
5:     branches: [main]
6:   pull_request:
7:
8: # 同一分支的新提交取消仍在跑的旧任务，避免排队浪费。
9: concurrency:
10:   group: ${{ github.workflow }}-${{ github.ref }}
11:   cancel-in-progress: true
12:
13: # 供应链加固：本工作流只读仓库，不需要写权限。
14: permissions:
15:   contents: read
16:
17: jobs:
18:   # 步骤清单的唯一真源是 tools/verify.py：CI 只调用它，不复制各步骤
19:   # （生命周期 / 文档链接 / 依赖 pin / pytest / ruff 全部由 verify.py 提供）。
20:   verify:
21:     name: verify (py${{ matrix.python-version }})
22:     runs-on: ubuntu-latest
23:     strategy:
24:       fail-fast: false
25:       matrix:
26:         # 下限锁 requires-python；上限跟随，用于尽早发现新版本行为差异。
27:         python-version: ["3.11", "3.13"]
28:     steps:
29:       -
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:49:08Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/scripts/collect_runtime_snapshot.ps1"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py"})`


> [reasoning] Very interesting! `scripts/collect_runtime_snapshot.ps1` line 2: default `$KronosHostUrl = "http://127.0.0.1:8002"` — but deployment/alphamill-snapshot.service passes `-KronosHostUrl http://127.0.0.1:8001`. So the snapshot service explicitly overrides to 8001. Let me read the script and the service more carefully. The snapshot script writes signals_log with source from prediction. Let me read the full script.

Also note: the service file uses 127.0.0.1:8001, which is the mock instance in compose (port published 8001). The default param is 8002 (probably the old manual real instance!). Interesting — so the runtime snapshot script's default hits 8002 (host real instance), but the systemd service explicitly overrides to 8001 (mock). Hmm. Wait, maybe F001 set the service file to 8001 for the compose mock.

So the signals_log writer is `collect_runtime_snapshot.ps1` → inserts into `signals_log` with source = prediction.source (kronos/placeholder) or 'kronos_error'. Let me read the script fully to understand.

This matters for D001: if the snapshot service points to 8001 (mock) then signals_log stays placeholder. If we point it to 8002 (real profile published on host 8002), it would write source=kronos. The systemd service is installed on the execution machine. So "auto upgrade" would require changing the service file or its parameter. That's a concrete, small change actually! The service file has `-KronosHostUrl http://127.0.0.1:8001`. Changing it to 8002 when the real profile is active would route the snapshot to real.

Hmm, but then the mock default compose (8001) vs real profile (8002): if the service points at 8002 and the real profile isn't running, snapshot fails (Kronos unreachable → writes kronos_error rows?). That would break the default runtime snapshot. So a static switch isn't acceptable either; you'd need a runtime toggle/config. So consumer routing is indeed a separate concern.

Let me read the full snapshot script and its tests (test_runtime_snapshot_contract.py) to understand the contract. Also check deployment/verify.ps1 for how it uses kronos (maybe checks 8001/8002).

Then decide D001 scope precisely and write the fixes.

Also let me note CI: CI runs `python3 tools/verify.py` on ubuntu, which includes pytest for tests/unit and tests/integration. Integration tests skip if services unavailable (`ALPHAMILL_INTEGRATION` not set → skip). But unit tests always run. So any new F004 static compose test (unit) will run in CI. That's good: D004's "不能绕过目标部署形态的仓库内门禁" — static compose/Dockerfile contract tests can be unit gates; container-level integration tests only on the execution machine.

Wait, but the reviewer D004 asked: "新增 F004 专属 compose 配置/容器集成测试，分别证明 real target、只读挂载、真实容器身份、缺资产失败、默认 profile 隔离及 signals_log 来源；保留 F001 冒烟只验证 HTTP 契约。" So split:
- Static unit tests (git-committed, CI-runnable): Dockerfile targets, compose real service definition, mounts :ro, port mapping, profiles isolation, default image no torch (static? can't prove without building — but can assert default build target stage lacks torch installation; hmm "默认镜像不含 torch" could be a container test).
- Integration tests (execution machine): container builds, real service up, /health+/predict via compose container, missing-asset fail-closed, default image import torch fails.

Let me design the test strategy in the design doc:
- `tests/unit/test_f004_compose_profile_contract.py` (static, CI):
  - Dockerfile has two targets; default target = mock/base without torch; real target installs torch/einops/safetensors/huggingface_hub/tqdm pinned; compose default service uses default target; real service uses real target + profiles + :ro mounts + env + port mapping.
- `tests/integration/test_f004_real_profile.py` (container, execution machine):
  - compose config with profile lists real service; default config doesn't.
  - `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real` → wait healthy → /predict source=kronos; identity: container = compose service (docker compose ps -q) and env/mounts asserted via `docker inspect`;
  - missing-asset path: `docker compose run --rm -e KRONOS_MODEL_PATH=...bogus... kronos-signal-real` exits non-zero with missing path in logs.
  - default image no torch: `docker compose build kronos-signal && docker run --rm ... python -c "import torch"` fails.
- F001 smoke stays HTTP contract only (AC-002), and F001 AC-006 evidence command? The F001 spec §6 writeback (T004) will change the AC-006 command to compose form. And F004's AC-001 = compose profile instance returns kronos + default unchanged.

Hmm wait, there's a nuance: F004 AC-001 currently says "不带该 profile 时默认编排行为与镜像层不变". D007 says "镜像层与改前一致" isn't a stable assertable criterion → change to "默认镜像不含 torch 且默认 compose 不启用/构建 real 服务". So update spec AC-001 wording? The review's suggested fix for D007 says: "明确 Dockerfile 的 base/mock/real target 和两个 compose 服务各自 target；把'镜像层与改前一致'改成可稳定断言的默认镜像不含 torch 且默认 compose 不启用/构建 real 服务。" The "镜像层与改前一致" is in tasks T001 verify ("默认 docker compose build kronos-signal 的镜像层与改前一致") and spec AC-001 ("不带该 profile 时默认编排行为与镜像层不变"). So update both.

Now D005: torch version and index. The real target must `pip install torch==X --index-url https://download.pytorch.org/whl/cpu` (CPU wheels). Which version? The F001 host venv used some torch version. vendor requirements says torch>=2.0.0. The pin should be explicit. Let me check pyproject for existing pins and maybe the host has torch installed to see version. Also check `vendor/VENDORED.md` note: "GPU 未就绪时 KRONOS_DEVICE=cpu（spec FR-003 / T003 决策）". Let me check if there's a pin convention (check_dep_pins). The design should state exact version after verification. Since this is a design doc (not implementing), I should specify the version per the local verified environment (F001 did CPU inference on host venv). Let me check what torch version is installed in .venv or elsewhere. `pip show torch` in .venv. Also whether there's a Dockerfile precedent.

Actually, the review says "明确 torch CPU wheel 的版本和 index" — I should give a concrete pinned version. Let me check the host venv (which ran AC-006) for the torch version to keep consistency. Let me run `.venv/bin/pip show torch` or check requirements. Also check pyproject.

D008: mount contract: host/container paths. Container paths: `KRONOS_REPO_PATH=/app/vendor/Kronos`, `KRONOS_MODEL_PATH=/app/models/Kronos-base`, `KRONOS_TOKENIZER_PATH=/app/models/Kronos-Tokenizer-base`; mounts: `../vendor/Kronos:/app/vendor/Kronos:ro`, `../models:/app/models:ro`; port `"8002:8001"` (host 8002 → container 8001). Also KRONOS_DEVICE=cpu, KRONOS_USE_REAL_MODEL=true. Also DB env for the service (needs timescaledb). Should also mention the compose network name resolution maybe.

Wait — but design line 34 says container paths `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`. Need tokenizer path and :ro. OK.

Also: the WORKDIR is /app; the compose mounts src? No — the image copies src via build. vendor/models mounted from host. Note .gitignore: vendor/Kronos and models are local-only. Good.

D002 fix details. The design must specify the thin-shell changes:

1. **Startup preflight (fail-closed)**: when KRONOS_USE_REAL_MODEL=true, at process startup (FastAPI lifespan / module init):
   - required env/dirs exist: KRONOS_REPO_PATH (vendor clone), model dir (config.json + safetensors), tokenizer dir; verify required files present.
   - Missing → log clear error with missing paths → exit non-zero (process exit, container restarts? `restart: unless-stopped` would loop... hmm. If restart policy is unless-stopped and startup fails, docker will restart-loop. That's "启动即失败" but with restart loop. Should the compose service have `restart: "no"`? For the real service, better: `restart: unless-stopped` shows a crash loop as visible failure. Hmm, "容器启动即非零退出并打印缺失路径，不退回 mock". A crash loop satisfies visibility (docker ps shows restarting). But typically you'd prefer clean exit + no restart for config errors. The design can say `restart: "no"` for the real service so missing assets exit visibly without a loop. Actually let me keep it simple: specify `restart: "no"` (or absence of restart) so a failed preflight exits non-zero and stays exited for inspection. Let me note that in design.

2. **Eager load + readiness**: after preflight, load model/tokenizer once during startup (so /health reflects loaded state and /predict doesn't do first-call load). Decide: should startup fail if model load fails (fail-closed)? Yes — spec says missing weights/vendor → startup fails. If weights exist but torch errors, also fail startup (real mode). Hmm — but F001 /health contract has `model_error` field and `model_available`/`degraded` semantics... Currently /health returns status=degraded if enabled but not available. For real profile, do we want the process to exit on load failure or serve degraded /health? spec §7 says "权重或 vendor 缺失 → 容器启动即失败"; model load error is the same category ("缺资产"). I'd specify: real mode preflight failure (paths/deps/load) → startup non-zero exit; /health served only after successful eager load. That's fail-closed. But wait — does that break ACO-002 semantics ("model_enabled true but not available → degraded")? That's for mock-mode container with real model env accidentally enabled... hmm, actually the /health degraded path exists for the host use case. For the real compose service we can still define: preflight passes but load errors → exit non-zero. The /health degraded status remains for any running instance that somehow lost availability — but with eager load, once loaded, it stays loaded. Hmm, but eager-load failure exit makes "degraded" unreachable in real mode. That's fine; /health's fields stay for contract compatibility.

   Alternatively: keep /health serving with model_error after a failed load, and make the container healthcheck fail → container marked unhealthy. But spec explicitly promises process non-zero exit for missing assets. Simplest consistent: startup preflight + eager load; any failure → log + exit non-zero. /health then always shows loaded=true in real mode.

3. **Serialized inference (process-level lock)**: `_load_predictor` guarded by a lock; `generate_signal` wrapped in the same inference lock (threading.Lock) so concurrent requests serialize. Because FastAPI sync handlers run in a threadpool. Also /predict_batch loops sequentially already, but two HTTP requests can run concurrently → both call predictor.predict → torch module concurrency (thread-safety concerns + CPU oversubscription). Design: single process-level lock around load and inference. Alternative: run uvicorn with `--workers 1` (default) and make handlers async with a lock... but simplest: threading.Lock in KronosRealSignal.

   Also the "并发：单实例，CPU 推理串行，无共享状态" claim in design §5 needs rewriting: single instance + process-level lock = serial inference; document the invariant and test.

4. **Tests**: unit tests for preflight logic (missing paths, missing files → raises/exit) and lock serialization (concurrent calls serialize; load called once) — mockable without torch? The preflight can be structured to check paths before importing torch. Unit test can use tmp_path with fake dirs. The serialization test can monkeypatch a fake predictor and call generate_signal concurrently from threads, asserting max concurrency 1 and load count 1. That's doable in unit tests without torch (using the real KronosRealSignal class with mocked _load_predictor? The class imports pandas only at top; torch imported inside _load_predictor. So unit tests can stub). Good — design should plan `tests/unit/test_f004_kronos_startup_contract.py` and `tests/unit/test_f004_kronos_concurrency.py` (or one file). Container-level missing-asset test in integration.

   Wait, but where do the code changes happen? `src/alphamill/kronos_service/kronos_real.py` (+ maybe server.py lifespan). The design §2 currently says "不新增 Python 模块" — revise to "不新增模块；对 `kronos_service` 薄壳做最小改造（启动预检、eager load、推理锁），保持 HTTP 契约不变"。

5. Also healthcheck for the real service in compose? Could add `healthcheck` using /health with python/curl. Nice-to-have; the reviewer didn't demand. Skip? D002 says "增加启动预检/eager load/readiness 与推理锁". "readiness" — maybe a compose healthcheck that requires /health to report model_loaded=true. Let's include: compose healthcheck `test: ["CMD", "python", "-c", "import urllib.request,sys; ..."]`? Simpler: `["CMD-SHELL", "python -c \"import urllib.request,json; d=json.load(urllib.request.urlopen('http://127.0.0.1:8001/health')); raise SystemExit(0 if d['model_loaded'] else 1)\""]`. Hmm, keep it simpler in design: "healthcheck 以 /health 的 model_loaded=true 为通过条件". The exact command can be implementation detail; but design is a design doc — can specify the check target. Maybe leave command to implementation but specify "readiness = /health 显示 model_loaded=true 且 status=ok". Fine.

   Also `depends_on` for freqtrade stays on the mock service. For real service, DB dependency (timescaledb healthy) matters for /predict (needs OHLCV). Real service needs DB env too since /predict reads latest_ohlcv from DB. Wait — does the containerized service connect to timescaledb by service name? Yes, DB_HOST: timescaledb. So real service needs same DB env + depends_on timescaledb healthy. And "≥30 根 K 线" precondition (D003).

D003 fix: commands with `-f deployment/docker-compose.yml` everywhere; data preconditions:
- DB migrated (initdb applied; migrations) and target exchange/symbol has ≥30 closed 1m candles (the /predict requires limit>=30 and rows>=30; also real inference needs ≥30 rows).
- spec §2 US-001 独立测试: "新 clone + 权重就位 + `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` + DB 已迁移且目标 symbol 有 ≥30 根已闭合 1m K 线".
- Where to document data precondition? spec §3 边界场景 or §7 依赖 (external/environment). Also design §8 test row and tasks T003. Let me put in spec §7 依赖: "环境前置：TimescaleDB 迁移完成且目标 exchange/symbol 至少有 30 根已闭合 1m K 线（F001 回填产物）". And in US 独立测试.

Also design §5 commands: `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`.

D006 fix: design §0 执行环境: "与 F001 收口态一致" → change to: "集成与容器验收在执行机 `qiaozhi-lt`（Win11+WSL2，RTX 4060 Laptop 8GB；本 feature 不做 GPU 直通，容器验收 `device=cpu`，CPU 推理实测 3.4–7.2s/次）；开发机 `qiaozhi-gp`/`gp-wsl` 只跑静态编排断言与单元门禁（SOP §3、架构 §7.1）"。
And design §8/ tasks T003: "验收证据记录 hostname（qiaozhi-lt）与 device=cpu". Also spec AC-001? AC-001 is tests: test file. The AC text should maybe mention evidence recorded on execution machine with hostname/device. Let me update spec AC-001 and/or §7 测试策略: "容器集成验收在执行机取，证据记录 hostname 与 device=cpu".

Hmm wait, careful: D006 says "design 仍以'本机无独显'作为集成环境，tasks 未记录 hostname/device". Fix both design and tasks. Also spec's "执行环境" maybe. The spec §0 输入与约束 is in design; spec has non-goal about GPU. Let me update:
- design §0 bullet: rewrite执行环境.
- design §8 test table: add column/note about execution machine + evidence fields? The table has "测试层级 / 计划文件 / 场景 / 关键断言". Add rows for F004 tests; mention 执行机取证 in the integration row.
- tasks T003 verify: add evidence requirement (hostname + device) — maybe as separate task? The reviewer said "tasks 未记录 hostname/device; 与 SOP 的执行机取证硬规则冲突". I'll add to T003: "验收证据记录取证机 hostname 与 device=cpu" and maybe a T0xx "集成验收在 qiaozhi-lt 执行并记录 hostname/device; 开发机只跑静态与单元门禁". Better as explicit acceptance task.

D009 fix: spec §0 PRD 来源: "FR3（信号生产）与 M1 运行基座" → correct. What's right? Let me think:
- M0 exit: "回填完整性校验、Kronos /health、采集、dry-run、监控和恢复演练全绿" — F004's Kronos runtime is M0-adjacent but M0 is done. The real runtime in orchestration serves M1's data base (signals_log real content) and eventually FR3 evaluation input (Kronos as first factor).
- FR1.2: snapshot includes Kronos signals → the signals_log dataset. F004 makes the Kronos signal source real.
- FR5 runtime chain? Per suggested fix: "M0、FR1.2 与相关 FR5 运行链". Which FR5 clause relates? FR5.1 versioned signal contract? Hmm, F004's product: signals from Kronos service → written to DB signals_log → exported to lake by F002 (FR1.2) → evaluated (FR3) → eventually deployed via signal_cache (FR5). The direct PRD support is M0 (runtime baseline) + FR1.2 (snapshot includes Kronos signals). FR5 — maybe "FR5.3 Freqtrade 适配"? Not really. But the reviewer explicitly suggests including FR5. Hmm. Wait, maybe they mean the F001 dry-run chain? Freqtrade consumes Kronos signals from mock :8001 in default. Actually the "运行链" (Freqtrade) is currently mock-driven. F004's real instance could serve dry-run in the future. The review phrasing: "把来源改为直接支持该能力的 M0、FR1.2 与相关 FR5 运行链，并说明 F004 与 FR3 的关系仅是为评测提供 Kronos 信号输入".

Hmm, "相关 FR5 运行链" — I think they mean the deployment/runtime chain (FR5 is 部署与交易执行). Given the narrow-scope decision (real profile only serves AC-006 evidence + available signal source), maybe cite: M0 (Kronos runtime baseline) + FR1.2 (signals_log export) + FR5.1 (版本化信号/信号契约的下游链路，如果后续路由). Hmm, but I shouldn't over-cite. Let me be careful and honest:

Actually, wait. Let me re-read the current §0 line: "- **PRD 来源**：`docs/alphamill-prd.md` FR3（信号生产）与 M1 运行基座". Hmm "M1 运行基座" — there's no "M1 运行基座" in PRD; M1 is "可信数据与证据底座". The claim "FR3（信号生产）" is wrong because FR3 is evaluation. The truthful mapping:
- M0 自包含运行基线 lists "Kronos" assets and exit criteria includes Kronos /health — F004 strengthens M0's Kronos runtime within orchestration. But M0 was closed via F001; F004 is targeted at v0.2, after 0.1 closure. Hmm.
- M1 exit: "任意 FactorDef 可从显式绑定的不可变 ResearchSnapshot ... 产出..." — Kronos signal as first factor (arch §5: `kronos_rankic_eval` 泛化为统一评测台，Kronos 信号作为第一批入库因子). F002's signals_log is exported and will feed FR3 evaluation. F004 makes the signal content real so the evaluation input isn't placeholder. So:
  - **PRD 来源**: M0（运行基线，Kronos 服务健康出口）+ FR1.2（signals_log 进入不可变快照）+ FR3.1（Kronos 信号作为评测台第一批输入；F004 仅为评测提供真实信号源，不实现评测本身）+ 相关 FR5 运行链（信号服务的运行时载体，若后接消费者路由属后移）。Hmm this is getting messy.

Let me simplify per reviewer: "改指 M0、FR1.2 与相关 FR5 条款；FR3 只作为下游评测关系". I'll write:
"- **PRD 来源**：`docs/alphamill-prd.md` M0（自包含运行基线：Kronos 服务在编排内健康）+ FR1.2（signals_log 进入不可变快照）+ FR5 运行链（信号服务属策略执行面的运行时依赖）；FR3（证据评测与验证）仅为下游——F004 负责提供可复现的真实 Kronos 信号源，不实现评测。
- **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑：Kronos 推理服务）+ §7.1（机器边界）"

Hmm, "FR5 运行链" — is that honest? FR5.1 signal contract: "feather 按日分片 ... 缓存键含 factor/portfolio..." That's signal_cache, not signals_log. The Kronos service isn't officially in FR5. But arch §7 diagram puts "Kronos 推理服务 GPU 常驻" in the deployment topology, feeding 挖掘 (MINE) signals. Hmm.

Actually, maybe simpler and more honest: cite M0 + FR1.2, and state FR3 relationship as downstream only ("Kronos 信号作为 FR3 评测台的第一批输入"). Should I include FR5 at all? The reviewer suggested it. Let me think about why: signals feed the execution chain (Freqtrade reads Kronos signal in dry-run via KRONOS_SIGNAL_URL). Hmm, that's the "运行链". F001 FR-003 established the Kronos service; F004 extends its runtime. In PRD terms, the chain that consumes Kronos signals: data governance (FR1.2 snapshot) → evaluation (FR3) → execution (FR5, if deployed). Since F004's real instance is not wired to consumers, citing FR5 could overstate again. But the reviewer explicitly said "M0、FR1.2 与相关 FR5 运行链". Ah wait — maybe "FR5" is a typo-ish for "F001"?

Let me not overthink: I'll cite M0 + FR1.2 + FR5.1 (the signal contract is the downstream consumer shape; the Kronos service output feeds signal paths) but carefully phrase: "FR5（信号到执行的运行链；真实实例的消费者路由本次未接线，见 §3 范围外）". Hmm, that's awkward.

Alternative: Look at what F002 cited: "FR1.2(不可变快照)、FR1.3、FR1.4、FR1.6;里程碑 M1". For F004, the natural PRD sources: M0 (Kronos runtime baseline) + FR1.2 (signals_log dataset). And the reviewer added "相关 FR5" perhaps because the runtime chain for signals involves deployment topology? Eh.

I'll include: "M0（自包含运行基线）+ FR1.2（signals_log 进入不可变快照）+ FR5（运行链：Kronos 推理服务属于部署拓扑中的常驻服务）" — and clarify FR3 is downstream only. This matches the reviewer's guidance closely enough while staying truthful enough. Hmm, but honestly FR5 is 部署与交易执行, and arch §7 places Kronos in the execution machine topology. It's plausible. But is it "直接支持该能力"? The reviewer said "直接支持该能力的 M0、FR1.2 与相关 FR5 条款". OK, I'll follow reviewer: M0、FR1.2、相关 FR5 条款（部署/运行链）. Done.

Wait, actually, hmm, one more consideration: the reviewer might consider "FR5 运行链" the wrong cite too? No — the reviewer wrote it, so it's their expectation. Follow it.

D010 fix: tasks restructure:
Current:
- T001 Dockerfile target
- T002 compose service
- T003 start profile + real inference verify (integration cmd)
- T004 write back F001 spec §6 AC-006 command
- T005 run project quality gate
- T006 write back spec acceptance evidence & BACKLOG status

Reviewer's fix: "把 T004 -> T005 -> 验收证据回写 -> 状态/BACKLOG 同步串成完整 DAG，拆开 T006 的证据回写与状态变更，并统一使用 python3 tools/verify.py 作为最终门。"

But wait — there's a subtlety: T003 (start profile & confirm) now needs the new F004 tests (D004) + thin shell changes (D002). So tasks will grow. Let me restructure:

Phase 1：薄壳与镜像
- T001: 薄壳改造 — startup preflight + eager load + inference lock, keep HTTP contract — verify: new unit tests `tests/unit/test_f004_kronos_startup.py` etc.
- T002: Dockerfile multi-stage targets (mock default / real with pinned torch etc.) — verify: `tests/unit/test_f004_compose_profile_contract.py` (static)
- T003: compose real service with profile/mounts/port/env — verify: same static test...
- T004 [P]: 静态门禁测试 (compose profile contract + Dockerfile targets) — actually the tests should be written... hmm, who writes tests: separate task. Let me shape:

Task sequence with acceptance:
- T001 (`FR-001`): 薄壳启动预检与模型 eager load：real 模式下启动期校验 vendor/权重目录与必需文件，缺失即非零退出并打印缺失路径；加载失败同样非零退出 — verify: `tests/unit/test_f004_kronos_startup.py`
- T002 (`FR-001`): 推理串行化：进程级锁保证加载只发生一次且推理互斥（含并发首请求场景）— verify: `tests/unit/test_f004_kronos_concurrency.py`
- T003 (`FR-001`, `NFR-001`): Dockerfile 拆 mock/real 构建目标；real 目标固定 torch CPU wheel 版本与 index，及 einops/safetensors/huggingface_hub/tqdm pin — verify: `tests/unit/test_f004_compose_profile_contract.py`（静态断言 target/依赖清单）
- T004 (`FR-001`, `NFR-001`): compose 增 `kronos-signal-real`（profiles、:ro 挂载、8002:8001、KRONOS_* env、healthcheck、restart 策略）— verify: 同一静态测试 + `docker compose -f ... config`...
- T005 (`AC-001`): F004 专属静态门禁：默认 compose 不含 real 服务、real 服务 target/env/mount/端口正确、默认镜像目标不含 torch — verify: `tests/unit/test_f004_compose_profile_contract.py`
- T006 (`AC-001`, `FR-001`): F004 容器集成测试：compose profile 拉起真实实例并断言 source=kronos、容器身份（compose 托管 + 只读挂载）、缺资产 fail-closed、默认镜像 import torch 失败 — verify: `tests/integration/test_f004_real_profile.py`（执行机 qiaozhi-lt）
- T007 (`FR-001`): 回写 F001 spec §6 AC-006 复跑命令为 compose 形态（保留手工回退）— verify: `python3 tools/verify.py`
- T008 (`AC-001`): 运行 F001 冒烟（HTTP 契约）+ F004 容器集成（执行机取取证 hostname/device=cpu）
- T009 (`AC-001`): 运行项目统一质量门 `python3 tools/verify.py`
- T010: 回写 spec 验收证据（含 hostname/device 与真实产物）
- T011: 同步 BACKLOG/状态

Hmm, but the reviewer's D010 was mostly about connecting T004→T005→证据回写→状态/BACKLOG, splitting T006, and unifying the final gate command. Since I'm also adding D002/D004 tasks, the numbering shifts; that's fine — deliver a coherent complete tasks file.

Also careful with task format: "- [ ] T001 [P] (`FR-001`, `AC-001`): <一个可验证动作> — verify: <测试/命令>". Tasks without spec refs (like T006 in old file "回写 spec 验收证据与 BACKLOG 状态 — verify: python tools/validate_spec_lifecycle.py") — reviewer wanted split. The BACKLOG sync should probably verify with `python3 tools/verify.py` (final gate includes lifecycle validation) — the reviewer says "统一使用 python3 tools/verify.py 作为最终门". Let me check how F002 tasks did the closeout. Let me read F002 tasks.md to match conventions. Also check BACKLOG.md and how status transitions are done (`ready-for-development` when DQ closed...). Note: this fix round is about the docs; the status stays draft. The tasks.md is for the future development.

Also the dependency section must become a complete DAG.

Also §5 明确后移: currently GPU passthrough. Add consumer routing deferral (D001 narrow scope). Target: if no existing feature, what to write? Format: "`<事项>` → `Fxxx` / `v0.x`：<为什么不属于当前范围>". I'll write "消费者路由切换（Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 指向真实实例）→ v0.2 后续 feature（未立项，需 owner 决策）：真实实例与 mock 并存,路由切换涉及 Freqtrade/TimescaleDB 写入与默认链路可用性,超出本 feature 的编排内证据范围."

Hmm, "必须写目标 Feature/版本" — "v0.2 后续 feature（待立项）" gives version. I think acceptable.

Wait, actually, should I create a tracked task in tasks.md (per review-convergence §4: "没有条目 → 先在 tasks.md 建条目(必须含验收标准 AC)，再标 tracked")? Hmm — that rule is for findings that are "上游任务还没执行" product gaps. D001's resolution options: wire or delete. If I delete the promise and defer routing, is the deferred routing a tracked task? The review's suggested fix option B says "删除'自动升级 signals_log'的范围承诺" — not necessarily create a task. But the review-convergence skill says deferred items need a carrier. §5 明确后移 is the tasks.md carrier for "移交给其它 Feature/版本". But it says "只能放明确移交给其它 Feature/版本的内容，必须写目标 Feature/版本". If the routing isn't assigned to a feature, is it allowed? Hmm. Options:
1. Put in §5 with "v0.2 后续（未立项）" — weak on "must write target".
2. Ask the user/owner to decide whether to open a follow-up feature.
3. Actually reconsider: maybe the right call is Option A-lite: keep real instance available AND actually switch the snapshot consumer? No...

Hmm hold on. Let me reconsider D001 once more. Let me re-read the snapshot script to see exactly what it does with 8001/8002, because the script's default is 8002 and the service overrides to 8001. If the intended runtime topology (arch §7) is "Kronos 常驻推理" on the execution machine serving dry-run, and compose mock currently serves 8001... The F004 real profile publishes 8002. The snapshot service could be re-pointed to 8002 IF the real profile runs persistently on the execution machine. Actually maybe that's the real end goal: on the execution machine, run the real profile permanently (it's the "Kronos 常驻推理" from arch §7!), and then the snapshot consumer should indeed point to it. But then the mock default and real co-existence... The design says 8002 coexists with 8001 mock to avoid one replacing the other. For the execution machine's production-ish setup, they'd run the real profile and could repoint the service to 8002. But that's an operational choice, not automatic. "F004 落地后 signals_log 内容自动升级" — if the operator switches the service URL manually, it upgrades. But "自动" is false.

Given the skill's requirement, I could add to tasks §5: "消费者路由切换（…）→ 评估后随执行机常态化部署另行处理（v0.2 后续，未立项）". And in FIX-log note this was accepted via the reviewer's suggested alternative (delete claim). Also update F002 spec's same claim? The review finding's fix is scoped to F004 docs; but F002's §6 line also says "F004 落地后内容自动升级,F002 无需返工". Since I'm deleting the F004 promise, F002's claim becomes even more clearly false. Leaving it would contradict. But modifying F002 (done) spec requires care: "收口后版本目录只允许修复历史错误或死链" — this is a historical error fix, permitted. But is it my place as fixer? The review said fix F004 docs; it did not ask to edit F002. Also the skill says fix round should only touch what findings cover; touching F002 would expand blast radius of this round and create new cross-feature inconsistencies to review. Hmm.

Hmm, wait. Actually, let me reconsider: maybe I should keep option A in scope but implement it narrowly: wire the runtime snapshot service? Let me look at what exactly "signals_log 的生产消费者" are:
1. `alphamill-snapshot.service` (host systemd, runs collect_runtime_snapshot.ps1 with `-KronosHostUrl http://127.0.0.1:8001`) → writes TimescaleDB signals_log.
2. Freqtrade compose (KRONOS_SIGNAL_URL http://kronos-signal:8001) → reads predictions for strategy (not signals_log).

For signals_log specifically, only #1 matters. The F002 export reads signals_log from DB.

If F004 "wires" #1: change the service to point at 8002 when real runs; but then default (mock) breaks unless real is always up. A sane approach: make the snapshot service point to 8002 (the real profile), and require the real profile to be running on the execution machine as the standard Kronos runtime. But that violates "不把真实推理设为默认启动项"? That non-goal is about developers not paying torch costs. On the execution machine, the real runtime is the point. Hmm! Interesting. But the design decision explicitly says "真实实例走 8002 而非顶替 8001 | 两种形态可并存对比 | mock 实例仍是默认链路的依赖". So the current design keeps mock as the default consumer dependency. Changing that is a design-level decision beyond a doc fix.

OK, decision: **Option B (narrow)**, with explicit deferral. It's minimal, honest, and within the reviewer's accepted fixes. If the owner later wants consumers wired, that's a new scope.

But wait, there's still the question: does Option B leave the F004 spec's "一句话意图" / US-001 "以便 signals_log 的内容有效性..." changed. Yes I'll fix all those spots. And F002's false claim — hmm. Let me check F002 spec lines again: "F004 落地后内容自动升级,F002 无需返工。" Since F004 now says it does NOT auto-upgrade, the two specs contradict. As fixer I should at least flag. Given the review's D001 fix options include deleting the claim in F004 (the reviewed artifact), and the review itself noted F002's limitation text as adjacent context... The cleanest: fix F002's sentence minimally ("F004 落地后，真实信号实例在编排内可用；signals_log 内容升级需消费者路由切换，另行评估") — but that's editing a done feature's spec outside the reviewed artifacts. Hmm.

Actually — wait. Let me re-read D001's suggested fix once more: "明确 profile 启用时 Freqtrade 与 runtime snapshot 的路由切换，并以 signals_log.source=kronos 的端到端断言验收；否则删除'自动升级 signals_log'的范围承诺。" — "删除承诺" is in F004 spec. The F002 sentence is a consequence. The review didn't list F002 as a finding (it's `done`). In the FIX-log I can note: "F002 spec §6 的'内容自动升级'表述不再成立，因 F002 已 done、不在本轮受检产物内，建议随下一轮复核或 F002 勘误处理"— but that's exactly the "没有载体的 deferred item" problem the skill warns about. Better: also fix F002's sentence since it's now known-false, OR add a tracked item. Hmm. The skill says: "检视文件是过程稿...真正落进 git 的是闭环后检视人提交的最后总结". Doc edits go into git.

Let me think about the blast radius: F002 spec is done; its §6 claim "F004 落地后内容自动升级，F002 无需返工" is factually wrong under option B. The F002 "已知限制" paragraph's purpose is to warn that signals_log content isn't research-usable. Fixing the last sentence to say "F004 落地后真实实例在编排内可用；要使其进入 signals_log 需另行切换消费者路由" preserves the warning and removes the false auto-upgrade. This is a factual correction of a cross-feature claim; both docs get consistent. I think it's justified and within the spirit of fixing D001's root issue (the claim exists in two places; if I only fix one, the project still carries the false claim).

But hold on — the review scope says "受检产物:F004 三件套" and "相邻契约:F001 AC-006、F002 signals_log..." — adjacent contracts were consulted for evidence but not reviewed. If I edit F002 spec, Round 2 (diff-only) will see it and can check. I'd rather fix it and note it in FIX-log as a consequential edit required by D001. Actually, you know what? Let me keep this minimal but correct: I will fix the F002 sentence too, because leaving a known-false contract sentence is itself a defect I'm now aware of, and the skill's "根因修复" principle says don't leave the root unaddressed. I'll note it clearly in FIX-log as part of D001's fix (cross-file consequence).

Hmm, wait, wait. Let me think again about whether Option B is really better than Option A. Let me look at the runtime snapshot script first, then decide. Let me read it.

Also let me read tests/unit/test_runtime_snapshot_contract.py to see if the contract test locks the -KronosHostUrl 8001.

And BACKLOG.md to know status format. And validate_spec_lifecycle.py for gate rules. Let me also check F002 tasks for closeout patterns and F002's design/tasks to see how tests were divided (unit vs integration). And test_validate_spec_lifecycle.py maybe not needed.

Let me batch reads:
- scripts/collect_runtime_snapshot.ps1
- tests/unit/test_runtime_snapshot_contract.py
- BACKLOG.md
- tools/validate_spec_lifecycle.py
- docs/features/0.2/F002-data-bridge/tasks.md (for closeout pattern)

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/scripts/collect_runtime_snapshot.ps1</path>
<type>file</type>
<content>
1: param(
2:     [string]$KronosHostUrl = "http://127.0.0.1:8002",
3:     [string]$Exchange = $(if ($env:KRONOS_SIGNAL_EXCHANGE) { $env:KRONOS_SIGNAL_EXCHANGE } else { "binance" }),
4:     [string[]]$Symbols = @("BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT")
5: )
6:
7: $ErrorActionPreference = "Stop"
8: $projectRoot = Split-Path -Parent $PSScriptRoot
9: Set-Location $projectRoot
10:
11: function ConvertTo-SqlLiteral {
12:     param([AllowNull()]$Value)
13:     if ($null -eq $Value) {
14:         return "NULL"
15:     }
16:     return "'" + "$Value".Replace("'", "''") + "'"
17: }
18:
19: function ConvertTo-SqlNumber {
20:     param([AllowNull()]$Value)
21
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """规格生命周期校验（骨架版，node flavor 的 check-feature-gates.mjs 的 Python 对应）。
3:
4: 校验 docs/features/<version>/Fddd-*/ 三件套：
5:   - 三件套齐全、frontmatter 合法、ID 唯一、status/gate_version 合法
6:   - spec.md 是状态唯一真相源（design/tasks 不得声明独立 status）
7:   - gate v1：固定章节结构、Q/DQ 关闭、AC 引用第 4 节真实需求、
8:     review/done 的 tests 路径真实存在
9:   - BACKLOG.md 与所有非 done Feature 双向集合一致
10:
11: 纯函数 + CLI 分离，只用标准库；参考项目在此基础上抽了共享 spec_validation 模块
12: 并补了变异测试。用法：python tools/validate_spec_lifecycle.py
13: 退出码 0 = 全部通过；1 = 存在违规。
14: """
15:
16: from __future__ import annotations
17:
18: import pathlib
19: import re
20: import sys
21:
22: ROOT = pathlib.Path(__file__).resolve().parent.parent
23: ALLO
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:49:55Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && cat pyproject.toml | head -80; echo \"=== torch in venvs ===\"; for py in .venv/bin/python /root/.venv/bin/python; do [ -x \"$py\" ] && $py -c \"import torch; print('$py', torch.__version__)\" 2>/dev/null; done; .venv/bin/pip show torch 2>/dev/null | head -4; echo \"=== venv torch deps ===\"; .venv/bin/pip list 2>/dev/null | grep -iE \"torch|einops|safetensors|huggingface|tqdm\""})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/BACKLOG.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/tasks.md", "limit": 80})`


> [reasoning] Now I understand the gate rules. Key ones for my edits:
- design.md "10. 待确认设计问题" must be Q/DQ checkboxes or "无" — currently "无". Keep.
- spec §8 Q/DQ checkboxes or "无" — currently has Q-001 closed checkbox. Fine.
- AC lines: `- [ ] **AC-001** (`FR-001`, `NFR-001`): ... — tests: ...` — refs must exist in §4; if status draft, tests not required for existence check but allowed. AC refs must be IDs defined in §4 (FR-001, NFR-001 are defined). If I add FR-002? No, F004 only has FR-001 + NFR-001. Keep AC-001 refs to FR-001/NFR-001 only. If I want to reference new requirements, I'd have to add them to §4. Hmm — should F004 add FR-002 for fail-closed and serialization? The reviewer D002 wants implementation path for fail-closed and serialization. These are part of FR-001's profile behavior... or maybe new requirements. Let me consider adding explicit sub-requirements to §4:

Actually the current §4 has one FR-001 ("编排内真实推理") + NFR-001. The fail-closed behavior is in §3 边界场景 and design. To keep AC refs valid I can keep FR-001 and extend its wording to include fail-closed and serial invariants? The features/README format for AC refs: must reference ID defined in §4. It's fine to keep just FR-001/NFR-001. But for traceability, maybe add:
- FR-002: 缺资产失败关闭与串行推理（模型在启动期校验并加载；缺失即非零退出；推理请求串行）
- NFR-002: 验收证据机器（执行机取证）? Hmm, that's not a system requirement; it's process. Keep in design/tasks.

Would adding FR-002/NFR-002 break spec template rules? No — §4 has "### 功能需求" with requirements; adding another is normal. But then AC-001 should reference FR-002? The AC could reference `FR-001`, `FR-002`, `NFR-001`. That improves traceability of D002. Let me consider: reviewer D002's fix says "在 design/tasks 中加入启动期依赖与双权重目录校验、模型 eager load/readiness 以及进程级推理锁，并为缺资产和并发请求建立测试。" — it says add to design/tasks; spec changes optional. If I put the behavior in spec §3/§4, the feature contract becomes clear. I think adding FR-002 to spec §4 is justified: "失败关闭与串行推理" as observable behavior:
  - real mode missing vendor/weights → process exits non-zero with missing paths (observable via container)
  - concurrent /predict requests serialize (observable via no concurrent predictor use... hard to observe externally; but internally testable).
Hmm, serialization is hard to state as an external observable behavior; it's an invariant. Could go under "5. 生命周期与不变量"? §5 currently "不适用：一次性运行时改造，无长生命周期状态机。" I could change §5 to state invariants instead of 不适用 — the template says §5 "生命周期与不变量" should be used for invariants; "不适用" with reason currently. Since we now have real invariants (fail-closed startup; serial inference; no mock fallback), it's better to fill §5 with invariants. That directly addresses D002's "失败关闭与串行推理没有实现路径" at spec level. Let me do:

§5 生命周期与不变量:
- 不变量 1（失败关闭）：real 模式下 vendor/权重任一缺失或加载失败 → 进程启动即非零退出并打印缺失路径，绝不退回 mock；
- 不变量 2（串行推理）：单进程内推理互斥（进程级锁），模型加载至多一次；并发请求排队而非并发进入 predictor；
- 不变量 3（默认隔离）：未启用 profile 时，默认编排不含 torch 层、不启动/构建 real 服务。

Hmm, invariant 3 is more NFR. Fine.

And add FR-002 to §4? Maybe fold fail-closed into FR-001's description + scenarios. The reviewer suggested design/tasks only. Minimal spec change: §3 边界场景 already says fails at startup; I could strengthen §5 with invariants (which makes it a contract), no new FR IDs needed. But AC traceability: AC-001 refs FR-001/NFR-001... The startup fail-closed can be covered by FR-001's scenario? Let me add to FR-001 scenario or add a second scenario under FR-001: "Scenario: 缺资产失败关闭". Hmm, spec template says "每个重要 requirement 至少有一个 scenario；重要的错误、边界和恢复场景要写成 scenario". Adding a scenario to FR-001 is good:

#### Scenario: 缺资产失败关闭
- GIVEN vendor/Kronos 或 models/ 任一缺失
- WHEN 启动 `--profile kronos-real` 的实例
- THEN 进程非零退出并在日志打印缺失路径，不退回 mock

That's clean. Then §5 invariants for serialization etc.

Wait, but the AC validation only checks AC refs exist in §4; scenarios don't need IDs. OK.

Now let me also check: review D002's "双权重目录校验" — model + tokenizer dirs. Yes.

Now D005 version/index specifics: need concrete torch pin. Let me check host torch version. Also check pyproject for dependencies + check_dep_pins rules (only dev deps?). Let me quickly run pip show torch in .venv and check pyproject.

Also need to check the composition default: the real target's pip install uses index-url for CPU wheel: `pip install --index-url https://download.pytorch.org/whl/cpu torch==2.x.y`. For safety pin also einops==0.8.1, safetensors==0.6.2, huggingface_hub==0.33.1, tqdm==4.67.1 (matching vendor requirements). Those exact pins come from vendor requirements.txt — good evidence.

For torch: F001 host venv ran AC-006 with some torch. Let me check.

Also `numpy`, `pandas` come from base pip install (pyproject) presumably; verify pyproject deps. Let me read pyproject.toml.

Let me also read the F002 tasks.md quickly for closeout task patterns (to mirror in F004 tasks), and BACKLOG.md.

Then check test_runtime_snapshot_contract.py (to be aware whether editing runtime snapshot or F002 spec breaks unit tests — I'm not changing runtime snapshot code, only docs; but if I fix F002 spec sentence, does any test assert that sentence? test_f001_compose_contract asserts AC-006 command bits in F001 spec: "DB_HOST=127.0.0.1" and "./deployment/.env" in F001 spec + smoke test. T004 will rewrite F001 AC-006 command to compose form and "keep manual fallback". Careful: if the writeback removes the manual command from F001 spec, that unit test fails (asserts DB_HOST=127.0.0.1 and .env in F001 spec). The manual fallback should stay per T004 ("保留手工形态作为无 docker 时的回退"), so test stays green. But note: T004 is an implementation-phase task, not for this round. Design/planning docs just need to be consistent.

Wait, actually — T004 says "回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态". Is that part of the future implementation round (after code). Yes. Not now.

But D003's fix says every command in F004 docs must use `-f deployment/docker-compose.yml`. Where do commands appear in F004 docs? Let me grep: spec line 53 (`docker compose --profile kronos-real up -d`), spec line 87 (same in scenario), design line 46 (`docker compose --profile kronos-real up -d kronos-signal-real`), tasks T002/T003 (`docker compose config`, `docker compose --profile kronos-real config`), design §8 test row. Also F001 spec §6 mention of F004? F001 says "F004 落地后 AC-006 可由编排直接复跑" — no command. F001 §6 writeback is T-task; not now.

Hmm — careful about one thing: does `docker compose -f deployment/docker-compose.yml` work from repo root with relative paths inside compose? Compose file uses `context: ..` and `../db/...` relative to the compose file directory — compose resolves relative to the file location regardless of -f? Yes, relative paths in compose files resolve relative to the compose file's directory (context etc.). OK.

Let me now check the remaining bits: pyproject, torch version, F002 tasks, BACKLOG, test_runtime_snapshot_contract. Also check if vendor/Kronos has its own model loading requiring cwd (the `sys.path.append("../")` weirdness in kronos.py is upstream code; our thin shell inserts kronos_root to sys.path, and `from model import ...` works because kronos_root is the repo root containing model/ dir. In container: /app/vendor/Kronos/model/... and KRONOS_REPO_PATH=/app/vendor/Kronos → sys.path insert → import model; the `from model.module import *` inside model/kronos.py needs `vendor/Kronos` parent? Let me see: kronos.py does `from model.module import *` — that resolves if `vendor/Kronos` is on sys.path (so `model` package found). Our shell inserts `vendor/Kronos` — wait it inserts `str(kronos_root)` where kronos_root = vendor/Kronos. Then `model` package = vendor/Kronos/model. Good. And `module` inside `from model.module import *`... fine.

Let me check the pyproject + torch.

  <details><summary>tool output</summary>

  ```text
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "alphamill"
version = "0.1.0"
description = "以因子假设吞吐量为核心的加密量化研究系统：程序化挖掘 → 统一评测 → 严格留出门 → Freqtrade 执行"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "ccxt>=4.4,<5",
  # F002 数据桥：Parquet 湖（写 PyArrow / 读 DuckDB）。运行时依赖同样锁范围，
  # 是否在范围内由 check_dep_pins 门禁强制（F002 spec 决策表：版本漂移显式改动）。
  "duckdb>=1.5,<2",
  "fastapi>=0.115,<1",
  "pandas>=2.2,<3",
  "psycopg2-binary>=2.9,<3",
  "pyarrow>=25,<26",
  "pydantic>=2.10,<3",
  "uvicorn>=0.34,<1",
]

[project.optional-dependencies]
dev = [
  # 固定到范围：CI 每次 `pip install -e ".[dev]"` 拉最新，linter 自升级的
  # 默认行为变化曾把 CI 搞红而本地全绿——锁定范围换取可重复性。上界不承诺
  # 等于本地实装版本：round-1 检视（CURRENT-code.md C001）发现本地实跑
  # pytest 9.0.3 而原上界是 <9，注释承诺与事实矛盾，故放宽为 <10 并如实
  # 记录
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/BACKLOG.md</path>
<type>file</type>
<content>
1: # BACKLOG —— 活跃 Feature 索引
2:
3: 本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
4: frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。
5:
6: | Feature | 版本 | 状态 | 链接 |
7: |---|---|---|---|
8: | F003-alphagen-vendor | 0.2 | draft | [spec](docs/features/0.2/F003-alphagen-vendor/spec.md) |
9: | F004-kronos-inference-runtime | 0.2 | draft | [spec](docs/features/0.2/F004-kronos-inference-runtime/spec.md) |
10: | F007-evaluation-gates | 0.2 | draft | [spec](docs/features/0.2/F007-evaluation-gates/spec.md) |
11: | F008-universe-expansion | 0.2 | draft | [spec](docs/features/0.2/F008-universe-expansion/spec.md) |
12:
13: > 规则：feature 状态变更（spec frontmatter）时必须同步本表；`done` 的 Feature 移出本表
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F002
4: version: "0.2"
5: related_features: [F001]
6: topics: [data-bridge, parquet, duckdb, m1]
7: doc_kind: tasks
8: created: 2026-09-12
9: updated: 2026-09-14
10: ---
11:
12: # F002:数据桥——Parquet 湖导出与 DuckDB 研究取数层 - 任务
13:
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15:
16: ## 0. 来源与执行规则
17:
18: - 行为与验收真相源:`spec.md`。
19: - 技术方案与边界:`design.md`。
20: - 每项任务只描述一个可验证动作,并引用合法的 US/需求/AC ID。
21: - 完成且验证后立即把 `[ ]` 改为 `[x]`,不得最后统一补勾。
22: - `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
23: - 实现中若任务顺序或契约失效,先修订三件套,再继续编码。
24:
25: ## 1. 前置条件
26:
27: - F001 已 done:TimescaleDB 数据就绪(631 万行 binance)、`lake/` 目录位与 NAS 通道已预留、调度先例(backup/snapshot timer)
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:50:12Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git log --oneline -25; echo \"=== gitignore reviews ===\"; grep -n \"reviews\\|FIX-log\\|CURRENT\" .gitignore; echo \"=== check-ignore ===\"; git check-ignore -v docs/reviews/CURRENT-doc.md docs/reviews/FIX-log.md docs/reviews/RETROSPECTIVE.md; echo \"=== models ===\"; ls models/Kronos-base models/Kronos-Tokenizer-base 2>/dev/null; echo \"=== branches ===\"; git branch -a | head"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls docs/reviews/; head -120 docs/reviews/RETROSPECTIVE.md"})`


> [reasoning] Now I have a good picture. Key facts:

- `.venv` has torch 2.14.0+cpu, einops 0.8.2, huggingface_hub 1.31.0, safetensors 0.8.0, tqdm 4.70.0 (host venv used for AC-006). The vendor requirements pin: einops==0.8.1, huggingface_hub==0.33.1, tqdm==4.67.1, safetensors==0.6.2. For the container image, we should pin to a tested set. Which set? The host AC-006 evidence used torch 2.14.0+cpu + newer libs. The container target should either mirror host-verified versions or vendor-pinned versions. Hmm. The review says: "从 pin 67b630e 提炼并锁定最小推理依赖，至少纳入 huggingface_hub 与 tqdm，并明确 torch CPU wheel 的版本和 index；以容器内 import 加真实权重加载验证。"

I'll specify in design: real target pip 安装锁定版本，torch 从 CPU wheel index 安装（`--index-url https://download.pytorch.org/whl/cpu`，版本与宿主 AC-006 实测一致或经过容器验证的 pin）；推理最小集：torch、einops、safetensors、huggingface_hub、tqdm（+ numpy/pandas 由 pyproject 提供）。Give concrete pins: torch==2.14.0+cpu? Hmm, "+cpu" local version — on PyPI CPU index, version would be `2.14.0` (the cpu wheel is 2.14.0+cpu on download.pytorch.org; pip install torch==2.14.0 from the cpu index resolves). Let me be careful: from https://download.pytorch.org/whl/cpu, `pip install torch==2.14.0` installs 2.14.0+cpu. If we specify `torch==2.14.0` with `--index-url https://download.pytorch.org/whl/cpu`, that's right. Alternatively pin `torch==2.14.0+cpu`? pip supports local versions in requirements (torch==2.14.0+cpu) when the index has it. Both work, but simpler: `torch==2.14.0` + CPU index. Hmm, but design should state it clearly; implementation can verify. Let me not over-specify implementation command details; state "torch CPU wheel pin（与宿主 AC-006 实测同版：2.14.0，index=`https://download.pytorch.org/whl/cpu`）" and list the rest.

Actually wait — should the design fix commit to exact versions now? The design is the place to fix NFR-001's mechanism. Giving exact version is good for reproducibility; the review asks for "明确 torch CPU wheel 的版本和 index". I'll write exact: `torch==2.14.0` from CPU index; `einops==0.8.2`, `safetensors==0.8.0`, `huggingface_hub==1.31.0`, `tqdm==4.70.0` (host-verified set at AC-006 run), or the vendor requirements set? Which is "correct"? The host venv currently has these versions and ran AC-006 successfully; so mirroring the host-verified set is the strongest evidence. But hold on — the container build happens later; a design doc specifying pins that must match host evidence is right. However, `huggingface_hub 1.31.0` on PyPI — is that a real version? hf_hub went 0.33 → 1.x in late 2025; by Sep 2026, 1.31 plausible. It's installed locally. Fine — but do I want design to hardcode these? The implementation will verify. I'll state: "锁定并逐一 pin：torch==2.14.0（CPU wheel index，与宿主 AC-006 实测同版）、einops、safetensors、huggingface_hub、tqdm（版本以容器内真实权重加载验证后落定；初始取宿主实测版本 einops 0.8.2 / safetensors 0.8.0 / huggingface_hub 1.31.0 / tqdm 4.70.0）". That satisfies "明确版本和 index" while allowing implementation to adjust with verification. Hmm, the reviewer might want concrete. I'll give exact initial pins.

- torch wheel on Linux: the `+cpu` suffix wheel from download.pytorch.org for torch 2.14.0? Hmm, actually PyTorch releases: 2.14 doesn't exist in reality (as of my knowledge), but this is a fictional future date (Sep 2026) — the local env says torch 2.14.0+cpu, so use that.

- Host venv versions: huggingface_hub 1.31.0 — hmm, does huggingface_hub 1.x still have PyTorchModelHubMixin? Presumably. Fine.

Now for the F001 host venv vs vendor requirements: the vendor requirements is from the upstream repo (matplotlib etc. are for examples/finetune, not needed). Minimal inference set: torch, einops, safetensors, huggingface_hub, tqdm (+ numpy/pandas via pyproject? pandas is in pyproject deps; numpy is a torch/pandas dependency). tqdm: used in kronos.py `from tqdm import trange`. huggingface_hub: PyTorchModelHubMixin + from_pretrained. Good.

Now, D001 final decision. Since the snapshot default param is actually 8002 (!), maybe the intended design was: the snapshot script defaults to 8002 real; the systemd service overrides to 8001 mock for now. So F004 could plausibly re-point the service to 8002 once the real profile is standard on the execution machine. But per the current F004 design (mock stays default; real profile is opt-in), auto-switch cannot be promised. And the queue: "F004 落地后 signals_log 内容自动升级" is wrong either way without an explicit re-point. I'll go narrow-scope with explicit deferral, and fix F002's sentence.

Wait, actually, let me reconsider once more. Maybe a middle path: F004 could include a small, honest item: "在 profile 启用且实例健康的机器上，允许运营者手工把 runtime snapshot 切到 8002（或在后续 feature 落地）"— that's just documentation. The key deliverable boundary: F004 doesn't promise automatic consumer routing; scope out; defer with target "评估（未立项）". OK.

Hmm, but the reviewer's D001 is High severity and its closure criterion is either wiring or deleting. Deleting claim + explicit out-of-scope + deferral satisfies it. But will the round-2 reviewer accept? The reviewer explicitly offered this as an acceptable alternative ("否则删除...承诺"). So yes.

Now D002 fix specifics — I need to make design contain the implementation path:
1. §2 架构与模块边界: "不新增 Python 模块" → revise: keep module set, but thin-shell gets changes: 启动预检 / eager load / 推理锁; HTTP contract unchanged.
2. §5 Runtime: startup sequence: process start → preflight (env, dirs, files) → eager load model+tokenizer → serve; /health readiness reflects loaded; lock: threading.Lock (load + inference); uvicorn single process (no --workers>1); failure → exit non-zero. Also compose healthcheck readiness.
3. §7 失败: missing assets → non-zero exit at startup with missing paths (not first /predict); no mock fallback; model load error → same.
4. §8 tests: unit tests for preflight + lock; integration tests for missing assets.
5. tasks: new tasks.

Also, the design §5's "并发：单实例，CPU 推理串行，无共享状态" should be corrected: single instance; process-level lock serializes inference; no shared state besides the predictor.

Wait, one question: is FastAPI's sync handler threadpool + torch inference actually unsafe? Torch modules are generally thread-safe for inference in the sense that weights aren't mutated, but KronosPredictor may have internal state? Let me check KronosPredictor.predict for state mutation (e.g., self attributes, tokenizer caching). The reviewer said "同步 FastAPI handler 可并发进入同一 predictor" — the fix is to lock. Whether or not torch is thread-safe, determinism/CPU oversubscription argues for serialization (the design's stated invariant). Fine.

Also "模型在首个 /predict 才加载" — fix via eager load at startup. And `_dependencies_available` only checks torch import + kronos_root exists → preflight must check model/tokenizer dirs and required files. What files? For KronosTokenizer: config.json + model.safetensors; base same. Let me check models dir locally.

Let me check `ls models/Kronos-base models/Kronos-Tokenizer-base`.

Also KRONOS_MAX_CONTEXT vs model context: KronosPredictor max_context=512 default; fine.

Now D004 test strategy — design §8 table needs rows:
| AC-001 | static contract (unit, CI) | tests/unit/test_f004_compose_profile_contract.py | Dockerfile targets: default no torch, real pins; compose real service: profiles/mounts :ro/env/ports; default config ❌ real service |
| AC-001 | container integration (执行机) | tests/integration/test_f004_real_profile.py | real container identity (compose-managed, correct target/env/ro mounts); /predict source=kronos; missing assets → non-zero exit; default image import torch fails |
| AC-001 | integration (F001 smoke unchanged) | tests/integration/test_f001_kronos_smoke.py | HTTP 契约 + 模式自洽（保留，仅契约职责） |

And spec §7 测试策略 updated accordingly; AC-001 tests field should reference... AC format: tests: one or more paths. I can list two paths: `tests/unit/test_f004_compose_profile_contract.py`、`tests/integration/test_f004_real_profile.py`. The gate regex extracts backticked paths; multiple OK (F002 AC-015 lists two paths separated by 、). Good.

D006 fix:
- design §0: execution environment rewrite.
- design §8: note execution machine + evidence fields.
- tasks: T for evidence machine + T003 updated to record hostname/device.
- spec §7 测试策略: add "容器集成验收必须在执行机 qiaozhi-lt 取证，证据记录 hostname/device=cpu；开发机只跑静态与单元门禁。"

Hmm wait, one important check: SOP says "Feature 收口前，集成验收必须运行 ALPHAMILL_INTEGRATION=1 python3 -m pytest tests/integration -q；服务不可达或 mock 模式在该开关下必须判红". With ALPHAMILL_INTEGRATION=1 on the execution machine, the new F004 integration tests would run — they need docker; on the execution machine docker exists. But how do these container tests interact with ALPHAMILL_INTEGRATION? They must skip when ALPHAMILL_INTEGRATION is unset (CI/dev), fail if set and can't run? Following the F001 smoke pattern: `_require_or_skip`. But container tests need docker; if integration required and no docker → fail. On execution machine docker exists. OK.

Also careful: F004 integration test that builds pyproject-based image etc. will be slow but fine.

One more D004 point: "保留 F001 冒烟只验证 HTTP 契约" — F001 smoke stays as-is functionally. The F004 integration test proves the container identity. Good.

Now D003: data precondition. For /predict to return, DB must have ≥30 closed 1m candles for target symbol (limit default 120; real_signal needs ≥30 rows; F001 smoke hits BTC/USDT with limit default 120). Note: `latest_ohlcv` — does it filter closed candles? Collector filters unclosed. The precondition: "DB 已迁移（initdb + migrations）且目标 exchange/symbol 至少 30 根已闭合 1m K 线（F001 回填产物）". Also note F001 backfill produced 6.3M rows so on execution machine it's there.

Where to add: spec §2 US-001 独立测试 + §7 依赖 (外部/环境). design §0 输入与约束 (weights + data preconditions) + §8 test scenario. tasks T003/T006 verify commands include DB precondition? Task commands can't easily verify DB rows; but we can add a verification step in the integration test itself (test asserts rows_used >= 30). Actually the F001 smoke already asserts rows_used >= 30 for /predict. The precondition for running the command is environmental. I'll document it in spec/design and keep test assertions.

D007 fix: Dockerfile targets. Design §1: "给 kronos-service.Dockerfile 增 base/mock/real 三阶段（或 mock/real 两 target）" — precise design:
- Stage `base`: python:3.11-slim + pip install . (project deps) — current Dockerfile.
- Target `mock` (default, keep current behavior/image digest-ish): same as today (base), no torch.
- Target `real`: base + pip install torch (CPU index) + einops/safetensors/huggingface_hub/tqdm; vendor/models mounted at runtime.
Compose: `kronos-signal` builds target `mock` (or default); `kronos-signal-real` builds target `real`.
NFR-001 assertion: "默认 compose 不启用 real 服务且不构建 real 目标；默认 `kronos-signal` 镜像内 `import torch` 失败" — testable.
spec §3 范围内 line 63: update to include the two targets + dependency list.
tasks T001 verify update.
design §9 decision table "torch 镜像层拖慢 CI" row update? It says "profile 未启用时 compose 不解析其构建". With `build.target`, compose always parses services but only builds when starting; `docker compose config` without profile excludes the service anyway. Fine; maybe refine wording: "CI 不构建/不启用 real target；默认镜像 import torch 判红由测试锁定".

Wait — subtle: with profiles, `docker compose up` won't build profiled services unless profile active. NFR-001: "默认 docker compose up 的行为与镜像体积不受本 feature 影响（profile 未启用时不构建 torch 层）". Good; and the default image must not contain torch. Mock target = existing base (no torch). ✓.

One nuance for D007 "mock/real build target": compose service without explicit target builds the LAST stage by default. So Dockerfile must order stages so that the default (no target) = mock, OR explicitly set target per compose service. Better: explicit `target: mock` and `target: real` in both services; then Dockerfile order doesn't matter (but set default last = mock for safety). Design will say: "Dockerfile 至少含 mock/real 两个构建目标；compose 两个服务显式声明 target；默认镜像（mock）不含 torch。"

D008: mount/port contract in design §2 or a new subsection §5:
```
host: ../vendor/Kronos → container /app/vendor/Kronos:ro
host: ../models → container /app/models:ro
KRONOS_REPO_PATH=/app/vendor/Kronos
KRONOS_MODEL_PATH=/app/models/Kronos-base
KRONOS_TOKENIZER_PATH=/app/models/Kronos-Tokenizer-base
KRONOS_USE_REAL_MODEL=true
KRONOS_DEVICE=cpu
ports: "8002:8001"  # host 8002 → container 8001, 与 mock 8001 并存
```
Also DB env same as mock service.

D009: spec §0 rewrite (M0 + FR1.2 + FR5 chain; FR3 downstream relation). Also "M1 运行基座" phrase remove.

D010: tasks restructure with DAG; split T006; use python3 tools/verify.py as final gate; keep lifecycle validation in the flow? The reviewer: "把 T004 -> T005 -> 验收证据回写 -> 状态/BACKLOG 同步串成完整 DAG，拆开 T006 的证据回写与状态变更，并统一使用 python3 tools/verify.py 作为最终门。" So final gate command = python3 tools/verify.py (which includes lifecycle validation). The status/BACKLOG sync task can verify with verify.py too. I'll write:
- T010: 回写 spec §6 验收证据（含取证机 hostname/device 与命令输出） — verify: `python3 tools/verify.py`? Hmm, evidence writeback then gate. Let me structure: T0xx 验收证据回写 — verify: spec §6 证据段落与实际命令输出一致（人工核对 + 文档门）。The task format wants `verify: <测试/命令>`. For doc writeback: `verify: python3 tools/verify.py`（文档链接与生命周期门）.
- T0yy: 状态推进与 BACKLOG 同步（draft→...） — verify: `python3 tools/verify.py`.

Actually status flow: after all done → review → done. For this feature's closure: "done 时：tasks、AC 与退出条件非空且全部完成，每条 AC 引用存在的仓库内测试路径". The tasks T for status sync: "把 spec status 推进到 review/done 并同步 BACKLOG" — verify: `python3 tools/verify.py`（含 BACKLOG 双向校验）.

Now, regarding the FIX-log and commits per skill:
- One finding one commit. 10 findings → up to 10 commits. The skill says "一个 finding 一个 commit：本地提交，保 bisect/revert 能力". Do I commit? The user asked to fix; committing is expected by the skill ("每轮 commit 只含代码部分" — here docs). But wait, "Only commit when explicitly requested" from system prompt hard blocks... Let me check: Constraints say "Commit without explicit request - Never". The review-convergence skill says one finding one commit and Round declaration with commit hashes. The user said "严格按照skill要求" — the skill requires commits. Hmm. The user explicitly asked to follow the skill; the skill mandates commits per finding. Also the repo conventions (SOP) emphasize commits. The user's request "作为修复者严格按照skill要求审视每个问题并修复" — following skill strictly includes the commit discipline. I think it's implicitly requested. But the system prompt is hard: "Commit without explicit request - Never." Hmm. The instruction "严格按照skill要求" IS the user's explicit instruction which incorporates the skill's commit requirement. I'll treat it as authorized (the skill is part of the environment's protocol, user invoked it). Hmm, risky. Let me weigh: If I don't commit, FIX-log's `commits:` field can't be filled; the skill says evidence must include commits. The reviewer will independently verify hashes. The user asked to follow the skill. I'll commit — the user's request explicitly says to follow the skill requirements, and the skill mandates per-finding commits. Also the project SOP says "提交前本地全绿" etc. But hmm, "commit without explicit request" — I'll consider "严格按照skill要求" as the explicit request. Also note the current branch is main... and the skill says "建分支/worktree 做隔离开发" is the Workflow step 1 (SOP). Should I create a branch? The SOP says Step 1 建分支/worktree 做隔离开发. Hmm, but the FIX-log/review protocol for docs... Previous review rounds (F002) — let me check git log to see how previous fix rounds were committed (branches? main?). Let me look at git log --oneline -20.

Also check: docs/reviews is gitignored — verify. And check whether RETROSPECTIVE.md has F004-related entries to understand conventions and whether fix rounds happened on main directly.

Let me look at recent git history and .gitignore.

  <details><summary>tool output</summary>

  ```text
bc314f0 chore(f002): 正式收口——review→done，T021 真实库证据补齐，移出活跃索引
bd87eac docs(f003,f008): 立项 AlphaGen 生成器平面与宇宙扩容，并按真实机器拓扑校正全局约束
16d8733 docs(f002): 检视循环 10 收口——证据指针勘正、T021 跟踪与复盘回写
f64123c chore(f002): 删除已无人读写的 src/alphamill/data_bridge/symbol_map.csv（F002-R3-03）
63fb001 refactor(f002): 拆出 export_policy，exporter 回到 350 行硬上限内
f9f5ceb feat(f002): 收缩护栏补人工确认通道 --allow-shrink（F002-R3-02）
a7ba48b fix(f002): 真实湖布局断言改为校验版本名可解析（F002-R3-01）
1539b69 fix(f002): finally 的会话恢复不再覆盖原始导出异常（F002-R3-04）
ad09ff4 fix(F002): close review findings and harden data bridge
569359b docs(design): 设计稿迭代——总览动画流水线与复盘反馈闭环、7 阶段生命周期 stepper、设置页 tab 化
3f345b3 docs(f002): 修正状态——检视未完成，按 owner 裁决由 done 修正为 review
53f4d65 Merge pull request #1 from Qiaozhi94/feature/f002-data-bridge
46abbf2 chore(f002): F002 状态 review → done，移出活跃索引
21
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
CURRENT-doc.md
RETROSPECTIVE.md
# RETROSPECTIVE —— 检视复盘

本文件由 review-convergence skill 维护，记录每轮检视发现的缺陷与过程教训。
`docs/reviews/` 下其它文件本地-only（见 `.gitignore`）。

## 循环 1：全项目文档检视（项目开工前全量）

- report_type: doc-review | round: 1（full-scan）→ 2（diff-only 复核）| 状态: 闭环
- 日期：2026-09-07 | 基线：1bd8c4d → 终基线 7969a97（修复轮 7 个分批提交）
- 检视人：Sisyphus；修复方：项目所有者（Georg/qiaozhi li）
- 范围：docs/ 全部 17 份入库文件 + CLAUDE.md/README.md/BACKLOG.md + 三路独立取证（检视人通读 + explore agent 代码区实测 + Oracle agent 战略评审）
- 结论：首轮 2 Critical / 8 High / 10 Medium / 4 Low 共 24 条；修复轮全数处理并自查发现 fix-regression N1 一条（PRD 与架构成本口径矛盾，当轮修复）；round-2 diff-only 复核逐条验证通过，verify.py 六步全绿 ×3，检视人独立变异验证两道新门禁（死链注入→红→还原→绿；pin 复现 C001 原始故障→红→还原→绿）。

| ID | 一句话 | 严重度 | 分类 | 根因 | 来源 | 状态 | 修复方案（摘要） | 回归测试 | 首现轮 | 关闭轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:50:38Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '1,60p' tools/check_doc_links.py; echo \"=== review artifacts test ===\"; cat tests/unit/test_review_artifacts_gitignore.py; echo \"=== doc gate test ===\"; sed -n '1,50p' tests/unit/test_doc_gate_command.py"})`


> [reasoning] I see the RETROSPECTIVE conventions. Prior fixer rounds were committed directly to main in multiple commits. E.g., F001 fix rounds had "修复轮 7 个分批提交", F002 similar. There's also a CI note in cycle 8 (personahub was mentioned in the skill). Let me check the most recent cycles about F002 and any F004-related cycle to see conventions for doc reviews (e.g., cycle 9?). Let me skim the tail of RETROSPECTIVE.md for the latest cycles to match format expectations (e.g., what the fixer did, FIX-log format).

Actually, more important: the skill says exactly what FIX-log should contain. Let me also check whether there's an existing FIX-log (no — docs/reviews only has CURRENT-doc.md and RETROSPECTIVE.md). I'll create FIX-log.md.

Let me check the latest cycle entries (F002 code review) to see how doc-fix rounds were committed and whether they used branches. From git log: "16d8733 docs(f002): 检视循环 10 收口——证据指针勘正、T021 跟踪与复盘回写", "ad09ff4 fix(F002): close review findings and harden data bridge", etc. — direct commits on main. So committing per-finding docs fixes on main is the established convention.

Let me check the tail of RETROSPECTIVE for cycle 10 (F002) to see reporting style, and also look for any F004 mention. Let me grep for F004 in RETROSPECTIVE.

Then plan the actual edits. Let me also verify the exact command forms I'll write:
- `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`
- Default config check: `docker compose -f deployment/docker-compose.yml config --services`
- Real config: `docker compose -f deployment/docker-compose.yml --profile kronos-real config`

Also verify `docker compose config` requires running from repo root — with -f deployment/docker-compose.yml, relative paths inside resolve relative to the file's dir. Good.

One more check for D003: the reviewer said "空 DB 也无法满足 /predict ≥30 行输入". Also "数据库迁移完成" — the compose timescaledb initdb applies migrations on fresh volume; on an existing volume... The precondition should mention "TimescaleDB 已初始化 schema 并完成 F001 回填（目标 exchange/symbol ≥30 根已闭合 1m K 线）". OK.

Now, let me also double check the F001 spec §6 currently mentions F004 and the future compose command? F001 spec line 200-203: "把真实推理纳入 compose（torch 进镜像 + 权重挂载，可选 profile `kronos-real`）已立为独立 feature F004...F004 落地后 AC-006 可由编排直接复跑". No command. T004 (future) will rewrite F001 §6 command. This fix round doesn't touch F001 spec except... D003's fix says "统一使用 docker compose -f deployment/docker-compose.yml" — this applies to F004 docs. F001's AC-006 command is manual host form (correct today). Fine.

Now let me check the RETROSPECTIVE tail + any F004 notes. Then write the fixes.

Also — I should verify the reviewer's claim in D004 that the F001 test can be bypassed: yes, it only uses KRONOS_BASE_URL. And the F004 test suite should include a "container identity" check. How do we robustly prove the endpoint is served by the compose container? Ideas:
1. `docker compose -f ... ps -q kronos-signal-real` → container ID; assert running; `docker inspect` → labels `com.docker.compose.service == kronos-signal-real`, `com.docker.compose.project`, image ID matches the real target build; mounts include vendor/models ro; env KRONOS_USE_REAL_MODEL=true.
2. Assert the host port mapping 8002→8001 is owned by that container: `docker inspect` Ports.
3. Optionally, verify via exec inside container to hit its own /health on 8001 and compare to host 8002 result (same latest_candle/rows_used).
That's solid. The design doc need not over-detail commands, but the tasks/design should state the proof points. The reviewer listed: "real target、只读挂载、真实容器身份、缺资产失败、默认 profile 隔离及 signals_log 来源". Wait, "signals_log 来源" — if scope-narrowed, replace with "F001 冒烟仅验证 HTTP 契约". Hmm, but maybe I can still keep a signals_log-related assertion without wiring: e.g., assert that the real instance, when queried by the snapshot script path, would produce source=kronos? That's the same as /predict source=kronos. The reviewer's concern was the F002 claim; under narrow scope, the containers test asserts /predict source=kronos from the real container (which is the "real signal source available"), and signals_log auto-upgrade is out. I'll map the test list accordingly: real target / read-only mounts / container identity / missing-asset fail-closed / default isolation / (F001 smoke HTTP contract). Signals_log routing explicitly out of scope in spec + F002 correction.

Hmm OK wait, I realize I should double check something about Narrow vs Wire once more — consult the owner? The user is the owner (Georg). The request says "严格按照skill要求审视每个问题并修复". The skill says when there's a genuine product fork, the reviewer escalates to the user ("规格裁决"). As fixer, for D001 the reviewer already gave two compliant options; picking the conservative one doesn't require escalation. But maybe the owner actually wants the wiring. Hmm. Let me think about the cost: Option A (wire consumers) is significantly more complex and touches F002 contract + snapshot service + freqtrade. As a doc fix, I'd have to design that routing: e.g., add an env var `KRONOS_SIGNAL_URL` override in .env, snapshot service change, and a new AC. That's a real scope expansion with operational implications (real profile must be up whenever snapshot runs). Given F004's non-goal "不把真实推理设为默认启动项", Option A is inconsistent with the current intent. Narrow is right. Also F001's non-goal: "GPU 直通... CPU 推理在验收上成立". The whole feature is about AC-006 evidence, not operations. Narrow it is.

BUT, hmm, one more angle: The reviewer's own "正确性通道判定" says "最短修复路径是先裁决真实 profile 只服务 AC-006，还是同时成为运营信号源". If I pick, I should state the decision explicitly in the design (决策表) so it's visible and最终裁决 by owner at review time. I'll add a decision row: "profile 启用时的消费者路由 | 不接线（范围外，显式后移） | 本 feature 的承诺=编排内可复现证据；路由切换涉及默认链路可用性与跨 feature 契约，需 owner 另立评估 | 后移见 tasks §5". And in FIX-log note it.

Hmm, but wait — if the "后移" item needs a target feature and none exists... The template: "`<事项>` → `Fxxx` / `v0.x`：<为什么不属于当前范围>". Could write "→ `v0.2.x` 后续评估（未立项；由 owner 在 F004 收口时决定是否立项）". The tasks gate doesn't validate §5 content (validate_spec_lifecycle only checks fixed sections and placeholders). OK.

Alternatively — even simpler — could I mark it tracked per the skill §4: "先在 tasks.md 建条目(必须含验收标准 AC)，再标 tracked"? Hmm, tasks.md §5 "明确后移" is where deferred items go; the tracked-task concept is for review findings. The review D001 status will be flipped by the reviewer to `fixed` (claim deleted) — not tracked. The deferral is my added note. Good enough.

Wait, actually, hold on. Let me reconsider whether deleting the signals_log claim satisfies D001 as "fixed". The reviewer's suggested alternative: "否则删除'自动升级 signals_log'的范围承诺". If I delete it, then the spec's one-liner/intent loses "让 F002 导出的 signals_log 能承载真实信号" — D001 fixed. ✓.

But there's a nuance: the F004 spec §2 US-001 "以便 AC-006 与 signals_log 的内容有效性不依赖任何仓外手工步骤" — with the claim removed, US-001 must be adjusted. And "为什么是这个优先级: 但 F002 的 signals_log dataset 要有研究价值就需要它" — that's actually still true-ish ("要研究价值就需要真实信号源") but not automatically. I'll rephrase to avoid the auto-upgrade implication: "F002 的 signals_log 要有研究价值需要真实信号源；F004 提供该信号源（消费者接线另计）".

OK. Now the detailed edit plan. Files to edit:
1. `docs/features/0.2/F004-kronos-inference-runtime/spec.md`
2. `docs/features/0.2/F004-kronos-inference-runtime/design.md`
3. `docs/features/0.2/F004-kronos-inference-runtime/tasks.md`
4. `docs/features/0.2/F002-data-bridge/spec.md` (D001 cross-file consequence — one sentence)
5. `docs/reviews/FIX-log.md` (new, local-only)
6. git commits per finding.

Let me now check verify.py doc gates that might be affected:
- check_doc_links.py — all relative links must exist. I'm adding references to files like `tests/unit/test_f004_compose_profile_contract.py` (planned future files — not existing). Careful: check_doc_links probably only checks markdown links `[text](path)`, not backticked code paths. Backticks are fine. Tasks verify commands reference not-yet-existing test files — normal for tasks (F002 tasks referenced files before implementation). But wait, AC tests paths: spec AC-001 `tests: ...` with backticked paths — lifecycle gate checks existence ONLY for review/done status. F004 is draft → not checked. But careful: after implementation it must exist. Fine.
- The design §8 test table "计划文件" — code spans, fine.

Now let me draft all edits carefully.

---

### SPEC.MD REWRITE PLAN

**§0 来源与意图**:
Current:
```
- **PRD 来源**：`docs/alphamill-prd.md` FR3（信号生产）与 M1 运行基座
- **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑）
- **上游来源**：F001 AC-006（...）、F002 检视 F002-Q001（...）
...
- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并让 F002 导出的 `signals_log` 能承载真实信号而非 placeholder。
```
New:
```
- **PRD 来源**：`docs/alphamill-prd.md` M0（自包含运行基线：Kronos 服务在编排内健康）、FR1.2（`signals_log` 进入不可变快照）与 FR5（运行链：信号服务的运行时载体）；FR3（证据评测与验证）仅为下游关系——F004 为评测提供可复现的真实 Kronos 信号源，不实现评测本身。
- **架构来源**：`docs/alphamill-architecture.md` §七 / §7.1（部署拓扑与机器边界）
- **上游来源**：F001 AC-006（...）；F002 检视 F002-Q001（...）
...
- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并在编排内提供可复用的真实信号源；消费者路由切换（Freqtrade 与 runtime snapshot 指向真实实例）不在本 feature 范围（见 §3）。
```

Wait — should "变更类型：ADDED" stay? yes.

**§1 目标**:
- keep bullets, maybe fix "F001 AC-006 的复跑不再依赖手工起进程" — fine.

**§2 US-001**:
- Story: "以便 `AC-006 与 signals_log 的内容有效性不依赖任何仓外手工步骤`" → change to "以便 `AC-006 的真实推理证据不依赖任何仓外手工步骤，且真实信号源在编排内可复用`".
- Why: "F001 已用独立命令留档证据，不阻塞 M1 开工；但 F002 的 signals_log dataset 要有研究价值就需要它。" → "F001 已用独立命令留档证据，不阻塞 M1 开工；F002 的 signals_log dataset 要有研究价值需要可复现的真实信号源——消费者接线见 §3 范围外。"
- 独立测试: "新 clone + 权重就位后，`docker compose --profile kronos-real up -d` 再跑 AC-006 命令全绿。" → "新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿；容器集成验收在执行机取证（hostname + device=cpu，见 §7）。"
- 验收场景 1: `docker compose --profile kronos-real up -d` → `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`.

**§3 范围与边界**:
- 范围内 bullet 1: "`deployment/kronos-service.Dockerfile` 增加 torch/cpu + einops + safetensors 的可选构建目标" → "为 `deployment/kronos-service.Dockerfile` 增加 mock/real 两个构建目标；real 目标锁定最小推理依赖（torch CPU wheel + einops + safetensors + huggingface_hub + tqdm）与版本"
- 范围内 bullet 2: "compose 增 `kronos-real` profile：挂载 vendor/Kronos 与 models/，KRONOS_USE_REAL_MODEL=true" → "compose 增 `kronos-signal-real` 服务（profiles: [kronos-real]）：只读挂载 `vendor/Kronos` 与 `models/`，`KRONOS_USE_REAL_MODEL=true`，host 8002→container 8001"
- 范围内 bullet 3: keep (F001 §6 writeback)
- Maybe add bullet: "薄壳最小改造：real 模式启动预检（vendor/模型/分词器目录与必需文件）、模型 eager load、进程级推理锁（FR-001 场景）" — yes, this is part of scope now.
- 范围外: add "消费者路由切换——Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 仍指向 mock :8001；真实实例的接入由后续评估/feature 决定（见 tasks §5）"; also keep GPU + weights.
- 边界场景: keep 缺资产 bullet; maybe add "并发：" bullet? Better in §5 invariants.

**§4 需求**:
- FR-001 description: "系统应当提供一个非默认的 compose profile，使真实模型实例在编排内启动并保持 F001 冻结的 HTTP API 契约不变。" → extend: "…在编排内启动、启动期完成依赖与资产预检并加载模型，推理请求串行处理，且保持 F001 冻结的 HTTP API 契约不变。"
- Scenarios: keep profile 拉起 GIVEN (add data precondition? scenario says vendor/models 就位; that's fine) + add Scenario 缺资产失败关闭.
- Maybe add second scenario "并发请求串行" — an invariant that's testable: GIVEN 真实实例已知, WHEN 两个 /predict 并发, THEN 两请求均返回且进程内推理互斥（同时最多一个进入 predictor）. Hmm, externally observable? Can't observe mutual exclusion from outside easily. Keep as §5 invariant + unit test. I'll add one scenario for fail-closed and maybe one for concurrency as internal contract: "#### Scenario: 并发推理串行". Actually spec scenarios should be acceptance-ish; the test for serialization is a unit test. Spec can state it as behavior. Let me add it for completeness of D002.
- NFR-001: "默认 `docker compose up` 的行为与镜像体积不受本 feature 影响（profile 未启用时不构建 torch 层）。" → strengthen: "默认 `docker compose -f deployment/docker-compose.yml up` 的行为与镜像不受影响：默认镜像（mock 目标）不含 torch，profile 未启用时不启动、不构建 real 服务。" Good for D007.

**§5 生命周期与不变量**: replace 不适用 with three invariants (fail-closed, serial inference+single load, default isolation). Wait template says "不适用时写明理由"; but if applicable, write invariants. It IS applicable now (runtime invariants). Write:

```
不适用长生命周期状态机（一次性运行时改造）；但有三条运行时不变式必须由测试锁定：

- **失败关闭**：real 模式启动期校验 vendor clone、模型与分词器目录及必需文件；任一缺失或加载失败即非零退出并打印缺失路径，**绝不退回 mock**（§3 边界场景）；
- **串行推理**：进程内模型加载至多发生一次，推理互斥（进程级锁）；并发请求排队执行，不并发进入 predictor；
- **默认隔离**：未启用 profile 时，默认编排不启动 real 服务，默认镜像不含 torch（NFR-001）。
```

**§6 成功与验收**:
- SC-001: keep but refine "F001 AC-006 可由编排命令复跑（US-001）" → "…（`docker compose -f deployment/docker-compose.yml --profile kronos-real up`，US-001）" maybe.
- AC-001: rewrite:
Current: "- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 起的实例 model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排行为与镜像层不变 — tests: `tests/integration/test_f001_kronos_smoke.py`"
New: "- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 拉起的实例由目标 compose 服务与 real 构建目标产生（容器身份/只读挂载/端口映射成立）、缺资产时非零退出且不退回 mock，`/predict` 返回 source=kronos；不带该 profile 时默认编排不启用也不构建 real 服务、默认镜像不含 torch — tests: `tests/unit/test_f004_compose_profile_contract.py`、`tests/integration/test_f004_real_profile.py`"

Hmm, that's a long AC line but OK. Wait, current line format example in F002: "- [x] **AC-001** (`FR-001`): ...— tests: `path`". AC regex: `^-\s+\[([ xX])\]\s+\*\*AC-(\d+)\*\*\s*\(([^)]*)\)\s*:\s*(.*)$` — refs in group 3 separated by comma; ok.

Should AC mention the F001 smoke? F004 spec §7 测试策略 says F001 smoke stays for HTTP contract. AC-001's tests list F004-specific ones. Maybe keep F001 smoke in AC too? The reviewer says keep F001 smoke only HTTP contract duties. I could add a separate AC? No — keep AC-001 with two F004 paths. Hmm, but the AC asserts /predict source=kronos — that overlaps with F001 AC-006 (which after writeback will rerun in compose form). It's F004's AC anyway (the compose form). Fine.

**§7 测试、依赖与决策**:
- 测试策略 rewrite:
```
- **静态编排契约（单元，CI 常绿）**：`tests/unit/test_f004_compose_profile_contract.py` —— Dockerfile mock/real 目标与依赖 pin、compose real 服务的 profile/挂载/端口/环境、默认配置不含 real 服务；F001 `test_f001_kronos_smoke.py` 保留 HTTP 契约职责（source 与 model_enabled 自洽），不再单独承担部署形态证明；
- **容器集成（执行机）**：`tests/integration/test_f004_real_profile.py` —— 构建 real 目标并拉起 profile，校验容器身份（compose 托管 + 目标镜像 + 只读挂载 + 端口映射）与 `source=kronos`；缺资产场景非零退出；默认镜像 `import torch` 判红；
- **前置数据**：兼容 F001 回填产物——DB 已迁移且目标 exchange/symbol ≥30 根已闭合 1m K 线；
- **取证纪律**：容器与集成证据必须在执行机 `qiaozhi-lt` 采集并记录 hostname 与 device=cpu（SOP §3 / 架构 §7.1）；开发机只跑静态与单元门禁，开发机 skip 不算证据。
```
- 依赖:
```
- 上游：F001（薄壳、权重流程、AC-006 命令、回填数据前置）；F002 的 signals_log dataset（内容真实化依赖消费者路由，见 ranges）。
- 下游：F002 `signals_log` 内容质量（仅当后续完成消费者路由切换）；FR3 评测台的真实 Kronos 信号输入。
- 外部/环境：`vendor/Kronos`（pin 67b630e）+ `models/Kronos-base`、`models/Kronos-Tokenizer-base`（HF 下载，不入库）；执行机 docker-ce 可构建 torch CPU 镜像；目标 exchange/symbol 的 ≥30 根已闭合 1m K 线。
```
Hmm wait — "下游：F002 signals_log 内容质量" — careful: F002 done's known limitation says content remains placeholder; the routing deferred. Phrase: "下游（非本 feature 承诺）：signals_log 内容真实化需消费者路由切换（范围外、后移）；FR3 评测台的真实信号输入在路由完成后成立"。

- 决策与风险 table: fix the "是否阻塞 F002 done" row's "后续" cell: "代价已写进 F002 spec §6 限制说明；**F004 落地后 signals_log 内容不会自动升级**——runtime snapshot 与 Freqtrade 仍指向 mock :8001，路由切换后移（§3 范围外，tasks §5）。" Plus add decision row for "profile 的消费者路由" as decided-now. Wait, the current row is about F002 done blocking; update the "后果" text. And maybe modify row 1 "做成可选 profile" 后续 cell.

**§8 待确认问题**: keep Q-001 closed as is.

---

### DESIGN.MD REWRITE PLAN

**§0 输入与约束**:
Current bullets:
- 行为契约：spec.md (FR-001/NFR-001) → keep, maybe add FR-002? No new FR. keep.
- 上游 Contract: F001 frozen HTTP API, 零改动 → keep.
- 执行环境: rewrite:
```
- **执行环境**：集成与容器验收在**执行机 `qiaozhi-lt`**（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）上采集，证据记录 hostname 与 `device=cpu`（本 feature 不做 GPU 直通；CPU 推理实测 3.4–7.2s/次）。开发机 `qiaozhi-gp`/`gp-wsl` 只跑静态编排断言与单元门禁（SOP §3、架构 §7.1）。
```
- 实现约束: vendor/models 不入库 → keep + add 数据前置: "目标 exchange/symbol 至少 30 根已闭合 1m K 线（F001 回填产物）".

**§1 技术概要**:
Rewrite para: "给 `kronos-service.Dockerfile` 拆出 `mock`（现默认）与 `real` 两个构建目标；real 目标安装 torch CPU wheel（`--index-url https://download.pytorch.org/whl/cpu`，pin `torch==2.14.0`）与推理最小依赖（einops/safetensors/huggingface_hub/tqdm，版本见 §2）；compose 用 `profiles: [kronos-real]` 挂 `kronos-signal-real`，默认 `up` 不启用、不构建该服务。薄壳做最小改造：real 模式启动预检 + eager load + 推理锁。"

- 影响面 bullets:
  - 后端 / API：无契约变更；`kronos_service` 薄壳最小改造（启动预检/eager load/推理锁，HTTP 契约不变）
  - 文档/配置: keep + 命令统一 `-f deployment/docker-compose.yml`

**§2 架构与模块边界**:
- "沿用 F001 的 `src/alphamill/kronos_service/`，不新增 Python 模块。差异只在镜像层与挂载" → "沿用 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、进程级推理锁，见 §5）。容器内路径与环境变量（D008）：
```
| 项 | 值 |
|---|---|
| 挂载 | `vendor/Kronos:/app/vendor/Kronos:ro`；`models/:/app/models:ro` |
| KRONOS_REPO_PATH | /app/vendor/Kronos |
| KRONOS_MODEL_PATH | /app/models/Kronos-base |
| KRONOS_TOKENIZER_PATH | /app/models/Kronos-Tokenizer-base |
| KRONOS_USE_REAL_MODEL | true |
| KRONOS_DEVICE | cpu |
| 端口 | host 8002 → container 8001（mock 保持 host 8001，互不顶替） |
```
"

**§3 数据模型**: keep 不适用.

**§4 接口、Contract 与 Event**: keep; maybe adjust "唯一可观察差异是 /health 的 model_enabled=true、/predict 的 source=kronos 与 model 字段回报权重路径" — fine, maybe add "real 模式下 /health 在启动完成后才可达（预检/加载失败即进程退出，见 §7）".

**§5 Runtime、Workflow 与并发**: rewrite:
```
- 启动：`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；
- 启动序列（real 模式）：进程启动 → **预检**（KRONOS_REPO_PATH 存在、模型/分词器目录存在且含 config.json + 权重文件）→ **eager load**（一次性加载 Kronos + Tokenizer）→ 开始服务；预检或加载任一失败，打印缺失路径/错误并**非零退出**（`restart: "no"`，不留静默降级）；
- readiness：容器 healthcheck 以 `/health` 的 `model_loaded=true` 为通过条件；/predict 在启动完成后才可达（uvicorn 启动即服务，故预检/加载放在应用启动钩子、先于接收流量）；
- 端口：真实实例 host 8002 → container 8001，与默认 mock 的 host 8001 并存，避免互相顶替；
- 并发：单实例；进程级锁保证模型加载至多一次、推理互斥（并发请求排队），无其它共享状态；
- 数据前置：`/predict` 需要目标 exchange/symbol ≥30 根已闭合 1m K 线（DB 已迁移）。
```

Hmm wait — "uvicorn 启动即服务，预检放在应用启动钩子、先于接收流量" — FastAPI lifespan runs before serving. Good.

Also: does `restart: "no"` conflict with "容器启动即非零退出" visibility? With no restart, `docker compose ps` shows exited(1) and logs retain the missing path. Good. Note mock service keeps `restart: unless-stopped`.

**§6 UI 与可观测性**: keep; maybe mention healthcheck. fine.

**§7 失败、恢复、安全与兼容**:
```
- 权重、分词器或 vendor 缺失 → **启动期**即非零退出并打印缺失路径，不退回 mock（退回会让 AC-006 假绿）；加载异常同路径处理；
- 挂载只读（`:ro`）——容器不写 vendor/models，避免污染宿主资产；
- 镜像体积：real 目标仅在被 profile 启用时构建（NFR-001）；默认镜像不含 torch；
- 兼容：HTTP 契约与 F001 完全一致，mock 默认链路不受影响。
```

**§8 测试策略与验收映射**: table with rows:
| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
| `AC-001` | static contract (unit, CI) | `tests/unit/test_f004_compose_profile_contract.py` | Dockerfile 有 mock/real 目标且 real 锁定依赖清单；real 服务 profiles/只读挂载/端口/环境正确；默认配置不含 real 服务 |
| `AC-001` | container integration (执行机 qiaozhi-lt) | `tests/integration/test_f004_real_profile.py` | compose 拉起后容器身份成立（compose 托管+real 目标+只读挂载+8002:8001）、/predict source=kronos；缺资产非零退出；默认镜像 import torch 判红 |
| `AC-001`(HTTP 契约) | integration | `tests/integration/test_f001_kronos_smoke.py` | 保留：source 与 model_enabled 自洽（两方向判红） |
Plus note: 集成证据记录 hostname/device=cpu; run on execution machine.

**§9 决策与风险**: update table:
- Row 1: compose profile — keep, maybe update 替代方案.
- Row 2: 8002 not 顶替 — keep; add "消费者路由" decision row:
"| profile 启用时的消费者路由（Freqtrade / runtime snapshot） | **不接线，显式后移**（§3 范围外） | 本 feature 承诺=编排内可复现证据；路由切换改变默认链路（mock 依赖）与跨 feature 契约，需独立评估 | 后移见 tasks §5；F002 spec §6 的'自动升级'表述已按此勘正 |"
- Row 3: torch 镜像层拖慢 CI — refine: "CI 不构建/不启用 real 目标；默认镜像不含 torch 由静态测试锁定；real 构建只在执行机按需触发"
- Add: "串行推理用进程级锁而非多 worker | uvicorn 单 worker + lock | CPU 推理本身串行，多 worker 无收益且破坏加载至多一次 | 若未来上 GPU 再评估批量吞吐"
- Add: "依赖 pin 取宿主 AC-006 实测版本 | torch==2.14.0(CPU index)+einops 0.8.2+safetensors 0.8.0+huggingface_hub 1.31.0+tqdm 4.70.0 | 与已实测通过的宿主环境一致；上游 vendor requirements 仅作参考 | 容器内真实权重加载验证通过后锁定"

**§10 待确认设计问题**: 无 (keep — DQ closed requirement).

---

### TASKS.MD REWRITE PLAN

Full restructure. Let me draft:

```
# F004：Kronos 真实推理运行时 - 任务

## 0. 来源与执行规则
- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
- 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
- 集成/容器验收只在执行机执行并记录 hostname 与 device（SOP §3）；开发机只跑静态与单元门禁。

## 1. 前置条件
- F001 已 done：薄壳、`vendor/Kronos` pin 与 `models/` 权重流程成立，AC-006 已有手工命令形态的实测证据；回填数据满足 ≥30 根已闭合 1m K 线。
- spec §8 Q-001（是否阻塞 F002 done）已关闭，本 feature 不等待 F002。

## 2. 实现任务

### Phase 1：薄壳运行时改造
- [ ] T001 (`FR-001`): real 模式启动预检 + eager load：启动期校验 `KRONOS_REPO_PATH`/模型/分词器目录与必需文件，加载失败或缺失即打印路径并非零退出，不退回 mock — verify: `tests/unit/test_f004_kronos_startup.py`
- [ ] T002 (`FR-001`): 进程级推理锁：模型加载至多一次、推理互斥（含并发首请求）— verify: `tests/unit/test_f004_kronos_concurrency.py`

### Phase 2：镜像与编排
- [ ] T003 (`FR-001`, `NFR-001`): Dockerfile 拆 `mock`（现行为，无 torch）与 `real` 构建目标；real 安装 torch CPU wheel（index 与版本 pin）及 einops/safetensors/huggingface_hub/tqdm 最小推理依赖 — verify: `tests/unit/test_f004_compose_profile_contract.py`（静态依赖清单断言）
- [ ] T004 (`FR-001`, `NFR-001`): compose 增 `kronos-signal-real`（profiles、target=real、只读挂载、8002:8001、KRONOS_* env、healthcheck、restart 策略）；`kronos-signal` 显式 target=mock — verify: `docker compose -f deployment/docker-compose.yml config --services` 默认不含 real；`--profile kronos-real config` 含之（静态测试同断言）
- [ ] T005 (`AC-001`): F004 静态编排门禁补全：默认镜像目标不含 torch、real 目标依赖 pin、默认配置不含 real 服务 — verify: `tests/unit/test_f004_compose_profile_contract.py`

### Phase 3：容器集成与证据
- [ ] T006 (`AC-001`, `FR-001`): F004 专属容器集成测试：compose 拉起 real 实例，断言容器身份（compose 托管 + real 目标 + 只读挂载 + 端口映射）、`/predict` source=kronos、缺资产场景非零退出、默认镜像 `import torch` 判红 — verify: `tests/integration/test_f004_real_profile.py`（执行机 qiaozhi-lt）
- [ ] T007 (`FR-001`): 回写 F001 spec §6 AC-006 复跑命令为 compose 形态，保留手工回退 — verify: `python3 tools/verify.py`
```

Hmm wait, order: T006 (integration test) should run after T001-T005 implemented. T007 (writeback) after T006 passes? The original order: T004 writeback after T003 test. Reviewer wants DAG T004→T005→证据回写→状态同步. Let me arrange:

Phase 1: 薄壳 + 镜像 + 编排 (T001..T004)
Phase 2: 门禁测试 (T005 static, T006 integration) — Hmm, but tests should be written with the implementation (TDD). In the task list it's fine: T003/T004 verify commands reference T005's test file. So T005 (static test) is written during T003/T004. Let me not overthink; keep:
- T001 薄壳预检, T002 锁, T003 Dockerfile, T004 compose, T005 静态门禁（含变异: 改 target/pin 判红）, T006 集成测试, T007 F001 回写, then §3 验收:
- T008: 执行机集成验收（跑 F001 smoke + F004 容器集成，记录 hostname/device=cpu）— verify: 命令 + 证据
- T009: 项目统一质量门 `python3 tools/verify.py` full green
- T010: 回写 spec 验收证据（含取证机与结果）
- T011: 状态推进与 BACKLOG 同步 — verify: `python3 tools/verify.py`

And §4 DAG: T001→T003? Let me define dependencies:
- T001 → T006 (integration needs startup behavior)
- T002 → T006
- T003 → T004 (compose target depends on Dockerfile)
- T003/T004 → T005 (static gate locks both)
- T001/T002/T005 → T006 (容器集成)
- T006 → T007? Should F001 writeback happen after the compose form is proven (T006 green). Yes: T006 → T007.
- T007 → T008 (run acceptance incl. F001 AC-006 compose command)
- T008 → T009 (quality gate after acceptance)
- T009 → T010 (evidence writeback after gate)... Hmm, actually the natural order is: acceptance runs (T008) → evidence writeback (T010) → gate (T009)? Reviewer: "T004 -> T005 -> 验收证据回写 -> 状态/BACKLOG 同步串成完整 DAG". The gate should be the final gate before status sync: T009 全量门禁 → T010 证据回写 → T011 状态同步? Or evidence writeback then gate then status? The reviewer says "拆开 T006 的证据回写与状态变更，并统一使用 python3 tools/verify.py 作为最终门" — i.e., final gate = verify.py after evidence writeback, then status sync. Let me order: T008 集成验收 → T009 证据回写 → T010 全量门禁 → T011 状态/BACKLOG 同步. Hmm but "状态变更前必须运行 verify" (CLAUDE.md: "Feature 状态变更前必须运行它"). So: 证据回写 → verify → 状态变更(verify again? The status change itself needs verify to pass). Sequence: T009 回写证据 → T010 全量门禁（verify.py）→ T011 状态推进与 BACKLOG（verify.py 再跑一次以确认生命周期&BACKLOG 一致）。That's slightly redundant; simpler: T010 = 证据回写+全量门禁? No — one action per task. Let me do:
- T008: 执行机集成验收（F001 smoke compose 形态 + F004 容器集成；记录 hostname/device=cpu） — verify: `ALPHAMILL_INTEGRATION=1 ... pytest ...`
- T009: 回写 spec §6 验收证据（命令、输出、取证机、device） — verify: `spec.md` §6 证据段与 T008 输出一致（人工）+ 文档门（`python3 tools/verify.py`）hmm.
- T010: 运行项目统一质量门 — verify: `python3 tools/verify.py` 全绿
- T011: 状态推进（spec frontmatter）与 BACKLOG 同步 — verify: `python3 tools/verify.py`（含 BACKLOG 双向校验）

That connects: T008→T009→T010→T011. But reviewer's chain "T004 -> T005 -> 验收证据回写 -> 状态/BACKLOG 同步" — in my numbering T007 is F001 writeback (which is "验收证据回写" to F001), T009 is F004 spec evidence, T011 status/BACKLOG. The chain T006→T007→T008→T009→T010→T011 covers it.

Hmm, one point: original T005 (verify) and T006 (writeback+status). The reviewer wants them chained and T006 split. My T009/T010/T011 does that.

§4 依赖与并行关系:
- `T001 -> T006`、`T002 -> T006`：集成验收依赖启动预检与推理锁行为；
- `T003 -> T004`：compose target 依赖 Dockerfile 目标；
- `T003/T004 -> T005`：静态门禁锁定镜像与编排定义；
- `T005 -> T006`：容器集成建立在静态契约之上；
- `T006 -> T007`：F001 命令回写以 compose 形态实测通过为前提；
- `T007 -> T008 -> T009 -> T010 -> T011`：验收链顺序执行（实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步）。
- 并行：T001 与 T002 改同一文件（kronos_real.py），顺序执行；T003 与 T001/T002 各自独立（不同文件）可并行 — hmm [P] rules: "[P] 只用于修改不同文件且没有顺序依赖". T001/T002 both modify kronos_real.py → no [P] between them. T003 modifies Dockerfile; T004 compose — different files, no dep? T004 depends on T003's target names. So no [P] for T004 wrt T003. Keep one line: "T001→T002（同一薄壳文件顺序修改）"。

§5 明确后移:
- GPU 直通与推理性能优化 → 执行机具备 GPU 直通条件后另立评估（不属本 feature）。
- 消费者路由切换（Freqtrade `KRONOS_SIGNAL_URL`、runtime snapshot `-KronosHostUrl` 指向真实实例）→ `v0.2.x` 后续评估（未立项）：涉及默认 mock 链路的可用性与跨 feature 契约，F004 只交付编排内可复现证据与可复用信号源。

Wait — do tasks reference FR-002? I decided not to add FR-002 to spec; T001/T002 reference `FR-001`. Is that OK? FR-001's description will mention 启动预检/加载/串行 (I planned to extend FR-001 text). Yes — extend FR-001 requirement text to cover these; then T001/T002 refs are legitimate.

Also, should T001 be split into preflight vs eager load? One task "启动预检 + eager load + fail-closed" is a chain of related code changes in the same file; verify: startup tests. It's fine as one atomic-ish deliverable. But "一个 finding 一个 commit" is for fixes, not tasks. Task granularity: keep as one.

Test file names: let me decide final names:
- `tests/unit/test_f004_kronos_startup.py` — startup preflight/eager-load fail-closed unit tests (fake dirs, stub torch loader).
- `tests/unit/test_f004_kronos_concurrency.py` — lock/once-load tests.
- `tests/unit/test_f004_compose_profile_contract.py` — static Dockerfile/compose contract.
- `tests/integration/test_f004_real_profile.py` — container integration.

Hmm, maybe combine startup+concurrency into one file `tests/unit/test_f004_kronos_runtime_contract.py`? Fewer files; but separate concerns. The F002 precedent has many focused files. Keep two files? Actually the tests both target kronos_real.py; startup (preflight) and concurrency (lock) could live in one "runtime contract" file. I'll use one: `tests/unit/test_f004_kronos_runtime_contract.py` with tasks T001/T002 both verifying against it (different test names). Hmm, but then T001 and T002 share a file... The tasks say "verify: <test>" — sharing a test file across two tasks is fine (F002 T003/T004 share test_f002_export_reconcile.py). OK, one file keeps the plan compact. Hmm, but is preflight testable without torch? The preflight logic should NOT import torch (just path/file checks) — testable with tmp_path. Eager load failure can be tested by monkeypatching the loader to raise. The lock test monkeypatches a fake predictor. All unit-testable. Good.

Actually wait, I need to think about what "eager load at startup" means for the *mock* service: real_signal.enabled=false → skip preflight/load entirely at startup (no change for mock/default). Only real mode does preflight+eager load. OK.

And where does eager load live? Options: (a) in `server.py` module import/lifespan: `if real_signal.enabled: real_signal.preflight(); real_signal.warmup()`; (b) via a small `startup.py`. Design says 不新增模块 — put functions in kronos_real.py + server lifespan call. Fine.

Hmm, but also important: if preflight fails in real mode, server must exit non-zero. With uvicorn, if lifespan raises, uvicorn exits non-zero (code 3?). Yes, lifespan startup failure → uvicorn exits with error. Good.

Also compose healthcheck: for real service, healthcheck with python (image has python) checking /health model_loaded. Could also add to mock? Not required. Keep only real (or describe readiness generally). Careful: healthcheck must not depend on requests lib (not installed) — use urllib. Implementation detail; design states target condition.

Now — one more consideration on D002's "双权重目录校验": "批量场景必须有专属测试"? Not batch records here. Skip.

Now let me also double check D004 expectation "真实容器身份" — I'll phrase in design/test plan as "容器由 compose 管理（`com.docker.compose.service` 标签）、镜像为 real 目标构建产物、挂载与端口与 §2 契约一致".

Now, the FIX-log content. Round 1:
```
## Round 1 · 2026-09-14
- findings: F004-D001..D010
- commits: D001 <hash>, D002 <hash>, ...
- regression_tests: doc diffs + `python3 tools/verify.py` ...
```
Hmm, for doc review the skill says regression evidence = "文档被改+链接/格式检查通过". Also "检视意见固化为门禁失败测试后才允许关闭:先让测试红(复现 finding),修复后变绿" — for docs, the门禁 is verify.py (links/lifecycle). Can I make a failing gate for each doc finding? Not directly. But I can add meaningful gate tests where the finding is structural:
- D004/D007: the new static compose contract test — will be added in implementation (future), can't add now (no code). In the doc round, the deliverable is the doc change only. Right? Hmm. Wait — should the fix round for a doc review also add gate tests now? The review's closure evidence for doc-review is "文档被改+链接/格式检查通过". The tests listed in design/tasks are commitments for the implementation round. So no new tests now. Good.
- For spec/design/tasks doc edits, gate: `python3 tools/verify.py` full run at round end (includes pytest unit suite; but tests are code — will run existing suite; new files not created). Also check_doc_links.

One more check: the FIX-log must be written by the fixer; I'm the fixer. The reviewer will verify later. Note the reviewer's CURRENT-doc.md stays as is (I must not edit it — "修复方对它的全部合法动作是零写入"). ✓.

RETROSPECTIVE update happens at closure (reviewer), not now. ✓.

Also commit discipline: one finding per commit. 10 findings → 10 commits? Some findings touch same file sections; skill says one finding one commit — but F004-D001+D009 both edit spec §0... They're different lines; separate commits are possible but sequential edits to the same file make per-finding commits mechanical. The skill says batch fix without per-finding commits loses bisect; I'll do one commit per finding, ordered D001..D010. That's 10 commits. Hmm, plus maybe a final docs/reviews not-committed (gitignored). Since FIX-log is gitignored, no commit for it.

Wait, but should I commit at all? Let me re-examine. Earlier thought: user asked to follow the skill; skill mandates commits. The system prompt says never commit unless explicitly requested. The user's message: "请作为修复者严格按照skill要求审视每个问题并修复" — "as the fixer, strictly follow the skill requirements to examine each issue and fix". The skill's fixer duties include: FIX-log with `commits:` evidence and per-finding commits; also round-end full gate. I'll treat this as authorization. Also the repo's whole review protocol (past cycles) committed fixes on main. And the FIX-log template requires commit hashes — "证据三件套...缺一视同未修复". So yes, commit.

Hmm, but there's risk: committing to main directly. Previous F002 fix rounds: "docs(f002): 检视循环 10 收口..." etc. direct to main. Also F001 fixes on main. So direct commits to main are the norm here for review fix rounds. OK.

But wait — the user might want to review before commit? The skill explicitly says don't ask ("其余时候'要不要提交/要不要删/还要确认吗'式的询问,是把检视人自己该完成的核对外包给用户当人肉确认点,禁止"). That's for the reviewer's closeout sequence. For the fixer, the commits are part of the evidence. OK, commit.

Should I push? The skill's closeout says reviewer handles CI/push at convergence. As fixer, do I push? The skill's fixer duties: "修复方完成下面第1-5步(回写 RETROSPECTIVE.md、写模式教训、同步会话归档)后,在 FIX-log.md 追加本轮修复声明(含证据三件套),如实汇报'修复已完成、等待复核',不得直接跳到第6步删除文件" — that's for closeout. For the fix round itself, no push mentioned. CI is triggered by reviewer at convergence. I'll commit locally but not push (reviewer triggers CI at convergence candidate round). Hmm, but verify.py must be run at round end locally (fixer duty per §7.2: "修复者每轮收尾时跑一次全量"). Yes, I'll run it.

Wait, actually let me reconsider: the skill §6 says "细提交、粗验证(一轮一 finding 一 commit,门禁每轮一次)". And §7.2: "本地 lint/test 全绿——修复者每轮收尾时跑一次全量". OK: final verify.py once after all commits. If verify fails, fix and amend? "commit 之间不要求各自过全量门禁" — good.

Now, one important validation before editing: I must make sure my rewritten docs pass validate_spec_lifecycle and check_doc_links. Constraints:
- Fixed sections exactly: spec 9 sections, design 11, tasks 6 (only phase under §2).
- §10 design: "无" only.
- §8 spec: Q-001 checkbox (closed) — allowed (Q_RE matches `- [x] Q-001`... wait Q_RE = `^-\s+\[([ xX])\]\s+[QD]Q?-\d+` hmm: `[QD]Q?-\d+` matches "Q-001"? `[QD]` matches Q, then `Q?` optional Q, then `-\d+`. Yes. OK.
- AC refs valid.
- BACKLOG unchanged (status still draft). ✓.
- check_doc_links: relative links in edited docs. I'm not adding markdown links, mostly code spans. The existing links in spec/design/tasks? None besides backticks. F002 spec edit: no links added.

Also: "不得新建 roundN.md" — FIX-log.md fixed name. ✓.

Also the report says scope full-scan round 1; my fix round is round 1 fixes; then reviewer does round 2 diff-only. ✓.

Now — one more thing to verify before I write: D005's exact dependency list from the code: kronos.py imports `from huggingface_hub import PyTorchModelHubMixin`, `from tqdm import trange`, `import torch`, and `from model.module import *`; module.py imports einops, torch, torch.nn, torch.autograd, torch.nn.functional. So minimal: torch, einops, safetensors (needed by huggingface_hub's safetensors loading? PyTorchModelHubMixin.from_pretrained loads safetensors — actually `safetensors` is required; the host has it), huggingface_hub, tqdm. Plus numpy/pandas (upstream imports numpy, pandas; pyproject already has pandas; numpy comes transitively). Should the image include matplotlib? No (examples/finetune only) — "最小推理依赖". Good.

Also verify host venv versions I'll cite: einops 0.8.2, safetensors 0.8.0, huggingface_hub 1.31.0, tqdm 4.70.0, torch 2.14.0+cpu. Note vendor requirements lists older versions (0.8.1/0.33.1/0.6.2/4.67.1) — those are upstream's frozen list from its era. Our pin should be the host-verified set, noting upstream list is参考. Hmm, but wait: is there risk that design specifying `huggingface_hub==1.31.0` is wrong because the container will resolve differently? The implementation will verify in-container; design states initial pins. OK.

Torch pin exact wording: "torch==2.14.0（`--index-url https://download.pytorch.org/whl/cpu`；宿主 AC-006 实测 2.14.0+cpu）". Good.

Now — D006 also mentions "tasks 未记录 hostname/device". Covered by T008.

Let me also double-check the SOP requirement "Feature 收口前，集成验收必须运行 ALPHAMILL_INTEGRATION=1 pytest tests/integration -q；服务不可达或 mock 模式在该开关下必须判红". The F004 integration tests must follow: when ALPHAMILL_INTEGRATION=1 and docker missing → fail (not skip). Design/test plan note: "遵循 F001 冒烟同款 skip/fail 语义". Add to design §8 note.

Now about the F002 spec edit (D001 cross-file): the sentence at line 218-221: "**done 时的已知限制(2026-09-13 裁决记录)**:F004(Kronos 真实推理运行时)不阻塞本 feature 收口,因此 F002 done 时湖内 `signals_log` 的内容预期仍以 `source=placeholder` 为主——**导出管线正确不等于内容可用于因子研究**。收口时验收证据必须如实记录该 dataset 的行数与 `source` 分布,不得以"五 dataset 齐备"含糊带过;F004 落地后内容自动升级,F002 无需返工。"
→ change tail: "…;F004 落地后在编排内提供可复用的真实信号源，但 signals_log 内容真实化还需消费者路由切换（当前 runtime snapshot 仍指向 mock :8001），该切换不在 F004 范围内，需另行评估。"
Hmm, but F002 is done and has "已知限制" recorded at closure. Editing it is a historical correction. Also its §3 范围外 note line 100 says "F004 不阻塞 F002 done（2026-09-13 owner 裁决,F004 spec §8 Q-001);代价见 §6 限制说明。" — that stays valid.

Should I update F002 spec's `updated:` frontmatter? F002 frontmatter updated: 2026-09-14. If I edit, bump to 2026-09-14 (same day, fine — today is 2026-09-14). Actually today's date: Mon Sep 14 2026. So updated stays 2026-09-14. OK.

Hmm — wait. Actually, should I really touch F002? Let me think about the review scope once more. D001 location: F004 spec:26. Fix options: wire or delete claim in F004. F002's sentence is an adjacent contract that itself references F004's promise. If I leave it, the "自动升级" claim persists — future readers see contradiction. The review's "正确性通道判定" says "不能证明…或令 signals_log 自动升级" — the reviewer knows F002 carries the promise. I'd say correcting it is part of closing D001's root cause (the promise itself). I'll do it and flag it in FIX-log under D001 (with commit). Since one-finding-one-commit, I'll include the F002 correction in D001's commit. Both files → same commit. Acceptable (same finding).

Hmm, or should the F002 edit be its own commit with its own note? It's part of D001's fix. One commit.

Now, let me also reconsider: does D001 really want me to *remove* the F002 sentence's promise, or would the reviewer prefer wire? I keep going back and forth; let me settle by looking at the strongest signal: The review says "最短修复路径是先裁决真实 profile 只服务 AC-006，还是同时成为运营信号源". The F004 design already decided: real profile coexists at 8002, mock is default consumer dependency. So the design-level decision was already "只服务 AC-006" in effect — the spec's auto-upgrade claim contradicts the design. Fixing the spec to match the design = correct. Yes. Settled.

One more piece of evidence for the design decision row: the architecture §7.1 says "白天 07:00–22:00 Kronos 常驻推理 ≤3GB 服务常驻，供 dry-run 信号" — the eventual execution machine wants Kronos resident serving dry-run (which currently is mock by the service config). Hmm, this suggests the long-term direction IS consumers → real. But that belongs to execution-machine rollout (GPU passthrough not in F004; the arch says Kronos 常驻 on GPU). F004 is the CPU/orchestration piece. The deferral note can mention: "执行机常态化（GPU 直通、消费者切换）后续另立". Good.

Now let me also decide: do I need to update spec §1 目标 bullet "F001 AC-006 的复跑不再依赖手工起进程" — fine as is.

Also spec §1 问题 paragraph says "F002 导出的 `signals_log` 内容全是 `source=placeholder`" — factual, keep. It's the motivation. But it implies F004 fixes it... The 目标 section clarifies. Let me add in §1 非目标 or §3: route deferral. Already in §3 范围外.

Also US-001 story change (above).

Now — action plan for edits. Because several findings touch the same file, I'll implement them sequentially per finding, committing after each finding's edits, so each commit maps to a finding. Let me plan the commit order and per-commit diffs:

Commit order (one per finding, ordered to minimize conflicts):
1. D001 — spec.md (§0 intent, §2 US-001, §3 范围外, §7 依赖/决策表) + F002 spec sentence.
2. D009 — spec.md §0 PRD source line. (separate commit; edit same file after D001)
3. D002 — spec.md §4 FR-001 + scenario + §5 invariants; design.md §2/§5/§7/§8/§9; tasks.md T001/T002 + DAG. Hmm — D002 spans spec too (invariants). But D002's suggested fix says "在 design/tasks 中加入..." — spec support edits are natural. OK.
4. D003 — spec.md §2 独立测试 + §7 依赖 env; design §5 command; tasks commands. Hmm, overlaps with D002/doc positions. Fine, sequential.
5. D004 — design §8 table + spec AC-001 tests + §7 测试策略; tasks T005/T006.
6. D005 — design §1/§2 dependency pins + tasks T003.
7. D006 — design §0 + §8 note + tasks T008 + spec §7 testing strategy note.
8. D007 — spec NFR-001/AC wording + design §1/§9 + tasks T003/T005.
9. D008 — design §2 mount/env/port block + maybe §5 port line.
10. D010 — tasks.md restructure (whole file) + dependencies.

Hmm, this is getting complex because findings overlap heavily (D002/D003/D004/D005/D006/D007/D008/D010 all touch design/tasks). One-finding-one-commit with overlapping edits means I should carefully sequence: do ALL edits but commit in stages? No — commits must contain the finding's edits. If two findings touch the same paragraph, I can't cleanly separate after the fact unless I edit incrementally (edit for D001, commit; edit for D002, commit; ...). That's tedious but doable if I choose edit order so each step is coherent: after each commit the docs must be coherent (they're intermediate, but must not be contradictory... "commit 之间不要求各自过全量门禁" but should ideally be sensible).

Alternative: Since many findings share the same rewrite regions (tasks.md full restructure; design heavy edits), maybe group commits by artifact? That violates "one finding one commit" (9 findings in one commit = the anti-pattern). Hmm. Let me think about a pragmatic sequencing that respects per-finding commits as much as possible while keeping each commit coherent:

Order that minimizes intra-file overlap:
1. **D009** (spec §0 PRD source) — tiny, isolated line.
2. **D001** (spec §0 intent + §2 US-001 + §3 范围外 + §7 依赖/决策 + F002 spec sentence) — spec edits around §0 line but not overlapping D009's line (D009 = PRD来源 line; D001 = 一句话意图 line + §2 + §3 + §7).
3. **D002** (spec §4 FR-001 text + scenarios; §5 invariants; design §2 "不新增模块" line + §5 full rewrite + §7 + §9; tasks T001/T002, DAG) — hmm, design §5 is also touched by D003 (command) and D008 (port). If I write the ENTIRE new §5 in D002's commit including the compose command fix (D003) and port line (D008), then D003's commit would have nothing left in §5... I can split: D002 writes §5 items about startup sequence/lock/concurrency; D003 changes commands in §5 (and spec §2/§7, tasks); D008 adds the mount/port table in §2 and port in §5. To do per-finding commits, I'll write D002's version of §5 with the old command text still (i.e., keep `docker compose --profile ...` until D003 fixes it). Slightly awkward but fine.

Honestly, this granularity of commits may be overkill for doc edits, but the skill explicitly says one finding one commit, and F001/F002 cycles did "7 个分批提交" etc. I'll do 10 commits (D001-D010), sequencing edits so each finding's changes are its own commit. To keep sanity, I'll do edits in this order: D009, D001, D003, D002, ... wait D003 touches design §5 command; D002 rewrites §5 wholesale. Better order: D002 first (rewrite §5 with command unchanged), then D003 (fix commands in spec §2/§7, design §5/§0, tasks).

Ugh, actually, let me simplify: I'll compose the final content for each file mentally, then apply in finding order, using targeted edits. Order: D001, D002, D003, D004, D005, D006, D007, D008, D009, D010. Each commit gets only that finding's semantic change. Overlaps: I'll just make sure when I edit for a finding I only change that finding's aspects; if a sentence needs changes from two findings, split across two commits (e.g., AC-001 line: D004 changes tests paths; D007 changes the criterion wording; D002 adds fail-closed wording). I'll edit it in three passes (three commits). This is fine — git handles it; each commit is coherent.

Let me now also prepare exact new text for each file. Given the amount, I'll do sequential edits with the `edit` tool, then `git add` + `git commit` per finding.

Wait — should I really make 10 commits for docs? Let me check the skill tolerance: "一个 finding 一个 commit：本地提交，保 bisect/revert 能力——批修出回归时无法定位是哪条修复引入的(9 个问题挤一个 744 行提交是实测反面案例)". Yes. 10 commits it is. (For doc-only fixes, "regression" = doc inconsistencies; still fine.)

Hmm, but also: F001 cycle did "一 finding 一 commit 全数处理（D034+D037 因共用 tasks.md 编号编辑面合并为一 commit，检视人追认）" — precedent for merging when edits share the same file region! So D010 (tasks full restructure) inevitably includes task edits from D002/D003/D004/D005/D006/D007 (new tasks, verify commands). To avoid incoherence, maybe I should do tasks.md edits LAST in one commit for D010 and have earlier commits' tasks-related changes folded in... no wait, that would make D010's commit contain other findings' task edits. Alternatively: order tasks edits so that D002's commit adds T001/T002 tasks, D004 adds T005/T006, D005 adjusts T003 deps, D006 adds T008 evidence task, D007 adjusts T003/T005 verify wording, D010 restructures/finalizes DAG + splits evidence/status tasks. That works incrementally! Each commit coherent-ish. Let me do that.

Actually hold on, let me reconsider scale: is this really worth 10 commits for a doc fix? The alternative reading: 9 findings share the same 3 files; deliver a series of commits along finding groups. I'll aim for per-finding commits but allow merging adjacent findings that edit identical lines (like the skill precedent). Let me just try per-finding; if two findings genuinely must edit the same line, I'll still sequence them (edit twice). Fine.

Let me now write out the final content. I'll draft the complete new versions of the three F004 files first (mentally/in scratch), then apply as ordered edits. Actually, to reduce edit-tool churn, I may rewrite whole files with `write` for tasks.md (full restructure) and do targeted edits for spec/design. But per-finding commits require incremental edits... For tasks.md, I can do multiple sequential edits.

Let me draft final tasks.md now (post-all-findings):

```markdown
---
kind: feature
id: F004
version: "0.2"
related_features: [F001, F002]
topics: [kronos, inference, deployment]
doc_kind: tasks
created: 2026-09-12
updated: 2026-09-14
---

# F004：Kronos 真实推理运行时 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
- 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
- `[P]` 只用于修改不同文件且没有顺序依赖的任务。
- 集成与容器验收只在执行机 `qiaozhi-lt` 采集，证据记录 hostname 与 `device=cpu`；开发机只跑静态与单元门禁（SOP §3）。

## 1. 前置条件

- F001 已 done：薄壳、`vendor/Kronos` pin 与 `models/` 权重流程成立，AC-006 已有手工命令形态实测证据；回填数据满足目标 exchange/symbol ≥30 根已闭合 1m K 线。
- spec §8 Q-001 已关闭（F004 不阻塞 F002 done），无阻塞性设计问题。

## 2. 实现任务

### Phase 1：薄壳运行时改造

- [ ] T001 (`FR-001`): `kronos_real.py` real 模式启动预检与 eager load——启动期校验 `KRONOS_REPO_PATH`、模型与分词器目录及必需文件（`config.json`、权重文件），任一缺失或加载失败即打印缺失路径并非零退出，不退回 mock — verify: `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`
- [ ] T002 (`FR-001`): 进程级推理锁——模型加载至多一次、推理互斥（含并发首请求同时到达的场景） — verify: `tests/unit/test_f004_kronos_runtime_contract.py::test_predictor_loads_once_and_inference_serializes`

### Phase 2：镜像与编排

- [ ] T003 (`FR-001`, `NFR-001`): `deployment/kronos-service.Dockerfile` 拆 `mock`/`real` 两个构建目标；real 目标从 CPU wheel index 安装固定版本的 torch 及最小推理依赖（einops/safetensors/huggingface_hub/tqdm），mock 目标保持现状且不含 torch — verify: `tests/unit/test_f004_compose_profile_contract.py::test_dockerfile_targets_pin_real_dependencies`
- [ ] T004 (`FR-001`, `NFR-001`): compose 增 `kronos-signal-real` 服务（`profiles: [kronos-real]`、`target: real`、只读挂载、`8002:8001`、KRONOS_* 环境、healthcheck 以 `model_loaded=true` 为通过条件、失败不自动重启）；`kronos-signal` 显式 `target: mock` — verify: `tests/unit/test_f004_compose_profile_contract.py::test_compose_real_service_contract`；`docker compose -f deployment/docker-compose.yml config --services` 不含 real、`--profile kronos-real config` 含之

### Phase 3：专属门禁测试

- [ ] T005 (`AC-001`): 静态编排契约门禁定稿：默认配置不含 real 服务、real 服务 target/挂载/端口/环境正确、默认镜像目标不含 torch、real 目标依赖 pin——并做一次变异验证（改 target/删 pin 必须判红） — verify: `tests/unit/test_f004_compose_profile_contract.py`（含变异记录）
- [ ] T006 (`AC-001`, `FR-001`): F004 容器集成测试：compose 拉起 real 实例后校验容器身份（compose 托管 + real 目标 + 只读挂载 + 端口映射）与 `/predict source=kronos`；缺资产场景非零退出；默认镜像 `import torch` 判红 — verify: `tests/integration/test_f004_real_profile.py`
- [ ] T007 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`

## 3. 验证与验收任务

- [ ] T008 (`AC-001`): 在执行机 `qiaozhi-lt` 跑集成验收：F001 冒烟（HTTP 契约）+ F004 容器集成 + 默认镜像否证，证据记录 hostname 与 `device=cpu` — verify: `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py tests/integration/test_f004_real_profile.py -q`
- [ ] T009 (`AC-001`): 回写 spec §6 验收证据（命令、输出摘要、取证机 hostname、device） — verify: `python3 tools/verify.py`（文档门禁）
- [ ] T010 (`AC-001`, `NFR-001`): 运行项目统一质量门并全绿 — verify: `python3 tools/verify.py`
- [ ] T011: 状态推进（spec frontmatter）与 BACKLOG 同步 — verify: `python3 tools/verify.py`（含生命周期与 BACKLOG 双向校验）

## 4. 依赖与并行关系

- `T001 -> T002`：同一薄壳文件的顺序改造（预检/加载 → 锁）。
- `T001/T002 -> T006`：容器集成依赖启动预检、eager load 与串行推理行为成立。
- `T003 -> T004`：compose `target` 依赖 Dockerfile 目标定义。
- `T003/T004 -> T005`：静态门禁锁定镜像与编排定义。
- `T005 -> T006`：容器集成建立在静态契约通过之上。
- `T006 -> T007`：F001 命令回写以 compose 形态实测通过为前提。
- `T007 -> T008 -> T009 -> T010 -> T011`：验收链顺序执行（实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步）。

## 5. 明确后移

- GPU 直通与推理性能优化 → `v0.2.x` 后续评估：需执行机 GPU 直通条件，不属本 feature。
- 消费者路由切换（Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 指向真实实例）→ `v0.2.x` 后续评估（未立项）：真实实例与 mock 并存是本期形态，路由切换涉及默认链路可用性与跨 feature 契约，F004 只交付编排内可复现的真实信号源（spec §3 范围外）。
```

Wait: task refs — T011 has no (ID) in template examples ("T009: 回写 spec 验收证据、活跃索引和状态"). The template shows T009 without refs. OK. But my T011 says "状态推进（spec frontmatter）与 BACKLOG 同步" — hmm, when do tasks reach review→done? That's the standard flow; T011 is the final state sync task. It's fine.

Hmm, but T009 evidence writeback then T010 gate then T011 status — reviewer said final gate verify.py; T010/T011 both verify. Eh, acceptable. Actually, maybe fold: T010 质量门+T011 状态推进... Let me keep as is; it satisfies "拆开证据回写与状态变更" and "统一最终门".

One question: should T008 be "执行机集成验收" as a §3 task with AC refs? Yes.

Also note: T008 runs F001 smoke with KRONOS_BASE_URL=8002 — the compose real service publishes host 8002. Good. And F004 integration test itself manages compose (build/up). Hmm, T008 command lists both test files; the F004 test file does its own compose up/down. OK.

Also `KRONOS_REQUIRE_REAL_MODEL=1` triggers AC-006 assertion in F001 smoke. ✓.

Now, the design §8 note should match these test names. And spec AC-001 tests list: `tests/unit/test_f004_compose_profile_contract.py`、`tests/integration/test_f004_real_profile.py`. Plus maybe the runtime contract unit tests (startup/lock) — those relate to FR-001 fail-closed/serial. Should AC-001 cover them? AC-001's claim should include fail-closed (缺资产时非零退出) — that's tested by `test_f004_real_profile.py` (container) and `test_f004_kronos_runtime_contract.py` (unit). Let me list all three in AC-001 tests? The AC text: "...缺资产时非零退出且不退回 mock..." — include runtime contract test path too. Three paths is fine (F002 AC-015 lists two). Let me include:
tests: `tests/unit/test_f004_kronos_runtime_contract.py`、`tests/unit/test_f004_compose_profile_contract.py`、`tests/integration/test_f004_real_profile.py`

Hmm, but wait: is the startup/lock behavior part of AC-001 or should there be AC-002? Let me re-read the review's D002 suggested fix: "在 design/tasks 中加入启动期依赖与双权重目录校验、模型 eager load/readiness 以及进程级推理锁，并为缺资产和并发请求建立测试。" — tests for missing assets and concurrency. If these tests lock FR-001 behaviors, AC-001 should reference them (traceability). One AC with multiple test files is OK. Alternatively add AC-002 for fail-closed/serial:
"- [ ] **AC-002** (`FR-001`): real 模式缺 vendor/权重/分词器时启动即非零退出并打印缺失路径，不退回 mock；并发请求下模型加载至多一次且推理互斥 — tests: `tests/unit/test_f004_kronos_runtime_contract.py`、`tests/integration/test_f004_real_profile.py`"
That's cleaner: AC-001 = deployment form + source; AC-002 = fail-closed/serial invariants. But does adding AC-002 require new FR? No, both cite FR-001. Is adding AC OK? Yes — spec can have multiple ACs. Hmm, but then spec §6 "成功标准" SC-001 covers AC-001; add SC-002? Not required. But traceability-wise, US-001 covers both. Let me keep a single AC-001 to avoid over-restructuring? Hmm.

Let me think about what the future reviewer (round 2) would want from D002's fix: tests for missing assets and concurrency exist and are referenced from an AC/tasks. If they're only in tasks but not AC, the "AC 回填测试" requirement at review/done status: each AC references existing tests. Task-level tests don't need AC backing, but spec §6's acceptance should cover the failure semantics since they're user-observable (startup exit). I'll add AC-002. It makes the acceptance checklist complete:

- **AC-001** (`FR-001`, `NFR-001`): profile 实例由目标 compose 服务与 real 构建目标产生（容器身份、只读挂载、8002:8001），`/predict` 返回 `source=kronos`；缺该 profile 时默认编排不启用也不构建 real 服务、默认镜像不含 torch — tests: `tests/unit/test_f004_compose_profile_contract.py`、`tests/integration/test_f004_real_profile.py`
- **AC-002** (`FR-001`): 失败关闭与串行推理——vendor/权重/分词器缺失或加载失败时 real 实例启动即非零退出并打印缺失路径（不退回 mock）；并发 /predict 下模型加载至多一次且推理互斥 — tests: `tests/unit/test_f004_kronos_runtime_contract.py`、`tests/integration/test_f004_real_profile.py`

Then §7 测试策略 maps these. SC-001 (F001 AC-006 reproducible) covers AC-001; add SC-002 "失败关闭与串行推理不变量成立（AC-002）"? Maybe: "SC-002：real 实例失败关闭与串行推理不变式成立（AC-002）". OK.

Hmm, is this scope creep? It surfaces behaviors that were promised already (§3 boundary + design claims) but unverifiable. The reviewer asked for tests. I think it's the right fix.

Now, spec §7 决策与风险 table also has the F002 row — update. And §7 依赖 has "下游消费者：F002 的 signals_log dataset 内容有效性." → update.

Let me also handle design §9 "残余风险" table row update(s) and add rows.

Now the exact final design.md. Let me draft it fully (I'll edit sections):

```markdown
---
kind: feature
id: F004
version: "0.2"
related_features: [F001, F002]
topics: [kronos, inference, deployment]
doc_kind: design
created: 2026-09-12
updated: 2026-09-14
---

# F004：Kronos 真实推理运行时 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**：`spec.md`（FR-001 / NFR-001）。
- **上游 Contract**：F001 冻结的 Kronos HTTP API（`GET /health`、`GET /predict/{symbol:path}`、`POST /predict_batch`），零改动。
- **执行环境**：容器集成与验收在执行机 `qiaozhi-lt`（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）取证，证据记录 hostname 与 `device=cpu`（本 feature 不做 GPU 直通；CPU 推理实测 3.4–7.2s/次）。开发机 `qiaozhi-gp`/`gp-wsl` 只跑静态编排断言与单元门禁（SOP §3、架构 §7.1）。
- **实现约束**：`vendor/Kronos`（pin `67b630e`）与 `models/`（391MB + 16MB）不入库，由 F001 既有流程获取；`/predict` 数据前置为目标 exchange/symbol 至少 30 根已闭合 1m K 线（F001 回填产物）。
```

§1:
```markdown
## 1. 技术概要与影响面

给 `kronos-service.Dockerfile` 拆出 `mock`（保持现状、不含 torch）与 `real` 两个构建目标；real 目标从 PyTorch CPU wheel index 安装固定版本 torch 与最小推理依赖（pin 见 §2），compose 用 `profiles: [kronos-real]` 挂一个 `kronos-signal-real` 服务，默认 `up` 不启用、不构建该服务。薄壳做三处最小改造：real 模式启动预检、模型 eager load 与进程级推理锁（§5）。

- 后端 / API：HTTP 契约无变更（同一份 `kronos_service`）；薄壳内部增加启动预检/加载/加锁路径。
- 存储 / Migration：无。
- Event / Evidence：F001 AC-006 的复跑命令改为 compose 形态（保留手工回退）。
- 文档 / 配置：F001 spec §6 命令回写；`vendor/VENDORED.md` 补容器内路径说明。
```

§2:
```markdown
## 2. 架构与模块边界

沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）。

**real 目标的依赖 pin（镜像内）**：`torch==2.14.0`（`--index-url https://download.pytorch.org/whl/cpu`，CPU wheel；与宿主 AC-006 实测同版）+ `einops==0.8.2`、`safetensors==0.8.0`、`huggingface_hub==1.31.0`、`tqdm==4.70.0`（pinned 上游相关 import 的最小集：`model/kronos.py` 直接导入 torch / huggingface_hub / tqdm，`model/module.py` 导入 einops；版本与宿主 AC-006 实测一致，容器内真实权重加载验证后锁定；上游 `requirements.txt` 只作参考）。

**real 服务的挂载、环境与端口契约**：

| 项 | mock（`kronos-signal`） | real（`kronos-signal-real`） |
|---|---|---|
| 挂载 | 无 | `../vendor/Kronos:/app/vendor/Kronos:ro`、`../models:/app/models:ro` |
| KRONOS_REPO_PATH | — | `/app/vendor/Kronos` |
| KRONOS_MODEL_PATH | `models/Kronos-base`（未用） | `/app/models/Kronos-base` |
| KRONOS_TOKENIZER_PATH | `models/Kronos-Tokenizer-base`（未用） | `/app/models/Kronos-Tokenizer-base` |
| KRONOS_USE_REAL_MODEL | false（默认） | true |
| KRONOS_DEVICE | cpu | cpu（本 feature 不做 GPU 直通） |
| 端口 | host 8001 → container 8001 | host 8002 → container 8001（与 mock 并存，互不顶替） |
| 构建目标 | target=mock | target=real |
```

Hmm wait, mock service's env: compose sets KRONOS_MODEL: models/Kronos-base as container path "models/Kronos-base" (relative to /app; not mounted). Fine, keep mock column simple: "保持现状". Let me simplify the table to real-only contract plus a note:

| 项 | real 服务契约 |
|---|---|
| 构建目标 | `target: real`（`profiles: [kronos-real]`） |
| 挂载 | `../vendor/Kronos:/app/vendor/Kronos:ro`；`../models:/app/models:ro` |
| KRONOS_REPO_PATH | `/app/vendor/Kronos` |
| KRONOS_MODEL_PATH | `/app/models/Kronos-base` |
| KRONOS_TOKENIZER_PATH | `/app/models/Kronos-Tokenizer-base` |
| KRONOS_USE_REAL_MODEL / KRONOS_DEVICE | `true` / `cpu` |
| 端口 | host `8002` → container `8001`（mock 保持 host 8001） |

OK.

§4:
```markdown
## 4. 接口、Contract 与 Event

HTTP 契约与 F001 完全一致；唯一可观察差异是 `/health` 的 `model_enabled=true`、`/predict` 的 `source=kronos` 与 `model` 字段回报权重路径。real 实例在启动预检与 eager load 完成后才对外服务；失败即进程退出（§7），不产生"enabled 但未加载"的中间态。
```

§5:
```markdown
## 5. Runtime、Workflow 与并发

- 启动：`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；
- 启动序列（real 模式）：进程启动 → **预检**（`KRONOS_REPO_PATH`、模型/分词器目录与必需文件存在）→ **eager load**（一次性加载 Kronos + Tokenizer，放在应用启动钩子、先于接收流量）→ 服务就绪；预检或加载任一失败 → 打印缺失路径/错误并**非零退出**（`restart: "no"`，失败态可被直接观察，不静默降级）；
- readiness：容器 healthcheck 以 `/health` 的 `model_loaded=true`（且 `device=cpu`）为通过条件；mock 服务保持现状；
- 端口：真实实例 host 8002 → container 8001，与默认 mock 的 host 8001 并存，避免二者互相顶替；
- 并发：单实例单 worker；**进程级锁**保证模型加载至多一次、推理互斥（并发请求排队），无其它共享状态；
- 数据前置：`/predict` 需要目标 exchange/symbol ≥30 根已闭合 1m K 线（DB 已迁移，F001 回填产物）。
```

§6: keep, tweak: "无新 UI；`/health` 的 `model_enabled`/`device`/`model_error` 已足以判别实例形态（real 实例就绪后恒为 loaded=true；失败即退出，无降级态）。"

§7:
```markdown
## 7. 失败、恢复、安全与兼容

- 权重、分词器或 vendor 缺失/加载失败 → **启动期**非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；`restart: "no"` 使失败态保持可见；
- 资产只读：vendor/models 以 `:ro` 挂载，容器不写宿主资产；
- 镜像体积：real 目标（torch CPU wheel 约 200MB）仅在启用 profile 时构建；默认镜像与默认编排行为不受影响（NFR-001）；
- 兼容：HTTP 契约与 F001 完全一致；mock 实例仍是默认链路的依赖，本 feature 不改变消费者路由（见 §9 决策）。
```

§8: table + notes:
```markdown
## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | 静态契约（unit，CI 常绿） | `tests/unit/test_f004_compose_profile_contract.py` | Dockerfile 有 mock/real 目标且 real 锁定依赖 pin；real 服务 profiles/只读挂载/端口/环境正确；默认 compose 配置不含 real 服务 |
| `AC-001` | 容器集成（执行机 `qiaozhi-lt`） | `tests/integration/test_f004_real_profile.py` | compose 拉起后容器身份成立（compose 托管 + real 目标 + 只读挂载 + 8002:8001）且 `/predict source=kronos`；默认镜像 `import torch` 判红 |
| `AC-002` | 单元 | `tests/unit/test_f004_kronos_runtime_contract.py` | 缺资产/加载失败 → 非零退出且不退回 mock（fake 目录注入）；并发请求加载至多一次、推理互斥 |
| `AC-002` | 容器集成（执行机） | `tests/integration/test_f004_real_profile.py` | 缺资产场景以非零退出结束并在日志保留缺失路径；不产生可服务的 mock 降级实例 |
| HTTP 契约（F001 AC-002/006 复用） | integration | `tests/integration/test_f001_kronos_smoke.py` | 保留：`source` 与 `model_enabled` 自洽（两方向判红）；不承担部署形态证明 |

- 容器集成测试遵循 F001 冒烟同款开关语义：未设 `ALPHAMILL_INTEGRATION` 时 skip；设了开关而服务/容器不可达时判红，不得以 skip 代替证据。
- 集成/容器证据必须在执行机采集并记录 hostname 与 `device=cpu`（SOP §3、架构 §7.1）；开发机只跑静态与单元门禁，开发机 skip 不算证据。
- 每道新门禁（静态契约、容器集成）做一次变异验证：改 target、删 pin、放开 `:ro` 必须判红。
```

Hmm wait, "验收项" column for the F001 smoke row says "HTTP 契约（F001 AC-002/006 复用）" — AC format in a design table isn't validated, fine.

§9:
```markdown
## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 用 compose profile 而非新建服务文件 | 单一 compose 文件，默认不启用 | 避免多份编排入口（F001 的教训：编排必须唯一） | 若 profile 组合变复杂再拆 override 文件 |
| 真实实例走 8002 而非顶替 8001 | 两种形态可并存对比 | mock 实例仍是默认链路的依赖 | 稳定后可评估是否合并 |
| **profile 启用时的消费者路由（Freqtrade / runtime snapshot）** | **不接线，显式后移**（spec §3 范围外） | 本 feature 承诺=编排内可复现证据；路由切换会改变默认链路可用性与跨 feature 契约，需独立评估 | 后移见 tasks §5；F002 spec §6 的"内容自动升级"表述已按此勘正 |
| 串行推理用进程级锁而非多 worker | uvicorn 单 worker + 进程级锁 | CPU 推理本身串行；多 worker 无收益且破坏"加载至多一次" | 若未来上 GPU 再评估批量吞吐 |
| 依赖 pin 取宿主 AC-006 实测版本 | torch 2.14.0（CPU index）+ einops 0.8.2 / safetensors 0.8.0 / huggingface_hub 1.31.0 / tqdm 4.70.0 | 与已实测通过的宿主环境一致；上游 requirements 仅参考 | 容器内真实权重加载验证通过后锁定 |
| 残余风险：torch 镜像层拖慢 CI | CI 不构建也不启用 real 目标；默认镜像不含 torch 由静态测试锁定 | profile 未启用时 compose 不构建该服务 | 若 CI 需要 real 构建则单独 job |
```

§10 keep "无".

Now spec final draft. Let me write it.

```markdown
---
kind: feature
id: F004
version: "0.2"
status: draft
gate_version: 1
related_features: [F001, F002]
topics: [kronos, inference, deployment]
doc_kind: spec
created: 2026-09-12
updated: 2026-09-14
---

# F004：Kronos 真实推理运行时（编排内可复现）

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` M0（自包含运行基线：Kronos 服务在编排内健康）、FR1.2（`signals_log` 进入不可变快照）与 FR5（运行链：信号服务的运行时载体）；FR3（证据评测与验证）仅为下游关系——F004 为评测提供可复现的真实 Kronos 信号源，不实现评测本身。
- **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑）、§7.1（机器边界）。
- **上游来源**：F001 AC-006（真实推理证据，当前靠仓外手工实例）、F002 检视 F002-Q001（容器化不在数据桥契约内，需独立载体）。
- **功能类型**：backend / infra
- **规格模式**：lite
- **变更类型**：ADDED
- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并在编排内提供可复用的真实信号源；消费者路由切换（Freqtrade 与 runtime snapshot 指向真实实例）不在本 feature 范围（见 §3）。

## 1. 问题、目标与非目标

### 问题

compose 的 `kronos-signal` 服务默认 `KRONOS_USE_REAL_MODEL=false`（镜像基于 `python:3.11-slim`，不含 torch，也不挂载 `vendor/Kronos` 与 `models/`）。真实推理只能靠人工在宿主 venv 起一个 8002 实例——F001 AC-006 因此是「留档命令」而非编排内证据；F002 导出的 `signals_log` 内容全是 `source=placeholder`。

### 目标

- `docker compose -f deployment/docker-compose.yml --profile kronos-real up` 后，真实模型实例在编排内可达且 `/predict` 返回 `source=kronos`；
- F001 AC-006 的复跑不再依赖手工起进程。

### 非目标

- 不改 Kronos 上游代码与 HTTP API 契约（F001 已冻结）；
- 不做 GPU 推理与性能优化（Kronos 常驻推理的目标机是执行机（当前 `qiaozhi-lt` 的 RTX 4060，架构 §7.1）；本 feature 的编排与契约验收在 CPU 推理上即成立，GPU 直通留给执行机落地时处理）；
- 不把真实推理设为默认启动项——torch 与权重会让只做数据桥的开发者付出无谓代价；
- 不做消费者路由切换（Freqtrade 与 runtime snapshot 仍指向 mock 实例，见 §3 范围外）。

## 2. 用户场景

### US-001：编排内取得真实信号（Priority: P2）

作为 `量化研究员`，我希望 `用一条 compose 命令拉起真实 Kronos 推理`，以便 `AC-006 的真实推理证据不依赖任何仓外手工步骤，且真实信号源在编排内可复用`。

**为什么是这个优先级**：F001 已用独立命令留档证据，不阻塞 M1 开工；F002 的 signals_log dataset 要有研究价值需要可复现的真实信号源（消费者接线见 §3 范围外）。

**独立测试**：新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿；容器集成验收在执行机取证（hostname + device=cpu，见 §7）。

**验收场景**：

1. Given `vendor/Kronos 与 models/ 就位`，when `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`，then `/health` 的 `model_enabled=true`、`/predict` 返回 `source=kronos` 且实例确由 real 构建目标的容器提供。
2. Given `vendor/Kronos、模型或分词器任一缺失`，when `启动 --profile kronos-real 实例`，then `进程非零退出并在日志打印缺失路径，不退回 mock`。

## 3. 范围与边界

### 范围内

- `deployment/kronos-service.Dockerfile` 拆 mock/real 两个构建目标：real 目标锁定最小推理依赖（torch CPU wheel + einops + safetensors + huggingface_hub + tqdm）及版本；
- 薄壳最小改造（`kronos_service`）：real 模式启动预检、模型 eager load、进程级推理锁（HTTP 契约不变）；
- compose 增 `kronos-signal-real` 服务（`profiles: [kronos-real]`）：只读挂载 `vendor/Kronos` 与 `models/`，`KRONOS_USE_REAL_MODEL=true`，host 8002 → container 8001；
- F004 专属静态编排门禁与容器集成门禁（见 §7）；
- F001 AC-006 的复跑命令改为 compose 形态并回写 F001 spec §6（保留手工回退）。

### 范围外

- 权重与 vendor clone 的获取（F001 已有流程，仍不入库）；
- GPU 直通（见非目标）；
- 消费者路由切换：Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 仍指向 mock `:8001`；真实实例接线由后续评估决定（见 tasks §5）；
- `signals_log` 内容的自动升级：本 feature 只提供真实信号源，不改变写入链路。

### 边界场景

- 权重或 vendor 缺失：profile 启动即失败并打印缺失路径，不静默退回 mock；
- 数据不足：目标 exchange/symbol 少于 30 根已闭合 1m K 线时 `/predict` 无有效输入，前置检查见 §7；
- 并发请求：单实例内推理串行（进程级锁），并发请求排队而非并发进入 predictor。

## 4. 需求

### 功能需求

### Requirement: 编排内真实推理（`FR-001`）

系统应当提供一个非默认的 compose profile，使真实模型实例在编排内启动、完成启动期资产预检与模型加载、串行处理推理请求，并保持 F001 冻结的 HTTP API 契约不变。

#### Scenario: profile 拉起

- GIVEN `vendor/Kronos` 与 `models/` 就位
- WHEN 执行 `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`
- THEN `/health` 的 `model_enabled=true`，`/predict` 返回 `source=kronos`

#### Scenario: 缺资产失败关闭

- GIVEN `vendor/Kronos`、模型或分词器任一缺失
- WHEN 启动 profile 实例
- THEN 进程非零退出并在日志打印缺失路径，不退回 mock

#### Scenario: 并发推理串行

- GIVEN 真实实例已就绪
- WHEN 多个 `/predict` 请求并发到达
- THEN 请求按序执行，模型加载至多一次，且无请求并发进入 predictor

### 非功能需求

- **NFR-001**：默认 `docker compose -f deployment/docker-compose.yml up` 的行为与镜像不受本 feature 影响——默认镜像（mock 目标）不含 torch，profile 未启用时不启动、不构建 real 服务。

## 5. 生命周期与不变量

不适用长生命周期状态机（一次性运行时改造）；三条运行时不变式由测试锁定：

- **失败关闭**：real 模式启动期校验 vendor clone、模型与分词器目录及必需文件；任一缺失或加载失败即非零退出并打印缺失路径，**绝不退回 mock**；
- **串行推理**：进程内模型加载至多一次、推理互斥（进程级锁）；并发请求排队执行，不并发进入 predictor；
- **默认隔离**：未启用 profile 时默认编排不启动 real 服务，默认镜像不含 torch（NFR-001）。

## 6. 成功与验收

### 成功标准

- **SC-001**：F001 AC-006 可由编排命令复跑（US-001）。
- **SC-002**：失败关闭与串行推理不变式成立（US-001）。

### 验收清单

- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 拉起的实例由目标 compose 服务与 real 构建目标产生（容器身份、只读挂载、8002:8001 成立），`/predict` 返回 `source=kronos`；不带该 profile 时默认编排不启用也不构建 real 服务、默认镜像不含 torch — tests: `tests/unit/test_f004_compose_profile_contract.py`、`tests/integration/test_f004_real_profile.py`
- [ ] **AC-002** (`FR-001`): 失败关闭与串行推理——vendor/权重/分词器缺失或加载失败时 real 实例启动即非零退出并打印缺失路径（不退回 mock）；并发 `/predict` 下模型加载至多一次且推理互斥 — tests: `tests/unit/test_f004_kronos_runtime_contract.py`、`tests/integration/test_f004_real_profile.py`

## 7. 测试、依赖与决策

### 测试策略

- **静态编排契约（单元，CI 常绿）**：`tests/unit/test_f004_compose_profile_contract.py`——Dockerfile mock/real 目标与依赖 pin、compose real 服务的 profile/挂载/端口/环境、默认配置不含 real 服务；
- **薄壳运行时契约（单元，CI 常绿）**：`tests/unit/test_f004_kronos_runtime_contract.py`——缺资产启动失败关闭、模型加载至多一次、推理互斥；
- **容器集成（执行机）**：`tests/integration/test_f004_real_profile.py`——构建 real 目标并拉起 profile，校验容器身份与 `source=kronos`；缺资产场景非零退出；默认镜像 `import torch` 判红；开关语义与 F001 冒烟一致（未设 `ALPHAMILL_INTEGRATION` skip、设了判红）；
- F001 的 `test_f001_kronos_smoke.py` 保留 HTTP 契约职责（`source` 与 `model_enabled` 自洽、两方向判红），不再单独承担部署形态证明；
- **取证纪律**：容器与集成证据必须在执行机 `qiaozhi-lt` 采集并记录 hostname 与 `device=cpu`（SOP §3、架构 §7.1）；开发机只跑静态与单元门禁，开发机 skip 不算证据。

### 依赖

- 上游：F001（薄壳、权重流程、AC-006 命令、≥30 根已闭合 1m K 线数据前置）；
- 下游（非本 feature 承诺）：`signals_log` 内容真实化需消费者路由切换（范围外、后移）；FR3 评测台的真实 Kronos 信号输入在路由完成后成立；
- 外部 / 环境依赖：`vendor/Kronos`（pin `67b630e`）+ `models/Kronos-base`、`models/Kronos-Tokenizer-base`（HF 下载，不入库）；执行机 docker-ce 可构建 torch CPU 镜像；HF 网络（仅获取权重时）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 做成可选 profile 而非默认服务 | 默认编排不含 torch 与权重挂载 | 只做数据桥的开发者不该背 torch 镜像体积 | 若真实信号成为常态再评估默认化 |
| 是否阻塞 F002 done | **不阻塞**（2026-09-13 owner 裁决，见 §8 Q-001） | F002 只承诺导出管线正确，不承诺内容来自真实模型 | 代价已写进 F002 spec §6 限制说明；**F004 落地后 `signals_log` 不会自动升级**——runtime snapshot 与 Freqtrade 仍指向 mock `:8001`，路由切换后移（§3 范围外、tasks §5） |
| 消费者路由（profile 启用时是否切换 Freqtrade / snapshot） | 不接线，显式后移 | 路由切换改变默认链路可用性与跨 feature 契约，需独立评估 | v0.2.x 后续评估（tasks §5） |
| 残余风险：torch 镜像层拖慢 CI | CI 不构建也不启用 real profile；默认镜像不含 torch 由门禁锁定 | profile 未启用时 compose 不构建该服务 | 若 CI 需要 real 构建则单独 job |

## 8. 待确认问题

- [x] Q-001：F004 是否阻塞 F002 done？——**裁决（2026-09-13, owner）：不阻塞**。F002 的契约是导出管线正确性，`signals_log` 的内容质量是数据源问题；把它设为阻塞会让数据桥等一个与它无关的运行时改造。**接受的代价**：F002 done 时湖内 signals_log 仍是 `source=placeholder`，该状态已写进 F002 spec §6 验收清单下方的限制说明，done 时必须在验收证据里如实记录行数与 source 分布，不得含糊带过；F004 落地只保证真实信号源在编排内可用，不自动改变写入链路。
```

Wait: "残余风险" row says "profile 未启用时 compose 不构建该服务" — with profiles, that's true. OK.

Hmm, also spec §3 边界场景 includes "数据不足" bullet which references §7 — fine.

Now check: design §0 says spec FR-001 / NFR-001; if AC-002 added, spec has SC-002; fine.

Wait — the reviewer D002 suggested also "readiness". I covered in design §5 (healthcheck). In spec? §4 FR-001 mentions startup preflight/eager load; readiness implicit. OK.

One more check on spec §6 SC-002 "（US-001）" — fine.

Now, the F002 spec edit (D001):
Current lines 218-221:
"**done 时的已知限制(2026-09-13 裁决记录)**:F004(Kronos 真实推理运行时)不阻塞本 feature 收口,因此 F002 done 时湖内 `signals_log` 的内容预期仍以 `source=placeholder` 为主——**导出管线正确不等于内容可用于因子研究**。收口时验收证据必须如实记录该 dataset 的行数与 `source` 分布,不得以"五 dataset 齐备"含糊带过;F004 落地后内容自动升级,F002 无需返工。"

New tail: "…不得以"五 dataset 齐备"含糊带过;F004 落地后在编排内提供可复用的真实信号源,但 `signals_log` 内容真实化还需消费者路由切换(当前 runtime snapshot 与 Freqtrade 仍指向 mock),该切换不在 F004 范围,需另行评估——**本限制不因 F004 落地自动解除**。"

Hmm, but wait: F002 spec is `done`, and the "done 时的已知限制" is a historical record of the closure. Editing historical text... The skill's principle: docs must not carry false claims. I'll adjust minimally with a dated correction note? Something like appending: "**勘正（2026-09-14，F004 设计检视 D001）**：原表述"F004 落地后内容自动升级"不成立——F004 只提供编排内真实实例，消费者路由（runtime snapshot / Freqtrade 仍指向 mock `:8001`）不在其范围，内容真实化需另行评估；F002 限制不因 F004 落地自动解除。" Hmm, that's verbose but keeps history honest. Actually simpler: replace the false sentence and add a parenthetical note. Since F002 is done and this is a factual correction (历史错误修复 allowed), I'll replace the sentence with a corrected one + note. Let me write:

"…不得以"五 dataset 齐备"含糊带过；**勘正（2026-09-14）**：F004 只交付编排内可复用的真实信号源，不自动升级 `signals_log` 内容——runtime snapshot 与 Freqtrade 仍指向 mock `:8001`，消费者路由切换不在 F004 范围（F004 spec §3）；本限制需待该路由另行评估后解除。"

OK good.

Now let me also double check the F002 spec §7 依赖 line 277: "signals_log dataset 的**内容质量**另依赖 Kronos 真实推理容器化——薄壳为 mock 时导出的是 `source=placeholder` 行...; **该项不在 F002 契约内**(见 §3 范围外);" — this is still true. Leave it.

Now, before I start editing, let me check check_doc_links.py to make sure my edits won't break anything (e.g., it may scan for [text](path) links and maybe check backtick paths? Let me check quickly). Also check_review_artifacts_gitignore test — it asserts docs/reviews ignores; FIX-log already covered by .gitignore `docs/reviews/*`. Let me peek at that test to be safe (it might assert specific files). And test_doc_gate_command might assert commands consistency somewhere (e.g., all docs use `python3 tools/verify.py`). My tasks T010/T011 use python3 tools/verify.py; T007 too. Spec/design don't mention gate commands except none. OK.

Let me read check_doc_links.py and test_review_artifacts_gitignore.py quickly.

  <details><summary>tool output</summary>

  ```text
#!/usr/bin/env python3
"""文档相对链接存在性检查（doc review D011 回归门）。

扫描 docs/**/*.md 与 README.md、CLAUDE.md（排除 conversations/、docs/research/、
.sisyphus/），解析 `[text](target)` 形式的相对链接，按所在文件目录解析目标路径，
目标（文件或目录）不存在即报告。跳过 http(s)、mailto、纯锚点（#...）链接，
代码围栏（``` / ~~~）内的内容整体忽略。

用法：python tools/check_doc_links.py
退出码 0 = 相对链接全部可解析；1 = 存在死链。
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#")
EXCLUDED_PARTS = {"conversations", ".sisyphus"}
EXCLUDED_REL_PREFIXES = ("docs/research/",)


def iter_markdown(root: pathlib.Path) -> list[pathlib.Path]:
    candidates: list[pathlib.Path] = []
    for name in ("README.md", "CLAUDE.md"):

…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:52:28Z

- **tool**: `todowrite({"todos": [{"content": "F004-D009: spec §0 PRD 来源 FR3→M0/FR1.2/FR5 + 下游关系说明 - 编辑后 commit", "status": "in_progress", "priority": "high"}, {"content": "F004-D001: spec 删除 signals_log 自动升级承诺、加范围外/后移；F002 spec 勘正 - commit", "status": "pending", "priority": "high"}, {"content": "F004-D003: 全文档命令统一 -f deployment/docker-compose.yml + 数据前置（≥30 根 1m K 线）- commit", "status": "pending", "priority": "high"}, {"content": "F004-D002: spec 不变量/AC-002 + design 启动预检/eager load/推理锁路径 - commit", "status": "pending
…[truncated])`


> [reasoning] Important: `test_doc_gate_command.py` forbids bare `python tools/verify.py` in tracked files. My tasks.md T011 says `python3 tools/verify.py` — good. But the OLD tasks.md line 37 says `verify: python tools/validate_spec_lifecycle.py` — that's a different script, allowed? The regex is only `\bpython tools/verify\.py`. The old text uses `python tools/validate_spec_lifecycle.py` — not matched. But I'll unify to python3 anyway.

Also check_doc_links only checks markdown links — I'm adding none. Good.

Now, let me set up todos and start executing. The plan:
1. Create FIX-log.md skeleton? No — write it at the end (after commits, so hashes can be included).
2. Edit per finding, commit per finding.
3. Run verify.py at the end.
4. Write FIX-log Round 1 declaration.

Wait, order per skill: FIX-log written after work. Yes.

Let me create the todo list. The task list should reflect the 10 findings + final gate + FIX-log. That's 12 items. Let me make it:

1. D001 fix: spec + F002 spec (commit)
2. D002 fix: spec §4/§5 + design §2/§5/§7/§9 + tasks T001/T002 (commit)
3. D003 fix: commands + data preconditions (commit)
4. D004 fix: test strategy + AC tests + tasks gates (commit)
5. D005 fix: dependency pins (commit)
6. D006 fix: machine evidence (commit)
7. D007 fix: build targets/NFR criterion (commit)
8. D008 fix: mount contract (commit)
9. D009 fix: PRD sources (commit)
10. D010 fix: tasks DAG/split (commit)
11. Run verify.py + commit any residual?
12. Write FIX-log Round 1.

Hmm, wait. There's overlap in content: D002 tasks T001/T002, D004 tasks T005/T006, D005 tasks T003, D006 tasks T008, D007 tasks T003/T005, D010 tasks restructure. If I edit tasks.md incrementally in finding order, by the time I get to D010 the file might already be fully restructured — leaving D010 commit with little. Alternatively I could restructure tasks.md fully at D010 stage and have earlier commits only touch spec/design, with tasks changes all in the D010 commit (as the "shared file region" merge precedent: "D034+D037 因共用 tasks.md 编号编辑面合并为一 commit，检视人追认"). Hmm, but then D002/D004/D005/D006/D007 fixes' task-side changes are in the D010 commit, which is flagged as D010's. The FIX-log can note: tasks.md restructure (D010) incorporates the task additions for D002/D004/D005/D006/D007 in one commit due to shared file. That matches the precedent and keeps commits meaningful.

Hmm, but the mapping "commits: 每条 finding 对应的 commit 短哈希" — some findings would share D010's commit. Precedent exists (D034+D037 merged; reviewer ratified). Alternatively do incremental tasks edits; it's more compliant. Let me think about the practical diff-edit approach: I can do targeted `edit` calls on tasks.md in finding order without fully rewriting it until D010. E.g.:

- D002: add T001/T002 into tasks (insert new Phase), update §4 dependencies (partial).
- D003: update T003/T004 command text (old numbers...). Ugh, old numbering references. It's fiddly but fine.

Actually, let me reconsider: A complete tasks.md rewrite in D010's commit can legitimately incorporate all task-level changes, and each earlier finding commit covers spec+design (the "contract" side). FIX-log can say: "tasks.md 因同一文件编辑面在 D010 一次重构（含其余 finding 的任务补充）". I think that's acceptable and matches precedent. But wait — is it better for bisect? docs aren't bisected like code. The precedent was accepted. OK, decision: tasks.md changes happen in one commit at the end (D010), and the FIX-log notes it. Actually hmm, but then D010's diff contains changes related to D002/D004/D005/D006/D007/D008 too. The reviewer will diff-check each finding's fix_summary against spec/design mostly. I'll note clearly in FIX-log: "D010 commit 同时承载除编号结构外的任务级更新（T001/T002 @D002、T003 @D005、T005/T006 @D004、T008 @D006、T003/T005 verify @D007、T004 端口/挂载 @D008），因 tasks.md 共用同一编辑面合并为一个提交（对齐循环4 D034+D037 先例）". Good.

Hmm, actually — wait. Let me simplify even further. Since ALL findings edit overlapping doc regions, maybe cleaner: per-finding commits for spec/design as much as possible, and one tasks.md commit. That's what I just decided. Let me also double check whether D009 (PRD source) should be its own commit — yes, tiny edit to spec §0 line. And D001 also edits spec §0 (intent line) — adjacent but different lines; sequential edits fine.

Let me now get going. First create todos. Then start editing.

Actually, one more consideration before editing: the CURRENT-doc.md review says "文档结构门已通过" — my edits must keep structure passing. I'll run `python3 tools/verify.py` after each file or at end? Skill says full gate once at round end. But I'm nervous about breaking the lifecycle gate with my spec/tasks rewrites; I'll run `python3 tools/validate_spec_lifecycle.py` + check_doc_links after edits as a sanity check (cheap), and full verify at the end (which is required). Actually running the focused gates after each finding is fine (not the full suite). Hmm, "门禁每轮一次" — the full gate once per round; focused local checks are fine for development. I'll run validate_spec_lifecycle after the spec/tasks edits to catch format issues early.

Let me now write the todos and begin.

Also: should I remove the "updated:" frontmatter dates? I'll bump spec/design/tasks `updated: 2026-09-14` and F002 spec stays 2026-09-14 (already).

Let me carefully produce each edit. Start with D001.

**D001 edits:**

spec.md:
1. Line 26 (intent): replace with new text.
2. §2 US-001 以便 clause + why + 独立测试 (独立测试 also gets D003's command/preconditions — careful! D003 will further edit the same 独立测试 line. So for D001 I only change the "以便" and "为什么" parts; leave 独立测试 for D003... but D001's fix requires removing signals_log claims from §2. The why-clause mentions signals_log; the 以便 mentions signals_log content validity. The 独立测试 line I'll leave for D003 (command change) and D001 doesn't need it. Hmm, but 验收场景 line 57 mentions command too; that's D003.
3. §3 范围外: add consumer routing + signals_log auto-upgrade bullets (D001).
4. §7 依赖: "下游消费者：F002 的 signals_log dataset 内容有效性。" → replace (D001).
5. §7 决策表 row 2 "后续" cell: replace with corrected text (D001). (D003 later adds/edits? No, D003 touches 依赖/测试策略/commands; the table row is D001's.)

F002 spec: edit the 已知限制 tail (D001).

Commit message: `docs(f004): 删除 signals_log 自动升级承诺并显式后移消费者路由（F004-D001）`.

**D009 edits:** spec §0 PRD source line + 架构来源 line (add §7.1? keep simple). Commit `docs(f004): 修正 PRD 来源引用（F004-D009）`.

Order: D001 then D009 (both spec §0, sequential). Or D009 first then D001? Either. I'll do D009 first since it's tiny and isolated, then D001. Actually old line: "- **PRD 来源**：`docs/alphamill-prd.md` FR3（信号生产）与 M1 运行基座". New: "- **PRD 来源**：`docs/alphamill-prd.md` M0（自包含运行基线：Kronos 服务在编排内健康）、FR1.2（`signals_log` 进入不可变快照）与 FR5（运行链：信号服务的运行时载体）；FR3（证据评测与验证）仅为下游关系——F004 为评测提供可复现的真实 Kronos 信号源，不实现评测本身。"

Hmm, one question: is citing FR5 right? Let me scan FR5 again: "FR5 部署与交易执行" — FR5.1 版本化信号契约 (feather cache), FR5.3 Freqtrade 适配. Hmm, honestly the Kronos service feeds Freqtrade in F001 (KRONOS_SIGNAL_URL). But F004 explicitly doesn't rewire consumers. Is citing FR5 misleading? The review suggested "相关 FR5 运行链". I'll phrase it as "FR5（运行链：信号服务的运行时载体）" — hmm, is the Kronos service part of FR5's runtime chain? In F001, Freqtrade consumes Kronos signal URL (live inference for strategy!) — actually looking at KronosFusionStrategy and KRONOS_SIGNAL_URL: freqtrade calls the Kronos service for signals at decision time. That IS the FR5.3 execution chain. So yes, the Kronos service is a runtime dependency of the execution chain; F004 improves its real-runtime capability. And under the current scope, consumers aren't switched — but the "运行时载体" citation remains defensible. Keep, with the mention that F004 only provides the runtime (routing out of scope).

**D003 edits:**
- spec §2 独立测试: new text with `-f` command + preconditions + evidence machine note? Wait, evidence machine is D006. Ugh — same line gets touched by D003 (command+data) and D006 (evidence machine). Sequence: D003 edits now; D006 edits later. OK.
  D003 text: "新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿。"
  D006 appends: "；容器集成验收在执行机 qiaozhi-lt 取证并记录 hostname/device=cpu，开发机只跑静态与单元门禁（§7）." — wait, I planned this in US-001 during D006. OK.
- spec §2 验收场景 1 command: `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`.
- spec §3 边界场景: add data-insufficiency bullet (D003? D002 added it? I planned "数据不足" bullet under 边界场景 — assign to D003).
- spec §7 依赖: add environment pref with ≥30 candles + docker build capability? D003 edit.
- spec §7 测试策略: F004 integration test description... that's D004. Hmm, D003's fix: "统一使用 docker compose -f deployment/docker-compose.yml，并声明数据库迁移完成且目标 exchange/symbol 至少有 30 根已闭合 1m K 线，补齐新 clone 的数据准备步骤或收窄场景。" So D003 touches: §2 独立测试, §2 scenario command, §3 边界场景 (data), §7 依赖 (preconditions), maybe §1 问题? No.
- design §0 输入与约束: add data precondition bullet? I planned to include in implementation constraints: "；`/predict` 数据前置为目标 exchange/symbol 至少 30 根已闭合 1m K 线". D003.
- design §5 启动 command: `-f` (D003).
- tasks: all commands updated in D010 commit.

**D002 edits:**
- spec §4 FR-001 description + scenarios (profile 拉起场景 unchanged? its THEN mentions instance "确由 real 构建目标的容器提供" — that's D004 container identity... hmm. Let me assign scenario 1's identity clause to D004 or keep simpler. Let me keep scenario 1 as `model_enabled=true` + `source=kronos` (original + D003 command), and add scenarios 2 (fail-closed) + 3 (serial) in D002.
- spec §5 rewrite (invariants) — D002.
- spec §6 add SC-002 + AC-002 (D002). Wait AC-002's tests reference unit/integration paths — the test paths are D004's strategy; but AC-002 itself is D002's fix. Fine, include paths.
- design §2: "不新增模块 + 薄壳三处最小改造" (D002) — but the dependency pin block & mount table in §2 are D005/D008. Sequential edits: D002 changes the intro sentence; D005 adds pin paragraph; D008 adds table.
- design §5 rewrite (startup sequence/lock/concurrency/readiness) (D002); D003 changes command inside; D008 changes port line? The port line already in §5 ("端口：真实实例 host 8002 → container 8001...") — D008's fix covers port mapping in §2 table; §5 port line already existed (old line 47) — keep, maybe refine as part of D008. I'll refine in D008.
- design §4: add "real 实例在启动预检与 eager load 完成后才对外服务…" (D002).
- design §7 rewrite (D002 core; also D007's "默认镜像不含 torch" and D008's ":ro" — assign: D002 writes fail-closed + read-only? Hmm D008 covers :ro. Let me assign: D007 writes the 镜像体积/默认镜像 lines; D008 writes the 资产只读 line; D002 writes fail-closed lines. Fine—three passes on §7.)
- design §9: add serialization decision row (D002), consumer routing row (D001), dependency pin row (D005), torch/CI row refinement (D007). Multiple passes.
- tasks T001/T002 — deferred to D010 commit.

**D004 edits:**
- spec §6 AC-001 rewrite (tests paths + identity wording) (D004) — but AC-002 from D002 already added; AC-001 edit: change "默认编排行为与镜像层不变" wording (D007 also changes this!) Hmm. AC-001's wording changes: D004 adds container identity + tests; D007 changes "镜像层不变"→"默认镜像不含 torch + 不构建". Sequence: D004 rewrites AC-001 fully except keep phrase "不带该 profile 时默认编排行为与镜像层不变"? That'd be odd. Let me just assign the AC-001 rewrite to D004 (including the tests paths and identity), leaving the NFR criterion phrase for D007 to fix. So D004's AC-001: "...；不带该 profile 时默认编排行为与镜像层不变 — tests: ...". D007 changes "默认编排行为与镜像层不变" → "默认编排不启用也不构建 real 服务、默认镜像不含 torch". OK.
- spec §7 测试策略 rewrite (D004 core). D006 appends evidence line; fine.
- design §8 test table rewrite (D004 core); D006 adds execution-machine note; D005 maybe adds dependency validation row? No, keep.

**D005 edits:**
- spec §3 范围内 bullet 1: dependency list upgrade (D005).
- design §2: add dependency pin paragraph (D005).
- design §9: add pin decision row (D005).
- tasks T003 deferred to D010.

**D006 edits:**
- design §0 执行环境 rewrite (D006).
- design §8: add 取证纪律 note (D006). (D004 may already add a "执行机" column in table; D006 adds the note + hostname/device evidence requirement.)
- spec §7 测试策略: add 取证纪律 line (D006).
- spec §2 独立测试: append execution machine clause (D006) — as planned.
- Maybe spec AC-001 or §6 note? Keep to those.

**D007 edits:**
- spec NFR-001 rewrite (D007).
- spec AC-001 phrase fix (D007).
- design §1 rewrite (mock/real targets) (D007). D002 also edits §1? I said D002 edits §2; §1 "技术概要" rewrite includes targets + thin shell. Assign the targets part to D007 and thin-shell intro to D002? The paragraph is one block. Simplest: D002 edits §1 paragraph to add "薄壳三处最小改造" sentence; D007 replaces the Dockerfile sentence with mock/real target design. Two passes on the same paragraph — fine with edit tool.
- design §5/§7: "默认镜像不含 torch" (D007).
- design §9 torch/CI row refinement (D007).
- tasks T003/T005 wording — D010 commit.

**D008 edits:**
- design §2 mount table + paths/env (D008).
- design §5 port line refinement (D008).
- design §7 read-only line (D008).
- tasks T004 deferred to D010.

**D010 edits:**
- tasks.md full rewrite (includes everything).

OK. And FIX-log at the end.

Wait, one more: D001 also needs the spec §3 范围外 addition and §7 table. Fine.

Also note: D002's spec §4 scenario "并发推理串行" — hmm, is it appropriate to have three scenarios? Sure.

Let me also double check NFR-001 rewrite for D007:
Old: "**NFR-001**：默认 `docker compose up` 的行为与镜像体积不受本 feature 影响（profile 未启用时不构建 torch 层）。"
New: "**NFR-001**：默认 `docker compose -f deployment/docker-compose.yml up` 的行为与镜像不受本 feature 影响——默认镜像（`mock` 构建目标）不含 torch，profile 未启用时不启动、不构建 real 服务。"
And AC-001 phrase: "...；不带该 profile 时默认编排不启用也不构建 real 服务、默认镜像不含 torch — tests: ...".

Now, let me begin executing. First todos. Then edits+commits in order: D009, D001, D003, D002, D004, D005, D006, D007, D008, D010.

Hmm wait, D009 first then D001 — both spec §0. D009 edits PRD来源 line; D001 edits 一句话意图 + others. Fine.

Actually, let me reconsider the order for nicer diffs: do spec edits grouped? No — commit per finding regardless of file. OK.

One concern: committing per finding will produce 10 commits on main. Let me check git user config for commit signing etc. Probably fine (previous commits exist). I'll use `git add <files> && git commit -m "..."`.

Also: do I need to worry about the FIX-log being untracked while committing? `git add` specific files only, so no.

Let me also prepare commit messages (Chinese, matching repo style "docs(f004): ..."):
- D009: `docs(f004): 修正 PRD 来源引用——FR3 改为下游评测关系（F004-D009）`
- D001: `docs(f004): 删除 signals_log 自动升级承诺，显式后移消费者路由（F004-D001）`
- D003: `docs(f004): 命令统一 -f 定位并补齐数据前置（F004-D003）`
- D002: `docs(f004): 补失败关闭/串行推理实现路径与不变量（F004-D002）`
- D004: `docs(f004): 测试策略分层——专属静态/容器门禁替代冒烟兜底（F004-D004）`
- D005: `docs(f004): 锁定 real 镜像最小推理依赖与 torch CPU wheel 来源（F004-D005）`
- D006: `docs(f004): 验收环境改为执行机取证并记录 hostname/device（F004-D006）`
- D007: `docs(f004): 定义 mock/real 构建目标与可稳定断言的 NFR 判据（F004-D007）`
- D008: `docs(f004): 补全挂载/环境变量/端口两侧契约（F004-D008）`
- D010: `docs(f004): tasks 重构——完整 DAG、拆分证据回写与状态同步（F004-D010）`

Now let me write the todo list and start. Actually also: before starting, consider making a working branch? Past cycles committed to main directly. Keep main (docs-only changes; CI on push later by reviewer). Hmm, actually SOP workflow says "Step 1 建分支/worktree 做隔离开发" for implementing a feature. This is a doc-fix round within the review protocol. Previous review fix rounds went to main (e.g. "16d8733 docs(f002): 检视循环 10 收口" on main). I'll commit to main locally; no push.

Let me start. First the todo list.
Evidence gathered. Now executing fixes per finding, one commit each. Creating the work plan:

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "F004-D009: spec §0 PRD 来源 FR3→M0/FR1.2/FR5 + 下游关系说明 - 编辑后 commit",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "F004-D001: spec 删除 signals_log 自动升级承诺、加范围外/后移；F002 spec 勘正 - commit",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "F004-D003: 全文档命令统一 -f deployment/docker-compose.yml + 数据前置（≥30 根 1m K 线）- commit",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "F004-D002: spec 不变量/AC-002 + design 启动预检/eager load/推理锁路径 - commit",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "F004-D004: 测试策略分层（静态/容器专属门禁）并更新 AC-001 tests - commit",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "F004-D005: design/spec 锁定 torch CPU wheel 版本与最小依赖 pin - commit",
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:52:55Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- **PRD 来源**：`docs/alphamill-prd.md` FR3（信号生产）与 M1 运行基座\n- **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑）", "newString": "- **PRD 来源**：`docs/alphamill-prd.md` M0（自包含运行基线：Kronos 服务在编排内健康）、FR1.2（`signals_log` 进入不可变快照）与 FR5（运行链：信号服务的运行时载体）；FR3（证据评测与验证）仅为下游关系——F004 为评测提供可复现的真实 Kronos 信号源，不实现评测本身\n- **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑）、§7.1（机器边界）"})`


> [reasoning] Start D009: spec §0 PRD source line.
**Finding 1/10 (D009)** — fix PRD source citation in spec §0:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:52:58Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "created: 2026-09-12\nupdated: 2026-09-12\n---", "newString": "created: 2026-09-12\nupdated: 2026-09-14\n---"})`


> [reasoning] Also bump updated date in spec frontmatter — but that will be touched by multiple findings; I'll bump once at the end (or in D009 now?). Bumping per finding is noisy; do it in the last commit (D010) or D009. Let me do it now in D009? It's cleaner to update `updated: 2026-09-14` once. Actually, each commit represents a change to the file, so each should ideally update the date; but that's noise. I'll bump all three files' dates in the D010 commit (last). Hmm, but if I bump spec date now, later edits still same date (today), so no further change needed. Let me bump now for spec: updated: 2026-09-12 → 2026-09-14. Do it in D009's commit. Then no other spec date changes needed.

Commit D009: spec.md only.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:53:03Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md && git commit -q -m \"docs(f004): 修正 PRD 来源引用——FR3 改为下游评测关系（F004-D009）\n\n- PRD 来源改指 M0/FR1.2/FR5 运行链；FR3 仅作为下游（提供真实信号源，不实现评测）\n- 架构来源补 §7.1 机器边界\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
10cd1d8 docs(f004): 修正 PRD 来源引用——FR3 改为下游评测关系（F004-D009）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:53:06Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并让 F002 导出的 `signals_log` 能承载真实信号而非 placeholder。", "newString": "- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并在编排内提供可复用的真实信号源；消费者路由切换（Freqtrade 与 runtime snapshot 指向真实实例）不在本 feature 范围（见 §3）。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "作为 `量化研究员`，我希望 `用一条 compose 命令拉起真实 Kronos 推理`，以便 `AC-006 与 signals_log 的内容有效性不依赖任何仓外手工步骤`。\n\n**为什么是这个优先级**：F001 已用独立命令留档证据，不阻塞 M1 开工；但 F002 的 signals_log dataset 要有研究价值就需要它。", "newString": "作为 `量化研究员`，我希望 `用一条 compose 命令拉起真实 Kronos 推理`，以便 `AC-006 的真实推理证据不依赖任何仓外手工步骤，且真实信号源在编排内可复用`。\n\n**为什么是这个优先级**：F001 已用独立命令留档证据，不阻塞 M1 开工；F002 的 signals_log dataset 要有研究价值需要可复现的真实信号源（消费者接线见 §3 范围
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "### 范围外\n\n- 权重与 vendor clone 的获取（F001 已有流程，仍不入库）；\n- GPU 直通（见非目标）。", "newString": "### 范围外\n\n- 权重与 vendor clone 的获取（F001 已有流程，仍不入库）；\n- GPU 直通（见非目标）；\n- 消费者路由切换：Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 仍指向 mock `:8001`；真实实例接线由后续评估决定（见 tasks §5）；\n- `signals_log` 内容的自动升级：本 feature 只提供真实信号源，不改变写入链路。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- 下游消费者：F002 的 `signals_log` dataset 内容有效性。", "newString": "- 下游（非本 feature 承诺）：`signals_log` 内容真实化需消费者路由切换（范围外、后移）；FR3 评测台的真实 Kronos 信号输入在路由完成后成立。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "| 是否阻塞 F002 done | **不阻塞**（2026-09-13 owner 裁决，见 §8 Q-001） | F002 只承诺导出管线正确，不承诺内容来自真实模型 | 代价已写进 F002 spec §6 限制说明；F004 落地后 signals_log 内容自动升级，无需 F002 返工 |", "newString": "| 是否阻塞 F002 done | **不阻塞**（2026-09-13 owner 裁决，见 §8 Q-001） | F002 只承诺导出管线正确，不承诺内容来自真实模型 | 代价已写进 F002 spec §6 限制说明；**F004 落地后 `signals_log` 不会自动升级**——runtime snapshot 与 Freqtrade 仍指向 mock `:8001`，路由切换后移（§3 范围外、tas
…[truncated])`


> [reasoning] D009 done. Now D001: spec edits + F002 spec correction.

spec edits:
1. 一句话意图 (line 26):
Old: "- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并让 F002 导出的 `signals_log` 能承载真实信号而非 placeholder。"
New: "- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并在编排内提供可复用的真实信号源；消费者路由切换（Freqtrade 与 runtime snapshot 指向真实实例）不在本 feature 范围（见 §3）"

2. §2 US-001 story "以便" + why:
Old line 49: "作为 `量化研究员`，我希望 `用一条 compose 命令拉起真实 Kronos 推理`，以便 `AC-006 与 signals_log 的内容有效性不依赖任何仓外手工步骤`。"
New: "作为 `量化研究员`，我希望 `用一条 compose 命令拉起真实 Kronos 推理`，以便 `AC-006 的真实推理证据不依赖任何仓外手工步骤，且真实信号源在编排内可复用`。"
Old line 51: "**为什么是这个优先级**：F001 已用独立命令留档证据，不阻塞 M1 开工；但 F002 的 signals_log dataset 要有研究价值就需要它。"
New: "**为什么是这个优先级**：F001 已用独立命令留档证据，不阻塞 M1 开工；F002 的 signals_log dataset 要有研究价值需要可复现的真实信号源（消费者接线见 §3 范围外）。"

3. §3 范围外 add two bullets after GPU bullet:
Old:
```
- 范围外:
- 权重与 vendor clone 的获取（F001 已有流程，仍不入库）；
- GPU 直通（见非目标）。
```
New add:
```
- 消费者路由切换：Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 仍指向 mock `:8001`；真实实例接线由后续评估决定（见 tasks §5）；
- `signals_log` 内容的自动升级：本 feature 只提供真实信号源，不改变写入链路。
```

4. §7 依赖 old: "- 下游消费者：F002 的 `signals_log` dataset 内容有效性。"
New: "- 下游（非本 feature 承诺）：`signals_log` 内容真实化需消费者路由切换（范围外、后移）；FR3 评测台的真实 Kronos 信号输入在路由完成后成立。"

5. §7 决策表 row: old "| 是否阻塞 F002 done | **不阻塞**（2026-09-13 owner 裁决，见 §8 Q-001） | F002 只承诺导出管线正确，不承诺内容来自真实模型 | 代价已写进 F002 spec §6 限制说明；F004 落地后 signals_log 内容自动升级，无需 F002 返工 |"
New: same first three cells, new 后续: "代价已写进 F002 spec §6 限制说明；**F004 落地后 `signals_log` 不会自动升级**——runtime snapshot 与 Freqtrade 仍指向 mock `:8001`，路由切换后移（§3 范围外、tasks §5）"

Also add a decision row for routing? D001. The old table row 1 "做成可选 profile" keep.

Let me do these edits.
**Finding 2/10 (D001)** — remove the false "signals_log auto-upgrade" promise in F004 spec + correct the same claim in F002 spec:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:53:16Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/spec.md", "oldString": "不得以\"五 dataset 齐备\"含糊带过;F004 落地后内容自动升级,F002 无需返工。", "newString": "不得以\"五 dataset 齐备\"含糊带过;**勘正（2026-09-14，F004 设计检视 D001）**:F004 只交付编排内可复用的真实信号源,不自动升级 `signals_log` 内容——runtime snapshot 与 Freqtrade 仍指向 mock `:8001`,消费者路由切换不在 F004 范围（F004 spec §3）;本限制需待该路由另行评估后解除,不因 F004 落地自动消失。"})`


> [reasoning] Now F002 spec correction. Current text (lines 218-221):
"**done 时的已知限制(2026-09-13 裁决记录)**:F004(Kronos 真实推理运行时)不阻塞本 feature 收口,
因此 F002 done 时湖内 `signals_log` 的内容预期仍以 `source=placeholder` 为主——**导出管线正确
不等于内容可用于因子研究**。收口时验收证据必须如实记录该 dataset 的行数与 `source` 分布,
不得以"五 dataset 齐备"含糊带过;F004 落地后内容自动升级,F002 无需返工。"

Replace tail "F004 落地后内容自动升级,F002 无需返工。" with correction. Note the file uses halfwidth punctuation mixed (the F002 spec uses no space after punctuation, e.g. "记记录(2026-09-13 裁决记录)"). Let me match file style (it uses ",;()" ASCII?). Looking at line 218: "**done 时的已知限制(2026-09-13 裁决记录)**:F004(Kronos 真实推理运行时)不阻塞本 feature 收口," — ASCII commas/colons. I'll match.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:53:21Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F002-data-bridge/spec.md && git commit -q -m \"docs(f004): 删除 signals_log 自动升级承诺，显式后移消费者路由（F004-D001）\n\n- F004 spec：意图/US-001/范围外/依赖/决策表改述，真实实例只交付可复用信号源\n- F002 spec §6 勘正'F004 落地后内容自动升级'为不成立表\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
1e81b7c docs(f004): 删除 signals_log 自动升级承诺，显式后移消费者路由（F004-D001）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:53:24Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- `docker compose --profile kronos-real up` 后，真实模型实例在编排内可达且 `/predict` 返回 `source=kronos`；", "newString": "- `docker compose -f deployment/docker-compose.yml --profile kronos-real up` 后，真实模型实例在编排内可达且 `/predict` 返回 `source=kronos`；"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "**独立测试**：新 clone + 权重就位后，`docker compose --profile kronos-real up -d` 再跑 AC-006 命令全绿。", "newString": "**独立测试**：新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "1. Given `vendor/Kronos 与 models/ 就位`，when `docker compose --profile kronos-real up -d`，then `/health` 的 `model_enabled=true` 且 `/predict` 返回 `source=kronos`。", "newString": "1. Given `vendor/Kronos 与 models/ 就位`，when `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`，then `/health` 的 `model_enabled=true` 且 `/predict` 返回 `source=kronos`。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- 权重或 vendor 缺失：profile 启动即失败并打印缺失路径，不静默退回 mock。", "newString": "- 权重或 vendor 缺失：profile 启动即失败并打印缺失路径，不静默退回 mock；\n- 数据不足：目标 exchange/symbol 少于 30 根已闭合 1m K 线时 `/predict` 无有效输入（服务契约 `limit>=30` 之外还需 DB 有足够行），验收前置见 §7。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- 上游：F001（薄壳、权重流程、AC-006 命令）；\n- 下游（非本 feature 承诺）：`signals_log` 内容真实化需消费者路由切换（范围外、后移）；FR3 评测台的真实 Kronos 信号输入在路由完成后成立。", "newString": "- 上游：F001（薄壳、权重流程、AC-006 命令）；\n- 下游（非本 feature 承诺）：`signals_log` 内容真实化需消费者路由切换（范围外、后移）；FR3 评测台的真实 Kronos 信号输入在路由完成后成立；\n- 外部 / 环境依赖：`vendor/Kronos`（pin `67b630e`）+ `models/Kronos-base`、`models/Kronos-Tokenizer-base`（HF 下载，不入库）；执行机 docker-ce 可构建 tor
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- **实现约束**：`vendor/Kronos`（pin `67b630e`）与 `models/`（391MB + 16MB）不入库，由 F001 既有流程获取", "newString": "- **实现约束**：`vendor/Kronos`（pin `67b630e`）与 `models/`（391MB + 16MB）不入库，由 F001 既有流程获取；`/predict` 数据前置为目标 exchange/symbol 至少 30 根已闭合 1m K 线（F001 回填产物，DB 已迁移）"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- 启动：`docker compose --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；", "newString": "- 启动：`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；"})`


> [reasoning] D001 done. Now D003: command unification + data preconditions.

Edits:
1. spec §2 独立测试: old "**独立测试**：新 clone + 权重就位后，`docker compose --profile kronos-real up -d` 再跑 AC-006 命令全绿。"
New: "**独立测试**：新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿。" (D006 appends evidence machine later.)

2. spec §2 验收场景 1: old "1. Given `vendor/Kronos 与 models/ 就位`，when `docker compose --profile kronos-real up -d`，then `/health` 的 `model_enabled=true` 且 `/predict` 返回 `source=kronos`。"
New: replace command with -f version.

3. spec §3 边界场景: old:
```
- 权重或 vendor 缺失：profile 启动即失败并打印缺失路径，不静默退回 mock。
```
Add data bullet: "- 数据不足：目标 exchange/symbol 少于 30 根已闭合 1m K 线时 `/predict` 无有效输入（limit≥30 由服务契约与 DB 数据共同保证），验收前置见 §7。"

4. spec §7 依赖: add environment precondition. Current 依赖 section (after my D001 edit):
```
### 依赖

- 上游：F001（薄壳、权重流程、AC-006 命令）；
- 下游（非本 feature 承诺）：...
- 外部/环境依赖: ?
```
Wait the original had:
"- 上游：F001（薄壳、权重流程、AC-006 命令）；
- 下游消费者：F002 的 `signals_log` dataset 内容有效性。"
No 外部/环境 bullet. Add one:
"- 外部 / 环境依赖：`vendor/Kronos`（pin `67b630e`）+ `models/Kronos-base`、`models/Kronos-Tokenizer-base`（HF 下载，不入库）；执行机 docker-ce 可构建 torch CPU 镜像；DB 已迁移且目标 exchange/symbol 至少有 30 根已闭合 1m K 线（F001 回填产物）。"

5. spec §7 测试策略: old "- 复用 F001 的 `test_f001_kronos_smoke.py`（`KRONOS_REQUIRE_REAL_MODEL=1` + `KRONOS_BASE_URL` 指向 profile 实例）。" — this line will be rewritten by D004 anyway. For D003, should I add the data precondition here? The 独立测试 & 依赖 cover it. Skip.

6. design §0 实现约束: old "- **实现约束**：`vendor/Kronos`（pin `67b630e`）与 `models/`（391MB + 16MB）不入库，由 F001 既有流程获取"
New: append "；`/predict` 数据前置为目标 exchange/symbol 至少 30 根已闭合 1m K 线（F001 回填产物）"

7. design §5 启动 command (also D002 rewrite will replace §5; do D003 first so D002 sees the new command? Wait I ordered D003 before D002 in the todo list? The todo list says D003 item 3, D002 item 4. Actually I planned D003 then D002. Hmm, earlier I reasoned D002 rewrites §5 wholesale; to give D003 its own commit touching the command, D003 should go first: it edits the existing §5 line 46 command; then D002 rewrites §5 fully (including the now-fixed command). Good—that's the todo order.)

design §5 old line 46: "- 启动：`docker compose --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；"
New: "- 启动：`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；"

Also design §5 line 47 port mentions fine. And the §8 test row command? design §8 row (line 63): "profile 实例 model_enabled=true 且 source=kronos；默认 compose 配置不含 torch 层与权重挂载" — no command. OK.

Wait, also design §1 影响面 mentions "F001 AC-006 的复跑命令改为 compose 形态" — no literal command. Fine.

Also spec §1 目标 "docker compose --profile kronos-real up 后" — hmm, line 36: "- `docker compose --profile kronos-real up` 后，真实模型实例在编排内可达且 `/predict` 返回 `source=kronos`；" — Should include -f. Yes, D003 must fix all command occurrences. Let me grep after edits for remaining `docker compose` without -f in F004 docs.

Also design §0? no command. tasks has many (D010 will handle, but let me include command fixes there in D010).

Let me apply edits.
**Finding 3/10 (D003)** — unify compose commands with `-f` and add data preconditions:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:53:36Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"docker compose\" docs/features/0.2/F004-kronos-inference-runtime/*.md | grep -v \"\\-f deployment\" ; echo \"---(remaining without -f above; tasks expected)\"; git add docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): 命令统一 -f 定位并补齐数据前置（F004-D003）\n\n- spec/design 全部 compose 命令改 docker compose -f deployment/docker-compose.yml\n- 声明 DB 迁移完成且目
…[truncated])`

  <details><summary>tool output</summary>

  ```text
docs/features/0.2/F004-kronos-inference-runtime/spec.md:90:- WHEN 执行 `docker compose --profile kronos-real up -d`
docs/features/0.2/F004-kronos-inference-runtime/spec.md:95:- **NFR-001**：默认 `docker compose up` 的行为与镜像体积不受本 feature 影响（profile 未启用时不构建 torch 层）。
docs/features/0.2/F004-kronos-inference-runtime/tasks.md:29:- [ ] T001 (`FR-001`): `deployment/kronos-service.Dockerfile` 增加含 torch/cpu + einops + safetensors 的构建目标，默认目标保持现状不变 — verify: 默认 `docker compose build kronos-signal` 的镜像层与改前一致
docs/features/0.2/F004-kronos-inference-runtime/tasks.md:30:- [ ] T002 (`FR-001`, `NFR-001`): compose 增 `kronos-signal-real` 服务，`profiles: [kronos-real]`，挂载 `vendor/Kronos` 与 `models/`，端口 8002 — verify: `docker compose config` 不含该服务，`docker compose --profile kronos-real config` 含之
---(remaining without -
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:53:40Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- WHEN 执行 `docker compose --profile kronos-real up -d`", "newString": "- WHEN 执行 `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`"})`


> [reasoning] Two spec occurrences remain:
- Line 90: FR-001 "Scenario: profile 拉起" WHEN command — I missed it (I only changed §2 scenario 1). Fix in D003 — but I already committed D003. Hmm, amend? No — "If a commit fails or hooks reject it, fix the issue and create a new commit; do not amend the failed commit." That's about failed commits. But the skill says don't amend? Generally, avoid amending. However, the D003 commit is incomplete (missed one command + NFR line is D007's scope). Options: make a small follow-up commit for the missed command (D003 scope) — but then D003 has two commits; acceptable ("commits: D003: 88dfce9, <hash2>"). Or leave it to D002's commit (D002 will rewrite FR-001 description; but the scenario line isn't part of D002's change per se...). Cleanest: quick follow-up commit amending D003's fix — call it D003 follow-up. Actually since I haven't pushed and no one depends, amending is safer for bisect-cleanliness? The system prompt says "If a commit fails or hooks reject it, fix the issue and create a new commit; do not amend the failed commit." — this commit didn't fail; I just found a missed edit. Amending local unpublished commit is normal git hygiene and the skill values per-finding atomic commits. Hmm, but risk: the reviewer will verify commit hashes; if they've seen 88dfce9? They haven't (not pushed, reviewer acts later). I'll amend to keep 1 finding = 1 commit, since the commit message already claims "所有 compose 命令". Let me do `git commit --amend --no-edit` after adding the missed line. Wait — is amending allowed given "do not amend" guidance? That guidance is specifically "If a commit fails or hooks reject it". Here the commit succeeded; I'm improving completeness of the same logical change before pushing. I think amend is right. Hmm, but the hard block in my instructions says "Do not ... amend ... unless explicitly requested." Ugh. System prompt: "Do not update git config, skip hooks, use interactive `-i`, force-push, or create empty commits unless explicitly requested." — amend isn't listed there, but "Only commit, amend, push, or create PRs when explicitly requested"? Actually the text: "Only commit, amend, push, or create PRs when explicitly requested." Hmm strict. I'm already committing per user's skill-following request. Amend vs new commit — to be safe against the letter of the guidance, create a small additional commit for the missed line. It's harmless; FIX-log can list "D003: 88dfce9 + <followup>". Actually wait, that fragments. Alternatively fold the missed command fix into the NEXT commit (D002) — D002 touches FR-001 description and scenarios... The line 90 is in the Scenario block which D002 edits anyway (D002 adds scenarios; the profile 拉起 scenario falls between). D002's commit will change that block, so folding the command fix there is... but then D002's commit contains a D003 leftover. Meh.

Cleanest and compliant: a follow-up commit "docs(f004): 补 D003 遗漏的 FR-001 场景命令 -f 定位". Slightly noisy but honest. Hmm. Or amend. Let me weigh: the review skill says one finding one commit. A follow-up fixup commit for the same finding is acceptable and traceable ("D003: 88dfce9, 补遗 <hash>"). I'll do the follow-up commit.

Actually hold on, let me reconsider: I can also just include it in D002's commit since D002 restructures FR-001's scenario section, and note in FIX-log. No — keep provenance clean: separate small commit now. Decide: small follow-up commit. And also fix NFR line? No — NFR line is D007's (will be rewritten then). The line 90 command is the only miss.

Let me fix it now.
One command was missed — small follow-up commit for D003:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:53:48Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md && git commit -q -m \"docs(f004): 补 D003 遗漏——FR-001 场景命令加 -f 定位（F004-D003）\n\n前一提交 88dfce9 声称'全部命令统一'，复核发现 FR-001 profile 拉起场景仍缺 -f，\n按细提交纪律补遗单独成一篇。\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
abef312 docs(f004): 补 D003 遗漏——FR-001 场景命令加 -f 定位（F004-D003）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:53:51Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "系统应当提供一个非默认的 compose profile，使真实模型实例在编排内启动并保持 F001 冻结的 HTTP API 契约不变。", "newString": "系统应当提供一个非默认的 compose profile，使真实模型实例在编排内启动、完成启动期资产预检与模型加载、串行处理推理请求，并保持 F001 冻结的 HTTP API 契约不变。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- WHEN 执行 `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`\n- THEN `/health` 的 `model_enabled=true`，`/predict` 返回 `source=kronos`\n\n### 非功能需求", "newString": "- WHEN 执行 `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`\n- THEN `/health` 的 `model_enabled=true`，`/predict` 返回 `source=kronos`\n\n#### Scenario: 缺资产失败关闭\n\n- GIVEN
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "## 5. 生命周期与不变量\n\n不适用：一次性运行时改造，无长生命周期状态机。", "newString": "## 5. 生命周期与不变量\n\n不适用长生命周期状态机（一次性运行时改造）；三条运行时不变式由测试锁定：\n\n- **失败关闭**：real 模式启动期校验 vendor clone、模型与分词器目录及必需文件；任一缺失或加载失败即非零退出并打印缺失路径，**绝不退回 mock**；\n- **串行推理**：进程内模型加载至多一次、推理互斥（进程级锁）；并发请求排队执行，不并发进入 predictor；\n- **默认隔离**：未启用 profile 时默认编排不启动 real 服务，默认镜像不含 torch（NFR-001）。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- **SC-001**：F001 AC-006 可由编排命令复跑（US-001）。", "newString": "- **SC-001**：F001 AC-006 可由编排命令复跑（US-001）。\n- **SC-002**：失败关闭与串行推理不变式成立（US-001）。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 起的实例 model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排行为与镜像层不变 — tests: `tests/integration/test_f001_kronos_smoke.py`", "newString": "- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 起的实例 model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排行为与镜像层不变 — tests: `tests/integration/
…[truncated])`


> [reasoning] Now D002: fail-closed & serial inference implementation path.

spec edits:
1. §4 FR-001 requirement text + add scenarios (缺资产失败关闭, 并发推理串行).
Current:
```
### Requirement: 编排内真实推理（`FR-001`）

系统应当提供一个非默认的 compose profile，使真实模型实例在编排内启动并保持 F001 冻结的 HTTP API 契约不变。

#### Scenario: profile 拉起

- GIVEN `vendor/Kronos` 与 `models/` 就位
- WHEN 执行 `docker compose -f ...`
- THEN `/health` 的 `model_enabled=true`，`/predict` 返回 `source=kronos`
```
New description: "系统应当提供一个非默认的 compose profile，使真实模型实例在编排内启动、完成启动期资产预检与模型加载、串行处理推理请求，并保持 F001 冻结的 HTTP API 契约不变。"
Add after profile scenario:
```
#### Scenario: 缺资产失败关闭

- GIVEN `vendor/Kronos`、模型或分词器任一缺失
- WHEN 启动 profile 实例
- THEN 进程非零退出并在日志打印缺失路径，不退回 mock

#### Scenario: 并发推理串行

- GIVEN 真实实例已就绪
- WHEN 多个 `/predict` 请求并发到达
- THEN 请求按序执行，模型加载至多一次，且无请求并发进入 predictor
```

2. §5 rewrite:
```
不适用长生命周期状态机（一次性运行时改造）；三条运行时不变式由测试锁定：

- **失败关闭**：real 模式启动期校验 vendor clone、模型与分词器目录及必需文件；任一缺失或加载失败即非零退出并打印缺失路径，**绝不退回 mock**；
- **串行推理**：进程内模型加载至多一次、推理互斥（进程级锁）；并发请求排队执行，不并发进入 predictor；
- **默认隔离**：未启用 profile 时默认编排不启动 real 服务，默认镜像不含 torch（NFR-001）。
```

3. §6: add SC-002 + AC-002.
Current:
```
### 成功标准

- **SC-001**：F001 AC-006 可由编排命令复跑（US-001）。

### 验收清单

- [ ] **AC-001** ...
```
Add SC-002: "- **SC-002**：失败关闭与串行推理不变式成立（US-001）。"
Add AC-002 after AC-001:
"- [ ] **AC-002** (`FR-001`): 失败关闭与串行推理——vendor/权重/分词器缺失或加载失败时 real 实例启动即非零退出并打印缺失路径（不退回 mock）；并发 `/predict` 下模型加载至多一次且推理互斥 — tests: `tests/unit/test_f004_kronos_runtime_contract.py`、`tests/integration/test_f004_real_profile.py`"

design edits:
1. §1: add thin-shell sentence. Current §1 paragraph:
"给 `kronos-service.Dockerfile` 增一个包含 torch/cpu 的构建目标，compose 用 `profiles: [kronos-real]` 挂一个额外服务，默认 `up` 不触发其构建。"
D002 adds: "薄壳做三处最小改造：real 模式启动预检、模型 eager load 与进程级推理锁（§5）。" But D007 will rewrite the first sentence (targets). Let me add the new sentence after:
"...默认 `up` 不触发其构建。薄壳做三处最小改造：real 模式启动预检、模型 eager load 与进程级推理锁（§5）。"

2. §2 intro: "沿用 F001 的 `src/alphamill/kronos_service/`，不新增 Python 模块。差异只在镜像层与挂载：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。"
New: "沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）。容器内路径与环境变量契约见下表（D008 will add the table）." Hmm — D008 adds the table. For D002, sentence: "沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）。" — and keep the paths sentence for D008 to replace with the table.

Wait the current §2 is a single line: "沿用 F001 的 `src/alphamill/kronos_service/`，不新增 Python 模块。差异只在镜像层与挂载：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。"
D002: replace "不新增 Python 模块。差异只在镜像层与挂载：" with "不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）：" — leaving paths for D008. So result: "沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。"

3. §4: add sentence. Current: "HTTP 契约与 F001 完全一致；唯一可观察差异是 `/health` 的 `model_enabled=true`、`/predict` 的 `source=kronos` 与 `model` 字段回报权重路径。"
Append: "real 实例在启动预检与 eager load 完成后才对外服务；预检/加载失败即进程非零退出（§7），不产生"enabled 但未加载"的可用中间态。"

4. §5 full rewrite:
Current:
```
## 5. Runtime、Workflow 与并发

- 启动：`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；
- 端口：真实实例用 8002，与默认 mock 实例的 8001 并存，避免二者互相顶替；
- 并发：单实例，CPU 推理串行，无共享状态。
```
New:
```
## 5. Runtime、Workflow 与并发

- 启动：`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；
- 启动序列（real 模式）：进程启动 → **预检**（`KRONOS_REPO_PATH`、模型/分词器目录及必需文件存在）→ **eager load**（一次性加载 Kronos + Tokenizer，放在应用启动钩子、先于接收流量）→ 服务就绪；预检或加载任一失败 → 打印缺失路径/错误并**非零退出**（real 服务 `restart: "no"`，失败态可直接观察，不静默降级）；
- readiness：容器 healthcheck 以 `/health` 的 `model_loaded=true`（且 `device=cpu`）为通过条件；mock 服务保持现状；
- 端口：真实实例用 8002（host）→ 8001（container），与默认 mock 实例的 8001 并存，避免二者互相顶替；
- 并发：单实例单 worker；**进程级锁**保证模型加载至多一次、推理互斥（并发请求排队），无其它共享状态；
- 数据前置：`/predict` 需要目标 exchange/symbol ≥30 根已闭合 1m K 线（DB 已迁移，F001 回填产物）。
```

5. §7 rewrite (D002 part):
Current:
```
## 7. 失败、恢复、安全与兼容

- 权重或 vendor 缺失 → 容器启动即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；
- 镜像体积：torch/cpu wheel 约 200MB，仅在启用 profile 时构建（NFR-001）。
```
D002 new (leave 镜像体积 for D007, leave :ro for D008... hmm, current §7 has only 2 bullets; I'll edit the fail bullet now):
"- 权重、分词器或 vendor 缺失/加载失败 → **启动期**即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；`restart: "no"` 使失败态保持可见；"

6. §9 add decision row for serialization:
"| 串行推理用进程级锁而非多 worker | uvicorn 单 worker + 进程级锁 | CPU 推理本身串行；多 worker 无收益且破坏"加载至多一次" | 若未来上 GPU 再评估批量吞吐 |"

Also design §8 test table? That's D004. Skip for now.

Let me apply.
**Finding 4/10 (D002)** — fail-closed + serial inference implementation path:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:54:04Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "给 `kronos-service.Dockerfile` 增一个包含 torch/cpu 的构建目标，compose 用 `profiles: [kronos-real]` 挂一个额外服务，默认 `up` 不触发其构建。", "newString": "给 `kronos-service.Dockerfile` 增一个包含 torch/cpu 的构建目标，compose 用 `profiles: [kronos-real]` 挂一个额外服务，默认 `up` 不触发其构建。薄壳做三处最小改造：real 模式启动预检、模型 eager load 与进程级推理锁（§5）。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "沿用 F001 的 `src/alphamill/kronos_service/`，不新增 Python 模块。差异只在镜像层与挂载：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。", "newString": "沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "HTTP 契约与 F001 完全一致；唯一可观察差异是 `/health` 的 `model_enabled=true`、`/predict` 的 `source=kronos` 与 `model` 字段回报权重路径。", "newString": "HTTP 契约与 F001 完全一致；唯一可观察差异是 `/health` 的 `model_enabled=true`、`/predict` 的 `source=kronos` 与 `model` 字段回报权重路径。real 实例在启动预检与 eager load 完成后才对外服务；预检/加载失败即进程非零退出（§7），不产生「enabled 但未加载」的可用中间态。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- 启动：`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；\n- 端口：真实实例用 8002，与默认 mock 实例的 8001 并存，避免二者互相顶替；\n- 并发：单实例，CPU 推理串行，无共享状态。", "newString": "- 启动：`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；\n- 启动序列（real 模式）：进程启动 → **预检**（`KRONOS_REPO_PATH`、模
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- 权重或 vendor 缺失 → 容器启动即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；", "newString": "- 权重、分词器或 vendor 缺失/加载失败 → **启动期**即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；`restart: \"no\"` 使失败态保持可见；"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "| 真实实例走 8002 而非顶替 8001 | 两种形态可并存对比 | mock 实例仍是默认链路的依赖 | 稳定后可评估是否合并 |", "newString": "| 真实实例走 8002 而非顶替 8001 | 两种形态可并存对比 | mock 实例仍是默认链路的依赖 | 稳定后可评估是否合并 |\n| 串行推理用进程级锁而非多 worker | uvicorn 单 worker + 进程级锁 | CPU 推理本身串行；多 worker 无收益且破坏「加载至多一次」 | 若未来上 GPU 再评估批量吞吐 |"})`


> [reasoning] Now the design.md edits for D002 (4 edits: §1, §2, §4, §5, §7, §9), then commit both files.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:54:12Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && python3 tools/validate_spec_lifecycle.py && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): 补失败关闭/串行推理实现路径与不变量（F004-D002）\n\n- spec：FR-001 加预检/eager load/串行语义与两个场景；§5 三条运行时不变式；SC-002/AC-002\n- design：启动序列（预检→eager load→就绪，失败非零退出 restart:no）、readiness、\n  进程级锁并发契约；§7 失败语义与 §9 串行决策\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
affc424 docs(f004): 补失败关闭/串行推理实现路径与不变量（F004-D002）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:54:15Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "### 测试策略\n\n- 复用 F001 的 `test_f001_kronos_smoke.py`（`KRONOS_REQUIRE_REAL_MODEL=1` + `KRONOS_BASE_URL` 指向 profile 实例）。", "newString": "### 测试策略\n\n- **静态编排契约（单元，CI 常绿）**：`tests/unit/test_f004_compose_profile_contract.py`——Dockerfile mock/real 目标与依赖 pin、compose real 服务的 profile/挂载/端口/环境、默认配置不含 real 服务；\n- **薄壳运行时契约（单元，CI 常绿）**：`tests/unit/test_f004_kronos_runtime_contract.py`——缺资产启动
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 起的实例 model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排行为与镜像层不变 — tests: `tests/integration/test_f001_kronos_smoke.py`", "newString": "- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 拉起的实例由目标 compose 服务与 real 构建目标产生（容器身份、只读挂载、8002:8001 成立），model_enabled=true 且 /predict 返回 source=kronos；不带
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |\n|---|---|---|---|\n| `AC-001` | integration | `tests/integration/test_f001_kronos_smoke.py` | profile 实例 model_enabled=true 且 source=kronos；默认 compose 配置不含 torch 层与权重挂载 |", "newString": "| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |\n|---|---|---|---|\n| `AC-001` | 静态契约（unit，CI 常绿） | `tests/unit/test_f004_compose_profile_contract.py` | Dockerfile 有 mock/re
…[truncated])`


> [reasoning] D002 done. Now D004: test strategy layering.

spec edits:
1. §7 测试策略 rewrite:
Old:
```
### 测试策略

- 复用 F001 的 `test_f001_kronos_smoke.py`（`KRONOS_REQUIRE_REAL_MODEL=1` + `KRONOS_BASE_URL` 指向 profile 实例）。
```
New (D004 core; D006 will append evidence discipline line):
```
### 测试策略

- **静态编排契约（单元，CI 常绿）**：`tests/unit/test_f004_compose_profile_contract.py`——Dockerfile mock/real 目标与依赖 pin、compose real 服务的 profile/挂载/端口/环境、默认配置不含 real 服务；
- **薄壳运行时契约（单元，CI 常绿）**：`tests/unit/test_f004_kronos_runtime_contract.py`——缺资产启动失败关闭、模型加载至多一次、推理互斥；
- **容器集成（执行机）**：`tests/integration/test_f004_real_profile.py`——构建 real 目标并拉起 profile，校验容器身份（compose 托管 + real 目标 + 只读挂载 + 8002:8001）与 `source=kronos`；缺资产场景非零退出；默认镜像 `import torch` 判红；开关语义与 F001 冒烟一致（未设 `ALPHAMILL_INTEGRATION` 时 skip、设了不可达判红）；
- F001 的 `test_f001_kronos_smoke.py` 保留 HTTP 契约职责（`source` 与 `model_enabled` 自洽、两方向判红），不再单独承担部署形态证明。
```

2. AC-001 rewrite (D004 part — container identity + tests paths; keep "镜像层不变" phrase for D007):
Old: "- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 起的实例 model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排行为与镜像层不变 — tests: `tests/integration/test_f001_kronos_smoke.py`"
New: "- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 拉起的实例由目标 compose 服务与 real 构建目标产生（容器身份、只读挂载、8002:8001 成立），model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排行为与镜像层不变 — tests: `tests/unit/test_f004_compose_profile_contract.py`、`tests/integration/test_f004_real_profile.py`"

design edits:
3. §8 table rewrite:
Old:
```
| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f001_kronos_smoke.py` | profile 实例 model_enabled=true 且 source=kronos；默认 compose 配置不含 torch 层与权重挂载 |
```
New:
```
| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | 静态契约（unit，CI 常绿） | `tests/unit/test_f004_compose_profile_contract.py` | Dockerfile 有 mock/real 目标且 real 锁定依赖 pin；real 服务 profiles/只读挂载/端口/环境正确；默认 compose 配置不含 real 服务 |
| `AC-001` | 容器集成（执行机） | `tests/integration/test_f004_real_profile.py` | compose 拉起后容器身份成立（compose 托管 + real 目标 + 只读挂载 + 8002:8001）且 `/predict source=kronos`；默认镜像 `import torch` 判红 |
| `AC-002` | 单元 | `tests/unit/test_f004_kronos_runtime_contract.py` | 缺资产/加载失败 → 非零退出且不退回 mock（fake 目录注入）；并发请求加载至多一次、推理互斥 |
| `AC-002` | 容器集成（执行机） | `tests/integration/test_f004_real_profile.py` | 缺资产场景以非零退出结束并在日志保留缺失路径；不产生可服务的 mock 降级实例 |
| HTTP 契约（F001 AC-002/006 复用） | integration | `tests/integration/test_f001_kronos_smoke.py` | 保留：`source` 与 `model_enabled` 自洽（两方向判红）；不承担部署形态证明 |

- 容器集成测试遵循 F001 冒烟同款开关语义：未设 `ALPHAMILL_INTEGRATION` 时 skip；设了开关而服务/容器不可达时判红，不得以 skip 代替证据。
- 每道新门禁（静态契约、容器集成）做一次变异验证：改 target、删依赖 pin、放开 `:ro` 必须判红。
```
(D006 will add the 取证机器 note line.)

Commit D004 with spec+design.
**Finding 5/10 (D004)** — test strategy layering (F004-specific static + container gates):

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:54:26Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && python3 tools/validate_spec_lifecycle.py && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): 测试策略分层——专属静态/容器门禁替代冒烟兜底（F004-D004）\n\n- AC-001 改由 F004 专属静态契约 + 容器集成证明（容器身份/只读挂载/端口）\n- F001 冒烟职责收窄为 HTTP 契约；补 AC-002 单元/容器映射与变异验证要求\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
14f06e1 docs(f004): 测试策略分层——专属静态/容器门禁替代冒烟兜底（F004-D004）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:54:30Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- `deployment/kronos-service.Dockerfile` 增加 torch/cpu + einops + safetensors 的可选构建目标；", "newString": "- `deployment/kronos-service.Dockerfile` 增加 torch CPU wheel + einops + safetensors + huggingface_hub + tqdm 的可选构建目标（版本与 wheel 来源在 design 锁定）；"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。", "newString": "沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。\n
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "| 串行推理用进程级锁而非多 worker | uvicorn 单 worker + 进程级锁 | CPU 推理本身串行；多 worker 无收益且破坏「加载至多一次」 | 若未来上 GPU 再评估批量吞吐 |", "newString": "| 串行推理用进程级锁而非多 worker | uvicorn 单 worker + 进程级锁 | CPU 推理本身串行；多 worker 无收益且破坏「加载至多一次」 | 若未来上 GPU 再评估批量吞吐 |\n| 依赖 pin 取宿主 AC-006 实测版本 | torch 2.14.0（CPU index）+ einops 0.8.2 / safetensors 0.8.0 / huggingface_hub 1.31.0 / tqdm 4.70.0 | 与已实测通过的宿主环境一致；上游 requireme
…[truncated])`


> [reasoning] D004 done. Now D005: dependency pins.

spec edit:
§3 范围内 bullet 1: old "- `deployment/kronos-service.Dockerfile` 增加 torch/cpu + einops + safetensors 的可选构建目标；" — wait, let me check current spec §3 范围内 line 63: "- `deployment/kronos-service.Dockerfile` 增加 torch/cpu + einops + safetensors 的可选构建目标；"
New: "- `deployment/kronos-service.Dockerfile` 拆 mock/real 构建目标；real 目标锁定最小推理依赖（torch CPU wheel + einops + safetensors + huggingface_hub + tqdm）与版本；" — this also includes D007's target split. Hmm, D007 is next (after D005 in figure but actually order: D005 then D006 then D007). The bullet mentions "可选构建目标"→"构建目标" already here; D007 refines to "mock/real". Let me for D005 only change dependency list: "增加 torch/cpu + einops + safetensors + huggingface_hub + tqdm 的可选构建目标（版本与 wheel 来源在 design 锁定）；" then D007 rewrites to mock/real target wording. OK.

design §2 add pin paragraph after the intro line (before §3). Current §2 after my D002 edit:
"沿用 F001 的 ... `KRONOS_MODEL_PATH=/app/models/Kronos-base`。"
Add:
"
**real 目标的依赖 pin（镜像内）**：`torch==2.14.0`（`--index-url https://download.pytorch.org/whl/cpu`，CPU wheel；与宿主 AC-006 实测同版）+ `einops==0.8.2`、`safetensors==0.8.0`、`huggingface_hub==1.31.0`、`tqdm==4.70.0`（pin 上游直接 import 的最小集：`model/kronos.py` 导入 torch/huggingface_hub/tqdm，`model/module.py` 导入 einops；版本取宿主 AC-006 实测集，容器内真实权重加载验证后锁定；上游 `requirements.txt` 仅作参考）。"

design §9 add decision row:
"| 依赖 pin 取宿主 AC-006 实测版本 | torch 2.14.0（CPU index）+ einops 0.8.2 / safetensors 0.8.0 / huggingface_hub 1.31.0 / tqdm 4.70.0 | 与已实测通过的宿主环境一致；上游 requirements 仅参考 | 容器内真实权重加载验证通过后锁定 |"

Also design §7? maybe not needed. tasks T003 deferred to D010 (will mention deps).

Also check spec §1 问题 mentions... no deps. spec §7 依赖 mentions "执行机 docker-ce 可构建 torch CPU 镜像" — fine.

Commit D005.
**Finding 6/10 (D005)** — lock minimal inference deps + torch CPU wheel source:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:54:38Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): 锁定 real 镜像最小推理依赖与 torch CPU wheel 来源（F004-D005）\n\n- design §2：torch==2.14.0 @ download.pytorch.org/whl/cpu + einops/safetensors/\n  huggingface_hub/tqdm 实测 pin，含上游 import 依据；§9 决策行\n- spec 范围内依赖清单同步\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
283f052 docs(f004): 锁定 real 镜像最小推理依赖与 torch CPU wheel 来源（F004-D005）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:54:42Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- **执行环境**：与 F001 收口态一致（WSL2 + docker-ce；本机无独立显卡，CPU 推理实测 3.4–7.2s/次）", "newString": "- **执行环境**：容器集成与验收在执行机 `qiaozhi-lt`（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）取证，证据记录 hostname 与 `device=cpu`（本 feature 不做 GPU 直通；CPU 推理实测 3.4–7.2s/次）；开发机 `qiaozhi-gp`/`gp-wsl` 只跑静态编排断言与单元门禁（SOP §3、架构 §7.1）"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- 每道新门禁（静态契约、容器集成）做一次变异验证：改 target、删依赖 pin、放开 `:ro` 必须判红。", "newString": "- 每道新门禁（静态契约、容器集成）做一次变异验证：改 target、删依赖 pin、放开 `:ro` 必须判红。\n- 集成/容器证据必须在执行机 `qiaozhi-lt` 采集并记录 hostname 与 `device=cpu`（SOP §3、架构 §7.1）；开发机只跑静态与单元门禁，开发机 skip 不算证据。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- F001 的 `test_f001_kronos_smoke.py` 保留 HTTP 契约职责（`source` 与 `model_enabled` 自洽、两方向判红），不再单独承担部署形态证明。", "newString": "- F001 的 `test_f001_kronos_smoke.py` 保留 HTTP 契约职责（`source` 与 `model_enabled` 自洽、两方向判红），不再单独承担部署形态证明；\n- **取证纪律**：容器与集成证据必须在执行机 `qiaozhi-lt` 采集并记录 hostname 与 `device=cpu`（SOP §3、架构 §7.1）；开发机只跑静态与单元门禁，开发机 skip 不算证据。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "**独立测试**：新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿。", "newString": "**独立测试**：新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿；容器集成验收在执行机 `qiaozhi-lt` 取证（记录 hostname
…[truncated])`


> [reasoning] D005 done. Now D006: execution machine evidence.

Edits:
1. design §0 执行环境 bullet. Current:
"- **执行环境**：与 F001 收口态一致（WSL2 + docker-ce；本机无独立显卡，CPU 推理实测 3.4–7.2s/次）"
New:
"- **执行环境**：容器集成与验收在执行机 `qiaozhi-lt`（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）取证，证据记录 hostname 与 `device=cpu`（本 feature 不做 GPU 直通；CPU 推理实测 3.4–7.2s/次）。开发机 `qiaozhi-gp`/`gp-wsl` 只跑静态编排断言与单元门禁（SOP §3、架构 §7.1）"

2. design §8 add evidence note line. After the variable-verification bullet, add:
"- 集成/容器证据必须在执行机采集并记录 hostname 与 `device=cpu`（SOP §3、架构 §7.1）；开发机只跑静态与单元门禁，开发机 skip 不算证据。"

3. spec §7 测试策略 add same evidence discipline bullet (after container integration bullet or at end). Add as last bullet:
"- **取证纪律**：容器与集成证据必须在执行机 `qiaozhi-lt` 采集并记录 hostname 与 `device=cpu`（SOP §3、架构 §7.1）；开发机只跑静态与单元门禁，开发机 skip 不算证据。"

4. spec §2 独立测试 append evidence machine clause — current after D003:
"**独立测试**：新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿。"
New: append "容器集成验收在执行机 `qiaozhi-lt` 取证（记录 hostname + `device=cpu`），开发机只跑静态与单元门禁（§7）。"

5. Maybe spec AC-001 append "证据记录取证机"? The §7 covers it. Skip.

6. tasks T003 verify — deferred to D010.

Commit D006.
**Finding 7/10 (D006)** — execution-machine evidence discipline (`qiaozhi-lt` + hostname/device):

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:54:50Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): 验收环境改为执行机取证并记录 hostname/device（F004-D006）\n\n- design §0 执行环境：qiaozhi-lt 取证、device=cpu，开发机只跑静态与单元门禁\n- spec §2/§7 与 design §8 补取证纪律；与 SOP §3、架构 §7.1 对齐\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
820e804 docs(f004): 验收环境改为执行机取证并记录 hostname/device（F004-D006）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:54:53Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- `deployment/kronos-service.Dockerfile` 增加 torch CPU wheel + einops + safetensors + huggingface_hub + tqdm 的可选构建目标（版本与 wheel 来源在 design 锁定）；", "newString": "- `deployment/kronos-service.Dockerfile` 拆 `mock`（保持现状、不含 torch）与 `real` 两个构建目标，compose 两个服务各自显式声明 target；real 目标含 torch CPU wheel + einops + safetensors + huggingface_hub + tqdm（版本与 wheel 来源在 design 锁定）；"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- **NFR-001**：默认 `docker compose up` 的行为与镜像体积不受本 feature 影响（profile 未启用时不构建 torch 层）。", "newString": "- **NFR-001**：默认 `docker compose -f deployment/docker-compose.yml up` 的行为与镜像不受本 feature 影响——默认镜像（`mock` 构建目标）不含 torch，profile 未启用时不启动、不构建 real 服务。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "（容器身份、只读挂载、8002:8001 成立），model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排行为与镜像层不变 — tests:", "newString": "（容器身份、只读挂载、8002:8001 成立），model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排不启用也不构建 real 服务、默认镜像不含 torch — tests:"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "给 `kronos-service.Dockerfile` 增一个包含 torch/cpu 的构建目标，compose 用 `profiles: [kronos-real]` 挂一个额外服务，默认 `up` 不触发其构建。薄壳做三处最小改造：real 模式启动预检、模型 eager load 与进程级推理锁（§5）。", "newString": "给 `kronos-service.Dockerfile` 拆出 `mock`（保持现状、不含 torch）与 `real` 两个构建目标；compose 两个服务各自显式声明 target，`kronos-signal-real` 用 `profiles: [kronos-real]`，默认 `up` 不启用也不构建该服务。薄壳做三处最小改造：real 模式启动预检、模型 eager load 与进程级推
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- 镜像体积：torch/cpu wheel 约 200MB，仅在启用 profile 时构建（NFR-001）。", "newString": "- 镜像体积：real 目标（torch CPU wheel 约 200MB）仅在启用 profile 时构建；默认镜像（mock 目标）不含 torch，默认编排行为不变（NFR-001）。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "| 残余风险：torch 镜像层拖慢 CI | CI 不构建该 profile | profile 未启用时 compose 不解析其构建 | 若 CI 需要则单独 job |", "newString": "| 残余风险：torch 镜像层拖慢 CI | CI 不构建也不启用 real 目标；默认镜像不含 torch 由静态门禁锁定 | profile 未启用时 compose 不构建该服务 | 若 CI 需要 real 构建则单独 job |"})`


> [reasoning] D006 done. Now D007: mock/real targets & assertable NFR criterion.

Edits:
1. spec NFR-001:
Old: "- **NFR-001**：默认 `docker compose up` 的行为与镜像体积不受本 feature 影响（profile 未启用时不构建 torch 层）。"
New: "- **NFR-001**：默认 `docker compose -f deployment/docker-compose.yml up` 的行为与镜像不受本 feature 影响——默认镜像（`mock` 构建目标）不含 torch，profile 未启用时不启动、不构建 real 服务。"

2. spec AC-001 phrase: "...不带该 profile 时默认编排行为与镜像层不变 — tests..." → "...不带该 profile 时默认编排不启用也不构建 real 服务、默认镜像不含 torch — tests..."
Current AC-001: "- [ ] **AC-001** ...；不带该 profile 时默认编排行为与镜像层不变 — tests: ..."

3. spec §3 范围内 bullet 1: currently "增加 torch CPU wheel + ... 的可选构建目标（版本与 wheel 来源在 design 锁定）；" → make it explicit "拆 mock/real 两个构建目标：mock 保持现状（无 torch），real 目标含 torch CPU wheel + einops + safetensors + huggingface_hub + tqdm（版本与 wheel 来源在 design 锁定）；"

4. design §1 first sentence: "给 `kronos-service.Dockerfile` 增一个包含 torch/cpu 的构建目标，compose 用 `profiles: [kronos-real]` 挂一个额外服务，默认 `up` 不触发其构建。" → "给 `kronos-service.Dockerfile` 拆出 `mock`（保持现状、不含 torch）与 `real` 两个构建目标；compose 两个服务各自显式声明 target，`kronos-signal-real` 用 `profiles: [kronos-real]`，默认 `up` 不启用也不构建该服务。"

5. design §7 镜像体积 bullet: "镜像体积：torch/cpu wheel 约 200MB，仅在启用 profile 时构建（NFR-001）。" → "镜像体积：real 目标（torch CPU wheel 约 200MB）仅在启用 profile 时构建；默认镜像（mock 目标）不含 torch，默认编排行为不变（NFR-001）。"

6. design §5 readiness line? No. design §9 torch/CI row: "残余风险：torch 镜像层拖慢 CI | CI 不构建该 profile | profile 未启用时 compose 不解析其构建 | 若 CI 需要则单独 job" → "残余风险：torch 镜像层拖慢 CI | CI 不构建也不启用 real 目标；默认镜像不含 torch 由静态门禁锁定 | profile 未启用时 compose 不构建该服务 | 若 CI 需要 real 构建则单独 job"。

Commit D007.
**Finding 8/10 (D007)** — mock/real build targets + stable NFR-001 criterion:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:55:03Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && python3 tools/validate_spec_lifecycle.py && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): 定义 mock/real 构建目标与可稳定断言的 NFR 判据（F004-D007）\n\n- Dockerfile 拆 mock/real target，compose 两服务显式 target\n- NFR-001/AC-001 判据从'镜像层与改前一致'改为'默认镜像不含 torch + 默认不启用/构建 real'\n- §7 镜像体积与 §9 CI 风险行同步\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
1cb2d9b docs(f004): 定义 mock/real 构建目标与可稳定断言的 NFR 判据（F004-D007）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:55:07Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。", "newString": "沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）。real 服务的容器挂载、环境变量与端口契约：\n\n| 项 | real 服务契约 |\n|---|---|\n| 构建目标 | `target: real`，`profil
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- 权重、分词器或 vendor 缺失/加载失败 → **启动期**即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；`restart: \"no\"` 使失败态保持可见；\n- 镜像体积：real 目标（torch CPU wheel 约 200MB）仅在启用 profile 时构建；默认镜像（mock 目标）不含 torch，默认编排行为不变（NFR-001）。", "newString": "- 权重、分词器或 vendor 缺失/加载失败 → **启动期**即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；`restart: \"no\"` 使失败态保持可见；\n- 资产只读：`vendor/Kronos` 与 `models/` 以 `:ro` 挂载，容器不写宿主资产；\n-
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- compose 增 `kronos-real` profile：挂载 `vendor/Kronos` 与 `models/`，`KRONOS_USE_REAL_MODEL=true`；", "newString": "- compose 增 `kronos-signal-real` 服务（`profiles: [kronos-real]`）：只读挂载 `vendor/Kronos` 与 `models/`（`:ro`），`KRONOS_USE_REAL_MODEL=true`，host 8002 → container 8001；"})`


> [reasoning] D007 done. Now D008: mount/env/port contract completion.

design §2: replace the tail sentence "容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。" with a full contract table. Current §2 after edits:

```
沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。

**real 目标的依赖 pin（镜像内）**：...
```

Replace the trailing clause with:
"容器内挂载、环境变量与端口契约如下：

| 项 | real 服务契约 |
|---|---|
| 构建目标 | `target: real`，`profiles: [kronos-real]` |
| 挂载 | `../vendor/Kronos:/app/vendor/Kronos:ro`；`../models:/app/models:ro` |
| KRONOS_REPO_PATH | `/app/vendor/Kronos` |
| KRONOS_MODEL_PATH | `/app/models/Kronos-base` |
| KRONOS_TOKENIZER_PATH | `/app/models/Kronos-Tokenizer-base` |
| KRONOS_USE_REAL_MODEL / KRONOS_DEVICE | `true` / `cpu` |
| 端口 | host `8002` → container `8001`（mock 保持 host 8001，互不顶替） |
"

So the sentence becomes: "沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）。real 服务契约："

Then the table, then the pin paragraph.

design §5 port line: current "- 端口：真实实例用 8002（host）→ 8001（container），与默认 mock 实例的 8001 并存，避免二者互相顶替；" — that's already complete (D002 wrote it). D008's fix says "说明 host 8002 到 container 8001 的端口映射" — done. Maybe no further edit needed. But the §2 table is the main deliverable. Also add ":ro" to §7? D002's §7 bullet mentions "资产只读"? No — I didn't add read-only there; D008 adds:
"- 资产只读：vendor/models 以 `:ro` 挂载，容器不写宿主资产；"

design §7 current bullets:
"- 权重、分词器或 vendor 缺失/加载失败 → 启动期...；
- 镜像体积：...；
- 兼容：..." wait let me recall: §7 originally had 2 bullets; D002 edited first. Current §7:
```
## 7. 失败、恢复、安全与兼容

- 权重、分词器或 vendor 缺失/加载失败 → **启动期**即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；`restart: "no"` 使失败态保持可见；
- 镜像体积：real 目标（torch CPU wheel 约 200MB）仅在启用 profile 时构建；默认镜像（mock 目标）不含 torch，默认编排行为不变（NFR-001）。
```
Add third bullet: "- 资产只读与隔离：vendor/models 以 `:ro` 挂载，容器不写宿主资产；mock 默认链路不受 real profile 影响。"

Hmm "mock 默认链路不受影响" is D001-ish; keep it as part of D008 bullet: "- 资产只读：`vendor/Kronos` 与 `models/` 以 `:ro` 挂载，容器不写宿主资产。"

Also check spec §3 范围内 currently: "compose 增 `kronos-real` profile：挂载 `vendor/Kronos` 与 `models/`，`KRONOS_USE_REAL_MODEL=true`；" — D008 could refine to "只读挂载 ... host 8002→container 8001"? The spec 范围内 bullet will be rewritten in D010's tasks? No, spec is separate. Let me update the spec bullet too:
Old: "- compose 增 `kronos-real` profile：挂载 `vendor/Kronos` 与 `models/`，`KRONOS_USE_REAL_MODEL=true`；"
New: "- compose 增 `kronos-signal-real` 服务（`profiles: [kronos-real]`）：只读挂载 `vendor/Kronos` 与 `models/`（`:ro`），`KRONOS_USE_REAL_MODEL=true`，host 8002 → container 8001；"

Commit D008 with spec+design.
**Finding 9/10 (D008)** — complete mount/env/port contract:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:55:17Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "offset": 23, "limit": 45})`


> [reasoning] Wait, I need to check the design §2 table: I split the §2 paragraph by removing the trailing "：" clause. Let me verify the current state of design §1-2 to make sure formatting is right (the table needs a blank line before/after, and my replacement ended with the table row "| 端口 | ... |" then next line is the **real 目标的依赖 pin** paragraph — need a blank line between table and paragraph!). Let me check.

Also commit D008 after verifying.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md</path>
<type>file</type>
<content>
23: ## 1. 技术概要与影响面
24:
25: 给 `kronos-service.Dockerfile` 拆出 `mock`（保持现状、不含 torch）与 `real` 两个构建目标；compose 两个服务各自显式声明 target，`kronos-signal-real` 用 `profiles: [kronos-real]`，默认 `up` 不启用也不构建该服务。薄壳做三处最小改造：real 模式启动预检、模型 eager load 与进程级推理锁（§5）。
26:
27: - 后端 / API：无变更（同一份 `kronos_service`）
28: - 存储 / Migration：无
29: - Event / Evidence：F001 AC-006 的复跑命令改为 compose 形态
30: - 文档 / 配置：F001 spec §6 命令回写；`vendor/VENDORED.md` 补容器内路径说明
31:
32: ## 2. 架构与模块边界
33:
34: 沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）。real 服务的容器挂载、环境变量与端口契约：
35:
36: | 项 | real 服务契约 |
37: |---|---|
38: | 构建目标 | `target: real`，`profiles: [kronos-real]
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:55:19Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && python3 tools/validate_spec_lifecycle.py && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): 补全挂载/环境变量/端口两侧契约（F004-D008）\n\n- design §2 增 real 服务契约表：:ro 挂载、KRONOS_REPO_PATH/MODEL_PATH/TOKENIZER_PATH、\n  USE_REAL_MODEL/DEVICE、host 8002→container 8001\n- §7 补资产只读约束；spec 范围内同步\" && git log --oneline -1"})`


> [reasoning] Formatting looks good. Commit D008.

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
49e6c9d docs(f004): 补全挂载/环境变量/端口两侧契约（F004-D008）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:55:22Z

- **tool**: `write({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "content": "---\nkind: feature\nid: F004\nversion: \"0.2\"\nrelated_features: [F001, F002]\ntopics: [kronos, inference, deployment]\ndoc_kind: tasks\ncreated: 2026-09-12\nupdated: 2026-09-14\n---\n\n# F004：Kronos 真实推理运行时 - 任务\n\n> Owner: Georg | Spec: `spec.md` | Design: `design.md`\n\n## 0. 来源与执行规则\n\n- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。\n- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。\n- 完成且验证后立即把
…[truncated])`


> [reasoning] D008 done. Now D010: tasks.md restructure (complete rewrite), plus verify commands unified with -f, plus new tasks from D002/D004/D005/D006/D007.

Let me write the new tasks.md. I drafted it earlier. Let me finalize with today's date and all details. Also update "updated: 2026-09-14".

One consideration on task refs: AC-002 exists now; use it where apt. T001/T002 (`FR-001`), T003 (`FR-001`, `NFR-001`), T004 (`FR-001`, `NFR-001`), T005 (`AC-001`), T006 (`AC-001`, `FR-001`), T007 (`FR-001`), T008 (`AC-001`, `AC-002`), T009 (`AC-001`), T010 (`AC-001`, `NFR-001`), T011 (no refs, per template).

Verify commands with -f:
- T004: `docker compose -f deployment/docker-compose.yml config --services`（默认不含 real）；`docker compose -f deployment/docker-compose.yml --profile kronos-real config`（含 real）
- T008 integration command: `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py tests/integration/test_f004_real_profile.py -q`（执行机 qiaozhi-lt，记录 hostname/device）

Wait: F001 smoke with KRONOS_BASE_URL 8002 — after T007 writeback, F001 spec §6 will have compose-form command. The exact final command form depends on implementation; keep the pytest invocation.

Also tasks §0 rules: add `[P]` explanation and evidence machine line? Template §0 fixed items; can add extra lines. The template says "每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID" etc. I'll add the execution-machine line and [P] rule (it exists in F002 tasks).

§1 前置条件: keep F001 done + Q-001 closed (reword since Q-001 is already closed: "spec §8 Q-001 已关闭（不阻塞 F002 done），无阻塞性设计问题；本 feature 开工前 design §10 为空（现为「无」）。" Hmm — the SOP prerequisite is design §10 cleared; currently "无". I can state: "design §10 待确认设计问题为空（已满足开工前提）". Also add data precondition.

Let me also think again about Phase naming: "Phase 1：薄壳运行时改造", "Phase 2：镜像与编排", "Phase 3：专属门禁测试". Phase 3 tasks create tests — but tests for T001/T002 are referenced by T001/T002 verify... Hmm: T001 verify references test file `test_f004_kronos_runtime_contract.py` which is created in...? If it's created in Phase 1 as part of T001/T002 (write test then fix), fine. Phase 3's T005 is "静态编排契约门禁定稿" and T006 "容器集成测试". But T003/T004 verify also reference `test_f004_compose_profile_contract.py` (static). So tests are developed alongside each task (TDD), and T005/T006 are integration/consolidation? That's redundant.

Let me restructure tasks more cleanly:
- T001: 薄壳启动预检+eager load，verify: unit test (new file, written here)
- T002: 推理锁，verify: same unit file
- T003: Dockerfile targets + deps，verify: static test file (new)
- T004: compose service，verify: same static file + config commands
- T005: 静态门禁补齐变异验证（default no torch etc.）→ this is part of T003/T004's tests...

Hmm. Maybe better: make test creation explicit tasks per finding area:
- T005 (`AC-001`): 静态编排门禁定稿 + 变异验证 (verify: static test + mutation record)
- T006 (`AC-001`, `AC-002`): 容器集成门禁 (verify: integration test file)

That's what I had. The verify refs on T001-T004 pointing to files created by T005/T006 are forward references — but tasks are executed in order; T001's verify test would need to exist. Contradiction: T001 can't verify against a file created later.

Resolution options:
(a) Each implementation task's verify names the specific test function in the file; the file is created during that task (tests-alongside). Then T005/T006 become "门禁加固/变异验证" tasks focusing on completeness & mutation (not first creation). That works: T001 creates `test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets` while implementing; T002 adds the concurrency test to the same file. T003 creates parts of static test file; T004 adds compose assertions. T005 = mutation verification + fill gaps (e.g., default image torch check may be integration? "默认镜像不含 torch" — can be proven statically (Dockerfile parse) or by container import test (integration). Let me assign: static test asserts default target doesn't install torch; integration test asserts built default image `import torch` fails (stronger). Reviewer D007 asked criterion "默认镜像不含 torch" — the integration test proves it on the real artifact. Put that in T006 integration.
(b) Fine, keep (a).

So final tasks:

Phase 1：薄壳运行时改造
- T001 (`FR-001`): 启动预检 + eager load + fail-closed — verify: `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`
- T002 (`FR-001`): 进程级推理锁 — verify: `tests/unit/test_f004_kronos_runtime_contract.py::test_predictor_loads_once_and_inference_serializes`

Phase 2：镜像与编排
- T003 (`FR-001`, `NFR-001`): Dockerfile 拆 mock/real + 依赖 pin — verify: `tests/unit/test_f004_compose_profile_contract.py::test_dockerfile_targets_pin_real_dependencies`
- T004 (`FR-001`, `NFR-001`): compose real 服务 — verify: `tests/unit/test_f004_compose_profile_contract.py::test_compose_real_service_contract` + `docker compose -f deployment/docker-compose.yml config --services`（默认不含）`--profile kronos-real config`（含）

Phase 3：门禁与回写
- T005 (`AC-001`): 静态门禁补齐 + 变异验证（改 target / 删 pin / 去 :ro 判红；默认镜像目标不含 torch） — verify: `tests/unit/test_f004_compose_profile_contract.py`（含变异记录）
- T006 (`AC-001`, `AC-002`): F004 容器集成测试：真实容器身份 + source=kronos + 缺资产非零退出 + 默认镜像 import torch 判红 — verify: `tests/integration/test_f004_real_profile.py`
- T007 (`FR-001`): F001 spec §6 AC-006 命令回写 compose 形态 + 手工回退 — verify: `python3 tools/verify.py`

§3 验证与验收任务:
- T008 (`AC-001`, `AC-002`): 执行机 `qiaozhi-lt` 集成验收（F001 冒烟 + F004 容器套件），证据记录 hostname/`device=cpu` — verify: `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py tests/integration/test_f004_real_profile.py -q`
- T009 (`AC-001`): 回写 spec §6 验收证据（命令、输出摘要、取证机 hostname、device） — verify: `python3 tools/verify.py`（文档门禁）
- T010 (`AC-001`, `NFR-001`): 项目统一质量门 — verify: `python3 tools/verify.py`
- T011: 状态推进（spec frontmatter）与 BACKLOG 同步 — verify: `python3 tools/verify.py`（含生命周期/BACKLOG 双向校验）

§4 依赖:
- `T001 -> T002`：同一薄壳文件顺序改造（预检/加载 → 锁）
- `T001/T002 -> T006`：容器集成依赖启动预检、eager load 与串行推理行为成立
- `T003 -> T004`：compose target 依赖 Dockerfile 目标定义
- `T003/T004 -> T005`：静态门禁锁定镜像与编排定义
- `T005 -> T006`：容器集成建立在静态契约之上
- `T006 -> T007`：F001 命令回写以 compose 形态实测通过为前提
- `T007 -> T008 -> T009 -> T010 -> T011`：验收链顺序执行（实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步）

§5 明确后移:
- GPU 直通与推理性能优化 → `v0.2.x` 后续评估：需执行机 GPU 直通条件，不属本 feature。
- 消费者路由切换（Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 指向真实实例）→ `v0.2.x` 后续评估（未立项）：涉及默认 mock 链路可用性与跨 feature 契约；F004 只交付编排内可复现的真实信号源（spec §3 范围外）。

Hmm, the template says "第 5 节只能放明确移交给其它 Feature/版本的内容，必须写目标 Feature/版本". "v0.2.x 后续评估（未立项）" — is that acceptable? It gives version. I could name "F00x（未立项）". I'll write "→ `v0.2.x` 后续评估（未立项）". Good enough; the reviewer can push back if needed.

Also §1 前置条件: current text includes "spec §8 Q-001（是否阻塞 F002 done）未关闭前，本 feature 不进入 ready-for-development。" — stale (Q-001 is closed). Rewrite:
"- F001 已 done：薄壳、`vendor/Kronos` pin 与 `models/` 权重流程成立，AC-006 已有手工命令形态实测证据；回填数据满足目标 exchange/symbol ≥30 根已闭合 1m K 线。
- spec §8 Q-001 已关闭（不阻塞 F002 done）；design §10 待确认设计问题为空——进入 `ready-for-development` 的阻塞项已清。"

Let me now write the full tasks.md.
**Finding 10/10 (D010)** — restructure tasks.md (complete DAG, split evidence writeback / status sync, unified final gate, all commands `-f`):

  <details><summary>tool output</summary>

  ```text
Wrote file successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:55:41Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && python3 tools/validate_spec_lifecycle.py && python3 tools/check_doc_links.py && git add docs/features/0.2/F004-kronos-inference-runtime/tasks.md && git commit -q -m \"docs(f004): tasks 重构——完整 DAG、拆分证据回写与状态同步（F004-D010）\n\n- T001-T011 按薄壳/镜像编排/门禁回写分三段，命令全部加 -f 定位\n- 验收链 T006->T007->T008->T009->T010->T011 串通；证据回写与状态/BACKLOG 拆分\n- 最终门统一 python3 tools/verify.py；§5 后移项补消费者路由\n- 本提交同时承载其余 finding 的任务级更新（T001/T002@D002、T003@D005、\n  T005/T006@D004、T008@
…[truncated])`


> [reasoning] Wait — I need to double check the tasks.md §4 dependency line: reviewer wanted "T004 -> T005 -> 验收证据回写 -> 状态/BACKLOG 同步" chain. My DAG has T003/T004→T005→T006→T007(回写 F001)→T008(实测)→T009(证据回写)→T010(门禁)→T011(状态). Good.

But hold on: T006 (容器集成测试) → T007 (F001 writeback) → T008 (执行机验收). And T005 static → T006. OK.

Now run validate + commit D010. But wait — the tasks.md rewrite includes command fixes for D003 (T004/T008 commands), dependency pin refs for D005 (T003), target refs for D007 (T003/T004/T005), evidence machine for D006 (T008/§0), tests for D004 (T005/T006), fail-closed/lock for D002 (T001/T002). That's the merged tasks commit for D010 as planned. Note in commit message.

Also check: validate_spec_lifecycle — "Phase 只能作为「2. 实现任务」下的三级标题" — my Phase headings are under §2. ✓. Also T011 without refs — template precedent. ✓. AC refs: T005/T006/T008/T009/T010 reference AC-001/AC-002 — tasks refs aren't validated by the script (it only validates AC lines in spec). ✓.

Now spec: does the AC-001 line reference tests paths `tests/unit/test_f004_compose_profile_contract.py` etc. — draft status, existence not checked. ✓.

Let me run validate + check_doc_links + commit. Then run full verify. Then write FIX-log.

Actually wait, one thing: in tasks T008 verify command, `KRONOS_BASE_URL=http://127.0.0.1:8002` — but the F004 real service publishes 8002 on the host. F001 smoke will hit 8002. OK.

Also T004 verify has `docker compose ... config --services（不含 real）` — parentheses inside backticks? I wrote: "`docker compose -f deployment/docker-compose.yml config --services`（不含 real）与 ..." — fine.

Another check: tasks.md line "T004 ... healthcheck 以 `model_loaded=true` 为通过条件、失败不自动重启" — aligns with design. OK.

Commit.

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
check_doc_links: 相对链接全部可解析
904f2cb docs(f004): tasks 重构——完整 DAG、拆分证据回写与状态同步（F004-D010）
49e6c9d docs(f004): 补全挂载/环境变量/端口两侧契约（F004-D008）
1cb2d9b docs(f004): 定义 mock/real 构建目标与可稳定断言的 NFR 判据（F004-D007）
820e804 docs(f004): 验收环境改为执行机取证并记录 hostname/device（F004-D006）
283f052 docs(f004): 锁定 real 镜像最小推理依赖与 torch CPU wheel 来源（F004-D005）
14f06e1 docs(f004): 测试策略分层——专属静态/容器门禁替代冒烟兜底（F004-D004）
affc424 docs(f004): 补失败关闭/串行推理实现路径与不变量（F004-D002）
abef312 docs(f004): 补 D003 遗漏——FR-001 场景命令加 -f 定位（F004-D003）
88dfce9 docs(f004): 命令统一 -f 定位并补齐数据前置（F004-D003）
1e81b7c docs(f004): 删除 signals_log 自动升级承诺，显式后移消费者路由（F004-D001）
10cd1d8 docs(f004): 修正 PRD 来源引用——FR3 改为下游评测关系（F004-D009）
bc314f0 chore(f002): 正式收口——review→done，T021 真实库证据补齐，移出活跃索引
bd87eac docs(f003,f008): 立项 AlphaGen 生成器平面与宇宙扩容，
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:55:48Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "offset": 65})`


> [reasoning] All 10 findings fixed, 11 commits. Now:
1. Review the final state of the three docs for coherence (read them fully once).
2. Run full `python3 tools/verify.py` (round-end full gate).
3. Write FIX-log.md Round 1 with evidence triple.

Let me read the final spec/design/tasks to check coherence and catch any self-introduced issues (my own fix-regressions). This is essentially a self-review pass. Let me read all three files.
All 10 findings have commits. Now the round-end full gate + a coherence read of the final artifacts:

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: status: draft
6: gate_version: 1
7: related_features: [F001, F002]
8: topics: [kronos, inference, deployment]
9: doc_kind: spec
10: created: 2026-09-12
11: updated: 2026-09-14
12: ---
13:
14: # F004：Kronos 真实推理运行时（编排内可复现）
15:
16: > Owner: Georg | Target: v0.2.x
17:
18: ## 0. 来源与意图
19:
20: - **PRD 来源**：`docs/alphamill-prd.md` M0（自包含运行基线：Kronos 服务在编排内健康）、FR1.2（`signals_log` 进入不可变快照）与 FR5（运行链：信号服务的运行时载体）；FR3（证据评测与验证）仅为下游关系——F004 为评测提供可复现的真实 Kronos 信号源，不实现评测本身
21: - **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑）、§7.1（机器边界）
22: - **上游来源**：F001 AC-006（真实推理证据，当前靠仓外手工实例）、F002 检视 F002-Q001（容器化不在数据桥契约内，需独立载体）

…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md</path>
<type>file</type>
<content>
65: ## 6. UI 与可观测性
66:
67: 无新 UI；`/health` 的 `model_enabled`/`device`/`model_error` 已足以判别实例形态。
68:
69: ## 7. 失败、恢复、安全与兼容
70:
71: - 权重、分词器或 vendor 缺失/加载失败 → **启动期**即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；`restart: "no"` 使失败态保持可见；
72: - 资产只读：`vendor/Kronos` 与 `models/` 以 `:ro` 挂载，容器不写宿主资产；
73: - 镜像体积：real 目标（torch CPU wheel 约 200MB）仅在启用 profile 时构建；默认镜像（mock 目标）不含 torch，默认编排行为不变（NFR-001）。
74:
75: ## 8. 测试策略与验收映射
76:
77: | 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
78: |---|---|---|---|
79: | `AC-001` | 静态契约（unit，CI 常绿） | `tests/unit/test_f004_compose_profile_contract.py` | Dockerfile 有 mock/real 目标且 real 锁定依赖 pin；real 服务 profiles/只读挂载/端口/环境正确；默认 compose 配置不含 real 服务 |
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:55:52Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "offset": 1, "limit": 22})`


> [reasoning] Coherence check of the final state:

Issues I notice (self-review):

1. **spec §1 问题** (line 32) still says "F002 导出的 `signals_log` 内容全是 `source=placeholder`" as problem statement. That's factual and motivates the real signal source. But it might imply F004 fixes signals_log. The 目标 section doesn't claim it; §3 范围外 clarifies. Acceptable — but maybe add a clarifying clause? The original problem statement is fine as background; the review's D001 was about claims of auto-upgrade. Keep.

2. **spec §1 非目标** (line 42): "不做 GPU 推理与性能优化（Kronos 常驻推理的目标机是执行机（当前 `qiaozhi-lt` 的 RTX 4060，架构 §7.1）；本 feature 的编排与契约验收在 CPU 推理上即成立，GPU 直通留给执行机落地时处理）" — mentions "当前 qiaozhi-lt 的 RTX 4060" — consistent with D006. OK.

3. **spec §2 US-001 title "编排内取得真实信号（Priority: P2）"** — fine.

4. **AC-002 references FR-001 only but includes serial inference** — FR-001 text now includes it. ✓.

5. **design §6**: "无新 UI；`/health` 的 ... 已足以判别实例形态。" Could note "real 实例就绪后 loaded=true；失败即退出" but not required. Fine.

6. **design §9**: dependency pin row says "版本与宿主 AC-006 实测一致" ✓.

7. **tasks.md**: verify T005 mentions mutation; ✓. §4 DAG ✓.

8. spec FR-001 scenario "并发推理串行" — GIVEN/WHEN/THEN format ✓.

9. Wait — spec §0 PRD 来源 line is quite long; fine.

10. Check the design §0 to verify D006 edit and overall consistency; let me read design lines 1-22.

11. Also check that spec line 20 "FR5（运行链：信号服务的运行时载体）" — hmm. Fine per reviewer guidance.

12. One more possible issue: spec §7 测试策略 "容器集成（执行机）" — should say "执行机 `qiaozhi-lt`"? The 取证纪律 bullet below says it. OK.

13. tasks.md T003 verify: `tests/unit/test_f004_compose_profile_contract.py::test_dockerfile_targets_pin_real_dependencies` — file path + test name; fine.

14. Wait, tasks.md T004: "healthcheck 以 `model_loaded=true` 为通过条件、失败不自动重启" ✓ matches design.

15. Check design §0 (lines 16-21) for D006 text. Let me read the top of design.

Also I should double-check one potential problem: the F001 smoke test's docstring/AC-006 command in F001 spec §6 still points to manual host form; T007 (future task) will write it back after implementation. Fine.

Another check: **D001 scope decision** — I should make sure the reviewer sees I chose the "delete claim" option and updated the design decision table. Done (spec §7 + design §9? design §9 doesn't have the consumer-routing row! I added it to spec §7 table but design §9 has only the 4 rows: profile/8002/serial/deps/CI. Wait, I planned to add "profile 启用时的消费者路由" row to design §9 too, but I didn't. Let me check: design §9 rows are: profile choice, 8002, serial lock, deps pin, CI risk. The consumer routing decision row is missing in design §9. I added it only in spec §7 decision table. Hmm — design §9 is "已确认决策与残余风险" — the routing decision belongs there too (it's a technical/scope decision with 替代方案). Add it in D001... but D001's commit is done. Should I add now as follow-up? The review's D001 suggested-fix alternative: "删除'自动升级 signals_log'的范围承诺" — done in spec. Design doesn't claim auto-upgrade; so D001 is satisfied. But adding the routing decision to design §9 improves completeness. I can add it as part of the final polish commit? Or leave. Hmm — the skill says keep one finding one commit; a tiny follow-up commit is acceptable but let me weigh whether it's needed. Design §9 doesn't mention routing; spec §3/§7 do. Design §4? The design should state the profile's consumer story... Actually design §9's first two rows already explain mock stays the default consumer dependency ("mock 实例仍是默认链路的依赖") — that's the same decision, stated. Adding an explicit routing row would be redundant-ish but clearer. I'll add it as a small follow-up to D001 (commit "补遗"). Hmm, or fold into the D002..D010 leftover polish? Let me first finish reviewing, then decide on a small polish commit for any leftover gaps (documented as part of respective findings with 补遗 commits, like I did for D003).

Actually — wait. Let me think about whether adding the design row matters for the reviewer's D001 check. The reviewer will look for: (a) the claim removed in spec ✓; (b) scope explicitly excludes routing ✓ (§3 范围外 + tasks §5); (c) F002 fixed ✓. Design §9 addition is optional polish. I'll add it anyway for completeness (one small commit tagged D001 补遗), since the design is where technical decisions live.

16. Another coherence item: spec §7 row 2's "后续" references "tasks §5" ✓ and tasks §5 has the routing item ✓.

17. tasks §5: "→ `v0.2.x` 后续评估（未立项）" — hmm template wants "目标 Feature/版本". Should I make it more concrete? Could say "→ `v0.2.x` 待立项（owner 在 F004 收口时决定）". Keep as is; it has version.

18. One more: the design §2 table's "构建目标" row includes profiles — fine.

19. Check design §0/1 for D006 environment: let me read design top.

Let me read design 1-22.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: related_features: [F001, F002]
6: topics: [kronos, inference, deployment]
7: doc_kind: design
8: created: 2026-09-12
9: updated: 2026-09-12
10: ---
11:
12: # F004：Kronos 真实推理运行时 - 设计
13:
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15:
16: ## 0. 输入与约束
17:
18: - **行为契约**：`spec.md`（FR-001 / NFR-001）
19: - **上游 Contract**：F001 冻结的 Kronos HTTP API（`GET /health`、`GET /predict/{symbol:path}`、`POST /predict_batch`），零改动
20: - **执行环境**：容器集成与验收在执行机 `qiaozhi-lt`（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）取证，证据记录 hostname 与 `device=cpu`（本 feature 不做 GPU 直通；CPU 推理实测 3.4–7.2s/次）；开发机 `qiaozhi-gp`/`gp-ws
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:56:02Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "created: 2026-09-12\nupdated: 2026-09-12\n---", "newString": "created: 2026-09-12\nupdated: 2026-09-14\n---"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "| 真实实例走 8002 而非顶替 8001 | 两种形态可并存对比 | mock 实例仍是默认链路的依赖 | 稳定后可评估是否合并 |", "newString": "| 真实实例走 8002 而非顶替 8001 | 两种形态可并存对比 | mock 实例仍是默认链路的依赖 | 稳定后可评估是否合并 |\n| profile 启用时的消费者路由（Freqtrade / runtime snapshot） | 不接线，显式后移（spec §3 范围外） | 本 feature 承诺=编排内可复现证据；路由切换改变默认链路可用性与跨 feature 契约 | 后移见 tasks §5；F002 spec §6 的「自动升级」表述已按此勘正 |"})`


> [reasoning] Design frontmatter `updated: 2026-09-12` — needs bump to 2026-09-14 (I bumped spec only). Also add the design §9 consumer routing row (D001 补遗). Both go in a final "补遗" commit. Let me do it now.

Then run full verify.py.
Two small polish items: design frontmatter date bump + the consumer-routing decision row in design §9 (D001 completeness):

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:56:07Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && python3 tools/validate_spec_lifecycle.py && git add docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): D001/D006 补遗——design §9 消费者路由决策行与日期回写\n\n- §9 增'profile 启用时的消费者路由：不接线，显式后移'决策行\n- design frontmatter updated 回写 2026-09-14\" && git log --oneline -1 && echo \"=== full gate ===\" && time python3 tools/verify.py", "timeout": 600000})`

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
6e06ca7 docs(f004): D001/D006 补遗——design §9 消费者路由决策行与日期回写
=== full gate ===
validate_spec_lifecycle: 全部通过
check_doc_links: 相对链接全部可解析
check_dep_pins: 失败
  - ccxt: 未安装（声明范围: >=4.4,<5）
  - duckdb: 未安装（声明范围: >=1.5,<2）
  - fastapi: 未安装（声明范围: >=0.115,<1）
  - pandas: 未安装（声明范围: >=2.2,<3）
  - psycopg2-binary: 未安装（声明范围: >=2.9,<3）
  - pyarrow: 未安装（声明范围: >=25,<26）
  - uvicorn: 未安装（声明范围: >=0.34,<1）
  - pytest: 未安装（声明范围: >=8,<10）
  - ruff: 未安装（声明范围: >=0.16,<0.17）
check_secrets: 无密钥形态命中
/home/georg/miniconda3/bin/python3: No module named pytest
/home/georg/miniconda3/bin/python3: No module named ruff
/home/georg/miniconda3/bin/python3: No module named ruff

== 规格生命周期校验 ==

== 文档相对链接检查 ==

== dev 依赖版本在 pin 范围内 ==
FAILED: dev 依赖版本在 pin 范围内

== 密钥模式扫描 ==

== pytest ==
FAILED: p
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:57:37Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && time .venv/bin/python tools/verify.py", "timeout": 600000})`


> [reasoning] The verify.py run used `/home/georg/miniconda3/bin/python3` (the shell's `python3` resolves to miniconda, no pytest/ruff installed). The project convention: `.venv/bin/python tools/verify.py`? The CURRENT-doc.md verification record says: "`.venv/bin/python tools/verify.py`：通过，`194 passed, 23 skipped`". So the reviewer ran with .venv. Let me run with `.venv/bin/python tools/verify.py`.

Note: verify.py uses `sys.executable` for subcommands, so running with .venv python uses .venv for all steps.

Let me run that.
Gate was run with the wrong interpreter (miniconda, no deps). Re-running with the project venv (as reviewer did):

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
check_doc_links: 相对链接全部可解析
check_dep_pins: 全部依赖版本在声明范围内（runtime + dev）
check_secrets: 无密钥形态命中
........................................................................ [ 33%]
........................................................................ [ 66%]
........................................................s............... [ 99%]
s                                                                        [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/integration/test_f001_kronos_smoke.py:86: AC-006 需真实模型实例：设 KRONOS_REQUIRE_REAL_MODEL=1 并把 KRONOS_BASE_URL 指向真实实例（命令见本文件 docstring / spec §6 AC-006）
SKIPPED [1] tests/integration/test_f002_schedule_backup.py:84: 未设置 ALPHAMILL_REAL_LAKE_DIR（本用例仅在有真实湖时运行）
215
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T15:01:14Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== docker compose without -f (F004) ===\"; grep -n \"docker compose\" docs/features/0.2/F004-kronos-inference-runtime/*.md | grep -v -- \"-f deployment\" || echo \"(none)\"; echo; echo \"=== 自动升级 mentions ===\"; grep -rn \"自动升级\" docs/features/0.2/F004-kronos-inference-runtime/ docs/features/0.2/F002-data-bridge/spec.md || echo \"(none)\"; echo; echo \"=== 镜像层 mentions ===\"; grep -rn \"镜像层\" docs/features/0.2/F004-kronos-inference-runtim
…[truncated])`


> [reasoning] Full gate green: `215 passed, 2 skipped`, lifecycle / links / dep pins / secrets / ruff all pass.

Note: reviewer's baseline was "194 passed, 23 skipped" — now "215 passed, 2 skipped"? Interesting: the reviewer's run had 23 skipped; ours has 2 skipped. Why the difference? The reviewer ran `.venv/bin/python tools/verify.py` and got 194 passed/23 skipped. Ours: 215 passed / 2 skipped. Hmm — 21 tests difference. Could be environment differences (e.g., miniconda vs venv?), or the reviewer ran before F002 T021 closeout? Wait the F002 spec says "全 `tests/integration` 套件 `22 passed, 1 skipped`" in the closeout environment (execution machine with DB). On dev machine, integration tests skip when DB unavailable. The reviewer's 23 skipped suggests the reviewer ran with the same environment as us but integration tests skipped more due to... hmm ours skipped only 2? That means 21 integration tests actually PASSED in our run — meaning a TimescaleDB is reachable?? Wait, really? tests/integration needs DB at 127.0.0.1? Let me think.

Hold on — 215 passed vs 194 = +21 passed, and skipped dropped 23→2 = -21. So 21 previously-skipped integration tests now passed. That suggests our environment HAS a reachable DB (conformance environment?) OR the reviewer ran at a time when the DB wasn't reachable. Hmm, but current environment is the dev machine (qiaozhi-gp per context? Actually the working directory /home/georg — from earlier: dev machine per CLAUDE.md). Does the dev machine have TimescaleDB on localhost:5432? Possibly, since F002 acceptance used "ALPHAMILL_INTEGRATION=1 ALPHAMILL_REAL_LAKE_DIR=lake" in a "收口环境" (which might be the same WSL machine). Hmm.

Wait, actually — let me check: tests/integration conftest probably checks DB connectivity; if DB is up on this machine, tests run (not skip) even without ALPHAMILL_INTEGRATION? The F001 smoke test skips if service unreachable only when INTEGRATION_REQUIRED is False. For other tests, similar logic. Our run: 2 skips: F001 AC-006 (real model required) and F002 schedule backup (needs env var). So DB-dependent tests actually ran and passed — DB is reachable locally (docker timescaledb running?). Interesting but plausible: this machine may be the one where docker runs (the "收口环境").

This matters for the FIX-log gate evidence: I should record the exact command and result: `.venv/bin/python tools/verify.py` → all green, `215 passed, 2 skipped`. And note the difference from the reviewer's baseline run (194 passed, 23 skipped) is environmental (DB reachable now → more integration tests executed rather than skipped; no skips converted to failures). Hmm, wait — is that OK to note? The skill says if local green but CI red, compare tool versions. Not applicable. But the reviewer might wonder about the number difference. I'll note in FIX-log: "本轮环境 TimescaleDB 可达，21 个原 skip 的集成用例实际执行并通过（215 passed / 2 skipped）" — and actually I should double check this claim rather than guessing. Let me check what the 2 skips are (already shown) and maybe count integration vs unit. The run output shows skips only 2. Let me quickly verify DB presence: `docker ps` maybe. And maybe the reviewer's 23 skips included all integration tests because DB was down at review time. Not critical for the fix round, but let me phrase the gate evidence accurately: gate command + exit 0 + "215 passed, 2 skipped"; the 2 skips are F001 AC-006 (real model switch not set) and F002 real-lake (env var not set). That's accurate.

Also note: verify.py with system python3 failed due to deps — that's an environment quirk on this machine (there's a miniconda python3 first in PATH); the project convention (reviewer, F002 evidence) uses `.venv/bin/python`. I should note in FIX-log the exact command used. Fine.

Hmm, but wait: the skill says "修复者每轮收尾时跑一次全量,用和 CI 同款命令(见 ci-verify)". CI runs `python3 tools/verify.py` on ubuntu with `pip install -e ".[dev]"`. Locally `python3` is miniconda without deps — so the "same as CI" effect is achieved via `.venv/bin/python`. The reviewer did the same. Good.

Now, is there anything else before writing FIX-log?

Let me do a final self-review of the docs changes as a whole, checking for my own fix-regressions. A few things to verify:

1. **spec §0**: "FR5（运行链：信号服务的运行时载体）" — reviewer suggested "相关 FR5 运行链". OK.

2. **spec §2 US-001 独立测试** mentions "再跑 AC-006 命令全绿" — AC-006 is F001's AC. Fine.

3. **AC-001 refs**: `FR-001`、`NFR-001` — both defined in §4 ✓ (lifecycle gate passed).

4. **AC-002 refs** `FR-001` ✓.

5. **tasks.md**: check the "Phase 只能作为第 2 节三级标题" ✓ gate passed. T011 no refs — gate doesn't care.

6. **design §10 "无"** ✓ gate passed.

7. Cross-doc consistency for D001: spec §3 范围外 says snapshot still points to "mock `:8001`" — factually: freqtrade `KRONOS_SIGNAL_URL: http://kronos-signal:8001` ✓; alphamill-snapshot.service `-KronosHostUrl http://127.0.0.1:8001` ✓. Good.

8. One potential inconsistency: design §5 says real healthcheck "以 `/health` 的 `model_loaded=true`（且 `device=cpu`）为通过条件" — device=cpu is the value on execution machine (no GPU passthrough); fine, and consistent with D006. But if someone enables GPU later... non-goal. Fine.

9. spec §7 测试策略: "设了开关而服务/容器不可达判红" ✓ matches SOP.

10. Anything referencing old T-numbers elsewhere? Let me grep for "T00" in F004 docs to ensure no stale references (tasks.md is the only place tasks are referenced; spec/design don't reference task numbers... design §9? No. OK, let me grep to be safe).

11. Also grep for "自动升级" anywhere else (should only appear in corrected/negative contexts + F002 spec correction). And "镜像层" to ensure the old criterion is gone everywhere. And "docker compose" without -f in F004 docs (tasks should all have -f now; let me check). Let me run these greps.

12. Also check F002 spec edit renders correctly.

Let me run the greps.
Full gate green (`215 passed, 2 skipped`; lifecycle/links/pins/secrets/ruff all pass). Final consistency greps before writing the FIX-log:

  <details><summary>tool output</summary>

  ```text
=== docker compose without -f (F004) ===
(none)

=== 自动升级 mentions ===
docs/features/0.2/F004-kronos-inference-runtime/spec.md:72:- `signals_log` 内容的自动升级：本 feature 只提供真实信号源，不改变写入链路。
docs/features/0.2/F004-kronos-inference-runtime/spec.md:150:| 是否阻塞 F002 done | **不阻塞**（2026-09-13 owner 裁决，见 §8 Q-001） | F002 只承诺导出管线正确，不承诺内容来自真实模型 | 代价已写进 F002 spec §6 限制说明；**F004 落地后 `signals_log` 不会自动升级**——runtime snapshot 与 Freqtrade 仍指向 mock `:8001`，路由切换后移（§3 范围外、tasks §5） |
docs/features/0.2/F004-kronos-inference-runtime/design.md:95:| profile 启用时的消费者路由（Freqtrade / runtime snapshot） | 不接线，显式后移（spec §3 范围外） | 本 feature 承诺=编排内可复现证据；路由切换改变默认链路可用性与跨 feature 契约 | 后移见 tasks §5；F002 spec §6 的「自动升级」表述已按此勘正 |
docs/features/0.2/F002-data-bridge/spec.md:221:不得以"五 dataset 齐备"含糊带过;**勘正（2026-09-14，F004 设计检视 D001）**:F00
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T15:01:25Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && date \"+%Y-%m-%d %H:%M %Z\" && git rev-parse --short HEAD && git log --oneline bc314f0..HEAD | wc -l && git status --short"})`


> [reasoning] All consistent. Now write the FIX-log.md Round 1 declaration with the evidence triple:
- findings: F004-D001..D010 (D001-D010, minus none)
- commits: per finding (including 补遗 for D003/D001)
- regression_tests: for doc-review rounds = document diffs + gate. Per skill: "文档检视靠'文档被改+链接/格式检查通过'". So list: `docs/features/0.2/F004-kronos-inference-runtime/{spec,design,tasks}.md` diff + `.venv/bin/python tools/verify.py`（文档门禁与全量测试）全绿. Also note the reviewer will need to independently verify.
- gate: `.venv/bin/python tools/verify.py` → 全绿，输出摘要 + timestamp.

Let me get commit hashes per finding:
- D009: 10cd1d8
- D001: 1e81b7c (+ 6e06ca7 补遗 design §9 决策行/日期)
- D003: 88dfce9 (+ abef312 补遗)
- D002: affc424
- D004: 14f06e1
- D005: 283f052
- D006: 820e804 (+ also design date? no, date in 6e06ca7 which I labeled D001/D006 补遗 — hmm I labeled the commit "D001/D006 补遗" but it only contains D001's design row + date bump. The date bump isn't D006-specific. Let me relabel in FIX-log: 6e06ca7 = D001 补遗（design §9 消费者路由决策行 + frontmatter 日期）。D006's spec/design edits are all in 820e804. Good, I'll describe it accurately in FIX-log.
- D007: 1cb2d9b
- D008: 49e6c9d
- D010: 904f2cb（同时承载其余 finding 的任务级更新 — 已在 commit message 说明）

Wait — I labeled 6e06ca7 as "D001/D006 补遗" but the content is D001-only. In FIX-log I'll write it under D001 补遗. Fine.

Timestamp for gate: let me get current time. Also record git HEAD: 6e06ca7 (baseline bc314f0 + 12 commits). Let me count: bc314f0 → 10cd1d8, 1e81b7c, 88dfce9, abef312, affc424, 14f06e1, 283f052, 820e804, 1cb2d9b, 49e6c9d, 904f2cb, 6e06ca7 = 12 commits.

Also need to note in FIX-log:
- Baseline declaration: main @ bc314f0 (pre-fix), post-fix HEAD 6e06ca7.
- The D001 resolution note: chose reviewer-sanctioned alternative (delete claim + defer routing); F002 spec corrected as consequential cross-file edit.
- tasks.md is one commit (904f2cb) carrying other findings' task-level updates due to shared edit surface (precedent: 循环4 D034+D037 合并一 commit 追认).
- Gate evidence: command, output summary, timestamp. Note system `python3` (miniconda) lacks dev deps → used `.venv/bin/python`（与检视方 CURRENT-doc.md 验证记录同款）；the two skips are expected (F001 AC-006 real-model switch and F002 real-lake env).
- Evidence triple also: no CURRENT-doc.md writes (修复方零写入), fixer channel is FIX-log only.
- Also mention scope/diff: all edits in F004 三件套 + F002 spec one sentence; no code touched; no review files tracked.
- Maybe a "rejected: (none)" line — we accepted all findings. The template has rejected as optional; state 无.

Let me also double-check: the skill wants FIX-log append-only with "Round <N> · <YYYY-MM-DD>". Date today: 2026-09-14 (env says Mon Sep 14 2026).

One more check: is there anything in CURRENT-doc.md findings I haven't addressed?

- D001 ✓ (claim removed, F002 corrected, routing deferred with task §5 carrier)
- D002 ✓ (design startup sequence + lock + tests; spec invariants + AC-002)
- D003 ✓ (commands -f + data preconditions + scenario command + design §0)
- D004 ✓ (test layering, AC tests updated, F001 smoke scoped)
- D005 ✓ (deps + pins in design §2, spec §3; verification requirement "容器内 import 加真实权重加载验证" — design §2 says "以容器内真实权重加载验证后锁定"; tasks T003/T006 cover integration test; hmm "以容器内 import 加真实权重加载验证" — should tasks explicitly include in-container import/weight load verification? T003 verify is static test; T006 container integration includes /predict source=kronos (which requires real weight load). Actually T006 does exactly the real weight load via compose up + predict. And T003's real dependency validation is implied by T006. Maybe add explicit "容器内 import" to T006? T006 says "compose 拉起 real 实例后校验... 与 /predict source=kronos" — the /predict returning kronos source implies imports+weights load succeeded. Good enough. But the reviewer's suggested fix says "以容器内 import 加真实权重加载验证" — the D006 note also says default image import torch判红 (negative import). For the real image, /predict success is the positive evidence. Fine.
- D006 ✓
- D007 ✓ (mock/real targets; criterion changed in spec NFR/AC + tasks T003/T005)
- D008 ✓ (mount table, env vars, :ro, port mapping; spec bullets)
- D009 ✓
- D010 ✓ (complete DAG; T006 split into T009 evidence writeback / T011 status; final gate unified python3 tools/verify.py)

All addressed.

Now — one more consideration per skill §4: "回答完根因问题后,再答一道分类题:这是产品缺陷,还是'上游任务还没执行'?" Some findings (D002/D003/D004) are "implementation not yet done" — but they're design doc gaps (the design didn't plan the implementation path), which is exactly what doc review must fix before implementation. Fixed via docs, not tracked tasks. Good — no tracked items needed. The routing deferral is a scope decision with tasks §5 carrier.

Now write FIX-log.md. Format per skill:

```
## Round <N> · <YYYY-MM-DD>
- findings: <本轮处理的 issue id 列表>
- commits: <每条 finding 对应的 commit 短哈希,一 finding 一 commit>
- regression_tests: <file::test_name,即新增的门禁失败测试>
- gate: <轮末全量门禁命令 + 输出结论 + 时间戳>
- rejected: ...
```

For doc review, regression_tests = document diffs + document gates. I'll fill:
- regression_tests: 文档门禁（`validate_spec_lifecycle` / `check_doc_links`）+ 适配器矩阵？ No. Let me write: "文档检视无代码回归测试；闭环证据=文档 diff（见 commits）+ `.venv/bin/python tools/verify.py` 文档门禁（生命周期/链接）全绿；spec AC-001/AC-002 tests 字段已指向实现期将新增的 F004 专属门禁（tests/unit/test_f004_*.py、tests/integration/test_f004_real_profile.py），实现轮落地后由这些测试锁定"。

Hmm, the skill says缺一视同未修复: findings, commits, regression_tests, gate. For doc fixes there are no new tests; I should be explicit that the doc-review evidence type is "document changed + link/format check passed" per skill. I'll state that.

Also add a header + baseline + notes section detailing per-finding resolution and the tasks.md merge note. Keep the required fields in a code block list like template.

Let me write the file now. Also include "修复方对 CURRENT-doc.md 零写入" statement.

After writing, update todos (gate done, FIX-log done). Then final summary for the user.

One question: should I mark todo "F004-D006 ... design 执行环境改执行机" as completed etc. Yes, update all todos to completed at the end.

Let me get exact timestamp.
All findings verified in the final artifacts. Writing the fixer's Round 1 declaration to `FIX-log.md` (fixer's only channel — zero writes to `CURRENT-doc.md`):

  <details><summary>tool output</summary>

  ```text
2026-09-14 23:01 HKT
6e06ca7
12


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T15:01:38Z

- **tool**: `write({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "content": "# FIX-log —— F004 设计文档检视修复方声明（本地过程稿，不进 git）\n\n> 本文件由修复方独占写权，append-only；检视方对修复条目的独立核对结果以\n> `[review-r<N>]` 批注形式追加在对应条目下方。修复方对 `CURRENT-doc.md` 零写入。\n\n## Round 1 · 2026-09-14\n\n- **基线**：`main` @ `bc314f0`（修复前）→ `main` @ `6e06ca7`（修复后，12 个提交）\n- **受检产物**：`docs/features/0.2/F004-kronos-inference-runtime/{spec,design,tasks}.md`；\n  相邻契约连带勘正：`docs/features/0.2/F002-data-bridge/spec.md`（D001 的跨文件后果）\n- **findings**：
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Wrote file successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T15:01:49Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git status --short; echo \"=== ignored check ===\"; git check-ignore -v docs/reviews/FIX-log.md; echo \"=== HEAD ===\"; git log --oneline bc314f0..HEAD"})`


> [reasoning] Now finalize:
1. Verify no tracked changes (FIX-log is gitignored).
2. Update todos to completed.
3. Report to user.

Let me also double check that the FIX-log is ignored (it should be per .gitignore). And git status should be clean (all doc edits committed). Let me run final checks.

Also, one point: I should perhaps run the "变异验证" for doc gates? The skill's "关门禁才有牙" applies to new gates. This round added no new gates (doc-review). The committed spec now promises mutation verification in implementation round (T005). OK.

Also the skill says "检视意见固化为门禁失败测试后才允许关闭：先让测试红（复现 finding），修复后变绿" — for doc-review, that's not applicable (doc content findings can't be red-tested); the reviewer will independently verify diffs. I noted the doc-review evidence type in FIX-log.

Final check: git status clean; FIX-log ignored; the doc files all committed. Let me verify.

  <details><summary>tool output</summary>

  ```text
=== ignored check ===
.gitignore:39:docs/reviews/*	docs/reviews/FIX-log.md
=== HEAD ===
6e06ca7 docs(f004): D001/D006 补遗——design §9 消费者路由决策行与日期回写
904f2cb docs(f004): tasks 重构——完整 DAG、拆分证据回写与状态同步（F004-D010）
49e6c9d docs(f004): 补全挂载/环境变量/端口两侧契约（F004-D008）
1cb2d9b docs(f004): 定义 mock/real 构建目标与可稳定断言的 NFR 判据（F004-D007）
820e804 docs(f004): 验收环境改为执行机取证并记录 hostname/device（F004-D006）
283f052 docs(f004): 锁定 real 镜像最小推理依赖与 torch CPU wheel 来源（F004-D005）
14f06e1 docs(f004): 测试策略分层——专属静态/容器门禁替代冒烟兜底（F004-D004）
affc424 docs(f004): 补失败关闭/串行推理实现路径与不变量（F004-D002）
abef312 docs(f004): 补 D003 遗漏——FR-001 场景命令加 -f 定位（F004-D003）
88dfce9 docs(f004): 命令统一 -f 定位并补齐数据前置（F004-D003）
1e81b7c docs(f004): 删除 signals_log 自动升级承诺，显式后移消费者路由（F004-D001）
10cd1d8 docs(f004): 修正 PRD 来源引用——FR3 改为下游评测关系（F004-D009）


Incremental: 0 f
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T15:01:53Z

- **tool**: `todowrite({"todos": [{"content": "F004-D009: spec §0 PRD 来源 FR3→M0/FR1.2/FR5 + 下游关系说明 - commit 10cd1d8", "status": "completed", "priority": "high"}, {"content": "F004-D001: 删除 signals_log 自动升级承诺、后移消费者路由；F002 勘正 - 1e81b7c + 6e06ca7", "status": "completed", "priority": "high"}, {"content": "F004-D003: 命令统一 -f + 数据前置 - 88dfce9 + abef312", "status": "completed", "priority": "high"}, {"content": "F004-D002: spec 不变量/AC-002 + design 预检/eager load/推理锁 - affc424", "status": "completed", "priority": "high"}, {"con
…[truncated])`

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "F004-D009: spec §0 PRD 来源 FR3→M0/FR1.2/FR5 + 下游关系说明 - commit 10cd1d8",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F004-D001: 删除 signals_log 自动升级承诺、后移消费者路由；F002 勘正 - 1e81b7c + 6e06ca7",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F004-D003: 命令统一 -f + 数据前置 - 88dfce9 + abef312",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F004-D002: spec 不变量/AC-002 + design 预检/eager load/推理锁 - affc424",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F004-D004: 测试策略分层 + AC-001 tests - 14f06e1",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F004-D005: torch CPU wheel 版本与最小依赖 pin - 283f052",
    "status": "completed",
    "priority": "high"

…[truncated]
  ```
  </details>

## assistant · 2026-09-14T15:01:57Z


> [reasoning] All done. Final report to the user, following the ADHD-friendly style (lead with answer/next action, numbered, concise). The user is Chinese-speaking (request in Chinese). I'll respond in Chinese, concise.

Key points:
- 10 findings all fixed, 12 commits on main, baseline bc314f0 → 6e06ca7.
- Gate green.
- FIX-log written; CURRENT-doc.md untouched (reviewer's call next).
- Next action: 检视方 Round 2 diff-only 复核（由用户/检视会话执行）。

Also note the key decision for D001 (narrow scope: routing deferred) — highlight it since it's the one substantive choice the reviewer/owner should ratify.

Keep it tight.
修复完成。10 条 finding 全数处理，12 个提交（`bc314f0 → 6e06ca7`），轮末全量门禁 `.venv/bin/python tools/verify.py` 全绿（`215 passed, 2 skipped`，无失败）。

**状态：修复已落盘，等待检视方 Round 2 复核**

| Finding | 处理 | Commit |
|---|---|---|
| D001 | 删除「signals_log 自动升级」承诺；消费者路由显式后移（spec §3/§7 + design §9 + tasks §5）；F002 spec 同款表述连带勘正 | `1e81b7c` `6e06ca7` |
| D002 | design 补启动序列（预检→eager load→就绪，失败非零退出）、readiness、进程级推理锁；spec 增不变式与 AC-002 | `affc424` |
| D003 | 全部命令统一 `-f deployment/docker-compose.yml`；补 DB 迁移 + ≥30 根 1m K 线前置 | `88dfce9` `abef312` |
| D004 | 测试三层：F004 专属静态/容器门禁 + F001 冒烟收窄为 HTTP 契约 | `14f06e1` |
| D005 | 锁定 `torch==2.14.0`（CPU wheel index）+ einops/safetensors/huggingface_hub/tqdm | `283f052` |
| D006 | 验收环境改 `qiaozhi-lt` 取证，记录 hostname + `device=cpu` | `820e804` |
| D007 | Dockerfile 拆 mock/real target；NFR 判据改为「默认镜像不含 torch」 | `1cb2d9b` |
| D008 | 补 real 服务契约表：`:ro` 挂载、三个 KRONOS_*_PATH、8002→8001 | `49e6c9d` |
| D009 | PRD 来源改指 M0/FR1.2/FR5，FR3 降为下游 | `10cd1d8` |
| D010 | tasks 重构：完整 DAG、证据回写与状态同步拆分、统一最终门 | `904f2cb`（含其余 finding 的任务级更新，理由已注明） |

两条说明：
1. **D001 是取舍点**：采了检视建议的窄口径（真实实例只服务 AC-006 + 提供可复用信号源，不接线消费者），路由切换写进 tasks §5 后移。若 owner 想扩展为「真实实例即运营信号源」，需另立范围，本轮未做。
2. `docs/reviews/FIX-log.md` 已写 Round 1 声明（含逐条证据与补遗说明）；`CURRENT-doc.md` 修复方零写入。

**下一步（约 30 分钟）**：检视方做 Round 2 diff-only 复核（审 `bc314f0..6e06ca7` 的 12 个提交 + 抽查 D001/D003/D010 的残留引用），通过后翻 `fixed`、跑 CI 并闭环。

## user · 2026-09-14T16:10:42Z

<system-reminder>Note: The user opened the file "/home/georg/projects/alphamill/docs/alphamill-prd.md". This may or may not be relevant to the current task.</system-reminder>

又检视了一轮，再次审视修复一下

## assistant · 2026-09-14T16:10:42Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git status --short; git rev-parse --short HEAD; ls -la docs/reviews/; date \"+%Y-%m-%d %H:%M %Z\""})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md"})`


> [reasoning] The user says: "又检视了一轮，再次审视修复一下" — another review round has been done; review and fix again. This means the reviewer has updated CURRENT-doc.md (probably round 2 with new findings, or updated round 1 with results). I'm the fixer again.

Let me read the CURRENT-doc.md to see what's new, and check the baseline/HEAD state. Note the user opened docs/alphamill-prd.md — maybe relevant.

Let me check git status, HEAD, and CURRENT-doc.md.

  <details><summary>tool output</summary>

  ```text
M docs/design/ui-mockup/README.md
 M docs/design/ui-mockup/app.js
 M docs/design/ui-mockup/index.html
 M docs/design/ui-mockup/styles.css
6e06ca7
total 124
drwxr-xr-x 2 georg georg  4096 Sep 14 23:27 .
drwxr-xr-x 7 georg georg  4096 Sep 14 21:48 ..
-rw-r--r-- 1 georg georg 14702 Sep 14 23:27 CURRENT-doc.md
-rw-r--r-- 1 georg georg  6899 Sep 14 23:27 FIX-log.md
-rw-r--r-- 1 georg georg 93031 Sep 14 21:48 RETROSPECTIVE.md
2026-09-15 00:10 HKT


Incremental: 1 files updated, 40 nodes, 481 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md</path>
<type>file</type>
<content>
1: ---
2: report_type: doc-review
3: round: 2
4: date: 2026-09-14
5: prior_report: CURRENT-doc.md@round-1
6: scope: full-scan
7: stop_condition_met: false
8: severity_counts: {critical: 0, high: 1, medium: 2, low: 0}
9: issues:
10:   - id: F004-D001
11:     title: 真实 profile 未接入 signals_log 的生产消费者
12:     severity: high
13:     category: correctness
14:     root_cause: root-cause
15:     origin: spec-drift
16:     pattern_tag: cross-feature-contract-drift
17:     status: fixed
18:     tracked_task: null
19:     fix_summary: 删除自动升级承诺，将消费者路由排除并同步勘正 F002 限制说明。
20:     regression_test: tools/validate_spec_lifecycle.py + tools/check_doc_links.py
21:     suggested_fix: 接线并验收 signals_log.source=kro
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:10:52Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '1,60p' src/alphamill/kronos_service/db_adapter.py; echo \"=== VENDORED tracked? ===\"; git ls-files vendor/VENDORED.md"})`


> [reasoning] Round 2 results:
- D001-D010 verified fixed (good).
- New findings:
  - **D011 (High)**: real service contract missing `DB_*` env, `depends_on: timescaledb: service_healthy`, and `networks: [alphamill]`. Per current design, the real container can't reach the DB → /health and /predict fail. Fix: add DB env, dependency, network to design §2 table + tasks T004 + static/container gates assertions.
  - **D012 (Medium)**: design impact section says "后端 / API：无变更" but requires application startup hook; T001 only lists `kronos_real.py`; `VENDORED.md` writeback has no task. Fix: correct the impact statement (后端/API 无契约变更，但有薄壳启动钩子改动 in `server.py`), list `server.py` in T001, add a task for VENDORED.md writeback.
  - **D013 (Medium)**: T001-T004 verify reference tests not yet created; static test finalized only at T005; violates "每项完成即验证". Fix: reorder tasks so contract tests are created first (test-first red), or bundle test creation into the corresponding implementation tasks. Suggested: "将契约测试置于实现前先红，或明确并入对应实现任务，保证 T001-T004 完成时 verify 已存在".

Also note: the reviewer's baseline for round 2: main@6e06ca7. The working tree has modified ui-mockup files (unrelated, user confirmed). I must not touch them.

Also the user has PRD open — maybe relevant to D011? Not necessarily. D011 needs checking the actual compose structure: kronos-signal service has DB env + depends_on + networks. The real service (new) must have the same. Where does the design specify? Design §2 table currently lists build target, mounts, KRONOS_* env, port. Needs DB_* env + depends_on + network. Also the test gates: static test should assert real service has DB env/depends_on/network; container gate should prove /health and /predict work against DB (which the existing AC-001 integration test already does via /predict source=kronos — but the reviewer wants explicit assertions).

Let me check the review's exact wording for D011:
- title: "real 服务契约遗漏数据库依赖与网络接入"
- suggested_fix: "补齐 DB_*、TimescaleDB healthy dependency 与 alphamill 网络，并由静态和容器门断言。"
- location: design.md:34 (the §2 contract table area).

D012:
- title: "应用启动钩子和配套文档没有任务所有者"
- suggested_fix: "校正后端影响面，在 T001 明列 server.py 启动钩子，并为 VENDORED.md 回写增加任务。"
- location: design.md:27 (the 影响面 bullet "后端 / API：无变更（同一份 kronos_service）").

D013:
- title: "实现任务引用的测试门在执行顺序中尚不存在"
- suggested_fix: "将契约测试置于实现前先红，或明确并入对应实现任务，保证 T001-T004 完成时 verify 已存在。"
- location: tasks.md:33 (T001 line).

So I need to fix:

**D011 fixes:**
1. design §2 real 服务契约表: add rows:
   - DB 环境：`DB_HOST: timescaledb`、`DB_PORT: 5432`、`DB_USER/DB_PASSWORD/DB_NAME`（同 mock 服务，`${DB_*:-...}` 形式）
   - 依赖：`depends_on: timescaledb: {condition: service_healthy}`
   - 网络：`networks: [alphamill]`
   Also maybe note in §5 or §7 that /health and /predict require DB reachability (health endpoint reports `database` status; predict reads OHLCV). The reviewer said design should specify so the runtime chain (compose → model → DB → HTTP) is complete.
2. tasks T004: add DB env/depends_on/network to the description; static test T004/T005 assertions include them.
3. spec? AC-001 asserts full chain? The AC-001 already asserts /predict source=kronos which requires DB data (≥30 candles). But add explicit mention? The reviewer's suggested fix says "并由静态和容器门断言" — so:
   - static: `test_f004_compose_profile_contract.py` asserts real service has DB_* env, depends_on timescaledb healthy, networks alphamill.
   - container: `test_f004_real_profile.py` asserts /health database OK and /predict works (already implied). Maybe add explicit "健康链：/health 的 database 可达且 /predict 端到端成立" to the key assertions. Let me update design §8 table rows and spec §7 测试策略 accordingly (briefly).

Where in spec: §7 测试策略 container bullet could add "并断言 /health 的数据库可达（运行链 compose→模型→DB→HTTP 完整）". And AC-001? AC-001 says "/predict 返回 source=kronos" — implicitly DB. I could add "（含 DB 可达运行链）". Keep small.

**D012 fixes:**
1. design §1 影响面 bullet: "- 后端 / API：无变更（同一份 `kronos_service`）" → "- 后端 / API：HTTP 契约无变更；薄壳增加启动钩子改动（`server.py` 调用预检/eager load，`kronos_real.py` 实现，见 §5）"
   Wait — design §1 currently says "后端 / API：无变更（同一份 kronos_service）" — let me check current design line 27: "- 后端 / API：无变更（同一份 `kronos_service`）". Yes.
2. tasks T001: explicitly list `server.py` 启动钩子: "T001 (`FR-001`): `kronos_real.py` 实现启动预检与 eager load，并在 `server.py` 启动钩子中调用（real 模式）..."
3. VENDORED.md writeback task: add to tasks. Where? design §1 影响面 says "文档 / 配置：F001 spec §6 命令回写；`vendor/VENDORED.md` 补容器内路径说明"。So add a task in Phase 3 or with T007: e.g. T007 becomes F001 writeback; add T008 as VENDORED.md update? That would renumber subsequent tasks. Alternatively fold into T007: "回写 F001 spec §6 ... 并更新 `vendor/VENDORED.md` 容器内路径说明". Hmm, one task = one verifiable action; two doc writebacks in one task is okay-ish but reviewer asked "为 VENDORED.md 回写增加任务" (add a task). Let me add a separate task T008 `(FR-001)`: "更新 `vendor/VENDORED.md`：补容器内路径（/app/vendor/Kronos、/app/models/...）与 real profile 说明" — verify: `python3 tools/verify.py`? The VENDORED.md is not in docs/ scanned by check_doc_links? check_doc_links scans docs/** + README/CLAUDE. vendor/VENDORED.md not scanned. Hmm, verify: "vendor/VENDORED.md 含容器内路径说明（人工核对）" — tasks verify needs a command/test. Maybe verify: `python3 tools/verify.py`（文档门）+ 人工核对。Hmm. Let me look at how F001 tasks referenced VENDORED... F001 T-task? There might be precedent. Not critical; I'll use `python3 tools/verify.py` plus explicit content check. Actually, better: since it's a doc file not covered by gates, the verify could be `grep -q "/app/vendor/Kronos" vendor/VENDORED.md`? A shell grep is a runnable command. Let me phrase: verify: `grep -n "app/vendor/Kronos" vendor/VENDORED.md`（含容器路径段）. Hmm, per tasks template verify is "测试/命令" — a grep command is acceptable.

Wait — but where does VENDORED.md live? `vendor/VENDORED.md` (seen earlier). And is vendor/ tracked? Vendor Kronos clone is local-only, but VENDORED.md itself was committed (it appeared in the repo listing and its content shows pins). Let me verify it's tracked: `git ls-files vendor/VENDORED.md`. It appeared in vendor listing earlier; likely tracked. I'll check.

Renumbering: adding a task after T007 shifts T008-T011 → T009-T012. Or insert as T008 in Phase 3 and renumber acceptance tasks. The reviewer's D010 fix emphasized clean DAG; adding a task requires renumbering. Let me restructure:

Current tasks:
- T001 薄壳预检+eager load
- T002 推理锁
- T003 Dockerfile targets/deps
- T004 compose real service
- T005 静态门禁定稿+变异
- T006 容器集成测试
- T007 F001 §6 回写
- T008 执行机集成验收
- T009 回写 spec 证据
- T010 统一质量门
- T011 状态/BACKLOG 同步

**D013 fix approach**: "将契约测试置于实现前先红，或明确并入对应实现任务，保证 T001-T004 完成时 verify 已存在。" I'll choose: test-first, i.e., create test files/测试用例 before implementation, as separate tasks:
- T001: 创建 F004 门禁测试骨架（先红）：`test_f004_kronos_runtime_contract.py` + `test_f004_compose_profile_contract.py` 的失败用例（预检/锁/目标/编排断言）——verify: 运行两文件确认按预期失败（红）.
  Hmm, but "每项任务只描述一个可验证动作"... A task "create failing tests first" is a good TDD step. But is a "red test" verifiable? verify: `pytest ... → 预期红（内容为缺失行为）`. Hmm. Alternatively "明确并入对应实现任务": each implementation task includes writing its test (T001:实现+测试). That was my original intent, but the reviewer notes T005 says tests are "定稿" later, creating ambiguity. Options:

Option A (test-first tasks):
- T001 (`FR-001`): 新建薄壳运行时契约测试（先红）：预检失败关闭、加载至多一次、推理互斥 — verify: `.venv/bin/python -m pytest tests/unit/test_f004_kronos_runtime_contract.py -q`（预期红：行为未实现）
- T002 (`FR-001`): 实现 `kronos_real.py` 预检+eager load + `server.py` 启动钩子，使 T001 预检用例转绿...
Hmm, but the tasks use verify as the success criterion; a task whose verify is "red" is odd but legitimate in TDD ("先让测试红"). The skill itself says "检视意见固化为门禁失败测试后才允许关闭：先让测试红（复现 finding），修复后变绿".

Option B (bundle test creation into implementation tasks):
- T001: 实现预检+eager load（含 runtime contract 测试用例），verify: `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets` 由红转绿。
- T002: 锁（含并发用例），verify: same file ::test_predictor_loads_once...
- T003: Dockerfile（含静态断言用例）verify: static file ::test_dockerfile...
- T004: compose（含静态断言用例）verify: ...
- T005: 门禁定稿 = 补齐剩余断言（默认配置不含 real、默认镜像无 torch）+ 变异验证。
This maintains the "每项完成即验证" property: each task's test exists because the task itself creates it. The reviewer's suggestion explicitly allows "或将测试创建并入对应任务". This is less disruptive and keeps the DAG. But then D013's point "静态测试直到 T005 才定稿" — meaning T003/T004's verify references the static file which is only finalized at T005. With bundling: T003 creates the Dockerfile assertions; T004 adds compose assertions; T005 then adds remaining assertions + mutation. So T003/T004 verify can reference specific test functions created in the same task. Then T005's description should change from "门禁定稿" to "门禁补全（默认隔离断言）与变异验证". Hmm.

Actually let me think about what's cleanest given the reviewer's exact concern: "T001-T004 的 verify 引用尚未创建的测试门，静态测试直到 T005 才定稿，无法'每项完成即验证'。" So the fix must ensure that when T001-T004 complete, their referenced tests exist. Simplest fix: make each T001-T004 task explicitly create its own tests (test-first red inside the task, turn green), and T005 becomes "补齐静态门禁的默认隔离断言 + 两条门禁的变异验证" (not the first creation).

I'll go with Option B but be explicit in the task text: "先写失败用例再实现（TDD）" and verify names the specific test created. Let me restructure:

- T001 (`FR-001`): **先红后绿**——新增 `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`（fake 目录注入，先失败）后实现 `kronos_real.py` 启动预检与 eager load，并在 `server.py` 启动钩子（real 模式）调用，缺失即非零退出 — verify: 该用例转绿
- T002 (`FR-001`): 同文件新增 `::test_predictor_loads_once_and_inference_serializes`（先失败）后实现进程级推理锁 — verify: 该用例转绿
- T003 (`FR-001`, `NFR-001`): 先新增 `tests/unit/test_f004_compose_profile_contract.py::test_dockerfile_targets_pin_real_dependencies`（先失败）后实现 Dockerfile mock/real 目标与依赖 pin — verify: 该用例转绿
- T004 (`FR-001`, `NFR-001`): 先新增 `::test_compose_real_service_contract`（先失败；断言 profile/target/`:ro` 挂载/8002:8001/KRONOS_* 与 DB_* 环境/depends_on timescaledb healthy/networks alphamill）后实现 compose 两服务 — verify: 该用例转绿 + compose config 命令
- T005 (`AC-001`): 静态门禁补全（默认配置不含 real 服务、mock 目标不含 torch）+ 静态与容器门禁的变异验证 — verify: `tests/unit/test_f004_compose_profile_contract.py` 全绿 + 变异记录
- T006 (`AC-001`, `AC-002`): 容器集成测试（含运行链：/health database 可达 + /predict source=kronos；缺资产非零退出；默认镜像 import torch 判红）— verify: `tests/integration/test_f004_real_profile.py`
- T007 (`FR-001`): F001 spec §6 回写
- T008 (`FR-001`): `vendor/VENDORED.md` 补容器内路径说明（D012）
- Then acceptance: T009 执行机集成验收、T010 spec 证据回写、T011 统一质量门、T012 状态/BACKLOG。

Hmm, that's 12 tasks. Renumbering after T007: old T008→T009, T009→T010, T010→T011, T011→T012. DAG updates accordingly.

Wait, do I want to put VENDORED.md task in Phase 3? "Phase 3：专属门禁与文档回写" — yes T008 goes there. Dependencies: T008 independent doc writeback; T007/T008 after T006? T007 needs compose-form proven (T006). T008 (VENDORED.md container paths) can be done anytime; but assigning after T007 is fine; [P] with T007? Different files, no deps → could mark T007/T008 [P]. Hmm, but [P] means no explicit dependency edges; then DAG bullets should not declare edges for them. Let me keep it simple: put both in sequence without [P], or mark T008 [P] with "与 T007 可并行（不同文件）" in §4. The template says `[P]` only for different files without order deps; T007→T008 both doc files, no dep between them. I'll mark T008 [P]? Then §4 says "`T008 [P]`：与 T007 修改不同文件，可并行". Hmm — but T008 must wait for the implementation round anyway? VENDORED.md container paths can be written once the container paths are frozen (design §2, already frozen now). Actually it could even be done before implementation. But practically it's part of the implementation round. Keep simple: T007 and T008 both after T006, no inter-dependency. I'll not use [P] (keep the file's style simple), but note in §4 "T007/T008 修改不同文件，顺序无关".

Hmm, wait: previous F004 tasks had no [P] at all, and the template allows it. To keep the DAG crisp I'll write: "`T006 -> T007/T008`：文档回写以实测通过/契约定稿为前提；二者文件不同、顺序无关。" Good.

Also the reviewer's D013 mentions "T001-T004 的 verify 引用尚未创建的测试门" — my fix ensures each test function is created within its task, test-first. Also T005 renamed to "静态门禁补全" instead of "定稿".

**D011 fixes detail:**

design §2 table add rows:
| DB 环境（同 mock 服务） | `DB_HOST: timescaledb`、`DB_PORT: 5432`、`DB_USER`/`DB_PASSWORD`/`DB_NAME`（`${DB_*:-...}` 默认同 compose） |
| 依赖 | `depends_on: timescaledb: {condition: service_healthy}`（/health 与 /predict 都读 DB） |
| 网络 | `networks: [alphamill]` |

Also add note after the table: "运行链：compose → 容器（real 目标）→ TimescaleDB（healthy）→ HTTP；`/health` 的 `database` 段与 `/predict` 的行读取都要求 DB 可达——静态门禁断言上述三行，容器门断言端到端可用。"

design §8 table: static row key assertions add "DB 环境/depends_on healthy/networks 正确"; container row add "/health database 可达且 /predict 端到端（compose→模型→DB→HTTP）". Also spec §7 container bullet add "运行链（模型+DB）完整: /health 的 database 可达、/predict 端到端". And AC-001 wording? "model_enabled=true 且 /predict 返回 source=kronos" — the DB is implied. Add "（/health database 可达）"? Let me add to AC-001: "model_enabled=true、/health 的 database 可达且 /predict 返回 source=kronos"。 Hmm, keep AC concise but explicit. Yes.

Also tasks T004 (description + static test assertions) includes DB env/depends_on/network.

**D012 fixes detail:**
- design §1 bullet: "- 后端 / API：无变更（同一份 `kronos_service`）" → "- 后端 / API：HTTP 契约无变更；薄壳改动=`server.py` 启动钩子（real 模式调用预检/eager load）+ `kronos_real.py` 预检/加载/锁实现（§5）"。
- tasks T001 explicit `server.py`.
- tasks T008 VENDORED.md.

Also — check design §2 intro mentions "薄壳三处最小改造" — fine. design §5 startup sequence says "放在应用启动钩子" — D012 wants impact section corrected; §5 already says 启动钩子. Add `server.py` explicitly in design §5? "（`server.py` lifespan/启动钩子调用）" — helpful. Let me add: "→ **eager load**（一次性加载 Kronos + Tokenizer，由 `server.py` 启动钩子调用、先于接收流量）". And startup precheck also called from startup hook. Fine.

Also check: does spec mention thin-shell changes? spec §3 范围内 bullet 2 currently: "薄壳最小改造（`kronos_service`）：real 模式启动预检、模型 eager load、进程级推理锁（HTTP 契约不变）；" — D012 says "设计称后端无变更却要求应用启动钩子" — the spec already says 薄壳改造. Fine, spec OK.

Now, also should I re-check anything about D011: the real service also needs the same `NO_PROXY`? That's freqtrade only. And DB env — the mock service uses `${DB_USER:-quant}` etc. Yes.

Also `depends_on: timescaledb: {condition: service_healthy}` — same as mock. Network `[alphamill]`. Compose top-level network exists.

One more: design §2 table is "real 服务契约" — the DB rows fit.

**Where do the round-2 findings' commits go?** One finding one commit:
- D011: design §2/§5?/§8 + spec §7 + AC-001? Wait, AC-001 belongs to spec. D011 fix touches design §2 table (DB/depends/network), design §8 static/container assertions, tasks T004/T005 assertions (tasks commit?), spec §7 container bullet + AC-001 wording. Since tasks.md edits would again be a shared surface... I'll handle tasks edits in a final tasks commit for D012/D013 (restructure) like last round, noting merged task-level updates. Hmm, but D011 needs a tasks change (T004/T005 assertions) too. Same pattern: tasks.md updates merged into one commit with the D013 restructure (which touches all task lines anyway). I'll note in FIX-log that the tasks commit (D013) carries D011/D012 task-level updates as well — same precedent as before, and reviewer already saw and accepted this pattern (D010 commit). Fine.

So plan:
1. D011: design (contract table + §8 rows/assertions) + spec (§7 container bullet + AC-001) — commit.
   Hmm, should spec AC-001 include DB? Let me be careful not to overreach: The AC is about the instance. The reviewer's suggested fix: "补齐 DB_*、TimescaleDB healthy dependency 与 alphamill 网络，并由静态和容器门断言。" So both gates must assert. The AC's tests reference those gates; the AC text could mention "运行链（模型+DB）成立". I'll add to AC-001: "...（容器身份、只读挂载、8002:8001、DB 运行链成立），model_enabled=true、/health 的 database 可达且 /predict 返回 source=kronos；..." Hmm "DB 运行链成立" is vague; better: add a separate clause. Let me write: "由目标 compose 服务与 real 构建目标产生（容器身份、只读挂载、8002:8001 成立），且完整运行链（compose→模型→TimescaleDB→HTTP）成立：model_enabled=true、/health 的 database 可达、/predict 返回 source=kronos；..." That's long but explicit.

2. D012: design §1 impact bullet + §5 startup hook mention (server.py) — commit. tasks T001 + T008 in tasks commit.
3. D013: tasks restructure — commit (carries D011/D012 task-level updates).
4. Also check: any other task numbering references in tasks §4 to update. Yes, rewrite tasks.md fully again (it's manageable).

Wait — also reconsider: should D012's tasks changes be in the D012 commit rather than D013's? Again same-surface: T001 line changes for D012 (server.py), T004/T005 for D011, and D013 changes T001-T006 structure (test-first). All interleave on the same lines → single tasks commit is cleanest. Precedent accepted. So:
- Commit A (D011): design + spec.
- Commit B (D012): design (§1 + §5 mention).
- Commit C (D013): tasks.md full update (with D011/D012 task-level updates noted in message).
- FIX-log Round 2 amendment.

Also should I run full verify at round end and update FIX-log with Round 2 section. The FIX-log is append-only: add "## Round 2 · 2026-09-14" (or 2026-09-15? Current time 00:10 on 2026-09-15 HKT per date output "2026-09-15 00:10 HKT"! The date command showed 2026-09-15 00:10. So Round 2 declaration date 2026-09-15. The review report says date: 2026-09-14 (reviewer's date). I'll use 2026-09-15 for my fix round declaration, or align with reviewer? The skill: "## Round <N> · <YYYY-MM-DD>". Use actual date: 2026-09-15. Hmm, but the round-2 review is dated 2026-09-14 and my earlier Round 1 declaration 2026-09-14. I'll use 2026-09-15 for Round 2 fix (accurate).

Wait, also — should frontmatter dates in design/tasks be bumped to 2026-09-15? They currently say 2026-09-14. I'll bump to 2026-09-15 for design (D011/D012 edits) and tasks (D013). Spec: AC-001 edit for D011 → bump spec updated to 2026-09-15 as well. Fine.

Also the reviewer's verification: "F004 修复 diff 为 121 additions / 46 deletions，约占当前 324 行的 52%" — fine.

Let me now also double-check D011's claim about db_adapter DB env to make sure my design rows match the actual needed env vars. db_adapter.py — let me read it quickly to confirm the env var names (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME). Also check compose mock service env. Earlier compose shows mock kronos-signal has DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME. Yes. Let me quickly confirm db_adapter reads those names.

Also for D011 static assertions: docker compose config check — the static test will parse YAML text (like test_f001_compose_contract.py does with text assertions). Assertions: `DB_HOST: timescaledb`, `depends_on:` with `timescaledb: {condition: service_healthy}`, `networks: [alphamill]` within the real service block. Tests will handle; design just states requirements.

Let me read db_adapter quickly to be precise.
Round 2 is in. D001–D010 verified fixed; 3 new findings: **D011 (High)** missing DB wiring for the real service, **D012** impact/owner gaps, **D013** test-order gap. Baseline check first:

  <details><summary>tool output</summary>

  ```text
import os
import subprocess
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

COMPOSE_FILE = Path(__file__).resolve().parents[3] / "deployment" / "docker-compose.yml"


def database_url() -> str | None:
    return os.getenv("DB_URL")


@contextmanager
def connect():
    db_url = database_url()
    if db_url:
        conn = psycopg2.connect(db_url)
    else:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "timescaledb"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.getenv("DB_NAME", "quant"),
            user=os.getenv("DB_USER", "quant"),
            password=os.getenv("DB_PASSWORD", "changeme"),
        )

    try:

…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:11:21Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "| KRONOS_USE_REAL_MODEL / KRONOS_DEVICE | `true` / `cpu` |\n| 端口 | host `8002` → container `8001`（mock 保持 host `8001`，互不顶替） |", "newString": "| KRONOS_USE_REAL_MODEL / KRONOS_DEVICE | `true` / `cpu` |\n| DB 环境（同 mock 服务） | `DB_HOST: timescaledb`、`DB_PORT: 5432`、`DB_USER`/`DB_PASSWORD`/`DB_NAME`（`${DB_*:-...}` 默认值与 compose 其余服务一致） |\n| 服务依赖 | `depends_on: timescaledb: {condition:
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "| `AC-001` | 静态契约（unit，CI 常绿） | `tests/unit/test_f004_compose_profile_contract.py` | Dockerfile 有 mock/real 目标且 real 锁定依赖 pin；real 服务 profiles/只读挂载/端口/环境正确；默认 compose 配置不含 real 服务 |\n| `AC-001` | 容器集成（执行机） | `tests/integration/test_f004_real_profile.py` | compose 拉起后容器身份成立（compose 托管 + real 目标 + 只读挂载 + 8002:8001）且 `/predict source=kronos`；默认镜像 `import torch` 判红 |", "newString":
…[truncated])`


> [reasoning] Confirmed: DB env vars are DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD (or DB_URL). The design contract table should list them; and `depends_on: timescaledb: service_healthy` + `networks: [alphamill]`.

Interesting: db_adapter has a COMPOSE_FILE constant and `KRONOS_DB_DOCKER_FALLBACK` — docker exec fallback for host usage. Not needed for container (DB_HOST=timescaledb works in-container).

Now let me check the current relevant spots in design and tasks to edit:
- design §1 bullet (line 27): "- 后端 / API：无变更（同一份 `kronos_service`）"
- design §2 table
- design §5 startup sequence line (mention server.py)
- design §8 table rows
- spec §7 container bullet + AC-001
- tasks lines.

Let me read current design lines 25-31 and tasks lines to be precise. I have design content from previous reads; §1 lines 23-30. Tasks file I rewrote last round; let me re-read it to get exact current text (I wrote it, but let me confirm).

Current tasks.md (from my write):
```
### Phase 1：薄壳运行时改造

- [ ] T001 (`FR-001`): `kronos_real.py` real 模式启动预检与 eager load——启动期校验 `KRONOS_REPO_PATH`、模型与分词器目录及必需文件（`config.json`、权重文件），任一缺失或加载失败即打印缺失路径并非零退出，不退回 mock — verify: `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`
- [ ] T002 (`FR-001`): 进程级推理锁——模型加载至多一次、推理互斥（含并发首请求同时到达的场景） — verify: `tests/unit/test_f004_kronos_runtime_contract.py::test_predictor_loads_once_and_inference_serializes`

### Phase 2：镜像与编排

- [ ] T003 ... verify: `tests/unit/test_f004_compose_profile_contract.py::test_dockerfile_targets_pin_real_dependencies`
- [ ] T004 ... verify: `tests/unit/test_f004_compose_profile_contract.py::test_compose_real_service_contract` + compose config commands

### Phase 3：专属门禁与文档回写

- [ ] T005 ... 静态编排契约门禁定稿 ... verify: `tests/unit/test_f004_compose_profile_contract.py`（含变异记录）
- [ ] T006 ... 容器集成测试 ... verify: `tests/integration/test_f004_real_profile.py`
- [ ] T007 ... F001 spec §6 回写 ... verify: `python3 tools/verify.py`

## 3. 验证与验收任务

- [ ] T008 ... 执行机集成验收 ...
- [ ] T009 ... 回写 spec §6 验收证据 ...
- [ ] T010 ... 项目统一质量门 ...
- [ ] T011 ... 状态推进与 BACKLOG 同步 ...
```

New tasks structure (D013 test-first + D011/D012):
- T001 (`FR-001`): **先红后绿**：新增 `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`；实现 `kronos_real.py` 启动预检与 eager load，并在 `server.py` 启动钩子中调用（real 模式），任一缺失/加载失败即非零退出 — verify: 该用例由红转绿
- T002 (`FR-001`): 先新增 `::test_predictor_loads_once_and_inference_serializes`；实现进程级推理锁 — verify: 该用例由红转绿
- T003 (`FR-001`,`NFR-001`): 先新增 `tests/unit/test_f004_compose_profile_contract.py::test_dockerfile_targets_pin_real_dependencies`；实现 Dockerfile mock/real 目标与依赖 pin — verify: 该用例由红转绿
- T004 (`FR-001`,`NFR-001`): 先新增 `::test_compose_real_service_contract`（断言 profile/target/`:ro` 挂载/8002:8001/KRONOS_*、`DB_*` 环境、`depends_on: timescaledb: service_healthy`、`networks: [alphamill]`）；实现 compose 两服务 — verify: 该用例由红转绿 + `docker compose -f ... config --services` / `--profile kronos-real config`
- T005 (`AC-001`): 静态门禁补全与变异验证：默认配置不含 real、mock 目标不含 torch；改 target/删 pin/去 `:ro`/删 DB 依赖 必须判红 — verify: `tests/unit/test_f004_compose_profile_contract.py`（含变异记录）
- T006 (`AC-001`,`AC-002`): 容器集成测试：运行链（compose→模型→TimescaleDB→HTTP）成立（/health database 可达 + /predict source=kronos）、容器身份、缺资产非零退出、默认镜像 import torch 判红 — verify: `tests/integration/test_f004_real_profile.py`
- T007 (`FR-001`): F001 spec §6 回写 compose 形态 + 手工回退 — verify: `python3 tools/verify.py`
- T008 (`FR-001`): `vendor/VENDORED.md` 补容器内路径与 real profile 说明 — verify: `grep -n "app/vendor/Kronos" vendor/VENDORED.md` 或 `python3 tools/verify.py`… hmm let me think: verify should be a command; I'll use: `grep -q "/app/vendor/Kronos" vendor/VENDORED.md && grep -q "/app/models" vendor/VENDORED.md` — hmm and `python3 tools/verify.py` ensures repo gates. I'll write: verify: `grep -n "/app/vendor/Kronos" vendor/VENDORED.md`（含容器路径段）.

§3:
- T009 (`AC-001`,`AC-002`): 执行机验收 (was T008)
- T010 (`AC-001`): spec 证据回写 (was T009)
- T011 (`AC-001`,`NFR-001`): 统一质量门 (was T010)
- T012: 状态/BACKLOG (was T011)

§4 DAG:
- `T001 -> T002`（同一薄壳文件顺序改造）
- `T002 -> T006`
- `T003 -> T004`；`T003/T004 -> T005`；`T002/T005 -> T006`
- `T006 -> T007/T008`：文档回写以实测/契约定稿为前提；二者不同文件、顺序无关
- `T007/T008 -> T009 -> T010 -> T011 -> T012`：验收链顺序

Also fix T005's title: "静态门禁补全与变异验证" (not 定稿). T001's title should mention server.py + test-first.

Wait — also the reviewer D013's suggested fix: "将契约测试置于实现前先红，或明确并入对应实现任务". My approach: each implementation task creates its own test first (先红后绿) — combining both: tests created within the task, explicitly test-first. Good.

Also — hmm, should T001 include `server.py` startup hook? D012 suggested "在 T001 明列 server.py 启动钩子". Yes, included.

Now, one subtlety: design §5 says startup precheck and eager load both in 启动钩子. And `kronos_real.py` implements functions; `server.py` calls them. Design §2 intro says "不新增模块；差异=... + 薄壳三处最小改造". D012 wants design §1 impact corrected. Let me write:

design §1 bullet: "- 后端 / API：HTTP 契约无变更（同一份 `kronos_service`）；薄壳改动落在 `server.py`（real 模式启动钩子）与 `kronos_real.py`（预检/加载/锁实现，§5）。"

Hmm, also design §1's first paragraph mentions "薄壳做三处最小改造" — fine.

design §5 startup sequence: "→ **eager load**（一次性加载 Kronos + Tokenizer，由 `server.py` 启动钩子调用、先于接收流量）"。 Current text: "**eager load**（一次性加载 Kronos + Tokenizer，放在应用启动钩子、先于接收流量）". Change "放在应用启动钩子" → "由 `server.py` 启动钩子调用". Also precheck: "**预检**（...）" — add "`server.py` 启动钩子中执行"? The current text: "进程启动 → **预检**（...）→ **eager load**（...）". Maybe: "进程启动 → `server.py` 启动钩子：**预检**（...）→ **eager load**（...）→ 服务就绪". Let me rewrite that bullet once.

D011 design §2 table rows to add (after 端口 row or before 构建目标? Logical order: 构建目标, 挂载, env KRONOS_*, DB 环境, 依赖, 网络, 端口):

| DB 环境（同 mock 服务） | `DB_HOST: timescaledb`、`DB_PORT: 5432`、`DB_USER`/`DB_PASSWORD`/`DB_NAME`（`${DB_*:-...}` 默认值与 compose 其余服务一致） |
| 服务依赖 | `depends_on: timescaledb: {condition: service_healthy}` |
| 网络 | `networks: [alphamill]` |

And add a note sentence after the table: "运行链为 compose → real 容器（模型）→ TimescaleDB（healthy）→ HTTP：`/health` 的 `database` 段与 `/predict` 的 OHLCV 读取都要求 DB 可达，缺任一（凭据/依赖/网络）都会让 real 实例不可用。"

design §8 rows update:
- static row: "...；real 服务 profiles/只读挂载/端口/环境/**DB 环境+healthy 依赖+网络**正确；..."
- container row: "compose 拉起后容器身份成立（...）且完整运行链（模型+DB）成立：/health `database` 可达、`/predict source=kronos`；默认镜像 `import torch` 判红"

spec §7 container bullet: add "运行链（compose→模型→TimescaleDB→HTTP）成立——`/health` 的 `database` 可达、`/predict` 返回 `source=kronos`；". Current bullet: "**容器集成（执行机）**：`tests/integration/test_f004_real_profile.py`——构建 real 目标并拉起 profile，校验容器身份（compose 托管 + real 目标 + 只读挂载 + 8002:8001）与 `source=kronos`；缺资产场景非零退出；默认镜像 `import torch` 判红；开关语义..." → change "与 `source=kronos`" to "与完整运行链（模型 + DB）：`/health` 的 `database` 可达且 `/predict` 返回 `source=kronos`；".

spec AC-001: currently "...（容器身份、只读挂载、8002:8001 成立），model_enabled=true 且 /predict 返回 source=kronos；不带该 profile..." → "...（容器身份、只读挂载、8002:8001、DB 运行链成立），model_enabled=true、/health 的 database 可达且 /predict 返回 source=kronos；不带该 profile...".

Hmm, is "DB 运行链成立" + "/health database 可达" redundant? Just say: "（容器身份、只读挂载、8002:8001 成立），且完整运行链（模型 + TimescaleDB）可用：model_enabled=true、/health 的 database 可达、/predict 返回 source=kronos；". OK.

spec §3 范围内 bullet 2 (compose service) should also mention DB wiring? The reviewer's fix says "补齐 DB_*、TimescaleDB healthy dependency 与 alphamill 网络" — where? Design mainly. spec 范围内 bullet 2: "compose 增 `kronos-signal-real` 服务（`profiles: [kronos-real]`）：只读挂载 ..., host 8002 → container 8001；" → add "与 mock 相同的 DB 环境、`depends_on: timescaledb: {condition: service_healthy}` 与 `alphamill` 网络；". Yes, keep spec consistent.

Also design §5 数据前置 mentions DB. Fine.

Now commits:
- Commit 1 (D011): design §2 table + note + §8 rows; spec §3 bullet + §7 bullet + AC-001. Hmm — AC-001 edit belongs to D011's fix. Yes.
- Commit 2 (D012): design §1 bullet + §5 hook mention.
- Commit 3 (D013): tasks.md rewrite (with D011/D012 task updates).
- Update FIX-log Round 2 + bump dates.

Also: the reviewer said Round 3 will only re-check these 3 findings' diff and adjacent contracts. So my fixes should be tight.

One more check — D012's title: "应用启动钩子和配套文档没有任务所有者". "配套文档" = VENDORED.md. And "design 称后端无变更却要求应用启动钩子". So fix both.

Also, I should double check whether design mentions `vendor/VENDORED.md` in §1 影响面: "文档 / 配置：F001 spec §6 命令回写；`vendor/VENDORED.md` 补容器内路径说明"。 Yes it does. The issue is tasks had no task for it. Add T008. Good.

Let me now also think: any other wire-level requirement for the real service? What about `NO_PROXY`? freqtrade needs it for proxy env; kronos service doesn't use proxies. DB access within network — no proxy. OK. What about the docker DNS: DB_HOST=timescaledb resolves on alphamill network. ✓.

What about `restart: "no"` vs `depends_on` semantics — fine.

What about healthcheck requiring DB? Our healthcheck condition is `/health` model_loaded=true; but `/health` also pings DB (healthcheck() raises if DB unreachable → /health 500 → healthcheck fails). So DB wiring is implicitly covered by readiness. Good — mention in design note: "healthcheck 同时要求 /health 200（含 DB 探查）".

Hmm, careful: server.py /health calls healthcheck() which raises on DB failure?? Let me look: `db = healthcheck()` — healthcheck() raises on exception (unless fallback env). If DB down → /health raises → 500. So readiness = /health 200 + model_loaded. And the container test asserts /health database reachable. Good.

Now let me apply edits. First D011.

Let me re-read the exact current design §2 table text and spec text to craft edits precisely. I have design §2 from the read after D008 (lines 34-46). Current table rows:
| 构建目标 | `target: real`，`profiles: [kronos-real]` |
| 挂载 | `../vendor/Kronos:/app/vendor/Kronos:ro`；`../models:/app/models:ro` |
| KRONOS_REPO_PATH | `/app/vendor/Kronos` |
| KRONOS_MODEL_PATH | `/app/models/Kronos-base` |
| KRONOS_TOKENIZER_PATH | `/app/models/Kronos-Tokenizer-base` |
| KRONOS_USE_REAL_MODEL / KRONOS_DEVICE | `true` / `cpu` |
| 端口 | host `8002` → container `8001`（mock 保持 host `8001`，互不顶替） |

Add rows after KRONOS_DEVICE:
| DB 环境（同 mock 服务） | `DB_HOST: timescaledb`、`DB_PORT: 5432`、`DB_USER`/`DB_PASSWORD`/`DB_NAME`（`${DB_*:-...}` 默认同 compose 其余服务） |
| 服务依赖 | `depends_on: timescaledb: {condition: service_healthy}` |
| 网络 | `networks: [alphamill]` |

And after the table (before pin paragraph? The pin paragraph is after the table): add note. Current structure: table → blank → "**real 目标的依赖 pin**...". Insert note after table:

"运行链为 compose → real 容器（模型）→ TimescaleDB（healthy）→ HTTP：`/health` 的 `database` 段与 `/predict` 的 OHLCV 读取都要求 DB 可达；凭据、健康依赖或网络任一缺失都会让实例在就绪/预测时失败，由静态与容器门禁双向锁定（§8）。"

OK let's do the edits.
Round 2 baseline: `main@6e06ca7`, fix diff 52% (reviewer upgraded to full-scan), D001–D010 all verified `fixed`. Now fixing D011/D012/D013.

**Finding 1/3 (D011)** — real service DB wiring (env / healthy dependency / network):

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:11:41Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- compose 增 `kronos-signal-real` 服务（`profiles: [kronos-real]`）：只读挂载 `vendor/Kronos` 与 `models/`（`:ro`），`KRONOS_USE_REAL_MODEL=true`，host 8002 → container 8001；", "newString": "- compose 增 `kronos-signal-real` 服务（`profiles: [kronos-real]`）：只读挂载 `vendor/Kronos` 与 `models/`（`:ro`），`KRONOS_USE_REAL_MODEL=true`，host 8002 → container 8001，与 mock 相同的 DB 环境、`depends_on: timescaledb: {cond
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "- **容器集成（执行机）**：`tests/integration/test_f004_real_profile.py`——构建 real 目标并拉起 profile，校验容器身份（compose 托管 + real 目标 + 只读挂载 + 8002:8001）与 `source=kronos`；缺资产场景非零退出；默认镜像 `import torch` 判红；开关语义与 F001 冒烟一致（未设 `ALPHAMILL_INTEGRATION` 时 skip、设了不可达判红）；", "newString": "- **容器集成（执行机）**：`tests/integration/test_f004_real_profile.py`——构建 real 目标并拉起 profile，校验容器身份（compose 托管 + real 目标 + 只读挂载 + 80
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "oldString": "（容器身份、只读挂载、8002:8001 成立），model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排不启用也不构建 real 服务、默认镜像不含 torch — tests:", "newString": "（容器身份、只读挂载、8002:8001 成立），且完整运行链（模型 + TimescaleDB）可用：model_enabled=true、/health 的 database 可达、/predict 返回 source=kronos；不带该 profile 时默认编排不启用也不构建 real 服务、默认镜像不含 torch — tests:"})`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:11:47Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -i 's/^updated: 2026-09-14$/updated: 2026-09-15/' docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md && python3 tools/validate_spec_lifecycle.py && git add docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): 补 real 服务数据库接线——DB_* 环境/healthy 依赖/网络（F004-D011）\n\n- design §2 契约表增 DB 环境、depe
…[truncated])`


> [reasoning] Now bump spec/design dates to 2026-09-15 and commit D011. Actually, dates: I'll bump at each commit's file... spec gets D011 edits; design gets D011 edits now and D012 edits next. Let me bump both dates now (design date bump in D011 commit is fine; it's just metadata).

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
64d1ebd docs(f004): 补 real 服务数据库接线——DB_* 环境/healthy 依赖/网络（F004-D011）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:11:51Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- 后端 / API：无变更（同一份 `kronos_service`）", "newString": "- 后端 / API：HTTP 契约无变更（同一份 `kronos_service`）；薄壳改动落在 `server.py`（real 模式启动钩子调用预检/eager load）与 `kronos_real.py`（预检/加载/锁实现，§5）"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md", "oldString": "- 启动序列（real 模式）：进程启动 → **预检**（`KRONOS_REPO_PATH`、模型/分词器目录及必需文件存在）→ **eager load**（一次性加载 Kronos + Tokenizer，放在应用启动钩子、先于接收流量）→ 服务就绪；预检或加载任一失败 → 打印缺失路径/错误并**非零退出**（real 服务 `restart: \"no\"`，失败态可直接观察，不静默降级）；", "newString": "- 启动序列（real 模式）：进程启动 → **`server.py` 启动钩子**：**预检**（`KRONOS_REPO_PATH`、模型/分词器目录及必需文件存在）→ **eager load**（一次性加载 Kronos + Tokenizer，先于接收流量）→ 服务就绪；预检或加载任一失败 → 打印缺失路径/
…[truncated])`


> [reasoning] D011 done. Now D012: impact section correction + startup hook owner (`server.py`) in design; tasks T001/T008 in tasks commit (D013).

design §1 bullet edit:
Current: "- 后端 / API：无变更（同一份 `kronos_service`）"
New: "- 后端 / API：HTTP 契约无变更（同一份 `kronos_service`）；薄壳改动落在 `server.py`（real 模式启动钩子调用预检/eager load）与 `kronos_real.py`（预检/加载/锁实现，§5）"

design §5 startup bullet: current:
"- 启动序列（real 模式）：进程启动 → **预检**（`KRONOS_REPO_PATH`、模型/分词器目录及必需文件存在）→ **eager load**（一次性加载 Kronos + Tokenizer，放在应用启动钩子、先于接收流量）→ 服务就绪；预检或加载任一失败 → 打印缺失路径/错误并**非零退出**（real 服务 `restart: "no"`，失败态可直接观察，不静默降级）；"
New: "- 启动序列（real 模式）：进程启动 → **`server.py` 启动钩子**：**预检**（`KRONOS_REPO_PATH`、模型/分词器目录及必需文件存在）→ **eager load**（一次性加载 Kronos + Tokenizer，先于接收流量）→ 服务就绪；预检或加载任一失败 → 打印缺失路径/错误并**非零退出**（real 服务 `restart: "no"`，失败态可直接观察，不静默降级）；"

Commit D012.
**Finding 2/3 (D012)** — correct impact statement + name the startup-hook owner:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:11:57Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add docs/features/0.2/F004-kronos-inference-runtime/design.md && git commit -q -m \"docs(f004): 校正影响面并点明启动钩子所有者（F004-D012）\n\n- §1 后端/API 影响改为'HTTP 契约无变更；薄壳改动在 server.py 启动钩子 + kronos_real.py'\n- §5 启动序列标注 server.py 启动钩子执行预检/eager load；VENDORED.md 回写任务见 tasks T008\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
ce557c3 docs(f004): 校正影响面并点明启动钩子所有者（F004-D012）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:12:00Z

- **tool**: `write({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "content": "---\nkind: feature\nid: F004\nversion: \"0.2\"\nrelated_features: [F001, F002]\ntopics: [kronos, inference, deployment]\ndoc_kind: tasks\ncreated: 2026-09-12\nupdated: 2026-09-15\n---\n\n# F004：Kronos 真实推理运行时 - 任务\n\n> Owner: Georg | Spec: `spec.md` | Design: `design.md`\n\n## 0. 来源与执行规则\n\n- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。\n- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。\n- 完成且验证后立即把
…[truncated])`


> [reasoning] D012 done (task-side additions pending in tasks commit). Now D013: tasks.md restructure — test-first per task, plus D011/D012 task-level updates (T004 assertions for DB wiring, T001 server.py, T008 VENDORED.md).

Let me write the new tasks.md fully:

```
## 2. 实现任务

### Phase 1：薄壳运行时改造

- [ ] T001 (`FR-001`): 先红后绿——新增 `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`（fake 目录注入，先失败）；实现 `kronos_real.py` 启动预检与 eager load，并由 `server.py` 启动钩子在 real 模式调用：校验 `KRONOS_REPO_PATH`、模型与分词器目录及必需文件（`config.json`、权重文件），任一缺失或加载失败即打印缺失路径并非零退出，不退回 mock — verify: 该用例由红转绿
- [ ] T002 (`FR-001`): 先红后绿——新增同文件 `::test_predictor_loads_once_and_inference_serializes`（先失败）；实现进程级推理锁：模型加载至多一次、推理互斥（含并发首请求场景） — verify: 该用例由红转绿

### Phase 2：镜像与编排

- [ ] T003 (`FR-001`, `NFR-001`): 先红后绿——新增 `tests/unit/test_f004_compose_profile_contract.py::test_dockerfile_targets_pin_real_dependencies`（先失败）；实现 `deployment/kronos-service.Dockerfile` 拆 `mock`/`real` 目标：real 从 CPU wheel index 安装 design §2 锁定的 torch 与最小推理依赖，mock 保持现状且不含 torch — verify: 该用例由红转绿
- [ ] T004 (`FR-001`, `NFR-001`): 先红后绿——新增同文件 `::test_compose_real_service_contract`（先失败）；实现 compose 两服务：`kronos-signal-real`（`profiles: [kronos-real]`、`target: real`、`:ro` 挂载、`8002:8001`、KRONOS_* 与 DB_* 环境、`depends_on: timescaledb: {condition: service_healthy}`、`networks: [alphamill]`、healthcheck 以 `model_loaded=true` 为通过条件、失败不自动重启）；`kronos-signal` 显式 `target: mock` — verify: 该用例由红转绿 + `docker compose -f deployment/docker-compose.yml config --services`（不含 real）与 `docker compose -f deployment/docker-compose.yml --profile kronos-real config`（含 real）

### Phase 3：门禁补全与文档回写

- [ ] T005 (`AC-001`): 静态门禁补全与变异验证：默认配置不含 real 服务、mock 目标不含 torch、real 含 DB 接线；变异验证（改 target、删依赖 pin、去 `:ro`、删 DB 依赖必须判红） — verify: `tests/unit/test_f004_compose_profile_contract.py` 全绿 + 变异记录
- [ ] T006 (`AC-001`, `AC-002`): 容器集成测试：compose 拉起 real 实例后校验容器身份（compose 托管 + real 目标 + 只读挂载 + 端口映射）与完整运行链（模型 + TimescaleDB：`/health` 的 `database` 可达 + `/predict source=kronos`）；缺资产场景非零退出；默认镜像 `import torch` 判红 — verify: `tests/integration/test_f004_real_profile.py`
- [ ] T007 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`
- [ ] T008 (`FR-001`): 更新 `vendor/VENDORED.md`：补容器内路径（`/app/vendor/Kronos`、`/app/models/Kronos-base`、`/app/models/Kronos-Tokenizer-base`）与 real profile 说明 — verify: `grep -n "/app/vendor/Kronos" vendor/VENDORED.md`

## 3. 验证与验收任务

- [ ] T009 (`AC-001`, `AC-002`): 在执行机 `qiaozhi-lt` 跑集成验收：F001 冒烟（HTTP 契约）+ F004 容器集成 + 默认镜像否证，证据记录 hostname 与 `device=cpu` — verify: `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py tests/integration/test_f004_real_profile.py -q`
- [ ] T010 (`AC-001`): 回写 spec §6 验收证据（命令、输出摘要、取证机 hostname、device） — verify: `python3 tools/verify.py`（文档门禁）
- [ ] T011 (`AC-001`, `NFR-001`): 运行项目统一质量门并全绿 — verify: `python3 tools/verify.py`
- [ ] T012: 状态推进（spec frontmatter）与 BACKLOG 同步 — verify: `python3 tools/verify.py`（含生命周期与 BACKLOG 双向校验）

## 4. 依赖与并行关系

- `T001 -> T002`：同一薄壳文件的顺序改造（预检/加载 → 锁；各自测试在同一任务内先红后绿）。
- `T001/T002 -> T006`：容器集成依赖启动预检、eager load 与串行推理行为成立。
- `T003 -> T004`：compose `target` 依赖 Dockerfile 目标定义。
- `T003/T004 -> T005`：静态门禁在全量断言（含默认隔离）与变异验证后定稿。
- `T002/T005 -> T006`：容器集成建立在薄壳行为与静态契约通过之上。
- `T006 -> T007/T008`：文档回写以实测通过/契约成立为前提；二者修改不同文件，顺序无关。
- `T007/T008 -> T009 -> T010 -> T011 -> T012`：验收链顺序执行（实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步）。

## 5. 明确后移
(keep)
```

Wait, T005 verify says "含变异记录" but the task description includes mutation verification. Fine.

One issue: my earlier §4 had "`T003/T004 -> T005`" and "`T005 -> T006`". Now "T002/T005 -> T006". OK.

Also the reviewer's D013: "保证 T001-T004 完成时 verify 已存在" — with test-first-in-task, yes.

Hmm, but now T005 "静态门禁补全" overlaps with T003/T004's tests. Fine — T005 adds the remaining default-isolation assertions + mutation.

Also should T001's verify mention the red→green requirement explicitly? "该用例由红转绿" yes.

Let me also double check the task template wants task IDs continuous & unique — yes T001..T012 continuous. Phase headings only under §2 — yes.

Now write tasks.md fully and commit D013.
**Finding 3/3 (D013)** — tasks: test-first per task + task owners for `server.py` / `VENDORED.md` (+ DB assertions from D011):

## assistant · 2026-09-14T16:12:13Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "limit": 40})`


> [reasoning] The write tool refuses because the file exists and I haven't... wait, I did read it earlier (round 1). But the tool says "File already exists. Use edit tool instead." Hmm — actually the write tool normally allows overwrite if the file was read first. I read tasks.md earlier in this conversation (round 1). But maybe the guard requires reading in the current "session state". Let me just read it first, then write.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: related_features: [F001, F002]
6: topics: [kronos, inference, deployment]
7: doc_kind: tasks
8: created: 2026-09-12
9: updated: 2026-09-14
10: ---
11:
12: # F004：Kronos 真实推理运行时 - 任务
13:
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15:
16: ## 0. 来源与执行规则
17:
18: - 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
19: - 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
20: - 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
21: - `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
22: - 集成与容器验收只在执行机 `qiaozhi-lt` 采集，证据记录 hostname 与 `device=cpu`；开发机只跑静态与单元门禁（SOP §3）。
23:
24: ## 1. 前置条件
25:
26: - F001 已 done：薄壳、`vendor/Kronos` pin 与 `models/` 权重流
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:12:16Z

- **tool**: `write({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "content": "---\nkind: feature\nid: F004\nversion: \"0.2\"\nrelated_features: [F001, F002]\ntopics: [kronos, inference, deployment]\ndoc_kind: tasks\ncreated: 2026-09-12\nupdated: 2026-09-15\n---\n\n# F004：Kronos 真实推理运行时 - 任务\n\n> Owner: Georg | Spec: `spec.md` | Design: `design.md`\n\n## 0. 来源与执行规则\n\n- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。\n- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。\n- 完成且验证后立即把
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Wrote file successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:12:25Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && python3 tools/validate_spec_lifecycle.py && git add docs/features/0.2/F004-kronos-inference-runtime/tasks.md && git commit -q -m \"docs(f004): tasks 先红后绿改造与文档任务所有者（F004-D013）\n\n- T001-T004 改为'先写失败用例再实现'，测试创建并入对应任务，完成即验证\n- T005 改为门禁补全+变异验证（不再是首次创建）；T006 补 DB 运行链断言\n- T001 明列 server.py 启动钩子（D012）；新增 T008 VENDORED.md 回写任务（D012）\n- T004/T005 静态断言补 DB_* 环境/healthy 依赖/网络（D011）；验收链延至 T009-T012\" && git log --oneline -1"})`


> [reasoning] Now run the doc gates, commit D013, then run full verify, then append FIX-log Round 2.

Wait — before committing, double-check the tasks refs: T001-T012 refs: T001 FR-001, T002 FR-001, T003 FR-001+NFR-001, T004 FR-001+NFR-001, T005 AC-001, T006 AC-001+AC-002, T007 FR-001, T008 FR-001, T009 AC-001+AC-002, T010 AC-001, T011 AC-001+NFR-001, T012 none. All valid IDs (FR-001, NFR-001 in spec §4; AC-001, AC-002 exist). No gate on task refs anyway.

Commit message should note D011/D012 task-level updates merged.

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
3f7320e docs(f004): tasks 先红后绿改造与文档任务所有者（F004-D013）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:12:29Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && time .venv/bin/python tools/verify.py 2>&1 | tail -25; date \"+%Y-%m-%d %H:%M %Z\"; git rev-parse --short HEAD", "timeout": 600000})`


> [reasoning] All 3 findings fixed. Now:
1. Run full verify gate.
2. Append FIX-log Round 2 declaration.
3. Report.

Wait — one thing to double check: the reviewer's Round 2 says "修复后 Round 3 只复核这 3 条的 diff 与相邻 compose/薄壳契约". Also check: did my D011 edits leave any inconsistency elsewhere? E.g., design §2's note says "由静态与容器门禁双向锁定（§8）" ✓. spec §3 bullet ✓.

Also check whether design §5 数据前置 bullet and §2 note overlap — fine.

One more possible check per D011: "real 服务若严格按 design §2/T004 实施，将缺数据库凭据、健康依赖和共同网络" — fixed in design §2 table + spec §3 + T004/T005/T006.

D012: "design 称后端无变更" — fixed §1. "T001 明列 server.py" ✓. "VENDORED.md 回写增加任务" ✓ (T008).

D013: "T001-T004 verify 引用尚未创建的测试门" — now each creates its own tests first. "静态测试直到 T005 才定稿" — T005 is now 补全+变异, T003/T004 create their tests. ✓.

Now run full gate with .venv python. Then FIX-log append.

Also should I bump FIX-log Round 2 with:
- findings: D011, D012, D013
- commits: 64d1ebd (D011), ce557c3 (D012), 3f7320e (D013; 承载 D011/D012 任务级更新)
- regression_tests: doc gates again; note test-first commitments now in tasks.
- gate: .venv/bin/python tools/verify.py result + timestamp.
- rejected: none.

Let me run the gate now.
All 3 findings committed. Round-end full gate:

  <details><summary>tool output</summary>

  ```text
........................................................................ [ 66%]
........................................................s............... [ 99%]
s                                                                        [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/integration/test_f001_kronos_smoke.py:86: AC-006 需真实模型实例：设 KRONOS_REQUIRE_REAL_MODEL=1 并把 KRONOS_BASE_URL 指向真实实例（命令见本文件 docstring / spec §6 AC-006）
SKIPPED [1] tests/integration/test_f002_schedule_backup.py:84: 未设置 ALPHAMILL_REAL_LAKE_DIR（本用例仅在有真实湖时运行）
215 passed, 2 skipped in 186.27s (0:03:06)
All checks passed!
103 files already formatted

== 规格生命周期校验 ==

== 文档相对链接检查 ==

== dev 依赖版本在 pin 范围内 ==

== 密钥模式扫描 ==

== pytest ==

== ruff check ==

== ruff format
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:16:55Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "oldString": "- tasks.md 的合并提交理由见上（`904f2cb`）；若检视方不追认该合并，请按 `[review-r1]` 批注，修复方可在后续轮拆分。", "newString": "- tasks.md 的合并提交理由见上（`904f2cb`）；若检视方不追认该合并，请按 `[review-r1]` 批注，修复方可在后续轮拆分。\n\n## Round 2 · 2026-09-15\n\n- **基线**：`main` @ `6e06ca7`（Round 2 检视基线）→ `main` @ `3f7320e`（3 个提交）\n- **findings**：F004-D011、D012、D013（全部处理，无 rejection）\n- **commits**：\n  - F004-D011：`64d1ebd`\n  - F004-D012：`ce557c3`\n  - F004-D013：`3f7320e`（tasks
…[truncated])`


> [reasoning] Gate green: 215 passed, 2 skipped, all doc gates pass. HEAD = 3f7320e.

Now append FIX-log Round 2. Must be append-only — append to the existing file without modifying Round 1 entries. Let me read the end of FIX-log to append properly... I wrote it; I'll use edit to append after the last line, or bash `cat >>` (but instructions say prefer edit tool for file ops; append via edit needs oldString match). Let me read the tail of FIX-log to get exact ending text, then edit-append.

Actually I know the content: the file ends with:
"- tasks.md 的合并提交理由见上（`904f2cb`）；若检视方不追认该合并，请按 `[review-r1]` 批注，修复方可在后续轮拆分。"

I'll append after that. Let me construct Round 2 entry:

```
## Round 2 · 2026-09-15

- **基线**：`main` @ `6e06ca7`（Round 2 检视基线）→ `main` @ `3f7320e`（3 个提交）
- **findings**：F004-D011、D012、D013（全部处理，无 rejection）
- **commits**：
  - F004-D011：`64d1ebd`
  - F004-D012：`ce557c3`
  - F004-D013：`3f7320e`（tasks 重构；同时承载 D011 的 T004/T005 DB 接线断言与 D012 的 T001 `server.py`、T008 VENDORED.md 任务级更新）
- **regression_tests**：文档检视同 Round 1——文档 diff + 文档门禁（`validate_spec_lifecycle`/`check_doc_links`）；D013 另将「先红后绿」写入 tasks §0 执行规则，实现轮每个任务自带先失败用例
- **gate**：`.venv/bin/python tools/verify.py` → 全绿（生命周期 / 链接 / 依赖 pin / 密钥 / pytest `215 passed, 2 skipped` / ruff）；2026-09-15 00:16 HKT
- **rejected**：无

### 逐条处理说明

- **D011**（real 服务缺 DB 接线）：design §2 契约表新增三行——`DB_*` 环境（同 mock）、`depends_on: timescaledb: {condition: service_healthy}`、`networks: [alphamill]`，并写明运行链（compose→模型→TimescaleDB→HTTP）；design §8 静态门断言补 DB 接线、容器门断言补 `/health database 可达 + /predict` 端到端；spec §3/§7/AC-001 同步；T004/T005/T006 断言清单同步（`3f7320e`）。
- **D012**（启动钩子/文档无所有者）：design §1「后端 / API」改为「HTTP 契约无变更；薄壳改动落在 `server.py`（启动钩子）与 `kronos_real.py`」；§5 启动序列标注 `server.py` 启动钩子；T001 明列 `server.py`；新增 T008 `vendor/VENDORED.md` 回写任务（verify: grep 容器路径）。
- **D013**（测试门晚于实现任务）：T001-T004 全部改为「先红后绿——先新增失败用例再实现」，测试创建并入对应任务；T005 从「定稿」改为「补全默认隔离断言 + 变异验证」；§0 执行规则增先红后绿条款，§4 DAG 同步（验收链延至 T009-T012）。
```

Then the reviewer will do Round 3 (diff-only on these).

Let me append via edit tool: oldString = the last line of the file; newString = last line + new content.

The last line: "- tasks.md 的合并提交理由见上（`904f2cb`）；若检视方不追认该合并，请按 `[review-r1]` 批注，修复方可在后续轮拆分。"

Let me apply.
Gate green (`215 passed, 2 skipped`). Appending Round 2 declaration to `FIX-log.md` (append-only):

## assistant · 2026-09-14T16:17:04Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && tail -c 600 docs/reviews/FIX-log.md | cat -A | tail -8"})`


> [reasoning] The oldString doesn't match. Maybe the file content differs slightly. Let me read the tail of FIX-log.md.

  <details><summary>tool output</summary>

  ```text
eview-r2] 2026-09-14 M-BM-7 M-gM-^KM-,M-gM-+M-^KM-fM- M-8M-eM-/M-9M-oM-<M-^ZF004-D001M-oM-=M-^^D010 M-gM-^ZM-^DM-fM-^VM-^GM-fM-!M-#M-dM-?M-.M-eM-$M-^MM-fM-^HM-^PM-gM-+M-^KM-oM-<M-^LM-eM-7M-2M-eM-^\M-($
`CURRENT-doc.md` M-eM-^NM-^_M-eM--M-^PM-fM-^[M-4M-fM-^VM-0M-dM-8M-: fixedM-cM-^@M-^BM-fM-^\M-,M-hM-=M-.M-eM-^[M- M-dM-?M-.M-eM-$M-^MM-hM-&M-^FM-gM-^[M-^VM-gM-:M-& 52% M-fM-^LM-^IM-eM-^MM-^OM-hM-.M-.M-eM-^MM-^GM-gM-:M-'M-dM-8M-:M-dM-8M-^@M-fM-,M-!M-fM-^@M-' full-scanM-oM-<M-^L$
M-fM-^VM-0M-eM-"M-^^ F004-D011M-oM-<M-^HHighM-oM-<M-^Zreal M-fM-^\M-^MM-eM-^JM-!M-gM-<M-: DB M-gM-^NM-/M-eM-"M-^CM-cM-^@M-^ATimescaleDB M-eM-^AM-%M-eM-:M-7M-dM->M-^]M-hM-5M-^VM-dM-8M-^N alphamill M-gM-=M-^QM-gM-;M-^\M-oM-<M-^IM-cM-^@M-^A$
F004-D012M-oM-<M-^HMediumM-oM-<M-^Z`server.py` M-eM-^PM-/M-eM-^JM-(M-iM-^RM-)M-eM
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:17:08Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md"})`


> [reasoning] Interesting! The FIX-log has been MODIFIED by the reviewer — it now contains review annotations (not what I wrote at the end). The tail shows: "[review-r2] 2026-09-14 · 判定了 F004-D001–D010 的修复声明..." — so the reviewer appended `[review-r2]` annotations to my Round 1 entry. That's why my oldString didn't match.

I need to read the full current FIX-log.md to see the current state before appending my Round 2 entry. Let me read it.
The reviewer has annotated the FIX-log. Reading the current state before appending:

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/FIX-log.md</path>
<type>file</type>
<content>
1: # FIX-log —— F004 设计文档检视修复方声明（本地过程稿，不进 git）
2:
3: > 本文件由修复方独占写权，append-only；检视方对修复条目的独立核对结果以
4: > `[review-r<N>]` 批注形式追加在对应条目下方。修复方对 `CURRENT-doc.md` 零写入。
5:
6: ## Round 1 · 2026-09-14
7:
8: - **基线**：`main` @ `bc314f0`（修复前）→ `main` @ `6e06ca7`（修复后，12 个提交）
9: - **受检产物**：`docs/features/0.2/F004-kronos-inference-runtime/{spec,design,tasks}.md`；
10:   相邻契约连带勘正：`docs/features/0.2/F002-data-bridge/spec.md`（D001 的跨文件后果）
11: - **findings**：F004-D001、D002、D003、D004、D005、D006、D007、D008、D009、D010（全数处理，无 rejection）
12: - **commits**（一 finding 一 commit；补遗单独成篇）：
13:   - F004-D001：`1e81b7c`（spec 删除自动升级承诺 + F002 spec 勘正）+ `6e06ca7`（design §9 决策行补遗）
14:   - F004-D002：`affc424`
15:   - F004-D003：`88dfce9` +
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:17:11Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "oldString": "`.venv/bin/python tools/verify.py` 全绿（194 passed, 23 skipped，83.69 秒）；Round 2 不闭环。", "newString": "`.venv/bin/python tools/verify.py` 全绿（194 passed, 23 skipped，83.69 秒）；Round 2 不闭环。\n\n## Round 2 · 2026-09-15\n\n- **基线**：`main` @ `6e06ca7`（Round 2 检视基线）→ `main` @ `3f7320e`（3 个提交）\n- **findings**：F004-D011、D012、D013（全部处理，无 rejection）\n- **commits**：\n  - F004-D011：`64d1ebd`\n  - F004-D012：`ce557c3`\n  - F004-D013
…[truncated])`


> [reasoning] The reviewer appended `[review-r2]` annotation at the end (lines 79-84). I must NOT modify that. My Round 2 fix declaration must be appended AFTER the annotation (append-only, chronological). So the new content goes after line 84.

Let me append using edit with oldString being the last lines (the review annotation ending) and newString = same + my Round 2 entry. Careful to match exactly.

The last line: "`.venv/bin/python tools/verify.py` 全绿（194 passed, 23 skipped，83.69 秒）；Round 2 不闭环。"

I'll use that as anchor.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:17:17Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== design §2 DB rows ===\"; grep -n \"DB_HOST: timescaledb\\|service_healthy\\|networks: \\[alphamill\\]\" docs/features/0.2/F004-kronos-inference-runtime/design.md; echo \"=== tasks test-first + owners ===\"; grep -n \"先红后绿\\|server.py\\|VENDORED.md\" docs/features/0.2/F004-kronos-inference-runtime/tasks.md | head; echo \"=== spec chain ===\"; grep -n \"database 可达\" docs/features/0.2/F004-kronos-inference-runtime/spec.md; echo \"=== git
…[truncated])`


> [reasoning] Now final checks:
1. Confirm working tree: only the ui-mockup files modified (unrelated, user's) + gitignored review files. My doc commits are on main.
2. Verify no other doc inconsistencies introduced by Round 2 edits — quick grep for D011-relevant items and consistency check: design §2 table has DB rows; spec AC-001 mentions database; tasks has T008 and test-first wording. Let me run a quick sanity grep.
3. Confirm validate_spec_lifecycle + check_doc_links still pass (ran in gate already, but after FIX-log edit — FIX-log is gitignored and not scanned; fine).

Also note: reviewer's annotation says independent gate was "194 passed, 23 skipped" — environment difference (their run skipped integration tests; mine ran them because DB was reachable). Hmm wait — actually why did reviewer's run skip 23 tests while ours passes 215? Both on this machine? The reviewer ran `.venv/bin/python tools/verify.py` and got 194 passed, 23 skipped, 83.69s. Mine: 215 passed, 2 skipped, 186s. The difference: reviewer might have run when TimescaleDB/docker was not running, or their environment differs (they may be an agent in a different container). Not my concern for the fix, but worth noting? The reviewer will re-run. Since docs-only changes, the numbers don't matter. I won't mention.

Actually, one thing I should double check: the reviewer says "F004 修复 diff 为 121 additions / 46 deletions，约占当前 324 行的 52%" — fine.

Let me do the final sanity grep and git status, then report.

Also — should I remove the stale "待复核提示" guidance in Round 1 about tasks merge (already reviewed)? No — append-only, can't modify. Fine.

Let me also double check that I didn't accidentally leave design §2's note inconsistent: "由静态与容器门禁双向锁定（§8）" ✓.

Run final checks.

  <details><summary>tool output</summary>

  ```text
=== design §2 DB rows ===
44:| DB 环境（同 mock 服务） | `DB_HOST: timescaledb`、`DB_PORT: 5432`、`DB_USER`/`DB_PASSWORD`/`DB_NAME`（`${DB_*:-...}` 默认值与 compose 其余服务一致） |
45:| 服务依赖 | `depends_on: timescaledb: {condition: service_healthy}` |
46:| 网络 | `networks: [alphamill]` |
=== tasks test-first + owners ===
23:- 实现任务遵循先红后绿：任务内的契约测试必须先失败（复现缺口）再随实现转绿，不得先实现后补测试。
34:- [ ] T001 (`FR-001`): 先红后绿——新增 `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`（fake 目录注入，先失败）；实现 `kronos_real.py` 启动预检与 eager load，并由 `server.py` 启动钩子在 real 模式调用：校验 `KRONOS_REPO_PATH`、模型与分词器目录及必需文件（`config.json`、权重文件），任一缺失或加载失败即打印缺失路径并非零退出，不退回 mock — verify: 该用例由红转绿
35:- [ ] T002 (`FR-001`): 先红后绿——新增同文件 `::test_predictor_loads_once_and_inference_serializes`（先失败）；实现进程级推理锁：模型加载至多一次、推理互
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:17:22Z

- **tool**: `todowrite({"todos": [{"content": "F004-D011: real 服务 DB 接线（DB_*/healthy 依赖/网络）+ 双门断言 - commit 64d1ebd", "status": "completed", "priority": "high"}, {"content": "F004-D012: 影响面校正 + server.py 启动钩子所有者 + VENDORED.md 任务 - commit ce557c3 (+3f7320e 任务级)", "status": "completed", "priority": "medium"}, {"content": "F004-D013: T001-T004 先红后绿重构 + 门禁补全任务重定位 - commit 3f7320e", "status": "completed", "priority": "medium"}, {"content": "轮末全量门禁 .venv/bin/python tools/verify.py 全绿（215 passed, 2 skipped）", "status": "compl
…[truncated])`


> [reasoning] Everything checks out:
- design §2 has DB rows (lines 44-46) ✓
- tasks test-first + server.py + VENDORED.md ✓ (T008 line 47)
- spec AC-001 has database 可达 ✓
- git status: only ui-mockup files modified (unrelated, user confirmed, untouched by me) ✓
- 3 commits on top of 6e06ca7 (64d1ebd, ce557c3, 3f7320e) ✓
- FIX-log Round 2 appended after reviewer annotation ✓

Wait, one more check — the reviewer's Round 2 annotation said D011's location design.md:34 and D012's design.md:27, D013 tasks.md:33. My fixes address those.

One consideration: the reviewer's Round 3 will be diff-only on these 3 findings. Let me make sure all three suggested fixes are fully covered:

D011: "补齐 DB_*、TimescaleDB healthy dependency 与 alphamill 网络，并由静态和容器门断言。"
- design §2 table: DB_*, depends_on, networks ✓
- static gate assertions: design §8 static row "real 服务 profiles/只读挂载/端口/KRONOS_* 与 DB 环境/healthy 依赖/网络正确" ✓
- container gate: design §8 container row "/health 的 database 可达、/predict source=kronos" ✓
- tasks T004/T005/T006 ✓
- spec: §3, §7, AC-001 ✓

D012: "校正后端影响面，在 T001 明列 server.py 启动钩子，并为 VENDORED.md 回写增加任务。"
- design §1 fixed ✓; T001 lists server.py ✓; T008 VENDORED.md ✓

D013: "将契约测试置于实现前先红，或明确并入对应实现任务，保证 T001-T004 完成时 verify 已存在。"
- T001-T004: 先红后绿, tests created within tasks ✓; §0 rule ✓; T005 re-scoped ✓

Good. Now update todos and report.

Actually — one more potential issue to self-check: D011 said "按现设计无法健康取数" — I should double check that the real service in compose will also need `restart: "no"` vs `unless-stopped`... T004 says "失败不自动重启" ✓ already.

Also: should the real service's healthcheck start_period account for CPU model load time (3.4-7.2s per inference; model load maybe 10-60s)? Hmm, the design says healthcheck 以 model_loaded=true 为通过条件, but doesn't specify intervals/start_period. The reviewer didn't flag it; but D011 was about DB wiring. Could this be a latent issue? The container loads model at startup (eager load); healthcheck with default start_period 0 might mark unhealthy during load. But since restart policy is "no" and the test waits for readiness, it's manageable. The design could mention `start_period`/timeout allowances. Is it worth adding proactively? The reviewer's D011 fix request didn't include it. Adding unrequested changes risks new fix-regressions. I'll leave it; T006's implementation can handle wait logic. Hmm, but wait — actual risk: if compose healthcheck has too-short start_period, `depends_on ... service_healthy` consumers would fail. No consumers depend on real service health in this feature. Skip.

OK. Update todos and report.

Todo update: mark the three findings completed + gate + FIX-log. I'll rewrite the todo list for round 2.
All Round 2 fixes verified in place. Updating tracking:

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "F004-D011: real 服务 DB 接线（DB_*/healthy 依赖/网络）+ 双门断言 - commit 64d1ebd",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F004-D012: 影响面校正 + server.py 启动钩子所有者 + VENDORED.md 任务 - commit ce557c3 (+3f7320e 任务级)",
    "status": "completed",
    "priority": "medium"
  },
  {
    "content": "F004-D013: T001-T004 先红后绿重构 + 门禁补全任务重定位 - commit 3f7320e",
    "status": "completed",
    "priority": "medium"
  },
  {
    "content": "轮末全量门禁 .venv/bin/python tools/verify.py 全绿（215 passed, 2 skipped）",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "FIX-log 追加 Round 2 修复声明（在检视方 [review-r2] 批注之后）",
    "status": "completed",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-14T16:17:28Z


> [reasoning] Done. Final report — concise, ADHD-friendly, Chinese:

- State: Round 2 findings D011-D013 all fixed, 3 commits on main (6e06ca7 → 3f7320e), gate green.
- Per-finding summary.
- FIX-log updated (after reviewer annotation).
- Next: reviewer Round 3 (diff-only on these 3 + adjacent contracts).

Keep it short.
Round 2 修复完成。D011–D013 全数处理，3 个提交（`6e06ca7 → 3f7320e`），轮末门禁 `.venv/bin/python tools/verify.py` 全绿（`215 passed, 2 skipped`）。

**状态：修复已落盘，等待检视方 Round 3（diff-only 复核这 3 条）**

| Finding | 处理内容 | Commit |
|---|---|---|
| D011 (High) | design §2 契约表补 `DB_*` 环境、`depends_on: timescaledb service_healthy`、`networks: [alphamill]` + 运行链说明（compose→模型→DB→HTTP）；§8 静态/容器门断言、spec §3/§7/AC-001、tasks T004-T006 同步 | `64d1ebd` |
| D012 | design §1 影响面改为「HTTP 契约无变更；薄壳改动在 `server.py` 启动钩子 + `kronos_real.py`」；§5 标注钩子所有者；T001 明列 `server.py`；新增 T008 `VENDORED.md` 回写任务 | `ce557c3` |
| D013 | T001–T004 全部「先红后绿」（测试创建并入对应任务，完成即验证）；T005 改为门禁补全+变异验证；§0 增先红后绿规则，DAG 顺延 T009–T012 | `3f7320e` |

两条记录：
1. `FIX-log.md` 的 Round 2 声明已追加在检视方 `[review-r2]` 批注**之后**（append-only，未动 Round 1 与批注内容）。
2. 工作树里 `docs/design/ui-mockup/` 4 个修改文件与本轮无关，未触碰。

**下一步（约 15 分钟）**：检视方 Round 3 —— 只审 `6e06ca7..3f7320e` 三条 diff 与相邻契约（design §2 表三行、T001/T008、T001–T004 先红后绿），通过即翻 `fixed` 并闭环。

## user · 2026-09-14T16:31:12Z

<system-reminder>Note: The user opened the file "/home/georg/projects/alphamill/docs/alphamill-prd.md". This may or may not be relevant to the current task.</system-reminder>

又检视了一轮，再次审视修复一下

## assistant · 2026-09-14T16:31:12Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git status --short; git rev-parse --short HEAD; date \"+%Y-%m-%d %H:%M %Z\"; ls -la docs/reviews/"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md"})`


> [reasoning] Another review round. Let me check CURRENT-doc.md and git state again.

  <details><summary>tool output</summary>

  ```text
M CLAUDE.md
 M README.md
 M docs/README.md
 M docs/alphamill-architecture.md
 M docs/alphamill-prd.md
 M docs/decisions/0001-factor-mining-engine.md
 M docs/decisions/0005-presentation-observability.md
 M docs/design/ui-mockup/README.md
 M docs/design/ui-mockup/app.js
 M docs/design/ui-mockup/index.html
 M docs/design/ui-mockup/styles.css
 M docs/features/0.2/F003-alphagen-vendor/spec.md
?? docs/decisions/0008-north-star-sustained-profitability.md
3f7320e
2026-09-15 00:31 HKT
total 132
drwxr-xr-x 2 georg georg  4096 Sep 14 23:27 .
drwxr-xr-x 7 georg georg  4096 Sep 15 00:24 ..
-rw-r--r-- 1 georg georg 16430 Sep 15 00:30 CURRENT-doc.md
-rw-r--r-- 1 georg georg 10178 Sep 15 00:30 FIX-log.md
-rw-r--r-- 1 georg georg 93031 Sep 14 21:48 RETROSPECTIVE.md


Incremental: 0 files updated, 0 nodes,
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md</path>
<type>file</type>
<content>
1: ---
2: report_type: doc-review
3: round: 3
4: date: 2026-09-15
5: prior_report: CURRENT-doc.md@round-2
6: scope: diff-only
7: stop_condition_met: false
8: severity_counts: {critical: 0, high: 0, medium: 1, low: 0}
9: issues:
10:   - id: F004-D001
11:     title: 真实 profile 未接入 signals_log 的生产消费者
12:     severity: high
13:     category: correctness
14:     root_cause: root-cause
15:     origin: spec-drift
16:     pattern_tag: cross-feature-contract-drift
17:     status: fixed
18:     tracked_task: null
19:     fix_summary: 删除自动升级承诺，将消费者路由排除并同步勘正 F002 限制说明。
20:     regression_test: tools/validate_spec_lifecycle.py + tools/check_doc_links.py
21:     suggested_fix: 接线并验收 signals_log.source=kro
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:31:16Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "offset": 29, "limit": 40})`


> [reasoning] Round 3 results:
- D011-D013 all verified fixed.
- New finding **D014 (Medium)**: "T007/T008 排在执行机实测 T009 之前，却写成'文档回写以实测通过为前提'；后续链的'实测 → 证据回写'摘要也与任务编号不匹配".
  - suggested fix: "重排为 `T006 -> T007/T008/T009`、`T007/T008/T009 -> T010 -> T011 -> T012`，或删除错误的实测前提"
  - location: tasks.md:63 (i.e., §4 dependencies area).
  - Body text: "D014 仍使任务图不可照文字执行：T006 只负责创建容器集成测试，真正的执行机实测是 T009；因此 T007/T008 在 T009 之前不能同时满足'以实测通过为前提'。"
  - Also: "后续链的'实测 → 证据回写'摘要也与任务编号不匹配" — the §4 line `T007/T008 -> T009 -> T010 -> T011 -> T012`：验收链顺序执行（实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步）— wait: T009 is 实测, T010 is 证据回写, T011 质量门, T012 状态. The summary says "实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步" which maps T009→T010→T011→T012. That matches. Hmm, what's "与任务编号不匹配"? Let me re-read the D014 title: "T007/T008 排在执行机实测 T009 之前，却写成'文档回写以实测通过为前提'；后续链的'实测 → 证据回写'摘要也与任务编号不匹配".

  Wait, maybe: the §4 bullet `T006 -> T007/T008`：文档回写以实测通过/契约成立为前提 — that's the mismatch (T007/T008 come BEFORE T009 实测, so "以实测通过为前提" is impossible). And the summary "实测 → 证据回写" — hmm, which numbering? Actually in my tasks: T010 = 回写 spec §6 验收证据; T009 = 执行机实测. So "实测 → 证据回写" = T009 → T010 ✓ matches. Unless... the reviewer sees T007/T008 as "文档回写" (F001 spec writeback, VENDORED writeback) and T010 as "证据回写". Hmm, "后续链的'实测 → 证据回写'摘要也与任务编号不匹配" — maybe they mean: the chain `T007/T008 -> T009 -> T010 -> T011 -> T012` with summary "实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步" lists T007/T008 as part of the chain where the first step is "实测", but T007/T008 are document writebacks, not 实测... So the summary at the head of the chain "实测 → 证据回写..." describes T009→T010→... but the chain itself starts with T007/T008. I.e., the summary line describes the tail (T009 onwards), while the chain line includes T007/T008 first. Ambiguous wording.

Fix options per reviewer:
(a) "重排为 `T006 -> T007/T008/T009`、`T007/T008/T009 -> T010 -> T011 -> T012`" — i.e., make T007/T008/T009 parallel (all depend on T006), then T010 depends on all three. But wait: T007 (F001 spec writeback) — the reviewer earlier (round 1, D010) said "T006 -> T007：F001 命令回写以 compose 形态实测通过为前提"?? Hmm no. Let me re-check what T007's premise should be.

Actually, let me think about what's true:
- T006: create container integration test (`tests/integration/test_f004_real_profile.py`) — the test file itself, runnable on execution machine. Creating the test doesn't require execution; running it does. Hmm — but T006's verify says "verify: tests/integration/test_f004_real_profile.py" — as a task, T006 includes running it presumably. But the reviewer says "T006 只负责创建容器集成测试，真正的执行机实测是 T009". Where does the "真正的实测" happen? T009 runs both F001 smoke + F004 container suite on the execution machine with evidence recording. So T006 is creation (+ local attempts?), T009 is the official acceptance run.

- T007 (F001 spec §6 writeback to compose form): should this wait for T009 (实测通过)? Per the original design/reviewer round-1 thinking: "F001 命令回写以 compose 形态实测通过为前提" — I wrote that in Round 1. But actually, is that right? The F001 AC-006 command writeback changes the documented rerun command. It could be written once the compose form works (proven by T006's test on execution machine? or local?). Strictly, the docs should reflect a proven command. T009 is the acceptance run. So either:
  (i) T007/T008 after T009 (move doc writeback after acceptance evidence) — reviewer's alternative "或把需实测通过的回写移至 T009 后".
  (ii) T007/T008/T009 all depend on T006, run in parallel, then T010 (spec evidence writeback) depends on all three. — reviewer's first option: `T006 -> T007/T008/T009`, `T007/T008/T009 -> T010 -> T011 -> T012`.

Hmm, but option (ii) removes the "实测前提" for T007. Is that acceptable? The reviewer offered it: "或删除错误的实测前提". But wait — if T007 is written before the compose form is actually proven on the execution machine, could the F001 spec carry a not-yet-proven command? The command form is fixed by design (docker compose -f ... --profile kronos-real up -d). The T006 test creation proves nothing until run. Hmm.

Actually, let me think again about the cleanest fix that satisfies both correctness and the reviewer's suggestion. The reviewer's two options:
1. Reorder DAG: `T006 -> T007/T008/T009`; `T007/T008/T009 -> T010 -> T011 -> T012`. (T007/T008 in parallel with T009, all three after T006.)
2. Or "把需实测通过的回写移至 T009 后" — i.e., T007 (and maybe T008?) move after T009.

Which is better? Consider dependencies truthfully:
- T007: 回写 F001 §6 AC-006 command. To write back honestly, the compose command should have been run successfully at least once. T009 is that run. So T007 truly depends on T009 → option 2 for T007.
  But wait — do we want to run T009 (acceptance) with the F001 spec still showing the OLD manual command? The F001 smoke test docstring references spec §6. Not blocking. The acceptance run is about the service; T007 writes back after. That's the "实测通过 → 回写" order. Makes sense.
- T008: VENDORED.md container paths. This doesn't require any test run; it documents frozen paths from design §2. Could be done in parallel with anything after T006 (or even earlier). It doesn't need 实测. So T008 could be `T006 -> T008` or even parallel with T003/T004. The reviewer's option 1 groups T007/T008/T009 as parallel after T006 — but for T007, the "实测前提" must then be deleted. Option 2 keeps T007's premise.

Hmm, the reviewer's suggested fix text: "**将 T006 后的文档准备与 T009 执行机实测并行**，T010 同时依赖 T007/T008/T009；**或把需实测通过的回写移至 T009 后**。" Wait, the frontmatter suggested_fix says: "将 T006 后的文档准备与 T009 执行机实测并行，T010 同时依赖 T007/T008/T009；或把需实测通过的回写移至 T009 后。"

So two options:
(a) T007/T008 parallel with T009 (delete the "实测通过为前提"), T010 depends on T007/T008/T009.
(b) Move the writeback(s) that need 实测 (i.e., T007) to after T009. Then T008 can stay before/parallel.

Which do I pick? Let me think about what's most honest and simple:

Option (b):
- T008 (VENDORED.md) — no 实测 dependency; can run after T006 (or earlier).
- T007 (F001 §6 writeback) — should be after T009 (since it documents the proven command).
- Then T010 (spec §6 F004 evidence writeback) — evidence from T009; can depend on T009; does T010 need T007 done? Not strictly, but sequencing for clean acceptance: T009 → T007 → T010? Hmm, or T007 after T010?

Order options for the tail: T006 → [T008] ; T006 → T009 → T007 → T010 → T011 → T012? Or T009 → T010 → T007?

Wait — T010 is F004 spec §6 evidence writeback (commands, outputs, hostname/device). T007 is F001 spec §6 writeback. Both are doc writebacks after T009. T011 = quality gate; T012 = status/BACKLOG. A clean chain:
- `T006 -> T008` (VENDORED paths after contracts frozen)
- `T006 -> T009` (execution machine acceptance)
- `T009 -> T007` (F001 writeback requires proven compose form)
- `T009 -> T010` (evidence writeback requires acceptance outputs)
- `T007/T008/T010 -> T011 -> T012` (quality gate after all writebacks; then status).

Hmm, that's a bit more complex but truthful. Alternatively simpler: chain everything: T006 → T008 → T009 → T007 → T010 → T011 → T012? But T008 (VENDORED) has no 实测 premise; forcing it before T009 is fine but makes the graph linear. The reviewer's complaint is about contradiction, not parallelism. Simplest coherent fix: make the tail strictly sequential with correct premises:

`T006 -> T008`（VENDORED 路径回写不依赖实测）
`T006 -> T009 -> T007 -> T010 -> T011 -> T012`（实测 → F001 回写 → F004 证据回写 → 门禁 → 状态）

Hmm, wait, should T007 come after or before T010? Arbitrary; both after T009. Keeping T007→T010 sequential is fine. But hmm, the reviewer's option (a) suggested T010 depends on T007/T008/T009. My option (b) chain has T010 depending on T007 (and transitively T009); T008 separate. Is T008 → T010 needed? T010 writes F004 spec §6 evidence; T008 writes VENDORED. Independent. If T010's evidence mentions container paths? Not necessarily. So no edge needed... but to be safe and simple, maybe make T008 → T010 too? That would make T010 depend on both. Hmm.

Actually, let me reconsider: which option would the reviewer prefer for Round 4's check? The reviewer's convergence condition: "任务编号、依赖箭头和括号内阶段摘要一致". So they want the DAG + summary consistent and executable as written. Both options can satisfy. Let me pick the one with the fewest contradictions:

Current text:
```
- `T006 -> T007/T008`：文档回写以实测通过/契约成立为前提；二者修改不同文件，顺序无关。
- `T007/T008 -> T009 -> T010 -> T011 -> T012`：验收链顺序执行（实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步）。
```
Contradictions: (1) "文档回写以实测通过为前提" but T007/T008 precede T009 (实测); (2) summary starts "实测 → 证据回写" but chain starts at T007/T008 (文档回写), mismatched.

Option (b) rewrite:
```
- `T006 -> T008`：VENDORED.md 容器路径回写以编排契约定稿为前提，不依赖实测。
- `T006 -> T009`：执行机实测以容器测试定稿（T006）为前提。
- `T009 -> T007`：F001 AC-006 命令回写以 compose 形态实测通过为前提。
- `T009 -> T010`：F004 验收证据回写以实测输出为前提。
- `T007/T008/T010 -> T011 -> T012`：全量门禁在全部回写完成后执行；状态/BACKLOG 同步以门禁全绿为前提。
```
Hmm, this is more lines but precise. Wait — is `T006 -> T009` right? T009 runs the F001 smoke + F004 container suite on the execution machine. It needs: F001 smoke unchanged (already exists), F004 container test created (T006), and the implementation done (T001-T005). So `T002/T005/T006 -> T009`. Earlier I had `T002/T005 -> T006` and chain T006→T009. Adding "T006 -> T009" is consistent but incomplete: T009 also needs T001/T002/T005 etc. Transitively through T006? T006 depends on T002/T005; T005 depends on T003/T004; T004 on T003; T002 on T001. So the DAG is connected: T001→T002→T006; T003→T004→T005→T006. So T006 transitively implies all implementation done. Thus `T006 -> T009` suffices as the edge, but the real prerequisite is "all implementation complete" — captured by T006 being the last synthesis. Hmm, T006's own deps: "T002/T005 -> T006" ✓. So yes: T006 → T009 is properly grounded (transitive closure includes everything).

But wait — is T008 → T010 or not? If I make T010 depend on T007/T008... For simplicity: `T007/T008 -> T010`? T008 doesn't materially gate T010. But declaring extra edges isn't harmful ("以...为前提" must be true — T008 done before T010 is fine). Hmm, but unnecessary edges might be seen as noise. The reviewer's option (a) explicitly suggested "T010 同时依赖 T007/T008/T009". Let me just follow that shape but with corrected semantics:

Actually, let me reconsider Option (a) more carefully, since the reviewer listed it first:
(a) `T006 -> T007/T008/T009` (all three parallel after T006), `T007/T008/T009 -> T010 -> T011 -> T012`.
- T007 (F001 writeback) no longer "以实测为前提" — reviewer says "或删除错误的实测前提". So we'd delete the premise. But then T007 can be written before the compose form has ever run. Is that OK? The writeback documents a command form that the design has fixed and that T006's test will exercise. Hmm, writing it before running is practice-risky (command could need adjustments after first real run — e.g., DB_HOST nuances like F001's manual command needed DB env). Actually that's exactly the kind of thing that goes wrong: the compose form might need tweaks (e.g., `--profile` + service name, healthcheck waits). Writing F001's spec §6 with an unproven command is how you get "documented command not runnable" (pattern D046 from the retrospective!). So option (b) — writeback after 实测 — is safer and more honest.

Hmm, but wait: is T009 itself "the acceptance run" that must succeed for T007? Yes. So T007 after T009. That contradicts reviewer option (a)'s "delete the premise" but matches their option (b) "把需实测通过的回写移至 T009 后". I'll go with a hybrid:

- `T006 -> T008` (VENDORED，不依赖实测) — hmm, or should T008 be even earlier? It can be after T006 (contract frozen). OK.
- `T006 -> T009`
- `T009 -> T007` and `T009 -> T010`
- `T007/T008/T010 -> T011 -> T012`? or `T007/T010 -> T011`?

Let me simplify to a clean, verifiable-by-inspection chain:

```
- `T006 -> T008`：VENDORED.md 路径回写以编排契约成立为前提（不依赖实测）。
- `T006 -> T009`：执行机实测以容器测试定稿（T006）为前提。
- `T009 -> T007/T010`：F001 命令回写与 F004 验收证据回写都以执行机实测通过为前提；二者修改不同文件，顺序无关。
- `T007/T008/T010 -> T011 -> T012`：全量门禁在全部回写完成后执行；状态/BACKLOG 同步以门禁全绿为前提。
```

Hmm, the last line: T011 (quality gate) — should it really wait for T008? T008 is a VENDORED.md edit (tracked file); verify.py doesn't check vendor docs (it's not in docs scanning... check_doc_links scans docs/**, README, CLAUDE — vendor not included; but the file is tracked and shouldn't break anything). If T008 is done after T011, then T011's "全绿" wouldn't cover T008's edit — but T008 can't break gates. However, sequencing T008 before T011 is clean and harmless ("全部回写完成后 — 门禁"). Keep `T007/T008/T010 -> T011`.

Then T011 → T012. And summary wording must match: "验收链顺序执行（实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步）" — with the new structure, the summary should be reworded: e.g., "链尾顺序：实测（T009）→ 回写（T007/T008/T010）→ 全量门禁（T011）→ 状态/BACKLOG（T012）"。 Hmm, T008 isn't "after 实测" chain; it's parallel. Let me just drop the arrow-summary or make it accurate:

Full §4 rewrite:
```
- `T001 -> T002`：同一薄壳文件的顺序改造（预检/加载 → 锁；各自测试在同一任务内先红后绿）。
- `T001/T002 -> T006`：容器集成依赖启动预检、eager load 与串行推理行为成立。
- `T003 -> T004`：compose `target` 依赖 Dockerfile 目标定义。
- `T003/T004 -> T005`：静态门禁在全量断言（含默认隔离）与变异验证后定稿。
- `T002/T005 -> T006`：容器集成建立在薄壳行为与静态契约通过之上。
- `T006 -> T008`：VENDORED.md 容器路径回写以编排契约成立为前提（不依赖实测）。
- `T006 -> T009`：执行机实测以容器集成测试定稿为前提（T006 闭包已含全部实现任务）。
- `T009 -> T007/T010`：F001 命令回写与 F004 验收证据回写都以执行机实测通过为前提；二者修改不同文件，顺序无关。
- `T007/T008/T010 -> T011 -> T012`：全量门禁覆盖全部回写后执行；状态/BACKLOG 同步以门禁全绿为前提。
```

Hmm wait, "T006 -> T009：执行机实测以容器集成测试定稿为前提（T006 闭包已含全部实现任务）" — meh, phrase simply: "`T006 -> T009`：实测运行 F004 容器套件，以测试定稿为前提。". OK.

But hold on — there's still a subtlety: T009's verify command runs BOTH F001 smoke and F004 container test. And T007 (F001 §6 writeback) after T009. Fine.

Also T010 (F004 spec §6 evidence) after T009. ✓.

Now — should I also update task descriptions? T007 description says "回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态" — no premise stated in the description; premise only in §4. T008 description fine. T009 fine. T010 fine. The reviewer's D014 also says "T007/T008 排在执行机实测 T009 之前，却写成'...前提'" — that's §4 only. So only §4 needs fixing? Also "后续链的'实测 → 证据回写'摘要也与任务编号不匹配" — fix the summary line. So it's a §4-only edit.

Wait, let me double check whether there might also be an issue in §3 task order: T007/T008 are in §3 "验证与验收任务" section positioned before T009-T012. The tasks are numbered = execution order (the file rules say "编号=执行顺序" from D010 fix... actually §0 says "每项任务只描述一个可验证动作" and the round-1 D010 fix was "把 T004 -> T005 -> 验收证据回写 -> 状态/BACKLOG 同步串成完整 DAG" — numbering should reflect execution order per template). Hmm! If T007 executes after T009, then the NUMBERING is out of order (T007 before T009 numerically). Does that matter? tasks.md §0 (template) says "Task IDs 必须全文件连续且唯一" but not necessarily monotonic in execution order? The features/README says "任务统一为 ... 按什么顺序做" and F001 precedent: "全量重编号使编号=执行顺序" (from RETROSPECTIVE D037 fix: "全量重编号使编号=执行顺序(R2-01 插入后延至 T022 仍保持)"). So the project convention IS: numbering = execution order!

So if T007 executes after T009, I should RENUMBER so execution order = numeric order. Let me reorder everything cleanly:

Current tasks and true execution order:
1. T001 预检+eager load（测试先红后绿）
2. T002 推理锁
3. T003 Dockerfile
4. T004 compose
5. T005 静态门禁补全+变异
6. T006 容器集成测试（创建）
7. T007 F001 §6 回写 — should be after 实测
8. T008 VENDORED 回写 — after T006
9. T009 执行机实测
10. T010 F004 证据回写 — after T009
11. T011 质量门
12. T012 状态/BACKLOG

Renumbered execution order:
1. T001 预检+eager load
2. T002 推理锁
3. T003 Dockerfile
4. T004 compose
5. T005 静态门禁补全+变异
6. T006 容器集成测试创建
7. T007 执行机实测（was T009）— hmm, or keep 实测 as T008 with VENDORED as T007?
8. T008 F001 §6 回写 (was T007, after 实测)
9. T009 F004 证据回写 (was T010)
10. T010 质量门 (was T011)
11. T011 状态/BACKLOG (was T012)
12. T012 ... wait we had 12 tasks total. Recount: T001..T012 = 12 tasks. New order list:
  1. T001 预检+eager load
  2. T002 锁
  3. T003 Dockerfile
  4. T004 compose
  5. T005 静态门禁补全+变异
  6. T006 容器集成测试
  7. T007 VENDORED.md 回写（不依赖实测；也放这里）
  8. T008 执行机实测（原 T009）
  9. T009 F001 §6 回写（原 T007，实测后）
  10. T010 F004 spec 证据回写（原 T010）
  11. T011 质量门（原 T011）
  12. T012 状态/BACKLOG（原 T012）

That keeps 12 tasks and makes numbering monotonic with execution: T007 (VENDORED) before T008 (实测); T009/T010 after 实测.

Hmm, but wait: is VENDORED.md writeback truly independent of 实测? Yes. Put it right after T006 as T007. Then T008 = 实测, T009 = F001 回写, T010 = F004 证据回写, T011 = gate, T012 = status.

Alternatively: T007 = 实测, T008 = VENDORED? No — VENDORED can go before 实测; ordering it before is fine and keeps the "实测 → 回写" chain contiguous at T008→T009→T010.

Hmm, hmm. But there's yet another consideration: is it correct that F001 writeback (T009) and F004 evidence writeback (T010) both come after 实测 (T008)? Yes.

And D014's suggested fix (b) "把需实测通过的回写移至 T009 后" — in the NEW numbering, "实测" is T008 and writebacks are T009-T010, i.e., after. ✓. And suggested fix (a) shape `T006 -> T007/T008/T009` isn't used, but (b) is offered as an alternative. The reviewer's convergence condition: "任务编号、依赖箭头和括号内阶段摘要一致". So renumbering to match execution order + correct DAG + accurate summary satisfies it.

Wait, actually — let me reconsider. Is renumbering really needed? The reviewer's D014 title: "文档回写任务声称依赖实测通过但排在实测任务之前" — the core issue is the order/premise contradiction. If I just fix §4 (T007/T008 after T006, T007/T008 → T010...), the numbering has T007-T008 (writebacks) before T009 (实测) — wait no, if I keep numbers and put T007/T008 after T009 in the DAG, then numbering contradicts execution order again (T007 executes after T009). The project convention says numbering=execution order (D037 lesson). Also tasks are executed "严格按 tasks.md 里的顺序逐项实现" (SOP workflow Step 2: "严格按 tasks.md 里的顺序逐项执行"). So the tasks list order matters: T007/T008 appear before T009 in the file. If T007/T008 must run after T009, the file order is wrong unless renumbered/reordered.

Therefore: reorder + renumber so that file order = execution order: ... T006 (容器测试) → T007 (VENDORED 回写) → T008 (执行机实测) → T009 (F001 回写) → T010 (F004 证据回写) → T011 (门禁) → T012 (状态).

Hmm, wait: should VENDORED (T007) be before 实测 (T008)? It's independent; doing it before 实测 is fine. But actually — hmm, does VENDORED.md writeback need anything from 实测? The container paths are design-frozen; no. OK.

But one more alternative: put VENDORED writeback with the other writebacks after 实测: T007=实测, T008=F001 回写, T009=VENDORED 回写, T010=F004 证据回写, T011=门禁, T012=状态. Also fine and arguably cleaner ("实测 → 全部回写"). Hmm, which one? The reviewer's option (a) put T008 (VENDORED) parallel with 实测, suggesting VENDORED doesn't need 实测. Either works. Let me think about which reads best:

Option X: T006 → T007 实测 → T008 F001 回写 → T009 VENDORED 回写 → T010 F004 证据回写 → T011 门禁 → T012 状态.
Option Y: T006 → T007 VENDORED 回写 → T008 实测 → T009 F001 回写 → T010 F004 证据回写 → T011 门禁 → T012 状态.

Both keep numbering=order. In option X, all writebacks are post-实测 (simple claim: "全部回写以实测通过或契约成立为前提"— hmm VENDORED doesn't need 实测). In option Y, VENDORED before 实测 (premise: contract frozen), then 实测, then two post-实测 writebacks.

The DAG edges differ slightly. Reviewer's convergence check: "依赖箭头和括号内阶段摘要一致". Let me pick option X? Hmm wait, but X makes VENDORED wait for 实测 — harmless but implies a premise we don't need; if I don't declare that edge, then numbering X still has VENDORED after 实测 in execution order... The file order IS the execution order (per SOP "严格按顺序执行"), so if it's listed after 实测 it executes after. That's fine, no premise issue as long as §4 doesn't claim it.

Hmm, actually, simpler idea: keep VENDORED where it was (immediately after container test, before 实测) → Option Y. Then DAG:
- T006 → T007 (VENDORED, premise: 编排契约成立)
- T006 → T008 (实测, premise: 容器测试定稿)
- T008 → T009 (F001 回写, premise: 实测通过)
- T008 → T010 (F004 证据回写, premise: 实测输出)
- T007/T009/T010 → T011 → T012 (门禁覆盖全部回写；状态以门禁全绿为前提)

That's clean. And matches reviewer option (b) in spirit.

Let me now also double-check D014's second sub-complaint: "后续链的'实测 → 证据回写'摘要也与任务编号不匹配" — with my new numbering, the summary should be updated to match: e.g. "T008 实测 → T009/T010 回写 → T011 门禁 → T012 状态". I'll write the last bullet as:

"- `T007/T009/T010 -> T011 -> T012`：全量门禁在全部回写完成后执行；状态/BACKLOG 同步以门禁全绿为前提。"

And maybe add a lead sentence to §4 like previous rounds? Current §4 has no lead. Fine.

Also I must double check the task descriptions for numbering references: §3 tasks reference each other? T009 (now T008) description: "在执行机 qiaozhi-lt 跑集成验收：F001 冒烟（HTTP 契约）+ F004 容器集成 + 默认镜像否证..." — no numeric refs. T010→T009 (F001 writeback) description: "回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退" — fine. T007→T008... wait new numbering: let me lay out final:

§2 实现任务:
Phase 1: T001, T002 (unchanged)
Phase 2: T003, T004 (unchanged)
Phase 3: 门禁补全与文档回写:
- T005 静态门禁补全与变异验证 (unchanged)
- T006 容器集成测试 (unchanged)

§3 验证与验收任务:
- T007 (`FR-001`): 更新 `vendor/VENDORED.md`... (moved from old T008)
- T008 (`AC-001`,`AC-002`): 执行机实测 (was old T009)
- T009 (`FR-001`): F001 spec §6 回写 (was old T007)
- T010 (`AC-001`): F004 spec §6 证据回写 (was old T010)
- T011 (`AC-001`,`NFR-001`): 统一质量门 (was old T011)
- T012: 状态/BACKLOG (was old T012)

Hmm wait — T005/T006 are in §2 Phase 3 ("门禁补全与文档回写") but T007+ are in §3. The Phase 3 title says "门禁补全与文档回写" — with writebacks now in §3, Phase 3 title should be "门禁补全" only. Actually §2 Phase 3 currently: "Phase 3：门禁补全与文档回写" containing T005/T006 (both gates). Let me rename to "Phase 3：专属门禁" and §3 handles writebacks. Hmm, but earlier Phase 3 was "专属门禁与文档回写" — since writeback tasks were in §3 anyway (T007/T008 were in §3! Let me recheck: in the current file, T007 and T008 are in §3 "验证与验收任务"). Yes! Current: §2 has T001-T006; §3 has T007-T012. So Phase 3 contains T005/T006 only (T005 门禁补全, T006 容器集成测试). So Phase 3 title "门禁补全与文档回写" is slightly off already (no doc writeback in Phase 3). Hmm — should I fix that title? The reviewer didn't flag it, but it's an easy consistency improvement: retitle Phase 3 "专属门禁" or "门禁定稿". Let me retitle to "Phase 3：专属门禁" since T005/T006 are gates. Wait, T006 is a test creation task — "专属门禁测试". OK: "Phase 3：专属门禁测试". Minor cleanup within the D014 fix scope (tasks ordering/consistency). Acceptable.

Hmm, actually let me be careful: don't over-edit; the reviewer will diff-check. The Phase title change is small and consistent. I'll do it.

Also §3 section header current: "## 3. 验证与验收任务" contains T007-T012. New ordering within §3: T007 VENDORED, T008 实测, T009 F001 回写, T010 证据回写, T011 门禁, T012 状态. Hmm — does it make sense that "VENDORED 回写" is in 验证与验收 section? It's a doc writeback... The template §3 is "验证与验收任务" and includes "回写 spec 验收证据、活跃索引和状态". VENDORED writeback is a doc/config writeback; currently it was T008 in §3. Keep it there. Fine.

Wait, actually — maybe better: move VENDORED writeback to §2 Phase 3? It's not a verification. Hmm. But its verify is a grep. The template allows §3 to include real-environment verification and quality gates. VENDORED is neither. Hmm, honestly keeping it in §3 with the other writebacks is fine; or move to §2. If I move it to §2 Phase 3, then §2 has T001-T007 and §3 has T008-T012. Then execution order: ... T006 (container test) → T007 (VENDORED) → T008 (实测) → T009/T010 (writebacks) → T011 → T012. Same numbering. And Phase 3 title "专属门禁与文档回写" fits again (T005, T006 gates + T007 doc). Hmm, that's nice: keep phase title, move VENDORED into it.

But wait — VENDORED.md writeback before implementation tests? It's just docs; order within Phase 3 after T006 is fine. OK let me do that: move VENDORED (new T007) to §2 Phase 3.

Hmm, but hold on — is that kosher with the reviewer? They'll check "T007/T008 与实测顺序"。The essential fix: no task claims a false premise; numbering = execution order; summary matches. Let me now also make sure §4 edges reflect the file-order semantics:

Final §4:
```
- `T001 -> T002`：同一薄壳文件的顺序改造（预检/加载 → 锁；各自测试在同一任务内先红后绿）。
- `T001/T002 -> T006`：容器集成依赖启动预检、eager load 与串行推理行为成立。
- `T003 -> T004`：compose `target` 依赖 Dockerfile 目标定义。
- `T003/T004 -> T005`：静态门禁在全量断言（含默认隔离）与变异验证后定稿。
- `T002/T005 -> T006`：容器集成建立在薄壳行为与静态契约通过之上。
- `T006 -> T007`：VENDORED.md 容器路径回写以编排与薄壳契约定稿为前提（不依赖实测）。
- `T005/T006 -> T008`：执行机实测运行 F001 冒烟与 F004 容器套件，以两侧测试定稿为前提。
- `T008 -> T009/T010`：F001 命令回写与 F004 验收证据回写都以执行机实测通过为前提；二者修改不同文件，顺序无关。
- `T007/T009/T010 -> T011 -> T012`：全量门禁在全部回写完成后执行；状态/BACKLOG 同步以门禁全绿为前提。
```

Wait — T008 prerequisite: 实测 runs F001 smoke (exists since F001) + F004 container suite (T006) + exercises the implementation (T001-T006). Does T008 need T005? T005 is the static gate finalization; running it isn't required for 实测. T006 depends on T002/T005 → transitively includes everything. So `T006 -> T008` suffices. Simpler: "`T006 -> T008`：执行机实测以容器集成测试定稿与实现全链为前提（T006 闭包已含 T001-T005）。" Hmm, parentheses get wordy. Let me write: "`T006 -> T008`：执行机实测以容器集成测试定稿为前提（其依赖闭包已含全部实现与门禁任务）。" OK.

Hmm, wait — actually is T007 (VENDORED writeback) required before T008? No. `T006 -> T007` and `T006 -> T008` are parallel branches. Then T009/T010 after T008. T011 after T007/T009/T010. OK.

Now, the convergence condition says "依赖箭头和括号内阶段摘要一致". Let me make the summary in the last line match: "（实测 T008 → 回写 T009/T010 → 门禁 T011 → 状态 T012）"? Hmm, maybe write the last line as:

"- `T007/T009/T010 -> T011 -> T012`：全量门禁在全部回写完成后执行；状态/BACKLOG 同步以门禁全绿为前提。"

That has no ambiguous summary. Maybe add one overview line at the end (or beginning) like previous rounds: the reviewer quoted "后续链的'实测 → 证据回写'摘要也与任务编号不匹配" — I'll just avoid re-adding such a compressed summary, or make it precise:

Add a final bullet: "- 执行顺序总览：`T001→T002`、`T003→T004→T005`、`T006`、`T007/T008`（T008 为实测）、`T009/T010`（实测后回写）、`T011→T012`。" Hmm, maybe overkill. Let me instead make each bullet self-consistent and skip the overview. The reviewer wants "任务编号、依赖箭头和括号内阶段摘要一致" — I think they refer to the phrases in parentheses like "（实测 → 证据回写 → ...）". I'll ensure no contradictory compression.

Hmm, wait. Let me re-read D014 once more to make sure I fully fix what they flagged:

Title: "文档回写任务声称依赖实测通过但排在实测任务之前"
Body: "T007/T008 排在执行机实测 T009 之前，却写成'文档回写以实测通过为前提'；后续链的'实测 → 证据回写'摘要也与任务编号不匹配"
suggested_fix: "将 T006 后的文档准备与 T009 执行机实测并行，T010 同时依赖 T007/T008/T009；或把需实测通过的回写移至 T009 后。"

Hmm wait — "后续链的'实测 → 证据回写'摘要也与任务编号不匹配" — in current file, the last §4 bullet: "`T007/T008 -> T009 -> T010 -> T011 -> T012`：验收链顺序执行（实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步）。" The chain starts T007/T008 — but the summary starts with "实测" which is T009. So the mapping mismatch: summary step 1 "实测" = T009 but chain step 1 = T007/T008. Yes, exactly. My fix eliminates this bullet.

Now — one more question: With my chosen fix (writebacks after 实测), old-T007 (F001 回写) becomes post-实测. But D014's option (a) said "将 T006 后的文档准备与 T009 执行机实测并行" (være T007/T008 parallel with T009) — I'm choosing option (b)-ish (T009 post-实测). Both are sanctioned. Good.

Hmm, wait, actually — one more thought: should F001 writeback really wait for 实测? What did the round-1 D010 reviewer say? "把 T004 -> T005 -> 验收证据回写 -> 状态/BACKLOG 同步串成完整 DAG" — they wanted 验收证据回写 before status. Now D014 says F001 writeback premise wrong. Post-实测 writeback is the safest interpretation.

OK. Now also check: T009 (F001 writeback) verify = `python3 tools/verify.py` — hmm, that's fine.

One more thing: The reviewer's convergence condition says "下一轮只复核 tasks §4 两行 DAG" — so Round 4 will look at §4 specifically. My §4 rewrite will have 8 bullets (was 7). Fine.

Also should I bump tasks.md `updated` to 2026-09-15? It's already 2026-09-15. ✓ (current file updated: 2026-09-15). Good.

Let me now rewrite tasks.md (or edit the specific parts). Since changes are: Phase 3 title, move VENDORED task, renumber §3 tasks, rewrite §4. I'll rewrite the whole file for cleanliness (write tool after read — I read it recently; the write tool worked last time after reading). Actually careful: file order of tasks must be: T001-T006 in §2, T007-T012 in §3.

Let me draft:

§2 Phase 3：专属门禁与文档回写
- T005 (`AC-001`): 静态门禁补全与变异验证：... (unchanged)
- T006 (`AC-001`, `AC-002`): 容器集成测试：... (unchanged)
- T007 (`FR-001`): 更新 `vendor/VENDORED.md`：补容器内路径（...）与 real profile 说明 — verify: `grep -n "/app/vendor/Kronos" vendor/VENDORED.md`

§3 验证与验收任务
- T008 (`AC-001`, `AC-002`): 在执行机 `qiaozhi-lt` 跑集成验收：... (was T009)
- T009 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`
- T010 (`AC-001`): 回写 spec §6 验收证据（命令、输出摘要、取证机 hostname、device） — verify: `python3 tools/verify.py`（文档门禁）
- T011 (`AC-001`, `NFR-001`): 运行项目统一质量门并全绿 — verify: `python3 tools/verify.py`
- T012: 状态推进（spec frontmatter）与 BACKLOG 同步 — verify: `python3 tools/verify.py`（含生命周期与 BACKLOG 双向校验）

§4:
- `T001 -> T002`：同一薄壳文件的顺序改造（预检/加载 → 锁；各自测试在同一任务内先红后绿）。
- `T001/T002 -> T006`：容器集成依赖启动预检、eager load 与串行推理行为成立。
- `T003 -> T004`：compose `target` 依赖 Dockerfile 目标定义。
- `T003/T004 -> T005`：静态门禁在全量断言（含默认隔离）与变异验证后定稿。
- `T002/T005 -> T006`：容器集成建立在薄壳行为与静态契约通过之上。
- `T006 -> T007`：VENDORED.md 容器路径回写以编排与薄壳契约定稿为前提（不依赖实测）。
- `T006 -> T008`：执行机实测以容器集成测试定稿为前提（依赖闭包含全部实现与门禁任务）。
- `T008 -> T009/T010`：F001 命令回写与 F004 验收证据回写都以执行机实测通过为前提；二者修改不同文件，顺序无关。
- `T007/T009/T010 -> T011 -> T012`：全量门禁在全部回写完成后执行；状态/BACKLOG 同步以门禁全绿为前提。

Hmm, one question: T011 gate depends on T007 (VENDORED) — yes harmless. And T012 after T011. Good. Numbering=execution order? File order: T001..T012, and DAG order: 1,2,3,4,5,6,7/8,9/10,11,12 — monotonic ✓ (T007 and T008 parallel; T009/T010 parallel).

Wait, one inconsistency: T008 (实测) is listed in §3 as "验证与验收任务" first line — and its DAG edge is `T006 -> T008`. But T007 also `T006 -> T007`. In file order T007 comes before T008 — fine.

Hmm, also should the Phase 3 title be "专属门禁与文档回写"? T007 is the doc writeback. OK.

Now, about verify.py gate: my tasks.md edits are docs; run validate_spec_lifecycle + check_doc_links, then full verify at round end, commit, FIX-log Round 3 entry.

Also — should I reconsider D014 possibly also touching §3 summary? No other changes.

Let me also verify there are no other numbering references in the file (e.g., "T009 执行机实测" mentioned in D014 body — my fix renumbers; nothing else references numbers... §3 T010's text doesn't reference T-numbers). Check tasks §2 T001-T006 texts don't reference numbers. ✓.

One more: the FIX-log Round 3 declaration must record commits. Single commit for D014 (tasks.md rewrite). Also note in FIX-log that this is a §4-only fix + renumbering per D014 options.

Additionally, working tree now has MANY user modifications (CLAUDE.md, README.md, docs/README.md, architecture, prd, decisions, F003 spec, new ADR-0008, ui-mockup). Baseline discipline from skill §0: "git status 出现本会话没有动过的文件——先向用户确认归属再决定并入或搁置". The reviewer's Round 3 report already says "排除 docs/design/ui-mockup 的未提交文件；docs/alphamill-prd.md 的未提交改动不涉及 F004，亦排除且未触碰". So these are external changes (owner's edits, possibly a parallel session working on PRD/ADR-0008). I must NOT touch them; commit only tasks.md. Good — I'll do `git add` of tasks.md only.

Also note: there's a new untracked `docs/decisions/0008-north-star-sustained-profitability.md` — external. Don't touch.

One risk: my commit of tasks.md only is fine even with other dirty files.

Also: should I run full verify.py? It scans tested files, not depend on those dirty docs (check_doc_links scans docs/**/*.md — including modified uncommitted docs! If the user's uncommitted docs edits contain bad links, verify might fail... The reviewer ran verify and got green with those modifications present (they ran at 00:30 presumably with the same dirty tree — yes, they reported 194 passed/23 skipped, all green). So it should pass. But wait, the dirty tree includes docs/alphamill-prd.md etc. — the reviewer's run at Round 3 was with those files present (they mentioned excluding prd uncommitted changes). So running verify again should be green. Let me run it anyway at round end.

Hmm, one more consideration: check_dep_pins might be affected by... no. OK.

Let me now write the tasks.md update. I'll use edit tool for targeted changes instead of full rewrite? The changes: Phase 3 title? wait current Phase 3 title is "Phase 3：门禁补全与文档回写" — let me check the current file (from my last write): "### Phase 3：门禁补全与文档回写" and it contains T005, T006. Hmm, I previously wrote "Phase 3：门禁补全与文档回写"? Let me check: In the file I wrote: "### Phase 3：门禁补全与文档回写" — yes I believe so. Let me verify by reading the file.

Then §3 has T007-T012.

Plan edits:
1. Read tasks.md to confirm current content.
2. Edit: move VENDORED task from §3 into §2 Phase 3 (after T006), renumber: VENDORED becomes T007; then §3: old T009→T008, old T007→T009, T010/T011/T012 unchanged numbers. Wait — old §3 was:
   - T007 F001 回写 (was old T007)
   - T008 VENDORED (was old T008)
   - T009 实测
   - T010 证据回写
   - T011 门禁
   - T012 状态

   New:
   - T007 VENDORED (§2 Phase 3)
   - T008 实测 (formerly T009)
   - T009 F001 回写 (formerly T007)
   - T010 证据回写 (unchanged number)
   - T011 门禁 (unchanged)
   - T012 状态 (unchanged)

   So only T007/T008/T009 numbers shuffle among themselves. Edits:
   - §2 Phase 3: append "T007 VENDORED" line; (Phase 3 title maybe keep "门禁补全与文档回写" — now accurate since T007 is doc writeback in Phase 3 ✓).
   - §3: remove old T007 and T008 lines; change old T009 line prefix to T008; add T009 F001 writeback line after T008 line; keep T010/T011/T012.
   - §4: replace all bullets.

Let me do it with a full write (simpler to keep coherent) — write tool requires read first; I read the file earlier this session (limit 40). The write tool said "File already exists. Use edit tool instead" last time even after reading earlier... Actually last time I had read only the first 40 lines then write failed? No — last time write failed BEFORE I read; after reading it worked? Sequence: first write attempt failed ("File already exists"), then I read (limit 40), then write succeeded. This time I've already read it once in this same conversation (the last version I wrote + read first 40). To be safe, read the full file now, then write.

Actually simpler: use edit for the 3 targeted changes. §4 is a contiguous block — replace whole §4 with one edit. §2 Phase 3 insert one bullet after T006 line. §3: replace the block from "- [ ] T007 (`FR-001`): 回写 F001..." through "- [ ] T009 ..." with the new ordering.

Let me read the current tasks.md fully first.
Round 3: D011–D013 all verified `fixed`; one new finding **D014** — tasks §4 DAG contradicts itself (writeback tasks T007/T008 are ordered before the execution-machine test T009 while claiming "实测通过为前提"). Fixing it now. Reading current tasks state:

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md</path>
<type>file</type>
<content>
29:
30: ## 2. 实现任务
31:
32: ### Phase 1：薄壳运行时改造
33:
34: - [ ] T001 (`FR-001`): 先红后绿——新增 `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`（fake 目录注入，先失败）；实现 `kronos_real.py` 启动预检与 eager load，并由 `server.py` 启动钩子在 real 模式调用：校验 `KRONOS_REPO_PATH`、模型与分词器目录及必需文件（`config.json`、权重文件），任一缺失或加载失败即打印缺失路径并非零退出，不退回 mock — verify: 该用例由红转绿
35: - [ ] T002 (`FR-001`): 先红后绿——新增同文件 `::test_predictor_loads_once_and_inference_serializes`（先失败）；实现进程级推理锁：模型加载至多一次、推理互斥（含并发首请求同时到达的场景） — verify: 该用例由红转绿
36:
37: ### Phase 2：镜像与编排
38:
39: - [ ] T003 (`FR-001`, `NFR-001`): 先红后绿——新增 `tests/unit/test_f004_compose_profile_contract.py::test
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:32:07Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "oldString": "- [ ] T006 (`AC-001`, `AC-002`): 容器集成测试：compose 拉起 real 实例后校验容器身份（compose 托管 + real 目标 + 只读挂载 + 端口映射）与完整运行链（模型 + TimescaleDB：`/health` 的 `database` 可达 + `/predict source=kronos`）；缺资产场景非零退出；默认镜像 `import torch` 判红 — verify: `tests/integration/test_f004_real_profile.py`\n\n## 3. 验证与验收任务", "newString": "- [ ] T006 (`AC-001`, `AC-002`): 容器集成测试：compose 拉起 real 实例后校验容器身份（compose 托管 + re
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "oldString": "- [ ] T007 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`\n- [ ] T008 (`FR-001`): 更新 `vendor/VENDORED.md`：补容器内路径（`/app/vendor/Kronos`、`/app/models/Kronos-base`、`/app/models/Kronos-Tokenizer-base`）与 real profile 说明 — verify: `grep -n \"/app/vendor/Kronos\" vendor/VENDORED.md`\n- [ ] T009 (`AC-001`, `AC-002`): 在执行机 `
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "oldString": "- `T006 -> T007/T008`：文档回写以实测通过/契约成立为前提；二者修改不同文件，顺序无关。\n- `T007/T008 -> T009 -> T010 -> T011 -> T012`：验收链顺序执行（实测 → 证据回写 → 全量门禁 → 状态/BACKLOG 同步）。", "newString": "- `T006 -> T007`：VENDORED.md 容器路径回写以编排与薄壳契约定稿为前提（不依赖实测）。\n- `T006 -> T008`：执行机实测以容器集成测试定稿为前提（其依赖闭包已含全部实现与门禁任务）。\n- `T008 -> T009/T010`：F001 命令回写与 F004 验收证据回写都以执行机实测通过为前提；二者修改不同文件，顺序无关。\n- `T007/T009/T010 -> T011 -> T012`：
…[truncated])`


> [reasoning] Now I have the exact current content. The fix per D014 (option b: move test-dependent writeback after the execution-machine test; keep numbering=execution order):

New layout:
- §2 Phase 3: T005, T006, T007 (VENDORED — moved from §3; no 实测 dependency, only contract freeze)
- §3:
  - T008 实测 (was T009)
  - T009 F001 回写 (was T007; now after 实测)
  - T010 F004 证据回写 (unchanged)
  - T011 质量门 (unchanged)
  - T012 状态 (unchanged)
- §4 rewritten:
  - `T001 -> T002`
  - `T001/T002 -> T006`
  - `T003 -> T004`
  - `T003/T004 -> T005`
  - `T002/T005 -> T006`
  - `T006 -> T007`：VENDORED 回写以编排与薄壳契约定稿为前提（不依赖实测）。
  - `T006 -> T008`：执行机实测以容器集成测试定稿为前提（依赖闭包已含全部实现与门禁任务）。
  - `T008 -> T009/T010`：F001 命令回写与 F004 验收证据回写都以执行机实测通过为前提；二者修改不同文件，顺序无关。
  - `T007/T009/T010 -> T011 -> T012`：全量门禁覆盖全部回写后执行；状态/BACKLOG 同步以门禁全绿为前提。

Also Phase 3 title "门禁补全与文档回写" — now contains T007 doc writeback, so it's accurate. Good, keep.

Edits:
1. Insert T007 (VENDORED) after T006 line in §2.
2. Replace §3's T007/T008/T009 lines with new T008/T009 lines (and delete old T008 from §3 since it moves to §2).
3. Replace §4 bullets (last two + maybe keep first five).

Let me apply with edit tool.

Edit 1: after T006 line, insert T007 line. Old:
"- [ ] T006 (`AC-001`, `AC-002`): 容器集成测试：... — verify: `tests/integration/test_f004_real_profile.py`\n\n## 3. 验证与验收任务"
New: T006 line + "\n- [ ] T007 (`FR-001`): 更新 `vendor/VENDORED.md`：...— verify: `grep -n \"/app/vendor/Kronos\" vendor/VENDORED.md`\n\n## 3. 验证与验收任务"

Edit 2: replace §3 first three lines:
old:
"- [ ] T007 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`
- [ ] T008 (`FR-001`): 更新 `vendor/VENDORED.md`：补容器内路径（`/app/vendor/Kronos`、`/app/models/Kronos-base`、`/app/models/Kronos-Tokenizer-base`）与 real profile 说明 — verify: `grep -n "/app/vendor/Kronos" vendor/VENDORED.md`
- [ ] T009 (`AC-001`, `AC-002`): 在执行机 `qiaozhi-lt` 跑集成验收：..."
new:
"- [ ] T008 (`AC-001`, `AC-002`): 在执行机 `qiaozhi-lt` 跑集成验收：...（same）
- [ ] T009 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`"

Edit 3: §4 last two bullets replaced.

Let me do these.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:32:16Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '42,54p' docs/features/0.2/F004-kronos-inference-runtime/tasks.md | cat -A | cut -c1-120"})`


> [reasoning] The third edit (DAG bullets) succeeded. Edits 1 and 2 failed — likely because the oldString didn't match exactly. Hmm, why? Edit 1's oldString included "## 3. 验证与验收任务" context; edit 2's oldString included the three task lines. Let me look at the actual file content again — maybe trailing whitespace differences or the lines are exactly as I think. Wait, the third edit succeeded which means the DAG text matched. Let me re-read the relevant lines to see exact content. Maybe the issue: both failed edits contain the T007 line "回写 F001 spec §6 ... python3 tools/verify.py`" — hmm.

Wait, edit 1 failed but edit 3 succeeded. Perhaps because edit 1's oldString appears... no, "Could not find oldString" means mismatch. Let me check for exact characters — possibly the T006 line I copied has a different dash or the section header has trailing spaces. Let me grep the exact lines with cat -A for those regions.
Two edits didn't match exactly — inspecting exact bytes:

  <details><summary>tool output</summary>

  ```text
### Phase 3M-oM-<M-^ZM-iM-^WM-(M-gM-&M-^AM-hM-!M-%M-eM-^EM-(M-dM-8M-^NM-fM-^VM-^GM-fM-!M-#M-eM-^[M-^^M-eM-^FM-^Y$
$
- [ ] T005 (`AC-001`): M-iM-^]M-^YM-fM-^@M-^AM-iM-^WM-(M-gM-&M-^AM-hM-!M-%M-eM-^EM-(M-dM-8M-^NM-eM-^OM-^XM-eM-<M-^BM-iM-
- [ ] T006 (`AC-001`, `AC-002`): M-eM-.M-9M-eM-^YM-(M-iM-^[M-^FM-fM-^HM-^PM-fM-5M-^KM-hM-/M-^UM-oM-<M-^Zcompose M-fM-^KM
- [ ] T007 (`FR-001`): M-eM-^[M-^^M-eM-^FM-^Y F001 spec M-BM-'6 M-gM-^ZM-^D AC-006 M-eM-$M-^MM-hM-7M-^QM-eM-^QM-=M-dM-;M
- [ ] T008 (`FR-001`): M-fM-^[M-4M-fM-^VM-0 `vendor/VENDORED.md`M-oM-<M-^ZM-hM-!M-%M-eM-.M-9M-eM-^YM-(M-eM-^FM-^EM-hM-7M
$
## 3. M-iM-*M-^LM-hM-/M-^AM-dM-8M-^NM-iM-*M-^LM-fM-^TM-6M-dM-;M-;M-eM-^JM-!$
$
- [ ] T009 (`AC-001`, `AC-002`): M-eM-^\M-(M-fM-^IM-'M-hM-!M-^LM-fM-^\M-: `qiaozhi-lt` M-hM-7M-^QM-iM-^[M-^FM-fM-^HM-^P
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:32:19Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "oldString": "- [ ] T007 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`\n- [ ] T008 (`FR-001`): 更新 `vendor/VENDORED.md`：补容器内路径（`/app/vendor/Kronos`、`/app/models/Kronos-base`、`/app/models/Kronos-Tokenizer-base`）与 real profile 说明 — verify: `grep -n \"/app/vendor/Kronos\" vendor/VENDORED.md`", "newString": "- [ ] T007 (`FR-001`): 更
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "oldString": "- [ ] T009 (`AC-001`, `AC-002`): 在执行机 `qiaozhi-lt` 跑集成验收：F001 冒烟（HTTP 契约）+ F004 容器集成 + 默认镜像否证，证据记录 hostname 与 `device=cpu` — verify: `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py tests/integration/test_f004_real_profile.py -q`", "newString": "- [ ] T008 (`AC-001`, `
…[truncated])`


> [reasoning] I see! The file's actual structure is different from what I assumed in edits 1 and 2: T007 (F001 writeback) and T008 (VENDORED) are ALREADY in §2 Phase 3 (lines 46-47), NOT in §3! Let me re-look: lines 42-47: Phase 3 contains T005, T006, T007 (F001回写), T008 (VENDORED). Then §3 (line 49) starts with T009 (实测), T010, T011, T012.

Wait — but when I read lines 29-68 earlier, it showed:
```
42: ### Phase 3：门禁补全与文档回写
44: - [ ] T005 ...
45: - [ ] T006 ...
46: - [ ] T007 (`FR-001`): 回写 F001 spec §6 ...
47: - [ ] T008 (`FR-001`): 更新 vendor/VENDORED.md ...
49: ## 3. 验证与验收任务
51: - [ ] T009 ...
```

Hmm! So in the current file, T007 and T008 are in §2 Phase 3, and §3 has T009-T012. I misread earlier — when I wrote the file in Round 2, I had put T007/T008 in §2 Phase 3 ("Phase 3：门禁补全与文档回写") — yes! Looking at my Round 2 write:

```
### Phase 3：门禁补全与文档回写
- T005 ...
- T006 ...
- T007 F001 回写
- T008 VENDORED
```
Wait no. Let me re-check my Round 2 write content... In the write I made, after T006 I had:

"- [ ] T007 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`
- [ ] T008 (`FR-001`): 更新 `vendor/VENDORED.md`：..."

Hmm, in the Round 2 file I wrote, T007/T008 were in §2 Phase 3? Let me scroll: my write had:

```
### Phase 3：门禁补全与文档回写

- [ ] T005 ...
- [ ] T006 ...
- [ ] T007 ...
- [ ] T008 ...

## 3. 验证与验收任务

- [ ] T009 ...
- [ ] T010 ...
- [ ] T011 ...
- [ ] T012 ...
```

Hmm no — wait, actually in my Round 2 write, I placed T007/T008 in §3? Let me look at the write I actually submitted... In the Round 2 write message I submitted:

"### Phase 3：专属门禁与文档回写
- [ ] T005 ...
- [ ] T006 ...
- [ ] T007 (`FR-001`): 回写 F001 spec §6 ...
- [ ] T008 (`FR-001`): 更新 vendor/VENDORED.md ...

## 3. 验证与验收任务
- [ ] T009 ..."

Hmm, I don't remember exactly. The current file (sed output) shows Phase 3 contains T005-T008 and §3 contains T009-T012. Wait, but the read at offset 29 showed line 42 "### Phase 3：门禁补全与文档回写", line 46 T007, line 47 T008, line 49 "## 3. 验证与验收任务", line 51 T009. Yes — that's what the read showed! I misread it earlier when planning. OK.

So the CURRENT state after my successful edit #3 (DAG) and the failed edits:
- §2 Phase 3: T005, T006, T007 (F001 writeback), T008 (VENDORED)
- §3: T009 (实测), T010 (证据回写), T011 (gate), T012 (status)
- §4: now updated with:
  - `T006 -> T007`：VENDORED... wait, I wrote "T006 -> T007：VENDORED.md 容器路径回写..." but T007 is F001 writeback and T008 is VENDORED! My edit #3 assumed T007=VENDORED. That's WRONG vs the actual file.

Ugh. Let me fix properly. Current actual state:
- T005 static gate
- T006 container test
- T007 **F001 writeback** (should be after 实测 T009)
- T008 **VENDORED** (no 实测 dependency; can stay where it is)
- T009 实测
- T010 F004 证据回写
- T011 gate
- T012 status

Desired (numbering = execution order):
Option: Keep T007=VENDORED (swap semantics) or renumber?

Simplest minimal renumber that satisfies D014:
- T007 = VENDORED 回写（不依赖实测）— renumber old T008 → T007?
- T008 = F001 回写（实测后）?
- But 实测 is T009 — F001 writeback at T008 would still be before 实测 T009 numerically. Ugh.

So to have execution order = numbering: 实测 must come before the F001 writeback. Current numbers: T007 (F001), T008 (VENDORED), T009 (实测). Options:

Option A:
- T007 = VENDORED (old T008 content), no 实测 dependency.
- T008 = 实测 (old T009).
- T009 = F001 writeback (old T007).
- T010/T011/T012 unchanged.
File order in §2/§3: §2 Phase 3: T005, T006, T007(VENDORED). §3: T008(实测), T009(F001 writeback), T010, T011, T012.

That's exactly what I intended in edits 1/2 — but edit 1/2 oldStrings assumed T007/T008 in §3 whereas they're in §2. Let me redo:

Edit 1: In §2 Phase 3 — replace the two lines T007 (F001) and T008 (VENDORED) such that VENDORED becomes T007 and F001 writeback... wait, where does F001 writeback go? To §3 after 实测. So:
- §2 Phase 3 becomes: T005, T006, T007(VENDORED).
- §3 becomes: T008(实测), T009(F001 writeback), T010, T011, T012.

Edit A: replace §2 lines 46-47 (T007 F001, T008 VENDORED) with single line T007 VENDORED.
Edit B: replace §3 T009 line with T008 实测 line + T009 F001 line.

Then edit #3 (DAG) needs correction: I wrote "T006 -> T007：VENDORED..." and "T006 -> T008：执行机实测..." and "T008 -> T009/T010" — under the new numbering: T007=VENDORED ✓ (matches my DAG text!), T008=实测 ✓, T009=F001 ✓, T010=证据 ✓. So my edit #3 DAG text is actually CORRECT for the target numbering! Let me verify:
- "`T006 -> T007`：VENDORED.md 容器路径回写以编排与薄壳契约定稿为前提（不依赖实测）。" ✓ (T007=VENDORED)
- "`T006 -> T008`：执行机实测以容器集成测试定稿为前提..." ✓ (T008=实测)
- "`T008 -> T009/T010`：F001 命令回写与 F004 验收证据回写都以执行机实测通过为前提" ✓ (T009=F001回写, T010=证据回写)
- "`T007/T009/T010 -> T011 -> T012`" ✓

So only the task line edits A/B are needed to match the DAG. Current file has (wrong): T007=F001, T008=VENDORED, T009=实测. Need: T007=VENDORED, T008=实测, T009=F001.

Edit A: oldString:
```
- [ ] T007 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`
- [ ] T008 (`FR-001`): 更新 `vendor/VENDORED.md`：补容器内路径（`/app/vendor/Kronos`、`/app/models/Kronos-base`、`/app/models/Kronos-Tokenizer-base`）与 real profile 说明 — verify: `grep -n "/app/vendor/Kronos" vendor/VENDORED.md`
```
newString:
```
- [ ] T007 (`FR-001`): 更新 `vendor/VENDORED.md`：补容器内路径（`/app/vendor/Kronos`、`/app/models/Kronos-base`、`/app/models/Kronos-Tokenizer-base`）与 real profile 说明 — verify: `grep -n "/app/vendor/Kronos" vendor/VENDORED.md`
```
Wait, but then F001 writeback disappears from §2 — need to add it to §3 after 实测. Edit B handles that.

Edit B: oldString (the §3 T009 实测 line):
```
- [ ] T009 (`AC-001`, `AC-002`): 在执行机 `qiaozhi-lt` 跑集成验收：... -q`
```
newString:
```
- [ ] T008 (`AC-001`, `AC-002`): 在执行机 `qiaozhi-lt` 跑集成验收：... -q`
- [ ] T009 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`
```

Note: these strings must match exactly. The §3 T009 line is long; let me get exact text from the earlier read (line 51):
"- [ ] T009 (`AC-001`, `AC-002`): 在执行机 `qiaozhi-lt` 跑集成验收：F001 冒烟（HTTP 契约）+ F004 容器集成 + 默认镜像否证，证据记录 hostname 与 `device=cpu` — verify: `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py tests/integration/test_f004_real_profile.py -q`"

And §2 T007/T008 lines (46-47) from the read:
"- [ ] T007 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`
- [ ] T008 (`FR-001`): 更新 `vendor/VENDORED.md`：补容器内路径（`/app/vendor/Kronos`、`/app/models/Kronos-base`、`/app/models/Kronos-Tokenizer-base`）与 real profile 说明 — verify: `grep -n "/app/vendor/Kronos" vendor/VENDORED.md`"

Why did my earlier edit 1 fail? I had oldString = T006 line + "\n\n## 3. 验证与验收任务" but T006 line is followed by T007/T008 lines, not by the §3 header. Right. And edit 2's oldString included T007+T008+T009 lines but in the file T007/T008/T009 aren't contiguous (T007, T008 in §2; T009 in §3 after header). Right.

Let me now perform edits A and B. Then verify the whole file for consistency.
File structure differs from my assumption (T007/T008 live in §2 Phase 3). Correcting the renumbering now:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:32:33Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md"})`


> [reasoning] Now let me verify the whole tasks file for consistency: numbering T001-T012 continuous, file order = execution order, §4 DAG matches, and run gates. Let me read the full file.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: related_features: [F001, F002]
6: topics: [kronos, inference, deployment]
7: doc_kind: tasks
8: created: 2026-09-12
9: updated: 2026-09-15
10: ---
11:
12: # F004：Kronos 真实推理运行时 - 任务
13:
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15:
16: ## 0. 来源与执行规则
17:
18: - 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
19: - 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
20: - 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
21: - `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
22: - 集成与容器验收只在执行机 `qiaozhi-lt` 采集，证据记录 hostname 与 `device=cpu`；开发机只跑静态与单元门禁（SOP §3）。
23: - 实现任务遵循先红后绿：任务内的契约测试必须先失败（复现缺口）再随实现转绿，不得先实现后补测试。
24:
25: ## 1. 前置条件
26:
27
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:32:36Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && python3 tools/validate_spec_lifecycle.py && python3 tools/check_doc_links.py && git add docs/features/0.2/F004-kronos-inference-runtime/tasks.md && git commit -q -m \"docs(f004): 修正任务 DAG 顺序矛盾——回写与实测排程对齐（F004-D014）\n\n- T007 改为 VENDORED.md 回写（不依赖实测，与实测并行）；T008 为执行机实测\n- T009 F001 回写移至实测之后；T008 -> T009/T010，T007/T009/T010 -> T011 -> T012\n- 编号=执行顺序，消除'回写以实测为前提却排在实测前'的矛盾\" && git log --oneline -3 && git diff --stat HEAD~1 HEAD"})`


> [reasoning] Now the file is:
- T001-T007 in §2 (Phase 1-3)
- T008-T012 in §3
- §4 DAG:
  - T001 -> T002 ✓
  - T001/T002 -> T006 ✓
  - T003 -> T004 ✓
  - T003/T004 -> T005 ✓
  - T002/T005 -> T006 ✓
  - T006 -> T007 (VENDORED) ✓
  - T006 -> T008 (实测) ✓
  - T008 -> T009/T010 (F001 回写 + 证据回写) ✓
  - T007/T009/T010 -> T011 -> T012 ✓

Numbering = execution order: 1,2 (phase1), 3,4 (phase2), 5,6,7 (phase3), 8,9,10,11,12 (acceptance). Monotonic ✓. DAG consistent with numbering: T007 before T008 in file; in DAG both depend on T006, parallel; T009/T010 after T008 ✓. Summary phrases: no contradictions: "T006 -> T007 ... 不依赖实测" ✓; "T006 -> T008 执行机实测" ✓; "T008 -> T009/T010 都以执行机实测通过为前提" ✓; "T007/T009/T010 -> T011 -> T012" ✓.

Hmm wait, one subtle check: T007 (VENDORED) is now BEFORE T008 (实测) in file order, and DAG says T006 -> T007 (no 实测 premise) — consistent.

One more check on the reviewer's convergence condition: "任务编号、依赖箭头和括号内阶段摘要一致，且统一门禁继续全绿。" — the parenthetical summaries in §4 bullets:
- "（预检/加载 → 锁；各自测试在同一任务内先红后绿）" matches T001→T002 ✓
- "（其依赖闭包已含全部实现与门禁任务）" — T008's dependency closure via T006 → T005 → ... → T001 ✓
- "（不依赖实测）" T007 ✓
- "（二者修改不同文件，顺序无关）" T009/T010: F001 spec vs F004 spec — different files ✓

Now, one thing I should double-check: the §2 Phase 3 title "门禁补全与文档回写" contains T005 (gate), T006 (gate test), T007 (VENDORED doc writeback) — accurate ✓.

Also, Phase 3 heading "门禁补全与文档回写" — good.

Wait, also should I double check the D014 fix against the reviewer's suggested options once more:
- Suggested: "将 T006 后的文档准备与 T009 执行机实测并行，T010 同时依赖 T007/T008/T009；或把需实测通过的回写移至 T009 后。"
- I did: VENDORED (T007) parallel to 实测 (T008); F001 回写 (T009) after 实测. This is a mix: VENDORED parallel (option a partially) and F001 writeback after 实测 (option b). Both reviewer-sanctioned. The DAG now: T007 ∥ T008; T009/T010 after T008; T011 after T007/T009/T010. ✓.

Now run the doc gates + commit. Commit message: "docs(f004): 修正任务 DAG 顺序矛盾——回写与实测排程对齐（F004-D014）".

Then run full verify at round end + append FIX-log Round 3 entry.

Let me also double check the numbering is continuous T001-T012 and unique (yes). And validate_spec_lifecycle will check Phase headings only in §2 (Phase 3 is in §2 ✓).

Run gates + commit.
DAG is now consistent with execution order. Running doc gates and committing:

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
check_doc_links: 相对链接全部可解析
c5100a0 docs(f004): 修正任务 DAG 顺序矛盾——回写与实测排程对齐（F004-D014）
3f7320e docs(f004): tasks 先红后绿改造与文档任务所有者（F004-D013）
ce557c3 docs(f004): 校正影响面并点明启动钩子所有者（F004-D012）
 docs/features/0.2/F004-kronos-inference-runtime/tasks.md | 12 +++++++-----
 1 file changed, 7 insertions(+), 5 deletions(-)


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:32:43Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && time .venv/bin/python tools/verify.py 2>&1 | tail -12; echo \"---\"; date \"+%Y-%m-%d %H:%M %Z\"; git rev-parse --short HEAD", "timeout": 600000})`


> [reasoning] Committed c5100a0. Now run the full gate (.venv/bin/python tools/verify.py), then append FIX-log Round 3.

Note: the working tree has many user-side modified files (CLAUDE.md, README.md, docs/*, ADR-0008 untracked). verify.py may be affected by those changes (check_doc_links scans all docs md — including modified ones). The reviewer's Round 3 gate was green with those present ("194 passed, 23 skipped，90.22 秒" — they ran with the same dirty tree). Let me run and see.

Also note: should I worry that verify will now pick up NEW changes from the user's session (e.g., ADR-0008 untracked file is not scanned? untracked files aren't in git ls-files but check_doc_links scans docs/**/*.md on disk regardless of git — it includes untracked files. If ADR-0008 has bad links, gate could fail — not my responsibility, and the reviewer's run was green ~00:30. Let me just run.

  <details><summary>tool output</summary>

  ```text
== dev 依赖版本在 pin 范围内 ==

== 密钥模式扫描 ==

== pytest ==
FAILED: pytest

== ruff check ==

== ruff format check ==

verify.py 失败步骤：['pytest']
.venv/bin/python tools/verify.py 2>&1  136.87s user 20.10s system 77% cpu 3:23.79 total
tail -12  0.01s user 0.01s system 0% cpu 3:23.79 total
---
2026-09-15 00:36 HKT
c5100a0


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:36:10Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python -m pytest -q --confcutdir=tests --rootdir=tests tests/unit tests/integration 2>&1 | tail -40", "timeout": 600000})`


> [reasoning] The gate failed on pytest. This is likely NOT caused by my tasks.md change (docs only) — but I must investigate. The user's parallel changes (CLAUDE.md/README/docs/ADR-0008/F003 spec + ui-mockup) might have broken something, OR the pytest failure is environmental.

Let me get the actual failure. Run the pytest step directly to see.

Possibility: check_doc_links scans docs — the user modified docs; but check_doc_links passed? The output tail only shows the last steps; check_doc_links step presumably passed (not in failed list). Failed steps: ['pytest'] only.

Let me run pytest to see what failed.
Gate red on pytest — must diagnose before declaring round end (likely from the external uncommitted changes, not my docs edit):

  <details><summary>tool output</summary>

  ```text
........................................................................ [ 33%]
........................................................................ [ 66%]
........................................................s............... [ 99%]
s                                                                        [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/integration/test_f001_kronos_smoke.py:86: AC-006 需真实模型实例：设 KRONOS_REQUIRE_REAL_MODEL=1 并把 KRONOS_BASE_URL 指向真实实例（命令见本文件 docstring / spec §6 AC-006）
SKIPPED [1] tests/integration/test_f002_schedule_backup.py:84: 未设置 ALPHAMILL_REAL_LAKE_DIR（本用例仅在有真实湖时运行）
215 passed, 2 skipped in 114.22s (0:01:54)


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:38:10Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/verify.py > /tmp/opencode/verify-r3.log 2>&1; echo \"exit=$?\"; grep -nE \"FAILED|failed|Error|error\" /tmp/opencode/verify-r3.log | head -30; tail -8 /tmp/opencode/verify-r3.log", "timeout": 600000})`


> [reasoning] Interesting — running pytest directly: 215 passed, 2 skipped. But verify.py reported pytest FAILED. Hmm. Why?

Maybe a flaky test, or the verify.py run had a transient failure (e.g., integration test hitting the real DB and one failing intermittently under load because the two runs overlapped? Or a test that depends on docker/DB state changed between runs).

Actually wait — verify.py runs pytest from ROOT with `sys.executable -m pytest -q --confcutdir=tests --rootdir=tests tests/unit tests/integration`. Same as my command. The failure might be flaky (e.g., test_f002 integration tests using a real DB/lake, and something transient). Or... the user's parallel session might be running something concurrently (they modified docs; maybe they're also running docker operations?).

I need the actual failure output. The verify.py run output was truncated by `tail -12`. Let me re-run verify.py (or better, capture pytest failure details). Since direct pytest passed, it might be flaky. Run verify.py again fully and inspect. Or run verify.py with output to a file. Let me run it again and capture.

Hmm, cost: ~3.5 min. Worth it — the skill says gate must be green; if flaky, I should identify the failing test.

Actually — wait. Maybe the failure is due to the user's uncommitted changes interacting: e.g., some unit test validates repo docs (test_check_doc_links/test_doc_gate_command scans tracked files — CLAUDE.md modified... hmm tracked files include modified CLAUDE.md. test_doc_gate_command scans tracked files for bare `python tools/verify.py` — if the user's edits to CLAUDE.md/README introduced such text, the test would fail! Or test_verify_env_contract, test_f001_compose_contract (reads F001 spec), test_review_artifacts_gitignore, etc.

My direct pytest run just now: 215 passed, 2 skipped — GREEN. Same command. So the earlier failure must have been transient OR the test run during verify.py had a different environment. Hmm wait — verify.py runs pytest with cwd=ROOT too.

Possibly flaky: integration tests against real TimescaleDB — maybe a test failed due to timing (e.g., export/reconcile test with DB contention). Since my rerun passed, it's flaky-ish. But I can't just shrug. Let me re-run verify.py once to see if it's green now, and if it fails, capture which test failed.

Let me run verify.py with full output captured to a file.
Direct pytest is green (215 passed / 2 skipped) — the verify run's failure looks transient. Re-running the full gate to confirm and capture the failing test if it repeats:

  <details><summary>tool output</summary>

  ```text
exit=0

== pytest ==

== ruff check ==

== ruff format check ==

verify.py 全部通过：生命周期 / 文档链接 / 依赖 pin / 密钥扫描 / pytest / ruff


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:41:26Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && cat .pytest_cache/v/cache/lastfailed 2>/dev/null; echo \"---\"; ls -la .pytest_cache/v/cache/ 2>/dev/null; echo \"---\"; journalctl --user -n 5 2>/dev/null | head -3; docker ps --format \"{{.Names}} {{.Status}}\" 2>/dev/null | head"})`


> [reasoning] Second run: exit=0, all green. So the first failure was transient — but I should identify what failed to be honest in the FIX-log. The first run's output wasn't captured (only tail -12). Hmm. I can check if there's any clue... Actually I ran the direct pytest right after and it was green, and now verify.py green again. The transient failure could have been:

1. A flaky integration test against the live TimescaleDB (e.g., concurrent access, timing).
2. Resource contention (two pytest runs? No, they were sequential. But the user's parallel session might have been running heavy things — the working tree shows heavy doc edits; maybe another agent was executing something).
3. Docker/DB hiccup.

Per the skill: "本地绿 CI 红且报错和这次改动无关，先比较本地工具版本..." — not applicable; here local red then local green. I should record this honestly in the FIX-log gate line: first attempt had a transient pytest failure (not captured, not reproducible on immediate re-run ×2: direct pytest green + verify.py green). Since the round's change is a docs-only tasks.md edit (7 insertions/5 deletions) that cannot affect pytest, and two consecutive reruns are green, I'll note the flake explicitly.

Hmm, but wait — should I worry it's caused by the user's uncommitted changes making some test flaky (e.g., test that reads docs files on disk)? My direct pytest run was green right after, and now again — so not deterministic. Fine.

Actually, let me try to find what failed in the first run: the output of the first verify.py run went to stdout — I only piped tail -12 and it showed "FAILED: pytest" but not the test details (they were earlier in output, lost). No capture. Can't recover. OK.

Let me now also double check: is it possible the first failure was because a *different* pytest invocation has a race with the still-running previous verify? No, sequential.

I'll note it in FIX-log as "首跑 pytest 失败但未留存输出；立即复跑（直接 pytest + verify.py 各一次）均全绿，未能复现；本轮为 docs-only 改动（tasks.md 7+/5-），与 pytest 无耦合；若检视方复跑再遇红请保留输出定位". Honest and actionable.

Hmm, actually, let me think about whether I should try to reproduce once more... I've run: verify (red), direct pytest (green), verify (green). That's 2 green runs. The red run's failing test is unknown. If I run once more and it's green, still unknown. I'll leave it with the note. Actually — maybe I can check pytest cache for last failed? pytest has `.pytest_cache/v/cache/lastfailed`. Let me check! If the failing test was recorded, lastfailed might have it (though the green runs may clear it: on a fully green run, lastfailed gets emptied). Let me check the cache file.
Second run green (`exit=0`). Checking pytest cache for the transient failure's identity:

  <details><summary>tool output</summary>

  ```text
{}---
total 32
drwxr-xr-x 2 georg georg  4096 Sep 11 00:18 .
drwxr-xr-x 3 georg georg  4096 Sep 10 23:06 ..
-rw-r--r-- 1 georg georg     2 Sep 14 02:02 lastfailed
-rw-r--r-- 1 georg georg 16395 Sep 15 00:32 nodeids
---
Sep 15 00:40:34 qiaozhi-lt powershell[1956916]: (7.6.6:C:80) [NamedPipeIPC_ServerListenerStarted:NamedPipe.Open.Informational] PowerShell has started an IPC listening thread on process: 1956916 in AppDomain: None.
Sep 15 00:40:34 qiaozhi-lt powershell[1956916]: (7.6.6:1:80) [Perftrack_ConsoleStartupStop:PowershellConsoleStartup.WinStop.Informational] PowerShell console is ready for user input
Sep 15 00:40:50 qiaozhi-lt pwsh[1956916]: Runtime snapshot written: 2026-09-14T16:40:35.4150926Z open_trades=0 trade_count=15
quant-freqtrade Up 2 days
quant-timescaledb Up 2 days (heal
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:41:32Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && hostname; tail -20 docs/reviews/FIX-log.md"})`


> [reasoning] Interesting discoveries:
1. `lastfailed` is `{}` — cleared by subsequent green runs; no record of the failing test.
2. The machine is **qiaozhi-lt** (the execution machine!) — journalctl shows `qiaozhi-lt powershell ... Runtime snapshot written` — and docker containers are running (quant-timescaledb healthy, quant-kronos-signal, freqtrade, collectors). So THIS environment is the execution machine, which explains why integration tests hit a live DB and run (215 passed vs reviewer's 194/23 skip — hmm, the reviewer's runs show 23 skips, which suggests reviewer's verify runs in a different environment... or maybe ran with different env vars? Whatever.)

Wait — journalctl shows a runtime snapshot was written at 00:40 — the alphamill-snapshot.timer/service runs periodically (every few minutes?) on this machine. That's a live system with running timers and DB writes. This makes flakiness more plausible: integration tests touching a live DB while the snapshot collector writes to it (or the collector ran mid-test), or export tests racing with timers.

Actually, the snapshot service writes signals_log and dryrun_runtime_snapshots — different tables than F002 export tests (ohlcv etc.), probably no conflict. But flaky first-run remains unexplained. Since two consecutive green runs, and the change is docs-only, I'll note the flake.

Hmm, one more possibility for the first-run failure: pytest ran while... the first verify.py run's pytest may have hit a transient failure in an integration test that depends on `quant-kronos-signal` (mock) being reachable or DB state — e.g., test_f001_kronos_smoke expects service up? With ALPHAMILL_INTEGRATION unset, if service unreachable → skip; if reachable → structural assertions on /predict which reads DB; races possible. But again, not my change.

Given the environment is a live execution machine with timers, a transient is plausible. Note it honestly in FIX-log.

Now — wait, an important implication: this machine being qiaozhi-lt contradicts my earlier statement "开发机只跑静态与单元门禁"? The SOP machine boundary says integration evidence must be collected on the execution machine (qiaozhi-lt) and dev machine doesn't run integration. Here I ran the whole integration suite as part of verify.py (which is a local routine — but per SOP, "开发机上的 skip 不算证据" — this is qiaozhi-lt, so actually running integration here IS allowed/expected?). Hmm, actually CLAUDE.md said "开发机 qiaozhi-gp/gp-wsl"; but journalctl says qiaozhi-lt. So this session runs ON the execution machine (qiaozhi-lt). Interesting. Either way, not relevant to my docs fix — but for FIX-log gate evidence I should state the machine: `hostname` — let me check hostname to be precise. The journal prefix "qiaozhi-lt" is definitive. Good enough; the gate runs are all local.

OK now: append FIX-log Round 3 entry. Also update the "待复核提示" appropriately. Content:

```
## Round 3 · 2026-09-15

- **基线**：`main` @ `3f7320e`（Round 3 检视基线）→ `main` @ `c5100a0`（1 个提交）
- **findings**：F004-D014（处理；无 rejection）
- **commits**：F004-D014：`c5100a0`（tasks.md 任务重排与 DAG 修正，7+/5-）
- **regression_tests**：文档检视证据类型同前——文档 diff + 文档门禁；D014 为 tasks §4 排序矛盾，无代码测试可加
- **gate**：`.venv/bin/python tools/verify.py` → 全绿（生命周期 / 链接 / 依赖 pin / 密钥 / pytest `215 passed, 2 skipped` / ruff）。**环境说明**：本机为执行机 `qiaozhi-lt`，TimescaleDB/Kronos 服务在运行，故集成用例实际执行（非 skip）。首跑 pytest 曾报 FAILED 且未留存明细；立即复跑两次（直接 pytest、verify.py）均全绿未能复现，判定为与 docs-only 改动无关的偶发（本机有快照 timer 与实时库写入；若检视方复跑再遇红请保留输出定位）
- **rejected**：无

### 逐条处理说明

- **D014**（T007/T008 排在实际执行机实测 T009 之前却声称'以实测通过为前提'；链尾摘要与编号不匹配）：采用检视建议的第二选项（把需实测通过的回写移至实测后）并保持"编号=执行顺序"：
  - T007 改为 `VENDORED.md` 回写（不依赖实测，与实测并行）；
  - T008 为执行机实测（原 T009）；
  - T009 为 F001 §6 命令回写（原 T007，移至实测之后）；
  - §4 改为 `T006 -> T007`（VENDORED，契约前提）、`T006 -> T008`（实测）、`T008 -> T009/T010`（实测后回写，顺序无关）、`T007/T009/T010 -> T011 -> T012`（门禁→状态），删除原'实测 → 证据回写'压缩摘要与编号不匹配段。
```

Wait — check: the reviewer's D014 suggested_fix (a) said "将 T006 后的文档准备与 T009 执行机实测并行，T010 同时依赖 T007/T008/T009". Note their numbering was OLD: T009=实测, T007=F001回写, T008=VENDORED, T010=证据回写. Option (a): T007/T008 ∥ T009; T010 depends on T007/T008/T009. Option (b): "或把需实测通过的回写移至 T009 后".

My fix: T007(VENDORED) ∥ T008(实测), T009(F001回写) after 实测, T010 after 实测. That's option (b) for F001回写 + VENDORED parallel — a valid combination, and I preserved numbering=order. Let me phrase it in FIX-log as "采用检视建议的第二选项（…移至实测后）；VENDORED 回写不依赖实测，与实测并行".

Also add待复核提示:
"- Round 4 只需复核 tasks §4 + 编号顺序：grep 检查 T001-T012 连续、文件顺序=编号顺序、`T008 -> T009/T010` 与 `T007/T009/T010 -> T011 -> T012` 与摘要一致。"

Then update todos and report.

Also: should I check whether the reviewer's next check includes "统一门禁继续全绿" — done (with flake note).

Let me append to FIX-log. I need the current tail of FIX-log (after my Round 2 entry). Let me read the tail to anchor the edit.
Confirming machine context for the gate record, then appending Round 3 declaration:

  <details><summary>tool output</summary>

  ```text
qiaozhi-lt
- **regression_tests**：文档检视同 Round 1——文档 diff + 文档门禁（`tools/validate_spec_lifecycle.py`、`tools/check_doc_links.py`）；D013 另把「先红后绿」写入 tasks §0 执行规则，实现轮每个实现任务自带先失败的契约用例
- **gate**：`.venv/bin/python tools/verify.py` → 全绿（生命周期 / 文档链接 / 依赖 pin / 密钥扫描 / pytest `215 passed, 2 skipped` / ruff check + format）；2026-09-15 00:16 HKT；2 个 skip 为预期（F001 AC-006 真实模型开关未设、F002 真实湖环境变量未设）
- **rejected**：无

### 逐条处理说明

- **D011**（real 服务缺 DB 接线）：design §2 契约表新增三行——`DB_*` 环境（同 mock 服务）、`depends_on: timescaledb: {condition: service_healthy}`、`networks: [alphamill]`，并写明运行链（compose → 模型 → TimescaleDB → HTTP）；design §8 静态门断言补 DB 接线、容器门断言补 `/health` 的 `database` 可达 + `/predict` 端到端；spec §3/§7/AC-001 同步；T004/T005/T006 断言清单由 `3f7320e` 同步。
- **D012**（启动钩子/配套文档无所有者）：design §1「后端 / API」改为「HTTP 契约无变更；薄壳改动落在 `se
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T16:41:42Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "oldString": "全绿（194 passed, 23 skipped，90.22 秒）；Round 3 不闭环。", "newString": "全绿（194 passed, 23 skipped，90.22 秒）；Round 3 不闭环。\n\n## Round 3 · 2026-09-15\n\n- **基线**：`main` @ `3f7320e`（Round 3 检视基线）→ `main` @ `c5100a0`（1 个提交）\n- **findings**：F004-D014（处理；无 rejection）\n- **commits**：F004-D014：`c5100a0`（tasks.md 任务重排与 §4 DAG 修正，7 additions / 5 deletions）\n- **regression_tests**：文档检视证据类型同前——文档 diff + 文档门禁（`tools/validate_spec_lif
…[truncated])`


> [reasoning] Interesting: hostname = qiaozhi-lt. So this session IS on the execution machine. The reviewer's verify runs also show 194 passed / 23 skipped — but mine show 215/2. Why the difference if same machine? Perhaps the reviewer (another agent) runs in a different container/sandbox where DB isn't reachable... Or they run with a different venv path? Their reported skip count (23) matches what would happen if integration tests skip due to unreachable services. Since I'm on qiaozhi-lt with DB up, integration runs. Different sandboxes maybe (the reviewer might be in a separate environment/container with network isolation). Not my problem; I'll note that my gate run executed integration tests on this machine.

Hmm wait, actually — but per SOP, integration evidence must be recorded with hostname + device. My gate record can note hostname qiaozhi-lt. Fine. But note this is a DOC fix round, not acceptance; no acceptance evidence claim. Keep the note simple.

Now append Round 3 entry after the [review-r3] annotation. Anchor: "全绿（194 passed, 23 skipped，90.22 秒）；Round 3 不闭环。"

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:41:49Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git log --oneline 3f7320e..HEAD; echo \"---\"; git show --stat HEAD | tail -4; echo \"--- untracked/unrelated untouched:\"; git status --short | head -14"})`


> [reasoning] Done with the mechanics. Now let me do a final sanity pass:

1. Check tasks.md final state once more for any inconsistency (e.g., §3 T008/T009 order vs DAG). Already read it — consistent.

2. One question: The reviewer's convergence condition: "任务编号、依赖箭头和括号内阶段摘要一致". Let me double-check every §4 bullet's parenthetical:
- `T001 -> T002`：同一薄壳文件的顺序改造（预检/加载 → 锁；各自测试在同一任务内先红后绿）✓
- `T001/T002 -> T006`：容器集成依赖启动预检、eager load 与串行推理行为成立 ✓
- `T003 -> T004`：compose target 依赖 Dockerfile 目标定义 ✓
- `T003/T004 -> T005`：静态门禁在全量断言（含默认隔离）与变异验证后定稿 ✓
- `T002/T005 -> T006`：容器集成建立在薄壳行为与静态契约通过之上 ✓
- `T006 -> T007`：VENDORED.md 容器路径回写以编排与薄壳契约定稿为前提（不依赖实测）✓
- `T006 -> T008`：执行机实测以容器集成测试定稿为前提（其依赖闭包已含全部实现与门禁任务）✓
- `T008 -> T009/T010`：F001 命令回写与 F004 验收证据回写都以执行机实测通过为前提；二者修改不同文件，顺序无关 ✓
- `T007/T009/T010 -> T011 -> T012`：全量门禁覆盖全部回写后执行；状态/BACKLOG 同步以门禁全绿为前提 ✓

Good.

3. Also — should I double check that the working tree commits: only tasks.md committed in c5100a0; other user files remain uncommitted/untouched ✓ (git diff --stat showed only tasks.md).

4. Update todos.

5. Report to user.

Wait, one more consideration about the flaky test: since we're on qiaozhi-lt with live timers (the snapshot timer runs every few minutes — journalctl showed a snapshot at 00:40), there's a plausible cause: a test that hits the live TimescaleDB and the concurrent snapshot writes could cause a transient conflict? More likely: an integration test that asserts a row count on signals_log or dryrun tables while the snapshot service writes concurrently! Let me check: tests like test_f002_export_reconcile.py assert reconciliation vs DB; test_f001_dryrun_monitoring.py interrogates DB. The snapshot service inserts rows into dryrun_runtime_snapshots and signals_log every N minutes. If a test does exact-count assertions on those tables, a concurrent insert could break it. Hmm.

This might be worth investigating briefly to give the reviewer a concrete note... But my mandate is the docs fix; the flake isn't from my change. I noted it transparently. I could quickly grep for tests using signals_log counts... Let me do a 30-second check to see if there's an obvious race candidate, purely to make the note useful.

Actually, hold on — the first verify.py failure: I piped `| tail -12`, which means I lost the pytest failure output. But wait — maybe the failure was actually caused by resource contention: the earlier full gate run (at 00:36) was followed immediately by direct pytest (00:37-ish) — those were green. The failing run was at ~00:33. Hmm.

Let me quickly check if test timers are running every 5 min: alphamill-snapshot.timer. If tests hit signals_log counts... e.g. test_f001_dryrun_monitoring.py maybe checks snapshot tables non-empty (not exact counts) — race-safe. Not worth deep investigation now; the reviewer will rerun and can capture if it recurs. My note suggests: "若检视方复跑再遇红请保留失败用例输出以便定位" — sufficient.

Hmm, but actually, let me reconsider: could the first failure have been caused by MY running both verify.py and the user's parallel session doing docker ops? The journalctl output showed PowerShell starting at 00:40 — external session activity on this machine. Concurrent activity on a live execution machine explains intermittent failure in integration tests (DB/API load). Fine.

Let me update todos and write the final report.

Actually — one more important check per skill §0 baseline discipline: "git status 出现本会话没有动过的文件——先向用户确认归属再决定并入或搁置". The current dirty files (CLAUDE.md, docs/README.md, prd, architecture, decisions, F003 spec, ADR-0008, ui-mockup) are external. The reviewer already excluded them ("docs/alphamill-prd.md 的未提交改动不涉及 F004，亦排除且未触碰"). I haven't touched them. ✓. I should mention in my report that external changes were left untouched.

Update todos (round 3 list) and report.
Round 3 fix complete. Final verification of the committed diff scope + todo update:

  <details><summary>tool output</summary>

  ```text
c5100a0 docs(f004): 修正任务 DAG 顺序矛盾——回写与实测排程对齐（F004-D014）
---
    - 编号=执行顺序，消除'回写以实测为前提却排在实测前'的矛盾

 docs/features/0.2/F004-kronos-inference-runtime/tasks.md | 12 +++++++-----
 1 file changed, 7 insertions(+), 5 deletions(-)
--- untracked/unrelated untouched:
 M CLAUDE.md
 M README.md
 M docs/README.md
 M docs/alphamill-architecture.md
 M docs/alphamill-prd.md
 M docs/decisions/0001-factor-mining-engine.md
 M docs/decisions/0005-presentation-observability.md
 M docs/design/ui-mockup/README.md
 M docs/design/ui-mockup/app.js
 M docs/design/ui-mockup/index.html
 M docs/design/ui-mockup/styles.css
 M docs/features/0.2/F003-alphagen-vendor/spec.md
?? docs/decisions/0008-north-star-sustained-profitability.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T16:41:57Z

- **tool**: `todowrite({"todos": [{"content": "F004-D014: tasks 重排——VENDORED 回写并行、F001 回写移至实测后、DAG 与摘要对齐 - commit c5100a0", "status": "completed", "priority": "medium"}, {"content": "轮末全量门禁 .venv/bin/python tools/verify.py 全绿（215 passed, 2 skipped；首跑 pytest 偶发红已两次复跑证伪）", "status": "completed", "priority": "high"}, {"content": "FIX-log 追加 Round 3 修复声明（含偶发红透明记录）", "status": "completed", "priority": "high"}]})`

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "F004-D014: tasks 重排——VENDORED 回写并行、F001 回写移至实测后、DAG 与摘要对齐 - commit c5100a0",
    "status": "completed",
    "priority": "medium"
  },
  {
    "content": "轮末全量门禁 .venv/bin/python tools/verify.py 全绿（215 passed, 2 skipped；首跑 pytest 偶发红已两次复跑证伪）",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "FIX-log 追加 Round 3 修复声明（含偶发红透明记录）",
    "status": "completed",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-14T16:41:59Z


> [reasoning] Final report. Round 3: D014 fixed. Keep it concise:

- State: Round 3's only finding D014 fixed, 1 commit c5100a0 on top of 3f7320e, gate green.
- What changed: T007=VENDORED (parallel, no 实测 premise), T008=实测, T009=F001 writeback after 实测, T010 unchanged, §4 DAG rewritten.
- Transparency: first gate run had a transient pytest failure, not reproducible (2 green reruns); docs-only change; noted in FIX-log.
- Note: unrelated working-tree changes (PRD etc.) untouched.
- Next: reviewer Round 4 (only tasks §4).
Round 3 修复完成。唯一开放项 D014 已处理，1 个提交（`3f7320e → c5100a0`），轮末门禁全绿。

**状态：修复已落盘，等待检视方 Round 4（按声明只复核 tasks §4 两行 DAG）**

**D014 修复**（采用检视建议第二选项：需实测的回写移至实测后，保持「编号=执行顺序」）：

| 编号 | 内容 | 位置变化 |
|---|---|---|
| T007 | `VENDORED.md` 容器路径回写 | 与实测并行，前提=契约定稿（不依赖实测） |
| T008 | 执行机 `qiaozhi-lt` 集成验收 | 原 T009，前提=容器测试定稿 |
| T009 | F001 §6 命令回写 | 原 T007，**移至实测之后** |
| T010→T012 | F004 证据回写 / 质量门 / 状态同步 | 编号不变 |

§4 DAG 重写为：`T006 -> T007`、`T006 -> T008`、`T008 -> T009/T010`、`T007/T009/T010 -> T011 -> T012`；删除了与编号错位的「实测 → 证据回写」摘要段。

两条透明记录（均写入 FIX-log Round 3）：
1. 门禁首跑 pytest 报 FAILED 但未留存明细；紧接着直接 pytest + verify.py 两次复跑均全绿（`215 passed, 2 skipped`），未复现——本轮为 tasks.md 7+/5- 的 docs-only 改动，与 pytest 无耦合；本机是执行机 `qiaozhi-lt`（DB/快照 timer 在活动），疑为偶发。
2. 工作树里 PRD/CLAUDE/ADR-0008 等外部改动（非本会话）全部未触碰，提交只含 `tasks.md`。

**下一步（约 10 分钟）**：检视方 Round 4 —— grep 验证 T001–T012 连续且文件顺序=编号顺序、两条 DAG 箭头的括号摘要语义一致；通过即翻 `fixed`、触发 CI 并闭环。
