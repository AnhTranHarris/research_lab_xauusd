"""R10 Alpha CLI: source validation, on-demand multi-resolution bars, smoke replay."""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from .data import (MONTH_SHA256, PRICE_SCALE, BAR_WIDTHS_MS, prepare_month,
                   load_month, bars_from_ticks, month_iso_week_rollup)
from .sim import (ExecutionConfig, TickPortfolio, deterministic_smoke_signals,
                  load_signals_csv, write_run_outputs)


def period_file_name(month:str)->str:return month.replace('-','_')


def _rollup_tables(portfolio:TickPortfolio,metadata:dict[str,dict],out:Path,tag:str):
    """Consolidated daily/monthly/UTC-ISO-week summaries, with no fake weekend trades.

    Open trades are NOT counted in P&L until actual exit. ISO week is
    a provisional research grouping, not a user-defined trading week.
    """
    all_days={}
    for m,meta in metadata.items():
        for date,rows in meta['daily_tick_rows'].items():
            all_days[date]={'date_utc':date,'source_month':m,
                'source_tick_rows':rows,'closed_trades':0,'realized_net_usd':0.0,
                'gross_profit_usd':0.0,'gross_loss_usd':0.0,'commission_usd':0.0}
    for t in portfolio.trades:
        d=datetime.fromtimestamp(t['exit_ms']/1000,timezone.utc).date().isoformat()
        if d not in all_days:
            # Trade exit day was not in the requested source subset; do not
            # invent a market-data row or silently misattribute P&L.
            raise ValueError(f'Unindexed trade exit date: {d}')
        row=all_days[d]
        row['closed_trades']+=1
        row['realized_net_usd']+=t['net_usd']
        row['commission_usd']+=t['commission_usd']
        row['gross_profit_usd']+=max(t['gross_usd'],0)
        row['gross_loss_usd']+=min(t['gross_usd'],0)
    daily=list(sorted(all_days.values(),key=lambda r:r['date_utc']))
    for d in daily:
        for key in ('realized_net_usd','gross_profit_usd','gross_loss_usd','commission_usd'):
            d[key]=round(d[key],6)
    weeks=defaultdict(lambda:{'ticks':0,'trades':0,'net':0.0,'gp':0.0,'gl':0.0})
    for day in daily:
        yw=datetime.fromisoformat(day['date_utc']).date().isocalendar()
        key=f'{yw.year}-W{yw.week:02d}'
        week=weeks[key];week['ticks']+=day['source_tick_rows'];week['trades']+=day['closed_trades']
        week['net']+=day['realized_net_usd'];week['gp']+=day['gross_profit_usd'];week['gl']+=day['gross_loss_usd']
    weekly=[{'iso_utc_week_PROVISIONAL':week,**{key:round(value,6) if isinstance(value,float) else value
             for key,value in record.items()}} for week,record in sorted(weeks.items())]
    for filename,rows in [(f'{tag}_daily.csv',daily),(f'{tag}_weeks_UTC_ISO_PROVISIONAL.csv',weekly)]:
        with (out/filename).open('w',newline='') as f:
            if not rows:continue
            wr=csv.DictWriter(f,fieldnames=rows[0].keys());wr.writeheader();wr.writerows(rows)
    return {'dates':len(daily),'weeks_utc_iso_provisional':len(weekly)}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['prepare','bar-audit','smoke','signals'])
    p.add_argument('--data-root',type=Path,default=Path('/mnt/data'))
    p.add_argument('--cache',type=Path,default=Path('./cache'))
    p.add_argument('--output',type=Path,default=Path('./results'))
    p.add_argument('--months',nargs='+',default=list(MONTH_SHA256))
    p.add_argument('--force',action='store_true')
    p.add_argument('--signals-folder',type=Path,default=None,
                   help='For action=signals, folder containing 2026-01.csv,...')
    p.add_argument('--balance',type=float,default=200.0)
    p.add_argument('--lot',type=float,default=0.01)
    p.add_argument('--contract-oz-per-lot',type=float,default=100)
    p.add_argument('--commission',type=float,default=.20)
    p.add_argument('--slippage-each-side',type=float,default=.05)
    p.add_argument('--max-spread',type=float,default=6.0)
    p.add_argument('--leverage',type=float,default=500.0)
    p.add_argument('--tag',default='ALPHA_INFRASTRUCTURE')
    args=p.parse_args(argv)
    if not args.months or any(m not in MONTH_SHA256 for m in args.months):
        p.error('Only explicitly named 2026-01 through 2026-07 permitted; August SEALED')
    if args.months != sorted(set(args.months)):
        p.error('Months must be unique and chronological')
    if args.action=='signals' and args.signals_folder is None:
        p.error('--signals-folder required for action=signals')
    t0=time.perf_counter()
    metas={}
    for m in args.months:
        metas[m]=prepare_month(args.data_root,args.cache,m,force=args.force)
        print(json.dumps({'stage':'PREPARED_SOURCE','month':m,
            'ticks':metas[m]['tick_count'],'source_sha256':metas[m]['source_sha256'],
            'cache_bytes':metas[m]['cache_bytes']},sort_keys=True),flush=True)
    if args.action=='prepare':
        print(json.dumps({'status':'READY_FOR_CAUSAL_REPLAY',
                          'months':args.months,'seconds':round(time.perf_counter()-t0,3)}))
        return
    if args.action=='bar-audit':
        audits=[]
        for m in args.months:
            ticks,_=load_month(args.cache,m)
            counts={}
            for width in BAR_WIDTHS_MS:
                arr=bars_from_ticks(ticks,width)
                if len(arr) and not (arr['end_ms']>arr['last_tick_ms']).all():
                    raise AssertionError(f'Bucket inclusion invalid month={m},width={width}')
                counts[str(width)]=len(arr)
                del arr
            audits.append({'month':m,'bars_with_real_ticks_by_width_ms':counts,
                           'tick_rows':len(ticks)})
            print(json.dumps({'stage':'BAR_AUDITED',**audits[-1]}),flush=True)
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'alpha_multiresolution_bar_audit.json').write_text(
            json.dumps({'status':'ALL_DERIVED_FROM_REAL_TICKS_NO_SYNTHETIC_EMPTY_BARS',
                        'months':audits,'price_scale':PRICE_SCALE},indent=2)+'\n')
        return
    cfg=ExecutionConfig(initial_balance_usd=args.balance,lot=args.lot,
        contract_oz_per_lot=args.contract_oz_per_lot,leverage=args.leverage,
        commission_roundtrip_usd=args.commission,
        slippage_each_side_usd=args.slippage_each_side,
        max_spread_usd=args.max_spread)
    portfolio=TickPortfolio(cfg)
    strategy_class='INFRASTRUCTURE_SMOKE_ONLY_NOT_ALPHA_STRATEGY' if args.action=='smoke' else 'UNVERIFIED_EXTERNAL_SIGNALS'
    for month in args.months:
        ticks,_=load_month(args.cache,month)
        if args.action=='smoke':signals=deterministic_smoke_signals(ticks,month)
        else:
            file=args.signals_folder/f'{month}.csv'
            signals=load_signals_csv(file) if file.exists() else []
        block=portfolio.run_block(month,ticks,signals)
        print(json.dumps({'stage':'REPLAYED_MONTH','strategy_class':strategy_class,**block}),flush=True)
    args.output.mkdir(parents=True,exist_ok=True)
    summary=write_run_outputs(portfolio,args.output,args.tag)
    summary['strategy_class']=strategy_class
    summary['reporting']=_rollup_tables(portfolio,metas,args.output,args.tag)
    summary['runtime_seconds_total_including_source_SHA256']=round(time.perf_counter()-t0,3)
    (args.output/f'{args.tag}_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'status':'NO_LOOKAHEAD_BOUNDARY_ENGINE_EXECUTED',
                      'strategy_class':strategy_class,'closed_trades':summary['trades_closed'],
                      'months':args.months,'seconds':summary['runtime_seconds_total_including_source_SHA256']},sort_keys=True))


if __name__=='__main__':main()