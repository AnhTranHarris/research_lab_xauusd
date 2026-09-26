# R9B_GAMMA2_NATIVE_R9_META_OWNERSHIP_016

VERIFIED_DURABLE_DIAGNOSTIC_CANDIDATE. Not promoted.

The validated native-R9 event population from 015 was used. R9 overfit/oracle information remained teacher-only: each native event was independently replayed as FADE and CONTINUE under the historical wide-room / near-immediate-harvest lifecycle; future outcomes created labels only. Jan-Mar trained a shallow transparent tree, April selected complexity/confidence, and May-Jul remained frozen.

Selected router: depth 4, leaf 800, abstain weight 1.5, minimum action confidence 0.45.

Jan-Jul result:
141,465 trades / 98,937 winners / 69.94% wins / -$16,824.25 net / -$43,422.84 GL / PF 0.613.
Against the validated native-R9 control, this reduces GL by 42.06%, improves net by $26,869.19, raises success by 25.19 percentage points, retains 59.86% of trades, and retains approximately 93.55% of native-R9 winners.

Against the same-event, same-harvest-lifecycle CONTINUE baseline:
GL improves -$62,556.26 -> -$43,422.84 (30.59% reduction);
net improves -$33,159.36 -> -$16,824.25;
win rate improves 66.50% -> 69.94%;
86.23% of baseline winners retained.

Frozen May-Jul:
54,447 trades / 36,556 winners / 67.14% / -$7,980.94 net / -$15,270.59 GL.
Versus same-lifecycle CONTINUE, GL is 30.92% lower, net improves by $5,532.70, win rate rises 3.24pp, and 82.55% of winners are retained.

Teacher-only capacity remains very large: only about 6-15% of native events per month have neither action profitable under the fixed teacher lifecycle. July is the highest-neither month.

Feature ablation:
- Regime confidence is the dominant ownership variable.
- ATR ratio and ATR excess are next.
- 1s/5s/30s directional path contributes secondarily.
- Regime age helps modestly.
- Same-minute wave/rearm and simple signal-fatigue counts did not add incremental value in this shallow-tree test.
Thus signal-fatigue remains a community hypothesis, not a surviving R9B mechanism yet.

July remains the main failure state: 61.36% success, average winner ~$0.173, average loser ~-$0.724, predicted abstain ~36.7%. This is still the same core pathology: weaker action ownership plus winner compression.

Community mechanisms retained:
- MQL5 Market Microstructure Part 7 classifies Normal/Stressed/Noisy/Informed/Trending/Mean-Reverting separately and exposes confidence; risk/entry behavior changes by state.
- Part 8 uses regime confidence to adapt micro-trend thresholds, explicitly suppressing more Stressed-session signals.
- Chinese dynamic mean-reversion/momentum work identifies repeated-signal fatigue and context-free re-entry as loss sources.
- Chinese ORB and breakout/retest work requires break -> retest -> secondary break, rather than first-touch entry.
- Japanese price-action work on XAUUSD waits for confirmed structural crossing rather than transient wick breaks.
- Korean community/material supports liquidity/execution sensitivity and multiple breakout paths, but product claims are not evidence.
- Reddit gold evidence repeatedly warns that hard regime filters can remove profitable trades; rejected opportunities need independent specialists, not deletion.
- Recent gold swing discussion strongly reinforces explicit bid/ask cost modeling; gross-only edges around 1-2bp/trade are not trustworthy for XAUUSD.

Next unit: R9B_GAMMA2_CONFIDENCE_SPECIALIST_ROUTER_017
Build separate ROTATION / EXPANSION / TRANSITION-STRESSED ownership models instead of one universal tree. Use regime confidence to decide whether to act immediately, require a bounded retest/rebreak proof, or hand the event to another specialist. Add explicit July-like slow/noisy ownership. Preserve one chronological ledger and the same Jan-Mar / April / frozen May-Jul discipline. Score GL first, winning trades/success second, net third.

Source SHA256 28d6fff7feb1095ba631d985086103b4e3a6eb4a40e9aa524727a27f62b2e713
Result SHA256 b77e172397f39207f0492980b335f54a15ace822b79e2df146b8fe8e203061bf
Ablation SHA256 105286b8fa1d10f09b2d5f5da079e972d34343519dddb7f8a041e776206034ea
August sealed.
