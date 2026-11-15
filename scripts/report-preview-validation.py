#!/usr/bin/env python3
"""Replay private validation observations and scheduler lifetimes offline."""
import argparse
from bisect import bisect_left, bisect_right
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validation_report_runner',ROOT/'scripts/run-preview-validation.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
v,o,require,read,write=r.v,r.o,r.require,r.read,r.write
p=v.p
stats=p.stats
CONTEXT=('pid','tid','service','observation','job','worker','preparation','validation','span','parent','ordinal','operation')
CONTAINERS={'runtime','generation','file','nested_runtime'}
OPERATIONS=CONTAINERS | {'initial_path_manifest','manifest_parse','manifest_read','manifest_policy','record_prepare',
    'attributes','file_open','read_hash','digest_compare','required_files','inventory','protected_base',
    'selector_descriptors','protected_generation','generation_manifest_open_read','generation_manifest_parse_policy',
    'generation_manifest_digest','generation_final_identity'}


def records(target):
    def unique(pairs):
        result={}
        for key,value in pairs:
            require(key not in result,'duplicate validation JSON key')
            result[key]=value
        return result
    result=[]
    for path in (target.with_suffix('.stderr'),target.with_suffix('.stdout')):
        for number,line in enumerate(path.read_text().splitlines(),1):
            if line.startswith('VALIDATION '):
                result.append(dict(json.loads(line[len('VALIDATION '):],object_pairs_hook=unique),file=str(path),line=number,text=line))
    return result


def spans(events):
    """Validate actual thread stacks before pairing or aggregating any file events."""
    threads=defaultdict(list); seen=set(); paired=[]
    for e in events:
        require(type(e.get('version')) is int and e['version']==1 and e.get('edge') in ('begin','end') and e.get('operation') in OPERATIONS,
                'malformed validation record')
        require(all(type(e.get(k)) is int and e[k]>0 for k in ('pid','tid','span','validation')),'invalid validation identity')
        require(type(e.get('ns')) is int and e['ns']>=0 and type(e.get('parent')) is int and e['parent']>=0,
                'invalid validation timestamp/parent')
        require(type(e.get('ordinal')) is int and e['ordinal']>=-1,'invalid manifest ordinal')
        require(all(e.get(k) is None or type(e.get(k)) is int and e[k]>0 for k in ('service','observation','job','worker','preparation')),
                'invalid existing context')
        threads[e['pid'],e['tid']].append(e)
    for thread,rs in threads.items():
        stack=[]; previous=-1
        for e in rs:
            require(e['ns']>=previous,'misordered validation thread'); previous=e['ns']
            key=e['pid'],e['span']
            if e['edge']=='begin':
                require(key not in seen,'duplicate/cross-thread validation span'); seen.add(key)
                require(e['parent']==(stack[-1]['span'] if stack else 0),'invalid validation nesting')
                if e['operation'] in ('runtime','generation'):
                    require(e['validation']==e['span'] and e['ordinal']==-1,'invalid validation root')
                else:
                    require(stack and e['validation']==stack[-1]['validation'],'validation ownership mismatch')
                stack.append(e)
            else:
                require(stack and stack[-1]['span']==e['span'],'unbalanced validation exit')
                begin=stack.pop()
                require(all(begin[k]==e[k] for k in CONTEXT),'validation boundary ownership mismatch')
                require(e['outcome'] in ('returned','exception'),'invalid validation exit outcome')
                require(begin['outcome']=='unavailable','invalid validation entry outcome')
                paired.append(dict(operation=e['operation'],start=begin['ns'],stop=e['ns'],begin=begin,end=e,
                                   depth=len(stack),parent=e['parent'],ordinal=e['ordinal']))
        require(not stack,'unclosed validation span')
    return sorted(paired,key=lambda s:(s['start'],s['begin']['pid'],s['begin']['span']))


def mapped_files(selected,mapping):
    roots=[s for s in selected if s['operation']=='runtime']
    require(len(roots)==1,'missing/ambiguous runtime validation')
    files=[s for s in selected if s['operation']=='file']
    require(sorted(s['ordinal'] for s in files)==list(range(len(mapping))),'manifest file coverage mismatch')
    for file in files:
        require(file['begin']['parent']==roots[0]['begin']['span'],'file validation parent mismatch')
        children=[s for s in selected if s['begin']['parent']==file['begin']['span']]
        require([s['operation'] for s in children]==['record_prepare','attributes','file_open','read_hash','digest_compare'],
                'missing/duplicate per-file operation')
        require(all(s['ordinal']==file['ordinal'] for s in children),'per-file ordinal ownership mismatch')
    return [dict(mapping[s['ordinal']],span=s,operations=[c for c in selected if c['begin']['parent']==s['begin']['span']]) for s in files]


def operation_ownership(selected,variant):
    by_name=defaultdict(list)
    for s in selected: by_name[s['operation']].append(s)
    expected={'runtime':None,'initial_path_manifest':'runtime','manifest_parse':'runtime',
              'manifest_read':'manifest_parse','manifest_policy':'runtime','required_files':'runtime','inventory':'runtime'}
    if variant=='C':
        expected.update(generation=None,nested_runtime='generation',runtime='nested_runtime',
            protected_base='generation',selector_descriptors='generation',protected_generation='generation',
            generation_manifest_open_read='generation',generation_manifest_parse_policy='generation',
            generation_manifest_digest='generation',generation_final_identity='generation')
    else:
        require(not any(by_name[n] for n in ('generation','nested_runtime','protected_base','protected_generation',
                'selector_descriptors','generation_manifest_open_read','generation_manifest_parse_policy',
                'generation_manifest_digest','generation_final_identity')),'unexpected A generation operation')
    for name,parent in expected.items():
        require(len(by_name[name])==1,'missing/duplicate validation operation: '+name)
        actual=by_name[name][0]['parent']
        require(actual==(by_name[parent][0]['begin']['span'] if parent else 0),'operation parent mismatch: '+name)


def intervals(selected,left,right):
    clipped=[dict(s,clipped_start=max(left,s['start']),clipped_stop=min(right,s['stop'])) for s in selected
             if s['start']<right and s['stop']>left]
    points=sorted({left,right,*(s[k] for s in clipped for k in ('clipped_start','clipped_stop'))})
    groups=defaultdict(int); segments=[]
    for start,stop in zip(points,points[1:]):
        active=[s for s in clipped if s['clipped_start']<=start and stop<=s['clipped_stop']]
        # Choose the deepest measured work on each thread, retaining every active
        # enclosing span separately. Other threads may overlap and are not additive.
        deepest={}
        for s in active:
            key=s['begin']['pid'],s['begin']['tid']
            if key not in deepest or s['depth']>deepest[key]['depth']: deepest[key]=s
        labels=sorted({s['operation'] if s['operation'] not in CONTAINERS else s['operation']+'_outside_children'
                       for s in deepest.values()})
        label=' + '.join(labels) or 'uncovered'
        groups[label]+=stop-start
        segments.append(dict(start_ns=start,stop_ns=stop,label=label,active=[s['begin']['span'] for s in active]))
    require(sum(groups.values())==right-left,'validation interval reconciliation failed')
    unions={name:p.b.g.g.intervals(left,right,[s for s in selected if s['operation']==name]) for name in sorted(OPERATIONS)}
    outside=[]
    for parent in selected:
        begin=max(left,parent['start']); end=min(right,parent['stop'])
        if begin>=end: continue
        children=[s for s in selected if s['begin']['pid']==parent['begin']['pid'] and s['parent']==parent['begin']['span']]
        coverage=p.b.g.g.intervals(begin,end,children)
        outside.append(dict(span=parent['begin']['span'],operation=parent['operation'],duration_ns=coverage['uncovered_ns'],
                            intervals=coverage['uncovered']))
    return dict(start_ns=left,stop_ns=right,duration_ns=right-left,spans=clipped,groups_ns=dict(groups),segments=segments,
                unions=unions,parent_outside_nested=outside,
                inclusive_ns=sum(s['clipped_stop']-s['clipped_start'] for s in clipped),
                largest_uncovered_ns=max((s['stop_ns']-s['start_ns'] for s in segments if s['label']=='uncovered'),default=0))


def scheduler_evidence(capture,clock):
    timelines,issues=r.r.a.scheduler(capture,clock)
    require(not any(i in issues for i in ('capture loss','incomplete export')),'scheduler capture loss/incomplete export')
    tasks=defaultdict(list); transitions=defaultdict(list)
    for key,rows in timelines.items(): tasks[key[:2]].append((key,rows))
    for event in capture['events']:
        for key in {tuple(event[field]) for field in ('prev','next','task') if field in event}:
            transitions[key].append(event)
    return dict(capture=capture,clock=clock,tasks=tasks,issues=issues,transitions=transitions,
                timestamps={key:[event['ns'] for event in rows] for key,rows in transitions.items()})


def scheduler_windows(selected,capture,clock,prepared=None):
    evidence=prepared if prepared is not None else scheduler_evidence(capture,clock)
    require(evidence['capture'] is capture and evidence['clock']==clock,'scheduler evidence input mismatch')
    rows=[]
    for span in selected:
        event=span['begin']; start,stop=span['start'],span['stop']
        require(start<=stop and capture['start_ns']<=start<=stop<=capture['stop_ns'],'span outside recording')
        candidates=[(key,rows) for key,rows in evidence['tasks'].get((event['pid'],event['tid']),[])
                    if rows and rows[0]['start_ns']<=start and rows[-1]['stop_ns']>=stop]
        require(len(candidates)==1,'missing/ambiguous scheduler task lifetime')
        key,timeline=candidates[0]; accounting=r.r.a.clipped(timeline,start,stop)
        require(accounting['complete'] and sum(accounting['totals'].values())==stop-start,'incomplete scheduler target coverage')
        establishing={row['start_ns'] for row in timeline if row['start_ns']<stop and row['stop_ns']>start}
        times=evidence['timestamps'].get(key,[])
        indices=set(range(bisect_left(times,start),bisect_right(times,stop)))
        for ns in establishing:
            if ns<start: indices.update(range(bisect_left(times,ns),bisect_right(times,ns)))
        transitions=[evidence['transitions'][key][index] for index in sorted(indices)]
        rows.append(dict(span=event['span'],task=list(key),operation=span['operation'],start_ns=start,stop_ns=stop,
                         **accounting,transitions=transitions))
    return dict(windows=rows,issues=evidence['issues'])


def scheduler_groups(part,accounting):
    """Partition one synchronous validator thread; do not add nested windows."""
    roots=[s for s in part['spans'] if s['parent']==0]
    require(len(roots)==1 and len({(s['begin']['pid'],s['begin']['tid']) for s in part['spans']})==1,
            'ambiguous validation thread')
    root=next(w for w in accounting['windows'] if w['span']==roots[0]['begin']['span'])
    grouped={}
    for segment in part['segments']:
        value=r.r.a.clipped(root['intervals'],segment['start_ns'],segment['stop_ns'])
        require(value['complete'],'scheduler group coverage incomplete')
        totals=grouped.setdefault(segment['label'],dict.fromkeys(('running','runnable','non_runnable','unknown'),0))
        for name,ns in value['totals'].items(): totals[name]+=ns
    require(all(sum(totals.values())==part['groups_ns'][name] for name,totals in grouped.items()),
            'scheduler group reconciliation failed')
    return grouped


def setup_validations(unowned,lifecycle,mapping,variant,observations,capture=None,clock=None,prepared_scheduler=None):
    """Retain explicit v3 setup activity without assigning an observation."""
    groups=defaultdict(list)
    measured={(row['endpoints']['pixels']['delivery']['pid'],row['endpoints']['pixels']['delivery']['service'])
              for row in observations}
    for span in unowned:
        e=span['begin']; key=e['pid'],e['service']
        require(e['observation'] is None and e['service'] is not None and key not in measured,
                'unowned validation spans')
        groups[key].append(span)
    result=[]
    for (pid,service),selected in sorted(groups.items()):
        require(any(key[0]==pid for key in measured),'foreign setup process')
        require(all(s['end']['outcome']=='returned' for s in selected),'exceptional setup validation')
        construction=[s for s in lifecycle['unassigned'] if s.get('cause')=='setup_activity' and
                      s['phase']=='service_construction' and all(s['begin'].get(k)==value for k,value in
                      (('pid',pid),('service',service),('observation',0)))]
        require(len(construction)==1,'missing/ambiguous setup construction')
        bindings=[]
        for span in selected:
            if span['operation'] not in ('generation','runtime'): continue
            e=span['begin']
            matches=[s for s in lifecycle['unassigned'] if s.get('cause')=='setup_activity' and
                     s['phase']==span['operation']+'_validation' and s['start']<=span['start']<=span['stop']<=s['stop'] and
                     all(s[edge].get(k)==(e[k] or 0) for edge in ('begin','end') for k in
                         ('pid','tid','service','observation','job','worker','preparation'))]
            require(len(matches)==1,'missing/ambiguous setup validation binding')
            bindings.append(dict(span=e['span'],legacy=matches[0]))
        operation_ownership(selected,variant)
        files=mapped_files(selected,mapping)
        roots=[s for s in selected if s['parent']==0]
        require(len(roots)==1 and roots[0]['start']<roots[0]['stop'] and
                roots[0]['stop']<=min(row['start_ns'] for row in observations),'setup overlaps observation')
        root=roots[0]
        require(all(root['start']<=s['start']<=s['stop']<=root['stop'] for s in selected),'setup span outside root')
        part=intervals(selected,root['start'],root['stop'])
        part['files']=files
        part['scheduler']=scheduler_windows(selected,capture,clock,prepared_scheduler) if capture else None
        if capture: part['scheduler_groups']=scheduler_groups(part,part['scheduler'])
        result.append(dict(pid=pid,service=service,observation=None,classification='v3_setup_activity',
                           construction=construction[0],bindings=bindings,validation=part))
    return result


def invocation(entry,index,built,execution,replay=False,setup_output=None):
    row=entry['invocation']; target=Path(entry['argv'][-1])
    require(target==execution/'observations'/f'{index:03}.json','invocation path mismatch')
    samples=read(target)['samples']; count=row['observations']
    process=read(target.with_suffix('.process.json'))
    o.validate(target,dict(row,mode='v4'),process,1000,replay=True)
    report=read(target.with_suffix('.v4.json')); lifecycle=read(target.with_suffix('.v3.json'))
    endpoints=[]
    for endpoint in p.b.g.endpoint_rows(report,row['variant'],row['fixture'],count):
        obs=endpoint['observation']
        life=[x for x in lifecycle['accounting'] if x['sample']==obs-1]
        require(len(life)==1,'missing/ambiguous original lifecycle')
        life=json.loads(json.dumps(life[0]).replace(str(target),str(target.with_suffix('.stderr'))))
        endpoint.update(invocation_index=index,block=row['block'],
                        harness_latency_ns=samples[obs-1]['first_ms' if endpoint['endpoint']=='pixels' else 'final_ms']*1e6)
        endpoints.append(p.b.partition(endpoint,life))
    observations=p.observations(endpoints)  # Enforces agreement before deduplication.
    parsed=spans(records(target))
    require(bool(parsed)==(row['mode']=='validation'),'validation stream contamination/missing')
    require(all(s['end']['outcome']=='returned' for s in parsed),'exceptional validation in accepted observation')
    mapping=read(built/row['mode']/row['variant']/'manifest-ordinals.json')
    require(mapping==r.ordinal_mapping(read(built/row['mode']/row['variant']/'runtime/manifest.json')),'manifest mapping drift')
    capture=None; clock=read(execution/'preregistration.json')['clock']
    if row['captured']:
        directory=execution/f'recording-{index:03}'
        capture=r.r.n.normalize((directory/'perf-export.stdout').read_text(),read(directory/'recording-metadata.json'),
                                read(directory/'task-identities.json'),str(directory/'perf-export.stdout'))
        require(capture==read(directory/'scheduler.json'),'scheduler normalization replay mismatch')
    prepared_scheduler=scheduler_evidence(capture,clock) if capture else None
    assigned=set()
    for obs in observations:
        endpoint=obs['endpoints']['pixels']['delivery']
        owned=[s for s in parsed if all(s['begin'][k]==endpoint[k] for k in ('pid','service','observation'))]
        assigned.update((s['begin']['pid'],s['begin']['span']) for s in owned)
        obs.update(arm=row['arm'],warmup=row['warmup'])
        if row['mode']=='validation':
            operation_ownership(owned,row['variant'])
            require(sum(s['operation']=='generation' for s in owned)==(row['variant']=='C'),'generation validation ownership mismatch')
            files=mapped_files(owned,mapping)
            require(all(obs['start_ns']<=s['start']<=s['stop']<=obs['stop_ns'] for s in owned),'validation outside predecode')
            roots=[s for s in owned if s['operation'] in ('generation','runtime') and s['parent']==0]
            require(len(roots)==1,'missing/ambiguous top validation root')
            bounds=roots[0]
            require(bounds['stop']>bounds['start'],'empty validation window')
            obs['validation']=intervals(owned,bounds['start'],bounds['stop'])
            obs['validation']['files']=files
            obs['validation']['predecode_coverage']=intervals(owned,obs['start_ns'],obs['stop_ns'])
            obs['validation']['scheduler']=scheduler_windows(owned,capture,clock,prepared_scheduler) if capture else None
            if capture:
                obs['validation']['scheduler_groups']=scheduler_groups(obs['validation'],obs['validation']['scheduler'])
    unowned=[s for s in parsed if (s['begin']['pid'],s['begin']['span']) not in assigned]
    setup_lifecycle=json.loads(json.dumps(lifecycle).replace(str(target),str(target.with_suffix('.stderr'))))
    setup=[dict(value,invocation_index=index,variant=row['variant'],arm=row['arm'],warmup=row['warmup'])
           for value in setup_validations(unowned,setup_lifecycle,mapping,row['variant'],observations,capture,clock,prepared_scheduler)]
    destination=setup_output or target.with_suffix('.validation-setup.json')
    if replay:
        require(read(destination)==setup,'setup validation replay mismatch')
    else:
        require(not destination.exists(),'setup validation output reused')
        write(destination,setup)
    return observations,endpoints


def summarize(rows):
    grouped=defaultdict(list); labels=sorted({n for row in rows if 'validation' in row for n in row['validation']['groups_ns']})
    for row in rows:
        for block in ('pooled',row['block']): grouped[row['variant'],row['arm'],block].append(row)
    result=[]
    for (variant,arm,block),rs in sorted(grouped.items(),key=lambda x:str(x[0])):
        cell=dict(variant=variant,arm=arm,block=block,observations=len(rs),endpoint_mappings=2*len(rs),
                  predecode_ns=stats([r['duration_ns'] for r in rs]),
                  harness_latency_ns={e:stats([r['endpoints'][e]['harness_latency_ns'] for r in rs]) for e in ('pixels','metadata')})
        if arm!='baseline':
            cell['validation_ns']=stats([r['validation']['duration_ns'] for r in rs])
            cell['groups']={name:dict(duration_ns=stats([r['validation']['groups_ns'].get(name,0) for r in rs]),
                                      share=stats([r['validation']['groups_ns'].get(name,0)/r['validation']['duration_ns'] for r in rs]))
                            for name in labels}
            # First union all matching file operations within each observation;
            # only these observation-level values enter distributions.
            cell['operations']={name:stats([r['validation']['unions'][name]['covered_ns'] for r in rs]) for name in sorted(OPERATIONS)}
            if arm=='captured':
                cell['scheduler_groups']={name:{state:stats([r['validation']['scheduler_groups'].get(name,{}).get(state,0) for r in rs])
                    for state in ('running','runnable','non_runnable')} for name in labels}
        result.append(cell)
    return result


def rankings(summary):
    result=[]
    for arm in ('validation','captured'):
        pooled={r['variant']:r for r in summary if r['block']=='pooled' and r['arm']==arm}
        require(set(pooled)=={'A','C'},'missing ranking variant')
        c=pooled['C']['groups']
        order=sorted(c,key=lambda n:(-c[n]['share']['median'],-c[n]['share']['p95'],n))
        result.append(dict(arm=arm,order=order,C=c,A=pooled['A']['groups']))
    return result


def selections(rows):
    selected=defaultdict(list)
    for variant in ('A','C'):
        for arm in ('baseline','validation','captured'):
            rs=[r for r in rows if r['variant']==variant and r['arm']==arm]
            require(bool(rs),'missing selection cell')
            metrics={'predecode':lambda r:r['duration_ns'],
                     'pixels_harness':lambda r:r['endpoints']['pixels']['harness_latency_ns'],
                     'metadata_harness':lambda r:r['endpoints']['metadata']['harness_latency_ns']}
            if arm!='baseline': metrics['validation']=lambda r:r['validation']['duration_ns']
            for name,metric in metrics.items():
                values=sorted((metric(r) for r in rs),reverse=True); cutoff=values[min(4,len(values)-1)]
                median=statistics.median(values); nearest=min(abs(x-median) for x in values)
                for row in rs:
                    key=row['invocation_index'],row['observation']
                    if metric(row)>=cutoff: selected[key].append(name+'_slowest_five_with_ties')
                    if abs(metric(row)-median)==nearest: selected[key].append(name+'_nearest_median_with_ties')
            for field in ('predecode','validation'):
                if field=='validation' and arm=='baseline': continue
                metric=lambda row: row['largest_uncovered_ns'] if field=='predecode' else row['validation']['largest_uncovered_ns']
                largest=max(metric(r) for r in rs)
                for row in rs:
                    if metric(row)==largest: selected[row['invocation_index'],row['observation']].append(field+'_largest_uncovered_with_ties')
    return [dict(row,selection_reasons=sorted(set(selected[row['invocation_index'],row['observation']]))) for row in rows
            if selected[row['invocation_index'],row['observation']]]


def comparisons(selected,ranking):
    result=[]
    for rank in ranking:
        for variant in ('A','C'):
            rows=[r for r in selected if r['arm']==rank['arm'] and r['variant']==variant]
            for reason in sorted({n for r in rows for n in r['selection_reasons']}):
                rs=[r for r in rows if reason in r['selection_reasons']]
                shares={name:stats([r['validation']['groups_ns'].get(name,0)/r['validation']['duration_ns'] for r in rs]) for name in rank['order']}
                result.append(dict(arm=rank['arm'],variant=variant,selection=reason,observations=len(rs),shares=shares,
                                   order=sorted(shares,key=lambda n:(-shares[n]['median'],-shares[n]['p95'],n))))
    return result


def effects(summary):
    rows=[]
    for variant in ('A','C'):
        for block in ('pooled',*range(10)):
            cell={r['arm']:r for r in summary if r['variant']==variant and r['block']==block}
            for left,right,label in [('baseline','validation','probe'),('validation','captured','recorder')]:
                for endpoint in ('pixels','metadata'):
                    a=cell[left]['harness_latency_ns'][endpoint]; b=cell[right]['harness_latency_ns'][endpoint]
                    rows.append(dict(variant=variant,block=block,endpoint=endpoint,effect=label,
                        left=a,right=b,difference_ns={n:b[n]-a[n] for n in ('minimum','median','p95','maximum')}))
    return rows


def raw_citations(value):
    """Keep the historical citation checks, reading each sealed file once."""
    refs={}; files={}
    def visit(item):
        if isinstance(item,dict):
            if 'file' in item and 'line' in item:
                name=item['file'];path=Path(name)
                if name not in files:
                    require(path.absolute()==path.resolve(),'raw citation symlink')
                    files[name]=(path.read_text().splitlines(),o.digest(path))
                lines,digest=files[name];line=item['line']
                require(type(line) is int and 1<=line<=len(lines),'invalid raw citation')
                text=lines[line-1]
                if 'text' in item: require(text==item['text'],'raw citation text mismatch')
                elif 'operation' in item:
                    require(text.startswith('DELIVERY ') and all(json.loads(text[9:]).get(k)==v
                        for k,v in item.items() if k not in ('file','line')),'raw delivery mismatch')
                refs[str(path),line]=dict(file=str(path),line=line,text=text,sha256=digest)
            for child in item.values(): visit(child)
        elif isinstance(item,list):
            for child in item: visit(child)
    visit(value)
    return list(refs.values())


def report(package,built,execution,output):
    def run(result):
        r.check_package(package); o.check_output(built); o.check_output(execution)
        assessment=read(execution/'assessment.json')
        require(assessment['status']=='complete','execution blocked')
        require(read(execution/'integrity.json')['passed'],'execution integrity blocked')
        require(all(c['passed'] for c in read(execution/'execution-final-checks.json').values()),'execution final gates blocked')
        prereg=read(execution/'preregistration.json')
        require(prereg['protocol']==v.protocol() and prereg['built']==str(built) and prereg['package']==str(package) and
                prereg['built_seal']==o.digest(built/'seal.json'),'execution provenance mismatch')
        expected=r.planned_commands(built,Path(prereg['protected_runtime']),execution/'observations')
        require(prereg['commands']==expected and len(assessment['invocations'])==66,'scheduled commands/count mismatch')
        rows=[]; endpoints=[]; warmups=[]; setup=[]
        for index,(entry,saved) in enumerate(zip(expected,assessment['invocations'])):
            require(saved['entry']==entry and saved['index']==index and saved['status']=='passed','incomplete scheduled invocation')
            observations,mappings=invocation(entry,index,built,execution,replay=True)
            setup.extend(read(Path(entry['argv'][-1]).with_suffix('.validation-setup.json')))
            if entry['invocation']['warmup']: warmups.extend(observations)
            else: rows.extend(observations); endpoints.extend(mappings)
        require(len(rows)==600 and len(endpoints)==1200 and len(warmups)==6,'experiment observation/endpoint budget mismatch')
        for variant,arm in v.COMBINATIONS:
            require(sum(r['variant']==variant and r['arm']==arm for r in rows)==100,'variant/arm observation count mismatch')
        summary=summarize(rows); ranking=rankings(summary); chosen=selections(rows); comparison=comparisons(chosen,ranking)
        citations=raw_citations([rows,endpoints,warmups,setup])
        # Validation events use exact raw records too, including balanced exceptional
        # exits in failed evidence. Accepted measurements require returned exits.
        source=[]
        for mode,variant in r.KEYS:
            base=package/mode/variant
            for group in v.GROUPS:
                for path in sorted((base/group).rglob('*.cpp')):
                    lines=path.read_text().splitlines()
                    for number,line in enumerate(lines,1):
                        if any(n in line for n in ('StandbyTrace::','DeliveryTrace::','ValidationTrace::')):
                            source.append(dict(file=str(path),sha256=o.digest(path),line=number,text=line))
        for name,value in [('observations',rows),('endpoint-mappings',endpoints),('warmups',warmups),('setup-validations',setup),('distributions',summary),
                           ('rankings',ranking),('selected-timelines',chosen),('selection-comparisons',comparison),
                           ('effects',effects(summary)),('raw-citations',citations),('source-citations',source)]:
            write(output/(name+'.json'),value)
        priority_agreement=ranking[0]['order'][0]==ranking[1]['order'][0]
        tail_agreement=all(c['order'][0]==next(x['order'][0] for x in ranking if x['arm']==c['arm']) for c in comparison if c['variant']=='C')
        dominant=ranking[0]['order'][0]
        recommendation=('Investigate '+dominant+' next; pooled and selected-tail priorities agree in both validation arms.'
                        if priority_agreement and tail_agreement else
                        'Priorities disagree between arms or selections; no single optimization investigation is supported.')
        lines=['# A/C validation and scheduler decision','',
               'Complete: 600 measured observations, 1,200 endpoint mappings; six warm-ups reported separately.', '',
               '| Arm | Validation group | C median share | C p95 share | C median ns | A median ns |',
               '|---|---|---:|---:|---:|---:|']
        for rank in ranking:
            for name in rank['order']:
                c,a=rank['C'][name],rank['A'][name]
                lines.append(f"| {rank['arm']} | {name} | {c['share']['median']} | {c['share']['p95']} | {c['duration_ns']['median']} | {a['duration_ns']['median']} |")
        lines += ['',recommendation,'',f'Between-arm priority agreement: {priority_agreement}. Selected-class priority agreement: {tail_agreement}.', '',
            'Probe and recorder effects describe baseline→validation and validation→captured original harness latency distributions under this protocol. '
            'No overhead is subtracted. Quantile differences describe effects only; phase subtraction is per observation.', '',
            'Scheduler running time does not isolate hashing CPU cost. read_hash combines device reading and SHA-256. '
            'Non-runnable time identifies neither I/O nor a blocking cause. Overlapping threads and nested spans are non-additive. '
            'This experiment supplies no significance, acceptance threshold, predicted gain, qualification rerun or C/D reassessment.', '',
            'Raw events, scheduler transitions, source citations, per-observation file totals, clipped unions, disjoint active sets, '
            'parent subtraction, pooled/per-block distributions and tied selections are retained in the adjacent JSON artifacts.']
        (output/'REPORT.md').write_text('\n'.join(lines)+'\n')
        result.update(status='complete',observations=600,endpoint_mappings=1200,warmups=6,
                      priority_agreement=priority_agreement,tail_agreement=tail_agreement)
    result=r.action(output,[package,built,execution],run)
    if result['status']!='complete':
        # action sealed its blocked assessment; retain it verbatim. REPORT.md must
        # be produced within the action on success, never appended after its seal.
        return result
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('prepared','built','execution','output'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    result=report(args.prepared,args.built,args.execution,args.output)
    print(result); sys.exit(result['status']!='complete')
