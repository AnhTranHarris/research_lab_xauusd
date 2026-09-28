# HOLD_EXIT_022 — January source-exact HARVEST/RUNNER trailing geometry study

**Scientific state:** VERIFIED_DURABLE_JAN_DISCOVERY_DIAGNOSTIC, NO formal promotion. August sealed. This is the third distinct historical Hold/Exit 022 mechanism family after rejected early-negative exits (18/18) and structural level failure exits (27/27), plus rejected long-unignited late stalls (18/18).

## Why this is different

Previous candidates all *cut* trades before their original exit. This screen leaves original causal sweep/reclaim entry generation, stop distances (weak $3.00; strong $1.00), trailing activation (weak +$0.18; strong +$0.10), 60-second original maxhold and modeled bid/ask ($0.10 half-spread each side) untouched; modifies **only** the profit-trailing gap once the original trail would activate. The altered lifecycle may lengthen or shorten the position, so the complete raw independent trade stream is replayed in one-position chronological order, reselecting new available signals.

**Source equivalence and golden:** Custom `replay_variant` used line-by-line original `replay_hybrid` arithmetic and *exactly* reproduced all 34,362 January raw-event profit values **and original exit timestamps** under baseline weak-trail .05 / strong-trail .04. Reconstructed signal timestamps, direction and structural alignments also exactly matched certified January raw cache. Control ledger: 28,088 trades, 19,087 winners, net -$4,510.087; gross profit +$7,001.464; gross loss -$11,511.551; PF .608212; max drawdown $4,554.886. Raw market January gzip hash validated against NET024 immutable record.

**Predeclared before January screen:** Alternative trail widths {.025,.10,.20,.40} price units, applied weak-only, strong-only or both = 12 variants; source signed and archived BEFORE market replay. No future payoff or later month used to select inputs. Two gates: strict primary system value = Jan net improvement & no gross-loss deterioration & >=95% winner/trade retention. Diagnostic partial monetization = Jan net and GP improvement, GL deterioration <=5% of parent GL, and >=95% winner/trade retention; a diagnostic cannot be promoted until complemented and independently replicated.

## January results

- **0/12 strict-system eligible.** Tightening to `.025` reduces GL slightly but clips GP more, worsening net. Widening trades profit frequency for winner size, raises gross profit *and* gross loss, and often sharply reduces number of winners.
- Broad both-owner trail `.40`: +$388.447 net, +$1,857.629 GP but **-$1,469.182 additional GL** and retains only 63.614% of winner count. It is not an acceptable system solution.
- **Exactly one partial monetization diagnostic**: `weak_only` trail `.10` (strong stays `.04`): Jan +$9.2695 net, +$62.728 GP, -$53.4585 extra GL (~0.46% of parent GL), +0.00261 PF; retains 98.0248% of winners and 99.9715% of trades. The apparent improvement is tiny and cannot yet be considered a robust gain. Its original parent GL priority remains unsolved.
- `strong_only` trail `.10`: +$103.539 net, +$192.854 GP, -$89.314 extra GL but winner retention **94.908%**, below the predeclared 95% floor. Retain only as rejected secondary diagnostic, do not turn threshold 94.908 into a passing value post hoc.

**Interpretation:** Widening trail genuinely increases runner capture, but the independent balance between increased GP, loser damage and win-count attrition has not justified promotion. Do not use the highest net-on-January variant alone; it destroys first-class winner-count objectives.

## Next bounded historical rebuild

Replicate **only the predeclared partial diagnostic** weak-alignment trail `0.10` / strong `0.04` in February and March using exact original raw input and quote event chronology; require each month positive net / GP, winner & trade retention >=95%, GL deterioration <5%, and source equivalence. If it fails discovery, classify diagnostic only and proceed to another state-conditioned ownership mechanism, rather than tuning on April/May–July. If it passes Jan–Mar, freeze and run April once, May–July forward once. Do not open August.

## Durable evidence

Source: `scripts/r9b_hold_exit_022_runner_geometry.py`, GitHub commit `b0bb4eb8191e59a9e25d29e27fc5d2d6e6f85635`, SHA-256 `4a23916632d5591bf1d25107f2b316432d410648fa3a1935f5fff2e483da52f1`.
Predeclared contract: `results/R9B_HOLD_EXIT_022_RUNNER_GEOMETRY_PREDECLARED.json`, commit `304a0235c1fbe09f78d62163ef1e2fee2ff711e5`, SHA `372e26c5771b1eac01eab1020e123ca0033e394e5f7b98b7dab947b60e826a87`.
Full Jan screen `results/R9B_HOLD_EXIT_022_JAN_RUNNER_TRAIL.json`, commit `7a6bda00d2454ce2d978f86be9ebeb24d241191a`, SHA `33efb4fa8ff97a4c620459299407cac1005b747d2f703b1a5796225a7ee96a93`.
Jan manifest commit `ee3756895f90d9cecd04650468b561accff9ba2f`, SHA `a0977bcef0b1516eec34a3b2be8fd349137272dfed9526dd3a758cc619ebf649`.
Private Library `/R9_Gamma_Checkpoints/HOLD_EXIT_022` also has complete source/contract/result. A prior short test fixture incorrectly lacked a terminal quote for one scenario; this test-only error was resolved and logged before any market replay. No missing original tick or result data.
