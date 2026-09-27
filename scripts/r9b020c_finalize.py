import json, hashlib
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier
BROOT=Path('/mnt/data/r9b020b_cache'); CROOT=Path('/mnt/data/r9b020c_cache')
BASE=['owner_tf','owner_align','owner_dist','owner_age','owner_bos_age','owner_depth','lower_confirm','lower_conflict','struct_align_count','struct_conflict_count']
OWNER=['owner_pen_align','owner_pen_type','owner_pen_age','owner_pen_depth','owner_reclaim_depth','owner_touch_count','owner_level_age','owner_accept_quality','owner_first_pen','owner_fail_align','owner_fail_age','owner_fail_depth','owner_active_acc_align','owner_active_acc_age']
SUMMARY=['accept_same_count','accept_opp_count','sweep_same_count','sweep_opp_count','fail_same_count','fail_opp_count','active_accept_same_count','active_accept_opp_count','recent_pen_count']
BFEAT=BASE+OWNER+SUMMARY
N=['pe','te','irr','forbid','edge_p','cur_self','cur_max','cur_h','pat_age']+[f'p{i}' for i in range(6)]
idx={n:i for i,n in enumerate(N)}
parts=[]; os=[]
for m in range(1,8):
    b=pd.read_pickle(BROOT/f'R9B_020B_M{m:02d}.pkl.gz',compression='gzip')
    parts.append(b[['month','cont_pnl','fade_pnl']+BFEAT].copy())
    z=np.load(CROOT/f'R9B_020C_M{m:02d}.npz')
    os.append(z['TICK_D3_W90'].astype(np.float32))
d=pd.concat(parts,ignore_index=True); O=np.concatenate(os).astype(float)
y=np.where(np.maximum(d.cont_pnl.values,d.fade_pnl.values)<=0,2,np.where(d.cont_pnl.values>=d.fade_pnl.values,1,0))
tr=d.month.values<=3
XB=d[BFEAT].replace([np.inf,-np.inf],np.nan).fillna(99.).to_numpy(float)
def metric(p,m):
    x=p[m]; x=x[np.isfinite(x)]
    eq=np.cumsum(x); peak=np.maximum.accumulate(np.r_[0.,eq]); dd=peak[1:]-eq if len(eq) else np.array([])
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'trades':int(len(x)),'winners':int((x>0).sum()),'win_rate':float((x>0).mean()) if len(x) else 0.,'net':float(x.sum()),'gross_profit':gp,'gross_loss':gl,'profit_factor':float(gp/abs(gl)) if gl<0 else 0.,'max_drawdown_trade_sequence':float(dd.max()) if len(dd) else 0.}
# Baseline 020-B
mb=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.,1:1.,2:1.5},random_state=17).fit(XB[tr],y[tr])
pr=mb.predict_proba(XB); cl=mb.classes_; pred=cl[np.argmax(pr,1)]; conf=np.max(pr,1)
bp=np.where((pred!=2)&(conf>=.45),np.where(pred==1,d.cont_pnl.values,d.fade_pnl.values),np.nan)
# Selected narrow ordinal subset from April-only calibration
ss=['pe','te','irr','forbid']; cols=[idx[x] for x in ss]
X=np.hstack([XB,O[:,cols]])
mc=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.,1:1.,2:1.5},random_state=17).fit(X[tr],y[tr])
pr=mc.predict_proba(X); cl=mc.classes_; pred=cl[np.argmax(pr,1)]; conf=np.max(pr,1)
cp=np.where((pred!=2)&(conf>=.45),np.where(pred==1,d.cont_pnl.values,d.fade_pnl.values),np.nan)
monthly=[]
for m in range(1,8):
    mm=d.month.values==m; b=metric(bp,mm); c=metric(cp,mm)
    monthly.append({'month':m,'stageB':b,'stageC':c,'delta':{'net':c['net']-b['net'],'gross_loss_improvement':c['gross_loss']-b['gross_loss'],'winners':c['winners']-b['winners'],'win_rate_pp':100*(c['win_rate']-b['win_rate']),'max_drawdown_improvement':b['max_drawdown_trade_sequence']-c['max_drawdown_trade_sequence']}})
spans={
 'april': d.month.values==4,
 'may_jun':np.isin(d.month.values,[5,6]),
 'july':d.month.values==7,
 'may_jul':d.month.values>=5,
 'jan_jul':d.month.values<=7,
}
res={}
for k,m in spans.items():
    b=metric(bp,m); c=metric(cp,m)
    res[k]={'stageB':b,'stageC':c,'delta':{'net':c['net']-b['net'],'gross_loss_improvement':c['gross_loss']-b['gross_loss'],'winners':c['winners']-b['winners'],'win_rate_pp':100*(c['win_rate']-b['win_rate']),'trades':c['trades']-b['trades'],'max_drawdown_improvement':b['max_drawdown_trade_sequence']-c['max_drawdown_trade_sequence']}}
feat=BFEAT+[f'TICK_D3_W90_{x}' for x in ss]
imp=sorted([{'feature':feat[i],'importance':float(v)} for i,v in enumerate(mc.feature_importances_) if v>0],key=lambda z:-z['importance'])
out={'unit':'R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_C_ORDINAL_TRANSITION','status':'VERIFIED_DURABLE_DIAGNOSTIC_REJECTED','decision':'DO_NOT_PROMOTE','selected_variant':'TICK_D3_W90_COMPLEX','selected_threshold':0.45,'selected_ordinal_features':ss,'architecture':'020-A hierarchical owner + 020-B acceptance/sweep context frozen; ordinal transition representation added only as contextual features to the same transparent CART','validation':'Jan-Mar discovery; April calibration; May-Jun strict forward; July stress-validation; August sealed','scoring_order':['gross_loss','winning_trades_and_success','net_profit'],'finding':'The best April-selected ordinal subset gives a small July improvement and tiny Jan-Jul net gain, but worsens May-Jun gross loss and full Jan-Jul gross loss. The effect is not durable and does not add integrated system value. Preserve ordinal transition descriptors as research context only.','spans':res,'monthly':monthly,'feature_importance':imp,'august_accessed':False}
Path('/mnt/data/r9b020c_cache/R9B_020C_FINAL.json').write_text(json.dumps(out,indent=2,sort_keys=True))
print(json.dumps(out,indent=2))
