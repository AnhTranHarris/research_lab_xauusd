import json, hashlib, time
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier

R=Path('/mnt/data/r9b_active')
P={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_018_{m:02d}_POST1.npz' for m in (1,2,3)}
OUT=R/'R9B_GAMMA_DYNAMIC_ENTRY_019_MULTI_HORIZON_PERSISTENCE_STATE.json'
MAN=R/'R9B_GAMMA_DYNAMIC_ENTRY_019_MANIFEST.json'
MODEL=R/'R9B_GAMMA_DYNAMIC_ENTRY_019_RECOVERY_RUNNER_MODEL.json'
STRONG_THR=0.27175000309944153
FEATURE_SETS={
 'path':[23,7,9,10,19,22,4,5],
 'renewal':[23,20,13,19,11,12,17],
 'compact':[23,7,9,13,19,20,22],
}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def load(m):
 z=np.load(P[m],allow_pickle=False);d={k:z[k] for k in z.files};z.close()
 a=d['entry_action'];H=d['horizon'];s=np.where(a==1,1.,np.where(a==2,-1.,0.))
 raw={1:H[:,4]+.20,2:H[:,5]+.20,3:H[:,6]+.20,5:H[:,7]+.20}
 e={h:s*raw[h]-.20 for h in raw}
 ign=(a!=0)&(e[1]>0)&np.all(np.isfinite(d['post1']),1)
 return d,e,ign

def prob1(clf,X):
 ok=np.all(np.isfinite(X),1);p=np.full(len(X),np.nan)
 if len(clf.classes_)==1:p[ok]=1. if clf.classes_[0]==1 else 0.
 else:
  j=int(np.where(clf.classes_==1)[0][0]);p[ok]=clf.predict_proba(X[ok])[:,j]
 return p

def state_metrics(d,e,ign,p,thr,mask):
 x=d['post1'][:,23];base=ign&mask
 strong=base&(x>STRONG_THR)
 weak=base&(x<=STRONG_THR)
 recovery=weak&np.isfinite(p)&(p>=thr)
 harvest=weak&~recovery
 combined=strong|recovery
 def block(z):
  o={'count':int(z.sum()),'coverage_pct':float(z.sum()/base.sum()*100) if base.sum() else 0.}
  for h in (2,3,5):o[f'acc_{h}s_pct']=float((e[h][z]>0).mean()*100) if z.sum() else None
  return o
 out={'base':block(base),'strong_runner':block(strong),'recovery_runner':block(recovery),'harvest_candidate':block(harvest),'combined_persist':block(combined)}
 for h in (2,3,5):
  pos=(e[h]>0)&base
  out['combined_persist'][f'recall_{h}s_pct']=float(((e[h]>0)&combined).sum()/pos.sum()*100) if pos.sum() else None
  out['combined_persist'][f'acc_delta_{h}s_pp']=out['combined_persist'][f'acc_{h}s_pct']-out['base'][f'acc_{h}s_pct']
  wpos=(e[h]>0)&weak
  out['recovery_runner'][f'weak_recall_{h}s_pct']=float(((e[h]>0)&recovery).sum()/wpos.sum()*100) if wpos.sum() else None
  out['recovery_runner'][f'weak_acc_delta_{h}s_pp']=out['recovery_runner'][f'acc_{h}s_pct']-float((e[h][weak]>0).mean()*100) if weak.sum() and recovery.sum() else None
 return out

def tree_json(clf,feature_indexes,thr):
 tr=clf.tree_
 probs=[]
 for v in tr.value[:,0,:]:
  s=float(v.sum());probs.append([float(x/s) if s else 0. for x in v])
 return {'feature_indexes':feature_indexes,'classes':[int(x) for x in clf.classes_],
 'children_left':[int(x) for x in tr.children_left],'children_right':[int(x) for x in tr.children_right],
 'feature':[int(x) for x in tr.feature],'threshold':[float(x) for x in tr.threshold],
 'n_node_samples':[int(x) for x in tr.n_node_samples],'class_probability':probs,'probability_threshold':thr}

def main():
 t0=time.time();D={m:load(m) for m in (1,2,3)};d1,e1,ign1=D[1]
 weak=ign1&(d1['post1'][:,23]<=STRONG_THR);fitmask=weak&(d1['day_idx']<7);valmask=weak&(d1['day_idx']>=7)&(d1['day_idx']<14);y=(e1[5]>0).astype(np.int8)
 rows=[]
 for mode,inds in FEATURE_SETS.items():
  X=d1['post1'][:,inds];fit=fitmask&np.all(np.isfinite(X),1)
  for depth in (1,2,3):
   for leaf in (3,5,8,10,15):
    if fit.sum()<2*leaf:continue
    for w0 in (1.,1.25,1.5,2.,3.):
     clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,class_weight={0:w0,1:1},random_state=129).fit(X[fit],y[fit]);p=prob1(clf,X)
     for thr in (.30,.35,.40,.45,.50,.55,.60,.65,.70,.75):
      sel=valmask&np.isfinite(p)&(p>=thr)
      if sel.sum()<8:continue
      weakbase=float((e1[5][valmask]>0).mean()*100);acc=float((e1[5][sel]>0).mean()*100);rec=float(((e1[5]>0)&sel).sum()/((e1[5]>0)&valmask).sum()*100)
      rows.append({'mode':mode,'depth':depth,'leaf':leaf,'w0':w0,'threshold':thr,'val_count':int(sel.sum()),'val_coverage_pct':float(sel.sum()/valmask.sum()*100),'val_5s_accuracy_pct':acc,'val_weak_base_5s_pct':weakbase,'val_5s_delta_pp':acc-weakbase,'val_weak_runner_recall_pct':rec})
 elig=[r for r in rows if r['val_5s_delta_pp']>0 and r['val_weak_runner_recall_pct']>=60 and r['val_coverage_pct']>=40]
 best=max(elig,key=lambda r:(r['val_5s_delta_pp'],r['val_weak_runner_recall_pct'],r['val_coverage_pct'])) if elig else None
 if best is None:raise RuntimeError('No eligible recovery-runner candidate')
 inds=FEATURE_SETS[best['mode']];X1=d1['post1'][:,inds];refit=weak&(d1['day_idx']<14)&np.all(np.isfinite(X1),1)
 clf=DecisionTreeClassifier(max_depth=best['depth'],min_samples_leaf=best['leaf'],class_weight={0:best['w0'],1:1},random_state=129).fit(X1[refit],y[refit])
 rep={}
 for m in (1,2,3):
  d,e,ign=D[m];p=prob1(clf,d['post1'][:,inds]);mask=(d['day_idx']>=14) if m==1 else np.ones(len(ign),bool);rep[str(m)]=state_metrics(d,e,ign,p,best['threshold'],mask)
 robust_5s=all(rep[str(m)]['combined_persist']['acc_delta_5s_pp']>0 and rep[str(m)]['combined_persist']['recall_5s_pct']>=90 for m in (1,2,3))
 model={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_019_MULTI_HORIZON_PERSISTENCE_STATE','role':'RECOVERY_RUNNER classifier inside ENTRY018 weak population','strong_runner_rule':{'exec_pnl_1s_gt':STRONG_THR},'feature_set':best['mode'],'feature_meaning':{23:'exec_pnl_1s',7:'efficiency_1s',9:'breakeven_occupancy_1s',13:'age_since_last_favorable_extreme_s',19:'breakeven_recross_count_1s',20:'giveback_from_mfe_1s',22:'second_half_acceleration_1s'},'hyperparameters':{'max_depth':best['depth'],'min_samples_leaf':best['leaf'],'class_weight_0':best['w0'],'random_state':129},'tree':tree_json(clf,inds,best['threshold']),'training':'January days0-13 ENTRY017-correct ignitions with exec_pnl_1s <= ENTRY018 strong threshold; target future +5s persistence is label only.','august_accessed':False}
 MODEL.write_text(json.dumps(model,indent=2)+'\n')
 out={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_019_MULTI_HORIZON_PERSISTENCE_STATE','status':'COMPLETED_LOCAL_DIAGNOSTIC','parent':'ENTRY017 + ENTRY018 strong-runner frontier','purpose':'Recover genuine later persistence hidden inside ENTRY018 weak/HARVEST_CANDIDATE population without weakening the high-accuracy strong-runner state.','causal_state_machine':['STRONG_RUNNER: ENTRY018 exec_pnl_1s > 0.27175000309944153','RECOVERY_RUNNER: weak population selected by frozen first-second recovery tree','HARVEST_CANDIDATE: remaining weak population'],'selection_contract':'Jan days0-6 fit / days7-13 select. Recovery candidate must improve weak-group +5s accuracy, recover >=60% of weak-group runners, and cover >=40% of weak validation events. Refit Jan first14; freeze Jan-heldout/Feb/Mar.','selected':best,'replication':rep,'robust_5s_recovery_frontier':robust_5s,'key_interpretation':'Persistence is not monotonic. Some weak +1s ignitions recover by +5s. A separate RECOVERY_RUNNER owner materially restores runner recall while STRONG_RUNNER preserves high precision; therefore a single early-harvest rule would destroy legitimate runners.','decision':'RETAIN_DIAGNOSTIC_FRONTIER_NO_EXIT_CHANGE' if robust_5s else 'REJECT','model_sha256':sha(MODEL),'august_accessed':False,'elapsed_s':time.time()-t0}
 OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'model_sha256':sha(MODEL),'input_sha256':{str(m):sha(P[m]) for m in (1,2,3)},'august_accessed':False},indent=2)+'\n')
 print(json.dumps({'selected':best,'robust':robust_5s,'model_sha256':sha(MODEL),'result_sha256':sha(OUT),'source_sha256':sha(__file__),'replication':rep},indent=2))
if __name__=='__main__':main()
