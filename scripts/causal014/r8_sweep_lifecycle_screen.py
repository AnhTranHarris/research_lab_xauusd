"""Rebuilt Gamma_2 sweep-event helper.

Default sweep_signals is a causal translation of the certified R8 MQL5 state
machine on the fixed modeled spread used by Gamma_2. Legacy compatibility is
separate, explicitly forensic, and may expose future completed-second state.
"""
import numpy as np
from numba import njit
H=.10; LIQ_LOOKBACK=20; VEL_LOOKBACK=5; PERSISTENCE_SEC=2; EXPIRY_SEC=20
BREAK_BUFFER=.10; RECLAIM=.15; CONFIRM=.08; MIN_VELOCITY=.15; MIN_EFF=.30; MAX_PER_MIN=5

@njit(cache=True)
def _session_floor(sec):
    lon_off=60 if (sec>=1774746000 and sec<1792890000) else 0
    ny_off=-240 if (sec>=1772953200 and sec<1793512800) else -300
    lm=((sec+lon_off*60)%86400)//60; nm=((sec+ny_off*60)%86400)//60
    london=lm>=480 and lm<990; ny=nm>=480 and nm<1020
    if london and ny:return 1.75
    if london:return 2.0
    if ny:return 1.75
    return 2.5

@njit(cache=True)
def _causal_core(t,mid,su,hi,lo,cl,sec_ids,atrsec,al,ash):
    cap=max(10000,min(300000,len(t)//20+1));X=np.empty((cap,4),np.float64);n=0
    state=0;level=0.;started=0;minute=-1;trades=0;cool=-1;j=0;k=0;lastsec=-1
    for i in range(len(t)):
        sec=t[i]//1000
        if sec!=lastsec:
            while j+1<len(sec_ids) and sec_ids[j+1]<=sec:j+=1
            while k+1<len(su) and su[k+1]<=sec:k+=1
            lastsec=sec
        if j>=len(sec_ids) or sec_ids[j]!=sec or k>=len(su) or su[k]!=sec:continue
        mn=sec//60
        if mn!=minute:minute=mn;trades=0;state=0;level=0.;started=0
        if sec<cool or trades>=MAX_PER_MIN or k<LIQ_LOOKBACK or j<VEL_LOOKBACK:continue
        av=atrsec[j]
        if not np.isfinite(av) or av+1e-12<_session_floor(sec):continue
        newest=k-1;oldest=newest-(LIQ_LOOKBACK-1);upper=-1e18;lower=1e18
        for q in range(oldest,newest+1):
            if hi[q]>upper:upper=hi[q]
            if lo[q]<lower:lower=lo[q]
        bid=mid[i]-H;ask=mid[i]+H
        oldestv=k-VEL_LOOKBACK;prev=cl[oldestv];start=prev;travel=0.
        for q in range(oldestv+1,k):
            v=cl[q];travel+=abs(v-prev);prev=v
        travel+=abs(bid-prev);disp=bid-start;eff=abs(disp)/(travel+1e-9)
        if state==0:
            if ask>=upper+BREAK_BUFFER:state=1;level=upper;started=sec
            elif bid<=lower-BREAK_BUFFER:state=-1;level=lower;started=sec
        if state==1:
            if ask<=level-RECLAIM:state=2;started=sec
            elif sec-started>=PERSISTENCE_SEC and ask>=level+CONFIRM and disp>=MIN_VELOCITY and eff>=MIN_EFF:
                state=0;level=0.;started=0;trades+=1;cool=sec+1
        elif state==-1:
            if bid>=level+RECLAIM:state=-2;started=sec
            elif sec-started>=PERSISTENCE_SEC and bid<=level-CONFIRM and disp<=-MIN_VELOCITY and eff>=MIN_EFF:
                state=0;level=0.;started=0;trades+=1;cool=sec+1
        elif state==2:
            if disp<=-MIN_VELOCITY and eff>=MIN_EFF:
                if n>=cap:break
                X[n,0]=t[i];X[n,1]=-1;X[n,2]=level;X[n,3]=ash[j];n+=1
                trades+=1;cool=sec+1;state=0;level=0.;started=0
        elif state==-2:
            if disp>=MIN_VELOCITY and eff>=MIN_EFF:
                if n>=cap:break
                X[n,0]=t[i];X[n,1]=1;X[n,2]=level;X[n,3]=al[j];n+=1
                trades+=1;cool=sec+1;state=0;level=0.;started=0
        if state!=0 and started>0 and sec-started>EXPIRY_SEC:state=0;level=0.;started=0
    return X[:n]

def sweep_signals(t,mid,su,hi,lo,cl,sec_ids,atrsec,align_long,align_short):
    return _causal_core(np.asarray(t,np.int64),np.asarray(mid,np.float64),np.asarray(su,np.int64),np.asarray(hi,np.float64),np.asarray(lo,np.float64),np.asarray(cl,np.float64),np.asarray(sec_ids,np.int64),np.asarray(atrsec,np.float64),np.asarray(align_long,np.int8),np.asarray(align_short,np.int8))

@njit(cache=True)
def _compat_core(t,mid,su,hi,lo,cl,sec_ids,atr,al,ash,feature_lead,timestamp_lag,liq_shift,cont_quota,cont_cool,atr_shift,align_shift):
    ch=np.empty(len(t),np.bool_);ch[0]=True
    for i in range(1,len(t)):ch[i]=(t[i]//1000)!=(t[i-1]//1000)
    idx=np.empty(len(t),np.int64);nn=0
    for i in range(len(t)):
        if ch[i]:idx[nn]=i;nn+=1
    first_t=t[idx[:nn]]
    cap=max(10000,min(300000,len(su)//2+1));X=np.empty((cap,4),np.float64);n=0
    state=0;level=0.;started=0;minute=-1;trades=0;cool=-1;N=min(len(su),len(sec_ids))
    for k in range(21,N):
        fk=k+feature_lead
        if fk>=len(su):break
        sec=sec_ids[k];mn=sec//60
        if mn!=minute:minute=mn;trades=0;state=0;level=0.;started=0
        if sec<cool or trades>=MAX_PER_MIN:continue
        ak=k+atr_shift
        if ak<0 or ak>=len(atr):continue
        av=atr[ak]
        if not np.isfinite(av) or av+1e-12<_session_floor(sec):continue
        newest=k-1+liq_shift;oldest=newest-(LIQ_LOOKBACK-1)
        if oldest<0 or newest>=len(hi):continue
        upper=-1e18;lower=1e18
        for q in range(oldest,newest+1):
            if hi[q]>upper:upper=hi[q]
            if lo[q]<lower:lower=lo[q]
        bhi=hi[fk];blo=lo[fk];bcl=cl[fk];ahi=bhi+2*H;acl=bcl+2*H
        if fk<VEL_LOOKBACK-1:continue
        start=cl[fk-(VEL_LOOKBACK-1)];prev=start;travel=0.
        for q in range(fk-(VEL_LOOKBACK-2),fk+1):
            v=cl[q];travel+=abs(v-prev);prev=v
        disp=bcl-start;eff=abs(disp)/(travel+1e-9)
        if state==0:
            if ahi>=upper+BREAK_BUFFER:state=1;level=upper;started=sec
            elif blo<=lower-BREAK_BUFFER:state=-1;level=lower;started=sec
        if state==1:
            if acl<=level-RECLAIM:state=2;started=sec
            elif sec-started>=PERSISTENCE_SEC and acl>=level+CONFIRM and disp>=MIN_VELOCITY and eff>=MIN_EFF:
                state=0;level=0.;started=0
                if cont_quota:trades+=1
                if cont_cool:cool=sec+1
        elif state==-1:
            if bcl>=level+RECLAIM:state=-2;started=sec
            elif sec-started>=PERSISTENCE_SEC and bcl<=level-CONFIRM and disp<=-MIN_VELOCITY and eff>=MIN_EFF:
                state=0;level=0.;started=0
                if cont_quota:trades+=1
                if cont_cool:cool=sec+1
        elif state==2 and disp<=-MIN_VELOCITY and eff>=MIN_EFF:
            ti=k-timestamp_lag
            if ti<0:ti=0
            aj=k+align_shift
            if aj<0:aj=0
            if aj>=len(ash):aj=len(ash)-1
            if n>=cap:break
            X[n,0]=first_t[ti];X[n,1]=-1;X[n,2]=level;X[n,3]=ash[aj];n+=1
            trades+=1;cool=sec+1;state=0;level=0.;started=0
        elif state==-2 and disp>=MIN_VELOCITY and eff>=MIN_EFF:
            ti=k-timestamp_lag
            if ti<0:ti=0
            aj=k+align_shift
            if aj<0:aj=0
            if aj>=len(al):aj=len(al)-1
            if n>=cap:break
            X[n,0]=first_t[ti];X[n,1]=1;X[n,2]=level;X[n,3]=al[aj];n+=1
            trades+=1;cool=sec+1;state=0;level=0.;started=0
        if state!=0 and started>0 and sec-started>EXPIRY_SEC:state=0;level=0.;started=0
    return X[:n]

def sweep_signals_legacy_compat(t,mid,su,hi,lo,cl,sec_ids,atrsec,align_long,align_short,feature_lead=1,timestamp_lag=0,liquidity_shift=0,cont_consumes_quota=True,cont_sets_cooldown=True,atr_index_shift=0,align_index_shift=0):
    return _compat_core(np.asarray(t,np.int64),np.asarray(mid,np.float64),np.asarray(su,np.int64),np.asarray(hi,np.float64),np.asarray(lo,np.float64),np.asarray(cl,np.float64),np.asarray(sec_ids,np.int64),np.asarray(atrsec,np.float64),np.asarray(align_long,np.int8),np.asarray(align_short,np.int8),int(feature_lead),int(timestamp_lag),int(liquidity_shift),bool(cont_consumes_quota),bool(cont_sets_cooldown),int(atr_index_shift),int(align_index_shift))
