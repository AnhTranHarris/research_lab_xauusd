import json, hashlib, time, sys
from pathlib import Path
import numpy as np
from numba import njit
R=Path('/mnt/data/r9b_active'); sys.path.insert(0,str(R)); import gamma014_replay as g
P={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_018_{m:02d}_POST1.npz' for m in (1,2,3)}
B17={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_017_{m:02d}_BRIDGE.npz' for m in (1,2,3)}
MODEL=R/'R9B_GAMMA_DYNAMIC_ENTRY_019_RECOVERY_RUNNER_MODEL.json'
OUT=R/'R9B_GAMMA_DYNAMIC_ENTRY_020_RECOVERY_RUNNER_TIMING_STATE.json'
MAN=R/'R9B_GAMMA_DYNAMIC_ENTRY_020_MANIFEST.json'
STRONG=0.27175000309944153
CHECK_MS=np.array([1250,1500,2000,2500,3000,4000,5000],np.int64)
H=.10

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def tree_apply(X, model):
 tr=model['tree'];cl=np.array(tr['children_left']);cr=np.array(tr['children_right']);ft=np.array(tr['feature']);th=np.array(tr['threshold']);probs=np.array(tr['class_probability']);thr=float(tr['probability_threshold'])
 out=np.zeros(len(X),np.bool_);pr=np.full(len(X),np.nan)
 for i in range(len(X)):
  if not np.all(np.isfinite(X[i])):continue
  n=0
  while cl[n]!=-1:n=cl[n] if X[i,ft[n]]<=th[n] else cr[n]
  p=float(probs[n,1]);pr[i]=p;out[i]=p>=thr
 return out,pr

@njit(cache=True)
def checkpoints(t,mid,sig,fade_side,entry_action):
 n=len(sig);K=len(CHECK_MS);E=np.full((n,K),np.nan);R=np.full((n,K,6),np.nan)
 for q in range(n):
  a=int(entry_action[q])
  if a==0:continue
  fs=int(fade_side[q]);side=fs if a==1 else -fs;s=int(sig[q]);ie=np.searchsorted(t,s,side='left')
  if ie>=len(t):continue
  m0=mid[ie];start=np.searchsorted(t,s+1000,side='right')
  for j in range(K):
   end=np.searchsorted(t,s+CHECK_MS[j],side='right');last=end-1
   if last<ie:last=ie
   final=side*(mid[last]-m0);E[q,j]=final-2*H
   if end<=start:
    R[q,j,0]=E[q,j];R[q,j,1]=0.;R[q,j,2]=0.;R[q,j,3]=0.;R[q,j,4]=0.;R[q,j,5]=0.;continue
   mx=-1e18;mn=1e18;travel=0.;prev=side*(mid[start]-m0);turns=0;ps=0;lastfav=s+1000
   for k in range(start,end):
    d=side*(mid[k]-m0)
    if d>mx:mx=d;lastfav=int(t[k])
    if d<mn:mn=d
    if k>start:
     step=d-prev;travel+=abs(step);sg=1 if step>0 else (-1 if step<0 else 0)
     if sg!=0:
      if ps!=0 and sg!=ps:turns+=1
      ps=sg
    prev=d
   R[q,j,0]=E[q,j];R[q,j,1]=mx-final;R[q,j,2]=final-mn;R[q,j,3]=final/(travel+1e-9);R[q,j,4]=turns;R[q,j,5]=(s+CHECK_MS[j]-lastfav)/1000.
 return E,R

def load_state(m,model):
 z=np.load(P[m],allow_pickle=False);d={k:z[k] for k in z.files};z.close();b=np.load(B17[m],allow_pickle=False);d['X']=b['X'].copy();b.close()
 a=d['entry_action'];p1=d['post1'];ign=(a!=0)&(p1[:,23]>0)&np.all(np.isfinite(p1),1);weak=ign&(p1[:,23]<=STRONG)
 inds=model['tree']['feature_indexes'];rec,prob=tree_apply(p1[:,inds],model);rr=weak&rec
 return d,ign,rr,prob

def summarize(E,mask):
 x=E[mask];n=len(x);out={'count':int(n)}
 if n==0:return out
 pos=x>0
 out['checkpoint_positive_pct']={str(ms):float(pos[:,j].mean()*100) for j,ms in enumerate(CHECK_MS)}
 onset=[]
 for r in range(n):
  k=-1
  for j in range(len(CHECK_MS)):
   if np.all(pos[r,j:]):k=j;break
  onset.append(k)
 onset=np.array(onset)
 out['durable_positive_by_checkpoint_pct']={str(ms):float(((onset>=0)&(onset<=j)).mean()*100) for j,ms in enumerate(CHECK_MS)}
 out['never_durable_positive_pct']=float((onset<0).mean()*100)
 out['durable_onset_distribution_pct']={str(ms):float((onset==j).mean()*100) for j,ms in enumerate(CHECK_MS)}
 out['dip_below_zero_after_1s_pct']=float((~pos[:,:-1]).any(axis=1).mean()*100)
 out['positive_at_5s_pct']=float(pos[:,-1].mean()*100)
 return out

def causal_threshold_screen(Rfeat,E,mask):
 rows=[]
 for j,ms in enumerate(CHECK_MS[:-1]):
  x=Rfeat[:,j,:];y=E[:,-1]>0;use=mask&np.all(np.isfinite(x),1)
  if use.sum()<20:continue
  for pnl in (-.10,0,.05,.10,.15,.20,.30):
   for gb in (.05,.10,.20,.30,.50,1.0):
    sel=use&(x[:,0]>=pnl)&(x[:,1]<=gb)
    if sel.sum()<10:continue
    rows.append({'checkpoint_ms':int(ms),'pnl_min':pnl,'giveback_max':gb,'count':int(sel.sum()),'coverage_pct':float(sel.sum()/use.sum()*100),'future5_accuracy_pct':float(y[sel].mean()*100),'future5_recall_pct':float((y&sel).sum()/(y&use).sum()*100) if (y&use).sum() else 0.})
 return rows

def main():
 t0=time.time();model=json.load(open(MODEL));D={}
 for m in (1,2,3):
  d,ign,rr,prob=load_state(m,model);t,mid=g.load_ticks(m);E,Rf=checkpoints(t,mid,d['X'][:,0].astype(np.int64),d['X'][:,1].astype(np.int8),d['entry_action']);D[m]=(d,rr,E,Rf)
 timing={}
 for m,(d,rr,E,Rf) in D.items():
  mask=rr&((d['day_idx']>=14) if m==1 else np.ones(len(rr),bool));timing[str(m)]=summarize(E,mask)
 d1,rr1,E1,R1=D[1];train=rr1&(d1['day_idx']<7);val=rr1&(d1['day_idx']>=7)&(d1['day_idx']<14)
 rows=causal_threshold_screen(R1,E1,train);viable=[]
 for r in rows:
  j=int(np.where(CHECK_MS==r['checkpoint_ms'])[0][0]);x=R1[:,j,:];use=val&np.all(np.isfinite(x),1);sel=use&(x[:,0]>=r['pnl_min'])&(x[:,1]<=r['giveback_max']);y=E1[:,-1]>0
  if sel.sum()<8:continue
  v={'checkpoint_ms':r['checkpoint_ms'],'pnl_min':r['pnl_min'],'giveback_max':r['giveback_max'],'val_count':int(sel.sum()),'val_coverage_pct':float(sel.sum()/use.sum()*100),'val_5s_accuracy_pct':float(y[sel].mean()*100),'val_5s_recall_pct':float((y&sel).sum()/(y&use).sum()*100) if (y&use).sum() else 0.}
  if v['val_coverage_pct']>=35 and v['val_5s_recall_pct']>=60:viable.append(v)
 best=max(viable,key=lambda q:(q['val_5s_accuracy_pct'],q['val_5s_recall_pct'],q['val_coverage_pct'])) if viable else None
 rep={}
 if best:
  for m,(d,rr,E,Rf) in D.items():
   j=int(np.where(CHECK_MS==best['checkpoint_ms'])[0][0]);x=Rf[:,j,:];mask=rr&((d['day_idx']>=14) if m==1 else np.ones(len(rr),bool))&np.all(np.isfinite(x),1);sel=mask&(x[:,0]>=best['pnl_min'])&(x[:,1]<=best['giveback_max']);y=E[:,-1]>0
   rep[str(m)]={'base_count':int(mask.sum()),'selected':int(sel.sum()),'coverage_pct':float(sel.sum()/mask.sum()*100) if mask.sum() else 0.,'base_5s_accuracy_pct':float(y[mask].mean()*100) if mask.sum() else None,'selected_5s_accuracy_pct':float(y[sel].mean()*100) if sel.sum() else None,'delta_pp':float(y[sel].mean()*100-y[mask].mean()*100) if sel.sum() and mask.sum() else None,'runner_recall_pct':float((y&sel).sum()/(y&mask).sum()*100) if (y&mask).sum() else 0.}
 out={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_020_RECOVERY_RUNNER_TIMING_STATE','status':'COMPLETED_LOCAL_DIAGNOSTIC','parent':'ENTRY019 RECOVERY_RUNNER population','purpose':'Characterize when weak/recovery runners become durably favorable and test whether an earlier causal checkpoint can certify recovery without using future ticks. No exit change.','checkpoint_ms':[int(x) for x in CHECK_MS],'teacher_timing_map':timing,'candidate_rule':best,'replication':rep,'decision':'RETAIN_TIMING_DIAGNOSTIC' if best else 'NO_EARLY_CERTIFICATION_RULE','next_unit':'R9B_GAMMA_DYNAMIC_ENTRY_021_RECOVERY_TRAJECTORY_OWNER' if best else 'R9B_GAMMA_DYNAMIC_ENTRY_021_RECOVERY_FEATURE_REBUILD','august_accessed':False,'elapsed_s':time.time()-t0}
 OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'input_sha256':{str(m):sha(P[m]) for m in (1,2,3)},'model_sha256':sha(MODEL),'august_accessed':False},indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
