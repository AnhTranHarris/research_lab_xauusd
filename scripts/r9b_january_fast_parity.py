"""January-only source/golden parity gate for legacy NET002-007 reconstruction.

This is a FAST DEBUG HARNESS, not a new trading strategy and not a market test.
It consumes frozen source-exact January event arrays, never reads April-July
or August, and only allows real-tick repricing in a separate new stage.
"""
from __future__ import annotations
import hashlib, json, time, sys
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parent
P=R/'R9B_GAMMA_NET002_007_JAN_EVENT_MAPPING_AUDIT.npz'
D=R/'R9B_GAMMA_NET004_NET005_JAN_DESCRIPTOR_AUDIT.npz'
OUT=R/'R9B_GAMMA_NET002_007_JAN_FAST_PARITY.json'
MAN=R/'R9B_GAMMA_NET002_007_JAN_FAST_PARITY_MANIFEST.json'
P_SHA='3fa88617bcc157ec4e6fcc2e62d48f888d93c380c8d18d1f2c79fcd4cc69ce6a'
D_SHA='ac5c996d1b8126906a2ca2f17af26614737d7c24ab3dfeb4beefb5fbb8a96567'
G={'raw':34362,'selected':28088,'winners':19087,
   'net':-4510.0870000207515,'gp':7001.463999985857,
   'gl':-11511.55100000661,'dd':4554.885500020489}

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()

def ensure(condition,why):
    if not bool(condition):raise ValueError(why)

def greedy(raw,ex,eligible=None):
    """Source-equivalent strict chronological one-position selection, NOT post-selection filtering."""
    if eligible is None:eligible=np.ones(len(raw),bool)
    ensure(eligible.shape==(len(raw),),'eligible shape')
    order=np.argsort(raw[:,0]);chosen=[];free=-1
    for q in order:
        # Condition is raw signal timestamp strictly AFTER selected prior exit.
        if not eligible[q] or raw[q,0]<=free or not np.isfinite(ex[q,0]):continue
        chosen.append(int(q));free=int(ex[q,4])
    return np.array(chosen,dtype=np.int64)

def economics(raw,ex,indices):
    v=ex[indices,0]
    gp=float(v[v>0].sum());gl=float(v[v<0].sum())
    eq=np.cumsum(v)
    pk=np.maximum.accumulate(np.r_[0.,eq])[:-1] if len(v) else np.array([])
    return {'raw':int(len(raw)),'selected':int(len(indices)),
            'winners':int(np.sum(v>0)),'net':float(v.sum()),'gp':gp,'gl':gl,
            'dd':float((pk-eq).max()) if len(v) else 0.}

def verify_golden(x):
    for key,target in G.items():
        val=x[key]
        ensure(abs(val-target)<(1e-7 if isinstance(target,float) else 0.5),
               f'golden {key}: {val} versus {target}')

def validate(raw,ex,indices,h1,h4bar,rr,ff,h1_events,childr,childf,
             h4_ends,h4_bar_owner,net004_at,net004_origin,net004_avail):
    t=raw[:,0].astype(np.int64)
    ensure(raw.shape==(34362,4) and ex.shape==(34362,6),'input event shapes')
    ensure(np.all(t[1:]>=t[:-1]),'raw timestamp ordering')
    ensure(len(np.unique(t))==len(t),'raw signal timestamps not unique')
    ensure(np.all(np.isin(raw[:,1],[-1.,1.])),'raw side invalid')
    ensure(np.isfinite(ex[:,0]).all(),'invalid causal014 independent raw exits')
    ensure(np.all(ex[:,4]>t),'raw exits precede original decisions')
    ensure(np.all(indices[1:]>indices[:-1]),'selected source indexes not ordered')
    ensure(np.all(t[indices[1:]]>ex[indices[:-1],4]),'selection non-overlap violation')
    ensure(np.array_equal(indices,greedy(raw,ex)),'nonoverlap account no longer source equivalent')
    has=h1>=0
    ensure(np.array_equal(has,net004_at>=0),'H1 BOS and NET004 descriptor identity mismatch')
    ensure(np.all(h1_events[h1[has],0].astype(np.int64)<=t[has]),'future H1 BOS')
    ensure(np.all(h1_events[h1[has],1]!=0),'neutral H1 BOS attached')
    d_has=net004_at>=0
    ensure(np.array_equal(net004_origin[net004_at[d_has]],h1[d_has]),'NET004 descriptor from wrong BOS')
    ensure(np.all(net004_avail[net004_at[d_has]]<=t[d_has]),'NET004 descriptor future visibility')
    ensure(np.array_equal(h4bar,np.searchsorted(h4_ends,t,side='right')-1),'H4 bar as-of index mismatch')
    h4good=h4bar>=0
    ensure(np.all(h4_ends[h4bar[h4good]]<=t[h4good]),'future H4 bar')
    for kind,link,events in [('retest',rr,childr),('failed',ff,childf)]:
        good=link>=0
        ensure(np.all(link[good]<len(events)),f'{kind} child out of range')
        ensure(np.all(events[link[good],0]<=t[good]),f'{kind} FUTURE child')
        ensure(np.array_equal(events[link[good],1].astype(np.int32),h1[good]),f'{kind} WRONG parent BOS')
        ensure(np.all(h1[good]>=0),f'{kind} child has no live parent')
    return {'raw_uniques':int(len(np.unique(t))),
            'h1_attached':int(has.sum()), 'h4_complete':int(h4good.sum()),
            'h4_non_neutral':int(np.sum(h4_bar_owner[h4bar[h4good]]!=0)),
            'retest_attached':int(np.sum(rr>=0)), 'failed_attached':int(np.sum(ff>=0)),
            'net004_attached':int(d_has.sum())}

def should_fail(name,action):
    try:action()
    except ValueError:return {'fixture':name,'rejected':True}
    raise AssertionError(f'MUTATION WAS NOT BLOCKED: {name}')

def main():
    st=time.perf_counter()
    ensure(sha(P)==P_SHA,'parent cache corrupt')
    ensure(sha(D)==D_SHA,'NET004 cache corrupt')
    with np.load(P,allow_pickle=False) as a, np.load(D,allow_pickle=False) as d:
        raw=a['raw_events'];ex=a['raw_exit'];ix=a['selected_raw_indices']
        h1=a['h1_owner_bos_asof_index'];h4bar=a['h4_completed_bar_index']
        rr=a['retest_child_asof_index'];ff=a['failed_child_asof_index']
        h1e=a['h1_events'];childr=a['retest_children'];childf=a['failed_children']
        h4ends=a['h4_bar_end_ms'];h4owner=a['h4_bar_owner']
        n4=d['causal014_event_to_net004_row'];n4origin=d['net004_origin_H1_event_index'];n4available=d['net004_available_ms']
        def check(**kw):
            keys=dict(raw=raw,ex=ex,indices=ix,h1=h1,h4bar=h4bar,rr=rr,ff=ff,
                      h1_events=h1e,childr=childr,childf=childf,h4_ends=h4ends,
                      h4_bar_owner=h4owner,net004_at=n4,net004_origin=n4origin,net004_avail=n4available)
            keys.update(kw)
            return validate(**keys)
        context=check()
        metrics=economics(raw,ex,greedy(raw,ex))
        verify_golden(metrics)
        # Mutate copies only! Never mutate the immutable cached arrays.
        i_desc=int(np.flatnonzero(n4>=0)[0]);i_child=int(np.flatnonzero(rr>=0)[0]);
        tests=[
          should_fail('FUTURE_NET004_TIMESTAMP',lambda:check(net004_avail=np.where(np.arange(len(n4available))==n4[i_desc],int(raw[i_desc,0])+1,n4available))),
          should_fail('WRONG_CHILD_ORIGIN_BOS',lambda:check(childr=np.column_stack((childr[:,0],(childr[:,1]+(np.arange(len(childr))==rr[i_child]).astype(np.int64)),childr[:,2:])))),
          should_fail('SAME_TICK_OR_PRIOR_POSITION_OVERLAP',lambda:check(indices=np.r_[ix[:1],ix[:1],ix[2:]])),
          should_fail('MISSING_DESCRIPTOR_ORIGIN',lambda:check(net004_at=np.where(np.arange(len(n4))==i_desc,-1,n4))),
          should_fail('TAMPERED_GOLDEN_CASH_PNL',lambda:verify_golden(economics(raw,np.column_stack((ex[:,0]+.01,ex[:,1:])),ix)))
        ]
        result={'status':'FAST_JAN_GOLDEN_AND_FAILURE_INJECTION_PASS',
                'source_contract':'JAN_ONLY_IMMUTABLE_SOURCE_CACHE',
                'cache_hashes':{'causal_parent':P_SHA,'net004_descriptors':D_SHA},
                'cache_bytes':P.stat().st_size+D.stat().st_size,
                'control':metrics,'context_identity':context,
                'mutation_tests':tests,
                'elapsed_seconds':round(time.perf_counter()-st,6),
                'full_jan_raw_gzip_loaded':False,
                'april_may_jul_loaded':False,'august_accessed':False,
                'not_oos_validation':True,'not_mql5_certification':True,
                'next':'NET002_NET007_JAN_CACHED_SOURCE_CONCORDANCE_REPLAY'}
        OUT.write_text(json.dumps(result,indent=2)+'\n')
    MAN.write_text(json.dumps({'source_sha256':sha(__file__),'parent_cache_sha256':P_SHA,
                  'descriptor_cache_sha256':D_SHA,'result_sha256':sha(OUT),
                  'status':'COMPLETED_LOCAL_TO_BE_DURABLE_COMMITTED',
                  'next':result['next'],'august_sealed':True},indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
