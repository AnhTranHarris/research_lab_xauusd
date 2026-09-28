# R10 Alpha — Dukascopy XAUUSD Tick-First Python Research Engine

**Status:** Infrastructure only. No research strategy has been certified. August 2026 is explicitly sealed. All outputs from the included `smoke` mode are **test-fixture results, not alpha**.

## Data authority

The seven separate Dukascopy compressed CSVs January–July 2026 are canonical **market feed** evidence, **not** the original R9 MT5 REAL/SYNTH EA execution logs. Each original CSV is expected to contain the exact header `timestamp_ms_utc,ask_raw,bid_raw,ask_volume,bid_volume` with UTC millisecond timestamp and *integer thousandths-of-dollar* quotes, e.g. `4327902` → `$4327.902`. All monthly gz sources are checked against recorded SHA-256 hashes and read completely, including gzip CRC, bid≤ask, timestamp monotonicity, and precise UTC-month membership. Duplicate-millisecond rows are intentionally preserved in source order. No resampling or gap filling alters execution ticks. Original `.gz` source is never overwritten.

Only explicitly allowed `2026-01` … `2026-07` files can be resolved by the loader, even if August 2026 exists beside them.

## Fast architecture

- One-time month-by-month stream conversion from compressed CSV to a memory-mappable **full numeric tick cache**, including both price sides and both quoted volumes. The cache is a derived local performance layer, while original gzip remains immutable evidence.
- 250 ms / 1s / 5s / 15s / 30s / 45s, then M1 / M5 / M7 / M15 / M30 / M45 / H1 / H4 / H12 / D1: **all from ticks**, in half-open UTC-anchored buckets. The independent 45s buckets are not nested in M1. Completed bars expose `end_ms` as earliest observable completion; candle gaps are left empty.
- Vectorized NumPy multi-resolution bar reconstruction; accelerated Numba exact tick replay, no candle-based assumed stop/target ordering.
- Candidate signals identify `known_at_ms`, `ready_ms`, expiry, direction, stop, target, max hold, and unique ID. Externally authored signals must respect `ready_ms>=known_at_ms`; completed bars require `ready_ms>=end_ms`, and tick-observed features must execute strictly after the observation tick.
- Single-portfolio, one position at a time; Bid/Ask entry/exit, conservative stop-first/target-second same-tick priority, actual next-tick timeout, adverse configurable slippage and round-trip fees, initial-margin and maintenance-margin checks; no synthetic fill between ticks.
- Position/equity state carries between selected adjacent monthly blocks, with outstanding position and pending signals reported instead of secretly force-closing at midnight. The research broker model is deliberately **not claimed Coinexx-identical**; calibrate against MT5 real ticks before strategy promotion.
- Small JSON/month manifests, one compact run summary and trades/month/daily/week CSVs. Weekly view uses **provisional UTC ISO weeks** until user fixes reporting timezone and weekly boundary. No derived candle files are uploaded by default.

## Run on current Project attachments

```bash
cd /mnt/data/r10_alpha_dukas_engine
python -m alpha_dukas.cli prepare --data-root /mnt/data --cache ./cache --months 2026-01 2026-02 2026-03 2026-04 2026-05 2026-06 2026-07
python -m alpha_dukas.cli bar-audit --data-root /mnt/data --cache ./cache --output ./results --months 2026-01
python -m alpha_dukas.cli smoke --data-root /mnt/data --cache ./cache --output ./results --months 2026-01 2026-02 2026-03 2026-04 2026-05 2026-06 2026-07 --tag INFRA_SMOKE
python -m pytest -q
```

`prepare` will reuse an existing cache that passes source SHA + file size/row-count identity checks. Use `--force` to reconstruct and verify each cache from source. A source replacement with the same compressed SHA is safe; data with an unexpected compressed SHA aborts before ingestion. Keep cache files local, out of GitHub/Drive, to avoid multi-GB duplication.

## Add a strategy later

Implement an offline candidate selector producing CSV files named `2026-01.csv` through `2026-07.csv` with header:

`ready_ms,known_at_ms,side,stop_usd,target_usd,max_hold_ms,expires_ms,signal_id`

Each month's producer sees only price data observable by each timestamp, with completed bar IDs and typed side. `side` is `1=BUY`, `-1=SELL`; bracket distances are positive in $/oz; signal IDs unique; prospective market order expires when the first executable tick arrives beyond `expires_ms`. No future labels may be used. The engine intentionally does NOT bless externally generated signals as causal just because a CSV field says `known_at_ms`.

```bash
python -m alpha_dukas.cli signals --data-root /mnt/data --cache ./cache --signals-folder ./my_candidates --output ./results --months 2026-01 2026-02 --tag MY_CANDIDATE_DIAGNOSTIC
```

The `smoke` generator is a reproducible arbitrary M1-candle direction probe every 180 completed M1 candles. Its profits/losses are **meaningless as a trading recommendation** and must not be compared to R9 SYNTH or promoted.

## Research integrity

Starting balance defaults to `$200` and lot to `0.01`, contract size `100 oz/lot`, leverage `500`, simulated commission `$0.20` round-trip, and adverse slippage `$0.05` per side. These are **research assumptions only** until independently calibrated to the actual MT5 broker account, available liquidity, stop levels and latency. Bid/Ask spreads already come from Dukascopy quotes. Lot ladder defaults OFF by omission; no MUWHAHA scale-up is programmed here. Mark-to-market drawdown uses sampled executable quote, while the capital model is a simplified single-position margin approximation, not an MT5 dealer liquidation replica.

The environment validates tick/quote arithmetic and temporal consistency but **does not yet reproduce original R9 trading signals, broker rejection policies, or Python-to-MQL5 parity**. Month-by-month research scope does not turn already inspected months into untouched forward validation. August is never read until explicit authorization.

**Next stage:** choose daily/week boundaries and frozen validation plan; implement first Entry/Hold/Exit/Profit candidate as a separate branch/ledger, then test with MT5 real ticks and exact code parity.