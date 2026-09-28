import json, hashlib, time
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier
R=Path('/mnt/data/r9b_active')
P={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_018_{m:02d}_POST1.npz' for m in (1,2,3)}
OUT=R/'R9B_GAMMA_DYNAMIC_ENTRY_018_BRIDGE_PERSISTENCE_OWNER.json'; MAN=R/'R9B_GAMMA_DYNAMIC_ENTRY_018_MANIFEST.json'
FEATURE_SETS={'renewal':[23,20,13,19,11,12,17],'path':[23,7,9,10,19,22,4,5],'compact':[23,7,9,13,19,20,22]}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def load(m):
 z=np.load(P[m],allow_pickle=False); d={k:z[k] for k in z.files}; z.close()
 a=d['entry_action']; H=d['horizon']; s=np.where(a==1,1.,np.where(a==2,-1.,0.))
 raw={1:H[:,4]+.20,2:H[:,5]+.20,3:H[:,6]+.20,5:H[:,7]+.20}; e={h:s*raw[h]-.20 for h in raw}
 d['ignition']=(a!=0)&(e[1]>0)&np.all(np.isfinite(d['post1']),1); d['e']=e; return d

def eval_hold(d,hold,mask):
 base=d['ignition']&mask; take=base&hold; e=d['e']
 def pct(h,m): return float((e[h][m]>0).mean()*100) if m.sum() else None
 persisted=(e[5]>0)&base; selected=(e[5]>0)&take
 return {'ignitions':int(base.sum()),'hold_count':int(take.sum()),'coverage_pct':float(take.sum()/base.sum()*100) if base.sum() else 0.,
 'hold2_accuracy_pct':pct(2,take),'hold3_accuracy_pct':pct(3,take),'hold5_accuracy_pct':pct(5,take),
 'baseline_hold2_pct':pct(2,base),'baseline_hold3_pct':pct(3,base),'baseline_hold5_pct':pct(5,base),
 'hold2_delta_pp':pct(2,take)-pct(2,base) if take.sum() and base.sum() else None,
 'hold3_delta_pp':pct(3,take)-pct(3,base) if take.sum() and base.sum() else None,
 'hold5_delta_pp':pct(5,take)-pct(5,base) if take.sum() and base.sum() else None,
 'persistent_runner_recall_pct':float(selected.sum()/persisted.sum()*100) if persisted.sum() else 0.,
 'false_hold_pct':float(((e[5]<=0)&take).sum()/take.sum()*100) if take.sum() else None}

def prob1(clf,X):
 ok=np.all(np.isfinite(X),1); p=np.full(len(X),np.nan)
 if len(clf.classes_)==1:p[ok]=1. if clf.classes_[0]==1 else 0.
 else:
  j=int(np.where(clf.classes_==1)[0][0]);p[ok]=clf.predict_proba(X[ok])[:,j]
 return p

def select_inner(d,mincov):
 tr=d['ignition']&(d['day_idx']<7); va=d['ignition']&(d['day_idx']>=7)&(d['day_idx']<14); y=(d['e'][5]>0).astype(np.int8); rows=[]
 for mode,inds in FEATURE_SETS.items():
  X=d['post1'][:,inds]; fit=tr&np.all(np.isfinite(X),1)
  for depth in (1,2,3):
   for leaf in (5,8,10,15,20):
    if fit.sum()<2*leaf:continue
    for w0 in (1.,1.25,1.5,2.,3.):
     clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,class_weight={0:w0,1:1},random_state=118).fit(X[fit],y[fit]); p=prob1(clf,X)
     for thr in (.40,.50,.55,.60,.65,.70,.75,.80):
      hold=np.isfinite(p)&(p>=thr);st=eval_hold(d,hold,va);rows.append({'mode':mode,'depth':depth,'leaf':leaf,'w0':w0,'threshold':thr,'inner':st})
 elig=[r for r in rows if r['inner']['coverage_pct']>=mincov and r['inner']['hold_count']>=20]
 return max(elig,key=lambda r:(r['inner']['hold5_delta_pp'],r['inner']['hold3_delta_pp'],r['inner']['persistent_runner_recall_pct'],r['inner']['coverage_pct'])) if elig else None

def main():
 t0=time.time();D={m:load(m) for m in (1,2,3)};d1=D[1];y1=(d1['e'][5]>0).astype(np.int8);profiles={}
 for cov in (40,50,70,85):
  p=select_inner(d1,cov)
  if p is None:continue
  inds=FEATURE_SETS[p['mode']];X1=d1['post1'][:,inds];tr=d1['ignition']&(d1['day_idx']<14)&np.all(np.isfinite(X1),1)
  clf=DecisionTreeClassifier(max_depth=p['depth'],min_samples_leaf=p['leaf'],class_weight={0:p['w0'],1:1},random_state=118).fit(X1[tr],y1[tr]);rep={}
  for m in (1,2,3):
   d=D[m];X=d['post1'][:,inds];pr=prob1(clf,X);hold=np.isfinite(pr)&(pr>=p['threshold']);mask=(d['day_idx']>=14) if m==1 else np.ones(len(hold),bool);rep[str(m)]=eval_hold(d,hold,mask)
  profiles[f'coverage_floor_{cov}']={'selected':p,'replication':rep,'min_hold5_delta_pp':min(rep[str(m)]['hold5_delta_pp'] for m in (1,2,3)),'min_hold3_delta_pp':min(rep[str(m)]['hold3_delta_pp'] for m in (1,2,3)),'min_hold2_delta_pp':min(rep[str(m)]['hold2_delta_pp'] for m in (1,2,3)),'min_coverage_pct':min(rep[str(m)]['coverage_pct'] for m in (1,2,3)),'min_runner_recall_pct':min(rep[str(m)]['persistent_runner_recall_pct'] for m in (1,2,3))}
 robust=[(k,v) for k,v in profiles.items() if v['min_hold5_delta_pp']>0];best=max(robust,key=lambda kv:(kv[1]['min_hold5_delta_pp'],kv[1]['min_runner_recall_pct'],kv[1]['min_coverage_pct'])) if robust else None
 out={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_018_BRIDGE_PERSISTENCE_OWNER','status':'COMPLETED_LOCAL_DIAGNOSTIC','parent':'ENTRY017 balanced bridge-only entry profile','purpose':'Directional persistence ownership after a causally correct +1s ignition; no actual exit/lifecycle change.','decision_time':'+1 second after entry','features':'Exact tick signal→+1s path only; no future path inputs.','target':'Executable same-direction PnL remains >0 at +5s; target is training label only.','selection_contract':'ENTRY017 fixed; Jan days0-6 fit / 7-13 select under predeclared coverage floors; refit Jan first14 and freeze Jan-heldout/Feb/Mar.','profiles':profiles,'best_robust':{'id':best[0],'metrics':best[1]} if best else None,'decision':'RETAIN_PERSISTENCE_FRONTIER' if best else 'NO_ROBUST_5S_PERSISTENCE_OWNER','next_unit':'R9B_GAMMA_DYNAMIC_ENTRY_019_MULTI_HORIZON_PERSISTENCE_STATE' if best else 'R9B_GAMMA_DYNAMIC_ENTRY_019_PERSISTENCE_FEATURE_REBUILD','august_accessed':False,'elapsed_s':time.time()-t0}
 OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'input_sha256':{str(m):sha(P[m]) for m in (1,2,3)},'august_accessed':False},indent=2)+'\n')
if __name__=='__main__':main()
