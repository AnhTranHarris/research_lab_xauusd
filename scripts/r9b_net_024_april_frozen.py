"""Execute the pre-April-frozen NET024 selected policy, once, on April only."""
import json,sys,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/net024_src')
import net024_h1_permission as N
ROOT=Path('/mnt/data/net024_results')
fr=ROOT/'NET024_DISCOVERY_FROZEN.json';f=json.loads(fr.read_text());
assert f['frozen_variant']=='veto_contra_weak_align|2'
assert f['status']=='FROZEN_BEFORE_APRIL'
month=4
p=ROOT/f'NET024_RAW_{month:02d}.npz'
z=np.load(p,allow_pickle=False)
e=z['raw_entry_ms'];ex=z['raw_exit_ms'];pnl=z['raw_pnl'];side=z['raw_side'];align=z['raw_align']
h1=N.owner_map(e,z['h1_close_ms'],z['h1_side'],2)
base_ix=N.raw_replay(e,ex,pnl,np.ones(len(e),bool))
selected=(~((h1!=0)&(side==-h1)&(align<3)))
candidate_ix=N.raw_replay(e,ex,pnl,selected)
base=N.mtr(pnl[base_ix]);cand=N.mtr(pnl[candidate_ix]);
expected=N.PARENT_EXPECT[month]
assert base['trades']==expected[1] and base['winners']==expected[2] and abs(base['net']-expected[3])<1e-8
r={'unit':'R9B_GAMMA_DYNAMIC_NET_024_H1_OWNERSHIP_SEQUENTIAL_PERMISSION',
 'stage':'APRIL_FROZEN_CALIBRATION','month':month,'status':'REPRODUCED_FROZEN_APRIL',
 'frozen_rule':'veto_contra_weak_align|2','discovery_sha256':N.sha(fr),
 'source_sha256':N.sha(N.__file__),'april_raw_cache_sha256':N.sha(p),
 'baseline':base,'candidate':cand,
 'delta':{'net':cand['net']-base['net'],'gross_loss_improvement':cand['gross_loss']-base['gross_loss'],
   'gross_profit_change':cand['gross_profit']-base['gross_profit'],
   'trades':cand['trades']-base['trades'],'winners':cand['winners']-base['winners']},
 'retention':{'winner_pct':cand['winners']/base['winners']*100,'trade_pct':cand['trades']/base['trades']*100},
 'pass_predeclared_gate':bool(cand['gross_loss']>base['gross_loss'] and cand['net']>=base['net']
  and cand['winners']/base['winners']>=.95 and cand['trades']/base['trades']>=.95),
 'august_accessed':False}
r['decision']='PROCEED_FROZEN_MAY_JUL_FORWARD' if r['pass_predeclared_gate'] else 'REJECT_APRIL_FROZEN_GATE'
r['next_stage']='NET024_FROZEN_FORWARD_MAY' if r['pass_predeclared_gate'] else 'NET024_MATERIALIZE_REJECTED_APRIL'
o=ROOT/'NET024_APRIL_FROZEN.json';o.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':r['decision'],'april_baseline':base,'april_candidate':cand,
 'delta':r['delta'],'retention':r['retention'],'sha256':N.sha(o),'next_stage':r['next_stage']}))