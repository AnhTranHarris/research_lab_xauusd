import gc, json, hashlib, time
from pathlib import Path
import numpy as np
import pandas as pd
import r9b020_core as core

ROOT=Path('/mnt/data')
A=ROOT/'r9b020a_cache'
B=ROOT/'r9b020b_cache'
B.mkdir(exist_ok=True)
TFS=core.TFS
TF_NAMES=core.TF_NAMES

def acceptance_state(bars,k=2):
    h=np.asarray(bars['h']); l=np.asarray(bars['l']); c=np.asarray(bars['c']); atr=np.asarray(bars['atr'])
    n=len(c)
    pen_dir=np.zeros(n,np.int8); pen_type=np.zeros(n,np.int8)
    pen_age=np.full(n,9999,np.int32); pen_depth=np.zeros(n,float); reclaim_depth=np.zeros(n,float)
    touch_count=np.zeros(n,np.int16); level_age=np.full(n,9999,np.int32); quality=np.zeros(n,float)
    first_pen=np.zeros(n,np.int8)
    fail_dir=np.zeros(n,np.int8); fail_age=np.full(n,9999,np.int32); fail_depth=np.zeros(n,float)
    active_acc_dir=np.zeros(n,np.int8); active_acc_age=np.full(n,9999,np.int32)
    up=np.nan; dn=np.nan; up_birth=-1; dn_birth=-1; up_touches=0; dn_touches=0
    lp_dir=0; lp_type=0; lp_i=-1; lp_depth=0.; lp_reclaim=0.; lp_touch=0; lp_level_age=9999; lp_q=0.
    aa_dir=0; aa_boundary=np.nan; aa_i=-1
    lf_dir=0; lf_i=-1; lf_depth=0.
    eps=1e-12
    for i in range(n):
        ev_dir=0; ev_type=0; ev_dep=0.; ev_rec=0.; ev_touch=0; ev_lage=9999; ev_q=0.; ev_first=0
        ai=atr[i]
        scale=(ai if np.isfinite(ai) and ai>eps else np.nan)
        upper_pen=np.isfinite(up) and h[i] > up + eps
        lower_pen=np.isfinite(dn) and l[i] < dn - eps
        cand=[]
        if upper_pen:
            up_touches+=1
            dep=(h[i]-up)/(scale+eps) if np.isfinite(scale) else 0.
            acc=c[i] > up + eps
            rec=max(0.,up-c[i])/(scale+eps) if np.isfinite(scale) else 0.
            q=max(0.,c[i]-up)/(max(h[i]-up,eps)) if acc else max(0.,up-c[i])/(max(h[i]-up,eps)+max(0.,up-c[i])+eps)
            cand.append((dep,1,1 if acc else -1,rec,up_touches,i-up_birth if up_birth>=0 else 9999,min(1.,max(0.,q)),1 if up_touches==1 else 0,up))
        if lower_pen:
            dn_touches+=1
            dep=(dn-l[i])/(scale+eps) if np.isfinite(scale) else 0.
            acc=c[i] < dn - eps
            rec=max(0.,c[i]-dn)/(scale+eps) if np.isfinite(scale) else 0.
            q=max(0.,dn-c[i])/(max(dn-l[i],eps)) if acc else max(0.,c[i]-dn)/(max(dn-l[i],eps)+max(0.,c[i]-dn)+eps)
            cand.append((dep,-1,1 if acc else -1,rec,dn_touches,i-dn_birth if dn_birth>=0 else 9999,min(1.,max(0.,q)),1 if dn_touches==1 else 0,dn))
        if cand:
            cand.sort(key=lambda x:x[0],reverse=True)
            ev_dep,ev_dir,ev_type,ev_rec,ev_touch,ev_lage,ev_q,ev_first,ev_boundary=cand[0]
            lp_dir=ev_dir; lp_type=ev_type; lp_i=i; lp_depth=ev_dep; lp_reclaim=ev_rec
            lp_touch=ev_touch; lp_level_age=ev_lage; lp_q=ev_q
            if ev_type==1:
                aa_dir=ev_dir; aa_boundary=ev_boundary; aa_i=i
        if aa_dir!=0 and i>aa_i:
            failed=(aa_dir>0 and c[i] < aa_boundary-eps) or (aa_dir<0 and c[i] > aa_boundary+eps)
            if failed:
                lf_dir=aa_dir; lf_i=i
                lf_depth=(abs(c[i]-aa_boundary)/(scale+eps)) if np.isfinite(scale) else 0.
                aa_dir=0; aa_boundary=np.nan; aa_i=-1
        pen_dir[i]=lp_dir; pen_type[i]=lp_type
        if lp_i>=0:
            pen_age[i]=i-lp_i; pen_depth[i]=lp_depth; reclaim_depth[i]=lp_reclaim
            touch_count[i]=lp_touch; level_age[i]=lp_level_age; quality[i]=lp_q
            first_pen[i]=1 if lp_touch==1 else 0
        fail_dir[i]=lf_dir
        if lf_i>=0:
            fail_age[i]=i-lf_i; fail_depth[i]=lf_depth
        active_acc_dir[i]=aa_dir
        if aa_i>=0: active_acc_age[i]=i-aa_i
        center=i-k
        if center>=k:
            wh=h[center-k:center+k+1]; wl=l[center-k:center+k+1]
            if h[center] >= np.nanmax(wh)-eps:
                new=float(h[center])
                if (not np.isfinite(up)) or abs(new-up)>eps:
                    up=new; up_birth=i; up_touches=0
            if l[center] <= np.nanmin(wl)+eps:
                new=float(l[center])
                if (not np.isfinite(dn)) or abs(new-dn)>eps:
                    dn=new; dn_birth=i; dn_touches=0
    return dict(pen_dir=pen_dir,pen_type=pen_type,pen_age=pen_age,pen_depth=pen_depth,
                reclaim_depth=reclaim_depth,touch_count=touch_count,level_age=level_age,
                quality=quality,first_pen=first_pen,fail_dir=fail_dir,fail_age=fail_age,
                fail_depth=fail_depth,active_acc_dir=active_acc_dir,active_acc_age=active_acc_age)

def event_accept_features(df,tf_bars):
    n=len(df); side=df.side.to_numpy(np.int8); ev_sec=df.event_sec.to_numpy(np.int64)
    per=[]; cols={}
    for j,tf in enumerate(TFS):
        z=tf_bars[tf]; st=z['accept']
        bi=np.searchsorted(z['end'],ev_sec,side='right')-1
        ok=bi>=0; jj=np.clip(bi,0,len(z['end'])-1)
        def take(name,default=0.):
            x=np.asarray(st[name][jj],dtype=float); x[~ok]=default; return x
        pd_=take('pen_dir'); pt=take('pen_type'); pa=take('pen_age',9999.); dep=take('pen_depth')
        rec=take('reclaim_depth'); tc=take('touch_count'); la=take('level_age',9999.); q=take('quality')
        fp=take('first_pen'); fd=take('fail_dir'); fa=take('fail_age',9999.); fdep=take('fail_depth')
        ad=take('active_acc_dir'); aa=take('active_acc_age',9999.)
        tag=TF_NAMES[tf]
        cols[f'{tag}_pen_align']=pd_*side; cols[f'{tag}_pen_type']=pt; cols[f'{tag}_pen_age']=pa
        cols[f'{tag}_pen_depth']=dep; cols[f'{tag}_reclaim_depth']=rec; cols[f'{tag}_touch_count']=tc
        cols[f'{tag}_level_age']=la; cols[f'{tag}_accept_quality']=q; cols[f'{tag}_first_pen']=fp
        cols[f'{tag}_fail_align']=fd*side; cols[f'{tag}_fail_age']=fa; cols[f'{tag}_fail_depth']=fdep
        cols[f'{tag}_active_acc_align']=ad*side; cols[f'{tag}_active_acc_age']=aa
        per.append((pd_*side,pt,pa,dep,rec,tc,la,q,fp,fd*side,fa,fdep,ad*side,aa))
    owner=df.owner_tf.fillna(-1).to_numpy(int)
    names=['pen_align','pen_type','pen_age','pen_depth','reclaim_depth','touch_count','level_age',
           'accept_quality','first_pen','fail_align','fail_age','fail_depth','active_acc_align','active_acc_age']
    for k,name in enumerate(names):
        arr=np.full(n,9999. if 'age' in name else 0.,float)
        for j in range(len(TFS)):
            m=owner==j
            if np.any(m): arr[m]=per[j][k][m]
        cols[f'owner_{name}']=arr
    pal=np.column_stack([x[0] for x in per]); typ=np.column_stack([x[1] for x in per]); age=np.column_stack([x[2] for x in per])
    fal=np.column_stack([x[9] for x in per]); fage=np.column_stack([x[10] for x in per])
    active=np.column_stack([x[12] for x in per]); recent=age<=3
    cols['accept_same_count']=np.sum((typ==1)&(pal>0)&recent,axis=1)
    cols['accept_opp_count']=np.sum((typ==1)&(pal<0)&recent,axis=1)
    cols['sweep_same_count']=np.sum((typ==-1)&(pal>0)&recent,axis=1)
    cols['sweep_opp_count']=np.sum((typ==-1)&(pal<0)&recent,axis=1)
    cols['fail_same_count']=np.sum((fal>0)&(fage<=3),axis=1)
    cols['fail_opp_count']=np.sum((fal<0)&(fage<=3),axis=1)
    cols['active_accept_same_count']=np.sum(active>0,axis=1)
    cols['active_accept_opp_count']=np.sum(active<0,axis=1)
    cols['recent_pen_count']=np.sum(recent & (typ!=0),axis=1)
    return cols

def build_month(m):
    out=B/f'R9B_020B_M{m:02d}.pkl.gz'; summ=B/f'R9B_020B_M{m:02d}_summary.json'
    if out.exists() and summ.exists():
        return pd.read_pickle(out,compression='gzip'),json.load(open(summ))
    t0=time.time()
    a=pd.read_pickle(A/f'R9B_020A_M{m:02d}.pkl.gz',compression='gzip')
    t,mid,av,bv=core.load_ticks(core.FILES[m])
    tf={}
    for tfsec in TFS:
        z=core.aggregate_tf(t,mid,tfsec)
        z['accept']=acceptance_state(z)
        tf[tfsec]=z
    extra=event_accept_features(a,tf)
    for k,v in extra.items(): a[k]=v
    a.to_pickle(out,compression='gzip')
    h=hashlib.sha256(out.read_bytes()).hexdigest()
    sm={'month':m,'rows':len(a),'elapsed_seconds':time.time()-t0,'cache_sha256':h,'august_accessed':False}
    json.dump(sm,open(summ,'w'),indent=2,sort_keys=True)
    del a,t,mid,av,bv,tf; gc.collect()
    return pd.read_pickle(out,compression='gzip'),sm

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--month',type=int,required=True)
    args=ap.parse_args()
    _,sm=build_month(args.month)
    print(json.dumps(sm,indent=2,sort_keys=True))
