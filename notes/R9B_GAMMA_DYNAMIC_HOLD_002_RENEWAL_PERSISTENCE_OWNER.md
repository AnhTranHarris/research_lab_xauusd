# HOLD 002 — Renewal/Persistence Owner

**Status:** VERIFIED_DURABLE_REJECTED.

A 1-second observed-only runner promotion was tested. Current stop was never loosened; the promotion only widened the post-activation trail to $0.15 and max hold to 120s. Profile was selected from January first-14-day capacity only. Candidate rules used observed MFE-so-far, favorable-extreme renewal count, age since favorable extreme, and giveback.

450 discovery rules were screened; 87 met the training constraints. No rule survived January-heldout + February + March with positive incremental net, non-worse gross loss, and >=95% winner retention. A representative training-selected rule (MFE>=.08, renewals>=6, age<=.5s, giveback<=.03) was effectively flat in Jan-heldout and worsened net/GL in February and March.

Conclusion: the runner extension has hindsight/capacity value, but simple favorable-extreme-renewal thresholds cannot causally own it robustly. Do not globally widen the lifecycle.

Next: **R9B_GAMMA_DYNAMIC_ENTRY_HOLD_007_TOXIC_RISK_GEOMETRY** — keep toxic events instead of vetoing them, but condition initial catastrophic risk geometry on pre-entry toxicity/opportunity state. This targets loser severity while preserving event/winner density. August sealed.
