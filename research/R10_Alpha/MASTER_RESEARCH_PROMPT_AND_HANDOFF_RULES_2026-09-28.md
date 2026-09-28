# R10 Alpha — Active Master Research Prompt, Acceptance Gates, MT5 Report Contract and Handoff Rules

**Scope:** XAUUSD, January–July 2026; August SEALED. **Branch:** `alpha`. **Status:** owner-governing workflow only. This file does not imply a candidate passed, an EA was built or MT5 was run.

**Authorities:** [Live Master Protocol (active canonical prompt Section 99; governance Sections 112, 114–115)](https://docs.google.com/document/d/1ycB5bQ3P24w7BZz54RwgJbc5CX5aRcqgr0KiI0Iidkw/edit); [Master Research Prompt / Reconstruction Protocol](https://docs.google.com/document/d/13xrtChGvE2MCpezzi2wN9alxHYE2NkGOweu8Fi2EJnk/edit); [Active Alpha handoff](https://docs.google.com/document/d/14ElgUCCXZeu7y4go9RAR5-v06rU_yOPqskQCCsqPRA4/edit); [CURRENT_STATE](../../CURRENT_STATE.json). Read newer explicit user directions before stale January-only/prelaunch text.

**Live canonical Alpha prompt mirror:** [MASTER_RESEARCH_PROMPT_CANONICAL.md](MASTER_RESEARCH_PROMPT_CANONICAL.md) replaces the former Gamma startup prompt inside Section 99. The old R9B Gamma prompt was archived under [archives/GAMMA_SECTION99_ORIGINAL_MASTER_PROMPT_ARCHIVE_2026-09-28.md](archives/GAMMA_SECTION99_ORIGINAL_MASTER_PROMPT_ARCHIVE_2026-09-28.md).

## 1. Storage and MT5 report hard limit

- **New MT5 tests are executed locally by the owner.** There is no direct Carson ↔ Coinexx terminal connection.
- The owner configures **XAUUSD, M1 chart/test/report timeframe**, selecting the MT5 test model **“Every tick based on real ticks”**. This is NOT “Open prices only,” “1-minute OHLC,” or “Every tick” generated path. MT5's tester internally handles available broker ticks despite M1 being the reporting/chart timeframe.
- Owner provides **normal reasonably sized Strategy Tester reports only** (HTML / XLSX or a compact equivalent). One-minute reporting is sufficient. Do **not** request new tick-by-tick MT5 log exports, per-tick execution traces, 6-way split GZIP archives, enormous tester tables, raw Coinexx history or files that exhaust Drive or chat upload limits.
- Original **historical R9 REAL/SYNTH** logger archives and their daily indexes remain read-only research sources already available. They are not a requirement to regenerate for every approved EA test.
- Compare *report-level* net, gross P/L, PF, trade count, DD, winning/losing trade statistics, test dates, inputs, account and broker costs. Standard M1 tester reports alone **cannot prove exact tick-by-tick Python ↔ MQL5 parity**, so describe their evidentiary status as **broker-specific aggregate real-tick backtest comparison**, not exact millisecond execution equivalence. Additional small diagnostics require separate owner permission.
- Do not copy raw Dukascopy tick sources, numeric memmap caches, or archived R9 logs into GitHub or duplicate them in Drive. Commit only compact metrics, provenance, code, monthly results, decisions, and original-data hashes.

## 2. Current research environment and roles

- The [Dukascopy Python month-block engine](../../scripts/r10_alpha_dukas/) is initialized; [engine guide](DUKAS_BACKTEST_ENGINE_README.md); [source/bar audit](../../results/R10_Alpha/DUKAS_SEVEN_MONTH_SOURCE_BAR_AUDIT.json). Preserve strict chronological original Bid/Ask, 1-position arbitration and state continuity across months.
- Requested tick-derived analysis intervals: **250 ms, 1 / 5 / 15 / 30 / 45 s; M1 / M5 / M7 / M15 / M30 / M45; H1 / H4 / H12 / D1**. All causal market information must be available at the decision timestamp. The M1 MT5 tester chart setting does not restrict the eventual EA from maintaining custom sub-minute internal state.
- **R9 REAL:** historical MT5 real-tick tester execution behavior. **R9 SYNTH:** generated-tick aspirational profit and velocity target, not an asserted attainable return. **R9 OVERFIT:** hindsight research oracle illustrating favorable trade direction, excursion, persistence and exit, not decision-time input or a guarantee. **Dukascopy:** independent research feed, not Coinexx tester ticks.
- Workstreams: **ENTRY, HOLD, EXIT, PROFIT**. Preserve reproducible mechanisms, explicit risk/survivability tradeoffs, the $100–$500 starting-account tests and every trading/no-trade day in daily/weekly/monthly reporting. Freeze forward/holdout evaluation rules before testing claims about OOS.

## 3. Two strict research candidacy gates

| Class | Gate |
|---|---|
| System-wide strategy | Strictly **greater than 10%** improvement in a **predeclared valid overall-performance measure** versus the **latest owner-approved cumulative EA** under matched dates, costs, sizing, exposures and risk rules. |
| Individual Entry / Hold / Exit / Profit module | Strictly **greater than 10%** improvement in its **predeclared category-specific KPI** relative to the matching module of the approved cumulative EA, without unacceptable decline in whole-account profitability, risk, survivability, trade frequency or other categories. |

The owner has not locked one universal profit/risk composite formula or per-category denominator. **Do not invent one as an established requirement.** Freeze each candidate's KPI/denominator before evaluation. A reduction in gross loss is not an equal percentage improvement in whole-system profit. A negative/zero/negligible net-profit baseline does not support naive percent-return improvement; specify a mathematically valid, prespecified measure, mark undefined ratios and report absolute deltas. Always show before/after numbers, GP, GL, net, PF, DD, trades, loss concentration and day/week/month results. The gate means **candidate for owner review, not approval**.

## 4. Human gate and incremental approved EA chain

1. Run causal Dukascopy Python test and category/system ablations against an explicitly identified approved EA control; freeze source/method and report all months and failure days. A candidate must clear its matching threshold and regression safeguards.
2. Write a compact breakthrough card: candidate ID; what changed versus approved incumbent; formulas and causal timeframes; source/data hashes; category KPI, denominator, sample periods and independent validation status; matched costs; original baseline and candidate net/gross/risk/velocity; versioned code reference and failures.
3. **Owner reviews BEFORE authorizing MQL5 coding.** Do not assume a pass automatically authorizes it.
4. Upon authorization, implement *only that approved candidate* ON TOP OF the **latest owner-approved cumulative EA**, retaining prior approved modules and versioned rollback.
5. Owner performs local Coinexx **M1-report, internally real-tick** MT5 tester run, supplies standard report. Compare to old approved EA tested with matched parameters. No requirement for new per-tick logs.
6. Owner explicitly accepts or rejects **after** MT5 report review. Only an accepted version becomes the **next approved baseline**. Failure leaves the previous EA intact. Repeat the cycle incrementally without resetting to original R9.
7. Report **distance to R9 SYNTH** separately from the >10% acceptance thresholds. Use **R9 OVERFIT** to investigate hindsight-success features, then causally reconstruct; no future-label leakage.

## 5. New-chat / long-running session handoff

On resumption read these live Google Docs, `alpha/CURRENT_STATE.json`, this contract, the exact committed source-manifest hashes and recent candidate ledger. Verify what actually ran; do not repeat already completed setup because of a chat interruption. Preserve approved EA identifier/commit, baseline cost/window/KPIs, the last authorized candidate, human-review status, M1 MT5 report links and the next incomplete action. If no owner-approved Alpha EA has been designated yet, explicitly say **“approved baseline not yet designated”** rather than inferring approval from R9 or prior Gamma research. Keep source models and results labeled **historical R9 / Dukascopy Python / Coinexx real-tick MT5 / demo / live**. Do not promote a model on in-sample gain, oracle hindsight or generated SYNTH results. Keep August sealed and avoid duplicate gigabyte assets.

**Current position:** Seven-month Dukascopy tick research infrastructure is tested; the four-category candidate campaign and first qualifying >10% breakthrough have not been launched/established by this workflow update. No MT5 build or test was conducted as part of updating these rules.
