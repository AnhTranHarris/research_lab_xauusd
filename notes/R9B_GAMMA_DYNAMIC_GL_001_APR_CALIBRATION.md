# R9B_GAMMA_DYNAMIC_GL_001 — April pooled calibration checkpoint

Status: VERIFIED_DURABLE_CALIBRATION_DIAGNOSTIC. Not promoted. August sealed.

Combined Jan-Mar ownership discovery data (108,819 events) were used to train shallow action routers. April alone was used to evaluate depth/leaf/confidence neighborhoods.

April parent from this cache representation: 26,684 trades / 18,068 winners / -$4,735.95 net / -$10,883.78 GL / DD $4,744.66.

The Jan-Mar pooled retrain does NOT preserve the ~9-10% GL reduction seen when the original January-selected router was frozen into February and March. The best numeric April candidate (depth5 / leaf1200 / confidence .45) gives only 0.45% GL reduction and +$53.69 net. The robust knee (depth5 / leaf800 / confidence .45) gives only 0.33% GL reduction and +$43.12 net.

This is a diagnostic warning, not a rejection of the ownership mechanism yet. It may reflect:
1. pooled Jan-Mar retraining changes the action boundary and over-expands April participation, or
2. April represents a genuine ownership-regime shift where the January relation no longer transfers.

Next bounded diagnostic must apply the ORIGINAL JANUARY-TRAINED OWNERSHIP MODEL unchanged to April. If the frozen January model still gives material GL compression, pooled retraining is the problem. If it also collapses, the ownership mechanism is regime-dependent and should not be forwarded unchanged to May-Jul.

Do not open May-Jul for this candidate until this distinction is resolved.

Artifacts:
- April cache SHA256 1fb6b0078fcbccb03c97261bb1aa6e47025b62be4b83debb1c77e683d3ef4d89
- April cache manifest SHA256 7c7b07e0ad279f09d7acd06ec4f05f55a9f0256568140e42bbee767123993947
- April calibration result SHA256 57680d46563bf93cf2267564c3175729b6294448fee14df7649ca8f5c0df64e7
- calibration source SHA256 ce7dc8b73ef66d7a1687e10a886d1e061edea25432b0441645603b674d3fd00d
- Topic1 April source-event cache SHA256 d1c98f3791238683ae974196c80ed4d85e3b8ff9da60bde97c5a0eaf1a57f826
