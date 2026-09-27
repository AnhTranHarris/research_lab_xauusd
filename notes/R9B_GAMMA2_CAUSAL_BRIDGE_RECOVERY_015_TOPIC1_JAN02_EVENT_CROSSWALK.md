# R9B_GAMMA2_CAUSAL_BRIDGE_RECOVERY_015 — Topic 1 Jan-02 Event Crosswalk

Status: VERIFIED_DURABLE_DIAGNOSTIC. Not a promotion result.

Parent: causal Gamma 014. Roadmap: FORMAL TOPIC 1 — GAMMA↔R9 EVENT POPULATION CROSSWALK. August sealed/unopened.

## Clock alignment
For R9 server date 2026-01-02, the day-level preflight resolves R9 time_msc to Dukascopy UTC with a -2 hour correction. At -2h, median absolute minute-close R9 REAL Bid vs Dukascopy Bid discrepancy is about $0.295; neighboring whole-hour offsets are many dollars worse. This offset is certified for this Jan-02 unit only and must be revalidated before month/DST generalization.

## Population
- Gamma raw signals: 1,327
- Gamma executable non-overlap trades: 1,040
- Gamma signals suppressed by non-overlap: 287 (21.63%)
- R9 REAL entries: 1,525
- R9 SYNTH entries: 1,083
- Gamma executable density: 68.20% of REAL; 96.03% of SYNTH
- Gamma raw-signal density: 87.02% of REAL; 122.53% of SYNTH

Gamma causal-014 economics for the common Jan-02 interval: 1,040 trades / 705 winners / 335 losers / 67.7885% win / -$156.6715 net / +$198.0470 GP / -$354.7185 GL.

## Five-second event crosswalk
Order-preserving maximum-cardinality timestamp matching; direction is measured after the time match.
- Gamma executable vs R9 REAL: 205 matches; 19.71% Gamma coverage; 13.44% REAL coverage; 48.78% same-side.
- Gamma executable vs R9 SYNTH: 190 matches; 18.27% Gamma coverage; 17.54% SYNTH coverage; 36.32% same-side.
- Gamma raw vs R9 REAL: 255 matches; 19.22% Gamma-raw coverage; 16.72% REAL coverage; 52.55% same-side.
- Gamma raw vs R9 SYNTH: 228 matches; 17.18% Gamma-raw coverage; 21.05% SYNTH coverage; 37.72% same-side.
- R9 REAL vs R9 SYNTH: 327 matches; 21.44% REAL coverage; 30.19% SYNTH coverage; 82.87% same-side.

At one second Gamma executable has only 23 REAL matches and 33 SYNTH matches. Same-side among those small subsets is 78.26% vs REAL and 30.30% vs SYNTH.

## Interpretation
This first-day QC supports event-population identity/timing as a major bridge axis. Gamma's executable trade count is already near the SYNTH count on this day, yet most Gamma entries are not temporally colocated with R9 entries even within five seconds. Near SYNTH matches also frequently disagree on direction. Non-overlap removes about one fifth of raw Gamma signals but does not explain most of the event-population mismatch.

R9 REAL and SYNTH themselves diverge strongly in timing, but their near-time matched entries retain about 83% side agreement. Gamma does not show comparable side agreement with SYNTH.

No Gamma logic changes are authorized from this one-day diagnostic. Next unit is additional January day crosswalk validation and stable population-class aggregation.

## Durable artifacts
Personal Library:
- /R9_Rebuild/R9B_GAMMA2_CAUSAL_BRIDGE_RECOVERY_015/topic1/crosswalk_topic1_jan02.py
- /R9_Rebuild/R9B_GAMMA2_CAUSAL_BRIDGE_RECOVERY_015/topic1/R9B_GAMMA2_TOPIC1_JAN02_EVENT_CROSSWALK.json
- /R9_Rebuild/R9B_GAMMA2_CAUSAL_BRIDGE_RECOVERY_015/topic1/R9B_GAMMA2_TOPIC1_JAN02_EVENT_CROSSWALK_MANIFEST.json
- /R9_Rebuild/R9B_GAMMA2_CAUSAL_BRIDGE_RECOVERY_015/topic1/R9B_GAMMA2_TOPIC1_JAN02_EVENT_CROSSWALK_NOTE.md

Hashes:
- source script: 05bdc8b68e413dee9fc2c02879a12fcbcf673cbc7949df3b52ff0ba559939f54
- result: 3222c82ae4bc6d53c0d903da4dfe6d8abeb629077a56df931cc110195330be74
- manifest: 8ff0a04cf169ecfdbf2c55653f87dc0d0c657af4a4d7304e475928a2d940ff3c
- note: aaceb69da25bec21047855331031f3dff608e2095737bbe25d1d1a5c52b96aef
