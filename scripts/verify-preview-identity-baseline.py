#!/usr/bin/env python3
"""Independent offline verifier. Imports neither preparation nor runner."""
import argparse
import hashlib
import importlib.util
import math
from pathlib import Path
import statistics
import struct
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('verified_identity_boundary', Path(__file__).with_name('preview-identity-evidence.py'))
e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e)
h = e.h


def expected_schedule():
    combinations = [('A-fixed', False), ('A-fixed', True), ('C', False), ('C', True)]
    sequence = [(None, 0, v, c) for v, c in combinations]
    for block in range(5):
        order = [combinations[(block + i) % 4] for i in range(4)]
        if block & 1:
            order.reverse()
        sequence += [(block, sample, v, c) for v, c in order for sample in range(5)]
    return [dict(invocation=i, variant=v, captured=c, block=b, sample=s, warmup=b is None, count=1)
            for i, (b, s, v, c) in enumerate(sequence)]


def check_protocol(value):
    h.require(value == dict(version=1, schedule=expected_schedule(), measured=100, warmups=4,
        timeout_seconds=30, cleanup_seconds=5, retries=0, event='dummy:u', no_samples=True, clock='mono',
        inheritance=True, buildid_mmap=True, namespaces=True, task=True, buildid_cache=False,
        symbol_downloads=False, cpu_samples=False, callstacks=False, scheduler_events=False,
        offscreen=True, cache_flush=False, affinity=False, artificial_load=False, qualification='78/80 unchanged',
        mapping_scope='captured executions only', installer_scope='new staging only; no historical attestation',
        acceptance='prepared; execution capability unvalidated'), 'protocol/schedule/population arithmetic')


def verify(package):
    h.sealed(package)
    result = h.read(package / 'assessment.json')
    h.require(result['status'] in ('prepared', 'blocked') and result['capability'] == 'unvalidated' and
              all(type(result[k]) is int and result[k] == 0 for k in ('workloads', 'builds', 'staging', 'recordings')),
              'preparation execution/claim mismatch')
    expected_report = ('# Identity-bound startup baseline preparation\n\n' + result['status'] +
        '; execution capability unvalidated.\n\nZero builds, staging operations, workloads or recordings launched. '
        'New installer identity does not attest historical execution. Qualification remains 78/80; '
        'no optimization selected. Mapping evidence will apply only to captured executions.\n\n' +
        result.get('failure', 'A later authorized capability rehearsal is required before real observations.') + '\n')
    h.require((package / 'REPORT.md').read_text() == expected_report, 'preparation report claims')
    tools = h.read(package / 'tools.json')
    h.require(tools == e.snapshots(), 'tool/installer/protocol membership or drift')
    h.require(h.inventory(package / 'tools') == {Path(k).name: v for k, v in tools.items()}, 'tool snapshot mismatch')
    if result['status'] == 'blocked':
        h.require(result.get('failure'), 'unexplained blocked preparation')
    else:
        h.require(set(result) == {'status', 'capability', 'workloads', 'builds', 'staging', 'recordings'}, 'unsupported preparation claim')
        inputs = h.read(package / 'inputs.json')
        h.require(inputs == e.retained(), 'retained input membership/substitution/drift')
        check_protocol(h.read(package / 'protocol.json'))
        expected = {}
        for variant, value in inputs['variants'].items():
            prefix = 'frozen/' + variant + '/'
            expected[prefix + 'preview-benchmark'] = value['harness']['sha256']
            for path, digest in value['inventory'].items():
                expected[prefix + 'runtime/' + path] = digest
            e.payload(package / 'frozen' / variant / 'runtime', value['inventory'])
            h.require(e.ordinary(package / 'frozen' / variant / 'preview-benchmark') ==
                      {k: value['harness'][k] for k in ('size', 'sha256')}, 'harness size/digest substitution')
        expected['frozen/3200x2400.png'] = inputs['fixture']['sha256']
        h.require(h.inventory(package / 'frozen') == {k[7:]: v for k, v in expected.items()}, 'frozen membership mismatch')
        expected.update({'tools/' + Path(k).name: v for k, v in tools.items()})
        expected.update({k: h.digest(package / k) for k in ('inputs.json', 'protocol.json', 'assessment.json',
                                                            'REPORT.md', 'tools.json', 'seal.json')})
        h.require(h.inventory(package) == expected, 'preparation artifact membership')
        h.require(h.recheck(inputs['inventories'], dict(inputs['files'], **tools)), 'verification drift')
    return dict(status='passed', outcome=result['status'], preparation_seal=h.digest(package / 'seal.json'),
                capability='unvalidated', imports_runner=False)


def check_events(events, root):
    lives = {root['pid']: [root['start'], root['namespace'], False]}
    seen = {(root['pid'], root['start'])}
    mappings, exclusions = [], []
    for index, record in enumerate(events):
        kind, pid = record['kind'], record.get('pid')
        if kind == 'fork':
            h.require(record['ppid'] in lives and pid not in lives and (pid, record['start']) not in seen and
                      record['namespace'] == lives[record['ppid']][1], 'invalid fork/PID reuse')
            lives[pid] = [record['start'], record['namespace'], lives[record['ppid']][2]]
            seen.add((pid, record['start']))
            continue
        h.require(pid in lives and lives[pid][0] == record['start'], 'missing explicit process lifetime')
        if kind == 'namespace':
            h.require(record['namespace'], 'missing namespace')
            lives[pid][1] = record['namespace']
            continue
        h.require(lives[pid][1] == record['namespace'], 'mapping namespace conflict')
        if kind == 'exec':
            lives[pid][2] = True
        elif kind == 'mapping':
            if not record['path'].startswith('/') or record['path'].startswith('//'):
                exclusions.append(dict(record=record, reason='anonymous/non-file mapping'))
            else:
                h.require(lives[pid][2] and record.get('build_id') and record.get('sha256') and
                          type(record.get('size')) is int and record['size'] > 0, 'missing mapping ELF identity')
                h.require(record.get('scope') == ('desktop' if record['namespace'] == root['namespace'] else 'sandbox'),
                          'missing/conflicting mapping namespace scope')
                mappings.append(dict(record, event_index=index))
        elif kind == 'exit':
            del lives[pid]
        else:
            h.require(kind == 'comm', 'capture loss/unsupported event')
    h.require(not lives and mappings, 'incomplete capture lifetimes')
    return dict(mappings=mappings, exclusions=exclusions, lifetimes=sorted([list(x) for x in seen]))


def check_recorder_access(access, identity, gate, recorder_sha256):
    path = Path(access['path'])
    h.require(path.is_absolute() and path.parent.parent == Path('/var/lib') and
              path.parent.name.startswith('holonight-identity-recorder-') and path.name == 'perf' and
              access == dict(path=str(path), sha256=recorder_sha256, capability='cap_perfmon=ep',
                             uid=0, gid=1000, mode=0o750), 'unsupported capability recorder binding')
    fields = dict(line.split(':', 1) for line in identity['status'].splitlines() if ':' in line)
    h.require(fields['Uid'].split() == ['1000'] * 4 and
              int(fields['CapPrm'], 16) == int(fields['CapEff'], 16) == 1 << 38 and
              identity['namespaces'] == gate['identity']['namespaces'], 'recorder privilege/namespace identity')


def checked_report(observations):
    populations, blocks = {}, []
    for captured in (False, True):
        for variant in ('A-fixed', 'C'):
            selected = [r for r in observations if not r['schedule']['warmup'] and
                        (r['schedule']['variant'], r['schedule']['captured']) == (variant, captured)]
            cells = {}
            for event in ('first_ms', 'final_ms'):
                data = sorted(r['sample'][event] for r in selected)
                cells[event] = dict(count=len(data), median=statistics.median(data), p95=data[math.ceil(.95 * len(data)) - 1]) if data else None
            populations[variant + ('/captured' if captured else '/uncaptured')] = cells
        for block in range(5):
            for event in ('first_ms', 'final_ms'):
                a, c = [[r['sample'][event] for r in observations if not r['schedule']['warmup'] and
                         (r['schedule']['variant'], r['schedule']['captured'], r['schedule']['block']) == (v, captured, block)]
                        for v in ('A-fixed', 'C')]
                if len(a) == len(c) == 5:
                    blocks.append(dict(captured=captured, block=block, event=event,
                        C_minus_A_fixed_median=statistics.median(c) - statistics.median(a), C_minus_A_fixed_p95=max(c) - max(a)))
    return dict(populations=populations, signed_blocks=blocks,
        mapping_scope='captured executions only; uncaptured loading identities unavailable',
        qualification='78/80 unchanged', optimization=None, overhead_correction=False,
        historical_timing_transfer=False, qualification_inference=False)


def check_raw_perf(path, root, exported):
    """Re-decode raw task/namespace/mapping records independently of the runner."""
    data = path.read_bytes()
    h.require(len(data) >= 104 and data[:8] == b'PERFILE2', 'truncated raw perf format')
    attr_stride, attr_offset, attr_bytes, begin, length = struct.unpack_from('<QQQQQ', data, 16)
    h.require(attr_bytes == attr_stride and attr_stride >= 112 and attr_offset + attr_stride <= len(data),
              'recorder event membership')
    attr = data[attr_offset:attr_offset + attr_stride]
    event_type, attr_size, config, period, sample_type = struct.unpack_from('<IIQQQ', attr)
    flags = struct.unpack_from('<Q', attr, 40)[0]
    required = sum(1 << bit for bit in (1, 5, 8, 9, 13, 18, 23, 24, 25, 28, 34))
    h.require(attr_size >= 96 and attr_size + 16 == attr_stride and event_type == 1 and config == 9 and
              period == 0 and flags & required == required and not flags & (1 << 26) and sample_type == 263 and
              struct.unpack_from('<i', attr, 92)[0] == 1, 'raw recorder is not metadata-only monotonic dummy:u')
    h.require(begin + length <= len(data), 'truncated raw capture')
    ordered = []
    cursor = begin
    while cursor < begin + length:
        h.require(begin + length - cursor >= 8, 'raw short header')
        kind, misc, count = struct.unpack_from('<IHH', data, cursor)
        h.require(count >= 8 and cursor + count <= begin + length, 'raw record length')
        body = data[cursor:cursor + count]
        position = cursor
        cursor += count
        h.require(kind not in (2, 5, 6, 9, 13), 'raw capture loss/samples/throttle')
        if kind >= 64:
            h.require(misc == 0, 'raw bookkeeping flags')
            if kind in (68, 82):
                h.require(count == 8, 'raw marker length')
            elif kind == 69 or kind == 73:
                h.require(count >= 16, 'raw bookkeeping count absent')
                entries = int.from_bytes(body[8:16], 'little')
                width = 32 if kind == 69 else 24
                h.require(count - 16 == entries * width, 'raw bookkeeping array length')
            elif kind == 74:
                h.require(count == 16, 'raw CPU_MAP length')
                h.require(body[8:10] == b'\x02\x00' and body[10] in (0, 1) and body[11] == 0 and
                          int.from_bytes(body[12:14], 'little') <= int.from_bytes(body[14:16], 'little') < 65535,
                          'raw CPU_MAP range/encoding/padding')
            elif kind == 78:
                h.require(count == 32, 'raw EVENT_UPDATE length')
                h.require(int.from_bytes(body[8:16], 'little') == 3, 'raw EVENT_UPDATE variant')
                ids_begin, ids_length = struct.unpack_from('<QQ', attr, attr_stride - 16)
                h.require(ids_length > 0 and ids_length % 8 == 0 and ids_begin + ids_length <= len(data),
                          'raw EVENT_UPDATE ID section')
                ids = [data[i:i + 8] for i in range(ids_begin, ids_begin + ids_length, 8)]
                h.require(body[16:24] in ids, 'raw EVENT_UPDATE event ID')
                h.require(body[24:26] == b'\x02\x00' and body[26] in (0, 1) and body[27] == 0 and
                          int.from_bytes(body[28:30], 'little') <= int.from_bytes(body[30:32], 'little') < 65535,
                          'raw EVENT_UPDATE CPU range/encoding/padding')
            elif kind == 79:
                h.require(count == 56, 'raw TIME_CONV length')
                h.require(int.from_bytes(body[8:16], 'little') < 64 and int.from_bytes(body[16:24], 'little') > 0 and
                          body[48] in (0, 1) and body[49] in (0, 1) and body[50:] == bytes(6),
                          'raw TIME_CONV fields')
            else:
                raise ValueError('raw unsupported metadata: ' + str(kind))
            continue
        h.require(kind in (1, 3, 4, 7, 8, 10, 14, 15, 16, 17, 18, 19, 20, 21), 'raw unsupported metadata')
        minimum = {1: 41, 3: 17, 4: 32, 7: 32, 10: 73, 16: 136}.get(kind, 8)
        h.require(count >= minimum + 16, 'raw missing timestamp trailer')
        timestamp = int.from_bytes(body[-8:], 'little')
        body = body[:-16]
        if kind in (1, 3, 10):
            h.require(b'\0' in body[{1: 40, 3: 16, 10: 72}[kind]:], 'raw string termination')
        if kind in (4, 7, 16):
            h.require(len(body) == (136 if kind == 16 else 32), 'raw fixed record length')
        ordered.append((timestamp, position, kind, misc, body))
    tasks = {root['pid']: [root['start'], root['namespace'], False]}
    actual = []
    def emit(kind, pid, **extra):
        life = tasks[pid]
        actual.append(dict(kind=kind, pid=pid, start=life[0], namespace=life[1], **extra))
    for _, _, kind, misc, body in sorted(ordered, key=lambda row: (row[0], row[1])):
        if kind in (4, 7):
            pid, parent, tid, _, stamp = struct.unpack_from('<IIIIQ', body, 8)
            if tid != pid:
                continue
            if kind == 7:
                if pid == root['pid'] and pid in tasks:
                    continue
                h.require(parent in tasks and pid not in tasks, 'raw fork lifetime conflict')
                tasks[pid] = [stamp, tasks[parent][1], tasks[parent][2]]
                emit('fork', pid, ppid=parent)
            else:
                h.require(pid in tasks, 'raw exit lifetime conflict')
                emit('exit', pid)
                del tasks[pid]
        elif kind in (1, 3, 10, 16):
            pid = struct.unpack_from('<I', body, 8)[0]
            h.require(pid in tasks, 'raw unavailable process')
            if kind == 16:
                h.require(struct.unpack_from('<Q', body, 16)[0] == 7 and len(body) >= 136, 'raw namespace membership')
                tasks[pid][1] = body[24:136].hex()
                emit('namespace', pid)
            elif kind == 3 and misc & (1 << 13):
                emit('exec', pid)
                tasks[pid][2] = True
            elif kind in (1, 10) and tasks[pid][2]:
                h.require(kind == 10, 'raw mapping missing build ID')
                name = body[72:].split(b'\0', 1)[0].decode()
                mapping = dict(path=name)
                if name.startswith('/') and not name.startswith('//'):
                    h.require(misc & (1 << 14) and 0 < body[40] <= 20, 'raw missing build ID')
                    h.require(len(actual) < len(exported), 'raw mapping membership')
                    saved = exported[len(actual)]
                    mapping.update(build_id=body[44:44 + body[40]].hex(),
                        scope='desktop' if tasks[pid][1] == root['namespace'] else 'sandbox',
                        size=saved.get('size'), sha256=saved.get('sha256'))
                emit('mapping', pid, **mapping)
        else:
            h.require(kind in (8, 14, 15, 17, 18, 19, 20, 21), 'raw unsupported metadata')
    h.require(actual == exported and not tasks, 'raw exported process/mapping/namespace binding')


def check_mapping_source(record, root, frozen, payload, staging):
    """Bind bytes to the namespace's source independently of the runner."""
    sandbox = record['namespace'] != root['namespace']
    h.require(record['scope'] == ('sandbox' if sandbox else 'desktop'), 'mapping source scope')
    path = record['path']
    member = None
    if sandbox:
        current, desktop = bytes.fromhex(record['namespace']), bytes.fromhex(root['namespace'])
        h.require(len(current) == len(desktop) == 112 and current[80:96] != desktop[80:96],
                  'sandbox mount namespace source binding')
        h.require(path.startswith('/usr/') and path[1:] in payload, 'sandbox source membership')
        member = path[1:]
        source = frozen / member
    elif Path(path).is_relative_to(Path(staging['runtime'])):
        # The disposable staged tree has already been removed at verification.
        # Join its retained outer identity to the exact frozen payload instead.
        relative = str(Path(path).relative_to(staging['runtime']))
        h.require(relative.startswith(staging['prefix']), 'staged source variant')
        member = relative[len(staging['prefix']):]
        h.require(member in payload, 'staged source membership')
        inode = staging['inventory'].get(relative, {})
        h.require(inode.get('kind') == 'file' and inode.get('uid') == 0 and not inode.get('mode', 0) & 0o022 and
                  all(inode.get(k) == payload[member][k] for k in ('size', 'sha256')), 'staged source inode binding')
        source = frozen / member
    else:
        source = Path(path).resolve()
    actual = e.ordinary(source)
    h.require(actual == {k: record[k] for k in ('size', 'sha256')} and e.elf_id(source) == record['build_id'],
              'mapped source ELF identity')
    if member is not None:
        h.require(actual == payload[member], 'mapped source payload identity')


def check_authorization(value, before_ns):
    h.require(value['argv'] == ['sudo', '-A', '-v'] and value['exit'] == 0 and
              value['worker_reaped'] is True and value['interrupted'] is False,
              'unsuccessful authorization')
    begin, end = value['started_ns'], value['completed_ns']
    h.require(type(begin) is int and type(end) is int and 0 <= begin <= end <= before_ns and
              math.isclose(value['wait_seconds'], (end - begin) / 1e9), 'authorization/timing boundary')


def check_elevated_phase(output, action):
    machine = h.read(output / (action + '-execution.json'))
    check_authorization(h.read(output / (action + '-authorization.json')), machine['started_ns'])
    begin, end = machine['started_ns'], machine['completed_ns']
    h.require(machine['argv'][:2] == ['sudo', '-n'] and machine['exit'] == 0 and
              machine['worker_reaped'] is True and machine['interrupted'] is False and
              type(begin) is int and type(end) is int and 0 <= begin <= end and
              math.isclose(machine['elapsed_seconds'], (end - begin) / 1e9), 'elevated worker completion')
    worker = h.read(output / (action + '-worker.json'))
    h.require(begin <= worker['started_ns'] <= worker['verified_ns'] <= worker['completed_ns'] <= end and
              math.isclose(worker['verification_seconds'], (worker['verified_ns'] - worker['started_ns']) / 1e9) and
              math.isclose(worker['operation_seconds'], (worker['completed_ns'] - worker['verified_ns']) / 1e9),
              'elevated worker phase timing')


def verify_execution(output):
    h.sealed(output)
    preparation = h.read(output / 'preparation.json')
    package = Path(preparation['path'])
    h.require(verify(package)['outcome'] == 'prepared' and preparation['seal'] == h.digest(package / 'seal.json'), 'execution preparation binding')
    result = h.read(output / 'assessment.json')
    observations = h.read(output / 'observations.json')
    h.require(result.get('mode') in ('baseline', 'capability-rehearsal'), 'execution population mode')
    rehearsal = result['mode'] == 'capability-rehearsal'
    schedule = expected_schedule()[:4] if rehearsal else expected_schedule()
    h.require(result['status'] in ('complete', 'synthetic-complete', 'rehearsed', 'synthetic-rehearsed', 'blocked') and
              type(result['synthetic']) is bool and 0 <= result['attempted'] <= len(schedule) and
              result['unexecuted'] == schedule[result['attempted']:] and
              result['accepted_observations'] == len(observations) and
              len(observations) <= result['attempted'] <= len(observations) + 1, 'execution counts/stop-on-failure')
    if result['status'] != 'blocked':
        h.require(result['attempted'] == len(observations) == len(schedule) and result['cleanup_verified'] and
                  result['status'] == (('synthetic-rehearsed' if result['synthetic'] else 'rehearsed') if rehearsal else
                                        ('synthetic-complete' if result['synthetic'] else 'complete')), 'incomplete/mislabelled population')
    else:
        h.require(result.get('failure') or result.get('cleanup_failure'), 'unexplained blocked execution')
    if not result['synthetic'] and result['status'] != 'blocked':
        for action in ('stage', 'cleanup'):
            check_elevated_phase(output, action)
        capability = h.read(output / 'capability.json')
        h.require(capability['uid'] != 0 and capability['preparation_seal'] == preparation['seal'] and
                  capability['protocol'] == h.read(package / 'protocol.json'), 'capability binding')
        outer = h.read(output / 'staged-outer.json')
        h.require(outer == h.read(output / 'cleanup-expected.json') and
                  all(row['uid'] == 0 and not row['mode'] & 0o022 for row in outer.values()), 'staging ownership/permissions')
        inputs = h.read(package / 'inputs.json')
        for variant in ('A-fixed', 'C'):
            if variant == 'C':
                generation = bytes.fromhex(outer['C/current']['bytes']).decode().strip() if 'bytes' in outer['C/current'] else None
                # Selectors are ordinary files; their exact bytes are retained
                # alongside the full outer inventory, not a nested payload row.
                h.require(generation is not None and '/' not in generation and generation not in ('', '.', '..'), 'staging generation selector')
                prefix = 'C/generations/' + generation + '/'
            else:
                prefix = 'A-fixed/'
            nested = {k[len(prefix):]: row['sha256'] for k, row in outer.items() if k.startswith(prefix) and row['kind'] == 'file'}
            h.require(nested == inputs['variants'][variant]['inventory'], 'outer/nested staging payload membership')
        if not rehearsal:
            checked = h.read(output / 'capability-verification.json')
            source = Path(checked['evidence'])
            h.require(source != output and checked['outcome'] == 'rehearsed' and not checked['synthetic'] and
                      checked == verify_execution(source) and h.read(source / 'capability.json') == capability,
                      'missing accepted capability rehearsal')
    capability = h.read(output / 'capability.json') if not result['synthetic'] and (output / 'capability.json').exists() else {}
    ledgers = {}
    for i, observation in enumerate(observations):
        h.require(observation['schedule'] == schedule[i], 'observation schedule mixing')
        raw = h.read(output / f'{i:03}/raw-result.json')
        if not result['synthetic'] and 'recorder_access' in capability:
            process = h.read(output / f'{i:03}/harness.process.json')
            check_authorization(h.read(output / f'{i:03}/workload-authorization.json'), process['start_ns'])
        h.require(raw['exit'] == 0 and not raw['timeout'] and 0 <= raw['elapsed_seconds'] <= 30 and
                  raw['cleanup'] and 0 <= raw['cleanup_seconds'] <= 5, 'execution deadline/cleanup')
        samples = raw['harness'].get('samples', [])
        h.require(len(samples) == 1 and not raw['harness'].get('cleanup_failure'), 'harness count/cleanup')
        sample = samples[0]
        h.require(all(sample.get(k) is True for k in ('success', 'setup_success', 'correct_pixels', 'correct_metadata')) and
                  not sample.get('cleanup_failure') and not sample.get('harness_timeout') and
                  all(type(sample.get(k)) in (float, int) and math.isfinite(sample[k]) for k in ('first_ms', 'final_ms')) and
                  0 <= sample['first_ms'] <= sample['final_ms'] and sample == observation['sample'], 'startup correctness/raw sample binding')
        if schedule[i]['captured']:
            h.require(raw['acknowledged'] and raw['ack_ns'] < raw['release_ns'] and raw['raw_recording'] and
                      not raw['capture_loss'], 'capture acknowledgement/loss')
            account = check_events(raw['events'], raw['root'])
            h.require(account == observation['identities'], 'lifetime attribution mismatch')
            ledger = {}
            for mapping in account['mappings']:
                value = {k: mapping[k] for k in ('size', 'sha256', 'build_id')}
                key = mapping['scope'] + ':' + mapping['path']
                h.require(key not in ledger or ledger[key] == value, 'conflicting mapping bytes')
                ledger[key] = value
            variant = schedule[i]['variant']
            if schedule[i]['warmup']:
                ledgers[variant] = ledger
            else:
                h.require(all(k in ledgers[variant] and ledgers[variant][k] == v for k, v in ledger.items()), 'unexpected/deviant measured mapping')
            if not result['synthetic']:
                recording = output / f'{i:03}/harness-recording'
                check_raw_perf(recording / 'perf.data', raw['root'], raw['events'])
                stderr = (recording / 'recorder.stderr').read_text().lower()
                h.require(not any(word in stderr for word in ('lost chunks', 'lost samples', 'perf_record_lost', 'error:', 'failed')),
                          'recorder loss/error diagnostic')

                gate = h.read(recording / 'gate.json')
                if 'recorder_access' in capability:
                    recorder = h.read(recording / 'recorder-identity.json')
                    check_recorder_access(capability['recorder_access'], recorder, gate, capability['recorder_sha256'])
                    reader = h.read(output / f"recorder-identity-reader-{recorder['pid']}.json")
                    h.require(reader['exit'] == 0 and reader['argv'][:2] == ['sudo', '-n'] and
                              reader['worker_reaped'] is True and reader['interrupted'] is False and
                              h.json.loads(reader['stdout']) == recorder,
                              'recorder identity reader evidence')
                h.require(raw['root']['pid'] == gate['pid'] and raw['root']['start'] ==
                          gate['stat'].rsplit(')', 1)[1].split()[19], 'gate PID/start identity')
                namespace_bytes = bytes.fromhex(raw['root']['namespace'])
                h.require(len(namespace_bytes) == 112, 'gate namespace membership')
                names = ('net', 'uts', 'ipc', 'pid', 'user', 'mnt', 'cgroup')
                h.require(all(struct.unpack_from('<Q', namespace_bytes, j * 16 + 8)[0] ==
                              int(gate['identity']['namespaces'][name].split('[')[1][:-1])
                              for j, name in enumerate(names)), 'gate namespace identity')
                harness_id = e.elf_id(package / 'frozen' / variant / 'preview-benchmark')
                helper_id = e.elf_id(package / 'frozen' / variant / 'runtime/usr/libexec/holonight-images-helper')
                h.require(any(m['pid'] == raw['root']['pid'] and m['build_id'] == harness_id for m in account['mappings']) and
                          any(m['pid'] != raw['root']['pid'] and m['namespace'] != raw['root']['namespace'] and
                              m['build_id'] == helper_id for m in account['mappings']), 'missing captured harness/helper identity')

                source_inputs = h.read(package / 'inputs.json')['variants'][variant]
                source_outer = h.read(output / 'staged-outer.json')
                source_request = h.read(output / 'stage-request.json')
                expected_runtime = '/run/holonight-identity-' + hashlib.sha256(str(output).encode()).hexdigest()[:20]
                h.require(source_request['runtime'] == expected_runtime, 'staged source root binding')
                source_prefix = 'A-fixed/'
                if variant == 'C':
                    selected = bytes.fromhex(source_outer['C/current']['bytes']).decode().strip()
                    h.require(len(selected) == 64 and all(c in '0123456789abcdef' for c in selected),
                              'staged source generation identity')
                    source_prefix = 'C/generations/' + selected + '/'
                source_staging = dict(runtime=expected_runtime, prefix=source_prefix, inventory=source_outer)
                for mapping in account['mappings']:
                    check_mapping_source(mapping, raw['root'], package / 'frozen' / variant / 'runtime',
                                         source_inputs['payload'], source_staging)

                if schedule[i]['warmup']:
                    for number, (_, identity) in enumerate(sorted(ledger.items())):
                        elf = output / f'{i:03}' / f'elf-{number:03}'
                        h.require(e.ordinary(elf) == {k: identity[k] for k in ('size', 'sha256')} and
                                  e.elf_id(elf) == identity['build_id'], 'frozen dependency ELF binding')
                h.require((recording / 'perf.data').stat().st_size > 0 and (recording / 'perf-raw.txt').stat().st_size > 0 and
                          h.read(recording / 'metadata-records.json') == raw['events'], 'raw capture/export binding')
                h.require(h.read(recording / 'recorder-ack.json')['ns'] == raw['ack_ns'] and
                          h.read(recording / 'release.json')['ns'] == raw['release_ns'], 'raw acknowledgement binding')
        else:
            h.require(not raw.get('events') and not raw.get('raw_recording') and observation['identities'] is None, 'uncaptured loading claim')
    h.require(ledgers == h.read(output / 'ledgers.json') and checked_report(observations) == h.read(output / 'report.json'), 'ledger/report claims or population mixing')
    return dict(status='passed', outcome=result['status'], synthetic=result['synthetic'],
                evidence_seal=h.digest(output / 'seal.json'), evidence=str(output), imports_runner=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--execution', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    h.require(args.output.absolute() == args.output.resolve() and not args.output.exists() and
              not args.output.absolute().is_relative_to(args.evidence.absolute()), 'verification destination collision/overlap')
    try:
        result = (verify_execution if args.execution else verify)(args.evidence.absolute())
    except (OSError, ValueError, KeyError, TypeError, IndexError, struct.error) as error:
        result = dict(status='blocked', failure=str(error))
    with args.output.open('x') as stream:
        stream.write(h.json.dumps(result, indent=2) + '\n')
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed' or result.get('outcome') == 'blocked')
