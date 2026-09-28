# R9B Gamma Dynamic ENTRY 023 — Late Ignition Owner

**Status:** VERIFIED_DURABLE diagnostic subclass breakthrough candidate; no formal Gamma promotion and no executable exit/lifecycle change.

ENTRY022 showed that roughly half of +5s winners are still non-positive at +1s. ENTRY023 isolates that late-ignition population.

The frozen depth-1 tree collapses to one deterministic rule at +4s: if current executable selected-direction P/L is greater than **$0.01675**, emit **LATE_IGNITION**; otherwise emit **NO_LATE_IGNITION**. The +5s outcome is a teacher/diagnostic label only.

Frozen Jan-heldout / Feb / Mar selected +5s accuracy is 83.14% / 84.98% / 85.78% versus late-ignition-population baselines 26.02% / 31.36% / 30.95%, an uplift of +57.12 / +53.62 / +54.82 pp. Winner recall is 74.87% / 77.32% / 78.50% at 23–29% coverage.

MT5 mapping: for ENTRY017-owned trades still non-positive at +1s, keep the legacy lifecycle unchanged while tracking selected-direction executable P/L. At the first tick >= +4000ms, compare current executable P/L to $0.01675 and emit the diagnostic LATE_IGNITION state. This state does not itself authorize an exit or extension yet.

Durable Drive source/result/model/manifest IDs are recorded in CURRENT_STATE and the Google Docs Build Capsule. August remains sealed.

Next: R9B_GAMMA_DYNAMIC_ENTRY_024_ENTRY_HOLD_ARCHITECTURE_REBASE.
