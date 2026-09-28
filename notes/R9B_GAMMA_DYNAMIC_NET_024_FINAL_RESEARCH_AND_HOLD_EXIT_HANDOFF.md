# NET024 — Completed-H1 Ownership as a Sequential Causal Veto

**Status:** VERIFIED_DURABLE_DIAGNOSTIC (after remote checkpoint sync), retained optional context; **NOT** a formal R9B Gamma promotion.

## Protocol and audited execution

- Parent: exact CAUSAL_RECERT_014 (all seven monthly trade/winner/net fingerprints reasserted).
- Independent event stream: all raw CAUSAL014 candidates, not just parent executed trades; strict one-position, chronological non-preemptive replay. All Jan–Jul candidate entries are strictly after preceding candidate exits.
- H1 owner: NET022 parity-reconstructed H1 signal from the completed bar only; latest owner expires after two hours. No future eight-hour outcome is used as an entry feature.
- Frozen Jan–Mar rule: veto a raw CAUSAL014 entry only when an active H1 owner points in the opposite direction AND parent five-scale alignment count is below three. Otherwise permit.
- April was calibrated once; May–July were evaluated without any further threshold change; August remains SEALED.
- All months follow the original month-cold-start contract of the authoritative CAUSAL014 raw-parent engine. The final Jan–Jul ledger is strictly non-overlapping across month boundaries as well.
- Fixed research cost model: $0.10 midpoint half-spread per side / $0.20 round-trip. Raw executable tick replay used before the frozen permission filter; real broker commission, variable spread/slippage and MT5 parity remain future validation tasks.

## Seven-month metrics

| Metric | CAUSAL014 | NET024 H1 veto | Change |
|---|---:|---:|---:|
| Trades | 197,574 | 192,669 | -4,905; 97.52% retained |
| Winners | 133,142 | 129,449 | -3,693; 97.23% retained |
| Net | -$35,399.913 | -$34,651.750 | +$748.164 |
| Gross profit | $47,325.469 | $45,869.114 | -$1,456.354 |
| Gross loss | -$82,725.382 | -$80,520.864 | $2,204.518 less loss (2.66%) |
| PF | 0.572079 | 0.569655 | -0.002424 |
| Continuous max DD | $35,400.698 | $34,652.535 | $748.163 less DD |

### Monthly result / forward wall

| Month | Net delta ($) | GL reduction ($) | Winner retention | Trade retention | PF direction | Evidence wall |
|---|---:|---:|---:|---:|---|---|
| 01 | +68.882 | +268.779 | 97.13% | 97.41% | Down | JAN_MAR_DISCOVERY |
| 02 | +103.081 | +442.497 | 96.59% | 96.97% | Down | JAN_MAR_DISCOVERY |
| 03 | +78.042 | +279.240 | 98.40% | 98.56% | Down | JAN_MAR_DISCOVERY |
| 04 | +70.693 | +241.154 | 97.54% | 97.86% | Down | APRIL_CALIBRATION |
| 05 | +127.103 | +308.712 | 97.01% | 97.29% | Down | FROZEN_FORWARD |
| 06 | +181.439 | +386.159 | 96.80% | 97.03% | Down | FROZEN_FORWARD |
| 07 | +118.926 | +277.979 | 96.72% | 97.19% | Down | FROZEN_FORWARD |

**Frozen May–July only:** 79,042 parent trades vs 76,802 candidate; parent net -$15,113.493 vs candidate -$14,686.025; +$427.468 net improvement and $972.849 less gross loss; 96.84% of parent winners retained, 97.17% of trades retained. PF falls 0.498824 → 0.496764. These are small absolute improvements in a strongly loss-making system.

## Decision

**Retain NET022 H1 ownership as an optional causal context input for entry/hold/exit hypotheses; do not promote NET024 veto as an always-on production filter.** It produces modest consistent loss compression and net improvement at small activity cost but reduces gross profit and monthly/aggregate PF. It does not fix HFT negative expectancy, July-like regime weakness, or $100–$500 account survivability. The hold/exit rebuild should default to the exact CAUSAL014 parent and run ablation with and without NET024 context; no arithmetic addition of sleeve returns.

## NEXT: HOLD_EXIT_022 — state-dependent HARVEST / RUNNER / FAIL_CONTAINMENT rebuild

1. **Source lock:** preserve CAUSAL014 exact helper bodies and golden January regression; if frozen ENTRY017/021/023 states are carried, reconstruct their missing dedicated Python bodies and assert parity with frozen model semantics. NET022 source and parity are now recovered.
2. **Preserve original event ownership:** derive live event/position states from raw bid/ask ticks; candidate hold/exit actions must be evaluated only at observable decision timestamps. Use one portfolio position and recompute downstream opportunity displacement after each exit change.
3. **Multi-trajectory state space:** IGNITION, EXTENSION, HEALTHY_PULLBACK, REACCELERATION, STALL, FAILED_ACCEPTANCE, EXHAUSTION. Action owners HARVEST, MEDIUM, RUNNER, FAIL_CONTAINMENT.
4. **Loss-tail specialist:** class/owner-specific predeclared failed-acceptance criteria using only observed P/L, realized-so-far MFE/MAE, adverse acceleration, structure conflict and bounded +250ms / +500ms / +1s / +2s / +3s checkpoints. An earlier failed generic loss-hazard classifier was NOT economically successful and is not evidence for blanket early-close.
5. **Profit-harvest specialist:** early banking on current-profits stall, giveback since currently observed MFE, profit extreme-renewal frequency, and nearby structure. Avoid reversing a banked runner simply to claim twice the teacher payoff.
6. **Persistence state router:** test frozen STRONG_RUNNER (+1s), RECOVERY (+4s), DELAYED (+4.5s), LATE_IGNITION (+4s) as causal input states, but do not call their prediction accuracy real economic improvement without complete re-entry/exit tick simulation.
7. **Independent controls and ablation:** CAUSAL014 same lifecycle; NET024 optional context with unchanged lifecycle; one Hold/Exit change; combined Hold/Exit+NET024 context. Evaluate gross loss first, winners/trade density second, net/GP recovery third, with PF, max DD and time-in-market reported.
8. **Testing walls:** Jan–Mar mechanism discovery, April fixed calibration, May–July frozen diagnostics; July has older project forensic usage and is not universally pristine for hypotheses informed by July. Keep August SEALED.
9. **Exit/portfolio ownership:** every candidate exit changes when the portfolio becomes free. Recompute full future raw entry eligibility chronologically; cannot sum reoptimized isolated trade PnLs or filter previously executed ledger and label it integrated.
10. **Production wall:** keep Hold/Exit as research until complete source closure, exact Python parity, economically useful results, spread sensitivity, $100–$500 capital overlays when serious, and later Coinexx MT5 real-tick certification.

## Audited artifacts

- Frozen discovery: `results/R9B_GAMMA_DYNAMIC_NET_024_DISCOVERY_FROZEN.json`
- Frozen April: `results/R9B_GAMMA_DYNAMIC_NET_024_APRIL_FROZEN.json`
- Forward run source: `scripts/r9b_net_024_forward_frozen.py`
- Seven-month finalizer: `scripts/r9b_net_024_finalize.py`
- Final result: `results/R9B_GAMMA_DYNAMIC_NET_024_FINAL_JAN_JUL.json`
- Final hash manifest: `results/R9B_GAMMA_DYNAMIC_NET_024_FINAL_JAN_JUL_MANIFEST.json`
- Full chronological PnL/source ledgers and raw-event month caches (January–July): private Library `/R9_Gamma_Checkpoints/NET024/`.
- July cache builder contains an inert generic `RAW_08` next-stage hint. The builder explicitly prohibits month=8; no August source was opened. The finalizer and live CURRENT_STATE explicitly route to Hold/Exit next.

**Audit status:** Jan–Jul gross-loss and net deltas are positive, but all monthly profit factors decline. Therefore the decision is retain research context, no formal Gamma promotion, no MQL5 build authority.
