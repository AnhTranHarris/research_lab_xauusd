> **QUARANTINED / NOT AN ACTIVE ALPHA RESEARCH PARENT — owner-directed pre-bootstrap reset, September 28, 2026.** This was one of six exploratory configurations tested under a subsequently invalidated Gamma-era startup path. Results remain read-only historical negatives, not approved EA science or a baseline. New reset research starts at [CLEAN_RESTART_INITIAL_ENTRY_HOLD_RESEARCH_RECORD.md](CLEAN_RESTART_INITIAL_ENTRY_HOLD_RESEARCH_RECORD.md). The original research body below is preserved.

# R10 Alpha — Initial ENTRY + HOLD accuracy discovery 001: completed, negative

**Evidence as of 2026-09-28.** Status: exploratory January, six preregistered combinations REJECTED. This is **not** an approved Alpha EA candidate, does **not** satisfy the owner's >10% candidate gate, contains **no new MQL5 build** and **no new Coinexx report**. R9 SYNTH is an aspirational teacher, not execution truth.

**Pre-registered rules:** [ENTRY_HOLD_DISCOVERY_001_PREREGISTRATION.md](ENTRY_HOLD_DISCOVERY_001_PREREGISTRATION.md); [Python implementation](../../scripts/r10_alpha_dukas/entry_hold_discovery_001.py); [unit tests](../../scripts/r10_alpha_dukas/tests/test_entry_hold_discovery_001.py); [complete compact results](../../results/R10_Alpha/ENTRY_HOLD_001_COMPACT_RESULTS.json); [daily source-date coverage](../../results/R10_Alpha/ENTRY_HOLD_001_DAILY_JAN_UTC.csv); [week view, provisional UTC ISO](../../results/R10_Alpha/ENTRY_HOLD_001_WEEKLY_UTC_ISO_PROVISIONAL.csv). The existing engine passed 15 unit tests; 3 added temporal-leakage/parentage tests passed, for **18** total. No raw source files have been copied into GitHub.

## A. R9 REAL versus R9 SYNTH: original historical entry behavior

Source: existing valid R9 full seven-month paired correlation quick references, separately supplemented with **fresh independent eight-day sample** of the existing archived R9 Coinexx logger partitions (2026-01-02, 01-30, 02-02, 03-02, 04-01, 05-01, 06-01, 07-01; see [raw diagnostic code](../../scripts/r10_alpha_dukas/r9_entry_markout_eight_days.py) and [day-level measurements](../../results/R10_Alpha/R9_ENTRY_MARKOUT_EIGHT_DAYS.csv)).

**Eight-day unpaired sample:** original R9 REAL = 11,433 ENTRY_* events; R9 SYNTH = 12,073 ENTRY_* events. Fixed-horizon executable **markout diagnostic** means side × (Bid at horizon minus entry Ask) for BUY, or side × (Ask at horizon minus entry Bid) for SELL. Horizons use first later tick within 1s of the target horizon. NOTE: original strategies may have EXITED before that horizon; post-exit markouts are hypothetical price paths, **NOT the tester's realized trade win rates**. The SYNTH and REAL ENTRY populations are NOT same-identity matched trades. Do not attribute their entire percentage gap to a single factor.

| Horizon | REAL fraction positive | SYNTH fraction positive | REAL mean markout $/oz | SYNTH mean markout $/oz |
|---|---:|---:|---:|---:|
| 1s | 19.33% | 39.44% | -0.1995 | +0.0454 |
| 3s | 28.19% | 52.50% | -0.2063 | +0.3522 |
| 10s | 36.15% | 86.15% | -0.2278 | +1.0432 |
| 20s | 40.20% | 67.87% | -0.2269 | +1.3830 |
| 30s | 42.52% | 61.33% | -0.2005 | +0.6944 |

The already validated full seven-month R9 original lifecycle summary (DIFFERENT, full-population denominator) shows 43.27% REAL realized wins vs 87.14% SYNTH, median holds 2.995s vs 17.7325s, median favorable excursion 0.07 vs 1.04, and trailing activation 46.79% vs 86.29%. M1 Bid OHLC often coincides despite radically different sub-minute paths. These two evidence layers support looking for causal **early acceptance AND persistence**, but do not prove that delayed confirmation will succeed.

On the eight-day sample, original R9 REAL mean daily median spread AT ENTRY was ~0.205 $/oz; original R9 SYNTH ~0.189 $/oz. In contrast, the independent Dukascopy January raw tick median spread was **$0.70**, with sampled 10th percentile $0.54 and 90th percentile $1.354. Cost / feed mismatch is substantial and NOT a justification for filling at Coinexx prices using Dukascopy market paths.

## B. New original Dukascopy January causal experiment

Original 2026-01 gzip SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`; **9,135,062** tick observations / **26** UTC dates with quotes / 344,037 completed 5s bars. The strict parent universe consists of **14,292** structure-aligned and direction-positive event IDs spaced >=30s; all use strictly completed M15/M30/H1 voting 2-of-3 and available 5s quotes. Filtering produces **5,160** pullback-resumption IDs and **1,014** pullback+path-quality IDs, with no re-entry from rejected root events. Evaluation is only on matched Dukascopy source and no August.

Trade setup before first outcomes: 0.01 lot, 100 oz/lot, 1:500, source Bid/Ask, simulated $0.20 round-trip commission + $0.05 each way slippage, cap spread $1.20, stop $1.20, target $3.00, one account/one concurrent position, 30s versus 120s maximum hold, $200 starting capital. **All six variants nearly exhausted the $200 account, ending between $7.38 and $8.99.** Later eligible signals were correctly margin-rejected and results cannot be interpreted as full-January accepted-trade accuracy at constant capital.

Additional **$100,000 constant-size diagnostic** was run ONLY to observe all-January conditional trade performance without the early near-bankruptcy truncation; this $100k counterfactual is NOT the required small-account financial performance, nor a promotion baseline:

| Family, 120s | Eligible root IDs | Chronological trades | Net win rate after fees | TP-first fraction | Net USD at fixed 0.01 lot | PF on net P&L |
|---|---:|---:|---:|---:|---:|---:|
| A: structural resumption | 14,292 | 10,037 | 14.37% | 7.75% | -$10,123.58 | 0.220 |
| B: + $1.20 pullback | 5,160 | 4,812 | 15.30% | 9.37% | -$4,702.67 | 0.252 |
| C: + path-quality filter | 1,014 | 992 | 15.83% | 9.38% | -$938.04 | 0.264 |

The apparent fractional win-rate uplift of C vs A is CONDITIONAL: it retains just 7.1% of root events and is still materially loss-making. It does **not** qualify for an Entry >10% gate because no current owner-approved cumulative Alpha EA baseline is designated, and economic regression is unacceptable. Out of 26 source dates, the C 120s diagnostic had active closed trades on 25 and only one marginal positive trading date. All three 120s strategies have approximately 79–82% stop-triggered exits (costed source Bid/Ask).

**Post-entry direction-only forensic labels**, on the frozen original root population, were computed separately using future midquote ONLY as an after-the-fact outcome (never as an input or a trade fill). At 60s, fraction of positive direction vs signal = A 49.274%, B 51.250%, C 54.910%, and mean signed mid-price movement = A +$0.0039, B -$0.0022, C +$0.1688 per oz. The late directional drift of C is far too small to cover the source median spread and commission/slippage on the entered $1.20 stop configuration. This observation is a useful *diagnostic*, not an executable winning strategy.

## C. Causal lesson and next bounded experiment

**The 5-second late-chase entry and too-close stop cannot survive January Dukascopy spread and bid/ask reversal.** Do not retest this failed frozen static geometry by rebranding it. The simple extra bar-quality gate improved directional labeling modestly but did not repair early stop hazard or trade economics.

Next falsifiable state-machine idea, NOT YET RUN OR APPROVED: separate an initial higher-timeframe *direction alert* from an actual executable *entry*. Require ordered evidence **break → pullback → tight-spread reclaim / acceptance → second confirmation** within a finite expiry; timestamp each state on actual ticks, and enter only on next executable quote. Evaluate early 1–3s acceptance and first 5/10/20s hazard before optimizing holds; anchor stops to source spread and observed volatility, not a blindly transplanted $1.20 R9 stop. This is an independent new experiment to pre-register and reject if no costed improvement. Use a fixed root event family and record rejected opportunities, overlap, small-account survivability and out-of-sample partition.

Reconstructible public development background (NOT third-party profit evidence):
- [MetaQuotes crossover → momentum → retracement finite-state machine, August 28 2026](https://www.mql5.com/en/articles/23620).
- [MetaQuotes conditioned order-flow momentum measurement, June 23 2026](https://www.mql5.com/en/articles/22939).
- [TradingView Gold Smart Scalper open-source trend/value-zone/reentry specification](https://www.tradingview.com/script/zMAKRynu-Gold-Smart-Scalper-V3-Clean-Chart/).
- [r/algotrading: using actual Bid/Ask and time/processing delay](https://www.reddit.com/r/algotrading/comments/zivzzd).
- [Japanese MQL5 implementation: chronological breakout → retest → bullish/bearish confirmation with explicit duplicate-event suppression](https://www.mql5.com/ja/articles/19968). Educational code mechanics only, no transferred performance claims.
- [Chinese XAUUSD trading explanation: key-level break → pullback → confirmation](https://dongyicaijing.com/archives/lianghua/2345.html). Strategy-outline source only; its forecasts/results are NOT evidence.

**Owner-governing gates:** the **system-wide >10%** versus currently owner-approved EA or **specific Entry/Hold >10% KPI** must be predeclared and measured under matched costs, with unacceptable system degradation disqualifying. No approved Alpha EA is designated; no Gate A/B candidate, no MT5 coding and no Coinexx M1 real-tick report result are asserted. Future MT5 outputs remain **normal M1 reports only**, with “Every tick based on real ticks” internal modeling—never new ticklogger exports. August SEALED.
