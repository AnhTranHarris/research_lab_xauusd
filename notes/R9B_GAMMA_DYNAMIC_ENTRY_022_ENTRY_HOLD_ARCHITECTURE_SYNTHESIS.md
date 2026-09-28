# R9B Gamma Dynamic ENTRY 022 — Entry/Hold Architecture Synthesis

**Status:** VERIFIED_DURABLE diagnostic. Entry/hold is not yet ready to freeze for exit research.

The ENTRY017→021 state chain is working well once a second-wave trade has a correct +1s ignition. Frozen Jan-heldout/Feb/Mar recall of +5s winners conditional on +1s correctness is 94.06% / 91.02% / 90.68%. Persist-state +5s accuracy is 77.74% / 72.24% / 76.43%. ENTRY021's terminal FAILED_IGNITION_CANDIDATE is only 8.11% / 14.06% / 7.61% positive at +5s.

The blocking gap is earlier: 46.59% / 53.12% / 56.08% of all +5s winners are non-positive at +1s. They are late ignitions and never reach the persistence owners. Therefore starting economic exit optimization now would optimize only the already-correct subset and leave roughly half of later winners structurally unreachable.

Next research unit is **ENTRY023 LATE_IGNITION_OWNER**: among ENTRY017 selections that are non-positive at +1s, identify a causal observable state that recovers later +5s winners without simply holding every failed ignition. No existing exit/lifecycle logic is changed.

Durable Drive source/result/manifest IDs and SHA256 are recorded in CURRENT_STATE and the Google Docs Build Capsule. August remains sealed.
