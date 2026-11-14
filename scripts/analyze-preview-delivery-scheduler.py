#!/usr/bin/env python3
"""Offline public-dispatch accounting. No process launch or inferred clock alignment."""
import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('scheduler_prepare',ROOT/'scripts/prepare-preview-delivery-scheduler.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
o=p.o
require=o.require
CONTRACT = dict(version=1, clock=dict(name='CLOCK_MONOTONIC', provenance='explicit shared host/boot identity required'),
    bounds='start_ns <= stop_ns; complete coverage required',
    tasks='pid, tid, lifetime, start_ns, stop_ns; reuse requires disjoint lifetimes',
    initial='one state per live task at capture start: running (with cpu), runnable, non_runnable, unknown',
    events='ordered ns, cpu; switch: prev/next task lifetime keys and prev_state (runnable/non_runnable); wakeup: task lifetime key; loss: ns/count',
    task_key='[pid, tid, lifetime]', limitation='Non-runnable time does not identify a blocking cause. Overlapping endpoint/thread intervals are non-additive.')


def integer(value):
    return type(value) is int and value>=0


def scheduler(capture, clock):
    require(capture['version']==1 and capture['clock']==clock and clock['name']=='CLOCK_MONOTONIC'
            and bool(clock['provenance']), 'clock mismatch or missing provenance')
    start,stop=capture['start_ns'],capture['stop_ns']
    require(integer(start) and integer(stop) and start<stop,'invalid capture bounds')
    tasks={}; intervals=defaultdict(list); state={}; issues=[]
    for task in capture['tasks']:
        key=tuple(task['key']); require(len(key)==3 and all(integer(v) for v in key),'invalid task key')
        require(key not in tasks and start<=task['start_ns']<task['stop_ns']<=stop,'invalid task lifetime')
        for other,t in tasks.items():
            require(key[:2]!=other[:2] or min(t['stop_ns'],task['stop_ns'])<=max(t['start_ns'],task['start_ns']), 'ambiguous task reuse')
        tasks[key]=task
        initial=task.get('initial','unknown')
        if initial=='running' and not integer(task.get('cpu')): initial='unknown'
        require(initial in ('running','runnable','non_runnable','unknown'),'invalid initial state')
        state[key]=(task['start_ns'],initial,task.get('cpu'))
    def transition(key,ns,new,cpu=None):
        require(key in tasks,'unknown task lifetime')
        t=tasks[key]; require(t['start_ns']<=ns<t['stop_ns'],'event outside task lifetime')
        a,old,old_cpu=state[key]
        require(a<=ns,'misordered transition')
        intervals[key].append(dict(start_ns=a,stop_ns=ns,state=old,cpu=old_cpu))
        state[key]=(ns,new,cpu)
    def cpu_conflicts(ns):
        cpus=defaultdict(list)
        for key,(_,value,cpu) in state.items():
            if value=='running' and tasks[key]['start_ns']<=ns<tasks[key]['stop_ns']: cpus[cpu].append(key)
        for keys in cpus.values():
            if len(keys)>1:
                issues.append('inconsistent CPU ownership')
                for key in keys:
                    at,_,_=state[key]; state[key]=(at,'unknown',None)
    cpu_conflicts(start)
    previous=start
    for event in capture['events']:
        ns=event['ns']; require(integer(ns) and previous<=ns<stop,'misordered or truncated event')
        previous=ns; kind=event['kind']
        if kind=='loss':
            require(integer(event['count']) and event['count']>0,'invalid loss')
            issues.append('capture loss')
            for key,t in tasks.items():
                if t['start_ns']<=ns<t['stop_ns']: transition(key,ns,'unknown')
            continue
        require(integer(event['cpu']),'missing CPU')
        if kind=='switch':
            prev,nxt=tuple(event['prev']),tuple(event['next'])
            require(event['prev_state'] in ('runnable','non_runnable'),'missing previous task state')
            if prev in state and (state[prev][1]!='running' or state[prev][2]!=event['cpu']):
                issues.append('missing switch transition')
                a,_,_=state[prev]; state[prev]=(a,'unknown',None)
            transition(prev,ns,event['prev_state'])
            if nxt in state and state[nxt][1] in ('running','non_runnable'):
                issues.append('missing wakeup or duplicate running task')
                a,_,_=state[nxt]; state[nxt]=(a,'unknown',None)
            transition(nxt,ns,'running',event['cpu'])
        elif kind=='wakeup':
            key=tuple(event['task'])
            require(key in state,'unknown wakeup task')
            if state[key][1]!='running': transition(key,ns,'runnable')
        else: raise ValueError('unknown scheduler event')
        cpu_conflicts(ns)
    for key,(a,s,cpu) in state.items():
        intervals[key].append(dict(start_ns=a,stop_ns=tasks[key]['stop_ns'],state=s,cpu=cpu))
    return intervals,issues


def clipped(intervals,start,stop):
    totals=dict.fromkeys(('running','runnable','non_runnable','unknown'),0); raw=[]
    for row in intervals:
        a,b=max(start,row['start_ns']),min(stop,row['stop_ns'])
        if a<b:
            raw.append(dict(row,start_ns=a,stop_ns=b)); totals[row['state']]+=b-a
    totals['unknown']+=stop-start-sum(totals.values())
    return dict(totals=totals,intervals=raw,complete=totals['unknown']==0)


def account(invocations, records, capture=None):
    require(isinstance(invocations,list) and isinstance(records,list),'malformed input')
    indexed=defaultdict(list); dispatches=defaultdict(list)
    for index,r in enumerate(records):
        require(isinstance(r,dict) and r.get('version')==1 and r.get('edge') in ('enter','exit','publication'),'malformed supplemental record')
        require(all(integer(r.get(k)) for k in ('ns','pid','tid','dispatch','parent','publication')) and r['pid']>0 and r['tid']>0,'malformed supplemental identity')
        require(isinstance(r.get('invocation'),str),'missing invocation-local identity')
        r=dict(r,raw_index=index)
        key=(r['invocation'],r['pid'],r['tid'],r['dispatch'])
        dispatches[key].append(r)
        if r['edge']=='publication': indexed[r['invocation'],r['pid'],r['publication']].append(r)
    spans={}; issues=[]
    for key,rs in dispatches.items():
        enters=[r for r in rs if r['edge']=='enter']; exits=[r for r in rs if r['edge']=='exit']
        if len(enters)!=1 or len(exits)!=1 or enters[0]['ns']>exits[0]['ns'] or enters[0]['parent']!=exits[0]['parent']:
            issues.append(dict(dispatch=key,reason='missing/duplicate dispatch boundary')); continue
        spans[key]=(enters[0],exits[0])
    for key,(entry,exit) in spans.items():
        if entry['parent']:
            parent=spans.get((*key[:3],entry['parent']))
            if parent is None or not parent[0]['ns']<=entry['ns']<=exit['ns']<=parent[1]['ns']:
                issues.append(dict(dispatch=key,reason='invalid nested dispatch'))
    timelines={}; sched_issues=[]
    if capture is not None:
        clocks=[v['clock'] for v in invocations]
        require(clocks and all(c==clocks[0] for c in clocks),'incompatible invocation clocks')
        timelines,sched_issues=scheduler(capture,clocks[0])
    rows=[]; seen=set()
    for invocation in invocations:
        name=invocation['invocation']; require(isinstance(name,str) and name not in seen,'duplicate invocation'); seen.add(name)
        report=invocation['accounting']; require(not report['issues'],'blocked v4 accounting')
        for handoff in report['handoffs']:
            identity=handoff['identity']; pid,pub=identity['pid'],identity['publication']
            links=indexed[name,pid,pub]; row=dict(invocation=name,identity=identity,handoff=handoff,links=links,scheduler='unavailable')
            candidates=[]
            for link in links:
                key=(name,pid,link['tid'],link['dispatch'])
                if key in spans:
                    a,b=spans[key]
                    if a['ns']<=link['ns']<=b['ns']: candidates.append((link,a,b))
            row['link_status']='linked' if len(links)==len(candidates)==1 else 'ambiguous_or_missing'
            if row['link_status']=='linked':
                link,a,b=candidates[0]; row['dispatch']=dict(entry=a,exit=b)
                callbacks=[s for s in report['spans'] if s['operation']=='callback_execution' and s['begin']['pid']==pid and s['begin']['publication']==pub]
                require(len(callbacks)==1,'missing/duplicate callback accounting')
                callback=callbacks[0]['begin']; require(callback['tid']==link['tid'] and link['ns']<=callback['ns']<=b['ns'],'callback link mismatch')
                row['dispatch_to_callback_ns']=callback['ns']-a['ns']
                row['callback_entry']=callback
                enqueues=[s for s in report['spans'] if s['operation']=='enqueue_call' and s['begin']['pid']==pid and s['begin']['publication']==pub]
                require(len(enqueues)==1,'missing/duplicate invoke accounting')
                invoke=enqueues[0]
                row['invoke_return']=invoke['end']
                row['invoke_return_to_dispatch_ns']=a['ns']-invoke['stop']
                row['callback_before_invoke_return']=callback['ns']<invoke['stop']
                if capture is not None:
                    matches=[v for k,v in timelines.items() if k[:2]==(pid,link['tid']) and v[0]['start_ns']<=a['ns'] and v[-1]['stop_ns']>=callback['ns']]
                    row['scheduler']=clipped(matches[0] if len(matches)==1 else [],a['ns'],callback['ns'])
                    row['scheduler']['complete'] &= not sched_issues
                    start,stop=invoke['start'],callback['ns']
                    require(start<=stop,'callback precedes invocation')
                    row['thread_accounting']=[]
                    for tid in sorted({invoke['begin']['tid'],callback['tid']}):
                        matches=[v for k,v in timelines.items() if k[:2]==(pid,tid) and v[0]['start_ns']<=start and v[-1]['stop_ns']>=stop]
                        value=clipped(matches[0] if len(matches)==1 else [],start,stop)
                        value['complete'] &= not sched_issues
                        row['thread_accounting'].append(dict(tid=tid,**value))
                    row['scheduler']['complete'] &= all(t['complete'] for t in row['thread_accounting'])
            rows.append(row)
    require(all(r['invocation'] in seen for r in records),'unknown invocation records')
    return dict(rows=rows,dispatches=[dict(key=k,records=v) for k,v in dispatches.items()],issues=issues,
                scheduler_issues=sched_issues, scheduler_available=capture is not None,
                attribution_complete=bool(rows) and capture is not None and not issues and not sched_issues and all(r['link_status']=='linked' and isinstance(r['scheduler'],dict) and r['scheduler']['complete'] for r in rows),
                interpretation='Boundary accounting only; exact queue insertion unavailable. Overlaps are non-additive; non-runnable time does not establish blocking cause.')


def analyze(accounting,supplemental,capture,output):
    inputs=[accounting,supplemental]+([capture] if capture else [])
    o.fresh(output,*inputs); before={}; result=dict(status='blocked')
    try:
        require(all(path.absolute()==path.resolve() for path in inputs),'symlink input ancestors refused')
        before={str(path):o.digest(path) for path in inputs}
        result.update(account(o.read(accounting),o.read(supplemental),o.read(capture) if capture else None),status='complete')
    except (OSError,ValueError,KeyError,TypeError,IndexError) as error: result['failure']=str(error)
    finally:
        checks={}
        for path in inputs:
            try: checks[str(path)]=dict(passed=o.digest(path)==before.get(str(path)))
            except OSError as error: checks[str(path)]=dict(passed=False,failure=str(error))
        if not all(c['passed'] for c in checks.values()): result['status']='blocked'
        o.write(output/'integrity.json',dict(before=before,final_checks=checks))
        o.write(output/'assessment.json',result); o.write(output/'scheduler-contract.json',CONTRACT); o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('accounting','supplemental','output'): parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--scheduler',type=Path)
    args=parser.parse_args()
    result=analyze(args.accounting,args.supplemental,args.scheduler,args.output)
    print(result['status']); sys.exit(result['status']!='complete')
