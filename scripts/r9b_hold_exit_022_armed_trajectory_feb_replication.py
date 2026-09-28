"""HOLD_EXIT_022: February ONLY replication of January-frozen AT07/AT11.

Research rules:
  * immutable January preregistration and original discovery result are verified by SHA.
  * independent literal original CAUSAL014 tick replay, exact all-event PnL/exit parity.
  * the same Jan-discovery Numba helper evaluates *unchanged* AT07/AT11;
    no Feb parameter search or use of February to decide a new variant.
  * stops checked before trailing; one-position strict chronological reselection.
  * trade signal, spread and contract-size semantics unchanged. August sealed.
"""
from pathlib import Path
import sys, json, time, hashlib, zipfile
import numpy as np
from numba import njit

ROOT=Path('/mnt/data')
ST=ROOT/'hold022_stage'; OUT=ROOT/'hold022_results'
RAW=ST/'NET024_RAW_02.npz'
MARKET=ROOT/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
CONTRACT=ST/'HOLD022_ARMED_TRAJECTORY_JAN_PREDECLARED.json'
JAN=OUT/'HOLD022_ARMED_TRAJECTORY_JAN_DISCOVERY.json'
JAN_MANIFEST=OUT/'HOLD022_ARMED_TRAJECTORY_JAN_DISCOVERY_MANIFEST.json'
BASE_SHA='c855f777d57c25ecbf49768afa1ab07eab138dd1e07ce30b246e42a788e42586'
MARKET_SHA='ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'
CONTRACT_SHA='d6a2ec4ca4ffccad16cd79fe33a2040f555b2bedce03a9f789bf10eb75a76f41'
JAN_SHA='ba6cb2a9971b3ff65f56d01f9e6efa1f4780d1ba272c26ac373239c7f0901a49'
JAN_SCRIPT_SHA='ca00ad43ea37146a2e8dfffb421ff8bd3be89e5083b935b07a00358c4e99569f'
FROZEN_IDS=('AT07','AT11')

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()

@njit(cache=True)
def independent_parent(t,mid,entry_ms,side_arr,align_arr):
 n=len(entry_ms)
 pnl=np.full(n,np.nan,np.float64);x=np.full(n,-1,np.int64); hold=np.full(n,np.nan,np.float64)
 H=.10
 for k in range(n):
  sig=entry_ms[k];side=side_arr[k];align=align_arr[k]
  if align>=3: stopd=1.0; act=.10; trail=.04
  else: stopd=3.0; act=.18; trail=.05
  i=np.searchsorted(t,sig)
  if i>=len(t): continue
  p=mid[i];entry=p+H if side>0 else p-H
  bid=p-H;ask=p+H
  stop=bid-stopd if side>0 else ask+stopd
  ot=t[i]
  for j in range(i+1,len(t)):
   tt=t[j];p=mid[j];bid=p-H;ask=p+H
   fav=bid-entry if side>0 else entry-ask
   if (side>0 and bid<=stop) or (side<0 and ask>=stop) or tt-ot>=60000:
    pnl[k]=(bid-entry) if side>0 else (entry-ask)
    x[k]=tt;hold[k]=(tt-ot)/1000.;break
   if fav>=act:
    cand=bid-trail if side>0 else ask+trail
    if side>0:
     if cand>stop:stop=cand
    else:
     if cand<stop:stop=cand
 return pnl,x,hold


def unit_test(J):
 t=np.array([100,200,500,1000,60100,60300],dtype=np.int64)
 mid=np.array([10.,9.99,10.30,10.24,10.25,10.25])
 e=np.array([100],dtype=np.int64);side=np.array([1],dtype=np.int8);align=np.array([3],dtype=np.int8)
 p,x,h=independent_parent(t,mid,e,side,align)
 assert np.isfinite(p[0]) and x[0]==1000
 P,X,PRO,*_=J.simulate_all(t,mid,e,side,align)
 assert np.all(P==p[0]) and np.all(X==x[0]) and PRO.sum()==0
 # Hard stop on same quote as timeout prevails in independent CAUSAL parent.
 t2=np.array([100,60100,60300],dtype=np.int64);mid2=np.array([10.,8.5,8.5])
 p,x,h=independent_parent(t2,mid2,e,side,align)
 assert p[0] < -1 and x[0] == 60100
 # Chronological selector excludes signal exactly equal to existing exit.
 ix=J.raw_replay(np.array([100,200,201],np.int64), np.array([200,300,400],np.int64), np.ones(3))
 assert ix.tolist()==[0,2]
 return ['original_stop_order','unqualified_parent_invariant','time_limit_stop_precedence','equal_time_entry_blocked']


def main():
 st=time.perf_counter();OUT.mkdir(exist_ok=True)
 sys.path.insert(0,str(ST));import hold022_armed_trajectory_discovery as J
 manifest=json.loads(JAN_MANIFEST.read_text());Jj=json.loads(JAN.read_text());C=json.loads(CONTRACT.read_text())
 assert sha(JAN)==JAN_SHA and sha(ST/'hold022_armed_trajectory_discovery.py')==JAN_SCRIPT_SHA
 assert sha(CONTRACT)==CONTRACT_SHA and sha(RAW)==BASE_SHA and sha(MARKET)==MARKET_SHA
 assert manifest['contract_sha256']==CONTRACT_SHA and manifest['result_sha256']==JAN_SHA
 assert Jj['strict_eligible_ids']==list(FROZEN_IDS)
 idx=[next(i for i,v in enumerate(C['variants']) if v['id']==name) for name in FROZEN_IDS]
 assert idx==[6,10]
 tests=unit_test(J)
 z=np.load(RAW,allow_pickle=False)
 e=z['raw_entry_ms'].astype(np.int64);side=z['raw_side'].astype(np.int8);align=z['raw_align'].astype(np.int8)
 pp=z['raw_pnl'].astype(np.float64);pex=z['raw_exit_ms'].astype(np.int64);phold=z['raw_hold_s'].astype(np.float64)
 assert len(e)==32862 and np.all(np.diff(e)>=0)
 # Exact operational order is required for numerical source parity.
 a=np.loadtxt(MARKET,delimiter=',',skiprows=1,usecols=(0,1,2),dtype=np.int64)
 t=a[:,0].astype(np.int64)
 ask=a[:,1].astype(np.float64)/1000.;bid=a[:,2].astype(np.float64)/1000.
 mid=(ask+bid)*.5
 del a,ask,bid
 assert np.all(np.diff(t)>=0)
 p0,x0,h0=independent_parent(t,mid,e,side,align)
 assert np.array_equal(p0,pp,equal_nan=True),('original raw pnl disparity',np.flatnonzero(~np.isclose(p0,pp,rtol=0,atol=0,equal_nan=True))[:10])
 assert np.array_equal(x0,pex),('original raw exit disparity',np.flatnonzero(x0!=pex)[:10])
 assert np.array_equal(h0,phold,equal_nan=True),'original holding-time disparity'
 base_ix=J.raw_replay(e,pex,pp);bm=J.metrics(pp[base_ix]); g=json.loads((ST/'NET024_RAW_02.manifest.json').read_text()) if (ST/'NET024_RAW_02.manifest.json').exists() else None
 if g is not None:
  assert abs(bm[2]-g['parent_metrics']['net'])<1e-8
  assert bm[0]==g['parent_metrics']['trades']
 assert bm[0]==28188 and abs(bm[2]-(-4450.956500020821))<1e-8
 P,X,PRO,DS,ARM,ARMT,DMS,DMFE,DFAV,DREN,DAGE,DEFF,DTRANS,REAS,OVERS,SWBEF,SWAFT=J.simulate_all(t,mid,e,side,align)
 jan={r['id']:r for r in Jj['variants']}
 results=[]
 for v in idx:
  name=C['variants'][v]['id'];mask=PRO[v]==0
  assert np.array_equal(P[v,mask],pp[mask],equal_nan=True),'nonpromoted raw PnL mismatch'
  assert np.array_equal(X[v,mask],pex[mask]),'nonpromoted exit mismatch'
  assert np.all(np.isfinite(P[v])) and np.all(X[v]>0)
  for k in np.flatnonzero(PRO[v]):
   if side[k]>0: assert SWAFT[v,k]>=SWBEF[v,k]-1e-10
   else: assert SWAFT[v,k]<=SWBEF[v,k]+1e-10
   assert DMS[v,k]>=ARMT[k]+C['variants'][v]['arm_relative_decision_ms']
   assert DMS[v,k]<pex[k]
  ix=J.raw_replay(e,X[v],P[v]);m=J.metrics(P[v,ix]);delta={'net':m[2]-bm[2],'gp':m[3]-bm[3],'gl_improvement':m[4]-bm[4],'dd_improvement':bm[6]-m[6],'pf':m[5]-bm[5], 'trades':int(m[0]-bm[0]),'winners':int(m[1]-bm[1])}
  strict=(m[2]>bm[2] and m[3]>=bm[3]-1e-10 and m[4]>=bm[4]-1e-10 and m[5]>=bm[5]-1e-12 and m[6]<=bm[6]+1e-10 and m[1]>=.95*bm[1] and m[0]>=.95*bm[0])
  material=(delta['net']>=.05*abs(bm[2]) and delta['gl_improvement']>=.05*abs(bm[4]))
  origwin={int(k) for k in base_ix if pp[k]>0};cand_set=set(int(k) for k in ix); forfeited=sum(1 for k in origwin if k not in cand_set or P[v,k]<=0)
  day=e[ix]//86400000
  daily=[{'utc_day_index':int(d),'trades':int(len(ix[day==d])),'net':float(P[v,ix[day==d]].sum())} for d in np.unique(day)]
  results.append({'id':name,'original_jan_strict':jan[name]['strict_eligible'],'frozen_profile':C['variants'][v]['profile'],'frozen_delay_ms':C['variants'][v]['arm_relative_decision_ms'],'frozen_width':C['variants'][v]['runner_trail_price'],'raw_decision_count':int(DS[v].sum()),'raw_promoted':int(PRO[v].sum()),'selected_promoted':int(PRO[v,ix].sum()),'results':{'trades':int(m[0]),'winners':int(m[1]),'net':m[2],'gp':m[3],'gl':m[4],'pf':m[5],'maxdd':m[6]},'delta':delta,'retention':{'trades_pct':100*m[0]/bm[0],'winners_pct':100*m[1]/bm[1]},'original_parent_winner_forfeited':forfeited,'strict_eligible_feb':bool(strict),'material_net_and_gl_feb':bool(material),'daily':daily,'reason_counts':{'hard_initial':int((REAS[v,ix]==1).sum()),'harvest_trail':int((REAS[v,ix]==2).sum()),'maxhold':int((REAS[v,ix]==3).sum()),'runner_trail':int((REAS[v,ix]==4).sum())},'max_quote_gap_overshoot':float(OVERS[v,ix].max())})
 audit=OUT/'HOLD022_ARMED_TRAJECTORY_FEB_REPLICATION_AUDIT.npz'
 np.savez_compressed(audit, entry_ms=e, parent_exit_ms=pex, parent_pnl=pp, at07_pnl=P[idx[0]],at07_exit_ms=X[idx[0]],at07_promoted=PRO[idx[0]],at07_decision_ms=DMS[idx[0]],at07_decision_efficiency=DEFF[idx[0]],at11_pnl=P[idx[1]],at11_exit_ms=X[idx[1]],at11_promoted=PRO[idx[1]],at11_decision_ms=DMS[idx[1]],at11_decision_efficiency=DEFF[idx[1]],parent_selected_idx=base_ix)
 with zipfile.ZipFile(audit) as az: assert az.testzip() is None
 result={'unit':C['unit'],'stage':'HOLD_EXIT_022_ARMED_TRAJECTORY_FEB_EXACT_TICK_REPLICATION','status':'VERIFIED_FEB_FROZEN_REPLICATION','original_parent_all_32862_raw_pnl_exit_hold_parity':True,'parent':{'trades':int(bm[0]),'winners':int(bm[1]),'net':bm[2],'gp':bm[3],'gl':bm[4],'pf':bm[5],'maxdd':bm[6]},'raw_candidates':len(e),'market_ticks':len(t),'feb_armed_raw_count':int(ARM.sum()),'frozen_ids':list(FROZEN_IDS),'variants':results,'unit_tests':tests,'execution':'Independent February Dukascopy midpoint, modeled fixed halfspread .10 each side, no true broker spread/slippage; one position strict event stream','january_contract_sha256':CONTRACT_SHA,'january_discovery_sha256':JAN_SHA,'january_discovery_script_sha256':JAN_SCRIPT_SHA,'feb_raw_cache_sha256':sha(RAW),'feb_market_sha256':sha(MARKET),'audit_sha256':sha(audit),'time_walls':{'january_original_predeclared_only':True,'february_replication_only':True,'march_accessed':False,'april_accessed':False,'may_jul_accessed':False,'august_accessed':False},'next':'STOP_FOR_HISTORICAL_FEB_REPLICATION_VERDICT__ONLY_IF_PREDECLARED_JAN_MAR_CAMPAIGN_CONTINUE_MARCH_WITHOUT_RETUNE', 'elapsed_s':round(time.perf_counter()-st,3)}
 out=OUT/'HOLD022_ARMED_TRAJECTORY_FEB_REPLICATION.json';out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
 man={'stage':result['stage'],'status':result['status'],'script_sha256':sha(__file__),'result_sha256':sha(out),'audit_sha256':sha(audit),'source_jan_contract_sha256':CONTRACT_SHA,'source_jan_discovery_sha256':JAN_SHA,'feb_raw_cache_sha256':sha(RAW),'feb_market_sha256':sha(MARKET),'source_equivalent_original_raw_parity':True,'august_accessed':False}
 mf=OUT/'HOLD022_ARMED_TRAJECTORY_FEB_REPLICATION_MANIFEST.json';mf.write_text(json.dumps(man,indent=2,sort_keys=True,allow_nan=False)+'\n')
 print(json.dumps({'status':result['status'],'parent':result['parent'],'feb_raw_count':len(e),'feb_ticks':len(t),'feb_raw_armed':result['feb_armed_raw_count'],'variants':[{k:r[k] for k in ('id','raw_promoted','selected_promoted','results','delta','retention','original_parent_winner_forfeited','strict_eligible_feb','material_net_and_gl_feb')} for r in results],'source_sha256':sha(__file__),'result_sha256':sha(out),'manifest_sha256':sha(mf),'audit_sha256':sha(audit),'elapsed_s':result['elapsed_s']},indent=2))
if __name__=='__main__':main()
