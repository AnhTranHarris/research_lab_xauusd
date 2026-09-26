# R9B_GAMMA2_REGIME_SPECIALIST_RECOVERY_013

Status: VERIFIED_DURABLE_DIAGNOSTIC_CANDIDATE. Not promoted.

## Result

The explicit regime-specialist mixture recovers part of the winner-density sacrificed by 012 while retaining material gross-loss compression versus the 010 identity baseline.

Jan-Jul:
- 165,784 trades
- 121,331 winners
- 73.186% win rate
- -$27,718.77 net
- -$75,797.93 gross loss
- PF 0.6343

010 same-population baseline:
- 232,112 trades
- 167,337 winners
- 72.093% win rate
- -$41,536.80 net
- -$106,249.14 gross loss

Delta versus 010:
- 28.66% less gross loss
- +$13,818.03 net improvement
- +1.09 percentage points win rate
- 72.51% winner retention

May-Jul frozen:
- 61,277 trades / 43,947 winners / 71.719% / -$11,329.43 net / -$25,319.44 GL
- versus 010: 89,925 / 63,898 / 71.057% / -$16,431.39 / -$36,568.08 GL
- 30.76% less GL, +$5,101.96 net improvement, +0.66 pp win rate, 68.78% winner retention

Compared with 012 low-loss specialist, 013 recovers 46,748 additional Jan-Jul winners but gives back $28,879 of gross-loss compression. This quantifies the current Pareto frontier.

## Architecture

Causal regime hierarchy:
- ROTATION specialist
- EXPANSION specialist
- COMPRESSION specialist
- STRUCTURAL specialist
- TRANSITION/Gamma fallback specialist

Each specialist has separate feature ownership and a separate action model. Future outcomes remain teacher labels in Jan-Mar only. April selects complexity. May-Jul are frozen. Execution is one chronological ledger using exact-tick FADE/CONTINUE outcomes.

## Interpretation

Regime awareness should not be used only as a trade filter. 012 proves it can sharply reduce loss; 013 proves separate state-conditioned experts can recover a substantial fraction of the discarded winners. The remaining task is to replace generic within-regime action trees with transparent mechanisms that already showed historical specialist value.

Project archaeology now prioritizes re-certification of:
- P4 low/normal-volatility inefficient-travel rotation/fade
- P6 high-volatility or high-efficiency expansion/continuation
- P7 volatility-normalized compression-release
- P5 H1/H4 structural trend

These old results are mechanism evidence only until rebuilt inside the current causal Gamma stack.

## Current public mechanism support

- MQL5 Market Regime Detection Part 1/2: statistical regime classification and strategy-specific routing.
  https://www.mql5.com/en/articles/17737
  https://www.mql5.com/en/articles/17781
- Chinese MQL5 dynamic EA: mean-reversion and momentum should be separate logic inside one adaptive engine, with signal-fatigue control.
  https://www.mql5.com/zh/articles/18037
- Japanese MQL5 self-optimizing EA: transition-matrix/regime selection between trend-following and mean-reversion.
  https://www.mql5.com/ja/articles/15040
- TradingView open-source regime classifier: regime describes conditions, not direction; continuation belongs to trend states and fading to range states.
  https://www.tradingview.com/script/aoaLrcvL-Market-Regime-Trend-or-Range/
- Reddit gold model discussion: combining uncorrelated models can help, but regime switching can also remove profitable trades; benchmark against running specialists without the gate.
  https://www.reddit.com/r/algotrading/comments/1v8u1pv/gold_model_strategy/
- Reddit gold scalper: combining regime settings into one engine reduced double triggers; author also warns that added filters often overfit.
  https://www.reddit.com/r/algotrading/comments/1shgpyf/improved_my_algo_again_and_adapted_to_gold/

## Decision

Do not promote 013. Preserve it as the middle frontier between 012's strong loss compression and 010's density.

Next unit: R9B_GAMMA2_TRANSPARENT_SPECIALIST_RECERT_014

Rebuild P4/P6/P7/P5 transparently on current exact-tick Dukascopy chronology, then route them through one owner ledger. Priority: loss -> winners/success -> net. August sealed.

Source SHA256: b8d50b06f1b8f883f1eead4d4aeaf4c876e30c8ba898c335c7e81b6add3a68c5
Full result SHA256: 8875f7ef2d8772774874219c08d8bc704323885a57b37fa9bfd62b025edfb252
