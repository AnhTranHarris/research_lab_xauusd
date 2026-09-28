"""Temporal, event-parent, symbol and time-boundary guards for discovery only."""
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from entry_hold_discovery_001 import generate_root_month, signals, BRANCHES
from alpha_dukas.data import TICK_DTYPE


def synthetic(n=3500):
    t=np.empty(n,dtype=TICK_DTYPE)
    base=1767315600000
    t['time_msc']=base+np.arange(n)*5000
    # Different regimes and pullback patterns with bid/ask both present.
    series=4320000+(np.arange(n)//500)*400+np.round(260*np.sin(np.arange(n)/8)).astype('int64')
    t['bid_raw']=series
    t['ask_raw']=series+190
    t['ask_volume']=.001;t['bid_volume']=.001
    return t

def test_signal_event_identity_and_completed_bar_visibility():
    t=synthetic()
    bars,idx,roots=generate_root_month(t,'2026-01')
    A=set(idx[BRANCHES[0]]);B=set(idx[BRANCHES[1]]);C=set(idx[BRANCHES[2]])
    assert C.issubset(B) and B.issubset(A)
    for fam,indices in idx.items():
        ss=signals(bars,indices,'2026-01',30000)
        assert all(s.ready_ms>=s.known_at_ms for s in ss)
        assert all(s.ready_ms in bars['end_ms'] for s in ss)
    if len(idx[BRANCHES[0]])>1:
        assert np.min(np.diff(bars['end_ms'][idx[BRANCHES[0]]]))>=30000


def test_modifying_future_quotes_cannot_change_past_parent_opportunities():
    t=synthetic();future=t.copy();cut=int(t['time_msc'][2600]);
    future['bid_raw'][2600:]+=4000;future['ask_raw'][2600:]+=4000
    bars_a,indices_a,_=generate_root_month(t,'2026-01')
    bars_b,indices_b,_=generate_root_month(future,'2026-01')
    for family in BRANCHES:
        a=bars_a['end_ms'][indices_a[family]];b=bars_b['end_ms'][indices_b[family]]
        assert np.array_equal(a[a<=cut],b[b<=cut])


def test_all_decisions_are_future_of_observation_timestamps():
    t=synthetic();bars,indices,_=generate_root_month(t,'2026-01')
    for family in BRANCHES:
        for signal in signals(bars,indices[family],'2026-01',120000):
            # With exactly one input tick per 5s bucket, completed-bar close
            # happens 5s after the last observation, not at same tick.
            assert signal.ready_ms>t['time_msc'][np.searchsorted(t['time_msc'],signal.ready_ms)-1]