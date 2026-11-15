#!/usr/bin/env python3
"""Offline manifest-derived validation work audit. Never launches a workload."""
import argparse
from collections import defaultdict
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('work_validation', ROOT / 'scripts/report-preview-validation.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
read, write, require, o = v.read, v.write, v.require, v.o


def distribution(values):
    values = sorted(values)
    return dict(count=len(values), minimum=values[0], median=statistics.median(values),
                p95=values[math.ceil(.95 * len(values))-1], maximum=values[-1]) if values else dict(count=0)


def provenance(execution, report):
    registration = read(execution / 'preregistration.json')
    package = Path(registration['package'])
    inputs = read(package / 'inputs.json')
    roots = {execution, report, package, Path(inputs['built']), Path(inputs['package']),
             *(Path(p) for p in inputs['seals'])}
    for root in roots:
        o.check_output(root)
    require(o.digest(package / 'seal.json') == registration['package_seal'], 'package binding drift')
    for name, digest in inputs['seals'].items():
        require(o.digest(Path(name) / 'seal.json') == digest, 'frozen provenance binding drift')
    prefix = execution.name.removesuffix('-execution')
    records = [execution.parent / (prefix + suffix) for suffix in
               ('-independent.json', '-final-verification.json')]
    for path in records:
        record = read(path)
        require(record['status'] == 'passed' and record['experiment_status'] == 'complete' and
                record['execution_seal'] == o.digest(execution / 'seal.json') and
                record['package_seal'] == o.digest(package / 'seal.json') and
                (record['invocations'], record['measured_observations'], record['warmup_observations']) == (10, 40, 2),
                'independent verification binding mismatch')
    report_status = read(report / 'assessment.json')
    require(report_status['status'] == 'complete' and report_status['observations'] == 40 and
            report_status['warmups'] == 2, 'report blocked or incomplete')
    manifest = Path(inputs['built']) / 'validation/C/runtime/manifest.json'
    mapping = v.r.ordinal_mapping(read(manifest))
    require(mapping == inputs['mapping'] == read(manifest.parents[1] / 'manifest-ordinals.json'), 'manifest mapping drift')
    for row in mapping:
        payload = manifest.parent / row['path']
        require(payload.stat().st_size == row['size'] and o.digest(payload) == row['sha256'], 'payload drift')
    identities = {str(root / 'seal.json'): o.digest(root / 'seal.json') for root in roots}
    identities.update({str(path): o.digest(path) for path in records})
    return inputs, mapping, identities


def source_audit(inputs):
    base = Path(inputs['package']) / 'validation/C'
    inventory = read(base / 'source-inventory.json')['source']
    names = ('holonight-images/src/isolated/generation.cpp', 'holonight-images/src/isolated/verification.cpp',
             'holonight-images/src/isolated/runtime.cpp', 'holonight-images/src/isolated/helper.cpp',
             'holonight-file-browser/src/preview/session_pool.cpp',
             'holonight-file-browser/src/preview/preview_service.cpp')
    citations = []
    for name in names:
        path = base / 'source' / name
        require(name in inventory and o.digest(path) == inventory[name], 'frozen source drift: ' + name)
        lines = path.read_text().splitlines()
        tokens = ('RuntimeOwner', 'refresh(', 'refreshRuntime', 'verifyRuntime', 'verifyProtectedRuntime',
                  'ValidationTrace::', 'StandbyTrace::', 'PreviewSessionPool', 'generation', 'lease')
        selected = {i for n, line in enumerate(lines) if any(t in line for t in tokens)
                    for i in range(max(0, n-2), min(len(lines), n+4))}
        citations.append(dict(file=str(path), sha256=inventory[name],
                              excerpts=[dict(line=i+1, text=lines[i]) for i in sorted(selected)],
                              validation_instrumented='ValidationTrace::' in '\n'.join(lines)))
    return citations


def accounting(part, mapping):
    spans = [{k: value for k, value in s.items() if k not in ('clipped_start', 'clipped_stop')}
             for s in part['spans']]
    require(all(s['stop'] > s['start'] and s['end']['outcome'] == 'returned' for s in spans),
            'nonpositive duration or exceptional validation')
    v.operation_ownership(spans, 'C')
    files = v.mapped_files(spans, mapping)
    require(files == part['files'], 'saved file accounting mismatch')
    root = next(s for s in spans if s['parent'] == 0)
    require(part['duration_ns'] == root['stop']-root['start'], 'saved validation duration mismatch')
    rows = []
    for file in files:
        span = next(s for s in file['operations'] if s['operation'] == 'read_hash')
        ns = span['stop']-span['start']
        rows.append(dict(**{k: file[k] for k in ('ordinal', 'path', 'size', 'sha256')},
                         successful_passes=1, inferred_bytes=file['size'], read_hash_ns=ns,
                         bytes_per_second=file['size'] * 1e9 / ns,
                         citations=[span['begin'], span['end']]))
    ns = sum(row['read_hash_ns'] for row in rows)
    # File spans are sequential children on one validator thread. No inclusive
    # generation/runtime/container durations are summed or subtracted twice.
    require(len({(s['begin']['pid'], s['begin']['tid']) for s in spans}) == 1 and
            ns <= part['duration_ns'], 'overlapping read/hash ownership')
    return dict(validation_ns=part['duration_ns'], read_hash_ns=ns,
                residual_validation_ns=part['duration_ns']-ns,
                inferred_bytes=sum(row['inferred_bytes'] for row in rows),
                bytes_per_second=sum(row['inferred_bytes'] for row in rows)*1e9/ns, files=rows,
                root=dict(pid=root['begin']['pid'], service=root['begin']['service'], span=root['begin']['span']))


def lifecycle_binding(root, lifecycle, observation, setup):
    """Identity agreement is required in addition to inclusive boundary checks."""
    rows = lifecycle['unassigned'] if setup else next(
        a['timeline'] for a in lifecycle['accounting'] if a['sample'] == observation-1)
    matches = [s for s in rows if s['phase'] == 'generation_validation' and
               all(s['begin'].get(k) == (root['begin'].get(k) or 0) for k in
                   ('pid', 'tid', 'service', 'observation')) and
               s['start'] <= root['start'] < root['stop'] <= s['stop']]
    require(len(matches) == 1, 'unclassified validation root')
    # Frozen source puts this probe in refresh(), called both by construction
    # and explicit refresh. Construction is asynchronous; service_construction
    # body containment is deliberately not required.
    constructions = [s for s in rows if s['phase'] == 'service_construction' and
                     all(s['begin'].get(k) == (root['begin'].get(k) or 0) for k in
                         ('pid', 'service', 'observation'))]
    require(len(constructions) == 1, 'missing service construction evidence')
    return dict(classification='setup construction' if setup else 'observation construction',
                binding=matches[0], construction=constructions[0],
                limitation='First refresh in a newly constructed service; owner construction inferred from frozen call path. '
                           'No generation identifier is emitted. Object addresses are not generation identity.')


def summarize(rows):
    result = []
    for population in ('measured', 'warmup', 'setup'):
        for arm in ('all', 'unprofiled', 'profiled'):
            for block in ('pooled', 0, 1, 2, 3):
                selected = [r for r in rows if r['population'] == population and
                            (arm == 'all' or r['arm'] == arm) and (block == 'pooled' or r['block'] == block)]
                if not selected:
                    continue
                files = [f for r in selected for f in r['files']]
                def total(fs):
                    ns = sum(f['read_hash_ns'] for f in fs)
                    size = sum(f['inferred_bytes'] for f in fs)
                    return dict(successful_passes=len(fs), inferred_bytes=size, read_hash_ns=ns,
                                bytes_per_second=size*1e9/ns,
                                duration_distribution=distribution([f['read_hash_ns'] for f in fs]),
                                throughput_distribution=distribution([f['bytes_per_second'] for f in fs]))
                result.append(dict(population=population, arm=arm, block=block, pooled=total(files),
                    timings={k: distribution([r[k] for r in selected]) for k in
                             ('validation_ns', 'read_hash_ns', 'residual_validation_ns', 'inferred_bytes', 'bytes_per_second')},
                    files=[dict(ordinal=i, **total([f for f in files if f['ordinal'] == i]))
                           for i in sorted({f['ordinal'] for f in files})]))
    return result


def audit(execution, report, output):
    o.fresh(output, execution, report)
    result = dict(status='blocked')
    try:
        inputs, mapping, identities = provenance(execution, report)
        source = source_audit(inputs)
        assessment = read(execution / 'assessment.json')
        require(assessment['status'] == 'complete' and len(assessment['invocations']) == 10,
                'incomplete execution')
        rows = []
        for index, entry in enumerate(assessment['invocations']):
            require(entry['status'] == 'passed' and entry['index'] == index and
                    entry['entry'] == read(execution / 'preregistration.json')['commands'][index], 'invocation drift')
            invocation = entry['entry']['invocation']
            target = Path(entry['entry']['argv'][-1])
            require(target == execution / 'observations' / f'{index:03}.json', 'invocation path mismatch')
            raw = v.spans(v.records(target))
            lifecycle = read(target.with_suffix('.v3.json'))
            observations = read(target.with_suffix('.cpu-observations.json'))
            setup = read(target.with_suffix('.validation-setup.json'))
            require(len(observations) == invocation['observations'], 'observation count drift')
            assigned = set()
            for saved, is_setup in [(r, False) for r in observations] + [(r, True) for r in setup]:
                part = saved['validation']
                keys = {(s['begin']['pid'], s['begin']['span']) for s in part['spans']}
                require(not assigned.intersection(keys), 'duplicate saved validation ownership')
                owned = [s for s in raw if (s['begin']['pid'], s['begin']['span']) in keys]
                # Saved spans include clipping metadata; raw paired fields must agree exactly.
                require(len(owned) == len(part['spans']) and all(
                    all(s[k] == next(x for x in part['spans'] if x['begin']['pid'] == s['begin']['pid'] and
                        x['begin']['span'] == s['begin']['span'])[k] for k in s) for s in owned), 'raw/saved span mismatch')
                assigned.update(keys)
                root = next(s for s in owned if s['parent'] == 0)
                observation = None if is_setup else saved['observation']
                require(root['begin']['observation'] == observation, 'observation ownership mismatch')
                value = accounting(part, mapping)
                value.update(invocation=index, arm=invocation['arm'], block=invocation['block'],
                             observation=observation, population='setup' if is_setup else
                             ('warmup' if invocation['warmup'] else 'measured'),
                             lifecycle=lifecycle_binding(root, lifecycle, observation, is_setup))
                if not is_setup:
                    value['endpoints_ns'] = {key: saved['endpoints'][key]['harness_latency_ns']
                                             for key in ('pixels', 'metadata')}
                rows.append(value)
            require(assigned == {(s['begin']['pid'], s['begin']['span']) for s in raw}, 'unexplained validation roots')
        require(sum(r['population'] == 'measured' for r in rows) == 40 and
                sum(r['population'] == 'warmup' for r in rows) == 2, 'population mismatch')
        lifetimes = defaultdict(list)
        for row in rows:
            lifetimes[row['invocation'], row['root']['pid'], row['root']['service']].append(row)
        # Multiple roots alone cannot establish unchanged generation/owner identity.
        require(all(len(rs) == 1 for rs in lifetimes.values()),
                'multiple refreshes require explicit owner/generation evidence; construction classification unavailable')
        tails = read(report / 'tails.json')
        require(len(read(report / 'observations.json')) == 40, 'report population mismatch')
        for row in read(report / 'observations.json'):
            match = [r for r in rows if r['population'] == 'measured' and
                     (r['invocation'], r['observation']) == (row['invocation'], row['observation'])]
            require(len(match) == 1 and match[0]['validation_ns'] == row['validation_ns'] and
                    match[0]['arm'] == row['arm'] and match[0]['block'] == row['block'] and
                    match[0]['endpoints_ns'] == dict(pixels=row['pixel_ns'], metadata=row['metadata_ns']),
                    'report reconciliation failed')
        proposal = dict(kind='native SHA-256 throughput diagnostic',
            text='Propose one bounded native Qt-versus-installed-backend SHA-256 throughput diagnostic on the frozen payload. '
                 'No diagnostic is executed by this audit. Offline elapsed throughput cannot establish unexpectedly slow crypto.')
        write(output / 'accounting.json', rows)
        write(output / 'distributions.json', summarize(rows))
        write(output / 'source-citations.json', source)
        write(output / 'tails.json', tails)
        write(output / 'proposal.json', proposal)
        write(output / 'lifetimes.json', [dict(invocation=k[0], pid=k[1], service=k[2], validations=len(rs),
              inferred_bytes=sum(r['inferred_bytes'] for r in rs), within_lifetime_repeated_bytes=0,
              generation_identity='unproven; matching frozen payload only') for k, rs in lifetimes.items()])
        write(output / 'inputs.json', dict(execution=str(execution), report=str(report), identities=identities, mapping=mapping))
        _, _, after = provenance(execution, report)
        require(after == identities and source_audit(inputs) == source, 'consumed evidence drift')
        result.update(status='complete', observations=40, warmups=2, setup=sum(r['population'] == 'setup' for r in rows),
                      service_lifetimes=len(lifetimes), proposal=proposal['kind'])
        (output / 'REPORT.md').write_text('# Runtime verification work\n\n' +
            '\n'.join(f"{p}: {sum(r['population'] == p for r in rows)} validations; "
                      f"{sum(r['inferred_bytes'] for r in rows if r['population'] == p)} inferred bytes."
                      for p in ('measured', 'warmup', 'setup')) + '\n\n'
            'Bytes are inferred from successful full-file validation, not read counters. Throughput combines reading and hashing '
            'and may include scheduling delays. Pooled rates use summed bytes and durations. CPU sample attribution remains separate. '
            'Generation wrappers are not additional file passes. Residual time subtracts only disjoint read/hash spans.\n\n'
            'Each observed validation belongs to a separate service lifetime. Matching payload content is established; unchanged '
            'generation identity across lifetimes is not. No repeated validation within one unchanged owner/generation lifetime is established. '
            'Owner construction follows the frozen asynchronous pool construction path; service constructor body containment is not assumed.\n\n'
            'Frozen source citations cover owner construction/refresh, pool construction/refresh, fallback launch validation and helper verification. '
            'validation_instrumented flags identify observable source paths. Absence of traces cannot rule out uninstrumented helper verification.\n\n' +
            proposal['text'] + '\n\nNo gain or significance claim. Mutable-runtime validation, generation identity, ownership, leases and installer protections remain intact.\n')
    except (OSError, ValueError, KeyError, TypeError, StopIteration, IndexError) as error:
        result['failure'] = str(error)
    write(output / 'assessment.json', result)
    o.seal(output)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('execution', 'report', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.execution.absolute(), args.report.absolute(), args.output.absolute())
    print(result)
    sys.exit(result['status'] != 'complete')
