"""Compare entry-timestamp spread and fixed-horizon side-aware executable markout.
Later points AFTER actual original exit are HYPOTHETICAL untraded paths. Does NOT
reproduce MT5 tester strategy exit nor measure R9 trades' realized profits.
"""
import pandas as pd, numpy as np, json
from pathlib import Path
D=Path('/mnt/data'); days=['2026-01-02','2026-01-30','2026-02-02','2026-03-02','2026-04-01','2026-05-01','2026-06-01','2026-07-01']
rows=[]
for day in days:
 for feed in ['REAL','SYNTH']:
  p=D/f'R9_{feed}_{day}_ticks.csv.gz'
  frame=pd.read_csv(p,compression='gzip',usecols=['time_msc','bid','ask','event','entry_price','position_side','spread'])
  sig=frame.event.isin(['ENTRY_BUY','ENTRY_SELL']);ent=frame.loc[sig]
  dirr=np.where(ent.event=='ENTRY_BUY',1,-1)
  t=frame.time_msc.to_numpy(np.int64);e=ent.time_msc.to_numpy(np.int64);price=ent.entry_price.to_numpy(np.float64)
  open_spread=(ent.ask-ent.bid).to_numpy(np.float64)
  record={'day':day,'feed':feed,'entries':len(e),'median_entry_spread':np.median(open_spread),'mean_entry_spread':round(np.mean(open_spread),5)}
  for h in [1000,3000,10000,20000,30000]:
   inds=np.searchsorted(t,e+h,side='left')
   valid=(inds<len(t))&(t[np.minimum(inds,len(t)-1)]-(e+h)<=1000)
   qbid=frame.bid.to_numpy()[np.minimum(inds,len(t)-1)]
   qask=frame.ask.to_numpy()[np.minimum(inds,len(t)-1)]
   exit_quotes=np.where(dirr>0,qbid,qask)
   marks=(exit_quotes-price)*dirr
   x=marks[valid]
   record[f'markout_{h//1000}s_n']=len(x)
   record[f'markout_{h//1000}s_pos_share']=round(float((x>0).mean()),5)
   record[f'markout_{h//1000}s_mean']=round(float(x.mean()),5)
   record[f'markout_{h//1000}s_gt_20c_share']=round(float((x>=0.20).mean()),5)
  rows.append(record)
  print(day,feed,'entries',record['entries'],'entry-spread',round(record['median_entry_spread'],3),'10s positive markout',record['markout_10s_pos_share'],flush=True)
out=pd.DataFrame(rows);out.to_csv('/mnt/data/r10_alpha_discovery/r9_entry_markout_8days.csv',index=False)
all_stats={}
for label,sub in out.groupby('feed'):
 info={'entries':int(sub.entries.sum()),'equal_day_count':len(sub)}
 for h in [1,3,10,20,30]:
  n=sub[f'markout_{h}s_n'].sum()
  info[f'{h}s_positive_markout_share_weighted']=round(float((sub[f'markout_{h}s_pos_share']*sub[f'markout_{h}s_n']).sum()/n),5)
  info[f'{h}s_mean_markout_usd_weighted']=round(float((sub[f'markout_{h}s_mean']*sub[f'markout_{h}s_n']).sum()/n),5)
 info['mean_daily_median_entry_spread_unweighted']=round(float(sub.median_entry_spread.mean()),5)
 all_stats[label]=info
print(json.dumps(all_stats,indent=2));Path('/mnt/data/r10_alpha_discovery/r9_entry_markout_8days.json').write_text(json.dumps(all_stats,indent=2)+'\n')