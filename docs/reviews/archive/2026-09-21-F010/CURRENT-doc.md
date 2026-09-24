---
report_type: doc-review
feature: F010
round: 3
date: 2026-09-21
prior_report: CURRENT-doc-F010.md round 2（本地过程稿）
scope: diff-only  # 封顶轮：只审 R2 修复 diff（669b850..6e8794b）
baseline: docs/F010-kronos-gpu-runtime @ f4a1321（worktree ../alphamill-f010-docs，自 origin/main 开出）
stop_condition_met: true
readiness: PASS
severity_counts: {critical: 0, high: 0, medium: 0, low: 0}  # 仅计 open
---

# F010 文档检视 · Round 3（封顶）

## 结论

**readiness = PASS，stop_condition_met = true。** R2 的 4 条修复经 diff 核对全部成立，本轮人工 diff 未产生新发现；流转后统一门禁的任务 DAG 检查抓到 1 条 R2 修复引入的缺口（R3-001），已当轮修复并由门禁红→绿证实；17 条（R1×12 + R2×4 + R3×1）全部 fixed，Critical/High 清零，spec §8 / design §10 无开放项。

门禁：`tools/verify.py` 的文档类检查（规格生命周期、相对链接、任务 DAG、文档一致性）与 ruff 全绿；pytest 1 failed / 844 passed / 13 skipped，唯一失败 `tests/integration/test_f001_row_reconciliation.py::test_f001_backfill_completeness_passes` 在不含本次改动的工作树上同样失败，属开发机本地 TimescaleDB 数据完整度的环境项，与本次文档改动无关。CI 在 T2.5 合入 main 并推送时触发，作为最终门禁。

## Round 2 结论（留档）


**R1 的 12 条全部核对通过并翻为 fixed**；本轮 diff 复核新增 4 条（1 Medium / 3 Low），全部为 `fix-regression`，无 Critical/High。readiness 暂定 **CONCERNS**：R2-001 修复并经第 3 轮（封顶轮）复核后转 PASS。

核对方式：逐条比对 `11e0a74` / `10f3328` / `94c2d27` / `669b850` 的 diff 与 FIX-log 声明；R1-001 的修法额外在开发机用 `docker compose config` 实测 override 合并语义——`healthcheck.test` 被替换、`KRONOS_DEVICE` 被覆盖为 `cuda`、`build.args` 合并、`count: 1` 保留，修法成立。

## Round 1 结论（留档）

Round 1 readiness = FAIL：R1-001 变量开关删不掉设备预留块、R1-002 `2.14.0` 无 cu128 包、R1-003 AC-004 开发机假绿。

## 检查清单（有限，走完即止）

1. 三件套内部一致（spec ↔ design ↔ tasks 的 FR/AC/任务追踪）
2. 机制能兑现承诺（compose / Dockerfile / 代码路径逐条对照实物）
3. 默认面不变（NFR-001）是否可机器证伪
4. 门禁强度 ≥ 声称（变异/证伪路径）
5. 机器边界（CLAUDE.md、SOP §3）
6. 跨 Feature 契约（F004 / F009 / F003 / 架构 §7.1）

## 取证记录

- 开发机 `qiaozhi-gp`，Docker Compose v5.5.1：`count: ${KRONOS_GPU_COUNT:-0}` 经 `docker compose config` 渲染后 **`count` 字段消失、`devices` 块保留**；`docker compose run` 报 `could not select device driver "nvidia" with capabilities: [[gpu]]`。
- `https://download.pytorch.org/whl/cu128/torch/`：cp311 最高为 `2.11.0+cu128`；`2.14.0` 只有 `+cu130` / `+cu132`。
- `src/alphamill/kronos_service/kronos_real.py:175-179`：`device_request` 以 cuda 开头且 `is_available()` 为假时静默取 `cpu`；预检只在 `real_mode_startup()`（:211）。
- F003 分支 `src/alphamill/factor_factory/cli.py:31`：`vram_limit_gb` 缺省 `6.0`（训练预算，不是 Kronos 常驻预算）。
- F009 `tasks.md` T013：同一 compose 块改端口为 `127.0.0.1:8002:8001`，同改 `test_f004_compose_profile_contract.py` 与 `.env.example`。

## 发现

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1-001 | compose 变量插值做不到"`KRONOS_GPU_COUNT=0` 不渲染预留"；默认路径渲染出无 count 的 nvidia 预留，开发机/CI 起 `kronos-real` 即失败 | high | correctness | root-cause | original-coding | fixed | GPU 面整体移入 `deployment/docker-compose.gpu.yml` override（`-f` 叠加：设备预留 + `KRONOS_DEVICE=cuda` + healthcheck 判据 + GPU build args），默认 compose 文件字节不动；同步改 design §2/§4/§5、spec FR-002/AC-002、tasks T004 | GPU 面四项移入 `deployment/docker-compose.gpu.yml`，默认文件不改；compose 合并语义 R2 实测成立 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | mechanism-cannot-deliver-promise |
| R1-002 | 默认 pin `torch==2.14.0` 没有 cu128 wheel（cu128 止于 2.11.0）；"≥2.7 + cu128 与 F003 同源"决策按现状构建失败，design §4 的 `2.7.*+` 也不是合法 pin | high | correctness | root-cause | original-coding | fixed | 重做 spec §7/design §4 的版本决策：GPU 取 `2.14.0 + cu130`（与 CPU 同版本）并写明宿主驱动下限，或显式接受 CPU/GPU 版本分叉；T002 的核验项加"驱动版本满足所选 CUDA wheel"；F003 `mining` 注释同步 | torch 维持 2.14.0，GPU 用 cu130；写明 R580+ 驱动下限与 arch 核验；BACKLOG 登记 F003 同步项 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | unverified-external-fact |
| R1-003 | AC-004/T015 在开发机执行时，守护进程先拒绝 nvidia 设备请求，容器从未启动，T006 预检不被执行也能"通过"；且开发机按机器边界不跑集成 | high | test-coverage | root-cause | original-coding | fixed | AC-004 拆两层：① 单元层——`KRONOS_DEVICE=cuda` + mock `torch.cuda.is_available()=False` → `real_mode_startup()` 抛 `SystemExit`，变异（删预检）必须判红；② 执行机集成层——不挂设备预留但 `KRONOS_DEVICE=cuda` 起容器，断言非零退出且日志含预检失败文案（区分"守护进程拒绝"与"预检拒绝"） | AC-004 拆单元层 `test_f010_device_strict.py` + 执行机层（不挂预留 + 显式 cuda），明令守护进程拒绝不算证据 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | gate-weaker-than-claim |
| R1-004 | 声称"三处同源"，实际是 `KRONOS_DEVICE` / `KRONOS_GPU_COUNT` / `KRONOS_HEALTH_DEVICE_PREFIX` + build arg 四个独立旋钮；`GPU_COUNT=1, DEVICE=cpu, PREFIX=cpu` 会得到占着 GPU 预留的健康 CPU 实例；CPU wheel 镜像 + `DEVICE=cuda` 只能靠 `is_available()` 间接拦 | medium | correctness | root-cause | original-coding | fixed | healthcheck 判据直接读容器内 `KRONOS_DEVICE`（去掉独立前缀变量）；预检加一条"要求 cuda 而 `torch.version.cuda is None` → 失败并点名镜像是 CPU wheel"；配合 R1-001 由 override 文件一处给齐 | 取消独立 GPU_COUNT/HEALTH_PREFIX 变量，四项集中 override；加 `torch.version.cuda is None` 判据 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | single-source-claimed-not-enforced |
| R1-005 | 静默回落只在启动预检堵；F009 `restore` 的重载路径复用 `_load_predictor()`，可绕过预检回落 cpu，违背 spec §5"能回答 /health 蕴含按配置设备加载" | medium | correctness | root-cause | spec-drift | fixed | 把"要求 cuda 必须真拿到 cuda"放进启动与 restore 共用的加载入口（如 `eager_load()` 的严格分支），或在 F009 restore 契约中显式复用该校验；AC 增一条 restore 路径用例 | 严格分支进 `_load_predictor()` 调用的 `_resolve_device()`，覆盖启动、restore、惰性加载；restore 失败落 F009 `E_UNAVAILABLE` | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | cross-feature-contract-drift |
| R1-006 | T010 / design §9 把 Kronos 常驻预算（≤3GB）超标与 F003 `vram_limit_gb`（训练预算 6.0）绑定重标，二者不是同一量 | medium | correctness | root-cause | original-coding | fixed | 常驻超标只重标 §7.1 白天行；`vram_limit_gb` 仅在 AC-009 实测"卸载后可用显存 < 训练预算"时才进入重标，并改写 T010 与 design §9 对应行 | 常驻超标只重标 §7.1 白天行；`vram_limit_gb` 仅在卸载后可用 <6GB 时随夜槽行重标 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| R1-007 | 与 F009 T013 撞车：同一 compose 块（端口）、同一 `test_f004_compose_profile_contract.py`、同一 `.env.example`，F010 Phase 1 与 F009 T013 无先后边 | medium | correctness | root-cause | spec-drift | fixed | tasks §4 加边"F009 T013 合入 → F010 T004/T005"（或写明以 F009 合入后的 main 为基线）；采纳 R1-001 后 F010 基本不再改默认 compose，冲突面缩到测试文件 | tasks §4 加 F009 T013 ⇄ T005 同文件非阻塞边与基线规则；spec §7 依赖段同步 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | cross-feature-contract-drift |
| R1-008 | AC-002 写"`docker compose config` 渲染"，而 F004 契约测试是纯文本断言；未说明单元测试是否调 docker、CI 无 docker 时怎么办 | low | test-coverage | root-cause | original-coding | fixed | 明确单元层用文本断言（沿用 F004 纯函数 + 变异）；`docker compose config` 渲染比对作为执行机/有 docker 环境的补充证据 | AC-002 明确纯文本断言、不调 docker；`compose config` 作执行机补充证据 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| R1-009 | spec §0/§7 称 F003 `mining` extra "已确立"，该 extra 只存在于未合入的 `feat/F003-alphagen-vendor` | low | quality | symptom-patch | spec-drift | fixed | 改为"F003 分支上的约定（未合入 main）"，并注明以合入后版本为准 | spec §0 / design §0 标注 mining extra 在未合入分支 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| R1-010 | design §1"后端不改代码/唯一改动是日志行"与 §5、T006 在 `real_mode_startup()` 加预检矛盾 | low | quality | symptom-patch | original-coding | fixed | §1 与 §2"服务代码零改动"改为"两处小改：预检一条 + 日志一行" | design §1/§2 改为「两处小改」 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| R1-011 | NFR-001/SC-002 要求"构建产物逐字一致"不可证伪（引入 ARG 后层缓存键/镜像 digest 必变） | low | quality | root-cause | original-coding | fixed | 改为"默认参数下 Dockerfile 解析出的安装命令与落地前等价 + 默认 compose 文件/渲染结果不变" | NFR-001/SC-002 改为安装命令等价 + 本 feature 不改默认文件，注明不承诺 digest | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | unfalsifiable-claim |
| R1-012 | 8GB 笔记本卡在 WSL2 下 Windows 桌面也占显存，AC-009"卸载后整卡可用 ≥6GB"可能物理达不到，风险表未列 | low | correctness | root-cause | original-coding | fixed | spec §7 风险表加一行：T002 顺带记录空载可用显存；若 <6GB，走 §7.1 重标而非判 AC-009 失败 | spec §7 风险行 + T002 ④ 记录空载可用显存 + T011 重标分支 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| R2-001 | override 未给 GPU 构建独立 `image:`，默认与 GPU 构建共用 `<project>-kronos-signal-real` 标签，执行机上互相覆盖：GPU 构建后不带 `--build` 的默认启动会跑 CUDA wheel 镜像（反之由严格分支拦下） | medium | correctness | root-cause | fix-regression | fixed | override 增 `image: alphamill/kronos-signal-real:gpu`（默认文件不变），AC-002 断言该标签存在且不等于默认名 | override 增 `image: alphamill/kronos-signal-real:gpu`，AC-002/design §8 断言并加删除变异；开发机 compose config 实测生效 | `tools/verify.py` 文档门禁 | 2 | 3 | shared-artifact-name |
| R2-002 | T002 ③ 只核验 `sm_89`，tasks §5 却称 T002 已核验 `sm_120`；design §4 要求两者 | low | quality | symptom-patch | fix-regression | fixed | T002 ③ 改为 `get_arch_list()` 同时含 `sm_89` 与 `sm_120` | T002 ③ 改为 arch list 同时含 sm_89 与 sm_120 | `tools/verify.py` 文档门禁 | 2 | 3 | — |
| R2-003 | T015 执行机层"不叠加设备预留但显式 cuda 启动 CUDA 镜像"没给出做法；两条严格分支（CPU wheel / 无设备）各需一个触发方式 | low | test-coverage | root-cause | fix-regression | fixed | 写明：GPU 标签镜像 `docker run` 不加 `--gpus` + `-e KRONOS_DEVICE=cuda` → 无设备分支；默认 CPU 镜像 + `-e KRONOS_DEVICE=cuda` → CPU wheel 分支 | AC-004/T015/design §8 写明执行机两例（GPU 镜像不加 --gpus；CPU 镜像显式 cuda） | `tools/verify.py` 文档门禁 | 2 | 3 | — |
| R2-004 | AC-002 的 override 禁止项列 ports/volumes/restart/privileged，漏了 design §4 同样禁止的 `depends_on` | low | quality | symptom-patch | fix-regression | fixed | AC-002 与 design §8 补 `depends_on` | AC-002 与 design §8 禁止项补 depends_on | `tools/verify.py` 文档门禁 | 2 | 3 | — |
| R3-001 | R2-003 让 T015 共用 `test_f010_gpu_runtime.py` 并依赖 GPU 镜像，但 tasks §4 未接生产者前置边；流转后 `check_task_dag` 判红 | low | quality | root-cause | fix-regression | fixed | 补 `T008 -> T015` 边 | tasks §4 补 `T008 -> T015`（GPU 镜像 + 共用载体） | `tools/check_task_dag.py`（红→绿） | 3 | 3 | gate-caught-fix-regression |

## 裁决记录

（暂无）

## 下一轮

- 修复方在 `docs/reviews/FIX-log-F010.md` 按轮追加声明（证据三件套）；不直接改本文件。
- Round 2 只审修复 diff 及其相邻契约。
- 检视档按项目 `.gitignore` 为本地过程稿（`docs/reviews/*` 仅 RETROSPECTIVE 与 archive 入库），项目 SOP 优先于 skill 默认的"入库"要求。
