"""HOLD_EXIT_022 frozen Jan-Mar trail geometry partial diagnostic verdict.

Only aggregates already verified January source-exact screen and February/March
unretuned replication artifacts. Explicitly does NOT read April, May-Jul or
SEALED August. Monthwise gate is authoritative: any failed month -> no OOS.
"""
from pathlib import Path
import json,hashlib,os
BASE=Path('/mnt/data/hold022_results')
OUT=BASE/'HOLD022_RUNNER_JAN_MAR_DISCOVERY_VERDICT.json'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())

def run():
 janfile=BASE/'HOLD022_JAN_RUNNER_TRAIL.json'
 febfile=BASE/'HOLD022_RUNNER_REPLICATION_2026_02.json'
 marfile=BASE/'HOLD022_RUNNER_REPLICATION_2026_03.json'
 j=load(janfile);f=load(febfile);m=load(marfile)
 assert j['strict_eligible_count']==0 and j['monetization_diagnostic_count']==1
 jr=j['monetization_diagnostics'][0]
 assert jr['owner_mode']=='weak_only' and jr['trail_width_price']==.10
 assert f['rule']==m['rule']=={'weak_trail':.10,'strong_trail':.04,'original_stop_and_activation_unchanged':True}
 assert f['source_replay_exact_pnl_and_exit_parity'] and m['source_replay_exact_pnl_and_exit_parity']
 months=[{'month':1,'parent':j['baseline'],'candidate':jr['metrics'],'delta':jr['delta'],'pass':True},
   {'month':2,'parent':f['parent'],'candidate':f['candidate'],'delta':f['delta'],'pass':f['frozen_partial_monetization_gate_pass']},
   {'month':3,'parent':m['parent'],'candidate':m['candidate'],'delta':m['delta'],'pass':m['frozen_partial_monetization_gate_pass']}]
 keys=['trades','winners','net','gross_profit','gross_loss']
 agg={kind:{k:sum(d[kind][k] for d in months) for k in keys} for kind in ['parent','candidate']}
 for kind in ['parent','candidate']:
  agg[kind]['pf']=agg[kind]['gross_profit']/-agg[kind]['gross_loss']
 delta={k:agg['candidate'][k]-agg['parent'][k] for k in keys+['pf']}
 wret=100*agg['candidate']['winners']/agg['parent']['winners']
 tret=100*agg['candidate']['trades']/agg['parent']['trades']
 verdict=all(d['pass'] for d in months)
 assert not verdict and not months[1]['pass']
 out={'unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD',
 'stage':'JAN_MAR_FROZEN_WEAK_0P10_RUNNER_DISCOVERY_VERDICT',
 'status':'COMPLETED_LOCAL','august_accessed':False,'april_accessed':False,'may_jul_accessed':False,
 'parent':'CAUSAL_RECERT_014',
 'selected_january_partial_diagnostic':{'weak_trail':.10,'strong_trail':.04},
 'frozen_monthly_criterion':'positive net AND GP, no >5% GL deterioration, >=95% winner and trade count retention EACH discovery month',
 'discovery_months':months,'jan_mar_parent':agg['parent'],'jan_mar_candidate':agg['candidate'],
 'jan_mar_delta':delta,'winner_retention_pct':wret,'trade_retention_pct':tret,
 'monthly_gates_all_pass':verdict,
 'decision':'REJECT_AS_STANDALONE_HARVEST_RULE_BECAUSE_FEBRUARY_FAILS_NET_GATE_AND_JAN_MAR_GROSS_LOSS_WORSENS; retain only original source-exact replay and trajectory economics as historical model evidence',
 'next':'HOLD_EXIT_022_EXIT_REASON_TRAJECTORY_HARVEST_VS_RUNNER_SOURCE_CLOSURE',
 'source_inputs':{file.name:sha(file) for file in [janfile,febfile,marfile]},
 'no_tuning_after_february':True,'do_not_release_april_may_july_for_rejected_rule':True}
 tmp=OUT.with_suffix('.partial.json');tmp.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');os.replace(tmp,OUT)
 mf=BASE/'HOLD022_RUNNER_JAN_MAR_DISCOVERY_VERDICT_MANIFEST.json'
 data={'status':'COMPLETED_LOCAL','source_sha256':sha(__file__),'result_sha256':sha(OUT),
  'dependencies':out['source_inputs'],'frozen_criterion_all_pass':False,'august_accessed':False,'next':out['next']}
 temp=mf.with_suffix('.partial.json');temp.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n');os.replace(temp,mf)
 print(json.dumps({'month_gate':[x['pass'] for x in months], 'jan_mar_parent':agg['parent'],
  'jan_mar_candidate':agg['candidate'],'delta':delta,'winners_retained_pct':wret,
  'trades_retained_pct':tret,'status':'COMPLETED_LOCAL_REJECT','result_sha256':sha(OUT),
  'manifest_sha256':sha(mf),'next':out['next']}))

if __name__=='__main__':run()