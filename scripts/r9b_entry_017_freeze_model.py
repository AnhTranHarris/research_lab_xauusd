import json, hashlib
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier
R=Path('/mnt/data/r9b_active')
P=R/'R9B_GAMMA_DYNAMIC_ENTRY_017_01_BRIDGE.npz'
OUT=R/'R9B_GAMMA_DYNAMIC_ENTRY_017_ENTRY_MODEL.json'
DEPTH=4; LEAF=50; W0=.25; THR=.25

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def entry_A(d):
 prior=np.column_stack([np.clip(d['prior_pnl'],-3,3),d['prior_hold'],d['close_gap_s'],d['base_conf']])
 return np.column_stack([d['bridge'],prior])

def raw_h(d,h): return d['horizon'][:,{1:4}[h]]+.20

def target(d):
 r=raw_h(d,1); y=np.zeros(len(r),np.int8); y[r>.20]=1; y[r<-.20]=2; return y

z=np.load(P,allow_pickle=False);d={k:z[k] for k in z.files};z.close();A=entry_A(d);y=target(d);tr=(d['day_idx']<14)&np.all(np.isfinite(A),1)
clf=DecisionTreeClassifier(max_depth=DEPTH,min_samples_leaf=LEAF,class_weight={0:W0,1:1,2:1},random_state=117).fit(A[tr],y[tr])
t=clf.tree_; probs=[]
for v in t.value[:,0,:]:
 s=float(v.sum()); probs.append([float(x/s) if s else 0. for x in v])
out={
 'unit':'R9B_GAMMA_DYNAMIC_ENTRY_017_POST_EXIT_REQUALIFICATION_BRIDGE',
 'role':'Frozen second-wave action owner used by ENTRY018+ descendants',
 'feature_contract':{'bridge_feature_count':22,'prior_features':['prior_pnl_clipped_-3_3','prior_hold','close_gap_s','base_conf'],'total_feature_count':26},
 'target':'At +1s teacher label only: 0 abstain when neither canonical action exceeds +$0.20 raw directional displacement; 1 FADE; 2 CONTINUE.',
 'hyperparameters':{'max_depth':DEPTH,'min_samples_leaf':LEAF,'class_weight':{'0':W0,'1':1.0,'2':1.0},'random_state':117,'decision_confidence_threshold':THR},
 'classes':[int(x) for x in clf.classes_],
 'children_left':[int(x) for x in t.children_left],
 'children_right':[int(x) for x in t.children_right],
 'feature':[int(x) for x in t.feature],
 'threshold':[float(x) for x in t.threshold],
 'n_node_samples':[int(x) for x in t.n_node_samples],
 'class_probability':probs,
 'training':'January days0-13 only, exact bridge cache; future +1s outcomes are labels only.',
 'source_reproducer':'r9b_entry_018_post1_cache.py::fit_entry / this freeze helper',
 'input_bridge_sha256':sha(P),
 'august_accessed':False
}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'output':str(OUT),'sha256':sha(OUT),'nodes':int(t.node_count)}))
