"""HOLD022 causally observable January state cohort DESCRIPTIVE audit.

Parent future outcomes are allowed EX POST for diagnosis and are NEVER input
features. All reported partitions use only already-observed checkpoints.
No new strategy selection or held-out month access.
"""
import sys,hashlib,json,os
from pathlib import Path
import numpy as np
BASE=Path('/mnt/data');sys.path.insert(0,str(BASE/'net024_src'))
import net024_h1_permission as N
R=BASE/'hold022_results'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cohort(i,refp):
 p=refp[i]; n=len(p)
 gp=float(p[p>0].sum());gl=float(p[p<0].sum())
 return {'count':int(n),'winners':int((p>0).sum()),'win_rate':float(np.mean(p>0)) if n else None,'net':float(p.sum()),'gross_loss':gl,'gross_profit':gp,'mean_pnl':float(p.mean()) if n else None}

def run():
 with np.load(R/'HOLD022_JAN_POSTENTRY_CAUSAL_STATES.npz',allow_pickle=False) as z:
  e=z['entry_ms'];ex=z['original_exit_ms'];pnl=z['original_pnl'];align=z['align'];ms=z['checkpoint_ms'];p=z['executable_pnl'];mfe=z['observed_net_mfe'];h=z['checkpoint_horizon_ms']
 ix=N.raw_replay(e,ex,pnl,np.ones(len(e),bool)); assert len(ix)==28088 and abs(np.sum(pnl[ix])+4510.0870000207515)<1e-8
 z={
  'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD',
  'stage':'JAN_EXPLORE_UNPROMOTED_CAUSAL_OBSERVABLE_COHORTS',
  'nature':'ex post diagnostic only; future outcomes never become execution features',
  'selected_baseline_count':len(ix),'parent_net':float(pnl[ix].sum()),
  'parent_gross_loss':float(pnl[ix][pnl[ix]<0].sum()),
  'state_cache_sha256':sha(R/'HOLD022_JAN_POSTENTRY_CAUSAL_STATES.npz'),
  'cohorts':[],'sequence_conditions':[],'august_accessed':False
 }
 # Cross-tab by existing parent align and state currently available.
 for k,hms in enumerate(h):
  for owner_name,owner in [('weak_align',(align[ix]<3)),('strong_align',(align[ix]>=3))]:
   ok=ms[ix,k]>=0
   for state_name,ss in [
    ('negative_no_net_mfe',(p[ix,k]<0)&(mfe[ix,k]<=.05)),
    ('negative_with_net_mfe',(p[ix,k]<0)&(mfe[ix,k]>.05)),
    ('positive_now',p[ix,k]>=0),
    ('deep_negative_-0.5_or_worse',(p[ix,k]<=-.5)),
    ('deep_negative_-0.75_or_worse',(p[ix,k]<=-.75))]:
    subset=ix[owner&ok&ss]
    z['cohorts'].append({'horizon_ms':int(hms),'owner':owner_name,'observable_state':state_name,'original_parent_outcome':cohort(subset,pnl)})
 # Nonthreshold-fitted geometry -- decrease between causally observed checkpoints.
 for (i,j) in [(0,1),(1,2),(0,2)]:
  both=(ms[ix,i]>=0)&(ms[ix,j]>=0)
  worsening=(p[ix,j]<p[ix,i]);still_negative=p[ix,j]<0
  no_mfe=(mfe[ix,j]<=.05)
  for owner_name,owner in [('weak_align',(align[ix]<3)),('strong_align',(align[ix]>=3))]:
   for name,qual in [('worsening_negative_no_mfe',worsening&still_negative&no_mfe),
       ('worsening_negative_with_mfe',worsening&still_negative&~no_mfe),
       ('recovering_still_negative',(p[ix,j]>p[ix,i])&still_negative)]:
    sel=ix[both&owner&qual]
    z['sequence_conditions'].append({'from_ms':int(h[i]),'to_ms':int(h[j]),'owner':owner_name,
      'observed_path':name,'original_parent_outcome':cohort(sel,pnl),
      'avg_net_change_when_originally_exiting_at_later_checkpoint':float(np.mean((p[sel,j]-pnl[sel]))) if len(sel) else None})
 out=R/'HOLD022_JAN_CAUSAL_COHORT_DIAGNOSTIC.json';tmp=out.with_suffix('.tmp')
 tmp.write_text(json.dumps(z,indent=2,sort_keys=True)+'\n');os.replace(tmp,out)
 print(json.dumps({'PASS':True,'file':str(out),'sha256':sha(out),
 'sequence_sample':z['sequence_conditions'][:6],'august_accessed':False}))
if __name__=='__main__':run()