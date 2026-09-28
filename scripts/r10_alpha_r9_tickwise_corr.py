#!/usr/bin/env python3
"""R10 Alpha: lossless, descriptive daily R9 REAL/SYNTH ticklog path comparison.

Reads complete *original daily logger CSV.GZ*; never pairs different feeds by row
number, never uses future REAL quotes for as-of alignment, never treats matching
bar OHLC as identical tick execution. Outputs no hypothetical trading profit.

Usage:
  python scripts/r10_alpha_r9_tickwise_corr.py \
    --real R9_REAL_2026-01-02_ticks.csv.gz \
    --synth R9_SYNTH_2026-01-02_ticks.csv.gz --out pair_2026-01-02.json
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

PERIODS_MS=(250,1000,5000,15000,30000,45000,60000)
FIELDS=['run_label','time_msc','bid','ask','event','gate_open','trail_armed']
DTYPE={'time_msc':'int64','bid':'float64','ask':'float64',
       'event':'category','run_label':'category','gate_open':'int8','trail_armed':'int8'}

def source(path,label):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while chunk:=stream.read(1<<22):h.update(chunk)
    df=pd.read_csv(path,compression='gzip',usecols=FIELDS,dtype=DTYPE)
    assert (df.run_label==label).all(), 'run_label mismatch'
    assert df.time_msc.is_monotonic_increasing, 'noncausal timestamp order'
    assert (df.ask>=df.bid).all(), 'invalid quote side'
    return df, {'name':path.name,'compressed_sha256':h.hexdigest(),
                'compressed_bytes':path.stat().st_size,'logged_rows':len(df)}

def corr(a,b):
    if len(a)<3 or np.std(a)==0 or np.std(b)==0:return None
    return round(float(np.corrcoef(a,b)[0,1]),6)

def bars(df,period):
    bucket=df.time_msc // period
    g=df.groupby(bucket,sort=True).bid
    return g.agg(o='first',h='max',l='min',c='last',n='size')

def main():
    cli=argparse.ArgumentParser()
    for field in ('real','synth','out'):
        cli.add_argument('--'+field,required=True,type=Path)
    args=cli.parse_args()
    real,rm=source(args.real,'REAL');synth,sm=source(args.synth,'SYNTH')
    # The last quote recorded within a millisecond is used solely for
    # diagnostic synchronization. Independent feed tie-order is unknowable.
    r=real[['time_msc','bid','ask']].drop_duplicates('time_msc',keep='last')
    s=synth[['time_msc','bid','ask']].drop_duplicates('time_msc',keep='last')
    same=r.merge(s,on='time_msc',suffixes=('_r','_s'))
    same_ms={'n':len(same),'unique_REAL':len(r),'unique_SYNTH':len(s),
             'median_abs_bid_usd':float((same.bid_r-same.bid_s).abs().median())}
    # Join the latest PRIOR real quote only, max quote age 250ms; this is
    # descriptive market-path comparison, NOT an executable cross-feed quote.
    rprior=r.rename(columns={'time_msc':'r_time_msc','bid':'rbid'})
    asof=pd.merge_asof(s[['time_msc','bid']],rprior[['r_time_msc','rbid']],
                       left_on='time_msc',right_on='r_time_msc',
                       direction='backward',tolerance=250)
    fresh=asof.r_time_msc.notna()
    resolutions={}
    for ms in PERIODS_MS:
        a=bars(real,ms);b=bars(synth,ms)
        z=a.join(b,how='inner',lsuffix='_r',rsuffix='_s')
        eq=np.logical_and.reduce([np.isclose(z[k+'_r'],z[k+'_s'],atol=.010001,rtol=0)
                                 for k in ['o','h','l','c']])
        resolutions[str(ms)]={'common_bars':len(z),
            'ohlc_match_share':float(eq.mean()),
            'net_bar_change_corr':corr(z.c_r-z.o_r,z.c_s-z.o_s),
            'tickcount_corr':corr(z.n_r,z.n_s)}
    result={'evidence':'COMPLETE_SINGLE_DAY_PRICE_TICK_COMPARISON_ONLY',
            'feeds':{'REAL':rm,'SYNTH':sm},'exact_ms':same_ms,
            'backward_asof_250ms':{'covered_synth_unique_ms':int(fresh.sum()),
                                  'covered_share':float(fresh.mean())},
            'median_spread_price_usd':{'REAL':float((real.ask-real.bid).median()),
                                       'SYNTH':float((synth.ask-synth.bid).median())},
            'events':{name:df.event.value_counts().to_dict()
                      for name,df in [('REAL',real),('SYNTH',synth)]},
            'resolution':resolutions}
    args.out.write_text(json.dumps(result,indent=2,default=int)+'\n')
    print(f'Wrote {args.out}; REAL {len(real):,} vs SYNTH {len(synth):,} rows')

if __name__=='__main__':main()
