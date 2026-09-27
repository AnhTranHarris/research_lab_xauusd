# R9B_GAMMA_DYNAMIC_GL_001 — January discovery checkpoint

Status: VERIFIED_DURABLE_DIAGNOSTIC. Not promoted. August sealed.

Parent is exact causal Gamma014. January was split chronologically: first 14 trading days discovery/training, last 7 trading days held-out diagnostic. Teacher FADE/CONTINUE outcomes use future path only to create discovery labels; all held-out execution decisions are causal and use exact observed ticks.

## Main findings

1. 016-style shallow ownership routing transfers modestly to Gamma014.
Held-out parent: 15,752 trades / 10,686 winners / -$2,448.73 net / -$7,087.69 GL / max DD $2,494.96.
Balanced ownership router: 14,122 trades / 9,725 winners / -$2,211.56 net / -$6,427.73 GL / max DD $2,222.12.
Delta: 9.31% GL reduction, 91.01% parent-winner retention, +$237.17 net improvement.

2. The first 017-style regime split based only on 30s path-efficiency is rejected as a regime definition.
Gamma sweep events are overwhelmingly low-efficiency under that representation, so the three-regime partition collapses. Historical 017 exact source code is not preserved; only method/results are durable. Do not claim source-equivalent 017 transfer.

3. Simple early failed-ignition cutoff is rejected.
Rules based only on fixed horizon + current adverse P/L + low MFE can cut GL sharply, but only by deleting too many eventual winners. This reproduces the prior 011 failure mode.

4. Ownership-conditioned post-entry path-state failure containment survives.
At a 3s causal horizon, a depth-3 shallow failure tree using pre-entry ownership state plus observed path-state features reduced held-out GL to -$6,255.76, net to -$2,175.41, max DD to $2,185.87, with 9,490 winners.
Versus Gamma014 parent: 11.74% less GL, +$273.32 net, ~12.39% lower DD, 88.81% winner retention.
Versus the ownership router alone: 2.68% additional GL reduction, +$36.15 net, 97.58% router-winner retention.
Inputs are causal at 3s: current P/L, MFE/MAE so far, giveback, recovery from MAE, excursion span, path efficiency, turn count, time since extrema, favorable extreme renewal count, plus pre-entry ownership/context.

5. 013-style recovery confirms the old Pareto cost.
Recovering abstained opportunities with separate FADE/CONTINUE profitability specialists can raise parent-winner retention to ~92.85%, but GL improvement falls from 9.31% to 7.08% and net improvement falls from +$237.17 to +$190.26. Recovery remains a later sleeve, not the GL core.

6. 019-style leading tick descriptors are mixed.
Pre-event PATH descriptors improve the ownership screen modestly: 10.83% GL reduction, 89.67% winner retention, +$305.57 net, DD $2,178.42.
Tick intensity alone adds no incremental value. Full microstructure stacking also adds no useful GL improvement. Preserve path descriptors; reject indiscriminate micro-feature stacking.

## Frozen February replication candidates

A. OWNERSHIP_BASE:
depth 4 shallow action tree, historical 016-style class weighting, minimum action confidence 0.50, causal pre-entry features only.

B. OWNERSHIP_PLUS_FAILURE:
A plus fixed 3-second post-entry shallow failure state; depth 3 / leaf 100 / loss-probability threshold 0.55. No delayed entry and no backdating.

C. PATH_OWNERSHIP:
pre-entry ownership with tick-path descriptors only, using the January-selected PATH family; no all-feature stack.

February must run these frozen January-selected configurations before any Jan-Feb refit. Score GL first, winner retention second, net third. If none replicates, do not broaden complexity blindly.

Durable Library root:
/R9_Rebuild/R9B_GAMMA_DYNAMIC_GL_001/

Key SHA256:
- Jan cache d29a7eb54b1abb5d7811da8cc1cf47ac11c9f65058d58e9bdef78785b5c61af4
- Jan ownership screen cf817177c669c659624d02cec626925a5808d354c3cf926dbcdb88d03fa9df09
- failure tree c2a35cd14f8842eae57a5be27e8f7a32f1fd216e6c765e2e53186c512d23fe29
- recovery screen b4a44e3184eb96424898a2ebd7bf17cf4c10e907ccafbfe9cfc7fbb5580eca06
- micro screen 8f609b4ad0b4522dceddbe2e0afb04833876082af94ba97a9400bb6400abaa31

No August access.
