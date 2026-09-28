import json, hashlib, argparse, time
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier
R=Path('/mnt/data/r9b_active')
P={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_018_{m:02d}_POST1.npz' for m in (1,2,3)}
C={m:R/f'R9B_GAMMA_DYNAMIC_HOLD_EXIT_001_{m:02d}_CACHE.npz' for m in (1,2,3)}
DISC=R/'R9B_GAMMA_DYNAMIC_HOLD_EXIT_010_DISCOVERY.json'
OUT=R/'R9B_GAMMA_DYNAMIC_HOLD_EXIT_010_RUNNER_CAPTURE_REBUILD.json'
MAN=R/'R9B_GAMMA_DYNAMIC_HOLD_EXIT_010_MANIFEST.json'
HORIZ=(3000,5000,8000,10000,15000,20000,30000)
FEATURE_SETS={
 'core':[23,7,9,10,19,22,4,5],
 'renewal':[23,4,5,7,9,11,12,13,14,17,19,20,21,22],
 'compact':[23,7,9,13,19,20,22],
 'full':list(range(24)),
}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def metric(p):
 p=np.asarray(p,float);p=p[np.isfinite(p)];n=len(p);w=p>0;gp=float(p[w].sum()) if n else 0.;gl=float(p[p<0].sum()) if n else 0.
 return {'trades':int(n),'winners':int(w.sum()),'win_rate_pct':float(w.mean()*100) if n else 0.,'net':float(p.sum()) if n else 0.,'gp':gp,'gl':gl,'avg':float(p.mean()) if n else None,'pf':float(gp/-gl) if gl<0 else None}

def delta(b,c):
 return {'net_improvement':c['net']-b['net'],'gp_improvement':c['gp']-b['gp'],'gl_change':c['gl']-b['gl'],'winner_delta':c['winners']-b['winners'],'winner_retention_pct':c['winners']/max(b['winners'],1)*100}

def load(m):
 z=np.load(P[m],allow_pickle=False);p={k:z[k] for k in z.files};z.close()
 z=np.load(C[m],allow_pickle=False);c={k:z[k] for k in z.files};z.close()
 return p,c

def probs(clf,X):
 ok=np.all(np.isfinite(X),1);p=np.full(len(X),np.nan)
 if len(clf.classes_)==1:p[ok]=1. if clf.classes_[0]==1 else 0.
 else:
  j=int(np.where(clf.classes_==1)[0][0]);p[ok]=clf.predict_proba(X[ok])[:,j]
 return p

def eval_policy(bank,ext,select,mask):
 use=mask&np.isfinite(bank)&np.isfinite(ext)
 cand=bank.copy();cand[select&use]=ext[select&use]
 b=metric(bank[use]);c=metric(cand[use]);d=delta(b,c)
 return {'base':b,'candidate':c,'delta':d,'extended':int((select&use).sum()),'extend_pct':float((select&use).sum()/use.sum()*100) if use.sum() else 0.}

def discover():
 t0=time.time();p,c=load(1);state=c['state'];strong=(state==1);day=c['day_idx'];h=c['horiz_ms'];bank=c['horizon_pnl'][:,int(np.where(h==1000)[0][0])]
 rows=[]
 fit=strong&(day<7);val=strong&(day>=7)&(day<14)
 for ext_ms in HORIZ:
  ext=c['horizon_pnl'][:,int(np.where(h==ext_ms)[0][0])]
  y=((ext-bank)>.05).astype(np.int8)
  for mode,inds in FEATURE_SETS.items():
   X=p['post1'][:,inds]
   tr=fit&np.all(np.isfinite(X),1)
   if tr.sum()<10:continue
   for depth in (1,2,3,4):
    for leaf in (2,3,4,5,6,8):
     if tr.sum()<2*leaf:continue
     for w0 in (.75,1.,1.25,1.5,2.,3.):
      clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,class_weight={0:w0,1:1},random_state=210).fit(X[tr],y[tr])
      pr=probs(clf,X)
      for thr in (.35,.40,.45,.50,.55,.60,.65,.70,.75):
       sel=np.isfinite(pr)&(pr>=thr)
       ef=eval_policy(bank,ext,sel,fit);ev=eval_policy(bank,ext,sel,val)
       wr=min(ef['delta']['winner_retention_pct'],ev['delta']['winner_retention_pct'])
       ok=(ef['delta']['net_improvement']>0 and ev['delta']['net_improvement']>0 and ef['delta']['gp_improvement']>0 and ev['delta']['gp_improvement']>0 and wr>=95 and ef['extended']>=3 and ev['extended']>=3)
       rows.append({'ext_ms':ext_ms,'mode':mode,'feature_indexes':inds,'depth':depth,'leaf':leaf,'w0':w0,'threshold':thr,'fit':ef,'validation':ev,'eligible':ok,'min_net':min(ef['delta']['net_improvement'],ev['delta']['net_improvement']),'sum_net':ef['delta']['net_improvement']+ev['delta']['net_improvement'],'min_gp':min(ef['delta']['gp_improvement'],ev['delta']['gp_improvement']),'min_winner_retention':wr})
 elig=[r for r in rows if r['eligible']]
 best=max(elig,key=lambda r:(r['min_net'],r['sum_net'],r['min_gp'],r['min_winner_retention'])) if elig else None
 out={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_010_RUNNER_CAPTURE_REBUILD','phase':'DISCOVERY','status':'COMPLETED_LOCAL_DISCOVERY','parent':'HOLD_EXIT005 + frozen ENTRY017-024 ownership','scope':'STRONG_RUNNER winner-side capture only. Bank at +1s by default; selectively extend to a later fixed horizon using only +1s observed path features.','teacher':'Future extension-vs-bank gain is training label only. No future feature enters the +1s decision.','selection_contract':'Jan days0-6 fit / days7-13 validate. Require positive net and GP improvement in both halves, >=95% winner retention, >=3 extensions per half.','screen_count':len(rows),'eligible_count':len(elig),'best':best,'top':sorted(rows,key=lambda r:(r['eligible'],r['min_net'],r['sum_net'],r['min_gp']),reverse=True)[:20],'next':'REPLICATE' if best else 'REBUILD','august_accessed':False,'elapsed_s':time.time()-t0}
 DISC.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'screen_count':len(rows),'eligible_count':len(elig),'best':best,'source_sha256':sha(__file__),'result_sha256':sha(DISC),'elapsed_s':out['elapsed_s']},indent=2))

def fit_frozen(best):
 p,c=load(1);h=c['horiz_ms'];bank=c['horizon_pnl'][:,int(np.where(h==1000)[0][0])];ext=c['horizon_pnl'][:,int(np.where(h==best['ext_ms'])[0][0])];y=((ext-bank)>.05).astype(np.int8);X=p['post1'][:,best['feature_indexes']];tr=(c['state']==1)&(c['day_idx']<14)&np.all(np.isfinite(X),1);clf=DecisionTreeClassifier(max_depth=best['depth'],min_samples_leaf=best['leaf'],class_weight={0:best['w0'],1:1},random_state=210).fit(X[tr],y[tr]);return clf

def replicate(m):
 t0=time.time();disc=json.load(open(DISC));best=disc['best'];clf=fit_frozen(best);p,c=load(m);h=c['horiz_ms'];bank=c['horizon_pnl'][:,int(np.where(h==1000)[0][0])];ext=c['horizon_pnl'][:,int(np.where(h==best['ext_ms'])[0][0])];X=p['post1'][:,best['feature_indexes']];pr=probs(clf,X);sel=np.isfinite(pr)&(pr>=best['threshold']);mask=(c['state']==1)&((c['day_idx']>=14) if m==1 else np.ones(len(c['state']),bool));ev=eval_policy(bank,ext,sel,mask);out={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_010_RUNNER_CAPTURE_REBUILD','month':m,'status':'COMPLETED_LOCAL_REPLICATION','rule':{k:best[k] for k in ('ext_ms','mode','feature_indexes','depth','leaf','w0','threshold')},'metrics':ev,'august_accessed':False,'elapsed_s':time.time()-t0};q=R/f'R9B_GAMMA_DYNAMIC_HOLD_EXIT_010_REPLICATION_{m:02d}.json';q.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

def finalize():
 disc=json.load(open(DISC));reps={str(m):json.load(open(R/f'R9B_GAMMA_DYNAMIC_HOLD_EXIT_010_REPLICATION_{m:02d}.json')) for m in (1,2,3)};rob=all(reps[str(m)]['metrics']['delta']['net_improvement']>0 and reps[str(m)]['metrics']['delta']['gp_improvement']>0 and reps[str(m)]['metrics']['delta']['winner_retention_pct']>=95 for m in (1,2,3));out={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_010_RUNNER_CAPTURE_REBUILD','status':'COMPLETED_LOCAL_DIAGNOSTIC','parent':'HOLD_EXIT005 + frozen ENTRY017-024 ownership','discovery':disc,'replication':reps,'robust':rob,'decision':'RETAIN_RUNNER_CAPTURE_FRONTIER' if rob else 'REJECT_RUNNER_CAPTURE_GRID','next_unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_INTEGRATED_RUNNER_CAPTURE' if rob else 'R9B_GAMMA_DYNAMIC_HOLD_EXIT_011_RUNNER_FEATURE_REBUILD','august_accessed':False};OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'discovery_sha256':sha(DISC),'result_sha256':sha(OUT),'replication_sha256':{str(m):sha(R/f'R9B_GAMMA_DYNAMIC_HOLD_EXIT_010_REPLICATION_{m:02d}.json') for m in (1,2,3)},'august_accessed':False},indent=2)+'\n');print(json.dumps({'robust':rob,'source_sha256':sha(__file__),'result_sha256':sha(OUT)},indent=2))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['discover','replicate','finalize']);ap.add_argument('--month',type=int);a=ap.parse_args()
 if a.phase=='discover':discover()
 elif a.phase=='replicate':assert a.month in (1,2,3);replicate(a.month)
 else:finalize()
