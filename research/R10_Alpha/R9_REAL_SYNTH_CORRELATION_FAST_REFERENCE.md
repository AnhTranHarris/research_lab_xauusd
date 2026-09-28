# R10 Alpha — R9 REAL ↔ SYNTH Correlation: Fast Reference v1
**Evidence class:** historical paired-R9 analysis, audited against available original MT5 tester headers; **NOT new Alpha strategy validation or a fresh replay of 14 full monthly ticklog files.** **Scope:** XAUUSD, 2026-01 through 2026-07; August SEALED. **Next state:** four-category research architecture prepared, not launched.

## Original tester baseline — newly header-checked from locally mounted full MT5 workbooks
Both: Coinexx-Demo build 6182; GoldMuwahahaMiner_R9_TickLogger; XAUUSD M1 (2026-01-01–2026-07-31); 0.01 lots; $100,000 original tester initial deposit, leverage 1:500; `InpMaxHoldSeconds=30`; separate REAL/SYNTH run labels.
| MT5 metric | REAL: based on real ticks | SYNTH: generated “Every tick” |
|---|---:|---:|
| tester ticks | 56,608,185 | 54,655,160 |
| completed M1 bars | 204,625 | 204,625 |
| trades | 236,647 | 219,342 |
| winning trades | 102,385 | 191,136 |
| win rate | 43.26% | 87.14% |
| net profit, USD | -50,285.28 | +309,122.85 |
| gross profit, USD | +30,180.23 | +325,361.51 |
| gross loss, USD | -80,465.51 | -16,238.66 |
| profit factor | 0.375070 | 20.036229 |
| tester mean hold (formatted report) | 00:00:05 | 00:00:16 |
Trade counts/net/GP/GL/PF come directly from the **report summary**, not the Gamma CAUSAL014 reconstruction or the deliberately overfit reference. R9 SYNTH is an *aspirational generated-tick benchmark*, not executable-real-tick P&L or evidence of a viable strategy. Header-only audit does NOT imply a fresh full-trade recomputation.

Local original tester copies:
- REAL `/mnt/data/ReportTester-871471_jan2026_jul2026_R9_ticklog_real(4).xlsx`; SHA-256 `19d5ffd785beaae2a9d0baa5efb50efcd36a7db635c7ef82957be442429c1064`; duplicate `(3)` copy matches exactly.
- SYNTH `/mnt/data/ReportTester-871471_jan2026_jul2026_R9_ticklog_synth(4).xlsx`; SHA-256 `e5fcf4d6879193fac88e7a8e101db1111d59e1a7f5abfb793c970b06cfce7cc7`; duplicate `(3)` copy matches exactly.
- Immutable original Drive report folder: https://drive.google.com/drive/folders/1FeQSPtlWXtgncXE6bsCtWNlKFS9t17Pr

## Previously validated seven-month correlation corpus — compact key statistics
Historical source: [paired R9 corpus](https://drive.google.com/drive/folders/1ES78vXb2mFsOsa50BiwCLsT6BXgLe-Oe), its README, and its **small CSV summaries** under `06_ANALYSIS`. These coefficients are *reused source-reported results*, not independently re-executed on the raw tick logger files in this Alpha turn. `r` = Pearson correlation for same-time/paired measurements; entry-minute Jaccard = intersection/union; pairing is analytical approximation, **not proof of identical causal trades**.

**Shared market structure:** 204,625 common M1 intervals; Bid OHLC, minute return, range and ATR match exactly in the prior study (`r≈1`). Minute tick count `r=0.988800`; gate-open share `r=0.868496`. **Different path:** path length `r=0.910361`, but mean intraminute traveled distance SYNTH 6.2264 vs REAL 19.1899 price units; absolute path efficiency SYNTH 0.2370 vs REAL 0.08773; mean spread `r=0.382858`.

**Entry/event transfer:** per-minute entry-count `r=0.341097`; 141,027 common entry minutes, minute Jaccard `0.758230`; same-minute side agreement `61.263%`. Original trade totals differ by 17,305 (REAL more). Pairing **same-minute/same-side/ordinal** in later canonical `SYNTH_REAL_trade_pair_correlation.csv` produces **165,630 research pairs**; a less restrictive earlier minute+ordinal pairing yielded **169,889**, which must not be conflated.

**Hold/exit transfer (full trade populations unless marked):** median holds SYNTH 17.7325 s vs REAL 2.995 s; trailing activated SYNTH 86.290% vs REAL 46.794%; survival to 20 s SYNTH 43.143% vs REAL 4.725%; early/base stop exit rate SYNTH 13.206% vs REAL 51.475%. Pair-conditioned correlations: hold `r=0.706665`, MFE `r=0.264394`, MAE `r=0.106738`, trade P&L `r=0.213223`. Only about 52.36% of matched paired trades agree in win/loss state. Distinguish paired-trade conditional medians/rates from full-population medians/rates.

### Month-by-month compact correlation flags
These are **historical paired R9 aggregates** (not Alpha experiments or fresh cross-month model validation).

| Month | common M1 minutes | minute entry count r | paired trades | paired P&L r |
|---|---:|---:|---:|---:|
| Jan | 28,820 | 0.331 | 20,886 | 0.132 |
| Feb | 27,440 | 0.300 | 26,001 | 0.142 |
| Mar | 30,358 | 0.250 | 31,473 | 0.196 |
| Apr | 28,961 | 0.322 | 23,962 | 0.417 |
| May | 28,809 | 0.331 | 21,175 | 0.200 |
| Jun | 30,120 | 0.334 | 23,658 | 0.196 |
| Jul | 30,117 | 0.384 | 18,475 | 0.326 |
| TOTAL | 204,625 | 0.341 (pooled) | 165,630 | 0.213 (pooled) |

**Quant conclusion (hypothesis, not causality claim):** completed M1 envelopes and broad regime/activity covary tightly, but intra-minute temporal order, directional opportunity ownership, short holding, stop/trail triggering and payoff do not transfer reliably from SYNTH to REAL. This is a *mechanism-prioritization inference* only: correlation alone does not prove why, or tell us which causal remediation will profit.

## Four future research programs (do not auto-launch)
**1 ENTRY:** which realtime R9/alternative event should be taken, which direction, at which Bid/Ask price and first eligible tick? Track eligibility, side agreement, event parent ID, reject reasons, missed winners, per-regime outcome; compare against all raw eligible events rather than survivor-selected winners.
**2 HOLD:** which observable sequence supports staying in a position for 2–30s versus early failure? Use ticks, 250ms/S1/S5/S15/S30/S45, completed higher bars, excursion path efficiency, turns, spread, persistence; quantify loss tail and survivability.
**3 EXIT:** distinguish bar-close visibility from intra-tick stop/trail/target priority; test adverse-stop geometry, profitable trail activation, recovery and stall/failed-acceptance states with one account and chronological tick ordering.
**4 PROFIT:** trade P&L net of executable spread/commission/slippage, expectancy and GP/GL/PF/drawdown/daily stability/throughput, $100–$500 survivability, variance and out-of-sample. Never substitute generated SYNTH profit for REAL attainable payoff or sum overlapping sleeve P&Ls.

For EACH category require causal mathematical/state definition, exact tick/higher-bar visibility, consistent broker-time alignment, 250ms→day reconstruction compatibility, duplicate-ms tick handling, Python↔MQL5 replay parity, and a frozen test plan. Research by day/week/month across Jan–Jul; classification of any month as untouched OOS must be explicitly justified and frozen, **not assumed**. August SEALED.

## Fast retrieval & cache contract (save space and prevent polling failures)
1. **Local /mnt/data** has seven separate Dukascopy market gzip archives (January–July) and both original MT5 Excel tester workbooks. The local Project attachment presence was checked this turn. These are distinct streams: Dukascopy MARKET ≠ R9 MT5 EA tick logs.
2. Drive original Dukascopy: https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV ; MT5 six-part each REAL/SYNTH: https://drive.google.com/drive/folders/1CidEgLMNVfgBZg6UYLYqcanc0oqgt9Vj . Only partial original R9 transport files are locally mounted; retrieve exact missing parts/daily indexed files from Drive IF actual tick-level reconstruction requires them.
3. **Use tiny existing 06_ANALYSIS CSV files first; do NOT re-download/recompute giant inputs just to rediscover the historical baseline**:
   - Minute alignment `SYNTH_REAL_minute_correlation.csv`: https://drive.google.com/file/d/1OvDIpXinnokdclVxGxbI2FzCyEb-LYLm/view
   - Full minute paths `SYNTH_REAL_intraminute_path_correlation.csv`: https://drive.google.com/file/d/1qoWqLwxv8tvG26F4JPPGlNxJcFa69VNg/view
   - Strict paired trades `SYNTH_REAL_trade_pair_correlation.csv`: https://drive.google.com/file/d/1s_vI-2B8iBINi4PuswZBtW4bIbyNQUUF/view
   - Lifecycle `SYNTH_REAL_lifecycle_summary.csv`: https://drive.google.com/file/d/1bTTaPktK65rltP8aeUF5uJymLWGn7vPp/view
   - Feature correlation `R9_SYNTH_REAL_TRANSFER_FEATURE_CORRELATIONS.csv`: https://drive.google.com/file/d/1zYGXg06PTrss0Co0dqhHBTRYFOxKJ6QB/view
   - Validation/reassembly instructions: https://drive.google.com/file/d/1-MH0CasorKt11v_1jsDsb43b0o7sM5vC/view
4. Governing: https://docs.google.com/document/d/1ycB5bQ3P24w7BZz54RwgJbc5CX5aRcqgr0KiI0Iidkw/edit (live Section 112) ; Alpha state `CURRENT_STATE.json` and `research/R10_Alpha/TEMPORAL_RECONSTRUCTION_CONTRACT.md`. R9 historical teacher reference: https://docs.google.com/document/d/18Ru-eSQ0ofNM2EvvSp5kaenZEML3KC5GRk8KrAN_SWs/edit .
5. Keep **ONE small fast reference** and versioned compact source manifests and daily/weekly/monthly summaries; use stored content hashes and exact IDs to resume. Never duplicate all raw ticks or large report workbooks into Google Docs or GitHub. Read only the needed month/day for exact tests, resume from durable checkpoints after interruptions. Never mix source roles or historical teacher forward labels.
6. **Status:** historical correlation structure assembled + tester headers and attachment hashes verified in this chat. Full new Alpha real/SYNTH tick-pair replay, independently recalculated coefficients and daily/weekly numeric reconciliation NOT YET performed. This fast reference must not be cited as a fresh Alpha tick replay. No four-category strategy experiments authorized or executed yet.

