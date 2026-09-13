# ADR-0006：证据边界与实验身份 —— 显式执行层级、内容寻址和失败关闭

- 日期：2026-09-13
- 状态：Accepted
- 决策人：Georg
- 背景：PRD FR3 / FR7；ADR-0003；F007 评测台/门禁；ml4t 配套仓的研究工作区与方法门实践

## 背景

AlphaMill 已有四平面、留出预算和不可变 manifest，但仍有三个跨 Feature 的空隙：探索运行与
正式裁决只有逻辑约定；实验 ID 没有明确区分“决定结果的语义输入”和“仅用于追踪的运行元数据”；
方法实现出错时，缺少统一的失败语义。若这些规则分别留给 F007、F005 和后续部署 Feature
自行解释，preview 可能污染正式样本，重跑可能生成不稳定身份，缺失统计量也可能被误当成 PASS。

ml4t 配套仓提供了可借鉴的模式：显式 `preview/canonical` 执行层级、正式 population 与探索产物
隔离、方法论静态守卫，以及 label endpoint / per-symbol calendar / widest-horizon embargo 等
时间边界测试。它同时是教学与参考实现，不是可直接接入的生产研究平台；其部分统计函数依赖
外部包并会把估计失败降为 warning/空值。因此 AlphaMill 接纳边界模式，自研最小裁决协议，
不复制其仓库分层或把配套包变成门禁依赖。

## 决策

1. **保留四平面，新增两条横向 seam**：`Evidence Boundary` 横跨数据、研究、评测与部署，
   `Lifecycle Feedback` 横跨运行事实、归因、人审和下一代假设。二者是跨平面约束，不是第五、
   第六个平面；`synthesis_report` 属于证据与治理面，呈现层只负责渲染。
2. **执行层级必须显式传递**：每次评测运行的不可变上下文必须声明
   `execution_tier = preview | canonical`。`preview` 只能写隔离命名空间，不得写 official
   population、消耗留出预算、访问永久确认窗或产生可晋级结论；只有 `canonical` 可执行这些
   动作。层级不得从环境变量、当前目录或进程全局状态推断。
3. **实验身份按语义内容寻址**：`experiment_id` 由上游对象 ID、cohort、规范化方法/窗口/成本
   配置、`research_snapshot_id`、代码/构建摘要与随机种子共同导出。ResearchSnapshot 如何组合
   dataset versions/value digests 由 ADR-0007 拥有。execution tier、supersedes、
   文件路径、压缩编码、写出时间、主机和 wall-clock 不参与身份；同一语义输入应得到同一 ID。
   输入或规则变化生成新 ID，以 `supersedes` 串联，不覆盖历史产物。
4. **正式试验按 cohort 记账**：`canonical` 运行在看结果前冻结 cohort、试验定义、选择阶段、
   窗口和规则版本。每个进入评测的表达式（含拒绝者）只在其预注册 cohort 内计数一次；诊断性
   重定价、图表生成和基准报告不得暗中新增选择机会。全部承诺成员形成终态证据并统一完成
   cohort 级校正前，任何成员不得产生可晋级结论。
5. **必需门禁失败关闭**：必需输入、指标或方法无法计算时，运行进入 `INCOMPLETE` 或 `FAIL`，
   不得以 warning、`null` 或跳过继续晋级。可选诊断必须明确标为 optional，其缺失可见但不改变
   硬门结论；训练/研究到决策时的 parity 校验被跳过时视为失败。
6. **配置化不等于可移植性**：市场、频率、标签与成本参数通过版本化配置对象传递，但改变市场
   仍需重新验证数据语义、日历、成交机制、容量与正控制。不得宣称“换市场只是换配置”。

## 证据边界不变量

- 标签切分以 outcome/label endpoint 为边界，而非信号起点；不同 pair 使用各自可交易日历。
- embargo 不短于本次运行全部标签中的最大 horizon；拟合型变换只在训练折拟合。
- 数据身份使用 ADR-0007 ResearchSnapshot；其成员使用 canonical rows/value digest，Parquet 文件
  SHA-256 仅作物理完整性校验。
- Agent 可以生成候选、读取允许的报告并提出建议，但不能设置 `canonical`、写正式台账、豁免门禁
  或改变生产状态。
- `preview` 产物升级为正式证据时必须以冻结上下文重新执行 `canonical`，不能改标签直接晋级。

## 后果

- 正面：探索速度与正式证据可信度解耦；实验可跨编码和机器稳定去重；统计实现异常不会伪装成
  通过；F005、F006 与后续执行记录共享同一身份链。
- 负面/义务：需要隔离存储、canonical 单写者/幂等约束、值语义摘要和 cohort 台账；preview
  结果不能直接复用为晋级结论，会增加一次正式重跑成本。
- 实施：F007 落 ResearchSnapshot、执行上下文、实验身份、cohort/population、方法论门和
  `synthesis_report`；F002 继续拥有 dataset manifest/value digest 与 point-in-time 数据契约，
  不负责跨 dataset 组合；F006/M3 落
  deployment parity、`run_record`、持久化 kill-switch 与启动对账。

## 备选方案

- 仅用 registry 标签区分 preview/canonical：拒绝。单表标签容易被漏传或误写，无法形成写边界。
- 直接依赖 ml4t 配套包：拒绝。教学仓与外部统计包的失败语义不满足 AlphaMill 硬门要求。
- 把综合诊断或 evidence boundary 建成新平面：拒绝。它们跨越现有职责，新增平面只会复制台账
  和所有权。
