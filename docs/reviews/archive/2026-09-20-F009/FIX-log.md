
### Round 2 补记 · reason 改名（owner 指示）

- `vram_below_budget_unconfirmed` → `training_budget_unconfirmed`（`2d75894`，分支 `feat/F003-alphagen-vendor`）：旧名字面是"已用读数低于预算"，与判据方向相反（判据在可用侧），会让 `kronos_offload` 运行记录的事后归因读反；证据尚未落盘，趁早改。
- 同步改源码注释、测试函数名 `test_release_requires_freeing_the_training_budget` 与其 docstring 的契约引述。
- 变异证明：reason 改回旧名即判红；门禁 `tools/verify.py` 全绿。

## Round 4 · 2026-09-20 · F009 文档检视（report: CURRENT-doc.md, round 4 · full-scan audit）

- findings: F009-R4-001..008 + 重开的 F009-R1-008 / R1-009（10 条全部处理，无不接纳声明；R4-002 的处置方式与建议不同，见下）
- commits:
  - `docs/alphamill-architecture.md` + F009 三件套 + `tools/check_doc_consistency.py`::`bab9d80` —— R4-001（`transitional` 上 wire）/ R4-004（`E_UNLOAD_FAILED` 与逐注入点落点）/ R4-002 文档侧（两端 deadline 关系、恢复所有权）/ R1-008（status deadline 归属与探测预算）/ R1-009（`KRONOS_VRAM_PROBE_MODE` 等五个变量的完整契约）/ R4-003 F009 侧（AC-012 收敛为载体+先红态）/ R4-005（AC-010 载体补 CLI 套件）/ R4-006（编号）/ R4-007（F004 端口契约迁移纳入 T013 与范围内）/ R4-008（`related_features` 与 T002）
  - `docs/features/0.2/F010-kronos-gpu-runtime/{spec,tasks}.md` + `CLAUDE.md`::`d1feee7` —— R4-003 的 F010 侧方向澄清 + R4-008 的活跃索引
  - `src/alphamill/factor_factory/{cli,mine_config}.py` + `generators/{kronos_offload,gpu_slot}.py` + `tests/unit/test_f003_{gpu_slot,cli_contract}.py`::`732d98e`（分支 `feat/F003-alphagen-vendor`）—— R4-002 客户端实现、R4-001 客户端判定、R4-005 三条退出路径证据
  - `tools/check_doc_consistency.py`::`78a398e` —— R4-006 编号与 R4-003 边界的钉点
- regression_tests（分支上实跑 + 变异判红）：
  - `test_f003_cli_contract.py::test_mine_restores_kronos_when_stop_timed_out`（R4-002；变异：恢复条件改回 `action=="stopped"` 即红）
  - `test_f003_cli_contract.py::test_mine_restores_kronos_after_a_normal_run` / `::test_mine_restores_kronos_after_a_failing_run`（R4-005；连同既有取锁失败用例共四条，各断言"恰调用一次"）
  - `test_f003_gpu_slot.py::test_each_lifecycle_action_uses_its_own_contract_timeout`（R4-002 的 deadline 半边；变异：`client_deadline` 去掉余量即红）
  - `test_f003_gpu_slot.py::test_transitional_state_fails_closed`（R4-001；变异：删掉 transitional 分支即红）
  - `check_doc_consistency` 新增四条契约钉点 + 两条编号/边界钉点（变异：各自删回去即红）
- gate: `.venv/bin/python tools/verify.py` 在 main 与分支上均全绿

### 逐条处置

- **R4-001（过渡态无合法 wire 值）**：`state` 取值域加 `transitional`，并写明它是**每次 stop/restore 的必经窗口**而非异常分支；客户端见到一律 fail-closed，决策表加一行并同步一致性脚本的期望表。
- **R4-002（迟到 stop 无恢复 owner + 两端同 deadline）**：**与检视建议的做法不同**——建议是"轮询 `operation` 到终态，若落到 stopped 则恢复"；实际落的是**发出过 `stop` 即持有恢复责任、无条件 `restore`**。理由：`restore` 幂等，未真停机时是一次空操作；而轮询必须设界，界外的迟到完成（服务端重试、GC 卡顿）照样漏，等于把一个确定性问题换成概率问题。客户端 deadline = 服务端 deadline + 余量（缺省 5s）这半边按建议照做。
- **R4-003（F009/F010 收口成环）**：按建议把真实显存证据的所有权完全移交 F010——F009 的 AC-012 止于"载体落盘 + 先红态成立"（无 GPU 即可验收），F010 的 AC-009/T011 独占"解除 xfail 并取证"；F010 spec/tasks 的方向表述同步改正（原文一边写"F009 不阻塞本 feature"，一边把 F009 的载体写进自己的 AC）。
- **R4-004（stop 失败无契约化终态）**：补 `E_UNLOAD_FAILED`，并以"模型引用是否已丢弃"为界定死落点——丢引用前回落 `running`，丢引用后（含 `empty_cache` 抛错）保持 `stopped` 不假装回滚；返回错误前必须已清 `operation` 且落在稳定态。
- **R1-008（status 超时机制，重开）**：裁决为**服务端处理 deadline**；显存探测只拿剩余预算并受 `KRONOS_VRAM_PROBE_TIMEOUT_S` 约束，探测超时按读数不可得返回成功响应；status **不进单飞执行器**，动作进行中照样可达。归档误关闭的成因是"接口表列了变量名"被当成"机制已落地"。
- **R1-009（探测配置契约，重开）**：给出完整变量表（`KRONOS_VRAM_PROBE_MODE=auto|torch|nvidia_smi`、`KRONOS_VRAM_PROBE_TIMEOUT_S` 与三个服务端 deadline），含值域、默认、非法值启动期判红，并明确单一来源模式**不跨源回退**。
- **R4-005（三条 restore 路径证据被高估）**：恢复发生在 `cli.py` 的 finally，控制流证据改落 `test_f003_cli_contract.py`；`gpu_slot` 套件只管 deadline 与显存判定。AC-010 / T014 / T021 的载体引用同步。
- **R4-006（编号）**：spec §3 与 NFR-006 改为 SC-005/AC-012，并加一致性钉点。
- **R4-007（F004 端口契约迁移）**：迁移写进 T013（同一提交内改 F004 spec/design 文字 + `test_f004_compose_profile_contract.py` 的精确断言与变异表），并进 spec §3 范围内、design §1 影响面；不留给 F010。
- **R4-008（依赖元数据）**：`related_features` 加 F010；T002 由"登记进 BACKLOG 规划中"改为"核对 F010 已是活跃 Feature 且两边完成边界无环"；CLAUDE 活跃列表的 F010 状态改为 `doc-reviewing`。

### 待检视方裁决

- R4-002 的"无条件 restore vs 轮询 operation"是本轮唯一的做法分歧，理由见上；若检视方坚持轮询，请一并给出"轮询界外的迟到完成由谁兜"的答案。
- 本轮跨两个会话并行修复（另一会话核对后提交了 `bab9d80`），FIX-log 由本会话统一登记；R1-008/R1-009 被误关闭的教训建议写进 RETROSPECTIVE：**"接口表里出现了变量名"不等于"机制有落点"**，关闭 medium 前应要求指出执行它的那段设计或任务。
