import json, hashlib
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier

C=Path('/mnt/data/r9b020b_cache')
BASE=['owner_tf','owner_align','owner_dist','owner_age','owner_bos_age','owner_depth',
      'lower_confirm','lower_conflict','struct_align_count','struct_conflict_count']
OWNER=['owner_pen_align','owner_pen_type','owner_pen_age','owner_pen_depth','owner_reclaim_depth',
       'owner_touch_count','owner_level_age','owner_accept_quality','owner_first_pen',
       'owner_fail_align','owner_fail_age','owner_fail_depth','owner_active_acc_align','owner_active_acc_age']
SUMMARY=['accept_same_count','accept_opp_count','sweep_same_count','sweep_opp_count',
         'fail_same_count','fail_opp_count','active_accept_same_count','active_accept_opp_count','recent_pen_count']
VARIANTS={'OWNER':BASE+OWNER,'SUMMARY':BASE+SUMMARY,'OWNER_SUMMARY':BASE+OWNER+SUMMARY}

def metrics(x):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    if len(x)==0: return {'trades':0,'winners':0,'win':0.,'net':0.,'gp':0.,'gl':0.,'pf':0.}
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    eq=np.cumsum(x); peak=np.maximum.accumulate(np.r_[0.0,eq]); curve=np.r_[0.0,eq]
    maxdd=float(np.max(peak-curve))
    return {'trades':int(len(x)),'winners':int((x>0).sum()),'win':float((x>0).mean()),
            'net':float(x.sum()),'gp':gp,'gl':gl,'pf':float(gp/(-gl)) if gl<0 else 1e9,'maxdd_trade_sequence':maxdd}

frames=[]
for m in range(1,8):
    frames.append(pd.read_pickle(C/f'R9B_020B_M{m:02d}.pkl.gz',compression='gzip'))
d=pd.concat(frames,ignore_index=True)
y=np.where(np.maximum(d.cont_pnl.values,d.fade_pnl.values)<=0,2,
           np.where(d.cont_pnl.values>=d.fade_pnl.values,1,0))
train=d.month.values<=3; apr=d.month.values==4

ma=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.,1:1.,2:1.5},random_state=17)
Xa=d[BASE].replace([np.inf,-np.inf],np.nan).fillna(99.).to_numpy(float)
ma.fit(Xa[train],y[train])
pra=ma.predict_proba(Xa); ca=ma.classes_; preda=ca[np.argmax(pra,axis=1)]; confa=np.max(pra,axis=1)
acta=(preda!=2)&(confa>=.45)
pnla=np.where(preda==1,d.cont_pnl.values,d.fade_pnl.values)
stageA=np.where(acta,pnla,np.nan)

period_masks={'jan_mar':d.month.values<=3,'april':apr,'may_jun':np.isin(d.month.values,[5,6]),
              'july':d.month.values==7,'jan_jul':d.month.values<=7,'may_jul':d.month.values>=5}
A={k:metrics(stageA[m]) for k,m in period_masks.items()}
A['months']={str(m):metrics(stageA[d.month.values==m]) for m in range(1,8)}

candidates=[]
thresholds=[.35,.40,.45,.50,.55,.60]
for name,feat in VARIANTS.items():
    X=d[feat].replace([np.inf,-np.inf],np.nan).fillna(99.).to_numpy(float)
    model=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.,1:1.,2:1.5},random_state=17)
    model.fit(X[train],y[train])
    pr=model.predict_proba(X); cls=model.classes_; pred=cls[np.argmax(pr,axis=1)]; conf=np.max(pr,axis=1)
    for th in thresholds:
        act=(pred!=2)&(conf>=th)
        raw=np.where(pred==1,d.cont_pnl.values,d.fade_pnl.values)
        p=np.where(act,raw,np.nan)
        apm=metrics(p[apr]); ar=A['april']
        trret=apm['trades']/max(1,ar['trades']); wret=apm['winners']/max(1,ar['winners'])
        eligible=(trret>=.95 and wret>=.97)
        candidates.append({'variant':name,'threshold':th,'eligible':eligible,
                           'trade_retention_vs_A':trret,'winner_retention_vs_A':wret,
                           'april':apm,'april_gl_improvement_vs_A':apm['gl']-ar['gl'],
                           'april_net_improvement_vs_A':apm['net']-ar['net'],
                           'features':feat,'feature_importance':{f:float(v) for f,v in zip(feat,model.feature_importances_) if v>0},
                           '_p':p,'_model':model,'_pred':pred,'_conf':conf})
elig=[x for x in candidates if x['eligible']]
pick=max(elig,key=lambda x:(x['april_gl_improvement_vs_A'],x['winner_retention_vs_A'],x['april_net_improvement_vs_A'])) if elig else max(candidates,key=lambda x:(x['winner_retention_vs_A']+x['trade_retention_vs_A'],x['april_gl_improvement_vs_A'],x['april_net_improvement_vs_A']))
p=pick['_p']
Bres={k:metrics(p[m]) for k,m in period_masks.items()}
Bres['months']={str(m):metrics(p[d.month.values==m]) for m in range(1,8)}
delta={}
for k in ['april','may_jun','july','jan_jul','may_jul']:
    a=A[k]; b=Bres[k]
    delta[k]={'net_change':b['net']-a['net'],'gl_improvement':b['gl']-a['gl'],
              'trades_delta':b['trades']-a['trades'],'winners_delta':b['winners']-a['winners'],
              'win_pp':100*(b['win']-a['win']),
              'trade_retention':b['trades']/max(1,a['trades']),
              'winner_retention':b['winners']/max(1,a['winners'])}
public_candidates=[]
for x in candidates:
    public_candidates.append({k:v for k,v in x.items() if not k.startswith('_') and k not in ('features','feature_importance')})
out={
 'unit':'R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_B_ACCEPTANCE_SWEEP',
 'status':'COMPLETED_LOCAL_PENDING_DURABLE_REVIEW',
 'architecture':'020-A structural owner frozen; acceptance/sweep memory added only; same depth-4/min-leaf-800 transparent CART; April selects confidence threshold',
 'features_selected':pick['features'],
 'selected_variant':pick['variant'],'selected_threshold':pick['threshold'],
 'april_selection':{k:v for k,v in pick.items() if k not in ('_p','_model','_pred','_conf','features','feature_importance')},
 'feature_importance':pick['feature_importance'],
 'stageA_reference':A,'stageB':Bres,'delta_vs_stageA':delta,
 'candidate_grid':public_candidates,
 'validation':'Jan-Mar discovery; April calibration; May-Jun strict forward; July stress validation; August sealed',
 'scoring_order':['gross_loss','winning_trades_and_success','net_profit'],
 'august_accessed':False,
}
out_path=C/'R9B_020B_RESULT.json'
json.dump(out,open(out_path,'w'),indent=2,sort_keys=True)
out['result_sha256']=hashlib.sha256(out_path.read_bytes()).hexdigest()
json.dump(out,open(out_path,'w'),indent=2,sort_keys=True)
print(json.dumps({
 'selected_variant':out['selected_variant'],'threshold':out['selected_threshold'],
 'A_april':A['april'],'B_april':Bres['april'],
 'A_may_jun':A['may_jun'],'B_may_jun':Bres['may_jun'],
 'A_july':A['july'],'B_july':Bres['july'],
 'A_jan_jul':A['jan_jul'],'B_jan_jul':Bres['jan_jul'],
 'delta':delta,'top_features':list(out['feature_importance'].items())[:20]
},indent=2))
