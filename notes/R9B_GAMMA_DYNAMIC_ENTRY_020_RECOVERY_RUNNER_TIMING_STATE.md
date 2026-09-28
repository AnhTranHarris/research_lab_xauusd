# R9B Gamma Dynamic ENTRY 020 — Recovery Runner Timing State

**Status:** VERIFIED_DURABLE diagnostic subclass breakthrough candidate; no formal promotion and no executable exit/lifecycle change.

## Purpose
ENTRY019 proved that weak +1s ignitions can later become valid runners. ENTRY020 maps that recovery timing and asks whether a later causal checkpoint can certify persistence without future information.

## Causal rule
Inside the frozen ENTRY019 RECOVERY_RUNNER population, observe exact ticks through +4s. At the first tick timestamp >= entry_time+4000ms, compute executable P/L in selected direction and giveback from the post-1s maximum favorable excursion.

Emit RECOVERY_CERTIFIED only when exec_pnl_4s >= 0.05 and giveback_from_post1_MFE <= 0.50. Otherwise remain RECOVERY_UNCERTAIN. The +5s outcome is a training/diagnostic label only and may never enter the +4s decision.

## Frozen replication
- Jan heldout: +5s accuracy 59.83% -> 85.48% (+25.65 pp), coverage 52.99%, runner recall 75.71%.
- February: 57.14% -> 82.72% (+25.57 pp), coverage 46.29%, runner recall 67.00%.
- March: 56.32% -> 90.27% (+33.94 pp), coverage 43.30%, runner recall 69.39%.

Teacher timing also shows roughly 60-67% of RECOVERY_RUNNER events dip below executable breakeven after +1s, confirming non-monotonic recovery.

## MT5 reconstruction capsule
ENTRY017 entry ownership, ENTRY018 STRONG_RUNNER, ENTRY019 RECOVERY_RUNNER, and ENTRY020 RECOVERY_CERTIFIED remain separate deterministic states. OnTick continues the selected-direction post-1s path accumulator through +4s. At the first tick >= +4000ms calculate current executable P/L and giveback = post1_MFE - current selected-direction displacement, then apply the exact thresholds above. ENTRY020 alone must not close or extend a position until later lifecycle economics authorize it.

Required parity log: lineage identifiers, entry time/mid/reference quote, +4s selected-direction displacement, executable P/L, post-1s MFE, giveback, RECOVERY_CERTIFIED/UNCERTAIN label, and later +5s diagnostic outcome.

## Durable identities
Canonical source: scripts/r9b_entry_020_recovery_timing_state.py.
Canonical result: results/R9B_GAMMA_DYNAMIC_ENTRY_020_RECOVERY_RUNNER_TIMING_STATE.json.
Canonical manifest: results/R9B_GAMMA_DYNAMIC_ENTRY_020_MANIFEST.json.
Raw source/result/manifest are mirrored in the Drive recovery folder. August remains sealed.

## Next
R9B_GAMMA_DYNAMIC_ENTRY_021_RECOVERY_TRAJECTORY_OWNER — separate delayed-runner from true failed-ignition states inside RECOVERY_UNCERTAIN before any executable hold/exit policy is attempted.
