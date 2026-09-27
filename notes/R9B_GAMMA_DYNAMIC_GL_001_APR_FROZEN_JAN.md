# R9B_GAMMA_DYNAMIC_GL_001 — April frozen-January ownership diagnostic

Status: VERIFIED_DURABLE_CALIBRATION. Not promoted. August sealed.

The original January ownership router (trained only on January's first 14 trading days, depth4 / leaf150 / class-weight ABSTAIN 1.5 / confidence 0.50) was applied unchanged to April.

April parent: 26,684 trades / 18,068 winners / -$4,735.95 net / -$10,883.78 GL / DD $4,744.66.
Frozen January ownership: 23,462 trades / 16,133 winners / -$4,121.26 net / -$9,593.23 GL / DD $4,131.79.
Delta: 11.86% less GL, 89.29% winner retention, 87.93% trade retention, +$614.68 net improvement, 12.92% lower DD.

This resolves the prior April ambiguity. The ownership relationship itself survives April; the problem is Jan-Mar pooled refitting, which nearly erased the GL edge. Therefore do not refit the candidate. Freeze the original January model for forward evaluation.

Frozen model is durably serialized with exact tree topology/thresholds/classes/features:
R9B_GAMMA_DYNAMIC_GL_001_JAN_OWNERSHIP_MODEL.json
SHA256 d7bd9421d5bc8e7ed67b96776e3f3a7e8b4bcbc43e1443f187781d9d2d8371ff.

April frozen diagnostic SHA256 487a24ad73a62c4785a6471f62a5c262bdf455149352b7de3135fc3107de5a7a.

Next: run the frozen model unchanged on May-Jul. No candidate selection or tuning may use May-Jul. August sealed.
