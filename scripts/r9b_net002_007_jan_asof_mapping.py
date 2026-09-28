"""Non-promotional NET002-007/CAUSAL014 January source-to-event archaeology.

Exact-source-sensitive CAUSAL014 core is reconstructed in-line from:
  scripts/causal014/r9b_screen.py (blob 9cfc940c0aea3329d1f3775e34a4110c69254aa4)
  scripts/causal014/r9b_r8_recert.py (blob c720e6aaf65586beb1e263715592609634029258)
  scripts/causal014/r8_sweep_lifecycle_screen.py (blob 411542bd842d31089142ac8a6016af6a2117e663)
  scripts/causal014/r9b_sweep_structure_exit_candidate.py (blob e171190bc209890908f2e593e2909a0220d55f6f)
NET002/003/004/005/006/007 identities are frozen by the prior predeclaration.
No production trades, strategy selection, August data, or fitted thresholds here.

Important: the CAUSAL014 main runner uses R.build_sec, sweep_signals and
replay_hybrid, but does not use the R.build_s1_quality fields. This script
computes ONLY those exact-source inputs the selected path consumes.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib, json, time
import numpy as np
import pandas as pd
from numba import njit

DATA=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
OUT=Path('/mnt/data/r9b_research')
EXPECTED_SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
H=.10
LIQ_LOOKBACK=20;VEL_LOOKBACK=5;PERSISTENCE_SEC=2;EXPIRY_SEC=20
BREAK_BUFFER=.10;RECLAIM=.15;CONFIRM=.08;MIN_VELOCITY=.15;MIN_EFF=.30;MAX_PER_MIN=5

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def raw():
    d=pd.read_csv(DATA,compression='gzip', usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
                  dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
    t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False)
    ask=d.ask_raw.to_numpy(np.float64,copy=False)/1000.0
    bid=d.bid_raw.to_numpy(np.float64,copy=False)/1000.0
    mid=(ask+bid)*0.5    # IMPORTANT source math order; NOT (ask_raw+bid_raw)/2000
    assert len(t)==9135062,(len(t),'unexpected tick rows')
    assert np.all(t[1:]>=t[:-1]),'Chronology violation'
    return t,mid

def active_seconds(t,price):
    sec=t//1000
    ch=np.empty(len(sec),dtype=bool)
    ch[0]=True
    ch[1:]=sec[1:]!=sec[:-1]
    ix=np.flatnonzero(ch)
    last=np.r_[ix[1:]-1,len(sec)-1]
    return (sec[ix].astype(np.int64),t[ix].astype(np.int64),
            price[ix].astype(np.float64),np.maximum.reduceat(price,ix).astype(np.float64),
            np.minimum.reduceat(price,ix).astype(np.float64),
            price[last].astype(np.float64),ix.astype(np.int64),last.astype(np.int64))

def aggregate_tf_from_ticks(t,mid,tf_sec):
    bucket=t//(int(tf_sec)*1000)
    ch=np.empty(len(bucket),dtype=bool)
    ch[0]=True
    ch[1:]=bucket[1:]!=bucket[:-1]
    ix=np.flatnonzero(ch);last=np.r_[ix[1:]-1,len(bucket)-1];ids=bucket[ix]
    c=mid[last];h=np.maximum.reduceat(mid,ix);l=np.minimum.reduceat(mid,ix)
    end=(ids+1)*int(tf_sec);prev=np.r_[np.nan,c[:-1]]
    tr=np.maximum(h-l,np.maximum(np.abs(h-prev),np.abs(l-prev)))
    atr=np.full(len(tr),np.nan,dtype=np.float64);e=np.nan
    for i,x in enumerate(tr):
        if not np.isfinite(x):continue
        e=x if not np.isfinite(e) else (13.0/14.0)*e+(1.0/14.0)*x
        if i>=13:atr[i]=e
    ret=np.r_[np.nan,np.diff(c)]
    return end.astype(np.int64),ret.astype(np.float64),atr

def map_completed(sec_ids,end,values):
    j=np.searchsorted(end,sec_ids,side='right')-1
    out=np.full(len(sec_ids),np.nan,dtype=np.float64)
    ok=j>=0
    out[ok]=values[j[ok]]
    return out

def build_features(t,mid):
    sec_ids,*_=active_seconds(t,mid)
    e5,r5,a5=aggregate_tf_from_ticks(t,mid,300)
    atrsec=map_completed(sec_ids,e5,a5)
    align_long=np.zeros(len(sec_ids),dtype=np.int8)
    align_short=np.zeros(len(sec_ids),dtype=np.int8)
    for tf in (60,180,300,600,1200):
        end,ret,atr=aggregate_tf_from_ticks(t,mid,tf)
        rr=map_completed(sec_ids,end,ret);aa=map_completed(sec_ids,end,atr)
        ok=np.isfinite(aa)
        align_long+=((rr>0)&ok).astype(np.int8)
        align_short+=((rr<0)&ok).astype(np.int8)
    return sec_ids,atrsec,align_long,align_short

def build_sec(t,mid,half_spread=H):
    t=np.asarray(t,dtype=np.int64);mid=np.asarray(mid,dtype=np.float64)
    bid=mid-float(half_spread);sec=t//1000
    ch=np.empty(len(sec),dtype=bool);ch[0]=True;ch[1:]=sec[1:]!=sec[:-1]
    ix=np.flatnonzero(ch);last=np.r_[ix[1:]-1,len(sec)-1]
    su=sec[ix].astype(np.int64)
    hi=np.maximum.reduceat(bid,ix).astype(np.float64)
    lo=np.minimum.reduceat(bid,ix).astype(np.float64)
    cl=bid[last].astype(np.float64)
    return su,hi,lo,cl

@njit(cache=True)
def _session_floor(sec):
    lon_off=60 if (sec>=1774746000 and sec<1792890000) else 0
    ny_off=-240 if (sec>=1772953200 and sec<1793512800) else -300
    lm=((sec+lon_off*60)%86400)//60; nm=((sec+ny_off*60)%86400)//60
    london=lm>=480 and lm<990; ny=nm>=480 and nm<1020
    if london and ny:return 1.75
    if london:return 2.0
    if ny:return 1.75
    return 2.5

@njit(cache=True)
def _causal_core(t,mid,su,hi,lo,cl,sec_ids,atrsec,al,ash):
    cap=max(10000,min(300000,len(t)//20+1));X=np.empty((cap,4),np.float64);n=0
    state=0;level=0.;started=0;minute=-1;trades=0;cool=-1;j=0;k=0;lastsec=-1
    for i in range(len(t)):
        sec=t[i]//1000
        if sec!=lastsec:
            while j+1<len(sec_ids) and sec_ids[j+1]<=sec:j+=1
            while k+1<len(su) and su[k+1]<=sec:k+=1
            lastsec=sec
        if j>=len(sec_ids) or sec_ids[j]!=sec or k>=len(su) or su[k]!=sec:continue
        mn=sec//60
        if mn!=minute:minute=mn;trades=0;state=0;level=0.;started=0
        if sec<cool or trades>=MAX_PER_MIN or k<LIQ_LOOKBACK or j<VEL_LOOKBACK:continue
        av=atrsec[j]
        if not np.isfinite(av) or av+1e-12<_session_floor(sec):continue
        newest=k-1;oldest=newest-(LIQ_LOOKBACK-1);upper=-1e18;lower=1e18
        for q in range(oldest,newest+1):
            if hi[q]>upper:upper=hi[q]
            if lo[q]<lower:lower=lo[q]
        bid=mid[i]-H;ask=mid[i]+H
        oldestv=k-VEL_LOOKBACK;prev=cl[oldestv];start=prev;travel=0.
        for q in range(oldestv+1,k):
            v=cl[q];travel+=abs(v-prev);prev=v
        travel+=abs(bid-prev);disp=bid-start;eff=abs(disp)/(travel+1e-9)
        if state==0:
            if ask>=upper+BREAK_BUFFER:state=1;level=upper;started=sec
            elif bid<=lower-BREAK_BUFFER:state=-1;level=lower;started=sec
        if state==1:
            if ask<=level-RECLAIM:state=2;started=sec
            elif sec-started>=PERSISTENCE_SEC and ask>=level+CONFIRM and disp>=MIN_VELOCITY and eff>=MIN_EFF:
                state=0;level=0.;started=0;trades+=1;cool=sec+1
        elif state==-1:
            if bid>=level+RECLAIM:state=-2;started=sec
            elif sec-started>=PERSISTENCE_SEC and bid<=level-CONFIRM and disp<=-MIN_VELOCITY and eff>=MIN_EFF:
                state=0;level=0.;started=0;trades+=1;cool=sec+1
        elif state==2:
            if disp<=-MIN_VELOCITY and eff>=MIN_EFF:
                if n>=cap:break
                X[n,0]=t[i];X[n,1]=-1;X[n,2]=level;X[n,3]=ash[j];n+=1
                trades+=1;cool=sec+1;state=0;level=0.;started=0
        elif state==-2:
            if disp>=MIN_VELOCITY and eff>=MIN_EFF:
                if n>=cap:break
                X[n,0]=t[i];X[n,1]=1;X[n,2]=level;X[n,3]=al[j];n+=1
                trades+=1;cool=sec+1;state=0;level=0.;started=0
        if state!=0 and started>0 and sec-started>EXPIRY_SEC:state=0;level=0.;started=0
    return X[:n]

@njit(cache=True)
def replay_hybrid(t,mid,X):
    n=len(X);o=np.empty((n,6),np.float64)
    for k in range(n):
        sig=int(X[k,0]);side=int(X[k,1]);align=X[k,3]
        if align>=3:
            stopd=1.0;act=.10;trail=.04;maxhold=60;mode=1
        else:
            stopd=3.0;act=.18;trail=.05;maxhold=60;mode=0
        i=np.searchsorted(t,sig)
        if i>=len(t):o[k]=np.nan;continue
        p=mid[i];entry=p+H if side>0 else p-H;bid=p-H;ask=p+H
        stop=bid-stopd if side>0 else ask+stopd;ot=t[i];mfe=0.;mae=0.;done=False
        for j in range(i+1,len(t)):
            tt=t[j];p=mid[j];bid=p-H;ask=p+H
            fav=(bid-entry) if side>0 else (entry-ask);adv=(entry-bid) if side>0 else (ask-entry)
            if fav>mfe:mfe=fav
            if adv>mae:mae=adv
            if (side>0 and bid<=stop) or (side<0 and ask>=stop) or tt-ot>=maxhold*1000:
                ex=bid if side>0 else ask
                o[k,0]=(ex-entry)*side;o[k,1]=(tt-ot)/1000.;o[k,2]=mfe;o[k,3]=mae;o[k,4]=tt;o[k,5]=mode;done=True;break
            if fav>=act:
                cand=bid-trail if side>0 else ask+trail
                if side>0:
                    if cand>stop:stop=cand
                else:
                    if cand<stop:stop=cand
        if not done:o[k]=np.nan
    return o

@njit(cache=True)
def nonoverlap(X,O):
    ix=np.argsort(X[:,0]);keep=np.empty(len(ix),np.int64);n=0;free=-1
    for q in ix:
        if X[q,0]<=free or not np.isfinite(O[q,0]):continue
        keep[n]=q;n+=1;free=int(O[q,4])
    return keep[:n]

def metrics(v):
    v=np.asarray(v,float);gp=float(v[v>0].sum());gl=float(v[v<0].sum())
    eq=np.cumsum(v);pk=np.maximum.accumulate(np.r_[0.,eq])[:-1] if len(v) else np.array([])
    return {'trades':len(v),'winners':int((v>0).sum()),'net':float(v.sum()),'gross_profit':gp,
            'gross_loss':gl,'profit_factor':gp/-gl if gl<0 else None,
            'max_drawdown':float((pk-eq).max()) if len(v) else 0}

def structural_bars(t,mid,tf_min):
    ms=tf_min*60000;k=t//ms;st=np.r_[0,np.where(k[1:]!=k[:-1])[0]+1];en=np.r_[st[1:]-1,len(k)-1]
    o=mid[st];h=np.maximum.reduceat(mid,st);l=np.minimum.reduceat(mid,st);c=mid[en]
    end=(k[st]+1)*ms
    rng=h-l;bf=np.divide(np.abs(c-o),rng,out=np.zeros(len(c)),where=rng>0)
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.r_[o[0],c[:-1]]),np.abs(l-np.r_[o[0],c[:-1]])))
    atr=np.full(len(c),np.nan)
    for i in range(3,len(c)):atr[i]=np.mean(tr[max(0,i-13):i+1])
    return dict(o=o,h=h,l=l,c=c,end=end,atr=atr,bf=bf)

def h1_bos(h,lookback=13,buffer=.10):
    """NET003 h1_bos operation order, no occupancy suppression."""
    o,hi,lo,c,atr,end=[h[k] for k in ('o','h','l','c','atr','end')]
    events=[]
    for i in range(max(lookback,14),len(c)):
        if not np.isfinite(atr[i]) or atr[i]<=0:continue
        top=np.maximum(o[i-lookback:i],c[i-lookback:i]);bot=np.minimum(o[i-lookback:i],c[i-lookback:i])
        up=float(np.max(top));dn=float(np.min(bot))
        if c[i]>up+buffer*atr[i] and c[i]>o[i]:events.append((int(end[i]),1,up,float(atr[i]),int(i)))
        elif c[i]<dn-buffer*atr[i] and c[i]<o[i]:events.append((int(end[i]),-1,dn,float(atr[i]),int(i)))
    return events

def h4_ownership(h,lookback=13,buffer=.10):
    """NET006 h4_state logic; n=13/buf=0.10 are SOURCE GRID profile, not promoted gating."""
    o,hi,lo,c,atr,end=[h[k] for k in ('o','h','l','c','atr','end')]
    owner=np.zeros(len(c),np.int8);age=np.full(len(c),999,np.int16);cur=0;a=999
    for i in range(len(c)):
        if i>=max(lookback,14) and np.isfinite(atr[i]) and atr[i]>0:
            top=np.maximum(o[i-lookback:i],c[i-lookback:i]);bot=np.minimum(o[i-lookback:i],c[i-lookback:i]);up=np.max(top);dn=np.min(bot)
            bos=1 if c[i]>up+buffer*atr[i] and c[i]>o[i] else (-1 if c[i]<dn-buffer*atr[i] and c[i]<o[i] else 0)
            if bos and bos!=cur:cur=bos;a=0
            elif bos and bos==cur:a=0
            elif cur:a=min(999,a+1)
        owner[i]=cur;age[i]=a
    net3=np.zeros(len(c),np.int8);body=np.sign(c-o).astype(np.int8)
    for i in range(3,len(c)):
        v=c[i]-c[i-3];net3[i]=1 if v>0 else (-1 if v<0 else 0)
    return dict(end=end,owner=owner,age=age,net3=net3,body=body)

def children(h1,m15):
    """Frozen NET003 screen contract as forensic candidate context, NET007 depth=0.05 ATR descriptive marker.
    First completed eligible child for EACH H1 BOS, as source (not one per selected CAUSAL014 trade).
    """
    mend=m15['end'];o=m15['o'];hh=m15['h'];ll=m15['l'];c=m15['c']
    retests=[];failures=[]
    WAIT=720;TOUCH=.20;PEN=.05;RECLAIM=.20;BODY=True;FAIL_DEPTH=.05
    for i,(e,side,bound,atr,bar_idx) in enumerate(h1):
        lo=np.searchsorted(mend,int(e)+1,side='left')
        hi=np.searchsorted(mend,int(e)+WAIT*60000,side='right')
        rr=None;ff=None
        for j in range(lo,min(hi,len(mend))):
            if rr is None:
                if side>0:ok=(ll[j]<=bound+TOUCH*atr) and (ll[j]>=bound-PEN*atr) and (c[j]>=bound+RECLAIM*atr) and ((not BODY) or c[j]>o[j])
                else:ok=(hh[j]>=bound-TOUCH*atr) and (hh[j]<=bound+PEN*atr) and (c[j]<=bound-RECLAIM*atr) and ((not BODY) or c[j]<o[j])
                if ok:rr=(int(mend[j]),int(i),int(side),int(j))
            if ff is None:
                ok=(c[j]<=bound-FAIL_DEPTH*atr) if side>0 else (c[j]>=bound+FAIL_DEPTH*atr)
                if ok:ff=(int(mend[j]),int(i),int(-side),int(j))
            if rr is not None and ff is not None:break
        if rr is not None:retests.append(rr)
        if ff is not None:failures.append(ff)
    return retests,failures

def attach_asof(times,events):
    """As-of join to latest *completed* event only, no future fill, strict lead time asserted."""
    if not events:return np.full(len(times),-1,np.int32),np.zeros(len(times),np.int64)
    evtime=np.array([row[0] for row in events],dtype=np.int64)
    assert np.all(evtime[1:]>=evtime[:-1]),'structural stream must be ordered'
    j=np.searchsorted(evtime,times,side='right')-1
    age=np.zeros(len(times),dtype=np.int64);yes=j>=0;age[yes]=times[yes]-evtime[j[yes]]
    assert not np.any(age[yes]<0),'FUTURE FEATURE LEAK'
    return j.astype(np.int32),age

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    st=time.monotonic();inputsha=digest(DATA)
    assert inputsha==EXPECTED_SHA,(inputsha,EXPECTED_SHA)
    print('SOURCE_SHA_PASS',inputsha,flush=True)
    t,mid=raw();print('RAW_TICKS',len(t),flush=True)
    sec,atr,al,ash=build_features(t,mid);print('SECOND_FEATURES',len(sec),flush=True)
    su,hi,lo,cl=build_sec(t,mid)
    X=_causal_core(t,mid,su,hi,lo,cl,sec,atr,al,ash)
    print('CAUSAL_RAW_EVENTS',len(X),flush=True)
    assert len(X)==34362,('CAUSAL014 RAW parity failed',len(X))
    O=replay_hybrid(t,mid,X);ix=nonoverlap(X,O)
    m=metrics(O[ix,0]);print('CAUSAL_SELECTED',m,flush=True)
    assert m['trades']==28088 and m['winners']==19087 and abs(m['net']-(-4510.0870000207515))<1e-7,'CAUSAL014 selected parity failed'
    assert all(np.isfinite(O[ix,0]))
    assert np.all(X[ix[1:],0]>O[ix[:-1],4]),'strict one-position chronology broken'
    # Causal original ledger is frozen here. The rest of the code may annotate it ONLY.
    raw_times=X[:,0].astype(np.int64);sides=X[:,1].astype(np.int8)
    h1=structural_bars(t,mid,60);h4=structural_bars(t,mid,240);m15=structural_bars(t,mid,15)
    bos=h1_bos(h1);own=h4_ownership(h4)
    rr,ff=children(bos,m15)
    # NET003/007 children can share timestamp and tie with different H1 owners; explicit sorted IDs.
    rr.sort(key=lambda e:(e[0],e[1]));ff.sort(key=lambda e:(e[0],e[1]))
    bosi,bosage=attach_asof(raw_times,bos)
    rri,rrage=attach_asof(raw_times,rr)
    ffi,ffage=attach_asof(raw_times,ff)
    # A child is valid only while its own originating H1 BOS is STILL the
    # latest completed BOS. An as-of join on child timestamp alone is unsafe.
    rr_parent=np.full(len(X),-1,dtype=np.int32)
    ff_parent=np.full(len(X),-1,dtype=np.int32)
    rr_has=rri>=0;ff_has=ffi>=0
    if np.any(rr_has):rr_parent[rr_has]=np.asarray(rr,dtype=np.int64)[rri[rr_has],1]
    if np.any(ff_has):ff_parent[ff_has]=np.asarray(ff,dtype=np.int64)[ffi[ff_has],1]
    wrong_rr=(rri>=0)&(rr_parent!=bosi)
    wrong_ff=(ffi>=0)&(ff_parent!=bosi)
    invalid_child_owner_rr=int(wrong_rr.sum());invalid_child_owner_ff=int(wrong_ff.sum())
    rri[wrong_rr]=-1;rrage[wrong_rr]=0
    ffi[wrong_ff]=-1;ffage[wrong_ff]=0
    h4i=np.searchsorted(own['end'],raw_times,side='right')-1
    ok4=h4i>=0; ownside=np.zeros(len(X),dtype=np.int8);ownage=np.full(len(X),999,dtype=np.int16)
    ownside[ok4]=own['owner'][h4i[ok4]];ownage[ok4]=own['age'][h4i[ok4]]
    assert np.all(own['end'][h4i[ok4]]<=raw_times[ok4])
    # Explicit fields: historical signals with independent provenance DO NOT become CAUSAL014 trades.
    bside=np.zeros(len(X),dtype=np.int8);present=bosi>=0
    bside[present]=np.array([bos[j][1] for j in bosi[present]],dtype=np.int8)
    # When an event family has no as-of state, use original -1; do not backfill a future owner.
    for a,items in ((bosi,bos),(rri,rr),(ffi,ff)):
        valid=a>=0
        if np.any(valid):
            tt=np.fromiter((items[j][0] for j in a[valid]),count=int(valid.sum()),dtype=np.int64)
            assert np.all(tt<=raw_times[valid])
    assert len(X)==34362 and len(ix)==28088
    par={
        'source_sha256':inputsha,'tick_rows':int(len(t)),'raw_events':int(len(X)),
        'raw_valid_exit_count':int(np.isfinite(O[:,0]).sum()),
        'baseline_selected_metrics':m,'raw_unique_time_count':int(np.unique(raw_times).size),
        'h1_bos_all':len(bos),'h4_completed_bars':int(len(own['end'])),
        'h4_non_neutral_completed_bars':int(np.sum(own['owner']!=0)),
        'm15_retest_children':len(rr),'m15_failure_children':len(ff),
        'raw_h1_context_count':int(np.sum(present)),
        'raw_h1_context_owner_agreement':int(np.sum(present & (bside==sides))),
        'raw_h1_owner_age_le_12h':int(np.sum(present & (bosage<=12*3600000))),
        'selected_h1_bos_context_count':int(np.sum(present[ix])),
        'selected_h1_direction_agreement':int(np.sum(present[ix] & (bside[ix]==sides[ix]))),
        'raw_h4_completed_state_count':int(np.sum(ok4)),
        'raw_h4_non_neutral_owner_count':int(np.sum(ownside!=0)),
        'raw_h4_owner_agreement':int(np.sum((ownside!=0)&(ownside==sides))),
        'raw_retest_child_context_count':int(np.sum(rri>=0)),
        'raw_retest_wrong_h1_owner_blocked':invalid_child_owner_rr,
        'raw_failure_wrong_h1_owner_blocked':invalid_child_owner_ff,
        'raw_failure_child_context_count':int(np.sum(ffi>=0)),
        'raw_never_seen_h1_bos':int(np.sum(bosi<0)),
        'raw_h4_neutral_or_missing':int(np.sum(ownside==0)),
        'raw_no_retest_yet':int(np.sum(rri<0)),
        'selected_retest_child_context_count':int(np.sum(rri[ix]>=0)),
        'selected_failure_child_context_count':int(np.sum(ffi[ix]>=0)),
        'raw_no_failure_yet':int(np.sum(ffi<0)),
        'future_visibility_violations':0,
        'child_origin_mismatch_in_retained_context':0,
        'structural_source_profiles':{'H1_BOS':'13 completed H1 body extrema, 0.10 current completed H1 ATR',
            'H4_OWNER':'NET006 source grid point N=13 BUF=0.10, persistent owner/age; context-only',
            'M15_RETEST':'NET003 source frozen historical forward candidate wait=720min touch=0.20 ATR penetration=0.05 ATR reclaim=0.20 ATR body required; excluded from trading',
            'M15_FAILURE':'NET007 source parameter grid point depth=0.05 ATR no additional candle-body check; descriptive only'},
        'impact':'ZERO_DELTA_ANNOTATION_ONLY','august_accessed':False,'production_mql5_authorized':False,
        'elapsed_s':round(time.monotonic()-st,3)
    }
    outp=OUT/'R9B_GAMMA_NET002_007_JAN_EVENT_MAPPING_SUMMARY.json'
    npzp=OUT/'R9B_GAMMA_NET002_007_JAN_EVENT_MAPPING_AUDIT.npz'
    np.savez_compressed(npzp,raw_events=X,raw_exit=O,selected_raw_indices=ix,
                        h1_owner_bos_asof_index=bosi,h1_owner_age_ms=bosage,h1_owner_side=bside,
                        h4_completed_bar_index=h4i,h4_owner_side=ownside,h4_owner_age_completed_bars=ownage,
                        retest_child_asof_index=rri,retest_child_age_ms=rrage,
                        failed_child_asof_index=ffi,failed_child_age_ms=ffage,
                        h1_events=np.array(bos,dtype=np.float64).reshape(-1,5),
                        retest_children=np.array(rr,dtype=np.int64).reshape(-1,4),
                        failed_children=np.array(ff,dtype=np.int64).reshape(-1,4),
                        h4_bar_end_ms=own['end'],h4_bar_owner=own['owner'],h4_bar_age=own['age'])
    par['audit_file_sha256']=digest(npzp)
    par['audit_file_bytes']=npzp.stat().st_size
    outp.write_text(json.dumps(par,indent=2)+'\n')
    manifest={'unit':'NET002_NET007_JAN_EVENT_VISIBILITY_AND_ZERO_DELTA_IDENTITY_MAPPING',
              'status':'COMPLETED_LOCAL_PARITY_VERIFIED',
              'input_sha256':inputsha,'source_sha256':digest(__file__),
              'parent_raw':34362,'parent_selected':28088,
              'result_sha256':digest(outp),'audit_sha256':digest(npzp),
              'source_code_location':str(Path(__file__).resolve()),
              'result_location':str(outp),'audit_location':str(npzp),
              'next':'NET002_NET007_JAN_MAPPING_SOURCE_PARITY_AND_EVENTS_AUDIT',
              'august_sealed':True,'production_mql5_authorized':False,
              'completed_utc':datetime.now(timezone.utc).isoformat()}
    mp=OUT/'R9B_GAMMA_NET002_007_JAN_EVENT_MAPPING_MANIFEST.json'
    mp.write_text(json.dumps(manifest,indent=2)+'\n')
    print('STAGE_COMPLETE',json.dumps({'summary':par,'manifest_sha':digest(mp)},default=str),flush=True)

if __name__=='__main__':run()
