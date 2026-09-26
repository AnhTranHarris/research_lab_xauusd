# R9B_GAMMA2_EVENT_POPULATION_IDENTITY_010

## Research purpose

Use the quarantined R9 overfit/oracle exactly as intended: a teacher for what a trade *could* have done tick-by-tick, while R9 SYNTH remains the aggregate economic target. The oracle is never an execution input on frozen forward months.

For each reconstructed sweep event, exact ticks replayed both specialist actions through the same fixed Gamma_2 lifecycle:

- FADE = sweep/reclaim direction.
- CONTINUE = opposite action.
- ABSTAIN = teacher-only label when neither action was profitable.

A transparent CART router was trained only on causal state available at the signal. Jan-Mar were discovery, April selected complexity, May-Jul were frozen forward.

## Main result

The teacher exposed a strong structural-ownership boundary: when the completed five-scale state weakly supports the sweep/fade direction (0-2 scales), FADE is more often the profitable owner; when 3-5 scales align with that direction, the teacher majority flips toward CONTINUE. This is a trade-identity result, not a profitability claim.

Frozen May-Jul compared with FADE-only on the exact same shadow event population:

- win rate: 67.11% -> 71.06%
- net: -$19,293.49 -> -$16,431.39
- gross loss: -$38,212.84 -> -$36,568.08
- improvement: +$2,862.10 net and $1,644.76 less gross loss

Jan-Jul same-population comparison:

- win rate: 67.39% -> 72.09%
- net: -$46,250.03 -> -$41,536.80
- gross loss: -$107,431.03 -> -$106,249.14

The system remains negative and is therefore not promoted.

## Scientific implication

Opportunity scarcity is not the dominant problem. Across all seven months, only a small minority of candidate events had neither specialist direction profitable under the future-informed teacher. The large remaining bridge is learning causal specialist ownership and then containing the losses when the chosen specialist is wrong.

Next unit: R9B_GAMMA2_IDENTITY_CONDITIONED_LOSS_011 — condition failed-ignition / competing-risk loss containment on the selected specialist identity, then freeze forward May-Jul.