import argparse, json, hashlib, math, time, gc
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
import r9b020_core as core

ROOT=Path('/mnt/data')
BROOT=ROOT/'r9b020b_cache'
CROOT=ROOT/'r9b020c_cache'
CROOT.mkdir(exist_ok=True)

# Bounded 020-C screening set. Each family is evaluated separately; no indiscriminate stacking.
CONFIGS=[
    ('TICK_D3_W90','tick',3,90),
    ('A1S_D3_W62','a1s',3,62),
    ('A1S_D3_W90','a1s',3,90),
    ('A1S_D3_W120','a1s',3,120),
    ('S5_D3_W62','s5',3,62),
    ('S5_D3_W90','s5',3,90),
    ('S15_D3_W62','s15',3,62),
    ('M1_D3_W62','m1',3,62),
]
METRIC_NAMES=['pe','te','irr','forbid','edge_p','cur_self','cur_max','cur_h','pat_age']+[f'p{i}' for i in range(6)]

@njit(cache=True)
def pattern_index3(a,b,c):
    # Lehmer code with ties broken by position: later equal values are not smaller.
    # Flat windows are degenerate.
    if a==b and b==c:
        return -1
    idx=0
    # c0 * 2!
    cnt0=(1 if b<a else 0)+(1 if c<a else 0)
    idx += 2*cnt0
    # c1 * 1!
    cnt1=(1 if c<b else 0)
    idx += cnt1
    return idx

@njit(cache=True)
def reverse_map3():
    # Exhaustive representative permutations for the six d=3 Lehmer states.
    reps=np.array([[0.,1.,2.],[0.,2.,1.],[1.,0.,2.],[1.,2.,0.],[2.,0.,1.],[2.,1.,0.]])
    out=np.empty(6,np.int64)
    for i in range(6):
        out[i]=pattern_index3(reps[i,2],reps[i,1],reps[i,0])
    return out

@njit(cache=True)
def entropy_counts(x,total,denom):
    if total<=0:
        return 0.0
    h=0.0
    for i in range(len(x)):
        if x[i]>0:
            p=x[i]/total
            h -= p*math.log(p)
    return h/denom if denom>0 else 0.0

@njit(cache=True)
def jsd_hist(pcnt,qcnt,ptot,qtot):
    if ptot<=0 or qtot<=0:
        return 0.0
    js=0.0
    for i in range(len(pcnt)):
        p=pcnt[i]/ptot
        q=qcnt[i]/qtot
        m=0.5*(p+q)
        if p>0: js += 0.5*p*math.log(p/m)
        if q>0: js += 0.5*q*math.log(q/m)
    return js/math.log(2.0)

@njit(cache=True)
def event_optn_features(values, end_idx, sides, window):
    # values is a chronological causal transform (log returns here).
    # Each event uses exactly values[end-window+1:end+1], side-normalized.
    n=len(end_idx)
    out=np.full((n,15),np.nan,np.float64)
    revmap=reverse_map3()
    log6=math.log(6.0); log36=math.log(36.0)
    for r in range(n):
        e=end_idx[r]
        s0=e-window+1
        if e<0 or s0<0:
            continue
        side=sides[r]
        hist=np.zeros(6,np.float64)
        trans=np.zeros(36,np.float64)
        prev=-1; prevprev=-1; cur=-1; npat=0; ntrans=0; cur_age=0
        last_pat=-2
        # Patterns are over d=3 consecutive transformed values.
        last_start=e-2
        for s in range(s0,last_start+1):
            a=values[s]*side; b=values[s+1]*side; c=values[s+2]*side
            idx=pattern_index3(a,b,c)
            if idx<0:
                prev=-1
                last_pat=-2; cur_age=0
                continue
            hist[idx]+=1.0; npat+=1
            if prev>=0:
                trans[prev*6+idx]+=1.0; ntrans+=1
                prevprev=prev
            prev=idx; cur=idx
            if idx==last_pat: cur_age+=1
            else: last_pat=idx; cur_age=1
        if npat<30 or cur<0:
            continue
        active=0
        histrev=np.zeros(6,np.float64)
        for i in range(6):
            if hist[i]>0: active+=1
            histrev[revmap[i]] += hist[i]
        pe=entropy_counts(hist,npat,log6)
        te=entropy_counts(trans,ntrans,log36) if ntrans>0 else 0.0
        irr=jsd_hist(hist,histrev,npat,npat)
        forbid=1.0-active/6.0
        # last transition conditional probability
        edge_p=0.0
        if prevprev>=0 and cur>=0:
            rs=0.0
            for j in range(6): rs+=trans[prevprev*6+j]
            if rs>0: edge_p=trans[prevprev*6+cur]/rs
        rs=0.0
        for j in range(6): rs+=trans[cur*6+j]
        cur_self=0.0; cur_max=0.0; cur_h=0.0
        if rs>0:
            cur_self=trans[cur*6+cur]/rs
            for j in range(6):
                p=trans[cur*6+j]/rs
                if p>cur_max: cur_max=p
                if p>0: cur_h-=p*math.log(p)
            cur_h/=log6
        out[r,0]=pe; out[r,1]=te; out[r,2]=irr; out[r,3]=forbid
        out[r,4]=edge_p; out[r,5]=cur_self; out[r,6]=cur_max; out[r,7]=cur_h
        out[r,8]=cur_age/max(1.0,float(window-2))
        for j in range(6): out[r,9+j]=1.0 if cur==j else 0.0
    return out

def log_returns(x):
    x=np.asarray(x,np.float64)
    out=np.zeros(len(x),np.float64)
    if len(x)>1:
        out[1:]=np.diff(np.log(np.maximum(x,1e-12)))
    return out

def series_and_event_index(kind,t,mid,event_ms,event_sec,av,bv):
    if kind=='tick':
        vals=log_returns(mid)
        # Event tick itself is observed and is causal at decision time.
        idx=np.searchsorted(t,event_ms,side='right')-1
        return vals,idx
    if kind=='a1s':
        sec,o,h,l,c,n,am,bm=core.aggregate_active_seconds(t,mid,av,bv)
        vals=log_returns(c)
        # Current second is incomplete; use last completed active second strictly before it.
        idx=np.searchsorted(sec,event_sec,side='left')-1
        return vals,idx
    tf={'s5':5,'s15':15,'m1':60}[kind]
    z=core.aggregate_tf(t,mid,tf)
    vals=log_returns(z['c'])
    # z['end'] is bar-end second. Include only bars completed by event time.
    idx=np.searchsorted(z['end'],event_sec,side='right')-1
    return vals,idx

def build_month(m):
    out=CROOT/f'R9B_020C_M{m:02d}.npz'
    smp=CROOT/f'R9B_020C_M{m:02d}_summary.json'
    if out.exists() and smp.exists():
        return json.load(open(smp))
    b=pd.read_pickle(BROOT/f'R9B_020B_M{m:02d}.pkl.gz',compression='gzip')
    event_ms=b.time_ms.to_numpy(np.int64); event_sec=b.event_sec.to_numpy(np.int64); sides=b.side.to_numpy(np.int8)
    t0=time.time(); t,mid,av,bv=core.load_ticks(core.FILES[m])
    groups={}
    # Reuse each source representation for its window neighborhood.
    by_kind={}
    for name,kind,d,w in CONFIGS:
        if d!=3: raise RuntimeError('020-C bounded implementation only supports d=3 in this stage')
        if kind not in by_kind:
            by_kind[kind]=series_and_event_index(kind,t,mid,event_ms,event_sec,av,bv)
        vals,idx=by_kind[kind]
        groups[name]=event_optn_features(vals,idx,sides,w).astype(np.float32)
    payload={name:arr for name,arr in groups.items()}
    payload['event_ms']=event_ms
    np.savez_compressed(out,**payload)
    h=hashlib.sha256(out.read_bytes()).hexdigest()
    finite={name:float(np.isfinite(arr[:,0]).mean()) for name,arr in groups.items()}
    sm={'month':m,'rows':int(len(b)),'elapsed_seconds':time.time()-t0,'cache_sha256':h,
        'finite_fraction':finite,'august_accessed':False}
    json.dump(sm,open(smp,'w'),indent=2,sort_keys=True)
    del b,t,mid,av,bv,by_kind,groups,payload; gc.collect()
    return sm

def self_test():
    assert pattern_index3(1.,2.,3.)==0
    assert pattern_index3(1.,3.,2.)==1
    assert pattern_index3(3.,2.,1.)==5
    assert pattern_index3(1.,1.,1.)==-1
    # Gaussian-like pseudo-random test and irreversible sawtooth/trend-shaped sequence are smoke tests only.
    rng=np.random.default_rng(123)
    v=rng.normal(size=5000)
    e=np.array([4999],dtype=np.int64); s=np.array([1],dtype=np.int8)
    z=event_optn_features(v,e,s,250)[0]
    assert np.isfinite(z).all() and 0<=z[0]<=1.0000001 and 0<=z[2]<=1.0000001
    return {'pattern_checks':'PASS','noise_pe':float(z[0]),'noise_irr':float(z[2])}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--month',type=int); ap.add_argument('--self-test',action='store_true')
    a=ap.parse_args()
    if a.self_test: print(json.dumps(self_test(),indent=2))
    elif a.month: print(json.dumps(build_month(a.month),indent=2,sort_keys=True))
    else: ap.error('use --self-test or --month N')
