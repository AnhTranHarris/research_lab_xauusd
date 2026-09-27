# Gamma Dynamic GL 001 — April frozen-January ownership replication

Status: VERIFIED_DURABLE_DIAGNOSTIC. Salvaged after polling timeout; compute was NOT rerun. August sealed.

The original January-trained ownership model (first 14 January trading days; depth 4; min leaf 150; class weight abstain 1.5; confidence 0.50) was applied unchanged to April.

April parent: 26,684 trades / 18,068 winners / -$4,735.9455 net / -$10,883.7750 GL / DD $4,744.6605.

Frozen January ownership: 23,462 trades / 16,133 winners / -$4,121.2620 net / -$9,593.2295 GL / DD $4,131.7885.

Delta: 11.8575% GL reduction, 89.2905% parent-winner retention, 87.9253% trade retention, +$614.6835 net improvement, 12.9171% DD reduction.

Interpretation: the ownership relation did not collapse in April. The Jan-Mar pooled retrain was the problem; retraining shifted the decision boundary and erased the GL edge. Preserve the original January-trained ownership router unchanged for May-Jul frozen-forward evaluation. Do not carry the January 3s failure layer or PATH augmentation.

Result SHA256 487a24ad73a62c4785a6471f62a5c262bdf455149352b7de3135fc3107de5a7a.
Source SHA256 54dfda1efe61de2688dfcb99dad86cab11f41657df7e2be8493f2e7534f53af6.
