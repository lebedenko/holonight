#!/usr/bin/env python3
"""Independent profile replay; deliberately imports no profiling reporter/runner."""
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import stat
import sys
import subprocess


def read(path):
    return json.loads(path.read_text())


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def seal(root):
    expected = read(root / 'seal.json')
    actual = {}
    for path in root.rglob('*'):
        check(not path.is_symlink(), 'symlink in evidence')
        if path.is_file() and path != root / 'seal.json':
            actual[str(path.relative_to(root))] = digest(path)
    check(actual == expected, 'seal mismatch: ' + str(root))


def verify_diagnostic(root):
    seal(root)
    registration = read(root / 'preregistration.json')
    assessment = read(root / 'assessment.json')
    expected = [dict(mode=mode, settings=settings) for mode in ('launched', 'attached')
                for settings in ('minimal', 'full')]
    check(registration['cases'] == expected and registration['synthetic_only'] and
          registration['timeout_seconds'] == 30 and registration['termination_grace_seconds'] == 5 and
          registration['retries'] == 0, 'diagnostic bounds drift')
    check(assessment['launched_invocations'] == 0 and assessment['unexecuted_invocations'] == 10,
          'diagnostic executed harness')
    check(read(root / 'preserved-before.json') == read(root / 'preserved-after.json'), 'protected input drift')
    check(len(assessment['cases']) <= 4, 'diagnostic retried')
    if assessment['status'] == 'diagnosed':
        check(len(assessment['cases']) == 4, 'incomplete comparisons')
    replay = []
    for index, row in enumerate(assessment['cases']):
        check(row['index'] == index and {key: row[key] for key in ('mode', 'settings')} == expected[index],
              'comparison order drift')
        directory = root / f'{index:02}-{row["mode"]}-{row["settings"]}-recording'
        command = read(directory / 'record-command.json')
        check(command[:2] == ['strace', '-f'] and '-vv' in command and 'sudo' not in command and
              'cpu-clock:u' in command and '--no-inherit' not in command and '--all-cpus' not in command,
              'diagnostic recorder drift')
        if row['settings'] == 'full':
            for option, value in (('--freq', '999'), ('--call-graph', 'dwarf,16384'),
                                  ('--clockid', 'mono'), ('--mmap-pages', '256')):
                check(command[command.index(option)+1] == value, 'full recorder drift')
            check(all(option in command for option in ('--strict-freq', '--timestamp', '--period',
                                                       '--no-buildid-cache')), 'full recorder drift')
        partial = read(directory / 'partial.json')
        check(partial['cleanup_outcomes']['passed'], 'cleanup failed')
        check(partial['stop_ns'] <= int(partial['cleanup_deadline'] * 1e9), 'cleanup deadline exceeded')
        if row['mode'] == 'attached':
            gate = read(directory / 'gate.json')
            check(command[command.index('--pid')+1] == str(gate['pid']), 'attachment PID drift')
            if partial['released']:
                ack = read(directory / 'recorder-ack.json')
                release = read(directory / 'release.json')
                check(ack['hex'] in ('61636b0a', '61636b0a00') and ack['ns'] <= release['ns'] and
                      release['pid'] == gate['pid'], 'released before acknowledgement')
            else:
                check(row['status'] == 'failed' and not partial['acknowledged'], 'unexpected held gate')
        else:
            check(command[-1] == 'synthetic' and command[-3] == '-B', 'non-synthetic launch')
        lines = [line for line in (directory / 'syscalls.log').read_text().splitlines()
                 if 'perf_event_open(' in line]
        check(lines == row['event_open_lines'] and lines, 'event-opening citation drift')
        if row['status'] == 'failed':
            check(any('= -1 E' in line and 'PERF_COUNT_SW_CPU_CLOCK' in line and
                      'PERF_SAMPLE_IP' in line for line in lines), 'unexplained failure')
        replay.append(dict(index=index, status=row['status'], event_open_lines=lines))
    return dict(status='passed', comparisons=replay, launched_invocations=0, unexecuted_invocations=10,
                diagnostic_seal=digest(root / 'seal.json'), imports_runner_or_reporter=False)


def verify_confirmation(root):
    seal(root)
    assessment = read(root / 'assessment.json')
    check(assessment['launched_invocations'] == 0 and assessment['unexecuted_invocations'] == 10 and
          assessment['attempts'] == 1, 'confirmation budget drift')
    registration = read(root / 'preregistration.json')
    check(registration['synthetic_only'] and not registration['traced'] and registration['retries'] == 0,
          'confirmation mode drift')
    diagnostic = Path(registration['diagnostic'])
    verify_diagnostic(diagnostic)
    check(digest(diagnostic / 'seal.json') == registration['diagnostic_seal'], 'diagnostic binding drift')
    check(read(root / 'preserved-before.json') == read(root / 'preserved-after.json'), 'protected input drift')
    mirror = root / 'symfs'
    inventory = {str(path.relative_to(mirror)): digest(path) for path in mirror.rglob('*') if path.is_file()}
    check(not any(path.is_symlink() for path in mirror.rglob('*')), 'linked symbol mirror')
    check(inventory == read(root / 'symbol-mirror.json'), 'symbol mirror drift')
    directory = root / 'rehearsal-recording'
    partial = read(directory / 'partial.json')
    if assessment['status'] != 'complete' and partial['first_failure'] is not None:
        check(partial['cleanup_outcomes']['passed'] and
              partial['stop_ns'] <= int(partial['cleanup_deadline']*1e9), 'unclean recording failure')
        check(partial['first_failure']['recorder_stderr'] == (directory / 'recorder.stderr').read_text(),
              'first recorder error drift')
        check(not partial['released'] or partial['acknowledged'], 'unacknowledged release')
        return dict(status='passed', confirmation='blocked', launched_invocations=0, unexecuted_invocations=10)
    validate_capture(root)
    if assessment['status'] != 'complete':
        # Reproduce the legacy post-recording failure from sealed export/markers.
        exported = read(directory / 'export.command.json')
        if exported['exit'] != 0:
            command = exported['argv']
            check(command[:2] == ['perf', 'script'] and '--symfs' in command and
                  command[command.index('--symfs')+1] == str(mirror) and
                  command[command.index('-i')+1] == str(directory / 'perf.data'), 'unsafe legacy reader')
            done = subprocess.run(command, capture_output=True, text=True,
                                  env=dict(os.environ, DEBUGINFOD_URLS='', DEBUGINFOD_PROGRESS='0', PERF_BUILDID_DIR='/dev/null'))
            check(done.returncode == exported['exit'], 'legacy export failure not reproduced')
            check(assessment['failure'] == 'command failed: export', 'legacy export error mismatch')
        else:
            try:
                confirmation_stacks(root, root)
            except ValueError as error:
                check(str(error) == 'inherited stack samples missing' and
                      assessment['failure'] == 'inheritance/timestamp/stack rehearsal failed',
                      'legacy rehearsal failure mismatch')
            else:
                raise ValueError('legacy rehearsal failure not reproduced')
        return dict(status='passed', confirmation='blocked', failure_reproduced=True,
                    launched_invocations=0, unexecuted_invocations=10)
    return confirmation_stacks(root, root)


def validate_capture(root, target=None):
    target = target or root / 'rehearsal.json'
    directory = target.parent / (target.stem + '-recording')
    command = read(directory / 'record-command.json')
    check(command[:2] == ['perf', 'record'] and '--user-callchains' in command and
          'strace' not in command and 'sudo' not in command and '--no-inherit' not in command,
          'confirmation command drift')
    for key, value in (('--event', 'cpu-clock:u'), ('--freq', '999'), ('--call-graph', 'dwarf,16384'),
                       ('--clockid', 'mono'), ('--mmap-pages', '256')):
        check(command[command.index(key)+1] == value, 'confirmation settings drift')
    check(all(key in command for key in ('--strict-freq', '--no-buildid-cache', '--timestamp', '--period')),
          'confirmation settings drift')
    gate = read(directory / 'gate.json'); release = read(directory / 'release.json')
    expected = ['perf', 'record', '--event', 'cpu-clock:u', '--freq', '999', '--strict-freq',
                '--call-graph', 'dwarf,16384', '--user-callchains', '--clockid', 'mono', '--mmap-pages', '256',
                '--no-buildid-cache', '--timestamp', '--period', '--pid', str(gate['pid']),
                '--delay', '-1', '--control', command[command.index('--control')+1],
                '--output', str(directory / 'perf.data')]
    check(command == expected and re.fullmatch(r'fd:\d+,\d+', command[command.index('--control')+1]),
          'actual recorder settings drift')
    check(gate['uid'] == 1000 and gate['identity']['pid'] == gate['pid'], 'gate identity drift')
    ack = read(directory / 'recorder-ack.json'); partial = read(directory / 'partial.json')
    check(ack['hex'] in ('61636b0a', '61636b0a00') and ack['ns'] <= release['ns'] and
          partial['acknowledged'] and partial['released'], 'acknowledgement/release drift')
    check(gate['pid'] == release['pid'] == int(command[command.index('--pid')+1]), 'exec PID drift')
    check(partial['cleanup_outcomes']['passed'] and partial['cleanup']['passed'] and
          partial['stop_ns'] <= int(partial['cleanup_deadline']*1e9), 'confirmation shutdown failure')
    check(partial['first_failure'] is None, 'workload failure')
    process = read(target.with_suffix('.process.json'))
    check(process['exit'] == 0 and not process['timeout'] and process['cleanup_verified'], 'workload failed')
    check(read(directory / 'recorder-shutdown.json')['passed'], 'recorder shutdown failed')
    check(not any(word in (directory / 'recorder.stderr').read_text().lower() for word in
                  ('lost chunks', 'lost samples', 'failed', 'error:')), 'recorder capture failure')


def confirmation_stacks(source, root):
    validate_capture(source)
    directory = root / 'rehearsal-recording'
    mirror = root / 'symfs'
    gate = read(source / 'rehearsal-recording/gate.json')
    release = read(source / 'rehearsal-recording/release.json')
    exported = read(directory / 'export.command.json')
    check(exported == dict(exit=0, argv=['perf', 'script', '--ns', '--show-task-events',
          '--show-lost-events', '--no-inline', '--symfs', str(mirror), '-F',
          'comm,pid,tid,time,period,event,ip,sym,symoff,dso', '-i',
          str(source / 'rehearsal-recording/perf.data')]), 'offline mirror replay drift')
    header = (directory / 'header.stdout').read_text()
    check(re.search(r'clockid\s*[:=]\s*(1\b|CLOCK_MONOTONIC|monotonic \(1\))', header),
          'monotonic recorder metadata missing')
    markers = [json.loads(line) for line in (root / 'rehearsal.stdout').read_text().splitlines()]
    starts = {(m['pid'], m['tid']): m['start_ns'] for m in markers if 'start_ns' in m}
    stops = {(m['pid'], m['tid']): m['stop_ns'] for m in markers if 'stop_ns' in m}
    check(len(markers) == 6 and starts.keys() == stops.keys() and len(starts) == 3 and (gate['pid'], gate['pid']) in starts,
          'thread/descendant/exec identity mismatch')
    text = (directory / 'export.stdout').read_text()
    check('PERF_RECORD_LOST' not in text and 'PERF_RECORD_THROTTLE' not in text, 'capture loss')
    samples = []
    for block in text.split('\n\n'):
        lines = block.splitlines()
        for index, line in enumerate(lines):
            match = re.search(r' (\d+)/(\d+)\s+(\d+)\.(\d+):\s+\d+\s+cpu-clock:u:', line)
            if match:
                pid, tid, seconds, fraction = match.groups()
                ns = int(seconds)*10**9 + int(fraction.ljust(9, '0'))
                frames = [frame for frame in lines[index+1:] if re.match(r'\s+[0-9a-f]+\s+', frame)]
                samples.append((int(pid), int(tid), ns, len(frames)))
    task_results = []
    check(any(pid == gate['pid'] and tid != pid for pid, tid in starts) and
          any(pid != gate['pid'] and pid == tid for pid, tid in starts), 'worker/descendant mismatch')
    for key, begin in starts.items():
        check(release['ns'] <= begin < stops[key] <= read(source / 'rehearsal-recording/partial.json')['stop_ns'], 'synthetic monotonic timing mismatch')
        check(any((pid, tid) == key and begin <= ns < stops[key] and depth > 1
                  for pid, tid, ns, depth in samples), 'inherited stack samples missing')
        selected = [depth for pid, tid, ns, depth in samples if (pid, tid) == key and begin <= ns < stops[key]]
        task_results.append(dict(pid=key[0], tid=key[1], start_ns=begin, stop_ns=stops[key],
                                 samples=len(selected), multiframe_samples=sum(depth > 1 for depth in selected),
                                 maximum_depth=max(selected)))
    return dict(status='passed', confirmation='complete', tasks=task_results, samples=len(samples), identities=[list(k) for k in starts],
                launched_invocations=0, unexecuted_invocations=10, confirmation_seal=digest(source / 'seal.json'),
                imports_runner_or_reporter=False)


def stable_raw_dump(text):
    # perf materializes the recorded vDSO under a fresh mkstemp name on each read.
    # Normalize only its decoded DSO annotation; raw bytes and MMAP records stay exact.
    return re.sub(r'(?m)^( \.{6} dso: /tmp/perf-vdso\.so-)[A-Za-z0-9]{6}$', r'\1<TEMP>', text)


def verify_replay(root):
    seal(root)
    assessment = read(root / 'assessment.json')
    check(assessment['status'] == 'complete', 'replay failed at ' + assessment.get('failure_stage', 'unknown') + ': ' + assessment.get('failure', 'unknown'))
    registration = read(root / 'preregistration.json')
    check(assessment['status'] == 'complete' and assessment['recording_attempts'] == 0 and
          assessment['attempts'] == 1 and assessment['retries'] == 0 and
          assessment['launched_invocations'] == 0 and assessment['unexecuted_invocations'] == 10,
          'replay budget/status drift')
    check(registration['offline_only'] and registration['attempts'] == 1 and
          registration['recording_attempts'] == registration['retries'] == 0, 'replay registration drift')
    check(os.getuid() == os.geteuid() == 1000, 'verification requires desktop UID 1000')
    check(Path('/proc/self/uid_map').read_text().split() == ['0', '0', '4294967295'], 'host user namespace mismatch')
    references = [path for path in Path('/proc').iterdir() if path.name.isdigit() and
                  path.stat().st_uid == 1000 and (path / 'comm').read_text().strip() == 'Hyprland']
    check(len(references) == 1, 'desktop compositor unavailable')
    for name in ('user', 'mnt', 'pid'):
        check(os.readlink('/proc/self/ns/' + name) == os.readlink(references[0] / 'ns' / name), 'host namespace mismatch')
    source = Path(registration['source'])
    original = verify_confirmation(source)
    check(digest(source / 'seal.json') == registration['source_seal'], 'source seal binding drift')
    perf = source / 'rehearsal-recording/perf.data'
    check(registration['perf_data'] == str(perf) and digest(perf) == registration['perf_sha256'],
          'recording binding drift')
    check(read(root / 'preserved-before.json') == read(root / 'preserved-after.json'), 'protected input drift')
    preserved = read(root / 'preserved-before.json')
    runtime = Path('/run/holonight-validation-preview-cpu-profile-20261115-01-execution/validation/C')
    actual_runtime = {}
    for path in [runtime, *sorted(runtime.rglob('*'))]:
        info = path.lstat()
        check(info.st_uid == 0 and (path.is_symlink() or not info.st_mode & 0o022), 'unprotected runtime')
        actual_runtime[str(path.relative_to(runtime))] = dict(mode=stat.S_IMODE(info.st_mode),
            uid=info.st_uid, gid=info.st_gid, link=os.readlink(path) if path.is_symlink() else None,
            sha256=digest(path) if path.is_file() else None)
    check(actual_runtime == preserved['runtime'], 'protected runtime drift')
    check(registration['tool_identities'] == {str(path.relative_to(root / 'tools')): digest(path)
          for path in (root / 'tools').rglob('*') if path.is_file()}, 'tool snapshot drift')
    check(set(registration['consumed_inputs']) == set(preserved['seals']), 'consumed input binding drift')
    for path, identity in preserved['seals'].items():
        seal(Path(path)); check(digest(Path(path) / 'seal.json') == identity, 'historical binding drift')
    check(preserved['source'] == {str(p.relative_to(source)): digest(p) for p in source.rglob('*') if p.is_file()},
          'consumed input drift')
    mirror = root / 'symfs'
    inventory = {str(p.relative_to(mirror)): digest(p) for p in mirror.rglob('*') if p.is_file()}
    check(not any(p.is_symlink() for p in mirror.rglob('*')) and inventory == read(root / 'symbol-mirror.json'),
          'mirror hash drift')
    for path in (source / 'symfs').rglob('*'):
        if path.is_file():
            check(digest(path) == digest(mirror / path.relative_to(source / 'symfs')), 'frozen file replaced')
    env = dict(os.environ, DEBUGINFOD_URLS='', DEBUGINFOD_PROGRESS='0', PERF_BUILDID_DIR='/dev/null')
    raw = subprocess.check_output(['perf', 'script', '-D', '-i', str(perf)], text=True, env=env)
    check(stable_raw_dump(raw) == stable_raw_dump((root / 'mappings.stdout').read_text()), 'raw mapping evidence drift')
    mappings = {}; excluded = []
    for line in raw.splitlines():
        if 'PERF_RECORD_MMAP2 ' not in line:
            continue
        match = re.search(r'\]: [rwxps-]+ (.+)$', line)
        check(match is not None, 'invalid recorded mapping')
        path = match[1]
        if path.startswith('[') or path.startswith('//anon'):
            excluded.append(line); continue
        check(path.startswith('/') and '..' not in Path(path).parts, 'unsafe mapping')
        candidate = mirror / path.lstrip('/')
        candidate = candidate if candidate.is_file() else Path(path).resolve(strict=True)
        with candidate.open('rb') as stream:
            elf = stream.read(4) == b'\x7fELF'
        if not elf:
            excluded.append(dict(record=line, source=str(candidate), sha256=digest(candidate),
                                 reason='non-ELF file contents'))
            continue
        identity = re.search(r'<([0-9a-f]+)>', line)
        check(identity is not None and set(identity[1]) != {'0'}, 'missing recorded build ID')
        check(path not in mappings or mappings[path] == identity[1], 'conflicting mapping')
        mappings[path] = identity[1]
    check(bool(mappings) and read(root / 'mapped-elfs.json') == dict(files=mappings, excluded=excluded),
          'mapping inventory drift')
    rows = read(root / 'mirror-sources.json')
    check(len(rows) == len(mappings) and {row['recorded_path'] for row in rows} == set(mappings), 'missing mapped ELF')
    for row in rows:
        path = mirror / row['recorded_path'].lstrip('/')
        check(row['build_id'] == mappings[row['recorded_path']] and
              digest(path) == row['sha256'] == digest(Path(row['source'])), 'mapped source drift')
        notes = subprocess.check_output(['readelf', '-n', str(path)], text=True, env=env)
        check(re.findall(r'Build ID: ([0-9a-f]+)', notes) == [row['build_id']], 'mapped build ID mismatch')
        expected_source = path if row['frozen'] else Path(row['recorded_path']).resolve(strict=True)
        check(Path(row['source']) == expected_source, 'source path substitution')
    for name in ('gate.json', 'release.json', 'recorder-ack.json', 'partial.json',
                 'recorder-shutdown.json', 'record-command.json', 'recorder.stderr'):
        check(digest(source / 'rehearsal-recording' / name) == digest(root / 'rehearsal-recording' / name),
              'capture evidence substituted')
    for suffix in ('.stdout', '.process.json'):
        check(digest(source / ('rehearsal'+suffix)) == digest(root / ('rehearsal'+suffix)), 'markers substituted')
    expected_commands = [
        ['perf', 'script', '-D', '-i', str(perf)],
        ['perf', 'report', '--header-only', '--stdio', '-i', str(perf)],
        ['perf', 'script', '--ns', '--show-task-events', '--show-lost-events', '--no-inline',
         '--symfs', str(mirror), '-F', 'comm,pid,tid,time,period,event,ip,sym,symoff,dso', '-i', str(perf)]]
    check(registration['commands'] == expected_commands, 'offline commands drift')
    for command, name, directory in zip(expected_commands, ('mappings', 'header', 'export'),
                                        (root, root / 'rehearsal-recording', root / 'rehearsal-recording')):
        check(read(directory / (name+'.command.json')) == dict(argv=command, exit=0), 'reader settings drift')
        reproduced = subprocess.check_output(command, text=True, env=env)
        saved = (directory / (name+'.stdout')).read_text()
        check((stable_raw_dump(reproduced) == stable_raw_dump(saved)) if name == 'mappings' else reproduced == saved,
              'reader output drift')
    result = confirmation_stacks(source, root)
    result.update(replay='complete', original_confirmation=original['confirmation'], replay_seal=digest(root / 'seal.json'))
    return result



def verify_recording_mirror(directory, mirror):
    perf = directory / 'perf.data'
    env = dict(os.environ, DEBUGINFOD_URLS='', DEBUGINFOD_PROGRESS='0', PERF_BUILDID_DIR='/dev/null')
    raw = subprocess.check_output(['perf', 'script', '-D', '-i', str(perf)], text=True, env=env)
    check(stable_raw_dump(raw) == stable_raw_dump((directory / 'mappings.stdout').read_text()), 'raw mapping evidence drift')
    mappings = {}; excluded = []
    for line in raw.splitlines():
        if 'PERF_RECORD_MMAP2 ' not in line:
            continue
        match = re.search(r'\]: [rwxps-]+ (.+)$', line)
        check(match is not None, 'invalid recorded mapping')
        path = match[1]
        if path.startswith('[') or path.startswith('//anon'):
            excluded.append(line); continue
        check(path.startswith('/') and '..' not in Path(path).parts, 'unsafe mapping')
        candidate = mirror / path.lstrip('/')
        candidate = candidate if candidate.is_file() else Path(path).resolve(strict=True)
        with candidate.open('rb') as stream:
            elf = stream.read(4) == b'\x7fELF'
        if not elf:
            excluded.append(dict(record=line, source=str(candidate), sha256=digest(candidate),
                                 reason='non-ELF file contents'))
            continue
        identity = re.search(r'<([0-9a-f]+)>', line)
        check(identity is not None and set(identity[1]) != {'0'}, 'missing recorded build ID')
        check(path not in mappings or mappings[path] == identity[1], 'conflicting mapping')
        mappings[path] = identity[1]
    check(bool(mappings) and read(directory / 'mapped-elfs.json') == dict(files=mappings, excluded=excluded),
          'mapping inventory drift')
    rows = read(directory / 'mirror-sources.json')
    check(len(rows) == len(mappings) and {row['recorded_path'] for row in rows} == set(mappings), 'missing mapped ELF')
    for row in rows:
        path = mirror / row['recorded_path'].lstrip('/')
        check(row['build_id'] == mappings[row['recorded_path']] and
              digest(path) == row['sha256'] == digest(Path(row['source'])), 'mapped source drift')
        notes = subprocess.check_output(['readelf', '-n', str(path)], text=True, env=env)
        check(re.findall(r'Build ID: ([0-9a-f]+)', notes) == [row['build_id']], 'mapped build ID mismatch')
        expected_source = path if row['frozen'] else Path(row['recorded_path']).resolve(strict=True)
        check(Path(row['source']) == expected_source, 'source path substitution')

    expected = [
        (directory, 'mappings', ['perf', 'script', '-D', '-i', str(perf)]),
        (directory, 'header', ['perf', 'report', '--header-only', '--stdio', '-i', str(perf)]),
        (directory, 'export', ['perf', 'script', '--ns', '--show-task-events', '--show-lost-events',
         '--no-inline', '--symfs', str(mirror), '-F', 'comm,pid,tid,time,period,event,ip,sym,symoff,dso',
         '-i', str(perf)])]
    for target, label, command in expected:
        check(read(target / (label + '.command.json')) == dict(argv=command, exit=0), 'reader command drift')
        reproduced = subprocess.check_output(command, text=True, env=env)
        saved = (target / (label + '.stdout')).read_text()
        check(stable_raw_dump(reproduced) == stable_raw_dump(saved) if label == 'mappings' else
              reproduced == saved, 'reader output drift')
    text = (directory / 'export.stdout').read_text().upper()
    check(not any(word in text for word in ('PERF_RECORD_LOST', 'PERF_RECORD_THROTTLE')), 'capture loss')


def protected_inventory(runtime):
    inventory = {}
    for path in [runtime, *sorted(runtime.rglob('*'))]:
        info = path.lstat()
        check(info.st_uid == 0 and (path.is_symlink() or not info.st_mode & 0o022), 'unprotected runtime')
        inventory[str(path.relative_to(runtime))] = dict(mode=stat.S_IMODE(info.st_mode),
            uid=info.st_uid, gid=info.st_gid, link=os.readlink(path) if path.is_symlink() else None,
            sha256=digest(path) if path.is_file() else None)
    return inventory


def verify_execution_context(execution, registration):
    preflight = registration['preflight']
    check(preflight['status'] == 'passed' and os.getuid() == os.geteuid() == 1000, 'desktop identity drift')
    check(Path('/proc/self/uid_map').read_text().split() == ['0', '0', '4294967295'], 'host user namespace mismatch')
    references = [path for path in Path('/proc').iterdir() if path.name.isdigit() and
                  path.stat().st_uid == 1000 and (path / 'comm').read_text().strip() == 'Hyprland']
    check(len(references) == 1, 'desktop compositor unavailable')
    for name, value in preflight['context']['namespaces'].items():
        check(os.readlink('/proc/self/ns/' + name) == value == os.readlink(references[0] / 'ns' / name),
              'host namespace drift')
    for source, value in preflight['historical_seals'].items():
        seal(Path(source)); check(digest(Path(source) / 'seal.json') == value, 'historical seal drift')
    final = Path(preflight['recovery_final'])
    check(digest(final) == preflight['recovery_final_sha256'] and read(final)['status'] == 'passed' and
          read(final)['replay_seal'] == digest(Path(preflight['recovery']) / 'seal.json'), 'recovery binding drift')
    for path, inventory in preflight.get('historical_runtimes', {}).items():
        check(protected_inventory(Path(path)) == inventory, 'historical runtime drift')
    old = Path('/run/holonight-validation-preview-cpu-profile-20261115-01-execution/validation/C')
    check(protected_inventory(old) == preflight['context']['runtime'], 'historical runtime drift')
    runtime = Path(preflight['runtime']) / 'validation/C'
    if (execution / 'protected-runtime.json').exists():
        check(protected_inventory(runtime) == read(execution / 'protected-runtime.json'), 'protected runtime drift')
    for name, value in registration['stage_request']['installer_hashes'].items():
        check(digest(Path(name)) == value, 'installer drift')
    mirror = execution / 'symfs'
    if mirror.exists():
        check(not any(p.is_symlink() for p in mirror.rglob('*')), 'linked mirror')
        check({str(p.relative_to(mirror)): digest(p) for p in mirror.rglob('*') if p.is_file()} ==
              read(execution / 'symbol-mirror.json'), 'mirror inventory drift')
    check(read(execution / 'residual-processes.json') == [], 'residual processes')
    built = Path(read(Path(registration['package']) / 'inputs.json')['built'])
    for index, entry in enumerate(registration['commands']):
        invocation = entry['invocation']
        check(invocation == dict(arm=invocation['arm'], block=invocation['block'], warmup=index < 2,
              observations=1 if index < 2 else 5, variant='C', mode='validation', fixture='3200x2400.png',
              captured=False), 'invocation contract drift')
        argv = entry['argv']
        check(argv == [str(built / 'validation/C/reuse-harness/preview-benchmark'), str(runtime), argv[2],
              'startup', str(invocation['observations']), str(execution / 'observations' / f'{index:03}.json')] and
              Path(argv[2]).name == '3200x2400.png' and
              argv[2] in read(Path(registration['package']) / 'inputs.json')['fixtures'], 'preregistered command drift')



def dist(values):
    values = sorted(values)
    if not values: return {'count': 0}
    return dict(count=len(values), minimum=values[0], maximum=values[-1],
                median=statistics.median(values), p95=values[math.ceil(len(values)*.95)-1])


def verify(package, execution, report=None):
    check(os.geteuid() != 0, 'offline verification requires desktop user')
    seal(package); seal(execution)
    registration = read(execution / 'preregistration.json')
    check(registration['package'] == str(package) and registration['package_seal'] == digest(package / 'seal.json'),
          'package binding mismatch')
    if registration.get('execution_version') == 2:
        verify_execution_context(execution, registration)
    inputs = read(package / 'inputs.json')
    helper_alias = execution / 'symfs/usr/libexec/holonight-images-helper'
    if helper_alias.exists():
        helper = inputs['binaries']['helper']
        check(not helper_alias.is_symlink() and digest(helper_alias) == helper['sha256'], 'helper mirror identity drift')
    for name, value in inputs['seals'].items():
        check(digest(Path(name) / 'seal.json') == value, 'historical seal identity drift')
    built = Path(inputs['built'])
    # Recompute only the consumed frozen payload/source identities, not historical workloads.
    for binary in inputs['binaries'].values():
        check(digest(Path(binary['path'])) == binary['sha256'], 'binary identity drift')
    base = built / 'validation/C'
    check(inputs['mapping'] == read(base / 'manifest-ordinals.json'), 'ordinal mapping drift')
    manifest = read(base / 'runtime/manifest.json')['files']
    check(inputs['mapping'] == [dict(ordinal=i, **{k: record[k] for k in ('path', 'size', 'sha256')})
                               for i, record in enumerate(manifest)], 'manifest ordinal mismatch')
    for row in manifest:
        path = base / 'runtime' / row['path']
        check(path.stat().st_size == row['size'] and digest(path) == row['sha256'], 'payload identity drift')
    for name, value in inputs['fixtures'].items():
        check(digest(Path(name)) == value, 'fixture identity drift')
    for identity in read(package / 'symbols.json').values():
        check(digest(Path(identity['path'])) == identity['sha256'], 'debug symbol identity drift')
    expected = [(None, arm, 1) for arm in ('unprofiled', 'profiled')]
    for block in range(4):
        expected += [(block, arm, 5) for arm in (('unprofiled', 'profiled') if block % 2 == 0 else ('profiled', 'unprofiled'))]
    commands = registration['commands']
    check([(e['invocation']['block'], e['invocation']['arm'], e['invocation']['observations']) for e in commands] == expected,
          'fixed schedule mismatch')
    template = registration['recorder_template']
    check('sudo' not in template and '--all-cpus' not in template and '--no-inherit' not in template and
          template[template.index('--event')+1] == 'cpu-clock:u' and
          template[template.index('--freq')+1] == '999' and '--strict-freq' in template and
          template[template.index('--call-graph')+1] == 'dwarf,16384' and
          template[template.index('--mmap-pages')+1] == '256', 'recorder contract drift')
    check(registration['environment']['DEBUGINFOD_URLS'] == '', 'automatic symbol downloads enabled')
    for name, value in read(execution / 'tool-identities.json').items():
        check(digest(execution / 'tools' / Path(name).name) == value, 'launch tool snapshot drift')
    assessment = read(execution / 'assessment.json')
    invocations = assessment['invocations']
    check(assessment['launched_invocations'] == len(invocations) and
          assessment['unexecuted_invocations'] == 10-len(invocations), 'launch accounting mismatch')
    check([row['entry'] for row in invocations] == commands[:len(invocations)], 'invocation ordering drift')
    if registration.get('execution_version') == 2 and (invocations or assessment['status'] == 'complete'):
        confirmation_stacks(execution, execution)
        verify_recording_mirror(execution / 'rehearsal-recording', execution / 'symfs')
    measured = warmups = 0
    replayed = []
    for row in invocations:
        if row['status'] != 'passed':
            check(row is invocations[-1] and assessment['status'] == 'blocked', 'continued after failure')
            continue
        invocation = row['entry']['invocation']
        target = Path(row['entry']['argv'][-1])
        data = read(target)
        check(len(data['samples']) == invocation['observations'], 'harness count drift')
        process = read(target.with_suffix('.process.json'))
        check(process['exit'] == 0 and not process['timeout'] and process['cleanup_verified'], 'accepted failed process')
        for sample in data['samples']:
            check(all(sample[k] for k in ('success', 'correct_pixels', 'correct_metadata', 'setup_success')) and
                  not any(sample[k] for k in ('cleanup_failure', 'harness_timeout')), 'correctness gate failed')
        if invocation['warmup']: warmups += len(data['samples'])
        else: measured += len(data['samples'])
        observations = read(target.with_suffix('.cpu-observations.json'))
        if registration.get('execution_version') == 2:
            gate = read(target.parent / (target.stem + '-recording') / 'gate.json')
            check(gate['argv'] == row['entry']['argv'] and gate['pid'] == process['pid'], 'workload command/PID drift')
        if invocation['arm'] == 'profiled':
            if registration.get('execution_version') == 2:
                validate_capture(execution, target)
                verify_recording_mirror(target.parent / (target.stem + '-recording'), execution / 'symfs')
            replay_samples(target, observations)
        replayed.extend((row['index'], invocation, obs) for obs in observations)
    check(measured == assessment['measured_observations'] and warmups == assessment['warmup_observations'], 'observation totals drift')
    if assessment['status'] == 'complete':
        check(len(invocations) == 10 and measured == 40 and warmups == 2, 'incomplete successful experiment')
    else:
        check(bool(assessment.get('failure') or assessment.get('cleanup_failure')), 'unexplained stop')
        rehearsal = execution / 'rehearsal-recording'
        if rehearsal.exists():
            cleanup = read(rehearsal / 'partial.json')
            check(cleanup['gate_reaped'] and (cleanup.get('cleanup') or cleanup.get('cleanup_outcomes', {}).get('recorder', {})).get('reaped', False), 'failed rehearsal left process unreaped')
            if not invocations and assessment.get('failure') == 'recorder readiness failed':
                check(not (rehearsal / 'release.json').exists(), 'unaccounted rehearsal release')
                check(not (execution / 'rehearsal.stdout').read_text(), 'synthetic ran despite blocked gate')
                check(read(rehearsal / 'recorder-ack.json')['hex'] == '', 'unexpected recorder acknowledgement')
        check(read(execution / 'residual-processes.json') == [], 'residual processes')
        check(not list((execution / 'observations').glob('[0-9][0-9][0-9].json')) if not invocations else True,
              'workload artifacts exist without accounted launch')
    if report is not None:
        verify_report(report, assessment, replayed)
    return dict(status='passed', experiment_status=assessment['status'], invocations=len(invocations),
                measured_observations=measured, warmup_observations=warmups,
                unexecuted_invocations=10-len(invocations), package_seal=digest(package / 'seal.json'),
                execution_seal=digest(execution / 'seal.json'), imports_new_reporter=False)


def replay_samples(target, observations):
    """Read raw export once, then reuse addresses and the frozen symbol table."""
    value = read(target.with_suffix('.cpu.json'))
    lines = (target.parent / (target.stem + '-recording') / 'export.stdout').read_text().splitlines()
    check(not any('PERF_RECORD_LOST' in line or 'PERF_RECORD_THROTTLE' in line for line in lines), 'capture loss')
    table = read(target.parents[1] / 'symbol-index.json')
    def symbol(frame):
        text = frame['symbol'].rsplit('+0x', 1)
        offset = int(text[1], 16) if len(text) == 2 else 0
        dso = Path(frame['dso']).name
        candidates = [names for lib, names in table.items() if lib == dso or
                      ('.so.' in lib and dso.startswith(lib.split('.so.')[0]+'.so.'))]
        sizes = [size for names in candidates for size in names.get(text[0], [])]
        return text[0] if sizes and min(sizes) > offset else None
    def category(sample):
        names = [symbol(frame) for frame in sample['frames']]
        leaf = names[0] if names else None
        if not leaf: return 'other/unresolved'
        if re.search(r'(sha256|sha2_|SHA256|SHA2_|EVP_(Digest|MD)|QCryptographicHash::|ossl_.*(sha256|digest))', leaf):
            return 'hashing/dispatch'
        if re.match(r'(__)?(memcpy|memmove|mempcpy|bcopy)', leaf): return 'userspace copying'
        if re.match(r'(QFile|QFileDevice|QIODevice|QRingBuffer|QFSFileEngine|QAbstractFileEngine|QFileSystemEngine)::', leaf):
            return 'Qt I/O/buffering'
        if any(name and re.match(r'(ValidationTrace|DeliveryTrace|StandbyTrace)::', name) for name in names):
            return 'demonstrated probe logging'
        return 'other/unresolved'
    samples = value['capture']['samples']
    for sample in samples:
        line = lines[sample['line']-1]
        check('cpu-clock:u:' in line and str(sample['period']) in line, 'sample citation drift')
        for frame in sample['frames']:
            check(frame['ip'] in lines[frame['line']-1] and frame['symbol'] in lines[frame['line']-1], 'frame citation drift')
    for file in value['files']:
        window = file['window']
        check((window['observation'] is None) == window['setup'], 'setup ownership drift')
        chosen = [s for s in samples if s['pid'] == window['pid'] and s['tid'] == window['tid'] and
                  window['start'] <= s['ns'] < window['stop']]
        counts = Counter(category(s) for s in chosen)
        periods = Counter()
        for s in chosen: periods[category(s)] += s['period']
        check(file['sample_count'] == len(chosen) and file['recorded_period'] == sum(s['period'] for s in chosen), 'sample arithmetic drift')
        for key in file['counts']:
            check(file['counts'][key] == counts[key] and file['periods'][key] == periods[key], 'classification drift')
            check(file['count_shares'] is None if not chosen else file['count_shares'][key] == counts[key]/len(chosen), 'count weighting drift')
            check(file['period_shares'] is None if not chosen else file['period_shares'][key] == periods[key]/file['recorded_period'], 'period weighting drift')
        # Bind each measured window to raw validation citations, not elapsed proximity.
        if not window['setup']:
            owned = [obs for obs in observations if obs['observation'] == window['observation']]
            check(len(owned) == 1, 'ambiguous observation owner')
            spans = [span for item in owned[0]['validation']['files'] for span in item['operations'] if
                     span['operation'] == 'read_hash' and span['ordinal'] == window['ordinal']]
            check(len(spans) == 1 and spans[0]['start'] == window['start'] and spans[0]['stop'] == window['stop'], 'sample/span boundary drift')


def verify_report(report, assessment, replayed):
    seal(report)
    status = read(report / 'assessment.json')
    if assessment['status'] != 'complete':
        check(status['status'] == 'blocked', 'stopped experiment reported complete')
        return
    rows = read(report / 'observations.json')
    check(len(rows) == 40, 'report population drift')
    for row in rows:
        source = [(inv, obs) for index, inv, obs in replayed if index == row['invocation'] and
                  obs['observation'] == row['observation'] and not inv['warmup']]
        check(len(source) == 1, 'report source mapping drift')
        invocation, observation = source[0]
        check(row['arm'] == invocation['arm'] and row['block'] == invocation['block'] and
              row['validation_ns'] == observation['validation']['duration_ns'] and
              row['pixel_ns'] == observation['endpoints']['pixels']['harness_latency_ns'] and
              row['metadata_ns'] == observation['endpoints']['metadata']['harness_latency_ns'], 'report timing citation drift')
        if row['arm'] == 'profiled':
            for category in row['sampled']['counts']:
                check(row['sampled']['counts'][category] == sum(f['counts'][category] for f in row['files']) and
                      row['sampled']['periods'][category] == sum(f['periods'][category] for f in row['files']), 'observation aggregation drift')
    for summary in read(report / 'summary.json'):
        selected = [r for r in rows if r['arm'] == summary['arm'] and
                    (summary['block'] == 'pooled' or r['block'] == summary['block'])]
        for key, value in summary['timings'].items():
            check(dist([r[key] for r in selected]) == value, 'distribution arithmetic drift')
        if summary['arm'] == 'profiled':
            for kind in ('count', 'period'):
                for key, value in summary['category_'+kind+'_shares'].items():
                    check(dist([r['sampled'][kind+'_shares'][key] for r in selected if r['sampled'][kind+'_shares'] is not None]) == value,
                          'category distribution drift')
    for arm, fields in read(report / 'tails.json').items():
        for field, selected in fields.items():
            population = [row for row in rows if row['arm'] == arm]
            cutoff = sorted(row[field] for row in population)[math.ceil(.95*len(population))-1]
            check({(r['invocation'], r['observation']) for r in selected} ==
                  {(r['invocation'], r['observation']) for r in population if r[field] >= cutoff}, 'cutoff tie selection drift')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path); parser.add_argument('--execution', type=Path)
    parser.add_argument('--diagnostic', type=Path)
    parser.add_argument('--confirmation', type=Path)
    parser.add_argument('--replay', type=Path)
    parser.add_argument('--report', type=Path); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.replay:
            check(args.package is None and args.execution is None and args.report is None and
                  args.diagnostic is None and args.confirmation is None, 'mixed verification modes')
            result = verify_replay(args.replay.absolute())
        elif args.confirmation:
            check(args.package is None and args.execution is None and args.report is None and
                  args.diagnostic is None, 'mixed verification modes')
            result = verify_confirmation(args.confirmation.absolute())
        elif args.diagnostic:
            check(args.package is None and args.execution is None and args.report is None, 'mixed verification modes')
            result = verify_diagnostic(args.diagnostic.absolute())
        else:
            check(args.package is not None and args.execution is not None, 'package and execution required')
            result = verify(args.package.absolute(), args.execution.absolute(), args.report.absolute() if args.report else None)
    except Exception as error:
        result = dict(status='failed', error=dict(type=type(error).__name__, message=str(error)))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
    print({k: value for k, value in result.items() if k != 'comparisons'})
    sys.exit(result['status'] != 'passed')
