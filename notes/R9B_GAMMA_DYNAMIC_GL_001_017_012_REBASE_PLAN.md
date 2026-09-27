# R9B Gamma Dynamic GL Reduction — Research Restart

Status: READY / research plan only. No strategy result implied.

Parent: exact causal Gamma014. August sealed.

## Objective
Reduce Gamma014 gross loss first, preserve/recover successful trades second, improve net third. R9 SYNTH/overfit is teacher/capacity map only; future information is prohibited from execution.

## Historical ranking by GL impact

### 1. 016→017 regime-confidence ownership chain — PRIMARY REBASE
016 reduced native-R9 GL by 42.06% while retaining 93.55% of native winners.
017 then reduced GL another 10.56% versus 016 while retaining 98.58% of 016 winners.
Combined historical 017 frontier: 137,288 trades / 97,533 winners / -$12,342.17 net / -$38,839.24 GL / PF 0.6822.
Relative to the native-R9 Python control GL of -$74,950.04, that is about 48.18% GL reduction. Approximate chained winner retention versus native is about 92.22%.
This is the strongest historical balance of GL compression and winner retention.
Mechanism: separate TRANSITION / ROTATION / EXPANSION ownership specialists; causal regime confidence + ATR ratio/excess + short-path returns; shallow transparent trees; April-fixed confidence thresholds.

### 2. 012 sequence-confirmed ownership — TARGETED TOXIC-LOSS SLEEVE
REGIME_GATED_5S reduced GL 55.84% versus its 010 parent and improved net by $24,338.90, but retained only 44.57% of winners.
Therefore do not reuse it as a global gate.
Reuse its sequence-confirmation/failure logic only on events already classified as high-risk / low-durability / low-confidence.

### 3. 013 regime-specialist recovery — WINNER-RECOVERY LAYER
Reduced GL 28.66% versus 010 while retaining 72.51% of winners and improving net by $13,818.03.
Use complementary regime-owned sleeves to recover winners rejected by the low-loss containment layer rather than simply flipping direction.

### 4. 019 event-time / raw microstructure — SECONDARY FEATURE LAYER
EVENT_TIME improved 017 GL by only $776.37 with 99.36% winner retention; raw microstructure improved GL more (~$1,711) but failed the April winner-retention guard.
Preserve event-time/tick-pressure descriptors as tie-breakers and early-failure state, not standalone hard filters.

## Rejected broad approaches not to repeat
- universal early-close/hazard rules from 011;
- delayed first-touch proof/OCO from 018;
- ordinary stop/trail/max-hold grids;
- unconditional flip;
- simple equal-weight MTF voting;
- indiscriminate all-feature stacking.

## Critical failure-path evidence
Real-tick history shows many losers develop negligible favorable excursion before large adverse excursion. Earlier REAL samples showed median/mean MAE far exceeding MFE and many losers with near-zero MFE. Therefore failure containment should target FAILED_IGNITION / STALL / FAILED_ACCEPTANCE after entry, but only when conditioned by ownership/regime state. Generic early-close logic was already rejected.

July evidence must be explicitly handled: teacher-neither share rises sharply, wrong-owner and toxic-executed rates rise, and regime age halves while confidence slightly rises. Classification confidence is not state durability.

## First dynamic research unit
ID: R9B_GAMMA_DYNAMIC_GL_001_017_012_REBASE

Test on causal Gamma014 event population:
1. Reconstruct 017-style regime ownership state on Gamma events.
2. Preserve 017 dominant causal features first: regime confidence, ATR ratio, ATR excess, short-path returns. Treat tree model only as discovery ceiling; later collapse viable behavior deterministically.
3. Add targeted 012-style sequence-confirmed containment only to low-confidence / low-durability events.
4. Add 013-style complementary specialist recovery for rejected winners.
5. Add 019 event-time/microstructure descriptors only after the ownership+containment core is measured.
6. Add post-entry failed-ignition state using only observed path: early P/L, MFE-so-far, MAE-so-far, time since favorable extreme, extreme renewals, adverse acceleration, recovery/reclaim attempts and turn density.

Scoring: gross-loss reduction first; winner retention / successful trades second; net third.
Validation: Jan-Mar discovery; April calibration; May-Jul frozen forward; August sealed.
No arithmetic addition of sleeve PnLs; one chronological ledger.

