---
kind: feature
id: F013
version: "0.2"
related_features: [F002, F003, F005, F007, F008, F012]
topics: [evaluation, batch, contracts]
doc_kind: design
created: 2026-09-29
updated: 2026-09-29
---

# F013：工厂批量闭环·评测侧 — 技术设计

> Owner: Georg | [行为契约](spec.md) | [任务](tasks.md)

## 0. 输入与约束

本文件冻结 BACKLOG 的五处契约；以下新增接口/文件均为设计，尚未实现。
上游：F012 IR-004；ADR-0003/0006/0007/0008；F007 单候选评测与不可变发布协议。
只读湖、单执行机、非 Agent 确定性编排；不修改已收口 Feature 文档来倒写本次增量。

代码核对基线：main 的 `evaluation/canonical_execute.py` 会立即登记 INCOMPLETE，
`canonical.py` 会复用该发布，`population.registrations` 拒绝同成员冲突终态；
因此真正的有界重试必须显式扩展 F007 执行/发布边界，不能只写外层循环。

## 1. 技术概要与影响面

| 区域 / 契约 | 去向 | 本次影响 |
|---|---|---|
| F012 window preset / CLI / config | 前置增量（T002） | 新增带选择期尾窗的 preset；合入并重新生成后才可消费；旧产物只读 |
| F012 run/config/events/factors/feature_maps | 只读消费 | v2 completed alphagen，核对 config_digest 和因子定义 |
| F003 binding/compiler/lake_tensor/operator_registry | 只读消费 | 显式绑定校验、信号求值、后缀表达式语义 |
| F002 manifest/reader、F008 universe | 只读消费 | 不改湖/联机库/宇宙口径 |
| F007 ResearchSnapshot/population/ExperimentContext | 新增旁置 binding，修改入口校验 | 身份算法保持不变，整批 pin 强制检查 |
| F007 canonical_execute/publisher/registration/abandon | 修改 | 批量 opt-in 尝试协议，旧单候选无 pin 路径兼容 |
| F007 run_config/pipeline/stability/guards | 修改 | 接收有摘要的日历 mask、折和真实 GuardContext；消费端一起改，不能仅写 sidecar |
| F007 finalize/dedup/registry_writeback | 修改 | 时间键相关性、冻结 registry 输入、已有 verdict 复用与原子补回写 |
| F007 generation_ingest | 新增边界适配 | 原扁平格式摄入继续可用，生成原文不改 |
| F007 synthesis/synthesis_analysis | 修改 | schema v2 来源/first-loss，新旧双读 |
| CLI、批次存储 | 新增 | batch / batch-close 子命令与外置 reports 根下 batches，不新增服务 |
| 文档与迁移矩阵 | 新增 F013，更新索引 | F001 迁移矩阵无变更；无 SQL migration |

UI/browser-check：不适用，无页面交付；F005 后续消费报告。设计稳定后在实施阶段把跨模块
接口增量回写架构 §4.4/§4.5，当前仅在 F013 冻结。

## 2. 架构与模块边界

`evaluation/batch_cli.py → batch_runner.py → batch_binding / generation_adapter / signal_producer /
expression_render → F007 canonical/finalize → synthesis`。
模块名为拟新增；单文件遵守 350 行上限。`batch_store.py` 拥有批次身份、锁、attempt journal；
`experiment_store` 继续拥有 snapshot/cohort/population/报告，runner 无裁决实现。

入口先完成结构检查和快照发布，再在 cohort 独占锁内原子写 batch manifest、binding 和
cohort。任何半完成准备都不能启动 canonical；恢复必须验证所有记录互相引用一致。
信号生产在 FROZEN 后开始，绝不从 prefilter 分数或 preview 结果选成员。

## 3. 数据模型与 Migration

### 批次身份与持久化

`batch_id = sha256(canonical_json({schema_version:1, source_run_id, source_digest,
cohort_id, research_snapshot_id, evaluation_config_digest, seed, code_build_digest,
producer_version, expression_format_version}))`。
重试预算唯一来源为 `method_config.normalized.batch.max_retries=2`，经
evaluation_config_digest 进入身份；不再存第二份 retry_limit。
source_digest 为 run.json/config.json/events.jsonl/prefilter.jsonl/全部 factors 与 feature_maps 的
排序相对路径+文件摘要清单摘要；物理根路径、主机、时间不进 batch 身份。prefilter 仅完整性
留证，不依据数值选样。batch identity 可以比 experiment identity 更严格，不替代后者。

| 路径（相对 reports） | 内容与写规则 |
|---|---|
| `batches/<batch_id>/manifest.json` | schema、上述身份输入、cohort 定义、candidate→factor/definition_digest、输入文件清单、配置副本引用、冻结时 `code_git_commit`（provenance，不进身份）；不可变 |
| `cohorts/<cohort_id>/batch_binding.json` | schema=1、batch_id、snapshot_id、config_digest、code_digest、seed、manifest ref；原子创建，同语义幂等，冲突拒绝 |
| `batches/<batch_id>/signals/<candidate_id>.csv` 与 `.json` | CSV 与 sidecar 成对原子发布，按摘要复用；sidecar 包含 DR-002 字段及实际输入范围 |
| `batches/<batch_id>/attempts/<candidate_id>/<1..3>/` | immutable started.json、结果 manifest/report/curves/events 或 error.json；不是 official population |
| `batches/<batch_id>/events/<event_key>.json` | 原子追加事件，event_key=候选/attempt/阶段；状态由事件与正式产物重建，checkpoint 只作缓存 |
| `batches/<batch_id>/calendar_mapping.json` | §4.1 的源/评测日历及组合 digest 映射、转换输入与版本；manifest 引用其摘要 |
| `cohorts/<cohort_id>/finalize_inputs.json` | §5 的冻结登记、registry 行/曲线快照和方法摘要；同 cohort 首次 finalize 原子创建 |
| `batches/<batch_id>/closure.json` | 操作员受限收尾的原因、原 pin、当前执行代码摘要；只追加收尾事实，不重绑定 |

cohort v1 保留原 IDENTITY_FIELDS；`commitments` 按完整 definition_digest 排序，
`candidate_id=factor_id`，同时冻结 factor_id 与完整 digest，发现短 ID 冲突或重复定义即拒绝。
`hypothesis_family` 必须与候选假设所属族一致（F012 默认 mechanism_unknown）；
`selection_stage` 取因子 scope（`cross_sectional | time_series`），整批必须一致；
当前 AlphaGen 入册者为 cross_sectional，混 scope 拒绝而不拆批。
`method_config_ref/cost_model_ref` 取规范化内容摘要；
`inclusion_rules` 固定为全部入册、不读取评测结果，并记录 source_run_id、source_digest。
`window` 按 §4.1 规范化后完整拷贝预注册配置，universe/calendar_digest 取已发布快照。
definition_digest 排序同时决定 cohort 内查重「保留在先者」优先级，不按收益择优；
effective_trials 的有序估计也固定用此顺序。
同 source 的文件改变视为篡改而非新批次：校验原 run 绑定和已有 source→batch 记录；
已冻结后不得以新 batch_id 绕过该 source/cohort 的语义冲突。
source→batch 记录为 `batches/_sources/<run_id>.json`，持有 source 锁时原子创建。

不迁移历史 cohort；无 binding 的旧单候选保持原行为。已有 cohort 如果有成员登记或 verdict，
拒绝新批次接管；未开始且无 pin 的同 ID cohort 只有逐字节一致才能绑定。
不提供删除/重置/rebind 命令；新研究输入需事先定义新的研究试验，不能续跑时更换。

## 4. 接口、Contract 与 Event

### 4.1 批量入口与绑定转换（缺口①）

```text
alphamill-evaluation batch --run-dir PATH --config PATH --seed INT [--snapshot sha256:...] [--json]
```

配置沿用 F007 `method_config/cost_model/window`，批量 v1 强制增加：
`method_config.normalized.batch = {schema_version:1, producer_version:"factor-csv-v1",
expression_format_version:"postfix-call-v1", signal_transform:"identity",
close_column:<完整湖通道名>, require_bitemporal:<bool>, max_retries:2}`。
这段进入 ExperimentContext 的 method_config，影响语义的方法不能只放 metadata。
`window.selection=[S,E)`、`window.label_horizons=[H]`（H 为正整数、单位为 resample bar）、
`window.folds=[{train:[a,b),validation:[c,d)}...]` 必填。区间写成二元素 UTC 字符串数组；
先校验 start < end，再统一成微秒精度 `+00:00` 文本并按 validation.start 排序后冻结。
不能借 ExperimentContext 把 selection 当集合排序来修复反向区间。所有折在 `[S,E)` 内，
train.end ≤ validation.start，validation 互不重叠。`method_config.normalized.stability`
须冻结 `n_folds`（等于 folds 数且 ≥ min_folds=3）、`embargo_bars`（整数且 ≥H）、
`purge=label_endpoint`；不自动从测试模板猜研究窗口。
F007 当前 window_digest 会丢 folds，故规范化完整 window 进入 cohort.window 与 batch
config digest，借 cohort_id 绑定实验；不改 ExperimentContext 既有身份算法。

只接受 F012 显式绑定，snapshot 绑定模式拒绝。datasets 从 config 读并校验摘要；
`config.resample == config.window.resample == run.window.resample == "1h"`，窗口起止也一致。
`run.window` 已有 resample，不宣称它缺失。ohlcv_1m 是 event_time_only，所以当前真实输入
必须显式 `require_bitemporal=false` 并展示用途限制；true 要求所有成员为 bitemporal，
不满足就拒绝，不能自动降级。1m 输出及其他频率不在 v1 范围。

**F012 前置增量（owner P0-1 选 a）**：增量在 F012 侧另立文档与实现（[F014](../F014-selection-tail-preset/spec.md)），命名以其为准，但必须
满足下列 F013 消费契约。新增版本化 preset `selection_tail_1h_2y_v1`，
参数为预注册选择窗长度 L（正整数小时）和 H（正整数 bar），Δ=1h。
`generation.window.end = cutoff − L − H*Δ`，start=end−730d（沿用 2y 语义，不截到湖起点；
现有湖起点 2024-09-10，start 会早 L+H，实际可用生成数据不足 730 天，F012 增量文档须注明）；
F013 使用 `S=generation.window.end`、`E=cutoff−H*Δ`，要求 `E−S=L`。
F012 CLI、config 和 run 持久化并互验 preset/参数/派生 window（新增元数据纳入 config_digest）。
批量配置的 `window.selection` 必须恰为 `[S,E)`、`label_horizons` 必须恰为 `[H]`，与 run 持久化的
preset 参数逐项相等，否则 E_BATCH_INPUT_INVALID；不能在评测侧另选 L/H。
生成、训练、预筛不得读到 end 及之后的尾窗；绑定 cutoff 与成员保持原值。
T002 必须先取得该增量的合入和回归证据，再生成新的 3–5 候选完整 run；旧 end=cutoff
产物明确拒绝，不能用改窗口 JSON 或截取旧 50 候选冒充。尾窗必须容纳预注册折及标签。
H*Δ 尾部余量不授权读取 E 之后数据，§4.2 仍要求标签端点处于所属折和 `[S,E)`。
评测 cutoff 晚于生成绑定的方案 b 不在 F013 范围，M2 之后另立增量。

**绑定逐字段一致与日历映射**：`load_verified_run`（F014 design §4 唯一入口，完成 config_digest 与 preset/L/H/window 三处互验）`→ validate_binding → 转换日历 →
build_snapshot(allow_latest=False) → 逐字段比较/映射核验 → publish_snapshot → load_snapshot`。
成员集完全相等，每成员的 data_version/value_digest/as_of_fidelity/event_time_min/event_time_max、
cutoff、symbol_map_digest、universe_digest 均与原绑定逐字段一致（时间先规范化）；
不只比较 data_version，不放宽为包含关系，不延后 cutoff、不增删成员。
注意两侧事件时间口径不同：F012 `validate_binding` 只要求声明范围被 manifest 全部分区覆盖
（`binding_checks.py:114-120`），F007 `build_snapshot` 按 rows>0 的分区重算
（`research_snapshot.py:143-146`）；二者不等时本比较必拒，不放宽。T002 预检须按后者口径预算并
比对，不等则回 F012 处理（BACKLOG 增量行验收④），不在评测侧改写。
日历因 schema 不同仅按以下可重算映射核验，不能把源 digest 与目标 digest 直接相等比较：

| 映射项 | 冻结规则（`continuous-to-windows-v1`） |
|---|---|
| 源 | 原 artifact 必须恰为 `{schema_version:1,kind:"continuous_24_7",timezone:"UTC"}`，核验源 calendar_digest 和原 universe_calendar_digest |
| 输入 | 规范化预注册 window、Δ、全部 token 推导的最大 warmup；W=S−warmup*Δ；转换前只读结构，不求值 |
| 目标 | `{schema_version:1,timezone:"UTC",windows:[{start:W,end:cutoff+Δ}]}`，时间采用上述 UTC 规范；末端加 Δ 仅为半开日历能包含 cutoff，不延长读数权限 |
| 摘要 | 源/目标分别按所属模块 canonical JSON 算 calendar_digest；源组合摘要按 F003 `binding_checks` 的 `{universe,calendar}` 公式重算并等于绑定值，目标组合摘要按 F007 `universe_calendar_digest(universe_digest,calendar_digest)` 重算；universe_digest 两侧相同；目标通过 F007 validate_calendar |
| 持久化 | mapping 保存 source_calendar_digest、source_universe_calendar_digest、evaluation_calendar_digest、evaluation_universe_calendar_digest、完整转换输入/版本及摘要；目标摘要进入 snapshot/cohort pin |

转换只把 continuous 日历在研究读取范围内显式化，不证明数据覆盖或 PIT 可交易性；
§4.2 的实际观测 mask 单独证明这些事实。成员 coverage、warmup、标签检查仍由原门禁执行。
`--snapshot` 须逐项等于按这份映射推导的快照，包括目标日历；不能只检查源 digest 存在。
错 kind/timezone、篡改源摘要、变换窗口/版本、伪造映射、错目标/组合摘要、晚 cutoff 或
成员缺失均在冻结前拒绝（AC-001）；重复构建须同 ID。

输出 JSON 固定字段：`batch_id,cohort_id,research_snapshot_id,state,completed_members,total_members,
cohort_statistics_status,cohort_incomplete_causes,verdict_counts,synthesis_ref,error_code,closure_reason`；
尚无数据的字段为 null 并带原因（cohort_incomplete_causes 口径见 §5 完整性小节）。
state 枚举：`PREPARED/FROZEN/EVALUATING/FINALIZING/REPORTING/COMPLETED/CLOSING/CLOSED`；
CLOSED 仅由 §5 batch-close 产生（closure_reason=batch_blocked，cohort_statistics 恒 INCOMPLETE），
不与 COMPLETED 合并。退出码 0/1/2 沿用 F007：batch 的 0 仅 COMPLETED 报告已发布，batch-close
的 0 仅 CLOSED 报告已发布；COMPLETED/CLOSED 与 evidence PASS 分列。
新错误码：`E_BATCH_INPUT_INVALID/E_BATCH_EMPTY/E_BATCH_BINDING_CONFLICT/E_BATCH_BUSY`；
上游数据摘要、方法论、统计、发布错误保留 F007 原码。

### 4.2 信号与 expression（缺口②）

生成数据通过 F003 lake_tensor/F002 reader 读取绑定版本，加载 FactorDef 必须走
factor_store.load 和已登记编译器，不直接反序列化执行 Python。核验 feature_map、scope、
definition_digest、数据通道、运行归属。窗口/通道/输入摘要先冻结，计算在 cohort 冻结后。

CSV 是 UTF-8 无 BOM、LF、固定表头 `time,symbol,close,signal,forward_return`，按
`(symbol,time)` 排序、键唯一；UTC 时间固定微秒精度并带 `+00:00`，float64 使用 `.17g`，
-0 规范为 0。symbol 为绑定 symbol-map 的 lake_pair。
`close` 取预注册 close_column；`signal=FactorDef.compute(panel)` 原始值，不做截面中心化、
排名、归一化或复用 prefilter 值。F012 的 cs_median 是生成预筛规则；F007 现有成本规则
仍从原信号取 sign，这一差异在 provenance 中明确展示，不暗改正式评测规则。

bar 时间统一为可用时刻：沿用 F003 1h 重采样的左闭右标签 `[t−1h,t)`，
源 1m timestamp 仍为开盘时间，不先平移再重采样；小时标签 t 是该小时收盘可用时刻。
不完整小时不作为有效观测，PIT/截止检查在小时可用时刻做；1m 直接输出的时间处理后移。

对 pair 的可交易日历计算 `forward_return(t)=close(t+H*Δ)/close(t)-1`；必须存在连续 H 个
可交易且有观测的 bar，t 与 endpoint 同属一个预注册 train 或 validation 区间及 `[S,E)`，
且 endpoint≤cutoff。训练行只供稳定性训练统计，正式 OOS 统计/曲线只取 validation 行；
角色与可能重用的训练行索引在 sidecar 按折保存，不复制 CSV 键或让训练行混入 OOS。
缺口/退市/尾部缺端点/跨折不能压缩后 shift、补零、跨 pair 或 forward-fill。
warmup 根据 token 嵌套求值所需历史长度递归求和/最大值推导，读取范围与推导长度入 sidecar；
不得把 warmup 计入评测。只能使用绑定内、S 前的历史，不读取 E 后数据来补端点。

剔除原因按「宇宙外 → warmup → 缺 close → 缺标签 → 因子非有限/退化」互斥计数。
共享湖的 Inf/非法索引/非正 close 属输入完整性错误，暂停批次；单候选输出全 NaN、Inf、
空或退化信号为确定性 INCOMPLETE，一次终结。attempt writer 在 `load_unified_panel`
前识别并写 reason/missing-artifacts，不能把空 CSV 的 E_INPUT_INVALID 冒泡成整批失败。
所有输出数值由 producer 显式做 isfinite 校验；不能依赖 CSV reader 的 float()。

**日历 mask 与 F007 消费端增量（T007/T008）**：CSV 五列保持不变；sidecar 保存完整
`(symbol,bar_time)` 1h 网格、PIT membership/observed/label_valid/finite mask、label_endpoint、
fold 的 train/validation 索引和连续 segment_id，含 CSV/映射/网格摘要。CSV 仅写有效行，
缺失网格不能补零。FROZEN 后整批湖面板只建一次，按最大 warmup 读取，因子计算共用只读面板。
batch 专用 panel loader 核验每个 CSV 键、mask 与摘要，再把结构化 panel_context 传至
execute_canonical/attempt → pipeline → 成本、稳定性、required_statistics、curves；
不能只保存在 sidecar 而继续调用旧裸数组路径。缺 sidecar、错行/错时刻直接失败关闭。
持仓/换手/持有时长仅在同 pair、同折的连续有效 segment 内相邻；断点结束持仓并按既有
成本模型计平仓，新段从空仓起算，缺失期不造收益。bootstrap block 不跨缺口/折，HAC
lag 以小时网格计，样本/块不足记 INCOMPLETE，不能压缩成相邻观测。聚合曲线保留时间键
与覆盖 mask，用于 §5 相关性核验。

稳定性显式消费上述 train/validation 索引、H、n_folds、embargo_bars；按标签端点 purge
训练行、按真实小时网格执行 embargo，禁止重新用旧 size 切 3 折或默认 horizon=embargo=1。
扩展 canonical 内核的 panel_context/GuardContext 参数，填实际 signal_times、label_endpoints、
fold_bounds、train/fit_indices、算子注册与跨 pair 能力事实；批量缺上下文不得记 PASS。
测试须证明改 H/折/embargo 会改变实际切分，越界端点和空 context 会拒绝。
旧无 pin 单候选继续旧调用方式；信号源为 real，L2/L3 原始状态保持 `not_yet_available`。

后缀序列化由校验过的 token AST 生成函数调用字符串（不用 eval），规则如下：

| token | 栈/输出规则 |
|---|---|
| `feature:X` / `constant:C` | 压入 `feature(<JSON双引号完整X>)` / 规范化有限数值（缺值/非有限值即拒绝） |
| `neg/abs/log/cs_rank` | 弹一项输出 `op(x)`；scope/窗口规则沿用 operator_registry |
| 二元 `add/sub/mul/div/greater/less` | 先弹 rhs 再 lhs，输出 `op(lhs,rhs)`；greater/less 是 vendor max/min，不改成比较符 |
| 单窗口 `op:N`（如 mean/ref/return/std） | 弹一项输出 `op(x,N)`；必须有合法正整数窗口 |
| 成对窗口 `corr:N/cov:N` | 弹 rhs/lhs，输出 `op(lhs,rhs,N)`；结束栈必须仅一项 |

例：`[feature:ohlcv_1m.close@1h,mean:10,neg]` →
`neg(mean(feature("ohlcv_1m.close@1h"),10))`。
原 token、rendered string、format version 和各摘要一并入 sidecar；预检复用 F003 purity，
正式调用仍跑 F007 L1，但它只是子串/正则扫描，不是完备 AST 验证器；负 ref/shift、未知
op、未来通道的保证来自 F003 purity + 已登记编译器 + renderer 白名单，不能归功于 L1。
cs_rank/corr/cov 的 cross_sectional 约束、delta 窗口白名单及所有 arity 均沿用 F003，
serializer 不另造更宽松语法。

### 4.3 生成事件适配（缺口③）

真实 GenerationEvent 为 `{schema_version:1,event_seq,ts,run_id,event_type,payload}`。
源序号从 1 连续递增，最后必须是唯一 `generation.run_completed`；不去重后继续，不拼接其他 run。
完成事件 payload **没有 status**：适配后的 status 从已核验 run.json 的 completed 补入。

| 源 | F007 摄入字段 / 规则 |
|---|---|
| event_type | type，原样保留全名 `generation.run_completed` / `generation.candidate_rejected` |
| run_id、payload.run_id（完成事件） | 必须与目录 run.json 一致 |
| payload.generator / payload.counts | 与 run.json 相同；扁平 counts={proposed,registered,rejected_total}，不将嵌套 dict 强转 int |
| unregistered_op / reachability | unregistered_operator / insufficient_reachability |
| lookahead / duplicate_definition | 同名保留 |

拒绝 expression 用 canonical JSON token 数组文本传给 F007 的字符串字段（诊断用途，不是
canonical 的 expression）；恶意/畸形拒绝 token 不应经过可执行表达式 renderer。
保留 `source_event_seq/source_reason_code/detail/definition_digest`（源缺 digest 则显式 null）
及源文件摘要用于溯源。reachability 的兼容桶仍映射 insufficient_reachability，但另存
原 detail 与子原因 `after_cost_return/trades_90d/degenerate_signal/unknown`；unknown 保留原文，
不得把所有子原因解释为市场不可达。报告展示原桶及子原因，子项和等于 reachability 总数。
`counts.rejected` 四类逐项核验事件数量，`registered` 等于全部可加载 factors 数；
`proposed=registered+rejected_total`。适配产物按 adapter_version 和 source_digest 固定，
只传给 `ingest_generation_events`/synthesis，不修改 run_dir。

### 4.4 批次与尝试事件

`batch.prepared/frozen/member_started/member_finished/abandoned/finalized/completed/closing/closed`
固定枚举；closing/closed 仅由 §5 batch-close 写出，与 §4.1 状态 CLOSING/CLOSED 一一对应。
公共字段：schema=1、batch/cohort/candidate/experiment ID、attempt_no、输入摘要、phase、
reason_code、evidence_refs、timestamp；墙钟只作 provenance。不能让这些事件直接模拟
`evaluation.registered`；终态登记仍由 F007 population 写入。

## 5. Runtime、Workflow 与并发

### 冻结与权限

本地 POSIX advisory 锁按 `source run_id → cohort_id → experiment_id` 固定顺序取得，
持锁范围覆盖写副作用；进程死亡由内核释放，不按超时偷锁。仍保留 F007 experiment claim；
任何绕过 runner 的 canonical/finalize/abandon 写入口，遇 batch_binding 都必须校验匹配批次
上下文并取得同一 cohort 锁；只凭知道 batch_id 不授予 Agent capability。
生产入口保留 clean-worktree/code digest 门禁，不提供绕过开关。
PREPARED 的任何发布之前，强制显式设置工作树外的 `ALPHAMILL_REPORTS_DIR`；realpath
不得位于当前工作树内（包括 symlink 回指），未设置或默认仓内 reports 以
E_BATCH_INPUT_INVALID 拒绝。所有 batch/snapshot/cohort/bench/registry/锁均解析到该根，
逻辑 `reports/...` 引用仍兼容；不补 ignore、不把脏工作树排除规则扩大。旅程覆盖默认根
零写入拒绝，以及外置根在快照发布和多成员执行后 `git status --porcelain` 仍为空。

冻结前只验证文件、元数据、表达式结构和输入范围；所有可能产生评测结果的求值在 FROZEN 后。
复用 cohort.json 时读回已有原文（含 frozen_at/by），不重新生成墙钟再调用逐字节 freeze。

### 批量尝试协议（新增，不冒充已有能力）

新增内部 `run_canonical_attempt(batch_context, attempt_no)`，共享 canonical 的校验/评测内核，
写批次 attempts 下的 canonical 级证据，**不写 population 或最终 bench 路径**。
旧 `run_canonical` 在无 batch binding 时保持旧行为；批量路径不用 require_clean_worktree=False。

每次算前以 exclusive create 持久化 started.json，持久计数 1/2/3；重启不重新发配额。
若 started 后中断且没有完整 attempt result，该次记 `INCOMPLETE/interrupted`，消耗一次尝试；
发布完成的 attempt 只核验后复用，不重复求值。临时目录不算完成；不能删除历史尝试重置预算。
尝试前共享数据/配置摘要冲突属于批次阻断，先于分配 attempt，不消耗候选预算。

首个 EVIDENCE_READY、REJECTED 或确定性 INCOMPLETE 立即选为终态。
`evidence_complete=False`、统计退化/样本不足、信号不可计算均不重算（bootstrap seed 固定
意味着同输入重试无意义）。仅未产出完整结果的瞬态 attempt 异常/中断/读取 IO 可重试，
记录 `retryable=true` 与错误分类；未知异常暂停批次，不能盲目重试。共享完整性错误、
磁盘满、正式发布失败不属于候选重算，修复后恢复对应副作用。
最多两次额外尝试，总数由 max_retries+1 导出；不改 seed/输入/方法，第 3 次仍无结果以
`batch_retry_exhausted` abandon。SIGINT/SIGTERM 停在检查点退出 1，后续候选不启动。

终态发布由 F007 统一 publisher 把选定 attempt 证据及 selected_attempt 引用发布到既有
`bench/<object>/<snapshot>/<experiment>/`，再 register_member；发布前不存在官方登记。
耗尽时同样发布 INCOMPLETE manifest 和可用证据，再调用扩展 abandon；无曲线时使用显式
缺证据状态，不造零曲线，finalize 仍按缺证据失败关闭。abandon 的重入先核对已有登记，
相同内容直接返回，不追加相互冲突的终态事件。
新 attempt 证据没有 official registration.json；旧 publisher 默认必备文件集不降级，
仅专用 attempt writer 支持未登记形态。新 canonical 最终 INCOMPLETE 容器允许显式
missing-artifacts 清单，此类容器仅用于弃置登记，不能通过 EVIDENCE_READY 完整性检查。

### 阻断批次的受限收尾（T010/T014，新增能力）

正常续跑 source/config/code/pin 不一致仍报 E_BATCH_BINDING_CONFLICT。另提供显式操作员
命令 `alphamill-evaluation batch-close --batch-id ID --reason batch_blocked`：只许关闭已冻结
且无 verdict 的批次，不接受新 snapshot/config/seed，也不提供 rebind。拥有 canonical writer
能力、持同一 source/cohort/experiment 锁并保持当前工作树干净；Agent 无权调用。
该命令可在代码 digest 改变后执行，但只能读取冻结 manifest/pin/成员/既有证据，禁止生成
信号、重算或提升 verdict。核验冻结材料及其摘要，closure.json 同时记录原 code digest 与
当前收尾执行 code digest；不是把新代码冒充原评测代码。冻结账本损坏时仍拒绝，先恢复
原字节证据，不允许捏造承诺。
已正式登记者保持原状；已发布未登记者核验后补原终态；其余所有未终态成员（包括 PENDING、
无 started、无 canonical manifest）均由专用 closure publisher 建无评测证据的 INCOMPLETE
容器，以 `batch_blocked` abandon 一次。experiment_id 从冻结上下文推导并核对；
selected_attempt=null、missing-artifacts 显式列出，不虚构尝试次数或曲线。
因此需扩展旧 abandon「先有 INCOMPLETE manifest」前提，普通单候选路径仍保持原校验。
全员登记后走下述 finalize 事务，closure 强制 cohort_statistics=INCOMPLETE，保留已登记的
负结论，禁止产生新可晋级结论；分母不变。命令中断可幂等恢复，已有相同 closure 直接续写。
状态路径 `FROZEN|EVALUATING|FINALIZING → CLOSING → CLOSED`（内部复用 finalize 事务与报告发布）；
已 COMPLETED 或已有 verdict 的批次拒绝 batch-close。CLOSED 之后普通 batch 续跑只读返回，不再评测。
已发布 verdict 但尚未 COMPLETED（回写/synthesis 未完）时若代码 digest 改变，唯一恢复路径是检出
冻结时代码续跑：verdict 已冻结，剩余回写/报告须由同一代码生成，batch-close 覆盖 verdict 或新代码
接手都会混入不同代码摘要，故均拒绝。为此 manifest 另记冻结时 `code_git_commit`（仅 provenance，
不进 batch_id），E_BATCH_BINDING_CONFLICT 的错误输出须给出该 commit 与恢复指引。

### finalize 与发布恢复

候选发布但未登记：利用 selected_attempt 补唯一登记，不重新计算。
cohort 缺一个登记：不执行统计，不写部分 verdict；共享基础设施错误使批次暂停。
**这是 F007 finalize 的事务重构，不是现有 API 的幂等保证**；当前每次都会重读 registry
重算，再分两步写 verdict/writeback。批量 pin 路径按如下持久化顺序执行：

1. 先查已发布 verdict；存在则核验 cohort、完整登记集合、binding、finalize_inputs 摘要及
   引用证据，直接复用原结论/原 finalized_at，不触发 dedup/统计或读取当前 registry 作裁决。
2. 无 verdict 时，在 cohort 锁内并取得 reports 根级 registry 锁，原子冻结 finalize_inputs：
   当前 cohort 的登记/报告/曲线摘要、方法、承诺顺序，以及排除本 cohort 的 registry 行
   快照、所引曲线的内容寻址副本/摘要（不能仅存指向可变文件的 hash）。释放 registry 锁。
   已有 finalize_inputs 则直接复用，首次计算前也不得因别的 cohort 回写而换输入。
3. 基于冻结输入计算相关性/统计/裁决，原子发布含 finalize_inputs_digest 的 verdict。
   发布中断按临时文件/最终文件事实恢复，不发布部分 verdict；缺证据与 batch_blocked
   收尾必须 INCOMPLETE。FINALIZED 不等于 cohort_statistics PASS。
4. 从冻结 verdict/成员证据及原 finalized_at 构造 summaries，再取 registry 锁补回写。
   `(cohort_id,factor_id)` 已有同内容则幂等；同 key 不同内容报完整性冲突，不能静默跳过。
   在同目录写完整新评测面、fsync、atomic replace 并 fsync 目录，保留其他 cohort 全部行；
   reader 只能见完整旧/新文件。旧格式不变，旧入口写此文件也必须用同锁和原子 writer。
   历史已有坏半行失败关闭，不以截断猜修；新协议须注入写中断证明不生成坏半行。
5. 全部 summaries 可核对后发 synthesis；崩溃在任一边界均只补缺步骤。

锁序在原 source→cohort→experiment 后增加 registry 锁；任何入口不能反向持锁。
首次输入冻结与回写各自持短 registry 锁，统计期间不阻塞其他 cohort。
synthesis 发布后补 completed 事件；若仅 journal 丢最后一条，可从报告/登记/manifest 重建。

### cohort 统计完整性口径（沿用 F007 失败关闭，不改门禁）

代码基线 `canonical_ops.finalize_cohort`：遍历全部登记成员，任一成员曲线或报告不可读即
cohort_statistics=INCOMPLETE；`cohort_statistics` 要求「有报告且非 rejected」成员集合与 p 值集合
完全相等，否则 INCOMPLETE；统计非 PASS 时 `EVIDENCE_ADEQUATE_VERDICTS`（promising/provisional/
blocked_pending_audit）一律降为 incomplete，dead/rejected/underpowered/incomplete 保持。批量路径
在冻结输入上执行同一口径，比较集合固定如下：

| 集合 | 定义 | 不满足时 |
|---|---|---|
| 登记集合 | 全部登记成员 = 承诺集合 = trial_count（含确定性 INCOMPLETE、batch_retry_exhausted、batch_blocked） | 未收齐不 finalize |
| 证据集合 | 登记集合中曲线与报告均可读者；必须等于登记集合 | cohort_statistics=INCOMPLETE |
| 多重检验集合 | 有报告且 verdict≠rejected 者；其 p 值集合必须与之完全相等 | cohort_statistics=INCOMPLETE |
| 相关性集合 | 有曲线且 verdict≠rejected 者 + 冻结 registry 行；下述必需配对全部可比 | dedup/cohort_statistics=INCOMPLETE |

后果：N=50 中只要 1 个成员确定性 INCOMPLETE（无曲线）、重试耗尽或受限收尾，整批即无可晋级
结论；这是 ADR-0003 下有意保留的失败关闭，不剔除该成员对剩余子集另做 BH/DSR，也不因此降级
门禁。报告与 CLI 首屏须输出 `cohort_incomplete_causes=[{candidate_id,cause,evidence_ref}]`
（cause ∈ missing_evidence/missing_p_value/comparison_unavailable/batch_blocked/retry_exhausted），
让运营者看见整批被哪几个成员拉下；成员层 verdict 与 cohort 层状态分列展示。

### 相关性与有效独立数输入（T013）

批量路径不得沿用按下标配对或异常后静默跳过。curves 的规范 UTC 时间键、horizon、
OOS 角色和有效覆盖 mask 必须进入比较；同 cohort 各成员要求完全相同的有效 OOS 时间键，
外部 registry 的比较序列也要求同时间键/同 horizon。等长错时、长度不同、缺时间键、
缺证据或常量/非有限序列均记显式 comparison_unavailable，dedup/cohort_statistics
为 INCOMPLETE，effective_trials=null+reason；不缩成共同交集、不回退 none 或 1.0。
这是 v1 保守策略：历史 registry 不可比可能使批次不完整，必须如实报告，不能换空根逃门禁。
比较键集合：同 cohort 以冻结的 OOS 网格 G（冻结 window 的 validation 区间 ∩ 共享面板观测 mask，
全员相同）为唯一键集；成员曲线在 G 的某键缺值（如该 bar 全部 pair 因因子非有限被剔除）即该成员
所有必需配对 comparison_unavailable，不补零、不取交集。该严格口径叠加上一小节会放大
「单成员致整批 INCOMPLETE」效应，T020/T021 须报告其发生频率；放宽（如平仓补值或交集配对）
需新方法版本与 owner 评审，不在 F013 v1。
当前 canonical 仅产 oos_pnl，无 rolling_ic；冻结可用指标和缺失原因，至少 oos_pnl 完整
可比才评测。不声称已用双指标；将来产出 rolling_ic 需新的方法版本。
仅真实单成员且无其他应比较成员时可记 effective_trials=1（basis=singleton）；
N>1 须核验 N(N−1)/2 对全有结果，任一必需配对缺失不能用剩余配对估计。

## 6. UI 与可观测性

不适用：无图形 UI。CLI 给计数、当前候选、尝试次数和产物路径，逐阶段记录单调时钟耗时。
synthesis schema 升 v2，新增语义字段 `source_distribution,first_loss,max_loss_stage,metric_version`。
旧 v1 保留原字段/原 hash 公式双读；不能给旧报告补默认键后重算旧 ID。

`source_distribution` 按 generator 排序，每项 `{generator,proposed,registered,generation_rejected,
canonical_trials,terminal_members,verdict_counts}`；来源取已验证完成事件和候选 meta，一致性必须
核验；v1 批量输入只有 alphagen 一项也完整输出。合成器测试包含多来源但批量 CLI 不开放混跑。
名义数为 proposed，canonical trials 为入册数，不把重复定义拒绝再算正式试验；有效独立数
只引用 finalize 的 effective_trials，新增 `effective_trials_method` 元数据进入 v2 语义 ID：
`name=ordered_mean_abs_rho_v1`、公式 `N/(1+(N−1)*rho_bar)`、N、承诺顺序摘要、
指标、有效/预期配对数、rho_bar、unavailable_reason。rho_bar 为第 2..N 个成员分别与
其在先成员的 |ρ| 均值再平均，并非所有 pair 等权均值；不是聚类估计器，也不是 DSR 本身。
在 F013 新 method_config 中明确此名称，保留旧 method-v1 不原地改写；实现须新增 metadata，
不能假称现有代码已有方法名。缺失时 null + unavailable_reason，来源 trial_count 不随之减少。

first-loss 固定顺序：`generation → methodology → signal_quality → portfolio_transform →
cost_capacity → temporal_stability → execution_implementation → cohort_correction`。
该顺序是独立 first_loss 结构的枚举，绝不写入五阶段 FailureBucket。
生成拒绝每事件一次归 generation（并展示 §4.3 子原因）；正式成员从原始
`signal_quality FAIL / mechanism=lookahead` 且 L1 拒绝事实映射到 methodology，保留
原 stage/mechanism/error_code 供核验，不能查找不存在的 methodology 阶段。其他按五阶段顺序
取首个 FAIL/UNDERPOWERED/INCOMPLETE，NOT_APPLICABLE 不算流失；全阶段无阻断但最终 dedup/
统计使其 rejected/dead/incomplete 则归 cohort_correction。L2/L3 的 `not_yet_available`
另列 audit_availability；blocked_pending_audit 仍保留原 verdict，不改写为 pending，
不能假造执行层 FAIL。证据缺失而无法归阶段的成员单列 `unattributed`，不得从分母删除。

每级 `{entered,lost,fail,underpowered,incomplete,loss_rate}`，lost 计不同候选（生成级计提案事件），
entered 从 proposed 逐级减掉前序 lost；同一候选不能因多个 failure record 重复计数。
`max_loss_stage={stage,lost,loss_rate,tied_stages,basis:"first_loss_absolute_count"}` 取绝对流失数
最大者，平局取上述顺序最早项并保留全体 tied_stages；全部零则 stage=null/reason=no_loss。
OPEN 或存在 unattributed：status=INCOMPLETE，stage=null/reason=incomplete_attribution，
可附 observed_max 但不能宣称完整最大级。first-loss 与现五阶段状态矩阵是不同明确口径。
facts 放可核计数；inferences 的最大约束引用这些 facts；recommendations 不改变门禁。

## 7. 失败、恢复、安全与兼容

| 位置 / 错误 | 行为与恢复 |
|---|---|
| 准备：partial、空批、坏绑定/事件/配置 | 非零拒绝，无 cohort；修正输入或提供新的合法完成批次 |
| 冻结后 source/pin/代码变化 | E_BATCH_BINDING_CONFLICT；恢复原环境续跑或 §5 batch-close 收尾，不 rebind |
| 已有 verdict 后代码变化 | E_BATCH_BINDING_CONFLICT 并输出冻结 `code_git_commit`；只能检出该 commit 续跑回写/报告，batch-close 拒绝 |
| 单候选空/退化信号、evidence_complete=False | 确定性 INCOMPLETE 一次终态，不调用空 CSV loader，不重试 |
| attempt 瞬态异常/中断/读取 IO | 分类留证后最多三次尝试；耗尽弃置，不剔除承诺 |
| 磁盘满/锁冲突/正式发布失败 | 非零暂停，不伪造 INCOMPLETE 统计结论；修复后从持久化事实继续 |
| finalize 统计不可计算 | 继承 F007 incomplete 裁决；若操作本身抛错则无新 verdict，续跑该阶段 |

artifact 引用只能解析到允许的 reports/lake 根，验证 symlink/路径穿越；不运行表达式文本、
不联网、不触碰数据库与交易接口。支持项目 WSL/Linux，本地锁不宣称支持多机共享 NFS。
保留既有 canonical/default publisher 行为，新增批次 binding 才启用专用协议；已登记历史
INCOMPLETE 不自动迁移为可重试，防同一成员出现两份终态。

## 8. 测试策略与验收映射

| 验收 | 层级 / 计划文件（tests 下） | 关键证据 |
|---|---|---|
| AC-001/002 | contract/test_f013_batch_binding.py | preset 前置、全字段 mismatch、源/目标日历映射反例、同 cohort 不同 snapshot、并发/崩溃冻结 |
| AC-003 | unit/test_f013_signal_producer.py | 1h 可用时刻、缺口/退市/跨折/warmup、空/退化候选隔离、mask 消费/持仓断点、非默认折/H/embargo 与空 context |
| AC-004 | unit/test_f013_expression_render.py | 全注册算子 arity/窗口、非交换算子、常数、恶意 token、重解析 AST 等价 |
| AC-005 | contract/test_f013_generation_adapter.py | F012 真实格式完成事件无 status、四原因、嵌套 counts、截断/重复/缺项 |
| AC-006 | integration/test_f013_batch_journey.py | 全路径 3–5 候选、默认 reports 根零写入拒绝、外置根不污染 git、Agent 禁止、冻结时序 |
| AC-007/008/012 | integration/test_f013_batch_recovery.py | 确定性失败仅一次/瞬态至多三次、未启动成员阻断收尾与 CLOSED、registry 并发改变、原子回写/冲突、不重裁、单成员缺曲线/耗尽/缺 p 值致整批 incomplete 与致因列表 |
| AC-008（AC-009 方法元数据） | contract/test_f013_batch_correlations.py | 等长错时/不等长/常量/缺证据均关闭、完整配对数、方法元数据与 digest 顺序 |
| AC-009/010 | unit/test_f013_batch_synthesis.py；contract/test_f013_synthesis_compatibility.py | 分母守恒、并列/零/缺证据、来源对账、v1/v2 ID 重建 |
| AC-011 | integration/test_f013_batch_capacity.py | 执行机真实小批 + N=50 fixture 性能基准 |

性能取证在执行机 CPU（device=cpu，如实记型号/内存）执行，不要求 GPU；不移动运行服务。
N=50 基准固定 seed=7、每成员 90 天×24=2160 个有效小时 OOS 观测（另备训练/warmup/折尾
标签数据，不把被剔除行计入 2160）、bootstrap 1000 resamples/block_size=5；数值沿用 method-v1：
HAC lag=5/kernel=bartlett、BH alpha=0.05、dsr_threshold=0.95；另显式 H=1、n_folds=3、
embargo_bars=1。配置采用 F013 新方法版本（新 method id，含 §4.1 batch/stability 显式字段、
`dedup.metrics=[oos_pnl]` 与 §6 effective_trials_method），不原地改 method-v1。50 成员全有非退化信号/收益、有限 p 值与完整
同时间键曲线，含独立及高相关样本；断言 bootstrap、BH、effective_trials、DSR 均真正执行，
不是缺阈值/缺 p 值提前返回。另设缺字段负例，不能计作基准成功；不要求通过率或盈利。
基准 namespace 在工作树外且独立于生产 registry，显式标 benchmark。固定两组测量：
R=0 和 R=50 的既有 registry（另一个 cohort 的确定性可比曲线，全部非 rejected）；
记录每组输入摘要、实际配对数及冷启动耗时，不声称覆盖任意生产 registry 规模。
生产规模超过 R=50 需另取证；不能以隔离空 registry 的结果代表实际查重成本。
从读湖/面板构建开始计时，整批面板只建一次、50 次 compute 单独计时，再统计 canonical/
finalize/report；不以预制 curves 跳过信号生产和成员 bootstrap。夹具可合成，但须走同一
producer/pipeline；F012 真实生成质量仅由真实小批验证，基准不冒充真实 50 候选。
输出相关计算调用数/耗时（50 成员首轮至少 1225 对，实际额外调用另报）、bootstrap 调用数/
耗时（包括逐候选 required_statistics；不假称 bootstrap 只发生在 finalize）、finalize 总耗时、
每组全程总耗时与峰值 RSS；bootstrap 位于逐候选 canonical，finalize 无 bootstrap。
dedup 和统计当前各算 1225 对，另有 50×R，分别记录调用数，不能只报首轮 1225。
计时工具不得替换统计实现；本轮预算每组 finalize ≤1800 s、全程 ≤3600 s、RSS ≤8 GiB，
两组都必须达标（总测量最长预算 7200 s）；不是收益/统计阈值。
超限阻断 AC-011，先测瓶颈，需改预算则先变更设计并复核，不自动减 bootstrap 样本。
机器迁移重测；证据文件（T002 `input-preflight.json`、T020/T021 `{journey,capacity}-evidence.json`）
一律写 `$ALPHAMILL_REPORTS_DIR/f013/`，与 §5 批次产物同一外置根口径（未设置/仓内根同样零写入拒绝），
记录 hostname、设备、commit/code digest、配置/输入摘要、各阶段时间、计数、退出码及产物引用。
仓内 `reports/f013/` 只放入库副本：在执行机最后一次 canonical（T023 结束）之后由 T024 复制并提交，
不在任何 canonical 前后穿插写入，故不与 AC-006 的 `git status --porcelain` 为空冲突；不补 ignore。
小批真实验收与基准不得标记 M2 ≥50 生产爬坡已完成；后者依赖 F005。

## 9. 已确认决策与残余风险

| 事项 | 设计决定与边界 |
|---|---|
| 一 run 一 cohort | 不按分数裁剪；计数与来源最容易审计，跨 run 留后续 |
| 后缀字符串不是新求值器 | 计算始终用已有 FactorDef 编译器，renderer 只服务方法论门与审计 |
| 原信号与预筛仓位不同 | 选择 identity 并显式记录，避免 CSV 生产者暗改因子；正式仓位改法需另评审 |
| 尝试目录与正式目录分开 | 保留不可变历史，同时仅终态一次登记；实施必须覆盖旧入口绕过和发布崩溃窗口 |
| 性能与统计估计局限 | 沿用 F007 现有 effective_trials 公式，但按 §6 新增 `ordered_mean_abs_rho_v1` 方法元数据；不能宣称已新增 PRD 的聚类估计器；保持门禁不降级 |
| F012 选择尾窗前置 | 接受 owner 方案 a；T002 合入 preset 并验证新 run；方案 b（更晚 cutoff）仅 M2 后另立增量 |
| 单成员致整批 INCOMPLETE | 保留 F007 失败关闭（§5 完整性口径）；如实报告致因成员与频率，放宽须新方法版本 + owner 评审 |

退役信号：未来 F007 原生支持受约束批次/尝试协议时，将本编排胶水合并进入统一 runner；
保持 batch/snapshot/cohort/experiment 身份与历史读取，不建立第二套门禁或持久真相表。

## 10. 待确认设计问题

无
