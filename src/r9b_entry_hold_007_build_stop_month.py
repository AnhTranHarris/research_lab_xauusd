import sys,argparse,time,json,hashlib
from pathlib import Path
import numpy as np
from numba import njit
R=Path('/mnt/data/r9b_active');sys.path.insert(0,str(R));import gamma014_replay as g
H=.10;MAXH=60000
CAPS=np.array([.25,.35,.50,.75,1.00,1.50],np.float64)
C={1:R/'R9B_GAMMA_DYNAMIC_GL_001_JAN_CACHE.npz',2:R/'R9B_GAMMA_DYNAMIC_GL_001_FEB_CACHE.npz',3:R/'R9B_GAMMA_DYNAMIC_GL_001_MAR_CACHE.npz'}
E={m:R/f'R9B_GAMMA_DYNAMIC_ENTRY_HOLD_001_{m:02d}_FEATURES.npz' for m in (1,2,3)}
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
@njit(cache=True)
def replay_caps(t,mid,ev,side,align,caps):
 n=len(ev); qn=len(caps); O=np.empty((n,qn,7),np.float64)
 for q in range(n):
  sig=int(ev[q]); s=int(side[q]); a=int(align[q])
  if s==0:
   for c in range(qn):
    for j in range(7): O[q,c,j]=np.nan
    O[q,c,6]=0.
   continue
  i=np.searchsorted(t,sig)
  if i>=len(t):
   for c in range(qn):
    for j in range(7): O[q,c,j]=np.nan
    O[q,c,6]=0.
   continue
  if a>=3: default_stop=1.0; act=.10; trail=.04
  else: default_stop=3.0; act=.18; trail=.05
  for ci in range(qn):
   stopd=caps[ci]
   if stopd>default_stop: stopd=default_stop
   entry=mid[i]+H if s==1 else mid[i]-H
   stop=(mid[i]-H-stopd) if s==1 else (mid[i]+H+stopd)
   mfe=-1e18; mae=1e18; ei=i; closed=0
   for k in range(i,len(t)):
    px=mid[k]-H if s==1 else mid[k]+H
    pnl=(px-entry) if s==1 else (entry-px)
    age=int(t[k]-sig)
    if pnl>mfe:mfe=pnl
    if pnl<mae:mae=pnl
    hit=(px<=stop) if s==1 else (px>=stop)
    if hit or age>=MAXH:
     ei=k; closed=1; break
    if pnl>=act:
     cand=px-trail if s==1 else px+trail
     if (s==1 and cand>stop) or (s==-1 and cand<stop):stop=cand
   pnl=(mid[ei]-H-entry) if s==1 else (entry-(mid[ei]+H))
   O[q,ci,0]=pnl;O[q,ci,1]=(t[ei]-sig)/1000.;O[q,ci,2]=mfe;O[q,ci,3]=mae;O[q,ci,4]=t[ei];O[q,ci,5]=a;O[q,ci,6]=1. if closed else 0.
 return O
def baseF(F):
 rg=(F[:,14]//10).astype(int);return np.column_stack([F[:,:14],F[:,14]-10*rg])
def frozen(A,m):
 tr=m['model'];cl=np.array(tr['children_left']);cr=np.array(tr['children_right']);ft=np.array(tr['feature']);th=np.array(tr['threshold']);vv=np.array(tr['value'])[:,0,:];cs=np.array(tr['classes'],np.int8);q=float(tr['confidence_threshold']);out=np.zeros(len(A),np.int8);cf=np.zeros(len(A));ok=np.all(np.isfinite(A),1)
 for i in np.where(ok)[0]:
  n=0
  while cl[n]!=-1:n=cl[n] if A[i,ft[n]]<=th[n] else cr[n]
  v=vv[n];p=v/v.sum();j=int(np.argmax(p));cf[i]=p[j];out[i]=cs[j] if p[j]>=q else 0
 return out,cf
def main(m):
 import json as _json
 t0=time.time(); z=np.load(C[m],allow_pickle=False); bm=_json.load(open(R/'R9B_GAMMA_DYNAMIC_GL_001_JAN_OWNERSHIP_MODEL.json')); B=baseF(z['F']); a,bc=frozen(B,bm)
 fade=z['X'][:,1].astype(np.int8); side=np.where(a==1,fade,np.where(a==2,-fade,0)).astype(np.int8); sel=np.where((a==1)[:,None],z['Of'],z['Oc']); align=sel[:,5].astype(np.int8)
 t,mid=g.load_ticks(m); O=replay_caps(t,mid,z['X'][:,0].astype(np.int64),side,align,CAPS)
 out=R/f'R9B_GAMMA_DYNAMIC_ENTRY_HOLD_007_{m:02d}_STOP_CAPS.npz'; np.savez_compressed(out,O=O,caps=CAPS,actions=a,base_conf=bc)
 man={'unit':'R9B_GAMMA_DYNAMIC_ENTRY_HOLD_007_TOXIC_RISK_GEOMETRY','month':m,'status':'COMPLETED_LOCAL_MONTH_CHECKPOINT','caps':CAPS.tolist(),'output_sha256':sha(out),'source_sha256':sha(__file__),'rows':len(O),'elapsed_s':time.time()-t0,'august_accessed':False}; mp=R/f'R9B_GAMMA_DYNAMIC_ENTRY_HOLD_007_{m:02d}_STOP_CAPS_MANIFEST.json';mp.write_text(json.dumps(man,indent=2)+'\n');print(json.dumps(man))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('month',type=int);x=ap.parse_args();assert x.month in (1,2,3);main(x.month)
