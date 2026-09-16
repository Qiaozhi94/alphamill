---
kind: feature
id: F003
version: "0.2"
related_features: [F001, F002, F007, F008]
topics: [factor-factory, alphagen, vendor, generators, m2]
doc_kind: design
created: 2026-09-14
updated: 2026-09-14
---

# F003：AlphaGen vendor 与可插拔生成器平面 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

> **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——
> 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
> 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。

## 0. 输入与约束

- **行为契约**：`spec.md`
- **PRD / Architecture / System Design**：`docs/alphamill-prd.md` FR2.1~FR2.6；`docs/alphamill-architecture.md` §三（`factor_factory/` 目录）、§4.0/§4.1/§4.1.1（FactorDef 与 AlphaGen 适配契约）、§7.1（机器边界与 GPU 槽位）；`docs/alphamill-research-factor-mining.md` §3.1
- **ADR / 上游 Contract**：ADR-0001（选型、冒烟闸门、降级判据）、ADR-0002（vendor 卫生规则、pin 纪律、永不 fork）、ADR-0003（门禁不降级）、ADR-0007（快照绑定）；F002 的 `alphamill.data_bridge.reader.read()` 与 `(dataset, data_version, value_digest)` 身份
- **实现约束**：
  - Python 3.11+，src-layout `src/alphamill/factor_factory/`；本仓代码 350 行硬上限、ruff（`E,F,I,B,UP,SIM`，line-length 100）；
  - `tools/verify.py` 只收集 `tests/unit` 与 `tests/integration` 两个目录——**本 feature 的全部测试必须落在这两个目录内**，否则不进质量门；
  - 研究数据只经 F002 湖快照读取，禁止直读 TimescaleDB（PRD 数据红线）；
  - **机器边界（架构 §7.1，事实源 env-manager `data/fleet.json`）**：开发机 `qiaozhi-gp`/`gp-wsl`（Legion Go，AMD Radeon 780M iGPU，**无 NVIDIA**；本工作树 2026-09-14 实测 `nvidia-smi` 不存在、`/usr/lib/wsl/lib/` 只有 `libd3d12/libdxcore`）只跑编码、单元测试与 `tools/verify.py`；**挖掘训练的目标机是执行机**，同一时刻只有一台——当前 `qiaozhi-lt`（Win11 + WSL2，RTX 4060 Laptop 8GB），成熟后整体迁移至 `qiaozhi-lab`（原生 Ubuntu 26.04，RTX 5070 Ti 16GB / Blackwell sm_120，CUDA 13.1/13.2）。本设计的 GPU 路径按「能力存在即启用、不存在即显式拒绝」编写，开发机上只走 CPU 契约路径（`docs/SOP.md` §3）。
  - **湖与训练同机**：执行机同时承载 TimescaleDB、导出与挖掘训练，`lake_root` 指向本机湖目录，没有跨机数据传输问题；NAS 仍只承担 F002 的备份职责。
  - **迁移前瞻**：显存上限、时段表、耗时/产能相关的值必须可配且写入运行记录，**不得写死常数**。迁移不只是换卡：平台从 Win11+WSL2 变成原生 Ubuntu，GPU 架构从 Ada 变成 Blackwell sm_120（**torch 必须是 CUDA 12.8+ 的构建，默认 wheel 不一定含该架构**），因此 `mining` extra 的 pin 要显式选择带 sm_120 的轮子。

## 1. 技术概要与影响面

三层结构，自外向内：**生成器平面（接口 + 两个后端 + 持久化 + CLI）→ 胶水层（数据面 / 适配器 / 算子登记 / 目标对齐 / 调度）→ vendor（AlphaGen 核心，原样最小 diff）**。依赖方向严格单向 `平面 → 胶水 → vendor`，vendor 不认识 alphamill。挖掘运行读 F002 湖快照构造张量，训练产出表达式，胶水层把表达式编译为 `FactorDef` 并做生成侧自检，最后把候选与协同池以内容寻址 JSON 落到 `reports/generation/<run_id>/`，同时写 append-only 事件供 F007 的漏斗第一级消费。

- 前端：不适用（无 UI；只读展示归 F005，ADR-0005）
- 后端 / API：新增 `src/alphamill/factor_factory/{generators,hypotheses,registry}/` 与 `cli.py`；不改 F002 任何模块，只调用其只读 reader
- 存储 / Migration：无数据库 migration；新增文件系统产物根 `reports/generation/`（运行产物，入 `.gitignore`）
- Runtime / Agent Adapter：新增 GPU 单槽仲裁与训练窗口校验；与 F004 的 Kronos 常驻推理**共用执行机的同一张卡**，夜槽内 Kronos 卸载（架构 §7.1）
- Event / Evidence：新增 `generation.run_completed` / `generation.candidate_rejected` 两类 append-only 事件；**不写任何 F007 台账、留出或晋级路径**
- 并行依赖：`F008` 宇宙扩容会把 `ohlcv_1m` 的 pair 数从 6 抬到 30~50——数据面代码不需要改（`lake_tensor` 本就按绑定解析 pair 集合），但显存占用与横截面 reward 信噪比随之变化，故 `universe` 必须进运行记录
- 文档 / 配置：`pyproject.toml` 新增 `mining` 可选依赖组与 vendor 的 ruff 排除；`docs/SOP.md` Code Quality 豁免表登记 vendor 目录；`alphagen_vendor/VENDORED.md` 新建

## 2. 架构与模块边界

```text
src/alphamill/factor_factory/
├── hypotheses/
│   ├── schema.py             # HypothesisDef 结构与校验（DR-003）
│   └── catalog.py            # 假设注册；mechanism_unknown 内置项
├── generators/
│   ├── base.py               # Generator 协议 + GenerationRequest/Result/Counts（FR-001）
│   ├── binding.py            # SnapshotBinding：research_snapshot_id | 显式元组（FR-003, Q-002）
│   ├── lake_tensor.py        # 快照绑定 → (T×P×F) 张量 + PIT 掩码 + feature_map（FR-003；掩码消费 F008 `universe_at(T)`）
│   ├── operator_registry.py  # 算子能力登记表（FR-005；F007 FR-002 的消费源）
│   ├── purity.py             # 生成侧 AST 自检与拒绝原因码（FR-005）
│   ├── objective.py          # 换手惩罚 / ≥30 笔 90 天可达性预筛（FR-005）
│   ├── alphagen_adapter.py   # 表达式 token ↔ FactorDef.compute（FR-004，架构 §4.1.1）
│   ├── alphagen_runner.py    # sb3/gymnasium 训练编排 + 协同池导出（FR-006, FR-007）
│   ├── gpu_slot.py           # 显存自检 + 单槽 FIFO + 训练窗口校验（NFR-002）
│   ├── egress_guard.py       # 进程级无网络出口护栏（NFR-004）
│   ├── manual/               # 人工 crypto 原生种子后端（FR-001，US-001）
│   └── alphagen_vendor/      # AlphaGen 核心 vendor（最小 diff）+ VENDORED.md
├── registry/
│   ├── factor_store.py       # FactorDef 内容寻址读写（DR-002）
│   ├── pool_store.py         # 协同池 meta-factor（DR-004）
│   └── run_store.py          # GenerationRun manifest + 事件 JSONL（DR-001, TR-001/002）
├── bench/                    # F001 原样迁入的历史评测脚本，本 feature 不触碰
└── cli.py                    # alphamill-generate（IR-001）
```

边界规则：

| 边界 | 规则 |
|---|---|
| 胶水 → vendor | 单向。vendor 内任何 `import alphamill.*` 视为卫生检查失败（AC-002） |
| 生成器 → 数据 | 只经 `data_bridge.reader.read()`；`lake_tensor` 是唯一取数入口，其他模块不得自行读湖 |
| 生成器 → 证据 | 无。生成器进程只被允许写 `reports/generation/<run_id>/` 前缀；F007 台账、留出目录不在其可写集合（NFR-004） |
| 后端 → 接口 | 后端只实现 `Generator` 协议；配置差异走 `GenerationRequest.config`，不得让调用方分支 |
| 唯一真相源 | 候选定义 = `factors/<factor_id>.json`；运行事实 = `run.json`；两者之外不得出现第二份候选清单 |
| PIT 宇宙 → F008 | `lake_tensor` 的横截面掩码只读消费 F008 的内容寻址宇宙台账（IR-002 的 `universe_at(T)` 与 digest、IR-003 的 `schema_version`）；F008 未落地时用显式 universe 配置并把其 digest 与来源写进 `run.json`，任何路径都不得用当前成员表回填历史（架构 §4.1.1 截面边界） |

**vendor 子集边界（按功能定义，不预先钉死上游路径）**：取表达式与算子、张量求值器、线性协同池、RL 环境与 token 化四块；**明确丢弃** `alphagen_qlib/`（qlib 数据层）、上游 `requirements.txt`、上游自带的 `gplearn/` 与 `dso/`（仅在降级到 L2 时按需再取）。精确文件清单在 vendor 落地任务中按上游实际布局核对后写入 `VENDORED.md`——本设计不替代实地核对。

与 Kronos vendor 的差异：Kronos 是"上游 clone + pin commit"，`vendor/Kronos/` 不入 git；AlphaGen 是"vendor 进主仓"（ADR-0002），`alphagen_vendor/` **必须入 git**，因为上游冻结后本项目全权维护。

## 3. 数据模型与 Migration

无数据库 schema、无 migration。全部为文件系统内容寻址产物。

**产物布局**（`reports/` 是架构定义的运行产物目录）：

```text
reports/generation/<run_id>/
├── run.json                  # GenerationRun manifest（最后写，原子 rename）
├── factors/<factor_id>.json  # FactorDef 定义（只含定义，无结论）
├── pool.json                 # 协同池 meta-factor（可选）
├── events.jsonl              # TR-001/TR-002 append-only
└── checkpoints/              # 训练 checkpoint（可清理，不属于证据）
```

**FactorDef（`schema_version: 1`）**：`factor_id` / `definition_digest` / `hypothesis_id` / `name` / `generator` / `generator_version` / `scope` / `expression` / `params` / `data_columns` / `feature_map_digest` / `run_id` / `created_at`。

- `definition_digest = sha256(canonical_json(定义字段))`，规范化时**排除** `factor_id`、`run_id`、`created_at`——同一表达式在不同 run 得到同一 digest，用于重复定义识别（拒绝原因码 `duplicate_definition`）；
- `factor_id = <generator>_<definition_digest[:12]>`：人读前缀 + 内容后缀，**不含 run 序号**——同一表达式跨 run 重跑得到同一 `factor_id`（NFR-003）；运行归属由独立的 `run_id` 字段承载，不进入身份；
- **禁止字段**：`ic`、`rank_ic`、`pnl`、`verdict`、`promoted` 等结论字段由 schema 白名单显式拒绝（AC-001）。
- **加载契约（可执行恢复）**：落盘 DTO 与架构 §4.1 的可执行 `FactorDef` 是**同一对象的两种形态**——磁盘只存定义字段，加载时由 `alphagen_adapter` 依据 `expression` 与校验过 digest 的 `feature_map` 重建 `compute` 闭包，并还原 `meta`（含 `meta["expression"]` 与假设来源）；`factor_store.load()` 必须返回可直接执行的对象，不得要求调用方自行重新编译（AC-001/AC-004）。

**HypothesisDef**：`hypothesis_id` / `mechanism`（经济动机与作用机制）/ `data_columns` / `applicable_state`（适用状态/regime；catalog 与自动候选给显式默认值 `unspecified`，不隐式留空）/ `expected_holding_period` / `cost_sensitivity` / `source` / `generation`。内置 `mechanism_unknown` 条目供自动候选绑定，并在 FactorDef 上如实标记（PRD FR2.1）。

**GenerationRun**：`schema_version` / `run_id` / `generator` / `engine`（`vendor_commit`、`code_digest`、pin 栈版本）/ `binding` / `seed` / `device` / `hostname` / `vram_limit_gb` / `universe`（`pairs` 数与 `symbol_map_digest`）/ `tier_level`（L0/L1/L2）/ `window`（含重采样频率）/ `objective`（`turnover_penalty_lambda`、`reachability_min_trades_90d`、`cost_model`、`min_after_cost_return`）/ `counts` / `pool` / `started_at` / `finished_at` / `status` / `termination`。

- `counts = {proposed, rejected: {unregistered_op, lookahead, reachability, duplicate_definition}, registered}`——逐级计数即 F007 漏斗的第一级分母；
- `universe` + `hostname` + `vram_limit_gb` 三项一起回答「这个结论在什么条件下成立」：宇宙规模决定横截面 reward 的信噪比（`F008` 并行扩容中），机器与显存上限决定产能数字可不可比。跨运行比较前必须先比这三项；
- `binding` 两种形态，**语义字段与 ADR-0007 的 `ResearchSnapshot` 逐项等价**，差别只在过渡态不落 `experiment_store` artifact：
  - `{"mode": "snapshot", "research_snapshot_id": "..."}`（F007 落地后，即 ADR-0007 的 `snapshot_id`）；
  - `{"mode": "explicit_tuples", "cutoff_time": "...", "members": [{dataset, data_version, value_digest, as_of_fidelity, event_time_min, event_time_max}], "symbol_map_digest": "...", "universe_calendar_digest": "..."}`（过渡态，spec Q-002）。
  两种形态都必须在启动时逐项校验成员 `value_digest`，并校验 `cutoff_time` / `as_of_fidelity` / `symbol_map_digest` / `universe_calendar_digest` 存在且可解析；字段名与 ADR-0007 的成员契约一一对应，F007 落地后过渡路径原地替换为 `snapshot_id`，下游消费字段不变。

**AlphaPoolDef**：`pool_id`（内容寻址）/ `members: [{factor_id, weight}]` / `run_id` / `pool_version`。成员集合变化即新 `pool_id`，不原地改写（DR-004）。

**Migration / 历史数据**：无历史数据。`reports/generation/` 加入 `.gitignore`（体积大、含 checkpoint）；需要入库的只有 curated 摘要，按需单独提交。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

```python
@dataclass(frozen=True)
class GenerationRequest:
    generator: str
    binding: SnapshotBinding
    seed: int
    window: Window                 # start/end/resample
    config: Mapping[str, Any]
    quota: int                     # 名义候选配额

@dataclass(frozen=True)
class GenerationResult:
    run_id: str
    factors: list[FactorDef]
    pool: AlphaPoolDef | None
    counts: GenerationCounts
    device: str
    tier_level: str

class Generator(Protocol):
    name: str
    def produce(self, request: GenerationRequest) -> GenerationResult: ...
```

CLI `alphamill-generate`（IR-001）：

| 子命令 | 作用 | 拒绝条件（非零退出） |
|---|---|---|
| `smoke --day {1,2}` | 逐条判定 ADR-0001 冒烟判据并写当日 manifest | 缺绑定；判据脚本无法执行 |
| `mine --generator <name> --binding <file> --seed N --quota K` | 完整挖掘运行 | 缺绑定 / 绑定 invalid / digest 不符 / 档位不明 / 窗口外且无 `--allow-offhours` / 无 CUDA 且无 `--allow-cpu` |
| `seed --generator manual --binding <file>` | 人工种子后端产出 | 同上（不含 GPU 相关项） |
| `show --run <id> \| --factor <id>` | 只读打印产物 | 产物不存在或 schema 版本不识别 |

适配契约（架构 §4.1.1，FR-004）：表达式 token 序列 → 闭包编译为 `FactorDef.compute`；表达式原文入 `meta["expression"]` 保证可反解；`feature_map: {数据列名 → 张量通道}` 反解出 `data_columns`；`time_series` 输入单 pair Frame，`cross_sectional` 输入带 PIT 宇宙掩码的面板。`feature_map` 本身内容寻址（`feature_map_digest`），改变映射即改变候选身份。

### Event / Trace Contract

append-only `events.jsonl`，每行一个事件，含 `event_type` / `ts` / `run_id` / payload：

- `generation.run_completed`（TR-001）：`generator`、`engine`、`binding`、`seed`、`device`、`tier_level`、`counts`、`pool`；
- `generation.candidate_rejected`（TR-002）：`expression`、`reason_code ∈ {unregistered_op, lookahead, reachability, duplicate_definition}`、`detail`。

幂等键：`(run_id, event_seq)`。查询方式：按 `run_id` 目录顺序读，F007 以此重建漏斗第一级；F003 不提供查询服务。

## 5. Runtime、Workflow 与并发

```text
mine/seed 调用
  → 解析并校验绑定（每个 dataset 逐项 value_digest 比对；invalid 立即 REJECTED）
  → 能力自检（device / mining extra 是否装齐 / egress guard 安装 / lake_root 可读）
  → 申请 GPU 单槽（flock 独占 reports/.locks/gpu.slot；不可得则 QUEUED 等待）
  → 训练窗口校验（22:00–06:30；窗口外需 --allow-offhours）
  → lake_tensor 构造张量（默认重采样 1h；PIT 掩码按 F008 `universe_at(T)`，F008 未落地时按显式 universe digest）
  → 后端 produce()：训练 / 枚举 → 候选表达式
      → 逐候选：operator_registry 校验 → purity 自检 → objective 预筛 → 编译 FactorDef
      → 通过者入池参与协同池增量 IC 选择
  → 写出：factors/*.json → pool.json → events.jsonl → run.json（最后写，tmp+fsync+rename）
  → 释放单槽
```

并发与恢复：

- **单槽 FIFO（可验证协议）**：`gpu_slot` 用文件锁（`reports/.locks/gpu.slot`）实现执行机内独占，配一个 append-only 队列记录 `reports/.locks/gpu.queue`；每次入队 / 取锁 / 释放 / 等待超时写一条 `{queue_seq, run_id, ts, event, vram_free_gb}`，其中 `queue_seq` 单调递增、先入队者先取锁、释放后由队首等待者取得。等待超过可配超时（默认 30min）即释放队位并写 `termination=queue_timeout` 的终态 `run.json`，不无限挂起。架构 §7.1 的硬规则——「队列赢，绝不并行赌 OOM」——落在这里，协议本身用两个并发挖掘运行即可取证（不依赖 GPU 或 Kronos）；
- **显存自检**：取锁后、建张量前读可用显存，低于配置上限即释放锁并回到队列（不强行启动）。上限**可配不写死**：当前执行机（4060 8GB）按 §7.1 标定为 ≤6GB，迁移到 5070 Ti 时改配置而非改代码，实际取值写进 `run.json`；
- **CPU 回退**：无 CUDA 时必须显式 `--allow-cpu`，否则拒绝启动——防止"静默跑了一夜 CPU"；CPU 运行在 `run.json` 标 `device=cpu` 与 `hostname`，产能与显存类断言对该运行不成立（spec NFR-005）。开发机只走这条路径，且只用于单元与契约测试；
- **checkpoint**：训练每 N steps 落 `checkpoints/`；崩溃后重跑以相同 `(seed, binding, code_digest, config)` 从头复算即可得到相同候选集（NFR-003），checkpoint 只用于省时，不参与身份；
- **优雅停机**：SIGTERM 走正常收尾（导出已产候选与池），`status=completed` + `termination=early`；非受控异常为 `FAILED`，此时 `run.json` 不写出，目录内残留物被下次 `show` 视为未完成运行（与 F002 的"manifest 最后写"同构）；
- **与 Kronos 的协同（live owner 与取证）**：训练夜槽内 Kronos 应卸载（架构 §7.1）。**卸载动作的 owner 是 F004 运行时**（服务控制入口由它提供）；F003 侧只拥有「编排请求 + 结果观测」任务——训练窗口开始时发起卸载请求，并把 `kronos_offload: {requested_at, observed_state, vram_before_gb, vram_after_gb}` 写进 `run.json`，绝不主动杀别人的进程。若卸载控制契约尚不可用（F004 已收口且把 GPU 直通后移，见 tasks §5），F003 **不降级为并行抢卡**：保持在单槽 FIFO 中等待显存达标，并把 `offload_contract_unavailable` 如实记入运行记录；此时 FIFO 协议仍可由两个并发挖掘运行独立取证。

## 6. UI 与可观测性

UI：不适用——本 feature 无页面。候选与产能的只读呈现归 `F005`，其数据源是 `run.json` / `factors/*.json`（ADR-0005：不新增口径载体，门禁裁决不页面化；F003 本来也不产裁决）。

可观测性：

- 结构化日志（JSONL）：运行阶段切换、取锁/排队、显存自检结果、每 N 个候选的拒绝原因分布；
- 运行摘要指标（写入 `run.json`，不进 Grafana 口径）：入册候选数、各拒绝原因码计数、训练吞吐（steps/s）、显存峰值、总耗时、device、档位；
- 冒烟闸门：每条判据的 `pass/fail` + 时间戳 + 证据指针写当日冒烟 manifest，裁决结论人可读、机器可解析；
- 运维可见性：`alphamill-generate show` 即诊断入口，不引入新的看板。

## 7. 失败、恢复、安全与兼容

- **校验与失败映射**：绑定缺失/invalid/digest 不符 → 启动期 `REJECTED`（退出码非零，原因入日志）；未登记算子/前视/可达性/重复定义 → 候选级拒绝并计数（运行继续）；训练或写出异常 → `FAILED` 且不写 `run.json`；mining extra 未装齐 → 启动期拒绝（不静默跳过）。
- **重启与恢复**：无 `run.json` 的运行目录视为未完成，可直接删除重跑；相同语义输入重跑得到相同 `factor_id` 集合，因此"重跑"永远是安全的恢复手段。
- **权限 / escalation / 凭据边界**：生成器进程无任何凭据需求（不访问 TimescaleDB、不访问交易所、不联网）；写路径白名单限定 `reports/generation/<run_id>/`；`egress_guard` 在 runner 入口替换 socket 构造函数、只放行 AF_UNIX——**这是进程级护栏，不等于内核级网络隔离**，如需更强隔离再引入 netns（本 feature 不做，如实记录）。
- **Windows / POSIX / 版本兼容**：开发机与当前执行机 `qiaozhi-lt` 都是 Win11 + WSL2，最终执行机 `qiaozhi-lab` 是原生 Ubuntu——因此不得依赖任何 WSL 专属路径（`/mnt/c`、`/usr/lib/wsl`）或 Windows 宿主行为；路径统一 `pathlib`，产物路径写 POSIX 逻辑路径，物理路径只进 provenance；运行记录必须带 `hostname` 与 `device`，让任何一份证据都能追到取证机器——迁移后这也是「哪些结论需要重跑」的判定依据；vendor 目录不参与 ruff 与 350 行限制（`extend-exclude` + `docs/SOP.md` 豁免表登记），理由是 ADR-0002 的最小 diff 卫生规则与"贴近上游原貌"直接冲突于本仓代码风格门；
- **依赖 pin**：`torch` / `numpy` / `stable-baselines3` / `gymnasium` 等进 `[project.optional-dependencies].mining` 并写版本范围；`tools/check_dep_pins.py` 扩展为"可选 extras 已安装才校验范围、未安装不判红"，同时由运行期能力自检保证未装齐时**拒绝启动**——两者配合才不会变成静默漏洞（SOP「安全校验降级必须声明」）。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | unit | `tests/unit/test_f003_generator_contract.py` | 两后端同一 schema；含 `ic`/`verdict` 等结论字段的结果被拒绝；落盘 DTO 加载后可执行（compute 重建、meta 还原） |
| `AC-002` | unit | `tests/unit/test_f003_vendor_hygiene.py` | vendor 内无标注差异行报错；vendor 内 `import alphamill` 报错；`VENDORED.md` 五项齐备 |
| `AC-003` | integration | `tests/integration/test_f003_lake_tensor.py` | invalid/digest 不符拒绝启动；张量与 reader 抽样点容差内一致；不可交易时点掩码为不可用 |
| `AC-004` | unit | `tests/unit/test_f003_alphagen_adapter.py` | 编译闭包与张量求值一致；表达式反解等价；`data_columns` 由 `feature_map` 反解；加载后的 FactorDef 可直接执行 |
| `AC-005` | unit | `tests/unit/test_f003_operator_registry.py` | 启用算子全部登记；未登记/前视/非法跨 pair 候选按原因码计数拒绝 |
| `AC-006` | integration | `tests/integration/test_f003_generation_run.py` | 零变号表达式被可达性预筛拒绝；一次运行入册 ≥50（在执行机上判定） |
| `AC-007` | integration | `tests/integration/test_f003_smoke_gate.py` | 四条判据逐条二元判定并入 manifest；任一触发即降级裁决；L1→L0 回切请求被拒 |
| `AC-008` | integration | `tests/integration/test_f003_alpha_pool.py` | 池成员与权重可反解；按成员重算与记录容差内一致；成员变化产生新 `pool_id` |
| `AC-009` | integration | `tests/integration/test_f003_generation_run.py` | 同 `(seed, binding, code_digest, config)` 重跑 factor_id 集合相同；自动候选绑定 `mechanism_unknown` |
| `AC-010` | unit | `tests/unit/test_f003_gpu_slot.py` | 显存低于上限/时段撞车进队列不并行；FIFO 先入队先取锁、释放后队首取得、超时留 `queue_timeout` 终态；无 CUDA 且无 `--allow-cpu` 拒绝启动；运行标注 `device`/`hostname` 与 `kronos_offload` 观测 |
| `AC-011` | integration | `tests/integration/test_f003_boundaries.py` | egress guard 拦截出网；写 `reports/generation/<run_id>/` 之外路径被拒；缺绑定 `mine` 非零退出 |
| `AC-012` | unit | `tests/unit/test_f003_cli_contract.py` | `run.json` 与 `factors/*.json` 均带 `schema_version`；`show` 遇未知 `schema_version` 非零退出，不猜测兼容 |

真实环境场景：冒烟闸门 time-box 实跑（US-002）与训练窗口实测（显存峰值、耗时、入册数）必须在**执行机**上执行并记录 hostname 与设备，不得以 skip 代替证据（`docs/SOP.md` §3 机器边界）。开发机上这些用例按「本机无该能力」跳过是预期行为，不算证据也不算失败；**任何情况下不以开发机的 CPU 结果冒充执行机 GPU 结论**。执行机迁移到 5070 Ti 后，依赖显存与耗时的用例必须在新机重跑，不继承旧机结论。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| vendor 目录的代码风格门 | `ruff extend-exclude` 排除 `alphagen_vendor/**`，并在 `docs/SOP.md` Code Quality 豁免表登记（无解除期限，随 vendor 存在） | ADR-0002 要求最小 diff、贴近上游原貌，与本仓 350 行/ruff 门直接冲突 | 不改上游代码风格；胶水层照常受全部门禁约束 |
| torch 等重依赖的安装面 | 放 `[project.optional-dependencies].mining`，默认不装 | 只做数据桥的开发者不该背 torch 镜像体积（与 F004 的可选 profile 同构） | 若挖掘成为常态再评估默认化 |
| 可选 extras 的 pin 门禁 | `check_dep_pins` 扩展为"已安装才校验"，配合运行期能力自检 fail-closed | 未装即判红会逼所有人装 torch；只放宽门禁而无运行期兜底则是静默漏洞 | 两处必须同时落地，缺一即为降级 |
| 候选身份 | `definition_digest` 内容寻址 + 人读前缀 `factor_id` | 既要跨 run 识别重复定义，又要人能扫读 | 与 ADR-0006/0007 的内容身份风格一致 |
| 默认重采样 1h | 1h × 2 年 × 6 对 × ~12 特征 float32 ≈ 5MB，扩到 50 对仍 <45MB；1m 全窗为 ~302MB（6 对）/ ~2.5GB（50 对） | 显存预算主要留给 PPO 网络与 batch，特征张量不该吃掉预算 | 1m 只按需切窗；分钟级吞吐目标由 GPU 批量评估承担 |
| IC 口径对齐不是评测台 | 只做 vendor 张量 IC 与 pandas 参考实现的数值一致性回归 | 评测权唯一属 F007（ADR-0003） | F007 落地后退化为 vendor 回归测试 |
| egress guard 强度 | 进程级护栏（socket 构造拦截），不等于网络隔离 | 本机直接跑训练，引入 netns 成本高于收益 | 如需强隔离，后续以容器/netns 补强 |
| 机器边界 | 开发机无 GPU 只跑单元与门禁；挖掘训练与 GPU/产能证据在执行机取，记录 hostname 与设备 | 架构 §7.1：开发机不承载 GPU 负载，也不作为性能证据来源 | 执行机主机名与实测可用显存在 tasks T004 钉死 |
| 执行机后续整体迁移到 `qiaozhi-lab` | 显存上限、时段、耗时阈值一律可配并写入运行记录，不写死常数；不依赖 WSL 专属路径；torch pin 显式覆盖 sm_120 | 迁移同时换平台（WSL2 → 原生 Ubuntu）与换架构（Ada → Blackwell），机器差异藏进常数或路径假设会让迁移变成改代码 | 迁移动作按独立 Feature 立项 |
| 横截面 reward 在 6 对上噪声大 | 接口与闸门可在 6 对上验收；产出质量结论必须标注宇宙规模 | ADR-0001 后果条 | spec Q-001：宇宙扩容 Feature 立项窗口 |
| 上游冻结 21 个月 | 现代化成本由 2 日 time-box 封顶，超时即降级 | ADR-0001 冒烟即闸门 | L1/L2 阶梯已预写为二元判据 |

## 10. 待确认设计问题

- [x] DQ-001: vendor 的精确文件清单如何确定？ — 决策：不在设计期钉死上游路径（本设计只按功能定义子集边界），由 vendor 落地任务按上游实际布局核对后写入 `VENDORED.md`
- [x] DQ-002: sb3 / gymnasium 现代栈能否驱动 vendor 的 RL 环境？ — 决策：按"需要小改 env wrapper（gym→gymnasium）"的假设推进，适配动作作为冒烟第 1 天任务；第 1 天结束仍未跑通最小训练循环即触发 ADR-0001 的 L1 判据，不追加时间
- [x] DQ-003: 特征张量规模与显存预算如何分配？ — 决策：默认重采样 1h（估算见 §9），1m 仅按需切窗；显存上限可配不写死（当前执行机按 §7.1 标定为 ≤6GB），实际取值写入 `run.json`，取锁后、建张量前自检——特征张量本身只占几十 MB，预算主要由 PPO 网络与 batch 决定
- [x] DQ-004: 协同池成员变化如何版本化？ — 决策：池定义内容寻址，成员集合变化即新 `pool_id`，不原地改写
- [x] DQ-005: 生成运行的产物放哪？ — 决策：`reports/generation/<run_id>/`（架构已定义 `reports/` 为运行产物目录），目录入 `.gitignore`，`run.json` 最后写实现原子可见性
