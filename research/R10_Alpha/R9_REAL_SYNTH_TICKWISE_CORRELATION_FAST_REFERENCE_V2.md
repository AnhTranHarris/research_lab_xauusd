<!-- Exact native Docs readback, with date smart-chip display text converted for GitHub portability. -->

[Canonical Google Doc](https://docs.google.com/document/d/1vT8JxT7pG7Ry-TMjEZRYGY3nAJC1slS8AnW3ieL033A/edit)



# R10 ALPHA | R9 REAL ↔ SYNTH TICK-LEVEL CORRELATION — FAST REFERENCE v2

## Evidence boundary and purpose

XAUUSD only. This document consolidates (A) the complete 149-session original R9 logger source-index audit, (B) a new 8-session direct raw-tick comparison across all seven months, and (C) separately marked historical seven-month paired tick/strategy summaries. It is an engineering/forensic reference, NOT a fresh 149-session tick-for-tick price replay, not Alpha trading strategy performance, and not proof that SYNTH gains can occur under real-tick execution. August is SEALED.

## Primary result

The MT5 generated and real-tick paths form identical completed one-minute Bid OHLC envelopes in all newly checked sessions, but the observed millisecond timestamps, sub-minute OHLC paths, spread regimes, entry opportunities and trailing sequences diverge sharply. Aggregated M1 correlation is therefore an inadequate proxy for tick-level execution equivalence.

## 1 | Original R9 tick-log identity, scope and integrity

Source: the user's R9_ticklog_csv_gz Drive folder (ID 1CidEgLMNVfgBZg6UYLYqcanc0oqgt9Vj) contains two immutable original logical GZIP ticklogger streams, each stored as six ordered transport parts. REAL: compressed 762,236,183 bytes, source SHA-256 ad82ee99ba60f6c7dcc5b85654971fecb9f4a5047dc6f97aa97083b3c60a663c; decompressed SHA-256 244e9fb2851de497a0a863584c34e634de3f1d79e77d0146556a8da1f2ee9d9c. SYNTH: compressed 729,902,943 bytes, source SHA-256 cd3a7dc68d2b260ea5f4a847bfef88bcb328d8687f3f8b35ce0d19602f88d6aa; decompressed SHA-256 56ce41ac888d240e750e0ebb3730b3b59d1e325b94d840c1ade2d389b4fe2a4b. These full-source digests are inherited from the Drive validation records; all twelve originals were not redownloaded this session.

Previously validated daily reconstruction: REAL 56,608,185 rows / 149 UTC session files; SYNTH 54,655,160 rows / 149 UTC session files. All days are covered by existing exact-file manifest and event indexes. A new integrity crosswalk of all 149 paired DAY/EVENT indexes reconciled their total rows against daily source manifests, with no discrepancy. Newly downloaded sample consists of 16 individual daily source GZIPs, and all 16 actual compressed byte hashes, sizes and row counts match their frozen Drive manifests. Coverage is 8 complete market sessions (one in each month plus an extra January stress day), 3,462,369 REAL and 3,324,449 SYNTH tick rows.

The same 31 logger columns are present in both feeds: run_label,time_msc,time,bid,ask,last,tick_volume,volume_real,flags,spread,minute_start,minute_second,cycle_buy,cycle_sell,pending_mode,rearm_number,s1_disp,s1_eff,s1_range,s1_turns,atr,session,gate_open,position_open,position_side,entry_price,mfe,mae,current_sl,trail_armed,event. Logging event labels: ENTRY_BUY, ENTRY_SELL, EXIT_MAX_HOLD, MINUTE_START, NONE, QUALITY_REJECT_BUY/SELL, REARM, TRAIL_MOVE. There is no generic explicit stop-fill event in this list: full exit truth needs a separate reconstructed position-state/MT5-trade reconciliation.

## 2 | Comparison method — do not pair ticks by CSV row number

Raw tick logs have different counts and event-time sequences. Within each source independently preserve ordered time_msc, including stable source-row order for equal milliseconds. For a same-millisecond diagnostic, collapse repeated timestamps to their last logged quote and inner-join the resulting millisecond keys; this does NOT assert causal identity between the two tester streams. For a second descriptive check, align a SYNTH tick to the most recent prior REAL quote, allowing a maximum 250 ms age; never match a future REAL quote. Attribute unmatched ticks explicitly. Both operations are quote comparisons, not tradable price substitutions or fair counterfactual fills.

Build time buckets from floor(UTC_time_msc / width_ms) with half-open [start,end) windows. For each feed independently compute Bid open, high, low, close and tick count; compare only buckets with ticks in BOTH streams, and report overlap. Require every Bid OHLC field to be within $0.01 to call a bar matched. Periods are exactly 250 ms, 1 s, 5 s, 15 s, 30 s, 45 s and 60 s/M1. The 45 s boundaries are independently anchored; they do not partition M1. Higher views follow the same tick chronology, not a fabricated OHLC execution path.

Same-ms sample result: 19,801 shared distinct millisecond keys across eight daily pairs, versus 3,460,955 REAL and 3,324,449 SYNTH unique millisecond keys. Equal-ms overlap therefore covers only about 0.57% of REAL and 0.60% of SYNTH unique millisecond timestamps in this sample. Different timestamps do NOT imply missing ticks; these are distinct streams. Within equal-ms pairs, median absolute Bid discrepancies vary from $0.36 to $2.04 depending on session.

## 3 | Direct observed daily tick comparison — eight complete UTC sessions

Date | REAL rows | SYNTH rows | equal-ms keys | median |Bid gap| at equal-ms | median spread REAL / SYNTH | matching 250 ms OHLC

Jan 2, 2026 | 341,569 | 330,217 | 1,595 | $0.36 | $0.19 / $0.19 | 2.31%

Jan 30, 2026 | 674,427 | 635,274 | 5,219 | $2.00 | $0.57 / $0.24 | 0.24% [January stress session]

Feb 2, 2026 | 594,529 | 570,377 | 4,289 | $2.04 | $0.26 / $0.20 | 0.24%

Mar 2, 2026 | 421,053 | 417,064 | 2,307 | $0.83 | $0.20 / $0.19 | 1.05%

Apr 1, 2026 | 370,298 | 368,323 | 1,726 | $0.61 | $0.18 / $0.17 | 1.47%

May 1, 2026 | 350,809 | 349,473 | 1,664 | $0.36 | $0.20 / $0.19 | 2.33%

Jun 1, 2026 | 371,243 | 320,815 | 1,555 | $0.39 | $0.21 / $0.20 | 2.41%

Jul 1, 2026 | 338,441 | 332,906 | 1,446 | $0.40 | $0.20 / $0.19 | 2.44%

Dates for the eight sample rows are native date chips. Source day filenames and full SHA-256 checks belong in the compact audit ledger, not in an extra Drive copy of 16 large gzip files.

The eight-session unweighted mean daily COMPLETE Bid-OHLC match shares by duration are: 250 ms 1.561%; 1 s 0.469%; 5 s 0.062%; 15 s 0.027%; 30 s 0.145%; 45 s 0.415%; M1 100.000%. Unweighted mean within-day bar net-price-change correlations by duration: 250 ms 0.019; 1 s 0.065; 5 s 0.201; 15 s 0.380; 30 s 0.833; 45 s 0.777; M1 1.000. These are eight-session sample diagnostics, NOT the pooled 149-session period coefficients. At equal-millisecond keys, one quote is chosen per source; intra-ms ties cannot establish true common execution chronology.

## 4 | Newly reconciled FULL 149-session entry/event counts

Total events from the two validated DAILY_EVENT_INDEX stores, reconciled to 149 daily source-row manifests: REAL 56,608,185 rows versus SYNTH 54,655,160. ENTRY_BUY 118,494 / 109,075; ENTRY_SELL 118,153 / 110,267; total entries 236,647 / 219,342. TRAIL_MOVE 285,587 / 6,936,274 (approximately 24.3 SYNTH trail-move events per REAL trail-move event). QUALITY_REJECT_* combined 19,801,481 / 14,913,486. EXIT_MAX_HOLD 4,241 / 20,088. REARM 230,245 / 219,342. Beware: TRAIL_MOVE is a count of trail updates, NOT unique trades with activated trailing.

Across the 149 calendar-matched trading sessions, Pearson correlations of DAILY event-count sequences REAL↔SYNTH: rows 0.969; entry total 0.777; ENTRY_BUY 0.757; ENTRY_SELL 0.785; quality rejects 0.281; trail moves 0.571; max-hold exit events -0.655; rearm events 0.713. These counts agree with each daily index; this is full-calendar EVENT aggregation rather than a fresh full-period bid-by-bid rejoin.

Month | REAL / SYNTH rows | REAL / SYNTH entries | REAL / SYNTH TRAIL_MOVE | REAL / SYNTH QUALITY_REJECT

Jan | 7,699,274 / 7,392,680 | 31,915 / 27,980 | 38,957 / 864,954 | 2,389,511 / 2,055,484

Feb | 7,102,818 / 6,916,826 | 35,394 / 33,523 | 44,134 / 1,051,800 | 2,139,119 / 1,460,687

Mar | 8,859,103 / 8,812,518 | 40,297 / 40,985 | 55,051 / 1,427,618 | 2,978,097 / 1,619,234

Apr | 7,831,685 / 7,798,140 | 33,613 / 31,758 | 40,833 / 985,997 | 2,909,552 / 2,138,070

May | 8,011,360 / 7,602,592 | 31,334 / 28,913 | 32,008 / 867,225 | 3,144,880 / 2,402,276

Jun | 9,347,508 / 8,504,707 | 33,603 / 31,801 | 39,793 / 1,028,255 | 3,338,814 / 2,417,254

Jul | 7,756,437 / 7,627,697 | 30,491 / 24,382 | 34,811 / 710,425 | 2,901,508 / 2,820,481

## 5 | Prior HISTORICAL all-month paired-corpus correlations (not rerun from all raw ticks)

The previously verified full R9 paired-research corpus reports 204,625 common one-minute keys with matching Bid OHLC and ATR (r≈1), minute tick-density r=0.9888, gate-open share r=0.8685, and minute entry-count r=0.3411. Although intraminute traveled path length correlates r=0.9104, its absolute means differ: SYNTH 6.23 versus REAL 19.19 price units/minute. Mean absolute path efficiency: SYNTH 0.237 versus REAL 0.0877. Entry-minute Jaccard 0.7582, side agreement on common entry minutes 61.26%. Later strict same-minute / same-side / ordinal research pairing has 165,630 trade pairs (not 169,889 from an earlier different, less restrictive matching rule).

Full-population lifecycle: SYNTH median hold 17.73 s, REAL 3.00 s; trail activation 86.29% versus 46.79%; survival to 20 s 43.14% versus 4.73%; stop/early exit share 13.21% versus 51.48%; median favorable excursion $1.04 versus $0.07; median adverse excursion $0.19 versus $0.33. Among paired trades, MFE correlation 0.2644, MAE correlation 0.1067 and P&L correlation 0.2132. Paired-subset survival rates differ from full-population rates: NEVER exchange denominators or treat approximate pairings as exact executions.

Historical paired monthly P&L correlations: Jan 0.132, Feb 0.142, Mar 0.196, Apr 0.417, May 0.200, Jun 0.196, Jul 0.326. Historical paired April hold-time correlation is anomalously near 1.000 while most other months are near zero; retain as a QA flag for matching and censoring semantics, not as evidence of a universal holding-time law.

## 6 | Quant interpretation and four subsequent mechanisms

Identical M1 Bid OHLC says little about which quote arrives first inside each minute. At faster resolutions the samples disagree strongly on price paths; generated SYNTH repeatedly reaches the same final one-minute geometry by a different route. REAL frequently faces a less persistent/retracing path and, in stressed sessions, a wider spread. Entry opportunity counts alone do not explain the economic gap. The major investigated structural differences are event direction/ownership, 250 ms→30 s persistence, stop/trail ordering and executable Bid/Ask payoff, not mere M1 volatility or a generic tighter stop. This is evidence-guided hypothesis framing, NOT proof of causality or a profitable fix.

ENTRY: compare raw eligible source events, as-of completed multiscale features, direction choice, entry execution side, rejects and lost profitable opportunities. HOLD: conditional survival/hazard, favorable/adverse excursions, path length/efficiency and reacceleration using 250 ms/1s/5s/15s/30s/45s plus completed minutes/hours. EXIT: preserve exact intrabar Bid/Ask ordering, explicit stop/target/trail/failed-acceptance events; reconstruct exits beyond the logger's EXIT_MAX_HOLD marker. PROFIT: use one chronological nonoverlapping account, net spread/commission/slippage, gross-profit/gross-loss, per-trade expectancy, risk/drawdown and $100–$500 survival, with daily/weekly/monthly attribution; never treat SYNTH generated profit as REAL attainable profit.

## 7 | Restart instructions, compact sources, research limits

For the entire corpus, FIRST reuse the original twelve-part source archives, validated 149 DAILY_TICK_MANIFEST + EVENT_DAILY_INDEX files, and compact prior seven-month 06_ANALYSIS correlation CSVs; do not duplicate 1.49 GB of compressed originals into this document or GitHub. Source Drive folder ID 1CidEgLMNVfgBZg6UYLYqcanc0oqgt9Vj; daily accelerator folder ID 11GY1A1pFkwHfaylt2n_-P7Bd4dJ9zFO4; compact historical paired corpus ID 1ES78vXb2mFsOsa50BiwCLsT6BXgLe-Oe. Exact run labels, source SHA-256, day spans and 31-column schema must be preserved.

New audit implementation: stream only day-sized original daily CSV.GZ sources, validate compressed SHA/bytes/rows against frozen manifests, test run labels, chronological timestamps and Bid≤Ask, perform exact-ms or backward-asof diagnostic joins, and separately construct Bid candle windows of 250/1000/5000/15000/30000/45000/60000 milliseconds from each stream. Save one small durable JSON per day plus monthly aggregated event-index CSV; do NOT save additional full derived candle/tick sources unless a future test explicitly needs them. Provisional UTC ISO weeks exist only as an index; user-defined reporting week/timezone not yet locked. The historical source spans 149 trading dates within January–July; do not invent weekend trades or assume a checked sampled date gives full-month price-path equivalence.

Status and blockers: the new sample tick audit is complete on eight selected days; full seven-month source-index daily event totals are crosschecked. The 141 other paired sessions were not independently rejoined tick-by-tick in this turn. Full Python-R9 execution equivalence, complete commission/slippage reconstruction, native MQL5 real-tick parity, and a frozen independent forward test remain NOT VERIFIED. August remains SEALED; no Alpha trading experiments or orders were launched.
