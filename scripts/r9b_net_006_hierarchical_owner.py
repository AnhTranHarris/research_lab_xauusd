import json,hashlib
from pathlib import Path
import numpy as np
import r9b_net_002_h1_h4_bos as b
R=Path('/mnt/data/r9b_active');OUT=R/'R9B_GAMMA_DYNAMIC_NET_006_HIERARCHICAL_OWNER.json';MAN=R/'R9B_GAMMA_DYNAMIC_NET_006_MANIFEST.json'
N4=(5,8,13,21); BUF4=(0.,.05,.10); AGE=(1,2,4,8,16,999); MODE=('OWNER','NET3','OWNER_AND_NET3'); BODY=(0,1)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for z in iter(lambda:f.read(1<<20),b''):h.update(z)
 return h.hexdigest()
def metric(x): return b.metric(np.asarray(x,float))
def h1_events(d):
 o=d['o_60'];h=d['h_60'];l=d['l_60'];c=d['c_60'];atr=d['atr_60'];end=d['end_60'];lp=d['long_60'][:,5];sp=d['short_60'][:,5];ev=[]
 for i in range(14,len(c)):
  if not np.isfinite(atr[i]) or atr[i]<=0:continue
  top=np.maximum(o[i-13:i],c[i-13:i]);bot=np.minimum(o[i-13:i],c[i-13:i]);up=np.max(top);dn=np.min(bot);side=1 if c[i]>up+.1*atr[i] and c[i]>o[i] else (-1 if c[i]<dn-.1*atr[i] and c[i]<o[i] else 0)
  if side:
   p=lp[i] if side>0 else sp[i]
   if np.isfinite(p):ev.append((int(end[i]),side,float(p)))
 return ev
def h4_state(d,n,buf):
 o=d['o_240'];h=d['h_240'];l=d['l_240'];c=d['c_240'];atr=d['atr_240'];end=d['end_240'];owner=np.zeros(len(c),np.int8);age=np.full(len(c),999,np.int16);cur=0;a=999
 for i in range(len(c)):
  if i>=max(n,14) and np.isfinite(atr[i]) and atr[i]>0:
   top=np.maximum(o[i-n:i],c[i-n:i]);bot=np.minimum(o[i-n:i],c[i-n:i]);up=np.max(top);dn=np.min(bot)
   bos=1 if c[i]>up+buf*atr[i] and c[i]>o[i] else (-1 if c[i]<dn-buf*atr[i] and c[i]<o[i] else 0)
   if bos and bos!=cur:cur=bos;a=0
   elif bos and bos==cur:a=0
   elif cur:a=min(999,a+1)
  owner[i]=cur;age[i]=a
 net3=np.zeros(len(c),np.int8);body=np.sign(c-o).astype(np.int8)
 for i in range(3,len(c)):
  v=c[i]-c[i-3];net3[i]=1 if v>0 else (-1 if v<0 else 0)
 return end,owner,age,net3,body
def eval_month(d,n,buf,age_max,mode,reqbody):
 end4,own,age,net3,body=h4_state(d,n,buf);ev=h1_events(d);out=[];last=-2**63
 for tm,side,p in ev:
  if tm<last:continue
  j=np.searchsorted(end4,tm,side='right')-1
  if j<0:continue
  good_owner=own[j]==side and age[j]<=age_max;good_net=net3[j]==side
  good=good_owner if mode=='OWNER' else (good_net if mode=='NET3' else (good_owner and good_net))
  if reqbody:good=good and body[j]==side
  if good:out.append(p);last=tm+8*60*60000
 return np.asarray(out,float)
def main():
 D={m:b.load(m) for m in (1,2,3,4)};rows=[]
 for n in N4:
  for buf in BUF4:
   for a in AGE:
    for mode in MODE:
     for rb in BODY:
      rep={};ok=True
      for m in (1,2,3):
       met=metric(eval_month(D[m],n,buf,a,mode,rb));rep[str(m)]=met
       if met['trades']<5 or met['net']<=0 or met['pf'] is None or met['pf']<=1:ok=False
      rows.append({'h4_lookback':n,'h4_atr_buffer':buf,'h4_owner_max_age_bars':a,'mode':mode,'require_h4_body_align':bool(rb),'replication':rep,'eligible':ok,'min_net':min(rep[str(m)]['net'] for m in (1,2,3)),'sum_net':sum(rep[str(m)]['net'] for m in (1,2,3)),'min_pf':min(rep[str(m)]['pf'] if rep[str(m)]['pf'] is not None else 999 for m in (1,2,3)),'min_trades':min(rep[str(m)]['trades'] for m in (1,2,3))})
 elig=[r for r in rows if r['eligible']];best=max(elig,key=lambda r:(r['min_net'],r['sum_net'],r['min_pf'],r['min_trades'])) if elig else None;ap=None;gate=False
 if best:
  ap=metric(eval_month(D[4],best['h4_lookback'],best['h4_atr_buffer'],best['h4_owner_max_age_bars'],best['mode'],int(best['require_h4_body_align'])));gate=ap['trades']>=5 and ap['net']>0 and ap['pf'] is not None and ap['pf']>1
 out={'unit':'R9B_GAMMA_DYNAMIC_NET_006_HIERARCHICAL_OWNER','phase':'JAN_MAR_DISCOVERY_THEN_APRIL_CALIBRATION','status':'COMPLETED_LOCAL_SCREEN','parent':'NET002 fixed H1 body-BOS immediate entry and fixed 8h hold. Only H4 causal completed-bar ownership context may gate participation.','mechanism':'Persistent H4 body-close BOS owner, H4 3-bar net direction and optional current H4 body alignment. H4 state uses completed bars only and carries forward until opposite BOS.','eligible_candidates':len(elig),'frozen_candidate':best,'april':ap,'april_gate_pass':gate,'decision':'FREEZE_FOR_MAY_JUL_FORWARD' if gate else 'REJECT_HIERARCHICAL_OWNER_GATE','next_unit':'R9B_GAMMA_DYNAMIC_NET_006_MAY_JUL_FROZEN_FORWARD' if gate else 'R9B_GAMMA_DYNAMIC_NET_007_STRUCTURAL_FAILURE_SPECIALIST','top':sorted(rows,key=lambda r:(r['eligible'],r['min_net'],r['sum_net'],r['min_pf']),reverse=True)[:30],'may_july_accessed':False,'august_accessed':False};OUT.write_text(json.dumps(out,indent=2)+'\n');MAN.write_text(json.dumps({'unit':out['unit'],'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),'input_cache_sha256':{str(m):sha(R/f'R9B_GAMMA_DYNAMIC_NET_002_{m:02d}_HTF_CACHE.npz') for m in (1,2,3,4)},'august_accessed':False},indent=2)+'\n');print(json.dumps({'eligible':len(elig),'best':best,'april':ap,'gate':gate,'decision':out['decision'],'result_sha256':sha(OUT)},indent=2))
if __name__=='__main__':main()
