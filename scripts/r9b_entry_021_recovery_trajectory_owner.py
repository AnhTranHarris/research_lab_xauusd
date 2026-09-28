import json, hashlib, time, sys
from pathlib import Path
import numpy as np
from numba import njit
from sklearn.tree import DecisionTreeClassifier

R=Path('/mnt/data/r9b_active'); sys.path.insert(0,str(R)); import gamma014_replay as g
P={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_018_{m:02d}_POST1.npz' for m in (1,2,3)}
B17={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_017_{m:02d}_BRIDGE.npz' for m in (1,2,3)}
M19=R/'R9B_GAMMA_DYNAMIC_ENTRY_019_RECOVERY_RUNNER_MODEL.json'
OUT=R/'R9B_GAMMA_DYNAMIC_ENTRY_021_RECOVERY_TRAJECTORY_OWNER.json'
MODEL=R/'R9B_GAMMA_DYNAMIC_ENTRY_021_DELAYED_RUNNER_MODEL.json'
MAN=R/'R9B_GAMMA_DYNAMIC_ENTRY_021_MANIFEST.json'
H=.10; STRONG=.27175000309944153
CHECKS=np.array([4250,4500,4750],np.int64)

FEATURE_SETS={
 'trajectory':[0,1,2,3,4,5,6,7,8,9,10],
 'compact':[0,1,4,5,6,8,10],
 'momentum':[0,1,6,7,8,10],
 'recovery':[0,2,3,4,5,9],
}

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
def obs_features(t,mid,sig,fade_side,entry_action):
 n=len(sig);K=len(CHECKS);F=np.full((n,K,11),np.nan);E5=np.full(n,np.nan);E4=np.full(n,np.nan)
 for q in range(n):
  a=int(entry_action[q])
  if a==0:continue
  fs=int(fade_side[q]);side=fs if a==1 else -fs;s=int(sig[q]);ie=np.searchsorted(t,s,side='left')
  if ie>=len(t):continue
  m0=mid[ie]
  j4=np.searchsorted(t,s+4000,side='right')-1
  if j4<ie:j4=ie
  d4=side*(mid[j4]-m0); E4[q]=d4-2*H
  j5=np.searchsorted(t,s+5000,side='right')-1
  if j5<ie:j5=ie
  E5[q]=side*(mid[j5]-m0)-2*H
  for z in range(K):
   ms=CHECKS[z];end=np.searchsorted(t,s+ms,side='right');last=end-1
   if last<j4:last=j4
   final=side*(mid[last]-m0);execp=final-2*H
   start=j4;mx=-1e18;mn=1e18;travel=0.;prev=side*(mid[start]-m0);turns=0;ps=0;pos=0;lastfav=s+4000;cross=0;prevsg=1 if (prev-2*H)>0 else (-1 if (prev-2*H)<0 else 0)
   for k in range(start,end):
    d=side*(mid[k]-m0)
    if d>mx:mx=d;lastfav=int(t[k])
    if d<mn:mn=d
    if d-2*H>0:pos+=1
    if k>start:
     step=d-prev;travel+=abs(step);sg=1 if step>0 else (-1 if step<0 else 0)
     if sg!=0:
      if ps!=0 and sg!=ps:turns+=1
      ps=sg
    sgbe=1 if d-2*H>0 else (-1 if d-2*H<0 else 0)
    if sgbe!=0:
     if prevsg!=0 and sgbe!=prevsg:cross+=1
     prevsg=sgbe
    prev=d
   cnt=max(1,end-start)
   delta=execp-E4[q];giveback=mx-final;recovery=final-mn;eff=delta/(travel+1e-9)
   F[q,z,0]=execp
   F[q,z,1]=delta
   F[q,z,2]=mx-2*H
   F[q,z,3]=mn-2*H
   F[q,z,4]=giveback
   F[q,z,5]=recovery
   F[q,z,6]=eff
   F[q,z,7]=travel
   F[q,z,8]=pos/cnt
   F[q,z,9]=turns
   F[q,z,10]=(s+ms-lastfav)/1000.
  
 return F,E4,E5

def tree_json(clf, feature_indexes, checkpoint_ms, prob_thr):
 tr=clf.tree_; probs=[]
 for v in tr.value[:,0,:]:
  s=float(v.sum()); probs.append([float(x/s) if s else 0. for x in v])
 return {'checkpoint_ms':int(checkpoint_ms),'feature_indexes':[int(x) for x in feature_indexes],'classes':[int(x) for x in clf.classes_],'children_left':[int(x) for x in tr.children_left],'children_right':[int(x) for x in tr.children_right],'feature':[int(x) for x in tr.feature],'threshold':[float(x) for x in tr.threshold],'n_node_samples':[int(x) for x in tr.n_node_samples],'class_probability':probs,'probability_threshold':float(prob_thr)}

def load_states(m,m19):
 z=np.load(P[m],allow_pickle=False);d={k:z[k] for k in z.files};z.close();b=np.load(B17[m],allow_pickle=False);X=b['X'].copy();b.close()
 a=d['entry_action'];p1=d['post1'];ign=(a!=0)&(p1[:,23]>0)&np.all(np.isfinite(p1),1);weak=ign&(p1[:,23]<=STRONG)
 inds=m19['tree']['feature_indexes'];rec,_=tree_apply(p1[:,inds],m19);rr=weak&rec
 return d,X,rr

def metrics(y,sel,base):
 n=int(base.sum());sn=int(sel.sum());pos=(y&base);sp=(y&sel)
 return {'base_count':n,'selected':sn,'coverage_pct':float(sn/n*100) if n else 0.,'base_5s_accuracy_pct':float(y[base].mean()*100) if n else None,'selected_5s_accuracy_pct':float(y[sel].mean()*100) if sn else None,'delta_pp':float(y[sel].mean()*100-y[base].mean()*100) if sn and n else None,'runner_recall_pct':float(sp.sum()/pos.sum()*100) if pos.sum() else 0.,'false_delayed_runner_pct':float((~y[sel]).mean()*100) if sn else None}

def main():
 t0=time.time();m19=json.load(open(M19));D={}
 for m in (1,2,3):
  d,X,rr=load_states(m,m19);t,mid=g.load_ticks(m);F,E4,E5=obs_features(t,mid,X[:,0].astype(np.int64),X[:,1].astype(np.int8),d['entry_action'])
  cert=rr&(E4>=.05)
  # reproduce ENTRY020 giveback at +4s from exact path via a lightweight recomputation using max from +1 to +4
  # ENTRY020 full rule will be recovered below from direct tick scan encoded as a helper function.
  # approximate certification mask is corrected by explicit helper below.
  D[m]=(d,X,rr,F,E4,E5,t,mid)

 # exact ENTRY020 certification mask helper
 def cert_mask(m):
  d,X,rr,F,E4,E5,t,mid=D[m];out=np.zeros(len(rr),bool)
  for q in np.where(rr)[0]:
   a=int(d['entry_action'][q]);fs=int(X[q,1]);side=fs if a==1 else -fs;s=int(X[q,0]);ie=np.searchsorted(t,s,side='left');st=np.searchsorted(t,s+1000,side='right');en=np.searchsorted(t,s+4000,side='right');last=en-1
   if ie>=len(t) or last<ie:continue
   m0=mid[ie];mx=-1e18
   for k in range(st,en):
    dd=side*(mid[k]-m0)
    if dd>mx:mx=dd
   final=side*(mid[last]-m0);execp=final-2*H;gb=mx-final
   out[q]=(execp>=.05 and gb<=.50)
  return out
 CERT={m:cert_mask(m) for m in (1,2,3)}

 d1,X1,rr1,F1,E41,E51,t1,mid1=D[1];unc1=rr1&~CERT[1];y1=E51>0
 fitdays=(d1['day_idx']<7);valdays=(d1['day_idx']>=7)&(d1['day_idx']<14)
 rows=[]
 for ck,ms in enumerate(CHECKS):
  for mode,inds in FEATURE_SETS.items():
   A=F1[:,ck,:][:,inds];fit=unc1&fitdays&np.all(np.isfinite(A),1);val=unc1&valdays&np.all(np.isfinite(A),1)
   if fit.sum()<15 or val.sum()<8:continue
   for depth in (1,2,3):
    for leaf in (2,3,5,8):
     if fit.sum()<2*leaf:continue
     for w0 in (1.,1.25,1.5,2.,3.):
      clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,class_weight={0:w0,1:1},random_state=131).fit(A[fit],y1[fit].astype(np.int8))
      pr=clf.predict_proba(A[val]); jj=int(np.where(clf.classes_==1)[0][0]) if 1 in clf.classes_ else -1
      if jj<0:continue
      p=pr[:,jj];vidx=np.where(val)[0]
      for thr in (.35,.40,.45,.50,.55,.60,.65,.70):
       sel=np.zeros(len(y1),bool);sel[vidx[p>=thr]]=True
       met=metrics(y1,sel,val)
       if met['selected']>=5 and met['coverage_pct']>=20 and met['runner_recall_pct']>=45 and met['delta_pp']>0:
        rows.append({'checkpoint_ms':int(ms),'mode':mode,'depth':depth,'leaf':leaf,'w0':w0,'threshold':thr,'validation':met})
 best=max(rows,key=lambda r:(r['validation']['delta_pp'],r['validation']['runner_recall_pct'],r['validation']['coverage_pct'])) if rows else None
 rep={};model=None
 if best:
  ck=int(np.where(CHECKS==best['checkpoint_ms'])[0][0]);inds=FEATURE_SETS[best['mode']];A1=F1[:,ck,:][:,inds];tr=unc1&(d1['day_idx']<14)&np.all(np.isfinite(A1),1)
  clf=DecisionTreeClassifier(max_depth=best['depth'],min_samples_leaf=best['leaf'],class_weight={0:best['w0'],1:1},random_state=131).fit(A1[tr],y1[tr].astype(np.int8))
  for m in (1,2,3):
   d,X,rr,F,E4,E5,t,mid=D[m];unc=rr&~CERT[m];A=F[:,ck,:][:,inds];base=unc&((d['day_idx']>=14) if m==1 else np.ones(len(unc),bool))&np.all(np.isfinite(A),1);sel=np.zeros(len(base),bool)
   if base.any():
    p=clf.predict_proba(A[base]);jj=int(np.where(clf.classes_==1)[0][0]) if 1 in clf.classes_ else -1;bi=np.where(base)[0]
    if jj>=0:sel[bi[p[:,jj]>=best['threshold']]]=True
   rep[str(m)]=metrics(E5>0,sel,base)
  model={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_021_RECOVERY_TRAJECTORY_OWNER','role':'DELAYED_RUNNER classifier inside ENTRY020 RECOVERY_UNCERTAIN','checkpoint_ms':best['checkpoint_ms'],'feature_set':best['mode'],'feature_meaning':{0:'current_exec_pnl',1:'exec_pnl_change_since_4s',2:'local_mfe_exec',3:'local_mae_exec',4:'giveback_from_local_mfe',5:'recovery_from_local_mae',6:'trajectory_efficiency',7:'travel_since_4s',8:'positive_breakeven_occupancy',9:'turn_count_since_4s',10:'age_since_local_mfe_s'},'hyperparameters':{'max_depth':best['depth'],'min_samples_leaf':best['leaf'],'class_weight_0':best['w0'],'random_state':131},'tree':tree_json(clf,inds,best['checkpoint_ms'],best['threshold']),'training':'January days0-13 ENTRY019 RECOVERY_RUNNER events that fail ENTRY020 +4s certification. +5s persistence is label only.','august_accessed':False}
  MODEL.write_text(json.dumps(model,indent=2)+'\n')
 robust=bool(best and all(rep[str(m)]['delta_pp']>0 and rep[str(m)]['runner_recall_pct']>=45 for m in (1,2,3)))
 out={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_021_RECOVERY_TRAJECTORY_OWNER','status':'COMPLETED_LOCAL_DIAGNOSTIC','parent':'ENTRY020 RECOVERY_UNCERTAIN','purpose':'Separate delayed runners from likely failed ignitions among recovery candidates not certified at +4s, using only post-4s observed trajectory before +5s. No exit change.','checkpoint_candidates_ms':[int(x) for x in CHECKS],'selection_contract':'Jan days0-6 fit / days7-13 select; validation requires positive accuracy delta, >=45% runner recall, >=20% coverage, >=5 selected. Refit Jan first14 then freeze Jan-heldout/Feb/Mar.','candidate':best,'replication':rep,'robust':robust,'decision':'RETAIN_DELAYED_RUNNER_FRONTIER_NO_EXIT_CHANGE' if robust else 'NO_ROBUST_DELAYED_RUNNER_OWNER','next_unit':'R9B_GAMMA_DYNAMIC_ENTRY_022_ENTRY_HOLD_ARCHITECTURE_SYNTHESIS' if robust else 'R9B_GAMMA_DYNAMIC_ENTRY_022_RECOVERY_FAILURE_GEOMETRY','model_sha256':sha(MODEL) if MODEL.exists() else None,'august_accessed':False,'elapsed_s':time.time()-t0}
 OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'model_sha256':sha(MODEL) if MODEL.exists() else None,'input_sha256':{str(m):sha(P[m]) for m in (1,2,3)},'parent_model_sha256':sha(M19),'august_accessed':False},indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()