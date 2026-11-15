#!/usr/bin/env python3
"""Independent sealed validation replay. Never import the validation reporter."""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validation_independent_runner',ROOT/'scripts/run-preview-validation.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
require,read=r.require,r.read


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def distribution(values):
    values=sorted(values)
    require(values and all(math.isfinite(x) for x in values),'invalid distribution')
    return dict(count=len(values),minimum=values[0],median=statistics.median(values),
                p95=values[(95*len(values)+99)//100-1],maximum=values[-1])


def sources(package):
    provenance=read(package/'provenance.json'); original=Path(provenance['prepared'])
    anchors=read(package/'anchors.json')
    for mode,variant in r.KEYS:
        source=original/'v4'/variant; target=package/mode/variant
        for group in ('source','harness-source'):
            old=r.o.inventory(source/group); new=r.o.inventory(target/group)
            require(set(old)==set(new),'independent source file-set mismatch')
            for name in old:
                data=(target/group/name).read_text() if (target/group/name).suffix in ('.cpp','.h') else None
                selected=[a for a in anchors if a['mode']==mode and a['variant']==variant and a['file']==group+'/'+name]
                if selected:
                    require(data is not None,'binary source anchor')
                    for a in reversed(selected):
                        require(data.count(a['replacement'])==1,'independent replacement mismatch')
                        data=data.replace(a['replacement'],a['anchor'],1)
                    actual=data.encode()
                else: actual=(target/group/name).read_bytes()
                expected=(source/group/name).read_bytes().replace(str(source/'trace.h').encode(),str(target/'trace.h').encode())
                require(actual==expected,'independent source reconstruction mismatch')
        old_header=(source/'trace.h').read_bytes(); new_header=(target/'trace.h').read_bytes()
        require(new_header==old_header if mode=='baseline' else new_header.startswith(old_header),'independent tracing header mismatch')


def arithmetic(row):
    part=row['validation']; start,stop=part['start_ns'],part['stop_ns']
    require(part['duration_ns']==stop-start and sum(part['groups_ns'].values())==stop-start,'independent validation reconciliation')
    points={start,stop}; selected=part['spans']
    for s in selected: points.update((s['clipped_start'],s['clipped_stop']))
    groups=defaultdict(int)
    points=sorted(points)
    for left,right in zip(points,points[1:]):
        active=[s for s in selected if s['clipped_start']<=left and s['clipped_stop']>=right]
        deepest={}
        for s in active:
            key=(s['begin']['pid'],s['begin']['tid'])
            if key not in deepest or s['depth']>deepest[key]['depth']: deepest[key]=s
        names=sorted({s['operation']+('_outside_children' if s['operation'] in ('runtime','generation','file','nested_runtime') else '') for s in deepest.values()})
        groups[' + '.join(names) or 'uncovered']+=right-left
    require(dict(groups)==part['groups_ns'],'independent disjoint groups mismatch')
    for name,coverage in part['unions'].items():
        bounds=sorted((max(start,s['start']),min(stop,s['stop'])) for s in selected if s['operation']==name and s['start']<stop and s['stop']>start)
        union=[]
        for left,right in bounds:
            if union and union[-1][1]>=left: union[-1][1]=max(union[-1][1],right)
            else: union.append([left,right])
        require(union==coverage['covered'] and sum(b-a for a,b in union)==coverage['covered_ns'],'independent operation union mismatch')
    for parent in part['parent_outside_nested']:
        source=next(s for s in selected if s['begin']['span']==parent['span'])
        children=[s for s in selected if s['parent']==parent['span'] and s['begin']['pid']==source['begin']['pid']]
        left,right=max(start,source['start']),min(stop,source['stop'])
        boundaries=sorted({left,right,*(max(left,min(right,s[k])) for s in children for k in ('start','stop'))})
        outside=sum(b-a for a,b in zip(boundaries,boundaries[1:]) if not any(s['start']<=a and b<=s['stop'] for s in children))
        require(outside==parent['duration_ns']==sum(b-a for a,b in parent['intervals']),'independent parent subtraction mismatch')
    if part['scheduler']:
        for window in part['scheduler']['windows']:
            totals=dict.fromkeys(('running','runnable','non_runnable','unknown'),0)
            for interval in window['intervals']: totals[interval['state']]+=interval['stop_ns']-interval['start_ns']
            require(totals==window['totals'] and totals['unknown']==0 and sum(totals.values())==window['stop_ns']-window['start_ns'],
                    'independent scheduler arithmetic mismatch')
        for name,totals in part['scheduler_groups'].items():
            require(sum(totals.values())==part['groups_ns'][name] and totals['unknown']==0,'independent scheduler group mismatch')


def selection_keys(observations):
    chosen=defaultdict(set)
    for variant,arm in r.v.COMBINATIONS:
        rs=[x for x in observations if x['variant']==variant and x['arm']==arm]
        require(len(rs)==100,'independent variant/arm count mismatch')
        measures={'predecode':lambda x:x['duration_ns'],
                  'pixels_harness':lambda x:x['endpoints']['pixels']['harness_latency_ns'],
                  'metadata_harness':lambda x:x['endpoints']['metadata']['harness_latency_ns']}
        if arm!='baseline': measures['validation']=lambda x:x['validation']['duration_ns']
        for name,measure in measures.items():
            values=sorted(measure(x) for x in rs); threshold=values[-5]; median=statistics.median(values)
            distance=min(abs(x-median) for x in values)
            for x in rs:
                key=x['invocation_index'],x['observation']
                if measure(x)>=threshold: chosen[key].add(name+'_slowest_five_with_ties')
                if abs(measure(x)-median)==distance: chosen[key].add(name+'_nearest_median_with_ties')
        for name in ('predecode',) if arm=='baseline' else ('predecode','validation'):
            measure=lambda x:x['largest_uncovered_ns'] if name=='predecode' else x['validation']['largest_uncovered_ns']
            threshold=max(measure(x) for x in rs)
            for x in rs:
                if measure(x)==threshold: chosen[x['invocation_index'],x['observation']].add(name+'_largest_uncovered_with_ties')
    return {key:sorted(reasons) for key,reasons in chosen.items() if reasons}


def scheduler_replay(row,execution,cache):
    index=row['invocation_index']
    if index not in cache:
        directory=execution/f'recording-{index:03}'
        capture=r.r.n.normalize((directory/'perf-export.stdout').read_text(),read(directory/'recording-metadata.json'),
                                read(directory/'task-identities.json'),str(directory/'perf-export.stdout'))
        require(capture==read(directory/'scheduler.json'),'independent scheduler normalization mismatch')
        timelines,issues=r.r.a.scheduler(capture,read(execution/'preregistration.json')['clock'])
        require(not any(i in issues for i in ('capture loss','incomplete export')),'independent scheduler completeness failure')
        cache[index]=timelines
    part=row['validation']; timelines=cache[index]
    require(len(part['scheduler']['windows'])==len(part['spans']),'independent scheduler window count mismatch')
    for window in part['scheduler']['windows']:
        span=next(x for x in part['spans'] if x['begin']['span']==window['span'])
        event=span['begin']
        matches=[(key,rs) for key,rs in timelines.items() if key[:2]==(event['pid'],event['tid']) and
                 rs[0]['start_ns']<=span['start'] and rs[-1]['stop_ns']>=span['stop']]
        require(len(matches)==1,'independent task lifetime ambiguity')
        key,rs=matches[0]; clipped=r.r.a.clipped(rs,span['start'],span['stop'])
        require(list(key)==window['task'] and clipped['complete'] and
                clipped['totals']==window['totals'] and clipped['intervals']==window['intervals'],'independent scheduler window mismatch')
    root=next(w for w in part['scheduler']['windows'] if w['start_ns']==part['start_ns'] and w['stop_ns']==part['stop_ns'])
    totals={}
    for segment in part['segments']:
        clipped=r.r.a.clipped(root['intervals'],segment['start_ns'],segment['stop_ns'])
        target=totals.setdefault(segment['label'],dict.fromkeys(('running','runnable','non_runnable','unknown'),0))
        for name,ns in clipped['totals'].items(): target[name]+=ns
    require(totals==part['scheduler_groups'],'independent group scheduler replay mismatch')


def span_ownership(observations,setup,execution):
    """Reconcile every raw span, retaining unavailable setup identities verbatim."""
    groups=defaultdict(list)
    for row in observations: groups[row['invocation_index']].append(row)
    require(all(x['invocation_index'] in groups for x in setup),'independent foreign setup invocation')
    for index,rows in groups.items():
        target=execution/'observations'/f'{index:03}.json'
        raw={}; stacks=defaultdict(list)
        for path in (target.with_suffix('.stderr'),target.with_suffix('.stdout')):
            for number,line in enumerate(path.read_text().splitlines(),1):
                if not line.startswith('VALIDATION '): continue
                event=dict(json.loads(line[len('VALIDATION '):]),file=str(path),line=number,text=line)
                key=event['pid'],event['span'],event['edge']
                require(key not in raw,'independent duplicate span boundary');raw[key]=event
                stack=stacks[event['pid'],event['tid']]
                if event['edge']=='begin':
                    require(event['parent']==(stack[-1] if stack else 0),'independent span parent mismatch')
                    stack.append(event['span'])
                else:
                    require(stack and stack.pop()==event['span'],'independent span nesting mismatch')
        require(not any(stacks.values()),'independent unbalanced span stack')
        accounted=[]
        services=set()
        for row in rows:
            endpoint=row['endpoints']['pixels']['delivery'];services.add((endpoint['pid'],endpoint['service']))
            if 'validation' not in row: continue
            for span in row['validation']['spans']:
                require(all(span['begin'][k]==endpoint[k] for k in ('pid','service','observation')),
                        'independent observation ownership mismatch')
                accounted.append(span)
        for group in (x for x in setup if x['invocation_index']==index):
            require(group['observation'] is None and (group['pid'],group['service']) not in services and
                    any(pid==group['pid'] for pid,_ in services),'independent setup ownership mismatch')
            part=group['validation'];arithmetic(group)
            require(part['stop_ns']<=min(row['start_ns'] for row in rows),'independent setup overlaps observation')
            selected=part['spans'];accounted.extend(selected)
            require(all(s['begin']['observation'] is None and s['begin']['pid']==group['pid'] and
                        s['begin']['service']==group['service'] for s in selected),'independent setup context mismatch')
            roots={s['begin']['span']:s for s in selected if s['operation'] in ('generation','runtime')}
            construction=group['construction']
            require(construction['cause']=='setup_activity' and construction['phase']=='service_construction' and
                    all(construction[edge][k]==value for edge in ('begin','end') for k,value in
                        (('pid',group['pid']),('service',group['service']),('observation',0))),
                    'independent setup construction mismatch')
            require({b['span'] for b in group['bindings']}==set(roots) and len(group['bindings'])==len(roots),
                    'independent setup root binding mismatch')
            for binding in group['bindings']:
                s=roots[binding['span']];legacy=binding['legacy']
                require(legacy['cause']=='setup_activity' and legacy['phase']==s['operation']+'_validation' and
                        legacy['start']<=s['start']<=s['stop']<=legacy['stop'],'independent setup legacy mismatch')
                for edge in ('begin','end'):
                    require(all(legacy[edge][k]==(s['begin'][k] or 0) for k in
                        ('pid','tid','service','observation','job','worker','preparation')),'independent setup identity mismatch')
            for legacy in [group['construction'],*[b['legacy'] for b in group['bindings']]]:
                for edge in ('begin','end'):
                    e=legacy[edge];text=Path(e['file']).read_text().splitlines()[e['line']-1]
                    require(text.startswith('TRACE ') and json.loads(text[6:])=={k:v for k,v in e.items() if k not in ('file','line')},
                            'independent setup v3 citation mismatch')
        represented={}
        for span in accounted:
            require(span['start']==span['begin']['ns'] and span['stop']==span['end']['ns'],
                    'independent raw span timestamp mismatch')
            for edge in ('begin','end'):
                e=span[edge];key=e['pid'],e['span'],edge
                require(key not in represented and raw.get(key)==e,'independent raw span ownership mismatch')
                represented[key]=e
        require(set(represented)==set(raw),'independent unassigned raw span')


def verify(package,built=None,execution=None,report=None,snapshots=None):
    r.o.check_output(package)
    integrity=read(package/'integrity.json')
    require(integrity['passed'] and all(integrity['checks'].values()),'preparation integrity failed')
    rebound={}
    for name,expected in integrity['consumed'].items():
        path=Path(name)
        if digest(path)!=expected and snapshots is not None:
            replacement=snapshots/path.name
            require(path.parent in (ROOT/'scripts',ROOT/'tests') and replacement.is_file() and digest(replacement)==expected,
                    'independent consumed mismatch')
            rebound[name]=str(replacement)
        else: require(digest(path)==expected,'independent consumed mismatch: '+name)
    for name,expected in integrity['before'].items(): require(r.o.inventory(Path(name))==expected,'independent provenance drift')
    protocol=read(package/'protocol.json')
    rows=protocol['schedule']
    require(len(rows)==66 and sum(x['observations'] for x in rows if x['warmup'])==6 and
            sum(x['observations'] for x in rows if not x['warmup'])==600,'independent schedule count mismatch')
    assessment=read(package/'assessment.json')
    if assessment['status']=='blocked':
        require(not any((package/mode).exists() for mode in ('baseline','validation')) and
                assessment['launched_invocations']==assessment['measured_observations']==0,'failed preparation launched/emitted sources')
        return dict(status='passed',experiment='blocked before build/workloads',observations=0,unexecuted_invocations=66,
                    original_failure=assessment['failure'],historical_tool_snapshots=rebound)
    sources(package)
    require(all(x is not None for x in (built,execution,report)),'complete experiment paths required')
    for path in (built,execution,report): r.o.check_output(path)
    require(read(report/'assessment.json')['status']=='complete' and read(execution/'assessment.json')['status']=='complete','experiment blocked')
    observations=read(report/'observations.json'); endpoints=read(report/'endpoint-mappings.json')
    require(len(observations)==600 and len(endpoints)==1200 and len(read(report/'warmups.json'))==6,'independent budget mismatch')
    setup=read(report/'setup-validations.json')
    span_ownership(observations+read(report/'warmups.json'),setup,execution)
    require(len({(x['invocation_index'],x['observation']) for x in observations})==600,'independent duplicate observation')
    prereg=read(execution/'preregistration.json')
    expected=r.planned_commands(built,Path(prereg['protected_runtime']),execution/'observations')
    require(expected==prereg['commands'],'independent preregistered command mismatch')
    for index,entry in enumerate(expected):
        target=Path(entry['argv'][-1])
        r.o.validate(target,dict(entry['invocation'],mode='v4'),read(target.with_suffix('.process.json')),1000,replay=True)
    grouped=defaultdict(list); cache={}
    for row in observations:
        matches=[e for e in endpoints if (e['invocation_index'],e['observation'])==(row['invocation_index'],row['observation'])]
        require(len(matches)==2 and {e['endpoint'] for e in matches}=={'pixels','metadata'},'independent endpoint mapping mismatch')
        require({k:v for k,v in matches[0]['coarse']['pre_decode'].items() if k!='share'}==
                {k:v for k,v in matches[1]['coarse']['pre_decode'].items() if k!='share'},'independent endpoint predecode mismatch')
        if 'validation' in row:
            arithmetic(row)
            if row['arm']=='captured': scheduler_replay(row,execution,cache)
        for block in ('pooled',row['block']): grouped[row['variant'],row['arm'],block].append(row)
    for group in setup:
        if group['arm']=='captured': scheduler_replay(group,execution,cache)
    for cell in read(report/'distributions.json'):
        rs=grouped[cell['variant'],cell['arm'],cell['block']]
        require(cell['observations']==len(rs) and cell['predecode_ns']==distribution([x['duration_ns'] for x in rs]),'independent predecode distribution mismatch')
        for endpoint in ('pixels','metadata'):
            require(cell['harness_latency_ns'][endpoint]==distribution([x['endpoints'][endpoint]['harness_latency_ns'] for x in rs]),'independent harness distribution mismatch')
        if cell['arm']!='baseline':
            require(cell['validation_ns']==distribution([x['validation']['duration_ns'] for x in rs]),'independent validation distribution mismatch')
            for name,value in cell['groups'].items():
                require(value['duration_ns']==distribution([x['validation']['groups_ns'].get(name,0) for x in rs]) and
                        value['share']==distribution([x['validation']['groups_ns'].get(name,0)/x['validation']['duration_ns'] for x in rs]),
                        'independent group distribution mismatch')
    for rank in read(report/'rankings.json'):
        require(rank['order']==sorted(rank['C'],key=lambda n:(-rank['C'][n]['share']['median'],-rank['C'][n]['share']['p95'],n)),
                'independent ranking mismatch')
    selected=read(report/'selected-timelines.json')
    require({(x['invocation_index'],x['observation']):x['selection_reasons'] for x in selected}==selection_keys(observations),
            'independent tied selections mismatch')
    for comparison in read(report/'selection-comparisons.json'):
        rs=[x for x in selected if x['variant']==comparison['variant'] and x['arm']==comparison['arm'] and comparison['selection'] in x['selection_reasons']]
        shares={name:distribution([x['validation']['groups_ns'].get(name,0)/x['validation']['duration_ns'] for x in rs]) for name in comparison['shares']}
        require(shares==comparison['shares'] and comparison['observations']==len(rs) and
                comparison['order']==sorted(shares,key=lambda n:(-shares[n]['median'],-shares[n]['p95'],n)),
                'independent selection comparison mismatch')
    summary=read(report/'distributions.json')
    for effect in read(report/'effects.json'):
        cell={x['arm']:x['harness_latency_ns'][effect['endpoint']] for x in summary if x['variant']==effect['variant'] and x['block']==effect['block']}
        left,right=('baseline','validation') if effect['effect']=='probe' else ('validation','captured')
        require(effect['left']==cell[left] and effect['right']==cell[right] and effect['difference_ns']==
                {n:cell[right][n]-cell[left][n] for n in ('minimum','median','p95','maximum')},'independent effects mismatch')
    citation_files={}
    for citation in read(report/'raw-citations.json')+read(report/'source-citations.json'):
        path=Path(citation['file'])
        if path not in citation_files: citation_files[path]=(digest(path),path.read_text().splitlines())
        sha,lines=citation_files[path]
        require(sha==citation['sha256'] and lines[citation['line']-1]==citation['text'],
                'independent citation mismatch')
    return dict(status='passed',observations=600,endpoint_mappings=1200)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('prepared','built','execution','report','snapshots','output'): parser.add_argument('--'+name,type=Path,required=name in ('prepared','output'))
    args=parser.parse_args()
    require(not args.output.exists() and not args.output.is_symlink() and args.output.absolute()==args.output.resolve() and
            args.output.is_relative_to(ROOT/'build'),'fresh independent output beneath build required')
    try:
        result=verify(args.prepared,args.built,args.execution,args.report,args.snapshots)
    except r.ERRORS as error: result=dict(status='blocked',failure=str(error))
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result); sys.exit(result['status']!='passed')
