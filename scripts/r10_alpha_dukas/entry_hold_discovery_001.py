"""R10 Alpha exploratory structural ENTRY + HOLD: registered before first outcome read.

Market source: independent Dukascopy 2026 XAUUSD ticks. The computed signals are
not original Coinexx R9 signals, and output is not an approved EA validation.
All price features based on completed UTC-anchored bars; execution is on the
next available source Bid/Ask tick through the existing TickPortfolio.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import pandas as pd
from alpha_dukas.data import bars_from_ticks, load_month
from alpha_dukas.sim import ExecutionConfig, Signal, TickPortfolio

EXPERIMENT = 'ENTRY_HOLD_DISCOVERY_001'
BRANCHES = ('STRUCTURE_RESUME','STRUCTURE_PULLBACK_RESUME','STRUCTURE_PULLBACK_QUALITY')
HOLD_MS = (30_000, 120_000)

def generate_root_month(ticks, month: str):
    b5=bars_from_ticks(ticks, 5000)
    end=b5['end_ms'];close=b5['bid_c'].astype(np.int64)
    opened=b5['bid_o'].astype(np.int64)
    spread_at_close=b5['ask_c'].astype(np.int64)-close
    votes=[]
    for width in (900000, 1800000, 3600000):
        h=bars_from_ticks(ticks,width)
        # Higher timeframe bar is only observable at its END; no forming bars.
        idx=np.searchsorted(h['end_ms'],end,side='right')-1
        valid=idx>=2
        cur=h['bid_c'][np.maximum(idx,0)].astype(np.int64)
        lag=h['bid_c'][np.maximum(idx-2,0)].astype(np.int64)
        # A trend vote must be based on a recent sequence, not pre-weekend bars.
        recent=(end-h['end_ms'][np.maximum(idx,0)])<=width
        vote=np.sign(cur-lag).astype(np.int8)
        vote[~(valid&recent)]=0
        votes.append(vote)
    score=votes[0]+votes[1]+votes[2]
    direction=np.where(score>=2,1,np.where(score<=-2,-1,0)).astype(np.int8)
    # Short-term signed 5s bar body; fixed preregistered minimum 25 cents.
    body=(close-opened)*direction
    base=(direction!=0)&(body>=250)&(spread_at_close<=1200)
    # Current close versus last 60s *previous completed* 5s Bid range extreme.
    past_hi=pd.Series(b5['bid_h'].astype(np.int64)).shift(1).rolling(12,min_periods=10).max().to_numpy()
    past_lo=pd.Series(b5['bid_l'].astype(np.int64)).shift(1).rolling(12,min_periods=10).min().to_numpy()
    # Stale prior days or gaps are not allowed to satisfy the lookback window.
    continuous=np.zeros(len(end),dtype=np.bool_)
    continuous[12:]=(b5['start_ms'][12:]-b5['start_ms'][:-12])<=60000
    pullback=base & continuous & np.where(direction>0,(past_hi-close)>=1200,(close-past_lo)>=1200)
    local_bar_range=(b5['bid_h']-b5['bid_l']).astype(np.float64)
    efficiency=np.divide(np.abs(close-opened),np.maximum(local_bar_range,1.0))
    # The 3-bar (15 s) directional quality uses only 5s bars completed by E.
    d=np.zeros(len(end),dtype=np.float64)
    changes=np.abs(np.diff(close.astype(np.float64),prepend=close[0]))
    denom=pd.Series(changes).rolling(3,min_periods=3).sum().to_numpy()
    d[3:]=(close[3:]-close[:-3])*direction[3:]
    smooth=np.divide(d,np.maximum(denom,1.),out=np.zeros_like(d),where=np.isfinite(denom))
    quality=pullback &(efficiency>=0.60)&(smooth>=0.35)
    # Anchor one root EVENT every >=30s from the full A parent universe.
    # Sub-branches can only remove events from this frozen root list.
    root=[];last=-999999999999
    for i in np.flatnonzero(base):
        if int(end[i])-last<30000:continue
        last=int(end[i]);root.append(int(i))
    all_idx=np.array(root,dtype=np.int64)
    keep_b=pullback[all_idx]
    keep_c=quality[all_idx]
    return b5,{BRANCHES[0]:all_idx,BRANCHES[1]:all_idx[keep_b],BRANCHES[2]:all_idx[keep_c]},dict(
        root_parent_events=len(all_idx),B_parent_eligible=int(keep_b.sum()),C_parent_eligible=int(keep_c.sum()),
        n_completed_5s_bars=len(b5),first_source_tick=int(ticks['time_msc'][0]),last_source_tick=int(ticks['time_msc'][-1]))

def signals(bars,indices,month,hold_ms):
    out=[]
    for i in indices:
        end=int(bars['end_ms'][i]);side=1 if bars['bid_c'][i]>=bars['bid_o'][i] else -1
        # actual trade side must follow higher-timeframe vote, which agrees with
        # 5s body by >=0.25 under A. For robustness verify side matches body.
        out.append(Signal(ready_ms=end, known_at_ms=end, side=side,
            stop_usd=1.20,target_usd=3.0,max_hold_ms=int(hold_ms),
            expires_ms=end+5000,signal_id=f'{month}:{i}',observation_type='completed_bar'))
    return out

def summarise(name,months,trades,ledger,rel):
    wins=[z for z in trades if z['net_usd']>0]
    tp=[z for z in trades if z['reason']=='TARGET_EXECUTABLE_TICK']
    losses=[z['net_usd'] for z in trades if z['net_usd']<0]
    gps=sum(max(0,z['net_usd']) for z in trades);gl=sum(min(0,z['net_usd']) for z in trades)
    return dict(strategy=name,months=months,trades=len(trades),wins=len(wins),win_rate=round(len(wins)/len(trades),6) if trades else None,
                target_hit_count=len(tp),target_hit_rate=round(len(tp)/len(trades),6) if trades else None,
                net_usd=round(sum(z['net_usd'] for z in trades),4),gross_profit_after_fees=round(gps,4),
                gross_loss_after_fees=round(gl,4),profit_factor=round(gps/(-gl),5) if gl else None,
                max_drawdown_usd=round(ledger.max_drawdown_usd,4),balance_final=round(ledger.balance,4),
                root_opportunities=rel['root_parent_events'],relative_opportunity_retention=round(rel['eligible_count']/max(1,rel['root_parent_events']),5),
                rejections=ledger.rejection_counts)

def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--months',nargs='+',default=['2026-01']);p.add_argument('--initial-balance',type=float,default=200.);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    models={(name,h):TickPortfolio(ExecutionConfig(initial_balance_usd=args.initial_balance,lot=.01,contract_oz_per_lot=100.,leverage=500.,commission_roundtrip_usd=.20,slippage_each_side_usd=.05,max_spread_usd=1.20,maintenance_margin_ratio=.5))for name in BRANCHES for h in HOLD_MS}
    roots={};monthly=[]
    for month in args.months:
        arr,meta=load_month(args.cache,month)
        b5,idxs,root=generate_root_month(arr,month);roots[month]=root
        for (name,h),port in models.items():
            ss=signals(b5,idxs[name],month,h)
            info=port.run_block(month,arr,ss)
            monthly.append(dict(model=name,hold_ms=h,signal_candidates=len(ss),**info))
    root_all=sum(x['root_parent_events'] for x in roots.values())
    summary=[];trade_records=[]
    for (name,h),p in models.items():
        count=sum(z['signal_candidates'] for z in monthly if z['model']==name and z['hold_ms']==h)
        rec=summarise(f'{name}_H{h//1000}s',args.months,p.trades,p,dict(root_parent_events=root_all,eligible_count=count))
        rec['hold_ms']=h;rec['eligible_events']=count
        summary.append(rec)
        for r in p.trades:trade_records.append(dict(model=name,max_hold_rule_ms=h,**r))
    pd.DataFrame(monthly).to_csv(args.output/'monthly.csv',index=False)
    pd.DataFrame(trade_records).to_csv(args.output/'trades.csv',index=False)
    results=dict(account_diagnostic_initial_balance_usd=args.initial_balance,protocol='R10 Alpha Entry+Hold 001 preregistration',evidence='EXPLORATORY_DUKASCOPY_JAN_ONLY_WHERE_APPLICABLE',months=args.months,source='DUKASCOPY_INDEPENDENT_FROM_R9_MT5',roots=roots,results=summary,approved_EA_baseline='NOT_DESIGNATED',owner_candidate_gate_status='CANNOT_EVALUATE',mql5_build='NONE',note='Each strategy uses own chronological single-account execution; stop/target uses tick bid/ask, slippage and commission assumptions; teacher future labels never used in signals.')
    (args.output/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(dict(months=args.months,root=roots,results=[{k:r[k] for k in ('strategy','eligible_events','trades','win_rate','target_hit_rate','net_usd','profit_factor','max_drawdown_usd','balance_final')} for r in summary]),indent=2))

if __name__=='__main__':main()