import json,time,hashlib
from pathlib import Path
import numpy as np
from numba import njit
R=Path('/mnt/data/r9b_active')
C={1:R/'R9B_GAMMA_DYNAMIC_GL_001_JAN_CACHE.npz',2:R/'R9B_GAMMA_DYNAMIC_GL_001_FEB_CACHE.npz',3:R/'R9B_GAMMA_DYNAMIC_GL_001_MAR_CACHE.npz'}
S={m:R/f'R9B_GAMMA_DYNAMIC_HOLD_001_{m:02d}_SNAPSHOTS.npz' for m in (1,2,3)}
U={m:R/f'R9B_GAMMA_DYNAMIC_HOLD_002_{m:02d}_RUNNER.npz' for m in (1,2,3)}
OUT=R/'R9B_GAMMA_DYNAMIC_HOLD_002_RENEWAL_PERSISTENCE_OWNER.json';MAN=R/'R9B_GAMMA_DYNAMIC_HOLD_002_MANIFEST.json'
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
@njit(cache=True)
def ledger(X,Of,Oc,a,mask,prom,Ru):
 n=len(X);p=np.empty(n,np.float64);nn=0;prev=-9223372036854775807
 for i in range(n):
  if not mask[i] or a[i]==0:continue
  B=Of if a[i]==1 else Oc
  if B[i,6]<.5:continue
  sig=int(X[i,0])
  if sig<=prev:continue
  if prom[i]:
   if Ru[i,6]<.5:continue
   p[nn]=Ru[i,0];prev=int(Ru[i,4])
  else:
   p[nn]=B[i,0];prev=int(B[i,4])
  nn+=1
 return p[:nn]
def met(p):
 w=p>0;l=p<0;gp=float(p[w].sum());gl=float(p[l].sum());c=np.cumsum(p);dd=float(np.max(np.maximum.accumulate(np.r_[0.,c])[1:]-c)) if len(c) else 0.;return {'trades':len(p),'winners':int(w.sum()),'net':float(p.sum()),'gp':gp,'gl':gl,'dd':dd,'win_rate':float(w.mean()) if len(p) else 0.}
def de(b,c):return {'net_improvement':c['net']-b['net'],'gl_reduction_pct':(abs(b['gl'])-abs(c['gl']))/abs(b['gl'])*100,'winner_retention_pct':c['winners']/b['winners']*100,'trade_retention_pct':c['trades']/b['trades']*100,'dd_reduction_pct':(b['dd']-c['dd'])/b['dd']*100}
def main():
 t0=time.time();D={};base={};masks={}
 for m in (1,2,3):
  z=np.load(C[m]);s=np.load(S[m]);Ru=np.load(U[m])['O'];a=s['actions'].astype(np.int8);sel=np.where((a==1)[:,None],z['Of'],z['Oc']);P=s['P'][:,0,:];alive=(s['close_time'][:,0]>0)&(sel[:,4]>s['close_time'][:,0])&(a!=0);D[m]=(z,s,Ru,a,P,alive);masks[m]=(z['day_idx']>=14) if m==1 else np.ones(len(a),bool);base[m]=met(ledger(z['X'],z['Of'],z['Oc'],a,masks[m],np.zeros(len(a),bool),Ru))
 z,s,Ru,a,P,alive=D[1];train=z['day_idx']<14;btrain=met(ledger(z['X'],z['Of'],z['Oc'],a,train,np.zeros(len(a),bool),Ru));rows=[]
 for mfe in (.03,.05,.08,.10,.15,.20):
  for renew in (2,4,6,10,15,20):
   for agefav in (.10,.25,.50,1.0,2.0):
    for gb in (.03,.05,.08,.12,.20):
     prom=alive&train&(P[:,1]>=mfe)&(P[:,7]>=renew)&(P[:,9]<=agefav)&(P[:,3]<=gb)
     if prom.sum()<50:continue
     mm=met(ledger(z['X'],z['Of'],z['Oc'],a,train,prom,Ru));d=de(btrain,mm);rows.append({'mfe_min':mfe,'renew_min':renew,'agefav_max':agefav,'giveback_max':gb,'train_promotions':int(prom.sum()),'train_metrics':mm,'train_vs_base':d})
 elig=[r for r in rows if r['train_vs_base']['net_improvement']>0 and r['train_vs_base']['gl_reduction_pct']>=0 and r['train_vs_base']['winner_retention_pct']>=97 and r['train_vs_base']['trade_retention_pct']>=97]
 top=sorted(elig,key=lambda r:(r['train_vs_base']['gl_reduction_pct'],r['train_vs_base']['net_improvement'],r['train_vs_base']['winner_retention_pct']),reverse=True)[:20]
 for r in top:
  r['replication']={}
  for m in (1,2,3):
   z,s,Ru,a,P,alive=D[m];mask=masks[m];prom=alive&mask&(P[:,1]>=r['mfe_min'])&(P[:,7]>=r['renew_min'])&(P[:,9]<=r['agefav_max'])&(P[:,3]<=r['giveback_max']);mm=met(ledger(z['X'],z['Of'],z['Oc'],a,mask,prom,Ru));r['replication'][str(m)]={'promotions':int(prom.sum()),'metrics':mm,'vs_base':de(base[m],mm)}
  r['replicated_all_positive_net']=all(r['replication'][str(m)]['vs_base']['net_improvement']>0 for m in (1,2,3));r['replicated_all_nonworse_gl']=all(r['replication'][str(m)]['vs_base']['gl_reduction_pct']>=0 for m in (1,2,3));r['min_wr_rep']=min(r['replication'][str(m)]['vs_base']['winner_retention_pct'] for m in (1,2,3));r['min_gl_rep']=min(r['replication'][str(m)]['vs_base']['gl_reduction_pct'] for m in (1,2,3));r['sum_net_rep']=sum(r['replication'][str(m)]['vs_base']['net_improvement'] for m in (1,2,3))
 robust=[r for r in top if r['replicated_all_positive_net'] and r['replicated_all_nonworse_gl'] and r['min_wr_rep']>=95];best=robust[0] if robust else None
 out={'unit':'R9B_GAMMA_DYNAMIC_HOLD_002_RENEWAL_PERSISTENCE_OWNER','status':'COMPLETED_LOCAL_DISCOVERY','parent':'GL001 / Gamma014','runner_profile':{'checkpoint_ms':1000,'post_checkpoint_trail':0.15,'max_hold_ms':120000,'activation_unchanged':True,'stop_never_loosened':True,'selected_from':'January first14 capacity only'},'mechanism':'At 1 second, only if alive, promote to wider-trail/longer-hold runner when MFE has ignited, favorable extremes renew frequently/recently, and giveback remains bounded. Current stop is never loosened. Thresholds selected only on January first14.','training_base':btrain,'screen_count':len(rows),'training_eligible':len(elig),'replicated_top':top,'robust_95_count':len(robust),'best':best,'selection_integrity':'Replication results were not used to select rule thresholds.','august_accessed':False,'elapsed_s':time.time()-t0};OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'runner_month_sha256':{str(m):sha(U[m]) for m in (1,2,3)},'august_accessed':False},indent=2)+'\n');print(json.dumps({'train_candidates':len(rows),'training_eligible':len(elig),'robust95':len(robust),'best':best,'top5':top[:5],'sha':sha(OUT),'elapsed':out['elapsed_s']},indent=2))
if __name__=='__main__':main()
