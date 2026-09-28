from dataclasses import replace
from pathlib import Path
import numpy as np
import pytest

from alpha_dukas.data import (TICK_DTYPE, PRICE_SCALE, MONTH_SHA256, bars_from_ticks,
                              load_month, resolve_month_source, BAR_WIDTHS_MS)
from alpha_dukas.sim import ExecutionConfig, Signal, TickPortfolio


def ticks(data):
    a=np.zeros(len(data),dtype=TICK_DTYPE)
    for i,(t,b,ask) in enumerate(data):
        a[i]['time_msc']=t;a[i]['bid_raw']=b;a[i]['ask_raw']=ask
    return a


def signal(ready,side=1,stop=1.0,target=2.0,hold=1000,expiry=2000,sid='s'):
    return Signal(ready_ms=ready,known_at_ms=ready,side=side,
                  stop_usd=stop,target_usd=target,max_hold_ms=hold,
                  expires_ms=expiry,signal_id=sid)


def cfg(**kwargs):
    return replace(ExecutionConfig(initial_balance_usd=200,slippage_each_side_usd=0,
                                   commission_roundtrip_usd=0,max_spread_usd=3),**kwargs)


def test_exact_all_widths_and_non_nested_45s():
    # 60s: has three 45s buckets because 45s crosses minute boundary.
    x=ticks([(0,10_000,10_100),(249,10_100,10_200),
             (250,9_900,10_000),(44_999,10_400,10_500),
             (45_000,10_700,10_800),(60_000,10_800,10_900),
             (90_000,10_900,11_000)])
    assert len(bars_from_ticks(x,45_000))==3
    for width in BAR_WIDTHS_MS:
        b=bars_from_ticks(x,width)
        assert all(b['first_tick_ms']>=b['start_ms'])
        assert all(b['last_tick_ms']<b['end_ms'])
        assert all(b['n_ticks']>0)
        assert int(b['n_ticks'].sum())==len(x)
    b=bars_from_ticks(x,250)
    assert b['bid_h'][0]==10_100 and b['bid_l'][0]==10_000
    assert int(b['bid_o'][1])==9_900
    assert int(b['n_ticks'].sum())==len(x)
    assert 44_999//45_000==0 and 60_000//45_000==1


def test_invalid_period_rejected():
    with pytest.raises(ValueError):bars_from_ticks(ticks([(0,1,2)]),44_000)


def test_ohlc_has_no_future_and_no_fake_missing():
    x=ticks([(100,10000,10100),(2500,11000,11100)])
    b=bars_from_ticks(x,1000)
    assert list(b['start_ms'])==[0,2000]
    assert int(b[0]['end_ms'])==1000
    assert int(b[0]['bid_c'])==10000


def test_buy_ask_fill_and_bid_stop_in_tick_order():
    p=TickPortfolio(cfg())
    x=ticks([(1000,10000,10100),(1001,9000,9100),(1500,12500,12600)])
    v=p.run_block('2026-01',x,[signal(1000,stop=.5,expiry=2000)])
    assert len(p.trades)==1
    tr=p.trades[0]
    assert tr['entry_price']==10.1 and tr['exit_price']==9.0
    assert tr['reason']=='STOP_EXECUTABLE_TICK'
    assert tr['net_usd']==-1.1


def test_short_sell_bid_cover_ask_plus_commission():
    p=TickPortfolio(cfg(commission_roundtrip_usd=.20))
    x=ticks([(1000,10000,10100),(1001,7950,8000)])
    p.run_block('2026-01',x,[signal(1000,side=-1,target=1.5,expiry=2000)])
    tr=p.trades[0]
    assert tr['entry_price']==10.0 and tr['exit_price']==8.0
    assert tr['reason']=='TARGET_EXECUTABLE_TICK'
    assert tr['net_usd']==1.8


def test_max_hold_fills_at_next_actual_tick_not_hypothetical_bar_close():
    p=TickPortfolio(cfg())
    x=ticks([(1000,10000,10100),(3500,10500,10600)])
    p.run_block('2026-01',x,[signal(1000,hold=1200,stop=10,target=10,expiry=3000)])
    assert p.trades[0]['exit_ms']==3500
    assert p.trades[0]['reason']=='HOLD_TIMEOUT_NEXT_EXECUTABLE_TICK'


def test_one_position_and_month_carry_without_forced_liquidation():
    p=TickPortfolio(cfg())
    jan=ticks([(1000,10000,10100),(2000,10010,10110)])
    feb=ticks([(3000,10500,10600),(3100,11900,12000)])
    # Simulated next-month ticks are deliberately adjacent to test carry.
    p.run_block('2026-01',jan,[signal(1000,stop=5,target=1.5,hold=10000,expiry=2000)])
    assert p.pos is not None and not p.trades
    p.run_block('2026-02',feb,[signal(3000,stop=1,target=1,expiry=4000,sid='overlap')])
    assert p.pos is None and len(p.trades)==1
    assert p.trades[0]['open_month']=='2026-01'
    assert p.trades[0]['reason']=='TARGET_EXECUTABLE_TICK'
    assert p.rejection_counts['ONE_POSITION_ACTIVE']==1


def test_margin_and_spread_gates():
    x=ticks([(1000,10000,16000),(2000,9800,9900)])
    p=TickPortfolio(cfg(max_spread_usd=2))
    p.run_block('2026-01',x,[signal(1000,expiry=3000)])
    assert p.rejection_counts['SPREAD_GATE']==1
    p=TickPortfolio(cfg(initial_balance_usd=0.01))
    p.run_block('2026-01',ticks([(1000,10000,10100)]),[signal(1000,expiry=3000)])
    assert p.rejection_counts['MARGIN_GATE']==1


def test_signal_causality_and_scope():
    with pytest.raises(ValueError):Signal(100,101,1,1,2,100,200,'peek')
    with pytest.raises(ValueError):Signal(100,100,1,1,2,100,200,'same_tick','tick_observed')
    assert Signal(101,100,1,1,2,100,200,'next_tick','tick_observed').ready_ms==101
    with pytest.raises(ValueError):resolve_month_source(Path('/mnt/data'),'2026-08')
    with pytest.raises(ValueError):load_month(Path('/tmp'),'2026-08')


def test_gaps_do_not_fill_hypothetical_prices():
    x=ticks([(1000,10000,10010),(2000,5000,5010)])
    p=TickPortfolio(cfg())
    p.run_block('2026-01',x,[signal(1000,stop=1,target=3,expiry=2000)])
    assert p.trades[0]['exit_price']==5.0
    assert p.trades[0]['net_usd']==-5.01


def test_replay_cannot_duplicate_month():
    x=ticks([(1000,10000,10100)])
    p=TickPortfolio(cfg());p.run_block('2026-01',x,[])
    with pytest.raises(ValueError):p.run_block('2026-01',x,[])


def test_costed_execution_includes_two_adverse_slippage_sides():
    x=ticks([(1000,10000,10100),(2000,10500,10600)])
    p=TickPortfolio(cfg(slippage_each_side_usd=.05,
                        commission_roundtrip_usd=.20))
    p.run_block('2026-01',x,[signal(1000,target=.3,stop=10,expiry=3000)])
    assert p.trades[0]['entry_price']==10.15
    assert p.trades[0]['exit_price']==10.45
    assert p.trades[0]['net_usd']==.10


def test_same_millisecond_input_order_not_silently_deduplicated():
    x=ticks([(1000,10000,10100),(1000,8000,8100),(1001,16000,16100)])
    p=TickPortfolio(cfg())
    p.run_block('2026-01',x,[signal(1000,stop=1,expiry=2000)])
    assert p.trades[0]['exit_ms']==1000
    assert p.trades[0]['reason']=='STOP_EXECUTABLE_TICK'
    assert p.trades[0]['exit_price']==8.0


def test_completed_bar_end_excludes_later_tick_and_fills_at_bar_close_boundary():
    x=ticks([(999,10000,10100),(1000,11000,11100),(1100,12000,12100)])
    m=bars_from_ticks(x,1000)
    assert m[0]['bid_c']==10000
    p=TickPortfolio(cfg())
    p.run_block('2026-01',x,[signal(1000,target=.3,expiry=2000)])
    assert p.trades[0]['entry_price']==11.1
    assert p.trades[0]['exit_ms']==1100


def test_pending_signal_survives_month_if_unexpired_and_is_first_filled_next_month():
    p=TickPortfolio(cfg())
    jan=ticks([(1000,10000,10100)])
    feb=ticks([(3000,10000,10100),(3500,12200,12300)])
    p.run_block('2026-01',jan,[signal(2000,expiry=4000)])
    assert p.pos is None and len(p.pending)==1
    p.run_block('2026-02',feb,[])
    assert len(p.trades)==1
    assert p.trades[0]['entry_ms']==3000
    assert p.trades[0]['open_month']=='2026-02'
    assert p.trades[0]['reason']=='TARGET_EXECUTABLE_TICK'