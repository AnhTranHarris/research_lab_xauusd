# R9B_GAMMA2_CONFIDENCE_SPECIALIST_ROUTER_017

Status: VERIFIED_DURABLE_DIAGNOSTIC_CANDIDATE. Not promoted.

## Specialist result
016 used one universal shallow ownership tree. 017 splits ownership into three transparent experts: TRANSITION, ROTATION, and EXPANSION, all trained only on Jan-Mar teacher labels. April selected fixed per-regime confidence thresholds; May-Jul stayed frozen.

Jan-Jul:
- 137,288 trades
- 97,533 winners
- 71.04% success
- -$12,342.17 net
- -$38,839.24 gross loss
- PF 0.6822

Versus 016:
- 10.56% less gross loss
- +$4,482.08 net improvement
- +1.11 percentage points success
- 97.05% trade retention
- 98.58% winner retention

Frozen May-Jul:
- 53,336 trades / 36,175 winners / 67.82% / -$6,921.76 / -$14,064.01 GL
- versus 016: 7.90% less GL, +$1,059.18 net, +0.68pp success, 98.96% winner retention.

July itself improves only modestly:
- 16,188 trades / 10,052 winners / 62.10% / -$2,412.19 / -$4,135.02 GL
- average winner +$0.171; average loser -$0.697.
July therefore remains the principal stress month.

## July macro/news deep dive
Official July 2026 USD schedules from BLS, BEA and the Federal Reserve were used only as diagnostics; event times never entered the strategy model.

The diagnostic set includes Employment Situation, international trade, FOMC minutes, CPI, PPI, import/export prices, the July FOMC decision, GDP/PCE, and ECI.

Within ±30 minutes of those scheduled releases:
- only 412 executed 017 trades, 2.55% of July trades;
- net -$55.08;
- gross loss -$120.83;
- success 66.26%, which is better than July overall.

Within ±60 minutes:
- 816 trades, 5.04% of July;
- net -$118.51;
- gross loss -$231.44;
- success 65.32%.

All native events within ±30 minutes of the scheduled releases show HIGHER, not lower, average ATR ratio, ATR excess, directional displacement, 10s range, 1s/5s/30s directional return, and slightly higher regime confidence than the rest of July. The teacher 'neither direction profitable' share is not abnormally high around the news windows.

Therefore a blanket news blackout does not explain or solve July in this fixed-cost Dukascopy replay. Removing ±30 minute windows would save only about $55 net while discarding roughly 2.5% of July opportunities and many winners.

Important limitation: current R9B shadow execution still uses a fixed modeled cost/spread geometry. Scheduled news can widen live broker spreads and slippage even when the underlying price state is tradable. Therefore news should remain a secondary execution-risk annotation or size/confirmation modifier, not be discarded from the production design.

## External research retained
- MQL5 Market Microstructure Part 7 separates Normal, Stressed, Noisy, Informed, Trending and Mean-Reverting states and attaches classification confidence. Part 8 explicitly tightens/loosens downstream signal thresholds according to regime confidence.
- MQL5 news-filter engineering emphasizes that calendar windows primarily protect against execution distortions such as spread widening/slippage, including for positions opened before releases.
- MQL5 calendar research recommends using the calendar primarily to anticipate increased volatility, not as a directional entry signal.
- High-frequency gold research reports that macro announcements materially contribute to intraday jumps and that much of the reaction occurs quickly; FOMC and major labor/GDP surprises are important, but liquidity/activity/order imbalance are also predictive of jumps.

## Next unit
R9B_GAMMA2_CONFIDENCE_PROOF_HANDOFF_018

Keep 017 as the ownership baseline. For low-confidence/abstained events:
1. do not immediately delete the opportunity;
2. place exact-tick virtual FADE and CONTINUE acceptance levels;
3. let first causal acceptance / retest / re-break determine specialist ownership within a bounded proof window;
4. expire unresolved events;
5. assign specialist-specific hold/exit after proof;
6. explicitly analyze July-like low-displacement / low-ATR-excess state;
7. keep calendar/news only as an execution-risk annotation unless a replicated state-conditional benefit is demonstrated.

Jan-Mar discovery, April calibration, May-Jul frozen. Priority: gross loss -> winners/success -> net. August sealed.

Source SHA256: f222e57848caab89064d94c88a4629fa2f950999ce28def726758d56b2fd61f6
Result SHA256: b1373d23d74da8b670e3ef93296d504bc18d0063ea9bf19f741dfebec9120e7e
