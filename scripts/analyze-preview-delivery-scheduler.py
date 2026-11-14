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
CONTRACT = dict(version=2, supported_versions=[1,2], unresolved_external_identity='version 2 permits null TGID; idle key uses CPU as lifetime; export_complete false blocks attribution', clock=dict(name='CLOCK_MONOTONIC', provenance='explicit shared host/boot identity required'),
    bounds='start_ns <= stop_ns; complete coverage required',
    tasks='pid, tid, lifetime, start_ns, stop_ns; reuse requires disjoint lifetimes',
    initial='one state per live task at capture start: running (with cpu), runnable, non_runnable, unknown',
    events='ordered ns, cpu; switch: prev/next task lifetime keys and prev_state (runnable/non_runnable); wakeup: task lifetime key; loss: ns/count',
    task_key='[pid, tid, lifetime]', limitation='Non-runnable time does not identify a blocking cause. Overlapping endpoint/thread intervals are non-additive.')


def integer(value):
    return type(value) is int and value>=0


def scheduler(capture, clock):
    require(type(capture['version']) is int and capture['version'] in (1,2) and capture['clock']==clock and clock['name']=='CLOCK_MONOTONIC'
            and bool(clock['provenance']), 'clock mismatch or missing provenance')
    start,stop=capture['start_ns'],capture['stop_ns']
    require(integer(start) and integer(stop) and start<stop,'invalid capture bounds')
    tasks={}; intervals=defaultdict(list); state={}; issues=[]
    if capture.get('export_complete') is False: issues.append('incomplete export')
    for task in capture['tasks']:
        key=tuple(task['key']); require(len(key)==3 and all(integer(v) or (capture['version']==2 and i==0 and v is None) for i,v in enumerate(key)),'invalid task key')
        require(key not in tasks and integer(task['start_ns']) and integer(task['stop_ns']) and start<=task['start_ns']<task['stop_ns']<=stop,'invalid task lifetime')
        for other,t in tasks.items():
            require(key[0]==0 or key[1]!=other[1] or min(t['stop_ns'],task['stop_ns'])<=max(t['start_ns'],task['start_ns']), 'ambiguous task reuse')
        tasks[key]=task
        initial=task.get('initial','unknown')
        if initial=='running' and not integer(task.get('cpu')): initial='unknown'
        require(initial in ('running','runnable','non_runnable','unknown'),'invalid initial state')
        state[key]=(task['start_ns'],initial,task.get('cpu'))
    def transition(key,ns,new,cpu=None):
        require(key in tasks,'unknown task lifetime')
        t=tasks[key]; require(t['start_ns']<=ns<=t['stop_ns'],'event outside task lifetime')
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
            require(nxt in tasks and ns<tasks[nxt]['stop_ns'],'switch into terminated task')
            transition(nxt,ns,'running',event['cpu'])
        elif kind=='wakeup':
            key=tuple(event['task'])
            require(key in state and ns<tasks[key]['stop_ns'],'unknown or terminated wakeup task')
            if state[key][1]!='running': transition(key,ns,'runnable')
        else: raise ValueError('unknown scheduler event')
        cpu_conflicts(ns)
    for key,(a,s,cpu) in state.items():
        intervals[key].append(dict(start_ns=a,stop_ns=tasks[key]['stop_ns'],state=s,cpu=cpu))
    if capture['version']==2:
        for diagnostic in capture.get('diagnostics',[]):
            if diagnostic.get('reason')!='unparsed perf record':
                for key,rows in intervals.items():
                    if key[1]==diagnostic.get('tid') or list(key)==diagnostic.get('key'):
                        for row in rows: row.update(state='unknown',cpu=None)
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
        require(isinstance(r,dict) and type(r.get('version')) is int and r.get('version')==1 and r.get('edge') in ('enter','exit','publication'),'malformed supplemental record')
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
    # Validate the actual per-thread stack, including sibling overlap and ownership.
    threads=defaultdict(list)
    for rs in dispatches.values():
        for r in rs: threads[r['invocation'],r['pid'],r['tid']].append(r)
    invalid=set()
    used={}
    for key in dispatches:
        token=(key[0],key[1],key[3])
        if token in used and used[token]!=key:
            invalid.update((key,used[token])); issues.append(dict(dispatch=key,reason='cross-thread dispatch identity collision'))
        used[token]=key
    for thread,rs in threads.items():
        rs.sort(key=lambda r:r['raw_index'])
        stack=[]
        if any(y['ns']<x['ns'] for x,y in zip(rs,rs[1:])):
            issues.append(dict(thread=thread,reason='misordered thread records'))
            invalid.update((*thread,r['dispatch']) for r in rs)
        for r in sorted(rs,key=lambda x:(x['ns'],x['raw_index'])):
            key=(*thread,r['dispatch'])
            good=r['dispatch']>0
            if r['edge']=='enter':
                good &= r['publication']==0 and r['parent']==(stack[-1] if stack else 0) and r['dispatch'] not in stack
                stack.append(r['dispatch'])
            elif r['edge']=='exit':
                good &= r['publication']==0 and bool(stack) and stack[-1]==r['dispatch']
                if stack and stack[-1]==r['dispatch']: stack.pop()
            else:
                good &= r['parent']==0 and r['publication']>0 and bool(stack) and stack[-1]==r['dispatch']
            if not good:
                issues.append(dict(dispatch=key,reason='invalid nesting or publication ownership'))
                invalid.add(key)
        if stack:
            issues.append(dict(thread=thread,reason='unclosed dispatch'))
            invalid.update((*thread,d) for d in stack)
    for key in invalid: spans.pop(key,None)
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
                require(not any(k[:3]==key[:3] and k!=key and x['ns']<=callback['ns']<y['ns'] and x['ns']>=a['ns'] for k,(x,y) in spans.items()),'callback owned by nested dispatch')
                enqueues=[s for s in report['spans'] if s['operation']=='enqueue_call' and s['begin']['pid']==pid and s['begin']['publication']==pub]
                require(len(enqueues)==1,'missing/duplicate invoke accounting')
                invoke=enqueues[0]
                row['invoke_return']=invoke['end']
                row['invoke_return_to_dispatch_ns']=a['ns']-invoke['stop']
                row['invoke_return_to_callback_ns']=callback['ns']-invoke['stop']
                row['callback_before_invoke_return']=callback['ns']<invoke['stop']
                if capture is not None:
                    matches=[v for k,v in timelines.items() if k[:2]==(pid,link['tid']) and v[0]['start_ns']<=a['ns'] and v[-1]['stop_ns']>=callback['ns']]
                    row['scheduler']=clipped(matches[0] if len(matches)==1 else [],a['ns'],callback['ns'])
                    row['scheduler']['complete'] &= len(matches)==1 and not any(i in sched_issues for i in ('capture loss','incomplete export'))
                    start,stop=invoke['stop'],callback['ns']
                    # Negative return-to-callback order is retained, never clipped into a positive window.
                    start=min(start,stop)
                    row['thread_accounting']=[]
                    for tid in sorted({invoke['begin']['tid'],callback['tid']}):
                        matches=[v for k,v in timelines.items() if k[:2]==(pid,tid) and v[0]['start_ns']<=start and v[-1]['stop_ns']>=stop]
                        value=clipped(matches[0] if len(matches)==1 else [],start,stop)
                        value['complete'] &= len(matches)==1 and not any(i in sched_issues for i in ('capture loss','incomplete export'))
                        parts={}
                        if invoke['stop']<callback['ns']:
                            for label,left,right in (('return_to_dispatch',invoke['stop'],max(invoke['stop'],a['ns'])),('dispatch_to_callback',max(invoke['stop'],a['ns']),callback['ns'])):
                                parts[label]=clipped(matches[0] if len(matches)==1 else [],left,right)
                        row['thread_accounting'].append(dict(tid=tid,parts=parts,**value))
                    row['scheduler']['complete'] &= all(t['complete'] for t in row['thread_accounting'])
            rows.append(row)
    known={(v['invocation'],h['identity']['pid'],h['identity']['publication']) for v in invocations for h in v['accounting']['handoffs']}
    for key in indexed:
        if key not in known: issues.append(dict(publication=key,reason='orphan publication'))
    require(all(r['invocation'] in seen for r in records),'unknown invocation records')
    return dict(rows=rows,dispatches=[dict(key=k,records=v) for k,v in dispatches.items()],issues=issues,
                scheduler_issues=sched_issues, scheduler_available=capture is not None,
                attribution_complete=bool(rows) and capture is not None and not issues and not any(i in sched_issues for i in ('capture loss','incomplete export')) and all(r['link_status']=='linked' and isinstance(r['scheduler'],dict) and r['scheduler']['complete'] for r in rows),
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
