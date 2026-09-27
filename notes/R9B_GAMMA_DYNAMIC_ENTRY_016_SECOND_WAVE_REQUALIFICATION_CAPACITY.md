# R9B Gamma Dynamic ENTRY 016 — Second-Wave Requalification Capacity

**Status:** VERIFIED_DURABLE diagnostic; direct R9 SYNTH re-entry transplantation rejected.  
**Parent:** GL001 / causal Gamma014.  
**Scope:** January discovery with January held-out + February + March replication. August not accessed.

## Question

R9 SYNTH historically showed an unusually strong second/opposite same-minute re-entry. This unit tested whether an analogous causal state already exists in Gamma and whether the existing causal feature stack can identify the correct second-wave action.

The state is defined only from information available at the new signal: the second executed Gamma trade in the same UTC minute, after the prior trade is closed, with direction opposite the prior executed direction. Previous realized P/L, previous hold time and time since close are observable and may be features. Future FADE/CONTINUE outcomes are teacher labels only.

## Result

The naive state is still negative in every tested month:

- January: 2,722 trades, 70.13% wins, -$347.60 net, -$1,110.13 GL.
- February: 3,101 trades, 68.33% wins, -$375.17 net, -$1,461.91 GL.
- March: 4,225 trades, 68.21% wins, -$759.36 net, -$1,952.74 GL.

Yet the teacher-only best-action capacity is extreme: about 96.3–97.0% of these events have a profitable FADE or CONTINUE path under the current lifecycle, and roughly 47–48% require the opposite action from the parent owner. Oracle net is +$1,287.05 / +$1,809.90 / +$1,981.31 for Jan/Feb/Mar respectively. This is capacity evidence only and cannot be used in execution.

A 180-cell transparent shallow-tree screen using current causal Gamma features, ENTRY009 pre-entry sequence features, parent confidence/action, previous realized trade outcome/hold, and close-to-signal gap produced **zero** robust candidates that were positive and improved net/GL across January-heldout, February and March.

## Interpretation

The R9 SYNTH effect is not “take the second opposite trade.” The useful information is in the **requalification transition between the prior close and the new signal**, and the current feature stack is aligned mainly to the new event rather than that transition anchor.

Therefore do not loosen rearm rules or promote a generic second-wave rule. The next bounded unit is **R9B_GAMMA_DYNAMIC_ENTRY_017_POST_EXIT_REQUALIFICATION_BRIDGE**: reconstruct exact-tick, post-close-to-new-signal features including displacement, efficiency, boundary recross/reclaim, renewal counts/ages, reversal density, and fresh acceptance durability. Then retest action ownership with January-only training and held-out replication. Only a self-consistent chronological integrated state machine can be considered for promotion.

No formal Gamma number is consumed. No MT5 build is authorized. August remains sealed.
