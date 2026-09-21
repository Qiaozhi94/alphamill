---
report_type: doc-review
feature: F009
round: 5
date: 2026-09-20
prior_report: CURRENT-doc.md@round4（同文件覆盖写；Round 4 的 10 条结转见下方「Round 4 结转」）
scope: diff-only
stop_condition_met: false
readiness: FAIL
change_scope: in-place
severity_counts: {critical: 0, high: 0, medium: 6, low: 2}
baseline:
  reviewed_at_start: main@78a398e + feat/F003-alphagen-vendor@732d98e
  re_baselined: true
  re_baseline_reason: >
    核对期间并行会话把工作树切到 feat/F003-alphagen-vendor 并暂存了一批 main 的文档
    （F010 三件套、BACKLOG/CLAUDE/README、RETROSPECTIVE、check_doc_consistency），
    HEAD 从 main@78a398e 漂到分支@732d98e。按协议 §0 显式 re-baseline：本轮全部取证改为
    只读（`git show <rev>:<path>`）+ 独立 worktree 跑变异，不再在共享工作树里写文件。
  reviewed_diff:
    - bab9d80 docs(f009) —— 架构 §7.1 + F009 三件套 + 门禁钉点
    - d1feee7 docs(f010) —— F010 方向澄清 + 活跃索引
    - 78a398e chore(gates) —— 编号与 AC-012 边界钉点
    - 732d98e fix(f003) —— 客户端恢复所有权、deadline 余量、transitional、CLI 证据（分支）
reviewer: 本会话（修复者视角切换为检视者，全部结论重新独立取证，不采信 FIX-log 文字）
issues:
  - id: F009-R5-001
    title: spec §3 范围内仍写客户端超时 5s/60s/120s，与 R4-002 后的 FR-009/AC-010 自相矛盾
    severity: medium
    category: correctness
    root_cause: root-cause
    origin: fix-regression
    pattern_tag: stale-acceptance-reference
    status: open
    tracked_task: null
    fix_summary: null
    regression_test: null
    suggested_fix: §3 那行改为"客户端 deadline = 服务端 deadline + 余量（缺省 5+5/60+5/120+5）"，并把 restore 所有权表述从"三条退出路径均须恢复"改成"发出过 stop 即触发"；同时给该句加一致性钉点
    disposition_reason: null
    location: docs/features/0.2/F009-kronos-lifecycle-endpoints/spec.md:119
    first_seen_round: 5
    resolved_round: null
  - id: F009-R5-002
    title: F004 端口契约迁移只挂在 T013，没有任何 AC 覆盖其结果
    severity: medium
    category: test-coverage
    root_cause: root-cause
    origin: process-gap
    pattern_tag: acceptance-evidence-gap
    status: open
    tracked_task: null
    fix_summary: null
    regression_test: null
    suggested_fix: AC-009 的 tests 增列 `tests/unit/test_f004_compose_profile_contract.py`，断言迁移后"host 绑回环 + 不顶替 mock 8001 + container 8001"三条同时成立且变异表仍逐条判红
    disposition_reason: null
    location: docs/features/0.2/F009-kronos-lifecycle-endpoints/spec.md:421
    first_seen_round: 5
    resolved_round: null
  - id: F009-R5-003
    title: F003（live owner，developing）的契约摘要与服务端归属未随本轮同步
    severity: medium
    category: correctness
    root_cause: root-cause
    origin: spec-drift
    pattern_tag: cross-feature-contract-drift
    status: open
    tracked_task: null
    fix_summary: null
    regression_test: null
    suggested_fix: F003 design §4 的错误码集合补 `E_BAD_REQUEST`/`E_UNLOAD_FAILED`，客户端行为补 transitional fail-closed、deadline 余量与"发出过 stop 即恢复"；spec AC-010 与 tasks §5 把"服务端归 BACKLOG 待分配 feature/规划中"改为"归 F009（ready-for-development）"
    disposition_reason: null
    location: docs/features/0.2/F003-alphagen-vendor/design.md:170
    first_seen_round: 5
    resolved_round: null
  - id: F009-R5-004
    title: 继承来的 stopped 没有恢复 owner，R4-002 要消除的终态仍有一条可达路径
    severity: medium
    category: correctness
    root_cause: root-cause
    origin: original-coding
    pattern_tag: recovery-ownership-hole
    status: open
    tracked_task: null
    fix_summary: null
    regression_test: null
    suggested_fix: 在架构 §7.1 裁决继承态的归属——或规定"本轮因 desired=stopped 而直接取锁的运行同样在退出前 restore"，或显式声明人工停机不得被自动恢复并要求运行记录标注 `inherited_stopped`；裁决后同步 FR-009/AC-010 与客户端
    disposition_reason: null
    location: src/alphamill/factor_factory/generators/kronos_offload.py:122（feat/F003-alphagen-vendor@732d98e）
    first_seen_round: 5
    resolved_round: null
  - id: F009-R5-005
    title: stop 的四种失败塌缩成同一个 reason=stop_failed，事后无法区分"迟到完成"与"根本没开始"
    severity: medium
    category: quality
    root_cause: root-cause
    origin: fix-regression
    pattern_tag: evidence-attribution-collapse
    status: open
    tracked_task: null
    fix_summary: null
    regression_test: null
    suggested_fix: 按错误码分记 reason（`stop_busy` / `stop_timeout` / `stop_unload_failed` / `stop_unexpected_state`），处置仍同为 fail-closed + 恢复责任；沿用 R2-002 立下的"处置相同但归因不同必须分开记"标准
    disposition_reason: null
    location: src/alphamill/factor_factory/generators/kronos_offload.py:132（feat/F003-alphagen-vendor@732d98e）
    first_seen_round: 5
    resolved_round: null
  - id: F009-R5-006
    title: 运行记录记了"背了恢复责任"，却不记"恢复成没成"
    severity: medium
    category: test-coverage
    root_cause: root-cause
    origin: fix-regression
    pattern_tag: acceptance-evidence-gap
    status: open
    tracked_task: null
    fix_summary: null
    regression_test: null
    suggested_fix: `kronos_offload` 增 `restore_result`（ok / failed / not_attempted）由 CLI 的 finally 回写；AC-010 增一条断言，使"当晚到底恢复了没有"能从 run.json 复核，而不是只靠 stderr 的 WARNING
    disposition_reason: null
    location: src/alphamill/factor_factory/cli.py:255（feat/F003-alphagen-vendor@732d98e）
    first_seen_round: 5
    resolved_round: null
  - id: F009-R5-007
    title: FR-004 与 NFR-002 的超时措辞没跟上"服务端 deadline / 五个变量"
    severity: low
    category: quality
    root_cause: symptom-patch
    origin: fix-regression
    pattern_tag: stale-acceptance-reference
    status: open
    tracked_task: null
    fix_summary: null
    regression_test: null
    suggested_fix: FR-004 的"默认超时 120s（可配）"比照 FR-002 标明是服务端动作 deadline；NFR-002 的"三个动作的超时与显存探测方式"改为指向 FR-007 的五变量表
    disposition_reason: null
    location: docs/features/0.2/F009-kronos-lifecycle-endpoints/spec.md:219
    first_seen_round: 5
    resolved_round: null
  - id: F009-R5-008
    title: 客户端超时参数名仍读作"客户端超时"，实际承载的是服务端 deadline
    severity: low
    category: quality
    root_cause: root-cause
    origin: fix-regression
    pattern_tag: ""
    status: open
    tracked_task: null
    fix_summary: null
    regression_test: null
    suggested_fix: `offload_kronos(status_timeout_s=/stop_timeout_s=)` 与 `restore_kronos(timeout_s=)` 改名为 `*_server_deadline_s`，或在 docstring 里写明"传入的是服务端 deadline，socket 超时由 client_deadline() 加余量"
    disposition_reason: null
    location: src/alphamill/factor_factory/generators/kronos_offload.py:64（feat/F003-alphagen-vendor@732d98e）
    first_seen_round: 5
    resolved_round: null
---

# F009 文档检视 · Round 5（diff-only 封顶轮）

## 结论先行

**High 清零，本轮 0 Critical / 0 High。** Round 4 的 10 条（含重开的 R1-008/R1-009）逐条独立核对通过：
机制不是措辞补丁——过渡态进了 wire 取值域、卸载失败有了错误码与逐注入点落点、两端 deadline
有了严格大小关系、恢复责任从"同步确认 stopped"改成"发出过 stop"，四条客户端断言在独立 worktree
里逐个变异判红。

**但 readiness 仍判 FAIL**：协议 §7 的停止条件是"Critical/High 清零**且**只剩 Low/Info"，本轮还有
6 条 Medium。它们不是新的机制缺口，是这次修复自己留下的三类尾巴：(a) 同一份 spec 里 §3 的摘要
没跟上 FR-009（R5-001）；(b) 新增的跨 Feature 动作没有 AC 兜（R5-002）、消费端 F003 的文档没同步
（R5-003）；(c) 新立的"恢复所有权"规则只覆盖了自己发出的 stop，继承来的 stopped 仍无人负责
（R5-004），且证据面只记责任不记结果（R5-005/R5-006）。

其中 **R5-004 建议在开工前裁决**——它决定 FR-009 的措辞，实现后再改要动客户端与运行记录两处。
其余 5 条一轮可闭，故裁决 `change_scope: in-place`，下一轮仍 diff-only。

## 基线与 re-baseline（协议 §0）

- 开审基线：`main@78a398e` + `feat/F003-alphagen-vendor@732d98e`，工作树当时干净。
- **核对中途 HEAD 漂移**：并行会话把工作树切到 F003 分支，并暂存了一批 main 的文档（F010 三件套、
  BACKLOG/CLAUDE/docs README、RETROSPECTIVE、`check_doc_consistency`，看形态是在把 main 并进分支），
  同时在 F009 spec/design 里做了"循环 15 → 循环 19"之类的编号改写。这些改动**不属于本轮范围**，
  未审、未改。
- 处置：本轮全部取证改为只读 `git show <rev>:<path>`；变异验证在 `git worktree add --detach 732d98e`
  的独立工作树里跑，跑完 `git checkout -- src` 复原并确认 0 处残留，不碰共享工作树。
- 一次自伤记录（如实登记）：re-baseline 之前，检视方在共享工作树里做钉点变异时脚本抛异常、
  未走到复原分支，导致 `spec.md` 一度留着被变异的文本；已用反向替换复原，并与 `main:spec.md`
  逐字对比确认一致（剩余差异全部是并行会话的编号改写）。教训写进下方模式小节。

## 独立核对方式（不采信 FIX-log 文字）

| 核对面 | 做法 | 结果 |
|---|---|---|
| commit 存在性与内容 | `git show` 四个短哈希，逐个比对声明与实际 diff | 一致，无"声明已修未落盘" |
| 文档落点 | 对 `transitional` / `E_UNLOAD_FAILED` / `KRONOS_VRAM_PROBE_MODE` / `test_f003_cli_contract.py` 四个机制关键词，在架构 + 三件套逐文件计数 | 全部命中且落在正确章节（架构 4/4、spec 9/8/5/2、design 6/7/2/1、tasks 3/1/1/2） |
| 门禁 | `.venv/bin/python tools/verify.py` on main | 全绿（生命周期/链接/DAG/一致性/依赖 pin/密钥/pytest/ruff） |
| 客户端回归 | 独立 worktree 跑 `test_f003_gpu_slot.py` + `test_f003_cli_contract.py` | 60 passed |
| 变异判红 | 四条：恢复条件改回 `action=="stopped"` / `client_deadline` 去余量 / 删 transitional 分支 / 忽略 `vram_readable` | 四条各自判红，且只红对应那一条用例 |
| 门禁钉点 | 把 NFR-006 编号改回 `SC-002/AC-010` | `check_doc_consistency` 判红 |

## Round 4 结转（10 条全部 fixed）

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F009-R4-001 | 过渡态无合法 wire 表示 | high | correctness | 根因 | original-coding | fixed | 明确第三态的 wire 值 | `state` 取值域加 `transitional`，客户端 fail-closed，决策表加行并同步期望表 | `test_f003_gpu_slot.py::test_transitional_state_fails_closed` | 4 | 5 | state-schema-gap |
| F009-R4-002 | E_TIMEOUT 后迟到 stop 无恢复 owner + 两端同 deadline | high | correctness | 根因 | fix-regression | fixed | 轮询 operation 至终态并恢复；客户端 deadline 更大 | 改为"发出过 stop 即持有恢复责任"（无条件幂等 restore，不轮询）+ `client_deadline()` 加余量 | `test_f003_cli_contract.py::test_mine_restores_kronos_when_stop_timed_out`、`test_f003_gpu_slot.py::test_each_lifecycle_action_uses_its_own_contract_timeout` | 4 | 5 | timeout-late-side-effect |
| F009-R4-003 | F009 AC-012 与 F010 AC-009/T018 成环 | high | correctness | 根因 | fix-regression | fixed | 证据所有权迁 F010 | F009 AC-012 止于载体+先红态（无 GPU 可验收），F010 独占解除 xfail；F010 spec/tasks 方向同步 | 文档侧 + `check_doc_consistency` 钉点「**本 AC 到此为止即算满足**」 | 4 | 5 | cross-feature-closure-cycle |
| F009-R4-004 | stop 后台异常无错误码与回滚规则 | high | correctness | 根因 | original-coding | fixed | 定义错误码与原子收敛策略 | 补 `E_UNLOAD_FAILED`，以"引用是否已丢"为界定死三个注入点落点，返回错误前必清 `operation` | 文档侧 + 架构钉点「**失败落点（逐注入点）**」；实现期载体 AC-002/AC-006 | 4 | 5 | incomplete-failure-contract |
| F009-R1-008 | status 的 5s 没有执行机制与 deadline owner | medium | correctness | 根因 | original-coding | fixed | 明确 deadline 归属与 probe 预算 | 裁决为服务端处理 deadline；探测只用剩余预算且受 `KRONOS_VRAM_PROBE_TIMEOUT_S` 约束；status 不进单飞执行器 | 架构钉点「**status 的 deadline 归属**」；实现期载体 AC-001/AC-007 | 1 | 5 | mechanism-weaker-than-claim |
| F009-R1-009 | 探测方式可配置无变量名/值域/默认 | medium | correctness | 根因 | original-coding | fixed | 定义变量或删掉该承诺 | FR-007 给出五变量表（`KRONOS_VRAM_PROBE_MODE=auto\|torch\|nvidia_smi` 等），单一来源不跨源回退，非法值启动判红 | 实现期载体 AC-007 / T005 | 1 | 5 | underspecified-config-contract |
| F009-R4-005 | 三条 restore 路径的证据被高估 | medium | test-coverage | 根因 | process-gap | fixed | AC/T014/T021 同时引用 CLI 测试 | 载体改 `test_f003_cli_contract.py`，新增正常结束/运行异常/stop 超时三条，连同取锁失败共四条各断言"恰一次" | `test_f003_cli_contract.py::test_mine_restores_kronos_after_a_normal_run` / `::..._after_a_failing_run` | 4 | 5 | acceptance-evidence-overclaim |
| F009-R4-006 | GPU 前置引用错误的 SC/AC 编号 | medium | quality | 症状 | fix-regression | fixed | 改为 AC-012/SC-005 并加钉点 | §3 与 NFR-006 改正，`check_doc_consistency` 增钉点 | 钉点变异：改回 SC-002/AC-010 即判红（本轮已复验） | 4 | 5 | stale-acceptance-reference |
| F009-R4-007 | 遗漏 F004 已验收端口契约迁移 | medium | correctness | 根因 | spec-drift | fixed | 在 F009 内显式迁移 | T013 写明同一提交内改 F004 spec/design + 精确断言 + 变异表；spec §3 与 design §1 纳入范围 | — （AC 覆盖缺口见本轮 R5-002） | 4 | 5 | accepted-contract-impact-omitted |
| F009-R4-008 | F010 立项后依赖元数据未同步 | low | quality | 症状 | process-gap | fixed | related_features 加 F010；T002 改核对 | 三件套 frontmatter 加 F010；T002 改为核对活跃 Feature 与完成边界无环；CLAUDE 索引改 doc-reviewing | 文档侧 | 4 | 5 | dependency-index-drift |

## 本轮新增 findings

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F009-R5-001 | §3 仍写客户端 5s/60s/120s，与 FR-009 矛盾 | medium | correctness | 根因 | fix-regression | open | 改为"服务端 deadline + 余量"并加钉点 | — | — | 5 | — | stale-acceptance-reference |
| F009-R5-002 | F004 端口迁移无 AC 覆盖 | medium | test-coverage | 根因 | process-gap | open | AC-009 增列 F004 契约测试载体 | — | — | 5 | — | acceptance-evidence-gap |
| F009-R5-003 | F003 契约摘要与服务端归属未同步 | medium | correctness | 根因 | spec-drift | open | 补错误码/transitional/恢复所有权；归属改 F009 | — | — | 5 | — | cross-feature-contract-drift |
| F009-R5-004 | 继承来的 stopped 无恢复 owner | medium | correctness | 根因 | original-coding | open | 架构 §7.1 裁决继承态归属后同步 FR-009 | — | — | 5 | — | recovery-ownership-hole |
| F009-R5-005 | stop 四种失败塌缩成同一 reason | medium | quality | 根因 | fix-regression | open | 按错误码分记 reason，处置不变 | — | — | 5 | — | evidence-attribution-collapse |
| F009-R5-006 | 记了恢复责任，不记恢复结果 | medium | test-coverage | 根因 | fix-regression | open | `kronos_offload` 增 `restore_result` + AC 断言 | — | — | 5 | — | acceptance-evidence-gap |
| F009-R5-007 | FR-004/NFR-002 的超时措辞未跟上 | low | quality | 症状 | fix-regression | open | 标明服务端 deadline；指向五变量表 | — | — | 5 | — | stale-acceptance-reference |
| F009-R5-008 | 参数名读作客户端超时、实为服务端 deadline | low | quality | 根因 | fix-regression | open | 改名或在 docstring 写明 | — | — | 5 | — | — |

## 关键证据

### F009-R5-001 · 同一份 spec 内部打架

`spec.md:119`（§3 范围内）仍写「F003 客户端的分动作超时（5s/60s/120s）与 `restore` 所有权
（三条退出路径均须恢复）」。R4-002 之后这两句都不成立了：客户端值是 10/65/125（服务端值 + 余量），
恢复的触发条件是「本轮发出过 stop」而不是"落在哪条退出路径上"。FR-009 / AC-010 / design §8 / T014 / T021
五处都改了，唯独范围段的摘要没改——照它实现，就会把 R4-002 修掉的缺陷原样写回来。

### F009-R5-002 · 能把统一门禁打红的动作没有 AC

R4-007 把 F004 端口契约迁移写进了 T013（含 `test_f004_compose_profile_contract.py` 的精确断言与
变异表），但 AC-009 的 tests 只有 `tests/integration/test_f009_lifecycle_deployment.py`。DAG 门禁不管
§2 实现任务的 verify 载体，一致性门禁也不校验 AC↔任务的载体交集，所以这条缺口没有任何机器会喊。
它恰好是 R4-005 的同型：**任务里有动作，验收里没有对应证据**。

### F009-R5-003 · live owner 的文档停在三轮之前

`docs/features/0.2/F003-alphagen-vendor/design.md:170` 的「Kronos 生命周期 Contract」仍写错误码
`E_UNAVAILABLE / E_BUSY / E_TIMEOUT / E_UNSUPPORTED_VERSION`（缺 R2-003 的 `E_BAD_REQUEST` 与
R4-004 的 `E_UNLOAD_FAILED`），客户端行为仍写「进入夜槽 → status →（running 则 stop）→ 确认释放 →
取锁 → **窗口结束 restore**」，没有 transitional 处置、没有 deadline 余量、没有"发出过 stop 即恢复"。
同一份 spec 的 AC-010 与 tasks §5 还把服务端写成「归 BACKLOG 待分配 feature / 规划中」，而 F009 早已是
`ready-for-development`。F003 正处于 `developing`，实现者读的就是这两页。

### F009-R5-004 · 恢复所有权规则只覆盖了一半入口

`kronos_offload.py:122`：`status.state == "stopped"` → `not_needed / already_stopped`，
`restore_required=False`。于是——上一轮运行在 stop 与 restore 之间被 SIGKILL（或断电）之后，
今晚这一轮看到实例已经是 stopped，照常取锁训练，跑完直接走人，**没有任何人把它恢复回去**。
这正是 R4-002 要消除的终态（Kronos 永久停机、白天 dry-line 没有实时信号），只是换了个入口到达。
契约文字本身没有自相矛盾（它只承诺"发出过 stop 的人负责"），但它给人的印象是该终态已被封死。

注意这条**不是简单地加一行 restore 就完事**：如果是运维人工停机，挖掘运行擅自把它恢复同样是错的。
因此需要一次裁决而不是一次补丁——这也是本轮唯一建议在开工前解决的条目。

### F009-R5-005 / R5-006 · 证据面只走了一半

- `stop` 的四种失败（`E_BUSY` 没开始 / `E_TIMEOUT` 仍在进行 / `E_UNLOAD_FAILED` 卸载炸了 /
  响应不是 stopped）全部记成 `reason="stop_failed"`。处置相同（fail-closed + 恢复责任）是对的，
  但事后归因完全不同——这正是 R2-002 当初立下"读数缺失与确实没释放必须分开记"的同一条标准，
  这次没有被执行。
- 运行记录新增了 `restore_required`（背没背责任），却没有任何字段记录**恢复成没成**：
  `cli.py` 的 finally 只在失败时往 stderr 打一行 WARNING。夜槽跑完第二天要复核"昨晚到底恢复了没"，
  run.json 答不出来。

## 正确性与质量双通道结论

- **正确性通道**：0 Critical / 0 High；4 条 Medium（R5-001/002/003/004）。不阻塞机制正确性，
  但 R5-004 触及契约措辞，建议开工前裁决。
- **质量通道**：2 条 Medium（R5-005/006，证据面）+ 2 条 Low。不阻塞。

## Readiness Gate

- [x] Critical/High 清零（本轮 0 High）
- [ ] 只剩 Low/Info：仍有 6 条 Medium → 停止条件未满足
- [x] Round 4 的 10 条独立核对全部成立（含四条变异判红）
- [x] 本地统一门禁全绿（main）
- [x] 客户端回归在独立 worktree 复跑通过（60 passed）
- [ ] CI：本轮非收敛候选轮，按协议 §7 未触发
- [x] 上游变更决策已做：`change_scope=in-place`，Round 6 仍 diff-only

裁决：**FAIL（不闭环）**。但性质与前四轮不同——无 High，6 条 Medium 中 3 条是纯文档同步
（R5-001/002/003）、2 条是证据字段（R5-005/006）、1 条需裁决（R5-004）。预计一轮闭合。

## 裁决记录

#1 · F009-R4-002 · partial→accepted · 修复方未采用建议的"轮询 `operation` 至终态"，改用"发出过 stop
即无条件幂等 restore"。**接纳**：证据成立——轮询必须设界，界外的迟到完成仍会漏；而 `restore` 幂等，
无条件调用的代价是一次空操作。检视方复核了 `test_mine_restores_kronos_when_stop_timed_out` 的变异判红，
确认该路径被锁死。原建议的"客户端 deadline 要大于服务端"半边已照做并有断言。· 裁决轮次 5

## 修复方下一轮入口

1. R5-001 / R5-007：改 spec 的两处措辞，R5-001 那句建议同时加一致性钉点（它已经错过一次）。
2. R5-002：AC-009 增列 F004 契约测试载体。
3. R5-003：改 F003 design §4 与 spec/tasks 的服务端归属——这是跨 Feature 提交，按文档拆开提交。
4. R5-004：**先在架构 §7.1 裁决继承态归属**，再同步 FR-009/AC-010 与客户端；不要直接在客户端打补丁。
5. R5-005 / R5-006：reason 分记 + `restore_result` 入运行记录，各配一条变异判红断言。
6. FIX-log 追加 Round 5 声明；Round 6 为收敛候选轮，届时由检视方触发一次 CI。
