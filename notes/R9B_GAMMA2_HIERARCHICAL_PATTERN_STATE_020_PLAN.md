# R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020 — Research Plan

Status: READY AFTER 019. This file is the explicit next-unit design and community/quant cross-reference. August remains sealed.

## Why 020 exists

019 showed that simple multi-timeframe HH/HL-LH/LL voting across completed 1m/3m/5m/10m/20m bars adds essentially no incremental value. That does NOT reject multi-timeframe structure. It rejects a coarse, equal-weight encoding.

July stress-validation says the missing state is more specific:
- broad regime mix remains similar;
- teacher no-edge/neither-side events almost double;
- state age/durability roughly halves;
- oracle excursion capacity falls about 45%;
- wrong-owner and toxic execution rates rise;
- average winner compresses;
- static pre-entry viability remains weak.

Therefore 020 must model *hierarchical structural ownership, state duration, active pattern phase, distance to liquidity/accepted structure, and leading tick pressure*.

## Core architecture

Native R9 event
-> regime class + regime confidence
-> hierarchical structural owner
-> structural durability / change-point state
-> liquidity-boundary relationship
-> pattern phase
-> leading tick pressure / execution state
-> specialist ownership
-> lifecycle owner.

No equal-weight voting. No post-signal confirmation tax. No future data.

## 1. Hierarchical structural owner

For each completed timeframe (1m, 3m, 5m, 10m, 20m, 1h, 4h where enough completed history exists), maintain:
- confirmed swing high/low sequence;
- bullish / bearish / transition state;
- last accepted BOS;
- last CHoCH / structural reversal;
- active structural high and low;
- age since last structural transition;
- distance to active boundary normalized by timeframe ATR;
- touch count;
- first penetration vs repeat penetration;
- accepted close beyond boundary vs wick-only sweep.

Ownership is not a vote count. The owner is the highest *active and locally relevant* timeframe whose accepted structure is within a normalized distance budget. Lower timeframes can confirm, conflict, or transition the owner.

Candidate normalized structural relevance:
R_tf = exp(-d_tf / ATR_tf) * D_tf * A_tf

where:
- d_tf = distance from current price to the relevant active swing/liquidity boundary;
- ATR_tf = completed causal ATR on that timeframe;
- D_tf = duration/persistence score of the structural state;
- A_tf = acceptance quality score.

Hierarchical structural energy:
S = sum_tf w_tf * dir_tf * R_tf

Weights w_tf are discovery/calibration parameters only; no future bars.

## 2. Accepted structure versus liquidity sweep

Maintain two separate ledgers:
- BODY / ACCEPTED structure: completed close/body beyond the structural boundary;
- WICK / LIQUIDITY event: penetration beyond boundary without accepted close.

Candidate state:
PENETRATION -> RECLAIMED -> ACCEPTED -> DISPLACED -> SHIFTED -> FAILED / EXPIRED.

This directly addresses the Japanese MQL5 liquidity-grab-vs-structure-shift research and avoids conflating a sweep with a structural break.

## 3. Semi-Markov duration hazard

July demonstrates regime label confidence is not state durability.

For structural state s with age a, estimate a causal duration hazard:

h_s(a, Δ) = P(T_end in [a,a+Δ) | T_end >= a, state=s)

Implementation:
- empirical hazard table from Jan-Mar only;
- optional parametric smoothing;
- April calibration only;
- May-Jun strict forward;
- July stress-validation.

Use hazard as:
- continuation confidence when low;
- reversal/transition risk when rising;
- lifecycle modifier, never a standalone directional signal.

Public quantitative support: duration-dependent semi-Markov models reproduce short-term momentum followed by reversal when state termination probability increases with age.

## 4. Bayesian online change-point state

Candidate reconstructible mechanism: Bayesian Online Changepoint Detection (BOCPD).

Maintain posterior run-length distribution:
P(r_t | x_1:t)

with:
- r_t = observations since last change point;
- hazard H(r) = prior change probability;
- predictive likelihood from the current run.

Use:
- posterior P(change at t)
- posterior mean/median run length
- run-length entropy

as transition/instability descriptors.

Use a bounded/pruned implementation for MT5 feasibility.

Do not make BOCPD direction itself; it detects structural instability.

## 5. Sequential CUSUM

For standardized causal feature z_t:

S_t+ = max(0, S_(t-1)+ + z_t - k)
S_t- = max(0, S_(t-1)- - z_t - k)

Candidates:
- return CUSUM;
- tick-arrival CUSUM;
- spread CUSUM;
- volatility/ATR-excess CUSUM;
- quote-volume-imbalance CUSUM.

019 generic return CUSUM was weak. 020 uses CUSUM conditioned on structural owner and regime, with XAUUSD-specific empirical thresholds rather than theoretical false-alarm thresholds.

## 6. Hawkes-style up/down tick intensity

Treat upward and downward mid-quote changes as two event streams.

Candidate bivariate exponential Hawkes approximation:

λ_up(t) = μ_up + Σ α_uu exp[-β_uu(t-t_up)] + Σ α_ud exp[-β_ud(t-t_down)]
λ_dn(t) = μ_dn + Σ α_dd exp[-β_dd(t-t_down)] + Σ α_du exp[-β_du(t-t_up)]

Normalized pressure:
HOFI = (λ_up - λ_dn) / (λ_up + λ_dn + ε)

Use as a leading ownership descriptor before the native event. Fit only on discovery data.

A lightweight exponentially decayed count approximation should be tested before a full optimizer.

## 7. Quote-volume imbalance and microprice

Dukascopy raw files contain ask_volume and bid_volume. Before use:
1. verify field semantics and nonzero coverage by month;
2. verify stability and units;
3. prove they are not synthetic artifacts.

If valid:

QImb = (V_bid - V_ask) / (V_bid + V_ask + ε)

Candidate weighted mid / microprice proxy:
P_micro = (Ask * V_bid + Bid * V_ask) / (V_bid + V_ask + ε)

Microprice displacement:
Δ_micro = P_micro - Mid

Important: this is a quote-liquidity proxy, not a true centralized XAUUSD LOB. Do not call it real order-book imbalance unless the feed semantics justify that claim.

## 8. Order-flow-imbalance-style quote events

Cont-Kukanov-Stoikov OFI motivates signed best-quote price/size updates. A Dukascopy-adapted quote OFI may be tested only if quote-volume semantics are validated.

Use quote changes rather than unsupported inferred trade volume.

## 9. Ordinal pattern transition network

Simple permutation entropy alone was weak in 019. Pattern *transitions* may retain the missing path state.

For embedding dimension m:
- encode ordinal permutation π_t of a short causal return window;
- track transition counts N(π_i -> π_j);
- normalize to transition probabilities;
- derive:
  - current-pattern persistence;
  - transition concentration;
  - forbidden-pattern fraction;
  - transition entropy;
  - forward/reverse Jensen-Shannon divergence as time-irreversibility.

This converts “pattern recognition” into a reconstructible finite state machine rather than subjective chart shapes.

## 10. Multiscale information / persistence

Candidates:
- conditional sign entropy;
- permutation entropy;
- short-window Hurst / DFA proxy;
- variance-ratio state;
- path efficiency.

These should be computed at multiple causal scales and attached to the structural owner rather than used globally.

Important: 019 showed generic variance ratio/permutation entropy/CUSUM are only weakly useful by themselves.

## 11. Pattern-phase state

Reconstructable phases:
- COMPRESSION
- IGNITION
- EXTENSION
- HEALTHY_PULLBACK
- REACCELERATION
- STALL
- FAILED_ACCEPTANCE
- EXHAUSTION

Candidate inputs:
- normalized range contraction/expansion;
- directional efficiency;
- extreme renewal interval;
- swing break/reclaim;
- ATR-normalized pullback depth;
- structural-owner alignment;
- tick intensity acceleration;
- entropy transition.

Entry/hold/exit policy must be phase-specific.

## 12. Multi-timeframe pattern recognition

Community-source vocabulary to rebuild transparently:
- higher-high / higher-low and lower-high / lower-low swing sequence;
- BOS / CHoCH;
- sweep vs accepted break;
- equal-high/equal-low liquidity cluster;
- pullback depth / structural return;
- engulfing/pin/inside-break patterns ONLY as LTF execution descriptors;
- higher-timeframe liquidity zone proximity;
- trend/range/volatile regime per timeframe.

Pattern shape alone never owns the trade. It must be conditional on structural owner and tradeability state.

## Validation protocol

Discovery:
- Jan-Mar.

Calibration:
- April only.

Strict forward:
- May-Jun.

Stress validation:
- July.

Sealed:
- August; do not inspect.

Primary score ordering:
1. reduce gross loss;
2. increase/retain winning trades and success rate;
3. increase net profit/captured favorable excursion.

Hard anti-overfit guards:
- no lookahead;
- completed higher-timeframe bars only;
- exact-tick entries/exits/trailing;
- no arithmetic PnL addition;
- one chronological ledger;
- no density collapse presented as accuracy improvement;
- preserve rejected branches.

## Key 019 starting point

017 baseline Jan-Jul:
137,288 trades / 97,533 winners / 71.043% / -$12,342.17 / -$38,839.24 GL.

019 EVENT_TIME:
136,450 / 96,908 / 71.021% / -$11,758.69 / -$38,062.86 GL.

Strict May-Jun improvement:
+$423.16 net and $484.30 less GL.

July worsens:
-$150.81 additional net damage, -$124.60 additional GL, -0.364pp success.

Tick feature family is interesting but fails April density guard:
Jan-Jul +$907.86 net improvement and $1,711.38 less GL; July +$10.90 and $46.77 less GL; April winner retention only 95.31%.

Simple MTF HH/HL vote: effectively zero.

## Community / professional sources

MetaQuotes / MQL5:
- Market Microstructure Part 6 — Order Flow.
- Market Microstructure Part 7 — Regime Classification.
- Multi-Timeframe Swing Structure Engine.
- Multi-Timeframe Structural Confirmation / Liquidity Strategy.
- Swing Extremes and Pullbacks.
- Japanese Liquidity Grab vs Market Structure Shift.
- Chinese Market Regime Detector / EA.
- Ordinal Pattern Transition Networks.
- Bayesian Online Change-Point Detection.
- Sequential CUSUM structural-break articles.

Academic:
- Cont, Kukanov & Stoikov — order-flow imbalance.
- Stoikov — microprice.
- Adams & MacKay — Bayesian Online Changepoint Detection.
- Hawkes-process OFI forecasting.
- semi-Markov duration-dependent momentum/reversal.
- ultra-high-frequency entropy/predictability.
- multiscale fractal/information analysis.

Community:
- current gold/algotrading reports on regime combinations and slippage;
- use only for hypotheses, never as performance proof.

## Promotion standard

020 is promoted only if it improves the integrated chronological system and survives May-Jun strict forward plus July stress validation. Richer complexity is acceptable only when each layer has explicit semantic ownership.

