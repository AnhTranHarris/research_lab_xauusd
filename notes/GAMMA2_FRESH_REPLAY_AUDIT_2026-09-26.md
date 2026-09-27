# Gamma_2 Fresh Dukascopy Jan-Jul Replay Audit — 2026-09-26

Status: VERIFIED_DURABLE_DIAGNOSTIC_SOURCE_EQUIVALENCE_BLOCKER.

A fresh independent replay was run from the raw Jan-Jul Dukascopy XAUUSD tick files using the literal durable Gamma_2 contract: 20s liquidity, wick sweep/reclaim, 5s displacement/efficiency, session-adaptive completed-M5 ATR, completed 1m/3m/5m/10m/20m alignment, fixed modeled $0.20 spread, exact ordered tick exits, and one-live-position non-overlap.

The original promoted Gamma_2 helper modules were not preserved, so this audit is explicitly not claimed binary/source equivalent to the historical promoted run.

Stored formal reference: 215,725 trades / 175,143 winners / 81.188% / +$29,583.12 net / -$45,456.19 gross loss / PF 1.6508.

Fresh literal replay: 203,225 trades / 137,145 winners / 67.484% / -$37,711.26 net / -$86,899.37 gross loss / PF 0.5660.

A control replay of the archived 007 wick-break/close-reclaim semantics reproduced its persisted January result exactly: 35,102 trades / 23,849 winners / 67.942% / -$5,916.02 / -$14,536.53 GL. This validates the current January raw data and replay machinery against the prior research environment.

Decision: do not use +$29,583.12 as a freshly reproduced investor figure. Keep it as a historical research result under a source-equivalence blocker until the missing helper semantics are recovered or a new fully preserved implementation independently reproduces the curve. Do not fold this audit into the 020 research shadow. August remained sealed and was not opened or inspected.

Local audit artifacts were hashed and supplied to the user for review before any investor report is written.