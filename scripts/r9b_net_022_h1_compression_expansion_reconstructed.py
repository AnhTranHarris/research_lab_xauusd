"""R9B NET022 H1 compression-expansion owner — parity-certified reconstruction.

Reconstructed 2026-09-28 from the durable frozen NET022 parameter contract and
Drive-recovered NET002 H1/H4 BOS parent. This is not claimed to be the
byte-identical lost original. It is a source-equivalent reconstruction that
reproduces every recorded Jan-Jul 2026 NET022 monthly fingerprint exactly.

Execution/observability contract:
- XAUUSD Dukascopy millisecond bid/ask CSV.GZ only.
- Completed H1 bars only; no partial/future bar state.
- Body-boundary accepted BOS across prior 13 completed H1 bars.
- ATR buffer 0.10 using the parent's 14-TR simple rolling mean semantics.
- Compression: mean range(prior 2) / median range(prior 13) <= 1.0.
- Expansion: current signal range / median range(prior 13) >= 1.0.
- Signal body/range >= 0.25.
- Enter at first actual quote at/after signal-bar close; long Ask, short Bid.
- Exit at first actual quote at/after +8 completed H1 hours; long Bid, short Ask.
- One position within this sleeve; signal time <= prior exit is blocked.
"""
from __future__ import annotations
import glob, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

TARGET = {
    1:(17,12,237.675,3.4331), 2:(19,9,99.301,1.3341),
    3:(14,7,160.296,1.5011), 4:(18,11,274.255,2.9176),
    5:(19,8,5.965,1.02287), 6:(17,10,175.842,1.8968),
    7:(21,9,88.95,1.48227),
}

def raw_path(month:int)->Path:
    return Path(sorted(glob.glob(f'/mnt/data/XAUUSD_DUKAS_2026_{month:02d}_ticks*.gz'))[0])

def metric(pnl):
    x=np.asarray(pnl,float); x=x[np.isfinite(x)]
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return dict(trades=int(len(x)), winners=int((x>0).sum()), net=float(x.sum()),
                gross_profit=gp, gross_loss=gl,
                pf=float(gp/-gl) if gl<0 else None)

def aggregate_h1(t,mid):
    ms=3_600_000; key=t//ms
    st=np.r_[0,np.where(key[1:]!=key[:-1])[0]+1]; en=np.r_[st[1:]-1,len(key)-1]
    return key[st], mid[st], np.maximum.reduceat(mid,st), np.minimum.reduceat(mid,st), mid[en]

def reconstruct(month:int):
    d=pd.read_csv(raw_path(month),usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
                  dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})
    t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False)
    ask=d.ask_raw.to_numpy(np.float64,copy=False)/1000.0
    bid=d.bid_raw.to_numpy(np.float64,copy=False)/1000.0
    mid=(ask+bid)*0.5
    key,o,h,l,c=aggregate_h1(t,mid); n=len(key)
    rng=h-l; body=np.abs(c-o); bf=np.divide(body,rng,out=np.zeros(n),where=rng>0)
    prevc=np.r_[o[0],c[:-1]]
    tr=np.maximum(h-l,np.maximum(np.abs(h-prevc),np.abs(l-prevc)))
    atr=np.full(n,np.nan)
    for i in range(3,n): atr[i]=np.mean(tr[max(0,i-13):i+1])
    end=(key+1)*3_600_000
    rows=[]; free=-1
    for i in range(14,n):
        if int(end[i])<=free or not np.isfinite(atr[i]): continue
        top=np.maximum(o[i-13:i],c[i-13:i]); bot=np.minimum(o[i-13:i],c[i-13:i])
        up=float(np.max(top)); dn=float(np.min(bot))
        side=1 if ((c[i]>up+0.1*atr[i]) and (c[i]>o[i])) else (-1 if ((c[i]<dn-0.1*atr[i]) and (c[i]<o[i])) else 0)
        if not side: continue
        ref=float(np.median(rng[i-13:i]))
        if not ref>0: continue
        comp=float(np.mean(rng[i-2:i])/ref); sigrr=float(rng[i]/ref)
        if not (comp<=1.0 and sigrr>=1.0 and bf[i]>=0.25): continue
        j=int(np.searchsorted(t,end[i],side='left'))
        exit_target=int(end[i]+8*3_600_000)
        q=int(np.searchsorted(t,exit_target,side='left'))
        if j>=len(t) or q>=len(t): continue
        entry=float(ask[j] if side>0 else bid[j]); exit_px=float(bid[q] if side>0 else ask[q])
        pnl=(exit_px-entry)*side
        rows.append((int(t[j]),int(t[q]),int(side),float(pnl),int(end[i]),comp,sigrr,float(bf[i])))
        free=int(t[q])
    return rows

def main(month:int):
    rows=reconstruct(month); m=metric([x[3] for x in rows]); target=TARGET[month]
    assert m['trades']==target[0] and m['winners']==target[1]
    assert abs(m['net']-target[2])<1e-8 and abs(m['pf']-target[3])<5e-5, (m,target)
    print(json.dumps({'month':month,'metric':m,'parity':'PASS','august_accessed':False},sort_keys=True))

if __name__=='__main__': main(int(sys.argv[1]))
