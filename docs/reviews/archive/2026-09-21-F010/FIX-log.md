# F010 FIX-log（修复方独占，append-only）

## Round 1 · 2026-09-21

- findings: R1-001, R1-002, R1-003, R1-004, R1-005, R1-006, R1-007, R1-008, R1-009, R1-010, R1-011, R1-012
- commits:
  - `docs/features/0.2/F010-kronos-gpu-runtime/spec.md::11e0a74`（+ `94c2d27` 措辞收窄）
  - `docs/features/0.2/F010-kronos-gpu-runtime/design.md::10f3328`（+ `94c2d27`）
  - `docs/features/0.2/F010-kronos-gpu-runtime/tasks.md::669b850`、`BACKLOG.md::669b850`
- 逐条处置：
  - R1-001 → GPU 面整体移入 `deployment/docker-compose.gpu.yml` override；spec FR-002/AC-002、design §1/§2/§4、tasks T004
  - R1-002 → torch `2.14.0` 不变、GPU 索引 `cu130`，写明驱动下限与 arch 核验；spec §7、design §4/§9、tasks T002；BACKLOG 登记 F003 同步项
  - R1-003 → AC-004 拆单元层（`tests/unit/test_f010_device_strict.py`）+ 执行机层（不挂预留 + 显式 cuda）；spec FR-004/AC-004、design §8、tasks T006/T015
  - R1-004 → 取消 `KRONOS_GPU_COUNT` / `KRONOS_HEALTH_DEVICE_PREFIX`；四项集中 override；加 `torch.version.cuda is None` 判据；design §4/§5
  - R1-005 → 严格分支进 `_load_predictor()` 调用的 `_resolve_device()`，覆盖启动、F009 restore、惰性加载；design §5/§7、tasks T006
  - R1-006 → 常驻超标只重标 §7.1 白天行，不动 `vram_limit_gb`；spec §7、design §9、tasks T010
  - R1-007 → tasks §4 加 F009 T013 ⇄ T005 同文件非阻塞边；spec §7 依赖段
  - R1-008 → AC-002 明确纯文本断言、不调 docker；`compose config` 为执行机补充证据
  - R1-009 → spec §0、design §0 标注 mining extra 在未合入分支
  - R1-010 → design §1/§2 改为"两处小改"
  - R1-011 → NFR-001/SC-002 改为"安装命令等价 + 本 feature 不改默认文件"，并注明不承诺 digest
  - R1-012 → spec §7 风险行、T002 ④、T011 重标分支
- regression_tests: 文档检视无代码回归测试；门禁载体为 `tools/verify.py` 的规格生命周期 / 相对链接 / 任务 DAG / 文档一致性检查
- gate: `DB 凭据加载后 python tools/verify.py` · 2026-09-21 22:43 · 文档类门禁（规格生命周期、相对链接、任务 DAG、文档一致性）、ruff check/format 全绿；pytest 1 failed / 844 passed / 13 skipped，唯一失败 `tests/integration/test_f001_row_reconciliation.py::test_f001_backfill_completeness_passes` 在不含本轮改动的工作树上同样失败（开发机本地 TimescaleDB 数据完整度，环境问题，与本轮文档改动无关）
- 自伤声明：首版把 NFR-001 写成"默认 compose 字节不动"，与 F009 T013 的端口改动冲突，已在 `94c2d27` 收窄为"本 feature 不改"

## Round 2 · 2026-09-21

- findings: R2-001, R2-002, R2-003, R2-004
- commits: 见 `git log --oneline 669b850..HEAD`（spec / design / tasks 各一）
- 逐条处置：
  - R2-001 → override 增 `image: alphamill/kronos-signal-real:gpu`，默认文件不设 `image`；AC-002 与 design §8 断言标签存在、删 `image` 即判红；开发机 `docker compose config` 实测合并后 `image` 生效
  - R2-002 → T002 ③ 改为 `get_arch_list()` 同时含 `sm_89` 与 `sm_120`
  - R2-003 → T015 / AC-004 / design §8 写明执行机两例：GPU 镜像不加 `--gpus`（无设备分支）、CPU 镜像显式 cuda（CPU wheel 分支）
  - R2-004 → AC-002 与 design §8 的 override 禁止项补 `depends_on`
- regression_tests: 文档检视无代码回归测试；门禁载体为 `tools/verify.py` 文档类检查
- gate: `python tools/verify.py`（已加载 DB 凭据）· 2026-09-21 22:50 · 文档类门禁与 ruff 全绿；pytest 1 failed / 844 passed / 13 skipped，唯一失败仍是 Round 1 已声明的环境项 `test_f001_backfill_completeness_passes`

## Round 3 · 2026-09-21

- findings: R3-001
- commits: `docs/features/0.2/F010-kronos-gpu-runtime/tasks.md`（本轮 DAG 边修复提交）
- 处置：tasks §4 补 `T008 -> T015`
- regression_tests: `tools/check_task_dag.py`——修复前判红（"T015 的 verify 文件已由更早任务声明，但未接线任何生产者前置"），修复后判绿
- gate: `python tools/verify.py`（已加载 DB 凭据）· 2026-09-21 22:55 · 除已声明的环境项 `test_f001_backfill_completeness_passes` 外全绿
