# R9B_GAMMA2_CONFIDENCE_PROOF_HANDOFF_018

Status: VERIFIED_DURABLE / REJECTED. No Gamma promotion.

## Exact causal question
The July 017A forensic showed that first $0.30 directional displacement within 5 seconds strongly correlates with the teacher's profitable owner. 018 tests whether that information is actually executable.

The proof must be observed first, then the trade enters at the exact proof tick. No trade receives signal-time entry after future proof is observed.

The 017 regime-specialist router is frozen. Four handoff modes were tested:
- ABSTAIN_ONLY
- low confidence within +0.05 of the 017 regime threshold
- low confidence within +0.10
- July-like young/low-energy state

First-touch grid covered $0.05-$0.35 and 3-10 second proof windows. Every candidate was merged with the surviving 017 trades using actual entry timestamps in one chronological one-position ledger.

## Result
No candidate passed April calibration while simultaneously:
1. reducing gross loss;
2. retaining at least 98% of 017 winners;
3. not worsening net;
4. keeping success within 0.5 percentage point.

The least-bad first-touch candidate was low-margin handoff at $0.35 / 5 seconds, but even it worsened April by:
- -$679.29 net
- -$574.88 additional gross loss
- -777 winners
- -1.84pp success

Jan-Jul it worsened 017 to:
131,545 trades / 91,129 winners / 69.28% / -$17,972.63 net / -$43,472.29 GL.

Frozen May-Jul:
47,559 trades / 31,632 winners / 66.51% / -$7,641.54 net / -$14,038.52 GL.

## Winner recovery is real, but too expensive
ABSTAIN_ONLY $0.35/5s recovers 17,056 additional Jan-Jul winning trades relative to 017, proving the low-confidence pool contains real opportunity.

But it also:
- worsens net by $5,383.81;
- adds $9,513.37 of gross loss;
- lowers success.

Therefore simply filling abstains with proof trades violates the project's current priority ordering.

## Confirmation-tax diagnosis
The 017A first-touch relationship was not fake. It was a selection relationship measured from the original signal.

When entry is moved to the actual proof tick, the system pays:
- the price displacement used to create the proof;
- bid/ask cost;
- chronological opportunity displacement while waiting;
- reduced remaining MFE;
- more exposure to the same rapid reversal that created July's one-side-only behavior.

This is a classic confirmation-tax/latency problem. For this HFT edge, confirmation becomes informative after too much of the monetizable excursion has already occurred.

The extended test down to $0.05-$0.15 proof levels does not solve the problem.

## Proof -> pullback -> reacceleration
A separate exact-tick screen tested:
first touch -> micro pullback from the new extreme -> reacceleration -> entry.

The best April version was:
$0.30 first touch within 5s -> $0.15 pullback -> $0.05 reacceleration within 20s.

It still worsened April versus 017:
- -$803.51 net
- -$780.76 additional GL
- -41 winners

Thus a reconstructible breakout/retest/reacceleration sequence is also rejected as the primary HFT entry layer.

## Community/quant cross-reference
The negative result is consistent with several external mechanisms:

- MQL5 Market Microstructure Part 5 explicitly warns that true microstructure is tick-level and that bar aggregation hides bid/ask bounce and adverse selection.
- Part 6 separates directional order-flow signal from its confidence, conditioning reliability on volatility/noise.
- Parts 7/8 separate regime state, confidence and directional response; low-confidence/Stressed states tighten signal thresholds.
- Dynamic Multi-Pair EA Part 9 treats spread expansion, tick velocity, quote gaps, micro-volatility and execution stability as a separate execution-quality layer.
- MQL5 breakout/retest state machines are mechanically reconstructible, but our Dukascopy HFT replay shows their confirmation delay is too costly for this specific short-horizon edge.
- Directional-change intrinsic-time work supports event-based clocks and overshoot states; these are more promising as leading state descriptors than as delayed entry confirmation.
- Community breakout discussions repeatedly describe the same economic issue: thin breakout edge disappears after fees, slippage and late confirmation.

## Integration decision
Do NOT integrate delayed OCO proof as an entry requirement into R9B Gamma.

Preserve these concepts:
- tradeability separate from regime classification;
- first-touch/acceptance as a state-transition descriptor;
- conditional proof information for lifecycle/handoff research;
- exact event-time chronology.

Move the next ownership research earlier in the information chain.

## Next recommended unit
R9B_GAMMA2_LEADING_TICK_MICROSTRUCTURE_019

On the validated native-R9 event population, build only causal features available before entry:
- signed up/down tick imbalance and run structure;
- tick-arrival velocity and acceleration;
- extreme-renewal asymmetry;
- quote-gap frequency and size;
- actual Dukascopy spread state rather than only the fixed half-spread model;
- local micro-VWAP / quote-volume imbalance if supported by the feed;
- tick-sequence entropy / compressibility;
- directional-change multi-threshold state and overshoot age;
- execution-stability state.

Use those as leading ownership/tradeability inputs to the separate regime specialists from 017, rather than waiting for post-signal price proof.

Jan-Mar discovery; April calibration; May-Jun strict forward; July stress-validation; August sealed.

## ROI reporting
After this stage, the correct ROI report should distinguish:
1. current formal profitable build (Gamma_2);
2. latest research ownership frontier (017);
3. rejected 018 delayed-proof layer;
4. fixed-lot historical return versus small-balance survivability;
5. realized backtest ROI versus forward-looking live expectation;
6. transaction-cost/slippage sensitivity;
7. monthly and cumulative return path.

The ROI report must not treat 017 or 018 shadow results as part of the deployable build.

August remains sealed.
