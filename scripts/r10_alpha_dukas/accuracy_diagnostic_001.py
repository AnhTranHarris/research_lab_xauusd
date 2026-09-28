"""Post-registered purely diagnostic ENTRY direction/holding behavior of fixed source events.
No outcome enters generate_root_month or a trading signal. Separate from market orders.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from entry_hold_discovery_001 import generate_root_month, BRANCHES
from alpha_dukas.data import load_month

def main():
 ticks,_=load_month(Path('/mnt/data/r10_alpha_discovery/cache'),'2026-01')
 bars,idxs,roots=generate_root_month(ticks,'2026-01')
 tm=ticks['time_msc'];mid=(ticks['bid_raw'].astype(np.int64)+ticks['ask_raw'].astype(np.int64))/2000.
 ends=bars['end_ms'];out={}
 for b in BRANCHES:
  ids=idxs[b];sides=np.where(bars['bid_c'][ids]>=bars['bid_o'][ids],1,-1)
  entry_idx=np.searchsorted(tm,ends[ids],side='left')
  if np.any(entry_idx>=len(tm)):raise ValueError('source exhausted')
  info={'n_root':len(ids)}
  for dur in [1000,3000,10000,30000,60000,120000]:
   f=np.searchsorted(tm,ends[ids]+dur,side='left')
   valid=(f<len(tm))&(tm[np.minimum(f,len(tm)-1)]-(ends[ids]+dur)<2000)
   change=sides[valid]*(mid[f[valid]]-mid[entry_idx[valid]])
   # Neutral direction counts as a miss for 0.50 price move.
   info[f'{dur//1000}s']={'n':int(valid.sum()),'favorable_50c':round(float(np.mean(change>=.5)),5),
                     'adverse_50c':round(float(np.mean(change<=-.5)),5),
                     'signed_midmean_usd':round(float(np.mean(change)),5),
                     'signed_midmedian_usd':round(float(np.median(change)),5),
                     'positive_direction_fraction':round(float(np.mean(change>0)),5)}
  out[b]=info
 print(json.dumps(out,indent=2))
 Path('/mnt/data/r10_alpha_discovery/results001/accuracy_diagnostics.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()