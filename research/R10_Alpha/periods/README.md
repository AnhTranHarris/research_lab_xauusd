# R10 Alpha period partitioning (workspace only)

All **seven months January–July 2026** will receive independent research and reporting records, plus an aggregate Jan–Jul report. No performance or trade results are asserted here.

For each calendar month `YYYY-MM`:

- `daily/` — one chronologically bounded report/ledger per date, with tick-source provenance, bid/ask costs, positions, and failures.
- `weekly/` — week-granularity aggregation of the source daily ledgers, without double-counting month-crossing days.
- `monthly/` — full-month reconciliation and result against original R9 REAL and the frozen Alpha parent.

Suggested future artifact naming convention:
`research/R10_Alpha/periods/YYYY-MM/daily/YYYY-MM-DD_*.json`;
`.../weekly/<WEEK_ID>_*.json`;
`.../monthly/YYYY-MM_*.json`.

The Google Drive `02_RESEARCH_BY_MONTH` folder already contains January–July monthly folders, each with `DAILY`, `WEEKLY`, and `MONTHLY_SUMMARY` destinations.

**Awaiting user clarification:** time-zone/accounting-day boundary; definition of the trading week (calendar, broker server, UTC/ISO, or Australia-open through NY-close); distinction between exploration months and frozen forward validation. Never silently assume a holdout remains untouched once it is used for optimization.

**August:** SEALED. No August research or fitting is authorized.
