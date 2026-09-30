---
kind: feature
id: F013
version: "0.2"
status: doc-reviewing
branch: docs/F013-batch-evaluation
gate_version: 1
related_features: [F002, F003, F005, F007, F008, F012]
topics: [evaluation, batch, cohort, snapshot, funnel]
doc_kind: spec
created: 2026-09-29
updated: 2026-09-29
---

# F013：工厂批量闭环·评测侧（批量评测编排）

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR3.3（cohort/多重检验）、FR3.8（正控制/漏斗）、FR3.9（canonical）；FR2.6 与 M2 批量能力标定。
- **架构来源**：`docs/alphamill-architecture.md` §4.4/§4.5（研究快照、评测产物）、§7.1（执行机边界）。
- **上游契约**：F012 `IR-004` completed run_dir；F003 FactorDef/生成事件；F007 ResearchSnapshot、canonical、population、synthesis；F008 PIT universe。
- **决策依据**：ADR-0003/0006/0007/0008；BACKLOG owner 2026-09-27「先 F012、再 F013、F005 后做 M2 爬坡」；[意图内核](kernel.md)。
- **功能类型 / 规格模式 / 变更类型**：backend + workflow / full / MIXED（新增适配与编排；增量扩展 F007 批量尝试/收尾、
  日历 mask 与折/GuardContext 消费、finalize 事务与原子回写、时间键相关性、synthesis v2；前置依赖 F012 选择尾窗 preset 增量）。
- **一句话意图**：把一个完成生成批次的全部已入册因子，在看评测结果前冻结成同一 cohort，以同一快照完成可恢复的 canonical → finalize → synthesis。

## 1. 问题、目标与非目标

### 问题

F012 已交付生成能力；评测仍要求手工提供 snapshot、signals、expression 和 cohort。
F003 事件封装与 F007 摄入格式不同；F007 当前报告缺少明确来源分布与最大流失级。
仅循环调用 canonical 还不能实现重试：现实现发布 INCOMPLETE 后立即登记，再调用会复用旧产物。

### 目标

补齐 BACKLOG 五处契约缺口，令批量执行、故障恢复和报告重建有唯一、可核验的输入与结果。
小批量先证明真实闭环；N=50 分别测量逐候选 canonical（含 bootstrap）与 finalize（相关性/统计，
无 bootstrap）成本，为后续 M2 排期提供证据。

### 非目标

不改生成算法/预筛、统计阈值、实验身份算法和 cohort 身份字段（F012 选择尾窗 preset 是 F012 侧
前置增量，不在本 Feature 内实现）；不接管组合最终留出、
永久确认窗、L2/L3 审计或实盘路径；不承诺候选通过数或盈利。
UI 归 F005，M2 正式 ≥50 候选爬坡在 F005 后单独验收。

## 2. 用户场景

### US-001：完成批次自动评测（Priority: P1）

运营者希望给出 completed run_dir 和预注册配置，得到整批正式证据与报告。
**为什么是这个优先级**：这是生成侧到评测侧的最小可用闭环。
**独立测试**：三个可加载因子及真实格式小湖，执行完整命令并核对承诺集合与注册集合。
**验收场景**：Given 三个已入册因子，when 启动批量评测，then 首次信号计算之前冻结三个成员，
所有实验引用同一快照；Given partial、事件计数不符、旧 end=cutoff 窗口或 reports 根在工作树内，
when 启动，then 非零拒绝且不冻结 cohort、不写任何产物。

### US-002：无人值守中断后继续（Priority: P1）

运营者希望中断后重跑同一命令能继续未完成成员，而不新增试验机会。
**为什么是这个优先级**：夜间批量运行必须防重复计数与无限重试。
**独立测试**：在发布、登记、finalize、synthesis 边界注入进程中断。
**验收场景**：Given 已完成一项、另一项确定性 INCOMPLETE，when 续跑，then 两者均幂等复用、不重算；
Given 一项 attempt 因中断/瞬态 IO 未产出结果，when 续跑，then 该项总尝试不超过三次，耗尽以
abandon/incomplete 终态登记且仍留在原分母；Given 冻结后代码变化导致批次阻断，when 操作员执行
batch-close，then 未终态成员（含未启动者）各以 batch_blocked 登记一次，cohort 以 INCOMPLETE 收口。

### US-003：读懂批次流失与成本（Priority: P2）

研究者希望在报告里区分生成拒绝、正式试验、有效独立数和最大流失级。
**为什么是这个优先级**：防止把名义产量或执行完成误读为证据通过。
**独立测试**：固定多个来源、并列流失、全零流失和不可计算独立数的台账夹具。
**验收场景**：Given 同一正式台账，when 两次重建，then synthesis 语义 ID 相同，来源总数和分母一致，
最大流失级按固定规则指认，统计缺失不伪装成零或 PASS。

## 3. 范围与边界

### 范围内

| BACKLOG 缺口 | 本 Feature 契约 | 验收 |
|---|---|---|
| ① 显式绑定 → 快照并整批钉死 | FR-001、DR-001；design §3/§4.1 | AC-001/002 |
| ② FactorDef → 信号与表达式串 | FR-002/003；design §4.2 | AC-003/004 |
| ③ 生成事件摄入适配 | FR-004；design §4.3 | AC-005 |
| ④ 冻结 → canonical → finalize → synthesis | FR-005/006/007/009；design §5 | AC-006/007/008/012 |
| ⑤ 来源分布与最大流失级 | FR-008；design §6 | AC-009/010 |

### 范围外

v1 每次只消费一个 F012 v2、generator=alphagen、显式绑定模式、resample=1h、以 F012 选择尾窗 preset
生成的 completed run_dir，pool 必须为 null；旧 end=cutoff 产物（含现有两次 50 候选 run）明确拒绝。
不混跑多个 run、不提供候选筛选/限量/preview 模式，不新增 GPU 调度、HTTP API、前端页面或定时服务。
评测快照 cutoff 晚于生成绑定（「生成绑定 ⊆ 评测快照」）不在本 Feature 范围，M2 之后另立增量。
保留 F007 既有单候选命令及旧报告读取；旧 manual/v1 产物仍由原入口消费。

### 边界场景

零入册 completed 批次以 `E_BATCH_EMPTY` 拒绝，不制造空正式 cohort；预算耗尽但有入册者可整批消费。
损坏因子、丢事件、改配置、替换快照或未知原因码在准备期整批失败，不静默删成员。
冻结后单候选信号失败（空/全 NaN/Inf/退化）在**成员层**只使该候选确定性 INCOMPLETE，不暂停批次、
不缩减承诺；但它仍在比较集合内，按 F007 finalize 失败关闭口径（FR-007）会使 **cohort 统计 INCOMPLETE**，
整批不产出可晋级结论——50 个里坏 1 个即如此，这是有意保留的门禁，不是「只影响该候选」。
已有正式成员/来源 pin 冲突则拒绝接管。未设置或位于工作树内的 reports 根在任何发布前拒绝。
只有 FINALIZED 且报告发布才算编排完成（COMPLETED；受限收尾为 CLOSED）；其中可能全部
dead/incomplete，仍不得宣传为通过。

## 4. 需求

### 功能需求

### Requirement: 绑定转换与整批快照（`FR-001`）

当接收有效生成批次时，系统应核验 run、config、因子与事件，使用 run 的显式成员、cutoff、
symbol/universe 构建并发布 ResearchSnapshot；成员集及每成员版本/摘要/保真度/事件时间范围、cutoff、
symbol_map、universe 与原绑定逐字段一致，不放宽为包含、不延后 cutoff、不增删成员。
选择窗 `[S,E)` 与 H 必须等于 F012 选择尾窗 preset 持久化的参数（S=生成窗 end，E=cutoff−H）。
F003 `continuous_24_7` 日历按 design §4.1 的版本化转换映射为 F007 windows 日历，
源/目标 calendar 与组合 digest 分别核验并留映射，不做源目标 digest 相等比较。
若提供 `--snapshot`，只接受已发布且与该映射推导完全一致者；不得 latest、换版本或按 exported_at 猜时点。
同 cohort 在首个 canonical 前钉死一个 batch binding，canonical/finalize/abandon 必须执行该约束。

### Requirement: 可复算信号生产（`FR-002`）

当批次已冻结时，系统应从绑定湖通过 FactorDef.compute 生成列序严格为
`time,symbol,close,signal,forward_return` 的 CSV；保留真实信号数值、逐 pair 日历和 PIT 宇宙，
不以当前宇宙筛历史，不跨缺口/退市拼标签，不读取选择窗之外的留出/确认数据。
标签端点、warmup、非有限值与输出编码按 design §4.2 固定，所有剔除计数留证；数值有限性由
producer 显式校验。日历 mask、折索引与标签端点写入有摘要的 sidecar，并由 F007 批量路径的
成本/持仓/稳定性/bootstrap/guard 实际消费：不相邻 bar 不得被当相邻，稳定性按预注册
n_folds/H/embargo 切分，GuardContext 填实际事实，缺上下文不得记 PASS。

### Requirement: 表达式序列化（`FR-003`）

当读取 token 序列时，系统应使用带版本的确定性后缀栈序列化，保留操作数顺序、常数、
通道全名与窗口；对未知算子、负窗口、栈错误失败关闭。canonical 的 expression 必须来自该
因子，不能由调用方手填另一个表达式，也不能靠 repr(tokens) 绕过生成纯度门与 F007 L1。
负窗口、未知算子与未来通道的保证归 F003 purity + 已登记编译器 + renderer 白名单；F007 L1 仍运行，
但它是子串扫描，不作为这些保证的依据。

### Requirement: 生成事件适配（`FR-004`）

当摄入 events.jsonl 时，系统应依据 `(run_id,event_seq)` 检查唯一性与连续性，严格映射
`event_type+payload` 到 F007 扁平格式（事件类型保留全名）、映射拒绝原因并展平嵌套 counts；
完成事件无 status，从已核验 run.json 补入；核对 run.json、唯一完成事件、因子数与拒绝事件数。
未知字段版本/类型/原因、重复或截断记录必须拒绝。保留源序号、原因、detail 与 definition_digest；
reachability 另存子原因（after_cost_return/trades_90d/degenerate_signal/unknown），子项之和守恒。
生成拒绝属于生成漏斗分母，不新增 canonical commitment。

### Requirement: 预注册整批 canonical（`FR-005`）

当所有结构前置检查通过时，系统应按 definition_digest 排序冻结全部入册成员及方法、窗口、
成本、种子、代码摘要和来源，不得在读评测分数后筛选。只有确定性、显式操作员入口可运行
canonical；Agent capability 不得调用。所有成员终态登记齐备后才允许 finalize。

### Requirement: 幂等与有界重试（`FR-006`）

当进程续跑时，系统应复用已终态成员与已完成 attempt。EVIDENCE_READY、REJECTED 与确定性
INCOMPLETE（evidence_complete=False、统计退化/样本不足、空/非有限/退化信号）首次即终态，不重算。
仅未产出完整结果的中断、瞬态异常与读取 IO 错误可在相同 experiment_id 下重试，总尝试
≤ max_retries+1=3（预算唯一来源为冻结的 method_config），保留每次不可变证据；耗尽后以
`batch_retry_exhausted` abandon 为 incomplete；未知异常暂停批次而非盲目重试。
正式登记只写一次；进程重启不得重置预算，旧单候选已登记结果不得被批量入口改写；
批次级输入/完整性错误暂停批次并非零返回，不作为统计拒绝吞掉。
重试耗尽、确定性 INCOMPLETE 与 batch_blocked 成员都留在比较集合，其 cohort 级后果按 FR-007 口径，
不得为保住其余成员的结论而把它们移出 finalize。

### Requirement: 完成与恢复顺序（`FR-007`）

当登记集合等于承诺集合时，系统应先原子冻结 finalize 输入（本 cohort 登记/曲线、排除本 cohort 的
registry 行及所引曲线内容副本），再基于冻结输入计算并原子发布带输入摘要的 verdict，最后
回写 registry 并发布 synthesis。已有 verdict 必须核验并复用，不能因后来的全局 registry 变化重新裁决；
回写同 key 不同内容报冲突，以锁 + 原子替换写入不产生坏半行。相关性按规范时间键配对，
错时/不等长/缺证据显式 comparison_unavailable 并使 cohort 统计 INCOMPLETE，不回退 1.0。
cohort 统计完整性口径沿用 F007 失败关闭（不改门禁，design §5）：比较集合为**全部登记成员**
（= 承诺集合 = trial_count）；任一成员缺可读曲线或报告、任一「有报告且非 rejected」成员缺 p 值、
或 §5 必需配对不可比，cohort_statistics 即 INCOMPLETE；此时全部 promising/provisional/
blocked_pending_audit 降为 incomplete，dead/rejected/underpowered/incomplete 保持原值。
不得剔除 INCOMPLETE 成员后对剩余子集另做多重检验；报告须列出致 INCOMPLETE 的成员与原因。
失败时依持久化事实续跑当前阶段；未 finalize 不输出可晋级结论。

### Requirement: 可核算的漏斗（`FR-008`）

当生成 synthesis 时，系统应输出名义生成数、正式试验数、有效独立数、按 generator 的
来源分布及显式最大流失级；first-loss 每候选只归因一次，平局按冻结阶段顺序处理，
INCOMPLETE、UNDERPOWERED 与 FAIL 保留分项。first-loss 是独立结构，不写入五阶段 FailureBucket；
L1 拒绝按 `signal_quality FAIL + mechanism=lookahead` 识别为 methodology，L2/L3 保留
`not_yet_available`。有效独立数带方法元数据（`ordered_mean_abs_rho_v1`），不可计算时显示
null+原因，不作零值。来源、最大流失级与方法版本纳入报告语义 ID；保留事实/推断/建议三栏与五阶段矩阵。

### Requirement: 阻断批次受限收尾（`FR-009`）

当冻结批次因代码/输入变化无法续跑时，系统应允许操作员以固定原因 `batch_blocked` 收尾：
只读冻结材料，不生成信号、不重算、不提升 verdict、不 rebind；已登记者保持原状，其余未终态成员
（含未启动者）各以无评测证据的 INCOMPLETE 登记一次，再 finalize 为 cohort_statistics=INCOMPLETE，
状态为 CLOSED，分母不变。已 COMPLETED 或已有 verdict 的批次拒绝收尾；已有 verdict 但未 COMPLETED
时代码变化只能检出 manifest 记录的冻结 commit 续跑回写与报告（design §5）。

### 数据 / 实体需求

- **DR-001**：新增不可变 batch manifest、cohort binding、日历映射、finalize 输入与收尾记录，绑定 snapshot、全部成员与配置摘要；进度从持久化尝试/登记/发布事实恢复，不能以可修改 checkpoint 取代 population 真相源。
- **DR-002**：信号字节摘要、生产者版本、表达式与 token 摘要、窗口/剔除统计、日历 mask 与折索引写 sidecar；源 run_dir、湖与已发布历史证据只读。

### 事件 / Trace 需求

- **TR-001**：批次和尝试事件记录 batch/cohort/experiment/candidate、attempt_no、输入摘要、阶段、错误和证据引用；重试与恢复不重复正式登记，abandon 留原因。

### API / 接口需求

- **IR-001**：提供 `alphamill-evaluation batch --run-dir PATH --config PATH --seed INT [--snapshot ID] [--json]`；同参数重跑即续跑，不暴露候选选择或重置预算参数。配置字段与返回结构见 design §4。
- **IR-002**：退出 0 仅表示 FINALIZED 报告已发布；1 为领域/运行失败，2 为用法错误；首屏同时显示编排状态、cohort 统计状态及各 verdict 数，不能将 0 等同 PASS。
- **IR-003**：提供操作员命令 `alphamill-evaluation batch-close --batch-id ID --reason batch_blocked`；不接受新 snapshot/config/seed，Agent 不可调用，退出 0 仅表示 CLOSED 报告已发布。

### 非功能需求

- **NFR-001**：单机本地文件系统单写者、候选串行、崩溃可恢复；对同 cohort 并发冻结/运行/finalize 失败关闭，无超时抢活锁。批次所有产物写入显式设置、realpath 位于工作树外的 `ALPHAMILL_REPORTS_DIR`，未设置或落在工作树内时零写入拒绝。
- **NFR-002**：在执行机取小批量真实闭环证据，并以 N=50 基准分别测信号生产、逐候选 canonical（含 bootstrap）、finalize（相关性/统计）耗时及峰值 RSS；基准钉死 dsr_threshold 等统计参数并断言 effective_trials/DSR 真正执行，分 R=0 与 R=50 既有 registry 两组；预注册预算见 design §8，超限报告并阻止 F013 性能验收。
- **NFR-003**：不降级统计/纯度/快照/干净工作树门禁（不补 ignore、不加绕过开关），不读取线上修订态或真实下单；旧单候选行为与旧 synthesis ID 保持可读兼容。

## 5. 生命周期与不变量

`PREPARED → FROZEN → EVALUATING → FINALIZING → REPORTING → COMPLETED`；
受限收尾 `FROZEN|EVALUATING|FINALIZING → CLOSING → CLOSED`（FR-009），CLOSED 与 COMPLETED 分列。
失败/中断停在当前阶段，依据持久化事实继续，不倒退、删除承诺或改语义输入。
候选 `PENDING → ATTEMPT(1..3) → terminal registration` 或 `PENDING → batch_blocked registration`；
只有未产出完整结果的瞬态/中断 attempt 可重试，确定性 INCOMPLETE 一次终态。

批次所有成员 snapshot/config/code/seed 固定；attempt 不进实验身份，不增加 trial_count。
`proposed = registered_generation + sum(generation_rejected)`；
`trial_count = registered_generation = len(commitments)`；finalize 时 `member_count = trial_count`。
cohort v1 身份字段不增加 snapshot_id，以强制的一对一 binding 检查防混快照。

## 6. 成功与验收

### 成功标准

- **SC-001**：执行机 3–5 个真实候选无人手工拼 signals/expression 完成闭环，重跑计数不变。
- **SC-002**：故障注入后每个承诺各一次终态登记，确定性 INCOMPLETE 不重算、瞬态尝试总数不超过三次，无部分 verdict；阻断批次可收尾为 CLOSED。
- **SC-003**：报告可确定性重建，五处缺口逐条有正反测试，N=50 性能取证达预算。

### 验收清单

以下 tests 路径为计划文件，此阶段不创建测试或伪造通过证据。

- [ ] **AC-001** (`FR-001`, `DR-001`): 当绑定转换或重复发布时，snapshot 与日历映射同 ID；反例（旧 end=cutoff 窗口、selection/H 与 preset 不符、成员增删、版本/digest/cutoff/覆盖不符、非 continuous_24_7/非 UTC 源日历、篡改源摘要、改转换版本/窗口、伪造映射、错目标或组合 digest、`--snapshot` 目标日历不符、snapshot 绑定模式、非 1h）均在冻结前拒绝 — tests: `tests/contract/test_f013_batch_binding.py`
- [ ] **AC-002** (`FR-001`, `FR-005`, `NFR-001`): 若续跑换 snapshot/config/code 或两个进程争同 cohort，则拒绝混写，首次评测前全部承诺已冻结 — tests: `tests/contract/test_f013_batch_binding.py`
- [ ] **AC-003** (`FR-002`, `DR-002`): 当从固定湖生产信号时，逐点匹配 compute，标签不跨缺口/折/退市，重复执行 CSV 字节相同；空/退化候选只成该候选 INCOMPLETE；缺口处持仓断开，改 H/折/embargo 改变实际切分，缺 sidecar 或空 GuardContext 拒绝 — tests: `tests/unit/test_f013_signal_producer.py`
- [ ] **AC-004** (`FR-003`, `NFR-003`): 当序列化窗口/成对算子与常数时语义不丢失；未知/负窗口/错栈必须拒绝 — tests: `tests/unit/test_f013_expression_render.py`
- [ ] **AC-005** (`FR-004`): 当真实格式生成事件被适配时四原因与 reachability 子原因正确且守恒、definition_digest 保留；重复/漏事件/未知原因/partial 不写 cohort — tests: `tests/contract/test_f013_generation_adapter.py`
- [ ] **AC-006** (`FR-005`, `IR-001`, `NFR-001`, `NFR-003`): 当执行小批命令时整批直接 canonical，Agent/零批/非法来源被拒，所有成员进入同一预注册总体；默认或仓内 reports 根零写入拒绝，外置根跑完后 `git status --porcelain` 为空 — tests: `tests/integration/test_f013_batch_journey.py`
- [ ] **AC-007** (`FR-006`, `TR-001`, `NFR-001`): 当确定性 INCOMPLETE 时只评测一次；当瞬态中断/IO 反复发生或各阶段崩溃时，预算持久化、总尝试 ≤3 且只登记一次；已成功者不重算 — tests: `tests/integration/test_f013_batch_recovery.py`
- [ ] **AC-008** (`FR-007`, `IR-002`): 若未收齐则无 verdict；verdict 发布后别的 cohort 改 registry 不引起重裁；回写中断不产生坏半行、同 key 异内容报冲突；错时/不等长/缺证据配对使统计 INCOMPLETE 且 effective_trials=null；统计 INCOMPLETE 不显示 PASS；当 N 个成员中恰有 1 个为确定性 INCOMPLETE（无曲线）、1 个重试耗尽 abandon 或 1 个有报告但缺 p 值时，cohort_statistics=INCOMPLETE，其余 promising/provisional/blocked_pending_audit 全部降为 incomplete、dead/rejected/underpowered 保持，比较集合仍为全部 N 个登记成员（不对剩余子集重算），报告列出致因成员与原因 — tests: `tests/integration/test_f013_batch_recovery.py`、`tests/contract/test_f013_batch_correlations.py`
- [ ] **AC-009** (`FR-008`, `DR-002`): 当聚合来源与 first-loss 时分母可对账，平局/零流失/未知证据显式表示，不重复计流失；L1 拒绝按 mechanism 归 methodology、L2/L3 保持 not_yet_available、effective_trials 带方法元数据 — tests: `tests/unit/test_f013_batch_synthesis.py`
- [ ] **AC-010** (`FR-008`, `NFR-003`): 当删除派生报告再重建时语义 ID 不变；旧 v1 报告仍以原 ID 读取 — tests: `tests/contract/test_f013_synthesis_compatibility.py`
- [ ] **AC-011** (`NFR-002`): 当执行机跑真实小批和 N=50 基准（R=0/R=50 两组）时，留机器/数据/代码/分阶段耗时/RSS 证据并达预算；缺统计参数的负例不计为基准成功 — tests: `tests/integration/test_f013_batch_capacity.py`
- [ ] **AC-012** (`FR-009`, `IR-003`, `NFR-003`): 当冻结后代码变化阻断批次时，batch-close 使含未启动者在内的每个未终态成员以 batch_blocked 登记一次、cohort INCOMPLETE、状态 CLOSED，已登记结论不变；Agent/已有 verdict/新 snapshot 参数被拒，中断可幂等续写；已有 verdict 后代码变化时 batch 报 E_BATCH_BINDING_CONFLICT 并给出冻结 code_git_commit，检出该 commit 后续跑补完回写与报告且 verdict 不变 — tests: `tests/integration/test_f013_batch_recovery.py`

## 7. 测试、依赖与决策

### 测试策略

先契约/旅程 RED，再实现 GREEN；测试映射见 [design §8](design.md#8-测试策略与验收映射)。
开发机跑统一 verify；执行机跑带 ALPHAMILL_INTEGRATION=1 的真实闭环与容量基准，skip 不算验收。
复用 F007 正负控制回归，不以「至少一个候选通过」作验收；现有 L2/L3 `not_yet_available` 状态如实保留。

### 依赖

- **前置（未就绪）**：F012 选择尾窗 window preset 增量（owner 2026-09-29 裁决 P0-1 选 a；
  `window.end = cutoff − 选择窗长度 − H`，契约见 design §4.1）。载体为 `BACKLOG.md`「规划中」
  表的「F012 选择尾窗 preset 增量（selection_tail_1h_2y_v1）」行（含验收标准）。须合入并以其
  重新生成合规 run，T002 核验后方可开始真实闭环；增量在 F012 侧另立文档与实现，不由本 Feature 代写。
- **已存在**：F012 IR-004、F003 registry/compiler/lake_tensor、F002 manifests/reader、F008 universe、
  F007 population/评测门。下游 F005 只读消费 v2 报告；M2 爬坡依赖 F005 上线。

### 决策与风险

| 决策 / 风险 | 结论与处置 |
|---|---|
| 直接 canonical | 沿用 owner 裁决，冻结前不跑 preview 挑选 |
| 已发布 INCOMPLETE 会被复用 | 新增 opt-in 批量尝试协议，终态前延迟正式登记；不得假装循环调用已有 CLI 即完成 |
| 确定性 INCOMPLETE 重试无意义 | 同输入 + 固定 bootstrap seed 结果不变，只重试未产出结果的瞬态/中断 attempt |
| snapshot 不在 cohort 身份 | 使用唯一 binding 并在下游写入口强制验证，不改已有身份算法 |
| 代码变化使冻结批次永久冲突 | 不 rebind；提供 FR-009 受限收尾，分母诚实地以 INCOMPLETE 收口 |
| 标签单列限制 | v1 只接受一个正整数 bar horizon；多 horizon 显式拒绝，后续增量再扩展 |
| 选择窗为空（现有 F012 end=cutoff） | owner 裁决方案 a：F012 选择尾窗 preset 前置增量；方案 b（评测 cutoff 晚于生成绑定）M2 之后另立增量 |
| 历史 registry 不可比 | 按时间键严格配对，不可比即 INCOMPLETE 如实报告，不换空根逃门禁 |
| 性能与真实数据覆盖 | 实测任务必须交证据；现有两次 50 候选 run 无独立选择窗，不挪用留出，以新 preset 重新生成 |

## 8. 待确认问题

无
