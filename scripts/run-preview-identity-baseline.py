#!/usr/bin/env python3
"""Future identity-bound baseline execution and reporting. Never run by preparation."""
import argparse
import hashlib
import importlib.util
import math
import os
from pathlib import Path
import shutil
import statistics
import struct
import subprocess
import sys
import time

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('execution_identity_boundary', Path(__file__).with_name('preview-identity-evidence.py'))
e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e)
h = e.h


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record_argv(path, pid, control, ack):
    return ['perf', 'record', '--event', 'dummy:u', '--no-samples', '--buildid-mmap',
            '--namespaces', '--clockid', 'mono', '--no-buildid-cache',
            '--timestamp', '--pid', str(pid), '--delay', '-1', '--control', f'fd:{control},{ack}',
            '--output', str(path)]


def valid_sample(data):
    rows = data.get('samples', [])
    h.require(not data.get('cleanup_failure') and len(rows) == 1, 'correctness/count/cleanup failure')
    row = rows[0]
    h.require(all(row.get(k) is True for k in ('success', 'setup_success', 'correct_pixels', 'correct_metadata')) and
              not row.get('cleanup_failure') and not row.get('harness_timeout'), 'startup correctness failure')
    first, final = row.get('first_ms'), row.get('final_ms')
    h.require(all(type(x) in (int, float) and math.isfinite(x) for x in (first, final)) and
              0 <= first <= final, 'invalid startup timing')
    return row


def identities(events, root):
    """Join by explicit active process lifetimes and namespace tokens, never proximity."""
    active = {root['pid']: dict(root, executed=False)}
    seen = {(root['pid'], root['start'])}
    mapped, excluded = [], []
    exited = set()
    for index, record in enumerate(events):
        kind, pid = record['kind'], record.get('pid')
        h.require(kind not in ('lost', 'sample', 'throttle', 'unknown'), 'capture loss/unsupported records')
        if kind == 'fork':
            parent = active.get(record['ppid'])
            h.require(parent is not None and pid not in active and (pid, record['start']) not in seen,
                      'ambiguous descendant/PID reuse')
            h.require(record['namespace'] == parent['namespace'], 'fork namespace identity conflict')
            active[pid] = dict(pid=pid, start=record['start'], namespace=record['namespace'], executed=parent['executed'])
            seen.add((pid, record['start']))
            continue
        process = active.get(pid)
        h.require(process is not None and record['start'] == process['start'], 'unavailable process lifetime')
        if kind == 'namespace':
            h.require(record['namespace'], 'unavailable namespace identity')
            process['namespace'] = record['namespace']
            continue
        h.require(record['namespace'] == process['namespace'], 'namespace attribution conflict')
        if kind == 'exec':
            process['executed'] = True
        elif kind == 'mapping':
            if record['path'].startswith(('[', '//')) or not record['path'].startswith('/'):
                excluded.append(dict(record=record, reason='anonymous/non-file mapping'))
                continue
            h.require(process['executed'] and record.get('build_id'), 'mapping missing exec/build ID')
            h.require(record.get('scope') == ('desktop' if record['namespace'] == root['namespace'] else 'sandbox'),
                      'missing/conflicting mapping namespace scope')
            h.require(record.get('sha256') and type(record.get('size')) is int and record['size'] > 0,
                      'unavailable mapped ELF bytes')
            mapped.append(dict(record, event_index=index))
        elif kind == 'exit':
            exited.add((pid, process['start']))
            del active[pid]
        else:
            h.require(kind == 'comm', 'unknown metadata record')
    h.require(not active and exited == seen and mapped, 'missing exits/mappings or incomplete capture')
    return dict(mappings=mapped, exclusions=excluded, lifetimes=sorted([list(x) for x in seen]))


def ledger_of(account):
    ledger = {}
    for row in account['mappings']:
        key = row['scope'] + ':' + row['path']
        value = {k: row[k] for k in ('size', 'sha256', 'build_id')}
        h.require(key not in ledger or ledger[key] == value, 'conflicting mapping bytes')
        ledger[key] = value
    return ledger


def distribution(values):
    ordered = sorted(values)
    return dict(count=len(values), median=statistics.median(ordered),
                p95=ordered[math.ceil(.95 * len(ordered)) - 1]) if values else None


def report(observations):
    measured = [row for row in observations if not row['schedule']['warmup']]
    populations = {}
    comparisons = []
    for captured in (False, True):
        for variant in ('A-fixed', 'C'):
            rows = [row for row in measured if row['schedule']['captured'] == captured and
                    row['schedule']['variant'] == variant]
            populations[f'{variant}/{"captured" if captured else "uncaptured"}'] = {
                event: distribution([row['sample'][event] for row in rows]) for event in ('first_ms', 'final_ms')}
        for block in range(5):
            for event in ('first_ms', 'final_ms'):
                values = [[row['sample'][event] for row in measured if row['schedule']['captured'] == captured and
                           row['schedule']['variant'] == variant and row['schedule']['block'] == block]
                          for variant in ('A-fixed', 'C')]
                if all(len(v) == 5 for v in values):
                    comparisons.append(dict(captured=captured, block=block, event=event,
                        C_minus_A_fixed_median=statistics.median(values[1]) - statistics.median(values[0]),
                        C_minus_A_fixed_p95=max(values[1]) - max(values[0])))
    return dict(populations=populations, signed_blocks=comparisons,
                mapping_scope='captured executions only; uncaptured loading identities unavailable',
                qualification='78/80 unchanged', optimization=None, overhead_correction=False,
                historical_timing_transfer=False, qualification_inference=False)


def execute(package, output, backend, rehearsal=False):
    """Backend isolates OS boundaries; synthetic backends never launch a process."""
    verifier = load('identity_preflight_verifier', 'verify-preview-identity-baseline.py')
    verifier.verify(package)
    h.fresh(output, [package, *e.protected_inputs()])
    protocol = h.read(package / 'protocol.json')
    schedule = protocol['schedule'][:4] if rehearsal else protocol['schedule']
    observations, ledgers = [], {}
    result = dict(status='blocked', synthetic=backend.synthetic, mode='capability-rehearsal' if rehearsal else 'baseline',
                  attempted=0, unexecuted=schedule)
    staged = False
    try:
        backend.capability(package, rehearsal=rehearsal)
        backend.stage(package, output)
        staged = True
        outer = backend.inventory()
        h.write(output / 'staged-outer.json', outer)
        for entry in schedule:
            # Historical source verification is reused; the executable package,
            # live tools, staged trees and dependency bytes are rechecked here.
            h.sealed(package)
            h.require(h.read(package / 'tools.json') == e.snapshots(), 'execution tool/installer drift')
            h.require(backend.inventory() == outer, 'staged outer identity drift')
            backend.recheck_dependencies(ledgers)
            result['attempted'] += 1
            directory = output / f"{entry['invocation']:03}"
            directory.mkdir(mode=0o700)
            value = backend.invoke(entry, directory)
            h.write(directory / 'raw-result.json', value)
            h.require(value['exit'] == 0 and 0 <= value['elapsed_seconds'] <= 30 and not value['timeout'], 'execution deadline/failure')
            h.require(value['cleanup'] and 0 <= value['cleanup_seconds'] <= 5, 'cleanup deadline/failure')
            sample = valid_sample(value['harness'])
            account = None
            if entry['captured']:
                h.require(value['acknowledged'] and value['ack_ns'] < value['release_ns'], 'capture acknowledgement before release')
                h.require(value['raw_recording'] and not value['capture_loss'], 'missing recording/capture loss')
                account = identities(value['events'], value['root'])
                ledger = ledger_of(account)
                if entry['warmup']:
                    ledgers[entry['variant']] = ledger
                    backend.freeze_dependencies(entry['variant'], ledger, directory)
                else:
                    h.require(ledger.keys() <= ledgers[entry['variant']].keys(), 'unexpected measured dependencies')
                    h.require(all(ledgers[entry['variant']][k] == v for k, v in ledger.items()), 'dependency identity drift')
            else:
                h.require(not value.get('events') and not value.get('raw_recording'), 'uncaptured population mixing')
            backend.recheck_dependencies(ledgers)
            h.sealed(package)
            h.require(backend.inventory() == outer, 'staged outer identity drift')
            row = dict(schedule=entry, sample=sample, identities=account)
            observations.append(row)
            h.write(output / 'observations.json', observations)
        result['status'] = ('synthetic-rehearsed' if backend.synthetic else 'rehearsed') if rehearsal else (
            'synthetic-complete' if backend.synthetic else 'complete')
    except (OSError, ValueError, KeyError, TypeError, IndexError, struct.error, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    finally:
        try:
            # Attempt conservative cleanup even when stage failed partway through.
            backend.cleanup(staged)
            result['cleanup_verified'] = True
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            result.update(status='blocked', cleanup_verified=False, cleanup_failure=str(error))
        result['unexecuted'] = schedule[result['attempted']:]
        result['accepted_observations'] = len(observations)
        h.write(output / 'observations.json', observations)
        h.write(output / 'ledgers.json', ledgers)
        h.write(output / 'report.json', report(observations))
        h.write(output / 'assessment.json', result)
        h.write(output / 'preparation.json', dict(path=str(package), seal=h.digest(package / 'seal.json')))
        h.write(output / 'seal.json', h.inventory(output))
    return result


# Linux perf metadata reader. Decode record order and explicit fork/exit identities;
# do not infer relationships from neighbouring timestamps or resolve old captures.
def decode_perf(path, root, resolve):
    data = path.read_bytes()
    h.require(data[:8] == b'PERFILE2', 'unsupported perf format')
    offset, length = struct.unpack_from('<QQ', data, 40)
    stop = offset + length
    h.require(stop <= len(data), 'truncated perf data')
    active = {root['pid']: dict(root)}
    events = []
    while offset < stop:
        kind, misc, size = struct.unpack_from('<IHH', data, offset)
        h.require(size >= 8 and offset + size <= stop, 'truncated perf record')
        raw = data[offset:offset + size]
        offset += size
        if kind in (2, 5, 6, 9, 13):
            raise ValueError('capture loss/samples/throttling')
        if kind in (7, 4):  # FORK/EXIT carry their own monotonic time.
            pid, ppid, tid, ptid, stamp = struct.unpack_from('<IIIIQ', raw, 8)
            if pid != tid:  # Threads share process mappings, but preserve raw bytes.
                continue
            if kind == 7:
                if pid == root['pid'] and pid in active:
                    continue  # perf's initial synthesized root task
                h.require(ppid in active and pid not in active, 'unavailable parent/PID reuse')
                process = dict(pid=pid, start=stamp, namespace=active[ppid]['namespace'],
                               exec_seen=active[ppid].get('exec_seen', False))
                active[pid] = process
                events.append(dict(kind='fork', ppid=ppid, **{k: process[k] for k in ('pid', 'start', 'namespace')}))
            else:
                h.require(pid in active, 'unavailable exited lifetime')
                process = active.pop(pid)
                events.append(dict(kind='exit', **{k: process[k] for k in ('pid', 'start', 'namespace')}))
        elif kind in (1, 3, 10, 16):
            pid, tid = struct.unpack_from('<II', raw, 8)
            h.require(pid in active, 'unavailable mapping/task lifetime')
            process = active[pid]
            if kind == 16:
                count = struct.unpack_from('<Q', raw, 16)[0]
                h.require(count == 7 and len(raw) >= 24 + count * 16, 'unsupported namespace metadata')
                process['namespace'] = raw[24:24 + count * 16].hex()
                events.append(dict(kind='namespace', **{k: process[k] for k in ('pid', 'start', 'namespace')}))
            elif kind == 3:
                if misc & (1 << 13):
                    events.append(dict(kind='exec', **{k: process[k] for k in ('pid', 'start', 'namespace')}))
                    process['exec_seen'] = True
            elif kind == 10:
                # Ignore the attached gate's pre-exec synthesis, while preserving
                # every byte in perf.data and the raw export.
                if not process.get('exec_seen'):
                    continue
                name = raw[72:].split(b'\0', 1)[0].decode('utf-8', 'strict')
                if name.startswith('/'):
                    h.require(misc & (1 << 14), 'missing mapping build ID')
                    count = raw[40]
                    h.require(0 < count <= 20, 'missing/unsupported mapping build ID')
                    build_id = raw[44:44 + count].hex()
                    identity = resolve(name, build_id, process['namespace'])
                    identity['scope'] = 'desktop' if process['namespace'] == root['namespace'] else 'sandbox'
                else:
                    identity = {}
                events.append(dict(kind='mapping', path=name, **{k: process[k] for k in ('pid', 'start', 'namespace')}, **identity))
            else:
                h.require(not process.get('exec_seen'), 'legacy mmap lacks required build ID')
        elif kind not in (8, 14, 15, 17, 18, 19, 20, 21):
            raise ValueError('unsupported perf metadata type: ' + str(kind))
    return events


class NativeBackend:
    """Ordinary-user recorder/workloads; narrowly scoped protected staging worker."""
    synthetic = False

    def __init__(self, package, rehearsal):
        self.package, self.rehearsal = package, rehearsal
        self.runtime = None
        self.sources = {}
        self.dependencies = {}

    def capability(self, package, rehearsal=False):
        h.require(os.geteuid() != 0, 'ordinary desktop user required; no privileged recorder fallback')
        if not rehearsal:
            h.require(self.rehearsal is not None, 'later authorized capability rehearsal required')
            checked = h.read(self.rehearsal)
            verifier = load('capability_identity_verifier', 'verify-preview-identity-baseline.py')
            source = Path(checked['evidence'])
            h.require(checked == verifier.verify_execution(source) and checked['status'] == 'passed' and
                      checked['outcome'] == 'rehearsed' and not checked['synthetic'], 'unsupported capability rehearsal')
            binding = h.read(source / 'capability.json')
            h.require(binding == dict(preparation_seal=h.digest(package / 'seal.json'),
                      recorder_sha256=h.digest(Path(shutil.which('perf'))), uid=os.getuid(),
                      boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(), host=os.uname().nodename,
                      protocol=h.read(package / 'protocol.json')), 'capability recorder/user/protocol drift')
        # The existing process primitive uses a fresh gated process, attach/enable
        # acknowledgement, a 30-second deadline and shared five-second cleanup.
        self.cpu = load('identity_gated_process', 'run-preview-cpu-profile.py')
        self.cpu.offline_env()

    def stage(self, package, output):
        self.output = output
        h.write(output / 'capability.json', dict(preparation_seal=h.digest(package / 'seal.json'),
                  recorder_sha256=h.digest(Path(shutil.which('perf'))), uid=os.getuid(),
                  boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(), host=os.uname().nodename,
                  protocol=h.read(package / 'protocol.json')))
        name = hashlib.sha256(str(output).encode()).hexdigest()[:20]
        self.runtime = Path('/run') / ('holonight-identity-' + name)
        h.require(not os.path.lexists(self.runtime), 'protected staging collision')
        if self.rehearsal is not None:
            h.write(output / 'capability-verification.json', h.read(self.rehearsal))
        self.request = output / 'stage-request.json'
        h.write(self.request, dict(package=str(package), seal=h.digest(package / 'seal.json'),
                                  runtime=str(self.runtime), execution=str(output)))
        self.elevated('stage')
        self.outer = self.inventory()
        h.write(output / 'cleanup-expected.json', self.outer)

    def elevated(self, action):
        command = ['sudo', '-A', sys.executable, '-B', str(Path(__file__).resolve()), action,
                   '--request', str(self.request)]
        with (self.output / (action + '.log')).open('x') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)

    def inventory(self):
        result = e.tree(self.runtime)
        h.require(all(row['uid'] == 0 and not row['mode'] & 0o022 for row in result.values()), 'unprotected staged inode')
        # Keep nested inventory distinct from outer permissions/selectors/bytes.
        for variant in ('A-fixed', 'C'):
            base = self.runtime / variant
            if variant == 'C':
                generation = (base / 'current').read_text().strip()
                h.require(generation and '/' not in generation and generation not in ('.', '..'), 'invalid generation selector')
                base = base / 'generations' / generation
            expected = h.read(self.package / 'inputs.json')['variants'][variant]['inventory']
            h.require(h.inventory(base) == expected, 'staged nested payload mismatch')
        return result

    def resolve(self, variant, path, build_id, namespace):
        # Namespace-local /usr paths can denote the protected helper payload.
        # Prefer exact build-ID matching; differing candidate bytes are ambiguous.
        candidates = [Path(path)]
        if path.startswith('/usr/'):
            candidates.append(self.package / 'frozen' / variant / 'runtime' / path[1:])
        matches = []
        for candidate in candidates:
            if candidate.is_file() and candidate.read_bytes()[:4] == b'\x7fELF' and e.elf_id(candidate) == build_id:
                matches.append((candidate.resolve(), e.ordinary(candidate.resolve())))
        h.require(matches and len({v['sha256'] for _, v in matches}) == 1, 'unavailable/conflicting mapped identity: ' + path)
        source, identity = matches[0]
        identity = dict(identity, build_id=build_id)
        scope = 'desktop' if namespace == self.root_namespace else 'sandbox'
        key = (variant, scope + ':' + path)
        h.require(key not in self.sources or self.sources[key] == (source, identity), 'mapping source conflict')
        self.sources[key] = (source, identity)
        return dict(identity)

    def isolation(self, directory, deadline=None):
        directory.mkdir(mode=0o700)
        deadline = time.monotonic() + 5 if deadline is None else deadline
        command = ['systemctl', '--user', 'list-units', '--all', '--plain', '--no-legend',
                   '--no-pager', 'holonight-images-*.scope']
        completed = subprocess.run(command, env=self.cpu.offline_env(), capture_output=True, text=True,
                                   timeout=max(.001, deadline - time.monotonic()))
        cgroup = Path(f'/sys/fs/cgroup/user.slice/user-{os.getuid()}.slice/user@{os.getuid()}.service')
        paths = sorted(str(p) for p in cgroup.glob('**/holonight-images-*.scope'))
        h.write(directory / 'scopes.json', dict(argv=command, exit=completed.returncode,
                stdout=completed.stdout, stderr=completed.stderr, cgroups=paths))
        self.cpu.r.residuals(directory)
        h.require(completed.returncode == 0 and not completed.stdout.strip() and not paths and
                  cgroup.is_dir() and time.monotonic() <= deadline, 'scope/process isolation or cleanup deadline')

    def invoke(self, entry, directory):
        variant = entry['variant']
        target = directory / 'harness.json'
        self.isolation(directory / 'before')
        argv = [str(self.package / 'frozen' / variant / 'preview-benchmark'), str(self.runtime / variant),
                str(self.package / 'frozen/3200x2400.png'), 'startup', '1', str(target)]
        previous = Path.cwd()
        try:
            os.chdir(directory)
            process = self.cpu.workload(argv, target, entry['captured'], recorder_command=record_argv)
        finally:
            os.chdir(previous)
        recording = directory / 'harness-recording'
        partial = h.read(recording / 'partial.json')
        self.isolation(directory / 'after', deadline=partial['cleanup_deadline'])
        gate = h.read(recording / 'gate.json')
        # Namespace tokens use the same seven namespaces, in perf's defined order.
        ns = gate['identity']['namespaces']
        names = ('net', 'uts', 'ipc', 'pid', 'user', 'mnt', 'cgroup')
        pairs = b''.join(struct.pack('<QQ', os.stat('/proc/self/ns/' + name).st_dev,
                      int(ns[name].split('[')[1][:-1])) for name in names)
        root = dict(pid=gate['pid'], start=gate['stat'].rsplit(')', 1)[1].split()[19], namespace=pairs.hex())
        release = h.read(recording / 'release.json')
        value = dict(exit=process['exit'], timeout=process['timeout'],
                     elapsed_seconds=(process['stop_ns'] - process['start_ns']) / 1e9,
                     cleanup=partial['cleanup_outcomes']['passed'],
                     cleanup_seconds=max(0, time.monotonic() - (partial['cleanup_deadline'] - 5)),
                     harness=h.read(target), root=root, events=[], raw_recording=False,
                     acknowledged=False, capture_loss=False, release_ns=release['ns'])
        if entry['captured']:
            diagnostics = (recording / 'recorder.stderr').read_text().lower()
            h.require(not any(word in diagnostics for word in ('lost chunks', 'lost samples', 'perf_record_lost', 'error:', 'failed')),
                      'recorder capture loss/error')
            ack = h.read(recording / 'recorder-ack.json')
            value.update(acknowledged=partial['acknowledged'], ack_ns=ack['ns'], raw_recording=True)
            self.root_namespace = root['namespace']
            value['events'] = decode_perf(recording / 'perf.data', root,
                lambda path, bid, namespace: self.resolve(variant, path, bid, namespace))
            harness_id = e.elf_id(self.package / 'frozen' / variant / 'preview-benchmark')
            helper_id = e.elf_id(self.package / 'frozen' / variant / 'runtime/usr/libexec/holonight-images-helper')
            maps = [event for event in value['events'] if event['kind'] == 'mapping']
            h.require(any(m.get('build_id') == harness_id and m['pid'] == root['pid'] for m in maps) and
                      any(m.get('build_id') == helper_id and m['pid'] != root['pid'] and
                          m['namespace'] != root['namespace'] for m in maps), 'missing harness/sandbox helper identity')
            load('raw_identity_verifier', 'verify-preview-identity-baseline.py').check_raw_perf(
                recording / 'perf.data', root, value['events'])
            h.write(recording / 'metadata-records.json', value['events'])
            # Preserve raw event export as well as normalized process/exec/map/exit records.
            with (recording / 'perf-raw.txt').open('x') as stream, (recording / 'export.stderr').open('x') as error:
                subprocess.run(['perf', 'script', '-D', '--no-itrace', '-i', str(recording / 'perf.data')],
                    stdout=stream, stderr=error, env=self.cpu.offline_env(), check=True, timeout=30)
        return value

    def freeze_dependencies(self, variant, ledger, directory):
        for index, (name, identity) in enumerate(sorted(ledger.items())):
            source, actual = self.sources[variant, name]
            h.require(actual == identity, 'dependency copy binding')
            destination = directory / f'elf-{index:03}'
            shutil.copy2(source, destination)
            h.require(e.ordinary(destination) == {k: identity[k] for k in ('size', 'sha256')} and
                      e.elf_id(destination) == identity['build_id'], 'ELF copy drift')
            self.dependencies[variant, name] = (source, identity, destination)
        h.write(directory / 'dependency-paths.json', {name: dict(identity, source=str(self.sources[variant, name][0]))
                                                     for name, identity in ledger.items()})

    def recheck_dependencies(self, ledgers):
        for source, identity, frozen in self.dependencies.values():
            for path in (source, frozen):
                h.require(e.ordinary(path) == {k: identity[k] for k in ('size', 'sha256')} and
                          e.elf_id(path) == identity['build_id'], 'dependency bytes/build ID drift')

    def cleanup(self, staged):
        if self.runtime is None or not self.runtime.exists():
            return
        h.require(staged, 'partial staging retained; cleanup identity unavailable')
        self.isolation(self.output / 'cleanup-isolation')
        h.require(self.inventory() == self.outer, 'modified staging retained')
        self.elevated('cleanup')
        h.require(not self.runtime.exists(), 'staging cleanup incomplete')


def stage_worker(request, cleanup=False):
    h.require(os.geteuid() == 0, 'protected staging requires scoped elevation')
    config = h.read(request)
    package, runtime, output = [Path(config[k]) for k in ('package', 'runtime', 'execution')]
    verifier = load('staging_identity_verifier', 'verify-preview-identity-baseline.py')
    verifier.verify(package)
    h.require(h.digest(package / 'seal.json') == config['seal'], 'staging preparation drift')
    name = hashlib.sha256(str(output).encode()).hexdigest()[:20]
    h.require(runtime == Path('/run') / ('holonight-identity-' + name) and runtime.resolve() == runtime,
              'unsafe staging destination')
    # Load the frozen installer and frozen support module, never a current replacement.
    sys.path.insert(0, str(package / 'tools'))
    spec = importlib.util.spec_from_file_location('identity_frozen_installer', package / 'tools/manage-images-generations.py')
    installer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installer)
    owner = dict(package=str(package), seal=config['seal'], execution=str(output))
    if cleanup:
        h.require(h.read(runtime / 'diagnostic-owner.json') == owner and
                  e.tree(runtime) == h.read(output / 'cleanup-expected.json'), 'cleanup ownership/drift conflict')
        from types import SimpleNamespace
        installer.run(SimpleNamespace(command='remove', runtime=runtime / 'C', helper=package / 'frozen/C/runtime/usr/libexec/holonight-images-helper',
                      source=None, ownership_manifest=None, maintenance_migrate=False))
        installer.remove_tree(runtime)
        return
    h.require(not os.path.lexists(runtime), 'staging collision')
    installer.chain(runtime.parent)
    runtime.mkdir(mode=0o755)
    h.write(runtime / 'diagnostic-owner.json', owner)
    (runtime / 'A-fixed').mkdir(mode=0o755)
    installer.copy_tree(package / 'frozen/A-fixed/runtime', runtime / 'A-fixed')
    from types import SimpleNamespace
    installer.run(SimpleNamespace(command='install', runtime=runtime / 'C', source=package / 'frozen/C/runtime',
                  helper=package / 'frozen/C/runtime/usr/libexec/holonight-images-helper',
                  ownership_manifest=None, maintenance_migrate=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('execute', 'rehearse', 'stage', 'cleanup', 'report'))
    parser.add_argument('--package', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--request', type=Path)
    parser.add_argument('--rehearsal', type=Path)
    parser.add_argument('--authorized-execution', action='store_true')
    args = parser.parse_args()
    if args.action in ('stage', 'cleanup'):
        stage_worker(args.request.absolute(), args.action == 'cleanup')
    elif args.action == 'report':
        h.require(not args.output.exists(), 'report collision')
        h.write(args.output, report(h.read(args.request)))
    else:
        h.require(args.authorized_execution and (args.action == 'rehearse' or args.rehearsal is not None),
                  'later authorized capability rehearsal required before execution')
        print(h.json.dumps(execute(args.package.absolute(), args.output.absolute(),
                                  NativeBackend(args.package.absolute(), args.rehearsal),
                                  rehearsal=args.action == 'rehearse'), indent=2))
