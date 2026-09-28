# ALPHA CLEAN RESTART — initial ENTRY + HOLD accuracy study (preregistration BEFORE outcome calculation)

## Owner-authorized scientific reset and contamination boundary
The user explicitly requested a reset to BEFORE the wrong Gamma bootstrap influenced Alpha discovery. The Jan-2026 `ENTRY_HOLD_DISCOVERY_001` study's six parameter configurations, selected hypotheses, interpretations and proposed 002 follow-up are **QUARANTINED** and may not become the clean study's benchmark or strategy parent. Keep immutable records and original data; no result may be deleted, silently reused or relabeled. The January 001 family had M15/M30/H1 2-of-3 structural vote, 5-second chase and filtered pullback; **none of those rules are included in this clean experiment**. The eight-day R9 original REAL↔SYNTH historical markout report is independently **REFERENCE-ONLY**; this study will not fit/optimize on future R9 outcomes or synthetic paths.

Audited, Alpha-only raw-data ingestion / bar-builder and bid/ask tick portfolio are permitted **only after integrity checks and independent unit tests**: engine was created to parse timestamped original Dukascopy market ticks, not the Gamma signal/model pipeline. Source data and market-feed identity are not invalidated by an erroneous governance link. Use only the original January Dukascopy SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5` and never read sealed August. February–July **UNINSPECTED FOR THIS CLEAN STRATEGY** until a frozen, separate future validation plan is submitted. January was previously viewed for other experiments and is exploratory/in-sample, NOT untouched holdout.

## Scientific question — no Gamma strategy inheritance
On a **clock-defined**, source-independent event population, do simple causal five-second quote movement continuation, reversal or two-step agreement predict **early executable after-spread/fee** direction, and how does outcome change at 1, 3, 10, 20, 30 and 60 seconds? These are neutral H0/H1 price-response tests, not proposed approved strategies, and not replications of old 001's 2-of-3 higher-timeframe chase/pullback filter.

## Frozen event universe and feature rules
1. One candidate at each UTC minute's **first 5-second bar close**, exactly `end_ms % 60000 == 5000`, if the current bar and preceding two five-second buckets each contain ≥2 real ticks, are contiguous, and all are from the same source month. **No synthetic gap candles**, one root per minute. No overlap inside 60-second horizon.
2. At end timestamp `T`, bar [T−5000,T) is completed. Define `delta = bid_close(T)−bid_close(T−5000)` in raw 1/1000 USD units. Require `abs(delta)>=500` ($0.50) and completed observed bar close spread <=$1.25. The previous bar direction is `sign(bid_close(T−5000)−bid_close(T−10000))`. All available by time T. The first admissible fill tick must have `time_msc>=T` and entry spread <=$1.25, and be observed <=1 second after T; otherwise skip and count no-fill. Do not choose event time using future price movements.
3. `FLOW_CONTINUE`: side = sign(delta).
4. `FLOW_FADE`: side = −sign(delta), on the **identical root timestamps**, no asymmetric event filtering.
5. `FLOW_AGREE`: side=sign(delta) only if prior adjacent completed 5s change is same sign and magnitude >=$0.15. Track smaller eligible subset explicitly rather than comparing unmatched wins as if matched.
6. `CALENDAR_NULL`: deterministic, nonmarket side=+1 on even Unix-minute number, −1 on odd, on the identical root timestamps. This is NOT an approved trading policy, only a diagnostic benchmark.

## Frozen execution/markout and holding metrics
At the first executable tick after completed five-second signal, BUY at Ask +$0.05 slippage; SELL at Bid −$0.05 slippage, 0.01 lot, 100oz/lot = **1oz exposure**. For each horizon H∈{1,3,10,20,30,60} seconds after entry, choose the FIRST tick at/after `entry_time+1000H` if <=1000ms late; exit BUY at that tick's Bid−$0.05, SELL at Ask+$0.05. Deduct **$0.20 round-trip commission** from each one-ounce net P&L. If horizon data unavailable within 1000ms, mark MISSING (no favorable forward fill or invented observation). Outcomes and missing counts reported per H and per hypothesis.

For each event: positive-net markout fraction, mean/median net dollars per 0.01 lot, gross gain, gross loss, PF, fraction of root opportunities retained, long/short mix, and a 30-second maximum-favorable / maximum-adverse-executable-excursion distribution. Holding diagnostics include transitions between positive at 1,3,10,30,60 seconds and the share of initially negative events recovering, with P&L and coverage denominators printed. The continuous barrier path must never use a future maximum as a live feature. This is a **diagnostic fixed-horizon, non-overlapping hypothetical trade population**, not chronological actual stop/target/capital-limited EA P&L; no 10% candidate pass or survivability certification may be inferred from markouts alone.

## Quality controls and thresholds frozen now
- Raw gzip compressed SHA, date/month membership, chronological order, Bid<=Ask, completion/earliest-fill invariants, all missing/gap counts and tick-row count must be reverified.
- This stage is **falsifiable and reportable even if negative**. No posthoc retune, no choice of favorite horizon after seeing data, no rerun of contaminated 001 rules.
- No full approval baseline has been designated: report any descriptive >10% differences as exploratory only, **formal owner-approval gate NOT EVALUABLE**.
- For any genuinely promising costed diagnostic, the NEXT independent study will preregister a full chronological, margin-aware position simulator and robust forward partition before running, including $100/$200/$500 survivability and Feb–Jul month blocks. No existing Gamma or 001 configuration automatically enters that phase.
- Historic R9 REAL/SYNTH paired direct raw-tick markouts are separate comparison populations; do not compare their hypothetical returns directly to Dukascopy without broker cost/feed reconciliation. R9 OVERFIT is hindsight teacher, never signal input.

## Expected compact artifacts
`CLEAN_RESTART_INITIAL_ENTRY_HOLD_ACCURACY.py`, tests, `CLEAN_RESTART_INITIAL_ENTRY_HOLD_JAN_RESULT.json`, per-calendar-UTC-date summary, source/engine hashes, and `CLEAN_RESTART_INITIAL_ENTRY_HOLD_RESEARCH_RECORD.md` linking all evidence, failures and next unit. Keep multi-GB tick cache local; no new MT5 tick logger. The owner runs any later M1 Coinexx tester only after human review and authorization.

**Pre-registration status:** Document registered before execution of this clean study, Sept 28 2026. No candidate/EA authorized by writing this.
