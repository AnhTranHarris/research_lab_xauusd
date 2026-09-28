# HOLD_EXIT_022 — January armed-trajectory discovery checkpoint

The frozen 12-cell HARVEST→RUNNER screen was executed on January 2026 exact Dukascopy ticks only, using the frozen CAUSAL_RECERT_014 raw candidate stream.

Parent parity: 28,088 selected trades, 19,087 winners, -$4,510.087 net, +$7,001.464 GP, -$11,511.551 GL, PF 0.6082120472, max DD $4,554.8855. Full raw chronological one-position re-selection was applied after each modified exit.

A numerical source-parity hazard was found: computing midpoint as `(ask_raw + bid_raw)/2000` produced 610 raw-PnL mismatches. Reproducing the historical operation order exactly — `ask=ask_raw/1000`, `bid=bid_raw/1000`, then `mid=(ask+bid)*0.5` — restored exact 34,362/34,362 raw parity. Preserve this operation order in future rebuilds.

Strict January survivors:
- AT07: renewal+efficiency, 750 ms decision, $0.08 runner trail. +$0.1435 net, +$0.1435 GP, GL unchanged, max-DD improvement $2.2815, 100% trade and winner retention.
- AT11: renewal+efficiency+strong-owner, 750 ms decision, $0.08 runner trail. +$2.1440 net, +$2.1440 GP, GL unchanged, max-DD improvement $2.1440, 100% trade and winner retention.

Both are **small-effect** and fail the predeclared materiality threshold, so they are not promoted Gamma alpha. They survive only as frozen February replication candidates. AT10 had the largest nominal net improvement (+$12.6235) but failed the strict gate because GL worsened by $2.8585 and 15 parent winners were forfeited.

Historical forensic flag: NET002–NET007 source families still exist — H1/H4 BOS + ATR/body-quality, H1→M15 retest/reclaim, structural regime state, H4 runner/ownership, persistent H4 owner + H1 BOS, and failed higher-timeframe acceptance. They were not mixed into this stage because source-to-CAUSAL014 lifecycle parity is not proven. Preserve them for a dedicated historical-combination archaeology lane after the current historical sequence.

Next bounded stage: frozen AT07 + AT11 February exact-tick replication. No January retuning; no April/May–July access; August remains sealed.

Full local artifact hashes: script ca00ad43ea37146a2e8dfffb421ff8bd3be89e5083b935b07a00358c4e99569f; result ba6cb2a9971b3ff65f56d01f9e6efa1f4780d1ba272c26ac373239c7f0901a49; manifest b0ce274a3905e95358c9f1965a122c1a363ae1cf99eda7650bbd68d05daebe72; audit NPZ bb94df704313aba6779a368fd298c801513813cd0ed78338cdeafb4149f51d55. Full artifact Library transfer hit a container-session bridge failure after computation; only the research note upload succeeded. The compact GitHub summary is authoritative for this stage until full artifact mirroring is retried.
