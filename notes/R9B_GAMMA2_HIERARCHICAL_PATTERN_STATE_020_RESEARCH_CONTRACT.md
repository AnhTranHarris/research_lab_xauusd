# R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020 — RESEARCH CONTRACT

Status: READY / RESEARCH CONTRACT ONLY. No scientific result or promotion yet.

## Purpose

The 019 exact-tick screen established three facts:
1. trade count is not the bottleneck;
2. leading event-time / tick features can modestly reduce GL while preserving almost all winners;
3. simple flat 1m/3m/5m/10m/20m HH-HL/LH-LL voting does not improve July and is therefore too coarse.

The user's revived hypothesis is now explicit: July may expose a missing hierarchical market-structure / pattern-recognition layer that can improve both July and the full Jan-Jul system.

The next unit must therefore represent structure as **ownership + transition + durability + shape**, not a majority vote.

## Frozen evidence entering 020

Formal profitable build remains:
R9B_Gamma_2_Structure_Aware_Sweep_Reclaim
Jan-Jul 215,725 trades / 175,143 winners / 81.188% / +$29,583.12 net / -$45,456.19 GL / PF 1.6508 / max DD $217.29.

017 research frontier:
137,288 / 97,533 / 71.043% / -$12,342.17 / -$38,839.24 GL.

019 diagnostic candidate:
136,450 / 96,908 / 71.021% / -$11,758.69 / -$38,062.86 GL.
019 improved GL ~2.0% and net +$583.48 vs 017 while retaining 99.36% of winners, but July worsened.

017A July forensic:
- teacher neither-side-profitable 8.12% Jan-Jun -> 15.04% July;
- daily 017 success vs teacher-neither Pearson about -0.897;
- regime age 95.46s -> 48.81s;
- oracle-best mean payoff about -45%;
- ATR excess about -51%;
- broad regime mix does not explain deterioration.

018 exact entry-at-proof was rejected due confirmation tax/latency.

## Proposed integrated state hierarchy

Tick stream
  -> execution/microstructure state
  -> intrinsic/event-time state
  -> hierarchical structural owner
  -> structural event type
  -> ordinal shape / transition state
  -> durability / break probability
  -> tradeability state
  -> specialist owner
  -> lifecycle owner

No layer is allowed to overwrite another layer semantically.

### 1. Execution / microstructure state

Carry from 019:
- actual Dukascopy spread;
- recent quote gaps;
- tick-arrival velocity / acceleration;
- signed tick imbalance and run length;
- activity and path efficiency;
- 5s / 60s directional context;
- directional-change state and age.

### 2. Hierarchical structural owner

Candidate timeframes:
- 1m
- 3m
- 5m
- 10m
- 20m
- H1 where causally available with sufficient warmup.

Do NOT calculate a vote.

For each timeframe maintain:
- confirmed swing high / swing low;
- protected high / protected low;
- current structural state: bullish / bearish / neutral / transition;
- last accepted BOS;
- last CHoCH / MSS-like transition;
- age since accepted structural event;
- number of defended touches;
- first penetration versus repeat penetration;
- whether break occurred by accepted body/close or wick only;
- whether a wick penetration was reclaimed or accepted.

Owner definition to test:
highest timeframe with a live, non-expired accepted structural state.
Lower timeframes may be:
- CONFIRMING
- TRANSITIONING
- CONFLICTING
- NEUTRAL

Do not let a lower timeframe majority overturn a higher-timeframe owner without an accepted transition.

Public reconstructible architecture:
MQL5 2026 Hierarchical Market Structure Framework:
https://www.mql5.com/en/articles/23049
It explicitly separates swing detection, protected levels, BOS/CHoCH classification, internal/external structure, state machine and MTF synchronization. It is an engineering framework, not performance evidence.

Japanese MQL5 liquidity/MTF structure:
https://www.mql5.com/ja/articles/21581
It separates macro/HTF liquidity context, intraday structure, and micro execution.

Chinese BOS reference:
https://www.mql5.com/zh/articles/15017
Useful mechanical distinction: accepted close/body break versus wick-only penetration.

## 3. Acceptance versus liquidity sweep

Maintain separate variables:
- accepted_body_break_side
- wick_sweep_side
- penetration_depth / ATR
- reclaim_depth / ATR
- time_to_reclaim
- retest_count
- level_age
- touch_count
- first_penetration flag
- post-break renewal count

A wick through a structural level is not automatically a BOS.
An accepted body close through a protected level is not automatically a continuation trade.
This state feeds the specialist router.

## 4. Ordinal pattern transition state

Public source:
https://www.mql5.com/en/articles/23451

Encode short price/return windows as ordinal permutations using Lehmer indexing.
For embedding dimension d:
number of possible patterns = d!

Recommended initial candidate:
d = 3 and d = 4 only.
Reason: d=5 requires far more observations and risks excessive lag for HFT.

### Permutation entropy

For ordinal-pattern probabilities p_i:

PE = -( SUM_i p_i * ln(p_i) ) / ln(d!)

Range 0..1.
High PE -> pattern distribution near-uniform / efficient-noisy.
Low PE -> concentrated structure.

Test on:
- tick-rule sign sequence;
- short returns;
- 1s / 5s causal return stream;
- owner-timeframe completed returns.

Do not assume raw-price encoding is superior; the public implementation found returns were more responsive for irreversibility on FX.

### Transition matrix

Let C_ij be count of pattern i followed by j.
Normalize per row:
P_ij = C_ij / SUM_j C_ij

Candidate descriptors:
- transition entropy;
- dominant outgoing transition probability;
- self-transition persistence;
- transition asymmetry;
- active-node fraction.

### Forbidden-pattern fraction

FPF = 1 - N_active / d!

Candidate interpretation:
higher forbidden fraction -> more constrained/deterministic local shape.
Must be validated; do not assume direction.

### Jensen-Shannon time irreversibility

Compare forward ordinal distribution P with reversed distribution Q.
Let M = (P + Q)/2.

JSD(P,Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)

KL(P || M) = SUM_i p_i * ln(p_i / m_i)

Use epsilon-safe zero handling.

Hypothesis:
higher time irreversibility may identify directional/structured states even when a flat structural vote looks unchanged.

## 5. Online durability / structural break equations

### Bayesian Online Change-Point Detection (BOCPD)

Public reconstructible MQL5 source:
https://www.mql5.com/en/articles/23482

The key hidden state is run length r_t: observations since the last change.

Causal recursion conceptually:

p(r_t, x_1:t)
  = SUM_{r_{t-1}}
      p(r_t | r_{t-1})
      p(x_t | x_{t-r:t-1})
      p(r_{t-1}, x_1:t-1)

Transition:
- growth: r_t = r_{t-1}+1 with probability 1-H(r_{t-1});
- change: r_t = 0 with hazard H(r_{t-1}).

Normalize to posterior p(r_t | x_1:t).

Candidate features:
- P(change now) = p(r_t=0 | x_1:t)
- expected run length E[r_t]
- run-length entropy
- posterior mass below short-run thresholds

This directly addresses July's observed problem:
classification confidence can be high while state durability is low.

BOCPD is NOT directional alpha. It is a durability / transition primitive.

Initial observation models to keep reconstructible:
- Gaussian / Normal-Gamma conjugate on short returns;
- volatility-normalized directional return;
- optionally multivariate bounded approximation later, only if scalar version survives.

### Two-sided standardized CUSUM

Public sources:
https://www.mql5.com/en/articles/23043
https://www.mql5.com/en/articles/23103
https://www.mql5.com/en/articles/23159

Let standardized observation z_t.

Positive accumulator:
S_t^+ = max(0, S_{t-1}^+ + z_t - k)

Negative accumulator:
S_t^- = max(0, S_{t-1}^- - z_t - k)

Break candidate when:
S_t^+ > h or S_t^- > h

Candidate features:
- S+ / h
- S- / h
- max(S+,S-)/h
- sign of dominant accumulator
- time since reset/break

Important public finding:
theoretical ARL calibration can be badly wrong on real financial data; h and k must be calibrated on XAUUSD under the project's frozen discovery protocol, not copied from theory.

## 6. Variance-ratio / efficiency state

Retain 019 equation candidates.

For q-period variance ratio:

VR(q) = Var( SUM_{i=1..q} r_{t-i+1} ) / ( q * Var(r_t) )

Interpretation candidate:
VR > 1 persistence / trending tendency;
VR < 1 mean-reverting tendency.

Use only as descriptive state; validate thresholds on XAUUSD.

Path efficiency over window:
EFF = abs(P_t - P_{t-n}) / SUM_{i=1..n} abs(P_i - P_{i-1})

Range 0..1.

Combine semantically:
- high efficiency + accepted structural owner + low PE -> directional continuation candidate;
- low efficiency + repeated sweeps + high PE -> rotation/noise candidate;
but these are hypotheses to test, not rules to promote.

## 7. Directional-change intrinsic-time state

Retain 019 DC state and age.

For threshold theta:
- Upturn event when price rises theta from current local minimum.
- Downturn event when price falls theta from current local maximum.
- Movement after DC event until opposite DC = overshoot.

Public research:
https://onlinelibrary.wiley.com/doi/epdf/10.1002/isaf.1552
https://www.tandfonline.com/doi/full/10.1080/14697688.2019.1669809
https://link.springer.com/article/10.1007/s10462-025-11390-9

Candidate multi-threshold stack:
theta = fixed-dollar values derived from current XAUUSD microstructure, e.g. existing $0.05/$0.10/$0.20 descriptors, plus volatility-normalized sensitivity screen.

Features:
- DC direction at each theta
- time/event age since DC
- overshoot distance / theta
- multi-threshold agreement
- threshold renewal rate
- exhaustion = long overshoot age without new extreme

No eventual overshoot length may be used before it is observed.

## 8. Pattern recognition beyond named candlesticks

Do not create a huge library of named candle patterns.

Prefer causal shape-state:
- ordinal pattern ID
- transition probability
- accepted-structure event
- wick sweep/reclaim
- path efficiency
- internal/external structural relationship.

Named patterns may be used only when they reduce to transparent geometry:
- engulfing
- pin/rejection
- inside-break
- breakout-retest
and only as secondary labels.

Japanese multi-timeframe liquidity article explicitly uses lower-timeframe reversal patterns around HTF zones, but the project should test geometry rather than copy discretionary names.

## 9. July-specific hypotheses to test

July is stress validation, not a mechanism-selection holdout.

Test whether July's higher teacher-neither share, shorter regime age and compressed excursion correspond to:

A. High BOCPD change probability / low expected run length.
B. Higher ordinal entropy / lower time irreversibility.
C. More frequent internal/external structural conflict.
D. More wick sweeps without accepted body transition.
E. Higher protected-level touch count / repeated penetration.
F. Lower owner-timeframe persistence.
G. More frequent CUSUM resets/breaks.
H. Directional-change disagreement across thresholds.
I. Lower transition-network persistence.

If any candidate improves July but harms Jan-Jun materially, reject as overfit.

## 10. 020 experimental contract

Discovery:
Jan-Mar.

Calibration:
April only after feature formulas and semantics are frozen.

Strict forward:
May-Jun.

Stress validation:
July.

Sealed:
August.

Scoring priority:
1. gross-loss reduction;
2. winning trade count / success ratio;
3. net profit / captured MFE.

No arithmetic PnL addition.
One chronological ledger.
Exact bid/ask chronology.
No future swing confirmation beyond the causal confirmation time.
No forward-looking pivot labels.
No eventual DC overshoot.
No future BOCPD state.
No reusing July to select numeric thresholds.

## 11. Screening order

Stage 020-A: Hierarchical structural owner only.
Stage 020-B: Structural owner + acceptance/sweep memory.
Stage 020-C: Add ordinal pattern transition state.
Stage 020-D: Add BOCPD/CUSUM durability.
Stage 020-E: Add retained 019 event-time/tick descriptors.
Stage 020-F: Integrated semantic router.

Each stage must report incremental value versus 017 and 019, not only standalone accuracy.

## 12. Promotion gate

Do not promote merely because 020 improves July.

A promoted Gamma successor must improve integrated Jan-Jul value versus current formal Gamma_2 after:
- transaction costs;
- trade overlap;
- one-position chronology;
- GL;
- DD;
- winner count;
- monthly robustness;
- forward integrity.

Formal promotion name only when earned:
R9B_Gamma_<next_order>_<name>

## Community / professional sources retained

English:
- MQL5 Hierarchical Market Structure Framework: https://www.mql5.com/en/articles/23049
- MQL5 Market Microstructure Regime Classification: https://www.mql5.com/en/articles/22940
- MQL5 Micro-Trend Strength: https://www.mql5.com/en/articles/23372
- MQL5 Ordinal Pattern Transition Networks: https://www.mql5.com/en/articles/23451
- MQL5 BOCPD: https://www.mql5.com/en/articles/23482
- MQL5 CUSUM Part 1: https://www.mql5.com/en/articles/23043
- MQL5 CUSUM Part 2: https://www.mql5.com/en/articles/23103
- MQL5 Structural Break Tests: https://www.mql5.com/en/articles/23159
- HFT micro-pattern permutation research: https://www.sciencedirect.com/science/article/pii/S0378437114005020
- Directional-change intrinsic time: https://www.tandfonline.com/doi/full/10.1080/14697688.2019.1669809
- DC nowcasting: https://onlinelibrary.wiley.com/doi/epdf/10.1002/isaf.1552

Chinese:
- BOS / accepted close versus wick distinction: https://www.mql5.com/zh/articles/15017
- Dynamic adaptive mean-reversion/momentum retained from prior research: https://www.mql5.com/zh/articles/18037
- Breakout/retest/secondary-break retained from prior research: https://www.mql5.com/zh/articles/18486

Japanese:
- Multi-timeframe liquidity / structure / LTF reaction: https://www.mql5.com/ja/articles/21581
- Swing extremes / pullback MTF state: https://www.mql5.com/ja/articles/21330
- Pattern-frequency / win-rate statistical extraction: https://www.mql5.com/ja/articles/15965

Korean:
Continue searching community implementations, but treat product claims as non-evidence. No Korean source is promoted into 020 unless its mechanics are transparent enough to reproduce independently.

## Current conclusion

The missing function is unlikely to be "more indicators".

The system needs a **hierarchical state representation** that answers:
1. what structure owns the market now?
2. was the structural event accepted or only swept?
3. how stable/durable is the state?
4. is the local price shape directional, random or transitioning?
5. what specialist is allowed to own the next tick-level trade?
6. what lifecycle is appropriate for that owner?

That is the 020 hypothesis.
