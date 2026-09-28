# R10 Alpha — research workspace

**Status:** infrastructure initialized; awaiting further user direction. No Alpha strategy, backtest, MQL5 build, or broker order has been executed or authorized by this scaffold.

**Scope:** XAUUSD, **2026-01-01 through 2026-07-31**, research and reporting at daily, weekly, monthly, and consolidated Jan–Jul levels. August 2026 remains **SEALED**.

**Scientific hierarchy:** original R9 REAL MT5 is the real-tick execution baseline; R9 SYNTH is an aspirational generated-tick benchmark; R9 OVERFIT is a noncausal diagnostic reference only; Dukascopy original raw ticks are independent market evidence. Do not mix source roles, historical Γ results, or future oracle labels into execution inputs.

**Lineage:** `alpha` branch only; Gamma and `main` remain untouched. A separately versioned Alpha `CURRENT_STATE.json` is authoritative for Alpha's restart point.

**Source of rules:** [Alpha handoff](https://docs.google.com/document/d/14ElgUCCXZeu7y4go9RAR5-v06rU_yOPqskQCCsqPRA4/edit) and [Master research protocol](https://docs.google.com/document/d/1ycB5bQ3P24w7BZz54RwgJbc5CX5aRcqgr0KiI0Iidkw/edit), Sections 109–111, subject to the latest user instructions.

**Drive working folder:** [R10_ALPHA_2026_JAN_JUL](https://drive.google.com/drive/folders/1QoEK99ax1fIGZ-fGc-OwWsBcnjiTmhPA). Original source archives stay at their current locations; do not bulk duplicate large tick files.

**Research organization:** `research/R10_Alpha/` for experimental records, `scripts/r10_alpha_*.py` for future runnable implementations, `results/R10_Alpha_*` for future deterministic artifacts, and `R10_Alpha_<order>_<mechanism>_WHITEPAPER.md` only for a validated reproducible improvement.

**Validation boundary:** expanding the January–July reporting period does not make previously inspected months blind/out-of-sample. A frozen validation plan and timestamp convention must be recorded before any performance claim.
