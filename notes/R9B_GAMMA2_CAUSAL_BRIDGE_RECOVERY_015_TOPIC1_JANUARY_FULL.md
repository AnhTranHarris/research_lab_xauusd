# Gamma 015 Topic 1 — January Full Crosswalk

VERIFIED_DURABLE_DIAGNOSTIC. No strategy change and no promotion.

Paired R9 daily logger coverage: 21 days; Gamma 28,086 executable vs 27,977 R9 SYNTH and 31,915 R9 REAL. Gamma monthly density is 100.39% of SYNTH, but pooled ±5s Gamma↔SYNTH matches are only 5,802 (20.66% of Gamma) with 36.97% same-side; 22,284 Gamma events and 22,175 SYNTH events remain unmatched within 5s.

Pooled ±5s Gamma↔REAL: 4,716 matches (16.79% Gamma coverage), 39.72% same-side. R9 REAL↔SYNTH: 7,734 matches, 77.63% same-side. At ±250ms, R9 REAL↔SYNTH same-side is 84.55%, while Gamma↔SYNTH is 36.98%.

Non-overlap suppresses 18.26% of raw Gamma over paired coverage, insufficient to explain the population mismatch.

Weekly behavior preserves the diagnosis; W05 is the strongest divergence regime, with Gamma at 120.75% of SYNTH density while R9 REAL↔SYNTH side agreement also weakens to 70.52%.

All 21 daily files independently validate R9 server→Dukascopy UTC = -2h.

Crosswalk economics differ from the authoritative Gamma January baseline by exactly 2 trades / $1.065 because paired logger common intervals exclude two Gamma trades; full Gamma014 remains economic authority.

January decision: Topic 1 event-population/timing hypothesis is verified diagnostically; event identity/timing and action ownership are separate axes. Continue February/March discovery before Topic 2.

Full crosswalk SHA256 4b8399b66f102ee4c53f62ccf2bbbd2503527020e9ea66053f79bffd3adb266c.
Summary SHA256 361013a635c63b91a9b0f09565125e36dd1dce7c78391d59f84eab152133f039.
August sealed.
