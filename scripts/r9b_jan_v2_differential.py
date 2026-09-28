"""January-only differential after H1-origin keyed M15 child-context repair.

Tests true completeness of parent-keyed child join in addition to causality;
previous golden checks detected WRONG attachments but did not catch MISSED
previously-completed source children. Re-selects original raw CAUSAL014 events
strictly chronologically for the four frozen 2026-01 diagnostic masks.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,time
import numpy as np
import r9b_january_fast_parity as Q
import r9b_jan_cached_concordance as S
import r9b_jan_parent_keyed_child_v2 as V

R=Path(__file__).resolve().parent
ORIG=R/'R9B_GAMMA_NET002_007_JAN_EVENT_MAPPING_AUDIT.npz'
FIX=R/'R9B_GAMMA_NET002_007_JAN_PARENT_KEYED_CHILD_V2.npz'
DESC=R/'R9B_GAMMA_NET004_NET005_JAN_DESCRIPTOR_AUDIT.npz'
OLD=R/'R9B_GAMMA_NET002_007_JAN_CACHED_CONCORDANCE.json'
OUT=R/'R9B_GAMMA_NET002_007_JAN_V2_DIFFERENTIAL.json'
MAN=R/'R9B_GAMMA_NET002_007_JAN_V2_DIFFERENTIAL_MANIFEST.json'
FIX_SHA='35e37b0028cf386aaf4107acdd98e2995f3989ea58f465720c74bf0d880e1e08'

def must_fail(name,call):
 try:call()
 except ValueError:return {'name':name,'rejected':True}
 raise AssertionError(f'Failed to reject mutation: {name}')

def require_complete(live,expected,kind):
 if not np.array_equal(live,expected):
  missing=int(np.sum((live<0)&(expected>=0)))
  wrong=int(np.sum((live>=0)&(live!=expected)))
  raise ValueError(f'{kind} incomplete parent-keyed asof: missing={missing}, wrong={wrong}')

def main():
 st=time.perf_counter()
 assert Q.sha(ORIG)==Q.P_SHA and Q.sha(DESC)==Q.D_SHA and Q.sha(FIX)==FIX_SHA
 with np.load(ORIG,allow_pickle=False) as orig,np.load(FIX,allow_pickle=False) as a,np.load(DESC,allow_pickle=False) as d:
  x=a['raw_events'];ex=a['raw_exit'];origix=a['selected_raw_indices'];n=len(x)
  for field in orig.files:
   if field not in ('retest_child_asof_index','retest_child_age_ms','failed_child_asof_index','failed_child_age_ms'):
    assert np.array_equal(orig[field],a[field]),'Immutable source unexpected change '+field
  h=a['h1_owner_bos_asof_index'];t=x[:,0].astype(np.int64)
  rr=a['retest_child_asof_index'];ff=a['failed_child_asof_index']
  cr=a['retest_children'];cf=a['failed_children'];
  expectr,ageR=V.parent_join(t,h,cr,len(a['h1_events']))
  expectf,ageF=V.parent_join(t,h,cf,len(a['h1_events']))
  require_complete(rr,expectr,'retest');require_complete(ff,expectf,'failed')
  assert np.array_equal(ageR,a['retest_child_age_ms'])
  assert np.array_equal(ageF,a['failed_child_age_ms'])
  # Causal-only checks from frozen fast harness, but with V2 child attachments.
  Q.validate(raw=x,ex=ex,indices=origix,h1=h,h4bar=a['h4_completed_bar_index'],
             rr=rr,ff=ff,h1_events=a['h1_events'],childr=cr,childf=cf,
             h4_ends=a['h4_bar_end_ms'],h4_bar_owner=a['h4_bar_owner'],
             net004_at=d['causal014_event_to_net004_row'],
             net004_origin=d['net004_origin_H1_event_index'],
             net004_avail=d['net004_available_ms'])
  # A deliberately missing *valid* child must now fail; old QA did not catch that.
  restoreR=np.flatnonzero((orig['retest_child_asof_index']<0)&(rr>=0));restoreF=np.flatnonzero((orig['failed_child_asof_index']<0)&(ff>=0))
  assert len(restoreR)==695 and len(restoreF)==7152
  wrongR=rr.copy();wrongR[restoreR[0]]=-1
  wrongF=ff.copy();wrongF[restoreF[0]]=-1
  mutants=[must_fail('MISSING_PREVIOUSLY_VISIBLE_RETEST_CHILD',lambda:require_complete(wrongR,expectr,'retest')),
           must_fail('MISSING_PREVIOUSLY_VISIBLE_FAILED_CHILD',lambda:require_complete(wrongF,expectf,'failed'))]
  side=x[:,1].astype(np.int8);h1side=a['h1_owner_side'];h4side=a['h4_owner_side'];
  r_ok=rr>=0;f_ok=ff>=0;rs=np.zeros(n,np.int8);fs=np.zeros(n,np.int8)
  rs[r_ok]=cr[rr[r_ok],2];fs[f_ok]=cf[ff[f_ok],2]
  nh=d['causal014_event_to_net004_row']
  masks={
      'JAN_DEBUG_A0_ALL_RAW':np.ones(n,dtype=bool),
      'JAN_DEBUG_A1_H1_H4_CONCORDANT':(h>=0)&(h1side==side)&(h4side==side),
      'JAN_DEBUG_A2_RETEST_CHILD_MATCH':(h>=0)&r_ok&(h1side==side)&(rs==side),
      'JAN_DEBUG_A3_FAILED_CHILD_SIDE_MATCH':(h>=0)&f_ok&(fs==side),
      'JAN_DEBUG_A4_H1_NET004_PLUS_NONNEUTRAL_H4':(h>=0)&(nh>=0)&(h4side!=0)
  }
  rows=[S.report(k,x,ex,v,origix) for k,v in masks.items()]
  Q.verify_golden(Q.economics(x,ex,Q.greedy(x,ex)))
  earlier=json.loads(OLD.read_text());older={e['id']:e for e in earlier['summary']}
  for row in rows:
   old=older[row['id']]
   row['v1_selected']=old['selected'];row['v1_net']=old['net']
   row['v2_minus_v1_selected']=row['selected']-old['selected']
   row['v2_minus_v1_net']=row['net']-old['net']
   if row['id'] in ('JAN_DEBUG_A0_ALL_RAW','JAN_DEBUG_A1_H1_H4_CONCORDANT','JAN_DEBUG_A4_H1_NET004_PLUS_NONNEUTRAL_H4'):
    assert row['selected']==old['selected'] and row['net']==old['net'], row['id']
  result={'status':'V2_PARENT_KEYED_SOURCE_CORRECTION_AND_JAN_DIFFERENTIAL_PASS',
          'scope':'2026-01 historical reconstruction debug only',
          'raw_source_unmodified':True,'parent_selected_unmodified':True,
          'source_cache_sha256':Q.P_SHA,'corrected_cache_sha256':FIX_SHA,
          'descriptor_source_sha256':Q.D_SHA,
          'restored_child_context':{'retest_raw':len(restoreR),'failed_raw':len(restoreF),
                      'retest_selected':int(np.sum((orig['retest_child_asof_index'][origix]<0)&(rr[origix]>=0))),
                      'failed_selected':int(np.sum((orig['failed_child_asof_index'][origix]<0)&(ff[origix]>=0)))},
          'previously_missing_child_mutants_rejected':mutants,
          'candidate_rows':rows,
          'parent_golden_control':Q.economics(x,ex,origix),
          'interpretation':'Corrects structural eligibility annotation only. A2/A3 are source-context diagnostic screens after the fixed CAUSAL014 generator. All potential independent child actions remain NOT PRICED, historical source win/forward not established. No fitted strategy promoted.',
          'elapsed_seconds':round(time.perf_counter()-st,6),
          'apr_may_jul_not_accessed':True,'august_sealed':True,
          'next':'NET002_NET007_JAN_FAST_PARITY_QUICKSTART_AND_SOURCE_REPAIR_HANDOFF'}
  OUT.write_text(json.dumps(result,indent=2)+'\n')
 MAN.write_text(json.dumps({'status':'COMPLETED_LOCAL_READY_TO_COMMIT',
                           'source_sha256':Q.sha(__file__),
                           'dependency_source_hashes':{'qa':Q.sha(R/'r9b_january_fast_parity.py'),
                                                       'screen':Q.sha(R/'r9b_jan_cached_concordance.py'),
                                                       'v2_join':Q.sha(R/'r9b_jan_parent_keyed_child_v2.py')},
                           'v2_cache_sha256':FIX_SHA,'result_sha256':Q.sha(OUT),
                           'next':result['next'],'august_sealed':True},indent=2)+'\n')
 print(json.dumps({'mutants':mutants,'rows':[{k:v[k] for k in ('id','selected','winners','net','gross_loss','v2_minus_v1_selected','v2_minus_v1_net')} for v in rows],
                   'elapsed_seconds':result['elapsed_seconds'],'result_sha':Q.sha(OUT)},indent=2))

if __name__=='__main__':main()
