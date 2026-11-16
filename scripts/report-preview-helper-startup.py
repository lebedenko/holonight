#!/usr/bin/env python3
"""Strict offline replay for the sealed private helper-startup experiment."""
import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    value=importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
r=module('helper_report_runner','run-preview-helper-startup.py')
a=module('helper_span_analyzer','analyze-preview-helper-startup.py')
p=module('helper_endpoint_report','report-preview-predecode.py')
o,require,read,write=r.o,r.require,r.read,r.write
COMMON=('runtime_lease_resolution','launcher_checks','command_environment_setup','process_start',
        'wait_for_started','scope_discovery_polling','limit_verification','gate_write_flush',
        'readiness_marker_receive','final_bookkeeping')
SESSION=('session_readiness','session_readiness_length','session_readiness_payload_receive','session_readiness_control_validation')


def strict_boundaries(records,identity,clock):
    threads=defaultdict(list); seen=set()
    for event in records:
        require(event['invocation']==identity,'missing/foreign invocation')
        require((event['host'],event['boot'],event['clock'])==
                (clock['provenance']['host'],clock['provenance']['boot_id'],clock['name']),'host/boot/clock mismatch')
        require(event['runtime_generation'] is None,'unproven runtime-generation identity')
        threads[event['pid'],event['tid']].append(event)
    for events in threads.values():
        stack=[]; previous=-1
        for e in events:
            require(e['ns']>=previous,'misordered helper thread'); previous=e['ns']
            key=e['pid'],e['span']
            if e['edge']=='begin':
                require(key not in seen,'duplicate/cross-thread span'); seen.add(key)
                require(e['outcome']=='unavailable','invalid begin outcome')
                require(e['parent']==(stack[-1]['span'] if stack else None),'invalid thread nesting')
                require(bool(stack)==(e['operation']!='preparation'),'invalid preparation root')
                stack.append(e)
            else:
                require(stack and stack[-1]['span']==e['span'],'unbalanced helper exit')
                begin=stack.pop()
                require(all(begin[k]==e[k] for k in (*a.IDENTITIES,'span','parent','operation')),'boundary identity mismatch')
                require(e['outcome'] in ('returned','exception'),'invalid end outcome')
        require(not stack,'missing helper boundary')


def required_operations(window,variant):
    root=window['begin']; rows=window['spans']
    require(root['parent'] is None,'nested preparation')
    names=[s['operation'] for s in rows]
    require(len(names)==len(set(names)),'duplicate preparation operation')
    require(all(s['end']['outcome'] in ('returned','exception') for s in rows),'invalid operation outcome')
    if window['end']['outcome']=='returned':
        expected=set(COMMON)|({'receive_setup'} if variant=='A' else set(SESSION))
        require(set(names)==expected,'missing/unexpected successful preparation operations')
        require(all(s['end']['outcome']=='returned' for s in rows),'successful root has exceptional child')
    else:
        # Exceptional/cancelled paths retain exactly the scopes they reached.
        require(set(names)<=set(COMMON)|({'receive_setup'} if variant=='A' else set(SESSION)),
                'foreign exceptional operation')
    by_name={s['operation']:s for s in rows}
    for s in rows:
        parent=by_name['session_readiness']['span'] if s['operation'] in SESSION[1:] else root['span']
        require(s['parent']==parent,'source operation parent mismatch')
    linear=[by_name[n] for n in (*COMMON[:7],*(['receive_setup'] if variant=='A' else []),*COMMON[7:]) if n in by_name]
    require(all(x['stop']<=y['start'] for x,y in zip(linear,linear[1:])),'source operation ordering mismatch')


def bind_lifecycle(window,lifecycle,events):
    e=window['begin']; candidates=[]
    spans=[s for row in lifecycle['accounting'] for s in row['timeline']]
    spans+=lifecycle['unassigned']
    for s in spans:
        if s['phase']!='helper_prepare': continue
        if all(s[edge].get(k)==(e[k] or 0) for edge in ('begin','end')
               for k in ('pid','tid','service','observation','job','worker','preparation')):
            candidates.append(s)
    require(len(candidates)==1,'missing/ambiguous v3 helper preparation binding')
    legacy=candidates[0]
    require(legacy['start']<=window['begin']['ns']<=legacy['stop'] and
            legacy['start']<=window['end']['ns'],'disjoint helper lifecycle boundaries')
    classification='setup' if legacy.get('cause')=='setup_activity' else legacy.get('role')
    require(classification in ('setup','demand','standby'),'unavailable helper lifecycle classification')
    if classification=='demand':
        if e['preparation'] is not None:
            selected=[event for event in events if event['phase']=='selected_worker' and
                      all(event.get(k)==(e[k] or 0) for k in ('pid','service','observation','worker','preparation'))]
        else:
            # A's one-shot lifecycle has no selected_worker or preparation ID.
            # Its explicit demand job/worker identifies the helper; retain the missing ID.
            selected=[event for event in events if event['phase']=='demand_dispatch' and event['edge']=='begin' and
                      all(event.get(k)==(e[k] or 0) for k in ('pid','service','observation','job','worker','preparation'))]
        require(len(selected)==1,'missing/ambiguous selected preparation identity')
    return dict(classification=classification,legacy=legacy,runtime_generation=None,
                supplemental_after_legacy_ns=max(0,window['end']['ns']-legacy['stop']))


def bind_scheduler(spans,capture):
    """Retain global startup issues; gate the actual preparation intervals."""
    timelines,issues=a.s.scheduler(capture,capture['clock'])
    require(capture.get('export_complete') is True and not capture.get('diagnostics') and
            not any(event['kind']=='loss' for event in capture['events']),
            'scheduler loss/incomplete export')
    require(not any(issue in ('capture loss','incomplete export') for issue in issues),'scheduler capture incomplete')
    for span in spans:
        # The original reconciler already makes affected intervals unknown. Unrelated
        # startup warnings do not invalidate fully reconciled target intervals.
        span['scheduler']=a.scheduler_span(span,capture,(timelines,[]))
        span['scheduler']['global_issues']=issues
    return issues


def invocation(package,entry,index,execution,replay=False,destination=None):
    row=entry['invocation']; target=Path(entry['argv'][-1])
    require(target==execution/'observations'/f'{index:03}.json','invocation destination mismatch')
    samples=read(target)['samples']; lifecycle=read(target.with_suffix('.v3.json'))
    text=target.with_suffix('.stderr').read_text()+'\n'+target.with_suffix('.stdout').read_text()
    legacy_events,_,legacy_issues=o.old.smoke.analysis.parse_trace(text,str(target))
    require(not legacy_issues,'legacy trace parsing failed')
    clock=read(execution/'preregistration.json')['clock']
    context=dict(arm=row['arm'],warmup=row['warmup'],block=row['block'],fixture=row['fixture'],invocation=entry['identity'])
    mode='baseline' if row['arm']=='baseline' else 'instrumented'
    citations=[c for c in read(package/'probe-to-source.json') if Path(c['file']).is_relative_to(package/mode/row['variant'])]
    for c in citations:
        path=Path(c['file'])
        require(o.digest(path)==c['sha256'] and path.read_text().splitlines()[c['line']-1]==c['text'],'source probe drift')
    capture=None
    if row['arm']=='captured':
        directory=execution/f'recording-{index:03}'
        records,issues=a.parse(text,str(target.with_suffix('.stderr')))
        require(not issues,'invalid helper records')
        require(records==read(directory/'task-identities.json'),'scheduler identity evidence mismatch')
        capture=r.r.n.normalize((directory/'perf-export.stdout').read_text(),read(directory/'recording-metadata.json'),
                                 records,str(directory/'perf-export.stdout'))
        require(capture==read(directory/'scheduler.json'),'scheduler replay mismatch')
    result=a.account(text,str(target.with_suffix('.stderr')),row['variant'],samples,context,capture,citations)
    require(result['status']=='complete','helper analyzer blocked')
    strict_boundaries(result['records'],entry['identity'],clock)
    if capture is not None: result['scheduler_issues']=bind_scheduler(result['spans'],capture)
    if mode=='instrumented':
        require(result['windows'] and not result['unavailable'],'missing supplemental preparations/boundaries')
        for span in result['spans']:
            require(span['source_citations'],'operation source probe missing')
        for window in result['windows']:
            required_operations(window,row['variant'])
            window['lifecycle_binding']=bind_lifecycle(window,lifecycle,legacy_events)
            if capture is not None and window['end']['outcome']=='returned':
                for span in result['spans']:
                    if span['begin']['preparation']==window['begin']['preparation'] and span['pid']==window['begin']['pid']:
                        require(span['scheduler']['available'],'incomplete required preparation scheduler coverage')
    endpoints=p.b.g.endpoint_rows(read(target.with_suffix('.v4.json')),row['variant'],row['fixture'],len(samples))
    require(len(endpoints)==2*len(samples),'endpoint population mismatch')
    for endpoint in endpoints:
        endpoint.update(invocation_index=index,block=row['block'],arm=row['arm'],warmup=row['warmup'],
            harness_latency_ns=samples[endpoint['observation']-1]['first_ms' if endpoint['endpoint']=='pixels' else 'final_ms']*1e6)
    result.update(endpoints=endpoints,lifecycle=lifecycle)
    path=destination or target.with_suffix('.helper.json')
    if replay: require(read(path)==result,'strict helper replay mismatch')
    else: write(path,result)
    return result


def summarize(endpoints):
    grouped=defaultdict(list)
    for e in endpoints:
        if e['warmup']: continue
        for block in ('pooled',e['block']): grouped[e['variant'],e['arm'],e['endpoint'],block].append(e['harness_latency_ns'])
    return [dict(variant=v,arm=arm,endpoint=e,block=b,latency_ns=p.stats(values))
            for (v,arm,e,b),values in sorted(grouped.items(),key=lambda x:str(x[0]))]


def effects(summary):
    rows=[]
    for variant in ('A','C'):
        for endpoint in ('pixels','metadata'):
            for left,right in (('baseline','instrumented'),('instrumented','captured')):
                differences=[]
                for block in range(5):
                    cell={r['arm']:r['latency_ns']['median'] for r in summary if
                          (r['variant'],r['endpoint'],r['block'])==(variant,endpoint,block)}
                    difference=cell[right]-cell[left]; differences.append(difference)
                    rows.append(dict(variant=variant,endpoint=endpoint,left=left,right=right,block=block,signed_block_median_difference_ns=difference))
                rows.append(dict(variant=variant,endpoint=endpoint,left=left,right=right,block='block_medians',
                                 signed_block_median_difference_ns=statistics.median(differences)))
    return rows


def report(package,built,execution,output):
    def work(result):
        r.check_package(package); o.check_output(built); o.check_output(execution)
        assessment=read(execution/'assessment.json')
        write(output/'evidence.json',dict(package=str(package),built=str(built),execution=str(execution),
            execution_seal=o.digest(execution/'seal.json'),assessment=assessment))
        if assessment['status']!='complete':
            partial=[]
            for saved in assessment['invocations']:
                entry=saved['entry']; target=Path(entry['argv'][-1])
                if not all(target.with_suffix(suffix).exists() for suffix in ('.json','.process.json','.v3.json','.v4.json')): continue
                o.validate(target,dict(entry['invocation'],mode='v4'),read(target.with_suffix('.process.json')),1000,replay=True)
                partial.append(invocation(package,entry,saved['index'],execution,
                    destination=output/f"partial-{saved['index']:03}.json"))
            write(output/'partial-accounting.json',partial)
            result.update(status='blocked',failure=assessment.get('failure','execution blocked'),
                          replayed_invocations=len(partial),original_launched=assessment['launched'],
                          original_unexecuted=assessment['unexecuted'])
            (output/'REPORT.md').write_text('Blocked attempt: '+str(assessment['launched'])+' invocations launched; '+
                str(assessment['unexecuted'])+' unexecuted. No measured blocks ran.\n\nOriginal failure: '+assessment.get('failure','')+
                '\n\nCorrected offline identity binding replayed '+str(len(partial))+' retained invocations without running processes. '
                'The original attempt remains blocked. Supplemental bookkeeping can end after the v3 helper interval; '
                'both intervals and their exact identities are retained. No optimization selected; qualification remains failed at 78/80 gates.\n')
            return
        require(read(execution/'integrity.json')['passed'],'execution integrity failed')
        require(all(c['passed'] for c in read(execution/'execution-final-checks.json').values()),'execution final gates failed')
        prereg=read(execution/'preregistration.json')
        require(prereg['protocol']==r.v.protocol() and prereg['built_seal']==o.digest(built/'seal.json'),'preregistration drift')
        commands=r.planned_commands(built,Path(prereg['protected_runtime']),execution/'observations')
        require(commands==prereg['commands'] and len(assessment['invocations'])==36,'schedule mismatch')
        endpoints=[]; accounts=[]
        for index,(entry,saved) in enumerate(zip(commands,assessment['invocations'])):
            require(saved['entry']==entry and saved['status']=='passed' and saved['index']==index,'incomplete invocation')
            target=Path(entry['argv'][-1])
            o.validate(target,dict(entry['invocation'],mode='v4'),read(target.with_suffix('.process.json')),1000,replay=True)
            account=invocation(package,entry,index,execution,replay=True)
            accounts.append(account); endpoints.extend(account['endpoints'])
        measured=[e for e in endpoints if not e['warmup']]
        require(len(measured)==300 and sum(len(a['original_samples']) for a in accounts[6:])==150,'measured population mismatch')
        require(sum(len(a['original_samples']) for a in accounts[:6])==6,'warmup population mismatch')
        summary=summarize(measured)
        write(output/'accounting.json',accounts); write(output/'endpoints.json',endpoints)
        write(output/'distributions.json',summary); write(output/'effects.json',effects(summary))
        (output/'REPORT.md').write_text('Complete: 150 measured observations, 300 measured endpoints, six excluded warm-ups.\n\n'
            'Setup, standby and selected demand preparations remain separate in accounting.json. Inclusive spans overlap; clipped unions '
            'and parent-exclusive intervals are retained. Running time includes instrumentation cost. Non-runnable time identifies no '
            'blocking cause. Runtime-generation identity remains unavailable. Signed block-median differences are descriptive; no '
            'overhead subtraction, cross-population quantile subtraction, optimization selection or qualification reassessment. '
            'Qualification remains failed at 78/80 gates.\n')
        result.update(status='complete',measured_observations=150,endpoints=300,warmup_observations=6)
    return r.action(output,[package,built,execution],work)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('prepared','built','execution','output'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    result=report(*(getattr(args,k).absolute() for k in ('prepared','built','execution','output')))
    print(json.dumps(result)); sys.exit(result['status']!='complete')
