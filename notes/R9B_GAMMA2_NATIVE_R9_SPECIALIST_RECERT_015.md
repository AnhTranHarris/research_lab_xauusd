# R9B_GAMMA2_NATIVE_R9_SPECIALIST_RECERT_015

## Status
VERIFIED_DURABLE_DIAGNOSTIC. No strategy promotion.

## Native R9 simulator validation
The exact-tick Dukascopy reconstruction now reproduces the MT5 R9 REAL activity population unusually closely:

- Python: 236,332 trades
- MT5 REAL: 236,647 trades
- Difference: only 315 trades
- Count match: 99.87%
- Python GP: $31,256.61 vs MT5 REAL $30,180.23
- Python GL: -$74,950.04 vs MT5 REAL -$80,465.51
- Python win rate approximately 44.75% vs MT5 REAL 43.26%

This establishes a much stronger native-R9 research control than the earlier sweep-only reconstruction.

## Transparent P4/P6 recertification on their native opportunity population
P4 rotation:
- 53,884 trades
- ~66.0% wins
- -$10,261.41 net
- -$18,225.93 GL
- average winner only ~$0.224
- average loser about -$0.995

P6 expansion:
- 59,033 trades
- ~67.8% wins
- -$11,151.12 net
- -$22,037.51 GL
- average winner only ~$0.272
- average loser about -$1.158

P4+P6 union:
- 112,755 trades
- ~67.0% wins
- -$21,354.85 net
- -$40,324.53 GL

R10 transparent core on native R9 events:
- 132,008 trades
- ~67.3% wins
- -$24,755.09 net
- -$47,398.64 GL

May-Jul stays negative for every raw specialist configuration.

## Interpretation
The old P4/P6 historical research was not merely a regime-threshold discovery. The raw P4/P6 rules identify different states, but their payoff geometry remains poor: they win often and still lose money because losing trades are roughly four to five times larger than average winners.

Therefore the missing value is inside the historical meta-label/ownership/lifecycle layer, not the P4/P6 regime split by itself.

## Community/quant research implications
Fresh public research reinforces this direction:
- MQL5 regime systems explicitly separate trend/range/high-volatility classification from the strategy used inside each state; the XAUUSD M1 example also shows generic regime routing can still perform poorly without specialist-specific logic.
- Chinese MQL5 adaptive mean-reversion/momentum work emphasizes signal fatigue, re-entry progress and state-dependent strategy selection.
- Japanese breakout/retest implementations use explicit break -> retest -> re-break state transitions to reject first-touch false breaks.
- Open-source TradingView regime engines combine efficiency with adaptive volatility clustering, but correctly treat regime as context rather than directional alpha.
- Semi-Markov research shows momentum-versus-reversal behavior depends on regime age/duration: short-lived states can continue while aging states become increasingly reversal-prone.
- Recent gold hobbyist discussion independently warns that a hard regime switch can delete profitable trades; specialists should be benchmarked both independently and under the router.

## Next unit
R9B_GAMMA2_NATIVE_R9_META_OWNERSHIP_016

Use R9 overfit/oracle only as teacher on the now-validated native R9 event population. Reconstruct causal specialist ownership:
- P4 ROTATION fade/take/abstain
- P6 EXPANSION continue/take/abstain
- ambiguous/transition state
- regime age / duration
- same-minute wave/rearm index and signal fatigue
- session, efficiency, ATR ratio, event path quality
- optional bounded break->retest->rebreak proof state

Jan-Mar discovery, April calibration, May-Jul frozen. Optimize gross loss first, winner count/success second, net third. Future information remains labels only. August sealed.

Source SHA256: 1c55a3c5534a51cdcaa4c6769d001d86282af55f89c43707003cc75f35b231a2
Recovered result SHA256: f8207aed56eb73ad47c4425eec23e74ba551ec13e0bf8cf72142ca3514281174
