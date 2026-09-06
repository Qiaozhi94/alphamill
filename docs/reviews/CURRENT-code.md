---
report_type: code-review
round: 2
date: 2026-09-07
prior_report: 本文件 Round 1（同文件覆盖写）
scope: diff-only（pyproject/ci.yml/verify.py diff + 5 个新文件全文）
stop_condition_met: true
severity_counts: {critical: 0, high: 0, medium: 0, low: 0}
baseline: main @ 1bd8c4d（工作树含修复轮全部改动，未提交）
reviewer: Sisyphus（review-convergence 协议，Round 2 显式切换检视人视角）
evidence: git diff 逐项核对 + 新测试文件全文审读（确认非自模拟：真读 tmp 树、真跑 verify_repo、断言真实错误文案）+ 实测 pytest 25 passed + verify.py 六步全绿 ×2 轮
note: 与 CURRENT-doc.md 并行，停止条件各自判断；CI 因无 remote 客观不可执行，本地门禁全绿
issues_index:
  - {id: C001, status: fixed（轮 1）}
  - {id: C002, status: fixed（轮 1，含变异验证）}
  - {id: C003, status: fixed（轮 1）}
  - {id: C004, status: fixed（轮 1）}
---

# AlphaMill 代码区检视报告（第 2 轮 · diff-only 复核）

## 1. 总评

**round-2 PASS：4 条 issue 全部核实修复，无 fix-regression。** 门禁链从 4 步扩到 6 步（新增文档链接检查、依赖 pin 检查），且两道新门都做了变异验证（注入死链→红、越界 pin→测试红）；C002 的 9 个回归测试全部走 `verify_repo(tmp_path)` 端到端实测校验器真实行为，非自模拟。`tools/validate_spec_lifecycle.py` 经变异验证后字节级还原（`git diff` 为空）。

## 2. Round 2 核对证据

| 检查 | 结果 |
|---|---|
| C001 | pyproject `pytest>=8,<10` + 注释如实改写（记录 9.0.3 实跑与放宽原因）；pytest-cov 同步移除（C004）；新增 check_dep_pins.py（tomllib+手写比较器，零新依赖）接入 verify 第 3 步 |
| C002 | tests/unit/test_validate_spec_lifecycle.py：9 测试 = frontmatter 解析/缺失 status 拒绝/gate-0 正例控制/AC 路径存在·不存在·`..` 逃逸/BACKLOG 缺行·status 不一致·幽灵行；变异验证：反转 validate_spec_lifecycle.py:243 `is_relative_to` → 2 测试变红 → 还原字节一致 → 全绿 |
| C003 | ci.yml 收敛为单 verify job（matrix 3.11+3.13）只调 `python tools/verify.py`；permissions(contents:read)/concurrency 保留；无复制步骤清单 |
| 新门 D011 | check_doc_links.py 接入 verify 第 2 步（排除 conversations/、docs/research/、.sisyphus/；跳过 http/mailto/锚点；忽略代码围栏）；变异验证通过 |
| 测试质量 | test_validate_spec_lifecycle.py 每个 reject 测试断言真实校验器错误文案（如"路径不合法（禁止绝对路径/.. 逃逸）"），非自模拟；test_check_dep_pins.py 注入 installed_version 为依赖注入而非 mock 校验对象本身 |
| 门禁实跑 | `python tools/verify.py` 六步全绿两轮；`python -m pytest tests/unit -q` 25 passed（1 旧冒烟 + 24 新） |

## 3. Issue 总表

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C001 | pytest pin 与本地实装矛盾（注释声称与本地验证版本一致，实际跑在 9.0.3） | 中 | 正确性 | 流程缺陷 | 原始编码 | fixed | pin 改 `>=8,<10` 并本地重验；增 pin 一致性检查 | pin 放宽 `<10` + 诚实注释；新增 tools/check_dep_pins.py 接入 verify 第 3 步（已装版本必须在声明范围内，否则非零退出） | tests/unit/test_check_dep_pins.py::9 tests（含越界→失败用例） | 1 | 1 | claim-vs-reality-pin-drift |
| C002 | validate_spec_lifecycle.py（全仓最复杂代码）零自身测试 | 中 | 测试覆盖 | 流程缺陷 | 原始编码 | fixed | 补最小单测三例+变异验证 | 9 个端到端测试（verify_repo(tmp) 实测）；变异验证：反转路径逃逸判定→2 测试红→还原；validator 本体零改动（diff 为空） | tests/unit/test_validate_spec_lifecycle.py::9 tests | 1 | 1 | gate-without-tests |
| C003 | CI 复制 verify.py 步骤清单，双份维护 | 低 | 质量 | 症状 | 原始编码 | fixed | CI 改为调用 verify.py | ci.yml 单 verify job（3.11+3.13）调 `python tools/verify.py`，注释指向其为步骤清单唯一真源 | — | 1 | 1 | — |
| C004 | pytest-cov 装而未用 | 低 | 质量 | 症状 | 原始编码 | fixed | 移除依赖（设计阶段） | 从 dev 依赖组移除；另有配套 `pythonpath=["."]` 进 pytest 配置（修复 tests 无法 import tools 的根因） | — | 1 | 1 | — |

## 4. 裁决记录

（本轮无修复方不接纳声明，无裁决。）

## 5. 停止条件状态

**本地停止条件全部满足**：Medium/High 清零；pytest 25 passed、ruff 全绿、verify.py 六步全绿（两轮）。CI 最终门禁因无 git remote 客观不可执行（与 CURRENT-doc.md 同一情形），配置 remote 后首推补验。闭环收尾待提交粒度裁决后执行。
