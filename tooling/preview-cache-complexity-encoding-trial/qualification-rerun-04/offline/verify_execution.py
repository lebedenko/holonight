#!/usr/bin/env python3
"""Independent reconstruction of the uninstrumented trial; no controller imports."""
import argparse
import math
import os
from pathlib import Path
import pwd
import statistics
import sys
import uuid
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import contract as t
h, e = t.h, t.e
support = e.load('trial_offline_support', t.DIRECTORY / 'offline/verify.py')


def protocol():
    return t.protocol()


def prerequisite(built, correctness):
    h.require(built == t.BUILT and correctness == t.CORRECTNESS, 'fixed trial prerequisites required')
    verify = e.load('trial_independent_correctness', t.DIRECTORY / 'offline/verify_correctness.py')
    proof = verify.verify(correctness)
    record = correctness.with_name(correctness.name + '-independent.json')
    h.require(h.read(record) == proof and proof['status'] == 'passed' and proof['outcome'] == 'qualified' and
              proof['required_cases_passed'] == 130 and proof['failed_command'] is None and proof['completed_commands'] == 61,
              'fresh independent 130-check qualification required')
    return dict(historical=t.prerequisite(), built=dict(path=str(built), seal=h.digest(built / 'seal.json')),
        correctness=dict(path=str(correctness), seal=h.digest(correctness / 'seal.json'),
                         independent_sha256=h.digest(record)))


def verify_schedule(root, built):
    rows = h.read(root / 'schedule.json')
    uid = next(r['uid'] for r in rows if not r['privileged'])
    h.require(type(uid) is int and uid > 0, 'desktop uid required')
    invocations = {}
    for row in rows:
        if row['workload']:
            value = row['environment']['HOLONIGHT_CACHE_INVOCATION']
            h.require(str(uuid.UUID(value)) == value and value not in invocations.values(), 'invocation reuse')
            invocations[row['name']] = value
    h.require(rows == expected_schedule(root, built, uid, invocations), 'independent schedule mismatch')
    return rows


def observation(root, row):
    base = root / row['name']
    value = h.read(base / 'harness.json')
    h.require(value['fixture'] == str(root / 'fixture.png'), 'fixture command mismatch')
    sample = t.sample(value)
    binary = t.BUILT / row['arm'] / 'harness-build/preview-benchmark'
    linked = support.linkage(t.BUILT / 'commands' / (row['arm'] + '-linkage.stdout'))
    images = support.mapped(h.read(base / 'harness.json.loading.json'), binary, linked)
    h.require('CACHE_PUBLICATION' not in (root / 'commands' / (row['name'] + '.stderr')).read_text(),
              'publication probes present')
    return dict(schedule=row['observation'], sample=sample, mapped=images,
                helper_loading='unavailable: helper exited before post-timing capture')


def summarize(rows, complete):
    """Independently calculate ranks, medians and gate; never trust producer statistics."""
    h.require([r['schedule'] for r in rows] == t.schedule()[:len(rows)], 'raw schedule mismatch')
    def distribution(values):
        values = sorted(values)
        if not values:
            return None
        size = len(values)
        middle = values[size // 2] if size % 2 else (values[size // 2 - 1] + values[size // 2]) / 2
        return dict(count=size, median=middle, p95=values[(95 * size + 99) // 100 - 1])
    for row in rows:
        first, final = [row['sample'][k] for k in ('first_ms', 'final_ms')]
        h.require(all(type(v) in (float, int) and math.isfinite(v) for v in (first, final)) and
                  0 <= first <= final <= 30000, 'malformed raw sample')
    measured = [r for r in rows if not r['schedule']['warmup']]
    populations = {a: {k: distribution([r['sample'][k] for r in measured if r['schedule']['arm'] == a])
                      for k in ('first_ms', 'final_ms')} for a in ('control', 'candidate')}
    blocks = []
    for block in range(10):
        for event in ('first_ms', 'final_ms'):
            cells = [[r['sample'][event] for r in measured if r['schedule']['arm'] == arm and
                      r['schedule']['block'] == block] for arm in ('control', 'candidate')]
            if all(len(cell) == 10 for cell in cells):
                control, candidate = [distribution(cell) for cell in cells]
                blocks.append(dict(block=block, event=event, median=candidate['median'] - control['median'],
                                   p95=candidate['p95'] - control['p95']))
    decision = 'Evidence insufficient'
    if complete and len(rows) == 202:
        decision = 'Recommend' if all(populations['control'][k]['p95'] - populations['candidate'][k]['p95'] >= 5 and
            populations['candidate'][k]['median'] <= populations['control'][k]['median'] for k in ('first_ms', 'final_ms')) else 'Deferred'
    return dict(populations=populations, blocks=blocks, decision=decision)


def verify(root):
    h.require(root == t.EXECUTION and root == root.resolve(), 'fixed trial execution root required')
    inventory = h.sealed(root)
    support.tools(root)
    request = h.read(root / 'request.json')
    built = Path(request['built'])
    binding = prerequisite(built, Path(request['correctness']))
    h.require(binding == h.read(root / 'binding.json') and h.read(root / 'protocol.json') == t.protocol(), 'trial binding drift')
    h.require(h.digest(root / 'fixture.png') == binding['historical']['diagnostic']['fixture']['sha256'], 'fixture identity')
    h.require(h.read(root / 'built.json') == dict(path=str(built), seal=h.digest(built / 'seal.json'),
              inventory=h.sealed(built)), 'staging build binding')
    h.require(h.read(root / 'artifact-bindings.json') == h.sealed(built), 'frozen build identity drift')
    rows = verify_schedule(root, built)
    assessment = h.read(root / 'assessment.json')
    names = [r['name'] for r in rows]
    attempted, completed = assessment['attempted'], assessment['completed']
    h.require(attempted == names[:len(attempted)] and completed == attempted[:len(completed)] and
              len(attempted) - len(completed) in (0, 1) and assessment['unexecuted'] == names[len(attempted):],
              'stopped schedule accounting')
    actual = {p.removeprefix('commands/').removesuffix('-command.json') for p in inventory
              if p.startswith('commands/') and p.endswith('-command.json')}
    extras = actual - set(attempted)
    h.require(extras <= {a + suffix for a in t.ARMS for suffix in ('-unstage', '-unstage-authorization')} and
              actual == set(attempted) | extras, 'work after stopped schedule')
    observations, failed, cleanup_failed = [], [], []
    previous = 0
    for row in rows:
        name = row['name']
        if name not in actual:
            continue
        base = root / 'commands' / name
        h.require(h.read(Path(str(base) + '-command.json')) == row, 'executed command mismatch')
        record = h.read(Path(str(base) + '-result.json'))
        h.require(previous <= record['start_ns'] <= record['stop_ns'], 'command chronology')
        previous = record['stop_ns']
        success = record['exit'] == 0 and record['failure'] is None and record['cleanup']
        if not record['cleanup'] or (name.endswith(('-unstage', '-unstage-authorization')) and not success):
            cleanup_failed.append(name)
        if record['cleanup']:
            h.require(0 <= record['cleanup_seconds'] <= 5, 'shared cleanup deadline')
        for suffix in ('.stdout', '.stderr'):
            h.require('commands/' + name + suffix in inventory, 'missing raw output')
        if row['privileged'] and row['argv'] != ['sudo', '-n', '-v']:
            authorization = h.read(root / 'commands' / (name + '-authorization-result.json'))
            h.require(authorization['exit'] == 0 and authorization['failure'] is None and authorization['cleanup'], 'authorization loss')
        if name in completed:
            h.require(success, 'completed failed command')
            if row['workload']:
                h.require(0 <= (record['process_stop_ns'] - record['launched_ns']) / 1e9 <= 30, 'workload deadline exceeded')
                for phase in ('before', 'after'):
                    scope = h.read(Path(str(base) + '-scopes-' + phase + '.json'))
                    h.require(scope['isolated'] and scope['exit'] == 0 and not scope['stdout'].strip() and
                              not scope['cgroups'], 'scope cleanup proof')
                observations.append(observation(root, row))
        elif name in attempted:
            failure = record['failure']
            if success and row['workload']:
                try:
                    observation(root, row)
                except (OSError, ValueError, KeyError, TypeError) as error:
                    failure = str(error)
            h.require(failure or not success, 'unexplained stopped command')
            failed.append(name)
    h.require(failed == attempted[len(completed):] and h.read(root / 'observations.json') == observations and
              assessment['observations'] == len(observations), 'raw observation accounting')
    for arm in t.ARMS:
        staging = root / (arm + '-staging.json')
        if arm + '-stage' in completed:
            h.require(staging.exists(), 'missing staged identity')
        if staging.exists():
            value = h.read(staging)
            h.require(value['owner'] == dict(output=str(root), arm=arm, built=str(built),
                seal=h.digest(built / 'seal.json')) and value['runtime'] == str(protected_path(root, arm)), 'staging ownership')
            generations = [p.split('/')[1] for p in value['tree'] if p.startswith('generations/') and p.count('/') == 1]
            h.require(len(generations) == 1, 'generation membership')
            for path, digest in h.inventory(built / arm / 'runtime').items():
                entry = value['tree']['generations/' + generations[0] + '/' + path]
                h.require(entry['sha256'] == digest and entry['uid'] == 0 and not entry['mode'] & 0o022, 'runtime identity/protection')
            if assessment['cleanup']:
                h.require(arm + '-unstage' in actual and not os.path.lexists(value['runtime']) and
                    h.read(root / (arm + '-staging-cleanup.json')) == dict(removed=True, owner=value['owner']), 'owned cleanup missing')
    if cleanup_failed:
        h.require(not assessment['cleanup'], 'false cleanup success')
    complete = assessment['status'] == 'complete'
    if complete:
        h.require(completed == names and not failed and assessment['cleanup'], 'false complete trial')
    else:
        h.require(assessment['status'] == 'blocked' and (failed or cleanup_failed or assessment.get('failure')), 'unsupported blocked trial')
    stats = summarize(observations, complete and assessment['cleanup'])
    h.require(stats == h.read(root / 'statistics.json') and assessment['decision'] == stats['decision'], 'statistics/decision mismatch')
    fixed = {'environment.json', 'artifact-bindings.json', 'request.json', 'built.json', 'binding.json', 'protocol.json', 'fixture.png', 'tools.json', 'schedule.json',
             'integrity.json', 'observations.json', 'assessment.json', 'statistics.json', 'REPORT.md', 'seal.json'}
    fixed |= {'tools/' + t.snapshot_name(p) for p in h.read(root/'tools.json')}
    fixed |= {a + suffix for a in t.ARMS for suffix in ('-staging.json', '-staging-cleanup.json')}
    fixed |= {'commands/' + name + suffix for name in actual for suffix in
              ('-command.json', '-result.json', '.stdout', '.stderr', '-scopes-before.json', '-scopes-after.json')}
    h.require(all(name in fixed or any(name in {row['name'] + '/' + suffix for suffix in ('harness.json', 'harness.json.loading.json', 'observation.json')} or
                    name.startswith((row['name'] + '/cache/', row['name'] + '/source/')) for row in rows if row['workload'])
                  for name in inventory), 'unexpected trial artifact')
    return dict(status='passed', outcome=assessment['status'], decision=stats['decision'], observations=len(observations),
        measured=sum(not r['schedule']['warmup'] for r in observations), cleanup=assessment['cleanup'],
        failed_command=failed[0] if failed else None, evidence_seal=h.digest(root / 'seal.json'), imports_runner=False,
        verifier_sha256=h.digest(Path(__file__)))


def protected_path(root, arm):
    import hashlib
    return Path('/run') / ('holonight-directional-' + hashlib.sha256(str(root).encode()).hexdigest()[:20] + '-' + arm)


def expected_schedule(output, built, uid, invocations):
    rows = []
    def add(name, argv, arm=None, privileged=False, workload=False, observation=None):
        environment = dict(PATH='/usr/bin:/bin', HOME=pwd.getpwuid(uid).pw_dir, LANG='C.UTF-8',
            QT_QPA_PLATFORM='offscreen', CMAKE_BUILD_PARALLEL_LEVEL='4',
            XDG_RUNTIME_DIR='/run/user/' + str(uid), DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/' + str(uid) + '/bus')
        if workload:
            base = output / name
            environment.update(HOLONIGHT_CACHE_INVOCATION=invocations[name], HN_SESSION_RUNTIME=str(protected_path(output, arm)),
                HN_BROWSER_SESSION_RUNTIME=str(protected_path(output, arm)),
                XDG_CACHE_HOME=str(base / 'cache'), TMPDIR=str(base / 'source'))
        rows.append(dict(index=len(rows), name=name, argv=[str(arg) for arg in argv], arm=arm,
            privileged=privileged, workload=workload, observation=observation, environment=environment,
            uid=0 if privileged else uid, timeout_seconds=30 if workload else 600,
            launch=dict(process_group=0) if privileged else dict(start_new_session=True)))
    add('authorization', ['sudo', '-n', '-v'], privileged=True)
    for arm in ('control', 'candidate'):
        add(arm + '-stage-authorization', ['sudo', '-n', '-v'], privileged=True)
        add(arm + '-stage', ['sudo', '-n', sys.executable, t.DIRECTORY / 'stage.py',
            '--output', output, '--arm', arm], arm, privileged=True)
    for observation in t.schedule():
        arm = observation['arm']
        name = 'observation-' + str(observation['index']).zfill(2)
        add(name, [built / arm / 'harness-build/preview-benchmark', protected_path(output, arm),
            output / 'fixture.png', 'startup', '1', output / name / 'harness.json'], arm,
            workload=True, observation=observation)
    for arm in ('control', 'candidate'):
        add(arm + '-unstage-authorization', ['sudo', '-n', '-v'], privileged=True)
        add(arm + '-unstage', ['sudo', '-n', sys.executable, t.DIRECTORY / 'stage.py',
            '--output', output, '--arm', arm, '--remove'], arm, privileged=True)
    return rows



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.evidence.absolute(), args.output.absolute()
    h.require(not output.exists() and not output.is_relative_to(root) and not root.is_relative_to(output), 'verification collision')
    try:
        result = verify(root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = dict(status='failed', decision='Evidence insufficient', failure=str(error))
    h.write(output, result)
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
