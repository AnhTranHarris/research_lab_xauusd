# R9B Gamma Dynamic HOLD/EXIT 012 — Late Persistence Runner Capture

**Status:** VERIFIED_DURABLE diagnostic rejection.

HOLD_EXIT012 moved the runner proof point from +2s to +5s. STRONG_RUNNER still banks at +1s as the economic baseline; a causal profit-lock protects the wait to +5s, and only +5s persistence-confirmed events may extend under a peak-giveback trail.

Discovery was split into five polling-safe horizon chunks (8/10/15/20/30s). Across **343,000** exact-tick causal rules, **zero** improved both net and GP in both January halves while retaining at least 95% of banked STRONG_RUNNER winners.

Conclusion: the problem is not merely finding a later hold threshold. Keeping the original position open through the noisy bridge destroys too much banked value. The next architecture should bank the original winner, then treat later persistence as a fresh requalified entry rather than an extension.

Drive source/discovery/result/manifest identities are recorded in CURRENT_STATE. August remains sealed.

Next: R9B_GAMMA_DYNAMIC_HOLD_EXIT_013_BANK_THEN_REQUALIFIED_REENTRY.