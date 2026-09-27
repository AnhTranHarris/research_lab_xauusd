# Gamma Dynamic GL 007 — Failed-ignition quarantine forward closure

Status: VERIFIED_DURABLE_REJECTED_AS_CORE. August sealed.

Mechanism: after GL004 ownership/extreme-veto selection, a January-trained loss classifier observes exactly 2 seconds of live path. When loss probability >=0.65 it closes at the observed 2s tick and applies a fixed 25s rearm quarantine. The quarantine is causal and never uses the original future exit time.

Discovery/calibration:
Jan: +3.1878% incremental GL reduction vs GL004, 97.0373% winner retention, +$64.684 net.
Feb: +2.2756% GL, 97.3772% winners, +$10.567 net.
Mar: +2.9690% GL, 97.1364% winners, +$137.6965 net.
Apr: +1.5184% GL, 98.3932% winners, +$40.670 net.

Frozen forward:
May: +1.0934% GL, 98.9241% winners, +$38.635 net.
June: +0.6697% GL, 98.3906% winners, -$29.8805 net.
July: +0.6586% GL, 98.9343% winners, -$0.471 net.

May-Jul aggregate:
GL004: 64,973 trades / 44,412 winners / -$11,942.4000 net / -$24,735.0500 GL.
GL007: 64,874 / 43,849 / -$11,934.1165 / -$24,535.7840 GL.
Incremental: 0.8056% GL reduction, 98.7323% winner retention, 99.8476% trade retention, +$8.2835 net.
Versus Gamma014: 18.6373% GL reduction, 82.7589% winner retention, +$3,179.376 net.

Decision: reject GL007 as an integrated core layer. Quarantine fixes the gross-loss direction and avoids the severe replacement-event failure of generic early exits, but forward incremental economics collapse to effectively zero and June/July net do not improve. Preserve the architectural lesson: any early-failure exit requires explicit rearm ownership/quarantine, but do not carry this particular classifier.

Next: return to the historically higher-impact 017 action-ownership mechanism. Test a targeted per-regime owner override/veto only on the residual high-loss low-alignment FADE population retained by GL004, rather than another exit-layer tweak.
