import json, hashlib
from pathlib import Path
import numpy as np
import r9b_net_002_h1_h4_bos as b
R=Path('/mnt/data/r9b_active')
DISC=R/'R9B_GAMMA_DYNAMIC_NET_002_H1_H4_FRESH_CAUSAL_RECONSTRUCTION.json'
OUT=R/'R9B_GAMMA_DYNAMIC_NET_002_MAY_JUL_FROZEN_FORWARD.json'
MAN=R/'R9B_GAMMA_DYNAMIC_NET_002_MAY_JUL_FROZEN_FORWARD_MANIFEST.json'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
def metric(x): return b.metric(np.asarray(x,float))
d=json.load(open(DISC)); c=d['frozen_candidate']
params={k:c[k] for k in ('tf_min','lookback','body_fraction_min','atr_break_buffer','boundary','hold_bars')}
assert params=={'tf_min':60,'lookback':13,'body_fraction_min':0.0,'atr_break_buffer':0.1,'boundary':'body','hold_bars':8}
monthly={}; allp=[]
for m in (5,6,7):
 D=b.load(m); p=b.candidate_pnl(D,params['tf_min'],params['lookback'],params['body_fraction_min'],params['atr_break_buffer'],params['boundary'],params['hold_bars']); allp.append(p); monthly[str(m)]=metric(p)
agg=metric(np.concatenate(allp))
robust=all(monthly[str(m)]['trades']>=12 and monthly[str(m)]['net']>0 and (monthly[str(m)]['pf'] or 0)>1 for m in (5,6,7))
out={'unit':'R9B_GAMMA_DYNAMIC_NET_002_H1_H4_FRESH_CAUSAL_RECONSTRUCTION','phase':'MAY_JUL_FROZEN_FORWARD','status':'COMPLETED_LOCAL_FROZEN_FORWARD','frozen_candidate':params,'selection_contract':'Frozen from Jan-Mar discovery and April calibration before May-Jul access. No forward retuning.','monthly':monthly,'aggregate':agg,'robust_all_forward_months':robust,'decision':'RETAIN_H1_STRUCTURAL_SLEEVE_FRONTIER_READY_SYSTEM_INTEGRATION' if robust else 'REJECT_H1_FROZEN_FORWARD','next_unit':'R9B_GAMMA_DYNAMIC_NET_003_H1_STRUCTURAL_SLEEVE_INTEGRATION' if robust else 'R9B_GAMMA_DYNAMIC_NET_003_H1_H4_RETEST_RECLAIM_RECONSTRUCTION','discovery_result_sha256':sha(DISC),'cache_sha256':{str(m):sha(R/f'R9B_GAMMA_DYNAMIC_NET_002_{m:02d}_HTF_CACHE.npz') for m in (5,6,7)},'august_accessed':False}
OUT.write_text(json.dumps(out,indent=2)+'\n')
man={'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'discovery_result_sha256':sha(DISC),'cache_sha256':out['cache_sha256'],'august_accessed':False};MAN.write_text(json.dumps(man,indent=2)+'\n')
print(json.dumps(out,indent=2));print('RESULT_SHA',sha(OUT));print('SOURCE_SHA',sha(__file__))
