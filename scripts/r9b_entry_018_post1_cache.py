import json, hashlib, argparse, time, sys
from pathlib import Path
import numpy as np
from numba import njit
from sklearn.tree import DecisionTreeClassifier
R=Path('/mnt/data/r9b_active'); sys.path.insert(0,str(R)); import gamma014_replay as g
H=.10
P={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_017_{m:02d}_BRIDGE.npz' for m in (1,2,3)}
ENTRY_DEPTH=4; ENTRY_LEAF=50; ENTRY_W0=.25; ENTRY_THR=.25

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def entry_A(d):
 prior=np.column_stack([np.clip(d['prior_pnl'],-3,3),d['prior_hold'],d['close_gap_s'],d['base_conf']])
 return np.column_stack([d['bridge'],prior])

def raw_h(d,h):
 c={1:4,2:5,3:6,5:7}[h]; return d['horizon'][:,c]+.20

def entry_target(d):
 r=raw_h(d,1); y=np.zeros(len(r),np.int8); y[r>.20]=1; y[r<-.20]=2; return y

def apply_entry(clf,A):
 ok=np.all(np.isfinite(A),1); out=np.zeros(len(A),np.int8)
 pr=clf.predict_proba(A[ok]); j=pr.argmax(1); mx=pr.max(1); lab=clf.classes_[j].astype(np.int8); lab[mx<ENTRY_THR]=0; out[ok]=lab
 return out

def fit_entry():
 z=np.load(P[1],allow_pickle=False); d={k:z[k] for k in z.files}; z.close(); A=entry_A(d); y=entry_target(d); tr=(d['day_idx']<14)&np.all(np.isfinite(A),1)
 return DecisionTreeClassifier(max_depth=ENTRY_DEPTH,min_samples_leaf=ENTRY_LEAF,class_weight={0:ENTRY_W0,1:1,2:1},random_state=117).fit(A[tr],y[tr])

@njit(cache=True)
def post1_features(t,mid,sig,fade_side,action):
 n=len(sig); F=np.full((n,24),np.nan); horizons=np.array([250,500,750,1000],np.int64)
 for q in range(n):
  if action[q]==0: continue
  s=int(sig[q]); fs=int(fade_side[q]); rel=1 if action[q]==1 else -1; side=fs*rel
  i0=np.searchsorted(t,s,side='left'); i1=np.searchsorted(t,s+1000,side='right')
  if i1<=i0: continue
  m0=mid[i0]; prev=0.; travel=0.; mx=-1e18; mn=1e18; favren=0; advren=0; lastfav=s; lastadv=s; turns=0; prevstep=0; above0=0; abovebe=0; recross0=0; recrossbe=0; prevsg0=0; prevsgbe=0; first_be=-1
  for k in range(i0,i1):
   d=side*(mid[k]-m0)
   if d>mx+1e-12: mx=d; favren+=1; lastfav=int(t[k])
   if d<mn-1e-12: mn=d; advren+=1; lastadv=int(t[k])
   if d>0: above0+=1
   if d>.20:
    abovebe+=1
    if first_be<0:first_be=int(t[k])
   if k>i0:
    step=d-prev; travel+=abs(step); sgstep=1 if step>0 else (-1 if step<0 else 0)
    if sgstep!=0:
     if prevstep!=0 and sgstep!=prevstep:turns+=1
     prevstep=sgstep
   sg0=1 if d>0 else (-1 if d<0 else 0)
   if sg0!=0:
    if prevsg0!=0 and sg0!=prevsg0: recross0+=1
    prevsg0=sg0
   xbe=d-.20; sgbe=1 if xbe>0 else (-1 if xbe<0 else 0)
   if sgbe!=0:
    if prevsgbe!=0 and sgbe!=prevsgbe: recrossbe+=1
    prevsgbe=sgbe
   prev=d
  vals=np.empty(4,np.float64)
  for h in range(4):
   j=np.searchsorted(t,s+horizons[h],side='right')-1
   if j<i0:j=i0
   vals[h]=side*(mid[j]-m0)
  final=vals[3]; eff=final/(travel+1e-9); cnt=i1-i0
  F[q,0]=vals[0];F[q,1]=vals[1];F[q,2]=vals[2];F[q,3]=vals[3];F[q,4]=mx;F[q,5]=mn;F[q,6]=travel;F[q,7]=eff;F[q,8]=above0/cnt;F[q,9]=abovebe/cnt;F[q,10]=turns;F[q,11]=favren;F[q,12]=advren;F[q,13]=(s+1000-lastfav)/1000.;F[q,14]=(s+1000-lastadv)/1000.;F[q,15]=float(cnt);F[q,16]=cnt;F[q,17]=((s+1000-first_be)/1000.) if first_be>=0 else -1.;F[q,18]=recross0;F[q,19]=recrossbe;F[q,20]=mx-final;F[q,21]=final-mn;F[q,22]=(vals[3]-vals[1])-vals[1];F[q,23]=vals[3]-.20
 return F

def main(m):
 t0=time.time(); clf=fit_entry(); z=np.load(P[m],allow_pickle=False); d={k:z[k] for k in z.files}; z.close(); A=entry_A(d); a=apply_entry(clf,A)
 t,mid=g.load_ticks(m); F=post1_features(t,mid,d['X'][:,0].astype(np.int64),d['X'][:,1].astype(np.int8),a)
 out=R/f'R9B_GAMMA_DYNAMIC_ENTRY_018_{m:02d}_POST1.npz'; np.savez_compressed(out,post1=F,entry_action=a,day_idx=d['day_idx'],horizon=d['horizon'],bridge=d['bridge'],prior_pnl=d['prior_pnl'],prior_hold=d['prior_hold'],close_gap_s=d['close_gap_s'],base_conf=d['base_conf'])
 man={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_018_BRIDGE_PERSISTENCE_OWNER','month':m,'status':'COMPLETED_LOCAL_MONTH_CACHE','rows':int(len(a)),'selected_entries':int((a!=0).sum()),'source_sha256':sha(__file__),'output_sha256':sha(out),'entry017_contract':{'depth':ENTRY_DEPTH,'leaf':ENTRY_LEAF,'w0':ENTRY_W0,'thr':ENTRY_THR},'august_accessed':False,'elapsed_s':time.time()-t0}
 (R/f'R9B_GAMMA_DYNAMIC_ENTRY_018_{m:02d}_POST1_MANIFEST.json').write_text(json.dumps(man,indent=2)+'\n'); print(json.dumps(man))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('month',type=int);x=ap.parse_args();assert x.month in (1,2,3);main(x.month)
