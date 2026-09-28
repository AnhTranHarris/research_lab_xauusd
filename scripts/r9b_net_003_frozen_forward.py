import json, hashlib
from pathlib import Path
import numpy as np
import r9b_net_003_h1_retest_reclaim as s
R=Path('/mnt/data/r9b_active'); DISC=R/'R9B_GAMMA_DYNAMIC_NET_003_H1_H4_RETEST_RECLAIM_RECONSTRUCTION.json'; OUT=R/'R9B_GAMMA_DYNAMIC_NET_003_MAY_JUL_FROZEN_FORWARD.json'; MAN=R/'R9B_GAMMA_DYNAMIC_NET_003_MAY_JUL_FROZEN_FORWARD_MANIFEST.json'
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
d=json.load(open(DISC));c=d['frozen_candidate'];params={k:c[k] for k in ('wait_min','touch_buffer_atr','max_penetration_atr','reclaim_atr','require_owner_body','hold_min')}
monthly={};allp=[]
for m in (5,6,7):
 D=s.load(m);p=s.pnl(D,params['wait_min'],params['touch_buffer_atr'],params['max_penetration_atr'],params['reclaim_atr'],int(params['require_owner_body']),params['hold_min']);monthly[str(m)]=s.metric(p);allp.append(p)
agg=s.metric(np.concatenate(allp));rob=all(monthly[str(m)]['trades']>=8 and monthly[str(m)]['net']>0 and (monthly[str(m)]['pf'] or 0)>1 for m in (5,6,7))
out={'unit':'R9B_GAMMA_DYNAMIC_NET_003_H1_H4_RETEST_RECLAIM_RECONSTRUCTION','phase':'MAY_JUL_FROZEN_FORWARD','status':'COMPLETED_LOCAL_FROZEN_FORWARD','frozen_candidate':params,'selection_contract':'Frozen on Jan-Mar discovery and April calibration. May-Jul evaluated once with no retuning.','monthly':monthly,'aggregate':agg,'robust_all_forward_months':rob,'decision':'RETAIN_RETEST_RECLAIM_SLEEVE_FRONTIER_READY_INTEGRATION' if rob else 'REJECT_RETEST_RECLAIM_FROZEN_FORWARD','next_unit':'R9B_GAMMA_DYNAMIC_NET_004_RETEST_RECLAIM_SYSTEM_INTEGRATION' if rob else 'R9B_GAMMA_DYNAMIC_NET_004_STRUCTURAL_STATE_SPECIALIST','discovery_result_sha256':sha(DISC),'cache_sha256':{str(m):sha(R/f'R9B_GAMMA_DYNAMIC_NET_003_{m:02d}_RETEST_CACHE.npz') for m in (5,6,7)},'august_accessed':False};OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'discovery_result_sha256':sha(DISC),'cache_sha256':out['cache_sha256'],'august_accessed':False},indent=2)+'\n');print(json.dumps(out,indent=2));print('RESULT_SHA',sha(OUT));print('SOURCE_SHA',sha(__file__))
