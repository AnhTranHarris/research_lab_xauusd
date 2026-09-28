"""Fix a forensic source-context bug without rerunning January raw ticks.

Original v1 made a GLOBAL as-of join to the latest M15 retest/failure
child, then blanked any result whose H1 BOS parent did not match the
current BOS. When older BOS children complete after newer BOS child
states, this erroneously drops the correctly attached earlier child.

Correct v2 joins the FIRST source child in each H1 BOS parent directly
by original parent key, then separately validates time <= raw tick.
Children are context-only; original CAUSAL014 signals/exits and account
are byte-for-byte identical. No new strategy or April-August data used.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,time
import numpy as np

R=Path(__file__).resolve().parent
IN=R/'R9B_GAMMA_NET002_007_JAN_EVENT_MAPPING_AUDIT.npz'
OUT=R/'R9B_GAMMA_NET002_007_JAN_PARENT_KEYED_CHILD_V2.npz'
RES=R/'R9B_GAMMA_NET002_007_JAN_PARENT_KEYED_CHILD_V2_SUMMARY.json'
MAN=R/'R9B_GAMMA_NET002_007_JAN_PARENT_KEYED_CHILD_V2_MANIFEST.json'
EXPECTED='3fa88617bcc157ec4e6fcc2e62d48f888d93c380c8d18d1f2c79fcd4cc69ce6a'

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def parent_join(event_t,cur_parent,children,nparent):
 """First-event-by-source-parent join; no global newest-child interference."""
 by_parent=np.full(nparent,-1,np.int32)
 for i,c in enumerate(children):
  parent=int(c[1]);assert 0<=parent<nparent
  assert by_parent[parent]<0,'Source must emit FIRST child per H1 BOS'
  by_parent[parent]=i
 ans=np.full(len(event_t),-1,np.int32);valid_parent=cur_parent>=0
 ans[valid_parent]=by_parent[cur_parent[valid_parent]]
 valid=ans>=0
 # Candidate can only be used after it is visible at the completed M15 close.
 ans[valid&(children[np.maximum(ans,0),0]>event_t)]=-1
 age=np.zeros(len(event_t),np.int64);good=ans>=0
 age[good]=event_t[good]-children[ans[good],0]
 assert np.all(age[good]>=0)
 assert np.array_equal(children[ans[good],1],cur_parent[good])
 assert np.all(children[ans[good],0]<=event_t[good])
 return ans,age

def economics(raw,ex,ix):
 p=ex[ix,0];return {'raw_events':len(raw),'selected':len(ix),
  'winners':int(np.sum(p>0)),'net':float(p.sum()),
  'gross_profit':float(p[p>0].sum()),'gross_loss':float(p[p<0].sum())}

def main():
 st=time.perf_counter()
 assert sha(IN)==EXPECTED,'source cache not exact'
 with np.load(IN,allow_pickle=False) as a:
  arrays={key:a[key] for key in a.files}
 raw=arrays['raw_events'];ex=arrays['raw_exit'];sel=arrays['selected_raw_indices']
 t=raw[:,0].astype(np.int64);bos=arrays['h1_owner_bos_asof_index'];nparent=len(arrays['h1_events'])
 stats={}
 for kind,name,age in [('retest','retest_child_asof_index','retest_child_age_ms'),
                      ('failed','failed_child_asof_index','failed_child_age_ms')]:
  c=arrays['retest_children'] if kind=='retest' else arrays['failed_children']
  prev=arrays[name]
  fix,fixage=parent_join(t,bos,c,nparent)
  # Existing positive links were valid, but global newest-child incorrectly
  # erased previous valid source parent states; this is an UNDERCOUNT fix.
  assert np.all(fix[prev>=0]==prev[prev>=0]), 'Existing links unexpectedly remapped'
  add=(prev<0)&(fix>=0)
  assert np.sum((prev>=0)&(fix<0))==0
  stats[kind]={
     'previous_raw_attached':int(np.sum(prev>=0)),
     'corrected_raw_attached':int(np.sum(fix>=0)),
     'restored_raw_links':int(add.sum()),
     'previous_selected_attached':int(np.sum(prev[sel]>=0)),
     'corrected_selected_attached':int(np.sum(fix[sel]>=0)),
     'restored_selected_links':int(np.sum(add[sel])),
     'false_existing_link_count':0,
     'negative_age_count':int(np.sum(fixage[fix>=0]<0)),
     'first_corrected_raw_event_ms':int(t[np.flatnonzero(add)[0]]) if np.any(add) else None}
  arrays[name]=fix;arrays[age]=fixage
 assert len(raw)==34362 and len(sel)==28088
 metrics=economics(raw,ex,sel)
 assert metrics['winners']==19087 and abs(metrics['net']+4510.0870000207515)<1e-8
 np.savez_compressed(OUT,**arrays)
 with np.load(OUT,allow_pickle=False) as re:
  # Immutable source arrays have IDENTICAL content, including float bits.
  for key in ['raw_events','raw_exit','selected_raw_indices','h1_owner_bos_asof_index',
              'h1_owner_side','h4_owner_side','h4_completed_bar_index','h4_bar_owner',
              'h1_events','retest_children','failed_children']:
   assert np.array_equal(re[key], arrays[key]), key
  assert re['retest_child_asof_index'].shape==(34362,)
 summary={'stage':'NET002_NET007_JAN_PARENT_KEYED_CHILD_ASOF_CORRECTION_V2',
    'status':'JANUARY_CAUSAL_MAPPING_CORRECTION_EXACT_ZERO_DELTA_PARENT',
    'root_cause':'global-latest-child-asof-then-discard-wrong-BOS falsely hides earlier visible child of current BOS',
    'source_parent_cache_sha256':EXPECTED,'output_source_npz_sha256':sha(OUT),
    'original_parent_economics_unchanged':metrics,
    'child_fixes':stats,
    'source_eligibility_semantics':'first completed M15 child for each originating H1 BOS, visible only at or after child M15 bar end, current BOS parent ID must match',
    'no_execution_changes':True,'no_new_trade_approval':True,
    'jan_month_only':True,'august_sealed':True,
    'elapsed_seconds':round(time.perf_counter()-st,6),
    'next':'NET002_NET007_JAN_V2_FAST_DIFFERENTIAL_REPLAY'}
 RES.write_text(json.dumps(summary,indent=2)+'\n')
 man={'status':'COMPLETED_LOCAL_SOURCE_MAPPING_CORRECTION','stage':summary['stage'],
      'source_sha256':sha(__file__),'parent_cache_sha256':EXPECTED,
      'output_cache_sha256':sha(OUT),'summary_sha256':sha(RES),
      'next':summary['next'],'completed_utc':datetime.now(timezone.utc).isoformat(),
      'august_sealed':True}
 MAN.write_text(json.dumps(man,indent=2)+'\n')
 print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
