import argparse, hashlib, json
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier
R=Path('/mnt/data/r9b_active')
FEATURE_NAMES=['break_strength_atr','body_frac','close_location','adverse_wick_frac','atr_ratio','eff3','eff6','h1_align3','h1_align6','m15_align4','m15_align8','m15_conflict4','m15_conflict8','m15_eff4','m15_eff8']
SETS={'acceptance':list(range(5)),'durability':list(range(9)),'full':list(range(15))}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def metric(x):
 x=np.asarray(x,float);x=x[np.isfinite(x)];n=len(x);w=x>0;gp=float(x[w].sum()) if n else 0.;gl=float(x[x<0].sum()) if n else 0.
 return {'trades':int(n),'winners':int(w.sum()),'win_rate_pct':float(w.mean()*100) if n else 0.,'net':float(x.sum()) if n else 0.,'gp':gp,'gl':gl,'pf':float(gp/-gl) if gl<0 else None,'avg':float(x.mean()) if n else None}
def eff(c,n,i):
 if i<n:return np.nan
 d=np.diff(c[i-n:i+1]);den=float(np.sum(np.abs(d)));return float(abs(c[i]-c[i-n])/(den+1e-12))
def build(m):
 z=np.load(R/f'R9B_GAMMA_DYNAMIC_NET_002_{m:02d}_HTF_CACHE.npz',allow_pickle=False);h={k:z[k] for k in z.files};z.close();z=np.load(R/f'R9B_GAMMA_DYNAMIC_NET_003_{m:02d}_RETEST_CACHE.npz',allow_pickle=False);q={k:z[k] for k in z.files};z.close()
 o=h['o_60'];hi=h['h_60'];lo=h['l_60'];c=h['c_60'];atr=h['atr_60'];end=h['end_60'];lp=h['long_60'][:,5];sp=h['short_60'][:,5];mend=q['m15_end'];mo=q['m15_o'];mc=q['m15_c'];X=[];Y=[];T=[];S=[]
 for e,side,bound,a in q['bos']:
  i=int(np.searchsorted(end,int(e))); 
  if i>=len(end) or end[i]!=int(e) or not np.isfinite(a) or a<=0:continue
  rng=max(float(hi[i]-lo[i]),1e-12); br=float(side*(c[i]-bound)/a); body=float(abs(c[i]-o[i])/rng); cl=float((c[i]-lo[i])/rng if side>0 else (hi[i]-c[i])/rng); aw=float((c[i]-lo[i])/rng if side<0 else (hi[i]-c[i])/rng)
  trs=[]
  for j in range(max(1,i-13),i+1):trs.append(max(hi[j]-lo[j],abs(hi[j]-c[j-1]),abs(lo[j]-c[j-1])))
  med=float(np.median(trs)) if trs else np.nan; ar=float(a/(med+1e-12)); e3=eff(c,3,i);e6=eff(c,6,i);a3=float(np.mean(side*np.diff(c[i-3:i+1])>0)) if i>=3 else np.nan;a6=float(np.mean(side*np.diff(c[i-6:i+1])>0)) if i>=6 else np.nan
  j=np.searchsorted(mend,int(e),side='right')-1
  vals=[]
  for n in (4,8):
   if j<n:vals += [np.nan,np.nan]
   else:
    d=np.diff(mc[j-n:j+1]);align=float(np.mean(side*d>0));conf=float(np.mean(side*d<0));vals += [align,conf]
  me=[]
  for n in (4,8):
   if j<n:me.append(np.nan)
   else:
    d=np.diff(mc[j-n:j+1]);me.append(float(abs(mc[j]-mc[j-n])/(np.sum(np.abs(d))+1e-12)))
  x=[br,body,cl,aw,ar,e3,e6,a3,a6,vals[0],vals[2],vals[1],vals[3],me[0],me[1]];p=lp[i] if side>0 else sp[i]
  if np.isfinite(p):X.append(x);Y.append(float(p));T.append(int(e));S.append(int(side))
 out=R/f'R9B_GAMMA_DYNAMIC_NET_004_{m:02d}_STATE_CACHE.npz';np.savez_compressed(out,X=np.asarray(X,float),pnl=np.asarray(Y,float),time=np.asarray(T,np.int64),side=np.asarray(S,np.int8));man={'unit':'R9B_GAMMA_DYNAMIC_NET_004_STRUCTURAL_STATE_SPECIALIST','phase':'STATE_CACHE','month':m,'status':'COMPLETED_LOCAL','rows':len(Y),'feature_names':FEATURE_NAMES,'target':'Frozen NET002 H1 BOS 8h exact bid/ask PnL; future outcome is training label only.','inputs':{'net002_cache_sha256':sha(R/f'R9B_GAMMA_DYNAMIC_NET_002_{m:02d}_HTF_CACHE.npz'),'net003_cache_sha256':sha(R/f'R9B_GAMMA_DYNAMIC_NET_003_{m:02d}_RETEST_CACHE.npz')},'source_sha256':sha(__file__),'output_sha256':sha(out),'august_accessed':False};(R/f'R9B_GAMMA_DYNAMIC_NET_004_{m:02d}_STATE_CACHE_MANIFEST.json').write_text(json.dumps(man,indent=2)+'\n');print(json.dumps(man))
def load(m):
 z=np.load(R/f'R9B_GAMMA_DYNAMIC_NET_004_{m:02d}_STATE_CACHE.npz');d={k:z[k] for k in z.files};z.close();return d
def prob(clf,X):
 ok=np.all(np.isfinite(X),1);p=np.full(len(X),np.nan);j=np.where(clf.classes_==1)[0];
 if len(j):p[ok]=clf.predict_proba(X[ok])[:,int(j[0])]
 elif len(clf.classes_)==1:p[ok]=1. if clf.classes_[0]==1 else 0.
 return p
def screen():
 D={m:load(m) for m in (1,2,3,4)};rows=[]
 for mode,idx in SETS.items():
  for depth in (1,2,3):
   for leaf in (8,12,16,24):
    for w0 in (1.,1.5,2.,3.):
     for thr in (.40,.45,.50,.55,.60,.65):
      rep={};valid=True
      for holdout in (1,2,3):
       tr=[m for m in (1,2,3) if m!=holdout];Xt=np.vstack([D[m]['X'][:,idx] for m in tr]);yt=np.concatenate([(D[m]['pnl']>0).astype(np.int8) for m in tr]);ok=np.all(np.isfinite(Xt),1)
       if ok.sum()<2*leaf:valid=False;break
       clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,class_weight={0:w0,1:1},random_state=304).fit(Xt[ok],yt[ok]);X=D[holdout]['X'][:,idx];pr=prob(clf,X);sel=np.isfinite(pr)&(pr>=thr);met=metric(D[holdout]['pnl'][sel]);cov=float(sel.mean()*100);rep[str(holdout)]={'metrics':met,'coverage_pct':cov}
       if met['trades']<10 or met['net']<=0 or met['pf'] is None or met['pf']<=1:valid=False
      if rep:
       rows.append({'mode':mode,'depth':depth,'leaf':leaf,'w0':w0,'threshold':thr,'replication':rep,'eligible':valid,'min_net':min(v['metrics']['net'] for v in rep.values()),'sum_net':sum(v['metrics']['net'] for v in rep.values()),'min_pf':min(v['metrics']['pf'] if v['metrics']['pf'] is not None else 999 for v in rep.values()),'min_coverage':min(v['coverage_pct'] for v in rep.values())})
 elig=[r for r in rows if r['eligible']];best=max(elig,key=lambda r:(r['min_net'],r['sum_net'],r['min_pf'],r['min_coverage'])) if elig else None;ap=None;gate=False;model=None
 if best:
  idx=SETS[best['mode']];Xt=np.vstack([D[m]['X'][:,idx] for m in (1,2,3)]);yt=np.concatenate([(D[m]['pnl']>0).astype(np.int8) for m in (1,2,3)]);ok=np.all(np.isfinite(Xt),1);clf=DecisionTreeClassifier(max_depth=best['depth'],min_samples_leaf=best['leaf'],class_weight={0:best['w0'],1:1},random_state=304).fit(Xt[ok],yt[ok]);pr=prob(clf,D[4]['X'][:,idx]);sel=np.isfinite(pr)&(pr>=best['threshold']);ap={'metrics':metric(D[4]['pnl'][sel]),'coverage_pct':float(sel.mean()*100)};gate=ap['metrics']['trades']>=10 and ap['metrics']['net']>0 and ap['metrics']['pf'] is not None and ap['metrics']['pf']>1
  tr=clf.tree_;model={'feature_set':best['mode'],'feature_names':[FEATURE_NAMES[i] for i in idx],'hyperparameters':{k:best[k] for k in ('depth','leaf','w0','threshold')},'classes':[int(x) for x in clf.classes_],'children_left':[int(x) for x in tr.children_left],'children_right':[int(x) for x in tr.children_right],'feature':[int(x) for x in tr.feature],'threshold':[float(x) for x in tr.threshold]}
 out={'unit':'R9B_GAMMA_DYNAMIC_NET_004_STRUCTURAL_STATE_SPECIALIST','phase':'JAN_MAR_LEAVE_ONE_MONTH_OUT_DISCOVERY_THEN_APRIL_CALIBRATION','status':'COMPLETED_LOCAL_SCREEN','parent':'Frozen NET002 H1 BOS 8h trade geometry. Router may only abstain; it cannot change direction, entry timestamp or exit horizon.','features':FEATURE_NAMES,'eligible_candidates':len(elig),'frozen_candidate':best,'april':ap,'april_gate_pass':gate,'model':model,'decision':'FREEZE_FOR_MAY_JUL_FORWARD' if gate else 'REJECT_STRUCTURAL_STATE_ROUTER','next_unit':'R9B_GAMMA_DYNAMIC_NET_004_MAY_JUL_FROZEN_FORWARD' if gate else 'R9B_GAMMA_DYNAMIC_NET_005_ORTHOGONAL_H4_SPECIALIST','top':sorted(rows,key=lambda r:(r['eligible'],r['min_net'],r['sum_net'],r['min_pf']),reverse=True)[:30],'may_july_accessed':False,'august_accessed':False};op=R/'R9B_GAMMA_DYNAMIC_NET_004_STRUCTURAL_STATE_SPECIALIST.json';op.write_text(json.dumps(out,indent=2)+'\n');(R/'R9B_GAMMA_DYNAMIC_NET_004_MANIFEST.json').write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(op),'cache_sha256':{str(m):sha(R/f'R9B_GAMMA_DYNAMIC_NET_004_{m:02d}_STATE_CACHE.npz') for m in (1,2,3,4)},'august_accessed':False},indent=2)+'\n');print(json.dumps({'eligible':len(elig),'best':best,'april':ap,'gate':gate,'decision':out['decision'],'result_sha256':sha(op)},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['build','screen']);ap.add_argument('--month',type=int);a=ap.parse_args();
 if a.phase=='build':assert a.month in (1,2,3,4,5,6,7);build(a.month)
 else:screen()
