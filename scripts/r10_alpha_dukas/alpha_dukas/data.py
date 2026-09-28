"""Source-authoritative Dukascopy monthly XAUUSD tick ingestion and on-demand bars.

MONTHS is intentionally hard-coded January--July. An uploaded August file MUST NEVER
be automatically discovered or opened by this module.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

PRICE_SCALE = 1000     # Explicit Dukascopy CSV converter convention: 4327902 -> $4327.902.
DAY_MS = 86_400_000
BAR_WIDTHS_MS = (250, 1000, 5000, 15000, 30000, 45000, 60000,
                 300000, 420000, 900000, 1800000, 2700000,
                 3600000, 14400000, 43200000, 86400000)
# Parse full input precision for quoted volumes; compressed CSV remains canonical.
TICK_DTYPE = np.dtype([('time_msc', '<i8'), ('ask_raw', '<i4'),
                       ('bid_raw', '<i4'), ('ask_volume', '<f8'),
                       ('bid_volume', '<f8')])
CSV_COLS = ['timestamp_ms_utc','ask_raw','bid_raw','ask_volume','bid_volume']
MONTH_SHA256 = {
    '2026-01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
    '2026-02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
    '2026-03':'814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177',
    '2026-04':'30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f',
    '2026-05':'3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d',
    '2026-06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
    '2026-07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7',
}


def resolve_month_source(data_root: Path, month: str) -> Path:
    if month not in MONTH_SHA256:
        raise ValueError(f'Month not authorized under R10 Alpha Jan--Jul scope: {month}')
    number = month[5:]
    # The attached Project files use (3) for Jan-Jun and (2) for July;
    # the original Drive names have no suffix. Never glob August.
    patterns = [f'XAUUSD_DUKAS_{month[:4]}_{number}_ticks.csv.gz',
                f'XAUUSD_DUKAS_{month[:4]}_{number}_ticks.csv(*).gz']
    hits = sorted({p for glob in patterns for p in data_root.glob(glob) if p.is_file()})
    if not hits: raise FileNotFoundError(f'No exact {month} Dukascopy gzip in {data_root}')
    if len(hits) != 1: raise ValueError(f'Ambiguous {month} source copies: {[str(p) for p in hits]}')
    return hits[0]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(4<<20), b''):h.update(chunk)
    return h.hexdigest()


def _atomic_json(path: Path, payload: dict) -> None:
    tmp=path.with_name(path.name+'.building')
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    os.replace(tmp,path)


def prepare_month(data_root: Path, cache_root: Path, month: str,
                  chunk_rows: int=200_000, force: bool=False) -> dict:
    """One-time GZIP→memory-mappable binary cache, source SHA validated.

    Chunked read avoids putting whole month into RAM; writes binary atomically.
    Neither missing ticks nor synthetic calendar bars are inserted.
    """
    src=resolve_month_source(Path(data_root),month)
    cache_root=Path(cache_root);cache_root.mkdir(parents=True,exist_ok=True)
    binfile=cache_root/f'{month}.ticks.bin'
    metafile=cache_root/f'{month}.manifest.json'
    source_hash=sha256_file(src)
    if source_hash != MONTH_SHA256[month]:
        raise ValueError(f'SOURCE_SHA_MISMATCH {month} actual={source_hash} expected={MONTH_SHA256[month]}')
    st=src.stat()
    if binfile.exists() and metafile.exists() and not force:
        meta=json.loads(metafile.read_text())
        if (meta.get('source_sha256')==source_hash
            and meta.get('cache_bytes')==binfile.stat().st_size
            and meta.get('tick_count')*TICK_DTYPE.itemsize == binfile.stat().st_size
            and meta.get('schema')=='r10_alpha_dukas_tick_cache_v1'):
            return meta
    y,mo=map(int,month.split('-'))
    month_start=int(datetime(y,mo,1,tzinfo=timezone.utc).timestamp()*1000)
    ny=y+(mo==12);nm=mo%12+1
    month_end=int(datetime(ny,nm,1,tzinfo=timezone.utc).timestamp()*1000)
    tmp=binfile.with_suffix('.bin.building')
    rows=0; previous=None; duplicates=0;first=None;last=None
    day_counts={}; spreads_min=None;spreads_max=None
    binhash=hashlib.sha256()
    try:
        with tmp.open('wb') as dest:
            iterator=pd.read_csv(src,compression='gzip',chunksize=chunk_rows,
                usecols=CSV_COLS,dtype={'timestamp_ms_utc':'int64','ask_raw':'int64',
                                       'bid_raw':'int64','ask_volume':'float64',
                                       'bid_volume':'float64'})
            for frame in iterator:
                if frame.empty:continue
                t=frame.timestamp_ms_utc.to_numpy(copy=False)
                a=frame.ask_raw.to_numpy(copy=False)
                b=frame.bid_raw.to_numpy(copy=False)
                if np.any((a < b)|(b<=0)|(a<=0)):
                    raise ValueError(f'NEGATIVE_SPREAD_OR_NONPOSITIVE_QUOTE {month}')
                if np.any((a>2_147_483_647)|(b>2_147_483_647)):
                    raise ValueError('QUOTE_INT32_OVERFLOW')
                if np.any((t<month_start)|(t>=month_end)):
                    raise ValueError(f'TICK_OUT_OF_UTC_MONTH {month}')
                if np.any(np.diff(t)<0) or (previous is not None and t[0]<previous):
                    raise ValueError(f'NONMONOTONIC_TIMESTAMP {month}')
                duplicates += int(np.count_nonzero(np.diff(t)==0))
                if previous is not None and t[0]==previous:duplicates+=1
                previous=int(t[-1]); first=int(t[0]) if first is None else first;last=previous
                spr=a-b;low=int(spr.min());high=int(spr.max())
                spreads_min=low if spreads_min is None else min(spreads_min,low)
                spreads_max=high if spreads_max is None else max(spreads_max,high)
                days,cts=np.unique(t//DAY_MS,return_counts=True)
                for day,n in zip(days,cts):
                    key=datetime.fromtimestamp(int(day)*86400,tz=timezone.utc).date().isoformat()
                    day_counts[key]=day_counts.get(key,0)+int(n)
                arr=np.empty(len(t),dtype=TICK_DTYPE)
                arr['time_msc']=t;arr['ask_raw']=a;arr['bid_raw']=b
                arr['ask_volume']=frame.ask_volume.to_numpy(copy=False)
                arr['bid_volume']=frame.bid_volume.to_numpy(copy=False)
                raw=arr.tobytes();dest.write(raw);binhash.update(raw)
                rows+=len(arr)
        os.replace(tmp,binfile)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    meta={'schema':'r10_alpha_dukas_tick_cache_v1','month':month,
          'market_feed':'Dukascopy XAUUSD MARKET TICKS, not R9 MT5 logger',
          'source_file':src.name,'source_sha256':source_hash,
          'source_compressed_bytes':st.st_size,'cache_file':binfile.name,
          'cache_sha256':binhash.hexdigest(),'cache_bytes':binfile.stat().st_size,
          'cache_dtype':TICK_DTYPE.descr,'tick_count':rows,'first_time_msc':first,
          'last_time_msc':last,'duplicate_timestamp_adjacent_pairs':duplicates,
          'price_scale':PRICE_SCALE,'min_spread_usd':spreads_min/PRICE_SCALE,
          'max_spread_usd':spreads_max/PRICE_SCALE,'daily_tick_rows':day_counts,
          'timezone':'UTC','bar_boundary':'floor(epoch_ms/width_ms), half-open [start,end)',
          'data_quality':'FULL_GZIP_CRC_READ__COMPRESSED_SHA256__ALL_ROWS_SCHEMA_ORDER_SPREAD_AND_MONTH_CHECKED',
          'cache_status':'IMMUTABLE_DERIVED_NUMERIC_REPLAY_CACHE__RAW_GZIP_AUTHORITATIVE'}
    _atomic_json(metafile,meta)
    return meta


def load_month(cache_root: Path, month: str) -> tuple[np.memmap, dict]:
    if month not in MONTH_SHA256:raise ValueError('Outside Jan-Jul 2026 seal')
    cache_root=Path(cache_root);j=cache_root/f'{month}.manifest.json'
    if not j.is_file():raise FileNotFoundError(f'Run prepare for {month} first')
    meta=json.loads(j.read_text())
    p=cache_root/meta['cache_file']
    if meta['source_sha256'] != MONTH_SHA256[month] or p.stat().st_size != meta['tick_count']*TICK_DTYPE.itemsize:
        raise ValueError(f'CACHE_IDENTITY_OR_LENGTH_INVALID {month}')
    ticks=np.memmap(p,mode='r',dtype=TICK_DTYPE,shape=(meta['tick_count'],))
    return ticks,meta


def bars_from_ticks(ticks: np.ndarray, width_ms: int) -> np.ndarray:
    """Exact tick-derived dual-side OHLC; no gap-filling or future data.

    An OHLC row with end_ms==T is eligible at the first subsequent
    executable tick timestamp >=T. 45s does NOT nest in 60s.
    """
    if width_ms not in BAR_WIDTHS_MS:raise ValueError(f'Unsupported width {width_ms}ms')
    dtype=np.dtype([('start_ms','<i8'),('end_ms','<i8'),
                    ('first_tick_ms','<i8'),('last_tick_ms','<i8'),('n_ticks','<i4')]
                   +[(f'{side}_{part}','<i4') for side in ('bid','ask')
                     for part in ('o','h','l','c')])
    if len(ticks)==0:return np.empty(0,dtype=dtype)
    ts=ticks['time_msc'];group=ts//width_ms
    starts=np.concatenate(([0],np.flatnonzero(group[1:]!=group[:-1])+1))
    ends=np.concatenate((starts[1:],[len(ts)]))
    out=np.empty(len(starts),dtype=dtype)
    out['start_ms']=group[starts]*width_ms
    out['end_ms']=out['start_ms']+width_ms
    out['first_tick_ms']=ts[starts];out['last_tick_ms']=ts[ends-1]
    out['n_ticks']=ends-starts
    for side in ('bid','ask'):
        values=ticks[f'{side}_raw']
        out[f'{side}_o']=values[starts]
        out[f'{side}_c']=values[ends-1]
        out[f'{side}_h']=np.maximum.reduceat(values,starts)
        out[f'{side}_l']=np.minimum.reduceat(values,starts)
    return out


def month_iso_week_rollup(meta: dict) -> dict:
    """PROVISIONAL UTC ISO-week view. Not the user-approved reporting boundary."""
    from collections import defaultdict
    counts=defaultdict(int)
    for day,rows in meta['daily_tick_rows'].items():
        y,w,_=datetime.fromisoformat(day).isocalendar()
        counts[f'{y}-W{w:02d}']+=rows
    return dict(sorted(counts.items()))