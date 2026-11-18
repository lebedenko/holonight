#!/usr/bin/env python3
"""Independent offline correctness-v4 verifier; imports no execution implementation."""
import argparse
import os
from pathlib import Path
import sys
import uuid
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evidence as e
h = e.h
PROTOCOL_SHA256 = '70ef538f90f8654f321d699108925626ad2346ec8626a7f3d8e7438b47ddafd3'
BUILT_SEAL = 'd2e45f0c05b464e1c22de87145f35160ac038ff482a0cc72ca04d6f1396b2d7a'
DIRECTORY = Path(__file__).resolve().parents[1]


def xml_cases(path, required):
    xml = ET.parse(path).getroot()
    cases = xml.findall('.//testcase')
    names = [case.attrib['classname'] + '.' + case.attrib['name'] for case in cases]
    h.require(len(names) == len(set(names)) == len(required) == int(xml.attrib['tests']) and
              set(names) == set(required), 'required test membership mismatch')
    h.require(all('DISABLED_' not in name for name in names) and
              all(int(xml.attrib.get(key, '0')) == 0 for key in ('failures', 'disabled', 'errors')) and
              not xml.findall('.//skipped') and not xml.findall('.//failure') and
              all(case.attrib.get('status') == 'run' and case.attrib.get('result') == 'completed' for case in cases),
              'required tests failed or skipped')
    return names


def expected_schedule(root, built, p):
    """Reconstruct every command and case independently of the qualifier."""
    import hashlib
    rows = []
    def add(name, argv, arm=None, cases=None, privileged=False, workload=False, runtime=None):
        if privileged and argv != ['sudo', '-n', '-v']:
            add(name + '-authorization', ['sudo', '-n', '-v'], privileged=True)
        rows.append(dict(name=name, argv=[str(x) for x in argv], arm=arm, cases=cases or [],
            privileged=privileged, workload=workload, runtime=runtime))
    add('authorization', ['sudo', '-n', '-v'], privileged=True)
    add('fixtures', [sys.executable, root / 'format-fixtures.py', root / 'fixtures'])
    add('compiler', ['c++', '--version'])
    add('cmake', ['cmake', '--version'])
    add('dependencies', ['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp'])
    for arm in ('control', 'early'):
        base = root / arm
        protected = Path('/run') / ('holonight-publication-' + hashlib.sha256(str(root).encode()).hexdigest()[:20] + '-' + arm)
        add(arm + '-configure', ['cmake', '-S', root / 'native-source', '-B', base / 'build', '-G', 'Ninja',
            '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(built / arm / 'prefix'),
            '-DFROZEN=' + str(e.PACKAGE / arm / 'source'), '-DRUNTIME=' + str(built / arm / 'runtime'),
            '-DFIXTURES=' + str(root / 'fixtures')], arm)
        add(arm + '-compile', ['cmake', '--build', base / 'build', '--parallel', '4'], arm)
        for binary in ('publication-correctness', 'session-correctness', 'images-consumer', 'preview-consumer'):
            add(arm + '-' + binary + '-linkage', ['ldd', base / 'build' / binary], arm)
        groups = [(group['label'], group['cases']) for group in p['prerequisites']]
        for label, cases in groups + [('mutable-publication', p['publication'])]:
            add(arm + '-' + label, [base / 'build/publication-correctness', '--gtest_filter=' + ':'.join(cases),
                '--gtest_fail_fast', '--gtest_output=xml:' + str(base / (label + '.xml'))], arm, cases, workload=True)
        for binary in ('images-consumer', 'preview-consumer'):
            add(arm + '-mutable-' + binary, [base / 'build' / binary], arm, workload=True)
        add(arm + '-stage', ['sudo', '-n', sys.executable, DIRECTORY / 'stage.py', '--output', root,
            '--arm', arm], arm, privileged=True)
        for label, binary, cases, privileged in (
            ('protected-fixture', 'publication-correctness', p['protected_fixture'], True),
            ('protected-publication', 'publication-correctness', p['publication'], False),
            ('protected-preview', 'publication-correctness', p['protected_preview'], False),
            ('session', 'session-correctness', p['session'], False)):
            add(arm + '-' + label, [base / 'build' / binary, '--gtest_filter=' + ':'.join(cases),
                '--gtest_fail_fast', '--gtest_output=xml:' + str(base / (label + '.xml'))], arm, cases,
                privileged, workload=not privileged, runtime=str(protected))
        add(arm + '-protected-consumer', [base / 'build/preview-consumer'], arm, workload=True, runtime=str(protected))
        add(arm + '-unstage', ['sudo', '-n', sys.executable, DIRECTORY / 'stage.py', '--output', root,
            '--arm', arm, '--remove'], arm, privileged=True)
    return rows


def verify_schedule(root, built, p):
    rows = h.read(root / 'schedule.json')
    expected = expected_schedule(root, built, p)
    h.require(len(rows) == len(expected), 'schedule membership')
    invocations = set()
    desktop_uid = next((row['uid'] for row in rows if not row['privileged']), None)
    h.require(type(desktop_uid) is int and desktop_uid > 0, 'desktop privilege boundary')
    for index, (row, wanted) in enumerate(zip(rows, expected)):
        for key in ('name', 'arm', 'cases', 'privileged', 'workload'):
            h.require(row[key] == wanted[key], 'schedule role/case mismatch')
        h.require(row['index'] == index, 'schedule index mismatch')
        if not row['privileged']:
            desktop_uid = row['uid'] if desktop_uid is None else desktop_uid
            h.require(row['uid'] == desktop_uid and desktop_uid != 0, 'desktop privilege boundary')
        else:
            h.require(row['uid'] == 0 and (row['cases'] == p['protected_fixture'] or
                      row['name'].endswith(('-stage', '-unstage')) or row['argv'] == ['sudo', '-n', '-v']), 'privileged model workload')
        h.require(row['launch'] == (dict(process_group=0) if row['privileged'] else
                  dict(start_new_session=True)), 'launch policy mismatch')
        env = row['environment']
        expected_env = dict(QT_QPA_PLATFORM='offscreen', CMAKE_BUILD_PARALLEL_LEVEL='4',
            XDG_RUNTIME_DIR='/run/user/' + str(desktop_uid),
            DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/' + str(desktop_uid) + '/bus')
        if row['arm']:
            invocation = env['HOLONIGHT_CACHE_INVOCATION']
            h.require(str(uuid.UUID(invocation)) == invocation and invocation not in invocations, 'invocation identity reused')
            invocations.add(invocation)
            arm, name = row['arm'], row['name']
            import hashlib
            protected = Path('/run') / ('holonight-publication-' + hashlib.sha256(str(root).encode()).hexdigest()[:20] + '-' + arm)
            expected_env.update(HOLONIGHT_CACHE_INVOCATION=invocation, PUBLICATION_ARM=arm,
                PUBLICATION_RUNTIME=wanted['runtime'] or str(built / arm / 'runtime'),
                HN_SESSION_RUNTIME=str(protected), HN_BROWSER_SESSION_RUNTIME=str(protected),
                XDG_CACHE_HOME=str(root / arm / 'private' / name / 'cache'),
                TMPDIR=str(root / arm / 'private' / name / 'source'))
        h.require(env == expected_env, 'environment propagation mismatch')
        argv = wanted['argv']
        if row['privileged'] and row['cases']:
            argv = ['sudo', '-n', '/usr/bin/env', *[k + '=' + v for k, v in sorted(env.items())], *argv]
        h.require(row['argv'] == argv, 'independent command reconstruction mismatch')
    return rows


def protected_path(root, arm):
    import hashlib
    return Path('/run') / ('holonight-publication-' + hashlib.sha256(str(root).encode()).hexdigest()[:20] + '-' + arm)


def fixture_contract(root, p):
    directory = root / 'fixtures'
    h.require(directory.is_dir() and not directory.is_symlink() and
              all(path.is_file() and not path.is_symlink() for path in directory.rglob('*')), 'unsafe fixture member')
    inventory = h.inventory(directory)
    h.require(inventory == p['fixtures'], 'fixture drift')
    h.require(inventory == h.read(root / 'fixtures.json'), 'fixture inventory mismatch')


def linkage_contract(path):
    text = path.read_text()
    h.require('not found' not in text, 'unresolved linked dependency')
    identities = {}
    for line in text.splitlines():
        tokens = line.split()
        value = tokens[2] if len(tokens) > 2 and tokens[1] == '=>' else tokens[0] if tokens else ''
        if value.startswith('/'):
            resolved = Path(value).resolve()
            identities[str(resolved)] = h.digest(resolved)
    h.require(identities, 'missing linked dependency identities')
    return identities


def resolution_contract(root, built, arm):
    cache = (root / arm / 'build/CMakeCache.txt').read_text()
    values = {line.split(':', 1)[0]: line.split('=', 1)[1] for line in cache.splitlines()
              if line.startswith(('HolonightImages_DIR:', 'HolonightThumbnails_DIR:', 'HolonightFileBrowser_DIR:'))}
    h.require(set(values) == {'HolonightImages_DIR', 'HolonightThumbnails_DIR', 'HolonightFileBrowser_DIR'} and
              all(Path(value).resolve().is_relative_to(built / arm / 'prefix') for value in values.values()),
              'installed consumer resolution mismatch')
    return values


def verify(root):
    inventory = h.sealed(root)
    assessment = h.read(root / 'assessment.json')
    h.require(assessment['phase'] == 'correctness-v4' and assessment['status'] in ('blocked', 'qualified') and
              assessment['decision'] == 'Evidence insufficient' and assessment['observations'] == 0,
              'unsupported correctness outcome')
    h.require(h.digest(root / 'protocol-v4.json') == PROTOCOL_SHA256, 'correctness protocol drift')
    p = h.read(root / 'protocol-v4.json')
    built = Path(h.read(root / 'request.json')['built'])
    preparation_failure = None
    try:
        h.require(built == built.resolve() and h.digest(built / 'seal.json') == BUILT_SEAL,
                  'pinned provider build mismatch')
        provider_inventory = h.sealed(built)
        historical = e.load('independent_native_build_verifier', Path(__file__).with_name('verify.py'))
        record = historical.verify(built)
        h.require(record['commands'] == 27 and record['failed_command'] is None, 'provider build prerequisite')
        package = e.package()
        h.require(package == h.read(built / 'package.json'), 'provider preparation binding')
        import stat
        for arm in ('control', 'early'):
            runtime = built / arm / 'runtime'
            for row in h.read(runtime / 'manifest.json')['files']:
                path = runtime / row['path']
                h.require(path.resolve().is_relative_to(runtime) and path.is_file() and
                          h.digest(path) == row['sha256'] and path.stat().st_size == row['size'] and
                          stat.S_IMODE(path.stat().st_mode) == row['mode'], 'runtime manifest payload mismatch')
            h.require(h.digest(runtime / 'usr/libexec/holonight-images-helper') ==
                      h.digest(built / arm / 'build/holonight-images/holonight-images-helper'), 'runtime helper mismatch')
    except (OSError, ValueError, KeyError, TypeError) as error:
        preparation_failure = str(error) or type(error).__name__
    if preparation_failure is None:
        binding = h.read(root / 'built.json')
        h.require(binding == dict(path=str(built), seal=BUILT_SEAL, inventory=provider_inventory),
                  'provider payload/inventory drift')
        h.require(h.read(root / 'package.json') == package, 'provider preparation binding')
    else:
        h.require(assessment['status'] == 'blocked' and assessment['stage'] == 'preparation' and
                  not assessment['attempted'] and not assessment['completed'] and assessment.get('failure'),
                  'unreported provider preparation failure')
    tools = h.read(root / 'tools.json')
    required_tools = {'qualify.py', 'correctness.py', 'stage.py', 'CORRECTNESS-v2.json', 'CORRECTNESS-v2.md',
        'CORRECTNESS-v4.json', 'CORRECTNESS-v4.md', 'verify_correctness_v4.py',
        'verify_correctness_v2.py', 'test_preview_cache_publication_correctness.py', 'manage-images-generations.py',
        'install_state.py', 'run-preview-cpu-profile.py', 'run-preview-startup-smoke.py', 'evidence.py', 'run.py'}
    h.require(required_tools <= {Path(path).name for path in tools}, 'missing tool snapshot')
    for path, digest in tools.items():
        h.require(h.digest(root / 'tools' / Path(path).name) == digest == h.digest(Path(path)),
                  'tool snapshot/input drift')
    native = h.read(root / 'native-inputs.json')
    h.require(native == h.inventory(root / 'native-source') == h.inventory(DIRECTORY / 'native'),
              'native snapshot drift')
    h.require(h.read(root / 'integrity.json') == dict(unchanged=preparation_failure is None), 'input integrity failure')
    generator = e.PACKAGE / 'control/source/holonight-images/tests/format-fixtures.py'
    h.require(h.digest(root / 'format-fixtures.py') == p['fixture_generator_sha256'], 'fixture generator protocol mismatch')
    h.require((root / 'format-fixtures.py').read_bytes() == generator.read_bytes() ==
              (e.PACKAGE / 'early/source/holonight-images/tests/format-fixtures.py').read_bytes(), 'fixture generator drift')
    rows = verify_schedule(root, built, p)
    names = [r['name'] for r in rows]
    attempted = assessment['attempted']
    completed = assessment['completed']
    h.require(attempted == names[:len(attempted)] and (attempted or preparation_failure) and
              assessment['unexecuted'] == names[len(attempted):] and
              completed == attempted[:len(completed)] and len(attempted) - len(completed) in (0, 1),
              'stopped schedule accounting')
    actual = {n.removeprefix('commands/').removesuffix('-command.json') for n in inventory
              if n.startswith('commands/') and n.endswith('-command.json')}
    cleanup_commands = actual - set(attempted)
    h.require(cleanup_commands <= {'control-unstage', 'early-unstage', 'control-unstage-authorization', 'early-unstage-authorization'}, 'execution after stopped schedule')
    h.require(actual == set(attempted) | cleanup_commands, 'missing/unexpected command artifacts')
    for row in rows:
        if row['name'] in actual and row['privileged'] and row['argv'] != ['sudo', '-n', '-v']:
            check = h.read(root / 'commands' / (row['name'] + '-authorization-result.json'))
            h.require(check['exit'] == 0 and check['failure'] is None and check['cleanup'],
                      'protected operation without authorization')
    for name in cleanup_commands:
        arm = name.split('-', 1)[0]
        h.require((root / (arm + '-staging.json')).exists(), 'cleanup without ownership record')
    previous = 0
    failed = []
    required_count = 0
    cleanup_failed = []
    for row in rows:
        name = row['name']
        if name not in actual:
            continue
        base = root / 'commands' / name
        h.require(h.read(Path(str(base) + '-command.json')) == row, 'executed command differs from frozen schedule')
        result = h.read(Path(str(base) + '-result.json'))
        h.require(type(result['start_ns']) is int and type(result['stop_ns']) is int and
                  previous <= result['start_ns'] <= result['stop_ns'], 'invocation chronology')
        previous = result['stop_ns']
        for suffix in ('.stdout', '.stderr'):
            h.require('commands/' + name + suffix in inventory, 'missing raw process output')
        successful = result['exit'] == 0 and result['failure'] is None and result['cleanup']
        if not result['cleanup'] or (name.endswith(('-unstage', '-unstage-authorization')) and not successful):
            cleanup_failed.append(name)
        if result['cleanup']:
            h.require(0 <= result['cleanup_seconds'] <= 5, 'cleanup deadline exceeded')
        if row['workload']:
            for phase in ('before', 'after'):
                path = Path(str(base) + '-scopes-' + phase + '.json')
                if successful:
                    value = h.read(path)
                    h.require(value['isolated'] and value['exit'] == 0 and not value['stdout'].strip() and
                              not value['cgroups'], 'scope cleanup proof missing')
        if name in completed:
            if name == 'fixtures':
                fixture_contract(root, p)
            h.require(successful, 'completed failed process')
            if row['cases']:
                xml = next(v.split('xml:', 1)[1] for v in row['argv'] if v.startswith('--gtest_output=xml:'))
                required_count += len(xml_cases(Path(xml), row['cases']))
                stdout = Path(str(base) + '.stdout').read_text()
                h.require('[  PASSED  ] ' + str(len(row['cases'])) + ' test' in stdout, 'raw test success mismatch')
            if name.endswith('-linkage'):
                identities = linkage_contract(Path(str(base) + '.stdout'))
                h.require(h.read(root / (name + '-identities.json')) == identities,
                          'current dependency identity mismatch')
            if name.endswith('-configure'):
                resolution = resolution_contract(root, built, row['arm'])
                h.require(h.read(root / row['arm'] / 'package-resolution.json') == resolution,
                          'installed consumer resolution mismatch')
        elif name in attempted:
            # A process may succeed but fail XML, linkage or source-identity validation.
            failure = result['failure']
            if successful:
                try:
                    if name == 'fixtures':
                        fixture_contract(root, p)
                    elif row['cases']:
                        xml = next(v.split('xml:', 1)[1] for v in row['argv'] if v.startswith('--gtest_output=xml:'))
                        xml_cases(Path(xml), row['cases'])
                    elif name.endswith('-linkage'):
                        linkage_contract(Path(str(base) + '.stdout'))
                    elif name.endswith('-configure'):
                        resolution_contract(root, built, row['arm'])
                except (OSError, ValueError, KeyError, ET.ParseError) as error:
                    failure = str(error)
            h.require(bool(failure) or not successful, 'blocked without independently corroborated failure')
            failed.append(name)
    h.require(failed == attempted[len(completed):], 'failure schedule mismatch')
    expected_accounting = []
    for row in rows:
        if not row['cases']:
            continue
        xmlpath = Path(next(arg.split('xml:', 1)[1] for arg in row['argv'] if arg.startswith('--gtest_output=xml:')))
        observed = []
        parse_failure = None
        if xmlpath.exists():
            try:
                observed = [dict(name=case.attrib['classname'] + '.' + case.attrib['name'],
                    status=case.attrib.get('status'), result=case.attrib.get('result'),
                    failed=case.find('failure') is not None, skipped=case.find('skipped') is not None)
                    for case in ET.parse(xmlpath).getroot().findall('.//testcase')]
            except (OSError, KeyError, ET.ParseError) as error:
                parse_failure = str(error)
        attempted_cases = [case['name'] for case in observed if case['status'] == 'run' and not case['skipped']]
        expected_accounting.append(dict(invocation=row['name'], required=row['cases'], observed=observed,
            attempted=attempted_cases, skipped=[case['name'] for case in observed if case['skipped']],
            unexecuted=[name for name in row['cases'] if name not in attempted_cases],
            parse_failure=parse_failure))
    h.require(h.read(root / 'case-accounting.json') == expected_accounting, 'stopped case accounting mismatch')

    for arm in ('control', 'early'):
        staged = root / (arm + '-staging.json')
        if arm + '-stage' in completed:
            h.require(staged.exists(), 'missing staging record')
        if staged.exists():
            row = h.read(staged)
            h.require(arm + '-stage' in actual and row['runtime'] == str(protected_path(root, arm)) and
                      row['owner'] == dict(output=str(root), arm=arm, built=str(built), seal=BUILT_SEAL),
                      'staging ownership/binding mismatch')
            generation = [name.split('/')[1] for name in row['tree'] if name.startswith('generations/') and name.count('/') == 1]
            h.require(len(generation) == 1, 'staged generation membership')
            payload = h.inventory(built / arm / 'runtime')
            for name, digest in payload.items():
                entry = row['tree']['generations/' + generation[0] + '/' + name]
                h.require(entry['sha256'] == digest and entry['uid'] == 0 and entry['mode'] & 0o022 == 0,
                          'staged provider binding/protection mismatch')
            if assessment['cleanup']:
                h.require(arm + '-unstage' in actual, 'missing staging removal command')
                h.require(h.read(root / (arm + '-staging-cleanup.json')) == dict(removed=True, owner=row['owner']) and
                          not os.path.lexists(row['runtime']), 'owned staging cleanup unverified')
    if (root / 'fixtures.json').exists():
        h.require(h.read(root / 'fixtures.json') == h.inventory(root / 'fixtures'), 'fixture inventory mismatch')
    if cleanup_failed:
        h.require(not assessment['cleanup'], 'false cleanup success')
    if not assessment['cleanup']:
        h.require(cleanup_failed or any(os.path.lexists(protected_path(root, arm))
                  for arm in ('control', 'early')), 'uncorroborated cleanup failure')
    if assessment['status'] == 'qualified':
        h.require(completed == names and not failed and assessment['cleanup'] and
                  assessment['native_correctness'] == 'qualified' and required_count == 130, 'false qualification')
    else:
        h.require(bool(failed) or preparation_failure or not assessment['cleanup'], 'unsupported blocked outcome')
        h.require(bool(assessment.get('failure') or assessment.get('cleanup_failure')), 'missing blocker')
    fixed = {'request.json', 'assessment.json', 'integrity.json', 'built.json', 'package.json', 'tools.json', 'protocol-v4.json',
             'schedule.json', 'native-inputs.json', 'REPORT.md', 'seal.json', 'case-accounting.json'}
    fixed |= {'format-fixtures.py', 'fixtures.json'}
    fixed |= {'fixtures/' + name for name in h.inventory(root / 'fixtures')} if (root / 'fixtures').is_dir() else set()
    fixed |= {'tools/' + Path(path).name for path in tools}
    fixed |= {'native-source/' + name for name in native}
    fixed |= {r['arm'] + '/package-resolution.json' for r in rows if r['arm']}
    for arm in ('control', 'early'):
        fixed |= {arm + '-staging.json', arm + '-staging-cleanup.json'}
        fixed |= {arm + '/' + label + '.xml' for label in (*[group['label'] for group in p['prerequisites']], 'mutable-publication',
            'protected-fixture', 'protected-publication', 'protected-preview', 'session')}
    fixed |= {r['name'] + '-identities.json' for r in rows if r['name'].endswith('-linkage')}
    command_files = {'commands/' + name + suffix for name in actual for suffix in
        ('-command.json', '-result.json', '.stdout', '.stderr', '-scopes-before.json', '-scopes-after.json')}
    h.require(all(name in fixed | command_files or any(name.startswith(arm + '/' + directory + '/')
        for arm in ('control', 'early') for directory in ('build', 'private')) for name in inventory),
        'unexpected artifact membership')
    return dict(status='passed', outcome=assessment['status'], decision='Evidence insufficient',
        evidence_seal=h.digest(root / 'seal.json'), completed_commands=len(completed), required_cases_passed=required_count,
        failed_command=failed[0] if failed else None, preparation_failure=preparation_failure,
        observations=0, imports_runner=False,
        verifier_sha256=h.digest(Path(__file__)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.evidence.absolute(), args.output.absolute()
    h.require(output == output.resolve() and not output.exists() and not output.is_relative_to(root) and
              not root.is_relative_to(output), 'verification collision/overlap')
    try:
        result = verify(root)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        result = dict(status='failed', decision='Evidence insufficient', failure=str(error))
    h.write(output, result)
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
