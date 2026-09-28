"""Historical January NET004/NET005 source identity and descriptor observability audit.
No PnL labels are used as live features. Prior CAUSAL014+NET002/3/6/7 NPZ is immutable.
Historical original NET002-005 result JSON files are incomplete 1000-line copies:
no claim of recovering historical frozen NET005 parameter selection is made.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
import r9b_net002_007_jan_asof_mapping as parent

ROOT=Path('/mnt/data/r9b_research')
ORIG=ROOT/'R9B_GAMMA_NET002_007_JAN_EVENT_MAPPING_AUDIT.npz'
OUTPUT=ROOT/'R9B_GAMMA_NET004_NET005_JAN_DESCRIPTOR_AUDIT.npz'
SUMMARY=ROOT/'R9B_GAMMA_NET004_NET005_JAN_DESCRIPTOR_SUMMARY.json'
MAN=ROOT/'R9B_GAMMA_NET004_NET005_JAN_DESCRIPTOR_MANIFEST.json'
FEATURE_NAMES=['break_strength_atr','body_frac','close_location','adverse_wick_frac','atr_ratio','eff3','eff6','h1_align3','h1_align6','m15_align4','m15_align8','m15_conflict4','m15_conflict8','m15_eff4','m15_eff8']


def eff(c,n,i):
    if i<n:return np.nan
    d=np.diff(c[i-n:i+1]);den=float(np.sum(np.abs(d)))
    return float(abs(c[i]-c[i-n])/(den+1e-12))


def build_004(H,M,bos):
    """Exact NET004 observable feature definitions, NO future 8h target/PnL."""
    o=H['o'];hi=H['h'];lo=H['l'];c=H['c'];atr=H['atr'];end=H['end']
    mend=M['end']; mc=M['c'];X=[];T=[];S=[];parentidx=[];coverage=[]
    for k,(e,side,bound,a,i) in enumerate(bos):
        i=int(np.searchsorted(end,int(e)))
        if i>=len(end) or end[i]!=int(e) or not np.isfinite(a) or a<=0:continue
        rng=max(float(hi[i]-lo[i]),1e-12)
        br=float(side*(c[i]-bound)/a);body=float(abs(c[i]-o[i])/rng)
        cl=float((c[i]-lo[i])/rng if side>0 else (hi[i]-c[i])/rng)
        aw=float((c[i]-lo[i])/rng if side<0 else (hi[i]-c[i])/rng)
        trs=[]
        for j in range(max(1,i-13),i+1):
            trs.append(max(hi[j]-lo[j],abs(hi[j]-c[j-1]),abs(lo[j]-c[j-1])))
        med=float(np.median(trs)) if trs else np.nan
        ar=float(a/(med+1e-12));e3=eff(c,3,i);e6=eff(c,6,i)
        a3=float(np.mean(side*np.diff(c[i-3:i+1])>0)) if i>=3 else np.nan
        a6=float(np.mean(side*np.diff(c[i-6:i+1])>0)) if i>=6 else np.nan
        j=np.searchsorted(mend,int(e),side='right')-1
        vals=[]
        for n in (4,8):
            if j<n:vals += [np.nan,np.nan]
            else:
                d=np.diff(mc[j-n:j+1]);align=float(np.mean(side*d>0));conf=float(np.mean(side*d<0));vals += [align,conf]
        me=[]
        for n in (4,8):
            if j<n:me.append(np.nan)
            else:
                d=np.diff(mc[j-n:j+1]);me.append(float(abs(mc[j]-mc[j-n])/(np.sum(np.abs(d))+1e-12)))
        x=[br,body,cl,aw,ar,e3,e6,a3,a6,vals[0],vals[2],vals[1],vals[3],me[0],me[1]]
        assert (j<0 or mend[j]<=e),('M15 future leak',e,j,mend[j])
        assert end[i]==e
        X.append(x);T.append(e);S.append(side);parentidx.append(k);coverage.append((int(i),int(j)))
    return np.asarray(X,dtype=np.float64),np.asarray(T,np.int64),np.asarray(S,np.int8),np.asarray(parentidx,np.int32),np.asarray(coverage,np.int32)


def independent_h4_event_stream(H,n=13,buf=.10,bodymin=.25):
    """NET005 source grid point (not claimed to be the historical frozen candidate)."""
    o=H['o'];h=H['h'];l=H['l'];c=H['c'];atr=H['atr'];bf=H['bf'];end=H['end']
    rows=[]
    for i in range(max(n,14),len(c)):
        if not np.isfinite(atr[i]) or atr[i]<=0:continue
        top=np.maximum(o[i-n:i],c[i-n:i]);bot=np.minimum(o[i-n:i],c[i-n:i]);up=np.max(top);dn=np.min(bot)
        side=1 if c[i]>up+buf*atr[i] and c[i]>o[i] and bf[i]>=bodymin else (-1 if c[i]<dn-buf*atr[i] and c[i]<o[i] and bf[i]>=bodymin else 0)
        if side:rows.append((int(end[i]),int(side),int(i)))
    return np.asarray(rows,dtype=np.int64).reshape(-1,3)


def main():
    assert parent.digest(parent.DATA)==parent.EXPECTED_SHA
    before=parent.digest(ORIG)
    a=np.load(ORIG,allow_pickle=False)
    Xraw=a['raw_events'];O=a['raw_exit'];ix=a['selected_raw_indices'];bosarr=a['h1_events']
    assert len(Xraw)==34362 and len(ix)==28088
    assert parent.metrics(O[ix,0])['net']==-4510.0870000207515
    h1idx=a['h1_owner_bos_asof_index'];h4idx=a['h4_completed_bar_index']
    rawtimes=Xraw[:,0].astype(np.int64)
    # Existing mapping must already have removed stale child identity mismatches.
    for child,childstr in [('retest_child_asof_index','retest_children'),('failed_child_asof_index','failed_children')]:
        j=a[child];yes=j>=0
        assert np.all(a[childstr][j[yes],1]==h1idx[yes]),'Source BOS link disagreement'
    t,mid=parent.raw();H=parent.structural_bars(t,mid,60);M=parent.structural_bars(t,mid,15);H4=parent.structural_bars(t,mid,240)
    bos=parent.h1_bos(H)
    assert np.array_equal(np.asarray(bos,float).reshape(-1,5),bosarr),'h1 source event population changed'
    X,T,S,srcid,srcbar=build_004(H,M,bos)
    assert len(X)==len(bos)==108 and X.shape==(108,15)
    # Map NET004 descriptors by exact source BOS identity, not guessed timestamp proximity.
    idx=np.full(len(Xraw),-1,dtype=np.int32)
    mapped=np.searchsorted(srcid,h1idx,side='left')
    ok=(h1idx>=0)&(mapped<len(srcid))
    if np.any(ok):
        ids=mapped[ok];keep=srcid[ids]==h1idx[ok]
        tmp=np.full(int(ok.sum()),-1,dtype=np.int32);tmp[keep]=ids[keep]
        idx[ok]=tmp
    valid=idx>=0
    assert np.all(T[idx[valid]]<=rawtimes[valid]),'NET004 feature future visible!'
    # Net005 H4 BOS independently forms a different event population; it is not a CAUSAL014 entry.
    h4event=independent_h4_event_stream(H4)
    h4last,_=parent.attach_asof(rawtimes,h4event.tolist())
    h4valid=h4last>=0
    assert not np.any(h4event[h4last[h4valid],0]>rawtimes[h4valid])
    # Same-timestamp candidate coincidence, not identity, should be counted explicitly.
    exact_h1_coincidence=int(np.isin(T,rawtimes).sum());exact_h4_coincidence=int(np.isin(h4event[:,0],rawtimes).sum()) if len(h4event) else 0
    source_004_nan=int(np.isnan(X).sum())
    assert not np.any(~np.isfinite(X)),'NET004 source feature unexpectedly nonfinite'
    assert before==parent.digest(ORIG),'Parent audit immutable'
    np.savez_compressed(OUTPUT,net004_feature_names=np.asarray(FEATURE_NAMES,'U40'),net004_features=X,
                        net004_origin_H1_event_index=srcid,net004_available_ms=T,net004_side=S,
                        net004_source_bar_indexes=srcbar,causal014_event_to_net004_row=idx,
                        net005_sample_independent_h4_raw_events=h4event,
                        causal014_net005_asof_index=h4last)
    summary={
        'unit':'NET002_NET007_JAN_SOURCE_EVENT_IDENTITY_AUDIT_AND_NET004_DESCRIPTORS',
        'status':'VERIFIED_LOCAL_DESCRIPTIVE_SOURCE_ONLY',
        'january_parent_audit_sha256':before,'parent_source_sha256':parent.digest(parent.__file__),
        'input_sha256':parent.EXPECTED_SHA,
        'net004_source_blob':'2fb13845d4a1ec8033619eeb55c791941dd27935',
        'net005_source_blob':'44b9863cad02e9f59ede350e142b220e32ea2934',
        'net004_feature_names':FEATURE_NAMES,'net004_bos_rows':int(len(X)),
        'net004_total_nonfinite':source_004_nan,
        'causal014_raw_events':int(len(Xraw)),
        'causal014_with_net004_exact_origin':int(valid.sum()),
        'causal014_with_net004_missing':int((~valid).sum()),
        'net005_h4_raw_BOS_events_under_nonfrozen_source_grid_point':int(len(h4event)),
        'net005_grid_point':{'h4_completed_lookback':13,'body_min':0.25,'atr_break_buffer':0.10,'boundary':'body','note':'SOURCE GRID POINT ONLY; historical frozen candidate not recoverable from incomplete old JSON'},
        'raw_events_with_any_prior_net005_candidate':int(h4valid.sum()),
        'exact_h1_vs_ca014_raw_signal_time_coincidence':exact_h1_coincidence,
        'exact_h4_vs_ca014_raw_signal_time_coincidence':exact_h4_coincidence,
        'source_feature_future_violations':0,'event_identity_action':'NONE; no order and no standalone PnL added',
        'january_control_metrics_unchanged':parent.metrics(O[ix,0]),
        'replay_cost':'modeled halfspread 0.10 side; no variable broker spread certification',
        'august_accessed':False,'production_mql5_authorized':False,
        'audit_npz_sha256':parent.digest(OUTPUT)
    }
    SUMMARY.write_text(json.dumps(summary,indent=2)+'\n')
    manifest={'unit':summary['unit'],'status':'COMPLETED_LOCAL_PARITY_VERIFIED',
              'code_sha256':parent.digest(__file__),'source_dependencies_sha256':{'jan_parent_script':parent.digest(parent.__file__),'jan_parent_npz':before},
              'summary_sha256':parent.digest(SUMMARY),'audit_npz_sha256':parent.digest(OUTPUT),
              'input_sha256':parent.EXPECTED_SHA,'next':'NET002_NET007_HISTORICAL_COMBINATION_IDENTITY_AND_COMPLEMENTARITY_PREDECLARATION',
              'completed_utc':datetime.now(timezone.utc).isoformat(),'august_sealed':True,'no_alpha_promotion':True}
    MAN.write_text(json.dumps(manifest,indent=2)+'\n')
    print('DESCRIPTOR_AUDIT_COMPLETE '+json.dumps(summary),flush=True)

if __name__=='__main__':main()
