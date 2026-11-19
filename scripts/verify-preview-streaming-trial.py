#!/usr/bin/env python3
"""Independent offline trial verifier; imports neither runner nor build recipes."""
import argparse
import importlib.util
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('streaming_verified_evidence', Path(__file__).with_name('preview-streaming-trial-evidence.py'))
e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e)
h = e.h


def schedule():
    values = [(arm, None, 0) for arm in ('control', 'candidate')]
    for block in range(10):
        order = ['candidate', 'control'] if block & 1 else ['control', 'candidate']
        values.extend((arm, block, sample) for arm in order for sample in range(10))
    return [dict(index=i, arm=a, block=b, observation=n, warmup=b is None, count=1)
            for i, (a, b, n) in enumerate(values)]


def statistics(rows, complete):
    def cell(values):
        data = sorted(values)
        if not data: return None
        count = len(data)
        middle = count // 2
        median = data[middle] if count % 2 else (data[middle - 1] + data[middle]) / 2
        return dict(count=count, median=median, p95=data[(95 * count + 99) // 100 - 1])
    measured = [r for r in rows if r['schedule']['block'] is not None]
    populations = {arm: {event: cell([r['sample'][event] for r in measured if r['schedule']['arm'] == arm])
        for event in ('first_ms', 'final_ms')} for arm in ('control', 'candidate')}
    blocks, signs = [], []
    for block in range(10):
        for event in ('first_ms', 'final_ms'):
            values = {arm: [r['sample'][event] for r in measured if r['schedule']['arm'] == arm and
                            r['schedule']['block'] == block] for arm in ('control', 'candidate')}
            if all(len(v) == 10 for v in values.values()):
                a, b = cell(values['control']), cell(values['candidate'])
                blocks.append(dict(block=block, event=event, median=b['median'] - a['median'], p95=b['p95'] - a['p95']))
    for event in ('first_ms', 'final_ms'):
        for statistic in ('median', 'p95'):
            counts = dict(negative=0, zero=0, positive=0)
            for block in blocks:
                if block['event'] == event:
                    value = block[statistic]
                    counts['negative' if value < 0 else 'positive' if value > 0 else 'zero'] += 1
            signs.append(dict(event=event, statistic=statistic, **counts))
    decision = 'Evidence insufficient'
    if complete:
        h.require(len(rows) == 202 and all(v['count'] == 100 for arm in populations.values() for v in arm.values()), 'complete populations')
        decision = 'Recommend later production work'
        for event in ('first_ms', 'final_ms'):
            a, b = populations['control'][event], populations['candidate'][event]
            if b['median'] > a['median'] or a['p95'] - b['p95'] < 5:
                decision = 'Deferred'
    return dict(populations=populations, blocks=blocks, signs=signs, decision=decision)


def check_protocol(value):
    expected = dict(version=1, schedule=schedule(), fresh_processes=202, measured_per_arm=100,
        warmups_per_arm=1, jobs=4, build_type='Release', chunk_bytes=65536, workload_seconds=30,
        shared_cleanup_seconds=5, retries=0, recording=False, offscreen=True, cache_flushing=False,
        affinity_changes=False, artificial_load=False, additional_timed_instrumentation=False,
        rule='Both startup p95s improve by at least 5 ms and neither median regresses.',
        qualification='78/80 unchanged', historical_timing_transfer=False, overhead_correction=False,
        loading_identity='New input/build identities only; uncaptured loading identities unavailable.')
    h.require(value == expected, 'protocol drift')


def check_build(built):
    package = e.check_built(built)
    e.check_package(package, provenance=True)
    check_protocol(h.read(package / 'protocol.json'))
    # Validate the actual commands, caches and test outcomes, not just declared success.
    for arm in e.ARMS:
        base = built / arm
        for component in ('holonight-images', 'holonight-thumbnails', 'holonight-file-browser'):
            cache = (base / 'build' / component / 'CMakeCache.txt').read_text()
            for line in ('CMAKE_BUILD_TYPE:STRING=Release', 'BUILD_TESTING:BOOL=OFF',
                         'CMAKE_INSTALL_PREFIX:PATH=' + str(base / 'prefix')):
                h.require(line in cache.splitlines(), 'native build configuration')
            command = h.read(base / (component + '-compile-command.json'))['argv']
            h.require(command[-2:] == ['--parallel', '4'], 'four build jobs')
        for name in ('correctness-tests', 'correctness-compile', 'harness-compile'):
            h.require(h.read(base / (name + '-process.json'))['exit'] == 0, 'failed native check')
        text = (base / 'correctness-tests.stdout').read_text()
        h.require(any(line in text.splitlines() for line in
                      ('100% tests passed, 0 tests failed out of 4', '100% tests passed out of 4')) and
                  sum(' Passed ' in line for line in text.splitlines()) == 4, 'focused native/consumer count')
        h.require('CMAKE_BUILD_TYPE:STRING=Release' in (base / 'reuse-harness/CMakeCache.txt').read_text().splitlines(), 'harness Release')
        for path in base.glob('*-process.json'):
            h.require(h.read(path)['exit'] == 0, 'build command failure')
    h.require(h.read(built / 'loop-tests-process.json')['exit'] == 0 and
              'Passed 11 streaming cases' in (built / 'loop-tests.stdout').read_text(), 'actual loop tests')
    h.require(h.read(built / 'tools.json') == e.tools(), 'build tool identity')
    return package


def verify(output):
    h.sealed(output)
    assessment = h.read(output / 'assessment.json')
    status = assessment['status']
    if status != 'blocked':
        h.require(h.read(output / 'integrity.json')['passed'], 'action integrity incomplete')
    if status == 'prepared':
        e.check_package(output, provenance=True)
        check_protocol(h.read(output / 'protocol.json'))
        return dict(status='passed', outcome=status, evidence_seal=h.digest(output / 'seal.json'))
    if status == 'built':
        check_build(output)
        return dict(status='passed', outcome=status, evidence_seal=h.digest(output / 'seal.json'))
    h.require(status in ('complete', 'blocked'), 'unknown assessment')
    binding = h.read(output / 'built.json')
    built = Path(binding['path'])
    h.require(h.digest(built / 'seal.json') == binding['seal'], 'execution/build seal')
    package = check_build(built)
    check_protocol(h.read(output / 'protocol.json'))
    e.check_tools(output)
    rows = h.read(output / 'observations.json')
    expected = schedule()
    h.require([r['schedule'] for r in rows] == expected[:len(rows)], 'schedule membership/order')
    attempted = assessment['attempted']
    h.require(type(attempted) is int and len(rows) <= attempted <= min(202, len(rows) + 1) and
              assessment['unexecuted'] == expected[attempted:] and assessment['accepted'] == len(rows), 'stop on failure accounting')
    request = h.read(output / 'stage-request.json')
    runtime = Path(request['runtime'])
    import hashlib
    h.require(runtime == Path('/run') / ('holonight-streaming-' + hashlib.sha256(str(output).encode()).hexdigest()[:20]), 'protected runtime binding')
    commands = h.read(output / 'commands.json')
    expected_commands = [dict(schedule=row, argv=[str(built / row['arm'] / 'reuse-harness/preview-benchmark'),
        str(runtime / row['arm']), str(package / '3200x2400.png'), 'startup', '1',
        str(output / f"{row['index']:03}" / 'harness.json')]) for row in expected]
    h.require(commands == expected_commands, 'frozen command schedule')
    if not (output / 'staged-outer.json').exists():
        h.require(status == 'blocked' and attempted == 0 and not rows and
                  not any(p.is_dir() and p.name.isdigit() for p in output.iterdir()), 'missing staged evidence')
        summary = statistics([], False)
        h.require(h.read(output / 'statistics.json') == summary and
                  assessment['decision'] == summary['decision'], 'partial decision drift')
        return dict(status='passed', outcome='blocked', assessment='incomplete', decision='Evidence insufficient',
            evidence_seal=h.digest(output / 'seal.json'), imports_runner=False, imports_build_recipes=False)
    h.require(h.read(output / 'staged-outer.json') == h.read(output / 'cleanup-expected.json'), 'staging cleanup binding')
    outer = h.read(output / 'staged-outer.json')
    h.require(all(v['uid'] == 0 and not v['mode'] & 0o022 for v in outer.values()), 'protected staging identities')
    for arm in e.ARMS:
        selector = bytes.fromhex(outer[arm + '/current']['bytes']).decode().strip()
        h.require(selector and '/' not in selector and selector not in ('.', '..'), 'staged selector')
        prefix = arm + '/generations/' + selector + '/'
        payload = {name[len(prefix):]: v['sha256'] for name, v in outer.items()
                   if name.startswith(prefix) and v['kind'] == 'file'}
        h.require(payload == h.read(built / arm / 'runtime-inventory.json'), 'staged complete payload membership')
    directories = {p.name for p in output.iterdir() if p.is_dir() and p.name.isdigit()}
    h.require(directories == {f'{i:03}' for i in range(attempted)}, 'unexpected process membership')
    for index, row in enumerate(rows):
        directory = output / f'{index:03}'
        raw = h.read(directory / 'harness.json')
        h.require(row['sample'] == e.sample(raw), 'raw sample binding')
        process = h.read(directory / 'harness.process.json')
        partial = h.read(directory / 'harness-recording/partial.json')
        cleanup = h.read(directory / 'cleanup.json')
        h.require(cleanup['deadline'] == partial['cleanup_deadline'] and
                  row['cleanup_seconds'] == cleanup['stopped'] - (cleanup['deadline'] - 5), 'cleanup raw timer binding')
        gate = h.read(directory / 'harness-recording/gate.json')
        release = h.read(directory / 'harness-recording/release.json')
        h.require(gate['argv'] == commands[index]['argv'] and gate['uid'] == 1000 and
                  gate['pid'] == process['pid'] == release['pid'] and not release['profiled'], 'process command/identity')
        h.require(process['exit'] == 0 and not process['timeout'] and
                  0 <= (process['stop_ns'] - process['start_ns']) / 1e9 <= 30, 'workload deadline')
        h.require(partial['cleanup_outcomes']['passed'] and partial['gate_reaped'] and
                  partial['released'] and not partial['acknowledged'] and not partial['timeout'] and
                  not partial['first_failure'] and 0 <= row['cleanup_seconds'] <= 5, 'cleanup deadline/correctness')
        h.require(not list(directory.rglob('perf.data')), 'unexpected recording')
        for phase in ('before', 'after'):
            scope = h.read(directory / phase / 'scopes.json')
            h.require(scope['exit'] == 0 and not scope['stdout'].strip() and not scope['cgroups'], 'residual scopes')
    complete = status == 'complete'
    if complete:
        h.require(attempted == len(rows) == 202 and assessment['cleanup_verified'], 'incomplete assessment')
        for action in ('stage', 'cleanup'):
            record = h.read(output / (action + '-execution.json'))
            authorization = h.read(output / (action + '-authorization.json'))
            h.require(record['exit'] == authorization['exit'] == 0 and record['worker_reaped'] and
                      authorization['worker_reaped'] and not record['interrupted'] and
                      not authorization['interrupted'] and h.read(output / (action + '-worker.json'))['passed'], 'staging/cleanup completion')
    summary = statistics(rows, complete)
    h.require(h.read(output / 'statistics.json') == summary and assessment['decision'] == summary['decision'], 'statistics/decision drift')
    return dict(status='passed', outcome=status, assessment='complete' if complete else 'incomplete',
        decision=summary['decision'], evidence_seal=h.digest(output / 'seal.json'),
        imports_runner=False, imports_build_recipes=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output = args.output.absolute()
    args.evidence = args.evidence.absolute()
    h.require(args.output == args.output.resolve() and not args.output.exists() and
              not args.output.is_relative_to(args.evidence), 'verification output collision/overlap')
    try:
        result = verify(args.evidence.absolute())
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        result = dict(status='failed', decision='Evidence insufficient', failure=str(error))
    h.write(args.output, result)
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
