# R9B Gamma Dynamic ENTRY 021 — Recovery Trajectory Owner

**Status:** VERIFIED_DURABLE diagnostic subclass breakthrough candidate; no formal Gamma promotion and no executable exit change.

Inside ENTRY020 RECOVERY_UNCERTAIN, January-only discovery selected a +4.5s delayed-runner rule. The fitted depth-1 tree collapses to one deterministic condition: if the worst executable selected-direction excursion observed from +4.0s through +4.5s is greater than -$0.24, classify DELAYED_RUNNER; otherwise classify FAILED_IGNITION_CANDIDATE. The +5s outcome is teacher/diagnostic only.

Frozen Jan-heldout / Feb / Mar selected +5s accuracy is 73.68% / 78.13% / 64.52% versus uncertified baselines 30.91% / 35.11% / 30.41%, an uplift of +42.78 / +43.02 / +34.11 pp. Runner recall is 82.35% / 75.76% / 88.89% at 34–42% coverage.

MT5 mapping: preserve the ENTRY017 -> ENTRY018 -> ENTRY019 -> ENTRY020 state lineage. Only when still RECOVERY_UNCERTAIN at +4s, keep an observed-only local MAE accumulator from +4.0s. At the first tick >= +4.5s, compare local executable MAE to -$0.24 and emit DELAYED_RUNNER or FAILED_IGNITION_CANDIDATE. Do not alter the existing exit/lifecycle yet.

Durable Drive source/result/model/manifest IDs are recorded in CURRENT_STATE and the Google Docs Entry/Hold build capsule. Source/result/model SHA256: 0b87ad40f72c51f1ed0cea72f24f340691cb127b9b31fb47d6cbbc7abbc6ffca / f79c4aa185b3e5708cc4cd60fdc07f08d4f1084025e9806a971eea00c6da7fa3 / f28c7726fedbe1aa44553c38923a8d48271fcab293363f2307b049f863623111.

Next: R9B_GAMMA_DYNAMIC_ENTRY_022_ENTRY_HOLD_ARCHITECTURE_SYNTHESIS. August remains sealed.
