# R9B Gamma Dynamic ENTRY 018 — Bridge Persistence Owner

**Status:** VERIFIED_DURABLE diagnostic subclass frontier; not a formal Gamma promotion and not an exit rule.

## Purpose and causal boundary
ENTRY017 is frozen. ENTRY018 asks only whether a second-wave entry that is already executable-positive at +1 second should still own its original direction through +2/+3/+5 seconds. The decision is evaluated at +1s. Every input feature is constructed exclusively from ticks at or before +1s. Future +5s outcome is a training label only.

## Exact first-second feature surface
The durable cache computes 24 causal features in selected-action coordinates: returns at 250/500/750/1000ms; first-second MFE/MAE; total travel and directional efficiency; fraction favorable and fraction above executable breakeven; turn count; favorable/adverse extreme-renewal counts and ages; tick count/intensity; age since first executable breakeven; zero/breakeven recross counts; giveback from first-second MFE; recovery from first-second MAE; second-half acceleration; and +1s executable PnL.

The retained transparent profile uses eight fields: +1s executable PnL, first-second efficiency, breakeven occupancy, turn count, breakeven recross count, second-half acceleration, first-second MFE and first-second MAE. Model: sklearn DecisionTreeClassifier, max_depth=1, min_samples_leaf=20, class_weight={0:3.0,1:1.0}, random_state=118, hold probability threshold 0.40.

## Discovery/freeze contract
ENTRY017 action ownership is fixed. January days 0–6 fit candidate persistence owners; days 7–13 select under predeclared ignition-coverage floors. The chosen >=50% coverage profile is refit on January days 0–13 and frozen. January heldout, February and March are replication only.

## Frozen replication
Jan heldout: 326 correct +1s ignitions; HOLD=185 (56.75% coverage). +5s persistence accuracy rises 67.18% → 75.14% (+7.96 pp). Persistent-runner recall 63.47%.

February: 511 ignitions; HOLD=296 (57.93%). +5s persistence 63.21% → 68.58% (+5.37 pp). Runner recall 62.85%.

March: 618 ignitions; HOLD=302 (48.87%). +5s persistence 64.24% → 72.85% (+8.61 pp). Runner recall 55.42%.

Minimum replicated improvement is +6.32 pp at +2s, +6.56 pp at +3s and +5.37 pp at +5s.

## Interpretation and boundary
The first second after a correct ignition contains real causal persistence information. The improvement is meaningful for the isolated directional-hold subclass, but it is not yet sufficient to change exits because the owner discards roughly half of correct ignitions and 37–45% of persistent runners. This is a research frontier, not a whole-system performance claim.

## Later MT5 reconstruction capsule
At eventual MQL5 translation, the entry owner and persistence owner must be separate state machines. OnTick must accumulate the exact first-second selected-direction path fields after an ENTRY017-qualified fill. At event_time+1000ms, compute the eight retained features, traverse the frozen depth-1 tree and emit HOLD_PERSIST or HARVEST_CANDIDATE. This diagnostic must not itself close a position until a later lifecycle experiment proves economic value. Log all 24 first-second fields, tree leaf, hold probability, decision, +2/+3/+5 diagnostic outcomes, and original ENTRY017 identifiers for Python parity.

## Next unit
R9B_GAMMA_DYNAMIC_ENTRY_019_MULTI_HORIZON_PERSISTENCE_STATE: determine whether one causal state can distinguish short persistence (2s), medium persistence (3s) and genuine runner persistence (5s+) without destroying runner recall. August remains sealed.

Source SHA256: post1 cache c4950ff4e02cd04ba27e3863187f7f2bc550f34c36ee01845653adec0da7afc5; screen 8be506297a9c9c4803ce854abc2275f2fe77de6a47159b31325509f07ae4cd2c. Result SHA256: 7d2d6fc4a89877ef713de732b98ac319bcbdc4c8453445b8d22a8b0a9bb18b6.
