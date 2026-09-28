# R9B Gamma Session Governance Bootstrap

## Purpose
Every new ordinary-Chat research session must materialize the live governing documents into local runtime files before any science begins. This prevents chat memory, stale handoff pointers, or delivery failures from silently changing project rules.

## Fixed governing sources
- Master Protocol Google Doc ID: `1ycB5bQ3P24w7BZz54RwgJbc5CX5aRcqgr0KiI0Iidkw`
- CURRENT Governing Handoff Google Doc ID: `1N5DRgTrg8JNo5t7tO1iA-Va0pAGFww8JV5S1ANRPmdQ`
- Live state: `AnhTranHarris/research_lab_xauusd` / `main` / `CURRENT_STATE.json`

## Hard startup gate
Before research/coding/backtesting:
1. Read both live Google Docs and record Drive revision IDs.
2. Raw-download/export both as DOCX so they are real files in `/mnt/data`.
3. Canonicalize them to:
   - `/mnt/data/r9b_governance/MASTER_PROTOCOL_CURRENT.docx`
   - `/mnt/data/r9b_governance/CURRENT_HANDOFF_CURRENT.docx`
4. Fetch and persist live `CURRENT_STATE.json` as:
   - `/mnt/data/r9b_governance/CURRENT_STATE.json`
5. Create:
   - `/mnt/data/r9b_governance/SESSION_GOVERNANCE_LOCK.json`
6. The lock records document IDs, revisions, local paths, SHA-256 hashes, GitHub state identity, bootstrap time, authority order, execution mode, and sealed-data state.
7. Verify files + hashes, then use the local snapshots as the working session control plane.

## Authority
Platform/system/developer rules remain higher authority. Within the project:
1. current explicit user direction,
2. Master Protocol methodology/execution rules,
3. GitHub CURRENT_STATE for the live science pointer/latest durable artifacts,
4. CURRENT Governing Handoff for restart/bootstrap/reconciliation,
5. historical handoffs as provenance only unless explicitly referenced.

## Runtime reset
If local governance files disappear, bootstrap again before further science.

## Governance changes during a session
If the user or assistant changes a governing document, remount the affected file and regenerate the lock before continuing research.

## Execution
Use Master Protocol Sections 107–108. Ordinary Chat checkpoint batching is the default. Do not use Work unless the user explicitly authorizes it. August remains sealed unless explicitly authorized.
