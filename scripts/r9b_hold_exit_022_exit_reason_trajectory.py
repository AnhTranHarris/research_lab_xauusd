"""HOLD_EXIT_022 -- causal CAUSAL_RECERT_014 exit-reason source closure.

Purpose: recover *observability and attribution* of the original Jan parent;
NOT an optimized/new exit strategy. Source-locked baseline identical to
r9b_sweep_structure_exit_candidate.replay_hybrid. All trajectories stop at
original exit, and exit-reason labels are ex-post, NEVER live inputs.

True Dukascopy bid/ask is not used here: original CAUSAL014 modeled midpoint
with a $0.10 half-spread. This is scientific parity, not broker certification.

ONE stage: January exit-reason attribution and exact parent replay parity.
April, May--July, and sealed August are deliberately not used.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import zipfile

import numpy as np
from numba import njit

ROOT = Path('/mnt/data')
OUT = ROOT/'hold022_results'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT/'net023_src'))
sys.path.insert(0, str(ROOT/'net024_src'))
import r9b_screen as R
import net024_h1_permission as N

PARENT_CACHE=ROOT/'net024_results'/'NET024_RAW_01.npz'
PARENT_MANIFEST=ROOT/'net024_results'/'NET024_RAW_01.manifest.json'
PARENT_GOLDEN={'raw':34362, 'trades':28088,'winners':19087,
    'net':-4510.0870000207515,'gross_profit':7001.463999985857,
    'gross_loss':-11511.55100000661}
REASON_NAMES={'1':'HARD_INITIAL_STOP', '2':'RATCHETED_TRAIL_STOP', '3':'MAXHOLD_TIMEOUT'}
HALF_SPREAD=.10


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for x in iter(lambda:f.read(1<<20),b''):
            h.update(x)
    return h.hexdigest()


def atomic_json(path,obj):
    path=Path(path)
    tmp=path.with_suffix('.tmp.json')
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')
    os.replace(tmp,path)


def atomic_npz(path,**arrays):
    path=Path(path);tmp=path.with_suffix('.tmp.npz')
    np.savez_compressed(tmp,**arrays)
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None, 'NPZ zip member CRC failed'
    with np.load(tmp,allow_pickle=False) as z:
        assert sorted(z.files)==sorted(arrays.keys())
        for k,v in arrays.items():
            assert z[k].shape==v.shape and z[k].dtype==v.dtype,(k,z[k].shape,v.shape)
            assert np.array_equal(z[k],v,equal_nan=True),k
    os.replace(tmp,path)


@njit(cache=True)
def traced_original_replay(t,mid,X):
    """Literal CAUSAL014 ordering; only new work is recording prior-to-exit state.

    Stop condition is evaluated BEFORE updating trailing on each quote. If
    stop and 60s horizon occur on the same quote, original stop wins. A quote
    at parent exit is not available for discretionary intervention.
    """
    n=len(X)
    o=np.empty((n,6),np.float64)
    # 0 actual_entry_quote_ms, 1 exit reason, 2 first armed ms, 3 first
    # positive executable quote ms, 4 count of trailing stop ratchets,
    # 5 last fresh MFE ms, 6 tick count to exit, 7 stop at exit,
    # 8 executable fav at exit, 9 giveback from observed MFE at exit,
    # 10 directional $0.02 MFE renewal count, 11 simultaneous timeout.
    a=np.full((n,12),np.nan,np.float64)
    H=.10
    for k in range(n):
        sig=int(X[k,0]);side=int(X[k,1]);align=X[k,3]
        if align>=3:
            stopd=1.0;act=.10;trail=.04;maxhold=60;mode=1
        else:
            stopd=3.0;act=.18;trail=.05;maxhold=60;mode=0
        i=np.searchsorted(t,sig)
        if i>=len(t):
            o[k]=np.nan
            continue
        p=mid[i];entry=p+H if side>0 else p-H;bid=p-H;ask=p+H
        stop=bid-stopd if side>0 else ask+stopd
        ot=t[i];mfe=0.;mae=0.;done=False
        armed=-1;profitable=-1;renew_at=-1;trail_moves=0;renews=0
        last_ren_mfe=0.
        for j in range(i+1,len(t)):
            tt=t[j];p=mid[j];bid=p-H;ask=p+H
            fav=(bid-entry) if side>0 else (entry-ask)
            adv=(entry-bid) if side>0 else (ask-entry)
            if fav>mfe:
                mfe=fav;renew_at=tt
                if mfe>=last_ren_mfe+.02:
                    renews+=1;last_ren_mfe=mfe
            if adv>mae:mae=adv
            if fav>0 and profitable<0:profitable=tt
            stop_hit=(side>0 and bid<=stop) or (side<0 and ask>=stop)
            time_hit=tt-ot>=maxhold*1000
            if stop_hit or time_hit:
                ex=bid if side>0 else ask
                o[k,0]=(ex-entry)*side
                o[k,1]=(tt-ot)/1000.
                o[k,2]=mfe;o[k,3]=mae;o[k,4]=tt;o[k,5]=mode
                a[k,0]=ot
                a[k,1]=2 if (stop_hit and trail_moves>0) else (1 if stop_hit else 3)
                a[k,2]=armed
                a[k,3]=profitable
                a[k,4]=trail_moves
                a[k,5]=renew_at
                a[k,6]=j-i
                a[k,7]=stop
                a[k,8]=fav
                a[k,9]=mfe-fav
                a[k,10]=renews
                a[k,11]=1 if (stop_hit and time_hit) else 0
                done=True
                break
            if fav>=act:
                if armed<0:armed=tt
                cand=bid-trail if side>0 else ask+trail
                if side>0:
                    if cand>stop:
                        stop=cand;trail_moves+=1
                else:
                    if cand<stop:
                        stop=cand;trail_moves+=1
        if not done:o[k]=np.nan
    return o,a


def test():
    # Stop prior to arming, with no ambiguity about the first stop trigger.
    t=np.array([100,200,1000,1500,2000,60100,60500],np.int64)
    mid=np.array([10,9.3,9,10,10.1,10.15,10.2],np.float64)
    X=np.array([[100,1,0,4]],dtype=float)
    o,a=traced_original_replay(t,mid,X)
    assert int(a[0,1])==1 and int(o[0,4])==1000
    assert int(a[0,2])==-1 and a[0,4]==0
    # Weak trail arms on +.40 and ratcheted exit occurs on next tick.
    t=np.array([100,300,500,700,1200,60001],np.int64)
    mid=np.array([10,10.4,10.7,10.55,10.5,10.5],np.float64)
    X=np.array([[100,1,0,1]],dtype=float)
    o,a=traced_original_replay(t,mid,X)
    assert int(a[0,1])==2 and int(a[0,2])==300
    assert int(o[0,4])==700 and a[0,4]>=2
    # No activation and no stop: exit at first quote at/after 60 seconds.
    t=np.array([100,200,65000],np.int64)
    mid=np.array([10,10.02,10.03],np.float64)
    X=np.array([[100,-1,0,1]],dtype=float)
    o,a=traced_original_replay(t,mid,X)
    assert int(a[0,1])==3 and int(o[0,4])==65000
    # Hard stop and timeout same first quote: stop check prevails.
    t=np.array([100,60100],np.int64)
    mid=np.array([10,5],np.float64)
    X=np.array([[100,1,0,4]],dtype=float)
    o,a=traced_original_replay(t,mid,X)
    assert int(a[0,1])==1 and a[0,11]==1
    # Full raw chronological parent selection is strict > previous exit.
    q=N.raw_replay(np.array([100,200,201]),np.array([200,300,400]),
         np.array([1.,2.,3.]),np.ones(3,bool))
    assert q.tolist()==[0,2]
    print('HOLD022_EXIT_REASON_SYNTHETIC_PARITY_PASS')


def attr(mask, pnl, aux, aligned, reason):
    p=pnl[mask]
    return {'trades':int(len(p)),'winners':int((p>0).sum()),
      'net':float(p.sum()),'gross_profit':float(p[p>0].sum()),
      'gross_loss':float(p[p<0].sum()),
      'arm_fraction_pct':float(100*np.mean(aux[mask,2]>=0)) if len(p) else 0.,
      'mean_hold_seconds':float(np.mean(aux[mask,6])) if len(p) else 0.}


def run_january():
    test();st=time.perf_counter()
    manifest=json.loads(PARENT_MANIFEST.read_text())
    assert sha(PARENT_CACHE)==manifest['raw_cache_sha256']
    assert sha(R.RAW_BY_MONTH[1])==manifest['raw_data_sha256']
    with np.load(PARENT_CACHE,allow_pickle=False) as zz:
        entry=zz['raw_entry_ms'].astype(np.int64)
        side=zz['raw_side'].astype(np.int8)
        align=zz['raw_align'].astype(np.int8)
        pnl=zz['raw_pnl'].astype(np.float64)
        exit_ms=zz['raw_exit_ms'].astype(np.int64)
        hold_s=zz['raw_hold_s'].astype(np.float64)
    assert len(entry)==PARENT_GOLDEN['raw']
    assert np.all(np.diff(entry)>=0)
    t,mid=R.load_ticks(1)
    assert len(t)==9135062 and np.all(np.diff(t)>=0)
    X=np.column_stack([entry.astype(float),side.astype(float),np.zeros(len(entry)),align.astype(float)])
    o,a=traced_original_replay(t,mid,X)
    assert np.array_equal(o[:,0],pnl,equal_nan=True),'raw PNL mismatch: not source-equivalent'
    assert np.array_equal(o[:,4].astype(np.int64),exit_ms),'raw exit chronology mismatch'
    assert np.array_equal(o[:,1],hold_s,equal_nan=True),'raw hold time mismatch'
    assert np.isfinite(a[:,1]).all()
    assert np.all(np.isin(a[:,1],[1.,2.,3.]))
    assert np.array_equal(a[:,0],entry) or np.all(a[:,0]>=entry)
    assert np.all(a[:,9]>=-1e-12)
    ix=N.raw_replay(entry,exit_ms,pnl,np.ones(len(entry),bool))
    bm=N.mtr(pnl[ix]);G=PARENT_GOLDEN
    assert bm['trades']==G['trades'] and bm['winners']==G['winners']
    for k in ['net','gross_profit','gross_loss']:
        assert abs(bm[k]-G[k])<1e-8,(k,bm[k],G[k])
    groups=[]
    for population, sel in [('all_raw',np.arange(len(entry))),('selected',ix)]:
        k=np.zeros(len(entry),bool);k[sel]=True
        for owner,owner_ok in [('all',np.ones(len(entry),bool)),('weak',align<3),('strong',align>=3)]:
            for code,name in REASON_NAMES.items():
                m=k&owner_ok&(a[:,1]==int(code));ps=pnl[m]
                dur=hold_s[m]
                groups.append({'population':population,'owner':owner,'reason':name,
                    'trades':int(m.sum()),'winners':int(np.count_nonzero(ps>0)),
                    'net':float(ps.sum()),'gp':float(ps[ps>0].sum()),
                    'gl':float(ps[ps<0].sum()),
                    'mean_hold_s':float(dur.mean()) if len(dur) else 0.,
                    'armed_trades':int(np.count_nonzero(a[m,2]>=0)),
                    'mean_mfe':float(o[m,2].mean()) if len(ps) else 0.,
                    'mean_mae':float(o[m,3].mean()) if len(ps) else 0.})
    selectedreason={name:sum(z['trades'] for z in groups if z['population']=='selected' and z['owner']=='all' and z['reason']==name) for name in REASON_NAMES.values()}
    assert sum(selectedreason.values())==G['trades']
    arrpath=OUT/'HOLD022_JAN_EXIT_REASON_SOURCE_CLOSURE.npz'
    atomic_npz(arrpath,entry_ms=entry,side=side,align=align,
        parent_exit_ms=exit_ms,parent_pnl=pnl,parent_hold_s=hold_s,
        original_o=o,causal_state_at_original_exit=a,
        selected_parent_raw_index=ix,reason_code=a[:,1].astype(np.int8))
    result={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD',
       'stage':'EXIT_REASON_TRAJECTORY_HARVEST_VS_RUNNER_SOURCE_CLOSURE',
       'status':'VERIFIED_LOCAL_SOURCE_CLOSURE',
       'month':1,'parent':'CAUSAL_RECERT_014','august_accessed':False,
       'time_walls':{'jan_source_regression':True,'feb_mar_used':False,'april_accessed':False,'may_jul_accessed':False,'august_accessed':False},
       'execution_model':'Dukascopy midpoint plus modeled fixed $0.10 half-spread per side, original CAUSAL014 check-stop-before-trail rule, original 60s hold, strict one-position replay',
       'all_original_raw_pnl_exact':True,'all_original_raw_exit_ms_exact':True,
       'all_original_raw_hold_s_exact':True,
       'market_tick_count':len(t),'raw_candidates':len(entry),
       'parent_selected':bm,'reason_names':REASON_NAMES,'selected_reason_counts':selectedreason,
       'exit_reason_attribution':groups,
       'historical_entry017_024_relation':'Original ENTRY017-024 diagnostics refer to a separate sweep/opposite requalification population. Their frozen 1/4/4.5s state semantics are not silently projected onto CAUSAL014 raw trades. Source body hashes are separately recorded; no ENTRY model used as a live execution signal.',
       'state_observability':'arm timestamp, pre-exit peak renewal, PNL, stop and reason are causally accumulated but recorded at parent exit; outcome/reason cannot enter earlier online decisions. A future arm-relative event decision must query only actual ticks <= its checkpoint and before original exit.',
       'mechanisms_previously_rejected':['universal early-negative/no-MFE checkpoint cut','standalone original sweep-level re-penetration exit','unignited late-stall checkpoint cut','weak-only 0.10 trail as standalone global rule'],
       'next':'HOLD_EXIT_022_ARMED_TRAJECTORY_JAN_DISCOVERY_PREDECLARATION',
       'source_file':Path(__file__).name,'source_sha256':sha(__file__),
       'raw_event_cache_sha256':sha(PARENT_CACHE),'market_sha256':sha(R.RAW_BY_MONTH[1]),
       'source_closure_npz_sha256':sha(arrpath),
       'elapsed_s':round(time.perf_counter()-st,3)}
    dest=OUT/'HOLD022_JAN_EXIT_REASON_SOURCE_CLOSURE.json'
    atomic_json(dest,result)
    mpath=OUT/'HOLD022_JAN_EXIT_REASON_SOURCE_CLOSURE_MANIFEST.json'
    mm={'stage':result['stage'],'status':result['status'],
      'source_sha256':sha(__file__),'result_sha256':sha(dest),
      'observation_cache_sha256':sha(arrpath),
      'parent_input_cache_sha256':sha(PARENT_CACHE),
      'market_sha256':sha(R.RAW_BY_MONTH[1]),
      'exact_parent_all_raw_pnl_exit_hold_parity':True,
      'jan_parent_selected':{'trades':bm['trades'],'winners':bm['winners'],'net':bm['net']},
      'august_accessed':False}
    atomic_json(mpath,mm)
    print(json.dumps({'status':result['status'],'stage':result['stage'],
      'baseline':bm,'selected_reason_counts':selectedreason,
      'selected_reason_detail':[z for z in groups if z['population']=='selected' and z['owner']=='all'],
      'source_sha256':result['source_sha256'],'result_sha256':sha(dest),
      'observation_cache_sha256':sha(arrpath),
      'manifest_sha256':sha(mpath),
      'elapsed_s':result['elapsed_s'],'next':result['next']},indent=2))

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('only test or jan supported')
    if sys.argv[1]=='test':test()
    elif sys.argv[1]=='jan':run_january()
    else:raise SystemExit('only test or jan supported')
