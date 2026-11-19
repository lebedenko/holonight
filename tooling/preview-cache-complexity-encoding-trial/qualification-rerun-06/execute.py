#!/usr/bin/env python3
"""Run one frozen cache-publication diagnostic after qualified correctness."""
import argparse
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import time
import uuid

sys.dont_write_bytecode = True
import correctness as c
import qualify
import stage

h, e = c.h, c.e
t = c.t
v = e.load('publication_trial_verifier', c.DIRECTORY / 'offline/verify_execution.py')
ERRORS = (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError, KeyboardInterrupt)
OUTPUT_NAME = t.EXECUTION.name


def validate_request(built, correctness, output):
    h.require(output == output.resolve() and output.parent == e.ROOT / 'build' and output.name == OUTPUT_NAME,
              'fresh diagnostic attempt path required')
    h.require(not os.path.lexists(output), 'diagnostic collision')
    h.require(output.parent.is_dir() and os.access(output.parent, os.W_OK | os.X_OK), 'destination unavailable')
    for path in (built, correctness, e.PACKAGE, c.DIRECTORY, e.ROOT / 'tests'):
        h.require(path == path.resolve() and not output.is_relative_to(path) and not path.is_relative_to(output),
                  'noncanonical or overlapping diagnostic input')
    uid = os.getuid()
    h.require(uid != 0 and os.geteuid() == uid, 'desktop user required')
    runtime = Path('/run/user') / str(uid)
    h.require(runtime == runtime.resolve() and runtime.is_dir() and runtime.stat().st_uid == uid and
              (runtime / 'bus').is_socket() and os.environ.get('XDG_RUNTIME_DIR') == str(runtime) and
              os.environ.get('DBUS_SESSION_BUS_ADDRESS') == 'unix:path=' + str(runtime / 'bus'),
              'desktop session identity mismatch')


def tools():
    return t.tools()


def schedule(built, output):
    uid = os.getuid()
    rows = []
    def add(name, argv, arm=None, privileged=False, workload=False, observation=None):
        environment = dict(PATH='/usr/bin:/bin', HOME=pwd.getpwuid(uid).pw_dir, LANG='C.UTF-8',
            QT_QPA_PLATFORM='offscreen', CMAKE_BUILD_PARALLEL_LEVEL='4',
            XDG_RUNTIME_DIR='/run/user/' + str(uid), DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/' + str(uid) + '/bus')
        if workload:
            base = output / name
            environment.update(HOLONIGHT_CACHE_INVOCATION=str(uuid.uuid4()), HN_SESSION_RUNTIME=str(stage.runtime_path(output, arm)),
                HN_BROWSER_SESSION_RUNTIME=str(stage.runtime_path(output, arm)),
                XDG_CACHE_HOME=str(base / 'cache'), TMPDIR=str(base / 'source'))
        rows.append(dict(index=len(rows), name=name, argv=[str(arg) for arg in argv], arm=arm,
            privileged=privileged, workload=workload, observation=observation, environment=environment,
            uid=0 if privileged else uid, timeout_seconds=30 if workload else 600,
            launch=dict(process_group=0) if privileged else dict(start_new_session=True)))
    add('authorization', ['sudo', '-n', '-v'], privileged=True)
    for arm in ('control', 'candidate'):
        add(arm + '-stage-authorization', ['sudo', '-n', '-v'], privileged=True)
        add(arm + '-stage', ['sudo', '-n', sys.executable, c.DIRECTORY / 'stage.py',
            '--output', output, '--arm', arm], arm, privileged=True)
    for observation in v.protocol()['schedule']:
        arm = observation['arm']
        name = 'observation-' + str(observation['index']).zfill(2)
        add(name, [built / arm / 'harness-build/preview-benchmark', stage.runtime_path(output, arm),
            output / 'fixture.png', 'startup', '1', output / name / 'harness.json'], arm,
            workload=True, observation=observation)
    for arm in ('control', 'candidate'):
        add(arm + '-unstage-authorization', ['sudo', '-n', '-v'], privileged=True)
        add(arm + '-unstage', ['sudo', '-n', sys.executable, c.DIRECTORY / 'stage.py',
            '--output', output, '--arm', arm, '--remove'], arm, privileged=True)
    return rows


def invoke(row, output):
    h.require(os.getuid() != 0, 'model workloads must run as desktop user')
    env = row['environment']
    target = output / 'commands'
    target.mkdir(exist_ok=True)
    h.write(target / (row['name'] + '-command.json'), row)
    record = dict(start_ns=time.monotonic_ns(), exit=None, failure=None, cleanup=False)
    process = None
    try:
        for key in ('XDG_CACHE_HOME', 'TMPDIR', 'PUBLICATION_EVIDENCE'):
            if key in env:
                Path(env[key]).mkdir(parents=True, mode=0o700, exist_ok=True)
        if row['workload']:
            before = qualify.scopes(env, time.monotonic() + 5)
            h.write(target / (row['name'] + '-scopes-before.json'), before)
            h.require(before['isolated'], 'preexisting helper scopes or unavailable supervision')
        with (target / (row['name'] + '.stdout')).open('x') as stdout, (target / (row['name'] + '.stderr')).open('x') as stderr:
            process = subprocess.Popen(row['argv'], cwd=e.ROOT, env=env, stdout=stdout, stderr=stderr, **row['launch'])
            record['pid'] = process.pid
            record['launched_ns'] = time.monotonic_ns()
            record['exit'] = process.wait(timeout=row['timeout_seconds'])
            record['process_stop_ns'] = time.monotonic_ns()
            h.require(record['exit'] == 0, 'command failed: ' + row['name'])
    except ERRORS as error:
        record['failure'] = str(error) or type(error).__name__
    finally:
        for suffix in ('.stdout', '.stderr'):
            (target / (row['name'] + suffix)).touch(exist_ok=True)
        start = time.monotonic()
        deadline = start + 5
        try:
            if process is not None:
                primitive = e.load('observation_cleanup', e.ROOT / 'scripts/run-preview-cpu-profile.py')
                primitive.terminate(process, deadline=deadline)
                try:
                    os.killpg(process.pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    raise ValueError('process group survived cleanup')
            if row['workload']:
                after = qualify.scopes(env, deadline)
                h.write(target / (row['name'] + '-scopes-after.json'), after)
                h.require(after['isolated'], 'helper scope cleanup unproven')
            record['cleanup_seconds'] = time.monotonic() - start
            h.require(time.monotonic() <= deadline, 'shared cleanup budget exceeded')
            record['cleanup'] = True
        except ERRORS as error:
            record['cleanup_failure'] = str(error) or type(error).__name__
            record['failure'] = record['failure'] or record['cleanup_failure']
        record['stop_ns'] = time.monotonic_ns()
        h.write(target / (row['name'] + '-result.json'), record)
    h.require(record['failure'] is None and record['cleanup'], record['failure'] or 'cleanup failed')


def execute(built, correctness, output, authenticate=False):
    validate_request(built, correctness, output)
    # Establish the qualified chain before authentication or creating any attempt.
    binding = v.prerequisite(built, correctness)
    if authenticate:
        h.require(sys.stdin.isatty() and os.tcgetpgrp(sys.stdin.fileno()) == os.getpgrp(), 'foreground terminal required')
        subprocess.run(['sudo', '-v'], check=True)
    validate_request(built, correctness, output)
    h.fresh(output, [built, correctness, e.PACKAGE, c.DIRECTORY, e.ROOT / 'tests'])
    result = dict(status='blocked', decision='Evidence insufficient', native_correctness='qualified',
        attempted=[], completed=[], unexecuted=[], observations=0, cleanup=True, stage='preparation')
    rows, observations = [], []
    frozen = {}
    try:
        h.write(output / 'request.json', dict(built=str(built), correctness=str(correctness)))
        h.write(output / 'binding.json', binding)
        h.write(output / 'built.json', c.built_binding(built))
        h.write(output / 'protocol.json', t.protocol())
        shutil.copyfile(e.PACKAGE / '3200x2400.png', output / 'fixture.png')
        frozen = tools()
        (output / 'tools').mkdir()
        for path in frozen:
            shutil.copyfile(path, output / 'tools' / t.snapshot_name(path))
        h.write(output / 'tools.json', frozen)
        h.write(output / 'environment.json', dict(host=list(os.uname()), effective=t.environment(),
            affinity=sorted(os.sched_getaffinity(0)), boot_id=Path('/proc/sys/kernel/random/boot_id').read_text()))
        h.write(output / 'artifact-bindings.json', h.sealed(built))
        rows = schedule(built, output)
        h.write(output / 'schedule.json', rows)
        v.verify_schedule(output, built)
        result['unexecuted'] = [r['name'] for r in rows]
        for row in rows:
            h.require(tools() == frozen and h.read(output / 'protocol.json') == t.protocol() and
                      h.digest(output / 'fixture.png') == binding['historical']['diagnostic']['fixture']['sha256'], 'frozen diagnostic input drift')
            result['stage'] = row['name']
            result['attempted'].append(row['name'])
            result['unexecuted'].remove(row['name'])
            if row['workload']:
                owner = h.read(output / (row['arm'] + '-staging.json'))
                h.require(c.tree(stage.runtime_path(output, row['arm'])) == owner['tree'], 'staged runtime drift')
                binary = built / row['arm'] / 'harness-build/preview-benchmark'
                expected = h.read(output / 'artifact-bindings.json')
                h.require(h.digest(binary) == expected[str(binary.relative_to(built))], 'timed binary drift')
            invoke(row, output)
            if row['workload']:
                observation = v.observation(output, row)
                h.write(output / row['name'] / 'observation.json', observation)
                observations.append(observation)
                result['observations'] = len(observations)
                print(str(len(observations)) + '/202 passed', flush=True)
            result['completed'].append(row['name'])
        result.update(status='complete')
    except ERRORS as error:
        result['failure'] = str(error) or type(error).__name__
        if result['attempted']:
            last = result['attempted'][-1]
            path = output / 'commands' / (last + '-result.json')
            if path.is_file() and (not h.read(path)['cleanup'] or last.endswith(('-unstage', '-unstage-authorization'))):
                result['cleanup'] = False
    finally:
        # Only authorized owned cleanup may run after the stopped schedule. Never retry a command.
        for arm in ('control', 'candidate'):
            runtime = stage.runtime_path(output, arm)
            if not os.path.lexists(runtime):
                continue
            try:
                h.require((output / (arm + '-staging.json')).is_file(), 'unverifiable staging retained')
                for name in (arm + '-unstage-authorization', arm + '-unstage'):
                    record = output / 'commands' / (name + '-result.json')
                    if record.exists():
                        prior = h.read(record)
                        h.require(prior['exit'] == 0 and prior['failure'] is None and prior['cleanup'],
                                  'failed cleanup command not retried; staging retained')
                    else:
                        invoke(next(r for r in rows if r['name'] == name), output)
                h.require(not os.path.lexists(runtime), 'staging retained')
            except ERRORS as error:
                result.update(status='blocked', decision='Evidence insufficient', cleanup=False,
                    cleanup_failure=str(error), failure=result.get('failure', str(error)))
        unchanged = False
        try:
            unchanged = bool(frozen) and frozen == tools()
            unchanged = unchanged and h.digest(output / 'fixture.png') == binding['historical']['diagnostic']['fixture']['sha256']
            unchanged = unchanged and h.read(output / 'protocol.json') == t.protocol()
            unchanged = unchanged and v.prerequisite(built, correctness) == binding
        except ERRORS:
            unchanged = False
        if not unchanged:
            result.update(status='blocked', decision='Evidence insufficient', failure=result.get('failure', 'input integrity drift'))
        h.write(output / 'integrity.json', dict(unchanged=unchanged))
        h.write(output / 'observations.json', observations)
        statistics = t.statistics_for(observations, result['status'] == 'complete' and result['cleanup'] and unchanged)
        result['decision'] = statistics['decision']
        h.write(output / 'statistics.json', statistics)
        h.write(output / 'assessment.json', result)
        lines = ['# Directional-variation encoding startup trial', '', 'Decision: ' + result['decision'], '',
                 result.get('failure', ''), '', '| Arm | Endpoint | Median ms | p95 ms |', '|---|---|---:|---:|']
        for arm, endpoints in statistics['populations'].items():
            for endpoint, data in endpoints.items():
                if data:
                    lines.append(f"| {arm} | {endpoint} | {data['median']:.6f} | {data['p95']:.6f} |")
        lines += ['', 'Block differences in statistics.json are candidate minus control and descriptive only.', '',
                  'Historical qualification 78/80 unchanged. No diagnostic-duration subtraction. '
                  'Streaming, validation reuse and SHA dispatch remain Deferred. '
                  'Production changes, full qualification, rollout and deployment require a subsequent plan.', '']
        (output / 'REPORT.md').write_text('\n'.join(lines))
        h.write(output / 'seal.json', h.inventory(output))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--built', type=Path, required=True)
    parser.add_argument('--correctness', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--authenticate', action='store_true')
    args = parser.parse_args()
    try:
        result = execute(args.built.absolute(), args.correctness.absolute(), args.output.absolute(), args.authenticate)
    except ERRORS as error:
        print('No attempt created: ' + (str(error) or type(error).__name__), file=sys.stderr)
        sys.exit(1)
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'complete')
