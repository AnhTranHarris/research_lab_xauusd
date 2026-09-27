# Gamma_2 Benchmark Recovery Lock — 2026-09-27

## Decision

The formal benchmark remains **R9B_Gamma_2_Structure_Aware_Sweep_Reclaim**:

- 215,725 Jan-Jul trades
- 175,143 winners
- 81.188% success
- +$29,583.12 net
- +$75,039.31 gross profit
- -$45,456.19 gross loss
- PF 1.6508
- max DD $217.29

This benchmark came from the frozen sequence:

1. `a314bf6114453e5175c2468d173d865c69099d16` — freeze structure-aware sweep lifecycle before forward
2. `f76cbc5c1640f7714297f9857289b44c77239b3d` — persist Jan-Apr freeze
3. `707cd70b6a81b68f2e89e03cc82d773d7c831c5b` — persist high-density structure-aware sweep candidate
4. `e32ddfd25cfd412188376732d8dc61bf0ac71ea3` — formal Gamma_2 promotion

The archived candidate source `r9b_sweep_structure_exit_candidate.py` is preserved, but it imported runtime-local helpers that were not preserved in the durable tree:

- `r9b_screen.py`
- `r9b_r8_recert.py`
- `r8_sweep_lifecycle_screen.py`

Frozen source hashes retained by the Jan-Apr freeze:

- hybrid/candidate: `59ce14e5e877be9af7d60daad60035deac46f79794d09e4d80cc558b1799f297`
- sweep generator: `e9ae373f037abd2617471fda366ed73956db7ed7db595d4d162df982769e1e6c`
- R8 recert helper: `0fb6156d36cdc6b475911466816c6c0af1c8fcc345300463e8973b3116b3704c`

The later ~68% replays are **source-equivalence reconstructions, not the formal Gamma_2 benchmark**. They must never replace the 81.188% benchmark in reporting or optimization comparisons.

## Recovery gate

No further Gamma_2 optimization is allowed to supersede the benchmark until source equivalence is restored.

First gate — January exact:
- 30,943 trades
- 25,368 winners
- 81.983001% success
- +$5,131.051 net
- -$6,091.2065 gross loss
- max DD ~$40.80

Second gate — full Jan-Jul:
- reproduce all seven monthly rows and the aggregate benchmark within exact/rounding tolerance.

Until both gates pass:
- 020-D and later optimization are paused as benchmark-dependent work;
- existing 009-020 results remain useful shadow diagnostics but are not Gamma_2 benchmark replacements;
- August remains sealed.

## Historical confirmation

Google Drive revision history shows no formal Gamma_2 in the 18:32 UTC handoff revision on 2026-09-26, then records Gamma_2 as the latest formal breakthrough by the 19:42 UTC revision. The Research Ledger later records the immediate same-day January source-equivalence failure and identifies the missing runtime-local helper stack as the cause class.

## Current priority

Recover the original helper semantics from any surviving source, cache, prior conversation artifact, or deterministic reconstruction. Do not optimize the ~68% reconstruction as though it were Gamma_2.
