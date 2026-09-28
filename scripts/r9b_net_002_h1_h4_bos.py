import argparse, glob, hashlib, json, time
from pathlib import Path
import numpy as np, pandas as pd
R=Path('/mnt/data/r9b_active')
TFS=(60,240)
LOOKBACK=(2,3,5,8,13,21)
BODY=(0.0,0.25,0.5)
BUF=(0.0,0.05,0.10)
HOLDS={60:(1,2,3,4,6,8),240:(1,2,3,4)}
BOUND=('wick','body')

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def raw(m): return Path(sorted(glob.glob(f'/mnt/data/XAUUSD_DUKAS_2026_{m:02d}_ticks*.gz'))[0])
def metric(x):
 x=np.asarray(x,float);x=x[np.isfinite(x)];n=len(x);w=x>0;gp=float(x[w].sum()) if n else 0.;gl=float(x[x<0].sum()) if n else 0.
 return {'trades':int(n),'winners':int(w.sum()),'win_rate_pct':float(w.mean()*100) if n else 0.,'net':float(x.sum()) if n else 0.,'gp':gp,'gl':gl,'pf':float(gp/-gl) if gl<0 else None,'avg':float(x.mean()) if n else None}
def aggregate(t,mid,tfmin):
 ms=tfmin*60000; key=t//ms; st=np.r_[0,np.where(key[1:]!=key[:-1])[0]+1]; en=np.r_[st[1:]-1,len(key)-1]
 return key[st], mid[st], np.maximum.reduceat(mid,st), np.minimum.reduceat(mid,st), mid[en]
def first_exec(t,ask,bid,ts,side):
 j=np.searchsorted(t,ts,side='left')
 if j>=len(t): return np.nan
 return ask[j] if side>0 else bid[j]
def exit_exec(t,ask,bid,ts,side):
 j=np.searchsorted(t,ts,side='left')
 if j>=len(t): return np.nan
 return bid[j] if side>0 else ask[j]
def build(m):
 t0=time.time();rp=raw(m);df=pd.read_csv(rp,usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})
 t=df.timestamp_ms_utc.to_numpy(np.int64,copy=False);ask=df.ask_raw.to_numpy(np.int64,copy=False)/1000.;bid=df.bid_raw.to_numpy(np.int64,copy=False)/1000.;mid=(ask+bid)*.5
 payload={}
 for tf in TFS:
  k,o,h,l,c=aggregate(t,mid,tf); n=len(k); rng=h-l; body=np.abs(c-o); bf=np.divide(body,rng,out=np.zeros(n),where=rng>0); tr=np.maximum(h-l,np.maximum(np.abs(h-np.r_[o[0],c[:-1]]),np.abs(l-np.r_[o[0],c[:-1]])))
  atr=np.full(n,np.nan)
  for i in range(3,n): atr[i]=np.mean(tr[max(0,i-13):i+1])
  end=(k+1)*tf*60000
  entry_ask=np.full(n,np.nan);entry_bid=np.full(n,np.nan)
  for i,x in enumerate(end):
   j=np.searchsorted(t,x,side='left')
   if j<len(t): entry_ask[i]=ask[j];entry_bid[i]=bid[j]
  hp=HOLDS[tf]; long=np.full((n,len(hp)),np.nan); short=np.full((n,len(hp)),np.nan)
  for q,hold in enumerate(hp):
   xt=end+hold*tf*60000
   for i,x in enumerate(xt):
    j=np.searchsorted(t,x,side='left')
    if j<len(t) and np.isfinite(entry_ask[i]):
     long[i,q]=bid[j]-entry_ask[i]
     short[i,q]=entry_bid[i]-ask[j]
  payload[f'k_{tf}']=k;payload[f'o_{tf}']=o;payload[f'h_{tf}']=h;payload[f'l_{tf}']=l;payload[f'c_{tf}']=c;payload[f'bf_{tf}']=bf;payload[f'atr_{tf}']=atr;payload[f'end_{tf}']=end;payload[f'long_{tf}']=long;payload[f'short_{tf}']=short
 out=R/f'R9B_GAMMA_DYNAMIC_NET_002_{m:02d}_HTF_CACHE.npz';np.savez_compressed(out,**payload)
 man={'unit':'R9B_GAMMA_DYNAMIC_NET_002_H1_H4_FRESH_CAUSAL_RECONSTRUCTION','phase':'HTF_CACHE','month':m,'status':'COMPLETED_LOCAL','timeframes_min':list(TFS),'execution':'Signal formed only after completed H1/H4 bar. Entry/exit use first Dukascopy tick at or after scheduled timestamp; long enters ask/exits bid, short enters bid/exits ask.','raw_tick_sha256':sha(rp),'source_sha256':sha(__file__),'output_sha256':sha(out),'august_accessed':False,'elapsed_s':time.time()-t0}
 mp=R/f'R9B_GAMMA_DYNAMIC_NET_002_{m:02d}_HTF_CACHE_MANIFEST.json';mp.write_text(json.dumps(man,indent=2)+'\n');print(json.dumps(man))
def load(m):
 z=np.load(R/f'R9B_GAMMA_DYNAMIC_NET_002_{m:02d}_HTF_CACHE.npz',allow_pickle=False);d={k:z[k] for k in z.files};z.close();return d
def candidate_pnl(d,tf,n,bodymin,buf,bound,hold):
 o=d[f'o_{tf}'];h=d[f'h_{tf}'];l=d[f'l_{tf}'];c=d[f'c_{tf}'];bf=d[f'bf_{tf}'];atr=d[f'atr_{tf}'];end=d[f'end_{tf}']; hp=HOLDS[tf]; q=hp.index(hold); lp=d[f'long_{tf}'][:,q];sp=d[f'short_{tf}'][:,q]
 out=[];last_exit=-2**63
 for i in range(max(n,14),len(c)):
  if end[i]<=last_exit or not np.isfinite(atr[i]): continue
  if bound=='wick': up=np.max(h[i-n:i]);dn=np.min(l[i-n:i])
  else:
   top=np.maximum(o[i-n:i],c[i-n:i]);bot=np.minimum(o[i-n:i],c[i-n:i]);up=np.max(top);dn=np.min(bot)
  longsig=(c[i]>up+buf*atr[i]) and (c[i]>o[i]) and (bf[i]>=bodymin)
  shortsig=(c[i]<dn-buf*atr[i]) and (c[i]<o[i]) and (bf[i]>=bodymin)
  if longsig and np.isfinite(lp[i]): out.append(lp[i]);last_exit=end[i]+hold*tf*60000
  elif shortsig and np.isfinite(sp[i]): out.append(sp[i]);last_exit=end[i]+hold*tf*60000
 return np.asarray(out,float)
def screen():
 D={m:load(m) for m in (1,2,3,4)};rows=[]
 for tf in TFS:
  mintr=12 if tf==60 else 4
  for n in LOOKBACK:
   for bodymin in BODY:
    for buf in BUF:
     for bound in BOUND:
      for hold in HOLDS[tf]:
       rep={};ok=True
       for m in (1,2,3,4):
        met=metric(candidate_pnl(D[m],tf,n,bodymin,buf,bound,hold));rep[str(m)]=met
        if m<=3 and (met['trades']<mintr or met['net']<=0 or met['pf'] is None or met['pf']<=1):ok=False
       rows.append({'tf_min':tf,'lookback':n,'body_fraction_min':bodymin,'atr_break_buffer':buf,'boundary':bound,'hold_bars':hold,'replication':rep,'discovery_eligible':ok,'min_net':min(rep[str(m)]['net'] for m in (1,2,3)),'sum_net':sum(rep[str(m)]['net'] for m in (1,2,3)),'min_pf':min(rep[str(m)]['pf'] if rep[str(m)]['pf'] is not None else 999 for m in (1,2,3)),'min_trades':min(rep[str(m)]['trades'] for m in (1,2,3))})
 elig=[r for r in rows if r['discovery_eligible']];best=max(elig,key=lambda r:(r['min_net'],r['sum_net'],r['min_pf'],r['min_trades'])) if elig else None;gate=False
 if best:
  a=best['replication']['4'];mintr=12 if best['tf_min']==60 else 4;gate=a['trades']>=mintr and a['net']>0 and a['pf'] is not None and a['pf']>1
 top=sorted(rows,key=lambda r:(r['discovery_eligible'],r['min_net'],r['sum_net'],r['min_pf'],r['min_trades']),reverse=True)[:40]
 out={'unit':'R9B_GAMMA_DYNAMIC_NET_002_H1_H4_FRESH_CAUSAL_RECONSTRUCTION','phase':'JAN_MAR_DISCOVERY_THEN_APRIL_CALIBRATION','status':'COMPLETED_LOCAL_SCREEN','mechanism':'Fresh completed-bar accepted BOS on H1/H4. Structure boundary is either prior wick extreme or prior candle-body extreme; signal requires completed bar close beyond boundary, same-direction body, optional ATR buffer and body-quality threshold. One position at a time. Exact Dukascopy bid/ask execution at first tick after completed-bar signal and fixed predeclared bar horizon.','community_semantics':'Close-confirmed BOS and completed HTF state; no partial future candle. Historical H1/H4 metrics are references only, not selection targets.','eligible_discovery_candidates':len(elig),'frozen_candidate':best,'april_gate_pass':gate,'decision':'FREEZE_FOR_MAY_JUL_EXACT_FORWARD' if gate else 'NO_ROBUST_H1_H4_BOS_BASELINE','top_discovery':top,'next_unit':'R9B_GAMMA_DYNAMIC_NET_002_MAY_JUL_EXACT_FORWARD' if gate else 'R9B_GAMMA_DYNAMIC_NET_003_H1_H4_RETEST_RECLAIM_RECONSTRUCTION','may_july_accessed':False,'august_accessed':False}
 outp=R/'R9B_GAMMA_DYNAMIC_NET_002_H1_H4_FRESH_CAUSAL_RECONSTRUCTION.json';outp.write_text(json.dumps(out,indent=2)+'\n');man={'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(outp),'cache_sha256':{str(m):sha(R/f'R9B_GAMMA_DYNAMIC_NET_002_{m:02d}_HTF_CACHE.npz') for m in (1,2,3,4)},'august_accessed':False};(R/'R9B_GAMMA_DYNAMIC_NET_002_MANIFEST.json').write_text(json.dumps(man,indent=2)+'\n');print(json.dumps({'eligible_discovery_candidates':len(elig),'frozen_candidate':best,'april_gate_pass':gate,'decision':out['decision'],'result_sha256':sha(outp)},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['build','screen']);ap.add_argument('--month',type=int);a=ap.parse_args();
 if a.phase=='build': assert a.month in (1,2,3,4);build(a.month)
 else:screen()
