"""Independently recheck *original R9* REAL/SYNTH 8-day, unpaired ENTRY price markouts.
Forensic only: no strategy inputs, no Dukascopy intermixing, no Gamma use.
"""
import gzip,hashlib,json
from pathlib import Path
import pandas as pd
import numpy as np

DATES=('2026-01-02','2026-01-30','2026-02-02','2026-03-02','2026-04-01','2026-05-01','2026-06-01','2026-07-01')
HORIZONS=(1,3,10,20,30)

def inspect_file(path:Path):
    # Original R9 EA tick-logger event is attached to its observed quote; entry
    # populations for REAL and SYNTH are separate, never matched ID-to-ID.
    df=pd.read_csv(path,compression='gzip',usecols=['time_msc','bid','ask','event'],
                    dtype={'time_msc':'int64','bid':'float64','ask':'float64','event':'str'},low_memory=False)
    ts=df.time_msc.to_numpy(copy=False)
    if len(ts)==0 or np.any(np.diff(ts)<0):raise ValueError('nonmonotonic ticklog '+str(path))
    bids=df.bid.to_numpy(copy=False);asks=df.ask.to_numpy(copy=False)
    if np.any(bids>asks):raise ValueError('negative spread '+str(path))
    events=df.event.to_numpy(copy=False)
    masks=(events=='ENTRY_BUY') | (events=='ENTRY_SELL')
    idx=np.flatnonzero(masks)
    side=np.where(events[idx]=='ENTRY_BUY',1,-1)
    entry=np.where(side>0,asks[idx],bids[idx])
    result={'filename':path.name,'sha256_original_gzip':hashlib.sha256(path.read_bytes()).hexdigest(),
            'rows':len(ts),'entry_events':len(idx),'buy':int((side>0).sum()),'sell':int((side<0).sum()),'horizons':{}}
    for h in HORIZONS:
        future=ts[idx]+h*1000
        ix=np.searchsorted(ts,future,side='left')
        ix=np.minimum(ix,len(ts)-1)
        valid=(ts[ix]>=future)&(ts[ix]<=future+1000)&(ix>idx)
        net=side*(np.where(side>0,bids[ix],asks[ix])-entry)
        a=net[valid]
        result['horizons'][str(h)]={'observed':len(a),'positive':int((a>0).sum()),
            'sum_markout_usd_per_oz':float(a.sum()),'mean_markout_usd_per_oz':float(a.mean()) if len(a) else None}
    return result

def main():
    items=[]
    for label in ('REAL','SYNTH'):
        for date in DATES:
            p=Path('/mnt/data')/f'R9_{label}_{date}_ticks.csv.gz'
            out=inspect_file(p);out['label']=label;out['date']=date;items.append(out)
    totals={}
    for label in ('REAL','SYNTH'):
        sub=[z for z in items if z['label']==label]
        totals[label]={'rows':sum(x['rows'] for x in sub),'entries':sum(x['entry_events'] for x in sub),'horizons':{}}
        for h in HORIZONS:
            a=[x['horizons'][str(h)] for x in sub]
            n=sum(x['observed'] for x in a);s=sum(x['positive'] for x in a)
            totals[label]['horizons'][str(h)]={'observed':n,'positive':s,'positive_fraction':s/n if n else None,
                'mean_spread_included_uncosted_markout_usd_per_oz':sum(x['sum_markout_usd_per_oz'] for x in a)/n if n else None}
    payload={'status':'ORIGINAL_R9_EIGHT_DAY_FORENSIC_RECHECK_NOT_ALPHA_PNL',
             'month_coverage':'eight selected source dates Jan-Jul, not all 149 historical sessions',
             'notes':['R9 REAL and SYNTH entries are unmatched populations',
                      'Markout ignores lifecycle closure and may run past original exit',
                      'Raw executable entry/exit sides include spread, no synthetic commission/slippage',
                      'Not a live strategy, forward test or trade realization'],
             'totals':totals,'days':items,'august':'SEALED'}
    out=Path('/mnt/data/clean_alpha_20260928/results/CLEAN_RESTART_R9_8DAY_MARKOUT_RECHECK.json')
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(totals,indent=2));print('SHA256',hashlib.sha256(out.read_bytes()).hexdigest())
if __name__=='__main__':main()
