# R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_C_ORDINAL_TRANSITION

Status: **VERIFIED_DURABLE_DIAGNOSTIC_REJECTED**. Not promoted.

## Purpose

Third bounded stage of 020. Freeze the 020-A hierarchical structural owner and the 020-B acceptance/sweep context, then test whether causal ordinal-pattern transition state adds durable incremental value without changing entry timing, structural ownership, or acceptance semantics.

The unit tested only reconstructible ordinal descriptors:
- d=3 ordinal permutation state on causal log returns;
- transition entropy;
- permutation entropy;
- forbidden-pattern fraction;
- forward/reverse transition-distribution Jensen-Shannon irreversibility;
- local edge probability, node self-transition, concentration, node entropy, pattern age, and current-pattern identity.

No future path, MFE/MAE, incomplete future candle, or August information enters the features.

## Method cross-reference

The mechanism family was reconstructed from transparent public methodology, used only as hypothesis/method support rather than performance evidence:
- MQL5, *Ordinal Pattern Transition Networks in MQL5*: https://www.mql5.com/en/articles/23451
- Physica A, *Characterizing the statistical complexity of nonlinear time series via ordinal pattern transition networks*: https://www.sciencedirect.com/science/article/pii/S037843712300225X
- *Time irreversibility of time series*: https://pmc.ncbi.nlm.nih.gov/articles/PMC7513188/
- Scientific Reports, *Ordinal partition transition networks*: https://www.nature.com/articles/s41598-017-08245-x

The MQL5 defaults were not imported as XAUUSD parameters. A bounded XAUUSD grid was screened using existing certified caches. Dimension was fixed at d=3 to preserve transition-count support; causal scales/windows included tick, active-1s, 5s, 15s and completed M1 representations. April alone selected representation/threshold after Jan-Mar discovery.

## Validation

- Jan-Mar: discovery/training.
- April: calibration/selection only.
- May-Jun: strict forward evidence.
- July: stress validation, not used for selection.
- August: sealed and not accessed.

Scoring order remained gross loss first, winning trades/success second, net third. Density-collapse candidates were ineligible.

## Broad ordinal screen

The full transition-network representations did not improve the durable frontier. The least-bad broad representation was active-1s d=3/window-90 at threshold 0.45, but it worsened May-Jun gross loss by about $116 and May-Jun net by about $95. July improved by about $54 net and $26 gross loss, which was insufficient because the strict forward period degraded.

Feature attribution showed most ordinal-network statistics were weak in the transparent tree. A local transition edge-probability feature appeared useful enough to justify one bounded decomposition rather than adding more feature families.

## Narrow decomposition

The bounded subsets were EDGE, IRR, COMPLEX (permutation entropy + transition entropy + irreversibility + forbidden fraction), TRANS, and FULL. April selected **TICK_D3_W90_COMPLEX**, threshold **0.45**.

April versus 020-B:
- same 32,007 trades;
- gross loss improves by $20.76;
- net improves by $20.35;
- 9 fewer winners.

Strict May-Jun versus 020-B:
- same 66,193 trades;
- +25 winners;
- success +0.0378pp;
- **gross loss worsens by $64.28**;
- **net worsens by $45.95**;
- max trade-sequence drawdown worsens by $45.95.

July versus 020-B:
- same 30,785 trades;
- 16 fewer winners;
- success -0.0520pp;
- gross loss improves by $16.86;
- net improves by $54.02;
- max trade-sequence drawdown improves by $54.02.

May-Jul combined:
- same 96,978 trades;
- +9 winners;
- net +$8.06;
- **gross loss worsens by $47.42**.

Jan-Jul:
- same 234,294 trades;
- 165,624 winners, +10 versus 020-B;
- success 70.6907%, +0.0043pp;
- net -$42,903.97, +$35.88 versus 020-B;
- **gross loss -$84,501.08, $47.38 worse than 020-B**;
- max trade-sequence drawdown improves by $35.88.

This fails the primary gross-loss objective and does not survive the strict forward gate as an incremental system layer.

## Diagnostic interpretation

Ordinal transition state is not completely inert: tick-scale transition entropy and time-irreversibility entered the transparent model, and July showed a small improvement. But the sign of the economic effect is unstable across May-Jun versus July. The mechanism behaves as a context descriptor, not a durable standalone ownership layer.

The result supports the next planned stage rather than more ordinal tuning: explicitly model **state durability / change probability** using the already planned semi-Markov duration, BOCPD run-length/change probability, and owner-conditioned CUSUM family. July's known state-age compression remains a more direct target than further ordinal-network complexity.

## Decision

**REJECT 020-C as standalone authority and do not alter formal R9B_Gamma_2.**

Preserve the ordinal descriptors and caches as diagnostic context. Do not retune the same ordinal grid over the same Jan-Jul data. Do not open August.

## Next bounded unit

**R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_D_BOCPD_CUSUM_DURABILITY — READY**

Freeze 020-A/020-B semantics. Test state-duration/change-point durability only: empirical semi-Markov duration hazard, bounded causal BOCPD run length/change probability/entropy, and structural-owner/regime-conditioned CUSUM. Jan-Mar discovery, April calibration, May-Jun strict forward, July stress validation, August sealed. Score gross loss first, winners/success second, net third.

## Reproducibility

Source SHA-256:
- r9b020c_ordinal.py: `7e40f3d33a875d930092b47663eab1737d495b0b79a1838d2bbace4ecfd6267c`
- r9b020c_eval.py: `354b2a0cf7f39e6c30ac4defeb0d7c23d98e52d6f2b8c4e321c0cd614fb80546`
- r9b020c_subscreen.py: `18fc031b9dfe5666f7681bf40419e305503c4dab512ffe0e9ec3714a974f739a`
- r9b020c_finalize.py: `df69e59e308ec695e6018999a54aaa6da747476a66fa34555b91d287e2403002`
- final result JSON: `7fbe48cd313d78fecf35bbde54a9021e1d0cd003d5215144cbcc8cf34635e15a`

Monthly 020-C cache hashes are bound inside the result JSON. August accessed: **false**.
