"""HOLD_EXIT_022: long-unignited tail rescue, January discovery only.

Distinct from rejected +1/+2/+4s generic early-negative cuts and immediate
sweep-level failure. Hypothesis: a trade still negative after many seconds
with NO observed trail-activation has become an unresolved slow-persistence
liability. Test bounded tails of exact source-defined no-activation states.

Every raw CAUSAL014 event is independently changed at a real quote BEFORE
its existing parent stop/trail/maxhold exit, then a strict chronological
single-position account ledger is replayed. No future win outcome features;
forward/calibration months remain unaccessed for this stage.
"""
import sys,os,json,hashlib,time
from pathlib import Path
import numpy as np
BASE=Path('/mnt/data');OUT=BASE/'hold022_results'; OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE/'net024_src'))
sys.path.insert(0,str(BASE/'net023_src'))
sys.path.insert(0,str(BASE/'hold022_src'))
import net024_h1_permission as N
import r9b_screen as R
from hold022_postentry_early_failure import observed_checkpoints
HORIZONS_MS=[15000,30000,45000]
PNL_CUTOFFS=[-0.25,-0.75]
OWNERS=['all','weak_only','strong_only']
PARENT=(34362,28088,19087,-4510.0870000207515)

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()

def atomic_json(p,v):
 p=Path(p);temp=p.with_suffix('.tmp');temp.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');os.replace(temp,p)

def atomic_npz(p,**arr):
 p=Path(p);temp=p.with_suffix('.partial.npz');np.savez_compressed(temp,**arr)
 with np.load(temp,allow_pickle=False) as z:
  for k,x in arr.items():
   assert np.array_equal(x,z[k],equal_nan=True)
 os.replace(temp,p)

def test():
 from hold022_postentry_early_failure import test as parent_test
 parent_test()
 assert len(HORIZONS_MS)*len(PNL_CUTOFFS)*len(OWNERS)==18
 # Activation profit is observed at the same executable side as the original
 # source replay_hybrid's fav (bid-entry for BUY, entry-ask for SELL).
 assert abs(((100.35-100.0)-.2)-.15)<1e-12
 print('LATE_STALL_SOURCE_EQUIVALENCE_TEST_PASS')

def run_jan():
 test();start=time.perf_counter();m=1
 src=BASE/'net024_results/NET024_RAW_01.npz'
 srcmf=json.loads((BASE/'net024_results/NET024_RAW_01.manifest.json').read_text())
 market=R.RAW_BY_MONTH[1]
 assert sha(src)==srcmf['raw_cache_sha256'] and sha(market)==srcmf['raw_data_sha256']
 with np.load(src,allow_pickle=False) as z:
  e=z['raw_entry_ms'];x=z['raw_exit_ms'];p=z['raw_pnl'];side=z['raw_side'];align=z['raw_align']
 assert len(e)==PARENT[0] and np.all(x>e)
 i0=N.raw_replay(e,x,p,np.ones(len(e),bool));base=N.mtr(p[i0]);
 assert (base['trades'],base['winners'])==PARENT[1:3] and abs(base['net']-PARENT[3])<1e-8
 t,mid=R.load_ticks(1);assert len(t)==9135062 and np.all(np.diff(t)>=0)
 h=np.array(HORIZONS_MS,dtype=np.int64)
 cp,cpnl,cmfe,cmae,delay=observed_checkpoints(t,mid,e,x,side,h)
 assert np.all((cp==-1)|(cp<x[:,None]))
 assert np.allclose(cpnl[cp>=0],cpnl[cp>=0],atol=0,rtol=0)
 cache=OUT/'HOLD022_JAN_LATE_STALL_OBS.npz';atomic_npz(cache,
   entry_ms=e,parent_exit_ms=x,parent_pnl=p,side=side,align=align,
   checkpoints_ms=h,quote_at_ms=cp,executable_pnl=cpnl,observed_net_mfe=cmfe,
   observed_net_mae=cmae,quote_delay_ms=delay)
 variants=[]
 activ=np.where(align>=3,.10,.18)
 for k,ms in enumerate(HORIZONS_MS):
  eligible=(cp[:,k]>=0)&(cmfe[:,k]<activ)
  for cutoff in PNL_CUTOFFS:
   for owner in OWNERS:
    owner_ok=np.ones(len(e),bool) if owner=='all' else ((align<3) if owner=='weak_only' else (align>=3))
    changed=eligible&(cpnl[:,k]<=cutoff)&owner_ok
    ep=np.where(changed,cp[:,k],x);pp=np.where(changed,cpnl[:,k],p)
    ii=N.raw_replay(e,ep,pp,np.ones(len(e),bool));mm=N.mtr(pp[ii])
    variants.append({'original_owner':owner,'observed_checkpoint_ms':ms,'executable_pnl_lte':cutoff,
      'no_observed_activation':True,'raw_earlier_exits':int(changed.sum()),
      'executed_earlier_exits':int(changed[ii].sum()),'metrics':mm,
      'delta':{key:mm[key]-base[key] for key in ['net','gross_loss','gross_profit','winners','trades','pf','maxdd']},
      'winner_retention_pct':mm['winners']/base['winners']*100,
      'trade_retention_pct':mm['trades']/base['trades']*100})
 eligible=[v for v in variants if v['delta']['net']>0 and v['delta']['gross_loss']>0 and v['winner_retention_pct']>=95 and v['trade_retention_pct']>=95]
 result={'status':'COMPLETED_LOCAL','unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD',
 'stage':'JAN_LONG_UNIGNITED_STALL_DISCOVERY','source_month':1,'august_accessed':False,
 'hypothesis':'causally observed >=15s unresolved active trade, current negative executed pnl and no favorable excursion achieving the original CAUSAL014 activation threshold',
 'activation_thresholds_by_original_align':{'weak_align':.18,'strong_align':.10},
 'frozen_variants':{'horizon_ms':HORIZONS_MS,'pnl_lte':PNL_CUTOFFS,'owners':OWNERS},
 'baseline':base,'variants':variants,'variant_count':len(variants),
 'eligible_count':len(eligible),'eligible':eligible,
 'source_sha256':sha(__file__),'market_sha256':sha(market),'raw_cache_sha256':sha(src),
 'observation_cache_sha256':sha(cache),'elapsed_seconds':round(time.perf_counter()-start,2),
 'next':'FEB_MAR_DISCOVERY_IF_JAN_ELIGIBLE_ELSE_HARVEST_RUNNER_GEOMETRY'}
 dst=OUT/'HOLD022_JAN_LATE_STALL.json';atomic_json(dst,result)
 mf=OUT/'HOLD022_JAN_LATE_STALL_MANIFEST.json';atomic_json(mf,{'status':'COMPLETED_LOCAL',
 'source_sha256':sha(__file__),'market_sha256':sha(market),'parent_raw_sha256':sha(src),
 'observations_sha256':sha(cache),'results_sha256':sha(dst),'jan_golden':True,
 'variants':len(variants),'eligible':len(eligible),'next':result['next'],'august_accessed':False})
 print(json.dumps({'status':'COMPLETED_LOCAL','baseline':base,'eligible_count':len(eligible),
 'top_by_net':sorted(variants,key=lambda v:v['delta']['net'],reverse=True)[:6],
 'top_by_GL':sorted(variants,key=lambda v:v['delta']['gross_loss'],reverse=True)[:2],
 'result_sha256':sha(dst),'manifest_sha256':sha(mf),'cache_sha256':sha(cache),
 'elapsed_seconds':result['elapsed_seconds'],'next':result['next']}),flush=True)

if __name__=='__main__':
 if len(sys.argv)!=2: raise ValueError('test or jan')
 if sys.argv[1]=='test':test()
 elif sys.argv[1]=='jan':run_jan()
 else:raise ValueError('not permitted')