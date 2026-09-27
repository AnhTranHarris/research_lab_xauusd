# R9B_GAMMA2_LEADING_TICK_MICROSTRUCTURE_019

Status: VERIFIED_DURABLE_DIAGNOSTIC_CANDIDATE. Not promoted.

## Question

Can leading information available before the native-R9 event improve 017 ownership without paying the confirmation tax discovered in 018? In parallel, can a richer multi-timeframe structure layer explain July?

The 017 regime-specialist architecture was frozen: separate TRANSITION / ROTATION / EXPANSION trees, depth 4, min leaf 800, existing confidence thresholds. Jan-Mar fit the ownership models, April selected the feature family, May-Jun remained strict forward, and July was used only as stress-validation. August remained sealed.

## Feature families rebuilt

### Raw tick microstructure
- signed up/down tick imbalance over 16/32/64 ticks
- current signed tick run
- binary sign entropy and transition entropy
- tick-arrival acceleration
- quote-gap mean/max
- actual Dukascopy spread state

### Intrinsic/event-time state
- side-aligned 250ms / 1s / 5s / 15s / 45s / 60s / 300s returns
- multihorizon sign vote
- directional-change state, age and local exhaustion at $0.05/$0.10/$0.20 thresholds

### Reconstructible equations
- Variance Ratio VR(2) and VR(4)
- normalized permutation entropy, embedding dimension 3
- two-sided standardized CUSUM accumulation
- 60-second and 300-second path efficiency

### Multi-timeframe market structure
Using completed 1m / 3m / 5m / 10m / 20m bars only:
- HH+HL bullish structural state
- LH+LL bearish structural state
- cross-timeframe structural vote/conflict
- completed candle body direction

## Result

017 baseline Jan-Jul:
137,288 trades / 97,533 winners / 71.043% success / -$12,342.17 net / -$38,839.24 GL / PF 0.6822.

Best April-qualified family = BASE_EVENTTIME:
136,450 trades / 96,908 winners / 71.021% / -$11,758.69 net / -$38,062.86 GL / PF 0.6911.

Delta:
- gross loss reduced 1.999%
- net improves $583.48
- winner retention 99.36%
- trade retention 99.39%
- success essentially unchanged (-0.022pp)

Strict May-Jun forward:
- gross loss reduced 4.88%
- net improves $423.16
- win rate effectively unchanged
- 99.56% of winners retained

July:
017 = 16,188 trades / 10,052 winners / 62.095% / -$2,412.19 / -$4,135.02 GL.
019 event-time = 16,042 / 9,903 / 61.732% / -$2,563.00 / -$4,259.62 GL.

Thus the same event-time family that helps April and May-Jun worsens July.

## What survived

The most useful new event-time descriptors in the selected models were:
- 5-second directional return relative to the native event side
- 60-second directional context
- $0.20 directional-change state
- $0.10 directional-change age

Existing state variables still dominate:
- regime confidence
- ATR ratio / ATR excess
- 10-second efficiency/range
- activity state

The raw-tick family showed useful information in:
- maximum recent quote gap
- mean recent quote gap
- tick-arrival acceleration
- actual Dukascopy spread

It reduced Jan-Jul GL more than the selected family, but failed the April winner-density guard. These descriptors remain candidates for specialist-specific rather than universal use.

The equation family showed:
- 60-second path efficiency
- variance ratio
- CUSUM
as nonzero ownership features. It slightly improved July economics, but worsened April net and therefore failed selection.

## Multi-timeframe result

The user's multi-timeframe hypothesis is NOT rejected.

The first implementation — a simple completed-bar HH/HL vs LH/LL state and vote across 1m/3m/5m/10m/20m — produced essentially no change to the 017 decisions. Only the completed 5m body direction received modest feature importance.

This means the encoding is too coarse. A flat vote loses the information that matters:
- which timeframe currently owns the structure;
- whether a structural break was accepted or swept;
- swing/level age and touch count;
- whether lower-timeframe structure is nested within or contradicting the higher-timeframe owner;
- whether the state just changed;
- shape/pattern transition rather than only direction.

## Community / quant equation cross-reference

Reconstructible mechanisms worth the next unit:

1. Ordinal Pattern Transition Networks (MQL5, 2026)
   - encode local price shape as ordinal permutations using Lehmer indexing;
   - permutation entropy measures pattern concentration/randomness;
   - forward-vs-reversed pattern distributions can be compared with Jensen-Shannon divergence for time-irreversibility;
   - transition networks preserve sequence information that simple pattern counts lose.
   Source: https://www.mql5.com/en/articles/23451

2. Bayesian Online Change-Point Detection
   - causal posterior over run length since the last structural change;
   - directly addresses the July result that regime classification confidence != state durability.
   Source: https://www.mql5.com/en/articles/23482

3. Sequential CUSUM / structural break tests
   - standardized upward/downward accumulators detect active distribution shifts;
   - recent MQL5 empirical work warns theoretical false-alarm calibration is inaccurate and must be calibrated on the target instrument.
   Sources:
   https://www.mql5.com/en/articles/23043
   https://www.mql5.com/en/articles/23103
   https://www.mql5.com/en/articles/23159

4. Market structure built from accepted bodies rather than wick extremes
   - open-source TradingView implementation explicitly separates body-based accepted structure from wick sweeps across multiple timeframes.
   Source: https://www.tradingview.com/script/2EdkRmfX-Market-Structure-Shift-and-CRT/

5. Open-source multi-timeframe structure / liquidity
   - objective internal + swing structure, sweeps, equal highs/lows, HTF levels, BOS/CHoCH; useful as reconstructible pattern vocabulary, not as proof of profitability.
   Sources:
   https://www.tradingview.com/script/IevJbc8C-structure-break-liquidity-sweep/
   https://www.tradingview.com/script/vXui7vrm-Market-Structure-Dashboard-Flux-Charts/

## Decision

Do not promote 019.

Preserve:
- 5s/60s event-time context
- directional-change state/age
- tick-gap / arrival / spread descriptors
- variance-ratio/CUSUM/path-efficiency equations

Reject:
- simple multi-timeframe vote as the final structure model
- indiscriminate all-feature stacking

## Next unit

R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020

Build a hierarchical, causal pattern/state layer rather than another broad feature dump:

1. STRUCTURAL OWNER
   - confirmed completed swing structure at 1m/3m/5m/10m/20m plus H1 where data permits
   - owner = highest timeframe with a live accepted structural state, not vote count
   - lower timeframe can confirm, transition, or conflict

2. ACCEPTANCE / SWEEP STATE
   - structure from candle bodies/accepted closes
   - wick penetration separately records liquidity sweep
   - level age, touch count, first penetration, reclaim/acceptance

3. ORDINAL SHAPE STATE
   - short-window ordinal patterns and transition probabilities
   - permutation entropy
   - time irreversibility (Jensen-Shannon forward/reverse divergence)
   - forbidden-pattern fraction

4. CHANGE-POINT / DURABILITY
   - BOCPD-style causal run-length probability or bounded approximation
   - target-instrument-calibrated CUSUM state
   - explicit distinction between regime label confidence and durability

5. INTRINSIC EVENT-TIME
   - directional-change state/age from 019
   - use as leading context, not delayed entry confirmation

Feed these into separate 017 specialists with semantic ownership. Jan-Mar discovery, April calibration, May-Jun strict forward, July stress-validation. August sealed.

Source SHA256: 482e39f694ccf3bb24f43097a7e38f06314e0546194b6e7952e6ea75c2e0e0e8
Trainer SHA256: 81a3892d2d1d238f9c5bc713574180b8b22c015ed9e50f4a09b1fb9bda55b245
Local result SHA256: 4825217f84f6d23343c6e63a154daa8a8c1e6aedd121973211471854ea76a647
August sealed.
