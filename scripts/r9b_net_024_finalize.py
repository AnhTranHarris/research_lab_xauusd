"""Source-bound NET024 seven-month frozen-rule audit and exit-research handoff.

No new parameter search or source gzip reads; uses verified Jan-July raw event
caches made by unchanged pre-April NET024 engine. August is sealed.
"""
from __future__ import annotations
import json, sys, os, hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/net024_src')
import net024_h1_permission as N
ROOT=Path('/mnt/data/net024_results')

def write_json(path, x):
 tmp=path.with_suffix('.tmp.json');tmp.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');os.replace(tmp,path)

def write_npz(path, **kw):
 tmp=path.with_suffix('.tmp.npz');np.savez_compressed(tmp,**kw);os.replace(tmp,path)

def dd(p):
 p=np.asarray(p,dtype=np.float64);e=np.r_[0,np.cumsum(p)]
 return float((np.maximum.accumulate(e)-e).max())

def run():
 fpath=ROOT/'NET024_DISCOVERY_FROZEN.json';f=json.loads(fpath.read_text());assert f['status']=='FROZEN_BEFORE_APRIL' and f['frozen_variant']=='veto_contra_weak_align|2'
 apath=ROOT/'NET024_APRIL_FROZEN.json';apr=json.loads(apath.read_text());assert apr['pass_predeclared_gate'] and apr['discovery_sha256']==N.sha(fpath)
 month_results=[];baseline_p=[];candidate_p=[];baseline_t=[];candidate_t=[];candidate_exit=[]
 for mon in range(1,8):
  src=ROOT/f'NET024_RAW_{mon:02d}.npz';man=ROOT/f'NET024_RAW_{mon:02d}.manifest.json';m=json.loads(man.read_text())
  assert m['month']==mon and m['source_sha256']==N.sha(N.__file__) and m['raw_cache_sha256']==N.sha(src)
  assert m['raw_data_sha256']==N.sha(N.R.RAW_BY_MONTH[mon]) # immutable verified original market source, no decompression
  with np.load(src,allow_pickle=False) as z:
   e=z['raw_entry_ms'];exit=z['raw_exit_ms'];p=z['raw_pnl'];side=z['raw_side'];align=z['raw_align'];h1t=z['h1_close_ms'];h1s=z['h1_side']
   assert len(e)==len(p)==len(side)==len(exit)==len(align)==m['raw_candidates']
   assert np.all(np.diff(e)>=0) and np.all(np.diff(h1t)>0) and np.all(np.abs(h1s)==1)
   owner=N.owner_map(e,h1t,h1s,2)
   veto=(owner!=0)&(side==-owner)&(align<3)
   bi=N.raw_replay(e,exit,p,np.ones(len(e),bool));ci=N.raw_replay(e,exit,p,~veto)
   b=N.mtr(p[bi]);c=N.mtr(p[ci]);expect=N.PARENT_EXPECT[mon]
   assert (b['trades'],b['winners'])==expect[1:3] and abs(b['net']-expect[3])<1e-8
   if mon<=3:
    expected=list(filter(lambda y:y['month']==mon,f['selected_discovery_metrics']['months']))
    assert len(expected)==1
    v=expected[0]['metrics'];assert c['trades']==v['trades'] and c['winners']==v['winners'] and abs(c['net']-v['net'])<1e-8
   if mon==4:
    assert c==apr['candidate'] and b==apr['baseline']
   if mon>=5:
    fw=ROOT/f'NET024_FORWARD_{mon:02d}.json';r=json.loads(fw.read_text());cm=ROOT/f'NET024_CHECKPOINT_{mon:02d}_MANIFEST.json';checkpoint=json.loads(cm.read_text());assert checkpoint['result_sha256']==N.sha(fw) and r['selected_rule']==f['frozen_variant']
    for key in ('trades','winners','net','gross_profit','gross_loss','pf','maxdd','win_rate'):
     assert abs(c[key]-r['candidate'][key])<1e-8 and abs(b[key]-r['baseline'][key])<1e-8
    lpath=ROOT/f'NET024_LEDGER_{mon:02d}.npz';assert N.sha(lpath)==r['ledger_sha256']
    with np.load(lpath,allow_pickle=False) as q:
     assert np.array_equal(q['baseline_entry_ms'],e[bi]) and np.array_equal(q['candidate_entry_ms'],e[ci])
     assert np.array_equal(q['candidate_pnl'],p[ci]) and np.array_equal(q['baseline_pnl'],p[bi])
   baseline_p.append(p[bi]);candidate_p.append(p[ci]);baseline_t.append(e[bi]);candidate_t.append(e[ci]);candidate_exit.append(exit[ci])
   month_results.append({'month':mon,'basis':'JAN_MAR_DISCOVERY' if mon<=3 else ('APRIL_CALIBRATION' if mon==4 else 'FROZEN_FORWARD'),
    'parent':b,'candidate':c,'delta_net':c['net']-b['net'],'delta_gross_loss':c['gross_loss']-b['gross_loss'],
    'delta_gross_profit':c['gross_profit']-b['gross_profit'],'delta_pf':c['pf']-b['pf'],
    'winner_retention_pct':100*c['winners']/b['winners'],'trade_retention_pct':100*c['trades']/b['trades'],
    'h1_completed_signals':len(h1t),'raw_veto_count':int(veto.sum()),'raw_cache_sha256':N.sha(src)})
 BP=np.concatenate(baseline_p);CP=np.concatenate(candidate_p);BT=np.concatenate(baseline_t);CT=np.concatenate(candidate_t);CE=np.concatenate(candidate_exit)
 assert np.all(np.diff(BT)>=0) and np.all(np.diff(CT)>=0);assert np.all(CT[1:] > CE[:-1]), 'Portfolio overlap across month boundary or inside month'
 # The chronological engine intentionally restarts at every month for comparability to exact CAUSAL014 golden; check intra-month.
 offs=0
 for arr in candidate_p:
  # separately verified by raw_replay in loop
  offs+=len(arr)
 agg_b=N.mtr(BP);agg_c=N.mtr(CP)
 assert (agg_b['trades'],agg_b['winners'])==(197574,133142)
 assert abs(agg_b['net']-(-35399.91300000000))<1e-5
 assert all(x['delta_gross_loss']>0 and x['delta_net']>0 and x['winner_retention_pct']>=95 and x['trade_retention_pct']>=95 for x in month_results)
 forward=month_results[4:];fw_b=N.mtr(np.concatenate(baseline_p[4:]));fw_c=N.mtr(np.concatenate(candidate_p[4:]));disc_b=N.mtr(np.concatenate(baseline_p[:3]));disc_c=N.mtr(np.concatenate(candidate_p[:3]))
 v={'unit':'R9B_GAMMA_DYNAMIC_NET_024_H1_OWNERSHIP_SEQUENTIAL_PERMISSION','stage':'FINAL_JAN_JUL_CAUSAL_AUDIT',
  'status':'VERIFIED_LOCAL_FULL_JAN_JUL','parent':'CAUSAL_RECERT_014',
  'rule':'2h NET022 completed H1 contra-veto when five-scale parent alignment <3',
  'discovery_frozen_before_april':True,'forward_tuning':False,'august_accessed':False,
  'discovery_frozen_sha256':N.sha(fpath),'april_sha256':N.sha(apath),
  'engine_sha256':N.sha(N.__file__),'forward_runner_sha256':N.sha('/mnt/data/net024_src/net024_forward_frozen.py'),
  'finalizer_sha256':N.sha(__file__),
  'monthly':month_results,'jan_jul':{'parent':agg_b,'candidate':agg_c,
    'net_improvement':agg_c['net']-agg_b['net'],
    'gross_loss_reduction':agg_c['gross_loss']-agg_b['gross_loss'],
    'gross_loss_reduction_pct':100*(agg_c['gross_loss']-agg_b['gross_loss'])/-agg_b['gross_loss'],
    'net_loss_reduction_pct':100*(agg_c['net']-agg_b['net'])/-agg_b['net'],
    'gp_change':agg_c['gross_profit']-agg_b['gross_profit'],
    'continuous_maxdd_parent':dd(BP),'continuous_maxdd_candidate':dd(CP),
    'continuous_dd_improvement':dd(BP)-dd(CP),
    'winner_retention_pct':100*agg_c['winners']/agg_b['winners'],
    'trade_retention_pct':100*agg_c['trades']/agg_b['trades']},
  'jan_mar_discovery':{'parent':disc_b,'candidate':disc_c},
  'may_jul_untuned_forward':{'parent':fw_b,'candidate':fw_c,
    'delta_net':fw_c['net']-fw_b['net'],'gross_loss_reduction':fw_c['gross_loss']-fw_b['gross_loss'],
    'winner_retention_pct':100*fw_c['winners']/fw_b['winners'],
    'trade_retention_pct':100*fw_c['trades']/fw_b['trades']},
  'validation':{'golden_parent_all_months':True,'jan_mar_selected_freeze_parity':True,
   'april_calibration_parity':True,'may_jul_forward_ledger_parity':True,
   'full_jan_jul_single_position_non_overlap':True,
   'all_months_positive_net_delta':True,'all_months_positive_gross_loss_delta':True,
   'all_months_retention_ge_95pct':True,
   'no_cross_month_open_positions_contract':'per-month engine intentionally cold-starts, as in CAUSAL014 goldens',
   'july_raw_manifest_next_stage_erratum':'Original cache-month generator points from July to RAW_08 generically, but month guard rejects month=8, no August was accessed; authoritative next unit is HOLD_EXIT_022.'},
  'decision':'RETAIN_H1_VETO_AS_OPTIONAL_CAUSAL_LOSS_CONTEXT_NOT_PROMOTED',
  'rationale':'All seven months produce small net and GL improvement with >95% winner/trade retention, but strategy remains materially net-negative and every monthly PF falls. H1-veto is an optional hold/exit owner context for ablation, not production entry filter or formal breakthrough.',
  'next_research_unit':'R9B_GAMMA_DYNAMIC_HOLD_EXIT_022_STATE_DEPENDENT_HARVEST_FAILURE_REBUILD',
  'hold_exit_objective':'Improve net/GP and contain loss tails while preserving high CAUSAL014 winner/trade density; source-complete frozen ENTRY017-024 diagnostic states available but need economics and full replays before entry/hold deployment.'}
 ledger=ROOT/'NET024_FINAL_JAN_JUL_LEDGER.npz';write_npz(ledger,parent_entry_ms=BT,parent_pnl=BP,candidate_entry_ms=CT,candidate_exit_ms=CE,candidate_pnl=CP)
 v['final_ledger_sha256']=N.sha(ledger);jpath=ROOT/'NET024_FINAL_JAN_JUL.json';write_json(jpath,v)
 cm={'stage':v['stage'],'status':'COMPLETED_LOCAL_AWAIT_DURABLE','source_sha256':N.sha(__file__),
  'engine_sha256':v['engine_sha256'],'discovery_sha256':v['discovery_frozen_sha256'],
  'april_sha256':v['april_sha256'],'monthly_input_sha256':{str(x['month']):x['raw_cache_sha256'] for x in month_results},
  'forward_result_sha256':{str(m):N.sha(ROOT/f'NET024_FORWARD_{m:02d}.json') for m in (5,6,7)},
  'final_result_sha256':N.sha(jpath),'final_ledger_sha256':v['final_ledger_sha256'],
  'next_stage':v['next_research_unit'],'august_accessed':False}
 mpath=ROOT/'NET024_FINAL_JAN_JUL_MANIFEST.json';write_json(mpath,cm)
 print(json.dumps({'status':v['decision'],'jan_jul':v['jan_jul'],'forward':v['may_jul_untuned_forward'],
   'result_sha256':N.sha(jpath),'ledger_sha256':N.sha(ledger),'manifest_sha256':N.sha(mpath),
   'next_unit':v['next_research_unit'],'august_accessed':False}))
if __name__=='__main__':run()