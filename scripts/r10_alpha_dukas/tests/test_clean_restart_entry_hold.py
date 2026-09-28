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

def test_short_executes_bid_to_ask_plus_fees():
    x=ticks_at([5000,6000,7000], [4000000,3999500,3999000])
    valid,net=eval_net(x,np.array([0]),np.array([-1]),1)
    # Short: bid(4000.000) - ask(3999.500+0.600)= -0.100,
    # minus 0.100 slippage and 0.200 commission = -0.400.
    assert valid.tolist()==[True] and abs(net[0]+0.4)<1e-12

def test_exact_boundary_exit_does_not_select_earlier_quote():
    x=ticks_at([5000,5999,6000,6100],[4000000,4002000,4000500,4003000])
    valid,net=eval_net(x,np.array([0]),np.array([1]),1)
    assert valid.tolist()==[True]
    # At 6000 quote moves only $0.5, not the +$2 earlier at 5999.
    assert abs(net[0]+0.4)<1e-12

def test_chronological_signal_features_ignore_future_ticks():
    # Three completed 5s buckets before minute :05 and a post-close fill.
    ts=list(range(45000,65000,500))
    bid=[4000000]*len(ts)
    for j,t in enumerate(ts):
        if 50000<=t<55000:bid[j]=4000000
        if 55000<=t<60000:bid[j]=4000100
        if 60000<=t<65000:bid[j]=4000900
    x=ticks_at(ts,bid)
    f=root_features(x)
    # This toy has an impulse on the 00:00-00:05 bar only if its end is 65s;
    # no other qualifying minute close can retroactively use post-65s ticks.
    assert f['candidate_all_before_fill']==1 and len(f['fill_idx'])==0
