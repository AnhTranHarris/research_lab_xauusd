# R9B Gamma Dynamic HOLD_EXIT 002 — Waiting Risk Containment

**Status:** VERIFIED_DURABLE diagnostic; static-stop frontier retained as capacity evidence, not promoted.

Separate pre-resolution loss stops were tested for the +1s weak-positive recovery branch and +1s non-positive late-ignition branch. Stops are evaluated only before the frozen +4/+4.5s state-resolution tick.

Best January-discovered pair: recovery wait stop -$1.00; late-ignition wait stop -$1.25. Frozen Jan-heldout / Feb / Mar gross-loss reduction versus HOLD_EXIT001 is 7.72% / 4.73% / 5.77%, while preserving 93.25% / 93.69% / 96.84% of valuable RECOVERY_CERTIFIED / DELAYED_RUNNER / LATE_IGNITION events.

Net improves +$13.86 / -$1.21 / +$48.14 versus HOLD_EXIT001. The February regression means the static-stop pair is not robust. It also does not robustly beat the canonical lifecycle.

Conclusion: waiting risk is real and distance stops help, but distance alone is too blunt. The next unit must condition early cut/continue decisions on observed pre-resolution path state while keeping the frozen entry/hold ownership semantics unchanged.

Next: R9B_GAMMA_DYNAMIC_HOLD_EXIT_003_DYNAMIC_WAITING_HAZARD. August remains sealed.
