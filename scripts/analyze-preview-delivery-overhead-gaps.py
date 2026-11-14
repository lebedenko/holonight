#!/usr/bin/env python3
"""Read-only gap accounting for a completed, sealed delivery overhead experiment."""
import argparse
from collections import Counter, defaultdict
import importlib.util
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


o = module('overhead_gap_runner', 'measure-preview-delivery-overhead.py')
g = module('overhead_gap_history', 'analyze-preview-delivery-gaps-v4.py')
require, read, write = o.require, o.read, o.write


def endpoint_rows(report, variant, fixture, count):
    """Validate count explicitly, then reuse historical ownership/interval helpers."""
    require(type(count) is int and count > 0, 'invalid observation count')
    require(isinstance(report, dict) and all(isinstance(report.get(k), list) for k in
            ('windows', 'spans', 'handoffs', 'events', 'unavailable')), 'malformed report')
    require(len(report['windows']) == count * 2, 'endpoint window count mismatch')
    rows, seen = [], set()
    for w in report['windows']:
        e = w['delivery']; start, stop = w['start_ns'], w['stop_ns']
        require(all(k in e for k in g.IDENTITY + g.CONTEXT + ('publication',)), 'missing identity')
        require(all(e[k] is not None for k in g.IDENTITY + ('publication',)), 'unavailable identity')
        require(type(start) is int and type(stop) is int and 0 <= start <= stop, 'invalid window')
        key = (e['observation'], w['endpoint'])
        require(type(e['observation']) is int and 1 <= e['observation'] <= count and
                w['endpoint'] in ('pixels', 'metadata') and key not in seen, 'duplicate or invalid window')
        seen.add(key)
        hs = [h for h in report['handoffs'] if (h['pid'], h['publication']) == (e['pid'], e['publication'])]
        require(len(hs) == 1 and g.owns(hs[0]['identity'], e), 'handoff identity mismatch')
        owned = [s for s in report['spans'] if g.owns(s['begin'], e, s['operation'] in g.ENVELOPES)
                 and not (s['operation'] == 'effective_cleanup' and s['begin']['transaction'] is None)]
        specific = [s for s in owned if s['operation'] not in g.ENVELOPES]
        rows.append(dict(variant=variant, fixture=fixture, endpoint=w['endpoint'], observation=e['observation'],
                         delivery=e, boundary=w['boundary'], start_ns=start, stop_ns=stop, elapsed_ns=stop-start,
                         specific=g.intervals(start, stop, specific), envelopes=g.intervals(start, stop, owned),
                         categories={k:g.intervals(start, stop, [dict(start=a, stop=b) for a,b in spans])
                                     for k,spans in w['categories'].items()}, operations=owned, handoff=hs[0],
                         branch_points=[b for b in report['events'] if b['edge']=='point' and g.owns(b,e)],
                         unavailable=report['unavailable']))
    return rows


def largest(r):
    return max((b-a for a,b in r['specific']['uncovered']), default=0)


def tie(r):
    return r['invocation_index'], r['observation'], r['delivery']['publication']


def distribution(values):
    v = sorted(values)
    return dict(count=len(v), minimum_ns=v[0], median_ns=statistics.median(v),
                p95_ns=v[math.ceil(.95*len(v))-1], maximum_ns=v[-1])


def summaries(rows):
    groups = defaultdict(list)
    for r in rows:
        for block in ('all', r['block']):
            groups[r['variant'], r['fixture'], r['endpoint'], block].append(r)
    return [dict(cell=k[:3], block=k[3], **{name:distribution([fn(r) for r in rs]) for name,fn in
            [('elapsed',lambda r:r['elapsed_ns']), ('covered',lambda r:r['specific']['covered_ns']),
             ('uncovered',lambda r:r['specific']['uncovered_ns']), ('largest_gap',largest)]})
            for k,rs in sorted(groups.items(), key=lambda x:str(x[0]))]


def selections(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[r['variant'],r['fixture'],r['endpoint']].append(r)
    selected = []
    for _, rs in sorted(groups.items()):
        median = statistics.median(r['harness_latency_ns'] for r in rs)
        reasons = defaultdict(list)
        for name,ordered,n in [
            ('slowest_harness',sorted(rs,key=lambda r:(-r['harness_latency_ns'],*tie(r))),5),
            ('nearest_harness_median',sorted(rs,key=lambda r:(abs(r['harness_latency_ns']-median),*tie(r))),5),
            ('largest_individual_gap',sorted(rs,key=lambda r:(-largest(r),*tie(r))),1)]:
            for r in ordered[:n]: reasons[tie(r)].append(name)
        selected += [dict(r, selection_reasons=reasons[tie(r)]) for r in sorted(rs,key=tie) if tie(r) in reasons]
    return selected


def boundaries(r):
    records = [r['boundary'],r['delivery']] + [s[k] for s in r['operations']
               if s['operation'] not in g.ENVELOPES for k in ('begin','end')]
    result = []
    for a,b in r['specific']['uncovered']:
        left = [e for e in records if e['ns']==a]; right = [e for e in records if e['ns']==b]
        require(left and right, 'unbounded gap')
        relationships = sorted({'same_thread' if x['tid']==y['tid'] else 'cross_thread' for x in left for y in right})
        result.append(dict(start_ns=a,stop_ns=b,duration_ns=b-a,left_records=left,right_records=right,
                           relationships=relationships))
    return result


def pattern(gap):
    def names(records):
        return tuple(sorted({(e.get('operation',e.get('phase')),e['edge']) for e in records}))
    return str((names(gap['left_records']),names(gap['right_records']),gap['relationships']))


def citations(prepared):
    result = {}
    for variant in 'ABCD':
        ps = g.validate_probes(prepared / 'v4', variant)
        result[variant] = []
        for p in ps:
            lines = Path(p['file']).read_text().splitlines(); lo=max(1,p['line']-12); hi=min(len(lines),p['line']+16)
            result[variant].append(dict(p, first_line=lo,last_line=hi,text_excerpt='\n'.join(lines[lo-1:hi])))
    return result


def analyze(attempt, prepared, prior, output):
    execution, built, report = (attempt / n for n in ('execution','native-build','report-privileged'))
    o.fresh(output, prepared, attempt, prior)
    roots = (prepared, execution, built, report, prior)
    before = {}; tools = {}; result = dict(status='blocked', attribution_complete=False)
    try:
        before = {str(p):o.inventory(p) for p in roots}
        tools = {str(p):o.digest(p) for p in (ROOT/'scripts').glob('*.py')}
        for p in (execution, report, prior): o.check_output(p)
        o.verify(prepared); o.built_integrity(built,execution)
        prereg=read(execution/'preregistration.json'); run=read(execution/'assessment.json')
        require(prereg['prepared']==str(prepared) and prereg['built']==str(built) and
                prereg['built_seal']==o.digest(built/'seal.json'), 'consumed identity mismatch')
        require(read(built/'assessment.json')['status']=='built' and read(report/'assessment.json')['status']=='complete'
                and read(prior/'status.json')['status']=='complete', 'incomplete consumed evidence')
        require(run['status']=='complete' and run['integrity_verified'] and
                all(run['final_checks'][k]['passed'] for k in ('inputs','artifacts','runtime','scopes')), 'incomplete execution')
        privileged=read(attempt/'independent-verification-privileged.json')
        require(privileged['status']=='passed' and all(c['passed'] for c in privileged['checks'].values()), 'privileged verification failed')
        require(read(execution/'runtime-before.json')==read(execution/'runtime-after.json'), 'saved ownership drift')
        require(o.inventory(built)==read(execution/'final-artifact-inventory.json') and
                o.inventory(prepared)==read(execution/'final-input-inventory.json')==read(built/'prepared-inventory.json'), 'saved inventory mismatch')
        require(len(run['invocations'])==264 and len(prereg['commands'])==264, 'incomplete schedule')
        source=citations(prepared); write(output/'source-citations.json',source)
        rows=[]; warmups=[]; context=[]
        for index,(entry,command,expected) in enumerate(zip(run['invocations'],prereg['commands'],o.prep.schedule())):
            require(entry['invocation']==command['invocation']==expected and entry['argv']==command['argv'] and entry['status']=='passed', 'schedule mismatch')
            target=execution/'observations'/f'{index:03}.json'
            require(entry['argv']==[str(built/expected['mode']/expected['variant']/'reuse-harness/preview-benchmark'),str(Path(prereg['runtime'])/expected['mode']/expected['variant']),str(o.old.FIXTURE_ROOT/expected['fixture']),'startup',str(expected['observations']),str(target)], 'command identity mismatch')
            process=entry['process']; require(process['exit']==0 and not process['timeout'] and process['cleanup_verified'], 'failed process')
            samples=read(target)['samples']; require(samples==entry['samples'] and len(samples)==expected['observations'], 'sample mismatch')
            text=target.with_suffix('.stderr').read_text()+'\n'+target.with_suffix('.stdout').read_text()
            v3=o.old.validate_trace(text,samples,str(target),expected['variant'])
            require(not v3['issues'] and v3==read(target.with_suffix('.v3.json')), 'v3 replay mismatch')
            context.append(dict(invocation=expected,samples=samples))
            if expected['mode']=='v3':
                require('DELIVERY ' not in text,'v3 contamination')
            else:
                replay=o.gate.analyzer.analyze(text,str(target.with_suffix('.stderr').resolve()),expected['variant'],samples)
                require(replay==read(target.with_suffix('.v4.json')), 'v4 replay mismatch')
                o.v4_gate(replay,expected['variant'],expected['observations'])
                endpoints=endpoint_rows(replay,expected['variant'],expected['fixture'],expected['observations'])
                for r in endpoints:
                    sample=samples[r['observation']-1]
                    r.update(invocation_index=index,block=expected['block'],harness_latency_ns=sample['first_ms' if r['endpoint']=='pixels' else 'final_ms']*1e6)
                if not expected['warmup']: rows.extend(endpoints)
            if expected['warmup']: warmups.append(dict(index=index,invocation=expected,target=str(target),samples=samples))
        require(len(rows)==2400 and len(warmups)==24,'endpoint accounting mismatch')
        cells=Counter((r['variant'],r['fixture'],r['endpoint']) for r in rows)
        require(len(cells)==24 and set(cells.values())=={100},'cell accounting mismatch')
        require(o.statistics_report(context)==read(execution/'statistics.json')==read(report/'statistics.json'),'overhead statistics mismatch')
        write(output/'endpoints.json',rows); write(output/'warmups.json',warmups)
        summary=summaries(rows); write(output/'summary.json',summary)
        patterns=Counter(); selected=selections(rows)
        for r in rows:
            for gap in boundaries(r): patterns[pattern(gap)]+=1
        for r in selected:
            r['gaps']=boundaries(r)
            for record in r['operations']:
                matches=[i for i,p in enumerate(source[r['variant']]) if '"'+record['operation']+'"' in p['text']]
                require(matches,'missing source operation '+record['operation'])
                record['source_citation_indexes']=matches
        write(output/'selected.json',selected)
        previous=read(prior/'review.json')
        write(output/'patterns.json',dict(current=patterns,prior_selections=[s['largest_gap'] for s in previous['selections']],comparison='Descriptive boundary comparison only; no pooled distributions or matched controls.'))
        result.update(status='complete',observations=1200,endpoints=len(rows),cells=len(cells),selected=len(selected))
        lines=['# Completed overhead experiment: delivery gaps','', '1,200 measured v4 observations; 2,400 endpoints; 100 per cell. All 264 invocations replayed; 24 warm-ups separately inventoried. v3 retained only as overhead context.','', '| Cell | Block | Metric | Count | Minimum ms | Median ms | p95 ms | Maximum ms |','|---|---|---|---:|---:|---:|---:|---:|']
        for cell in summary:
            for metric in ('elapsed','covered','uncovered','largest_gap'):
                d=cell[metric]; lines.append('| '+' / '.join(cell['cell'])+' | '+str(cell['block'])+' | '+metric+' | '+str(d['count'])+' | '+' | '.join(f'{d[k]/1e6:.6f}' for k in ('minimum_ns','median_ns','p95_ns','maximum_ns'))+' |')
        lines += ['', 'Elapsed starts at decode end; original harness latency is retained separately in endpoints.json. Categories, nested scopes and wrapper envelopes are non-additive. Cross-thread operation overlaps remain in the original spans. Ownership is supported by sealed inventories and successful privileged verification; current /run ownership was not revalidated.', '', 'Recurring boundary patterns (all endpoint windows):']
        lines += [f'- {n}: `{p}`' for p,n in patterns.most_common(12)]
        lines += ['', f'Compare the earlier source review at {prior}/ASSESSMENT.md descriptively; its three observations per cell are a separate run. Selected cases retain all tied bounding records and frozen source citations. See patterns.json for earlier selected boundary records.', '', f'Completed overhead results: {report}/REPORT.md. No overhead subtraction or tracing-harmlessness claim is made.', '', 'Minimum next diagnostic: bound actual queue insertion and callback dispatch, and collect runnable/running/blocked transitions for the worker and QObject threads over the recurring gaps. Add finer transaction-return/store-predicate boundaries only where same-thread gaps recur. These elapsed intervals cannot distinguish scheduling, blocking, uninstrumented work and trace emission. Unavailable-transaction cleanup remains unassigned; absent short-circuit conditions remain unevaluated. C failed qualification and D failed pilot remain unchanged. New instrumentation requires a separate plan.']
        (output/'ASSESSMENT.md').write_text('\n'.join(lines)+'\n')
    except (OSError,ValueError,KeyError,TypeError,IndexError,AttributeError) as error:
        result['failure']=str(error)
        (output/'ASSESSMENT.md').write_text('# Blocked offline analysis\n\n'+str(error)+'\n')
    finally:
        checks={}
        for p in roots:
            try:
                after=o.inventory(p); require(before.get(str(p))==after,'input drift')
                if p==built: o.built_integrity(built,execution)
                else: o.check_output(p)
                checks[str(p)]=dict(passed=True)
            except (OSError,ValueError,KeyError,TypeError) as error: checks[str(p)]=dict(passed=False,failure=str(error))
        checks['tools']=dict(passed=all(o.digest(Path(p))==h for p,h in tools.items()))
        write(output/'integrity.json',dict(before=before,tools=tools,final_checks=checks))
        if not all(c['passed'] for c in checks.values()): result['status']='blocked'
        write(output/'assessment.json',result); o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('attempt','prepared','prior-review','output'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    require(args.output.absolute()==args.output.resolve(),'symlink output ancestors refused')
    result=analyze(args.attempt.resolve(),args.prepared.resolve(),args.prior_review.resolve(),args.output.absolute())
    print(result)
    sys.exit(result['status']!='complete')
