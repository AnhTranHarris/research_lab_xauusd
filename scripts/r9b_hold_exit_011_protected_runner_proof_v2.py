import json,hashlib,argparse,time,sys,itertools
from pathlib import Path
import numpy as np
from numba import njit
R=Path('/mnt/data/r9b_active');sys.path.insert(0,str(R));import gamma014_replay as g
C={m:R/f'R9B_GAMMA_DYNAMIC_HOLD_EXIT_001_{m:02d}_CACHE.npz' for m in (1,2,3)}
B={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_017_{m:02d}_BRIDGE.npz' for m in (1,2,3)}
DISC=R/'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_DISCOVERY.json'
OUT=R/'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_PROTECTED_RUNNER_PROOF.json'
MAN=R/'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_MANIFEST.json'
START=R/'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_STARTED.json'
H=.10
LOCK_ABS=(0.0,.05,.10,.15,.20)
PRE_GB=(.10,.15,.20,.30,.40,.50)
PROOF_PNL=(.30,.40,.50,.60,.75,1.00)
RENEW=(0.0,.05,.10,.20,.30,.50)
MAXH=(5000,8000,10000,15000,20000,30000)
TRAIL=(.15,.20,.25,.30,.40,.50,.75,1.00)
STALE=(0,250,500,750)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def M(p):
 p=np.asarray(p,float);p=p[np.isfinite(p)];n=len(p);w=p>0;gp=float(p[w].sum()) if n else 0.;gl=float(p[p<0].sum()) if n else 0.
 return {'trades':int(n),'winners':int(w.sum()),'win_rate_pct':float(w.mean()*100) if n else 0.,'net':float(p.sum()) if n else 0.,'gp':gp,'gl':gl,'avg':float(p.mean()) if n else None,'pf':float(gp/-gl) if gl<0 else None}
def D(b,c):return {'net_improvement':c['net']-b['net'],'gp_improvement':c['gp']-b['gp'],'gl_change':c['gl']-b['gl'],'winner_delta':c['winners']-b['winners'],'winner_retention_pct':c['winners']/max(b['winners'],1)*100}
def load(m):
 z=np.load(C[m],allow_pickle=False);d={k:z[k] for k in z.files};z.close();b=np.load(B[m],allow_pickle=False);d['X']=b['X'].copy();b.close();return d

@njit(cache=True)
def simulate(t,mid,sig,fade,action,idx,lock_abs,pre_gb,proof_pnl,renew,max_ms,trail,stale):
 out=np.full(len(idx),np.nan);reason=np.zeros(len(idx),np.int8)
 for ii in range(len(idx)):
  q=int(idx[ii]);a=int(action[q]);fs=int(fade[q]);side=fs if a==1 else -fs;s=int(sig[q]);ie=np.searchsorted(t,s,side='left')
  if ie>=len(t):continue
  m0=mid[ie];j1=np.searchsorted(t,s+1000,side='right')-1
  if j1<ie:j1=ie
  bank1=side*(mid[j1]-m0)-2*H; floor=max(lock_abs,bank1-pre_gb); peak=bank1; lastpeak=s+1000
  start=np.searchsorted(t,s+1000,side='right');end2=np.searchsorted(t,s+2000,side='right');stopped=False;ep2=bank1
  for k in range(start,end2):
   ep=side*(mid[k]-m0)-2*H;ep2=ep
   if ep>peak+1e-12:peak=ep;lastpeak=int(t[k])
   if ep<=floor:
    out[ii]=ep;reason[ii]=1;stopped=True;break
  if stopped:continue
  j2=end2-1
  if j2<j1:j2=j1
  ep2=side*(mid[j2]-m0)-2*H
  if not (ep2>=proof_pnl and (peak-bank1)>=renew):
   out[ii]=ep2;reason[ii]=2;continue
  end=np.searchsorted(t,s+max_ms,side='right');start2=end2;exitp=np.nan
  for k in range(start2,end):
   ep=side*(mid[k]-m0)-2*H
   if ep>peak+1e-12:peak=ep;lastpeak=int(t[k])
   dyn=max(lock_abs,peak-trail)
   if ep<=dyn and (int(t[k])-lastpeak)>=stale:
    exitp=ep;reason[ii]=3;break
  if not np.isfinite(exitp):
   last=end-1
   if last<ie:last=ie
   exitp=side*(mid[last]-m0)-2*H;reason[ii]=4
  out[ii]=exitp
 return out,reason

def eval_rule(base,vals,mask):
 use=mask&np.isfinite(vals);b=M(base[use]);c=M(vals[use]);return {'base':b,'candidate':c,'delta':D(b,c),'count':int(use.sum())}

def started():
 d=load(1);obj={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_RUNNER_FEATURE_REBUILD','status':'STARTED','parent':'HOLD_EXIT005 + frozen ENTRY017-024 ownership','mechanism':'Protected STRONG_RUNNER extension. At +1s establish a profit-lock floor while waiting to +2s. Only if +2s executable P/L and new-MFE renewal prove persistence does the trade enter a longer runner with peak-giveback trail; otherwise stop/exit causally.','discovery_window':'January days0-6 fit / days7-13 validate','inputs':{'hold_exit_001_cache_sha256':sha(C[1]),'entry017_bridge_sha256':sha(B[1])},'source_sha256':sha(__file__),'target_outputs':[DISC.name],'resume_pointer':'run phase discover','august_accessed':False};START.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))

def discover_chunk(maxh):
 t0=time.time();d=load(1);sm=d['state']==1;day=d['day_idx'];h=d['horiz_ms'];j1=int(np.where(h==1000)[0][0]);base=d['horizon_pnl'][:,j1];fit=sm&(day<7);val=sm&(day>=7)&(day<14);idx=np.where(sm&(day<14))[0].astype(np.int64);t,mid=g.load_ticks(1);rows=[]
 for lock_abs,pre_gb,proof_pnl,renew,trail,stale in itertools.product(LOCK_ABS,PRE_GB,PROOF_PNL,RENEW,TRAIL,STALE):
  vals0,_=simulate(t,mid,d['X'][:,0].astype(np.int64),d['X'][:,1].astype(np.int8),d['entry_action'].astype(np.int8),idx,float(lock_abs),float(pre_gb),float(proof_pnl),float(renew),int(maxh),float(trail),int(stale));vals=np.full(len(sm),np.nan);vals[idx]=vals0
  ef=eval_rule(base,vals,fit);ev=eval_rule(base,vals,val);wr=min(ef['delta']['winner_retention_pct'],ev['delta']['winner_retention_pct'])
  ok=(ef['delta']['net_improvement']>0 and ev['delta']['net_improvement']>0 and ef['delta']['gp_improvement']>0 and ev['delta']['gp_improvement']>0 and wr>=95)
  if ok or (ef['delta']['net_improvement']>0 and ev['delta']['net_improvement']>0):
   rows.append({'lock_abs':lock_abs,'pre_giveback':pre_gb,'proof_pnl_2s':proof_pnl,'renewal_from_1s':renew,'max_horizon_ms':int(maxh),'trail':trail,'stale_ms':stale,'fit':ef,'validation':ev,'eligible':ok,'min_net':min(ef['delta']['net_improvement'],ev['delta']['net_improvement']),'sum_net':ef['delta']['net_improvement']+ev['delta']['net_improvement'],'min_gp':min(ef['delta']['gp_improvement'],ev['delta']['gp_improvement']),'min_winner_retention':wr})
 elig=[r for r in rows if r['eligible']];best=max(elig,key=lambda r:(r['min_net'],r['sum_net'],r['min_gp'],r['min_winner_retention'])) if elig else None
 out={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_RUNNER_FEATURE_REBUILD','phase':'DISCOVERY_CHUNK','max_horizon_ms':int(maxh),'status':'COMPLETED_LOCAL_DISCOVERY_CHUNK','evaluated_grid_size':len(LOCK_ABS)*len(PRE_GB)*len(PROOF_PNL)*len(RENEW)*len(TRAIL)*len(STALE),'retained_rows':len(rows),'eligible_count':len(elig),'best':best,'rows':rows,'august_accessed':False,'elapsed_s':time.time()-t0}
 q=R/f'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_DISCOVERY_CHUNK_{int(maxh)}.json';q.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'max_horizon_ms':int(maxh),'evaluated_grid_size':out['evaluated_grid_size'],'retained_rows':len(rows),'eligible_count':len(elig),'best':best,'chunk_sha256':sha(q),'elapsed_s':out['elapsed_s']},indent=2))

def consolidate():
 chunks=[];rows=[]
 for mh in MAXH:
  q=R/f'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_DISCOVERY_CHUNK_{int(mh)}.json'
  if not q.exists():raise RuntimeError(f'missing chunk {mh}')
  x=json.load(open(q));chunks.append({'max_horizon_ms':int(mh),'sha256':sha(q),'eligible_count':x['eligible_count'],'retained_rows':x['retained_rows']});rows.extend(x['rows'])
 elig=[r for r in rows if r['eligible']];best=max(elig,key=lambda r:(r['min_net'],r['sum_net'],r['min_gp'],r['min_winner_retention'])) if elig else None
 out={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_RUNNER_FEATURE_REBUILD','phase':'DISCOVERY','status':'COMPLETED_LOCAL_DISCOVERY','parent':'HOLD_EXIT005 + frozen ENTRY017-024 ownership','mechanism':'Protected +1s→+2s proof then stateful runner extension for STRONG_RUNNER. No future data enters decisions.','selection_contract':'Jan days0-6 / days7-13. Require positive net+GP in both halves and >=95% winner retention.','chunks':chunks,'evaluated_grid_size':sum(json.load(open(R/f'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_DISCOVERY_CHUNK_{int(mh)}.json'))['evaluated_grid_size'] for mh in MAXH),'retained_rows':len(rows),'eligible_count':len(elig),'best':best,'top':sorted(rows,key=lambda r:(r['eligible'],r['min_net'],r['sum_net'],r['min_gp']),reverse=True)[:30],'next':'REPLICATE' if best else 'REBUILD','august_accessed':False};DISC.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'evaluated_grid_size':out['evaluated_grid_size'],'eligible_count':len(elig),'best':best,'result_sha256':sha(DISC)},indent=2))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['started','discover_chunk','consolidate']);ap.add_argument('--maxh',type=int);a=ap.parse_args();
 if a.phase=='started':started()
 elif a.phase=='discover_chunk':assert a.maxh in MAXH;discover_chunk(a.maxh)
 else:consolidate()
