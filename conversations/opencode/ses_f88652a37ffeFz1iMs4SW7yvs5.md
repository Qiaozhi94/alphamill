---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f88652a37ffeFz1iMs4SW7yvs5"
title: "Fix PRD issues D002/D004/D007/D011/D015/D018/D024 (@general subagent)"
project: "D:/Projects/alphamill"
model: "glm-5.3-flash"
created_at: "2026-09-06T16:43:51Z"
updated_at: "2026-09-06T16:49:50Z"
tokens_input: 54438
tokens_output: 4164
cost: 0.0
parent_id: "ses_f886c33ddffed2Ehk0OBMbTqR2"
---

# Fix PRD issues D002/D004/D007/D011/D015/D018/D024 (@general subagent)

## user · 2026-09-06T16:43:51Z

You are the FIXER in a review-convergence loop for AlphaMill (D:\Projects\alphamill), a crypto quant research system at design stage. Baseline: main @ 1bd8c4d. Language: Chinese, match existing PRD style.

YOUR FILE OWNERSHIP (do NOT touch any other file): docs/alphamill-prd.md ONLY.

First READ docs/alphamill-prd.md fully + the round-1 review report docs/reviews/CURRENT-doc.md (issues D002, D004, D007, D011, D015, D018, D024) + docs/decisions/0003-validation-gate-non-degradation.md for context.

MANDATORY — do NOT break: ADR-0003 frozen gate criteria (your changes only ADD protections/tighten), PRD non-goals list, G1-G5 goal numbering, FR1-FR6 numbering scheme (amend within existing FRs; if a sub-item is added use the existing numbering pattern like FR2.5).

TASKS (each maps to one review issue — keep the issue id in a brief HTML comment or note is NOT needed; just fix the content):

1. D002 (Critical, cost wall outside selection loop): RL reward = RankIC, eval-bench verdict by IC, cost tiers only enter at validation stage — the ×20 throughput amplifies candidates dying of the same cost wall that killed the predecessor; funding rate (perpetual futures, settled every 8h) appears NOWHERE. Fix in PRD:
   - Eval bench (FR2 area): verdict must include a cost tier as HARD FILTER (taker fee + slippage), not just IC; a candidate positive on IC but negative after costs must not be `promising`.
   - Cost model: add funding rate as a first-class cost component (perp 8h settlement; crowded-direction funding can reach double-digit annualized).
   - Mining loop (FR2.1/FR2.2 area): reward/pre-screen includes a cost penalty term (or explicit pre-screen cost sanity), so the RL loop doesn't optimize IC divorced from survivability.
2. D004 (High, multiple-testing trial counting undefined): FR2.4 names deflated significance + white-noise control but never defines "one trial". Fix: define explicitly — every evaluated expression (every candidate entering the eval bench, including rejected ones) counts as one trial; note that RL produces thousands of correlated expressions weekly so the raw count is the denominator for deflated significance; add a note that candidates share data/reward/synergy-pool so effective independent hypothesis count is far lower (order 5-10/week per round-1 analysis) — deflation must use the full evaluated-expression count, not the surviving count.
3. D007 (High, hidden backfill workstream): universe expansion 30-50 pairs needs ~46M new 1m rows (weeks-months at OKX rate limits), unowned and unbudgeted; M1 "1 week incl. all FR1" is not realistic. Fix: make backfill an explicit workstream inside M1 milestone with its own estimate (1-2 weeks wall-clock, runs parallel to dev work, explicit owner line), and adjust M1 wording so FR1 does not claim to include full backfill.
4. D015 (Medium, cost calibration source): FR3.4 cost parameters are quoted taker prices; add clause: cost parameters must be calibrated from quant-crypto dry-run actual fill records (existing asset), not exchange sticker prices.
5. D018 (Medium, RL reproducibility): FR6.1 manifest schema must include seed + determinism switches (torch deterministic mode etc.) for mining runs, else G5 (full-chain reproducibility) is a slogan for the mining step.
6. D011 (Medium, stale doc refs): fix any references to old numbered docs (docs/02-系统架构, docs/05-*, "doc 03") → current names (docs/alphamill-architecture.md etc.). Grep the file for `docs/0` and `doc 0` patterns.
7. D024 (Low, machine-specific absolute paths): PRD header references D:\Projects\... — replace with repo-relative or descriptive references (project name only, no drive letter).

Also: wherever the PRD states the Top1-only / single-factor deployment policy, align it with the new portfolio-construction decision (ADR-0004, being created in parallel at docs/decisions/0004-portfolio-construction.md) — reference it as `docs/decisions/0004-portfolio-construction.md` (file will exist by end of day; referencing it is correct even if you can't read it yet — the decision content: synergy pool combos deployable as meta-factors, Top-K portfolio replacing Top1-only).

Update frontmatter `updated:` to 2026-09-07.

VALIDATION: run `python tools/validate_spec_lifecycle.py` (cwd D:\Projects\alphamill) after edits — must stay green. If other agents' concurrent edits cause unrelated failures, ignore those and report; your own file must not introduce failures.

MUST NOT: touch any file other than docs/alphamill-prd.md; loosen gates; renumber existing FRs/goals; commit.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-06T16:43:51Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\reviews\\CURRENT-doc.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0003-validation-gate-non-degradation.md"})`


> [reasoning] Let me start by reading the required files: the PRD, the round-1 review report, and the ADR-0003.

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\alphamill-prd.md</path>
<type>file</type>
<content>
1: # AlphaMill — 产品需求文档（PRD）
2: 
3: > 版本：v0.1 | 日期：2026-09-06 | 状态：草案
4: > 前置文档：`D:\Projects\tradingview-quant-research\research.md`（TradingView 调研）、`D:\Projects\quant-crypto\00-系统总体方案.md`（上一代系统）
5: 
6: ---
7: 
8: ## 一、背景与问题定义
9: 
10: ### 1.1 quant-crypto 复盘（2026-05 ~ 2026-06）
11: 
12: 上一代项目 quant-crypto 用 5 周时间完成了大量基础设施：
13: 
14: | 资产 | 状态 | 位置 |
15: |---|---|---|
16: | TimescaleDB 数据湖 | ✅ 631 万行 1m OHLCV（6 个 OKX 永续对，2 年回补）+ 质量标记表 + 多周期连续聚合 | `D:\Projects\quant-crypto` |
17: | 衍生品特征数据 | ✅ funding / mark-index basis / open interest 已回补 | `db/migrations/003` |
18: | Kronos 信号基建 | ✅ Kronos-base GPU 推理，RankIC > 0.05（自定"强有效"门槛） | `kronos-signal/` |
19: | 信号缓存模式 | ✅ 预计算 → feather → 策略按时间戳读取，**已通过无前视审计** | `freq
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\reviews\CURRENT-doc.md</path>
<type>file</type>
<content>
1: ---
2: report_type: doc-review
3: round: 1
4: date: 2026-09-07
5: prior_report: 无（首轮全量检视）
6: scope: full-scan
7: stop_condition_met: false
8: severity_counts: {critical: 2, high: 8, medium: 10, low: 4}
9: issue_count: 24
10: baseline: main @ 1bd8c4d（2026-09-07 00:08 +0800，唯一 bootstrap 提交，工作树干净）
11: reviewer: Sisyphus（review-convergence 协议）
12: evidence: 检视人全量通读 docs 全部 17 份文件 + explore agent 代码区实测（verify.py 四步全绿）+ Oracle agent 战略/架构交叉评审（三路独立取证）
13: note: 本仓 CLAUDE.md 约定 CURRENT-doc.md / CURRENT-code.md 入库（覆盖 skill 默认的 local-only）；本文件为第 1 轮全量扫描，尚无修复方声明
14: issues_index:
15:   - {id: D001, severity: critical, title: 组合构建层缺失——协同池产物无部署路径}
16:   - {id: D002, severity: critical, title: 成本墙（费用+滑点+资金费率）不在
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\decisions\0003-validation-gate-non-degradation.md</path>
<type>file</type>
<content>
1: # ADR-0003：验证门禁不降级 —— quant-crypto 教训制度化
2: 
3: - 日期：2026-09-06
4: - 状态：Accepted
5: - 决策人：Georg
6: - 背景：`D:\Projects\quant-crypto` Phase 4 决策报告（2026-06-17，`blocked_no_paper_candidate`）与
7:   PRD G2 / FR3
8: 
9: ## 背景
10: 
11: quant-crypto 的最终 90 天留出门连续拦下全部候选（低频 Ridge/HGB、regime 增强、成本感知、
12: 衍生品 basis），看起来是"失败"，实际是验证协议在正确工作——它拦下的是会亏钱的东西。
13: 真正的问题是 alpha 供给量（每周 ~5 个假设）与留出期样本量不足（69 笔交易的 FAIL/PASS
14: 判定统计上不可信；regime filter 方向正确但 27 笔欠功效）。
15: 
16: 该门禁的价值来自它**从不放水**。任何"先上盘再观察"的妥协都会摧毁整个系统的可信度。
17: 
18: ## 决策
19: 
20: 1. **留出门不降级**：任何候选必须通过最终 90 天留出才能进入 paper/实盘——此规则从
21:    quant-crypto 原样继承，永不为吞吐量让路。
22: 2. **样本量门槛**：留出期 ≥30 笔交易才允许 FAIL/PASS 判定；样本不足输出 `UNDERPOWERED`
23:    
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:43:59Z

- **tool**: `grep({"output_mode": "content", "path": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "pattern": "docs/0|doc 0|doc03|D:\\\\"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\tools\\validate_spec_lifecycle.py"})`


> [reasoning] Now let me understand the tasks:

1. **D002**: Eval bench verdict must include cost tier as HARD FILTER (taker fee + slippage). Add funding rate as first-class cost component (perp 8h settlement). Mining loop reward/pre-screen includes cost penalty.

2. **D004**: FR2.4 define "one trial" = every evaluated expression (every candidate entering eval bench, including rejected). RL produces thousands of correlated expressions weekly → raw count is denominator for deflated significance. Note effective independent hypothesis count is far lower (5-10/week) — deflation must use full evaluated-expression count, not surviving count.

3. **D007**: Backfill explicit workstream inside M1 with own estimate (1-2 weeks wall-clock, runs parallel, explicit owner line). Adjust M1 wording so FR1 doesn't claim to include full backfill.

4. **D015**: FR3.4 cost parameters calibrated from quant-crypto dry-run actual fill records, not exchange sticker prices.

5. **D018**: FR6.1 manifest schema includes seed + determinism switches (torch deterministic mode) for mining runs.

6. **D011**: fix references to old numbered docs (docs/02-系统架构, docs/05-*, "doc 03") → current names. Grep for `docs/0` and `doc 0` patterns.

7. **D024**: PRD header references D:\Projects\... — replace with repo-relative or descriptive references (project name only, no drive letter).

Also: align Top1-only / single-factor deployment policy references with ADR-0004 (docs/decisions/0004-portfolio-construction.md) — synergy pool combos deployable as meta-factors, Top-K portfolio replacing Top1-only.

Wait — does the PRD actually mention "Top1-only"? Let me check. Looking at the PRD, I don't see an explicit Top1-only mention in the PRD. The review says "Top1-only 进 dry-run（integration §四）" — that's in the integration doc. But the task says "wherever the PRD states the Top1-only / single-factor deployment policy". Let me grep the PRD for such mentions.

From my read: S5 部署 says "留出通过 → 信号写 feather 缓存 → Freqtrade 策略模板挂载 → dry-run → paper". FR5.2 mentions strategy templates. No explicit Top1-only in PRD. But maybe I should check for "Top1" or "单因子" mentions. The PRD doesn't seem to have them. But I can still reference ADR-0004 where deployment is discussed — S5 and FR5.3. Actually the task says "wherever the PRD states the Top1-only / single-factor deployment policy, align it with the new portfolio-construction decision". If the PRD doesn't state it, I can add a reference to ADR-0004 in the deployment section (S5/FR5.3) noting portfolio construction follows ADR-0004. That's an additive change, safe.

Let me grep the PRD for patterns:
- `docs/0` — line 61: "见 docs/05" in non-goals
- `doc 03` — line 95: "vendor 策略见 doc 03"
- M0 milestone line 145: "docs/05 迁移清单"
- Line 4: "D:\Projects\tradingview-quant-research\research.md", "D:\Projects\quant-crypto\00-系统总体方案.md"
- Line 16: "D:\Projects\quant-crypto" in the table

Let me grep to be thorough.

Now the current doc names: docs/alphamill-architecture.md etc. From docs/README.md:
- alphamill-prd.md
- alphamill-architecture.md
- alphamill-research-factor-mining.md
- alphamill-integration.md
- decisions/0001-factor-mining-engine.md
- decisions/0002-external-dependency-policy.md
- decisions/0003-validation-gate-non-degradation.md
- features/0.1/F001-quant-crypto-migration/migration-plan.md

Mapping:
- "docs/05" (migration checklist) → docs/features/0.1/F001-quant-crypto-migration/migration-plan.md
- "doc 03" (vendor 策略) → docs/decisions/0001-factor-mining-engine.md (ADR-0001 is the vendor strategy decision)
- "docs/02-系统架构" → docs/alphamill-architecture.md (not present in PRD? need to grep)

Let me grep the PRD for all these patterns.

Also D024: header line 4: 前置文档 references. Replace with project names: "tradingview-quant-research 项目的 research.md（TradingView 调研）"、"quant-crypto 项目的 00-系统总体方案.md（上一代系统）". Also line 16 table cell "D:\Projects\quant-crypto" → "quant-crypto（已归档）". Hmm, D024 says "PRD header references D:\Projects\..." — the header specifically. But to be safe, I'll fix the header ones (line 4) and also line 16 which is in the background table. The task says "PRD header references D:\Projects\... — replace with repo-relative or descriptive references (project name only, no drive letter)". I'll replace all D:\Projects\ occurrences in the PRD with descriptive references. Let me grep for `D:\` in the PRD.

Also frontmatter `updated:` — wait, the PRD doesn't have YAML frontmatter, it has a header line "> 版本：v0.1 | 日期：2026-09-06 | 状态：草案". The instruction says "Update frontmatter `updated:` to 2026-09-07." Hmm. The PRD has no YAML frontmatter. docs/README.md has frontmatter with `updated:`. But my file ownership is only docs/alphamill-prd.md. So I should update the PRD's header date line: "日期：2026-09-06" → "日期：2026-09-07". Maybe add `updated: 2026-09-07` as YAML frontmatter? The PRD currently starts with `# AlphaMill — 产品需求文档（PRD）` — no frontmatter. The instruction likely means "update the date to 2026-09-07". I'll change the 日期 in the header line to 2026-09-07. That matches "Update frontmatter `updated:` to 2026-09-07" in spirit — since there is no YAML frontmatter, the 日期 field is the equivalent. Actually, to be safe and satisfy possible validator checks... let me check the validator to see if it checks frontmatter of PRD. Let me read tools/validate_spec_lifecycle.py quickly. It probably only validates features spec. I'll grep quickly.

Now let me draft the changes:

### Change 1: Header (D024 + date)

```
> 版本：v0.1 | 日期：2026-09-07 | 状态：草案
> 前置文档：tradingview-quant-research 仓库的 `research.md`（TradingView 调研）、quant-crypto 仓库的 `00-系统总体方案.md`（上一代系统）
```

### Change 2: line 16 table — `D:\Projects\quant-crypto` → `quant-crypto（已归档）`. Actually the column is "位置". Change to "quant-crypto 仓库（已清算迁移并入本仓）". Hmm — but at the time of PRD writing, migration hasn't happened yet (M0 pending). The PRD says asset liquidation migration planned. The 位置 column: "D:\Projects\quant-crypto". Replace with "quant-crypto 仓库（待 M0 清算迁移入本仓）". Keep it simple: `quant-crypto 仓库（将随 M0 迁入本仓）`.

### Change 3: line 38 mentions [F001 migration-plan](features/0.1/F001-quant-crypto-migration/migration-plan.md) — that's fine (relative link).

### Change 4: Non-goals line 61: "见 docs/05" → "见 [F001 migration-plan](features/0.1/F001-quant-crypto-migration/migration-plan.md)" or "docs/features/0.1/F001-quant-crypto-migration/migration-plan.md".

### Change 5: FR2.1 line 95: "vendor 策略见 doc 03" → "vendor 策略见 docs/decisions/0001-factor-mining-engine.md" (ADR-0001).

### D002 changes:

a) FR2.2 统一评测台 — add cost tier as hard filter in verdict. Current FR2.2:

```
- FR2.2 **统一评测台**：由 `kronos_rankic_eval.py` / `kronos_ic_decay_eval.py` 泛化而来——输入任意因子信号序列，输出 RankIC、IC 衰减曲线、分市场状态表现、分位数分组收益。评测台与生成器完全解耦。
```

Add sub-item FR2.5 (per instructions: "if a sub-item is added use the existing numbering pattern like FR2.5"). Wait — the instruction says amend within existing FRs; add sub-items with existing numbering pattern like FR2.5. FR2 currently has FR2.1-FR2.4. So new sub-item = FR2.5.

Actually, let me structure:

- Amend FR2.2: verdict output includes cost-tier hard filter: "评测 verdict 除 IC 外必须包含成本硬过滤（taker 费 + 滑点成本后为负 → 不得判 promising）".
- Add FR2.5 成本模型 (first-class): funding rate as first-class cost component — perp 8h settlement, crowded-direction funding double-digit annualized. Cost model = taker/maker fee + slippage + funding.
- Amend FR2.1: generator/reward — RL reward includes cost penalty term / pre-screen cost sanity so loop doesn't optimize IC divorced from survivability.

Wait, the reward is in the mining loop (FR2.1 生成器 is AlphaGen RL mining). Add to FR2.1: "挖掘奖励不得只含 RankIC：必须叠加成本惩罚项（或评测前置的成本健全性预筛），避免 RL 在 IC 上过拟合而候选在成本后全灭。"

Where to put funding rate? FR2.5 as cost model. Also update FR3.4 (cost sensitivity) to mention funding? FR3.4 says "taker/maker/零成本三档回测". The instruction says "Cost model: add funding rate as a first-class cost component". I'll create FR2.5 with the full cost model including funding, and reference it from FR3.4 and the eval bench.

Also non-functional requirements table line 134: "成本现实 | 默认按 taker 0.05% + 滑点建模；maker-only 策略显式声明" → add funding: "默认按 taker 0.05% + 滑点 + 资金费率建模（见 FR2.5）". This strengthens D002 fix coherence.

b) Also scenario S2 统一评测 mentions "因子 → RankIC / IC 衰减 / 分市场状态 / 分位数收益 → 存活者进回测与留出" — could add 成本硬过滤. Yes, update S2 to include cost filter: "因子 → RankIC / IC 衰减 / 分市场状态 / 分位数收益 / 成本硬过滤 → 存活者进回测与留出".

### D004 changes: FR2.4 amend:

Current:
```
- FR2.4 多重检验控制：候选通过数随时间累积时，显著性阈值需要校正（deflated significance / 白噪声基准对照）。
```

New:
```
- FR2.4 多重检验控制：候选通过数随时间累积时，显著性阈值需要校正（deflated significance / 白噪声基准对照）。**"一次试验"的计数口径**：每一条进入评测台的表达式（含被拒者）计 1 次试验——RL 每周产出数千条高相关表达式，试验总数（而非存活数）是 deflated significance 的分母。注意：候选共享数据、奖励与协同池，有效独立假设数远低于名义试验数（按第 1 轮检视分析约 5~10 个/周）；折减必须基于全部被评估表达式计数，不得用存活者计数替代。
```

### D007 changes: FR1.3 and M1 milestone.

FR1.3 current:
```
- FR1.3 宇宙扩容：复用 `discover_okx_swap_universe.py`，从 6 对扩到 30~50 对，质量标记流程沿用。
```

Add: backfill explicit workstream. Maybe amend FR1.3: "…质量标记流程沿用。**历史回填是显式工作流**：30~50 对需新增约 4600 万行 1m 数据（现有 631 万行），按 OKX 限速需 1~2 周 wall-clock，作为独立后台任务与开发工作并行推进，不阻塞 FR1 其余交付，但阻塞挖掘 reward 质量与评测台统计功效（见 M1）。"

Hmm wait — 46M rows. Review says ~4600 万行. The task says ~46M new 1m rows. Good.

M1 milestone current:
```
| **M1 数据桥 + 统一评测台** | FR1 全部 + FR2.2/2.3（kronos 评测器泛化） | 任意 feather 信号 → 一条命令出 RankIC/衰减/分状态报告；Kronos 现有缓存全部重新入库 | 1 周 |
```

Fix: "FR1 全部" → clarify FR1 开发交付全含但历史回填单独计。New:

```
| **M1 数据桥 + 统一评测台** | FR1 开发交付 + FR2.2/2.3（kronos 评测器泛化）；FR1.3 历史回填作为独立并行工作流（归属：数据桥负责人/项目所有者，1~2 周 wall-clock，不占用开发排期） | 任意 feather 信号 → 一条命令出 RankIC/衰减/分状态/成本硬过滤报告；Kronos 现有缓存全部重新入库；回填完成前评测台可先跑 6 对 | 1 周（开发）+ 1~2 周（回填并行） |
```

Owner line: "explicit owner line" — the project owner is Georg (single person). Owner: 项目所有者（Georg）or just "项目所有者". Since PRD doesn't name people except implicitly... ADR-0003 says 决策人：Georg. I'll write "归属：项目所有者". Keep it generic: "归属人：项目所有者". Hmm, single-person project — owner is the project owner. Write "归属：项目所有者（唯一开发人）" — simpler: "归属：项目所有者". OK.

### D015: FR3.4:

Current: "- FR3.4 成本敏感性：taker/maker/零成本三档回测，成本后收益为主要指标。"

New: "- FR3.4 成本敏感性：taker/maker/零成本三档回测，成本后收益为主要指标。成本参数（费率/滑点/资金费率）必须以 quant-crypto dry-run 实际成交记录（现有资产）校准，不得直接采用交易所牌价。"

### D018: FR6.1:

Current: "- FR6.1 每个实验写 manifest：数据快照版本、代码 commit、参数、评测结果、结论（PASS/FAIL + 原因）。"

New: add seed + determinism switches: "…结论（PASS/FAIL + 原因）。挖掘类实验的 manifest 必须额外记录随机种子与确定性开关（torch deterministic mode / cudnn deterministic 等），保证 G5 对挖掘步骤可复现。"

### D011: grep for docs/0 and doc 0 patterns. From my read:
- line 61: "见 docs/05" (non-goals)
- line 95: "vendor 策略见 doc 03"
- line 145: "docs/05 迁移清单"

Any "docs/02-系统架构"? Not in PRD it seems. I'll grep to confirm all occurrences including `D:\`.

### ADR-0004 alignment:

Where does PRD state deployment policy? S5: "部署 | 留出通过 → 信号写 feather 缓存 → Freqtrade 策略模板挂载 → dry-run → paper". FR5.3: "部署流水线：留出 PASS → 自动生成策略配置 → dry-run 冒烟 → 人工确认挂载。"

Add reference to ADR-0004. E.g., in S5: "留出通过 → 信号写 feather 缓存 → 组合构建（协同池组合可作为 meta-factor 部署、Top-K 组合替代 Top1-only，见 docs/decisions/0004-portfolio-construction.md）→ Freqtrade 策略模板挂载 → dry-run → paper". And FR5.3: add "组合构建与部署映射遵循 docs/decisions/0004-portfolio-construction.md（ADR-0004：协同池组合作为 meta-factor、Top-K 组合替代 Top1-only）".

Also maybe G-goal or risk table? The risk table line 159: "信号仍过不了成本墙 | 成本三档敏感性为一级指标；maker-only/微择时 overlay 方向优先实验" — could update to include funding and hard filter, strengthening D002. Let me update: "成本三档敏感性为一级指标；成本硬过滤前置于评测台 verdict（FR2.2/FR2.5）；maker-only/微择时 overlay 方向优先实验". That's an addition/tightening, fine.

Also line 161 (risk): "评测台自动分诊：RankIC + 相关性查重先行过滤" → "评测台自动分诊：RankIC + 成本硬过滤 + 相关性查重先行过滤". Good.

Also G1? "≥ 100 个因子候选/周 进入统一评测台" — no change needed. G2 — gate criteria, don't touch (frozen). G5 — manifest; FR6.1 fix covers it.

Now, one consideration: the task says "amend within existing FRs; if a sub-item is added use the existing numbering pattern like FR2.5". So FR2.5 is the suggested new sub-item for cost model. I'll do exactly that.

Also make sure not to break the validator. Let me check validate_spec_lifecycle.py to see if it parses the PRD (e.g., checks FR numbering or links). Let me read it quickly.

Also need to check: does verify.py check markdown links existence in PRD? Review D011 says "verify 可加相对链接存在性检查防复发" — suggested, not implemented. But I'm adding links to docs/decisions/0004-portfolio-construction.md which may not exist yet ("file will exist by end of day"). If a link-existence check existed, that could fail. Let me check the tools quickly before finalizing the link format. If there's a link check, I'd write the reference as plain text (backticks) rather than a markdown link. Actually, safer: use backtick plain text reference `docs/decisions/0004-portfolio-construction.md` — the task explicitly says reference it as that path. Plain text avoids link-check failures. But if the file will exist by end of day and validator runs now... plain text is safest. Hmm, but markdown-style links look better. Let me check verify.py first.

Let me now do the greps and read the validator.

  <details><summary>tool output</summary>

  ```text
Found 5 match(es) in 1 file(s)

D:\Projects\alphamill\docs\alphamill-prd.md
  4: > 前置文档：`D:\Projects\tradingview-quant-research\research.md`（TradingView 调研）、`D:\Projects\quant-crypto\00-系统总体方案.md`（上一代系统）
  16: | TimescaleDB 数据湖 | ✅ 631 万行 1m OHLCV（6 个 OKX 永续对，2 年回补）+ 质量标记表 + 多周期连续聚合 | `D:\Projects\quant-crypto` |
  61: - ❌ 不重建数据管道/数据湖（quant-crypto 数据资产整体迁入，见 docs/05）
  95: - FR2.1 **生成器**：至少两种可插拔后端——程序化（**AlphaGen RL 挖掘为主**，vendor 策略见 doc 03；GP/表达式枚举对照）与人工/LLM 辅助（论文因子、假设清单）。生成器只负责产出**因子定义**，不做评测。
  145: | **M0 资产清算迁移** | docs/05 迁移清单：数据卷 + 采集器 + Kronos 上游化 + 风控/监控搬迁 | verify 全绿：行数对账 / Kronos /health / Freqtrade dry-run / 监控有数据 | 2-3 天 |
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\tools\validate_spec_lifecycle.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """规格生命周期校验（骨架版，node flavor 的 check-feature-gates.mjs 的 Python 对应）。
3: 
4: 校验 docs/features/<version>/Fddd-*/ 三件套：
5:   - 三件套齐全、frontmatter 合法、ID 唯一、status/gate_version 合法
6:   - spec.md 是状态唯一真相源（design/tasks 不得声明独立 status）
7:   - gate v1：固定章节结构、Q/DQ 关闭、AC 引用第 4 节真实需求、
8:     review/done 的 tests 路径真实存在
9:   - BACKLOG.md 与所有非 done Feature 双向集合一致
10: 
11: 纯函数 + CLI 分离，只用标准库；参考项目在此基础上抽了共享 spec_validation 模块
12: 并补了变异测试。用法：python tools/validate_spec_lifecycle.py
13: 退出码 0 = 全部通过；1 = 存在违规。
14: """
15: 
16: from __future__ import annotations
17: 
18: import pathlib
19: import re
20: import sys
21: 
22: ROOT = pathlib.Path(__file__).resolve().parent.parent
23: ALLOWED_STATU
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:45:54Z

- **tool**: `grep({"output_mode": "content", "path": "D:\\Projects\\alphamill\\tools\\verify.py", "pattern": "link|\\.md|href|\\]\\("})`


> [reasoning] The validator doesn't touch the PRD at all — only features specs and BACKLOG. Safe.

Now apply edits to docs/alphamill-prd.md. The PRD has no YAML frontmatter; the date lives in the header line "> 版本：v0.1 | 日期：2026-09-06". I'll update that to 2026-09-07 (that's the "updated" equivalent for this file).

Edits:

1. Header (D024 + date):
```
> 版本：v0.1 | 日期：2026-09-07 | 状态：草案
> 前置文档：tradingview-quant-research 仓库的 `research.md`（TradingView 调研）、quant-crypto 仓库的 `00-系统总体方案.md`（上一代系统，均已归档）
```
Hmm, "均已归档" — tradingview-quant-research isn't archived; only quant-crypto is. Keep simple:
`> 前置文档：tradingview-quant-research 仓库的 research.md（TradingView 调研）、quant-crypto 仓库的 00-系统总体方案.md（上一代系统）`

2. Line 16: `D:\Projects\quant-crypto` → `quant-crypto 仓库（待 M0 清算迁入本仓）`

3. Non-goals line 61: "见 docs/05" → "见 [F001 migration-plan](features/0.1/F001-quant-crypto-migration/migration-plan.md)"

4. FR2.1: "vendor 策略见 doc 03" → "vendor 策略见 docs/decisions/0001-factor-mining-engine.md"。 Plus add cost penalty to reward:
```
- FR2.1 **生成器**：至少两种可插拔后端——程序化（**AlphaGen RL 挖掘为主**，vendor 策略见 [ADR-0001](decisions/0001-factor-mining-engine.md)；GP/表达式枚举对照）与人工/LLM 辅助（论文因子、假设清单）。生成器只负责产出**因子定义**，不做评测。RL 挖掘的奖励不得只含 RankIC：必须叠加成本惩罚项（FR2.5 成本模型）或评测前置的成本健全性预筛（成本后收益为负的候选不得进入存活名单），防止挖掘回路在 IC 上优化而产出死于成本墙的候选。
```

5. FR2.2: add cost hard filter to verdict:
```
- FR2.2 **统一评测台**：由 `kronos_rankic_eval.py` / `kronos_ic_decay_eval.py` 泛化而来——输入任意因子信号序列，输出 RankIC、IC 衰减曲线、分市场状态表现、分位数分组收益。评测台与生成器完全解耦。评测 verdict 必须包含成本档硬过滤：在 taker 费 + 滑点成本后收益为负的候选不得判 `promising`（IC 为正但成本后为负 → dead），不得只按 IC 定 promising/weak/dead。
```

6. Add FR2.5 cost model:
```
- FR2.5 **成本模型（一等公民）**：成本 = 交易费（taker/maker）+ 滑点 + **资金费率**。资金费率为永续合约核心持有成本（每 8 小时结算，拥挤方向的年化可达两位数），持有类信号必须计入；成本参数口径见 FR3.4 校准条款。
```

7. FR2.4 trial counting:
```
- FR2.4 多重检验控制：候选通过数随时间累积时，显著性阈值需要校正（deflated significance / 白噪声基准对照）。**"一次试验"口径**：每条进入评测台的表达式（含被拒者）计 1 次试验；RL 每周产出数千条高相关表达式，试验总数（而非存活数）是 deflated significance 的分母。同时注意：候选间共享数据、奖励与协同池，有效独立假设数远低于名义试验数（第 1 轮检视分析约 5~10 个/周）——折减必须基于全部被评估表达式计数，不得用存活者计数替代。
```

8. FR3.4 calibration:
```
- FR3.4 成本敏感性：taker/maker/零成本三档回测，成本后收益为主要指标。成本参数（费率/滑点/资金费率）必须以 quant-crypto dry-run 的实际成交记录（现有资产）校准，不得直接采用交易所牌价。
```

9. FR5.3 + S5 ADR-0004 alignment:
S5: `| S5 | 部署 | 留出通过 → 信号写 feather 缓存 → 组合构建（协同池组合作为 meta-factor、Top-K 组合替代 Top1-only，见 docs/decisions/0004-portfolio-construction.md）→ Freqtrade 策略模板挂载 → dry-run → paper |`

FR5.3: `- FR5.3 部署流水线：留出 PASS → 自动生成策略配置 → dry-run 冒烟 → 人工确认挂载。单因子 Top1-only 部署政策由 ADR-0004（docs/decisions/0004-portfolio-construction.md）取代：协同池组合可作为 meta-factor 部署，部署形态为 Top-K 组合。`

Wait — does the PRD state Top1-only anywhere? Grep found no "Top1" in PRD. So the PRD doesn't state it; but to align, I add the ADR-0004 reference in the deployment sections. That's additive and safe. I'll add to S5 and FR5.3.

10. FR6.1 manifest:
```
- FR6.1 每个实验写 manifest：数据快照版本、代码 commit、参数、评测结果、结论（PASS/FAIL + 原因）。挖掘类实验的 manifest 必须额外记录随机种子与确定性开关（torch deterministic mode / cudnn deterministic 等），否则 G5 的全链路复现对挖掘步骤不成立。
```

11. M0 milestone line 145: "docs/05 迁移清单" → "F001 migration-plan 迁移清单"

12. M1 milestone:
```
| **M1 数据桥 + 统一评测台** | FR1 开发交付（FR1.3 历史回填单列为并行工作流，不并入 FR1 开发排期）+ FR2.2/2.3（kronos 评测器泛化） | 任意 feather 信号 → 一条命令出 RankIC/衰减/分状态/成本硬过滤报告；Kronos 现有缓存全部重新入库；**回填工作流**：归属=项目所有者，30~50 对约新增 4600 万行 1m 数据（现有 631 万行），OKX 限速下 1~2 周 wall-clock，与开发并行、不阻塞 FR1 其余交付，但回填完成前挖掘 reward 与评测台功效受限 | 1 周（开发）+ 1~2 周（回填，并行） |
```

Hmm, the出口标准 column is getting long. Maybe better: put backfill detail in FR1.3 and keep M1 mention brief. Let me restructure:

FR1.3:
```
- FR1.3 宇宙扩容：复用 `discover_okx_swap_universe.py`，从 6 对扩到 30~50 对，质量标记流程沿用。**历史回填为显式工作流**（不隐藏在 FR1 开发内）：30~50 对需新增约 4600 万行 1m 数据（现有 631 万行），OKX 限速下预估 1~2 周 wall-clock；归属：项目所有者；与开发工作并行推进，不阻塞 FR1 其余交付，但未完成前挖掘横截面 reward 噪声与评测台统计功效受限。
```

M1:
```
| **M1 数据桥 + 统一评测台** | FR1 开发交付 + FR2.2/2.3（kronos 评测器泛化）；FR1.3 历史回填（约 4600 万行，1~2 周 wall-clock）作为独立并行工作流，归属：项目所有者，不计入开发排期 | 任意 feather 信号 → 一条命令出 RankIC/衰减/分状态/成本硬过滤报告；Kronos 现有缓存全部重新入库 | 1 周（开发）+ 1~2 周（回填并行） |
```

13. Non-functional 成本现实 row: "默认按 taker 0.05% + 滑点建模" → "默认按 taker 0.05% + 滑点 + 资金费率建模（FR2.5）；参数以 dry-run 实测成交校准（FR3.4）；maker-only 策略显式声明"

14. Risk table updates:
- "信号仍过不了成本墙" row: "成本三档敏感性为一级指标" → "成本三档敏感性为一级指标；成本硬过滤前置于评测台 verdict（FR2.2），资金费率入模（FR2.5）；maker-only/微择时 overlay 方向优先实验"
- 人审瓶颈 row: "RankIC + 相关性查重先行过滤" → "RankIC + 成本硬过滤 + 相关性查重先行过滤"

Also, should I update S2 scenario? "因子 → RankIC / IC 衰减 / 分市场状态 / 分位数收益 → 存活者进回测与留出" → add 成本硬过滤. Yes: "因子 → RankIC / IC 衰减 / 分市场状态 / 分位数收益 / 成本硬过滤（taker+滑点，FR2.2）→ 存活者进回测与留出".

Now regarding links: verify.py — does it check markdown link existence? Review says "verify 可加相对链接存在性检查防复发" as a *suggestion*, implying it doesn't exist yet. Let me check tools/verify.py quickly to be safe before using markdown links to 0004 which doesn't exist yet. Actually the task says the file "will exist by end of day; referencing it is correct even if you can't read it yet". To be safe I'll reference it as inline code path text (backticks) rather than markdown links — that avoids any link-existence checker failing now. But ADR-0001 exists, so a real link there is fine. Let me check verify.py for link checks first.

Let me look at tools/verify.py.
Validator only checks `features/` specs + BACKLOG — PRD is out of its scope. Now checking whether `verify.py` does link-existence checks (I'll reference ADR-0004 which may not exist yet):

  <details><summary>tool output</summary>

  ```text
No matches found
  ```
  </details>

## assistant · 2026-09-06T16:46:53Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "> 版本：v0.1 | 日期：2026-09-07 | 状态：草案\n> 前置文档：tradingview-quant-research 仓库的 `research.md`（TradingView 调研）、quant-crypto 仓库的 `00-系统总体方案.md`（上一代系统）", "oldString": "> 版本：v0.1 | 日期：2026-09-06 | 状态：草案\n> 前置文档：`D:\\Projects\\tradingview-quant-research\\research.md`（TradingView 调研）、`D:\\Projects\\quant-crypto\\00-系统总体方案.md`（上一代系统）"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "| TimescaleDB 数据湖 | ✅ 631 万行 1m OHLCV（6 个 OKX 永续对，2 年回补）+ 质量标记表 + 多周期连续聚合 | quant-crypto 仓库（待 M0 清算迁入本仓） |", "oldString": "| TimescaleDB 数据湖 | ✅ 631 万行 1m OHLCV（6 个 OKX 永续对，2 年回补）+ 质量标记表 + 多周期连续聚合 | `D:\\Projects\\quant-crypto` |"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "- ❌ 不重建数据管道/数据湖（quant-crypto 数据资产整体迁入，见 [F001 migration-plan](features/0.1/F001-quant-crypto-migration/migration-plan.md)）", "oldString": "- ❌ 不重建数据管道/数据湖（quant-crypto 数据资产整体迁入，见 docs/05）"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "| **M0 资产清算迁移** | [F001 migration-plan](features/0.1/F001-quant-crypto-migration/migration-plan.md) 迁移清单：数据卷 + 采集器 + Kronos 上游化 + 风控/监控搬迁 | verify 全绿：行数对账 / Kronos /health / Freqtrade dry-run / 监控有数据 | 2-3 天 |", "oldString": "| **M0 资产清算迁移** | docs/05 迁移清单：数据卷 + 采集器 + Kronos 上游化 + 风控/监控搬迁 | verify 全绿：行数对账 / Kronos /health / Freqtrade dry-run / 监控有数据 | 2-3 天 |"})`


> [reasoning] No link checks in verify.py. Still, I'll use a mix: real links for existing docs (ADR-0001, migration-plan), and for ADR-0004 I'll use inline-code path text to be safe (per task instruction "reference it as `docs/decisions/0004-portfolio-construction.md`"). Actually the task literally writes it in backticks — inline code is fine and matches.

Now apply all edits.
No link checks — safe. Applying all edits to `docs/alphamill-prd.md` now (step 1 of 4: header/refs D024+D011+date):

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:47:24Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "- FR2.1 **生成器**：至少两种可插拔后端——程序化（**AlphaGen RL 挖掘为主**，vendor 策略见 [ADR-0001](decisions/0001-factor-mining-engine.md)；GP/表达式枚举对照）与人工/LLM 辅助（论文因子、假设清单）。生成器只负责产出**因子定义**，不做评测。RL 奖励不得只含 RankIC：必须叠加成本惩罚项（按 FR2.5 成本模型）或评测前置的成本健全性预筛（成本后收益为负者不得进入存活名单），防止挖掘回路优化 IC 却批量产出死于成本墙的候选（quant-crypto 的死因不得被 ×20 吞吐量放大）。\n- FR2.2 **统一评测台**：由 `kronos_rankic_eval.py` / `kronos_ic_decay_eval.py` 泛化而来——输入任意因子信号序列，输出 RankIC、IC 衰减曲线、分市场状态表现、分位数分组收益
…[truncated])`


> [reasoning] Step 2 of 4: FR2 area (D002: FR2.1 cost penalty, FR2.2 hard filter, FR2.5 cost model w/ funding; D004: FR2.4 trial counting).
Step 2 of 4: FR2 area (D002 + D004):

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:47:56Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "- FR1.3 宇宙扩容：复用 `discover_okx_swap_universe.py`，从 6 对扩到 30~50 对，质量标记流程沿用。**历史回填为显式工作流**（不隐藏在 FR1 开发内）：30~50 对需新增约 4600 万行 1m 数据（现有 631 万行），OKX 限速下预估 1~2 周 wall-clock；归属：项目所有者；与开发并行推进、不阻塞 FR1 其余交付，但回填完成前挖掘横截面 reward 噪声与评测台统计功效受限。", "oldString": "- FR1.3 宇宙扩容：复用 `discover_okx_swap_universe.py`，从 6 对扩到 30~50 对，质量标记流程沿用。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "- FR3.4 成本敏感性：taker/maker/零成本三档回测，成本后收益为主要指标。成本参数（费率/滑点/资金费率）必须以 quant-crypto dry-run 的实际成交记录（现有资产）校准，不得直接采用交易所牌价。", "oldString": "- FR3.4 成本敏感性：taker/maker/零成本三档回测，成本后收益为主要指标。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "- FR5.3 部署流水线：留出 PASS → 自动生成策略配置 → dry-run 冒烟 → 人工确认挂载。部署形态遵循 [ADR-0004](decisions/0004-portfolio-construction.md)：协同池组合可作为 meta-factor 部署，Top-K 组合替代单因子 Top1-only。", "oldString": "- FR5.3 部署流水线：留出 PASS → 自动生成策略配置 → dry-run 冒烟 → 人工确认挂载。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "| S5 | 部署 | 留出通过 → 信号写 feather 缓存 → 组合构建（协同池组合作为 meta-factor、Top-K 替代 Top1-only，见 `docs/decisions/0004-portfolio-construction.md`）→ Freqtrade 策略模板挂载 → dry-run → paper |", "oldString": "| S5 | 部署 | 留出通过 → 信号写 feather 缓存 → Freqtrade 策略模板挂载 → dry-run → paper |"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "- FR6.1 每个实验写 manifest：数据快照版本、代码 commit、参数、评测结果、结论（PASS/FAIL + 原因）。挖掘类实验的 manifest 必须额外记录随机种子与确定性开关（torch deterministic mode / cudnn deterministic 等）——否则 G5 的全链路复现对挖掘步骤不成立。", "oldString": "- FR6.1 每个实验写 manifest：数据快照版本、代码 commit、参数、评测结果、结论（PASS/FAIL + 原因）。"})`


> [reasoning] Step 3 of 4: FR1.3 backfill (D007), FR3.4 calibration (D015), FR5.3/S5 ADR-0004, FR6.1 manifest (D018).
Step 3 of 4: FR1.3 (D007), FR3.4 (D015), FR5.3/S5 (ADR-0004), FR6.1 (D018):

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:48:28Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "| **M1 数据桥 + 统一评测台** | FR1 开发交付 + FR2.2/2.3（kronos 评测器泛化）；FR1.3 历史回填（约 4600 万行 1m 数据，1~2 周 wall-clock）为独立并行工作流，归属：项目所有者，不计入开发排期，FR1 不声称包含全部回填 | 任意 feather 信号 → 一条命令出 RankIC/衰减/分状态/成本硬过滤报告；Kronos 现有缓存全部重新入库；回填完成前评测台先跑 6 对 | 1 周（开发）+ 1~2 周（回填，并行） |", "oldString": "| **M1 数据桥 + 统一评测台** | FR1 全部 + FR2.2/2.3（kronos 评测器泛化） | 任意 feather 信号 → 一条命令出 RankIC/衰减/分状态报告；Kronos 现有缓存全部重新入库 | 1 周 |"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "| S2 | 统一评测 | 因子 → RankIC / IC 衰减 / 分市场状态 / 分位数收益 / 成本硬过滤（taker+滑点，FR2.2）→ 存活者进回测与留出 |", "oldString": "| S2 | 统一评测 | 因子 → RankIC / IC 衰减 / 分市场状态 / 分位数收益 → 存活者进回测与留出 |"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "| 成本现实 | 默认按 taker 0.05% + 滑点 + 资金费率建模（FR2.5）；参数以 dry-run 实测成交校准（FR3.4）；maker-only 策略显式声明 |", "oldString": "| 成本现实 | 默认按 taker 0.05% + 滑点建模；maker-only 策略显式声明 |"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "| 信号仍过不了成本墙 | 成本三档敏感性为一级指标；成本硬过滤前置于评测台 verdict（FR2.2），资金费率入模（FR2.5）；maker-only/微择时 overlay 方向优先实验 |", "oldString": "| 信号仍过不了成本墙 | 成本三档敏感性为一级指标；maker-only/微择时 overlay 方向优先实验 |"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "newString": "| 吞吐量上来后人审瓶颈 | 评测台自动分诊：RankIC + 成本硬过滤 + 相关性查重先行过滤，人只看存活者 |", "oldString": "| 吞吐量上来后人审瓶颈 | 评测台自动分诊：RankIC + 相关性查重先行过滤，人只看存活者 |"})`


> [reasoning] Step 4 of 4: M1 milestone (D007 wording), S2 scenario, non-functional cost row, risk table rows. Then validate.
Step 4 of 4: M1 milestone wording (D007), S2, non-functional cost row, risk table:

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:48:57Z

- **tool**: `bash({"command": "python tools/validate_spec_lifecycle.py", "workdir": "D:\\Projects\\alphamill"})`
- **tool**: `grep({"output_mode": "content", "path": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "pattern": "docs/05|doc 03|docs/02|D:\\\\"})`


> [reasoning] Now validate: run the validator + grep for leftover stale patterns (docs/0, doc 0, D:\) in the PRD.
Validation — run validator + confirm no stale patterns remain in my file:

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No matches found
  ```
  </details>

## assistant · 2026-09-06T16:49:15Z


> [reasoning] All done:
- D002: FR2.1 reward cost penalty, FR2.2 hard filter, FR2.5 funding rate cost model, S2, NFR row, risk rows.
- D004: FR2.4 trial counting defined.
- D007: FR1.3 explicit backfill workstream + M1 milestone wording.
- D015: FR3.4 dry-run calibration clause.
- D018: FR6.1 seed + determinism switches.
- D011: docs/05 ×2 → migration-plan links, doc 03 → ADR-0001 link.
- D024: D:\ paths removed (header + table).
- ADR-0004 referenced in S5 + FR5.3.
- Date updated to 2026-09-07.
- Validator green. No stale patterns.

Constraints check: no FR/goal renumbering (FR2.5 follows existing pattern; G1-G5 untouched; ADR-0003 criteria untouched — only added cost protections which ADR-0003 §4 already gestures at). No other files touched. Not committing.

Report concisely per ADHD-style: what changed, validation status, next action.
All 7 issues fixed in `docs/alphamill-prd.md` — validator green (`validate_spec_lifecycle: 全部通过`), no other files touched, nothing committed.

Changes by issue:
1. **D002**: FR2.1 reward now requires cost penalty/pre-screen; FR2.2 verdict adds cost-tier **hard filter** (IC positive + cost-negative → `dead`, not `promising`); new **FR2.5** cost model with funding rate as first-class component (perp 8h settlement, double-digit annualized in crowded directions); S2, 非功能成本行、风险表同步。ADR-0003 gate criteria untouched — only additions.
2. **D004**: FR2.4 defines "one trial" = every evaluated expression incl. rejected ones; raw count is the deflated-significance denominator; notes effective independent hypotheses ~5-10/week and forbids substituting survivor counts.
3. **D007**: FR1.3 backfill is now an explicit workstream (~46M new 1m rows, 1-2 weeks wall-clock, owner line: 项目所有者， runs parallel); M1 wording no longer claims FR1 includes full backfill, estimate split “1 周（开发）+ 1~2 周（回填，并行）”.
4. **D015**: FR3.4 — cost parameters must be calibrated from quant-crypto dry-run actual fill records, not sticker prices.
5. **D018**: FR6.1 manifest schema adds random seed + determinism switches (torch/cudnn deterministic) for mining runs, tied to G5.
6. **D011**: `docs/05` ×2 → F001 migration-plan links; `doc 03` → ADR-0001 link; zero stale patterns remain (grep-verified).
7. **D024**: both `D:\Projects\...` references (header + asset table) replaced with repo-relative/project-name descriptions.
8. **ADR-0004**: deployment policy (synergy pool as meta-factors, Top-K replacing Top1-only) referenced in S5 and FR5.3 as `docs/decisions/0004-portfolio-construction.md`.
9. Date updated to 2026-09-07; G1-G5, FR1-FR6 numbering, non-goals all intact.

Next action: rerun `python tools/validate_spec_lifecycle.py` after the parallel ADR-0004 lands to confirm nothing drifted.
