"""Rebuilt R8 recert helper used by Gamma_2.

`build_sec` is intentionally small and deterministic. It constructs active-second
completed bid bars from the fixed-$0.20 modeled spread used by the Gamma_2 lab.
"""
import numpy as np
H = 0.10


def build_sec(t, mid, half_spread=H):
    t = np.asarray(t, dtype=np.int64)
    mid = np.asarray(mid, dtype=np.float64)
    bid = mid - float(half_spread)
    sec = t // 1000
    ch = np.empty(len(sec), dtype=bool)
    ch[0] = True
    ch[1:] = sec[1:] != sec[:-1]
    ix = np.flatnonzero(ch)
    last = np.r_[ix[1:] - 1, len(sec) - 1]
    su = sec[ix].astype(np.int64)
    hi = np.maximum.reduceat(bid, ix).astype(np.float64)
    lo = np.minimum.reduceat(bid, ix).astype(np.float64)
    cl = bid[last].astype(np.float64)
    return su, hi, lo, cl
