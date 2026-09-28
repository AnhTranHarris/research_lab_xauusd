# HOLD_EXIT_022 — Exit-reason and trajectory source closure (January)

**Unit:** `R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD`  
**Stage:** `EXIT_REASON_TRAJECTORY_HARVEST_VS_RUNNER_SOURCE_CLOSURE`  
**Status:** source-parity / scientific diagnostic only. **No candidate, optimization, promotion or production authorization.** August **SEALED**.

## Input authority and exact replay

- Causal execution parent: `CAUSAL_RECERT_014` from surviving Python source `r9b_sweep_structure_exit_candidate.replay_hybrid` with historical parent candidate/ledger cache in `NET024_RAW_01.npz`.
- Reconstruct the precise position: tick at/after signal; midpoint-price plus fixed **$0.10 half-spread each side**, long entry at ask and exit at bid; short entry at bid and exit at ask. **Not actual varying Dukascopy or Coinexx spread/slippage**.
- Original ownership unchanged: `align >= 3` → initial stop $1.00, activation +$0.10, trail $0.04; otherwise stop $3.00, activation +$0.18, trail $0.05; max holding target 60s, realized at first actual tick at/after target. No synthetic quote insertion.
- The **stop/maxhold check occurs before any trail adjustment on each tick**; initial stop wins simultaneous stop/time condition, and the instrumented runner keeps original sequencing. Stop reason is disambiguated by whether a trailing ratchet occurred **before** an exit.
- Identical all-raw PnL, exit millisecond, and hold-time arrays; strict chronological one-position account selection reproduced 28,088 January selected trades, 19,087 winners, net -$4,510.087, GP +$7,001.464, GL -$11,511.551, PF .608212. January raw candidates: 34,362. Raw Jan Dukascopy ticks: 9,135,062. All underlying source-cache and gzip hashes checked against immutable NET024 Jan manifest before replay.

## Historical exit attribution — *executed original CAUSAL014 trades only*

| Attributed original exit | Trades | Winners | GP | GL | Net | Avg hold seconds |
|---|---:|---:|---:|---:|---:|---:|
| Original hard stop without ratcheted trail | 4,557 | 0 | $0 | -$8,407.2605 | -$8,407.2605 | 18.211 |
| Original ratcheted trail stop | 20,593 | 18,984 | +$6,985.3195 | -$286.1015 | +$6,699.2180 | 9.893 |
| Max-hold expiry on first available quote | 2,938 | 103 | +$16.1445 | -$2,818.1890 | -$2,802.0445 | 64.237 |

This **does not** say an EA could foresee a stop or timeout label at entry: the attribution is only known at the original exit. Hard-stop and timeout groups present *separate* possible research surfaces; a loss-avoidance action must be based on pre-exit observable precursors and undergo full re-selection to prove benefit. In particular, January HOLD022's earlier 18 generic negative/low-MFE cuts, 27 structural level invalidations and 18 late stalls were all already rejected. Do **not** mechanically cut the hard-stop group by its terminal label; that would leak future information. Retain a bankable harvester and test any runner variant separately, with GP/GL and trade/winner retention jointly constrained.

### Exact feature semantics recovered

On each actual quote, the instrumented baseline updates *only causal state through that quote*: current executable PnL (including modeled spread), cumulative MFE/MAE, first positive PnL time, first original trail-activation quote, the number of trail ratchets already executed, meaningful $0.02 favorable-extreme renewals, last actual MFE renewal timestamp, and stop position. The emitted record *at the original exit* additionally contains terminal reason, lifetime, final favorability, peak-to-exit giveback and stop-versus-maxhold collision. **Attribution and terminal exit state are retrospective forensic fields and are prohibited as earlier decision features.** Future research must capture these fields at the first valid quoted tick *before* the original parent exit; lifecycle changes must re-run every raw candidate's subsequent opportunity chronology.

### Historical entry/hold diagnostics are not the CAUSAL014 population

The frozen `ENTRY017 → ENTRY018 → ENTRY019 → ENTRY020 → ENTRY021 → ENTRY023 → ENTRY024` diagnostic lifecycle uses second/opposite requalification events. This January HoldExit022 economic ledger uses **CAUSAL014** raw sweep/structural events, not those selected ENTRY017 events. The population and signal timestamps are not interchangeable. The retained prior ENTRY017 diagnostic model has a separately reconstituted source-equivalence dossier, while the local ENTRY021/ENTRY023 source bodies and frozen models are available for later independent parity. We do **not** import their diagnostic +5s win labels, holdout success rates, or raw PNL as online inputs. Translating those states onto the current parent requires a separate explicit event-population mapping and verified equal-timestamp joins.

## Next scientific unit (not run)

`HOLD_EXIT_022_ARMED_TRAJECTORY_JAN_DISCOVERY_PREDECLARATION`: preregister a *distinct*, causally-observable post-arming `HARVEST` vs `RUNNER` rule. Begin with the arm-time survivor population, staggered real-tick post-arm checkpoints, age-since-last-meaningful MFE renewal, observed giveback, and whether current executable PnL remains behind the live stop. An action must execute on a new actual tick prior to the parent exit; only one 0.01-lot position exists; keep original trail stop as protected control. First freeze a small coherent grid and explicit net/GL/GP/DD/winner-count/trade-density gates **before** running January discovery. Avoid resurrecting pure global trail-widening, arbitrary loss cuts, post-bank re-entry, or unfrozen ENTRY diagnostics. Do not open April or May–July while diagnosing a failing January condition, and never open August without separate authorization.

## Durable artifact contract

- Exact diagnostic replay source: `scripts/r9b_hold_exit_022_exit_reason_trajectory.py`.
- Baseline checksum and source parity plus selected/raw exit attribution: `results/R9B_HOLD_EXIT_022_JAN_EXIT_REASON_SOURCE_CLOSURE.json`.
- Hash ledger: `results/R9B_HOLD_EXIT_022_JAN_EXIT_REASON_SOURCE_CLOSURE_MANIFEST.json`.
- Original candidate-index, no-future attribution arrays: private Library `/R9_Gamma_Checkpoints/HOLD_EXIT_022/HOLD022_JAN_EXIT_REASON_SOURCE_CLOSURE.npz`.
- No MQL5 build or MT5 real-tick claims.
