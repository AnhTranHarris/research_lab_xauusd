"""Owner-authorized clean Alpha restart: preregistered fixed-horizon ENTRY/HOLD accuracy.

Uses only source Dukascopy Bid/Ask, causal completed 5s buckets and fixed UTC
clock opportunities; no Gamma or quarantined Alpha001 strategy code is imported.
This is a MARKOUT DIAGNOSTIC, NOT a chronological capital/trading backtest.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from numba import njit
from alpha_dukas.data import prepare_month, load_month, bars_from_ticks, MONTH_SHA256, DAY_MS

HORIZONS=(1,3,10,20,30,60)
FAMILIES=('CALENDAR_NULL','FLOW_CONTINUE','FLOW_FADE','FLOW_AGREE')
PREREG='CLEAN_RESTART_20260928_INITIAL_ENTRY_HOLD_PREREGISTRATION.md'


def root_features(ticks):
    """Fully observable root at the first completed 5s close of each UTC minute."""
    b=bars_from_ticks(ticks,5000)
    ends=b['end_ms']
    idx=np.flatnonzero((ends%60000)==5000)
    idx=idx[idx>=2]
    consecutive=(b['start_ms'][idx]-b['start_ms'][idx-1]==5000)&(b['start_ms'][idx-1]-b['start_ms'][idx-2]==5000)
    valid_ticks=(b['n_ticks'][idx]>=2)&(b['n_ticks'][idx-1]>=2)&(b['n_ticks'][idx-2]>=2)
    idx=idx[consecutive&valid_ticks]
    delta=b['bid_c'][idx].astype(np.int64)-b['bid_c'][idx-1].astype(np.int64)
    prior=b['bid_c'][idx-1].astype(np.int64)-b['bid_c'][idx-2].astype(np.int64)
    spr=b['ask_c'][idx].astype(np.int64)-b['bid_c'][idx].astype(np.int64)
    ok=(np.abs(delta)>=500)&(spr<=1250)
    idx,delta,prior=idx[ok],delta[ok],prior[ok]
    end=b['end_ms'][idx]
    tt=ticks['time_msc']
    fi=np.searchsorted(tt,end,side='left')
    fi=np.minimum(fi,len(tt)-1)
    fill_ok=(tt[fi]>=end)&(tt[fi]<=end+1000)&((ticks['ask_raw'][fi].astype(np.int64)-ticks['bid_raw'][fi].astype(np.int64))<=1250)
    return {
        'bar_total':int(len(b)), 'candidate_all_before_fill':int(len(idx)),
        'skipped_fill_missing_or_spread':int(np.count_nonzero(~fill_ok)),
        'idx':idx[fill_ok], 'delta':delta[fill_ok], 'prior':prior[fill_ok],
        'end':end[fill_ok], 'fill_idx':fi[fill_ok]
    }


def eval_net(ticks, fill_idx, side, horizon_s):
    """Real Bid exit of long / Ask exit of short, both slippages and commission."""
    ts=ticks['time_msc'];entry_ts=ts[fill_idx];tgt=entry_ts+horizon_s*1000
    ix=np.searchsorted(ts,tgt,side='left'); ix=np.minimum(ix,len(ts)-1)
    valid=(ts[ix]>=tgt)&(ts[ix]<=tgt+1000)&(ix>fill_idx)
    ask0=ticks['ask_raw'][fill_idx].astype(np.int64)
    bid0=ticks['bid_raw'][fill_idx].astype(np.int64)
    bid1=ticks['bid_raw'][ix].astype(np.int64)
    ask1=ticks['ask_raw'][ix].astype(np.int64)
    # Units USD per oz in integer-thousandths; one-ounce exposure at 0.01 lot.
    net=np.where(side>0,(bid1-ask0)/1000.,(bid0-ask1)/1000.)-.10-.20
    return valid,net


@njit

def excursions_30(ts,bid,ask,fi,side):
    n=len(fi); hi=np.empty(n,np.float64);lo=np.empty(n,np.float64)
    for k in range(n):
        a=fi[k];s=side[k];deadline=ts[a]+30_000
        ent=ask[a] if s>0 else bid[a]
        best=-1e9;worst=1e9
        j=a+1
        while j<len(ts) and ts[j]<=deadline:
            price=bid[j] if s>0 else ask[j]
            pnl=(price-ent)*s/1000.-.30
            if pnl>best:best=pnl
            if pnl<worst:worst=pnl
            j+=1
        hi[k]=best if best>-1e8 else np.nan
        lo[k]=worst if worst<1e8 else np.nan
    return hi,lo


def summary(net,valid,retention,total,side,excur_hi,excur_lo):
    x=net[valid];n=len(x)
    gp=float(x[x>0].sum());gl=float(x[x<0].sum())
    mh=excur_hi[np.isfinite(excur_hi)];ml=excur_lo[np.isfinite(excur_lo)]
    return dict(attempts=int(total),filled=int(len(net)),observed=int(n),missing=int(len(net)-n),
                retained_fraction_of_filled_root=float(retention),long_share=float(np.mean(side>0)) if len(side) else None,
                after_cost_positive_fraction=float(np.mean(x>0)) if n else None,
                mean_net_usd=float(np.mean(x)) if n else None,
                median_net_usd=float(np.median(x)) if n else None,
                sum_hypothetical_net_usd=float(np.sum(x)),
                gross_positive_usd=gp,gross_negative_usd=gl,
                profit_factor=float(gp/-gl) if gl<0 else None,
                horizon_MFE_30s_net_median=float(np.median(mh)) if len(mh) else None,
                horizon_MAE_30s_net_median=float(np.median(ml)) if len(ml) else None)


def analyze(data_root:Path, cache_root:Path, output:Path):
    meta=prepare_month(data_root,cache_root,'2026-01');ticks,manifest=load_month(cache_root,'2026-01')
    f=root_features(ticks);fi=f['fill_idx'];tt=ticks['time_msc'];barend=f['end']
    assert len(fi)>0 and np.all(tt[fi]>=barend) and np.all(tt[fi]<=barend+1000)
    assert np.all((barend%60000)==5000) and np.min(f['delta']!=0)
    primary=np.sign(f['delta']).astype(np.int8)
    null=np.where((barend//60000)%2==0,1,-1).astype(np.int8)
    same=(np.sign(f['prior'])==primary)&(np.abs(f['prior'])>=150)
    designs={'CALENDAR_NULL':(np.ones(len(fi),dtype=np.bool_),null),
             'FLOW_CONTINUE':(np.ones(len(fi),dtype=np.bool_),primary),
             'FLOW_FADE':(np.ones(len(fi),dtype=np.bool_),-primary),
             'FLOW_AGREE':(same,primary)}
    outputs={};horizons={};day_rows=[]
    dates=np.array([datetime.fromtimestamp(int(t/1000),tz=timezone.utc).date().isoformat() for t in barend],dtype='U10')
    for name in FAMILIES:
        mask,side_all=designs[name];ix=fi[mask];side=side_all[mask];on_date=dates[mask]
        mh,ml=excursions_30(tt,ticks['bid_raw'],ticks['ask_raw'],ix,side)
        horizons[name]={}
        all_h={}
        for h in HORIZONS:
            valid,net=eval_net(ticks,ix,side,h);all_h[h]=(valid,net)
            stat=summary(net,valid,len(ix)/len(fi),len(fi),side,mh,ml)
            # If horizons not 30s, the early path MFE/MAE are separate 30s diagnostics.
            horizons[name][str(h)]=stat
        # Transition from 1s net negative into 10/30/60s positive with paired valid paths.
        v1,x1=all_h[1]; transitions={}
        for h in (3,10,20,30,60):
            vh,xh=all_h[h];paired=v1&vh;negative=paired&(x1<=0)
            transitions[str(h)]={'paired':int(np.sum(paired)),'initially_nonpositive':int(np.sum(negative)),
                'recovered_net_positive_fraction':float(np.mean(xh[negative]>0)) if np.any(negative) else None,
                'positive_at_1s_and_h_fraction':float(np.mean((x1[paired]>0)&(xh[paired]>0))) if np.any(paired) else None}
        outputs[name]={'attempt_count':int(len(ix)), 'mfe_path_30s_available':int(np.count_nonzero(np.isfinite(mh))),
                       'transitions':transitions}
        for date in np.unique(on_date):
            mask_d=(on_date==date)
            for h in (10,30):
                v,x=all_h[h];val=mask_d&v;z=x[val]
                day_rows.append(dict(utc_date=date,family=name,horizon_s=h,root_filled=int(np.sum(mask_d)),
                     observed=int(np.sum(val)),positive_after_cost=int(np.count_nonzero(z>0)),
                     net_sum_fixed_horizon_usd=round(float(np.sum(z)),5),
                     mean_net_usd=round(float(np.mean(z)),6) if len(z) else ''))
    # Matched root parent compare CONTINUE vs FADE/NULL at the same event/horizon.
    pair={}
    for h in (1,3,10,20,30,60):
        vals={};valids={}
        for name in ('CALENDAR_NULL','FLOW_CONTINUE','FLOW_FADE'):
            v,x=eval_net(ticks,fi,designs[name][1],h);vals[name]=x;valids[name]=v
        paired=valids['CALENDAR_NULL']&valids['FLOW_CONTINUE']&valids['FLOW_FADE']
        diffs=vals['FLOW_CONTINUE'][paired]-vals['CALENDAR_NULL'][paired]
        days=dates[paired]
        unique=np.unique(days)
        # Resample DATE BLOCKS (not individual correlated trades).
        cnt=np.array([np.count_nonzero(days==d) for d in unique]);sumdiff=np.array([np.sum(diffs[days==d]) for d in unique])
        rng=np.random.default_rng(20260928+h)
        if len(unique)>1:
            picks=rng.integers(0,len(unique),size=(2000,len(unique)))
            bs=np.sum(sumdiff[picks],axis=1)/np.maximum(np.sum(cnt[picks],axis=1),1)
            bounds=np.quantile(bs,[0.025,0.975]).tolist()
        else:bounds=[None,None]
        pair[str(h)]={'paired_roots':int(np.count_nonzero(paired)),'continue_less_null_mean_net_usd':float(np.mean(diffs)) if len(diffs) else None,
                      'cluster_day_bootstrap_95pct_CI':bounds,'paired_utc_days':len(unique)}
    packet={ 'schema':'clean_restarted_initial_entry_hold_accuracy_v1',
         'scientific_status':'EXPLORATORY_CAUSAL_MARKOUT_ONLY_NOT_EA_PNL_NOT_APPROVED',
         'month':'2026-01','original_source_sha256':meta['source_sha256'],
         'source_rows':meta['tick_count'],'source_dates':len(meta['daily_tick_rows']),
         'bar_interval_ms':5000,'bar_total':f['bar_total'],
         'opportunities_before_fill':f['candidate_all_before_fill'],
         'skip_missing_or_wide_entry_spread':f['skipped_fill_missing_or_spread'],
         'after_bidask_spread_and_fees_filled_root':len(fi),
         'families':outputs,'horizons_seconds':horizons,'paired_comparisons':pair,
         'future_months_inspected_for_this_clean_experiment':[],
         'august':'SEALED','gamma_strategy_imported':False,
         'owner_approved_alpha_ea_baseline':'NOT_DESIGNATED',
         'formal_10pct_gate':'NOT_EVALUABLE',
         'limitations':['January in sample from previous investigation','No capital/margin/stop simulation in fixed horizon markouts','Different source feed from R9 Coinexx','R9 future-informed labels never features','Repeated horizons are counterfactual, not realized simultaneous profits']}
    output.mkdir(parents=True,exist_ok=True)
    p=output/'CLEAN_RESTART_INITIAL_ENTRY_HOLD_JAN_RESULT.json'
    p.write_text(json.dumps(packet,indent=2,sort_keys=True)+'\n')
    with (output/'CLEAN_RESTART_INITIAL_ENTRY_HOLD_JAN_DAILY.csv').open('w',newline='') as wf:
        wr=csv.DictWriter(wf,fieldnames=list(day_rows[0]));wr.writeheader();wr.writerows(day_rows)
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    print(json.dumps({'run_status':'COMPLETE','source_rows':meta['tick_count'],'source_sha256':meta['source_sha256'],
                      'parents':f['candidate_all_before_fill'],'fill_roots':len(fi),
                      'sha256_result':digest,'root_output':str(p),
                      'h10':{k:horizons[k]['10']['mean_net_usd'] for k in FAMILIES},
                      'h30':{k:horizons[k]['30']['mean_net_usd'] for k in FAMILIES}},indent=2))
    return packet

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('/mnt/data'))
    ap.add_argument('--cache',type=Path,default=Path('/mnt/data/clean_alpha_20260928/cache'))
    ap.add_argument('--out',type=Path,default=Path('/mnt/data/clean_alpha_20260928/results'))
    a=ap.parse_args();analyze(a.root,a.cache,a.out)
