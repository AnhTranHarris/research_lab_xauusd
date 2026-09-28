import json,hashlib
from pathlib import Path
import numpy as np
import r9b_net_002_h1_h4_bos as b
R=Path('/mnt/data/r9b_active');OUT=R/'R9B_GAMMA_DYNAMIC_NET_005_H4_SPECIALIST.json';MAN=R/'R9B_GAMMA_DYNAMIC_NET_005_MANIFEST.json'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
def main():
 D={m:b.load(m) for m in (1,2,3,4)};rows=[]
 for n in b.LOOKBACK:
  for body in b.BODY:
   for buf in b.BUF:
    for bound in b.BOUND:
     for hold in b.HOLDS[240]:
      rep={};ok=True
      for m in (1,2,3):
       met=b.metric(b.candidate_pnl(D[m],240,n,body,buf,bound,hold));rep[str(m)]=met
       if met['trades']<4 or met['net']<=0 or met['pf'] is None or met['pf']<=1:ok=False
      rows.append({'tf_min':240,'lookback':n,'body_fraction_min':body,'atr_break_buffer':buf,'boundary':bound,'hold_bars':hold,'replication':rep,'eligible':ok,'min_net':min(rep[str(m)]['net'] for m in (1,2,3)),'sum_net':sum(rep[str(m)]['net'] for m in (1,2,3)),'min_pf':min(rep[str(m)]['pf'] if rep[str(m)]['pf'] is not None else 999 for m in (1,2,3)),'min_trades':min(rep[str(m)]['trades'] for m in (1,2,3))})
 elig=[r for r in rows if r['eligible']];best=max(elig,key=lambda r:(r['min_net'],r['sum_net'],r['min_pf'],r['min_trades'])) if elig else None;ap=None;gate=False
 if best:
  ap=b.metric(b.candidate_pnl(D[4],240,best['lookback'],best['body_fraction_min'],best['atr_break_buffer'],best['boundary'],best['hold_bars']));gate=ap['trades']>=4 and ap['net']>0 and ap['pf'] is not None and ap['pf']>1
 out={'unit':'R9B_GAMMA_DYNAMIC_NET_005_ORTHOGONAL_H4_SPECIALIST','phase':'JAN_MAR_DISCOVERY_THEN_APRIL_CALIBRATION','status':'COMPLETED_LOCAL_SCREEN','mechanism':'Independent H4 completed-body/wick BOS specialist reconstructed from the NET002 causal bar/execution cache. Selected without May-Jul inspection.','eligible_candidates':len(elig),'frozen_candidate':best,'april':ap,'april_gate_pass':gate,'decision':'FREEZE_FOR_MAY_JUL_FORWARD' if gate else 'REJECT_H4_BASELINE','next_unit':'R9B_GAMMA_DYNAMIC_NET_005_MAY_JUL_FROZEN_FORWARD' if gate else 'R9B_GAMMA_DYNAMIC_NET_006_STRUCTURAL_PHASE_ROUTER','top':sorted(rows,key=lambda r:(r['eligible'],r['min_net'],r['sum_net'],r['min_pf']),reverse=True)[:30],'may_july_accessed':False,'august_accessed':False};OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'input_cache_sha256':{str(m):sha(R/f'R9B_GAMMA_DYNAMIC_NET_002_{m:02d}_HTF_CACHE.npz') for m in (1,2,3,4)},'august_accessed':False},indent=2)+'\n');print(json.dumps({'eligible':len(elig),'best':best,'april':ap,'gate':gate,'decision':out['decision'],'result_sha256':sha(OUT)},indent=2))
if __name__=='__main__':main()
