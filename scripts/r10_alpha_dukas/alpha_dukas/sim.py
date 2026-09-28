"""Causal Bid/Ask tick replay with one portfolio position across month blocks.

Signal policies are external; the built-in smoke generator is explicitly NOT
an alpha strategy. No trade is ever filled at a historical candle close.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Callable

import numpy as np
from numba import njit

from .data import PRICE_SCALE, bars_from_ticks, load_month, MONTH_SHA256

REASONS={1:'STOP_EXECUTABLE_TICK',2:'TARGET_EXECUTABLE_TICK',
         3:'HOLD_TIMEOUT_NEXT_EXECUTABLE_TICK',4:'MARGIN_LIQUIDATION'}

@njit(cache=True)
def _scan_position(times, bids, asks, start_index, side, entry_raw,
                   stop_raw, target_raw, deadline_ms, volume_oz,
                   balance_before, entry_commission_usd, minimum_equity_ratio,
                   margin_required):
    """Return (end_tick_index, exit_quote_raw, reason_code, mfe, mae, trough).

    Same-tick STOP before TARGET before timed close. Exact quote chronology.
    An unresolved position returns last observed excursions and end=-1.
    """
    mfe=0.0;mae=0.0;trough=balance_before-entry_commission_usd
    for i in range(start_index,len(times)):
        quote=bids[i] if side>0 else asks[i]
        pnl=(quote-entry_raw)*side*volume_oz/PRICE_SCALE
        if pnl>mfe:mfe=pnl
        if pnl<mae:mae=pnl
        equity=balance_before+pnl-entry_commission_usd
        if equity<trough:trough=equity
        if equity <= margin_required*minimum_equity_ratio:
            return i,quote,4,mfe,mae,trough
        if (side>0 and quote<=stop_raw) or (side<0 and quote>=stop_raw):
            return i,quote,1,mfe,mae,trough
        if (side>0 and quote>=target_raw) or (side<0 and quote<=target_raw):
            return i,quote,2,mfe,mae,trough
        if times[i]>=deadline_ms:
            return i,quote,3,mfe,mae,trough
    return -1,0,0,mfe,mae,trough


@dataclass(frozen=True)
class ExecutionConfig:
    initial_balance_usd: float=200.0
    lot: float=0.01
    contract_oz_per_lot: float=100.0
    leverage: float=500.0
    # Explicit configurable broker assumptions: NOT verified Coinexx fee terms.
    commission_roundtrip_usd: float=0.20
    slippage_each_side_usd: float=0.05
    max_spread_usd: float=6.0
    maintenance_margin_ratio: float=0.5
    terminal_liquidation: bool=False

    def __post_init__(self):
        if not(0<self.lot<=100 and self.contract_oz_per_lot>0 and self.leverage>0):
            raise ValueError('Invalid volume/contract/leverage')
        if not(self.initial_balance_usd>0 and self.commission_roundtrip_usd>=0
                and self.slippage_each_side_usd>=0 and self.max_spread_usd>=0
                and 0<=self.maintenance_margin_ratio<=1):
            raise ValueError('Invalid account/economic assumptions')


@dataclass(frozen=True)
class Signal:
    """Ready time is the first legally executable time after feature visibility.

    For completed bar [start,end), ready_ms must be >= end; for a decision
    made ON a tick at t, use ready_ms > t. Researcher supplies known_at_ms.
    """
    ready_ms: int
    known_at_ms: int
    side: int
    stop_usd: float
    target_usd: float
    max_hold_ms: int
    expires_ms: int
    signal_id: str

    def __post_init__(self):
        if self.side not in(-1,1) or self.ready_ms<self.known_at_ms:
            raise ValueError('Side or future-leaking observation time')
        if self.stop_usd<=0 or self.target_usd<=0 or self.max_hold_ms<=0:
            raise ValueError('Invalid bracket/timeout')
        if self.expires_ms<self.ready_ms:raise ValueError('Invalid expiry')


@dataclass
class Position:
    source_signal_id: str
    side: int
    entry_ms: int
    entry_raw: int
    stop_raw: int
    target_raw: int
    max_hold_end_ms: int
    margin_required_usd: float
    balance_before_usd: float
    opened_month: str
    mfe_usd: float=0.0
    mae_usd: float=0.0
    lowest_equity_usd: float=float('inf')


class TickPortfolio:
    """Serial, deterministic, single-account tick replay; state persists months."""
    def __init__(self,config:ExecutionConfig):
        self.cfg=config;self.balance=config.initial_balance_usd
        self.pos:Position|None=None
        self.pending:list[Signal]=[]
        self.trades:list[dict]=[]
        self.blocks:list[dict]=[]
        self.rejection_counts:dict[str,int]={}
        self.worst_equity_usd=config.initial_balance_usd
        self.peak_equity_usd=config.initial_balance_usd
        self.max_drawdown_usd=0.0
        self.last_month='';self.last_tick_ms=0;self.last_bid=0;self.last_ask=0
        self.processed_months=[]

    def _reject(self,reason:str):
        self.rejection_counts[reason]=self.rejection_counts.get(reason,0)+1

    @staticmethod
    def _price_raw(dollars:float)->int:return int(round(dollars*PRICE_SCALE))

    def _resolve(self,ticks,first_idx:int)->tuple[int,bool]:
        if self.pos is None:return first_idx,True
        p=self.pos;c=self.cfg
        idx,quote,why,mfe,mae,trough=_scan_position(
            ticks['time_msc'],ticks['bid_raw'],ticks['ask_raw'],first_idx,p.side,
            p.entry_raw,p.stop_raw,p.target_raw,p.max_hold_end_ms,
            c.lot*c.contract_oz_per_lot,p.balance_before_usd,
            c.commission_roundtrip_usd/2,c.maintenance_margin_ratio,
            p.margin_required_usd)
        p.mfe_usd=max(p.mfe_usd,mfe);p.mae_usd=min(p.mae_usd,mae)
        p.lowest_equity_usd=min(p.lowest_equity_usd,trough)
        self.worst_equity_usd=min(self.worst_equity_usd,trough)
        if idx<0:return len(ticks),False
        exit_raw=quote-self._price_raw(c.slippage_each_side_usd)*p.side
        gross=(exit_raw-p.entry_raw)*p.side*c.lot*c.contract_oz_per_lot/PRICE_SCALE
        net=gross-c.commission_roundtrip_usd
        self.balance=round(self.balance+net,6)
        self.worst_equity_usd=min(self.worst_equity_usd,self.balance)
        self.peak_equity_usd=max(self.peak_equity_usd,self.balance)
        self.max_drawdown_usd=max(self.max_drawdown_usd,
                                  self.peak_equity_usd-self.balance,
                                  self.peak_equity_usd-p.lowest_equity_usd)
        self.trades.append(dict(id=p.source_signal_id,open_month=p.opened_month,
            entry_ms=p.entry_ms,exit_ms=int(ticks['time_msc'][idx]),
            side=p.side,entry_price=p.entry_raw/PRICE_SCALE,
            exit_price=exit_raw/PRICE_SCALE,reason=REASONS[why],
            hold_ms=int(ticks['time_msc'][idx])-p.entry_ms,
            gross_usd=round(gross,6),commission_usd=c.commission_roundtrip_usd,
            net_usd=round(net,6),mfe_usd=round(p.mfe_usd,6),
            mae_usd=round(p.mae_usd,6),balance_after_usd=self.balance))
        self.pos=None
        return idx+1,True

    def run_block(self,month:str,ticks:np.ndarray,signals:list[Signal])->dict:
        if month not in MONTH_SHA256 or month in self.processed_months:
            raise ValueError('Duplicated or non-Alpha month')
        if self.processed_months and month<=self.processed_months[-1]:
            raise ValueError('Month blocks MUST replay chronologically')
        if len(ticks)==0:raise ValueError('Empty source month')
        if int(ticks['time_msc'][0])<=self.last_tick_ms:
            raise ValueError('Cross-month ticks out of order')
        self.processed_months.append(month)
        self.last_month=month
        n=len(ticks);tt=ticks['time_msc'];beg_balance=self.balance
        first_trades=len(self.trades);start_idx=0;earliest_ready=-1
        busy_until_ms=-1
        for sig in signals:
            if sig.ready_ms<earliest_ready:raise ValueError('Unsorted signal times')
            earliest_ready=sig.ready_ms
        candidates=sorted(self.pending+signals,key=lambda s:(s.ready_ms,s.signal_id))
        self.pending=[]
        # If a position survives previous month, it is updated BEFORE any new
        # signals are considered. Candidate signals that arise before exit
        # are rejected for overlapping a one-position portfolio.
        if self.pos is not None:
            start_idx,closed=self._resolve(ticks,0)
            if not closed:
                for sig in candidates:self._reject('ONE_POSITION_ACTIVE')
                candidates=[]
            elif self.trades:
                busy_until_ms=self.trades[-1]['exit_ms']
        for sig in candidates:
            if sig.ready_ms<=busy_until_ms:
                self._reject('ONE_POSITION_ACTIVE')
                continue
            if start_idx>=n:
                if sig.expires_ms>int(tt[-1]):self.pending.append(sig)
                else:self._reject('SIGNAL_EXPIRED')
                continue
            target_idx=int(np.searchsorted(tt,sig.ready_ms,side='left'))
            if target_idx<start_idx:
                self._reject('ONE_POSITION_ACTIVE');continue
            if target_idx>=n:
                if sig.expires_ms>int(tt[-1]):self.pending.append(sig)
                else:self._reject('SIGNAL_EXPIRED')
                continue
            fill_ms=int(tt[target_idx])
            if fill_ms>sig.expires_ms:
                self._reject('SIGNAL_EXPIRED');continue
            b=int(ticks['bid_raw'][target_idx]);a=int(ticks['ask_raw'][target_idx])
            spread=(a-b)/PRICE_SCALE
            if spread>self.cfg.max_spread_usd:
                self._reject('SPREAD_GATE');continue
            rawslip=self._price_raw(self.cfg.slippage_each_side_usd)
            entry_raw=(a+rawslip) if sig.side>0 else (b-rawslip)
            exposure=self.cfg.lot*self.cfg.contract_oz_per_lot
            margin=entry_raw/PRICE_SCALE*exposure/self.cfg.leverage
            if self.balance<=margin+self.cfg.commission_roundtrip_usd/2:
                self._reject('MARGIN_GATE');continue
            sl_dist=self._price_raw(sig.stop_usd)
            tp_dist=self._price_raw(sig.target_usd)
            self.pos=Position(source_signal_id=sig.signal_id,side=sig.side,
                entry_ms=fill_ms,entry_raw=entry_raw,
                stop_raw=entry_raw-sig.side*sl_dist,
                target_raw=entry_raw+sig.side*tp_dist,
                max_hold_end_ms=fill_ms+sig.max_hold_ms,
                margin_required_usd=margin,balance_before_usd=self.balance,
                opened_month=month,lowest_equity_usd=self.balance)
            start_idx,closed=self._resolve(ticks,target_idx+1)
            if closed and self.trades:
                busy_until_ms=self.trades[-1]['exit_ms']
            elif not closed:
                busy_until_ms=int(tt[-1])
        self.last_tick_ms=int(tt[-1]);self.last_bid=int(ticks['bid_raw'][-1]);self.last_ask=int(ticks['ask_raw'][-1])
        ended=self.trades[first_trades:];gross_pos=sum(x['gross_usd'] for x in ended if x['gross_usd']>0)
        gross_neg=sum(x['gross_usd'] for x in ended if x['gross_usd']<0)
        block={'month':month,'source_rows':n,'first_ms':int(tt[0]),'last_ms':int(tt[-1]),
               'realized_net_usd':round(sum(x['net_usd'] for x in ended),6),
               'gross_positive_usd':round(gross_pos,6),'gross_negative_usd':round(gross_neg,6),
               'trades_closed':len(ended),'balance_start_usd':beg_balance,
               'balance_end_usd':self.balance,'open_position_carry':self.pos is not None,
               'pending_signal_count':len(self.pending)}
        self.blocks.append(block)
        return block

    def final_summary(self)->dict:
        # A month boundary does not liquidate existing holdings or book
        # future unrealized profits as if realized. Explicitly report carry.
        tr=self.trades
        gross_profit=sum(x['gross_usd'] for x in tr if x['gross_usd']>0)
        gross_loss=sum(x['gross_usd'] for x in tr if x['gross_usd']<0)
        fees=sum(x['commission_usd'] for x in tr)
        pnl=sum(x['net_usd'] for x in tr)
        unreal=0.0
        if self.pos is not None:
            p=self.pos;quote=self.last_bid if p.side>0 else self.last_ask
            unreal=(quote-p.entry_raw)*p.side*self.cfg.lot*self.cfg.contract_oz_per_lot/PRICE_SCALE
            unreal-=self.cfg.commission_roundtrip_usd
        return {'schema':'r10_alpha_dukas_tick_backtest_v1',
                'result_class':'INFRASTRUCTURE_SMOKE_ONLY_UNLESS_STRATEGY_SEPARATELY_VALIDATED',
                'months':self.processed_months,'config':asdict(self.cfg),
                'trades_closed':len(tr),'gross_profit_usd':round(gross_profit,4),
                'gross_loss_usd':round(gross_loss,4),'total_fees_usd':round(fees,4),
                'net_realized_usd':round(pnl,4),
                'profit_factor_gross':round(gross_profit/-gross_loss,4) if gross_loss<0 else None,
                'win_rate_net':round(sum(x['net_usd']>0 for x in tr)/len(tr),6) if tr else None,
                'balance_usd':round(self.balance,4),
                'unrealized_after_exit_cost_usd':round(unreal,4),
                'open_position':asdict(self.pos) if self.pos else None,
                'pending_signals':len(self.pending),'peak_closed_balance_usd':round(self.peak_equity_usd,4),
                'worst_observed_equity_usd':round(self.worst_equity_usd,4),
                'max_observed_drawdown_usd':round(self.max_drawdown_usd,4),
                'rejection_counts':self.rejection_counts,
                'week_reporting':'UTC ISO PROVISIONAL ONLY; NOT USER-APPROVED',
                'validation_wall':'NO OOS STATEMENT; ALL JAN--JUL POTENTIALLY RESEARCH-EXPOSED; AUG SEALED'}


def deterministic_smoke_signals(ticks:np.ndarray, month:str,step_bars:int=180)->list[Signal]:
    """Non-optimized, arbitrary M1 up/down test; proves bar-close causality ONLY.

    Entries are not a recommended trading strategy and not research results.
    Small signal count makes functional regression checks cheap.
    """
    bars=bars_from_ticks(ticks,60_000)
    result=[]
    for k in range(step_bars,len(bars),step_bars):
        b=bars[k-1]                  # LAST finished M1 candle; never bars[k]
        side=1 if int(b['bid_c'])>=int(b['bid_o']) else -1
        eligible=int(b['end_ms'])    # first following executable tick >= close
        result.append(Signal(ready_ms=eligible,known_at_ms=eligible,
            side=side,stop_usd=2.0,target_usd=4.0,max_hold_ms=15_000,
            expires_ms=eligible+30_000,signal_id=f'SMOKE_{month}_{k}'))
    return result


def load_signals_csv(path:Path)->list[Signal]:
    """External strategy producer supplies fully specified as-of opportunities."""
    import csv
    result=[]
    with Path(path).open(newline='') as f:
        for row in csv.DictReader(f):
            result.append(Signal(ready_ms=int(row['ready_ms']),
                known_at_ms=int(row['known_at_ms']),side=int(row['side']),
                stop_usd=float(row['stop_usd']),target_usd=float(row['target_usd']),
                max_hold_ms=int(row['max_hold_ms']),expires_ms=int(row['expires_ms']),
                signal_id=str(row['signal_id'])))
    result.sort(key=lambda z:(z.ready_ms,z.signal_id))
    return result


def write_run_outputs(portfolio:TickPortfolio,folder:Path,tag:str)->dict:
    import csv
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    report=portfolio.final_summary()
    (folder/f'{tag}_summary.json').write_text(json.dumps(report,indent=2)+'\n')
    for suffix,rows in [('trades',portfolio.trades),('monthly',portfolio.blocks)]:
        path=folder/f'{tag}_{suffix}.csv'
        if rows:
            with path.open('w',newline='') as f:
                wr=csv.DictWriter(f,fieldnames=rows[0].keys());wr.writeheader();wr.writerows(rows)
        else:path.write_text('')
    return report