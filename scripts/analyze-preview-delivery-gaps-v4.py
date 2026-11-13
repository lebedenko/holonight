#!/usr/bin/env python3
"""Offline source-linked audit of sealed v4 startup evidence."""
import argparse
from collections import defaultdict
import statistics
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import importlib.util
spec = importlib.util.spec_from_file_location('smoke', Path(__file__).with_name('run-preview-delivery-smoke.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


def intervals(start, stop, spans):
    union = s.analyzer.a.union([(max(start, x['start']), min(stop, x['stop'])) for x in spans if x['start'] < stop and x['stop'] > start])
    gaps, cursor = [], start
    for left, right in union:
        if cursor < left:
            gaps.append([cursor, left])
        cursor = max(cursor, right)
    if cursor < stop:
        gaps.append([cursor, stop])
    return dict(covered=union, uncovered=gaps, covered_ns=sum(b-a for a,b in union), uncovered_ns=sum(b-a for a,b in gaps))


def audit(runtime, prepared, output):
    runtime, prepared, output = (p.resolve() for p in (runtime, prepared, output))
    s.require(output.is_relative_to(s.ROOT / 'build') and all(not output.is_relative_to(p) and not p.is_relative_to(output) for p in (runtime, prepared)), 'disjoint build destination required')
    output.mkdir()
    result = dict(status='blocked', attribution_complete=False)
    try:
        before = {str(p): s.digest(p) for root in (runtime, prepared) for p in root.rglob('*') if p.is_file()}
        tools = {str(p): s.digest(p) for p in (s.ROOT / 'scripts').glob('*.py')}
        s.smoke.verify_hashes(runtime, s.read(runtime / 'seal.json'))
        assessment = s.read(runtime / 'assessment.json')
        s.require(assessment['status'] == 'passed' and assessment['passed_observations'] == 36 and len(assessment['invocations']) == 12 and all(assessment[k] for k in ('cleanup_verified','runtime_integrity','retained_integrity')), 'runtime gate failed')
        manifest = s.read(prepared / 'manifest.json')
        s.smoke.verify_hashes(prepared, {'trace.h': manifest['header_sha256']})
        for v in 'ABCD':
            s.require(s.inventory(prepared / v) == manifest['outputs'][v], 'prepared inventory mismatch')
        rows, groups = [], defaultdict(list)
        for index, invocation in enumerate(assessment['invocations']):
            command = invocation['command']; target = Path(command[-1]); variant = 'ABCD'[index // 3]
            s.require(target.is_relative_to(runtime) and target.name == f'{variant}-{s.FIXTURES[index % 3]}.json' and command[3:5] == ['startup','3'] and invocation['status'] == 'passed', 'schedule mismatch')
            report = s.trace_validation(target.with_suffix('.stderr').read_text(), s.read(target)['samples'], str(target.with_suffix('.stderr')), variant)
            s.require(report == s.read(target.with_suffix('.accounting.json')), 'accounting replay mismatch')
            s.write(output / target.with_suffix('.accounting.json').name, report)
            probes = s.read(prepared / variant / 'probe-to-source.json')['probes']
            for probe in probes:
                p = Path(probe['file'])
                s.require(p.is_relative_to(prepared / variant) and s.digest(p) == probe['sha256'] and p.read_text().splitlines()[probe['line']-1] == probe['text'], 'probe mismatch')
            for window in report['windows']:
                e = window['delivery']; start, stop = window['start_ns'], window['stop_ns']
                owned = [x for x in report['spans'] if all(x['begin'][k] == e[k] for k in ('pid','service','observation','job','worker','generation')) and all(x['begin'][k] is None or x['begin'][k] == e[k] for k in ('preparation','session','transaction'))]
                specific = [x for x in owned if x['operation'] not in ('transaction_wrapper','retirement_call')]
                row = dict(variant=variant, fixture=s.FIXTURES[index % 3], endpoint=window['endpoint'], observation=e['observation'], elapsed_ns=stop-start, boundary=window['boundary'], delivery=e, envelopes=intervals(start,stop,owned), specific=intervals(start,stop,specific), categories=window['categories'], handoff=next(h for h in report['handoffs'] if h['publication']==e['publication'] and h['pid']==e['pid']), unavailable=report['unavailable'], operations=owned, branch_points=[x for x in report['events'] if x['edge']=='point' and all(x[k]==e[k] for k in ('pid','service','observation','job','worker','generation'))])
                rows.append(row); groups[variant, row['fixture'], row['endpoint']].append(row['elapsed_ns'])
            s.write(output / f'{variant}-{index}-source-probes.json', probes)
        s.require(len(rows)==72, '72 endpoints required')
        s.write(output / 'endpoints.json', rows)
        summary = [dict(variant=k[0],fixture=k[1],endpoint=k[2],count=len(v),minimum_ns=min(v),median_ns=statistics.median(v),maximum_ns=max(v)) for k,v in groups.items()]
        s.write(output / 'summary.json', summary)
        after = {str(p): s.digest(p) for root in (runtime, prepared) for p in root.rglob('*') if p.is_file()}
        s.require(before==after and all(s.digest(Path(p))==h for p,h in tools.items()), 'inputs changed')
        s.write(output / 'integrity.json', dict(before=before,after=after,tools=tools))
        result.update(status='complete', endpoints=len(rows))
        lines=['# Offline v4 delivery accounting','', '72 endpoints accounted for. Durations are descriptive; v4 overhead is unmeasured. Category unions overlap and are not additive. Enqueue-to-callback elapsed time is not pure queue residence. Envelope coverage does not explain its contents. Branch conditions absent from branch_points remain unevaluated. Later cleanup with unavailable transaction identity remains unassigned.','', '| Variant | Fixture | Endpoint | Observation | Elapsed ns | Specific uncovered ns |','|---|---|---|---:|---:|---:|']
        lines += [f"| {r['variant']} | {r['fixture']} | {r['endpoint']} | {r['observation']} | {r['elapsed_ns']} | {r['specific']['uncovered_ns']} |" for r in rows]
        lines += ['', 'See endpoints.json for original raw references, explicit operation identities, branch outcomes and handoffs; source-probes files identify frozen source locations. Remaining uncovered intervals need additional boundaries before attribution. No optimization or experiment is authorized. C qualification and D pilot conclusions remain unchanged.']
        (output / 'ASSESSMENT.md').write_text('\n'.join(lines)+'\n')
    except (OSError,ValueError,KeyError) as error:
        result['failure']=str(error)
    s.write(output / 'assessment.json',result)
    s.write(output / 'seal.json',s.inventory(output))
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('runtime','prepared','output'): p.add_argument(name,type=Path)
    args=p.parse_args()
    raise SystemExit(audit(args.runtime,args.prepared,args.output)['status']!='complete')
