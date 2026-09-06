---
topics: [features, spec-driven-development, docs]
doc_kind: guide
created: 2026-09-06
updated: 2026-09-07
---

# Feature Specs Guide

本目录记录 AlphaMill 的 feature-level SDD artifacts。所有需求按「一 feature 一
文件夹」输出，feature 文件夹按 PRD 的大版本（`0.1`、`0.2`…）分层存放。

## Directory Shape

```text
docs/features/
  README.md                   本文：规则与入口
  TEMPLATE/
    spec.md                   feature 行为契约模板（状态唯一真源）
    design.md                 技术设计模板
    tasks.md                  实施 checklist 模板
  releases/
    <version>.md              版本发布与收口摘要（全部 done 后创建）
  <version>/                  例如 0.1/
    Fxxx-feature-name/
      spec.md
      design.md
      tasks.md
```

创建新 feature：从 `docs/features/TEMPLATE/` 复制三件套到对应版本目录并重命名。
命名规则：

- Feature ID 用 `F001`、`F002` 递增，**跨版本连续编号**，不按版本重新从 001 开始。
- 文件夹名 `Fxxx-kebab-case-feature-name`，放在其所属大版本目录下。
- `BACKLOG.md` 中的链接指向该 feature 的 `spec.md`。

## Feature Status Model（状态唯一真相源）

Feature 状态只保存在 `spec.md` 的 frontmatter，是机器可读的唯一真相源。允许的
状态流转（单向推进，不可回退）：

```text
draft → ready-for-development → in-progress → review → done
```

- `design.md` / `tasks.md` **不允许**再声明独立 Status。
- `spec.md` frontmatter 固定包含 `kind: feature`、`id`、`version`、`status`、
  `gate_version`、`updated`。
- `gate_version`：
  - `0`：只做结构 / 元数据 / BACKLOG 校验（显式记录的历史债务；**不允许新建 v0 Feature**）。
  - `1`：新建 Feature 强制。额外校验章节结构、验收清单、测试路径、待确认问题等。
- `BACKLOG.md` 是由该状态派生的活跃索引（只列 `status != done`），不是第二个状态真相源。

## Artifact Responsibilities

### `spec.md` —— 做什么、怎样算完成（状态唯一真源）

固定使用以下 9 个顶层章节（标题不得省略或改号）：

```text
0. 来源与意图         # PRD/architecture/system-design/ADR 指针 + 一句话意图
1. 问题、目标与非目标 # 为什么做、成功改变什么、产品层明确不做什么
2. 用户场景           # US-xxx（Priority）+ 独立测试 + Given/When/Then 验收场景
3. 范围与边界         # 范围内 / 范围外 / 边界场景
4. 需求               # FR/DR/TR/IR/UX/NFR 子标题按需出现
5. 生命周期与不变量   # 状态机、工作流、不变量；不适用时写明理由
6. 成功与验收         # SC-xxx + AC-xxx；可追踪性内联，不再单列追踪表
7. 测试、依赖与决策   # 三个固定子标题；风险和已关闭权衡放“决策”
8. 待确认问题         # 固定保留；无开放项时明确写“无”
```

- 「1. 非目标」只记录产品意图层的明确排除；「3. 范围外」记录本次交付切片的具体
  边界，两者不得复制同一段文字。
- 「5. 生命周期与不变量」和「8. 待确认问题」标题始终存在。前者不适用时写
  `不适用：<理由>`；后者无开放项时写 `无`。
- 待确认问题用 `Q-xxx`，统一 checkbox：`- [ ] Q-001: <问题>` 开放，
  `- [x] Q-001: <问题> — 决策：<结论>` 关闭；无问题时只写 `无`。
- 「7. 测试、依赖与决策」固定包含 `### 测试策略`、`### 依赖`、`### 决策与风险`
  三个子标题。schema/service/repository/component 等实现拆分属于 `design.md`。

### `design.md` —— 怎么实现

固定使用以下 11 个顶层章节：

```text
0. 输入与约束
1. 技术概要与影响面
2. 架构与模块边界
3. 数据模型与 Migration
4. 接口、Contract 与 Event
5. Runtime、Workflow 与并发
6. UI 与可观测性
7. 失败、恢复、安全与兼容
8. 测试策略与验收映射
9. 已确认决策与残余风险
10. 待确认设计问题
```

- 不适用的技术关注面保留标题并写 `不适用：<理由>`，不得通过删章节隐藏未评估面。
- 第 10 节只允许规范的 `DQ-xxx` checkbox 或单独一行 `无`；进入
  `ready-for-development` 前必须全部关闭。
- design 只描述结构、契约、状态、失败和技术取舍，不写逐步编码任务。
- **硬性约束：`design.md` 的「待确认设计问题」章节必须清空（或所有条目标注"已关闭"
  并给出结论）才能进入代码开发阶段。** 确实要等实现阶段验证的问题，写成已拍板的
  假设/决定，并把验证动作作为具体任务写进 `tasks.md`。

### `tasks.md` —— 按什么顺序做

固定使用以下 6 个顶层章节：

```text
0. 来源与执行规则
1. 前置条件
2. 实现任务
   ### Phase 1：<按 Feature 定义>
   ### Phase 2：<按 Feature 定义>
3. 验证与验收任务
4. 依赖与并行关系
5. 明确后移
```

- Phase 数量和名称可以变化，但只能作为第 2 节的三级标题，不能各自成为顶层章节。
- 任务统一为
  `- [ ] T001 [P] (FR-001, AC-001): <一个可验证动作> — verify: <测试/命令>`；
  `[P]` 只用于修改不同文件且没有顺序依赖的任务。
- 第 3 节必须包含 AC 对应的自动化测试、所需真实环境验证与最终质量门；第 5 节
  只能放明确移交给其它 Feature/版本的内容，必须写目标 Feature/版本。
- tasks 不重复声明状态，也不重新解释需求或技术设计；只链接 `spec.md` / `design.md`。

## Writing Rules

- 每个 feature 应有一个清晰 intent，能用一句话说清。
- `spec.md` 中的每个 requirement 应描述一个可观察行为；每个重要 requirement 至少有
  一个 scenario；重要的错误、边界和恢复场景要写成 scenario 或 acceptance check。
- 如果实现过程中发现 spec 与现实不一致，先更新 artifact，再继续实现。
- 高风险 feature 写 full spec；低风险 feature 可以保留 lite spec，但必须至少有 scope、
  requirements、acceptance checklist。

## Review Checklist

**验收清单硬性规则（对应 `spec.md` 第 6 节）：**

- 验收清单每项必须有唯一 `AC-xxx`，并引用至少一个在第 4 节中真实定义的需求 ID
  （允许类型 `FR/DR/TR/IR/UX/NFR`，不强制引用 FR）。
- 进入 `review` 前必须回填仓库内真实存在的测试文件；标记 `done` 前还必须勾选。
- 唯一格式：

  ```markdown
  - [ ] **AC-001** (`FR-001`, `NFR-002`): 可观察行为 — tests: `server/tests/integration/example.test.ts`
  ```

- `draft`、`ready-for-development`、`in-progress` 阶段允许 `tests:` 暂缺；此时 AC
  仍须有合法 ID、需求引用和可观察行为。

在实现前检查：

- [ ] 这个 feature 是否只有一个主要 intent？
- [ ] `spec.md` 是否使用了 9 节固定结构，顶层标题未省略或改号？
- [ ] `spec.md` 是否定义了可测试的完成标准，且每条 AC 有唯一 `AC-xxx` 并引用第 4 节真实需求 ID？
- [ ] `spec.md` 第 8 节与 `design.md` 第 10 节是否用 `Q-xxx` / `DQ-xxx` checkbox 或单独 `无`？
- [ ] `design.md` 是否覆盖数据、API、UI、runtime、failure handling 中相关的部分？不适用章节是否写了 `不适用：<理由>`？
- [ ] `design.md` 的「待确认设计问题」章节是否已清空？**未清空不得开始编码。**
- [ ] `tasks.md` 是否使用 6 节固定结构，Phase 只出现在第 2 节？
- [ ] `tasks.md` 是否能按顺序执行，并能追踪回 spec？
- [ ] `BACKLOG.md` 是否链接到该 feature 的 `spec.md`，且状态与 spec frontmatter 一致？

## Version Closure Rules（版本收口规则）

某大版本（如 0.1）全部 feature 状态为 `done` 后，执行逻辑收口，**不移动版本目录**：

1. 新建 `docs/features/releases/<version>.md`，汇总该版本交付的 feature 列表、每个
   feature 的 FR 摘要、已知限制与遗留项（数据来源：版本目录内各 `spec.md` + PRD）。
2. 保留版本原路径，在版本目录内增加 `README.md` 注明已收口；不破坏稳定路径。
3. 在 `docs/README.md` 的 releases 索引增加 `<version> → 收口于 <日期>`；BACKLOG
   删除该版本全部 done Feature。
4. 收口动作必须跑一遍 verify，确认该版本所有 Feature 确实 `done`，再写入 release 的
   `closed_at` 元数据。收口后版本目录只允许修复历史错误或死链。

## Relationship To Other Docs

- `docs/alphamill-prd.md`：产品真相源。Feature spec 必须服从 PRD。
- `docs/alphamill-architecture.md`：全局架构设计。Feature design 不应绕过其中的
  runtime / storage / safety 边界。design 与架构边界的关系，稳定后应回写到这里。
- `BACKLOG.md`：active feature 索引，只记录状态和入口链接。
