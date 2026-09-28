"""R9B HOLD_EXIT_022 / structural-invalidation causal January discovery.

A sweep/reclaim level is fixed at each independently generated CAUSAL014 entry.
After entry, a structural failure occurs only after executable quote penetrates
that exact prior sweep level against the position (with chosen buffer) for the
specified continuous observed duration. The original stop/trail/maxhold and
chronological availability ALWAYS remain active. No future outcome as input.

This is a separate hypothesis from generic 1/2/4-second early-negative cuts,
which failed January discovery. January--March discovery; April calibration;
May--July frozen forward; August prohibited. Used raw midpoint plus fixed
$0.10 half-spread to retain identical CAUSAL014 modeled execution cost.
"""
from __future__ import annotations
import sys,os,json,hashlib,time,platform
from pathlib import Path
import numpy as np
from numba import njit
BASE=Path('/mnt/data'); OUT=BASE/'hold022_results'; OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE/'net024_src'))
sys.path.insert(0,str(BASE/'net023_src'))
import net024_h1_permission as N
import r9b_screen as R
import r9b_r8_recert as B
import r8_sweep_lifecycle_screen as S

BUFFER_PRICE=np.array([0.00,0.10,0.25],dtype=np.float64)
CONFIRM_MS=np.array([0,500,1500],dtype=np.int64)
OWNERS=['all','weak_only','strong_only']
JANGOLDEN=(34362,28088,19087,-4510.0870000207515)

def sha(file):
 h=hashlib.sha256()
 with Path(file).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def atomic_json(file,v):
 file=Path(file);temp=file.with_suffix('.tmp')
 temp.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');os.replace(temp,file)

def atomic_npz(file,**arrays):
 file=Path(file);temp=file.with_suffix('.partial.npz')
 np.savez_compressed(temp,**arrays)
 with np.load(temp,allow_pickle=False) as z:
  assert set(z.files)==set(arrays)
  for key,a in arrays.items():
   assert z[key].shape==a.shape and np.array_equal(z[key],a,equal_nan=True)
 os.replace(temp,file)

@njit(cache=True)
def observed_structural_failures(t,mid,entry,base_exit,side,level,buffers,confirm):
 """One independent scan per raw entry; earliest legal failure/price by variant.

 Current *executable contra quote*: short ask exceeds level+buffer;
 long bid falls below level-buffer. One positional predecessor state per
 buffer; the consecutive structural violation is reset on reclaim.
 Stop/trail/maxhold priority is enforced by strictly excluding the parent's
 exit tick. No backdating to first crossing when requiring duration proof.
 """
 n=len(entry);nv=len(buffers)*len(confirm)
 xt=np.full((n,nv),-1,np.int64);xp=np.full((n,nv),np.nan,np.float64)
 onset=np.empty(len(buffers),np.int64)
 for i in range(n):
  st=np.searchsorted(t,entry[i],side='left')
  if st>=len(t) or t[st]!=entry[i]: continue
  ep=mid[st];sd=side[i];le=level[i]
  for b in range(len(buffers)): onset[b]=-1
  completed=0
  for j in range(st+1,len(t)):
   tt=t[j]
   if tt>=base_exit[i]: break
   for b in range(len(buffers)):
    # midpoint -> executable bid/ask at the same fixed H=.10 as parent
    violated=sd*(mid[j]-le)<-(0.10+buffers[b])
    if not violated:
     onset[b]=-1
    else:
     if onset[b]<0:onset[b]=tt
     for k in range(len(confirm)):
      u=b*len(confirm)+k
      if xt[i,u]==-1 and tt-onset[b]>=confirm[k]:
       xt[i,u]=tt
       xp[i,u]=(mid[j]-ep)*sd-.20
       completed+=1
   if completed==nv:break
 return xt,xp

def test():
 t=np.array([100,300,800,1000,1500,1700,2100,3000],np.int64)
 mid=np.array([10.,10.02,9.7,9.73,9.65,9.72,9.5,9.3])
 e=np.array([100,100,100],np.int64)
 ex=np.array([3000,1500,1000],np.int64)
 sd=np.array([1,1,1],np.int8)
 lvl=np.array([10.,10.,10.])
 x,p=observed_structural_failures(t,mid,e,ex,sd,lvl,np.array([0.,.1,.25]),np.array([0,500,1500]))
 assert x[0,0]==800 and x[0,1]==1500 and x[0,2]==3000 or x[0,2]==-1, x
 assert x[1,1]==-1, 'Original exit at 1500 must preempt structural hold proof'
 assert x[2,0]==800 and x[2,1]==-1, 'strict precedence at parent exit'
 assert abs(p[0,0]-(-.5))<1e-9
 assert np.all((x==-1)|(x<ex[:,None]))
 print('STRUCTURAL_INVALIDATION_CAUSAL_TEST_PASS')

def get_x(m,t,mid):
 # Rebuild from exact currently accessible historical source, without using
 # future-completed second or forensic/legacy compatibility switch.
 sec_ids,_,_,_,_,_,_,_=R.active_seconds(t,mid)
 e5,_,a5=R.aggregate_tf_from_ticks(t,mid,300)
 atr=R.map_completed(sec_ids,e5,a5)
 al=np.zeros(len(sec_ids),np.int8);ash=np.zeros(len(sec_ids),np.int8)
 for tf in (60,180,300,600,1200):
  en,ret,a=R.aggregate_tf_from_ticks(t,mid,tf)
  r=R.map_completed(sec_ids,en,ret);aa=R.map_completed(sec_ids,en,a)
  ok=np.isfinite(aa)
  al+=((r>0)&ok).astype(np.int8)
  ash+=((r<0)&ok).astype(np.int8)
 su,hi,lo,cl=B.build_sec(t,mid)
 return S.sweep_signals(t,mid,su,hi,lo,cl,sec_ids,atr,al,ash)

def run_january():
 t0=time.perf_counter();m=1
 market=R.RAW_BY_MONTH[m];src=BASE/'net024_results/NET024_RAW_01.npz'
 manifest=json.loads((BASE/'net024_results/NET024_RAW_01.manifest.json').read_text())
 assert sha(market)==manifest['raw_data_sha256']
 assert sha(src)==manifest['raw_cache_sha256']
 with np.load(src,allow_pickle=False) as z:
  e=z['raw_entry_ms'];base_ex=z['raw_exit_ms'];base_pnl=z['raw_pnl'];sd=z['raw_side'];align=z['raw_align']
 assert np.all(base_ex>e) and len(e)==JANGOLDEN[0]
 ix=N.raw_replay(e,base_ex,base_pnl,np.ones(len(e),bool));base=N.mtr(base_pnl[ix])
 assert (base['trades'],base['winners'])==JANGOLDEN[1:3] and abs(base['net']-JANGOLDEN[3])<1e-8
 t,mid=R.load_ticks(m);assert len(t)==9135062 and np.all(np.diff(t)>=0)
 X=get_x(m,t,mid)
 assert len(X)==len(e) and np.array_equal(X[:,0].astype(np.int64),e)
 assert np.array_equal(X[:,1].astype(np.int8),sd) and np.array_equal(X[:,3].astype(np.int8),align)
 level=X[:,2].astype(np.float64)
 assert np.all(np.isfinite(level))
 xt,xp=observed_structural_failures(t,mid,e,base_ex,sd,level,BUFFER_PRICE,CONFIRM_MS)
 assert np.all((xt==-1)|(xt<base_ex[:,None]))
 assert np.all(np.isfinite(xp[xt>=0]));assert np.all(np.isnan(xp[xt==-1]))
 obs=OUT/'HOLD022_JAN_STRUCT_LEVEL_OBS.npz'
 atomic_npz(obs,entry_ms=e,base_exit_ms=base_ex,base_pnl=base_pnl,side=sd,align=align,
            event_sweep_level=level,buffer_price=BUFFER_PRICE,confirm_ms=CONFIRM_MS,
            failure_exit_ms=xt,failure_pnl=xp)
 variants=[]
 for b,buffer in enumerate(BUFFER_PRICE):
  for k,hold in enumerate(CONFIRM_MS):
   u=b*len(CONFIRM_MS)+k;trigger=xt[:,u]>=0
   for owner in OWNERS:
    own=np.ones(len(e),bool) if owner=='all' else (align<3 if owner=='weak_only' else align>=3)
    q=trigger & own
    ex=np.where(q,xt[:,u],base_ex);p=np.where(q,xp[:,u],base_pnl)
    i=N.raw_replay(e,ex,p,np.ones(len(e),bool));met=N.mtr(p[i]);d={key:met[key]-base[key] for key in ('net','gross_loss','gross_profit','winners','trades','pf')}
    variants.append({'contra_buffer_price':float(buffer),'observed_confirmation_ms':int(hold),
      'owner':owner,'raw_modified':int(q.sum()),'executed_modified':int(q[i].sum()),
      'metrics':met,'delta':d,'winners_retained_pct':100*met['winners']/base['winners'],
      'trades_retained_pct':100*met['trades']/base['trades']})
 eligible=[r for r in variants if r['delta']['net']>0 and r['delta']['gross_loss']>0 and r['winners_retained_pct']>=95 and r['trades_retained_pct']>=95]
 result={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD',
 'stage':'JAN_SWEEP_LEVEL_CAUSAL_INVALIDATION_DISCOVERY','status':'COMPLETED_LOCAL',
 'hypothesis':'opposite executable quote re-penetrates the original causal sweep/reclaim level and remains in contra territory for an observed duration before original parent exit; same one-position re-selection',
 'source_month':1,'august_accessed':False,'frozen_predeclared_parameters':{'price_buffers':BUFFER_PRICE.tolist(), 'confirmation_ms':CONFIRM_MS.tolist(),'owner_modes':OWNERS},
 'predeclared_gate':'net + GL improvement on discovery month; >=95% winner and trade retention; no April/forward access',
 'parent':base,'raw_events':len(e),'market_ticks':len(t),'variants':variants,
 'eligible_candidate_count':len(eligible),'eligible_candidates':eligible,
 'source_sha256':sha(__file__),'original_market_sha256':sha(market),'parent_cache_sha256':sha(src),
 'level_observation_cache_sha256':sha(obs),'elapsed_seconds':round(time.perf_counter()-t0,2),
 'next':'FEB_MAR_DISCOVERY_ONLY_IF_JAN_ELIGIBLE_ELSE_DO_NOT_SPEND_FORWARD_WINDOW_ON_REJECTED_FAMILY'}
 dst=OUT/'HOLD022_JAN_STRUCT_INVALIDATION.json';atomic_json(dst,result)
 mf=OUT/'HOLD022_JAN_STRUCT_INVALIDATION_MANIFEST.json'
 atomic_json(mf,{'status':'COMPLETED_LOCAL','stage':result['stage'],'source_sha256':sha(__file__),
 'source_tick_sha256':sha(market),'parent_event_cache_sha256':sha(src),
 'structural_cache_sha256':sha(obs),'result_sha256':sha(dst),'test_count':len(variants),
 'eligible_count':len(eligible),'parent_golden_reproduced':True,'august_accessed':False,
 'exact_next':result['next']})
 print(json.dumps({'status':'COMPLETED_LOCAL','parent':base,'variant_count':len(variants),
 'eligible_count':len(eligible),'top_net':sorted(variants,key=lambda a:a['delta']['net'],reverse=True)[:5],
 'top_GL':sorted(variants,key=lambda a:a['delta']['gross_loss'],reverse=True)[:3],
 'output_sha256':sha(dst),'manifest_sha256':sha(mf),'elapsed_s':result['elapsed_seconds'],
 'next':result['next']}),flush=True)

if __name__=='__main__':
 if len(sys.argv)!=2:raise ValueError('Command: test or jan')
 if sys.argv[1]=='test':test()
 elif sys.argv[1]=='jan':run_january()
 else:raise ValueError(sys.argv[1])
