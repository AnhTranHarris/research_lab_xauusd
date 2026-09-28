"""HOLD_EXIT_022 frozen January--March discovery verdict (no market re-screen).

Consumes the immutable January 12-cell discovery result plus February and March
frozen AT07/AT11, independently reconstructing the selected one-position portfolio
from the stored raw-event audit ledgers. Does not touch Apr-Aug or tune rules.
"""
from pathlib import Path
import json, hashlib
import numpy as np

ROOT=Path('/mnt/data/hold022_results')
ST=Path('/mnt/data/hold022_stage')
FILES={
 'jan':ROOT/'HOLD022_ARMED_TRAJECTORY_JAN_DISCOVERY.json',
 'feb':ROOT/'HOLD022_ARMED_TRAJECTORY_FEB_REPLICATION.json',
 'mar':ROOT/'HOLD022_ARMED_TRAJECTORY_MAR_DIAGNOSTIC.json',
}
AUDITS={k:ROOT/('HOLD022_ARMED_TRAJECTORY_'+{'jan':'JAN_DISCOVERY','feb':'FEB_REPLICATION','mar':'MAR_DIAGNOSTIC'}[k]+'_AUDIT.npz') for k in FILES}
RAW={k:ST/f'NET024_RAW_0{i}.npz' for i,k in enumerate(FILES,1)}
CONTRACT=ST/'HOLD022_ARMED_TRAJECTORY_JAN_PREDECLARED.json'
FROZEN=('AT07','AT11')

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for buf in iter(lambda:f.read(1<<20),b''):h.update(buf)
 return h.hexdigest()

def select_one_position(entry, exits, pnl):
 chosen=[];free=-1
 assert np.all(np.diff(entry)>=0)
 for i in range(len(entry)):
  if not np.isfinite(pnl[i]) or exits[i]<0 or entry[i]<=free:continue
  chosen.append(i);free=int(exits[i])
 return np.array(chosen,dtype=np.int64)

def stats(p):
 n=len(p);w=int(np.count_nonzero(p>0));gp=float(p[p>0].sum());gl=float(p[p<0].sum());net=float(p.sum())
 eq=np.cumsum(p);previous_peaks=np.maximum.accumulate(np.r_[0.,eq])[:-1]
 maxdd=float(np.max(previous_peaks-eq)) if n else 0.
 return {'trades':n,'winners':w,'net':net,'gp':gp,'gl':gl,'pf':gp/-gl if gl<0 else None,'maxdd':maxdd}

def verify_month(month,r,raw,aud):
 with np.load(raw,allow_pickle=False) as z:
  entry=z['raw_entry_ms'].astype(np.int64);pex=z['raw_exit_ms'].astype(np.int64);pp=z['raw_pnl'].astype(float)
 with np.load(aud,allow_pickle=False) as z:
  if month=='jan':
   assert np.array_equal(z['parent_selected_raw_index'],select_one_position(entry,pex,pp))
   candidate={id:(z['variant_exit_ms'][pos].astype(np.int64),z['variant_pnl'][pos].astype(float)) for id,pos in [('AT07',6),('AT11',10)]}
  else:
   assert np.array_equal(z['entry_ms'],entry) and np.array_equal(z['parent_exit_ms'],pex) and np.array_equal(z['parent_pnl'],pp)
   assert np.array_equal(z['parent_selected_idx'],select_one_position(entry,pex,pp))
   candidate={id:(z[id.lower()+'_exit_ms'].astype(np.int64),z[id.lower()+'_pnl'].astype(float)) for id in FROZEN}
 parent=stats(pp[select_one_position(entry,pex,pp)])
 for k in ('trades','winners','net'):
  assert abs(parent[k]-r['parent'][k])<1e-8,(month,k,parent[k],r['parent'][k])
 for id,(ex,p) in candidate.items():
  v=next(x for x in r['variants'] if x['id']==id)
  m=stats(p[select_one_position(entry,ex,p)])
  ref=v.get('metrics',v.get('results'))
  for k in ('trades','winners','net','maxdd'):
   assert abs(m[k]-ref[k])<1e-8,(month,id,k,m[k],ref[k])
 return entry,pex,pp,candidate,parent

def main():
 C=json.loads(CONTRACT.read_text());assert C['variant_count']==12 and sha(CONTRACT)=='d6a2ec4ca4ffccad16cd79fe33a2040f555b2bedce03a9f789bf10eb75a76f41'
 results={k:json.loads(p.read_text()) for k,p in FILES.items()}
 assert results['jan']['strict_eligible_ids']==list(FROZEN)
 assert results['feb']['frozen_ids']==list(FROZEN) and results['mar']['frozen_ids']==list(FROZEN)
 assert all(not v['strict_eligible_feb'] for v in results['feb']['variants'])
 assert not results['mar']['promotion_permitted']
 months={}
 for name in FILES:
  assert sha(AUDITS[name])==results[name].get('audit_npz_sha256',results[name].get('audit_sha256'))
  months[name]=verify_month(name,results[name],RAW[name],AUDITS[name])
 entry=np.concatenate([months[m][0] for m in FILES]);ex=np.concatenate([months[m][1] for m in FILES]);p=np.concatenate([months[m][2] for m in FILES])
 assert np.all(np.diff(entry)>=0),'Cross-month order violation'
 original_idx=select_one_position(entry,ex,p)
 parent=stats(p[original_idx]); assert parent['trades']==91849 and parent['winners']==62090 and abs(parent['net']+15550.675000067717)<1e-8
 variants={}
 for id in FROZEN:
  cx=np.concatenate([months[m][3][id][0] for m in FILES]);cp=np.concatenate([months[m][3][id][1] for m in FILES]);selected_idx=select_one_position(entry,cx,cp)
  metric=stats(cp[selected_idx]); delta={k:metric[k]-parent[k] for k in ('net','gp','gl','maxdd','pf','trades','winners')}
  per=[]
  for m in FILES:
   r=results[m];v=next(x for x in r['variants'] if x['id']==id)
   d=v['delta'];per.append({'month':m,'net_delta':d['net'],'gp_delta':d.get('gross_profit',d.get('gp')),
    'gl_improvement':d.get('gross_loss_improvement',d.get('gl_improvement')),
    'trades_change':d['trades'],'winners_change':d['winners'],
    'month_strict_gate':v.get('strict_eligible',v.get('strict_eligible_feb',v.get('strict_eligible_mar')))})
  assert metric['trades']==parent['trades'] and metric['winners']==parent['winners']
  assert abs(delta['net']-sum(x['net_delta'] for x in per))<1e-8
  assert abs(delta['gl'])<1e-8
  variants[id]={'aggregate':metric,'delta':delta,'monthly':per,
   'any_strict_eligibility_failure':not all(x['month_strict_gate'] for x in per),
   'material_net_and_GL_5pct':delta['net']>=.05*abs(parent['net']) and delta['gl']>=.05*abs(parent['gl']),
   'promotion':'REJECT_STANDALONE_FROZEN_REPLICATION'}
 out={'unit':C['unit'],'stage':'HOLD_EXIT_022_ARMED_TRAJECTORY_JAN_MAR_FROZEN_VERDICT',
  'status':'VERIFIED_HISTORICAL_REPLICATION_REJECTED_STANDALONE',
  'parent':parent,'frozen_ids':list(FROZEN),'variants':variants,
  'validation':'Exact February and March original raw exits/PnL/hold times, Jan source frozen, 1-position raw event reselection separately and across months, no new parameters',
  'retention':'100% original trade and winning-position counts for these frozen candidates in each month',
  'interpretation':'Slight gross-profit changes after causal armed runner promotion do not address gross loss and fail February frozen gate. Neither candidate qualifies for April calibration or future months. No MT5 live/demo promotion.',
  'next':'HISTORICAL_NET002_NET007_STRUCTURAL_INDICATOR_COMBINATION_SOURCE_TO_PARENT_ARCHAEOLOGY',
  'historical_combinations_source_gap':'NET002-NET007 source families are present but parity into active CAUSAL014 engine/portfolio not established; separate hypotheses, not validated inheritance',
  'execution_model':'Midquote and fixed modeled $0.10 spread each side, 0.01-lot XAUUSD equivalent; not variable-spread Coinexx MT5 REAL',
  'source_input_sha256':{str(p.relative_to('/mnt/data')):sha(p) for p in [CONTRACT,*FILES.values(),*AUDITS.values(),*RAW.values()]},
  'time_walls':{'jan_used':True,'feb_used':True,'mar_used':True,'apr_used':False,'may_jul_used':False,'aug_used':False}}
 dst=ROOT/'HOLD022_ARMED_TRAJECTORY_JAN_MAR_FROZEN_VERDICT.json';dst.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
 mf=ROOT/'HOLD022_ARMED_TRAJECTORY_JAN_MAR_FROZEN_VERDICT_MANIFEST.json'
 mf.write_text(json.dumps({'stage':out['stage'],'status':out['status'],'script_sha256':sha(Path(__file__)),'verdict_sha256':sha(dst),'time_walls':out['time_walls']},indent=2,sort_keys=True)+'\n')
 print(json.dumps({'stage':out['stage'],'parent':parent,'variants':variants,'verdict_sha256':sha(dst),'manifest_sha256':sha(mf),'script_sha256':sha(Path(__file__)),'read_all_2026_04_onward':False},indent=2))

if __name__=='__main__':main()
