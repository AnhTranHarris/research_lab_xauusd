import numpy as np, json, sys, time
from pathlib import Path
from numba import njit
sys.path.insert(0,'/mnt/data')
import r9b_screen as R
import r9b_r8_recert as B
import r8_sweep_lifecycle_screen as S
ROOT=Path('/mnt/data/R9B_FAST_CACHE');H=.10

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

def met(v,h):
    v=np.asarray(v,float);gp=float(v[v>0].sum());gl=float(v[v<0].sum())
    eq=np.cumsum(v);pk=np.maximum.accumulate(np.r_[0.,eq])[:-1] if len(v) else np.array([])
    return {'trades':int(len(v)),'net':float(v.sum()),'gp':gp,'gl':gl,
            'pf':gp/-gl if gl<0 else 999.,'win':float((v>0).mean()) if len(v) else 0.,
            'maxdd':float((pk-eq).max()) if len(v) else 0.,
            'avg_hold':float(np.mean(h)) if len(h) else 0.}

def run(m):
    z=np.load(ROOT/f'm{m:02d}.npz',mmap_mode='r')
    t=np.asarray(z['t']);mid=np.asarray(z['mid']);sec=np.asarray(z['sec_ids'])
    atr=np.asarray(z['atrsec']);al=np.asarray(z['align_long']);ash=np.asarray(z['align_short'])
    su,hi,lo,cl=B.build_sec(t,mid)
    X=S.sweep_signals(t,mid,su,hi,lo,cl,sec,atr,al,ash)
    O=replay_hybrid(t,mid,X);ix=nonoverlap(X,O);Q=O[ix]
    mm=met(Q[:,0],Q[:,1])
    mm['weak_struct_trades']=int((Q[:,5]==0).sum());mm['aligned_trades']=int((Q[:,5]==1).sum())
    mm['weak_struct_net']=float(Q[Q[:,5]==0,0].sum());mm['aligned_net']=float(Q[Q[:,5]==1,0].sum())
    return mm
