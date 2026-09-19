# F007 测试夹具（v1）

本目录是 F007（统一评测台与证据门禁）的**预注册方法与控制夹具**，由任务 T002 建立。
它们同时是 T016（全链控制 golden）与 T023（执行机真实环境取证）的输入，也是契约测试
`tests/contract/test_f007_upstream_contracts.py` 的对照数据。

自检：`tests/unit/evaluation/test_prereg_fixtures.py`（校验本目录的 schema 与本文件的清单一致）。

## 目录

```text
tests/fixtures/f007/
├── README.md                    本文（T002 的 verify 产物）
├── method-v1.json               预注册 v1 方法/阈值/成本/样本量/五阶段/失败三维 schema
├── cohort-template-v1.json      v1 cohort schema 模板与不变量
├── expected-outcomes-v1.json    四个控制的预期门禁结果
└── controls/
    ├── funding_carry.csv        正控制 1（时序）
    ├── eth_btc_momentum.csv     正控制 2（截面）
    ├── white_noise.csv          负控制（统计门）
    └── future_fill_leakage.csv  负控制（方法论门 / 故意泄漏）
```

## 阈值归属（`FR-004`）

所有方法、阈值与成本参数只存在于 `method-v1.json`，**不得硬编码进评测函数**。
变更任何阈值/方法都必须是新的 `method_id` / `cost_model_id`，不得原地改数；`method-v1.json`
的 `method_config.normalized` 与 `cost_model.normalized` 是实验身份（`experiment_id`）的输入，
改了就会产生新 ID。

已冻结的关键口径（与 `design.md` §3.3 同一份，不得在此另立第二真相源）：

| 口径 | 值 | 来源 |
|---|---|---|
| 样本量三级（半开区间，以笔计） | `[0,30)` underpowered · `[30,69)` provisional · `[69,∞)` trustworthy | `design.md` §3.3 / `spec.md` `FR-005` |
| 查重阈值 | `\|ρ\| > 0.99` → rejected；`0.90 ~ 0.99` → variant | `spec.md` `FR-008` |
| 五阶段 ID | `signal_quality` / `portfolio_transform` / `cost_capacity` / `temporal_stability` / `execution_implementation` | `design.md` §3.3 |
| 失败三维 | `stage` × `owner` × `mechanism` | `design.md` §3.3 |
| 无前视三层 | L1=F007（AST 纯度，fail-closed）；L2/L3=F006/M3 | `spec.md` `FR-007` |

## 统一数据格式

四个控制共用同一列集（`expected-outcomes-v1.json` 的 `unified_columns`）：

```text
time,symbol,close,signal,forward_return
```

- `time`：UTC ISO-8601；
- `signal`：待评测因子的信号列（适配器不得改变其数值，`DR-007`）；
- `forward_return`：前瞻收益标签；
- `close`：价格序列，供引用价格/未来算子的表达式使用。

数据全部由固定 seed 确定性生成（`funding_carry` 无随机，`eth_btc_momentum` seed=20260101，
`white_noise` seed=7，`future_fill_leakage` seed=11），**不含网络依赖、不含 wall-clock 依赖**。

## 四个控制与预期结果

| 控制 | 类型 | 形状 | 预期门禁结果 | 判据要点 |
|---|---|---|---|---|
| `funding_carry` | 正控制 | 时序 1×40 | 五阶段完整；统计显著；`cost_positive`；`trustworthy` | 信号与前瞻收益同向 |
| `eth_btc_momentum` | 正控制 | 截面 6×40 | 五阶段完整；统计显著；`cost_positive`；`trustworthy` | 截面 rank 与前瞻收益同向；同一 timestamp 的 PIT 宇宙内计算 |
| `white_noise` | 负控制 | 截面 6×40 | 统计门拦截；`cost_negative`；`dead` | 信号与前瞻收益独立 |
| `future_fill_leakage` | 负控制 | 时序 1×40 | 方法论门 `FAIL`（`mechanism=lookahead`）；`REJECTED`；仍登记入分母 | 表达式 `shift(close, -1)/close - 1` 引用未来算子 |

**正控制的 `promotion_verdict_ceiling` 是 `blocked_pending_audit`，不是 `promising`**：v0.2 的
L2/L3 无前视审计归 F006/M3，缺失层记 `not_yet_available`，因此证据达标的成员也只能到
`blocked_pending_audit`（`spec.md` `FR-007` / `design.md` §7）。夹具断言必须遵守这一点，
不得把正控制当成「可晋级」。

`expected-outcomes-v1.json` 是上面判定表的机器可读版本，两类消费者都以它为准：

1. **T016 全链控制**（`tests/integration/test_f007_controls.py`）：fixture 模式，不变量是
   「同一输入 → 同一结论」，与真实数据无关；
2. **T023 执行机真实环境取证**（`tests/integration/test_f007_controls_real.py`）：必须换用
   不可变 crypto 快照与独立命令，**不得复用本目录夹具冒充真实环境证据**（SOP §3）。

## 如何加载

夹具是**数据文件**，按显式路径读取，不依赖 pytest 的 sys.path 约定：

```python
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[2] / "tests/fixtures/f007"
method = json.loads((FIXTURES / "method-v1.json").read_text(encoding="utf-8"))
for control in json.loads((FIXTURES / "expected-outcomes-v1.json").read_text())["controls"]:
    frame = pd.read_csv(FIXTURES / control["path"])
```
