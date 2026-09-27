# R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_B_ACCEPTANCE_SWEEP

Status: **VERIFIED_DURABLE_DIAGNOSTIC_REJECTED**. Not promoted.

## Purpose

Second bounded stage of 020. The 020-A hierarchical structural owner is frozen. This stage adds only reconstructible, causal completed-bar acceptance/sweep state around that owner:

- wick penetration versus accepted close beyond a confirmed swing boundary;
- reclaim and failed acceptance;
- first versus repeated penetration;
- touch count and level age;
- ATR-normalized penetration and reclaim depth;
- owner-relative acceptance quality;
- recent cross-scale acceptance/sweep/failure counts.

No delayed post-signal confirmation is required and no future MFE/MAE enters execution.

## Source equivalence and chronology

The missing 020-A cache layer was rebuilt from the bound source semantics. January reproduced the certified V2 source-equivalence target exactly: **33,793 trades / -$6,253.808 net**.

Discovery: Jan-Mar. April: calibration only. May-Jun: strict forward. July: stress validation. August: sealed and not accessed.

The transparent model architecture from 020-A remained fixed: CART depth 4, minimum leaf 800, abstain class weight 1.5, random state 17. April selected only the acceptance-state representation and confidence threshold. The selected representation was **OWNER_SUMMARY**, threshold **0.45**.

## Result

The acceptance/sweep layer improved the forward period without meaningful density loss:

- May-Jun: **+$300.48 net improvement**, **$391.22 less gross loss**, **+242 winners**, +0.349pp success, +16 trades.
- July: **+$120.98 net improvement**, **$167.94 less gross loss**, **+120 winners**, +0.400pp success, -5 trades.
- May-Jul combined: **+$421.47 net improvement**, **$559.17 less gross loss**, **+362 winners**, essentially unchanged trade count.

However, Jan-Mar degraded enough that full Jan-Jul economics did not improve:

- 020-A Jan-Jul: 234,740 trades / 165,215 winners / 70.382% / -$42,586.87 net / -$84,552.45 GL.
- 020-B Jan-Jul: **234,294 trades / 165,614 winners / 70.686% / -$42,939.86 net / -$84,453.71 GL**.
- Jan-Jul: **+$98.74 GL improvement and +399 winners, but net worsens by $352.99**.

Therefore this is not an integrated-system breakthrough and is not promoted.

## Diagnostic value

Acceptance/sweep state is not noise. Important selected variables include owner penetration depth, structural level age, owner acceptance quality, failed-acceptance depth, opposite-direction acceptance count, same-direction sweep count, and recent penetration count. The forward improvement in both May-Jun and July supports preserving these descriptors for later pattern-transition/phase routing.

The failure is that one static action tree cannot apply the same acceptance-state interpretation across the early and late regimes. This supports the next planned step: transition-state recognition rather than additional static filtering.

## Decision

**REJECT 020-B as standalone authority.**

Preserve:
- frozen 020-A structural owner as context;
- 020-B acceptance/sweep memory as context;
- source-equivalent compact caches and hashes.

Do not promote, do not change the formal Gamma_2 build, and do not open August.

## Next bounded unit

**R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_C_ORDINAL_TRANSITION**

Add ordinal-pattern transition state only, conditioned on frozen structural ownership and preserved acceptance/sweep context. Keep Jan-Mar discovery, April calibration, May-Jun strict forward, July stress validation, and August sealed. Score gross loss first, winner retention/success second, net third.

## Reproducibility

Production source commits:
- source-equivalent 020-A core: `5c8e7992d53692d329278ce9eaeb999148e44a39`
- acceptance/sweep feature builder: `39f399a587790d885f1ed4baca2c77ed250c0975`
- evaluator: `425c1c046e0922a2edb4c09e76a578ae3ec7ab1`
- result: `ae65ab08c76de532c257742a9ef3b64c7aaa84f5`

Local execution SHA-256:
- core: `7a37b2d4fbba73b83346fe835a21c13a37ae57d4a9065ac921143e135d4c5086`
- feature builder: `656e3a4163231bb8fca0fc38669330f472a2a0b8edd4f3b48012192f7e13e833`
- evaluator: `705e9ad4f852ac1cf35990d7573021fdcf5de139336630d7f28a7fa2f8af5d92`
- full local result: `877920213aed0624b60542debda8e7d12fc571d28490601f9eae40d9db817a57`

August accessed: **false**.
