# R9B Gamma Dynamic HOLD_EXIT 001 — State-Conditioned Economic Lifecycle

**Status:** VERIFIED_DURABLE diagnostic; rejected as a replacement lifecycle.

Frozen ENTRY017–024 ownership states were consumed without retraining. Jan-only discovery selected state-specific fixed exits. Several specialist states improve economically, especially LATE_IGNITION and DELAYED_RUNNER, but the aggregate candidate is not robust versus the canonical lifecycle.

Frozen replication versus canonical same-event lifecycle: Jan heldout net -$169.73 vs -$113.56 (worse $56.17), February -$213.98 vs -$218.90 (better $4.92), March -$372.97 vs -$397.50 (better $24.53). Gross loss is worse in all three replications, so the candidate is rejected.

Failure diagnosis: ownership states such as LATE_IGNITION and NO_LATE_IGNITION are not known until +4s, and DELAYED_RUNNER/FAILED until +4.5s. Simply forcing all unresolved trades to wait for those states accumulates too much adverse path loss. The next unit must add causal waiting-risk containment before state resolution while preserving the recovered late/recovery winners.

This remains event-level second-wave research under the fixed $0.20 reference cost surface, not a chronological account-PnL promotion. August remains sealed.

Next: R9B_GAMMA_DYNAMIC_HOLD_EXIT_002_WAITING_RISK_CONTAINMENT.
