import json,hashlib
from pathlib import Path
import numpy as np
import r9b_net_003_h1_retest_reclaim as r
R=Path('/mnt/data/r9b_active');OUT=R/'R9B_GAMMA_DYNAMIC_NET_007_FAILED_ACCEPTANCE_SPECIALIST.json';MAN=R/'R9B_GAMMA_DYNAMIC_NET_007_MANIFEST.json'
WAIT=(60,120,240,480,720);DEPTH=(0.,.05,.10,.20,.30);BODY=(0,1);HOLDS=(60,120,240,480)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def metric(x):return r.metric(np.asarray(x,float))
def pnl(d,wait,depth,body,hold):
 B=d['bos'];o=d['m15_o'];c=d['m15_c'];end=d['m15_end'];q=HOLDS.index(hold);lp=d['long_pnl'][:,q];sp=d['short_pnl'][:,q];cand=[]
 for e,side,bound,atr in B:
  lo=np.searchsorted(end,int(e)+1,side='left');hi=np.searchsorted(end,int(e)+wait*60000,side='right');found=None
  for j in range(lo,min(hi,len(end))):
   # original long BOS fails if completed M15 closes below broken upper body boundary; reverse for short BOS
   ok=(c[j]<=bound-depth*atr) if side>0 else (c[j]>=bound+depth*atr)
   if body:ok=ok and ((c[j]<o[j]) if side>0 else (c[j]>o[j]))
   if ok:found=j;break
  if found is not None:cand.append((int(end[found]),-int(side),found))
 cand.sort();out=[];last=-2**63
 for tm,newside,j in cand:
  if tm<last:continue
  x=lp[j] if newside>0 else sp[j]
  if np.isfinite(x):out.append(x);last=tm+hold*60000
 return np.asarray(out,float)
def main():
 D={m:r.load(m) for m in (1,2,3,4)};rows=[]
 for w in WAIT:
  for dep in DEPTH:
   for bd in BODY:
    for hold in HOLDS:
     rep={};ok=True
     for m in (1,2,3):
      met=metric(pnl(D[m],w,dep,bd,hold));rep[str(m)]=met
      if met['trades']<8 or met['net']<=0 or met['pf'] is None or met['pf']<=1:ok=False
     rows.append({'wait_min':w,'failure_depth_atr':dep,'require_failure_body':bool(bd),'hold_min':hold,'replication':rep,'eligible':ok,'min_net':min(rep[str(m)]['net'] for m in (1,2,3)),'sum_net':sum(rep[str(m)]['net'] for m in (1,2,3)),'min_pf':min(rep[str(m)]['pf'] if rep[str(m)]['pf'] is not None else 999 for m in (1,2,3)),'min_trades':min(rep[str(m)]['trades'] for m in (1,2,3))})
 elig=[x for x in rows if x['eligible']];best=max(elig,key=lambda x:(x['min_net'],x['sum_net'],x['min_pf'],x['min_trades'])) if elig else None;ap=None;gate=False
 if best:
  ap=metric(pnl(D[4],best['wait_min'],best['failure_depth_atr'],int(best['require_failure_body']),best['hold_min']));gate=ap['trades']>=8 and ap['net']>0 and ap['pf'] is not None and ap['pf']>1
 out={'unit':'R9B_GAMMA_DYNAMIC_NET_007_STRUCTURAL_FAILURE_SPECIALIST','phase':'JAN_MAR_DISCOVERY_THEN_APRIL_CALIBRATION','status':'COMPLETED_LOCAL_SCREEN','parent':'NET002 fixed H1 completed-body BOS event population. This sleeve does not enter the breakout; it waits for causal failed acceptance and trades the opposite direction.','mechanism':'After H1 BOS, first completed M15 close back through the broken H1 body boundary by a bounded ATR depth marks failed acceptance. Optional M15 reversal body confirms. Fresh opposite-direction trade opens at the first tick after that close and uses a fixed exact bid/ask time exit.','eligible_candidates':len(elig),'frozen_candidate':best,'april':ap,'april_gate_pass':gate,'decision':'FREEZE_FOR_MAY_JUL_FORWARD' if gate else 'REJECT_FAILED_ACCEPTANCE_SPECIALIST','next_unit':'R9B_GAMMA_DYNAMIC_NET_007_MAY_JUL_FROZEN_FORWARD' if gate else 'R9B_GAMMA_DYNAMIC_NET_008_STRUCTURAL_PHASE_SWITCH','top':sorted(rows,key=lambda x:(x['eligible'],x['min_net'],x['sum_net'],x['min_pf']),reverse=True)[:30],'may_july_accessed':False,'august_accessed':False};OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'input_cache_sha256':{str(m):sha(R/f'R9B_GAMMA_DYNAMIC_NET_003_{m:02d}_RETEST_CACHE.npz') for m in (1,2,3,4)},'august_accessed':False},indent=2)+'\n');print(json.dumps({'eligible':len(elig),'best':best,'april':ap,'gate':gate,'decision':out['decision'],'result_sha256':sha(OUT)},indent=2))
if __name__=='__main__':main()
