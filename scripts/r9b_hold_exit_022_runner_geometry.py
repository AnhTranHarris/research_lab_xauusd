"""HOLD_EXIT_022: source-equivalent original trail-geometry research.

January discovery for HARVEST / RUNNER geometry. This is *not* a historical
profitable Gamma_2 restoration claim. We preserve original event generator,
original stop distances, activation threshold, 60s maxhold and original
executable modeled spread, modifying ONLY post-activation trailing distance.

Same raw chronological event population can change outcome/position lifetime;
full account single-position replay is required. Unknown future path is never a
feature. Geometry variants predeclared before reading January outcomes.
"""
from __future__ import annotations
import sys,os,json,hashlib,time
from pathlib import Path
import numpy as np
from numba import njit
BASE=Path('/mnt/data');OUT=BASE/'hold022_results';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE/'net023_src'));sys.path.insert(0,str(BASE/'net024_src'));sys.path.insert(0,str(BASE/'hold022_src'))
import net024_h1_permission as N
import r9b_screen as R
from hold022_structural_invalidation import get_x
WIDTHS=[0.025,0.10,0.20,0.40]
MODES=['weak_only','strong_only','both']
JANGOLDEN=(34362,28088,19087,-4510.0870000207515)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def atomic_json(path,data):
 path=Path(path);tmp=path.with_suffix('.partial.json');tmp.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n');os.replace(tmp,path)

@njit(cache=True)
def replay_variant(t,mid,X,trail_weak,trail_strong):
 """Line-by-line source semantics of CAUSAL014 replay_hybrid except trail width."""
 n=len(X);o=np.empty((n,6),np.float64);H=.10
 for k in range(n):
  sig=int(X[k,0]);side=int(X[k,1]);align=X[k,3]
  if align>=3:
   stopd=1.0;act=.10;trail=trail_strong;maxhold=60;mode=1
  else:
   stopd=3.0;act=.18;trail=trail_weak;maxhold=60;mode=0
  i=np.searchsorted(t,sig)
  if i>=len(t):o[k]=np.nan;continue
  p=mid[i];entry=p+H if side>0 else p-H;bid=p-H;ask=p+H
  stop=bid-stopd if side>0 else ask+stopd;ot=t[i];mfe=0.;mae=0.;done=False
  for j in range(i+1,len(t)):
   tt=t[j];p=mid[j];bid=p-H;ask=p+H
   fav=(bid-entry) if side>0 else (entry-ask)
   adv=(entry-bid) if side>0 else (ask-entry)
   if fav>mfe:mfe=fav
   if adv>mae:mae=adv
   if (side>0 and bid<=stop) or (side<0 and ask>=stop) or tt-ot>=maxhold*1000:
    ex=bid if side>0 else ask
    o[k,0]=(ex-entry)*side;o[k,1]=(tt-ot)/1000.;o[k,2]=mfe;o[k,3]=mae;o[k,4]=tt;o[k,5]=mode;done=True;break
   if fav>=act:
    cand=bid-trail if side>0 else ask+trail
    if side>0:
     if cand>stop:stop=cand
    else:
     if cand<stop:stop=cand
  if not done:o[k]=np.nan
 return o

def test():
 t=np.array([100,200,500,900,1500,2100,3000,60100],dtype=np.int64)
 m=np.array([10.,10.2,10.4,10.25,10.20,10.5,10.1,10.0])
 X=np.array([[100,1,9.0,2],[100,-1,11.0,5]],dtype=np.float64)
 a=replay_variant(t,m,X,.05,.04)
 b=replay_variant(t,m,X,.40,.40)
 assert len(a)==2 and np.all(np.isfinite(a[:,0]))
 assert not np.array_equal(a[:,0],b[:,0]) or not np.array_equal(a[:,4],b[:,4]),'Trail width should be executable'
 assert np.all(a[:,4]>X[:,0])
 print('RUNNER_GEOMETRY_SYNTHETIC_SOURCE_TEST_PASS')

def run_jan():
 test();start=time.perf_counter()
 zfile=BASE/'net024_results/NET024_RAW_01.npz'
 mf=json.loads((BASE/'net024_results/NET024_RAW_01.manifest.json').read_text())
 assert sha(zfile)==mf['raw_cache_sha256'] and sha(R.RAW_BY_MONTH[1])==mf['raw_data_sha256']
 with np.load(zfile,allow_pickle=False) as z:
  e=z['raw_entry_ms'];x=z['raw_exit_ms'];p=z['raw_pnl'];side=z['raw_side'];align=z['raw_align']
 assert len(e)==JANGOLDEN[0]
 t,mid=R.load_ticks(1);X=get_x(1,t,mid)
 assert np.array_equal(X[:,0].astype(np.int64),e)
 assert np.array_equal(X[:,1].astype(np.int8),side) and np.array_equal(X[:,3].astype(np.int8),align)
 control=replay_variant(t,mid,X,.05,.04)
 assert np.array_equal(control[:,0],p,equal_nan=True),'Exact price PNL source parity failed'
 assert np.array_equal(control[:,4].astype(np.int64),x), 'Exact exit-time source parity failed'
 first=N.raw_replay(e,x,p,np.ones(len(e),bool));bm=N.mtr(p[first])
 assert (bm['trades'],bm['winners'])==JANGOLDEN[1:3] and abs(bm['net']-JANGOLDEN[3])<1e-8
 variants=[]
 for width in WIDTHS:
  for mode in MODES:
   w=.05 if mode=='strong_only' else width
   s=.04 if mode=='weak_only' else width
   O=replay_variant(t,mid,X,w,s)
   newex=np.where(np.isfinite(O[:,4]),O[:,4],-1).astype(np.int64)
   ii=N.raw_replay(e,newex,O[:,0],np.ones(len(e),bool))
   metr=N.mtr(O[ii,0]);delts={key:metr[key]-bm[key] for key in ['net','gross_profit','gross_loss','pf','trades','winners','maxdd']}
   variants.append({'trail_width_price':width,'owner_mode':mode,
      'weak_trail_width':w,'strong_trail_width':s,'metrics':metr,
      'delta':delts,'winner_retention_pct':100*metr['winners']/bm['winners'],
      'trade_retention_pct':100*metr['trades']/bm['trades'],
      'source_comparison_count_different_raw_pnl':int(np.count_nonzero(~np.isclose(O[:,0],p,atol=0,rtol=0,equal_nan=True)))})
 shortlist=[v for v in variants if v['delta']['net']>0 and v['delta']['gross_loss']>=0 and v['winner_retention_pct']>=95 and v['trade_retention_pct']>=95]
 monetization=[v for v in variants if v['delta']['net']>0 and v['delta']['gross_profit']>0 and v['delta']['gross_loss']>=-.05*abs(bm['gross_loss']) and v['winner_retention_pct']>=95 and v['trade_retention_pct']>=95]
 result={'status':'COMPLETED_LOCAL','unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD',
 'stage':'JAN_RUNNER_TRAIL_GEOMETRY_SOURCE_EXACT','parent':'CAUSAL_RECERT_014',
 'exact_raw_pnl_and_exit_timestamp_source_parity':True,'month':1,'august_accessed':False,
 'frozen_parameter_grid':{'widths':WIDTHS,'owner_modes':MODES},
 'source_semantics':'original init stop 3.0 weak / 1.0 strong, activate favorable executable +.18 weak/+ .10 strong, 60s maxhold; original entry generator untouched, only post-activation trail distance changed; source-equivalent mid/fixed $0.10 halfspread each side',
 'baseline':bm,'raw_candidates':len(e),'variants':variants,'strict_eligible_count':len(shortlist),
 'strict_eligible':shortlist,'monetization_diagnostic_count':len(monetization),
 'monetization_diagnostics':monetization,
 'strict_gate':'positive net AND no worse GL, winner/trade >=95% Jan, then Feb-Mar replication before April/forward',
 'partial_value_gate':'positive net and GP, <=5% GL deterioration, winner/trade >=95%; retain as diagnostic only until a distinct loss-control complement closes the tail',
 'source_sha256':sha(__file__),'source_data_sha256':sha(R.RAW_BY_MONTH[1]),'base_raw_sha256':sha(zfile),
 'duration_s':round(time.perf_counter()-start,3),
 'next':'FEB_MAR_FROZEN_DISCOVERY_FOR_PREDECLARED_SHORTLIST_IF_ANY_OTHERWISE_REJECT_AND_CLOSE_RUNNER_GRID'}
 dst=OUT/'HOLD022_JAN_RUNNER_TRAIL.json';atomic_json(dst,result)
 manifest=OUT/'HOLD022_JAN_RUNNER_TRAIL_MANIFEST.json'
 atomic_json(manifest,{'status':'COMPLETED_LOCAL','baseline_exact_source_parity_pass':True,
  'source_sha256':sha(__file__),'input_source_sha256':sha(R.RAW_BY_MONTH[1]),
  'parent_cache_sha256':sha(zfile),'result_sha256':sha(dst),
  'variant_count':len(variants),'strict_eligible':len(shortlist),'monetization_diagnostic_count':len(monetization),
  'august_accessed':False,'next':result['next']})
 print(json.dumps({'status':'COMPLETED_LOCAL','source_exact':True,'parent':bm,
 'strict_eligible':len(shortlist),'monetization_diagnostics':len(monetization),
 'top_by_net':sorted(variants,key=lambda v:v['delta']['net'],reverse=True)[:6],
 'source_sha256':result['source_sha256'],'result_sha256':sha(dst),
 'manifest_sha256':sha(manifest),'elapsed_s':result['duration_s']}),flush=True)

if __name__=='__main__':
 if len(sys.argv)!=2:raise ValueError('test or jan')
 if sys.argv[1]=='test':test()
 elif sys.argv[1]=='jan':run_jan()
 else:raise ValueError('not permitted')
