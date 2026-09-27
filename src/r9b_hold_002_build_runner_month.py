import sys,argparse,time,json,hashlib
from pathlib import Path
import numpy as np
from numba import njit
R=Path('/mnt/data/r9b_active');sys.path.insert(0,str(R));import gamma014_replay as g
H=.10;CP=1000;TRAIL2=.15;MAXH=120000
C={1:R/'R9B_GAMMA_DYNAMIC_GL_001_JAN_CACHE.npz',2:R/'R9B_GAMMA_DYNAMIC_GL_001_FEB_CACHE.npz',3:R/'R9B_GAMMA_DYNAMIC_GL_001_MAR_CACHE.npz'}
S={m:R/f'R9B_GAMMA_DYNAMIC_HOLD_001_{m:02d}_SNAPSHOTS.npz' for m in (1,2,3)}
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
@njit(cache=True)
def runner(t,mid,ev,side,align):
 n=len(ev);O=np.empty((n,7),np.float64)
 for q in range(n):
  sig=int(ev[q]);s=int(side[q]);a=int(align[q])
  if s==0:
   for j in range(7):O[q,j]=np.nan
   O[q,6]=0.;continue
  i=np.searchsorted(t,sig)
  if a>=3:stopd=1.;act=.10;trail=.04
  else:stopd=3.0;act=.18;trail=.05
  entry=mid[i]+H if s==1 else mid[i]-H;stop=(mid[i]-H-stopd) if s==1 else (mid[i]+H+stopd);mfe=-1e18;mae=1e18;ei=i;closed=0;prom=0
  for k in range(i,len(t)):
   px=mid[k]-H if s==1 else mid[k]+H;pnl=(px-entry) if s==1 else (entry-px);age=int(t[k]-sig)
   if pnl>mfe:mfe=pnl
   if pnl<mae:mae=pnl
   hit=(px<=stop) if s==1 else (px>=stop);mh=60000 if prom==0 else MAXH
   if hit or age>=mh:ei=k;closed=1;break
   trd=trail if prom==0 else TRAIL2
   if pnl>=act:
    cand=px-trd if s==1 else px+trd
    if (s==1 and cand>stop) or (s==-1 and cand<stop):stop=cand
   if prom==0 and age>=CP:prom=1
  pnl=(mid[ei]-H-entry) if s==1 else (entry-(mid[ei]+H))
  O[q,0]=pnl;O[q,1]=(t[ei]-sig)/1000.;O[q,2]=mfe;O[q,3]=mae;O[q,4]=t[ei];O[q,5]=a;O[q,6]=1. if closed else 0.
 return O
def main(m):
 t0=time.time();z=np.load(C[m],allow_pickle=False);snp=np.load(S[m],allow_pickle=False);a=snp['actions'].astype(np.int8);fade=z['X'][:,1].astype(np.int8);side=np.where(a==1,fade,np.where(a==2,-fade,0)).astype(np.int8);sel=np.where((a==1)[:,None],z['Of'],z['Oc']);align=sel[:,5].astype(np.int8);t,mid=g.load_ticks(m);O=runner(t,mid,z['X'][:,0].astype(np.int64),side,align);out=R/f'R9B_GAMMA_DYNAMIC_HOLD_002_{m:02d}_RUNNER.npz';np.savez_compressed(out,O=O,profile=np.array([CP,TRAIL2,MAXH],float));man={'unit':'R9B_GAMMA_DYNAMIC_HOLD_002_RENEWAL_PERSISTENCE_OWNER','month':m,'status':'COMPLETED_LOCAL_MONTH_CHECKPOINT','profile':{'cp_ms':CP,'trail':TRAIL2,'maxhold_ms':MAXH},'output_sha256':sha(out),'source_sha256':sha(__file__),'rows':len(O),'elapsed_s':time.time()-t0,'august_accessed':False};mp=R/f'R9B_GAMMA_DYNAMIC_HOLD_002_{m:02d}_RUNNER_MANIFEST.json';mp.write_text(json.dumps(man,indent=2)+'\n');print(json.dumps(man))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('month',type=int);x=ap.parse_args();assert x.month in (1,2,3);main(x.month)
