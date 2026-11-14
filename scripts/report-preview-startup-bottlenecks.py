#!/usr/bin/env python3
"""Rank retained startup intervals offline, without launching any process."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util
spec = importlib.util.spec_from_file_location('startup_report_context', Path(__file__).with_name('report-preview-delivery-scheduler.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
g, o = s.g, s.o
v3 = s.r.module('startup_retained_v3', 'analyze-preview-startup-v3.py')
require, read, write = o.require, o.read, o.write
NAMES = ('pre_decode', 'decode_exchange', 'post_decode')


def stats(values):
    values = sorted(values)
    require(bool(values) and all(math.isfinite(x) for x in values), 'invalid distribution')
    return dict(count=len(values), minimum=values[0], median=statistics.median(values),
                p95=values[math.ceil(.95*len(values))-1], maximum=values[-1])


def partition(row, lifecycle):
    e = row['delivery']
    origins = lifecycle['boundaries']['startup_origin']
    require(len(origins) == 1, 'missing/ambiguous origin')
    origin = origins[0]
    require(all(origin[k] == e[k] for k in ('pid', 'service', 'observation')), 'origin ownership mismatch')
    exchanges = [x for x in lifecycle['timeline'] if x['phase'] == 'decode_exchange_including_transport'
                 and x['role'] == 'demand' and all(x['begin'].get(k) == e[k] for k in ('pid','service','observation','job','worker'))]
    require(len(exchanges) == 1, 'missing/ambiguous decode boundary')
    decode = exchanges[0]
    require(decode['stop'] == row['start_ns'], 'decode boundary mismatch')
    start, stop = origin['ns'], e['ns']
    require(start <= decode['start'] <= decode['stop'] <= stop and stop > start, 'invalid coarse ordering')
    bounds = (start, decode['start'], decode['stop'], stop)
    # V3 phases and v4 operations are both retained. Broad lifecycle envelopes
    # remain timelines rather than contributing to operation coverage.
    spans = [dict(x, operation=x['phase']) for x in lifecycle['timeline']
             if x['role'] in ('demand', 'service_control') and x['phase'] in v3.a.PHASES]
    spans += [x for x in row['operations'] if x['operation'] not in g.g.ENVELOPES]
    parts = {}
    for name, left, right in zip(NAMES, bounds, bounds[1:]):
        clipped = [dict(x, clipped_start=max(left,x['start']), clipped_stop=min(right,x['stop']))
                   for x in spans if x['start'] < right and x['stop'] > left]
        coverage = g.g.intervals(left, right, spans)
        inclusive = sum(x['clipped_stop']-x['clipped_start'] for x in clipped)
        parts[name] = dict(start_ns=left, stop_ns=right, duration_ns=right-left,
                           share=(right-left)/(stop-start), spans=clipped, **coverage,
                           overlapping_span_excess_ns=inclusive-coverage['covered_ns'])
    require(sum(x['duration_ns'] for x in parts.values()) == stop-start, 'partition mismatch')
    return dict(row, trace_origin=origin, trace_window_ns=stop-start, coarse=parts,
                v3_timeline=lifecycle['timeline'], decode_boundary=decode,
                largest_uncovered_ns=max((b-a for p in parts.values() for a,b in p['uncovered']), default=0))


def denominators(rows):
    return dict(observations=len({(r['invocation_index'],r['observation']) for r in rows}),
                endpoints=len(rows), publications=len({(r['invocation_index'],r['delivery']['pid'],r['delivery']['publication']) for r in rows}))


def summaries(rows):
    groups = defaultdict(list)
    for row in rows:
        for block in ('pooled', row['block']):
            groups[row['variant'],row['endpoint'],block].append(row)
    result = []
    for (variant, endpoint, block), rs in sorted(groups.items(), key=lambda x:str(x[0])):
        result.append(dict(variant=variant,endpoint=endpoint,block=block,**denominators(rs),
            harness_latency_ns=stats([r['harness_latency_ns'] for r in rs]),
            trace_window_ns=stats([r['trace_window_ns'] for r in rs]),
            intervals={name:{metric:stats([r['coarse'][name][metric] for r in rs])
                       for metric in ('duration_ns','share','covered_ns','uncovered_ns','overlapping_span_excess_ns')} for name in NAMES}))
    return result


def rankings(summary):
    result = []
    for endpoint in ('pixels','metadata'):
        c = next(x for x in summary if x['variant']=='C' and x['endpoint']==endpoint and x['block']=='pooled')
        a = next(x for x in summary if x['variant']=='A' and x['endpoint']==endpoint and x['block']=='pooled')
        order = sorted(NAMES, key=lambda n:(-c['intervals'][n]['share']['median'],-c['intervals'][n]['share']['p95'],n))
        result.append(dict(endpoint=endpoint,order=order,C=c['intervals'],A=a['intervals']))
    return result


def selections(rows):
    result=[]
    for variant in ('A','C'):
        for endpoint in ('pixels','metadata'):
            rs=[r for r in rows if r['variant']==variant and r['endpoint']==endpoint]
            values=sorted((r['harness_latency_ns'] for r in rs),reverse=True)
            cutoff=values[min(4,len(values)-1)]; median=statistics.median(values)
            nearest=min(abs(x-median) for x in values); gap=max(r['largest_uncovered_ns'] for r in rs)
            for r in rs:
                reasons=[]
                if r['harness_latency_ns']>=cutoff: reasons.append('slowest_five_with_ties')
                if abs(r['harness_latency_ns']-median)==nearest: reasons.append('nearest_median')
                if r['largest_uncovered_ns']==gap: reasons.append('largest_uncovered')
                if reasons: result.append(dict(r,selection_reasons=reasons))
    return result


def report(delivery, scheduler, qualification, output):
    delivery, scheduler, qualification = (p.absolute() for p in (delivery, scheduler, qualification))
    output = output.absolute()
    inputs=(delivery,scheduler,qualification)
    o.fresh(output,*inputs)
    before={}; tracked={str(p):o.digest(p) for p in Path(__file__).parent.glob('*.py')}; result=dict(status='blocked')
    def consume(path, digest=None):
        actual=o.digest(path)
        require(digest is None or actual==digest,'consumed hash mismatch: '+str(path))
        tracked[str(path)]=actual
        return read(path)
    try:
        before={str(p):o.inventory(p) for p in inputs}
        for p in (delivery,scheduler):
            o.check_output(p)
            require(read(p/'assessment.json')['status']=='complete','blocked input')
        scheduler_integrity=read(scheduler/'integrity.json')
        require(scheduler_integrity['passed'], 'scheduler integrity failed')
        for name,digest in scheduler_integrity['consumed'].items():
            require(o.digest(Path(name))==digest, 'scheduler consumed drift: '+name)
            tracked[name]=digest
        integrity=read(delivery/'integrity.json')
        require(all(c['passed'] for c in integrity['final_checks'].values()),'delivery integrity failed')
        hashes={str(Path(root)/name):digest for root,inv in integrity['before'].items() for name,digest in inv.items()}
        execution=[Path(p) for p in integrity['before'] if p.endswith('/execution')]
        prepared=[Path(p) for p in integrity['before'] if (Path(p)/'v4/A/probe-to-source.json').exists()]
        require(len(execution)==len(prepared)==1,'ambiguous provenance')
        execution,prepared=execution[0],prepared[0]
        def retained(path):
            require(str(path) in hashes,'unrecorded consumed file: '+str(path))
            return consume(path,hashes[str(path)])
        run=retained(execution/'assessment.json'); prereg=retained(execution/'preregistration.json')
        source={}
        for variant in ('A','C'):
            probes=retained(prepared/f'v4/{variant}/probe-to-source.json')['probes']
            probes += retained(prepared/f'v3/{variant}/probe-to-source.json')['probes']
            for probe in probes:
                path=Path(probe['file']); require(any(path.is_relative_to(prepared/f'{mode}/{variant}') for mode in ('v3','v4')),'source escape')
                require(str(path) in hashes and hashes[str(path)]==probe['sha256'],'unsealed source')
                tracked[str(path)]=o.digest(path); require(tracked[str(path)]==probe['sha256'],'source drift')
                require(path.read_text().splitlines()[probe['line']-1]==probe['text'],'source citation mismatch')
            source[variant]=probes
        saved=read(delivery/'endpoints.json')
        selected=[r for r in saved if r['variant'] in ('A','C') and r['fixture']=='3200x2400.png']
        rows=[]; publications=[]; invocations=[]
        for index in sorted({r['invocation_index'] for r in selected}):
            entry=run['invocations'][index]; inv=entry['invocation']; command=prereg['commands'][index]
            require(inv==command['invocation'] and inv['mode']=='v4' and not inv['warmup'] and inv['observations']==10,'invalid selected invocation')
            target=execution/'observations'/f'{index:03}.json'
            samples=retained(target)['samples']; require(samples==entry['samples'] and len(samples)==10,'sample mismatch')
            for ext in ('.stderr','.stdout'):
                path=target.with_suffix(ext); require(o.digest(path)==hashes[str(path)],'raw drift'); tracked[str(path)]=hashes[str(path)]
            text=target.with_suffix('.stderr').read_text()+'\n'+target.with_suffix('.stdout').read_text()
            replay=o.gate.analyzer.analyze(text,str(target.with_suffix('.stderr')),inv['variant'],samples)
            require(replay==retained(target.with_suffix('.v4.json')),'v4 replay mismatch')
            o.v4_gate(replay,inv['variant'],10)
            lifecycle=o.old.validate_trace(text,samples,str(target),inv['variant'])
            require(lifecycle==retained(target.with_suffix('.v3.json')) and not lifecycle['issues'],'v3 replay mismatch')
            regenerated=g.endpoint_rows(replay,inv['variant'],inv['fixture'],10)
            for row in regenerated:
                matches=[r for r in selected if r['invocation_index']==index and r['observation']==row['observation'] and r['endpoint']==row['endpoint']]
                require(len(matches)==1 and all(matches[0][k]==v for k,v in row.items()),'endpoint replay mismatch')
                prior=matches[0]; life=[x for x in lifecycle['accounting'] if x['sample']==row['observation']-1]
                require(len(life)==1,'ambiguous lifecycle ownership')
                require(prior['harness_latency_ns']==samples[row['observation']-1]['first_ms' if row['endpoint']=='pixels' else 'final_ms']*1e6,'harness mismatch')
                life = json.loads(json.dumps(life[0]).replace(str(target), str(target.with_suffix('.stderr'))))
                rows.append(partition(prior,life))
            pubs=s.publication_rows(replay,str(index)); s.observations(pubs,10)
            publications.extend(pubs); invocations.append(dict(index=index,invocation=inv))
        require(len(invocations)==20 and len(rows)==400 and denominators(rows)['observations']==200,'selected corpus mismatch')
        # Qualification is a historical inventory rather than a delivery-style seal.
        # Preserve all its original inventories and reports, without changing its outcome.
        qualification_context={name:consume(qualification/name) for name in ('freeze.json','post-run-identity-checks.json','baseline-diff-audit.json','reused-evidence.json')}
        require(all(qualification_context['post-run-identity-checks.json'].values()), 'qualification identity failure')
        for variant, inventory in qualification_context['freeze.json']['source_inventories'].items():
            for name,digest in inventory.items():
                path=qualification/variant/'source'/name
                require(o.digest(path)==digest, 'qualification source drift: '+str(path))
                tracked[str(path)]=digest
        qualification_text=(qualification/'ASSESSMENT.md').read_text(); tracked[str(qualification/'ASSESSMENT.md')]=o.digest(qualification/'ASSESSMENT.md')
        require('fail' in qualification_text.lower(),'missing qualification result')
        (output/'qualification-context.md').write_text(qualification_text)
        summary=summaries(rows); ranking=rankings(summary); tails=selections(rows)
        raw=s.raw_citations([rows,publications]); tracked.update({r['file']:r['sha256'] for r in raw})
        overhead=retained(execution/'statistics.json')
        provenance=dict(invocations=invocations,inputs={str(p):before[str(p)] for p in inputs},consumed=tracked,
                        qualification=qualification_context,
                        A_equivalence='Unavailable: frozen tracing provenance identifies A as A-fixed in the matched v3 preparation, but no normalized source equivalence proof to this qualification freeze is established here. Treat these runs separately.',
                        scheduler='Separate B / 160x80.png pilot; its states are not assigned to A/C.',
                        matched_overhead='Existing validated v3/v4 statistics reused; no 264-invocation replay or overhead subtraction.')
        for name,value in [('observations',rows),('publications',publications),('distributions',summary),('rankings',ranking),('selected-timelines',tails),('raw-citations',raw),('source-citations',source),('provenance',provenance),('matched-overhead-context',overhead),('scheduler-context',read(scheduler/'summary.json'))]: write(output/(name+'.json'),value)
        lines=['# Retained A/C large-PNG startup priorities','',f'Complete: {denominators(rows)}; 20 measured v4 invocations. Durations are nanoseconds; shares use each corresponding trace-origin-to-endpoint window. Original harness timers remain separate.','', '| Endpoint | Rank | Interval | C median share | C median ns | C p95 ns | A median ns | A p95 ns |','|---|---:|---|---:|---:|---:|---:|---:|']
        recommendations=[]
        for rank in ranking:
            for number,name in enumerate(rank['order'],1):
                c,a=rank['C'][name],rank['A'][name]
                lines.append(f"| {rank['endpoint']} | {number} | {name} | {c['share']['median']:.6f} | {c['duration_ns']['median']} | {c['duration_ns']['p95']} | {a['duration_ns']['median']} | {a['duration_ns']['p95']} |")
            tail=[r for r in tails if r['variant']=='C' and r['endpoint']==rank['endpoint'] and 'slowest_five_with_ties' in r['selection_reasons']]
            tail_order=sorted(NAMES,key=lambda n:(-statistics.median(r['coarse'][n]['share'] for r in tail),n))
            recommendations += ['',f"{rank['endpoint']}: investigate {rank['order'][0]} next. Selected harness tails prioritize {tail_order[0]}. "+('Median and tail priorities agree.' if rank['order'][0]==tail_order[0] else 'Median and tail priorities differ; neither establishes the cause of qualification failure.')]
        lines += recommendations
        lines += ['', 'Qualification results are retained separately in [qualification-context.md](qualification-context.md). Qualification remains failed; traced-run rankings identify observed elapsed intervals, not causes of the separate gate failure or predicted optimization gains. '+provenance['A_equivalence'], '', 'Nested spans, clipped unions, uncovered intervals and overlap excess are retained per coarse interval. Inclusive spans and overlapping thread/endpoint views are non-additive; quantiles are never subtracted. Signed return-to-callback intervals are retained once per invocation-local publication in publications.json, including dual endpoints.', '', 'The scheduler pilot is separate B/small-PNG context. Its states cannot explain these A/C windows. Matched overhead context reuses validated summaries; overhead is not subtracted.', '', 'Missing evidence: matched qualification-time phase traces; an explicit normalized A/A-fixed source comparison; scheduling and blocking evidence on the A/C critical windows; and finer boundaries separating transport, validation, decoding, trace emission and uninstrumented work. Decode exchange includes transport. No follow-up experiment was executed.', '', 'Artifacts: [distributions](distributions.json), [rankings](rankings.json), [selected timelines](selected-timelines.json), [observations](observations.json), [publications](publications.json), [source citations](source-citations.json), [raw citations](raw-citations.json), [provenance](provenance.json). Pooled and per-block distributions include minimum, median, nearest-rank p95 and maximum with explicit denominators.']
        (output/'REPORT.md').write_text('\n'.join(lines)+'\n')
        result.update(status='complete',**denominators(rows),invocations=20)
    except (OSError,ValueError,KeyError,TypeError,IndexError,StopIteration) as error:
        result['failure']=str(error)
    finally:
        try:
            require(all(o.inventory(p)==before.get(str(p)) for p in inputs),'input drift')
            require(all(o.digest(Path(p))==h for p,h in tracked.items()),'consumed input drift')
        except (OSError,ValueError) as error: result.update(status='blocked',integrity_failure=str(error))
        if result['status']!='complete':
            (output/'REPORT.md').write_text('# Blocked startup assessment\n\n'+str(result)+'\n\nPartial rankings are not verified conclusions.\n')
        write(output/'assessment.json',result); write(output/'integrity.json',dict(before=before,consumed=tracked,passed=result['status']=='complete'))
        (output/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
        o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('delivery','scheduler','qualification','output'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    result=report(args.delivery,args.scheduler,args.qualification,args.output)
    print(result)
    sys.exit(result['status']!='complete')
