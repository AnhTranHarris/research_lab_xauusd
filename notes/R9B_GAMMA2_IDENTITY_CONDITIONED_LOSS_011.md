# R9B_GAMMA2_IDENTITY_CONDITIONED_LOSS_011

The frozen 010 specialist router was held fixed. Separate FADE and CONTINUE loss-hazard models used causal 1s/2s/3s/5s post-entry state: current PnL, MFE, MAE, giveback, path efficiency, tick/turn state, stop room, recent movement, and the pre-entry structural/context vector. Jan-Mar fit the models, April selected separate thresholds, and May-Jul remained frozen forward.

The models did learn loss risk: train AUC rose from roughly 0.65 at 1 second to roughly 0.69-0.70 at 5 seconds. But the trading rule did not transfer.

May-Jul identity baseline: 89,925 trades / 63,898 winners / 71.057% wins / -$16,431.39 net / -$36,568.08 GL.
011: 90,381 trades / 64,010 winners / 70.822% wins / -$16,540.29 net / -$36,716.92 GL.

Jan-Jul identity baseline: 232,112 / 167,337 / 72.093% / -$41,536.80 / -$106,249.14 GL.
011: 233,945 / 167,437 / 71.571% / -$42,057.27 / -$106,662.89 GL.

Decision: REJECT as loss control. Statistical predictability of eventual failure is not enough; early close thresholds selected in April slightly worsen frozen-forward economics. This independently agrees with the 2026 MQL5 competing-risk study, whose XAUUSD hazard model calibrated well but whose fixed exit rule worsened trading economics.

Next research moves the loss-control decision earlier: liquidity source -> sweep/break -> reclaim versus acceptance -> structural shift / secondary break / retest -> HTF/LTF owner -> specialist entry -> lifecycle. This is a sequence-confirmed entry/ownership state machine, not another static filter.

Community mechanisms retained as reconstructible hypotheses:
- MQL5 competing-risk exits: time-varying MFE/MAE/volatility are informative, but exit policy must be strategy/state specific.
- Chinese MQL5 ORB: breakout -> retest -> secondary break in an OnTick state machine.
- Japanese MQL5 multi-timeframe liquidity confirmation: HTF liquidity context plus LTF execution.
- Korean MQL5 breakout logic: multi-bar continuation plus retest; failed retest invalidates the setup.
- Open-source TradingView: sweep -> state shift/CHoCH -> displacement/FVG/retest sequences; sweep alone is not a signal.
- 2026 source-code XAUUSD M15 sweep EA: swing sweep -> H1 trend -> bounded confirmation; author explicitly reports stricter first-half filters later failed, reinforcing frozen forward validation.

Source SHA256: 3782f26c0b9ae23d773c8956ff11a5724f11a01221c7963426d0bcc9bcc0e739
Full local result SHA256: f04a1a779b1c01dceb15caa6c7a0dec0d09084f521ec12981c9dc6c8d1f543c0
August sealed.
