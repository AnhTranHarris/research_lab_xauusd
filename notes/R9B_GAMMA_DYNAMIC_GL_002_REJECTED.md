# R9B_GAMMA_DYNAMIC_GL_002 — State-conditioned lifecycle / orthogonal gate screen

Status: VERIFIED_DURABLE_REJECTED_AS_CORE. August sealed.

Working parent: GL001 frozen January ownership.

Residual Jan-Apr loss attribution shows the remaining GL is concentrated in owned alignment 0-2 trades, especially FADE A1/A2 low-confidence groups, with loser severity around -$1.8 despite ~73% win rates. This motivated state-conditioned stop caps rather than a universal stop grid.

Exact-tick January stop-cap replay rejects the idea at the system level. Tighter stops shorten occupancy, admit replacement events and recreate the loss. Even the best tested variant improves GL only ~0.17% and worsens net/DD. Do not revisit simple state-conditioned stop caps without an explicit rearm/ownership change.

The exact historical GAMMA-01 session-normalized ATR ratio overlay was also tested on fixed GL001 ownership over Jan-Apr. Because Gamma014 sweep eligibility already lives almost entirely in ATR/session ratio >=1.5 states, the canonical 1.50 gate adds only 1.35% GL reduction with 98.39% winner retention. At 1.60 it adds 2.12% GL reduction. This layer is largely redundant with the current event population and should not be integrated.

Next mechanism: state durability / transition hazard. Prior 017A evidence showed state age collapsed in July while classification confidence stayed high. GL003 will add only reconstructible causal duration features (structural-owner age, alignment-state age, recent owner-transition count) to the ownership decision and test whether durability information adds incremental GL compression.

Artifacts:
- residual attribution SHA b7f69e92d81358fe4092ed3238a911943643af111ed314487be529bebf06dcfb
- stopcap screen SHA 784055661291388631790533f1447e8ba987e767c5ddf4955a375665f25c7b5c
- GAMMA01 overlay SHA c2f9ea344c8063918d10a1bbd1074a7294e14964348aee7265a052561268bc77
