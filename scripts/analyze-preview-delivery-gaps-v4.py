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


IDENTITY = ('pid', 'service', 'observation', 'job', 'worker', 'generation')
CONTEXT = ('preparation', 'session', 'transaction')
ENVELOPES = ('transaction_wrapper', 'retirement_call')


def owns(record, delivery, envelope=False):
    return (all(record[k] == delivery[k] for k in IDENTITY)
            and all(record[k] == delivery[k] or (envelope and record[k] is None)
                    for k in CONTEXT))


def endpoint_rows(report, variant, fixture):
    s.require(isinstance(report, dict), 'malformed report')
    for key in ('windows', 'spans', 'handoffs', 'events', 'unavailable'):
        s.require(isinstance(report.get(key), list), 'malformed report: ' + key)
    s.require(len(report['windows']) == 6, 'six complete endpoint windows required')
    rows, identities = [], set()
    for window in report['windows']:
        s.require(isinstance(window, dict) and all(k in window for k in
                  ('delivery', 'start_ns', 'stop_ns', 'endpoint', 'boundary', 'categories')),
                  'incomplete endpoint window')
        e = window['delivery']; start, stop = window['start_ns'], window['stop_ns']
        s.require(isinstance(e, dict) and all(k in e for k in IDENTITY + CONTEXT + ('publication',)),
                  'malformed endpoint identity')
        s.require(all(e[k] is not None for k in IDENTITY) and type(start) is int
                  and type(stop) is int and 0 <= start <= stop, 'invalid endpoint window')
        identity = (e['pid'], e['publication'], window['endpoint'])
        s.require(window['endpoint'] in ('pixels', 'metadata') and identity not in identities,
                  'duplicate or invalid endpoint window')
        identities.add(identity)
        s.require(isinstance(window['boundary'], dict) and isinstance(window['categories'], dict),
                  'malformed endpoint boundary or categories')
        handoffs = [h for h in report['handoffs'] if h['publication'] == e['publication'] and h['pid'] == e['pid']]
        s.require(len(handoffs) == 1, 'exactly one matching handoff required')
        s.require(owns(handoffs[0]['identity'], e), 'handoff identity mismatch')
        owned = [x for x in report['spans'] if owns(x['begin'], e, x['operation'] in ENVELOPES)
                 and not (x['operation'] == 'effective_cleanup' and x['begin']['transaction'] is None)]
        specific = [x for x in owned if x['operation'] not in ENVELOPES]
        rows.append(dict(variant=variant, fixture=fixture, endpoint=window['endpoint'],
                         observation=e['observation'], elapsed_ns=stop-start, boundary=window['boundary'],
                         delivery=e, envelopes=intervals(start, stop, owned), specific=intervals(start, stop, specific),
                         categories=window['categories'], handoff=handoffs[0], unavailable=report['unavailable'],
                         operations=owned, branch_points=[x for x in report['events'] if x['edge'] == 'point' and owns(x, e)]))
    s.require(len({r['observation'] for r in rows}) == 3 and all(
        {r['endpoint'] for r in rows if r['observation'] == observation} == {'pixels', 'metadata'}
        for observation in {r['observation'] for r in rows}), 'incomplete observation endpoints')
    return rows


def validate_probes(prepared, variant):
    probes = s.read(prepared / variant / 'probe-to-source.json')['probes']
    s.require(isinstance(probes, list), 'malformed probes')
    for probe in probes:
        s.require(isinstance(probe, dict) and all(k in probe for k in ('file', 'sha256', 'line', 'text'))
                  and isinstance(probe['file'], str), 'malformed probe')
        p = Path(probe['file']).resolve()
        s.require(p.is_relative_to(prepared / variant), 'probe outside prepared variant')
        s.require(s.digest(p) == probe['sha256'], 'probe hash mismatch')
        lines = p.read_text().splitlines()
        line = probe['line']
        s.require(type(line) is int and 1 <= line <= len(lines), 'invalid probe line')
        s.require(lines[line-1] == probe['text'], 'probe text mismatch')
    return probes


def audit(runtime, prepared, output):
    s.require(not output.is_symlink(), 'fresh destination required')
    runtime, prepared, output = (p.resolve() for p in (runtime, prepared, output))
    s.require(output.is_relative_to(s.ROOT / 'build') and all(not output.is_relative_to(p) and not p.is_relative_to(output) for p in (runtime, prepared)), 'disjoint build destination required')
    s.require(not output.exists() and not output.is_symlink(), 'fresh destination required')
    output.mkdir()
    result = dict(status='blocked', attribution_complete=False)
    try:
        before = {str(p): s.digest(p) for root in (runtime, prepared) for p in root.rglob('*') if p.is_file()}
        tools = {str(p): s.digest(p) for p in (s.ROOT / 'scripts').glob('*.py')}
        s.smoke.verify_hashes(runtime, s.read(runtime / 'seal.json'))
        assessment = s.read(runtime / 'assessment.json')
        s.require(assessment['status'] == 'passed' and assessment['passed_observations'] == 36 and len(assessment['invocations']) == 12 and all(assessment[k] for k in ('cleanup_verified','runtime_integrity','retained_integrity')), 'runtime gate failed')
        manifest = s.read(prepared / 'manifest.json')
        s.require(manifest['status'] == 'prepared' and manifest['unchanged'] is True and manifest['issues'] == [] and manifest['before'] == manifest['after'], 'prepared manifest invalid')
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
            probes = validate_probes(prepared, variant)
            try:
                invocation_rows = endpoint_rows(report, variant, s.FIXTURES[index % 3])
            except (KeyError, TypeError, IndexError) as error:
                raise ValueError('malformed endpoint report: ' + str(error)) from error
            for row in invocation_rows:
                rows.append(row)
                groups[variant, row['fixture'], row['endpoint']].append(row['elapsed_ns'])
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
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        result['failure']=str(error)
        (output / 'ASSESSMENT.md').write_text('# Blocked offline v4 accounting\n\n' + str(error) + '\n')
    s.write(output / 'assessment.json',result)
    s.write(output / 'seal.json',s.inventory(output))
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('runtime','prepared','output'): p.add_argument(name,type=Path)
    args=p.parse_args()
    raise SystemExit(audit(args.runtime,args.prepared,args.output)['status']!='complete')
