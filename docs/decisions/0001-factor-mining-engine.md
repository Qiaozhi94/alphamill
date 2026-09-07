# ADR-0001：因子挖掘主引擎选型 —— AlphaGen vendor + 冒烟闸门 + 降级阶梯

- 日期：2026-09-06
- 状态：Accepted
- 决策人：Georg
- 证据全文：[`docs/alphamill-research-factor-mining.md`](../alphamill-research-factor-mining.md)

## 背景

PRD G3 要求因子工厂达到 ≥100 名义候选/周，同时报告有效独立数、来源和门禁漏斗；
quant-crypto 实测约 5 个/周，探索能力不足。
对 2026-09 时点开源生态的调研结论：

- **AlphaGen**（ICT-FinD-Lab/alphagen，原 RL-MLDM，1.2k★）：RL 表达式生成 + 线性协同池；
  核心优势是代码冻结带不走的——协同池（增量 IC reward，机制性防冗余）+ GPU 张量评估（吞吐）+ 量化原生算子。
  已知问题：无 LICENSE（个人私有使用，风险可忽略）；核心 21 个月未实质更新；
  requirements.txt 自身损坏（`qlib==0.0.2.dev20` 是装错的包、numpy/pandas 为 2021 版）。
- **gplearn**：v0.4.3 复活（2026-01），BSD-3，但无协同概念、fitness 全样本评估有结构性泄漏、分钟级慢。
- **Qlib 表达引擎**：maintainer 在 issue #1988 确认无法脱离 bin 数据独立使用——排除独立提取。
- 2024-2026 新浪潮（RD-Agent(Q)/AlphaAgent/FactorMiner/alpha-foundry）：或太重或太年轻，列为观察项。

## 决策

1. **主引擎 = AlphaGen，vendor 方式接入**（非安装）：核心子集（expression / tensor calculator /
   LinearAlphaPool）进 `factor_factory/generators/alphagen_vendor/`；丢弃其 requirements.txt，
   自定现代栈（torch 2.x / numpy 2.x / pandas 2.x / sb3 最新+gymnasium）；自写 feather→tensor
   数据适配器替代 `alphagen_qlib`（qib 依赖连同装错包问题一起消失）。
2. **冒烟即闸门（time-box 2 个工作日）**：第 1 天 vendor+现代栈跑通 1 个 PPO epoch；第 2 天产出
   因子做 RankIC 对齐。通过 → 锁定；超时/坑深 → 降级，不沉没成本。
3. **降级阶梯**：L1 = AlphaGen 表达式求值器 + 自写搜索（绕开 sb3/RL，保留 GPU 批量评估）；
   L2 = 纯 gplearn（1h/4h 重采样 + 自建算子 + 滚动 fitness）。
4. **对照基线**：AlphaGen 仓库自带的 gplearn/ 与 dso/ 直接利用，不单独引入 gplearn 项目。

## 降级切换判据

冒烟闸门 time-box 已定（2 个工作日），但"何时降级"此前未成文——单人 time-box 最容易
自我豁免。以下判据预写为**二元可测项**：到期未达标即切换，不允许"再给一天"；切换动作
与触发原因记入当日 experiment manifest。降级不自动回切，回切须重开一轮冒烟 time-box。

**切到 L1（AlphaGen 表达式求值器 + 自写搜索，绕开 sb3/RL）**——满足任一条即触发：

- [ ] 第 2 个工作日结束时仍未跑通 1 个 PPO epoch（time-box 用尽）；
- [ ] 第 1 个工作日结束时，sb3/gymnasium 现代栈仍未跑通最小训练循环（依赖阻塞，判定
  vendor+RL 路线风险不可控，直接止损）；
- [ ] 第 2 个工作日结束时，feather→tensor 适配器未产出首个可做 RankIC 对齐的因子。

**从 L1 切到 L2（纯 gplearn）**——满足任一条即触发：

- [ ] L1 连续 2 周每周进评测台候选 <50（周配额取 M2 出口标准的量化线：单次挖掘 ≥50）；
- [ ] L1 连续 2 周零候选通过无前视审计（产出质量归零，吞吐量无意义）。

## M2 冒烟验收

冒烟通过标准在"跑通 1 个 PPO epoch + RankIC 对齐"之外，追加两条记账/抽查义务（预写为
二元可测项，防"以后补"）：

- [ ] **漏斗计数自冒烟第一天逐级入库**（PRD FR3.8/FR7.5）：生成 → 纯度门 → IC/收益证据
  → 成本门 → 样本量门 → 留出门 → 组合门 → 部署前复核，逐级记录绝对数与转化率；
- [ ] **奖励频率维度抽查**：对冒烟产出的首批候选抽查奖励构成——换手/交易频率惩罚项或
  ≥30 笔/90 天可达性预筛已生效（PRD FR2.3），IC 最优解未机制性偏向零交易/持仓型
  表达式（抽查记录进当日 experiment manifest）。

## 后果

- 正面：探索产能上限高；协同池提高候选互补性；主仓自包含。
- 负面/义务：vendor 卫生规则（最小 diff、`# [alphamill]` 标注、VENDORED.md 溯源，见 ADR-0002）；
  放弃上游升级路径；横截面 reward 在 6~12 对上噪声大——**宇宙扩容到 30~50 对必须与对接并行**（产出质量前提）；
  现代化改造成本未知量由冒烟闸门控制。
