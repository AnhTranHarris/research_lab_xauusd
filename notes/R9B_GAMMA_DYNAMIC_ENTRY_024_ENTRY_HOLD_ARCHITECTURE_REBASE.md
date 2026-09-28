# R9B Gamma Dynamic ENTRY 024 — Entry/Hold Architecture Rebase

**Status:** VERIFIED_DURABLE diagnostic gate pass. The isolated second-wave entry/hold architecture is now frozen for the next research phase.

ENTRY023 closes enough of the late-ignition gap for the architecture gate to pass. Frozen Jan-heldout / Feb / Mar all-+5s-winner recall is 85.12% / 83.74% / 83.85%. Persist-state +5s accuracy is 79.86% / 77.97% / 81.07%. The combined terminal failure states are only 8.51% / 10.24% / 9.16% positive at +5s.

Frozen state order for later MT5 parity: ENTRY017 action owner -> ENTRY018 STRONG_RUNNER -> ENTRY019 RECOVERY_RUNNER -> ENTRY020 RECOVERY_CERTIFIED / RECOVERY_UNCERTAIN -> ENTRY021 DELAYED_RUNNER / FAILED_IGNITION_CANDIDATE; in parallel, ENTRY017 selections non-positive at +1s may become ENTRY023 LATE_IGNITION at +4s. These are research ownership states, not yet economic exit actions.

The entry/hold research gate is passed. Next phase may optimize hold/exit economics, but it must consume the frozen ownership states exactly and must not silently retrain or change them.

Durable Drive source/result/manifest IDs and SHA256 are recorded in CURRENT_STATE and the Google Docs Build Capsule. August remains sealed.

Next: R9B_GAMMA_DYNAMIC_HOLD_EXIT_001_STATE_CONDITIONED_ECONOMIC_LIFECYCLE.
