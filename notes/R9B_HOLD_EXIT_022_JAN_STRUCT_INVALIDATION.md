# HOLD_EXIT_022 — January causal sweep-level invalidation (historical lifecycle rebuild)

**Decision: REJECT_HISTORICAL_RECLAIM_LEVEL_EXIT_AS_STANDALONE.** This is the second distinct January containment hypothesis under HOLD_EXIT_022. The first, static current-PnL / MFE loss cuts, had all 18 variants worsen economics. The new experiment tests whether price truly re-invalidates the original sweep/reclaim setup before the original fixed-horizon/stop/trail lifecycle closes, using the *same original causal level* captured from the reconstructed Gamma_2 event engine.

## Source closure and tests

- Source: `scripts/r9b_hold_exit_022_structural_invalidation.py`, frozen pre-outcome source commit `b06b9cb57741cb7a52c29b1bfbfd8956da14207d`; SHA-256 `710b3729a5e24b22eb11de9f20014709cb4931095b45352b0eb4cf0d489be0af`.
- Frozen pre-outcome contract: `results/R9B_HOLD_EXIT_022_STRUCT_INVALIDATION_PREDECLARED.json` commit `bcee0d74fd832b137d32a9cdc3cf52211d6d3f5e`, SHA-256 `0eabf6603b7e8ff4adc209f60626b96e7816adbc04a32603a8ebc7d91c2dc0a6`.
- Reconstructs original raw sweep/reclaim events from immutable Dukascopy Jan 2026 ticks (9,135,062) using `r9b_screen.py`, `r9b_r8_recert.py`, `r8_sweep_lifecycle_screen.py`. `event_ms`, `side`, and `five_scale_align` exactly equal frozen NET024 raw-event cache for all 34,362 events; source raw and parent cache SHA validated.
- Golden baseline exact: 28,088 parent selected trades; 19,087 winners; net -$4,510.0870; gross profit $7,001.464; gross loss -$11,511.551; PF .608212; max DD $4,554.886.
- Exact causal rule: **for a short**, simulated executable ask > prior sweep/reclaim level + buffer; **for a long**, executable bid < same original level - buffer; the adverse penetration must remain observed for specified consecutive duration. Close on the actual first qualifying tick *strictly before* the parent exit, which retains precedence. Every RAW parent event is independently counterfactually closed or left unchanged, then the full account is chronologically reselected (one active position, no overlap). Fixed model half-spread $0.10 per side, not historical broker bid/ask parity.
- Parameter grid declared before market replay: buffer ∈ {0.00,0.10,0.25} price units; sustained failure confirmation ∈ {0,500,1500} ms; structural ownership ∈ {all, weak five-scale alignment (<3), strong alignment (≥3)} = **27 variants**.
- Synthetic tests verify level polarity, stop-before-failure same-tick ordering and no backdating. New `.npz` observation cache was successfully ZIP-CRC checked and SHA-256 hashed. Jan screen completed in approximately 8.9 seconds, no August access.

## Results and interpretation

**0 of 27** variants improved January net. None passed the predeclared combined gate (net improvement, less gross loss, ≥95% retention of winners/trades). Even the least harmful variant (strong-align only; +$0.25 buffer, 1500ms confirmation) worsened net by $59.3245, lowered gross profit by $105.0755, compressed gross loss by only $45.7510, lost 290 winner-count units, and reduced PF .608212 → .601475. Immediate adverse quote-crossing across both owner classes compressed gross loss by $319.262 but sacrificed $1,240.430 gross profit, worsened net by $921.168 and retained only 85.48% of winners. The apparent new trade opportunities freed by earlier closure did not save net. H1 NET024 context was not forced into this independent test.

**Scientific conclusion:** a single adverse recross of the causal sweep level, even held for up to 1.5 seconds, is not enough to distinguish a failed thesis from a legitimate longer recovery under CAUSAL014. The level is a meaningful setup anchor, but it is not an independent universal exit. Do not optimize its thresholds on April or frozen forward months. This is a negative/diagnostic result, not a formal Gamma breakthrough.

## Full traceability

- JSON screen: `results/R9B_HOLD_EXIT_022_JAN_STRUCT_INVALIDATION.json`, GitHub commit `484cf21373c766024b4459e2e964b6b0f0587dd9`, SHA-256 `9bdd1c3dd85dfe7719e3d00eeebee9122fe59e8f91c06bbacf55f55af16e0e6a`.
- SHA and January regression manifest: `results/R9B_HOLD_EXIT_022_JAN_STRUCT_INVALIDATION_MANIFEST.json`, commit `70733f397b61a9c03b38466a6c0b4f22c4a2fa96`, SHA-256 `d9085630608d3742719ce2520b19d50894f538bb0cae53d8c43f7761d1d66c11`.
- Validated observed failure tick cache: private Library `/R9_Gamma_Checkpoints/HOLD_EXIT_022/HOLD022_JAN_STRUCT_LEVEL_OBS.npz`, SHA-256 `eb1752974724a3c7d11466e0182b2d7949ebb9974c466fb860691327fc5047c9`.
- Chronological candidate outcomes and full January screen in GitHub JSON; no forward data accessed. August SEALED.

## Exact successor within historical rebuild

**HOLD_EXIT_022_CAUSAL_HARVEST_RUNNER_PROOF_DESIGN**: evaluate original Gamma_2 lifecycle tail anatomy by causal entry cohort, and test controlled BANK / MEDIUM / RUNNER profit capture or trailing-geometry adaptation on raw ticks. Distinguish stops, max-hold, and early trailing payouts before specifying a hold extension. January discovery first; continue Feb/Mar only if a causal contender actually improves original-account economics. Do not resurrect generic early-negative cuts or free a position retrospectively. Any candidate must model the full chronological competing raw entry set, fixed transaction costs, and requalification of changed availability. Historical ENTRY017–024 state categories are diagnostic; source parity required prior to transplant.