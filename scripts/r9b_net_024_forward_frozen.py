"""NET024 immutable two-hour H1 contra-veto forward runner.

Freeze authority: NET024_DISCOVERY_FROZEN.json Jan-Mar, calibrated April.
Executes only the selected frozen decision on one month, honoring the original
raw CAUSAL014 candidate stream and independent one-position chronological replay.
Never optimize using May-July results; August unavailable by contract.
"""
import sys,json,hashlib,time,os
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/net024_src')
import net024_h1_permission as N
ROOT=Path('/mnt/data/net024_results')
FR=ROOT/'NET024_DISCOVERY_FROZEN.json';APR=ROOT/'NET024_APRIL_FROZEN.json'

def atomic_json(path,obj):
 tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n');os.replace(tmp,path)

def atomic_npz(path,**arrays):
 tmp=path.with_suffix('.tmp.npz');np.savez_compressed(tmp,**arrays);os.replace(tmp,path)

def run(month):
 assert month in (5,6,7), 'May-Jul are only remaining frozen forward months; August SEALED'
 f=json.loads(FR.read_text());a=json.loads(APR.read_text())
 assert f['status']=='FROZEN_BEFORE_APRIL' and f['frozen_variant']=='veto_contra_weak_align|2'
 assert a['pass_predeclared_gate'] and a['discovery_sha256']==N.sha(FR)
 assert f['frozen_rule']['owner_duration_h']==2 and f['frozen_rule']['contra_veto_only_when_parent_align_lt']==3
 started=time.perf_counter();raw=ROOT/f'NET024_RAW_{month:02d}.npz';man=ROOT/f'NET024_RAW_{month:02d}.manifest.json'
 manifest=json.loads(man.read_text());assert N.sha(raw)==manifest['raw_cache_sha256']
 assert manifest['source_sha256']==N.sha(N.__file__)
 with np.load(raw,allow_pickle=False) as z:
  e=z['raw_entry_ms'];exit_ms=z['raw_exit_ms'];pnl=z['raw_pnl'];side=z['raw_side'];align=z['raw_align'];h1t=z['h1_close_ms'];h1s=z['h1_side'];
  assert len(e)==len(pnl)==len(side)==len(exit_ms)==len(align)==manifest['raw_candidates'];assert np.all(np.diff(e)>=0)
  assert np.all(np.diff(h1t)>0);assert np.all(np.abs(h1s)==1);assert np.all((align>=0)&(align<=5))
  owner=N.owner_map(e,h1t,h1s,2)
  veto=(owner!=0)&(side==-owner)&(align<3)
  base_ix=N.raw_replay(e,exit_ms,pnl,np.ones(len(e),dtype=bool))
  selected_ix=N.raw_replay(e,exit_ms,pnl,~veto)
  baseline=N.mtr(pnl[base_ix]);candidate=N.mtr(pnl[selected_ix])
  expected=N.PARENT_EXPECT[month]
  assert (baseline['trades'],baseline['winners'])==expected[1:3]
  assert abs(baseline['net']-expected[3])<1e-8
  assert len(np.intersect1d(base_ix,selected_ix))<=len(base_ix)
  diffs={'net_improvement':candidate['net']-baseline['net'],
    'gross_loss_reduction':candidate['gross_loss']-baseline['gross_loss'],
    'gross_profit_change':candidate['gross_profit']-baseline['gross_profit'],
    'maxdd_reduction_month':baseline['maxdd']-candidate['maxdd'],
    'trade_change':candidate['trades']-baseline['trades'],
    'winner_change':candidate['winners']-baseline['winners'],
    'win_rate_pp_change':100*(candidate['win_rate']-baseline['win_rate']),
    'pf_change':candidate['pf']-baseline['pf']}
  retention={'winners_pct':candidate['winners']/baseline['winners']*100,
             'trades_pct':candidate['trades']/baseline['trades']*100,
             'gross_profit_pct':candidate['gross_profit']/baseline['gross_profit']*100}
  ledger=ROOT/f'NET024_LEDGER_{month:02d}.npz'
  atomic_npz(ledger,
    baseline_entry_ms=e[base_ix],baseline_exit_ms=exit_ms[base_ix],baseline_pnl=pnl[base_ix],
    candidate_entry_ms=e[selected_ix],candidate_exit_ms=exit_ms[selected_ix],candidate_pnl=pnl[selected_ix],
    candidate_side=side[selected_ix],candidate_align=align[selected_ix],candidate_h1_owner=owner[selected_ix],
    veto_raw_count=np.array([veto.sum()],dtype=np.int64))
  res={'unit':'R9B_GAMMA_DYNAMIC_NET_024_H1_OWNERSHIP_SEQUENTIAL_PERMISSION',
    'stage':'FROZEN_FORWARD','month':month,'state':'COMPLETED_LOCAL',
    'calibration_gate':'APRIL_PASS_WITHOUT_FORWARD_TUNING',
    'selected_rule':'veto_contra_weak_align|2',
    'frozen_discovery_sha256':N.sha(FR),'april_calibration_sha256':N.sha(APR),
    'source_sha256':N.sha(__file__),'engine_sha256':N.sha(N.__file__),
    'raw_cache_sha256':N.sha(raw),'raw_market_input_sha256':manifest['raw_data_sha256'],
    'raw_candidates':len(e),'raw_veto_count':int(veto.sum()),'h1_completed_signals':len(h1t),
    'baseline':baseline,'candidate':candidate,'delta':diffs,'retention':retention,
    'ledger_file':ledger.name,'ledger_sha256':N.sha(ledger),'elapsed_s':time.perf_counter()-started,
    'august_accessed':False,'forward_rule_changed':False}
  out=ROOT/f'NET024_FORWARD_{month:02d}.json';atomic_json(out,res)
  checkpoint={'stage':res['stage'],'month':month,'status':'COMPLETED_LOCAL',
    'raw_cache_sha256':res['raw_cache_sha256'],'engine_sha256':res['engine_sha256'],
    'runner_sha256':res['source_sha256'],'rule':'veto_contra_weak_align|2',
    'discovery_sha256':res['frozen_discovery_sha256'],'april_sha256':res['april_calibration_sha256'],
    'ledger_sha256':res['ledger_sha256'],'result_sha256':N.sha(out),
    'baseline_golden_pass':True,'next_stage':f'NET024_FROZEN_FORWARD_{month+1:02d}' if month<7 else 'NET024_FORWARD_FINAL_AUDIT',
    'august_accessed':False}
  cm=ROOT/f'NET024_CHECKPOINT_{month:02d}_MANIFEST.json';atomic_json(cm,checkpoint)
  print(json.dumps({'month':month,'baseline':baseline,'candidate':candidate,'delta':diffs,
    'retention':retention,'raw_veto_count':res['raw_veto_count'],
    'result_sha256':N.sha(out),'ledger_sha256':res['ledger_sha256'],
    'manifest_sha256':N.sha(cm),'next':checkpoint['next_stage'],'august_accessed':False}),flush=True)

if __name__=='__main__':
 assert len(sys.argv)==2
 run(int(sys.argv[1]))