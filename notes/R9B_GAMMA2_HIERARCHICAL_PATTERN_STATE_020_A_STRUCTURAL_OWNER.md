# R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_A_STRUCTURAL_OWNER

Status: VERIFIED_DURABLE_DIAGNOSTIC_REJECTED. Not promoted.

## Purpose

First bounded stage of 020. Test whether a causal hierarchical multi-timeframe structural owner improves the 017/019 native-R9 ownership frontier before adding acceptance/sweep memory, duration hazard, change-point, or ordinal-transition state.

The unit regenerated only the minimum native-R9 cache because the historical 016/019 local checkpoint files named in the handoff were no longer retrievable. The authoritative native-R9 source was preserved. January reproduced the source-bound V2 checksum exactly: 33,793 trades and -$6,253.808 net. This was cache recovery, not re-selection of completed 016-019 science.

## Causal structural-owner encoding

Completed 1m / 3m / 5m / 10m / 20m / H1 / H4 bars only. No partial future candle state.

Per timeframe, maintain confirmed swing/accepted-body structure and derive:
- current structural direction;
- active structural boundary;
- ATR-normalized distance to the active boundary;
- age of current owner state;
- age since accepted BOS;
- lower-timeframe confirmation/conflict;
- cross-timeframe aligned/conflicting structure count.

Owner is hierarchical rather than majority vote: the highest active locally relevant timeframe under the frozen distance rule owns the event. Lower timeframes confirm or conflict.

A shallow transparent Jan-Mar classifier used only the structural-owner descriptors to choose FADE / CONTINUE / ABSTAIN teacher labels. April calibrated only the action-confidence threshold. Selected threshold = 0.45, retaining 98.35% of April trades and 98.34% of April winners versus the unthresholded structural model. May-Jun were strict forward; July was stress validation. August remained sealed and was not opened, hashed, or inspected.

## Result

020-A Jan-Jul:
- 234,740 trades
- 165,215 winners
- 70.382% success
- -$42,586.87 net
- -$84,552.45 gross loss
- PF 0.4963

Versus 017 Jan-Jul:
- +97,452 trades
- +67,682 winners
- success -0.661 percentage points
- net worse by $30,244.70
- gross loss worse by $45,713.22

May-Jun strict forward:
- 66,177 trades
- 46,374 winners
- 70.076% success
- -$12,483.25 net
- -$22,016.23 gross loss
- PF 0.4330

May-Jul:
- 96,967 trades
- 65,884 winners
- 67.945% success
- -$18,603.47 net
- -$31,377.03 gross loss

July:
- 30,790 trades
- 19,510 winners
- 63.365% success
- -$6,120.22 net
- -$9,360.80 gross loss
- PF 0.3462

July success is +1.269pp versus 017 and +1.633pp versus 019, but this comes with much higher loss and substantially worse net. Hierarchical structure by itself therefore increases coverage/ownership density without sufficient loss discrimination.

## Feature diagnostic

Structural importance in the frozen model:
- owner_age 0.2271
- owner_dist 0.1989
- lower_conflict 0.1677
- owner_bos_age 0.1264
- owner_tf 0.1200
- struct_align_count 0.0911
- struct_conflict_count 0.0369
- lower_confirm 0.0319

This is the useful finding. Direction alone is not the missing mechanism. Freshness/duration, distance to the live boundary, and lower-timeframe conflict carry more ownership information than simple confirmation count. That directly supports 020-B acceptance/sweep memory and later duration/change-point state.

## Decision

REJECT 020-A as a standalone replacement or promoted layer.

Preserve the hierarchical owner representation as context for the next bounded unit, but do not grant it standalone trade authority. The failure mode is excess participation without loss containment.

## Next bounded unit

R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_B_ACCEPTANCE_SWEEP

Add only causal acceptance/sweep state around the 020-A structural owner:
- wick penetration versus accepted close beyond boundary;
- reclaim/failed acceptance;
- first penetration versus repeated penetration;
- touch count and level age;
- normalized penetration/reclaim depth;
- owner-relative acceptance quality.

Keep the structural owner frozen. Jan-Mar discovery, April calibration, May-Jun strict forward, July stress validation, August sealed. Score gross loss first, winner count/success second, net third.

## Reproducibility

Source hashes:
- r9b_020a_hierarchical_owner.py: 1d5312f771768ba618d2b8792072216f4ecacf58eb50d2ca81b6fe0f1c081a0d
- r9b_020a_freeze.py: 897b92fdf32de4435ab68cac9bf14282b3f95d2f878784b123e6992377b6aff8
- r9b_020a_forward_eval.py: 466f3f576c91967417967f40fe053c669ef2f8d096c9124a8c442f6a12cf6431
- freeze JSON: 4c4ef4f86f7ca19cc48c43370386051d60b65328324356c214b48f784eb8ebba
- result JSON payload before durable metadata augmentation: 4f030b06d9151ba3838071f30eaf420412bc7c5ea7d03b7770252aba261abdeb

Source commits on production research branch:
- hierarchical owner source: c5b4ccf2273fbf95e5e553e9b054e66929569a2d
- freeze source: d188217cfb3735b4d58e220032f146beb9c90eb9
- forward evaluator: c62c354218b419a002b3102bf4ce064c1e4280c0

August accessed: false.
