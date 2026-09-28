import argparse, glob, hashlib, json, time
from pathlib import Path
import numpy as np, pandas as pd
R=Path('/mnt/data/r9b_active')
H1_LOOKBACK=13; H1_BUF=.10
HOLDS=(60,120,240,480)
WAIT=(60,120,240,480,720)
TOUCH=(0.,.05,.10,.20)
PEN=(.05,.10,.25,.50)
RECLAIM=(0.,.05,.10,.20)
BODYDIR=(0,1)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def raw(m): return Path(sorted(glob.glob(f'/mnt/data/XAUUSD_DUKAS_2026_{m:02d}_ticks*.gz'))[0])
def agg(t,mid,tfmin):
 ms=tfmin*60000;k=t//ms;st=np.r_[0,np.where(k[1:]!=k[:-1])[0]+1];en=np.r_[st[1:]-1,len(k)-1]
 return {'k':k[st],'o':mid[st],'h':np.maximum.reduceat(mid,st),'l':np.minimum.reduceat(mid,st),'c':mid[en],'end':(k[st]+1)*ms}
def metric(x):
 x=np.asarray(x,float);x=x[np.isfinite(x)];n=len(x);w=x>0;gp=float(x[w].sum()) if n else 0.;gl=float(x[x<0].sum()) if n else 0.
 return {'trades':int(n),'winners':int(w.sum()),'win_rate_pct':float(w.mean()*100) if n else 0.,'net':float(x.sum()) if n else 0.,'gp':gp,'gl':gl,'pf':float(gp/-gl) if gl<0 else None,'avg':float(x.mean()) if n else None}
def h1_bos(A):
 o,h,l,c=A['o'],A['h'],A['l'],A['c'];n=len(c);tr=np.maximum(h-l,np.maximum(np.abs(h-np.r_[o[0],c[:-1]]),np.abs(l-np.r_[o[0],c[:-1]])));atr=np.full(n,np.nan)
 for i in range(3,n):atr[i]=np.mean(tr[max(0,i-13):i+1])
 rows=[]
 for i in range(max(H1_LOOKBACK,14),n):
  if not np.isfinite(atr[i]) or atr[i]<=0:continue
  top=np.maximum(o[i-H1_LOOKBACK:i],c[i-H1_LOOKBACK:i]);bot=np.minimum(o[i-H1_LOOKBACK:i],c[i-H1_LOOKBACK:i]);up=float(np.max(top));dn=float(np.min(bot))
  if c[i]>up+H1_BUF*atr[i] and c[i]>o[i]:rows.append((int(A['end'][i]),1,up,float(atr[i])))
  elif c[i]<dn-H1_BUF*atr[i] and c[i]<o[i]:rows.append((int(A['end'][i]),-1,dn,float(atr[i])))
 return np.asarray(rows,float) if rows else np.empty((0,4),float)
def build(m):
 t0=time.time();rp=raw(m);df=pd.read_csv(rp,usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'});t=df.timestamp_ms_utc.to_numpy(np.int64,copy=False);ask=df.ask_raw.to_numpy(np.int64,copy=False)/1000.;bid=df.bid_raw.to_numpy(np.int64,copy=False)/1000.;mid=(ask+bid)*.5;del df
 H=agg(t,mid,60);M=agg(t,mid,15);B=h1_bos(H);end=M['end'].astype(np.int64);ei=np.searchsorted(t,end,side='left');valid=ei<len(t);entry_ask=np.full(len(end),np.nan);entry_bid=np.full(len(end),np.nan);entry_ask[valid]=ask[ei[valid]];entry_bid[valid]=bid[ei[valid]]
 lp=np.full((len(end),len(HOLDS)),np.nan);sp=np.full_like(lp,np.nan)
 for q,hold in enumerate(HOLDS):
  xi=np.searchsorted(t,end+hold*60000,side='left');ok=valid&(xi<len(t));lp[ok,q]=bid[xi[ok]]-entry_ask[ok];sp[ok,q]=entry_bid[ok]-ask[xi[ok]]
 out=R/f'R9B_GAMMA_DYNAMIC_NET_003_{m:02d}_RETEST_CACHE.npz';np.savez_compressed(out,bos=B,m15_o=M['o'],m15_h=M['h'],m15_l=M['l'],m15_c=M['c'],m15_end=end,long_pnl=lp,short_pnl=sp)
 man={'unit':'R9B_GAMMA_DYNAMIC_NET_003_H1_H4_RETEST_RECLAIM_RECONSTRUCTION','phase':'RETEST_CACHE','month':m,'status':'COMPLETED_LOCAL','h1_owner':{'lookback':H1_LOOKBACK,'boundary':'body','atr_break_buffer':H1_BUF},'bos_events':int(len(B)),'m15_bars':int(len(end)),'holds_min':list(HOLDS),'execution':'Retest/reclaim signal uses only completed M15 bar after completed H1 BOS. Entry at first Dukascopy tick at/after M15 close; fixed-time exit at first tick at/after hold. Long ask->bid, short bid->ask.','raw_tick_sha256':sha(rp),'source_sha256':sha(__file__),'output_sha256':sha(out),'august_accessed':False,'elapsed_s':time.time()-t0};mp=R/f'R9B_GAMMA_DYNAMIC_NET_003_{m:02d}_RETEST_CACHE_MANIFEST.json';mp.write_text(json.dumps(man,indent=2)+'\n');print(json.dumps(man))
def load(m):
 z=np.load(R/f'R9B_GAMMA_DYNAMIC_NET_003_{m:02d}_RETEST_CACHE.npz',allow_pickle=False);d={k:z[k] for k in z.files};z.close();return d
def pnl(d,wait,touch,pen,reclaim,bodydir,hold):
 B=d['bos'];o=d['m15_o'];h=d['m15_h'];l=d['m15_l'];c=d['m15_c'];end=d['m15_end'];q=HOLDS.index(hold);lp=d['long_pnl'][:,q];sp=d['short_pnl'][:,q];cand=[]
 for e,side,bound,atr in B:
  lo=np.searchsorted(end,int(e)+1,side='left');hi=np.searchsorted(end,int(e)+wait*60000,side='right');found=None
  for j in range(lo,min(hi,len(end))):
   if side>0:
    ok=(l[j]<=bound+touch*atr) and (l[j]>=bound-pen*atr) and (c[j]>=bound+reclaim*atr) and ((not bodydir) or c[j]>o[j])
   else:
    ok=(h[j]>=bound-touch*atr) and (h[j]<=bound+pen*atr) and (c[j]<=bound-reclaim*atr) and ((not bodydir) or c[j]<o[j])
   if ok:found=j;break
  if found is not None:cand.append((int(end[found]),int(side),found))
 cand.sort();out=[];last=-2**63
 for tm,side,j in cand:
  if tm<last:continue
  x=lp[j] if side>0 else sp[j]
  if np.isfinite(x):out.append(x);last=tm+hold*60000
 return np.asarray(out,float)
def screen():
 D={m:load(m) for m in (1,2,3,4)};rows=[]
 for wait in WAIT:
  for touch in TOUCH:
   for pen in PEN:
    for rec in RECLAIM:
     if rec>touch+.20:continue
     for bd in BODYDIR:
      for hold in HOLDS:
       rep={};ok=True
       for m in (1,2,3):
        met=metric(pnl(D[m],wait,touch,pen,rec,bd,hold));rep[str(m)]=met
        if met['trades']<8 or met['net']<=0 or met['pf'] is None or met['pf']<=1:ok=False
       rows.append({'wait_min':wait,'touch_buffer_atr':touch,'max_penetration_atr':pen,'reclaim_atr':rec,'require_owner_body':bool(bd),'hold_min':hold,'replication':rep,'eligible':ok,'min_net':min(rep[str(m)]['net'] for m in (1,2,3)),'sum_net':sum(rep[str(m)]['net'] for m in (1,2,3)),'min_pf':min(rep[str(m)]['pf'] if rep[str(m)]['pf'] is not None else 999 for m in (1,2,3)),'min_trades':min(rep[str(m)]['trades'] for m in (1,2,3))})
 elig=[x for x in rows if x['eligible']];best=max(elig,key=lambda x:(x['min_net'],x['sum_net'],x['min_pf'],x['min_trades'])) if elig else None;ap=None;gate=False
 if best:
  ap=metric(pnl(D[4],best['wait_min'],best['touch_buffer_atr'],best['max_penetration_atr'],best['reclaim_atr'],int(best['require_owner_body']),best['hold_min']));gate=ap['trades']>=8 and ap['net']>0 and ap['pf'] is not None and ap['pf']>1
 out={'unit':'R9B_GAMMA_DYNAMIC_NET_003_H1_H4_RETEST_RECLAIM_RECONSTRUCTION','phase':'JAN_MAR_DISCOVERY_THEN_APRIL_CALIBRATION','status':'COMPLETED_LOCAL_SCREEN','parent_owner':'NET002 frozen H1 13-bar completed-body BOS with 0.10 ATR close buffer. Simple immediate-entry sleeve was rejected on July frozen forward.','mechanism':'After H1 BOS, wait for first completed M15 retest of exact broken body boundary within a bounded window. Retest penetration is bounded; M15 must close back on owner side by reclaim threshold, optionally with owner-direction body. Enter only after that completed reclaim bar. Fixed-time exact bid/ask exit.','eligible_discovery_candidates':len(elig),'frozen_candidate':best,'april':ap,'april_gate_pass':gate,'decision':'FREEZE_FOR_MAY_JUL_FORWARD' if gate else 'REJECT_RETEST_RECLAIM_BASELINE','next_unit':'R9B_GAMMA_DYNAMIC_NET_003_MAY_JUL_FROZEN_FORWARD' if gate else 'R9B_GAMMA_DYNAMIC_NET_004_STRUCTURAL_STATE_SPECIALIST','top':sorted(rows,key=lambda x:(x['eligible'],x['min_net'],x['sum_net'],x['min_pf']),reverse=True)[:40],'may_july_accessed':False,'august_accessed':False}
 op=R/'R9B_GAMMA_DYNAMIC_NET_003_H1_H4_RETEST_RECLAIM_RECONSTRUCTION.json';op.write_text(json.dumps(out,indent=2)+'\n');man={'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(op),'cache_sha256':{str(m):sha(R/f'R9B_GAMMA_DYNAMIC_NET_003_{m:02d}_RETEST_CACHE.npz') for m in (1,2,3,4)},'august_accessed':False};(R/'R9B_GAMMA_DYNAMIC_NET_003_MANIFEST.json').write_text(json.dumps(man,indent=2)+'\n');print(json.dumps({'eligible':len(elig),'best':best,'april':ap,'gate':gate,'decision':out['decision'],'result_sha256':sha(op)},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['build','screen']);ap.add_argument('--month',type=int);a=ap.parse_args();
 if a.phase=='build':assert a.month in (1,2,3,4,5,6,7);build(a.month)
 else:screen()
