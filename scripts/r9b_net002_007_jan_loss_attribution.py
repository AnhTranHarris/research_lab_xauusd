"""Descriptive January loss-concentration inventory for source-audited NET002–007 states.

NO fitted trading strategy, no hindsight feature, no portfolio modification.
Trade PnL/exit are used ONLY as outcomes for post-hoc subgroup diagnostics.
Reference CAUSAL014 selected ledger and NET004 source descriptors are immutable.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json
import numpy as np

ROOT=Path('/mnt/data/r9b_research')
ORIG=ROOT/'R9B_GAMMA_NET002_007_JAN_EVENT_MAPPING_AUDIT.npz'
DESC=ROOT/'R9B_GAMMA_NET004_NET005_JAN_DESCRIPTOR_AUDIT.npz'
SUM=ROOT/'R9B_GAMMA_NET002_007_JAN_STRUCTURAL_LOSS_ATTRIBUTION.json'
MAN=ROOT/'R9B_GAMMA_NET002_007_JAN_STRUCTURAL_LOSS_ATTRIBUTION_MANIFEST.json'


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def group(label,mask,pnl,global_m):
    q=np.asarray(pnl)[mask];trades=len(q)
    gp=float(q[q>0].sum());gl=float(q[q<0].sum());net=float(q.sum())
    return {'group':label,'trades':int(trades),'winners':int(np.sum(q>0)),
            'win_rate':float(np.mean(q>0)) if trades else None,
            'net':net,'gross_profit':gp,'gross_loss':gl,
            'profit_factor':float(gp/-gl) if gl<0 else None,
            'trade_share_pct':float(100*trades/len(pnl)),
            'winner_share_pct':float(100*np.sum(q>0)/global_m['winners']),
            'gross_loss_share_pct':float(100*gl/global_m['gross_loss']) if global_m['gross_loss'] else None,
            'NOTE':'SUBGROUP_DIAGNOSTIC_ONLY_NOT_INDEPENDENT_ACCOUNT_OR_TRADE_FILTER'}

def main():
    a=np.load(ORIG,allow_pickle=False);d=np.load(DESC,allow_pickle=False)
    sel=a['selected_raw_indices'];ev=a['raw_events'];ex=a['raw_exit'];p=ex[sel,0]
    assert len(sel)==28088 and len(ev)==34362
    baseline={'trades':int(len(sel)),'winners':int((p>0).sum()),'net':float(p.sum()),
              'gross_profit':float(p[p>0].sum()),'gross_loss':float(p[p<0].sum())}
    assert baseline['winners']==19087 and baseline['net']==-4510.0870000207515
    sides=ev[sel,1].astype(np.int8)
    h1=a['h1_owner_side'][sel];h1idx=a['h1_owner_bos_asof_index'][sel]
    h4=a['h4_owner_side'][sel];h4age=a['h4_owner_age_completed_bars'][sel]
    h1age=a['h1_owner_age_ms'][sel]
    rr=a['retest_child_asof_index'][sel];ff=a['failed_child_asof_index'][sel]
    rawtime=ev[sel,0].astype(np.int64)
    assert not np.any(h1age[h1idx>=0]<0)
    # As-of NET004 row may be present ONLY for the originating H1 bar ID.
    desidx=d['causal014_event_to_net004_row'][sel];des=d['net004_features']
    assert np.array_equal(h1idx>=0,desidx>=0)
    assert np.all(d['net004_origin_H1_event_index'][desidx[desidx>=0]]==h1idx[desidx>=0])
    assert np.all(d['net004_available_ms'][desidx[desidx>=0]]<=rawtime[desidx>=0])
    desc_ok=desidx>=0
    body=np.full(len(p),np.nan)
    body[desc_ok]=des[desidx[desc_ok],1]
    strength=np.full(len(p),np.nan)
    strength[desc_ok]=des[desidx[desc_ok],0]
    # Disjoint source-defined ownership cohorts: no strategy tuning or direction flip.
    cohorts={
      'H1_MATCH':(h1idx>=0)&(h1==sides),
      'H1_OPPOSE':(h1idx>=0)&(h1==-sides),
      'H1_MISSING':(h1idx<0),
      'H4_MATCH':(h4==sides),
      'H4_OPPOSE':(h4==-sides),
      'H4_NEUTRAL':(h4==0),
      'H1H4_BOTH_MATCH':(h1==sides)&(h4==sides),
      'H1H4_BOTH_OPPOSE':(h1==-sides)&(h4==-sides),
      'H1_MATCH_H4_OPPOSE':(h1==sides)&(h4==-sides),
      'H1_OPPOSE_H4_MATCH':(h1==-sides)&(h4==sides),
      'H1_OWNER_AGE_LE_1H':(h1idx>=0)&(h1age<=3600000),
      'H1_OWNER_AGE_1H_TO_4H':(h1idx>=0)&(h1age>3600000)&(h1age<=4*3600000),
      'H1_OWNER_AGE_4H_TO_12H':(h1idx>=0)&(h1age>4*3600000)&(h1age<=12*3600000),
      'H1_OWNER_AGE_GT_12H':(h1idx>=0)&(h1age>12*3600000),
      'H4_OWNER_AGE_LE_2_BARS':(h4!=0)&(h4age<=2),
      'H4_OWNER_AGE_GT_2_BARS':(h4!=0)&(h4age>2),
      'RETEST_CONTEXT_ONLY':(rr>=0)&(ff<0),
      'FAILURE_CONTEXT_ONLY':(ff>=0)&(rr<0),
      'BOTH_RETEST_AND_FAILURE_CONTEXT':(rr>=0)&(ff>=0),
      'NEITHER_CHILD_CONTEXT':(rr<0)&(ff<0),
      'NET004_BODY_FRAC_LE_025':desc_ok&(body<=0.25),
      'NET004_BODY_FRAC_GT_025':desc_ok&(body>0.25),
      'NET004_BREAK_STRENGTH_LE_05_ATR':desc_ok&(strength<=0.5),
      'NET004_BREAK_STRENGTH_GT_05_ATR':desc_ok&(strength>0.5),
    }
    # Partition/accounting checks for each disjoint comparison family.
    def part(*labels):
        masks=[cohorts[x] for x in labels]
        assert np.all(np.sum(np.array(masks,dtype=np.int8),axis=0)==1),('Not a partition',labels)
        assert sum(int(mask.sum()) for mask in masks)==len(p)
    part('H1_MATCH','H1_OPPOSE','H1_MISSING')
    part('H4_MATCH','H4_OPPOSE','H4_NEUTRAL')
    part('RETEST_CONTEXT_ONLY','FAILURE_CONTEXT_ONLY','BOTH_RETEST_AND_FAILURE_CONTEXT','NEITHER_CHILD_CONTEXT')
    combined_gp=sum(group(k,cohorts[k],p,baseline)['gross_profit'] for k in ('H1_MATCH','H1_OPPOSE','H1_MISSING'))
    combined_gl=sum(group(k,cohorts[k],p,baseline)['gross_loss'] for k in ('H1_MATCH','H1_OPPOSE','H1_MISSING'))
    assert np.isclose(combined_gp,baseline['gross_profit'],atol=1e-8)
    assert np.isclose(combined_gl,baseline['gross_loss'],atol=1e-8)
    allgroups=[group(k,v,p,baseline) for k,v in cohorts.items()]
    out={'unit':'NET002_NET007_JAN_STRUCTURAL_COMPOSITION_LOSS_ATTRIBUTION_DIAGNOSTIC',
         'status':'POSTHOC_DIAGNOSTIC_ONLY_NOT_ALPHA_AND_NOT_A_NEW_PORTFOLIO',
         'parent_npz_sha256':sha(ORIG),'descriptor_npz_sha256':sha(DESC),
         'parent_summary':baseline,'causal_join_validation':'PASS_SOURCE_BOS_IDS_AND_COMPLETED_TIMESTAMPS',
         'categories':'source-time causal descriptors, terminal outcomes only in AFTER-THE-FACT diagnostics',
         'mutual_exclusion_checks':'PASS_H1_DIRECTION_H4_DIRECTION_CHILD_CONTEXT',
         'metrics':allgroups,
         'no_raw_entry_exit_changes':True,
         'no_historical_profit_claim':True,
         'interpretation_rules':[
             'This is JANUARY ONLY. Never treat subgroup returns as independent strategies or out-of-sample confirmation.',
             'Gross-loss shares are ex-post contribution descriptions, not forecasts or immediately promotable filters.',
             'All future child-state context must remain tied to original H1 BOS ID and first available M15 close.',
             'Any optional gating, routing or separate child trade requires a new frozen state-machine contract and one chronological portfolio replay.',
             'NET005 source-grid point is not a recovered historical frozen strategy.',
             'August stays SEALED.'
         ],'next':'NET002_NET007_HISTORICAL_COMBINATION_IDENTITY_AND_COMPLEMENTARITY_PREDECLARATION',
         'august_sealed':True,'production_mql5_authorized':False}
    SUM.write_text(json.dumps(out,indent=2)+'\n')
    man={'status':'COMPLETED_LOCAL_NON_PROMOTIONAL','unit':out['unit'],
         'source_sha256':sha(__file__),'source_dependency_sha256':{'parent':sha(ORIG),'net004':sha(DESC)},
         'result_sha256':sha(SUM),'next':out['next'],'august_sealed':True,
         'completed_utc':datetime.now(timezone.utc).isoformat()}
    MAN.write_text(json.dumps(man,indent=2)+'\n')
    print('LOSS_ATTRIBUTION_COMPLETE',json.dumps({'parent':baseline,'groups':[{k:r[k] for k in ('group','trades','winners','net','gross_loss','gross_loss_share_pct')} for r in allgroups], 'result_sha256':sha(SUM)}))

if __name__=='__main__':main()
