"""Pre-April lock for NET024; only Jan-Mar inputs accepted."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/mnt/data/net024_results')
cache=[]
for m in (1,2,3):
 p=ROOT/f'NET024_SCREEN_{m:02d}.json'
 d=json.loads(p.read_text()); assert d['month']==m and d['august_accessed']==False
 cache.append((p,d))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
variants={}
for p,d in cache:
 for x in d['rules']:
  k=f"{x['rule']}|{x['owner_hours']}"
  variants.setdefault(k,[]).append({'month':d['month'],'metrics':x['metrics'],'delta':x['delta_vs_parent'],'retention':x['retention']})

qual=[]; rejected=[]
for k,months in variants.items():
 assert len(months)==3
 s={'variant':k,'months':months,
 'cumulative_gl_reduction':sum(x['delta']['gross_loss_improvement'] for x in months),
 'cumulative_net_improvement':sum(x['delta']['net'] for x in months),
 'min_winner_retention_pct':min(x['retention']['winners_pct'] for x in months),
 'min_trade_retention_pct':min(x['retention']['trades_pct'] for x in months),
 'all_months_positive_net_delta':all(x['delta']['net']>0 for x in months),
 'all_months_positive_gl_delta':all(x['delta']['gross_loss_improvement']>0 for x in months)}
 good=(s['min_winner_retention_pct']>=95 and s['min_trade_retention_pct']>=95
   and s['all_months_positive_net_delta'] and s['all_months_positive_gl_delta'])
 if good:qual.append(s)
 else:rejected.append(k)
qual.sort(key=lambda a:(-a['cumulative_gl_reduction'],-a['min_winner_retention_pct'],-a['cumulative_net_improvement']))
selected=qual[0]
assert selected['variant']=='veto_contra_weak_align|2',selected['variant']
result={'unit':'R9B_GAMMA_DYNAMIC_NET_024_H1_OWNERSHIP_SEQUENTIAL_PERMISSION',
 'stage':'FROZEN_DISCOVERY_JAN_MAR','status':'FROZEN_BEFORE_APRIL',
 'frozen_variant':selected['variant'],'frozen_rule':{'owner_duration_h':2,'contra_veto_only_when_parent_align_lt':3,
 'net022_h1_lookback':13,'net022_h1_compression_prior':2,'net022_h1_compression_ratio_max':1.,
 'net022_h1_signal_expansion_ratio_min':1.,'net022_signal_body_min':.25,
 'net022_breakout_atr_buffer':.10,
 'feature_observability':'completed H1 bar at close timestamp, never a partial H1 state',
 'decision':'if latest H1 signal <= candidate timestamp and is younger than 2h, reject parent raw event only when side is opposite and parent five-scale alignment count <3; otherwise allow',
 'execution':'all accepted raw CAUSAL014 entry events chronological; first eligible; no preemption; one position; exclude entry time equal to previous exit'},
 'gate':'positive GL and net deltas in each Jan-Mar; >=95% trade and winner retention in each discovery month; rank eligible by sum GL reduction',
 'selected_discovery_metrics':selected,
 'eligible_variants_ranked':[{k:v for k,v in q.items() if k!='months'} for q in qual],
 'rejected_variants':rejected,
 'discovery_source_sha256':hashlib.sha256(Path('/mnt/data/net024_src/net024_h1_permission.py').read_bytes()).hexdigest(),
 'screen_sha256':{str(d['month']):sha(p) for p,d in cache},
 'calibration_policy':'Run April once with frozen selected rule; compare to CAUSAL014 for GL, trade/winner retention, net, before any May-Jul read. If April fails, stop or reject, do not retune Apr then claim untouched forward.',
 'august_accessed':False,
 'next_stage':'NET024_APRIL_CALIBRATION'}
p=ROOT/'NET024_DISCOVERY_FROZEN.json';p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'frozen_variant':selected['variant'], 'eligible':len(qual),'gl_reduction':selected['cumulative_gl_reduction'],
 'net_improvement':selected['cumulative_net_improvement'],'min_winner_retention':selected['min_winner_retention_pct'],
 'discovery_file':str(p),'sha256':sha(p),'next_stage':result['next_stage']}))