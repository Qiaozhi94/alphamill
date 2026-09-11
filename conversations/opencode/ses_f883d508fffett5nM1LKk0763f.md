---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f883d508fffett5nM1LKk0763f"
title: "Oracle 评估 pivot 风险 (@oracle subagent)"
project: "D:/Projects/alphamill"
model: "glm-5.3-flash"
created_at: "2026-09-06T17:27:22Z"
updated_at: "2026-09-06T17:32:32Z"
tokens_input: 28799
tokens_output: 1573
cost: 0.0
parent_id: "ses_f887c8e5cffeXNR2u34Pzo7U7H"
---

# Oracle 评估 pivot 风险 (@oracle subagent)

## user · 2026-09-06T17:27:22Z

Strategic risk consultation for a quant research project. This is a SECOND-round review: round 1 found and the owner fixed 29 findings (portfolio layer ADR-0004, cost/funding in selection loop, trial counting, holdout budget, sample-power clarification, src-layout, doc hygiene, etc.). All gates green. Now the owner asks a different question: "What FUNDAMENTAL problems remain in goals/plans that could force a LARGE-SCALE direction change after development starts?" Your job: cross-validate my candidate findings, refute what's wrong, and hunt blind spots I missed. Adversarial, specific, no hedging filler.

[PROJECT STATE (post-fix)]:
- AlphaMill: solo dev, Windows laptop + RTX 4060, successor to quant-crypto (5 weeks infra, ALL candidates died at 90-day holdout; diagnosed root cause: hypothesis throughput ~5/week vs needed 100+/week).
- Core loop: RL expression mining (AlphaGen vendored) → unified bench (RankIC + cost hard-filter incl. funding) → holdout gates (90d, ≥30 trades absolute floor, 30-69 = UNDERPOWERED band temp-PASS, ≈69+ credible) → signal cache → Freqtrade dry-run. Top-K=3 deployment of meta-factors (ADR-0004: synergy-pool composites validated as meta-factors through the SAME gates, inverse-vol weights, netting before signal cache).
- Milestones: M0 asset migration (2-3d) → M1 data bridge + bench (1wk dev + 1-2wk universe backfill parallel, 46M rows 1m data) → M2 AlphaGen vendor pipeline (2wk, 2-day smoke gate, L1/L2 degradation ladder with binary criteria) → M3 Vibe-Trading integration (1wk, second-opinion backtest + agent postmortem) → M4 production loop (ongoing: ≥100 candidates/week, first holdout pass → dry-run).
- Docs now state BOTH: (a) G1 justification: "honest OOS pass rate 1-5%, therefore need 100+ hypotheses/week tested" AND (b) FR2.4 fix: "candidates share data/reward/pool, effective independent hypotheses ≈5-10/week; deflation must use total-expression count".

[MY CANDIDATE FINDINGS — validate/refute each, severity as pivot-risk]:
F1. Thesis economics unclosed + no project-level stop-loss. G1's arithmetic (100/wk × 1-5% = 1-5 survivors/wk) is hollowed out by the 5-10 effective-independent correction: honest expectation is ~1 survivor per 2-20 weeks (3-26/year). M4's exit ("first candidate passes holdout") has NO time bound; if true pass rate ≈0, the system grinds indefinitely and every failure reads as "gates working correctly" — exactly quant-crypto's pattern. No pre-registered thesis checkpoint (e.g., N total independent candidates all-dead → mandatory strategic review of universe/frequency/cost assumptions). Risk: 3 months of green G1 + zero survivors → crisis-mode pivot instead of planned decision.
F2. Unit-of-validation drift: post-ADR-0004 the thing consuming holdout budget (k=5/wk) and facing ≥30/69-trade thresholds is a meta-factor COMPOSITE, but those numbers were derived for single strategies (quant-crypto history). Composite trade autocorrelation/distribution differs; power analysis doesn't transfer. The numbers feel precise but their derivation object changed. Cheap doc fix now (define unit-of-validation + acknowledge thresholds apply to composite realized trades); expensive re-derivation later.
F3. Highest-information evidence arrives last. M1 is already a natural thesis probe (Kronos signals re-run through new bench incl. cost hard-filter on 6 pairs) but framed as plumbing, not probe. Proposal: extend M1 exit with "seed candidate kill-rate report" (py-alpha-lib GTJA191 subset + Kronos) — first direction-relevant evidence ~weeks earlier, 1 day of work. Also note: hypothesis-source diversity (paper formulas, ~190 semi-independent) may deliver more INDEPENDENT hypotheses/week than the RL engine's correlated output — the humble seed channel is underemphasized vs AlphaGen.
F4. M3 Vibe-Trading is the least load-bearing milestone and should be officially declared droppable (release valve). It's insurance/research-UX, serves no alpha outcome directly; if it becomes a time sink it eats core-loop schedule.
F5. Pivot-cost map (the good news): 1m raw lake = frequency/universe-pivot-proof; Freqtrade+risk = execution-pivot-proof; AlphaGen = replaceable via ladder; Vibe = droppable; the ONLY expensive-to-change core is the validation stack's calibrated numbers (thresholds, windows, budgets). So direction-change risk concentrates in thesis/metrics, not architecture.

[QUESTIONS]:
1. F1: Is my arithmetic reading right? What would a WELL-DESIGNED pre-registered thesis checkpoint look like for this system (N candidates? leading indicators like cost-filter kill-rate? what decisions unlock at trigger?) — and what's the failure mode where such a checkpoint causes PREMATURE abandonment of a viable thesis (false kill)?
2. F2: How much does composite-vs-single power transfer actually matter at these scales? Refute if overblown.
3. F3: Is the M1 seed kill-rate probe the highest information-per-day addition? What else surfaces pivot-relevant evidence earliest (specific, cheap)?
4. F5: Validate/correct the pivot-cost map. What pivot scenarios remain EXPENSIVE that I've missed?
5. BLIND SPOTS: the single most dangerous unexamined assumption that could force large-scale direction change after dev starts — one that neither round-1 findings nor F1-F5 covers. Think: things that look settled but aren't.
6. If you had to bet: which is more likely for this project in 6 months — (a) thesis holds, first survivors emerge; (b) cost wall kills everything, pivot to maker-only/micro-structuring; (c) discovery that effective-independent-hypothesis throughput was the real constraint all along, pivot to hypothesis-source diversity; (d) abandonment of RL mining for the seed-library + postmortem loop? Rank and justify briefly.

[FORMAT]: markdown, per-question verdicts (agree/refute/modify + why), severity ratings for anything new. ≤1200 words. No praise, no summary of what I said back to me.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-06T17:27:22Z


> [reasoning] The user is asking me to cross-validate candidate findings for a quant research project (AlphaMill). This is a strategic risk consultation. Let me think carefully about each question.

Context recap:
- Solo dev, Windows laptop + RTX 4060
- Previous project failed: 5 weeks infra, all candidates died at 90-day holdout, root cause: hypothesis throughput ~5/week vs needed 100+/week
- Core loop: RL expression mining (AlphaGen) → bench (RankIC + cost hard-filter incl. funding) → holdout gates (90d, ≥30 trades floor, 30-69 UNDERPOWERED band temp-PASS, ≈69+ credible) → signal cache → Freqtrade dry-run
- Top-K=3 deployment of meta-factors (composites validated through same gates)
- Milestones M0-M4

Candidate findings F1-F5 need validation/refutation. Then blind spots, then a bet on 6-month outcomes.

Let me think hard about each.

**F1: Thesis economics + no project-level stop-loss**

The arithmetic: G1 says 100 candidates/week × 1-5% honest OOS pass rate = 1-5 survivors/week. But FR2.4 correction says candidates share data/reward/pool, so effective independent hypotheses ≈ 5-10/week. So real expectation: 5-10 independent × 1-5% = 0.05-0.5 survivors/week, i.e., 1 survivor per 2-20 weeks. That's 2.6-26/year. The user's arithmetic reads correct: 3-26/year. Actually let me recompute: 0.05-0.5 per week → per year (52 weeks): 2.6-26. Yes matches.

But wait — there's a subtlety. The 1-5% pass rate applies to... what population? If the pass rate is per-independent-hypothesis, then yes. But the 1-5% figure itself came from... presumably quant literature on honest OOS pass rates of tested alpha ideas. If the effective independent count is 5-10/week and each has 1-5% chance, expectation is ~0.25/week at midpoint. First survivor expected around 4 weeks at midpoint of midpoint. But the distribution matters — it's roughly geometric/Poisson. With λ = 0.25/week, P(no survivor in 8 weeks) = e^-2 ≈ 13.5%. P(no survivor in 12 weeks) = e^-3 ≈ 5%. So even at the midpoint assumption, 8-12 weeks without a survivor isn't crazy. At the pessimistic corner (5 indep/wk × 1% = 0.05/wk), 26 weeks no-survivor has probability e^-1.3 ≈ 27%. So the arithmetic is right and the concern is real: "grinds indefinitely" is a genuine failure mode.

But — important caveat — the pass-rate model conflates "survivor" with "deployable PnL". A pass is ≥30 trades over 90d positive net. Even if survivors emerge, they might be too weak to matter (RankIC small, net Sharpe <1). The stop-loss needs to be about the THESIS (discovery engine produces net-positive deployable signals at acceptable rate), not just any survivor.

Well-designed pre-registered checkpoint: What would it look like?
- Trigger variables should be leading indicators, not just survival counts:
  1. Cost-filter kill-rate: what fraction of expressions die at the cost hard-filter? If 95%+ die at costs before even reaching holdout, that's a cost-wall signal (funding costs on perps, taker fees) — a leading indicator for outcome (b).
  2. IC-survival rate: fraction of mined expressions with OOS RankIC > threshold (e.g., |IC|>0.02 ICIR>0.3) — measures discovery quality independent of trade frequency.
  3. Independent-hypothesis diversity metric: correlation structure of top candidates (avg pairwise correlation of OOS PnL). If avg pairwise corr > 0.7, the RL engine is producing one hypothesis dressed N ways — leading indicator for outcome (c).
  4. Underpowered-band fraction: if most passes are in 30-69 trade band, evidence quality is weak; temp-PASS accumulates unearned confidence.
- Decision structure: e.g., checkpoint at T = 8-12 weeks after M4 start or after N_eff ≈ 100 independent candidates (whichever first). Decisions gated:
  - Zero survivors AND cost-kill-rate > X → cost-wall pivot (maker-only, longer horizon, fewer trades)
  - Zero survivors AND IC-survival ≈ 0 → hypothesis-generation pivot (source diversity, seed library)
  - Survivors exist but all UNDERPOWERED and pairwise corr high → diversification/deployment-design pivot
  - ≥2 credible survivors → thesis holds, continue

False-kill failure mode: The checkpoint kills the thesis when the engine is actually fine but the environment is in a regime where alphas are temporarily absent (crypto alpha regimes are cyclical; e.g., low-vol chop periods kill mean-reversion signals). Also: the pipeline itself might have silent bugs early (data snooping in reverse — e.g., misaligned timestamps making everything look bad). Mitigation: checkpoint requires a "pipeline health attestation" — a known-good reference factor (e.g., a published factor like a simple momentum or funding-rate carry) must PASS the full gate before the kill counts. If the reference factor passes and your mined candidates all die, kill is justified; if the reference also fails, the bench is broken, not the thesis. That's the single most important guard against false kill. Actually — this is important and might be my blind-spot contribution folded into F1's answer. But wait, they asked for blind spot separately; the "control factor / positive control" idea is a strong one. Let me think whether it's covered by F1-F5: F3 is about seed kill-rate probe which partially covers it (py-alpha-lib GTJA191 subset through the bench = essentially positive controls). Actually yes! F3's proposal IS the positive control. So the false-kill mitigation is built into F3: don't kill the thesis unless the seed library also demonstrates the bench can pass known-published factors. Good.

But there's still a subtlety: GTJA191 factors are equity factors (A-share), being run on crypto — many may genuinely not transfer. So the positive control needs to be crypto-native known-good: funding-rate carry, simple momentum/breakout, cross-sectional momentum on majors. If even funding carry dies at the cost filter, the cost model is too strict or the universe wrong. So the kill-report should be tiered: crypto-native controls must pass (or diagnose the bench), paper-derived factors have uncertain prior.

Severity F1: agree, HIGH. The user's reading of arithmetic is right.

**F2: composite-vs-single power transfer**

The question: holdout thresholds (≥30 trades, 69+ credible) were derived for single strategies. Now the unit is a Top-K=3 meta-factor composite. Does power analysis transfer?

Key points:
- Trade count for a composite: if K=3 underlying factors are averaged/netted, trade count of the composite is roughly the union of constituent trade events where positions change. Combining 3 signals typically INCREASES trade count or keeps similar (if signals agree, fewer flips; if decorrelated, more rebalancing). Actually for inverse-vol weighted combination of 3 factor exposures on perps, the composite position changes whenever any component changes — trade count ≥ each individual's count roughly, often 1-3x.
- 30-69 trades threshold: this presumably comes from power analysis of detecting Sharpe > 0 with some confidence. Power depends on per-trade Sharpe (mean/std of trade returns) and number of trades, and importantly on autocorrelation of returns and overlapping holding periods. For a composite, per-trade distribution changes: combining decorrelated signals RAISES composite Sharpe (diversification), which makes detection EASIER per trade, but ALSO the composite trades may be smaller (position sizing netting reduces per-trade magnitude) — mixed effect.
- The direction of the error matters more than the precision: if anything, composites are usually MORE detectable per unit trade (higher Sharpe, lower variance) than marginal single factors. So the threshold ≥30 trades for a composite is likely CONSERVATIVE (more powerful than assumed), not optimistic. The dangerous direction would be autocorrelated trades (overlapping holds) inflating effective N — that applies to both singles and composites.
- However, there IS a real issue: netting before signal cache means composite position can be much flatter (offsetting positions), reducing gross exposure and thus per-trade PnL magnitude — trade count may rise while per-trade edge shrinks; t-stat still fine, but economic significance (net PnL after fixed costs per trade... wait costs are proportional). Hmm, actually proportional costs scale with turnover not trade count per se. Netting can REDUCE turnover (offsets), which helps. So netting is mostly good.
- Verdict: user says "cheap doc fix now, expensive re-derivation later." I'd modify: the power-transfer concern is real but direction is mostly favorable/conservative; the bigger composite issue is NOT power, it's (a) the composite is fit AFTER seeing constituents' OOS behavior? No — ADR-0004 says composites go through the SAME gates, so they're re-validated. The real composite risks: (1) weight optimization on what sample? inverse-vol weights estimated on the same window used for gating — mild in-sample optimism in the gate itself; (2) selection of Top-3 from a pool introduces selection bias if the pool was screened on overlapping data — is the holdout truly untouched by the synergy-pool construction? If pool construction used data within the holdout window, the gate is contaminated. That's the sharp question: WHERE does the synergy pool get built relative to the holdout boundary? Round 1 apparently didn't cover this (not listed). Hmm, this could be my blind spot or part of F2. Let me hold it.

Actually wait — let me reconsider. The user asks "does composite-vs-single power transfer actually matter at these scales? Refute if overblown." At 30-69 trades scale, the difference between single and composite power is second-order compared to the underlying problem: 30-69 trades over 90 days is 1/min(90) ≈ underpowered for ANY return-distribution assumption unless per-trade edge is huge. With 69 trades, detecting Sharpe 1 annualized requires... let me do rough math: annualized Sharpe S, over T years, t-stat ≈ S·√T. 90 days = 0.25y, S=1 → t ≈ 0.5. Hopeless. The trade-count threshold must be about per-trade statistics instead (t = mean/std_trade × √N). For t=2 with N=69, need per-trade Sharpe (mean/std of per-trade returns) ≈ 2/√69 ≈ 0.24. That's a big per-trade edge. For N=30, need 0.365. So the "credible" band at 69 requires per-trade edge of ~0.24 std — plausible only for high-conviction signals. This means: the gate is mostly a filter for VERY strong signals; the UNDERPOWERED temp-PASS band is where most marginal-but-real alphas will live. The composite-vs-single shift changes per-trade edge distribution mildly. So verdict: F2 is directionally valid but LOW severity; doc fix is right-sized; the sharper issue is that the whole gate only catches high per-trade-edge signals, meaning the system is structurally biased toward low-frequency, high-conviction candidates — and 90d window with ≥30 trades means ≥1 trade per 3 days — this biases against slower signals whose holding periods are weeks. That's a unit/frequency design constraint that's arguably F1-adjacent (universe/frequency pivot). Hmm, this could feed Q5 pivot map: the gate itself embeds a frequency prior — a pivot to lower frequency (where costs bite less) is expensive NOT because of data (1m lake is fine) but because the validation window/trade-count calibration needs redoing (they already flagged validation stack as the expensive core in F5 — consistent).

So F2: modify — agree with the doc fix but downgrade severity; the numbers don't transfer precisely but error direction is likely conservative for composites; the real composite issue is gate contamination via pool construction timing, not power.

**F3: M1 seed kill-rate probe as highest info/day**

Is extending M1 exit with a kill-rate report the highest information-per-day addition? I think yes — it's essentially positive controls + first data on bench discrimination. Details to sharpen:
- Use crypto-native controls (funding carry, momentum) as MUST-PASS calibration anchors; GTJA191 subset as exploratory prior. If funding carry can't survive the cost filter, the cost model or universe is wrong — that's pivot-relevant evidence for outcome (b) at week ~2.
- Also the pairwise-correlation matrix of the seed library's OOS PnL gives you the independence structure baseline to compare AlphaGen output against — directly measures "effective independent hypotheses" assumption (5-10/wk). That's cheap and high value: it converts a docs-assumption into a measured quantity in week 1-2.
- What else surfaces early, cheap: (1) cost-decomposition report — what fraction of gross alpha is eaten by funding vs taker fees vs slippage per pair; tells you WHERE the cost wall is if it exists; (2) universe liquidity check: turnover feasibility at assumed sizing on the 6 pairs (market impact realism); (3) label/horizon sensitivity: does RankIC stability change with 1h/4h/1d horizon — cheap on cached data, informs frequency pivot before committing.
- One caution: a "kill-rate report" on seeds risks misreading GTJA191 non-transfer as bench harshness. Tier the interpretations.

Agree F3, with the crypto-native control tier added. Severity of the addition: Medium.

**F4: Vibe-Trading droppable**

Agree it's the least load-bearing. But check: M3 includes "second-opinion backtest" — is Vibe the second-opinion engine? If Vibe provides an independent backtest implementation (cross-validation of the bench), it has some load-bearing value for correctness, not alpha. If second-opinion is merely nice-to-have, fine. The user says it serves no alpha outcome directly. I'd agree with the modification: declare it droppable EXCEPT the second-opinion backtest function, which can be satisfied cheaper (e.g., a different library like vectorbt or a hand-rolled shadow calc on a subset) if bench-bug suspicion arises. Also dropping it removes the "agent postmortem" UX. Fine. Low severity, agree.

**F5: pivot-cost map**

Their map: 1m lake = frequency/universe pivot-proof; Freqtrade = execution pivot-proof; AlphaGen replaceable via ladder; Vibe droppable; validation stack calibrated numbers = the expensive core.

Corrections/additions:
- The 1m lake is 6 pairs. Universe pivot BEYOND those 6 pairs (e.g., adding 50 alts) is NOT free: backfill compute, storage, and — importantly — the liquidity/cost model must be re-validated per pair. So lake is frequency-pivot-proof but only semi universe-pivot-proof (within-major pivot cheap, breadth expansion = Medium cost).
- Missing expensive pivot: EXCHANGE/venue pivot. Cost structure (fees, funding, depth) is venue-specific. If cost wall appears on perp taker fees, the pivot is venue/fee-tier/maker-execution — Freqtrade config change is cheap but the cost MODEL inside the bench (hard-filter assumptions) is calibrated to current venue fees; changing venue means re-running history with new cost model — that's re-running the whole candidate population. So cost-model parameters should be config-separated (they probably are after round 1's cost/funding fix) so re-pricing is cheap. Verify that: cost model as first-class config, versioned, with ability to re-score cached expressions without re-mining. That's the single most valuable "pivot insurance" artifact: an expression→metrics cache that can be re-priced under new cost assumptions in hours, not weeks. If the bench stores per-candidate gross returns and trade logs, re-scoring under new cost model is cheap. If it stores only pass/fail, pivot to maker-only requires re-running everything. This is a concrete, checkable design point.
- Another possibly expensive pivot: FROM perps (funding-sensitive) TO spot (no funding but no short on most) — universe and cost model change, plus long-only constraint changes factor viability. Probably second-order.
- Also: signal-cache schema and Freqtrade strategy interface — if meta-factor construction changes (Top-K → different aggregation), does the cache need rebuild? Minor.

So F5: agree with core, add (1) cost-model-as-data (re-priceable cache) is the real pivot insurance, (2) universe breadth ≠ free, (3) venue pivot cost hidden in bench cost model.

**Q5 Blind spot: the single most dangerous unexamined assumption**

Candidates:
1. Holdout contamination via iterative gate usage: The 90d holdout is being walked repeatedly (every week new candidates face it). It's only honest the FIRST time each window is used. With 100+ expressions/week over months, the holdout effectively becomes a validation set — selection on holdout erodes its OOS-ness. Round 1 addressed "holdout budget" — the user listed "holdout budget" as a fixed item, so maybe partially covered. The residual: even with counting, the SAME 90d window is reused for every candidate; once you deploy based on it, dry-run is the true OOS. Freqtrade dry-run = final arbiter. Is that a direction-change risk? If dry-run systematically contradicts holdout (regime change or gate leakage), the whole validation stack's credibility collapses — that IS a large-scale direction change trigger. But "holdout budget" fix presumably covers counting. The deeper unexamined thing might be:

2. Non-stationarity of crypto microstructure: costs/funding today ≠ costs at deployment scale; and 1m data lake — is it survivorship-bias-free (delisted pairs)? Universe construction on today's pairs embeds survivorship. For 6 majors, mild.

3. The "≥100 candidates/week" throughput itself is the unexamined assumption — engineering throughput ≠ information throughput. Covered by F1/effective-independent.

4. Data quality at 1m for 46M rows: gaps, exchange downtime, funding timestamps, mark vs last price for funding calc. Boring but classic source of everything-dies-at-holdout (same failure signature as thesis death!). If data bugs make all candidates fail, you read it as "gates working" (F1's trap). The discriminator is the positive control (F3). Covered indirectly.

5. RankIC as the bench metric for a TRADES-based gate: RankIC selects for cross-sectional predictive power, but the holdout gate is trade-count/PnL-based (time-series strategy behavior). Misalignment between selection metric (IC) and survival metric (net PnL after costs, trade frequency) means the optimizer mines IC-rich, trade-poor expressions — most candidates die not at costs but at the ≥30 trades floor. That's a structural throughput sink: the RL engine optimizes the wrong objective relative to the gate. THIS is potentially the biggest blind spot: the loop optimizes RankIC (rank correlation of factor values with forward returns) but survival requires enough round trips AND net-positive per-trade edge after taker+funding. High-IC factors are often slow/positional (few trades) → die at trade floor → wasted throughput → F1's "no survivors" arrives even though the engine "works." The fix is cheap-ish: multi-objective reward in AlphaGen (include turnover/trade-frequency and cost-penalized IC), or gate-relevant pre-filter. Is this covered by round-1 ("cost/funding in selection loop" — costs are IN the loop now, but trade-frequency/holding-period alignment may not be)? The listed fix was "cost/funding in selection loop" — that covers cost penalty, not necessarily trade-count alignment. I think this is my strongest blind-spot candidate: SELECTION-GATE MISALIGNMENT (objective = IC; gate = net-PnL-with-min-trades). Severity HIGH; it directly produces outcome (c)/(d) in Q6.

Wait, but is it true AlphaGen optimizes RankIC only? AlphaGen (ML4Algo) uses IC-based rewards, optionally with diversity. Yes, standard AlphaGen reward is IC-based (rank IC) with a diversity term. The user's bench does "RankIC + cost hard-filter". So costs are a hard filter AFTER mining, not in the RL reward (unless the round-1 fix put it in the reward — the listed fix says "cost/funding in selection loop," ambiguous between reward and filter). If costs are only a post-filter, the engine keeps generating cost-blind expressions and the kill-rate at cost filter could be 90%+ → throughput illusion. That's exactly the leading indicator I proposed in F1's checkpoint (cost-kill-rate). So blind spot ties to F1's instrumentation but is distinct: it's about WHERE cost/turnover pressure enters the optimization. I'll present it as: "the loop's optimizer objective and the survival gate measure different things; the population the RL engine produces is not the population the gate admits; measure admission funnel per stage (mined → IC-pass → cost-pass → trade-floor-pass → holdout-pass) from day one — the stage with the biggest attrition is where direction change will be forced."

Hmm, but honestly the strongest "looks settled but isn't" might be the holdout window reuse / walk-forward design: a FIXED 90d holdout vs ROLLING holdout. With a single fixed 90d window, all candidates are validated on ONE market regime slice. If that slice is 2026-Q2 chop or bull, survivors are regime-fits; dry-run then fails; trust collapse. A fixed-window holdout gives regime-specific answers. Rolling/multi-window holdouts cost more data but de-risk. Is this covered? "holdout gates (90d)" and round-1 "holdout budget" — budget is about how many candidates consume it, not regime coverage. I think regime-coverage of the holdout is genuinely unexamined and dangerous: it can invalidate the entire validation stack → large-scale direction change. But its fix is expensive (more data, longer). Alternatively the funnel-alignment issue.

The question asks for THE single most dangerous unexamined assumption. Let me decide: which one, if discovered wrong 3 months in, forces the largest pivot?
- Regime-slice holdout: discovery = "all our survivors were regime artifacts" → forces re-validation architecture change (rolling holdouts, longer windows) = validation-stack overhaul = exactly F5's "expensive core." Large.
- Objective-gate misalignment: discovery = "engine wastes throughput on unsalvageable candidates" → fix = reward re-engineering (AlphaGen reward modification) + re-mine = Medium-Large, and it manifests as F1's no-survivors grind.
- Both are good. The misalignment one is more certain to be at least partially true (AlphaGen's default reward is IC-only; even with cost hard-filter the REWARD is IC). The regime one is probabilistic.

I'll lead with the funnel/objective-gate misalignment as the single blind spot, and mention holdout-regime-slice as the runner-up in one line... but the format says ONE blind spot. The user says "the single most dangerous unexamined assumption." I can name one and add a one-line runner-up. Keep within word budget.

Actually, wait. Let me reconsider: is objective-gate misalignment truly "unexamined"? Round-1 fix: "cost/funding in selection loop" — if that means the RL reward now includes cost, then partially examined. The user wrote "cost/funding in selection loop" — selection loop suggests the bench selection, i.e., hard-filter. The phrase "incl. funding" appears in the bench description: "unified bench (RankIC + cost hard-filter incl. funding)". So costs are a hard FILTER in the bench, and RankIC is the score. The selection loop = bench selection. So the RL reward is presumably still IC-based. Misalignment stands. Also the ≥30-trade floor: RankIC-maximizing expressions on 1m-crypto with typical rebalancing... AlphaGen expressions are usually evaluated on daily-ish cross-sections. On crypto with 46M rows of 1m data... what's the evaluation horizon? Unclear, but if IC is computed at some horizon, expressions maximizing it may have arbitrary trade frequency. The trade floor then kills many. Yes, I'm fairly confident this is real and dangerous. Name it: "Objective–gate misalignment: RankIC reward + cost hard-filter + trade-floor gate select for different populations; nobody has measured the funnel attrition per stage."

Severity: HIGH. Cheap instrumentation: log funnel counts from M2 smoke onward.

**Q6: The bet**

Options:
(a) thesis holds, first survivors emerge
(b) cost wall kills everything → pivot maker-only/micro-structuring
(c) effective-independent throughput was the real constraint → pivot to hypothesis-source diversity
(d) abandon RL mining for seed-library + postmortem loop

Rank with probabilities (my honest priors for a solo-dev crypto alpha project):
- Base rates: most retail quant crypto alpha attempts don't produce deployable net alpha. But this setup has realistic gates and cost-awareness, which raises the chance of a clean diagnosis rather than false failure.
- (b) cost wall: on 1m-frequency crypto perps with taker fees + funding, cost wall is very likely to kill MOST candidates; whether it kills EVERYTHING depends on whether low-turnover candidates survive the trade floor. Given the trade-floor ≥30/90d forces minimum activity, and costs bite activity, the tension is real. I'd put meaningful probability on (b)-flavored partial outcomes, but full "kills everything" is less likely than "cost wall forces hybrid."
- (c): the effective-independent correction is already written in the docs (FR2.4) — so this is partly pre-acknowledged; the pivot to source diversity (GTJA191, papers, postmortem-driven hypotheses) is the natural response and cheap. Likelihood high that throughput independence becomes the binding constraint IF the engine works at all.
- (d): abandoning RL — plausible if AlphaGen output correlation is extreme and seed library outperforms; the ladder (L1/L2 degradation) already anticipates partial abandonment. Full abandonment to seed+postmortem is a real possibility.
- (a): thesis holds with survivors — possible but I'd put it below 50%.

Honest ranking, I'd say: (c) > (b) > (a) > (d)? Or (b) > (c)? Let me think. The single most predictable force: costs on active crypto strategies are brutal, and the gate requires ≥30 trades (active). Meanwhile the RL engine's independence deficit is already acknowledged in docs — meaning the team has partially pre-pivoted (source diversity is in F3). So (c) is partially underway regardless; as a "surprise that forces direction change" it's less surprising. The event that would actually force LARGE-SCALE change: discovering the funnel is cost-dominated → (b). But micro-structuring/maker-only on a solo Windows laptop setup is a big lift (queue position, colocation... realistically maker-only via limit orders in Freqtrade is feasible without colo, just harder to fill).

I'd rank: (b) ≈ (c) > (d) > (a), with (a) maybe 25-35%. Hmm, actually, let me commit: 1. (c), 2. (b), 3. (a), 4. (d)? Or should (a) be second? The system was designed specifically to fix the throughput failure of the predecessor; the predecessor died from throughput, and the fix targets that. The un-fixed residual is costs-at-frequency and objective misalignment. I'll rank: (c) most likely (the docs already concede it; source-diversity pivot is cheap and will happen), then (b) (cost wall manifests as huge cost-filter kill-rate; pivot to lower turnover/maker), then (a), then (d) (full RL abandonment less likely than demotion via ladder; AlphaGen stays as one channel). Note (c) and (d) are cousins; (d) is the terminal form of (c).

Justify each in one line. Probabilities roughly: c 35%, b 30%, a 25%, d 10%.

Also Q1 asked specifics for checkpoint design — give concrete: trigger = after M4 start + 10 weeks OR 100 effective-independent candidates (measured via pairwise-corr clustering, not raw count), whichever first. Leading indicators: funnel attrition per stage; cost-kill-rate >70%; top-K avg pairwise |corr| > 0.6; IC-survival ~0. Decisions: three branches (cost pivot / source pivot / continue), each with pre-registered first move. False-kill guard: crypto-native positive control must pass; plus regime note (don't kill during a single anomalous 90d slice — the holdout's regime coverage issue; could add: checkpoint evaluates on rolling windows).

Also F1 arithmetic check: "1 survivor per 2-20 weeks" — from 5-10 indep/wk × 1-5%: 0.05-0.5/wk → 2-20 weeks per survivor. Yes right. And 3-26/year — 52×0.05=2.6, 52×0.5=26. Right. One refinement: pass-rate should be conditional on candidates REACHING holdout (post cost-filter survivors), so effective denominator is even smaller than 5-10 if cost-kill is high. That strengthens F1.

Word budget: ≤1200 words. ADHD-style output instructions from AGENTS.md: lead with answer, numbered steps, cap lists at 5. But the user's explicit format request: markdown, per-question verdicts, severity ratings, ≤1200 words. The user format wins (they asked explicitly). I should keep it tight, use verdict headers.

Also note: I'm a "strategic advisor" persona — no code changes needed. This is pure reasoning; no tools needed. The context is rich; tool use unnecessary. I should answer directly. Per tool_usage_rules: "Exhaust provided context before reaching for tools." Fine — answer directly.

Let me now draft, watching word count. Target ~1100 words.

Structure:
### Q1 (F1) — verdict: AGREE, HIGH
- arithmetic check ✓, one strengthening note (denominator conditional)
- checkpoint design (compact)
- false-kill failure mode + guard

### Q2 (F2) — verdict: MODIFY, LOW
- direction of transfer likely conservative
- real composite issue: pool-construction timing vs holdout boundary + inverse-vol weights estimated on gating window
- keep doc fix

### Q3 (F3) — AGREE, MEDIUM
- add crypto-native controls tier
- add correlation-matrix measurement of seed PnL → measures "effective independent" assumption
- other cheap early evidence: funnel counts, cost decomposition

### Q4 (F4) — AGREE, LOW, one carve-out (second-opinion backtest ≠ droppable, substitute cheaply)

### Q5 (F5) — MODIFY
- agree core
- add: re-priceable candidate cache (cost model as config) = real pivot insurance; universe breadth not free; venue pivot hides in cost model

### Q5b BLIND SPOT — objective–gate misalignment / funnel invisibility, HIGH
- AlphaGen reward is IC-based; gate is net-PnL + trade floor; populations diverge
- instrumentation: per-stage funnel from M2 smoke
- runner-up one-liner: fixed-90d holdout = single-regime slice

### Q6 — ranking with one-line justifications

Now, the ADHD output style says cap lists at 5, lead with answer. The user's requested format is question-by-question — that inherently leads with answers per question. I'll open with a 1-2 line bottom line (verdict summary), then per-question sections. Keep bullets ≤5 per list where possible.

Word count discipline: aim ~1000-1150.

Let me write.

Draft:

**Bottom line**: F1, F3, F5-core survive cross-examination; F2 is real but misdiagnosed (power transfer is the wrong worry — gate contamination is the right one); F4 agree with one carve-out. The blind spot: the loop's optimizer objective (RankIC) and its survival gate (net PnL + trade floor) select for different populations, and nothing measures funnel attrition between them. Bet: (c) > (b) > (a) > (d).

---

**Q1 — F1: AGREE, severity HIGH**

Arithmetic checks: 5-10 indep × 1-5% = 0.05-0.5 survivors/wk → 1 per 2-20 weeks, 2.6-26/yr. It's actually worse than stated: 1-5% pass rates are conditional on candidates reaching holdout; the cost hard-filter shrinks the denominator further. "First pass" is a heavy-tailed wait, and M4 has no clock.

Checkpoint design (concrete):
- Trigger: whichever comes first — 10 weeks after M4 start, or 100 effective-independent candidates. Independence must be MEASURED (cluster OOS PnL correlation, count clusters), not asserted from docs.
- Leading indicators (log from M2 smoke): per-stage funnel (mined → IC-pass → cost-pass → trade-floor-pass → holdout-pass); cost-kill rate; avg pairwise |corr| of top-K; IC-survival rate.
- Decision branches, pre-registered: cost-kill > ~70% or cost stage dominates attrition → cost pivot (lower turnover / maker-first); IC-survival ≈ 0 and top-K corr high → hypothesis-source pivot; ≥2 credible (69+) survivors → continue.
- Unlock rule: trigger alone doesn't kill — it forces a one-week structured review with the three branches; "continue" must be re-justified in writing.

False-kill failure mode: two of them. (1) Bench/data bug: everything dies for the wrong reason and reads as thesis death. Guard: the kill is only valid if a crypto-native positive control (funding carry, simple momentum) PASSES the full gate in the same window. (2) Regime: one 90d slice can be alpha-hostile; kill decisions should look at rolling windows, not the single fixed slice. GTJA191 non-transfer is NOT evidence of thesis death — tier seed interpretations.

**Q2 — F2: MODIFY, severity LOW (as power), MEDIUM (the real issue)**

Refute the framing: at 30-69 trades, the composite-vs-single difference is second-order. Combining decorrelated signals raises per-trade Sharpe, so the ≥30 floor is likely conservative for composites, not optimistic — error direction favors you. Per-trade edge needed at t≈2 is ~0.24σ (N=69) to ~0.37σ (N=30); that dwarfs transfer error.

The composite issue that DOES matter: where is the synergy pool built relative to the holdout boundary? If pool construction/Top-K selection touches data inside or overlapping the 90d window, the gate is contaminated — composites get an in-sample advantage singles never had, and thresholds become theater. Second: inverse-vol weights estimated on the gating window inject mild optimism into the gate itself. Keep the doc fix; add one sentence pinning pool-construction data boundary to pre-holdout only.

**Q3 — F3: AGREE, severity MEDIUM**

Highest info/day: yes, and two upgrades make it more decisive:
- Tier the controls: crypto-native (funding carry, cross-sectional momentum on majors) must-pass → these calibrate the bench; GTJA191 subset = exploratory prior, non-transfer ≠ diagnosis. If funding carry dies at the cost filter, that's week-2 evidence for a cost wall (outcome b).
- Compute the OOS PnL correlation matrix of the seed library: this converts "effective independent ≈5-10/wk" from a doc assertion into a measured baseline that AlphaGen output must beat. Cheapest possible test of outcome (c).
Also cheap and early: cost decomposition per pair (taker vs funding vs slippage share of gross) and RankIC stability across 1h/4h/1d horizons — both directly inform a frequency pivot before you're committed.

**Q4 — F4: AGREE, severity LOW**

One carve-out: the second-opinion backtest function is correctness insurance, not research-UX; keep a cheap substitute (recompute a handful of gate decisions with a second implementation on a subset) available if bench-bug suspicion arises. Everything else in M3 — declare droppable in writing now.

**Q5 — F5: MODIFY (mostly agree)**

Map is right with three corrections:
1. The lake is frequency-pivot-proof but only 6 pairs: breadth expansion (adding alts) is a Medium task — backfill, liquidity/cost re-validation per pair. Not free.
2. Venue/fee pivot is hidden inside the bench cost model. If the cost model isn't config-separated and versioned, a maker-only pivot means re-running the entire candidate history. The single best pivot-insurance artifact: store per-candidate gross trade logs so the population can be re-priced under a new cost model in hours. If the bench stores only pass/fail, you've rebuilt the expensive core by accident.
3. Perp→spot pivot changes shortability and factor viability, not just costs — second-order but nonzero.

**Q5b — BLIND SPOT: objective–gate misalignment (HIGH)**

AlphaGen's reward is IC-based; your gate is net-PnL-after-costs plus a ≥30-trade floor. These select different populations: IC-maximizing expressions skew slow/positional and cost-blind, then die at the trade floor or cost filter — the engine manufactures throughput the gate structurally rejects. Symptom: exactly F1's green-grind-no-survivors, but the cause is fixable inside M2 (add turnover/trade-frequency and cost-penalized terms to the reward, or pre-filter on the reward side). Round 1 put costs in the selection loop as a filter; nobody verified the REWARD and the GATE admit the same population. Instrumentation: funnel counts per stage from the 2-day smoke, not after.

Runner-up (one line): the fixed 90d holdout is one regime slice; every survivor is regime-conditional, and a dry-run contradiction would invalidate the validation stack — the expensive core per your own F5.

**Q6 — The bet**

1. (c) ~35% — the docs already concede it (FR2.4); the source-diversity pivot is cheap and F3 effectively starts it. Least surprising, most likely.
2. (b) ~30% — the ≥30-trade floor forces activity; activity meets taker+funding costs; the tension is structural. Maker/low-turnover pivot is the natural escape.
3. (a) ~25% — the gates are honest, which raises the chance a survivor, once found, is real.
4. (d) ~10% — full RL abandonment less likely than demotion: the L1/L2 ladder already institutionalizes partial retreat; AlphaGen stays as one channel.

Note (c) and (d) are the same force at different terminal states; if the measured seed-library independence beats AlphaGen's by >3× in M1, move (d) up.

---

Word count check — I'll estimate this is around 1050-1150 words. Need to trim a bit maybe. Also check list caps: Q1 has a 5-bullet list (trigger, indicators, branches, unlock, false-kill) — that's 5, fine.

One more sanity check on F1 arithmetic strengthening: "1-5% pass rate conditional on reaching holdout" — is that stated? The docs say honest OOS pass rate 1-5% for tested hypotheses. Reasonable to note the conditional. Hedge lightly: "if the 1-5% is conditional on reaching holdout..." — I'll phrase it as a strengthening conditional, not a claim about their docs.

Also per-trade edge math: t = mean_trade/std_trade × √N ≥ 2 → mean/std ≥ 2/√N. N=69 → 0.241; N=30 → 0.365. Correct.

Formatting: user asked markdown, per-question verdicts, severity ratings, ≤1200 words. ADHD style wants lead-with-answer — my bottom line does that. Also "next action under two minutes" ending — the AGENTS.md says end with one next action doable in <2 min. I can add a single final line: "Next action: add funnel-count logging to the M2 smoke checklist (10 min)." That satisfies the house style without bloating.

Let me finalize with tight wording.
**Bottom line:** F1, F3, F5-core survive cross-examination. F2 is real but misdiagnosed — power transfer isn't the worry, gate contamination is. F4 agree, one carve-out. The blind spot: optimizer objective and survival gate select for different populations, and nothing measures funnel attrition between them. Bet: (c) > (b) > (a) > (d).

---

## Q1 — F1: AGREE, severity HIGH

Arithmetic checks: 5–10 indep/wk × 1–5% = 0.05–0.5 survivors/wk → 1 per 2–20 weeks, ~2.6–26/yr. It's slightly worse than stated: if the 1–5% is conditional on candidates *reaching* holdout, the cost hard-filter shrinks the effective denominator further. "First pass" is a heavy-tailed wait; M4 has no clock.

Checkpoint design (concrete):

1. **Trigger**: whichever first — 10 weeks after M4 start, or 100 effective-independent candidates. Independence must be *measured* (cluster OOS PnL correlations, count clusters), not asserted from docs.
2. **Leading indicators** (log from M2 smoke onward): per-stage funnel counts (mined → IC-pass → cost-pass → trade-floor-pass → holdout-pass), cost-kill rate, avg pairwise |corr| of top-K, IC-survival rate.
3. **Pre-registered branches**: cost-kill > ~70% or cost stage dominates attrition → cost pivot (lower turnover / maker-first). IC-survival ≈ 0 and top-K corr high → hypothesis-source pivot. ≥2 credible (69+) survivors → continue.
4. **Unlock rule**: trigger alone doesn't kill — it forces a one-week structured review against the branches; "continue" must be re-justified in writing.

**False-kill failure modes (two, not one):** (1) Bench/data bug — everything dies for the wrong reason and reads as thesis death. Guard: a kill is only valid if a crypto-native positive control (funding carry, simple momentum on majors) *passes* the full gate on the same window. (2) Regime — one 90d slice can be alpha-hostile; kill decisions must inspect rolling windows, not the single fixed slice. And GTJA191 non-transfer is *not* thesis evidence — tier seed interpretations.

## Q2 — F2: MODIFY — LOW severity as power, MEDIUM as contamination

Refute the framing: at 30–69 trades, composite-vs-single transfer error is second-order. Combining decorrelated signals *raises* per-trade Sharpe, so the ≥30 floor is likely conservative for composites — the error direction favors you. Calibration: t≈2 requires per-trade edge ~0.24σ at N=69, ~0.37σ at N=30; that dwarfs transfer error.

What actually matters about composites: **where is the synergy pool / Top-K selection built relative to the holdout boundary?** If pool construction touches data inside or overlapping the 90d window, composites get an in-sample advantage singles never had and the thresholds become theater. Second: inverse-vol weights estimated on the gating window inject mild optimism into the gate itself. Keep the doc fix; add one sentence pinning pool construction to pre-holdout data only.

## Q3 — F3: AGREE, severity MEDIUM

Highest info/day: yes. Two upgrades make it decisive:

- **Tier the controls**: crypto-native (funding carry, cross-sectional momentum) = must-pass calibration anchors — if funding carry dies at the cost filter, that's week-2 evidence for a cost wall. GTJA191 subset = exploratory prior only.
- **Compute the seed library's OOS PnL correlation matrix**: this converts "effective independent ≈5–10/wk" from a doc assertion into a measured baseline AlphaGen must beat. Cheapest possible probe of outcome (c).

Also cheap and early: cost decomposition per pair (taker vs funding vs slippage share of gross alpha) and RankIC stability across 1h/4h/1d horizons — both inform a frequency pivot before commitment.

## Q4 — F4: AGREE, severity LOW

One carve-out: the *second-opinion backtest* function is correctness insurance, not research-UX. Keep a cheap substitute (recompute a handful of gate decisions with a second implementation on a subset) available for bench-bug suspicion. Declare the rest of M3 droppable in writing now.

## Q5 — F5: MODIFY (core holds)

Three corrections:

1. The lake is frequency-pivot-proof but only **6 pairs** — breadth expansion is a Medium task (backfill + per-pair liquidity/cost re-validation). Not free.
2. **Venue/fee pivot hides inside the bench cost model.** If cost parameters aren't config-separated and versioned, a maker-only pivot means re-running the entire candidate history. Best pivot-insurance artifact: store per-candidate *gross trade logs* so the population can be re-priced under a new cost model in hours. If the bench stores only pass/fail, you've rebuilt the expensive core by accident.
3. Perp→spot changes shortability and factor viability, not just costs — second-order but nonzero.

## Q5b — BLIND SPOT: objective–gate misalignment (HIGH)

AlphaGen's reward is IC-based; your gate is net-PnL-after-costs plus a ≥30-trade floor. These select *different populations*: IC-maximizing expressions skew slow/positional and cost-blind, then die at the trade floor or cost filter — the engine manufactures throughput the gate structurally rejects. The symptom is exactly F1's green-grind-no-survivors, but the cause is fixable inside M2: add turnover/trade-frequency and cost-penalized terms to the reward, or pre-filter on the reward side. Round 1 put costs in the selection loop as a *filter*; nobody verified the reward and the gate admit the same population. Funnel counts per stage from the 2-day smoke — not after.

Runner-up (one line): the fixed 90d holdout is one regime slice; every survivor is regime-conditional, and a dry-run contradiction would invalidate the validation stack — your own F5 expensive core.

## Q6 — The bet

1. **(c) ~35%** — FR2.4 already concedes it; the source-diversity pivot is cheap and F3 effectively starts it. Least surprising, most likely.
2. **(b) ~30%** — the ≥30-trade floor forces activity; activity meets taker+funding costs; the tension is structural. Maker/low-turnover is the natural escape.
3. **(a) ~25%** — honest gates raise the odds that a survivor, once found, is real.
4. **(d) ~10%** — full RL abandonment less likely than demotion; the L1/L2 ladder institutionalizes partial retreat, AlphaGen stays a channel.

(c) and (d) are one force at different terminal states. If the M1 correlation matrix shows the seed library beats AlphaGen independence by >3×, promote (d).

---

**Next action (<2 min):** add "log funnel counts per stage" as a line item on the M2 smoke-gate checklist.
