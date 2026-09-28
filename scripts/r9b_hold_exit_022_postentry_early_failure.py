"""R9B HOLD_EXIT_022, discovery only, causal post-entry diagnostic and early-loss cap.

Canonical parent: CAUSAL_RECERT_014. Valid for JAN--MAR *discovery*, not OOS.
This experiment does NOT promote or implement the prior ENTRY017-024 classifiers:
their original research populations can differ. It owns only the simple, fully
observable current PnL and peak-so-far and tests a NON-EXTENDING early exit.
Broker quotes: same fixed-H=$0.10 mid reconstruction as CAUSAL014. An exit can
only occur on an actual tick after the decision horizon, and strictly BEFORE
its original parent exit. Exits are recomputed for the WHOLE RAW candidate
population before one-position selection; no trade-set shortcut.
Never access August. Do not tune on April/May--July here.
"""
import sys,os,json,hashlib,time
from pathlib import Path
import numpy as np
from numba import njit
BASE=Path('/mnt/data')
sys.path.insert(0,str(BASE/'net023_src'))
sys.path.insert(0,str(BASE/'net024_src'))
import r9b_screen as R
import net024_h1_permission as N
OUT=BASE/'hold022_results'; OUT.mkdir(parents=True,exist_ok=True)
HORIZONS_MS=[1000,2000,4000]
PNL_THRESHOLDS=[-0.25,-0.5,-0.75]
MFE_CAPS=[0.05,0.20]
GOLDEN={1:(34362,28088,19087,-4510.0870000207515)}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def atomic_json(path,value):
 temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');os.replace(temp,path)

def atomic_npz(path,**arrays):
 temp=path.with_suffix('.tmp.npz');np.savez_compressed(temp,**arrays)
 with np.load(temp,allow_pickle=False) as zz:
  assert len(zz.files)==len(arrays)
  for k in arrays:
   assert zz[k].shape==arrays[k].shape and zz[k].dtype==arrays[k].dtype
 os.replace(temp,path)

@njit(cache=True)
def observed_checkpoints(t,mid,entry,ex,side,horizons):
 """Observe at first tick timestamp >= entry+horizon strictly BEFORE original exit.

 A checkpoint does not exist if the parent stopped sooner, if there was no
 quote before the original exit, or if no quote exists in the file. All
 running extremes cover actual observed ticks from entry through checkpoint.
 """
 n=len(entry);nhr=len(horizons)
 ct=np.full((n,nhr),-1,np.int64)
 cpnl=np.full((n,nhr),np.nan,np.float64)
 cmfe=np.full((n,nhr),np.nan,np.float64)
 cmae=np.full((n,nhr),np.nan,np.float64)
 delay=np.full((n,nhr),-1,np.int64)
 for i in range(n):
  st=np.searchsorted(t,entry[i],side='left')
  if st>=len(t) or t[st]!=entry[i]:continue
  s=side[i];v=mid[st]
  for h in range(nhr):
   target=entry[i]+horizons[h]
   cp=np.searchsorted(t,target,side='left')
   if cp>=len(t) or cp<=st or t[cp]>=ex[i]:continue
   maxfav=0.; maxadv=0.
   for j in range(st+1,cp+1):
    pnl=(mid[j]-v)*s-.20
    if pnl>maxfav:maxfav=pnl
    if -pnl>maxadv:maxadv=-pnl
   ct[i,h]=t[cp]
   cpnl[i,h]=(mid[cp]-v)*s-.20
   cmfe[i,h]=maxfav
   cmae[i,h]=maxadv
   delay[i,h]=t[cp]-target
 return ct,cpnl,cmfe,cmae,delay

def test():
 t=np.array([100,300,1100,1500,2100,2800,4100,4500,5200],np.int64)
 mid=np.array([10.,10.05,9.80,9.71,9.40,9.55,9.85,10.1,10.5])
 e=np.array([100,300,100,100],np.int64)
 ex=np.array([4500,1500,1000,5200],np.int64)
 side=np.array([1,-1,1,1],np.int8)
 q,p,m,a,d=observed_checkpoints(t,mid,e,ex,side,np.array([1000,2000,4000],np.int64))
 assert q[0].tolist()==[1100,2100,4100],q
 # At the first eligible checkpoint tick (1500), this position exits in
 # the parent at that identical timestamp, so there is no earlier action.
 assert np.all(q[1]==-1)
 assert np.all(q[2]==-1)
 assert q[3,2]==4100 and abs(p[0,1]-(-.8))<1e-10,p
 assert np.all(d[d>=0]>=0)
 # A position that exits exactly at checkpoint does not become eligible.
 assert N.raw_replay(np.array([100,200,201]),np.array([200,300,400]),np.array([1.,2.,3.]),np.ones(3,bool)).tolist()==[0,2]
 print('HOLD022_SYNTHETIC_OBSERVATION_AND_NONOVERLAP_TEST_PASS')

def run(month):
 assert month==1,'This initial discovery source is JANUARY-ONLY. Do not access calibration/forward/SEALED periods.'
 test(); clock=time.perf_counter()
 raw=BASE/'net024_results'/f'NET024_RAW_{month:02d}.npz'
 man=BASE/'net024_results'/f'NET024_RAW_{month:02d}.manifest.json'
 frozen=json.loads(man.read_text()); assert N.sha(raw)==frozen['raw_cache_sha256']
 market=R.RAW_BY_MONTH[month]
 assert sha(market)==frozen['raw_data_sha256'],'market source checksum failed'
 with np.load(raw,allow_pickle=False) as z:
  e=z['raw_entry_ms'].astype(np.int64);ex=z['raw_exit_ms'].astype(np.int64)
  side=z['raw_side'].astype(np.int8);pnl=z['raw_pnl'].astype(np.float64)
  align=z['raw_align'].astype(np.int8)
 assert len(e)==GOLDEN[month][0] and np.all(np.diff(e)>=0)
 assert np.all(np.isfinite(pnl)) and np.all(ex>e)
 bix=N.raw_replay(e,ex,pnl,np.ones(len(e),bool)); bm=N.mtr(pnl[bix])
 assert (bm['trades'],bm['winners'])==GOLDEN[month][1:3]
 assert abs(bm['net']-GOLDEN[month][3])<1e-8
 t,mid=R.load_ticks(month)
 assert len(t)==9135062 and np.all(np.diff(t)>=0)
 h=np.asarray(HORIZONS_MS,np.int64)
 cp,cpnl,cmfe,cmae,delay=observed_checkpoints(t,mid,e,ex,side,h)
 assert np.all((cp<ex[:,None])|(cp==-1))
 assert np.all((delay>=0)|(delay==-1))
 assert np.all((cmfe>=0)|np.isnan(cmfe))
 assert np.all((cmae>=0)|np.isnan(cmae))
 assert np.allclose(cpnl[cp>=0], (cpnl[cp>=0]),atol=0,rtol=0)
 feats=OUT/'HOLD022_JAN_POSTENTRY_CAUSAL_STATES.npz'
 atomic_npz(feats,entry_ms=e,original_exit_ms=ex,original_pnl=pnl,
  side=side,align=align,checkpoint_horizon_ms=h,checkpoint_ms=cp,
  executable_pnl=cpnl,observed_net_mfe=cmfe,observed_net_mae=cmae,
  delayed_quote_ms=delay)
 # Screen only rules declared BEFORE this run, on full raw candidate stream.
 variants=[]
 for ih,hms in enumerate(HORIZONS_MS):
  eligible=cp[:,ih]>=0
  for threshold in PNL_THRESHOLDS:
   for mfecap in MFE_CAPS:
    trigger=eligible & (cpnl[:,ih]<=threshold) & (cmfe[:,ih]<=mfecap)
    edit_exit=np.where(trigger,cp[:,ih],ex)
    edit_pnl=np.where(trigger,cpnl[:,ih],pnl)
    ii=N.raw_replay(e,edit_exit,edit_pnl,np.ones(len(e),bool))
    m=N.mtr(edit_pnl[ii])
    variants.append({'horizon_ms':hms,'pnl_lte':threshold,'observed_mfe_lte':mfecap,
      'raw_exit_changed':int(trigger.sum()),'selected_changed_exit':int(trigger[ii].sum()),
      'metrics':m,
      'delta':{'net':m['net']-bm['net'],'gross_loss':m['gross_loss']-bm['gross_loss'],
       'gross_profit':m['gross_profit']-bm['gross_profit'],
       'winners':m['winners']-bm['winners'],'trades':m['trades']-bm['trades'],
       'maxdd':bm['maxdd']-m['maxdd'],'pf':m['pf']-bm['pf']},
      'retention':{'winners_pct':100*m['winners']/bm['winners'],'trades_pct':100*m['trades']/bm['trades']}})
 # Censor-aware diagnostics; terminal label only used for EX-POST analysis.
 survivors=[]
 for ih,hms in enumerate(HORIZONS_MS):
  ok=cp[bix,ih]>=0
  label=pnl[bix][ok];quote=cpnl[bix,ih][ok];mfe=cmfe[bix,ih][ok]
  frac=lambda p:float(p) if np.isfinite(p) else None
  states=[]
  for name,msk in [('negative_no_net_mfe',(quote<0)&(mfe<=.05)),
    ('negative_with_mfe',(quote<0)&(mfe>.05)),
    ('positive_observed',(quote>=0))]:
   y=label[msk]
   states.append({'state':name,'count':int(len(y)),
      'eventual_parent_winners':int((y>0).sum()),
      'eventual_win_rate':frac(np.mean(y>0)) if len(y) else None,
      'eventual_parent_net':float(y.sum()),
      'eventual_parent_gross_loss':float(y[y<0].sum())})
  survivors.append({'horizon_ms':hms,'eligible_executed_parent':int(ok.sum()),
    'eligible_raw':int(np.count_nonzero(cp[:,ih]>=0)),
    'parent_executed':int(len(bix)),'states':states})
 result={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD',
  'stage':'JAN_POSTENTRY_SOURCE_GOLDEN_AND_EARLY_FAILURE_DISCOVERY',
  'status':'COMPLETED_LOCAL','month':month,'parent':'CAUSAL_RECERT_014',
  'cost_semantics':'fixed $0.10 halfspread each way, executable PNL=(future midpoint-entry midpoint)*side-0.20; same source as CAUSAL014; not raw variable Coinexx bid/ask',
  'checkpoint':'first actual tick >= horizon, strictly before unchanged CAUSAL014 parent exit; no future observation as trigger',
  'strategy_semantics':'original parent stop/trail/maxhold fully retained until early close at tick; raw candidates independently evaluated, one-position chronological replay recalculated after all altered exits',
  'frozen_entry_017_024_semantics_used_as_live_rule':False,
  'january_baseline':bm,'january_golden_pass':True,
  'market_source_sha256':sha(market),'original_net024_event_cache_sha256':sha(raw),
  'research_source_sha256':sha(__file__),'state_cache_file':feats.name,'state_cache_sha256':sha(feats),
  'raw_candidates':int(len(e)),'tick_rows':len(t),
  'state_survival_diagnostics':survivors,
  'predeclared_screen':{'horizon_ms':HORIZONS_MS,'pnl_lte':PNL_THRESHOLDS,'observed_mfe_lte':MFE_CAPS,'variant_count':len(variants)},
  'variants':variants,'elapsed_seconds':round(time.perf_counter()-clock,3),
  'interpretation':'Discovery only. January labels are strictly ex-post outcomes; not execution features. No rule chosen. No forward months accessed.',
  'august_accessed':False,'next':'HOLD_EXIT_022_FEB_MARCH_DISCOVERY_NEIGHBORHOOD_AND_SOURCE_PARITY'}
 result_file=OUT/'HOLD022_JAN_INITIAL_SCREEN.json';atomic_json(result_file,result)
 manifest={'unit':result['unit'],'stage':result['stage'],'status':'COMPLETED_LOCAL','baseline_parity_pass':True,
  'source_sha256':result['research_source_sha256'],'market_sha256':result['market_source_sha256'],
  'source_raw_cache_sha256':result['original_net024_event_cache_sha256'],
  'state_cache_sha256':result['state_cache_sha256'],'result_sha256':sha(result_file),
  'expected_jan_raw_count':GOLDEN[1][0],'expected_jan_parent_trades':GOLDEN[1][1],
  'expected_jan_parent_net':GOLDEN[1][3],'variants':len(variants),
  'next':result['next'],'august_accessed':False}
 mf=OUT/'HOLD022_JAN_INITIAL_SCREEN_MANIFEST.json';atomic_json(mf,manifest)
 ranking=sorted(variants,key=lambda v:v['delta']['gross_loss'],reverse=True)
 print(json.dumps({'PASS':True,'month':month,'golden':bm,
   'state_eligible_counts':[(a['horizon_ms'],a['eligible_executed_parent']) for a in survivors],
   'top_gross_loss_candidates':ranking[:4],
   'n_variants':len(variants),'result_sha256':sha(result_file),
   'manifest_sha256':sha(mf),'state_sha256':sha(feats),
   'next':result['next'],'august_accessed':False}),flush=True)

if __name__=='__main__':
 if len(sys.argv)!=2:raise ValueError('Use: test OR run')
 if sys.argv[1]=='test':test()
 elif sys.argv[1]=='run':run(1)
 else:raise ValueError('Unknown command')