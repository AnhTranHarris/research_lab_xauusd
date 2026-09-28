import json, hashlib, time, sys
from pathlib import Path
import numpy as np
from numba import njit
from sklearn.tree import DecisionTreeClassifier
R=Path('/mnt/data/r9b_active'); sys.path.insert(0,str(R)); import gamma014_replay as g
P={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_018_{m:02d}_POST1.npz' for m in (1,2,3)}
B17={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_017_{m:02d}_BRIDGE.npz' for m in (1,2,3)}
OUT=R/'R9B_GAMMA_DYNAMIC_ENTRY_023_LATE_IGNITION_OWNER.json'
MODEL=R/'R9B_GAMMA_DYNAMIC_ENTRY_023_LATE_IGNITION_MODEL.json'
MAN=R/'R9B_GAMMA_DYNAMIC_ENTRY_023_MANIFEST.json'
H=.10; CHECKS=np.array([1500,2000,2500,3000,4000],np.int64)
FEATURE_SETS={'trajectory':list(range(12)),'compact':[0,1,4,5,6,8,10,11],'recovery':[0,1,3,5,8,10,11],'path':[0,6,7,8,9,10]}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

@njit(cache=True)
def features(t,mid,sig,fade_side,action,e1):
 n=len(sig);K=len(CHECKS);F=np.full((n,K,12),np.nan);E5=np.full(n,np.nan)
 for q in range(n):
  a=int(action[q])
  if a==0:continue
  fs=int(fade_side[q]);side=fs if a==1 else -fs;s=int(sig[q]);ie=np.searchsorted(t,s,side='left')
  if ie>=len(t):continue
  m0=mid[ie];j5=np.searchsorted(t,s+5000,side='right')-1
  if j5<ie:j5=ie
  E5[q]=side*(mid[j5]-m0)-2*H
  start=np.searchsorted(t,s+1000,side='right')
  for z in range(K):
   ms=CHECKS[z];end=np.searchsorted(t,s+ms,side='right');last=end-1
   if last<ie:last=ie
   final=side*(mid[last]-m0);execp=final-2*H
   mx=-1e18;mn=1e18;travel=0.;prev=side*(mid[start]-m0) if start<len(mid) else final;turns=0;ps=0;pos=0;lastfav=s+1000;cross=0;prevsg=1 if e1[q]>0 else (-1 if e1[q]<0 else 0)
   for k in range(start,end):
    d=side*(mid[k]-m0);ep=d-2*H
    if ep>mx:mx=ep;lastfav=int(t[k])
    if ep<mn:mn=ep
    if ep>0:pos+=1
    if k>start:
     step=d-prev;travel+=abs(step);sg=1 if step>0 else (-1 if step<0 else 0)
     if sg!=0:
      if ps!=0 and sg!=ps:turns+=1
      ps=sg
    sgb=1 if ep>0 else (-1 if ep<0 else 0)
    if sgb!=0:
     if prevsg!=0 and sgb!=prevsg:cross+=1
     prevsg=sgb
    prev=d
   cnt=max(1,end-start);delta=execp-e1[q];giveback=mx-execp;recovery=execp-mn;eff=delta/(travel+1e-9)
   F[q,z,0]=execp;F[q,z,1]=delta;F[q,z,2]=mx;F[q,z,3]=mn;F[q,z,4]=giveback;F[q,z,5]=recovery;F[q,z,6]=eff;F[q,z,7]=travel;F[q,z,8]=pos/cnt;F[q,z,9]=turns;F[q,z,10]=(s+ms-lastfav)/1000.;F[q,z,11]=cross
 return F,E5

def tree_json(clf,inds,ms,thr):
 t=clf.tree_;probs=[]
 for v in t.value[:,0,:]:
  s=float(v.sum());probs.append([float(x/s) if s else 0. for x in v])
 return {'checkpoint_ms':int(ms),'feature_indexes':[int(x) for x in inds],'classes':[int(x) for x in clf.classes_],'children_left':[int(x) for x in t.children_left],'children_right':[int(x) for x in t.children_right],'feature':[int(x) for x in t.feature],'threshold':[float(x) for x in t.threshold],'n_node_samples':[int(x) for x in t.n_node_samples],'class_probability':probs,'probability_threshold':float(thr)}

def metric(y,sel,base):
 n=int(base.sum());s=int(sel.sum());pos=y&base
 return {'base_count':n,'selected':s,'coverage_pct':float(s/n*100) if n else 0.,'base_5s_accuracy_pct':float(y[base].mean()*100) if n else None,'selected_5s_accuracy_pct':float(y[sel].mean()*100) if s else None,'delta_pp':float(y[sel].mean()*100-y[base].mean()*100) if s and n else None,'winner_recall_pct':float((y&sel).sum()/pos.sum()*100) if pos.sum() else 0.}

def load(m):
 z=np.load(P[m],allow_pickle=False);d={k:z[k] for k in z.files};z.close();b=np.load(B17[m],allow_pickle=False);X=b['X'].copy();b.close();a=d['entry_action'];sel=a!=0;e1=d['post1'][:,23];wrong=sel&(e1<=0)&np.all(np.isfinite(d['post1']),1);t,mid=g.load_ticks(m);F,E5=features(t,mid,X[:,0].astype(np.int64),X[:,1].astype(np.int8),a,e1);return d,wrong,F,E5

def main():
 t0=time.time();D={m:load(m) for m in (1,2,3)};d1,w1,F1,E51=D[1];y1=E51>0;fitdays=d1['day_idx']<7;valdays=(d1['day_idx']>=7)&(d1['day_idx']<14);rows=[]
 for ck,ms in enumerate(CHECKS):
  for mode,inds in FEATURE_SETS.items():
   A=F1[:,ck,:][:,inds];fit=w1&fitdays&np.all(np.isfinite(A),1);val=w1&valdays&np.all(np.isfinite(A),1)
   if fit.sum()<40 or val.sum()<20:continue
   for depth in (1,2,3):
    for leaf in (10,20,30,50):
     if fit.sum()<2*leaf:continue
     for w0 in (1.,1.25,1.5,2.,3.):
      clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,class_weight={0:w0,1:1},random_state=133).fit(A[fit],y1[fit].astype(np.int8));pr=clf.predict_proba(A[val]);jj=int(np.where(clf.classes_==1)[0][0]) if 1 in clf.classes_ else -1
      if jj<0:continue
      p=pr[:,jj];vi=np.where(val)[0]
      for thr in (.30,.35,.40,.45,.50,.55,.60,.65,.70,.75):
       sel=np.zeros(len(y1),bool);sel[vi[p>=thr]]=True;met=metric(y1,sel,val)
       if met['selected']>=15 and met['coverage_pct']>=20 and met['winner_recall_pct']>=45 and met['delta_pp']>=15:
        rows.append({'checkpoint_ms':int(ms),'mode':mode,'depth':depth,'leaf':leaf,'w0':w0,'threshold':thr,'validation':met})
 # Favor earlier checkpoint once it is within 5 pp of best validation accuracy delta.
 best=None
 if rows:
  maxd=max(r['validation']['delta_pp'] for r in rows);near=[r for r in rows if r['validation']['delta_pp']>=maxd-5]
  best=min(near,key=lambda r:(r['checkpoint_ms'],-r['validation']['winner_recall_pct'],-r['validation']['delta_pp'],-r['validation']['coverage_pct']))
 rep={};model=None
 if best:
  ck=int(np.where(CHECKS==best['checkpoint_ms'])[0][0]);inds=FEATURE_SETS[best['mode']];A1=F1[:,ck,:][:,inds];tr=w1&(d1['day_idx']<14)&np.all(np.isfinite(A1),1);clf=DecisionTreeClassifier(max_depth=best['depth'],min_samples_leaf=best['leaf'],class_weight={0:best['w0'],1:1},random_state=133).fit(A1[tr],y1[tr].astype(np.int8))
  for m in (1,2,3):
   d,w,F,E5=D[m];A=F[:,ck,:][:,inds];base=w&((d['day_idx']>=14) if m==1 else np.ones(len(w),bool))&np.all(np.isfinite(A),1);sel=np.zeros(len(w),bool)
   if base.any():
    pr=clf.predict_proba(A[base]);jj=int(np.where(clf.classes_==1)[0][0]) if 1 in clf.classes_ else -1;bi=np.where(base)[0]
    if jj>=0:sel[bi[pr[:,jj]>=best['threshold']]]=True
   rep[str(m)]=metric(E5>0,sel,base)
  model={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_023_LATE_IGNITION_OWNER','role':'LATE_IGNITION classifier inside ENTRY017 selections non-positive at +1s','feature_meaning':{0:'current_exec_pnl',1:'exec_pnl_change_since_1s',2:'local_mfe_exec',3:'local_mae_exec',4:'giveback_from_local_mfe',5:'recovery_from_local_mae',6:'trajectory_efficiency',7:'travel_since_1s',8:'positive_breakeven_occupancy',9:'turn_count_since_1s',10:'age_since_local_mfe_s',11:'breakeven_recross_count'},'hyperparameters':{'max_depth':best['depth'],'min_samples_leaf':best['leaf'],'class_weight_0':best['w0'],'random_state':133},'tree':tree_json(clf,inds,best['checkpoint_ms'],best['threshold']),'training':'January days0-13 ENTRY017 selections with +1s executable P/L <=0. +5s persistence is label only.','august_accessed':False};MODEL.write_text(json.dumps(model,indent=2)+'\n')
 robust=bool(best and all(rep[str(m)]['delta_pp']>=15 and rep[str(m)]['winner_recall_pct']>=45 for m in (1,2,3)))
 out={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_023_LATE_IGNITION_OWNER','status':'COMPLETED_LOCAL_DIAGNOSTIC','parent':'ENTRY017 selections non-positive at +1s','purpose':'Recover late-ignition +5s winners that the existing persistence chain cannot see, using only exact-tick trajectory observed after +1s. No exit change.','selection_contract':'Jan days0-6 fit / 7-13 validate; require >=15pp validation accuracy uplift, >=45% winner recall, >=20% coverage, >=15 selected; among near-best candidates prefer earliest checkpoint. Refit Jan first14 and freeze Jan-heldout/Feb/Mar.','candidate':best,'replication':rep,'robust':robust,'decision':'RETAIN_LATE_IGNITION_FRONTIER_NO_EXIT_CHANGE' if robust else 'NO_ROBUST_LATE_IGNITION_OWNER','next_unit':'R9B_GAMMA_DYNAMIC_ENTRY_024_ENTRY_HOLD_ARCHITECTURE_REBASE' if robust else 'R9B_GAMMA_DYNAMIC_ENTRY_024_LATE_IGNITION_FEATURE_REBUILD','model_sha256':sha(MODEL) if MODEL.exists() else None,'august_accessed':False,'elapsed_s':time.time()-t0}
 OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'model_sha256':sha(MODEL) if MODEL.exists() else None,'input_sha256':{str(m):sha(P[m]) for m in (1,2,3)},'august_accessed':False},indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()