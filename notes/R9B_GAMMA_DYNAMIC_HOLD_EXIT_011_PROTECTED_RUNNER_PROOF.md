# R9B Gamma Dynamic HOLD/EXIT 011 — Protected Runner Proof

**Status:** VERIFIED_DURABLE diagnostic rejection.

After HOLD_EXIT010 showed that +1s-only runner extension overfit, HOLD_EXIT011 added causal protection: establish a +1s profit-lock, wait only to +2s for executable-P/L and new-MFE renewal proof, then allow a longer runner with a causal peak-giveback trail.

Discovery was intentionally split into six polling-safe max-horizon chunks (5/8/10/15/20/30s). Across **207,360** exact-tick causal rules, **zero** achieved positive net and GP improvement in both January halves while retaining at least 95% of banked STRONG_RUNNER winners.

Conclusion: +2s is still too early/noisy to unlock the long-runner GP available later in the path. Do not loosen the protection gates. Next research moves the proof point later, toward persistence-confirmed runner capture.

Drive source v2/discovery/result/manifest are recorded in CURRENT_STATE. August remains sealed.

Next: R9B_GAMMA_DYNAMIC_HOLD_EXIT_012_LATE_PERSISTENCE_RUNNER_CAPTURE.