"""R9B Gamma NET024: completed-H1 NET022 ownership permission screen on CAUSAL014.

Research-only causal candidate replay. Independent parent raw events remain active;
apply a side-veto at an eligible raw event, then re-run strict single-position
chronology. Never filter only the already executed parent ledger for promotion.
Only timestamped, fully completed H1 bars can affect an entry. No August data.

Research walls: Jan-Mar discovery; April calibration; May-Jul frozen forward.
"""
from __future__ import annotations
import os, sys, json, time, hashlib, argparse
from pathlib import Path
import numpy as np

BASE=Path('/mnt/data')
SOURCE=BASE/'net023_src'
sys.path.insert(0, str(SOURCE))
import r9b_screen as R
import r9b_r8_recert as B
import r8_sweep_lifecycle_screen as S
from r9b_sweep_structure_exit_candidate import replay_hybrid,nonoverlap,met

OUT=BASE/'net024_results'
OUT.mkdir(parents=True,exist_ok=True)
H1_MS=3_600_000
PARENT_EXPECT={
 1:(34362,28088,19087,-4510.0870000207515),
 2:(32862,28188,18834,-4450.956500020821),
 3:(41595,35573,24169,-6589.631500026144),
 4:(33302,26683,18068,-4735.74550001993),
 5:(32556,25525,17412,-4425.295500019026),
 6:(35381,27710,18828,-5345.316000013228),
 7:(34734,25807,16744,-5342.881000002722)
}


def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for c in iter(lambda: f.read(1<<20),b''): h.update(c)
 return h.hexdigest()


def completed_h1_signals(t,mid):
 """NET022 parity-certified H1 *trigger only*; not a future-exit-dependent sleeve.

 Uses completed signal H1 close and prior 13 completed bars. Only output signal
 close_ms and side, together with causal signal features. No need to know
 whether a quote exists eight hours later. Duplicate signals permitted.
 """
 bucket=np.asarray(t,dtype=np.int64)//H1_MS
 st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
 en=np.r_[st[1:]-1,len(t)-1]
 k=bucket[st];o=mid[st];h=np.maximum.reduceat(mid,st)
 l=np.minimum.reduceat(mid,st);c=mid[en]
 rng=h-l;body=np.abs(c-o)
 prevc=np.r_[o[0],c[:-1]]
 tr=np.maximum(h-l,np.maximum(np.abs(h-prevc),np.abs(l-prevc)))
 rows=[]
 for i in range(14,len(k)):
  # This matches NET022's original trailing 14 true-range SMA, including current completed signal bar.
  atr=float(np.mean(tr[max(0,i-13):i+1]))
  top=np.maximum(o[i-13:i],c[i-13:i]);bot=np.minimum(o[i-13:i],c[i-13:i])
  up=float(np.max(top));dn=float(np.min(bot))
  side=1 if (c[i]>up+.1*atr and c[i]>o[i]) else (-1 if (c[i]<dn-.1*atr and c[i]<o[i]) else 0)
  if side==0:continue
  ref=float(np.median(rng[i-13:i]));
  if ref<=0:continue
  compression=float(np.mean(rng[i-2:i])/ref)
  expansion=float(rng[i]/ref)
  bf=float(body[i]/rng[i]) if rng[i]>0 else 0.0
  if compression<=1.0 and expansion>=1.0 and bf>=.25:
   close_ms=int((k[i]+1)*H1_MS)
   rows.append((close_ms,side,compression,expansion,bf))
 dtype=[('close_ms','i8'),('side','i1'),('compression_ratio','f8'),('expansion_ratio','f8'),('body_fraction','f8')]
 return np.array(rows,dtype=dtype)


def parent_raw(month):
 s=time.perf_counter()
 t,mid=R.load_ticks(month)
 sec_ids,_,_,_,_,_,_,_=R.active_seconds(t,mid)
 e5,r5,a5=R.aggregate_tf_from_ticks(t,mid,300)
 atr=R.map_completed(sec_ids,e5,a5)
 al=np.zeros(len(sec_ids),np.int8);ash=np.zeros(len(sec_ids),np.int8)
 for tf in (60,180,300,600,1200):
  ee,ret,aa=R.aggregate_tf_from_ticks(t,mid,tf)
  rr=R.map_completed(sec_ids,ee,ret);a=R.map_completed(sec_ids,ee,aa)
  ok=np.isfinite(a)
  al+=((rr>0)&ok).astype(np.int8)
  ash+=((rr<0)&ok).astype(np.int8)
 su,hi,lo,cl=B.build_sec(t,mid)
 X=S.sweep_signals(t,mid,su,hi,lo,cl,sec_ids,atr,al,ash)
 O=replay_hybrid(t,mid,X)
 ii=nonoverlap(X,O)
 baseline=met(O[ii,0],O[ii,1])
 expected=PARENT_EXPECT[month]
 assert (len(X),len(ii),int(np.count_nonzero(O[ii,0]>0)))==expected[:3], (month,len(X),len(ii),baseline)
 assert abs(baseline['net']-expected[3])<1e-8, (month,baseline['net'],expected[3])
 h1=completed_h1_signals(t,mid)
 return X,O,h1,baseline,time.perf_counter()-s


def cache_month(month:int):
 assert month in range(1,8), 'AUGUST SEALED'
 X,O,h1,baseline,elapsed=parent_raw(month)
 p=OUT/f'NET024_RAW_{month:02d}.npz'
 np.savez_compressed(p,raw_entry_ms=X[:,0].astype(np.int64),
  raw_side=X[:,1].astype(np.int8),raw_align=X[:,3].astype(np.int8),
  raw_pnl=O[:,0].astype(np.float64),raw_exit_ms=O[:,4].astype(np.int64),
  raw_hold_s=O[:,1].astype(np.float64),
  h1_close_ms=h1['close_ms'].astype(np.int64),h1_side=h1['side'].astype(np.int8),
  h1_compression_ratio=h1['compression_ratio'].astype(np.float64),
  h1_expansion_ratio=h1['expansion_ratio'].astype(np.float64),
  h1_body_fraction=h1['body_fraction'].astype(np.float64))
 manifest={'unit':'R9B_GAMMA_DYNAMIC_NET_024_H1_OWNERSHIP_SEQUENTIAL_PERMISSION',
  'stage':'RAW_MONTH_CAUSAL_PARENT_AND_COMPLETED_H1',
  'month':month,'parent':'CAUSAL_RECERT_014','status':'VERIFIED_LOCAL',
  'parent_metrics':baseline,'raw_candidates':len(X),'completed_h1_signals':len(h1),
  'raw_cache':p.name,'raw_cache_sha256':sha(p),
  'raw_data_sha256':sha(R.RAW_BY_MONTH[month]),
  'source_sha256':sha(__file__),'elapsed_s':elapsed,
  'h1_lookahead_prevention':'bar close only; no future 8-hour exit check; cold month start',
  'candidate_semantics':'independent CAUSAL014 raw outcomes; permission/veto is checked at every raw event before one-position replay',
  'august_accessed':False,
  'next_stage':('NET024_DISCOVERY_JAN_MAR' if month==3 else f'NET024_RAW_{month+1:02d}')}
 mf=OUT/f'NET024_RAW_{month:02d}.manifest.json'
 mf.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'month':month,'status':'VERIFIED_LOCAL','parent':baseline,
 'h1_signals':len(h1),'raw_candidates':len(X),'cache_sha256':manifest['raw_cache_sha256'],
 'next':manifest['next_stage'],'august_accessed':False}))


def mtr(pnl):
 p=np.asarray(pnl,dtype=float);gp=float(p[p>0].sum());gl=float(p[p<0].sum())
 eq=np.cumsum(p);peak=np.maximum.accumulate(np.r_[0,eq])[:-1] if len(p) else np.empty(0)
 dd=float((peak-eq).max()) if len(eq) else 0.
 return {'trades':len(p),'winners':int((p>0).sum()),'net':float(p.sum()),'gross_profit':gp,'gross_loss':gl,
  'pf':gp/(-gl) if gl<0 else None,'maxdd':dd,'win_rate':float((p>0).mean()) if len(p) else 0.}


def raw_replay(e,x,p,eligible):
 """Full raw chronological replay. Block entry at the exact previous exit."""
 ix=np.flatnonzero(eligible & (x>=0) & np.isfinite(p))
 ix=ix[np.argsort(e[ix],kind='stable')]
 free=-1; chosen=[]
 for q in ix:
  if int(e[q])<=free:continue
  chosen.append(int(q));free=int(x[q])
 return np.array(chosen,dtype=np.int64)


def owner_map(entries,h1_start,h1_side,hours):
 j=np.searchsorted(h1_start,entries,side='right')-1
 side=np.zeros(len(entries),dtype=np.int8)
 ok=j>=0
 owner_idx=j[ok]
 active=(entries[ok]-h1_start[owner_idx])<int(hours*H1_MS)
 side[ok]=np.where(active,h1_side[owner_idx],0)
 return side


def analyze(month:int,hours=(1,2,4,8),modes=('veto_contra','active_match_only','neutral_only','veto_contra_weak_align','veto_contra_strong_align')):
 p=OUT/f'NET024_RAW_{month:02d}.npz'
 z=np.load(p,allow_pickle=False)
 e=z['raw_entry_ms'];ex=z['raw_exit_ms'];side=z['raw_side'];pnl=z['raw_pnl'];align=z['raw_align']
 h1t=z['h1_close_ms'];h1s=z['h1_side']
 all_ok=np.ones(len(e),dtype=bool)
 base_ix=raw_replay(e,ex,pnl,all_ok);base=mtr(pnl[base_ix]);
 t=PARENT_EXPECT[month]
 assert (base['trades'],base['winners'])==t[1:3] and abs(base['net']-t[3])<1e-8,base
 result={'unit':'R9B_GAMMA_DYNAMIC_NET_024_H1_OWNERSHIP_SEQUENTIAL_PERMISSION',
   'month':month,'status':'VERIFIED_LOCAL_SCREEN','parent':base,
   'rules':[],'august_accessed':False}
 for hh in hours:
  owners=owner_map(e,h1t,h1s,hh)
  conflict=(owners!=0)&(side==-owners)
  matching=(owners!=0)&(side==owners)
  neutral=owners==0
  for mode in modes:
   if mode=='veto_contra': elig=~conflict
   elif mode=='active_match_only':elig=matching
   elif mode=='neutral_only':elig=neutral
   elif mode=='veto_contra_weak_align':elig=~(conflict&(align<3))
   elif mode=='veto_contra_strong_align':elig=~(conflict&(align>=3))
   else:raise ValueError(mode)
   ix=raw_replay(e,ex,pnl,elig);m=mtr(pnl[ix]);
   b=base
   result['rules'].append({'rule':mode,'owner_hours':hh,'metrics':m,
     'delta_vs_parent':{'net':m['net']-b['net'],'gross_loss_improvement':m['gross_loss']-b['gross_loss'],
      'winners':m['winners']-b['winners'],'trades':m['trades']-b['trades']},
     'retention':{'trades_pct':m['trades']/b['trades']*100,'winners_pct':m['winners']/b['winners']*100}})
 out=OUT/f'NET024_SCREEN_{month:02d}.json'
 out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'month':month,'parent':base,'top_by_net':sorted(result['rules'],key=lambda a:a['delta_vs_parent']['net'],reverse=True)[:5],
  'out':str(out),'sha256':sha(out)},default=str))


def unit_tests():
 # H1 signal is not active before its close, and the most recent opposite completed signal replaces the prior owner.
 T=np.array([3600000,7200000],np.int64);S=np.array([1,-1],np.int8)
 Q=np.array([3599999,3600000,7199999,7200000,7200001,10799999],np.int64)
 expected=np.array([0,1,1,-1,-1,-1],np.int8)
 assert np.array_equal(owner_map(Q,T,S,1),expected)
 assert np.array_equal(owner_map(Q,T,S,0.5),np.array([0,1,0,-1,-1,0],dtype=np.int8))
 E=np.array([100,120,130,140,200]);EX=np.array([150,155,160,210,230]);P=np.array([1.,2.,3.,4.,5.]);A=np.array([1,1,0,1,1],dtype=bool)
 assert raw_replay(E,EX,P,A).tolist()==[0,4]
 assert raw_replay(E,EX,P,np.ones(5,bool)).tolist()==[0,4]
 assert raw_replay(np.array([100,150,151]),np.array([150,170,180]),np.array([1.,2.,3.]),np.ones(3,bool)).tolist()==[0,2] # strict <= free
 print('NET024_UNIT_TESTS_PASS')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['cache','screen','test']);parser.add_argument('month',nargs='?',type=int)
 a=parser.parse_args()
 if a.command=='cache': cache_month(a.month)
 elif a.command=='screen':analyze(a.month)
 else:unit_tests()