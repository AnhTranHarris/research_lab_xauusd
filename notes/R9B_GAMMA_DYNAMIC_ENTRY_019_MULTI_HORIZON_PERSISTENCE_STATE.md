# R9B Gamma Dynamic ENTRY 019 — Multi-Horizon Persistence State

**Status:** VERIFIED_DURABLE diagnostic subclass frontier; no formal Gamma promotion and no exit/lifecycle change.

## Purpose

ENTRY018 proved that a high-confidence first-second state can identify strong +5s persistence, but runner recall remained only about 55–63%. ENTRY019 tests whether the rejected/weak population contains a distinct causal recovery-runner state rather than treating all weak +1s ignitions as early-harvest candidates.

## Frozen state machine

At +1000 ms after an ENTRY017-qualified ignition:

1. **STRONG_RUNNER** if ENTRY018 `exec_pnl_1s > 0.27175000309944153`.
2. Otherwise evaluate the frozen RECOVERY_RUNNER tree using only first-second observed fields: `exec_pnl_1s`, path efficiency, breakeven occupancy, age since last favorable extreme, breakeven recross count, MFE giveback, and second-half acceleration.
3. If recovery probability >= 0.45 -> **RECOVERY_RUNNER**.
4. Otherwise -> **HARVEST_CANDIDATE**.

The recovery classifier is a transparent depth-3 CART, min leaf 3, class weight 1:1, random state 129. The exact tree is frozen in the model artifact.

## Discovery / freeze

January days 0–6 fit candidate recovery owners. January days 7–13 select only candidates that:
- improve weak-population +5s accuracy,
- recover at least 60% of weak-population +5s runners,
- cover at least 40% of weak validation events.

Selection maximizes weak-population +5s accuracy improvement first, then recall, then coverage. The winner is refit on January days 0–13 and frozen. January heldout, February and March are replication only.

## Replication

Combined STRONG_RUNNER + RECOVERY_RUNNER:

- **Jan heldout:** +5s accuracy 67.18% -> 69.21% (+2.03 pp), runner recall **95.43%**, coverage 92.64%.
- **February:** 63.21% -> 64.33% (+1.12 pp), runner recall **93.81%**, coverage 92.17%.
- **March:** 64.24% -> 65.19% (+0.95 pp), runner recall **92.44%**, coverage 91.10%.

The STRONG_RUNNER state preserves the higher-precision ENTRY018 frontier. RECOVERY_RUNNER adds approximately 30–37 percentage points of total +5s runner recall. The recovery state is non-monotonic: some legitimate +5s runners are weak or adverse at intermediate horizons, so a single early-harvest rule would destroy valid runners.

March combined +3s accuracy is slightly below baseline (-0.69 pp). Therefore ENTRY019 is retained as a **+5s persistence/recovery diagnostic**, not as an executable hold/exit policy.

## Later MT5 reconstruction capsule

ENTRY017 entry ownership, ENTRY018 strong-runner ownership, and ENTRY019 recovery-runner ownership must remain separate deterministic states. OnTick must finalize the first-second feature vector at the first tick timestamp >= entry_time+1000 ms, then evaluate STRONG_RUNNER first and RECOVERY_RUNNER second. No future +2/+3/+5 tick may enter the decision. Log the exact tree path, leaf probability, owner state, and later diagnostic horizons for parity.

Canonical source: `scripts/r9b_entry_019_multi_horizon_state.py`.
Frozen model: `models/R9B_GAMMA_DYNAMIC_ENTRY_019_RECOVERY_RUNNER_MODEL.json`.
Full result: `results/R9B_GAMMA_DYNAMIC_ENTRY_019_MULTI_HORIZON_PERSISTENCE_STATE.json`.
Manifest: `results/R9B_GAMMA_DYNAMIC_ENTRY_019_MANIFEST.json`.

Source SHA-256: `fc5c7d10ec0a9521ff9d824251cd9beb523522327cecc84c46c174a50dd6c3f6`.
Result SHA-256: `394e1ec597eb2a81c7bce6693b12379db8506e854123f29ceeab3dc75b45dca2`.
Model SHA-256: `2c0dbc29e91b1083e6344fbc033c4eb56db3c267e6159119eab35a5621e6f84c`.

## Next bounded unit

**R9B_GAMMA_DYNAMIC_ENTRY_020_RECOVERY_RUNNER_TIMING_STATE** — characterize when RECOVERY_RUNNER transitions from weak/interim adverse to durable favorable ownership, so later hold/exit research can distinguish temporary pullback from true failed ignition without using future information. August remains sealed.
