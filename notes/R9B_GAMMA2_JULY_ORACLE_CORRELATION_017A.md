# R9B_GAMMA2_JULY_ORACLE_CORRELATION_017A

Status: VERIFIED_DURABLE_FORENSIC. This is a July diagnostic sidecar; it does not replace or promote a Gamma build.

## Why July is failing

The R9 teacher/oracle and 017 exact-tick event population show that July is not primarily a broad-regime-mix problem. TRANSITION / ROTATION / EXPANSION shares remain broadly similar to Jan-Jun. What changes is the quality inside every regime.

### 1. Opportunity viability collapses
Jan-Jun teacher "neither FADE nor CONTINUE profitable" share is 8.12%. July rises to 15.04% — an 85% relative increase.

Daily 017 success has Pearson -0.897 / Spearman -0.876 correlation with the day's teacher-neither share. This is the strongest July correlation in the current forensic screen.

A separate pre-entry binary viability classifier performs poorly on July:
- shallow transparent tree AUC 0.538
- logistic AUC 0.522
So the toxic population cannot be reliably removed with another static pre-entry filter.

### 2. July becomes less forgiving about direction
Both FADE and CONTINUE are profitable on 44.27% of Jan-Jun teacher events, but only 33.05% in July.
One-side-only profitable events rise from 47.60% to 51.91%.

017 wrong-owner losses rise from 20.31% of acted events Jan-Jun to 23.84% in July.
Toxic executions rise from 7.58% to 13.95%.

Thus July needs more precise ownership, not merely a lower trade count.

### 3. State half-life collapses
Average regime age falls from 95.46s Jan-Jun to 48.81s in July (-48.9%), while mean classification confidence actually rises slightly from 0.518 to 0.540.

This means regime confidence is not the same as state durability. July often produces a confidently classified state that does not persist long enough to monetize.

### 4. Excursion/monetization capacity compresses
Teacher-best mean payoff falls from about $0.291 to $0.159 (-45.5%).
Median falls from about $0.187 to $0.105 (-43.7%).
ATR excess falls about 50.9%.
10s displacement and range fall about 33%.
5s and 30s directional returns fall about 32-34%.

This is the native-R9 version of the same signature already seen in formal Gamma_2 July: winning conversion falls and average winner compresses.

### 5. Broad regime label is not enough
Teacher-neither rate approximately doubles within each regime:
- TRANSITION 7.93% -> 14.68%
- ROTATION 8.71% -> 17.25%
- EXPANSION 7.77% -> 13.35%

017 selected-action positive rate falls in every regime:
- TRANSITION 71.74% -> 61.05%
- ROTATION 80.86% -> 67.23%
- EXPANSION 70.79% -> 62.38%

Therefore July is a cross-regime deterioration in tradeability, not a single bad regime.

## Failure-class comparison

Correct 017 winners and wrong-owner losers have very similar pre-entry ATR ratio, ATR excess, displacement, efficiency, range, persistence and activity. Likewise, abstained-profitable events look very similar to abstained-toxic events.

That is the key reason another static feature gate is unlikely to solve July.

Current July event counts:
- 4,702 wrong-owner losses
- 2,752 toxic executions
- 9,321 abstained but teacher-profitable events

The teacher-only independent salvage pool is large enough to matter:
- wrong-owner opposite-side capacity +$808.73 versus -$3,906.61 on the chosen side
- abstained-profitable oracle capacity +$1,647.29
- total positive oracle-best capacity +$5,113.58
These are capacity numbers, not executable PnL.

## Exact-tick proof diagnostic for 018

A causal first-move diagnostic was run after each July signal.

If price first displaces $0.30 in one direction within 5 seconds:
- 58.68% of all events produce a proof
- selected direction is profitable 79.39% of the time under the teacher replay
- median proof time 1.804s
- 45.75% of current 017 abstains receive a proof
- across all abstains receiving proof, selected direction is positive 78.95%
- among abstained events that the oracle knows are profitable, 48.89% receive proof and the selected side is profitable 88.96%

A $0.30 / 10s proof increases abstain coverage to 69.72% but reduces selected-positive rate to 75.67%.

Important: these are selection correlations only. 018 must enter at the actual proof tick and replay from there. It is invalid to observe the proof and then credit signal-time PnL.

A crude mandatory retest/re-break sequence underperformed the fast first-touch diagnostic. Therefore retest/re-break should be conditional after first-touch, not a universal requirement.

## Quant/day-trader interpretation

July behaves like a market with:
1. shorter-lived setups;
2. lower excursion amplitude;
3. more one-sided rather than two-sided profitable opportunities;
4. more genuinely dead/toxic events;
5. similar headline regime labels but lower within-regime tradeability.

That implies a desk-style separation:
- classification confidence: what state is this?
- tradeability confidence: is there enough live auction energy to trade?
- ownership proof: which side is actually gaining acceptance?
- lifecycle owner: harvest, medium, runner, or fail containment.

The present system partially conflates the first two.

## 018 changes

R9B_GAMMA2_CONFIDENCE_PROOF_HANDOFF_018 should now:
1. add a separate tradeability/viability score;
2. add regime durability/age;
3. treat low-energy and young-regime states as proof-required, not automatically rejected;
4. test exact-tick OCO first-touch acceptance at about $0.30 / 5s and $0.30 / 10s first;
5. replay entry only at proof time;
6. use retest/re-break only when first-touch state is ambiguous/noisy;
7. expire unresolved events;
8. hand rejected events to complementary specialists rather than flip automatically;
9. keep news as execution-cost/spread/slippage context, not the directional owner.

## Community cross-check

MQL5 Market Microstructure Part 7 explicitly separates Stressed, Noisy, Trending and Mean-Reverting conditions and distinguishes regime classification from directional signal; Part 8 adapts downstream signal thresholds according to state confidence. Directional-change research in FX supports event/intrinsic-time confirmation rather than fixed wall-clock sampling, while semi-Markov research supports duration-dependent state transitions. These ideas support the 018 proof architecture, but the July Dukascopy evidence above is the actual project evidence.

August remains sealed.
