"""NET023 chronological integration of CAUSAL014 + parity-certified NET022.

Scientific contract:
- Actual Dukascopy tick chronology and bid/ask execution.
- CAUSAL014 raw event engine continues while portfolio is occupied.
- NET022 H1 event engine continues independently while portfolio is occupied.
- One live portfolio position total.
- Strict first-eligible, no preemption.
- Event/entry timestamp <= current free timestamp is blocked.
- Exact entry-timestamp ties are awarded to CAUSAL014 parent.
- No arithmetic sleeve-PnL addition.

Dependencies are frozen in scripts/causal014/.
"""
import sys,time,json,hashlib,glob,os
from pathlib import Path
import numpy as np, pandas as pd

HERE=Path(__file__).resolve().parent
HELPERS=HERE/'causal014'
sys.path.insert(0,str(HELPERS))
DATA_ROOT=Path(os.environ.get('R9B_DATA_ROOT','/mnt/data'))
OUT=Path(os.environ.get('R9B_NET023_OUT',str(DATA_ROOT/'net023_integrated')))
OUT.mkdir(parents=True,exist_ok=True)

import r9b_screen as R
import r9b_r8_recert as B
import r8_sweep_lifecycle_screen as S
from r9b_sweep_structure_exit_candidate import replay_hybrid

NET022_TARGET={
1:(17,12,237.675,3.4331),2:(19,9,99.301,1.3341),3:(14,7,160.296,1.5011),
4:(18,11,274.255,2.9176),5:(19,8,5.965,1.02287),6:(17,10,175.842,1.8968),
7:(21,9,88.95,1.48227)}
CAUSAL_TARGET={
1:(28088,19087,-4510.0870000207515),2:(28188,18834,-4450.956500020821),
3:(35573,24169,-6589.631500026144),4:(26683,18068,-4735.74550001993),
5:(25525,17412,-4425.295500019026),6:(27710,18828,-5345.316000013228),
7:(25807,16744,-5342.881000002722)}

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def metric(pnl):
    x=np.asarray(pnl,float); n=len(x)
    gp=float(x[x>0].sum()) if n else 0.; gl=float(x[x<0].sum()) if n else 0.
    eq=np.cumsum(x)
    peak=np.maximum.accumulate(np.r_[0.,eq])[:-1] if n else np.array([])
    dd=float((peak-eq).max()) if n else 0.
    return {'trades':int(n),'winners':int((x>0).sum()),
            'win_rate':float((x>0).mean()) if n else 0.,
            'net':float(x.sum()) if n else 0.,
            'gross_profit':gp,'gross_loss':gl,
            'pf':float(gp/-gl) if gl<0 else None,'maxdd':dd}

def agg_h1(t,mid):
    ms=3_600_000; key=t//ms
    st=np.r_[0,np.where(key[1:]!=key[:-1])[0]+1]
    en=np.r_[st[1:]-1,len(key)-1]
    return key[st],mid[st],np.maximum.reduceat(mid,st),np.minimum.reduceat(mid,st),mid[en]

def net022_raw_quotes(t,ask,bid,mid):
    key,o,h,l,c=agg_h1(t,mid); n=len(key)
    rng=h-l; body=np.abs(c-o); bf=np.divide(body,rng,out=np.zeros(n),where=rng>0)
    prevc=np.r_[o[0],c[:-1]]
    tr=np.maximum(h-l,np.maximum(np.abs(h-prevc),np.abs(l-prevc)))
    atr=np.full(n,np.nan)
    for i in range(3,n): atr[i]=np.mean(tr[max(0,i-13):i+1])
    end=(key+1)*3_600_000
    out=[]
    for i in range(14,n):
        if not np.isfinite(atr[i]): continue
        top=np.maximum(o[i-13:i],c[i-13:i]); bot=np.minimum(o[i-13:i],c[i-13:i])
        up=float(np.max(top)); dn=float(np.min(bot))
        side=1 if ((c[i]>up+0.1*atr[i]) and (c[i]>o[i])) else (-1 if ((c[i]<dn-0.1*atr[i]) and (c[i]<o[i])) else 0)
        if not side: continue
        ref=float(np.median(rng[i-13:i]))
        if not ref>0: continue
        comp=float(np.mean(rng[i-2:i])/ref); sigrr=float(rng[i]/ref)
        if not (comp<=1.0 and sigrr>=1.0 and bf[i]>=0.25): continue
        j=int(np.searchsorted(t,end[i],side='left'))
        q=int(np.searchsorted(t,end[i]+8*3_600_000,side='left'))
        if j>=len(t) or q>=len(t): continue
        entry=float(ask[j] if side>0 else bid[j])
        exit_px=float(bid[q] if side>0 else ask[q])
        pnl=(exit_px-entry)*side
        out.append((int(t[j]),int(t[q]),int(side),float(pnl),int(end[i]),comp,sigrr,float(bf[i])))
    return np.array(out,dtype=[
        ('entry_ms','i8'),('exit_ms','i8'),('side','i1'),('pnl','f8'),
        ('signal_end_ms','i8'),('compression_ratio','f8'),
        ('signal_range_ratio','f8'),('body_fraction','f8')])

def select_one(entries,exits,pnl,priority=None):
    pri=priority if priority is not None else np.zeros(len(entries),int)
    order=np.lexsort((pri,entries))
    keep=[]; free=-1
    for q in order:
        if int(entries[q])<=free or not np.isfinite(pnl[q]): continue
        keep.append(int(q)); free=int(exits[q])
    return np.asarray(keep,np.int64)

def run(month):
    started=time.time()
    t,mid=R.load_ticks(month)
    path=sorted(glob.glob(str(DATA_ROOT/f'XAUUSD_DUKAS_2026_{month:02d}_ticks*.gz')))[0]
    d=pd.read_csv(path,usecols=['ask_raw','bid_raw'],dtype={'ask_raw':'int64','bid_raw':'int64'})
    ask=d.ask_raw.to_numpy(np.float64)/1000.; bid=d.bid_raw.to_numpy(np.float64)/1000.; del d

    sec_ids,first_t,oo,hh,ll,cc,first_ix,last_ix=R.active_seconds(t,mid)
    e5,r5,a5=R.aggregate_tf_from_ticks(t,mid,300); atr=R.map_completed(sec_ids,e5,a5)
    al=np.zeros(len(sec_ids),np.int8); ash=np.zeros(len(sec_ids),np.int8)
    for tf in (60,180,300,600,1200):
        ee,ret,aa=R.aggregate_tf_from_ticks(t,mid,tf)
        rr=R.map_completed(sec_ids,ee,ret); aaa=R.map_completed(sec_ids,ee,aa)
        ok=np.isfinite(aaa); al+=((rr>0)&ok).astype(np.int8); ash+=((rr<0)&ok).astype(np.int8)
    su,hi,lo,cl=B.build_sec(t,mid)
    X=S.sweep_signals(t,mid,su,hi,lo,cl,sec_ids,atr,al,ash)
    O=replay_hybrid(t,mid,X)
    c_entry=X[:,0].astype(np.int64)
    c_pnl=O[:,0].astype(float)
    c_exit=np.where(np.isfinite(O[:,4]),O[:,4],-1).astype(np.int64)

    ci=select_one(c_entry,c_exit,c_pnl)
    cm=metric(c_pnl[ci]); ct=CAUSAL_TARGET[month]
    assert cm['trades']==ct[0] and cm['winners']==ct[1] and abs(cm['net']-ct[2])<1e-8

    N=net022_raw_quotes(t,ask,bid,mid)
    ni=select_one(N['entry_ms'],N['exit_ms'],N['pnl'])
    nm=metric(N['pnl'][ni]); nt=NET022_TARGET[month]
    assert nm['trades']==nt[0] and nm['winners']==nt[1]
    assert abs(nm['net']-nt[2])<1e-8 and abs(nm['pf']-nt[3])<5e-5

    entries=np.concatenate([c_entry,N['entry_ms']])
    exits=np.concatenate([c_exit,N['exit_ms']])
    pnl=np.concatenate([c_pnl,N['pnl']])
    source=np.concatenate([np.zeros(len(c_entry),np.int8),np.ones(len(N),np.int8)])
    valid=np.isfinite(pnl)&(exits>=0)
    base=np.where(valid)[0]
    selected=base[select_one(entries[base],exits[base],pnl[base],priority=source[base])]
    sm=metric(pnl[selected])
    sel_src=source[selected]

    attribution={}
    for sv,name in [(0,'CAUSAL014'),(1,'NET022')]:
        attribution[name]=metric(pnl[selected][sel_src==sv])

    out_path=OUT/f'NET023_INTEGRATED_2026_{month:02d}.npz'
    np.savez_compressed(out_path,entry_ms=entries[selected].astype(np.int64),
                        exit_ms=exits[selected].astype(np.int64),
                        source=sel_src.astype(np.int8),pnl=pnl[selected].astype(float))

    standalone_entries=set(map(int,N['entry_ms'][ni]))
    integrated_entries=set(map(int,entries[selected][sel_src==1]))
    result={
        'unit':'R9B_GAMMA_DYNAMIC_NET_023_INTEGRATED_LEDGER',
        'month':month,'status':'MONTH_RECONSTRUCTED',
        'arbitration':'strict chronological first-eligible; no preemption; parent CAUSAL014 wins exact timestamp ties; one position total; candidate event engines continue independently while portfolio busy',
        'causal014_standalone':cm,'net022_standalone':nm,'integrated':sm,
        'attribution':attribution,'net022_raw_candidates':int(len(N)),
        'net022_standalone_selected':int(len(ni)),
        'net022_integrated_selected':int((sel_src==1).sum()),
        'net022_standalone_entries_retained_in_integration':int(len(standalone_entries & integrated_entries)),
        'delta_vs_causal014':{
            'net':sm['net']-cm['net'],
            'gross_profit':sm['gross_profit']-cm['gross_profit'],
            'gross_loss_improvement':sm['gross_loss']-cm['gross_loss'],
            'trades':sm['trades']-cm['trades'],
            'winners':sm['winners']-cm['winners'],
            'maxdd_improvement':cm['maxdd']-sm['maxdd']},
        'ledger_sha256':sha(out_path),'august_accessed':False,
        'elapsed_s':time.time()-started}
    json_path=OUT/f'NET023_INTEGRATED_2026_{month:02d}.json'
    json_path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__': run(int(sys.argv[1]))
