import numpy as np
from CLEAN_RESTART_INITIAL_ENTRY_HOLD_ACCURACY import eval_net,root_features
from alpha_dukas.data import TICK_DTYPE

def ticks_at(t,mid,bid_offset=0):
    x=np.zeros(len(t),dtype=TICK_DTYPE);x['time_msc']=np.array(t)
    x['bid_raw']=np.array(mid)+bid_offset;x['ask_raw']=x['bid_raw']+600
    return x

def test_long_short_execution_sides_and_costs():
    x=ticks_at([5000,6000,7000,8000], [4000000,4000500,4001000,4001500])
    yes,pnl=eval_net(x,np.array([0]),np.array([1]),1)
    assert yes.tolist()==[True] and abs(pnl[0]+.4)<1e-12

def test_no_lookahead_entry_timing_and_gap():
    x=ticks_at([1000,2000,3000,4000,4999,5000,5001,10000,11000,12000],
               [1000000,1000000,1000000,1000000,1000000,1000000,1000000,1000000,1000500,1000700])
    f=root_features(x)
    # first candidate bar ends at :05 but only two preceding buckets are not available
    assert f['candidate_all_before_fill']==0

def test_missing_horizon_not_fabricated():
    x=ticks_at([5000,8000,9000], [4000000,4000500,4000800])
    yes,_=eval_net(x,np.array([0]),np.array([1]),1)
    assert yes.tolist()==[False]
