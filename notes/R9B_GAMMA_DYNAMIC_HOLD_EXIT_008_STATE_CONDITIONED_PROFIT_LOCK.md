# R9B Gamma Dynamic HOLD/EXIT 008 — State-Conditioned Profit Lock

**Status:** VERIFIED_DURABLE diagnostic rejection.

Exact tick trailing used an absolute executable-P/L floor plus peak giveback after frozen state resolution. Only LATE_IGNITION survived January discovery: max horizon +5s, floor -$0.50, trail $0.60.

Frozen replication: Jan-heldout +$3.89 net and 14.25% GL reduction; February -$3.33 net despite 15.00% GL reduction; March +$12.25 net and 36.65% GL reduction. Winner retention stayed ~99.5–100%.

The mechanism is therefore too eager to monetize in February: it compresses losses but also clips profitable excursion. Next rebuild requires the trail to become active only after favorable excursion is proven and to incorporate renewal age / staleness rather than a static absolute floor.

All source, discovery, monthly replication, result and manifest artifacts are durably mirrored in Drive. August remains sealed.

Next: R9B_GAMMA_DYNAMIC_HOLD_EXIT_009_MFE_RENEWAL_HAZARD.
