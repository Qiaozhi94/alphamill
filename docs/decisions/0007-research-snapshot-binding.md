# ADR-0007：研究快照绑定 —— 独立 DatasetVersion 的不可变组合

- 日期：2026-09-13
- 状态：Accepted（2026-09-18 修订：universe/calendar 拆为两个独立 artifact 引用并冻结 `universe_calendar_digest` 组合公式，见文末「修订记录」）
- 决策人：Georg
- 背景：PRD FR1/FR7；F002 dataset 独立版本；F007 多数据集评测与实验身份；ADR-0006

## 背景

F002 已决定 `data_version` 按 dataset 独立递增，因为 OHLCV、funding、basis、OI 与 signals
具有不同采集节奏和失败域。这个决定对数据桥是正确的，但不能直接充当多数据集实验身份：
若 F007 在运行时分别解析各 dataset 的 “latest valid”，相同命令在不同时间会绑定到不同版本，
还可能把不同 source snapshot、不同覆盖范围的数据临时拼成一个不可复现的输入。

用各 manifest 的 `exported_at` 临时聚合也不足以解决问题。`exported_at` 是写出 provenance，
不是跨 dataset 的一致性边界；它既不固定 point-in-time universe/symbol map，也不证明各成员满足
同一个信息截止时刻和评测窗口。另一方面，把所有 dataset 强绑成一个全湖版本会让单个低频
dataset 的延迟或失败阻塞全湖发布，反转 F002 已确立的独立失败域。

因此需要一个位于 DatasetVersion 与 ExperimentContext 之间的引用对象：它不复制 Parquet，
只冻结一次研究实际使用的成员版本、值摘要和时间/映射语义。

## 决策

1. **DatasetVersion 继续独立演进**：F002 仍以 `(dataset, data_version)` 唯一标识单 dataset
   的不可变快照；不新增全湖全局 `data_version`，也不让一个 dataset 的失败作废其他版本。
2. **新增不可变 `ResearchSnapshot`**：它是对多个有效 DatasetVersion 的内容寻址引用集合，
   由 `experiment_store` 负责构造和持久化，F002 只提供 manifest/digest reader。最小契约为：

   ```text
   ResearchSnapshot = {
     schema_version,
     snapshot_id,
     cutoff_time,
     members: {
       <dataset>: {data_version, value_digest, as_of_fidelity,
                   event_time_min, event_time_max}
     },
     symbol_map_digest,
     universe_digest,
     calendar_digest,
     universe_calendar_digest,
     provenance: {created_at, artifact_path, member_manifest_paths,
                  symbol_map_path, universe_path, calendar_path}
   }
   ```

   `universe_calendar_digest` 由两个独立 artifact 的 digest 按冻结的组合公式导出：
   `sha256(canonical_json({"universe": <universe_digest>, "calendar": <calendar_digest>}))`。
   universe digest 是 F008 内容寻址宇宙台账（`lake/_metadata/universes/<digest>.csv`）的 digest；
   calendar digest 是规范化 calendar JSON 的内容摘要。组合公式是 F007 DR-006 与 F003 过渡
   元组绑定的同一冻结式，不得回退为「单一 JSON 文件摘要」。`snapshot_id` 仍只哈希
   `universe_calendar_digest`（它已确定性地决定 digest 对），不重复哈希两个成员 digest。

   `members` 只包含本次研究声明的必需数据集，不要求每个快照固定包含湖内全部 dataset。
3. **身份只哈希语义字段**：`snapshot_id` 由 `schema_version`、`cutoff_time`、按 dataset 名排序的
   `(dataset, data_version, value_digest, as_of_fidelity, event_time_min, event_time_max)`、
   `symbol_map_digest` 与 `universe_calendar_digest` 导出。创建时间、路径、codec、文件 SHA 和主机
   只进 provenance；相同语义成员必须得到相同 ID。
4. **构造时失败关闭**：成员缺失、版本 invalid、manifest/value digest 不一致、覆盖范围不足、
   as-of 保真度不满足声明用途，或 symbol/universe/calendar 摘要缺失时，不得发布
   ResearchSnapshot。已发布对象不原地修改；成员或 cutoff 改变生成新 ID。
5. **canonical 禁止动态 latest**：F007 canonical 只接受已发布的 `snapshot_id`，不得在运行中
   解析 latest、按 `exported_at` 猜全湖时点或替换成员。preview 可以请求 latest，但必须先解析、
   校验并发布一个 ResearchSnapshot，再开始计算；报告必须显示实际 snapshot ID。
6. **下游统一引用 snapshot ID**：ExperimentContext/experiment identity、评测产物目录、
   PortfolioDef 证据、signal cache 与 DeploymentRun 都引用 `research_snapshot_id`。需要审计单项
   数据时，通过 ResearchSnapshot 反查 `(dataset, data_version, value_digest)`，不复制第二份成员
   清单到各下游对象。

## 所有权与生命周期

- F002 拥有 DatasetVersion、dataset manifest、canonical row/value digest、valid/invalid、不可变
  symbol-map artifact 与只读接口。
- `experiment_store` 拥有 ResearchSnapshot schema、构造器、不可变 artifact 和 `snapshot_id`。
- F007 拥有 canonical 必须显式绑定 ResearchSnapshot 的门禁；preview 的 latest 解析只是构造输入，
  不是可复现身份。
- F005/F006/Freqtrade bridge 只能消费已绑定的 snapshot ID，不重新选择 dataset 版本。
- snapshot artifact 存放于 `reports/research_snapshots/<snapshot_id>/manifest.json`；它只引用 lake
  manifest，不复制数据，因此不突破“研究只读 lake”红线。
- symbol-map artifact 由 F002 内容寻址保存于 `lake/_metadata/symbol_maps/<digest>.csv`；universe
  artifact 由 **F008** 内容寻址台账拥有（`lake/_metadata/universes/<digest>.csv`，`F008 IR-002`
  提供加载与 `universe_at(T)` 语义），F007 只读消费、**不复制进 reports**；calendar JSON 由
  `experiment_store` 规范化并保存于 `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`
  （该目录只承载 calendar）。ResearchSnapshot provenance 以 `universe_path` / `calendar_path`
  分别引用这两个不可变 artifact，不能仅记录一个日后可能失去原文的摘要。

## 后果

- 正面：保留 dataset 独立发布与修订，同时使多数据集实验、信号缓存和部署记录可精确复现；
  “latest” 从隐式运行状态变为可审计的显式解析结果。
- 负面/义务：每次新的成员组合或 cutoff 都会多一个小型 manifest；symbol map、PIT universe 和
  calendar 必须拥有稳定摘要及可重放的不可变 artifact，缺失时会阻塞 canonical，而不能再靠当前
  文件或当前成员表补齐。F002 提供 symbol-map artifact；universe artifact 由 F008 内容寻址台账
  提供（F007 只读消费），calendar JSON 由调用 F007 snapshot builder 的研究配置显式提供，
  均不扩入 F002。
- 实施：F002 reader 回报解析后的 dataset/version/value digest；F007 T001 实现 snapshot builder/
  reader contract；架构 §4.4/§4.5 与 PRD FR1/FR5/FR7 统一改用 ResearchSnapshot 语义。

## 备选方案

- **全湖单一版本号**：拒绝。耦合不同采集节奏和失败域，任一 dataset 失败都会阻塞全部研究。
- **运行时分别读取 latest valid**：拒绝。结果依赖执行时刻，无法重放，也会产生跨数据集时点漂移。
- **按 exported_at 临时聚合**：拒绝。它是 provenance，不是 PIT、覆盖范围或映射一致性证明。
- **选定方案：不可变引用集合**：只增加小型 manifest，不复制数据，同时保留精确成员谱系。

## 修订记录

- 2026-09-18：universe 与 calendar 拆为**两个独立 artifact 引用**——universe 归 F008 内容寻址
  台账（`IR-002`/`IR-003`），calendar 归 F007 拥有；provenance 中原先指向合并 artifact 的单一
  路径字段拆为 `universe_path` / `calendar_path`；冻结 `universe_calendar_digest` 组合公式
  `sha256(canonical_json({"universe": <universe_digest>, "calendar": <calendar_digest>}))`。
  动因：F007 检视 D030——DR-006 拆分后 ADR 原文仍写单一 JSON 摘要，产生第二真相源。
  身份语义不变（`snapshot_id` 仍哈希组合摘要）。
