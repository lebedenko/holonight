#!/usr/bin/env python3
"""Offline helper-startup spans and optional normalized scheduler attribution."""
import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    value=importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
p=module('helper_preparation','prepare-preview-helper-startup.py')
s=module('helper_scheduler','analyze-preview-delivery-scheduler.py')
d=module('helper_delivery','analyze-preview-delivery-tracing.py')
o,require=p.o,p.require
IDENTITIES=('invocation','host','boot','clock','pid','tid','service','observation','job','worker',
            'preparation','request_generation','runtime_generation')
NUMBERS=('service','observation','job','worker','preparation','request_generation','span','parent')
OPERATIONS={'preparation','runtime_lease_resolution','launcher_checks','command_environment_setup',
            'process_start','wait_for_started','scope_discovery_polling','limit_verification','receive_setup',
            'gate_write_flush','readiness_marker_receive','session_readiness','session_readiness_length',
            'session_readiness_payload_receive','session_readiness_control_validation','final_bookkeeping'}
FIELDS={'version','ns',*IDENTITIES,'span','parent','operation','edge','outcome'}


def union(parts):
    merged=[]
    for left,right in sorted((a,b) for a,b in parts if a<b):
        if merged and left<=merged[-1][1]: merged[-1][1]=max(right,merged[-1][1])
        else: merged.append([left,right])
    return merged


def subtract(left,right,parts):
    cursor=left; result=[]
    for a,b in union((max(left,a),min(right,b)) for a,b in parts):
        if cursor<a: result.append([cursor,a])
        cursor=max(cursor,b)
    if cursor<right: result.append([cursor,right])
    return result


def duration(parts): return sum(b-a for a,b in parts)


def unique(pairs):
    result={}
    for k,v in pairs:
        require(k not in result,'duplicate JSON key'); result[k]=v
    return result


def parse(text,source):
    records=[]; issues=[]
    for line,raw in enumerate(text.splitlines(),1):
        if 'HELPER_STARTUP' not in raw: continue
        ref=dict(file=source,line=line,text=raw)
        try:
            require(raw.startswith('HELPER_STARTUP '),'noncanonical prefix')
            e=json.loads(raw[len('HELPER_STARTUP '):],object_pairs_hook=unique)
            require(set(e)==FIELDS and type(e['version']) is int and e['version']==1,'invalid schema')
            for k in ('ns',*NUMBERS):
                if isinstance(e[k],str):
                    require(e[k].isdigit() and str(int(e[k]))==e[k],'noncanonical integer'); e[k]=int(e[k])
            require(type(e['ns']) is int and e['ns']>=0,'invalid timestamp')
            require(all(type(e[k]) is int and e[k]>0 for k in ('pid','tid','span')),'invalid process/thread/span')
            require(all(e[k] is None or type(e[k]) is int and e[k]>0 for k in NUMBERS),'invalid identity')
            require(e['runtime_generation'] is None or isinstance(e['runtime_generation'],str) and bool(e['runtime_generation']), 'invalid runtime identity')
            require(all(e[k] is None or isinstance(e[k],str) and bool(e[k]) for k in ('invocation','host','boot')), 'invalid external identity')
            require(e['clock']=='CLOCK_MONOTONIC' and e['operation'] in OPERATIONS,'invalid clock/operation')
            require(e['edge'] in ('begin','end') and e['outcome'] in ('unavailable','returned','exception'),'invalid boundary')
            records.append(dict(e,raw=ref))
        except (ValueError,TypeError,KeyError) as error: issues.append(dict(raw=ref,reason=str(error)))
    return records,issues


def scheduler_span(span,capture,normalized=None):
    unavailable=lambda reason:dict(available=False,reason=reason)
    if capture is None: return unavailable('scheduler evidence unavailable')
    e=span['begin']; clock=capture.get('clock',{})
    if not (e['host'] and e['boot'] and clock.get('name')==e['clock'] and
            isinstance(clock.get('provenance'),dict) and clock['provenance'].get('host')==e['host'] and
            clock['provenance'].get('boot_id')==e['boot']):
        return unavailable('clock/host/boot agreement unavailable')
    try:
        intervals,issues=normalized if normalized is not None else s.scheduler(capture,clock)
        if intervals is None: return unavailable(str(issues))
        if issues or capture.get('diagnostics') or not capture.get('export_complete',True):
            return unavailable('scheduler loss/incomplete evidence: '+str(issues))
        tasks=[t for t in capture['tasks'] if t['key'][:2]==[e['pid'],e['tid']] and
               t['start_ns']<=span['start'] and t['stop_ns']>=span['stop']]
        if len(tasks)!=1: return unavailable('task lifetime mismatch')
        task=tasks[0]
        # Require explicit evidence binding the same invocation and both boundaries.
        identity=task.get('identity_evidence',[])
        if not all(any(r.get('invocation')==e['invocation'] and e['invocation'] is not None and
                       r.get('pid')==e['pid'] and r.get('tid')==e['tid'] and r.get('ns')==ns
                       for r in identity) for ns in (span['start'],span['stop'])):
            return unavailable('task invocation identity evidence unavailable')
        result=s.clipped(intervals[tuple(task['key'])],span['start'],span['stop'])
        return dict(available=result['complete'],task=task,**result,
                    limitation='Non-runnable time identifies no blocking cause.')
    except (ValueError,KeyError,TypeError) as error: return unavailable(str(error))


def account(text,source,variant,samples,context,capture=None,source_citations=None):
    require(variant in ('A','C'),'foreign variant')
    require(context['arm'] in ('baseline','instrumented','captured') and type(context['warmup']) is bool and
            context['fixture']=='3200x2400.png' and isinstance(context['invocation'],str) and bool(context['invocation']),
            'foreign population/context')
    require((context['block'] is None if context['warmup'] else type(context['block']) is int and 0<=context['block']<5), 'invalid block')
    require(len(samples)==(1 if context['warmup'] else 5),'sample population mismatch')
    records,issues=parse(text,source); unavailable=[]; spans=[]
    if not records: unavailable.append(dict(reason='no supplemental records'))
    for e in records:
        if e['invocation'] is not None and e['invocation']!=context['invocation']:
            issues.append(dict(reason='invocation identity mismatch',record=e))
        if e['observation'] is not None and not 1<=e['observation']<=len(samples):
            issues.append(dict(reason='observation population mismatch',record=e))
        if variant=='A' and e['operation'].startswith('session_readiness'):
            issues.append(dict(reason='A cannot have C session readiness',record=e))
    groups=defaultdict(list)
    for e in records: groups[e['pid'],e['span']].append(e)
    for key,rs in groups.items():
        begin=[r for r in rs if r['edge']=='begin']; end=[r for r in rs if r['edge']=='end']
        if len(begin)>1 or len(end)>1:
            issues.append(dict(reason='duplicate span boundary',records=rs)); continue
        if not begin or not end:
            unavailable.append(dict(reason='missing span boundary',records=rs)); continue
        b,e=begin[0],end[0]
        if any(b[k]!=e[k] for k in (*IDENTITIES,'operation','parent')) or b['ns']>e['ns'] or rs[0]['edge']!='begin':
            issues.append(dict(reason='span identity/order mismatch',records=rs)); continue
        spans.append(dict(pid=b['pid'],span=b['span'],parent=b['parent'],operation=b['operation'],
                          start=b['ns'],stop=e['ns'],inclusive_ns=e['ns']-b['ns'],begin=b,end=e))
    normalized=None
    if capture is not None:
        try: normalized=s.scheduler(capture,capture.get('clock',{}))
        except (ValueError,KeyError,TypeError) as error: normalized=(None,str(error))
    indexed={(r['pid'],r['span']):r for r in spans}
    for row in spans:
        node=row; ancestors=set()
        while node is not None:
            key=(node['pid'],node['span'])
            if key in ancestors:
                issues.append(dict(reason='cyclic parent identity',span=row['span'])); break
            ancestors.add(key)
            node=indexed.get((node['pid'],node['parent'])) if node['parent'] is not None else None
        if row['parent'] is not None:
            parent=indexed.get((row['pid'],row['parent']))
            if parent is None: unavailable.append(dict(reason='parent boundary unavailable',span=row['span']))
            elif not (parent['start']<=row['start']<=row['stop']<=parent['stop'] and
                      all(parent['begin'][k]==row['begin'][k] for k in IDENTITIES)):
                issues.append(dict(reason='parent identity/containment mismatch',span=row['span']))
        children=[r for r in spans if r['pid']==row['pid'] and r['parent']==row['span']]
        row['child_union']=union((max(row['start'],r['start']),min(row['stop'],r['stop'])) for r in children)
        missing_child=any(any(e['pid']==row['pid'] and e['parent']==row['span'] for e in item.get('records',[])) for item in unavailable)
        row['exclusive_intervals']=None if missing_child else subtract(row['start'],row['stop'],row['child_union'])
        row['exclusive_ns']=None if missing_child else duration(row['exclusive_intervals'])
        row['scheduler']=scheduler_span(row,capture,normalized)
        row['source_citations']=[c for c in source_citations or [] if '"'+row['operation']+'"' in c['text']]
    roots=[r for r in spans if r['operation']=='preparation']
    windows=[]
    for root in roots:
        eligible=[]
        for row in spans:
            node=row; seen=set()
            while node['parent'] is not None and (node['pid'],node['span']) not in seen:
                seen.add((node['pid'],node['span']))
                node=indexed.get((node['pid'],node['parent']))
                if node is None: break
                if node is root: eligible.append(row); break
        clipped=union((max(root['start'],r['start']),min(root['stop'],r['stop'])) for r in eligible)
        windows.append(dict(root_span=root['span'],begin=root['begin'],end=root['end'],spans=eligible,
                            clipped_union=clipped,covered_ns=duration(clipped),
                            uncovered=subtract(root['start'],root['stop'],clipped)))
    summaries=[]
    for operation in sorted({r['operation'] for r in spans}):
        values=[r['inclusive_ns'] for r in spans if r['operation']==operation]
        summaries.append(dict(operation=operation,count=len(values),minimum_ns=min(values),median_ns=statistics.median(values),maximum_ns=max(values)))
    # Original harness predicates and existing lifecycle validation remain authoritative.
    historical=d.analyze(text,source,variant,samples)
    if not historical['assessment_available']: issues.append(dict(reason='historical validation blocked',issues=historical['issues']))
    if context['arm']=='baseline' and records: issues.append(dict(reason='baseline has supplemental instrumentation'))
    return dict(status='blocked' if issues else 'complete',assessment_available=not issues,variant=variant,
                population=context,original_samples=samples,records=records,spans=spans,windows=windows,
                source_citations=source_citations,source_availability='bound' if source_citations else 'unavailable',
                block_summaries=summaries,issues=issues,unavailable=unavailable,historical=historical,
                limitation='Inclusive spans and overlapping unions are non-additive. Missing boundaries are unavailable. '
                'No overhead subtraction, optimization selection or qualification reassessment.')


def run(trace,samples,context,variant,output,scheduler=None,prepared=None):
    paths=[trace,samples,context]+([scheduler] if scheduler else [])+([prepared] if prepared else [])
    o.fresh(output,*paths); tracked={}; roots={}; result=dict(status='blocked')
    try:
        require(prepared is not None,'sealed preparation required for source citations')
        o.check_output(prepared)
        require(o.read(prepared/'assessment.json')['status']=='prepared','blocked preparation')
        roots[str(prepared)]=o.inventory(prepared)
        tracked={str(p):o.digest(p) for p in paths if p!=prepared}
        tracked[str(prepared/'seal.json')]=o.digest(prepared/'seal.json')
        citations=o.read(prepared/'probe-to-source.json')
        arm=o.read(context)['arm']
        base=prepared/('baseline' if arm=='baseline' else 'instrumented')/variant
        citations=[c for c in citations if Path(c['file']).is_relative_to(base)]
        require(bool(citations),'source citations unavailable')
        for citation in citations:
            path=Path(citation['file'])
            require(path==path.resolve() and o.digest(path)==citation['sha256'] and
                    path.read_text().splitlines()[citation['line']-1]==citation['text'],'source citation mismatch')
            tracked[str(path)]=citation['sha256']
        result=account(trace.read_text(),str(trace),variant,o.read(samples)['samples'],o.read(context),
                       o.read(scheduler) if scheduler else None,citations)
        o.write(output/'accounting.json',result)
    except p.ERRORS as error: result=dict(status='blocked',failure=str(error))
    finally:
        checks={}
        for name,digest in tracked.items():
            try: checks[name]=o.digest(Path(name))==digest
            except OSError: checks[name]=False
        for name,inv in roots.items():
            try: checks[name]=o.inventory(Path(name))==inv
            except OSError: checks[name]=False
        if not all(checks.values()): result.update(status='blocked',integrity_failure='input drift')
        o.write(output/'integrity.json',dict(consumed=tracked,before=roots,checks=checks,passed=all(checks.values())))
        o.write(output/'assessment.json',dict(status=result['status'],failure=result.get('failure'))); o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('trace','samples','context','output','prepared'): parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--variant',choices=('A','C'),required=True)
    parser.add_argument('--scheduler',type=Path)
    args=parser.parse_args()
    for name in ('trace','samples','context','output','prepared','scheduler'):
        if getattr(args,name) is not None: setattr(args,name,getattr(args,name).absolute())
    result=run(**vars(args)); print(result['status']); sys.exit(result['status']!='complete')
