#!/usr/bin/env python3
"""Normalize saved nanosecond perf script text, without launching processes.

Input format: perf script --ns -F comm,pid,tid,cpu,time,event,trace
             --show-task-events --show-lost-events
Metadata is saved by the recorder, not inferred from timestamp similarity.
"""
import argparse
import importlib.util
import re
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('scheduler_analysis',ROOT/'scripts/analyze-preview-delivery-scheduler.py')
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
o=a.o
# perf may render unknown sample-prefix identities as -1. Scheduler task
# identities still come exclusively from tracepoint payloads and explicit evidence.
SAMPLE=re.compile(r'^\s*(.*?)\s+(-1|\d+)\s*/\s*(-1|\d+)\s+\[(\d+)\]\s+(\d+)\.(\d{9}):\s+(sched:\w+):\s*(.*)$')


def normalize(text, metadata, identities=(), source='<saved perf export>'):
    o.require(metadata['clock']['name']=='CLOCK_MONOTONIC' and metadata['clock']['provenance'] and metadata['clock_verified'] is True, 'unverified recorder clock')
    o.require(isinstance(metadata['boot_before'],str) and metadata['boot_before'] and metadata['boot_before']==metadata['boot_after'], 'recording boot mismatch')
    provenance=metadata['clock']['provenance']
    if isinstance(provenance,dict): o.require(provenance.get('boot_id')==metadata['boot_before'],'recording clock provenance mismatch')
    start,stop=metadata['start_ns'],metadata['stop_ns']
    o.require(type(start) is int and type(stop) is int and start<stop,'invalid recorder bounds')
    tasks=[]; active={}; events=[]; raw=[]; diagnostics=[]; serial={}; exiting={}
    def task(tid,ns,cpu=None,birth=False):
        token=(tid,cpu if tid==0 else None)
        if token not in active:
            serial[token]=serial.get(token,0)+1
            # sched tracepoint pids are TIDs. No task-group identity is invented.
            key=[0 if tid==0 else None,tid,cpu if tid==0 else serial[token]]
            at=ns if birth or serial[token]>1 else start
            t=dict(key=key,start_ns=at,stop_ns=stop,initial='unknown')
            tasks.append(t); active[token]=t
        return active[token]
    previous=start
    for line_no,line in enumerate(text.splitlines(),1):
        if not line.strip() or line.startswith('#'): continue
        ref=dict(file=source,line=line_no,text=line)
        raw.append(ref)
        if re.search(r'PERF_RECORD_LOST(?:_SAMPLES)?\b|\bLOST\s+\d+\s+events\b',line,re.I):
            # Unknown location/count is still a global completeness blocker.
            count=re.search(r'(?:\blost\s*=\s*|\bLOST\s+)(\d+)',line,re.I)
            events.append(dict(kind='loss',ns=max(previous,start),count=max(1,int(count[1])) if count else 1,count_is_lower_bound=count is None,raw=ref)); continue
        m=SAMPLE.match(line)
        if not m and re.search(r'PERF_RECORD_(?:FORK|EXIT|COMM|MMAP2?|FINISHED_ROUND|FINISHED_INIT|THREAD_MAP|CPU_MAP|TIME_CONV)\b',line):
            # Synthetic metadata is retained verbatim. TGID remains unresolved unless
            # corroborated by publication records within a lifetime.
            continue
        if not m:
            diagnostics.append(dict(reason='unparsed perf record',raw=ref)); continue
        comm,pid,tid,cpu,sec,nsec,event,body=m.groups()
        ns=int(sec)*10**9+int(nsec); cpu=int(cpu)
        o.require(previous<=ns<stop and ns>=start,'misordered or truncated perf export')
        previous=ns
        fields=dict(re.findall(r'(\w+)=([^\s]+)',body))
        def number(key): return int(fields[key])
        if event=='sched:sched_switch':
            prev=task(number('prev_pid'),ns,cpu); nxt=task(number('next_pid'),ns,cpu)
            state=fields['prev_state']
            o.require(re.fullmatch(r'(?:R|[SDTtXZPIWK](?:\|[SDTtXZPIWK])*)\+?',state) is not None,'unknown previous-task state')
            events.append(dict(kind='switch',ns=ns,cpu=cpu,prev=prev, next=nxt,
                               prev_state='runnable' if state.startswith('R') else 'non_runnable',raw=ref))
            token=(number('prev_pid'),None)
            if token in exiting:
                prev['stop_ns']=ns
                active.pop(token,None); exiting.pop(token)
        elif event in ('sched:sched_wakeup','sched:sched_wakeup_new'):
            if fields.get('success','1')=='1': events.append(dict(kind='wakeup',ns=ns,cpu=cpu,task=task(number('pid'),ns,cpu),raw=ref))
        elif event=='sched:sched_process_fork':
            child=number('child_pid'); token=(child,None)
            if token in active:
                diagnostics.append(dict(reason='fork overlaps live task',tid=child,ns=ns,raw=ref))
                active[token]['stop_ns']=ns; active.pop(token)
            exiting.pop(token,None)
            task(child,ns,birth=True)
        elif event=='sched:sched_process_exit':
            t=task(number('pid'),ns,cpu)
            t['exit_ns']=ns; exiting[(number('pid'),None)]=t
        elif event=='sched:sched_process_exec':
            # Exec can change the TID; do not merge ambiguous lifetimes.
            if number('old_pid')!=number('pid'):
                diagnostics.append(dict(reason='exec identity change',tid=number('pid'),ns=ns,raw=ref))
        else: raise ValueError('unexpected tracepoint: '+event)
    for token,t in exiting.items():
        diagnostics.append(dict(reason='exit without final switch',tid=token[0],ns=t['exit_ns']))
    # Explicit publication records bind a target TID to its process in one lifetime.
    for t in tasks:
        if t['key'][0]==0: continue
        found={r['pid'] for r in identities if r['tid']==t['key'][1] and t['start_ns']<=r['ns']<t['stop_ns']}
        if len(found)==1:
            t['key'][0]=found.pop()
            t['identity_evidence']=[r for r in identities if r['tid']==t['key'][1] and t['start_ns']<=r['ns']<t['stop_ns']]
        elif len(found)>1: diagnostics.append(dict(reason='conflicting target identity',key=t['key']))
    for e in events:
        for field in ('prev','next','task'):
            if field in e: e[field]=e[field]['key'][:]
    return dict(version=2,clock=metadata['clock'],start_ns=start,stop_ns=stop,tasks=tasks,events=events,
                raw_records=raw,diagnostics=diagnostics,export_complete=not any(d['reason']=='unparsed perf record' for d in diagnostics),
                identity_policy='Unresolved external TGIDs remain null; idle lifetimes are per CPU.')


def convert(export, metadata, identities, output):
    inputs=[export,metadata,identities]; o.fresh(output,*inputs); before={}; result=dict(status='blocked')
    try:
        o.require(all(p.absolute()==p.resolve() for p in inputs),'symlink input refused')
        before={str(p):o.digest(p) for p in inputs}
        capture=normalize(export.read_text(),o.read(metadata),o.read(identities),str(export))
        o.write(output/'scheduler.json',capture); result['status']='complete'
    except (OSError,ValueError,KeyError,TypeError,IndexError) as error: result['failure']=str(error)
    finally:
        checks={}
        for p in inputs:
            try: checks[str(p)]=dict(passed=o.digest(p)==before.get(str(p)))
            except OSError as error: checks[str(p)]=dict(passed=False,failure=str(error))
        if not all(c['passed'] for c in checks.values()): result['status']='blocked'
        o.write(output/'integrity.json',dict(before=before,final_checks=checks)); o.write(output/'assessment.json',result); o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('export','metadata','identities','output'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args(); result=convert(args.export,args.metadata,args.identities,args.output)
    print(result); sys.exit(result['status']!='complete')
