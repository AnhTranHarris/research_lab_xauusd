import json, hashlib
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier

BROOT=Path('/mnt/data/r9b020b_cache')
CROOT=Path('/mnt/data/r9b020c_cache')
BASE=['owner_tf','owner_align','owner_dist','owner_age','owner_bos_age','owner_depth',
      'lower_confirm','lower_conflict','struct_align_count','struct_conflict_count']
OWNER=['owner_pen_align','owner_pen_type','owner_pen_age','owner_pen_depth','owner_reclaim_depth',
       'owner_touch_count','owner_level_age','owner_accept_quality','owner_first_pen',
       'owner_fail_align','owner_fail_age','owner_fail_depth','owner_active_acc_align','owner_active_acc_age']
SUMMARY=['accept_same_count','accept_opp_count','sweep_same_count','sweep_opp_count',
         'fail_same_count','fail_opp_count','active_accept_same_count','active_accept_opp_count','recent_pen_count']
BFEAT=BASE+OWNER+SUMMARY
CONFIGS=['TICK_D3_W90','A1S_D3_W62','A1S_D3_W90','A1S_D3_W120','S5_D3_W62','S5_D3_W90','S15_D3_W62','M1_D3_W62']
METRIC_NAMES=['pe','te','irr','forbid','edge_p','cur_self','cur_max','cur_h','pat_age']+[f'p{i}' for i in range(6)]

def metrics(x):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    if len(x)==0: return {'trades':0,'winners':0,'win':0.,'net':0.,'gp':0.,'gl':0.,'pf':0.,'maxdd_trade_sequence':0.}
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    eq=np.cumsum(x); curve=np.r_[0.0,eq]; peak=np.maximum.accumulate(curve)
    maxdd=float(np.max(peak-curve))
    return {'trades':int(len(x)),'winners':int((x>0).sum()),'win':float((x>0).mean()),
            'net':float(x.sum()),'gp':gp,'gl':gl,'pf':float(gp/(-gl)) if gl<0 else 1e9,
            'maxdd_trade_sequence':maxdd}

# Load only the compact fields needed from 020-B and align ordinal caches by event timestamp.
parts=[]; ordparts={k:[] for k in CONFIGS}
for m in range(1,8):
    b=pd.read_pickle(BROOT/f'R9B_020B_M{m:02d}.pkl.gz',compression='gzip')
    keep=['month','time_ms','side','cont_pnl','fade_pnl']+BFEAT
    parts.append(b[keep].copy())
    z=np.load(CROOT/f'R9B_020C_M{m:02d}.npz')
    if len(z['event_ms'])!=len(b) or not np.array_equal(z['event_ms'],b.time_ms.to_numpy(np.int64)):
        raise RuntimeError(f'020-C event alignment mismatch month {m}')
    for k in CONFIGS: ordparts[k].append(z[k].astype(np.float32))
    del b,z
d=pd.concat(parts,ignore_index=True); del parts
O={k:np.concatenate(v,axis=0) for k,v in ordparts.items()}; del ordparts

y=np.where(np.maximum(d.cont_pnl.values,d.fade_pnl.values)<=0,2,
           np.where(d.cont_pnl.values>=d.fade_pnl.values,1,0))
train=d.month.values<=3; apr=d.month.values==4
period_masks={'jan_mar':d.month.values<=3,'april':apr,'may_jun':np.isin(d.month.values,[5,6]),
              'july':d.month.values==7,'jan_jul':d.month.values<=7,'may_jul':d.month.values>=5}

# Reproduce the selected 020-B OWNER_SUMMARY baseline exactly.
XB=d[BFEAT].replace([np.inf,-np.inf],np.nan).fillna(99.).to_numpy(float)
mb=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.,1:1.,2:1.5},random_state=17)
mb.fit(XB[train],y[train]); pr=mb.predict_proba(XB); cls=mb.classes_; pred=cls[np.argmax(pr,axis=1)]; conf=np.max(pr,axis=1)
act=(pred!=2)&(conf>=.45); raw=np.where(pred==1,d.cont_pnl.values,d.fade_pnl.values); bp=np.where(act,raw,np.nan)
B={k:metrics(bp[m]) for k,m in period_masks.items()}; B['months']={str(m):metrics(bp[d.month.values==m]) for m in range(1,8)}

thresholds=[.35,.40,.45,.50,.55,.60]
candidates=[]
for name in CONFIGS:
    a=O[name]
    # NaNs are explicitly unavailable; 99 sentinel matches established transparent-tree convention.
    X=np.hstack([XB,a.astype(np.float64)])
    feat=BFEAT+[f'{name}_{q}' for q in METRIC_NAMES]
    model=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.,1:1.,2:1.5},random_state=17)
    model.fit(X[train],y[train]); pr=model.predict_proba(X); cc=model.classes_; pp=cc[np.argmax(pr,axis=1)]; cf=np.max(pr,axis=1)
    raw=np.where(pp==1,d.cont_pnl.values,d.fade_pnl.values)
    imp={f:float(v) for f,v in zip(feat,model.feature_importances_) if v>0}
    for th in thresholds:
        use=(pp!=2)&(cf>=th); p=np.where(use,raw,np.nan)
        am=metrics(p[apr]); br=B['april']
        trret=am['trades']/max(1,br['trades']); wret=am['winners']/max(1,br['winners'])
        eligible=(trret>=.95 and wret>=.97)
        candidates.append({'variant':name,'threshold':th,'eligible':eligible,
                           'trade_retention_vs_B':trret,'winner_retention_vs_B':wret,
                           'april':am,'april_gl_improvement_vs_B':am['gl']-br['gl'],
                           'april_net_improvement_vs_B':am['net']-br['net'],
                           'feature_importance':imp,'_p':p})

elig=[x for x in candidates if x['eligible']]
pick=max(elig,key=lambda x:(x['april_gl_improvement_vs_B'],x['winner_retention_vs_B'],x['april_net_improvement_vs_B'])) if elig else max(candidates,key=lambda x:(x['winner_retention_vs_B']+x['trade_retention_vs_B'],x['april_gl_improvement_vs_B'],x['april_net_improvement_vs_B']))
p=pick['_p']
C={k:metrics(p[m]) for k,m in period_masks.items()}; C['months']={str(m):metrics(p[d.month.values==m]) for m in range(1,8)}

delta={}
for k in ['april','may_jun','july','may_jul','jan_jul']:
    a=B[k]; b=C[k]
    delta[k]={'net_change':b['net']-a['net'],'gl_improvement':b['gl']-a['gl'],
              'trades_delta':b['trades']-a['trades'],'winners_delta':b['winners']-a['winners'],
              'win_pp':100*(b['win']-a['win']),
              'trade_retention':b['trades']/max(1,a['trades']),
              'winner_retention':b['winners']/max(1,a['winners']),
              'maxdd_change':b['maxdd_trade_sequence']-a['maxdd_trade_sequence']}

public=[]
for x in candidates:
    public.append({k:v for k,v in x.items() if k!='_p' and k!='feature_importance'})
# Compact per-variant best eligible April choice for diagnostics.
variant_best={}
for name in CONFIGS:
    xs=[x for x in candidates if x['variant']==name and x['eligible']]
    if not xs: xs=[x for x in candidates if x['variant']==name]
    q=max(xs,key=lambda x:(x['april_gl_improvement_vs_B'],x['winner_retention_vs_B'],x['april_net_improvement_vs_B']))
    variant_best[name]={k:v for k,v in q.items() if k not in ('_p','feature_importance')}

out={
 'unit':'R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_C_ORDINAL_TRANSITION',
 'status':'COMPLETED_LOCAL_PENDING_DURABLE_REVIEW',
 'architecture':'020-B structural ownership + acceptance/sweep context frozen; add one ordinal-transition representation at a time; same depth-4/min-leaf-800 transparent CART; April selects representation/threshold only',
 'ordinal_method':{
   'source_transform':'causal log returns; event-side normalized before ordinal encoding',
   'embedding_dimension':3,
   'patterns':6,
   'metrics':['permutation entropy','transition entropy','forward/reverse JSD irreversibility','forbidden fraction','last-edge conditional probability','current-node self-transition probability','current-node outgoing concentration','current-node outgoing entropy','current-pattern age','one-hot current ordinal state'],
   'anti_lookahead':'tick series may include the observed trigger tick; active-second and fixed bars use only completed intervals available at event time'
 },
 'selected_variant':pick['variant'],'selected_threshold':pick['threshold'],
 'feature_importance':pick['feature_importance'],
 'stageB_reference':B,'stageC':C,'delta_vs_stageB':delta,
 'variant_best_april':variant_best,'candidate_grid':public,
 'validation':'Jan-Mar discovery; April calibration; May-Jun strict forward; July stress/frozen evaluation; May-Jul combined reported; August sealed',
 'scoring_order':['gross_loss','winning_trades_and_success','net_profit'],
 'august_accessed':False,
}
outp=CROOT/'R9B_020C_RESULT.json'
json.dump(out,open(outp,'w'),indent=2,sort_keys=True)
out['result_sha256']=hashlib.sha256(outp.read_bytes()).hexdigest()
json.dump(out,open(outp,'w'),indent=2,sort_keys=True)
print(json.dumps({
 'selected_variant':out['selected_variant'],'threshold':out['selected_threshold'],
 'B_april':B['april'],'C_april':C['april'],
 'B_may_jun':B['may_jun'],'C_may_jun':C['may_jun'],
 'B_july':B['july'],'C_july':C['july'],
 'B_may_jul':B['may_jul'],'C_may_jul':C['may_jul'],
 'B_jan_jul':B['jan_jul'],'C_jan_jul':C['jan_jul'],
 'delta':delta,
 'top_features':sorted(out['feature_importance'].items(),key=lambda kv:-kv[1])[:20],
 'variant_best_april':variant_best
},indent=2))
