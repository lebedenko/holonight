#!/usr/bin/env python3
"""One frozen correctness-only attempt against the retained Release providers."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

sys.dont_write_bytecode = True
import correctness as c
import stage

h, e = c.h, c.e
ERRORS = (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, KeyboardInterrupt)


def schedule(built, output):
    p = c.protocol()
    rows = []
    def add(name, argv, arm=None, cases=None, privileged=False, workload=False, runtime=None):
        environment = dict(QT_QPA_PLATFORM='offscreen', CMAKE_BUILD_PARALLEL_LEVEL='4',
            XDG_RUNTIME_DIR='/run/user/' + str(os.getuid()),
            DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/' + str(os.getuid()) + '/bus')
        if arm:
            base = output / arm
            environment.update(HOLONIGHT_CACHE_INVOCATION=str(uuid.uuid4()), PUBLICATION_ARM=arm,
                PUBLICATION_RUNTIME=str(runtime or built / arm / 'runtime'),
                HN_SESSION_RUNTIME=str(stage.runtime_path(output, arm)),
                HN_BROWSER_SESSION_RUNTIME=str(stage.runtime_path(output, arm)),
                XDG_CACHE_HOME=str(base / 'private' / name / 'cache'),
                TMPDIR=str(base / 'private' / name / 'source'))
        argv = [str(v) for v in argv]
        if privileged and cases:
            argv = ['sudo', '-n', '/usr/bin/env', *[k + '=' + v for k, v in sorted(environment.items())], *argv]
        rows.append(dict(index=len(rows), name=name, arm=arm, argv=argv, environment=environment,
            cases=cases or [], privileged=privileged, workload=workload, uid=0 if privileged else os.getuid()))
    add('fixtures', [sys.executable, output / 'format-fixtures.py', output / 'fixtures'])
    add('compiler', ['c++', '--version'])
    add('cmake', ['cmake', '--version'])
    add('dependencies', ['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp'])
    for arm in p['arms']:
        base = output / arm
        prefix = built / arm / 'prefix'
        add(arm + '-configure', ['cmake', '-S', output / 'native-source', '-B', base / 'build', '-G', 'Ninja',
            '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(prefix),
            '-DFROZEN=' + str(e.PACKAGE / arm / 'source'), '-DRUNTIME=' + str(built / arm / 'runtime'),
            '-DFIXTURES=' + str(output / 'fixtures')], arm)
        add(arm + '-compile', ['cmake', '--build', base / 'build', '--parallel', '4'], arm)
        for binary in ('publication-correctness', 'session-correctness', 'images-consumer', 'preview-consumer'):
            add(arm + '-' + binary + '-linkage', ['ldd', base / 'build' / binary], arm)
        groups = [(group['label'], group['cases']) for group in p['prerequisites']]
        for label, cases in groups + [('mutable-publication', p['publication'])]:
            add(arm + '-' + label, [base / 'build/publication-correctness', '--gtest_filter=' + ':'.join(cases),
                '--gtest_fail_fast', '--gtest_output=xml:' + str(base / (label + '.xml'))], arm, cases, workload=True)
        for binary in ('images-consumer', 'preview-consumer'):
            add(arm + '-mutable-' + binary, [base / 'build' / binary], arm, workload=True)
        add(arm + '-stage', ['sudo', '-n', sys.executable, c.DIRECTORY / 'stage.py', '--output', output,
            '--arm', arm], arm, privileged=True)
        for label, binary, cases, privileged in (
            ('protected-fixture', 'publication-correctness', p['protected_fixture'], True),
            ('protected-publication', 'publication-correctness', p['publication'], False),
            ('protected-preview', 'publication-correctness', p['protected_preview'], False),
            ('session', 'session-correctness', p['session'], False)):
            add(arm + '-' + label, [base / 'build' / binary, '--gtest_filter=' + ':'.join(cases),
                '--gtest_fail_fast', '--gtest_output=xml:' + str(base / (label + '.xml'))], arm, cases,
                privileged, workload=not privileged, runtime=stage.runtime_path(output, arm))
        add(arm + '-protected-consumer', [base / 'build/preview-consumer'], arm,
            workload=True, runtime=stage.runtime_path(output, arm))
        add(arm + '-unstage', ['sudo', '-n', sys.executable, c.DIRECTORY / 'stage.py', '--output', output,
            '--arm', arm, '--remove'], arm, privileged=True)
    return rows


def scopes(env, deadline):
    """Same scope identity query as the existing startup-smoke supervision gate."""
    uid = os.getuid()
    argv = ['systemctl', '--user', 'list-units', '--all', '--plain', '--no-legend',
            '--no-pager', 'holonight-images-*.scope']
    value = subprocess.run(argv, env=env, capture_output=True, text=True,
        timeout=max(.001, deadline - time.monotonic()))
    group = Path(f'/sys/fs/cgroup/user.slice/user-{uid}.slice/user@{uid}.service')
    paths = sorted(str(p) for p in group.glob('**/holonight-images-*.scope'))
    return dict(argv=argv, exit=value.returncode, stdout=value.stdout, stderr=value.stderr,
        cgroups=paths, isolated=value.returncode == 0 and not value.stdout.strip() and not paths and group.is_dir())


def invoke(row, output):
    h.require(os.getuid() != 0, 'qualifier and model workloads must run as desktop user')
    env = dict(os.environ, **row['environment'])
    target = output / 'commands'
    target.mkdir(exist_ok=True)
    h.write(target / (row['name'] + '-command.json'), row)
    record = dict(start_ns=time.monotonic_ns(), exit=None, failure=None, cleanup=False)
    process = None
    try:
        for key in ('XDG_CACHE_HOME', 'TMPDIR'):
            if key in row['environment']:
                Path(env[key]).mkdir(parents=True, mode=0o700, exist_ok=True)
        if row['workload']:
            before = scopes(env, time.monotonic() + 5)
            h.write(target / (row['name'] + '-scopes-before.json'), before)
            h.require(before['isolated'], 'preexisting helper scopes or supervision unavailable')
        with (target / (row['name'] + '.stdout')).open('x') as stdout, (target / (row['name'] + '.stderr')).open('x') as stderr:
            process = subprocess.Popen(row['argv'], cwd=e.ROOT, env=env, stdout=stdout, stderr=stderr,
                start_new_session=True)
            record['pid'] = process.pid
            record['exit'] = process.wait(timeout=600)
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
                # Existing group termination/reaping primitive shares this deadline with scope proof.
                primitive = e.load('publication_process_cleanup', e.ROOT / 'scripts/run-preview-cpu-profile.py')
                primitive.terminate(process, deadline=deadline)
                try:
                    os.killpg(process.pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    raise ValueError('process group survived cleanup')
            if row['workload']:
                after = scopes(env, deadline)
                h.write(target / (row['name'] + '-scopes-after.json'), after)
                h.require(after['isolated'], 'helper scope cleanup unverified')
            record['cleanup_seconds'] = time.monotonic() - start
            h.require(time.monotonic() <= deadline, 'shared cleanup budget exceeded')
            record['cleanup'] = True
        except ERRORS as error:
            record['cleanup_failure'] = str(error) or type(error).__name__
            record['failure'] = record['failure'] or record['cleanup_failure']
        record['stop_ns'] = time.monotonic_ns()
        h.write(target / (row['name'] + '-result.json'), record)
    h.require(record['failure'] is None and record['cleanup'], record['failure'] or 'cleanup failed')


def case_accounting(rows, output):
    import xml.etree.ElementTree as ET
    records = []
    for row in rows:
        if not row['cases']:
            continue
        path = Path(next(v.split('xml:', 1)[1] for v in row['argv'] if v.startswith('--gtest_output=xml:')))
        observed = []
        failure = None
        if path.exists():
            try:
                observed = [dict(name=case.attrib['classname'] + '.' + case.attrib['name'],
                    status=case.attrib.get('status'), result=case.attrib.get('result'),
                    failed=case.find('failure') is not None, skipped=case.find('skipped') is not None)
                    for case in ET.parse(path).getroot().findall('.//testcase')]
            except (OSError, KeyError, ET.ParseError) as error:
                failure = str(error)
        attempted = [c['name'] for c in observed if c['status'] == 'run' and not c['skipped']]
        records.append(dict(invocation=row['name'], required=row['cases'], observed=observed,
            attempted=attempted, skipped=[c['name'] for c in observed if c['skipped']],
            unexecuted=[name for name in row['cases'] if name not in attempted],
            parse_failure=failure))
    return records


def qualify(built, output):
    h.fresh(output, [built, e.PACKAGE, c.DIRECTORY, e.ROOT / 'tests'])
    result = dict(status='blocked', phase='correctness-v3', decision='Evidence insufficient',
        attempted=[], completed=[], unexecuted=[], native_correctness='unvalidated',
        observations=0, staging='not attempted', cleanup=True, stage='preparation')
    tools = {}
    rows = []
    native = binding = None
    h.write(output / 'request.json', dict(built=str(built)))
    try:
        h.require(output.name == 'preview-cache-publication-correctness-20261118-02', 'fresh approved attempt name required')
        h.require(os.getuid() != 0, 'desktop user required')
        shutil.copytree(c.DIRECTORY / 'native', output / 'native-source')
        native = h.inventory(output / 'native-source')
        h.write(output / 'native-inputs.json', native)
        tools = c.tools()
        (output / 'tools').mkdir()
        for path in tools:
            shutil.copyfile(path, output / 'tools' / Path(path).name)
        h.write(output / 'tools.json', tools)
        shutil.copyfile(c.DIRECTORY / 'CORRECTNESS-v3.json', output / 'protocol-v3.json')
        verifier = e.load('protocol_v3_pin', c.DIRECTORY / 'offline/verify_correctness_v3.py')
        h.require(h.digest(output / 'protocol-v3.json') == verifier.PROTOCOL_SHA256, 'correctness protocol drift')
        shutil.copyfile(c.generator(), output / 'format-fixtures.py')
        generator_digest = h.digest(output / 'format-fixtures.py')
        rows = schedule(built, output)
        h.write(output / 'schedule.json', rows)
        result['unexecuted'] = [r['name'] for r in rows]
        binding = c.built_binding(built)
        h.write(output / 'built.json', binding)
        h.write(output / 'package.json', e.package())
        c.validate_membership(c.DIRECTORY / 'native')
        for row in rows:
            h.require(c.tools() == tools and h.inventory(output / 'native-source') == native, 'frozen source/tool drift')
            h.require(h.digest(output / 'protocol-v3.json') == verifier.PROTOCOL_SHA256 and
                      h.digest(output / 'format-fixtures.py') == generator_digest == h.digest(c.generator()), 'frozen preparation drift')
            if (output / 'fixtures.json').exists():
                h.require(c.fixtures(output / 'fixtures') == h.read(output / 'fixtures.json'), 'fixture drift')
            result['stage'] = row['name']
            result['attempted'].append(row['name'])
            result['unexecuted'].remove(row['name'])
            invoke(row, output)
            if row['name'] == 'fixtures':
                h.write(output / 'fixtures.json', h.inventory(output / 'fixtures'))
                c.fixtures(output / 'fixtures')
            if row['cases']:
                xmlarg = next(v for v in row['argv'] if v.startswith('--gtest_output=xml:'))
                c.validate_xml(Path(xmlarg.split('xml:', 1)[1]), row['cases'])
            if row['name'].endswith('-linkage'):
                linkage = (output / 'commands' / (row['name'] + '.stdout')).read_text()
                h.require('not found' not in linkage, 'unresolved linkage')
                identities = {}
                for line in linkage.splitlines():
                    tokens = line.split()
                    path = tokens[2] if len(tokens) > 2 and tokens[1] == '=>' else tokens[0] if tokens else ''
                    if path.startswith('/'):
                        resolved = Path(path).resolve()
                        identities[str(resolved)] = h.digest(resolved)
                h.require(identities, 'missing linked dependency identities')
                h.write(output / (row['name'] + '-identities.json'), identities)
            if row['name'].endswith('-configure'):
                cache = (output / row['arm'] / 'build/CMakeCache.txt').read_text()
                resolution = {line.split(':', 1)[0]: line.split('=', 1)[1] for line in cache.splitlines()
                    if line.startswith(('HolonightImages_DIR:', 'HolonightThumbnails_DIR:', 'HolonightFileBrowser_DIR:'))}
                h.require(len(resolution) == 3 and all(Path(v).resolve().is_relative_to(built / row['arm'] / 'prefix')
                          for v in resolution.values()), 'installed package resolution mismatch')
                h.write(output / row['arm'] / 'package-resolution.json', resolution)
            result['completed'].append(row['name'])
        h.require(c.built_binding(built) == binding, 'provider drift')
        result.update(status='qualified', native_correctness='qualified')
    except ERRORS as error:
        result['failure'] = str(error) or type(error).__name__
        if result['attempted']:
            command_result = output / 'commands' / (result['attempted'][-1] + '-result.json')
            if command_result.exists() and (not h.read(command_result)['cleanup'] or
                    result['attempted'][-1].endswith('-unstage')):
                result['cleanup'] = False
    finally:
        # Cleanup is the only permitted work after a failed invocation. Never resume tests.
        for arm in ('control', 'early'):
            runtime = stage.runtime_path(output, arm)
            if os.path.lexists(runtime):
                result['staging'] = 'attempted'
                try:
                    h.require((output / (arm + '-staging.json')).exists(), 'unverifiable staging retained')
                    row = next(r for r in rows if r['name'] == arm + '-unstage')
                    if row['name'] not in result['attempted']:
                        invoke(row, output)
                    h.require(not os.path.lexists(runtime), 'staging retained')
                except ERRORS as error:
                    result.update(status='blocked', cleanup=False, cleanup_failure=str(error))
        if (output / 'fixtures').is_dir() and not (output / 'fixtures.json').exists():
            try:
                h.write(output / 'fixtures.json', h.inventory(output / 'fixtures'))
            except ERRORS as error:
                result['fixture_inventory_failure'] = str(error)
        unchanged = False
        try:
            unchanged = bool(tools) and c.tools() == tools
            unchanged = unchanged and h.inventory(output / 'native-source') == native and c.built_binding(built) == binding
            unchanged = unchanged and h.digest(output / 'protocol-v3.json') == verifier.PROTOCOL_SHA256 and \
                h.digest(output / 'format-fixtures.py') == generator_digest == h.digest(c.generator())
            if (output / 'fixtures.json').exists():
                unchanged = unchanged and h.inventory(output / 'fixtures') == h.read(output / 'fixtures.json')
        except ERRORS:
            unchanged = False
        if not unchanged:
            result.update(status='blocked', failure=result.get('failure', 'tool drift'))
        h.write(output / 'integrity.json', dict(unchanged=unchanged))
        h.write(output / 'case-accounting.json', case_accounting(rows, output))
        h.write(output / 'assessment.json', result)
        (output / 'REPORT.md').write_text('# Correctness protocol v3\n\n' + result['status'] + ': ' +
            result.get('failure', '') + '\n\nOverlap: Evidence insufficient. No warm-ups or diagnostic observations.\n'
            'Streaming and validation reuse Deferred; candidate selection Evidence insufficient; '
            'historical qualification 78/80 unchanged. Uncaptured historical loading identities remain unavailable.\n')
        h.write(output / 'seal.json', h.inventory(output))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--built', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = qualify(args.built.absolute(), args.output.absolute())
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'qualified')
