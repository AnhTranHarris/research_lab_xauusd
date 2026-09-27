# R9B_GAMMA_DYNAMIC_GL_008 — targeted regime-owner veto freeze

Status: VERIFIED_DURABLE_CALIBRATION_READY_FORWARD.

Parent: GL004 extreme-veto shadow on top of GL001 frozen January ownership.

Mechanism: a January-trained per-regime action classifier is consulted only for GL004-retained FADE events whose fade-alignment state is exactly 2. If the classifier is sufficiently confident and its action disagrees with FADE, the event is vetoed. It cannot create a trade or flip ownership. This is a targeted owner-disagreement veto, not generic abstention.

Frozen contract:
- train: January first 14 trading days only;
- depth 4;
- minimum leaf 75;
- class weight {ABSTAIN:1.5, FADE:1, CONTINUE:1};
- confidence threshold 0.45;
- target = GL004-retained FADE with alignment exactly 2;
- mode = DISAGREE_VETO;
- router model SHA256 2b8dff99aabde5a5196440e65306d599722869fe920e0299ce46c9c76d1a2d0f.

Discovery/calibration:
- January heldout: +2.5875% incremental GL reduction vs GL004, 97.4251% winner retention, +$29.3995 net.
- February frozen replication: +3.3706% GL, 97.0739% winners, +$103.4415 net.
- March frozen replication: +3.0858% GL, 97.3473% winners, +$192.4500 net.
- April calibration: +2.1161% GL, 97.8855% winners, +$62.1335 net.

All four stages improve GL and net with >=97% winner retention. Freeze unchanged for May-Jul. No May-Jul tuning. August sealed.

Durable Library root: /R9_Rebuild/R9B_GAMMA_DYNAMIC_GL_008/
