# F007 SDT RED/GREEN 证据

本文件记录 F007 开发期间**实际发生过的** red → green 循环（`sdt_gate` 闸 1 的 `red:` 证据源）。

## 诚实声明（先读这条）

F007 **未采用严格 RED-first 流程**：多数任务里测试与源码在同一次提交中落地，因此 `sdt_gate` 闸 3
（反测试作弊）记为 `warn: 最近提交同时改测试与源码`，这是事实，不是误报。

下面 8 条是开发过程中**真实观测到的红灯**（失败先于修复发生），不是事后补写的声称。每条都写明
观测到的失败与使其转绿的改动；其中第 3、4、5、7、8 条是真实数据／真实运行路径暴露的缺陷。

## 循环清单

### R1 状态词表与门禁执法
- red: `tools/validate_spec_lifecycle.py` 报 `F003-alphagen-vendor: 非法 status: developing`，
  `tools/verify.py` 以「规格生命周期校验」失败退出非零
- green: 词表迁移到 v4.2（认 `doc-reviewing`/`developing`/`code-reviewing` 并归一化旧词）后，
  `validate_spec_lifecycle: 全部通过`、`verify.py` 全绿

### R2 任务契约断言被勾选动作打破
- red: 勾选 T012（`- [ ]` → `- [x]`）后 `check_doc_consistency` 报
  `f007_dedup_precedes_verdict: tasks T012（finalize）未承接查重实现`——门禁只在任务未勾选时匹配
- green: 新增 `find_task_line`（按任务号取行、忽略勾选状态）后该 check 通过，并加 2 条回归测试锁定

### R3 canonical 方法论拒绝未登记拒绝者
- red: `tests/integration/test_f007_controls.py` 中泄漏控制跑 canonical 时抛 `CanonicalError`，
  成员**未登记**——违反 `spec.md` §5「被拒者照常 REGISTERED 并计入漏斗分母」
- green: 新增 `evaluation/rejection.py`，拒绝路径发布 REJECTED 批 + 写 `evaluation.gate_rejected`
  + `population.register_member(promotion_verdict=rejected)`；T030 旅程断言 `rejected_count == 1`

### R4 证据引用违反逻辑路径口径
- red: `tests/contract/test_f007_artifact_schemas.py` 的 POSIX 逻辑路径断言拒绝
  `evidence_ref`（当时存的是 `/tmp/.../reports/bench/...` 绝对物理路径）——违反 `NFR-005`
- green: canonical/abandon 改存相对逻辑路径（`bench/<obj>/<snap>/<exp>/curves.parquet`），
  synthesis 按 reports 根解析（兼容历史绝对引用）

### R5 拒绝 manifest 缺三层无前视
- red: T030 旅程读拒绝成员的 manifest 时 `KeyError: 'no_lookahead'`——违反 `FR-007`
  「manifest 必须逐层记录三层无前视状态」
- green: `rejection.py` 补 `no_lookahead`（L1=FAIL 带表达式摘要证据、L2/L3=not_yet_available
  owner=F006/M3）；旅程按 manifest state 分别断言 L1 FAIL/PASS

### R6 AC 正文标识符 backtick 被当成测试路径
- red: 收口预演时 `validate_spec_lifecycle` 会把 AC 正文里 28 个标识符 backtick
  （`promotion_verdict`、`E_INPUT_INVALID`、`[0,30)` …）当 tests 路径查存在性 → 28 条假
  「路径不存在」；首版 `.py`-only 过滤器又把 F001 的 `deployment/verify.ps1` 判红
- green: 判据改为「非 URL ∧ 含 `/` ∧ 末段带扩展名」，F001/F002/F004 与 F007 同时通过，
  加 3 组回归测试

### R7 取证命令参数不被 pytest 接受
- red: T023 的文档化命令 `pytest ... --snapshot <id>` 直接以
  `unrecognized arguments: --snapshot` 失败
- green: `tests/integration/conftest.py` 注册 `pytest_addoption` 与 `f007_snapshot_id` 夹具

### R8 真实数据下控制派生缺陷
- red: 在 `qiaozhi-lt` 真实快照上首次运行 T023，`_emit` 把 `time` 列强转 `float` →
  `TypeError: float() argument must be ... not 'Timestamp'`
- green: 去掉强转、改由调用点按需转换；同时把读取窗口收紧到**预注册窗口**（不再扫全历史），
  重跑通过（1 passed in 23.76s），证据落 `reports/f007/real_env/20260918T173439Z-1368718/`

## 终态验收

- 全量质量门：`.venv/bin/python tools/verify.py` → 全部通过（生命周期 / 链接 / 任务 DAG /
  文档一致性 / 依赖 pin / 密钥扫描 / pytest / ruff）
- 真实环境取证：`reports/f007/real_env/20260918T173439Z-1368718/manifest.json`
  （hostname=qiaozhi-lt、device=cpu、绑定 snapshot 与两个成员 value_digest）
