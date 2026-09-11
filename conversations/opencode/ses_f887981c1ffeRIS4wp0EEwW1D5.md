---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f887981c1ffeRIS4wp0EEwW1D5"
title: "Oracle 深度评估 alphamill 项目 (@oracle subagent)"
project: "D:/Projects/alphamill"
model: "glm-5.3-flash"
created_at: "2026-09-06T16:21:37Z"
updated_at: "2026-09-06T16:26:11Z"
tokens_input: 29045
tokens_output: 2032
cost: 0.0
parent_id: "ses_f887c8e5cffeXNR2u34Pzo7U7H"
---

# Oracle 深度评估 alphamill 项目 (@oracle subagent)

## user · 2026-09-06T16:21:38Z

You are reviewing a brand-new quantitative trading research project for strategic/architectural soundness. Read-only consultation — produce a critical analysis, not code.

[CONTEXT]: Project "AlphaMill" (D:\Projects\alphamill), created 2026-09-06, solo developer (Georg), Windows 11 single machine + RTX 4060 Laptop GPU. Successor to "quant-crypto" which spent 5 weeks building infra (6.3M rows 1m OHLCV TimescaleDB, Kronos signal service RankIC>0.05, Freqtrade dry-run, risk trio, Grafana monitoring) but ALL candidates died at the final 90-day holdout gate (`blocked_no_paper_candidate`). Diagnosed root cause: hypothesis throughput ~5/week vs needed 100+/week.

[PROJECT DESIGN — from docs I've read]:
1. PRD goals: G1 factor throughput ×20 (≥100 candidates/week into unified bench); G2 validation non-degradation (90-day holdout, ≥30 trades mandatory); G3 Vibe-Trading integration (second-opinion backtest + agent postmortem); G4 Freqtrade execution inheritance; G5 full reproducibility (manifest per experiment). Non-goals: no infra rebuild, no live trading until holdout pass, OKX USDT perpetuals 30-50 pairs, 1h/4h low frequency only.
2. Milestones: M0 asset migration from quant-crypto (2-3 days) → M1 data bridge (TimescaleDB→Parquet+manifest) + unified evaluation bench (1 week) → M2 AlphaGen vendor mining pipeline (2 weeks: smoke gate 2 days + feather→tensor adapter ~1 week) → M3 Vibe-Trading integration (1 week) → M4 production loop (ongoing, ≥100 candidates/week).
3. Architecture: 3 layers. Data: TimescaleDB (operational) → data_bridge daily export → Parquet lake (immutable snapshots) → DuckDB (query entry). Middle: factor factory (generators: AlphaGen RL main, GP baseline, manual/LLM; AST purity gate; unified bench: RankIC/decay/regime/quantile/dedup/multiple-testing; factor registry with lifecycle) → validation gates (selection → 90d holdout ≥30 trades → no-lookahead audit + cost 3-tier) → Freqtrade execution (signal cache feather, merge_asof). Top: Vibe-Trading (local loader reading Parquet, MC/Bootstrap/Walk-Forward, quantlib, agent postmortem) + Prometheus/Grafana monitoring. Closed loop: mining → bench → second opinion → holdout → signal cache → trading → results → postmortem → new hypotheses.
4. ADR-0001: AlphaGen (RL expression mining, linear synergy pool) as main engine via VENDOR (not install): core frozen 21 months, broken requirements.txt (qlib==0.0.2.dev20 wrong package, numpy 2021), no LICENSE (personal use OK). Plan: vendor core subset (expression/tensor calculator/LinearAlphaPool), discard requirements, modern stack (torch 2.x/numpy 2.x/pandas 2.x/sb3 latest+gymnasium), self-written feather→tensor adapter replacing alphagen_qlib. Smoke gate time-boxed 2 working days; degradation ladder L1 (expression evaluator + own search) / L2 (pure gplearn). Cross-sectional reward noisy on 6-12 pairs → universe expansion to 30-50 pairs must run PARALLEL with integration.
5. ADR-0002: no-fork policy. AlphaGen vendored; Freqtrade official docker image zero source changes; Vibe-Trading pip pin; Kronos upstream clone+pin, self-built thin service shell.
6. ADR-0003: holdout gate never degrades. ≥30 trades else UNDERPOWERED (not PASS/FAIL). No-lookahead: AST purity gate + independent K-line replay audit + signal cache timestamp alignment, three layers. Cost 3-tier standard output. No live trading until holdout pass.
7. F001 (draft): quant-crypto asset liquidation migration — pg_dump/restore, row/checksum reconciliation, collector/risk/monitoring code move, Kronos upstream-ization, verify.ps1 full-chain checks, then archive old repo.
8. Research doc (2026-09): thorough ecosystem survey — AlphaGen main pick (synergy pool mechanism, GPU tensor eval), gplearn baseline (structural leakage: full-sample fitness), Qlib expression engine NOT extractable (maintainer-confirmed issue #1988), purgedcv for CPCV/PSR/DSR, vectorbt OSS for fast pre-screen, py-alpha-lib GTJA191 formula library as seed candidates, FreqAI stays execution-side only.

[MY PRELIMINARY FINDINGS (doc-quality)]:
- 13 stale doc references (docs/05, docs/02, "doc 03" — old numbering scheme) across 6 files, now renamed alphamill-*.md
- SOP.md core principles table has unfilled "<按项目定义>" placeholder rows
- docs/README.md has a duplicated line; features/README.md has a broken sentence fragment
- Code area state (tools/verify.py etc.) being investigated separately

[QUESTIONS — answer each with severity-rated findings (Critical/High/Medium/Low) + reasoning]:
1. STRATEGIC: Is the "throughput ×20 cures the alpha drought" thesis sound? Blind spots? Consider: 100/week of RL-generated factors vs multiple-testing burden (does the deflated significance machinery scale to 5000 candidates/year?); does the linear synergy pool + RankIC reward actually produce factors that survive cost walls (quant-crypto died on cost, not IC); regime non-stationarity in crypto 2026; is the 1-5% honest OOS pass-rate assumption consistent with 100/week throughput producing ~1-5 survivors/week?
2. ROADMAP: Critique M0-M4 sequencing and time estimates. What's underestimated? (e.g., AlphaGen gym→gymnasium + sb3 2.x migration on frozen code; universe expansion 6→30-50 pairs historical backfill duration; Vibe-Trading local loader pair-mapping contract; Windows GPU nightly batch ops.) What's misordered?
3. ARCHITECTURE: Coherence gaps between storage trio / factor lifecycle / gate placement? Is signal-cache→Freqtrade merge_asof pattern sound for multi-factor portfolios? Single factor per strategy template — how do surviving factors combine (linear pool synergy at mining time vs portfolio-level combination)? Is that specified anywhere or is it a hole?
4. PROCESS: SDD feature trio + status machine + verify gates + review-convergence protocol for a SOLO developer — right-sized or bureaucratic overhead? What would you cut?
5. MISSING ENTIRELY: What critical concerns are absent from all docs? Consider: multi-factor portfolio construction (weights, capacity, turnover budget), funding-rate drag modeling for perpetuals, execution cost model realism (taker 0.05% assumption vs 2026 OKX actuals), exchange counterparty/regulatory risk, data snooping via agent postmortem loops feeding mined hypotheses back into same data, GPU contention between Kronos inference and AlphaGen training on a 4060 laptop, disk growth of Parquet lake + 6.3M rows×50 pairs backfill, backup/DR for the lake.
6. TOP-3: If you could only make the project change 3 things before M0 starts, what are they?

[FORMAT]: Structured markdown. Per-question findings with severity. End with TOP-3 list. Be adversarial — find real weaknesses, not nitpicks. Max ~1500 words.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-06T16:21:38Z


> [reasoning] Let me think about this carefully. The user wants a critical architectural review of their quantitative trading research project "AlphaMill". They've given me extensive context from the docs. This is a read-only consultation — no code changes. They want severity-rated findings per question, ~1500 words max, adversarial.

Let me first decide whether I need to read anything. They've provided very rich context. They mention "Code area state (tools/verify.py etc.) being investigated separately" — so I shouldn't go deep into code. The questions are strategic/architectural and mostly answerable from the provided context. I could optionally do a quick look at the docs to verify a couple of claims, but the user explicitly says "from docs I've read" and asks for analysis. Given the 1500-word cap and the depth of questions, I should mostly reason rather than burn time on tool calls. Maybe a quick sanity check of the repo structure to ground myself — but the instructions say exhaust provided context first. The context is exhaustive. I'll answer directly.

Actually, let me reconsider — should I peek at the docs directory to verify a few claims? The user says read-only consultation, produce critical analysis. The questions are strategic. The provided context is detailed enough. Tool calls would add little. I'll answer from context, with hedged language where I'm inferring.

Let me now actually think hard about each question. This is a quant research methodology review. Let me be genuinely adversarial and technically substantive.

**Q1: STRATEGIC — throughput ×20 thesis**

Core thesis: quant-crypto failed because hypothesis throughput was ~5/week. AlphaMill targets ≥100 candidates/week into bench. Is ×20 throughput the cure?

Key issue: throughput of *candidates* is not throughput of *validated alpha*. The bottleneck in quant research is rarely idea generation count — it's the survival rate through cost walls and multiple testing. AlphaGen is an RL system that mines cross-sectional expressions optimized on RankIC. Known issues:

1. **AlphaGen's reward is RankIC, not net-of-cost PnL.** The linear synergy pool selects alphas that jointly explain residual returns — this optimizes IC-space, not strategy-space. quant-crypto died at cost (they said candidates died at final holdout gate). Mining more factors optimized on an objective that doesn't include costs will produce candidates that die at the same wall. The throughput gain multiplies the population of factors that share the same death mode. This is the single biggest blind spot: **you cannot fix a cost-survival problem with an IC-throughput machine.** Mitigation: cost-aware reward shaping or a cost-penalized pre-screen stage inside the bench before the synergy pool admission — i.e., make the bench's cost tier part of the RL fitness signal, not just a downstream gate.

2. **Multiple testing burden.** 100/week × 50 weeks = 5000 candidates/year. Deflated Sharpe Ratio (DSR) machinery: the deflation depends on number of trials N. If the bench tracks ALL trials, N=5000 makes the required Sharpe hurdle climb steeply. If the bench only counts survivors of pre-screening (survivorship within the pipeline), the effective N is understated — that's data snooping via pipeline structure. Key question: does the multiple-testing counter count candidates entering the bench or every expression the RL miner generated? AlphaGen generates tens of thousands of expressions per run. If N counts 5000 but the true N is 50,000+, DSR is still too lenient. Severity: High. Recommendation: count every expression evaluated as a trial (or at minimum, per-generation population), and report deflated metrics accordingly. Also, selection of the holdout *window* itself becomes a multiple-testing dimension if run repeatedly.

3. **1-5% OOS pass rate math check.** 100/week × 1-5% = 1-5 survivors/week. But: pass rate is not independent of throughput. With RL mining, candidates within a week are highly correlated (same data, same reward, same synergy pool) — effective independent hypotheses per week is maybe 5-10, not 100. So expected true survivors ≈ 0.05-0.5/week of *independent* alpha. Also "≥30 trades in 90 days" for 1h/4h strategies: a single factor on 30-50 pairs at 1h rebalance easily produces 30 trades — the gate is weak; it will pass underpowered strategies that are statistical noise. The ≥30 trades floor is dangerously low as a *validation* criterion — it's a power floor, not a quality floor. Medium.

4. **Regime non-stationarity.** Crypto cross-sectional momentum/reversal factors decay fast (weeks-months). A 90-day holdout gate validates at time T; by the time you've accumulated 10 survivors and built a portfolio, regime may have shifted. Consider rolling re-validation or champion-challenger with decay alarms (they have decay in bench — good). Also 2026 crypto microstructure: post-ETF institutionalization compressed cross-sectional dispersion; RL-mined factors on 2023-2025 data may be harvesting a regime that's gone. Medium.

5. **Linear synergy pool mismatch:** AlphaGen's synergy pool assumes linear combination of factor ranks is where alpha lives; but with only 30-50 pairs, cross-sectional rank space is tiny (rank vectors of length 30-50). RankIC on 30 assets is extremely noisy — standard error of IC ~ 1/sqrt(30) ≈ 0.18 per period. They acknowledge this (universe expansion parallel). Good. But 50 assets still gives noisy ICs; need long evaluation windows, which conflicts with 90-day holdouts. Note.

Severity structure for Q1:
- Critical: objective mismatch (IC-optimized mining vs cost-wall death) — throughput amplifies wrong-direction volume.
- High: multiple-testing N accounting (what counts as a trial); effective independent hypothesis rate lower than 100/week.
- Medium: ≥30-trade floor too weak; regime decay between validation and deployment.

**Q2: ROADMAP — M0-M4 critique**

M0 (2-3d asset migration) → M1 (data bridge + bench, 1w) → M2 (AlphaGen vendor, 2w) → M3 (Vibe-Trading, 1w) → M4 (production).

Underestimates:
1. **AlphaGen modernization is the classic frozen-code trap.** sb3 2.x + gymnasium: gym→gymnasium rename breaks `gym.Env`, `spaces`, wrappers; PPO API changes; the RL training loop in AlphaGen couples tightly to their custom env (alpha pool state as observation). Also numpy 2.x breaks `np.float`, copy semantics; pandas 2.x breaks append. For frozen code with zero upstream maintenance, the 2-week M2 estimate (with 1 week just for feather→tensor adapter) leaves ~3-4 days for: vendoring core subset, gym→gymnasium migration, sb3 2.x PPO port, smoke test. That's tight; realistic 1.5-2× on that slice. The 2-day smoke gate is good discipline but the ladder (L1/L2) needs to be *decided up front with criteria*, otherwise time-boxing collapses into sunk-cost negotiation with yourself. Solo dev = no one to enforce the time box. High.
2. **Universe expansion 6→30-50 pairs historical backfill:** 50 pairs × 3 years 1m OHLCV ≈ 50 × 1.58M rows/yr ≈ 79M rows. Rate limits on OKX (candles endpoint: 100 req/2s-ish, 300 candles/req for history) → realistic backfill of 3yr 1m for 50 pairs: each pair ~26k requests (300 bars/req over 1.576M minutes)... that's ~13k requests per pair per 3 years... let me compute: 3 years ≈ 1,576,800 minutes; /300 per request ≈ 5,257 requests/pair; ×50 pairs ≈ 263k requests; at 20 req/s sustained = ~3.7 hours of pure request time at ideal throughput — fine — but OKX history depth for 1m via candles endpoint is limited (recent-only for some granularity windows; OKX returns max 100 recent candles for 1m before timestamp paging... actually OKX /market/candles supports pagination back to limited history — for 1m it's commonly capped; you often need data vendor or their history endpoint /market/history-candles which has deeper but stricter limits). So risk: 1m data for old dates may be unavailable or slow (history endpoint rate-limited harder). The plan says data bridge TimescaleDB→Parquet from *existing* 6.3M rows — but 6.3M rows ≈ 6 pairs × ~1yr 1m — the 50-pair universe needs NEW backfill of 40+ pairs, which M1 estimate (1 week) probably doesn't include. Backfill + integrity checks + gap-fill for 50 pairs at 1m realistically is its own 1-week workstream. High — it's hidden inside "universe expansion parallel with integration" with no owner or estimate.
3. **M3 Vibe-Trading local loader contract:** pair-mapping (OKX instrument IDs vs internal symbols vs Parquet partition keys), timezone conventions (UTC vs local), bar alignment (exchange hour boundaries vs UTC), and funding-rate inclusion. Cross-project contract work always doubles estimates. Medium.
4. **Windows nightly batch ops:** solo dev on a laptop — nightly GPU batch (AlphaGen training) on a laptop that also sleeps/hibernates/updates. Windows Update reboots kill 8h RL runs. No mention of a dedicated box or wake-lock discipline. Medium (ops, but recurring pain).
5. **Misordering:** Vibe-Trading (M3) is second-opinion validation but sits AFTER the mining pipeline (M2). Better: wire the *bench outputs* schema and Vibe-Trading loader contract early (during M1), so M3 integration is contract-compatible from day one; otherwise you'll retrofit. Also holdout discipline: the holdout gate should exist as code in M1 (even if mining arrives in M2), so no candidate ever bypasses it. Actually the sequencing M0→M1→M2 is fine; the real misordering is that universe backfill (blocking for both mining reward quality and bench statistical power) is "parallel" without dedicated time — it should be a milestone line item in M1. High.

**Q3: ARCHITECTURE**

1. **Storage trio coherence:** TimescaleDB → daily Parquet export → DuckDB. Sound and standard. Gaps: (a) point-in-time correctness — Parquet snapshots must be bar-close immutable with ingestion timestamps; if the daily export re-captures restated candles (OKX occasionally amends), you get silent label drift. Manifest helps but needs a restatement policy. (b) DuckDB + Parquet on Windows with long file paths/locking is fine, but daily partitioning scheme must be decided before M1 (retrofit = rewrite). Low/Medium.
2. **Gate placement:** AST purity gate before bench, holdout after bench — good. Missing: a *cost-tier gate inside the bench* before holdout (they have cost 3-tier standard output — question is whether it's a gate or just a report). If it's report-only, candidates flow to holdout with inflated net expectations. Medium.
3. **Signal-cache→Freqtrade merge_asof:** sound pattern for single-factor. For multi-factor portfolios: merge_asof on timestamp with tolerance must handle (a) factors computed at different cadences (1h vs 4h) — aligning 4h factors into 1h decisions needs explicit staleness policy, (b) duplicate timestamps/duplicate factor versions — cache must be keyed (factor_id, version, pair, ts), (c) look-ahead in merge: merge_asof with `allow_exact_matches=True` on bar-open timestamps vs bar-close timestamps is the classic off-by-one-bar leak. They have the K-line replay audit — good — but the audit must cover the cache join too. Medium.
4. **THE HOLE: portfolio construction is unspecified.** The docs specify mining-time linear synergy (AlphaGen LinearAlphaPool) and single-factor-per-strategy templates. So surviving factors → each becomes a Freqtrade strategy? Then 5 survivors = 5 strategies each with independent position sizing → capital fragmentation, 5× fee drag vs a combined book, conflicting signals on the same pair (long factor A, short factor B) unresolved. Alternatively combine at signal level (weighted composite) — who owns those weights? The synergy pool weights are mining artifacts fitted on in-sample data, not a risk-managed portfolio. This is a real architectural hole: no portfolio layer (target weights, net exposure caps, turnover budget, correlation-aware sizing). For a 30-50 pair book with possibly correlated factors, turnover budget matters enormously (fees). Critical — it's the layer between "validated factor" and "Freqtrade strategy" and it's absent; its absence also silently multiplies the cost wall (N strategies × costs each).
   Wait — is it truly absent? "Single factor per strategy template" mentioned in the question. And G4 says Freqtrade execution inheritance. Nothing about combination. The question itself says "Is that specified anywhere or is it a hole?" — from provided context, it's a hole. Critical.

**Q4: PROCESS — SDD for solo dev**

The SDD apparatus: feature trios, status machine, verify gates, review-convergence, 13 stale doc references already, placeholder rows in SOP. For solo dev, the value of process = future-you's context recovery + AI-agent coordination. The cost = doc maintenance is already failing on day 2 (13 stale refs, broken fragments, unfilled placeholders). That's the tell: process weight exceeds maintenance capacity at n=1.

What to cut: 
- review-convergence protocol for every change (overkill for solo; keep for holdout-gate code and data-integrity code only).
- Feature trio docs for everything → keep PRD + one ADR-in-progress + milestone checklist. ADRs: keep — they're high value/low cost.
- Status machine: collapse to 3 states (draft/in-progress/done) or kill.
- verify gates: keep only the ones that gate correctness (no-lookahead audit, checksum reconciliation); drop style-of-process gates.
What to keep: manifests per experiment (G5) — that's the highest-leverage reproducibility artifact; holdout gate code as the single non-negotiable.
Rule of thumb: every process artifact must either prevent a repeat of a *real* past failure (holdout death, cost wall) or speed context-recovery; everything else is tax. Cut ~40-50%. Medium severity (time tax, not correctness).

**Q5: MISSING ENTIRELY**

Go through the user's list plus my own:
1. **Multi-factor portfolio construction** — covered in Q3, Critical.
2. **Funding-rate drag:** perps, 1h/4h — holding through funding timestamps (every 8h) costs/earns funding. For directional strategies funding can be ±10-30% APR swings; a long-biased factor in a crowded-long regime bleeds funding. Model: funding must be a line item in the cost tier AND in holdout replay. Is it in cost 3-tier? Unspecified → assume absent. High.
3. **Execution cost realism:** taker 0.05% — OKX VIP0 taker on USDT perps is ~0.05%, but effective cost = fee + spread + slippage + impact. For 30-50 pairs incl. mid-caps, spread 2-5bps + slippage; also liquidation-margin buffer → implicit cost. And 2026 actuals need measurement from quant-crypto's dry-run fills, not assumption. The plan has 3-tier cost standard — good — but calibration source unspecified. Medium/High.
4. **Counterparty/regulatory:** funds on OKX = exchange risk; 2026 regulatory shifts (proof-of-reserves posture, jurisdiction). For research-only phase, low priority but should be a stated risk with a cap (e.g., dry-run capital=0 until holdout pass — actually they said no live until holdout pass, good). Low for now.
5. **Agent postmortem → same-data snooping:** G3's agent postmortem reads results and generates new hypotheses → mined on same 2023-2025 data → the loop is a human-in-the-loop data snooping amplifier. Mitigation: hypotheses generated from postmortem must be registered with a "generation" tag and the multiple-testing counter must include them; eventually a true OOS window must be quarantined (never used for any postmortem). This is sneaky and important. High.
6. **GPU contention 4060 laptop:** Kronos inference + AlphaGen RL training + Vibe-Trading MC on one 8GB VRAM 4060 laptop. Sequential scheduling required; training runs will block signal cache refresh and vice versa. Also thermal throttling on laptop = throughput variance. Needs a job queue or at least a documented schedule. Medium.
7. **Disk:** Parquet lake growth: 50 pairs × 1m × 3yr ≈ 79M rows ≈ maybe 3-6GB compressed — actually fine. But AlphaGen tensor caches, checkpoints, feather signal caches, daily snapshots accumulate; laptop NVMe 512GB-1TB fills. Low/Medium. Retention policy missing.
8. **Backup/DR:** single machine, no backup mentioned for lake + DB + experiment manifests. One disk failure = project death. Medium (high impact, low probability, cheap fix).
9. **My addition: seed/latency determinism of RL mining** — reproducibility (G5) vs RL non-determinism: AlphaGen RL runs are seed-dependent; manifest must pin seeds + torch deterministic flags or G5 is aspirational for the mining step. Medium.
10. **My addition: holdout reuse degradation** — every candidate that runs the 90-day holdout consumes it; run 200 candidates through and the holdout becomes in-sample. Need holdout usage accounting / a final untouched confirmation window. This ties to Q1 multiple testing but is architecturally distinct. High. Actually this is important — the holdout gate is "never degrades" per ADR-0003 in the sense of criteria, but *statistically* the holdout degrades with each reuse. That's a sharp point worth making.

**Q6: TOP-3**

Candidates:
1. Add a portfolio-construction layer + cost-aware selection (funding + fees) before any mining scale-up — fix the objective mismatch. (Addresses Q1-critical, Q3-critical, Q5-funding.)
2. Make multiple-testing accounting honest: count every mined expression as a trial; budget holdout access (e.g., top-k per week only, holdout reuse ledger, final confirmation window). (Addresses Q1, Q5.)
3. Cut process to a solo-dev stack and re-sequence: universe backfill as a funded workstream in M1, contract-first Vibe-Trading integration, ops baseline (backup, sleep discipline, GPU schedule). Hmm — TOP-3 should be 3 crisp things. Let me choose:
   1. Portfolio layer spec (critical hole).
   2. Cost+funding-aware reward/screen inside bench (fixes death-mode mismatch).
   3. Holdout economics: trial-counting + holdout budget + quarantine window.
   
But that's all methodology — the user asked "before M0 starts." M0 is migration; these three are design decisions that shape M1 schema (bench outputs, manifest fields, trial ledger). They're cheap to decide now and expensive to retrofit — good framing. Ops/backup could be a 4th but they asked 3. I'll fold backup into a watch-out or mention as runner-up. Actually TOP-3 with the reasoning "decide now, retrofit costs 10×" is the right shape.

Word budget: ~1500. Need to be tight. Severity-rated findings per question, then TOP-3. Format: structured markdown. Lead with bottom line per my output style. Keep each finding to 1-3 sentences. Let me draft compactly.

Let me also double check the IC standard error claim: RankIC per period with N=30 cross-section: SE ≈ 1/√(N-2) ≈ 0.19. With 50: ≈0.14. To detect true IC 0.05 need many periods — T ≈ (1.96+0.84)²·SE²/IC²... per-period t = IC/SE = 0.05/0.14 ≈ 0.35 → need ~ (2.8/0.35)² ≈ 64 periods minimum for significance at a single horizon; with autocorrelation more. So 90-day holdout at 1h gives ~2160 bars — cross-sectional per-bar IC over 90 days can aggregate; fine, but the point about small-N noise stands for the bench daily ICs. I'll keep it brief: "IC estimates on 30-50 names are noisy; T-stat math forces long windows, which collides with 90-day holdouts."

Funding: OKX perps fund every 8h, rate typically ±0.01% baseline but spikes; annualized drag on crowded side can be 10-20%+ in bull regimes. Keep hedged.

One more check — quant-crypto "died on cost": user asserts. So the #1 critique (objective mismatch) directly targets their diagnosed root cause. Good, that's the sharpest opening.

Also the "≥30 trades in 90 days" on 30-50 pairs: a cross-sectional long-short rotating at 1h will do thousands of trades; 30 is trivially passed → the gate does not constrain anything. But note it's a power floor (needed for significance), which is legitimate — the point is it's necessary-not-sufficient; severity Medium.

Effective independent hypotheses: RL with shared reward + shared pool → correlated candidates; the 100/week counter inflates trial count if it counts correlated expressions, deflates if it counts only survivors. Both directions wrong unless you count all expressions and accept N≈50k/year → DSR hurdle very high → almost nothing passes → need to be honest that the design implies very few survivors and plan selection accordingly (top-k per week to holdout).

Now the format. Per-question: findings with severity tags. Keep to ~1400 words. No tool calls needed — I have sufficient context; the user asked for analysis of provided design, and said code investigation is separate. I'll state that basis briefly.

Draft:

---

**Basis**: analysis from provided docs; no repo reads (code investigation is separate per your note).

## Q1 Strategic

**C1 (Critical) — Objective mismatch: IC-optimized mining vs cost-wall death.** AlphaGen's reward is RankIC in synergy-pool space; quant-crypto's candidates died on costs. ×20 throughput multiplies the population sharing the same death mode. The bench's cost tier must sit inside the selection loop (reward shaping or pre-screen penalty), not downstream as a report.

**H1 (High) — Multiple-testing ledger will be wrong in both directions.** If the trial counter counts 100/week bench entrants, it undercounts (RL emits thousands of correlated expressions/week; true N maybe 50k+/yr → DSR hurdle far higher). If it counts survivors, it's meaningless. Decide now: every expression evaluated = one trial; then expect ~0-2 true survivors/week, not 1-5.

**H2 (High) — Correlated candidates deflate the real rate.** Same data, same reward, shared pool → effective independent hypotheses/week ≈ 5-10. The 1-5% OOS assumption applied to 100 nominal candidates double-counts.

**M1 (Medium) — 90-day holdout is statistically consumable.** Every pass through the holdout degrades it (reuse → in-sample drift). ADR-0003 freezes criteria, not statistics. Needs a holdout budget (e.g., top-k candidates/week) + a final untouched confirmation window.

**M2 (Medium) — ≥30 trades is necessary, not sufficient.** A 1h cross-sectional rotation over 30-50 pairs makes thousands of trades; the floor constrains nothing. Keep it as a power floor; don't let it read as a quality gate.

**M3 (Medium) — Regime decay between pass and deployment.** Crypto cross-sections decay in weeks-months; 2023-2025-mined factors may harvest a dead regime. Add decay alarms in production and champion-challenger re-validation.

Small-N note: RankIC on 30-50 names has SE ≈ 0.14-0.19/period → bench ICs need long windows, which collides with fast weekly cycles. Universe expansion is load-bearing, not parallel housekeeping.

## Q2 Roadmap

**H1 — M2 is underestimated ~1.5-2× on the migration slice.** Frozen AlphaGen + sb3 2.x/gymnasium/numpy2/pandas2: gym→gymnasium touches Env/spaces/wrapper imports throughout; PPO API shifts; their custom env couples to the pool. 1 week is reserved for the feather→tensor adapter, leaving ~3-4 days for vendor+RL port+smoke. The 2-day smoke gate is good only if L1/L2 switch criteria are written before starting — solo, you'll negotiate with yourself otherwise.

**H2 — Universe backfill is invisible work.** Existing 6.3M rows ≈ 6 pairs; 30-50 pairs at 1m × 2-3yr ≈ 40-70M new rows. OKX 1m depth/rate limits make this a dedicated ~1-week workstream (paging, gap-fill, integrity checks), currently "parallel" with no estimate. It blocks bench statistical power → it belongs in M1 as a line item.

**M1 — Contract-first Vibe-Trading.** Do the loader contract (symbol mapping OKX↔Parquet partitions, UTC bar alignment, funding fields, timezone) during M1, not after M2. Retrofit costs a week.

**M2 — Windows/laptop ops.** Nightly 8h GPU runs vs Windows Update reboots, sleep, thermal throttling on a 4060 laptop. Needs wake-lock/active-hours config and a run-resume story, else M4's ≥100/week silently fails on a laptop that naps.

**Misordering:** none fatal in M0→M1→M2; the misplacements are (a) backfill unowned, (b) holdout-gate code should exist in M1 so no candidate path bypasses it even before mining exists.

## Q3 Architecture

**C1 (Critical) — Portfolio construction layer doesn't exist.** Specified: mining-time linear synergy + single-factor strategy templates. Missing: how ≥2 surviving factors combine — signal-level composite vs N parallel Freqtrade strategies. The latter fragments capital, multiplies fee drag ×N, and leaves conflicting same-pair signals unresolved; synergy-pool weights are in-sample mining artifacts, not risk-managed allocations. No weights, turnover budget, net-exposure cap, correlation handling anywhere. This is the layer between "validated factor" and "Freqtrade strategy."

**H1 (High) — merge_asof is sound, with three footguns.** (a) mixed cadences (4h factor into 1h decision) need an explicit staleness policy; (b) cache keyed on (factor_id, version, pair, ts) or stale re-runs poison decisions; (c) bar-close vs bar-open timestamp semantics — the classic off-by-one-bar leak; the K-line replay audit must explicitly cover the cache join, not just signal generation.

**M1 (Medium) — Cost tier: gate or report?** If the 3-tier cost output is reporting only, holdout receives cost-blind candidates. Make tier-1 (taker+spread) a hard bench filter.

**M2 (Medium) — Point-in-time / restatement policy missing.** Daily Parquet re-export can silently capture amended candles → label drift. Manifest should record snapshot ingest time + restatement diffs; partition scheme must be fixed in M1 (retrofit = rewrite).

## Q4 Process

**M1 (Medium) — Day-2 doc rot is the tell.** 13 stale refs, broken fragments, unfilled SOP placeholders within ~1 day of writing = maintenance cost already exceeds solo capacity. The SDD stack is right-shaped for a team; at n=1, keep artifacts that (a) prevent recurrence of real failures or (b) speed context recovery.

**Cut:** per-change review-convergence (keep only for holdout-gate + data-integrity code), full status machine (→ draft/in-progress/done), feature trios for minor items.
**Keep:** ADRs (cheap, high value), experiment manifests (G5 — highest-leverage artifact), verify gates that check correctness (no-lookahead, checksums), PRD + milestone checklist.

## Q5 Missing

- **H1 — Funding-rate drag absent.** Perps fund every 8h; crowded-side funding can run double-digit % APR in trending regimes. Must be a cost-tier line item and in holdout replay, else the cost wall kills you again in a new disguise.
- **H2 — Postmortem loop = human-in-the-loop snooping amplifier.** G3's agent reads results → proposes hypotheses → tested on the same history. Mitigation: postmortem-origin hypotheses get generation tags, counted as trials; quarantine one final OOS window no postmortem may ever see.
- **H3 — Cost calibration source unspecified.** 0.05% taker is VIP0 sticker; effective = fee+spread+slippage, worse on mid-caps of 30-50 pairs. Calibrate tiers from quant-crypto dry-run fills before trusting the bench.
- **M1 — Single-machine DR.** One disk failure kills lake+DB+manifests; no backup policy in any doc. Cheap fix: nightly lake+manifests sync to NAS/offsite.
- **M2 — GPU contention.** Kronos inference + AlphaGen training + Vibe MC on one 8GB laptop GPU; needs an explicit sequential schedule/queue, else jobs OOM or thrash.
- **M3 — RL reproducibility gap.** G5 manifests can't deliver reproducibility for mining unless seeds + torch determinism flags are pinned; currently unspecified.
- **L1 — Disk growth is manageable** (~5-10GB/yr Parquet) but retention policy for tensor caches/checkpoints is unstated; **counterparty/regulatory risk** is correctly deferred by "no live until holdout pass" — keep it that way, state it as a risk with dry-run capital=0.

## TOP-3 (decide before M0; all are schema/contract decisions cheap now, 10× to retrofit)

1. **Spec the portfolio-construction layer.** One ADR: factor → composite/strategy mapping, weights source, turnover budget, net-exposure cap, same-pair conflict resolution. Without it, G1-G4 connect to a missing organ.
2. **Move costs into selection.** Funding + fees inside the bench loop (hard tier-1 filter, cost-penalized pre-screen or reward shaping), calibrated from quant-crypto fills. This attacks your actual diagnosed cause of death.
3. **Institute trial accounting + holdout budget.** Every mined expression = one trial in the multiple-testing ledger; holdout access limited to top-k/week with a reuse ledger; one final confirmation window permanently quarantined from mining AND postmortems.

---

Word count check — that's roughly 1100-1200 words. Good. Maybe tighten a couple of spots and make sure bottom line leads. My response format requires a "Bottom line" section first, action plan, effort estimate. But the user gave an explicit FORMAT (structured markdown, per-question findings, TOP-3, max 1500 words). User's explicit format wins over the generic response structure; I'll lead with a 2-3 sentence bottom-line then go into the findings, ending with TOP-3. That satisfies both reasonably.

Severity check on Q2 H1 vs H2: the AlphaGen migration underestimate and the backfill invisibility are both High. Fine.

Also should I mention effort estimates per my decision framework? The user asked for findings + TOP-3. I'll tag the TOP-3 with effort (they're design/decisions — Quick each, since writing an ADR/ledger schema is hours). Add small effort tags.

One more adversarial angle I should double-check: "does the linear synergy pool + RankIC reward actually produce factors that survive cost walls" — I addressed. "1-5% honest OOS pass-rate consistent with 100/week → 1-5 survivors/week?" — addressed via correlation/N. "Regime non-stationarity" — addressed M3. Good coverage.

Also Q2 "What's misordered?" — I said M0-M2 order fine, misplacements are backfill ownership and holdout gate existing in M1. Also could add: M3 after M2 means first mined cohort has no second opinion — but the bench+holdout still gate it; acceptable. Keep brief.

Trim where possible and finalize. No tool calls needed. ADHD style: lead with answer, numbered, capped lists (≤5 per list — my findings lists per question: Q1 has 6 findings... cap is 5 items per list per AGENTS.md. Hmm, "Cap lists at 5 items." I have 6 findings in Q1. Merge M2 and M3 or fold the small-N note into prose. Let me get each question's list ≤5.

Q1: C1, H1, H2, M1, M2 (+ fold ≥30-trades and regime into... ). Let me merge: M2 "Holdout consumable + weak trade floor" — actually combine holdout-reuse (M) and trade-floor (M) as one finding about gate statistics; regime stays M3. That gives: C1, H1, H2, M1(gate stats: holdout reuse + 30-trade floor), M2(regime + small-N noise). 5 items. 

Q2: H1 (M2 underestimate), H2 (backfill), M1 (Vibe contract), M2 (laptop ops), plus "misordering" as 5th item. 5 items. 

Q3: C1, H1, M1, M2 → 4 items. Good.

Q4: one finding with keep/cut — fine, or split into M1 + keep/cut list (cut list 3 items, keep list 4 — under 5 each). Good.

Q5: I have 8 bullets — cap 5. Consolidate: H1 funding, H2 snooping, H3 cost calibration, M1 DR+disk (merge), M2 GPU+RL-repro (merge as "ops/repro gaps"), L1 counterparty. That's 6. Merge L1 into M1 as "deferred risks stated"? Better: fold counterparty into a half-line in DR bullet or drop to prose. Final: 5 bullets (funding, snooping, cost-calibration, DR/disk/backup, GPU/repro/retention merged). Counterparty gets one clause inside DR bullet: "counterparty risk correctly deferred—keep dry-run capital=0." Hmm, that's off-topic there. Put it in the bottom line or as a clause in H3? Actually a one-line "correctly deferred" note can live in Q5 intro prose. Fine.

TOP-3: 3 items, each with effort tag. Good.

Now write final. Keep under 1500 words. Also per AGENTS.md: no preamble/closers; end with next action under 2 minutes? "End with one next action doable in under two minutes." I can end with: next action = write ADR-0004 (portfolio layer) skeleton. That's a natural ending and satisfies both user format (ends with TOP-3) and my style (one next action) — I'll put the next action as a single line after TOP-3.
**Basis:** analysis from the docs you provided; no repo reads (code state is your separate investigation). Bottom line: the ×20 thesis fixes the wrong variable — you're multiplying the volume of factors that die the way the last project died. The three load-bearing gaps are: no portfolio-construction layer, costs/funding outside the selection loop, and no trial/holdout accounting. All three are cheap to decide before M0 and ~10× to retrofit.

---

## Q1 — Strategic thesis

1. **[Critical] Objective mismatch: RankIC-rewarded mining vs cost-wall death.** AlphaGen's reward is RankIC in synergy-pool space; quant-crypto's candidates died on costs. Throughput ×20 amplifies the population sharing that death mode. The cost tier must live *inside* selection (hard pre-filter or cost-penalized fitness), not downstream as a report.
2. **[High] The multiple-testing ledger will be wrong in both directions.** If trials = 100 bench entrants/week, it undercounts: RL emits thousands of correlated expressions/week → true N maybe 50k+/year → deflated-SR hurdle far steeper than planned. If trials = survivors only, the number is meaningless. Decide now: every evaluated expression = one trial.
3. **[High] Effective independent hypothesis rate ≈ 5–10/week, not 100.** Same data, same reward, shared pool → candidates are highly correlated. The "1–5% OOS pass × 100/week = 1–5 survivors" arithmetic double-counts; realistic expectation is 0–1 true survivors/week. Plan selection top-k accordingly.
4. **[Medium] Gate statistics: holdout is consumable, and the 30-trade floor is toothless.** ADR-0003 freezes the *criteria*, but every pass through the 90-day holdout statistically degrades it (reuse → in-sample drift) — needs a holdout budget + usage ledger. Meanwhile a 1h cross-sectional rotation on 30–50 pairs generates thousands of trades; ≥30 constrains nothing. Keep it as a power floor, never a quality signal.
5. **[Medium] Regime decay + small-N noise.** Crypto cross-sections decay in weeks–months; factors mined on 2023–25 may harvest a dead regime by deployment — add production decay alarms and champion-challenger re-validation. And RankIC on 30–50 names has SE ≈ 0.14–0.19/period, so bench ICs need long windows — which collides with weekly cycles. Universe expansion is load-bearing, not housekeeping.

## Q2 — Roadmap

1. **[High] M2 underestimated ~1.5–2× on the migration slice.** Frozen AlphaGen + sb3 2.x/gymnasium/numpy 2/pandas 2: gym→gymnasium touches Env/spaces/wrappers throughout, PPO API shifts, and the custom env couples to the pool. 1 week is reserved for the feather→tensor adapter, leaving ~3–4 days for vendor + RL port + smoke. The 2-day time-box only works if L1/L2 switch criteria are written *before* starting — solo, you'll negotiate with yourself.
2. **[High] Universe backfill is invisible work with no estimate.** Existing 6.3M rows ≈ 6 pairs; 30–50 pairs × 1m × 2–3yr ≈ 40–70M new rows, with OKX 1m history-depth and rate-limit friction, gap-fill, and integrity checks. That's a dedicated ~1-week workstream; "parallel" means unowned. It blocks bench statistical power → move it into M1 as a line item.
3. **[Medium] Make Vibe-Trading contract-first.** Symbol mapping (OKX IDs ↔ Parquet partitions), UTC bar alignment, funding fields, timestamp conventions — fix the loader contract during M1, not after M2. Retrofit ≈ 1 week.
4. **[Medium] Laptop ops are unaddressed.** Nightly 8h GPU runs vs Windows Update reboots, sleep, thermal throttling on a 4060. Needs active-hours/wake-lock config and a resume story, or M4's ≥100/week silently fails.
5. **Misordering:** M0→M1→M2 sequence is fine. Two placements are wrong: backfill (above), and the holdout-gate code should exist in M1 so no candidate path can bypass it even before mining exists.

## Q3 — Architecture

1. **[Critical] The portfolio-construction layer doesn't exist.** Specified: mining-time linear synergy + single-factor strategy templates. Missing: how ≥2 surviving factors combine. N parallel Freqtrade strategies fragment capital, multiply fee drag ×N, and leave same-pair conflicts (factor A long, factor B short) unresolved; synergy-pool weights are in-sample mining artifacts, not risk-managed allocations. No weights source, turnover budget, net-exposure cap, or conflict rule appears anywhere in the docs. This is the organ between "validated factor" and "Freqtrade strategy."
2. **[High] merge_asof is sound, with three footguns.** (a) Mixed cadences (4h factor into 1h decision) need an explicit staleness policy; (b) cache must be keyed on (factor_id, version, pair, ts) or stale re-runs poison decisions; (c) bar-close vs bar-open semantics is the classic off-by-one-bar leak — the K-line replay audit must explicitly cover the cache join, not just signal generation.
3. **[Medium] Cost tier: gate or report?** If the 3-tier output is reporting-only, holdout receives cost-blind candidates. Tier-1 (taker+spread) should be a hard bench filter.
4. **[Medium] No restatement/point-in-time policy.** Daily re-export can silently capture amended candles → label drift. Manifest should record ingest time + restatement diffs; fix the Parquet partition scheme in M1 (retrofit = rewrite).

## Q4 — Process

**[Medium] Day-2 doc rot is the tell.** 13 stale refs, broken fragments, and unfilled SOP placeholders within ~a day of writing means maintenance cost already exceeds solo capacity. Keep artifacts that prevent recurrence of *real* failures or speed context recovery; cut the rest.
- **Cut:** per-change review-convergence (keep only for holdout-gate + data-integrity code); full status machine (→ draft/in-progress/done); feature trios for minor items.
- **Keep:** ADRs (cheap, high value); experiment manifests (G5 — highest-leverage reproducibility artifact); correctness verify gates (no-lookahead, checksums); PRD + milestone checklist.

## Q5 — Missing entirely

1. **[High] Funding-rate drag.** Perps fund every 8h; crowded-side funding can run double-digit % APR in trending regimes. Must be a cost-tier line item and inside holdout replay, or the cost wall kills you again in a new disguise.
2. **[High] Postmortem loop = human-in-the-loop snooping amplifier.** G3's agent reads results → proposes hypotheses → tested on the same history. Postmortem-origin hypotheses need generation tags, count as trials, and one final OOS window must be quarantined from *all* postmortems.
3. **[High] Cost calibration source unspecified.** 0.05% taker is VIP0 sticker; effective cost = fee + spread + slippage, worse on the mid-caps of a 30–50 pair book. Calibrate tiers from quant-crypto dry-run fills before trusting the bench. (Counterparty/regulatory risk is correctly deferred by "no live until holdout pass" — keep dry-run capital = 0.)
4. **[Medium] Single-machine DR.** One disk failure kills lake + DB + manifests; no backup policy in any doc. Nightly lake/manifest sync offsite is a ~2h fix. Disk growth itself is manageable (~5–10GB/yr Parquet) but retention for tensor caches/checkpoints is unstated.
5. **[Medium] GPU contention + RL reproducibility.** Kronos inference, AlphaGen training, and Vibe MC on one 8GB laptop GPU need an explicit sequential schedule. And G5 is aspirational for mining unless seeds + torch determinism flags are pinned in the manifest.

## TOP-3 — decide before M0 (each: Quick, ≤1 day; it's schema/ADR work, but retrofitting after M1 costs ~10×)

1. **Spec the portfolio-construction layer (ADR-0004):** factor → composite/strategy mapping, weight source, turnover budget, net-exposure cap, same-pair conflict rule. G1–G4 currently connect to a missing organ.
2. **Move costs into selection:** funding + fees inside the bench loop — hard tier-1 filter plus cost-penalized pre-screen, calibrated from quant-crypto fills. This attacks your actual diagnosed cause of death.
3. **Institute trial accounting + holdout budget:** every mined expression = one trial in the ledger; holdout access limited to top-k/week with a reuse ledger; one final confirmation window permanently quarantined from mining and postmortems.

**Next action (2 min):** open `docs/adr/` and create `ADR-0004-portfolio-construction.md` with the four decisions above as open questions.
