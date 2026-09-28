"""HOLD_EXIT_022 frozen Jan PARTIAL_VALUE candidate discovery replication.

FEB/MAR only. Widths fixed pre-run to weak=.10,strong=.04 (no calendar,
source data, forward or teacher features), original CAUSAL014 baseline fully
reconstructed and raw PNL plus exit times must match before comparison.
"""
from pathlib import Path
import sys,os,json,hashlib,time
import numpy as np
BASE=Path('/mnt/data');OUT=BASE/'hold022_results';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE/'net024_src'));sys.path.insert(0,str(BASE/'net023_src'));sys.path.insert(0,str(BASE/'hold022_src'))
import net024_h1_permission as N
import r9b_screen as R
from hold022_structural_invalidation import get_x
from hold022_runner_geometry import replay_variant
FROZEN_WEAK_TRAIL=.10; FROZEN_STRONG_TRAIL=.04
EXPECT={2:(32862,28188,18834,-4450.956500020821),3:(41595,35573,24169,-6589.631500026144)}
PARENT_REPLAY_SOURCE_SHA='4a23916632d5591bf1d25107f2b316432d410648fa3a1935f5fff2e483da52f1'

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()

def atomic_json(p,v):
 p=Path(p);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');os.replace(tmp,p)

def run(month:int):
 assert month in [2,3], 'Only FEB/MAR historical discovery replication; April-May-Jul and August forbidden'
 assert sha(BASE/'hold022_src/hold022_runner_geometry.py')==PARENT_REPLAY_SOURCE_SHA
 start=time.perf_counter()
 f=BASE/'net024_results'/f'NET024_RAW_{month:02d}.npz';fm=f.with_suffix('.manifest.json')
 frozen=json.loads(fm.read_text());assert frozen['raw_cache_sha256']==sha(f)
 assert sha(R.RAW_BY_MONTH[month])==frozen['raw_data_sha256']
 with np.load(f,allow_pickle=False) as z:
  e=z['raw_entry_ms'];x=z['raw_exit_ms'];p=z['raw_pnl'];sd=z['raw_side'];al=z['raw_align']
 assert len(e)==EXPECT[month][0]
 t,mid=R.load_ticks(month)
 X=get_x(month,t,mid)
 assert len(X)==len(e) and np.array_equal(X[:,0].astype(np.int64),e)
 assert np.array_equal(X[:,1].astype(np.int8),sd) and np.array_equal(X[:,3].astype(np.int8),al)
 baseline_raw=replay_variant(t,mid,X,.05,.04)
 assert np.array_equal(baseline_raw[:,0],p,equal_nan=True)
 assert np.array_equal(np.where(np.isfinite(baseline_raw[:,4]),baseline_raw[:,4],-1).astype(np.int64),x)
 ib=N.raw_replay(e,x,p,np.ones(len(e),bool));base=N.mtr(p[ib]);
 assert (base['trades'],base['winners'])==EXPECT[month][1:3] and abs(base['net']-EXPECT[month][3])<1e-8
 new_raw=replay_variant(t,mid,X,FROZEN_WEAK_TRAIL,FROZEN_STRONG_TRAIL)
 new_exit=np.where(np.isfinite(new_raw[:,4]),new_raw[:,4],-1).astype(np.int64)
 ic=N.raw_replay(e,new_exit,new_raw[:,0],np.ones(len(e),bool));m=N.mtr(new_raw[ic,0]);
 d={k:m[k]-base[k] for k in ['net','gross_profit','gross_loss','pf','trades','winners','maxdd']}
 wret=100*m['winners']/base['winners'];tret=100*m['trades']/base['trades']
 passed=bool(d['net']>0 and d['gross_profit']>0 and d['gross_loss']>=-.05*abs(base['gross_loss']) and wret>=95 and tret>=95)
 result={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD',
   'stage':'FROZEN_WEAK_ONLY_0P10_DISCOVERY_REPLICATION','status':'COMPLETED_LOCAL',
   'month':month,'august_accessed':False,
   'source_replay_exact_pnl_and_exit_parity':True,
   'rule':{'weak_trail':FROZEN_WEAK_TRAIL,'strong_trail':FROZEN_STRONG_TRAIL,'original_stop_and_activation_unchanged':True},
   'parent':base,'candidate':m,'delta':d,
   'winner_retention_pct':wret,'trade_retention_pct':tret,
   'frozen_partial_monetization_gate_pass':passed,
   'raw_candidates':len(e),'tick_rows':len(t),
   'source_sha256':sha(__file__),'frozen_historical_source_sha256':PARENT_REPLAY_SOURCE_SHA,
   'market_sha256':sha(R.RAW_BY_MONTH[month]),'parent_raw_sha256':sha(f),
   'elapsed_seconds':round(time.perf_counter()-start,3),
   'next':('HOLD_EXIT_022_RUNNER_REPLICATION_MARCH' if month==2 else 'HOLD_EXIT_022_RUNNER_DISCOVERY_VERDICT')}
 dst=OUT/f'HOLD022_RUNNER_REPLICATION_2026_{month:02d}.json';atomic_json(dst,result)
 man=OUT/f'HOLD022_RUNNER_REPLICATION_2026_{month:02d}.manifest.json'
 atomic_json(man,{'status':'COMPLETED_LOCAL','month':month,'original_control_parity_pass':True,
 'raw_source_sha256':result['market_sha256'],'parent_event_sha256':result['parent_raw_sha256'],
 'canonical_replay_source_sha256':PARENT_REPLAY_SOURCE_SHA,
 'replicator_source_sha256':result['source_sha256'],
 'result_sha256':sha(dst),'gate_pass':passed,'next':result['next'],'august_accessed':False})
 print(json.dumps({'month':month,'status':'COMPLETED_LOCAL','frozen_partial_value_pass':passed,
   'parent':base,'candidate':m,'delta':d,'winner_retention_pct':wret,
   'trade_retention_pct':tret,'source_sha256':result['source_sha256'],
   'result_sha256':sha(dst),'manifest_sha256':sha(man),'elapsed_s':result['elapsed_seconds']}),flush=True)

if __name__=='__main__':
 if len(sys.argv)!=2:raise ValueError('month 2 or 3 required')
 run(int(sys.argv[1]))