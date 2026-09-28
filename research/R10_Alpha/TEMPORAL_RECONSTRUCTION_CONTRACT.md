# R10 Alpha — Tick-to-Timeframe Reconstruction Contract
**Status:** REQUIRED ARCHITECTURAL RULE, NOT A TRADING BREAKTHROUGH OR A TEST RESULT.
**Scope:** XAUUSD January 1–July 31, 2026. August SEALED.
**Authority:** user's timeframe-architecture clarification, R10 Alpha handoff, Master Sections 109–111.

## Single market stream, multiple causal views
The canonical event stream is actual ordered ticks with millisecond timestamp, bid, ask, flags (where available), and stable input sequence order for ties. Python Dukascopy source ticks and MQL5 broker/MT5 real ticks remain **distinct datasets**, each source-verified. They are never claimed to generate identical profit merely because each is called 'tick data'.

The **required custom intervals in milliseconds** are: `250, 1000, 5000, 15000, 30000, 45000`. Build all from ticks. Then construct M1 and longer minute/hour/day intervals from the same tick stream or from lossless OHLC aggregations of completed aligned lower bars. Retain raw ticks for all price-path, spread, stops, fill, and intrabar-ordering questions.

This is one synchronized **logical hierarchy**, not an assertion that native MT5 server bars are literally built from the EA's custom second bars. The EA may compare independently constructed native-equivalent bars against actual MT5 M1/H1/D1 bars to diagnose broker session/time-zone aggregation differences.

## Exact deterministic bar semantics
- Define a universal bucket start `start_ms = floor(timestamp_ms / interval_ms) * interval_ms` on an explicit UTC-based time axis; bars are half-open `[start_ms, end_ms)`. Record UTC-to-broker-server offset rules rather than mixing clocks.
- Preserve tick sequence order when timestamps collide; no inventing future tick order or quote updates.
- Retain at least first/last observed Bid and Ask, separate Bid/Ask high and low, tick count, available tick flags, first/last tick timestamps, and spread metrics. Select and document one signal price convention per feature (bid, ask, or mid); execution always uses executable sides.
- A bar is **complete only after its ending boundary has passed**; consume a completed bar no earlier than the first subsequently processed executable tick. The ongoing bar may be used only by formulas explicitly designed for incomplete-bar observations, with a matching Python/MQL5 proof. No future high/low/close is visible early.
- No tick in a time bucket: no factual OHLC candle. Mark missing/empty; if a separate carry-forward display/state convention is needed, distinguish synthetic no-trade observations from real sampled bars.
- The 45-second bar does **not** partition a minute. Its independently anchored boundaries must not be reset at each M1 open; ensure exact temporal overlap handling without recasting an H/M aggregate as a chain of 45-second candles.
- Minute/hour/day aggregations may use completed lower bars for OHLC when temporal boundaries exactly nest; for non-nesting intervals, aggregate from source ticks or independently aligned finer bars and never assume lossless derivation of event ordering from OHLC.

## Every research mechanism must disclose temporal inputs
For each candidate strategy, meaningful improvement, formula, indicator, or state machine, specify its tick or bar input resolutions, event/source IDs, earliest causally available time, time-zone and session alignment, current-versus-completed bar availability, first executable tick, bid/ask treatment, spread and explicit costs, order lifecycle, position arbitration and collision rules. Multiple timeframes share **one time-indexed market state**, not independent votes or profit ledgers. Derived multi-timescale features must never include a bar that has not finished by the decision tick.

All decisions are tick-driven. Historical Python must execute entries/exits/stops and simulate slippage on chronological ticks rather than assuming a fill at a candle close or resolving stop/target order from an OHLC candle. If a fast test uses precomputed bars, mark it a screen; rerun the candidate in exact tick replay before promoting.

## Eventual MT5 EA design
- Maintain a memory-bounded per-interval rolling bar builder updated from `MqlTick.time_msc` + bid/ask; process every retained new real tick exactly once where possible.
- Use `OnTick` as notification, but guard against event coalescing: MetaQuotes states that NewTick events are not queued when an OnTick event is already queued/processing. Evaluate catching up using `CopyTicksRange` / `CopyTicks` from the last processed millisecond+stable tie order, and explicitly handle duplicate timestamps, gaps and reconnects. Do **not** claim automatic lossless live feed capture without measurement.
- The main EA chart may be M1; the internal 250ms / S1 / S5 / S15 / S30 / S45 series require no native MT5 chart periods. M1/H1/D1 platform candles can provide cross-checks but cannot silently replace the specified exact source-tick build.
- Keep state calculation fast enough to avoid OnTick event loss, prove replay/restart recovery, use bounded tick-ring buffers, and log bar boundary/state/decision identities for diagnostics.
- For Python↔MQL5 parity, replay the **same timestamped Bid/Ask tick input** through both implementations to compare OHLC, feature vectors, decision times, orders, fills, stops, trail behavior, positions and PnL. Separately certify real Coinexx MT5 history and demo behavior. Dukascopy and Coinexx cross-feed differences must be reported, not hidden.

## Scope and reporting
Maintain **daily / weekly / monthly / Jan–Jul aggregate** tick-identity and trading ledgers. A weekly calendar definition and accounting/session time zone remain **PENDING USER DIRECTION**. Scope expansion does not make months previously observed for optimization untouched forward tests; validation partitioning must be frozen independently before certification. August remains sealed.

**This file only establishes an engineering contract. No Alpha backtests have run and no EA has been compiled.**

## Relevant platform specifications
- https://www.mql5.com/en/docs/constants/structures/mqltick
- https://www.mql5.com/en/docs/series/copyticksrange
- https://www.mql5.com/en/docs/event_handlers/ontick
- https://www.mql5.com/en/docs/constants/chartconstants/enum_timeframes
- https://www.metatrader5.com/en/terminal/help/algotrading/tick_generation
