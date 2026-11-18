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
v = e.load('publication_observation_contract', c.DIRECTORY / 'offline/verify_execution.py')
ERRORS = (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, KeyboardInterrupt, v.struct.error, v.zlib.error)
OUTPUT_NAME = 'preview-cache-publication-execution-20261118-01'


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
    paths = set(Path(path) for path in c.tools())
    paths.update(c.DIRECTORY.glob('EXECUTION*'))
    paths.update((c.DIRECTORY / 'diagnostic-native').glob('*'))
    paths.add(e.ROOT / 'tests/test_preview_cache_publication_diagnostic.py')
    h.require(len({p.name for p in paths}) == len(paths), 'ambiguous tool snapshot basenames')
    return {str(path): h.digest(path) for path in sorted(paths)}


def prepare_sources(output):
    for arm in ('control', 'early'):
        target = output / 'native-source' / arm
        target.mkdir(parents=True)
        source = (e.PACKAGE / arm / 'harness-source/reuse.cpp').read_text()
        for before, after in v.protocol()['harness_insertions']:
            h.require(source.count(before) == 1, 'harness insertion anchor drift')
            source = source.replace(before, after)
        (target / 'main.cpp').write_text(source)
        for name in ('CMakeLists.txt', 'publication_checks.h'):
            shutil.copyfile(c.DIRECTORY / 'diagnostic-native' / name, target / name)
    v.source_contract(output)


def schedule(built, output):
    uid = os.getuid()
    rows = []
    def add(name, argv, arm=None, privileged=False, workload=False, observation=None):
        environment = dict(PATH='/usr/bin:/bin', HOME=pwd.getpwuid(uid).pw_dir, LANG='C.UTF-8',
            QT_QPA_PLATFORM='offscreen', CMAKE_BUILD_PARALLEL_LEVEL='4',
            XDG_RUNTIME_DIR='/run/user/' + str(uid), DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/' + str(uid) + '/bus')
        if workload:
            base = output / name
            environment.update(HOLONIGHT_CACHE_INVOCATION=str(uuid.uuid4()), PUBLICATION_EVIDENCE=str(base),
                HN_SESSION_RUNTIME=str(stage.runtime_path(output, arm)),
                HN_BROWSER_SESSION_RUNTIME=str(stage.runtime_path(output, arm)),
                XDG_CACHE_HOME=str(base / 'cache'), TMPDIR=str(base / 'source'))
        rows.append(dict(index=len(rows), name=name, argv=[str(arg) for arg in argv], arm=arm,
            privileged=privileged, workload=workload, observation=observation, environment=environment,
            uid=0 if privileged else uid, timeout_seconds=30 if workload else 600,
            launch=dict(process_group=0) if privileged else dict(start_new_session=True)))
    add('authorization', ['sudo', '-n', '-v'], privileged=True)
    for arm in ('control', 'early'):
        base = output / arm
        add(arm + '-configure', ['cmake', '-S', output / 'native-source' / arm, '-B', base / 'build',
            '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(built / arm / 'prefix')], arm)
        add(arm + '-compile', ['cmake', '--build', base / 'build', '--parallel', '4'], arm)
        add(arm + '-linkage', ['ldd', base / 'build/publication-observation'], arm)
        add(arm + '-stage-authorization', ['sudo', '-n', '-v'], privileged=True)
        add(arm + '-stage', ['sudo', '-n', sys.executable, c.DIRECTORY / 'execution_stage.py',
            '--output', output, '--arm', arm], arm, privileged=True)
    for observation in v.protocol()['schedule']:
        arm = observation['arm']
        name = 'observation-' + str(observation['index']).zfill(2)
        add(name, [output / arm / 'build/publication-observation', stage.runtime_path(output, arm),
            output / 'fixture.png', 'startup', '1', output / name / 'harness.json'], arm,
            workload=True, observation=observation)
    for arm in ('control', 'early'):
        add(arm + '-unstage-authorization', ['sudo', '-n', '-v'], privileged=True)
        add(arm + '-unstage', ['sudo', '-n', sys.executable, c.DIRECTORY / 'execution_stage.py',
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
            record['exit'] = process.wait(timeout=row['timeout_seconds'])
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
    frozen, native = {}, {}
    try:
        h.write(output / 'request.json', dict(built=str(built), correctness=str(correctness)))
        h.write(output / 'binding.json', binding)
        shutil.copyfile(c.DIRECTORY / 'EXECUTION-v1.json', output / 'protocol.json')
        shutil.copyfile(e.PACKAGE / '3200x2400.png', output / 'fixture.png')
        frozen = tools()
        (output / 'tools').mkdir()
        for path in frozen:
            shutil.copyfile(path, output / 'tools' / Path(path).name)
        h.write(output / 'tools.json', frozen)
        prepare_sources(output)
        native = h.inventory(output / 'native-source')
        rows = schedule(built, output)
        h.write(output / 'schedule.json', rows)
        v.verify_schedule(output, built)
        result['unexecuted'] = [r['name'] for r in rows]
        for row in rows:
            h.require(tools() == frozen and h.inventory(output / 'native-source') == native and
                      h.digest(output / 'protocol.json') == v.PROTOCOL_SHA256 and
                      h.digest(output / 'fixture.png') == v.protocol()['fixture_sha256'], 'frozen diagnostic input drift')
            result['stage'] = row['name']
            result['attempted'].append(row['name'])
            result['unexecuted'].remove(row['name'])
            invoke(row, output)
            if row['name'].endswith('-configure'):
                h.write(output / (row['arm'] + '-resolution.json'), v.resolution(output, built, row['arm']))
            if row['name'].endswith('-linkage'):
                h.write(output / (row['arm'] + '-linkage.json'), v.linkage((output / 'commands' / (row['name'] + '.stdout')).read_text()))
            if row['workload']:
                observation = v.observation(output, row)
                h.write(output / row['name'] / 'observation.json', observation)
                observations.append(observation)
                result['observations'] = len(observations)
            result['completed'].append(row['name'])
        result.update(status='complete', decision='overlap observed' if any(o['supports'] for o in observations
            if not o['schedule']['warmup'] and o['schedule']['arm'] == 'early') else 'overlap not observed in this population')
    except ERRORS as error:
        result['failure'] = str(error) or type(error).__name__
        if result['attempted']:
            last = result['attempted'][-1]
            path = output / 'commands' / (last + '-result.json')
            if path.is_file() and (not h.read(path)['cleanup'] or last.endswith(('-unstage', '-unstage-authorization'))):
                result['cleanup'] = False
    finally:
        # Only authorized owned cleanup may run after the stopped schedule. Never retry a command.
        for arm in ('control', 'early'):
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
            unchanged = bool(frozen) and frozen == tools() and h.inventory(output / 'native-source') == native
            unchanged = unchanged and h.digest(output / 'fixture.png') == v.protocol()['fixture_sha256']
            unchanged = unchanged and h.digest(output / 'protocol.json') == v.PROTOCOL_SHA256
            unchanged = unchanged and v.prerequisite(built, correctness) == binding
        except ERRORS:
            unchanged = False
        if not unchanged:
            result.update(status='blocked', decision='Evidence insufficient', failure=result.get('failure', 'input integrity drift'))
        h.write(output / 'integrity.json', dict(unchanged=unchanged))
        h.write(output / 'observations.json', observations)
        h.write(output / 'assessment.json', result)
        (output / 'REPORT.md').write_text('# Cache publication diagnostic\n\n' + result['status'] + ': ' + result['decision'] +
            '\n\n' + result.get('failure', '') + '\n\nNo performance or visible-rendering claim. Candidate selection Evidence insufficient; '
            'streaming and validation reuse Deferred; historical qualification 78/80 unchanged.\n')
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
