import json, hashlib, time
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier

R=Path('/mnt/data/r9b_active')
MODEL=R/'R9B_GAMMA_DYNAMIC_GL_001_JAN_OWNERSHIP_MODEL.json'
C={1:R/'R9B_GAMMA_DYNAMIC_GL_001_JAN_CACHE.npz',2:R/'R9B_GAMMA_DYNAMIC_GL_001_FEB_CACHE.npz',3:R/'R9B_GAMMA_DYNAMIC_GL_001_MAR_CACHE.npz'}
S={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_009_{m:02d}_SEQUENCE.npz' for m in (1,2,3)}
OUT=R/'R9B_GAMMA_DYNAMIC_ENTRY_016_SECOND_WAVE_REQUALIFICATION_CAPACITY.json'
MAN=R/'R9B_GAMMA_DYNAMIC_ENTRY_016_MANIFEST.json'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def bf(F):
 rg=(F[:,14]//10).astype(int)
 return np.column_stack([F[:,:14],F[:,14]-10*rg])

def frozen(A,bm):
 tr=bm['model']; cl=np.array(tr['children_left']); cr=np.array(tr['children_right']); ft=np.array(tr['feature']); th=np.array(tr['threshold']); vv=np.array(tr['value'])[:,0,:]; cs=np.array(tr['classes'],np.int8); q=float(tr['confidence_threshold'])
 out=np.zeros(len(A),np.int8); cf=np.zeros(len(A)); ok=np.all(np.isfinite(A),1)
 for i in np.where(ok)[0]:
  n=0
  while cl[n]!=-1: n=cl[n] if A[i,ft[n]]<=th[n] else cr[n]
  v=vv[n]; p=v/v.sum(); j=int(np.argmax(p)); cf[i]=p[j]; out[i]=cs[j] if p[j]>=q else 0
 return out,cf

def metric(p):
 p=np.asarray(p,float); p=p[np.isfinite(p)]
 if len(p)==0:return {'trades':0,'winners':0,'win_rate':0,'net':0,'gp':0,'gl':0,'pf':None,'expectancy':None,'avg_win':None,'avg_loss':None}
 w=p>0;l=p<0;gp=float(p[w].sum());gl=float(p[l].sum())
 return {'trades':int(len(p)),'winners':int(w.sum()),'win_rate':float(w.mean()),'net':float(p.sum()),'gp':gp,'gl':gl,'pf':float(gp/-gl) if gl<0 else None,'expectancy':float(p.mean()),'avg_win':float(p[w].mean()) if w.any() else None,'avg_loss':float(p[l].mean()) if l.any() else None}

def delta(base,cand):
 return {'net_improvement':cand['net']-base['net'],'gl_reduction_pct':(abs(base['gl'])-abs(cand['gl']))/abs(base['gl'])*100 if base['gl'] else None,'winner_retention_pct':cand['winners']/base['winners']*100 if base['winners'] else None,'trade_retention_pct':cand['trades']/base['trades']*100 if base['trades'] else None}

def build_month(m,bm):
 z0=np.load(C[m],allow_pickle=False); z={k:z0[k] for k in z0.files}; z0.close()
 s0=np.load(S[m],allow_pickle=False); SV=s0['S'].copy(); s0.close()
 B=bf(z['F']); ba,bc=frozen(B,bm)
 X,Of,Oc=z['X'],z['Of'],z['Oc']
 prev_close=-9223372036854775807; prev=None; ord_by_min={}; rows=[]
 for i,a in enumerate(ba):
  if a==0:continue
  O=Of if a==1 else Oc
  if O[i,6]<.5:continue
  sig=int(X[i,0])
  if sig<=prev_close:continue
  side=int(X[i,1]) if a==1 else -int(X[i,1]); minute=sig//60000; ord_=ord_by_min.get(minute,0)+1; ord_by_min[minute]=ord_
  if ord_==2 and prev is not None and prev['minute']==minute and side!=prev['side']:
   gap_ms=sig-prev['close']; prior_pnl=prev['pnl']; prior_hold=prev['hold']; prior_win=1.0 if prior_pnl>0 else (-1.0 if prior_pnl<0 else 0.0)
   feat=np.concatenate([B[i],SV[i],[bc[i],float(a),np.clip(prior_pnl,-3,3),prior_hold,prior_win,gap_ms/1000.]])
   best=max(Of[i,0],Oc[i,0]); y=0 if best<=0 else (1 if Of[i,0]>=Oc[i,0] else 2)
   rows.append({'i':i,'day':int(z['day_idx'][i]),'feat':feat,'base_a':int(a),'base_p':float(O[i,0]),'of':float(Of[i,0]),'oc':float(Oc[i,0]),'y':int(y),'prior_p':float(prior_pnl)})
  prev={'minute':minute,'side':side,'close':int(O[i,4]),'pnl':float(O[i,0]),'hold':float(O[i,1])}; prev_close=int(O[i,4])
 F=np.vstack([r['feat'] for r in rows]); y=np.array([r['y'] for r in rows],np.int8); base=np.array([r['base_p'] for r in rows]); of=np.array([r['of'] for r in rows]); oc=np.array([r['oc'] for r in rows]); days=np.array([r['day'] for r in rows],np.int16)
 return {'F':F,'y':y,'base':base,'of':of,'oc':oc,'days':days,'rows':rows}

def apply(clf,F,thr):
 ok=np.all(np.isfinite(F),1); out=np.zeros(len(F),np.int8)
 pr=clf.predict_proba(F[ok]); j=pr.argmax(1); mx=pr.max(1); lab=clf.classes_[j].astype(np.int8); lab[mx<thr]=0; out[ok]=lab
 return out

def pnl_from_actions(d,a):
 p=np.full(len(a),np.nan)
 p[a==1]=d['of'][a==1]; p[a==2]=d['oc'][a==2]
 return p[a!=0]

def main():
 t0=time.time(); bm=json.load(open(MODEL)); D={m:build_month(m,bm) for m in (1,2,3)}
 diag={}
 for m in (1,2,3):
  d=D[m]; oracle=np.maximum(d['of'],d['oc'])
  diag[str(m)]={'parent_second_opposite':metric(d['base']),'oracle_best_action':metric(oracle),'teacher_profitable_pct':float((oracle>0).mean()*100),'teacher_action_flip_pct':float((((d['y']==1)&(np.array([r['base_a'] for r in d['rows']])==2))|((d['y']==2)&(np.array([r['base_a'] for r in d['rows']])==1))).mean()*100)}
 d1=D[1]; tr=(d1['days']<14)&np.all(np.isfinite(d1['F']),1)
 rows=[]
 for depth in (2,3,4):
  for leaf in (50,100,200,300):
   if tr.sum()<leaf*3: continue
   for w0 in (1.0,1.5,2.0):
    clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,class_weight={0:w0,1:1,2:1},random_state=116).fit(d1['F'][tr],d1['y'][tr])
    for thr in (.40,.45,.50,.55,.60):
     row={'depth':depth,'leaf':leaf,'class0_weight':w0,'threshold':thr,'months':{}}
     for m in (1,2,3):
      d=D[m]; mask=(d['days']>=14) if m==1 else np.ones(len(d['y']),bool); a=apply(clf,d['F'],thr); a=np.where(mask,a,0); base=d['base'][mask]; cand=pnl_from_actions(d,a); mm=metric(cand); bb=metric(base); row['months'][str(m)]={'base':bb,'candidate':mm,'delta':delta(bb,mm),'selected':int((a!=0).sum())}
     row['robust_positive']=all(row['months'][str(m)]['candidate']['net']>0 for m in (1,2,3))
     row['robust_improve']=all(row['months'][str(m)]['delta']['net_improvement']>0 and row['months'][str(m)]['delta']['gl_reduction_pct']>0 for m in (1,2,3))
     row['min_trade_retention']=min(row['months'][str(m)]['delta']['trade_retention_pct'] for m in (1,2,3))
     row['min_winner_retention']=min(row['months'][str(m)]['delta']['winner_retention_pct'] for m in (1,2,3))
     row['min_gl_reduction']=min(row['months'][str(m)]['delta']['gl_reduction_pct'] for m in (1,2,3))
     row['sum_net']=sum(row['months'][str(m)]['candidate']['net'] for m in (1,2,3)); rows.append(row)
 elig=[r for r in rows if r['robust_positive'] and r['robust_improve']]
 elig30=[r for r in elig if r['min_trade_retention']>=30]
 key=lambda r:(r['min_trade_retention'],r['sum_net'],r['min_gl_reduction'],r['min_winner_retention'])
 best=max(elig30,key=key) if elig30 else (max(elig,key=key) if elig else None)
 out={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_016_SECOND_WAVE_REQUALIFICATION_CAPACITY','status':'COMPLETED_LOCAL_DIAGNOSTIC','parent':'GL001 / Gamma014','purpose':'Test whether the R9 SYNTH second/opposite re-entry phenomenon survives naively in causal Gamma, then test a transparent pre-entry requalification/action owner inside that state. This is a capacity map only; parent-conditioned second-wave identity is not yet a self-consistent integrated state machine.','state_definition':'Second executed Gamma trade in the same UTC minute, after prior trade close, with current executed direction opposite the prior trade direction. Prior trade outcome/hold/gap are observable before the second signal.','features':['GL001 causal base features including regime confidence','pre-entry reclaim/secondary-transition sequence features from ENTRY009','GL001 confidence/action','prior realized PnL clipped','prior realized hold','prior win/loss sign','seconds since prior close'],'teacher':'Current-lifecycle FADE vs CONTINUE future outcomes are training labels only; never execution features.','training':'January first 14 trading days only','replication':['January heldout','February','March'],'naive_r9_pattern_diagnostic':diag,'screen_count':len(rows),'eligible_robust':len(elig),'eligible_robust_density30':len(elig30),'best':best,'top':sorted(rows,key=lambda r:(r['robust_positive'],r['robust_improve'],r['min_trade_retention'],r['sum_net']),reverse=True)[:20],'interpretation':'If naive second/opposite remains negative but a causal requalification owner creates replicated positive expectancy, proceed to a self-consistent chronological state machine. Otherwise reject direct transplantation of the R9 SYNTH re-entry effect.','august_accessed':False,'elapsed_s':time.time()-t0}
 OUT.write_text(json.dumps(out,indent=2)+'\n')
 MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'input_sha256':{str(m):{'gl001_cache':sha(C[m]),'sequence_cache':sha(S[m])} for m in (1,2,3)},'august_accessed':False},indent=2)+'\n')
 print(json.dumps({'diag':diag,'screen_count':len(rows),'eligible':len(elig),'eligible30':len(elig30),'best':best,'result_sha256':sha(OUT),'source_sha256':sha(__file__),'elapsed_s':out['elapsed_s']},indent=2))
if __name__=='__main__':main()
