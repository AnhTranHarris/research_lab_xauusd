# HOLD_EXIT_022 — February frozen armed-trajectory replication

## Scope and provenance
Historical reconstruction stage `HOLD_EXIT_022_ARMED_TRAJECTORY_FEB_EXACT_TICK_REPLICATION`. January's 12-cell preregistration was NOT revised. Only January-surviving `AT07` and `AT11` were evaluated for the February replication verdict. In the unchanged February event population, the same source-equivalent midpoint and modeled $0.10-per-side halfspread, owner-specific original activation and stops, first actual quote after arm+750 ms, signed 750-ms quote-path efficiency, and protected one-sided $0.08 RUNNER trail applied. The previous original February raw-event cache and original January experiment were hash-verified before the new market replay. No new signals, parameters or portfolio shortcuts were introduced.

**Numerical strictness:** source order `ask=ask_raw/1000.0`, `bid=bid_raw/1000.0`, `mid=(ask+bid)*0.5` exactly; equivalent algebraic rewrite previously broke parent parity. February Dukascopy 7,538,339 actual observed ticks (not dynamically synthesized to bridge gaps). Original 32,862 candidate events' PnL, exit timestamp, and holding time reproduce EXACTLY. Strict one-position chronological event selection excludes a new entry whose signal timestamp equals a previous exit.

### Original February control
- 28,188 selected positions; 18,834 winners.
- Net **-$4,450.956500020821**; gross profit **+$9,217.450999985955**; gross loss **-$13,668.407500006775**.
- PF **0.674361735263**; maximal drawdown **$4,472.950500020631**.

### Frozen candidate replication
| Rule | Feb raw promotions | Feb selected promotions | Feb net | Feb net delta | Feb GP delta | Feb GL reduction | Max-DD change (improvement positive) | Trade/winner retention | Strict Feb gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| AT07: renewal+efficiency, +750 ms, trail 0.08 | 713 | 616 | -$4,452.4285000208165 | **-$1.472** | -$1.472 | $0 | -$1.472 | 100% / 100% | **FAIL** |
| AT11: same plus strong structural align >=3 | 269 | 250 | -$4,451.2175000208235 | **-$0.261** | -$0.261 | $0 | -$0.261 | 100% / 100% | **FAIL** |

January effects were AT07 +$0.1435 and AT11 +$2.1440. Neither replicated February; gross loss remains unchanged, gross profit drops, and drawdown worsens. This falsifies their **per-month strict requirement**, regardless of later month outcomes. NO Gamma alpha promotion, MQL5 coding, April calibration, or May–July/ sealed August usage is permitted from these failed standalone mechanisms.

### Execution and safeguards
- All frozen raw events were re-evaluated before one-position chronological selection. Parent all-raw parity, non-promoted raw parity and a stop-level no-loosening assertion on promoted events were required.
- Unit fixtures: original stop ordering, unqualified parent invariance, stop-versus-time-limit, and equality-timestamp entry blocking. These fixtures are bounded and do not prove full live broker equivalence.
- Ex-post final exit reason, completed favorable excursion, and forward price action were never selection inputs.
- $0.01-lot equivalent with fixed modeled spread **is not broker-native MT5 Every tick based on real ticks, commissions or variable slippage**; no $100-$500 survivability inference from these still deeply net-negative portfolios.

### Historical reconstruction
This does **not** negate the user's separate concern about missing historical structure/indicator combinations. NET002–NET007 source paths (H1/H4 BOS, ATR/body-quality, M15 reclaim, regime and H4 structural ownership) are extant but not yet shown to be entry/lifecycle-parity integrated into this CAUSAL014 trade population. A future dedicated forensic stage must map original signals, gates, sequencing and costs before transplanting. Do not hide failed exit research by silently switching populations.

### Decision / next stage
**Reject AT07 and AT11 as standalone candidates on the February replication gate.** The preregistration specified Jan–Mar discovery/replication; a separate March run may be performed only as a *frozen diagnostic completion*, incapable of overturning the February fail, with no retune and no forward sample access. If March is skipped on fail-fast grounds, record that the Jan–Mar promotion campaign is already disproven and switch explicitly to the next independently justified historical HOLD_EXIT source-recovery lane. No automatic promotion.

## Durable artifacts
- `hold022_armed_trajectory_feb_replication.py` (immutable January engine imported by SHA).
- `HOLD022_ARMED_TRAJECTORY_FEB_REPLICATION.json` (full results, chronological daily outputs, exit reasons and gates).
- `HOLD022_ARMED_TRAJECTORY_FEB_REPLICATION_AUDIT.npz` (full raw-event outcomes for both frozen variants).
- `HOLD022_ARMED_TRAJECTORY_FEB_REPLICATION_MANIFEST.json` (content SHA-256 and input provenance).
