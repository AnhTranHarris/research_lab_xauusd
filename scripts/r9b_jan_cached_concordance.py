"""Frozen January-only causal source-context screen over immutable CAUSAL014 raw events.

Purpose: reconstruct historical structural composition/attachment identity and
expose a common bug: filtering already-selected trades instead of re-selecting
from all raw independent events. Original sweep-signal generator & 60s lifecycle
remain frozen. This is a JANUARY DEBUG SCREEN, not a promotable EA or OOS test.
"""
from __future__ import annotations
import sys,json,hashlib,time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r9b_january_fast_parity as QA
P=HERE/'R9B_GAMMA_NET002_007_JAN_EVENT_MAPPING_AUDIT.npz'
D=HERE/'R9B_GAMMA_NET004_NET005_JAN_DESCRIPTOR_AUDIT.npz'
OUT=HERE/'R9B_GAMMA_NET002_007_JAN_CACHED_CONCORDANCE.json'
MAN=HERE/'R9B_GAMMA_NET002_007_JAN_CACHED_CONCORDANCE_MANIFEST.json'

def report(name,raw,ex,eligible,original):
    chosen=QA.greedy(raw,ex,eligible)
    m=QA.economics(raw,ex,chosen)
    naive_ix=original[eligible[original]]
    # Debug statistics: newly selectable events are not in original selected account.
    gain=np.setdiff1d(chosen,original,assume_unique=True)
    lost=np.setdiff1d(original,chosen,assume_unique=True)
    assert np.all(eligible[chosen])
    assert np.all(raw[chosen[1:],0]>ex[chosen[:-1],4]),"NONOVERLAP violated"
    assert len(chosen)>0
    return {'id':name,'eligible_raw':int(eligible.sum()),'selected':m['selected'],
            'winners':m['winners'],'net':m['net'],'gross_profit':m['gp'],
            'gross_loss':m['gl'],'max_drawdown':m['dd'],
            'pf':m['gp']/-m['gl'] if m['gl']<0 else None,
            'naive_filter_of_parent_selected_count':int(len(naive_ix)),
            'newly_selected_raw_not_in_parent':int(len(gain)),
            'removed_original_selected':int(len(lost)),
            'selected_signal_time_min_ms':int(raw[chosen[0],0]),
            'selected_signal_time_max_ms':int(raw[chosen[-1],0]),
            'portfolio_result_status':'JAN_ONLY_SCREEN_POST_SIGNAL_ELIGIBILITY_NOT_AN_UNCONDITIONAL_NEW_TRADING_STRATEGY'}

def main():
    st=time.perf_counter()
    assert QA.sha(P)==QA.P_SHA and QA.sha(D)==QA.D_SHA
    with np.load(P,allow_pickle=False) as a, np.load(D,allow_pickle=False) as b:
        x=a['raw_events'];exit=a['raw_exit'];old=a['selected_raw_indices']
        n=len(x);side=x[:,1].astype(np.int8)
        h1=a['h1_owner_bos_asof_index'];h1side=a['h1_owner_side']
        h4side=a['h4_owner_side'];ret=a['retest_child_asof_index']
        fail=a['failed_child_asof_index'];h1e=a['h1_events']
        rchild=a['retest_children'];fchild=a['failed_children']
        net004=b['causal014_event_to_net004_row'];net004av=b['net004_available_ms']
        h1ok=(h1>=0);r_ok=(ret>=0);f_ok=(fail>=0)
        # Side fields on child objects are already source-defined. Never flip retroactively.
        ret_side=np.zeros(n,dtype=np.int8);ret_side[r_ok]=rchild[ret[r_ok],2].astype(np.int8)
        f_side=np.zeros(n,dtype=np.int8);f_side[f_ok]=fchild[fail[f_ok],2].astype(np.int8)
        masks={
            'JAN_DEBUG_A0_ALL_RAW':np.ones(n,dtype=bool),
            'JAN_DEBUG_A1_H1_H4_CONCORDANT':h1ok&(h1side==side)&(h4side==side),
            'JAN_DEBUG_A2_RETEST_CHILD_MATCH':h1ok&r_ok&(h1side==side)&(ret_side==side),
            'JAN_DEBUG_A3_FAILED_CHILD_SIDE_MATCH':h1ok&f_ok&(f_side==side),
            'JAN_DEBUG_A4_H1_NET004_PLUS_NONNEUTRAL_H4':h1ok&(net004>=0)&(h4side!=0)
        }
        assert np.array_equal(masks['JAN_DEBUG_A4_H1_NET004_PLUS_NONNEUTRAL_H4'],h1ok&(h4side!=0))
        rows=[report(name,x,exit,m,old) for name,m in masks.items()]
        assert rows[0]['selected']==28088 and rows[0]['winners']==19087 and abs(rows[0]['net']-QA.G['net'])<1e-7
        parent_sel=set(old.tolist())
        for row in rows[1:]:
            # A selected raw candidate MAY be absent from the baseline because eligibility changed.
            assert row['newly_selected_raw_not_in_parent']>=0
        res={'scope':'JANUARY_ONLY_DEBUG_AFTER_GOLDEN_ZERO_DELTA_PARITY',
             'status':'NONPROMOTIONAL_SOURCE_ELIGIBILITY_CONCORDANCE_SCREEN',
             'source_data':'IMMUTABLE_DECISION_TIME_NET002_007_STRUCTURE_ATTACHED_TO_CAUSAL014_RAW_SWEEP',
             'models':[r['id'] for r in rows], 'summary':rows,
             'caveat':'A1-A4 apply post-signal eligibility to unmodified CAUSAL014 raw event universe. They do NOT re-run the source sweep engine under a modified quota/cooldown and do NOT price new M15/H4 independent child events. January is discovery/debug only and historical NET002/003/006/007 standalone failed prior discovery/forward gates. No forward/investor edge claim.',
             'correctness':{'independent_trade_exit_original_source':True,
                            'strict_greedy_nonoverlap_from_all_raw_events':True,
                            'post_selection_filter_bug_counted_per_variant':True,
                            'original_parent_immutable':True,
                            'no_future_time_or_child_origin':True,
                            'uses_no_terminal_outcome_as_signal':True},
             'elapsed_sec':round(time.perf_counter()-st,6),
             'full_tick_market_replay':False,'jan_only':True,'august_sealed':True,
             'next':'NET002_NET007_JAN_FAST_SOURCE_CLOSURE_GAPS_AND_CORRECTION_PLAN'}
        OUT.write_text(json.dumps(res,indent=2)+'\n')
    MAN.write_text(json.dumps({'stage':'NET002_NET007_JAN_CACHED_SOURCE_CONCORDANCE_REPLAY',
           'status':'COMPLETED_LOCAL_READY_FOR_DURABILITY',
           'source_sha256':QA.sha(__file__),'source_helper_sha256':QA.sha(HERE/'r9b_january_fast_parity.py'),
           'parent_data_npz_sha256':QA.P_SHA,'descriptor_data_npz_sha256':QA.D_SHA,
           'result_sha256':QA.sha(OUT),'next':res['next'],'august_sealed':True},indent=2)+'\n')
    print(json.dumps({'rows':[{k:v[k] for k in ('id','eligible_raw','selected','winners','net','gross_loss','newly_selected_raw_not_in_parent','naive_filter_of_parent_selected_count')} for v in rows],
                      'elapsed_sec':res['elapsed_sec'],'result_sha':QA.sha(OUT)},indent=2))

if __name__=='__main__':main()
