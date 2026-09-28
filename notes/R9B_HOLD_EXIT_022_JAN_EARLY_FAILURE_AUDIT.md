# HOLD_EXIT_022 — January early-failure screen and structural entry/hold source audit

**Classification:** VERIFIED_DURABLE_DISCOVERY_DIAGNOSTIC upon checkpoint sync; NO promotion, NO active exit change.
**Parent:** CAUSAL_RECERT_014, strict first-eligible one-position exact tick chronology, 0.01-lot-style price PnL with modeled $0.10 halfspread on each side (not live Coinexx bid/ask).
**Time split:** January discovery only. February–March not accessed by this unit, April and May–July not accessed, August SEALED.

## Golden and source integrity
* January canonical market gzip SHA validated against NET024 January raw manifest; 9,135,062 raw ticks.
* Verified event cache 34,362 raw CAUSAL014 candidates. January chronological control EXACT: 28,088 trades / 19,087 winners / net -$4,510.0870000 / GP $7,001.464 / GL -$11,511.551 / PF 0.608212 / month DD $4,554.886.
* Entry and postentry observations anchored to the first real quote at or after +1s, +2s, +4s; checkpoint eligible only if strictly earlier than the original trade exit; endpoint cash at same-tick does not override original exit. Observed MFE, MAE, PnL use only ticks through checkpoint.
* All raw event exit timestamps and PnL re-evaluated BEFORE one-position portfolio selection. Modifying exit timing can free the account and allow different subsequent signals; this was explicitly reselected.
* Original optional R9B_FAST_CACHE/m01.npz is invalid ZIP and was **not** used; incident logged in R9 Error Ledger. Fresh source-golden run read immutable January gzip and wrote a new independently zip-validated compressed causal cache.

## Ex-post result of 18 predeclared early containment variants
* Preconditions were frozen and stored before the heavy run: first actual tick after +1/+2/+4s, current PnL <= {-0.25,-0.50,-0.75}, peak-observed net favorable excursion <= {+0.05,+0.20}. Any triggered event closes at that actual tick; otherwise unchanged parent lifecycle.
* **All 18 variants worsen January net and PF** compared with unchanged CAUSAL014. Thus universal early loss cutting on current negative PnL + low MFE fails the January discovery screen and is REJECTED for this parent. Do not repeat unchanged family across forward months.
* Most generous GL reduction came at +1s / PnL <= -$0.25 / net-MFE <= $0.20: GL compressed ~$885.72 but gross profit fell ~$1,537.33, the selected portfolio contained 4,139 fewer winning trades (78.32% count retention), net worsened ~$651.60, PF fell from 0.6082 to 0.5142. This is a net count difference after chronological reselection, not a one-for-one set of baseline winners directly closed early.
* The least net-damaging variant (+2s / PnL <= -$0.75 / net-MFE <= $0.05) still worsened net by ~$53.05 and PF by ~0.0075, despite ~$83.94 less GL. Winner retention ~98.57%.

## Mechanistic diagnosis: slow-ignition recovery is a major confound
* January parent trades surviving to +1s: 23,780; +2s: 20,776; +4s: 16,950.
* At +1s, 20,385 surviving executed parent trades were currently negative and had realized no net favorable excursion > $0.05 so far, **yet 63.2% later finished as parent winners**; at +2s, the comparable 17,371 cohort had 60.4% eventual winners; at +4s, the 13,750 cohort had 56.5%. These are EX POST labels, not decision variables.
* Causal two-checkpoint price deterioration without observed net MFE distinguishes different structures but is not enough alone: between +1 and +2s, `weak_align` had 4,735 such cases with 60.5% eventual winners, and `strong_align` had 4,147 with 51.9% eventual winners.
* These numbers directly explain why standalone universal early exits clip a large legitimate recovery-winner population. Counterfactual early close reduces loss on some losers but often also preempts a future winner, and new freed entries cannot offset the damage in the tested January rules.

## Design implications — next hold/exit subunit
1. Keep ENTRY017-024 frozen **as diagnostic semantics**, not automatically ported code to the CAUSAL014 population; ENTRY017/021/023 dedicated source-body closure remains conditional before MQL5 claims.
2. Stop generic fixed-horizon negative PnL+low-MFE exits. Shift to **causal path invalidation** (observed acceptance/reclaim failure or structural owner conflict), not mere temporary adverse excursion; compare weak/strong structure and slow-vs-fast persistence.
3. Develop an independent **HARVEST/MEDIUM/RUNNER** branch that can bank strong winners without sacrificing recovery; assess opportunity and gross-profit effects in whole raw chronological portfolio, not on fixed selected trades.
4. Test any new mechanism first on January–March discovery with predeclared observables, and only later April calibration and May–July frozen forward. August remains SEALED.
5. No promotion/MT5 build until an integrated, source-closed model improves total-system economics and passes relevant robustness.

## Durable provenance
* Script: `scripts/r9b_hold_exit_022_postentry_early_failure.py`, GitHub commit `c83252d9b206e9425e851becf231e2c0cd41dc66`.
* Predeclared contract: `results/R9B_HOLD_EXIT_022_JAN_PREDECLARED_CONTRACT.json`, commit `0c559f1b62fe10e769684a41f954b681d81868b8`.
* Results: `results/R9B_HOLD_EXIT_022_JAN_INITIAL_SCREEN.json`, commit `496ac5a37ffe1b5ac710b02ebf98849db80f0c77`.
* Result manifest: `results/R9B_HOLD_EXIT_022_JAN_INITIAL_SCREEN_MANIFEST.json`, commit `46f38090a3514f928196aaceb0588ca0680b89ce`.
* Full causal observation arrays `.npz` and run log are stored in persistent private Library `/R9_Gamma_Checkpoints/HOLD_EXIT_022/`.
* Source supplementary analysis: `scripts/r9b_hold_exit_022_cohort_diagnostics.py` and `results/R9B_HOLD_EXIT_022_JAN_CAUSAL_COHORT_DIAGNOSTIC.json`.
