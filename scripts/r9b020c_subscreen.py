import json, numpy as np, pandas as pd
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
BROOT=Path('/mnt/data/r9b020b_cache'); CROOT=Path('/mnt/data/r9b020c_cache')
BASE=['owner_tf','owner_align','owner_dist','owner_age','owner_bos_age','owner_depth','lower_confirm','lower_conflict','struct_align_count','struct_conflict_count']
OWNER=['owner_pen_align','owner_pen_type','owner_pen_age','owner_pen_depth','owner_reclaim_depth','owner_touch_count','owner_level_age','owner_accept_quality','owner_first_pen','owner_fail_align','owner_fail_age','owner_fail_depth','owner_active_acc_align','owner_active_acc_age']
SUMMARY=['accept_same_count','accept_opp_count','sweep_same_count','sweep_opp_count','fail_same_count','fail_opp_count','active_accept_same_count','active_accept_opp_count','recent_pen_count']
BFEAT=BASE+OWNER+SUMMARY
N=['pe','te','irr','forbid','edge_p','cur_self','cur_max','cur_h','pat_age']+[f'p{i}' for i in range(6)]
idx={n:i for i,n in enumerate(N)}
configs=['TICK_D3_W90','A1S_D3_W62','A1S_D3_W90','A1S_D3_W120','S5_D3_W62','S5_D3_W90','S15_D3_W62','M1_D3_W62']
parts=[]; oo={k:[] for k in configs}
for m in range(1,8):
 b=pd.read_pickle(BROOT/f'R9B_020B_M{m:02d}.pkl.gz',compression='gzip'); parts.append(b[['month','cont_pnl','fade_pnl']+BFEAT].copy())
 z=np.load(CROOT/f'R9B_020C_M{m:02d}.npz')
 for k in configs: oo[k].append(z[k].astype(np.float32))
d=pd.concat(parts,ignore_index=True); O={k:np.concatenate(v) for k,v in oo.items()}
y=np.where(np.maximum(d.cont_pnl.values,d.fade_pnl.values)<=0,2,np.where(d.cont_pnl.values>=d.fade_pnl.values,1,0)); tr=d.month.values<=3; ap=d.month.values==4
XB=d[BFEAT].replace([np.inf,-np.inf],np.nan).fillna(99.).to_numpy(float)
def met(p,m):
 x=p[m]; x=x[np.isfinite(x)]; gp=x[x>0].sum(); gl=x[x<0].sum(); return dict(trades=len(x),winners=int((x>0).sum()),win=float((x>0).mean()),net=float(x.sum()),gl=float(gl),gp=float(gp))
mb=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.,1:1.,2:1.5},random_state=17).fit(XB[tr],y[tr]); pr=mb.predict_proba(XB); cl=mb.classes_; pd=cl[np.argmax(pr,1)]; cf=np.max(pr,1); bp=np.where((pd!=2)&(cf>=.45),np.where(pd==1,d.cont_pnl.values,d.fade_pnl.values),np.nan)
Bap=met(bp,ap)
subsets={'EDGE':['edge_p'],'IRR':['irr'],'COMPLEX':['pe','te','irr','forbid'],'TRANS':['edge_p','cur_self','cur_max','cur_h','pat_age']+[f'p{i}' for i in range(6)],'FULL':N}
rows=[]
for k in configs:
 for sn,ss in subsets.items():
  if sn not in ('EDGE','IRR','COMPLEX','TRANS','FULL'): continue
  # Keep all subsets only for A1S90; for other configs only EDGE/TRANS/COMPLEX to bound search.
  if k!='A1S_D3_W90' and sn in ('IRR','FULL'): continue
  cols=[idx[x] for x in ss]; A=O[k][:,cols].astype(float)
  X=np.hstack([XB,A]); model=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.,1:1.,2:1.5},random_state=17).fit(X[tr],y[tr])
  pr=model.predict_proba(X); cc=model.classes_; pred=cc[np.argmax(pr,1)]; conf=np.max(pr,1); raw=np.where(pred==1,d.cont_pnl.values,d.fade_pnl.values)
  for th in [.35,.40,.45,.50,.55,.60]:
   p=np.where((pred!=2)&(conf>=th),raw,np.nan); a=met(p,ap); tret=a['trades']/Bap['trades']; wret=a['winners']/Bap['winners']; elig=tret>=.95 and wret>=.97
   rows.append((k,sn,th,elig,a['gl']-Bap['gl'],a['net']-Bap['net'],wret,tret,p,model,ss))
el=[r for r in rows if r[3]]; best=max(el,key=lambda r:(r[4],r[6],r[5]))
k,sn,th,elig,gli,ni,wret,tret,p,model,ss=best
masks={'may_jun':np.isin(d.month.values,[5,6]),'july':d.month.values==7,'may_jul':d.month.values>=5,'jan_jul':d.month.values<=7}
print(json.dumps({'best':{'config':k,'subset':sn,'threshold':th,'april_gl_improvement':gli,'april_net_improvement':ni,'winner_retention':wret,'trade_retention':tret},'forward':{q:{'B':met(bp,m),'C':met(p,m),'gl_improvement':met(p,m)['gl']-met(bp,m)['gl'],'net_change':met(p,m)['net']-met(bp,m)['net']} for q,m in masks.items()},'top_importance':sorted([[(BFEAT+['%s_%s'%(k,x) for x in ss])[i],float(v)] for i,v in enumerate(model.feature_importances_) if v>0], key=lambda x:-x[1])[:15]},indent=2))
