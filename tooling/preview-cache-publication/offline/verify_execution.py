#!/usr/bin/env python3
"""Independent publication observation verifier; imports no controller or build implementation."""
import argparse
import hashlib
import os
from pathlib import Path
import pwd
import re
import struct
import sys
import uuid
import zlib

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evidence as e

h = e.h
DIRECTORY = Path(__file__).resolve().parents[1]
PROTOCOL_SHA256 = '6b15e3179fcac726b838bce3b1725989bf0d30ecea63466beb666f2f27a29d53'
CORRECTNESS_SEAL = '86ffc201c84924df0d06c2aa7a20a33bfa687bd079ba92befc65198b1c6f5727'
BUILT_SEAL = 'd2e45f0c05b464e1c22de87145f35160ac038ff482a0cc72ca04d6f1396b2d7a'


def protocol():
    h.require(h.digest(DIRECTORY / 'EXECUTION-v1.json') == PROTOCOL_SHA256, 'execution protocol drift')
    return h.read(DIRECTORY / 'EXECUTION-v1.json')


def prerequisite(built, correctness):
    h.require(built == built.resolve() and correctness == correctness.resolve(), 'noncanonical prerequisite')
    h.require(h.digest(built / 'seal.json') == BUILT_SEAL and
              h.digest(correctness / 'seal.json') == CORRECTNESS_SEAL, 'prerequisite seal mismatch')
    verifier = e.load('execution_correctness_verifier', DIRECTORY / 'offline/verify_correctness_v4.py')
    proof = verifier.verify(correctness)
    proof_path = correctness.with_name(correctness.name + '-independent.json')
    h.require(h.read(proof_path) == proof and proof['status'] == 'passed' and
              proof['outcome'] == 'qualified' and proof['required_cases_passed'] == 130 and
              proof['completed_commands'] == 55 and proof['failed_command'] is None,
              'qualified independently verified correctness required')
    h.require(Path(h.read(correctness / 'request.json')['built']) == built, 'correctness provider mismatch')
    fixture = e.PACKAGE / '3200x2400.png'
    h.require(h.digest(fixture) == protocol()['fixture_sha256'], 'fixture mismatch')
    return dict(built=dict(path=str(built), seal=BUILT_SEAL, inventory=h.sealed(built)),
        correctness=dict(path=str(correctness), seal=CORRECTNESS_SEAL, proof_sha256=h.digest(proof_path)),
        package=e.package(), fixture=dict(path=str(fixture), sha256=h.digest(fixture)))


def protected_path(root, arm):
    return Path('/run') / ('holonight-publication-' + hashlib.sha256(str(root).encode()).hexdigest()[:20] + '-' + arm)


def environment(uid):
    return dict(PATH='/usr/bin:/bin', HOME=pwd.getpwuid(uid).pw_dir, LANG='C.UTF-8',
        QT_QPA_PLATFORM='offscreen', CMAKE_BUILD_PARALLEL_LEVEL='4',
        XDG_RUNTIME_DIR='/run/user/' + str(uid), DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/' + str(uid) + '/bus')


def expected_schedule(root, built, uid, invocations):
    # Construct commands independently; never import execution scheduling code.
    rows = []
    def add(name, argv, arm=None, privileged=False, workload=False, observation=None):
        env = environment(uid)
        if workload:
            base = root / name
            env.update(HOLONIGHT_CACHE_INVOCATION=invocations[name], PUBLICATION_EVIDENCE=str(base),
                HN_SESSION_RUNTIME=str(protected_path(root, arm)),
                HN_BROWSER_SESSION_RUNTIME=str(protected_path(root, arm)),
                XDG_CACHE_HOME=str(base / 'cache'), TMPDIR=str(base / 'source'))
        rows.append(dict(index=len(rows), name=name, argv=[str(v) for v in argv], arm=arm,
            privileged=privileged, workload=workload, observation=observation, environment=env,
            uid=0 if privileged else uid, timeout_seconds=30 if workload else 600,
            launch=dict(process_group=0) if privileged else dict(start_new_session=True)))
    add('authorization', ['sudo', '-n', '-v'], privileged=True)
    for arm in ('control', 'early'):
        base = root / arm
        add(arm + '-configure', ['cmake', '-S', root / 'native-source' / arm, '-B', base / 'build',
            '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(built / arm / 'prefix')], arm)
        add(arm + '-compile', ['cmake', '--build', base / 'build', '--parallel', '4'], arm)
        add(arm + '-linkage', ['ldd', base / 'build/publication-observation'], arm)
        add(arm + '-stage-authorization', ['sudo', '-n', '-v'], privileged=True)
        add(arm + '-stage', ['sudo', '-n', sys.executable, DIRECTORY / 'execution_stage.py',
            '--output', root, '--arm', arm], arm, privileged=True)
    for observation in protocol()['schedule']:
        arm = observation['arm']
        name = 'observation-' + str(observation['index']).zfill(2)
        add(name, [root / arm / 'build/publication-observation', protected_path(root, arm),
            root / 'fixture.png', 'startup', '1', root / name / 'harness.json'], arm,
            workload=True, observation=observation)
    for arm in ('control', 'early'):
        add(arm + '-unstage-authorization', ['sudo', '-n', '-v'], privileged=True)
        add(arm + '-unstage', ['sudo', '-n', sys.executable, DIRECTORY / 'execution_stage.py',
            '--output', root, '--arm', arm, '--remove'], arm, privileged=True)
    return rows


def verify_schedule(root, built):
    rows = h.read(root / 'schedule.json')
    h.require([row['name'] for row in rows] == protocol()['execution_commands'], 'command schedule membership')
    uid = next((r['uid'] for r in rows if not r['privileged']), None)
    h.require(type(uid) is int and uid > 0, 'desktop privilege boundary')
    invocations = {r['name']: r['environment']['HOLONIGHT_CACHE_INVOCATION'] for r in rows if r['workload']}
    h.require(len(set(invocations.values())) == 12 and
              all(str(uuid.UUID(v)) == v for v in invocations.values()), 'invocation identity mismatch')
    h.require(rows == expected_schedule(root, built, uid, invocations), 'independent schedule/launch/privilege mismatch')
    return rows


def source_contract(root):
    p = protocol()
    for arm in ('control', 'early'):
        source = root / 'native-source' / arm
        text = (source / 'main.cpp').read_text()
        for before, after in reversed(p['harness_insertions']):
            h.require(text.count(after) == 1, 'harness diagnostic insertion mismatch')
            text = text.replace(after, before)
        h.require(text == (e.PACKAGE / arm / 'harness-source/reuse.cpp').read_text(), 'harness workload changed')
        for name in ('CMakeLists.txt', 'publication_checks.h'):
            h.require((source / name).read_bytes() == (DIRECTORY / 'diagnostic-native' / name).read_bytes(),
                      'harness support source drift')
        h.require(set(h.inventory(source)) == {'main.cpp', 'CMakeLists.txt', 'publication_checks.h'}, 'harness source membership')


def resolution(root, built, arm):
    cache = (root / arm / 'build/CMakeCache.txt').read_text()
    values = {line.split(':', 1)[0]: line.split('=', 1)[1] for line in cache.splitlines()
              if line.startswith(('HolonightImages_DIR:', 'HolonightThumbnails_DIR:', 'HolonightFileBrowser_DIR:'))}
    h.require(len(values) == 3 and all(Path(v).resolve().is_relative_to(built / arm / 'prefix')
              for v in values.values()), 'installed package resolution mismatch')
    # Providers are static archives: record the exact link inputs, never claim separate mapped providers.
    ninja = (root / arm / 'build/build.ninja').read_text()
    archives = sorted(set(re.findall(r'(/[^\s]+\.a)(?=\s|$)', ninja)))
    h.require(len(archives) == 6 and all(Path(v).is_relative_to(built / arm / 'prefix') for v in archives),
              'static provider link inputs mismatch')
    return dict(packages=values, archives={v: h.digest(Path(v)) for v in archives})


def linkage(text):
    h.require('not found' not in text, 'unresolved linkage')
    values = {}
    for line in text.splitlines():
        tokens = line.split()
        path = tokens[2] if len(tokens) > 2 and tokens[1] == '=>' else tokens[0] if tokens else ''
        if path.startswith('/'):
            resolved = Path(path).resolve()
            values[str(resolved)] = h.digest(resolved)
    h.require(values, 'missing linkage identities')
    return values


def parse_events(text):
    def pairs(items):
        result = {}
        for key, value in items:
            h.require(key not in result, 'duplicate event field')
            result[key] = value
        return result
    events = []
    for line in text.splitlines():
        if 'CACHE_PUBLICATION' not in line:
            continue
        h.require(line.startswith('CACHE_PUBLICATION '), 'malformed event prefix')
        event = h.json.loads(line[len('CACHE_PUBLICATION '):], object_pairs_hook=pairs)
        stamp = event.get('ns')
        h.require(isinstance(stamp, str) and stamp.isascii() and stamp.isdecimal(), 'nondecimal event timestamp')
        event['ns'] = int(stamp)
        events.append(event)
    h.require(len(events) == 7 and {r['event'] for r in events} ==
              {'eligible', 'store_entry', 'store_return', 'enqueue', 'accepted', 'adequate', 'final'}, 'event membership')
    return events


def png_metadata(path):
    data = path.read_bytes()
    h.require(data.startswith(b'\x89PNG\r\n\x1a\n'), 'cache evidence is not PNG')
    offset, metadata, dimensions = 8, {}, None
    while offset < len(data):
        size = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        chunk = data[offset + 8:offset + 8 + size]
        h.require(len(chunk) == size and size <= 32 * 1024 * 1024 and
                  zlib.crc32(kind + chunk) == struct.unpack('>I', data[offset + 8 + size:offset + 12 + size])[0],
                  'invalid cache PNG chunk')
        if kind == b'IHDR':
            dimensions = struct.unpack('>II', chunk[:8])
        elif kind == b'tEXt':
            key, value = chunk.split(b'\0', 1)
            metadata[key.decode('latin1')] = value.decode('latin1')
        elif kind == b'zTXt':
            key, value = chunk.split(b'\0', 1)
            h.require(value[0] == 0, 'invalid PNG text compression')
            metadata[key.decode('latin1')] = zlib.decompress(value[1:]).decode('latin1')
        offset += size + 12
        if kind == b'IEND':
            h.require(offset == len(data), 'cache PNG trailing data')
            break
    h.require(dimensions is not None and offset == len(data), 'incomplete cache PNG')
    return dimensions, metadata


def observation(root, row):
    base = root / row['name']
    data = h.read(base / 'harness.json')
    h.require(data['scenario'] == 'startup' and data['fixture'] == str(root / 'fixture.png') and
              data['cleanup_failure'] is False and len(data['samples']) == 1, 'harness observation membership')
    sample = data['samples'][0]
    h.require(all(sample[key] is True for key in ('success', 'setup_success', 'correct_pixels', 'correct_metadata')) and
              all(sample[key] is False for key in ('cleanup_failure', 'harness_timeout')) and not sample['error'] and
              sample['superseded_selections'] == 0 and 0 <= sample['first_ms'] <= sample['final_ms'],
              'harness correctness failure')
    h.require([d['event'] for d in sample['deliveries']] == ['pixels', 'metadata'] and
              all(d['selection'] == 4 for d in sample['deliveries']), 'unexpected pixel/metadata deliveries')
    checks = sample['publication_checks']
    h.require(all(checks[k] is True for k in ('cache_available_at_final', 'cache_pixels_match', 'copied')),
              'cache unavailable or wrong pixels at final')
    h.require(checks['source_sha256'] == h.digest(base / 'source.png') == protocol()['fixture_sha256'] and
              checks['cache_sha256'] == h.digest(base / 'cache.png'), 'source/cache evidence mismatch')
    source = Path(checks['source_path'])
    cache = Path(checks['cache_path'])
    h.require(source.is_relative_to(base / 'source') and cache.is_relative_to(source.parent / 'cache'),
              'private source/cache binding mismatch')
    events = parse_events((root / 'commands' / (row['name'] + '.stderr')).read_text())
    first = events[0]
    h.require(isinstance(checks['check_ns'], str) and checks['check_ns'].isascii() and
              checks['check_ns'].isdecimal(), 'nondecimal final-check timestamp')
    identities = ('invocation', 'service', 'request', 'worker', 'preparation', 'transaction', 'source',
                  'generation', 'width', 'height', 'original_decode', 'tier', 'outcome')
    h.require(all(all(item.get(k) == first.get(k) for k in identities) for item in events), 'cross-identity join')
    for key in ('service', 'request', 'worker', 'preparation', 'transaction', 'generation'):
        h.require(isinstance(first.get(key), str) and bool(first[key]), 'missing event identity')
    h.require(first['invocation'] == row['environment']['HOLONIGHT_CACHE_INVOCATION'] and
              first['source'] == checks['source_identity'] and first['width'] == first['height'] == 256 and
              first['original_decode'] is True and type(first['tier']) is int and first['tier'] == 256 and
              type(first['outcome']) is int and first['outcome'] == 0,
              'ineligible request/source/size/tier/outcome')
    h.require(all(not item.get('cancelled') and not item.get('stale') for item in events), 'stale/cancelled event')
    times = {v['event']: v['ns'] for v in events}
    h.require(times['eligible'] <= times['store_entry'] < times['store_return'] <= times['final'] and
              times['eligible'] <= times['enqueue'] <= times['accepted'] <= times['adequate'] <= times['final'] <= int(checks['check_ns']),
              'event ordering mismatch')
    h.require(times['store_return'] <= times['enqueue'] if row['arm'] == 'control' else
              times['enqueue'] <= times['store_entry'], 'arm publication order mismatch')
    identity = checks['source_identity'].split(':')
    h.require(len(identity) == 7 and all(part.isdecimal() for part in identity) and
              int(identity[2]) == (base / 'source.png').stat().st_size, 'invalid source stat identity')
    dimensions, metadata = png_metadata(base / 'cache.png')
    h.require(dimensions == (256, 192) and metadata['Thumb::URI'] == source.as_uri() and
              metadata['Thumb::MTime'] == identity[3] and
              metadata.get('Files::Revision', checks['source_identity']) == checks['source_identity'], 'cache metadata mismatch')
    staged = h.read(root / (row['arm'] + '-staging.json'))
    lease = checks['lease']
    h.require({'target', 'device', 'inode', 'fdinfo'} <= set(lease), 'live protected generation lease unproven')
    expected = protected_path(root, row['arm']) / 'generations' / checks['selected_generation']
    h.require(checks['selected_generation'] == staged['generation'] and lease['target'] == str(expected) and
              lease['device'] == staged['generation_identity']['device'] and
              lease['inode'] == staged['generation_identity']['inode'] and
              re.search(r'FLOCK\s+ADVISORY\s+READ\s+\d+\s+\S+:' + re.escape(lease['inode']) + r'\s+0\s+EOF', lease['fdinfo']),
              'live protected generation lease unproven')
    executable = (root / row['arm'] / 'build/publication-observation').resolve()
    h.require(data['mapped_executable'] == str(executable), 'actual executable identity mismatch')
    mapped = {}
    for line in data['loaded_maps'].splitlines():
        parts = line.split(maxsplit=5)
        if len(parts) == 6 and parts[5].startswith('/'):
            h.require(not parts[5].endswith(' (deleted)'), 'deleted loaded image')
            path = Path(parts[5]).resolve()
            info = path.stat()
            device = parts[3].split(':')
            h.require(path.is_file() and info.st_ino == int(parts[4]) and
                      os.major(info.st_dev) == int(device[0], 16) and os.minor(info.st_dev) == int(device[1], 16),
                      'mapped inode/device mismatch')
            mapped[str(path)] = h.digest(path)
    linked = h.read(root / (row['arm'] + '-linkage.json'))
    h.require(str(executable) in mapped and all(mapped.get(path) == digest for path, digest in linked.items()),
              'actual loaded image mismatch')
    return dict(schedule=row['observation'], events=events, cache_available_at_final=True,
        correct_pixels=True, correct_metadata=True, cleanup_passed=True, native_bindings_passed=True,
        mapped=mapped, helper_loading=protocol()['helper_loading'],
        supports=times['store_entry'] < times['adequate'] < times['store_return'])


def verify(root):
    inventory = h.sealed(root)
    p = protocol()
    h.require(h.digest(root / 'protocol.json') == PROTOCOL_SHA256, 'recorded protocol mismatch')
    request = h.read(root / 'request.json')
    binding = prerequisite(Path(request['built']), Path(request['correctness']))
    h.require(h.read(root / 'binding.json') == binding, 'prerequisite binding drift')
    tools = h.read(root / 'tools.json')
    required = {'execute.py', 'execution_stage.py', 'verify_execution.py', 'EXECUTION-v1.json', 'EXECUTION-v1.md',
                'CMakeLists.txt', 'publication_checks.h', 'test_preview_cache_publication_diagnostic.py'}
    h.require(required <= {Path(path).name for path in tools}, 'missing execution tool snapshot')
    for path, digest in tools.items():
        h.require(h.digest(Path(path)) == digest == h.digest(root / 'tools' / Path(path).name), 'execution tool drift')
    h.require(h.read(root / 'integrity.json')['unchanged'], 'execution input drift')
    h.require(h.digest(root / 'fixture.png') == p['fixture_sha256'], 'attempt fixture drift')
    source_contract(root)
    rows = verify_schedule(root, Path(request['built']))
    names = [r['name'] for r in rows]
    assessment = h.read(root / 'assessment.json')
    attempted, completed = assessment['attempted'], assessment['completed']
    h.require(attempted == names[:len(attempted)] and completed == attempted[:len(completed)] and
              assessment['unexecuted'] == names[len(attempted):] and len(attempted) - len(completed) in (0, 1),
              'stopped execution accounting mismatch')
    actual = {name[len('commands/'):-len('-command.json')] for name in inventory
              if name.startswith('commands/') and name.endswith('-command.json')}
    extra = actual - set(attempted)
    h.require(extra <= {arm + suffix for arm in ('control', 'early') for suffix in ('-unstage', '-unstage-authorization')} and
              set(attempted) <= actual, 'unauthorized execution after stop')
    previous, failed, observations, cleanup_failures = 0, [], [], []
    for row in rows:
        name = row['name']
        if name not in actual:
            continue
        h.require(h.read(root / 'commands' / (name + '-command.json')) == row, 'executed command drift')
        result = h.read(root / 'commands' / (name + '-result.json'))
        h.require(type(result['start_ns']) is int and type(result['stop_ns']) is int and
                  previous <= result['start_ns'] <= result['stop_ns'], 'execution chronology mismatch')
        previous = result['stop_ns']
        h.require(all('commands/' + name + suffix in inventory for suffix in ('.stdout', '.stderr')), 'missing raw output')
        success = result['exit'] == 0 and result['failure'] is None and result['cleanup']
        if result['cleanup']:
            h.require(0 <= result['cleanup_seconds'] <= 5, 'cleanup exceeded shared deadline')
        if not result['cleanup'] or (name.endswith(('-unstage', '-unstage-authorization')) and not success):
            cleanup_failures.append(name)
        if row['privileged'] and row['argv'] != ['sudo', '-n', '-v']:
            check = h.read(root / 'commands' / (name + '-authorization-result.json'))
            h.require(check['exit'] == 0 and check['failure'] is None and check['cleanup'], 'protected command without authorization')
        validation_failure = None
        validated = None
        if success:
            try:
                if name.endswith('-configure'):
                    h.require(h.read(root / (row['arm'] + '-resolution.json')) == resolution(root, Path(request['built']), row['arm']), 'resolution drift')
                elif name.endswith('-linkage'):
                    h.require(h.read(root / (row['arm'] + '-linkage.json')) == linkage((root / 'commands' / (name + '.stdout')).read_text()), 'linkage drift')
                elif row['workload']:
                    for phase in ('before', 'after'):
                        scopes = h.read(root / 'commands' / (name + '-scopes-' + phase + '.json'))
                        h.require(scopes['isolated'] and scopes['exit'] == 0 and not scopes['stdout'].strip() and not scopes['cgroups'], 'scope cleanup unproven')
                    validated = observation(root, row)
            except (OSError, ValueError, KeyError, TypeError, struct.error, zlib.error) as error:
                validation_failure = str(error) or type(error).__name__
        if name in completed:
            h.require(success and validation_failure is None, validation_failure or 'completed failed command')
            if validated:
                h.require(h.read(root / name / 'observation.json') == validated, 'observation reconstruction mismatch')
                observations.append(validated)
        elif name in attempted:
            h.require(not success or validation_failure, 'uncorroborated execution blocker')
            failed.append(name)
    h.require(failed == attempted[len(completed):], 'execution failure accounting mismatch')
    h.require(h.read(root / 'observations.json') == observations, 'observation accounting mismatch')
    for arm in ('control', 'early'):
        staged = root / (arm + '-staging.json')
        if arm + '-stage' in completed:
            h.require(staged.is_file(), 'missing staging ownership record')
        if staged.is_file():
            record = h.read(staged)
            h.require(record['owner'] == dict(output=str(root), arm=arm, built=request['built'], seal=BUILT_SEAL) and
                      record['runtime'] == str(protected_path(root, arm)) and arm + '-stage' in actual, 'staging ownership binding mismatch')
            for name, digest in h.inventory(Path(request['built']) / arm / 'runtime').items():
                member = record['tree']['generations/' + record['generation'] + '/' + name]
                h.require(member['uid'] == 0 and member['mode'] & 0o022 == 0 and member['sha256'] == digest, 'protected staging payload mismatch')
            if assessment['cleanup']:
                h.require(arm + '-unstage' in actual and
                    h.read(root / (arm + '-staging-cleanup.json')) == dict(removed=True, owner=record['owner']) and
                    not os.path.lexists(protected_path(root, arm)), 'owned cleanup unproven')
        for name in extra:
            if name.startswith(arm + '-'):
                h.require(staged.is_file(), 'cleanup without ownership')
    h.require(not cleanup_failures or not assessment['cleanup'], 'false cleanup success')
    if not assessment['cleanup']:
        h.require(cleanup_failures or any(os.path.lexists(protected_path(root, a)) for a in ('control', 'early')), 'uncorroborated cleanup failure')
    if assessment['status'] == 'complete':
        h.require(completed == names and not failed and assessment['cleanup'] and len(observations) == 12, 'incomplete diagnostic')
        decision = 'overlap observed' if any(o['supports'] for o in observations if not o['schedule']['warmup'] and o['schedule']['arm'] == 'early') else 'overlap not observed in this population'
        h.require(e.historical.outcome(observations) == decision, 'frozen observation contract mismatch')
    else:
        h.require(assessment['status'] == 'blocked' and (failed or not assessment['cleanup']) and assessment.get('failure'), 'unsupported blocker')
        decision = 'Evidence insufficient'
    h.require(assessment['decision'] == decision and assessment['observations'] == len(observations), 'false evidence decision')
    fixed = {'request.json', 'binding.json', 'protocol.json', 'schedule.json', 'tools.json', 'fixture.png',
             'integrity.json', 'assessment.json', 'observations.json', 'REPORT.md', 'seal.json'}
    fixed |= {'tools/' + Path(path).name for path in tools}
    fixed |= {'native-source/' + arm + '/' + name for arm in ('control', 'early')
              for name in ('main.cpp', 'CMakeLists.txt', 'publication_checks.h')}
    for arm in ('control', 'early'):
        fixed |= {arm + suffix for suffix in ('-resolution.json', '-linkage.json', '-staging.json', '-staging-cleanup.json')}
    command_files = {'commands/' + name + suffix for name in actual for suffix in
        ('-command.json', '-result.json', '.stdout', '.stderr', '-scopes-before.json', '-scopes-after.json')}
    observation_files = {r['name'] + '/' + name for r in rows if r['workload'] for name in
        ('harness.json', 'observation.json', 'source.png', 'cache.png')}
    h.require(all(name in fixed | command_files | observation_files or
              any(name.startswith(a + '/build/') for a in ('control', 'early')) or
              any(name.startswith(r['name'] + '/' + part + '/') for r in rows if r['workload'] for part in ('source', 'cache'))
              for name in inventory), 'unexpected diagnostic artifact')
    return dict(status='passed', outcome=assessment['status'], decision=decision,
        observations=len(observations), measured=sum(not o['schedule']['warmup'] for o in observations),
        supporting_early=sum(o['supports'] for o in observations if not o['schedule']['warmup'] and o['schedule']['arm'] == 'early'),
        failed_command=failed[0] if failed else None, cleanup=assessment['cleanup'], imports_runner=False,
        evidence_seal=h.digest(root / 'seal.json'), verifier_sha256=h.digest(Path(__file__)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.evidence.absolute(), args.output.absolute()
    h.require(output == output.resolve() and not os.path.lexists(output) and not output.is_relative_to(root) and
              not root.is_relative_to(output), 'verification collision/overlap')
    try:
        result = verify(root)
    except (OSError, ValueError, KeyError, TypeError, struct.error, zlib.error) as error:
        result = dict(status='failed', decision='Evidence insufficient', failure=str(error))
    with output.open('x') as stream:
        h.json.dump(result, stream, indent=2)
        stream.write('\n')
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
