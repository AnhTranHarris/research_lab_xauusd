# R9B Gamma Dynamic ENTRY 017 — Post-Exit Requalification Bridge

**Status:** VERIFIED_DURABLE diagnostic subclass frontier; no formal promotion.

This unit isolates two quantities before any hold/exit change: **entry accuracy** = positive executable P/L at +1s under the fixed reference spread; **directional hold accuracy** = among +1s-positive selections, remaining executable-positive in the same direction at +5s.

The balanced **bridge-only** profile uses exact-tick information observed strictly between the prior trade close and the new candidate signal, plus prior realized trade state. It was selected only inside January-first14 via an inner chronological split and then frozen.

Frozen replication:
- Jan heldout: coverage 59.32%; entry accuracy 30.75% vs parent 29.71% (+1.04 pp); +5s conditional hold 67.18% vs 67.61% (-0.43 pp).
- Feb: coverage 54.11%; entry accuracy 30.45% vs 25.93% (+4.53 pp); hold 63.21% vs 61.82% (+1.39 pp).
- Mar: coverage 53.40%; entry accuracy 27.39% vs 23.74% (+3.65 pp); hold 64.24% vs 64.81% (-0.57 pp).

A combined bridge+old-event profile improved entry accuracy more (+3.40/+5.42/+5.43 pp) but reduced coverage to 35–43% and degraded March hold persistence by 2.33 pp. It is not the preferred frontier.

**Conclusion:** requalification-bridge state is real causal entry information, but entry selection and persistence ownership remain distinct. Retain the bridge-only profile as the balanced research frontier. Do not alter exits yet.

**Next:** R9B_GAMMA_DYNAMIC_ENTRY_018_BRIDGE_PERSISTENCE_OWNER — freeze the ENTRY017 bridge entry profile and model only whether a correctly ignited second-wave direction deserves continued directional ownership through +2/+3/+5s. This is an accuracy diagnostic first, not an exit rule.

Source/result hashes: source 3395da77cb1b95a96e66caf42d68c16f763097df701270c94aa990603ec3565a; result 2f44ac5cecb0f4d02b9d3a191142ad8e66de369ce17623fafb0a7b2cc95b13f7. August sealed.

## Frozen action-owner artifact
The carried-forward ENTRY017 action owner is now explicitly frozen for later MT5 parity as `models/R9B_GAMMA_DYNAMIC_ENTRY_017_ENTRY_MODEL.json`. The exact 17-node tree, class probabilities, confidence threshold, feature contract, and January training boundary are preserved. Drive model ID `1rqKJiDD1sHVv4u-yKJLfr57IuYLa6-RZ`; freeze-helper ID `102DWpFZqoonlE5b0LR52IivbFLm7KjXh`; model SHA-256 `57e1a27941b7aefba27bcc5eb35bfd7e8aa1a3e72df6e658a4048e806003e50a`. Future descendants must use this frozen identity or explicitly recertify a replacement.
