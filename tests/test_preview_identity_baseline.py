"""Offline protocol regressions. Every real process execution API is disabled."""
import copy
import importlib.util
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


p = module('test_identity_preparation', 'prepare-preview-identity-baseline.py')
r = module('test_identity_runner', 'run-preview-identity-baseline.py')
v = module('test_identity_verifier', 'verify-preview-identity-baseline.py')
h = p.h


def capture():
    root = dict(pid=10, start=100, namespace='desktop-namespace')
    child = dict(pid=20, start=200, namespace='desktop-namespace')
    sandbox = dict(child, namespace='sandbox-namespace')
    def mapping(process, scope, digest):
        return dict(kind='mapping', path='/usr/lib/lib.so', scope=scope, build_id='ab'*20,
                    size=4, sha256=digest*64, **process)
    events = [dict(kind='exec', **root), mapping(root, 'desktop', 'a'),
              dict(kind='fork', ppid=10, **child), dict(kind='namespace', **sandbox),
              dict(kind='exec', **sandbox), mapping(sandbox, 'sandbox', 'b'),
              dict(kind='exit', **sandbox), dict(kind='exit', **root)]
    return root, events


class SyntheticBackend:
    synthetic = True

    def __init__(self, mutate=None, fail=None):
        self.calls = []
        self.mutate = mutate
        self.fail = fail
        self.cleaned = False
        self.current = None

    def capability(self, package, rehearsal=False):
        if self.fail == 'capability':
            raise ValueError('unsupported capability')

    def stage(self, package, output):
        if self.fail == 'stage':
            raise ValueError('staging collision')

    def inventory(self):
        return {'outer': 'selectors, owners, modes and manifest bytes'}

    def invoke(self, entry, directory):
        self.current = entry
        self.calls.append(entry)
        root, events = capture()
        value = dict(exit=0, timeout=False, elapsed_seconds=1, cleanup=True, cleanup_seconds=1,
                     harness=dict(samples=[dict(success=True, setup_success=True, correct_pixels=True,
                         correct_metadata=True, first_ms=10 + (entry['variant'] == 'C'), final_ms=20)]),
                     acknowledged=entry['captured'], ack_ns=1, release_ns=2, capture_loss=False,
                     raw_recording=entry['captured'], root=root, events=events if entry['captured'] else [])
        if self.mutate:
            self.mutate(entry, value)
        return value

    def freeze_dependencies(self, variant, ledger, directory):
        pass

    def recheck_dependencies(self, ledgers):
        if self.fail == 'drift' and self.calls:
            raise ValueError('dependency drift')

    def cleanup(self, staged):
        self.cleaned = True
        if self.fail == 'cleanup':
            raise ValueError('cleanup preserved modified tree')


class IdentityBaselineTests(unittest.TestCase):
    def native_backend(self):
        backend = r.NativeBackend(self.package, None, Path('/var/lib/holonight-identity-recorder-test/perf'))
        backend.output = self.root
        backend.request = self.root / 'request.json'
        return backend

    def mapping_candidates(self):
        # Equal GNU build IDs need not mean byte-identical ELF files.
        elf = bytearray(120)
        elf[:6] = b'\x7fELF\x02\x01'
        struct.pack_into('<Q', elf, 32, 64)
        struct.pack_into('<HH', elf, 54, 56, 1)
        note = struct.pack('<III', 4, 20, 3) + b'GNU\0' + bytes.fromhex('ab'*20)
        struct.pack_into('<IIQQQQ', elf, 64, 4, 0, 120, 0, 0, len(note))
        desktop = self.root / 'desktop-lib.so'
        desktop.write_bytes(elf + note + b'desktop')
        package = self.root / 'mapping-package'
        frozen = package / 'frozen/A-fixed/runtime'
        source = frozen / 'usr/lib/test.so'
        source.parent.mkdir(parents=True)
        source.write_bytes(elf + note + b'sandbox')
        payload = {'usr/lib/test.so': p.e.ordinary(source)}
        h.write(package / 'inputs.json', dict(variants={'A-fixed': dict(payload=payload)}))
        namespace = b''.join(struct.pack('<QQ', 7, i + 1) for i in range(7))
        sandbox = bytearray(namespace)
        struct.pack_into('<Q', sandbox, 5 * 16 + 8, 999)
        backend = r.NativeBackend(package, None)
        backend.root_namespace = namespace.hex()
        return backend, desktop, source, payload, namespace.hex(), sandbox.hex()

    def test_same_build_id_different_bytes_are_bound_to_their_namespace(self):
        backend, desktop, sandbox, _, host_ns, sandbox_ns = self.mapping_candidates()
        def filesystem(path):
            return desktop if str(path) == '/usr/lib/test.so' else Path(path)
        with patch.object(r, 'Path', side_effect=filesystem):
            host = backend.resolve('A-fixed', '/usr/lib/test.so', 'ab'*20, host_ns)
            isolated = backend.resolve('A-fixed', '/usr/lib/test.so', 'ab'*20, sandbox_ns)
        self.assertEqual(host, dict(p.e.ordinary(desktop), build_id='ab'*20))
        self.assertEqual(isolated, dict(p.e.ordinary(sandbox), build_id='ab'*20))
        self.assertNotEqual(host['sha256'], isolated['sha256'])
        self.assertEqual(backend.sources['A-fixed', 'desktop:/usr/lib/test.so'][0], desktop)
        self.assertEqual(backend.sources['A-fixed', 'sandbox:/usr/lib/test.so'][0], sandbox)

    def test_independent_verifier_rejects_swapped_namespace_bytes(self):
        backend, desktop, sandbox, payload, host_ns, sandbox_ns = self.mapping_candidates()
        staging = dict(runtime=str(self.root / 'staged'), prefix='A-fixed/', inventory={})
        frozen = backend.package / 'frozen/A-fixed/runtime'
        host = dict(path='/usr/lib/test.so', namespace=host_ns, scope='desktop',
                    build_id='ab'*20, **p.e.ordinary(desktop))
        isolated = dict(path='/usr/lib/test.so', namespace=sandbox_ns, scope='sandbox',
                        build_id='ab'*20, **p.e.ordinary(sandbox))
        with patch.object(v, 'Path', side_effect=lambda path: desktop if str(path) == '/usr/lib/test.so' else Path(path)):
            for record in (host, isolated):
                v.check_mapping_source(record, dict(namespace=host_ns), frozen, payload, staging)
            for record, wrong in ((host, isolated), (isolated, host)):
                with self.assertRaisesRegex(ValueError, 'source ELF identity'):
                    v.check_mapping_source(dict(record, size=wrong['size'], sha256=wrong['sha256']),
                                           dict(namespace=host_ns), frozen, payload, staging)

    def test_resolver_does_not_fallback_across_namespace_sources(self):
        backend, desktop, sandbox, _, host_ns, sandbox_ns = self.mapping_candidates()
        with patch.object(r, 'Path', side_effect=lambda path: desktop if str(path) == '/usr/lib/test.so' else Path(path)):
            desktop.unlink()
            with self.assertRaisesRegex(ValueError, 'desktop mapped build ID'):
                backend.resolve('A-fixed', '/usr/lib/test.so', 'ab'*20, host_ns)
            desktop.write_bytes(sandbox.read_bytes())
            sandbox.unlink()
            with self.assertRaisesRegex(ValueError, 'sandbox mapped build ID'):
                backend.resolve('A-fixed', '/usr/lib/test.so', 'ab'*20, sandbox_ns)

    def test_resolver_rejects_build_id_payload_and_in_scope_source_drift(self):
        backend, desktop, sandbox, _, host_ns, sandbox_ns = self.mapping_candidates()
        with patch.object(r, 'Path', side_effect=lambda path: desktop if str(path) == '/usr/lib/test.so' else Path(path)):
            with self.assertRaisesRegex(ValueError, 'desktop mapped build ID'):
                backend.resolve('A-fixed', '/usr/lib/test.so', 'cd'*20, host_ns)
            backend.resolve('A-fixed', '/usr/lib/test.so', 'ab'*20, host_ns)
            desktop.write_bytes(desktop.read_bytes() + b'changed')
            with self.assertRaisesRegex(ValueError, 'mapping source conflict'):
                backend.resolve('A-fixed', '/usr/lib/test.so', 'ab'*20, host_ns)
            sandbox.write_bytes(sandbox.read_bytes() + b'changed')
            with self.assertRaisesRegex(ValueError, 'payload drift'):
                backend.resolve('A-fixed', '/usr/lib/test.so', 'ab'*20, sandbox_ns)

    def test_sandbox_source_requires_a_changed_mount_namespace_and_listed_path(self):
        backend, _, sandbox, payload, host_ns, sandbox_ns = self.mapping_candidates()
        user_only = bytearray.fromhex(host_ns)
        struct.pack_into('<Q', user_only, 4 * 16 + 8, 999)
        with self.assertRaisesRegex(ValueError, 'mount namespace'):
            backend.resolve('A-fixed', '/usr/lib/test.so', 'ab'*20, user_only.hex())
        with self.assertRaisesRegex(ValueError, 'unlisted sandbox mapping'):
            backend.resolve('A-fixed', '/usr/lib/unlisted.so', 'ab'*20, sandbox_ns)
        record = dict(path='/usr/lib/test.so', namespace=user_only.hex(), scope='sandbox',
                      build_id='ab'*20, **p.e.ordinary(sandbox))
        with self.assertRaisesRegex(ValueError, 'mount namespace'):
            v.check_mapping_source(record, dict(namespace=host_ns), backend.package / 'frozen/A-fixed/runtime',
                                   payload, dict(runtime=str(self.root / 'staged'), prefix='A-fixed/', inventory={}))

    def test_independent_verifier_binds_removed_staging_to_frozen_payload(self):
        backend, _, sandbox, payload, host_ns, _ = self.mapping_candidates()
        relative = 'A-fixed/usr/lib/test.so'
        staging = dict(runtime=str(self.root / 'staged'), prefix='A-fixed/',
                       inventory={relative: dict(kind='file', uid=0, mode=0o644, **p.e.ordinary(sandbox))})
        record = dict(path=staging['runtime'] + '/' + relative, namespace=host_ns, scope='desktop',
                      build_id='ab'*20, **p.e.ordinary(sandbox))
        frozen = backend.package / 'frozen/A-fixed/runtime'
        v.check_mapping_source(record, dict(namespace=host_ns), frozen, payload, staging)
        staging['inventory'][relative]['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'staged source inode'):
            v.check_mapping_source(record, dict(namespace=host_ns), frozen, payload, staging)

    def test_human_wait_is_separate_from_machine_staging_duration(self):
        backend = self.native_backend()
        now = [0]
        commands = []
        def launch(command, **options):
            commands.append(command)
            self.assertNotIn('timeout', options)
            self.assertEqual(options['process_group'], 0)
            self.assertNotIn('start_new_session', options)
            worker = Mock(returncode=0)
            def finish():
                now[0] += (300 if command == ['sudo', '-A', '-v'] else 119) * 10**9
                return None, None
            worker.communicate.side_effect = finish
            return worker
        with patch.object(subprocess, 'Popen', side_effect=launch), patch.object(r.time, 'monotonic_ns', side_effect=lambda: now[0]):
            backend.elevated('stage')
        auth = h.read(self.root / 'stage-authorization.json')
        machine = h.read(self.root / 'stage-execution.json')
        self.assertEqual(auth['wait_seconds'], 300)
        self.assertEqual(machine['elapsed_seconds'], 119)
        self.assertGreaterEqual(machine['started_ns'], auth['completed_ns'])
        self.assertEqual(commands[1][:2], ['sudo', '-n'])
        self.assertTrue(machine['worker_reaped'])

    def test_authorization_failure_never_launches_staging(self):
        backend = self.native_backend()
        worker = Mock(returncode=1)
        worker.communicate.return_value = (None, None)
        with patch.object(subprocess, 'Popen', return_value=worker) as launch:
            with self.assertRaises(subprocess.CalledProcessError):
                backend.elevated('stage')
        self.assertEqual(launch.call_count, 1)
        self.assertFalse((self.root / 'stage-execution.json').exists())
        self.assertEqual(h.read(self.root / 'stage-authorization.json')['exit'], 1)

    def test_cancelled_wait_joins_worker_before_reporting_cancellation(self):
        backend = self.native_backend()
        auth = Mock(returncode=0)
        auth.communicate.return_value = (None, None)
        worker = Mock(returncode=0)
        worker.communicate.side_effect = [KeyboardInterrupt, KeyboardInterrupt, (None, None)]
        with patch.object(subprocess, 'Popen', side_effect=[auth, worker]):
            with self.assertRaisesRegex(InterruptedError, 'after worker completion'):
                backend.elevated('stage')
        evidence = h.read(self.root / 'stage-execution.json')
        self.assertTrue(evidence['worker_reaped'])
        self.assertTrue(evidence['interrupted'])
        self.assertEqual(backend.completed_actions['stage'], 0)

    def test_workload_authorization_precedes_timed_process(self):
        backend = self.native_backend()
        backend.runtime = self.root / 'runtime'
        backend.cpu = Mock()
        auth = Mock(returncode=0)
        auth.communicate.return_value = (None, None)
        def workload(*args, **kwargs):
            self.assertEqual(h.read(self.root / 'workload-authorization.json')['exit'], 0)
            raise ValueError('timed workload boundary reached')
        backend.cpu.workload.side_effect = workload
        with patch.object(subprocess, 'Popen', return_value=auth), patch.object(backend, 'isolation'):
            with self.assertRaisesRegex(ValueError, 'timed workload boundary reached'):
                backend.invoke(dict(variant='A-fixed', captured=True), self.root)

    def test_timed_recorder_read_cannot_show_askpass(self):
        backend = self.native_backend()
        worker = Mock(returncode=0)
        worker.communicate.return_value = ('{"pid": 777}', '')
        with patch.object(subprocess, 'Popen', return_value=worker) as launch:
            self.assertEqual(backend.recorder_identity(os.getpid()), dict(pid=777))
        self.assertEqual(launch.call_args.args[0][:2], ['sudo', '-n'])
        self.assertNotIn('timeout', launch.call_args.kwargs)

    def test_independent_verifier_excludes_human_wait_and_requires_completed_workers(self):
        auth = dict(argv=['sudo', '-A', '-v'], exit=0, started_ns=0, completed_ns=300_000_000_000,
                    wait_seconds=300, worker_reaped=True, interrupted=False)
        v.check_authorization(auth, 300_000_000_001)
        with self.assertRaisesRegex(ValueError, 'timing boundary'):
            v.check_authorization(auth, 299_000_000_000)
        h.write(self.root / 'stage-authorization.json', auth)
        machine = dict(argv=['sudo', '-n', 'worker'], exit=0, started_ns=300_000_000_000,
                       completed_ns=600_000_000_000, elapsed_seconds=300, worker_reaped=True, interrupted=False)
        worker = dict(started_ns=301_000_000_000, verified_ns=500_000_000_000,
                      completed_ns=599_000_000_000, verification_seconds=199, operation_seconds=99)
        h.write(self.root / 'stage-execution.json', machine)
        h.write(self.root / 'stage-worker.json', worker)
        v.check_elevated_phase(self.root, 'stage')  # Machine work is not capped at 120 either.
        h.write(self.root / 'stage-execution.json', dict(machine, worker_reaped=False))
        with self.assertRaisesRegex(ValueError, 'worker completion'):
            v.check_elevated_phase(self.root, 'stage')

    def test_capability_recorder_rejects_unprotected_location(self):
        with self.assertRaisesRegex(ValueError, 'unsafe capability recorder path'):
            r.recorder_access(Path('/tmp/perf'))

    def test_recorder_identity_reader_rejects_unprivileged_call(self):
        with patch.object(os, 'geteuid', return_value=1000):
            with self.assertRaisesRegex(ValueError, 'scoped elevation'):
                r.recorder_snapshot(123, '100', Path('/tmp/perf'))

    def test_independent_recorder_check_requires_only_perfmon_and_matching_namespaces(self):
        access = dict(path='/var/lib/holonight-identity-recorder-test/perf', sha256='a'*64,
                      capability='cap_perfmon=ep', uid=0, gid=1000, mode=0o750)
        identity = dict(status='Uid:\t1000 1000 1000 1000\nCapPrm:\t4000000000\nCapEff:\t4000000000\n',
                        namespaces={'mnt': 'mnt:[1]'})
        gate = dict(identity=dict(namespaces={'mnt': 'mnt:[1]'}))
        v.check_recorder_access(access, identity, gate, 'a'*64)
        for bad in (dict(identity, status=identity['status'].replace('4000000000', '4000000001')),
                    dict(identity, namespaces={'mnt': 'mnt:[2]'})):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                v.check_recorder_access(access, bad, gate, 'a'*64)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='identity-synthetic-', dir=ROOT / 'build')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('Popen', 'run', 'check_output', 'call', 'check_call'):
            self.enterContext(patch.object(subprocess, name, side_effect=AssertionError('real process forbidden')))
        for name in ('system', 'execv', 'execve', 'execvpe', 'fork'):
            self.enterContext(patch.object(os, name, side_effect=AssertionError('real process forbidden')))
        source = self.root / 'source'
        source.mkdir()
        variants = {}
        files = {}
        for variant in ('A-fixed', 'C'):
            base = source / variant
            (base / 'runtime/usr/lib').mkdir(parents=True)
            (base / 'preview-benchmark').write_bytes(variant.encode())
            (base / 'runtime/usr/lib/lib.so').write_bytes(b'ABCD')
            row = dict(path='usr/lib/lib.so', size=4, sha256=h.digest(base / 'runtime/usr/lib/lib.so'))
            h.write(base / 'runtime/manifest.json', dict(version=1, files=[row]))
            inventory = h.inventory(base / 'runtime')
            variants[variant] = dict(harness=dict(path=str(base / 'preview-benchmark'), **p.e.ordinary(base / 'preview-benchmark')),
                runtime=str(base / 'runtime'), inventory=inventory, payload={'usr/lib/lib.so': {k: row[k] for k in ('size', 'sha256')}})
            files.update({str(base / 'runtime' / k): digest for k, digest in inventory.items()})
            files[str(base / 'preview-benchmark')] = h.digest(base / 'preview-benchmark')
        fixture = source / '3200x2400.png'
        fixture.write_bytes(b'fixture')
        files[str(fixture)] = h.digest(fixture)
        self.inputs = dict(inventories={}, files=files, variants=variants,
                           fixture=dict(path=str(fixture), **p.e.ordinary(fixture)), audit_seal=p.e.AUDIT_SEAL)
        # The retained filesystem is an external boundary. All package validation,
        # file copies, inventories, seals, schedule and reporting run unchanged.
        tools = {str(ROOT / 'scripts' / n): h.digest(ROOT / 'scripts' / n) for n in (*p.e.TOOLS, *p.e.INSTALLER)}
        for boundary in (p.e, r.e, v.e):
            self.enterContext(patch.object(boundary, 'retained', return_value=self.inputs))
            self.enterContext(patch.object(boundary, 'snapshots', return_value=tools))
        self.package = self.root / 'prepared'
        self.assertEqual(p.prepare(self.package)['status'], 'prepared')
        # The runner loads a separate verifier module. Its boundary still uses the
        # same real filesystem fixture, without importing runner implementations.
        self.enterContext(patch.object(r, 'load', side_effect=lambda name, filename: v if filename == 'verify-preview-identity-baseline.py' else
                                      (_ for _ in ()).throw(AssertionError('execution module forbidden'))))

    def execute(self, backend):
        output = self.root / 'execution'
        result = r.execute(self.package, output, backend)
        return output, result

    def test_prepared_package_has_zero_execution_and_independent_verification(self):
        self.assertEqual(v.verify(self.package)['outcome'], 'prepared')
        self.assertNotIn('subprocess', p.__dict__)
        self.assertNotIn('runner', v.__dict__)
        self.assertEqual(h.read(self.package / 'assessment.json')['workloads'], 0)

    def test_schedule_has_four_excluded_warmups_and_100_count_one_processes(self):
        rows = p.schedule()
        self.assertEqual(rows, v.expected_schedule())
        self.assertEqual(len(rows), 104)
        self.assertEqual(sum(x['warmup'] for x in rows), 4)
        for variant in ('A-fixed', 'C'):
            for captured in (False, True):
                selected = [x for x in rows if (x['variant'], x['captured']) == (variant, captured)]
                self.assertEqual(len(selected), 26)
                self.assertEqual([sum(x['block'] == b for x in selected) for b in range(5)], [5]*5)
        self.assertEqual([rows[i]['variant'] for i in (24, 29, 34, 39)], ['A-fixed', 'C', 'C', 'A-fixed'])

    def test_full_synthetic_execution_verifies_without_real_processes(self):
        backend = SyntheticBackend()
        output, result = self.execute(backend)
        self.assertEqual(result['status'], 'synthetic-complete')
        self.assertEqual(v.verify_execution(output)['outcome'], 'synthetic-complete')
        self.assertEqual(len(backend.calls), 104)
        self.assertTrue(backend.cleaned)
        report = h.read(output / 'report.json')
        self.assertEqual(len(report['signed_blocks']), 20)
        self.assertEqual(report['populations']['C/captured']['first_ms']['count'], 25)
        self.assertEqual(report['signed_blocks'][0]['C_minus_A_fixed_median'], 1)

    def test_unsupported_capability_stops_before_staging_or_observations(self):
        output, result = self.execute(SyntheticBackend(fail='capability'))
        self.assertEqual(result['attempted'], 0)
        self.assertEqual(len(result['unexecuted']), 104)
        self.assertEqual(v.verify_execution(output)['outcome'], 'blocked')

    def test_first_failure_stops_and_seals_partial_evidence(self):
        def corrupt(entry, value):
            if entry['invocation'] == 6:
                value['harness']['samples'][0]['correct_pixels'] = False
        backend = SyntheticBackend(corrupt)
        output, result = self.execute(backend)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['attempted'], 7)
        self.assertEqual(result['accepted_observations'], 6)
        self.assertEqual(len(result['unexecuted']), 97)
        self.assertTrue(backend.cleaned)
        self.assertEqual(v.verify_execution(output)['outcome'], 'blocked')
        h.sealed(output)

    def test_ack_deadline_loss_correctness_and_population_failures(self):
        failures = [lambda d: d.update(ack_ns=3), lambda d: d.update(capture_loss=True),
                    lambda d: d.update(raw_recording=False), lambda d: d.update(elapsed_seconds=31),
                    lambda d: d.update(timeout=True), lambda d: d.update(cleanup_seconds=6),
                    lambda d: d.update(cleanup=False), lambda d: d.update(exit=1),
                    lambda d: d['harness']['samples'][0].update(correct_metadata=False)]
        for i, mutation in enumerate(failures):
            with self.subTest(failure=i):
                backend = SyntheticBackend(lambda entry, value: mutation(value) if entry['captured'] else None)
                output = self.root / f'failure-{i}'
                result = r.execute(self.package, output, backend)
                self.assertEqual(result['status'], 'blocked')
                self.assertEqual(len(backend.calls), 2)
                self.assertTrue(backend.cleaned)

    def test_uncaptured_cannot_claim_mappings(self):
        backend = SyntheticBackend(lambda entry, value: value.update(events=capture()[1]))
        _, result = self.execute(backend)
        self.assertIn('population mixing', result['failure'])
        self.assertEqual(len(backend.calls), 1)

    def test_cleanup_failure_blocks_complete_synthetic_run(self):
        output, result = self.execute(SyntheticBackend(fail='cleanup'))
        self.assertEqual(result['status'], 'blocked')
        self.assertFalse(result['cleanup_verified'])
        self.assertEqual(v.verify_execution(output)['outcome'], 'blocked')

    def test_dependency_drift_stops_without_retry(self):
        backend = SyntheticBackend(fail='drift')
        _, result = self.execute(backend)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(len(backend.calls), 1)

    def test_new_measured_dependency_blocks(self):
        def corrupt(entry, value):
            if not entry['warmup'] and entry['captured']:
                value['events'][1]['path'] = '/unexpected.so'
        _, result = self.execute(SyntheticBackend(corrupt))
        self.assertIn('unexpected measured', result['failure'])

    def test_dependency_same_size_different_bytes_blocks(self):
        def corrupt(entry, value):
            if not entry['warmup'] and entry['captured']:
                value['events'][1]['sha256'] = 'c'*64
        _, result = self.execute(SyntheticBackend(corrupt))
        self.assertIn('dependency identity drift', result['failure'])

    def test_process_reuse_and_descendant_namespace_attribution(self):
        root, events = capture()
        extra = [dict(kind='fork', pid=20, ppid=10, start=300, namespace=root['namespace']),
                 dict(kind='exit', pid=20, start=300, namespace=root['namespace'])]
        events[-1:-1] = extra
        account = r.identities(events, root)
        self.assertEqual(account, v.check_events(events, root))
        self.assertEqual(len(account['lifetimes']), 3)
        self.assertEqual(len(r.ledger_of(account)), 2)

    def test_fork_inherits_exec_identity_before_child_exec(self):
        root, events = capture()
        del events[4]  # A child can mmap inherited code without executing again.
        account = r.identities(events, root)
        self.assertEqual(account, v.check_events(events, root))
        self.assertEqual(account['mappings'][1]['pid'], 20)

    def test_unavailable_reused_ambiguous_namespace_and_missing_buildid(self):
        for mutate in (lambda events: events[5].update(start=999), lambda events: events[5].update(namespace='other'),
                       lambda events: events[5].update(scope='desktop'),
                       lambda events: events[5].update(build_id=None), lambda events: events[2].update(ppid=999),
                       lambda events: events[2].update(pid=10), lambda events: events.pop(),
                       lambda events: events[5].update(kind='lost')):
            root, events = capture(); mutate(events)
            with self.assertRaises((ValueError, KeyError)):
                r.identities(events, root)
            with self.assertRaises((ValueError, KeyError)):
                v.check_events(events, root)

    def test_conflicting_mapping_bytes_and_anonymous_exclusion(self):
        root, events = capture()
        anonymous = dict(events[1], path='[anon]', sha256=None, build_id=None)
        events.insert(2, anonymous)
        account = r.identities(events, root)
        self.assertEqual(len(account['exclusions']), 1)
        self.assertEqual(account, v.check_events(events, root))
        events.insert(2, dict(events[1], sha256='e'*64))
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            r.ledger_of(r.identities(events, root))

    def test_protocol_and_population_tampering_rejected_after_reseal(self):
        data = h.read(self.package / 'protocol.json')
        data['schedule'][0]['warmup'] = False
        h.write(self.package / 'protocol.json', data)
        self.reseal(self.package)
        with self.assertRaisesRegex(ValueError, 'protocol'):
            v.verify(self.package)

    def test_resealed_preparation_report_cannot_claim_real_execution(self):
        (self.package / 'REPORT.md').write_text('All qualification gates passed after real observations.\n')
        self.reseal(self.package)
        with self.assertRaisesRegex(ValueError, 'report claims'):
            v.verify(self.package)

    def test_resealed_harness_substitution_and_extra_payload_rejected(self):
        (self.package / 'frozen/C/preview-benchmark').write_bytes(b'X')
        self.reseal(self.package)
        with self.assertRaisesRegex(ValueError, 'harness'):
            v.verify(self.package)

    def test_installer_or_tool_drift_rejected(self):
        tool = self.package / 'tools/manage-images-generations.py'
        tool.write_text(tool.read_text() + '\n')
        self.reseal(self.package)
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            v.verify(self.package)

    def test_nested_membership_size_digest_and_outer_scope(self):
        root = self.root / 'source/C/runtime'
        expected = self.inputs['variants']['C']['inventory']
        self.assertEqual(len(p.e.payload(root, expected)), 1)
        (root / 'usr/lib/lib.so').write_bytes(b'DCBA')
        with self.assertRaises(ValueError):
            p.e.payload(root, expected)
        (root / 'usr/lib/lib.so').write_bytes(b'ABCD')
        (root / 'extra').write_bytes(b'x')
        with self.assertRaises(ValueError):
            p.e.payload(root, expected)
        with self.assertRaises(ValueError):
            p.e.payload(root, {'generations/id/usr/lib/lib.so': 'a'*64})

    def test_collisions_overlap_and_symlink_escape(self):
        with self.assertRaisesRegex(ValueError, 'collision'):
            p.prepare(self.package)
        with self.assertRaisesRegex(ValueError, 'overlaps'):
            h.fresh(self.root / 'inside', [self.root])
        (self.root / 'link').symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'destination'):
            p.prepare(self.root / 'link/escaped')

    def test_blocked_preparation_is_sealed_and_retained(self):
        with patch.object(p.e, 'retained', side_effect=ValueError('missing historical identity')):
            out = self.root / 'blocked'
            self.assertEqual(p.prepare(out)['status'], 'blocked')
        self.assertEqual(v.verify(out)['outcome'], 'blocked')
        h.sealed(out)

    def test_resealed_reporting_claim_or_mixed_population_rejected(self):
        output, _ = self.execute(SyntheticBackend())
        report = h.read(output / 'report.json')
        report['overhead_correction'] = True
        h.write(output / 'report.json', report)
        self.reseal(output)
        with self.assertRaisesRegex(ValueError, 'report'):
            v.verify_execution(output)

    def test_recorder_options_have_no_sampling_or_cache_writes(self):
        argv = r.record_argv(Path('perf.data'), 10, 3, 4)
        for option in ('dummy:u', '--no-samples', '--buildid-mmap', '--namespaces', '--no-buildid-cache'):
            self.assertIn(option, argv)
        for option in ('--call-graph', '--freq', '--all-cpus', '--no-inherit'):
            self.assertNotIn(option, argv)

    def test_truncated_or_loss_perf_data_rejected(self):
        raw = self.root / 'perf.data'
        for data in (b'', b'PERFILE2' + bytes(96)):
            raw.write_bytes(data)
            with self.assertRaises(ValueError):
                r.decode_perf(raw, capture()[0], lambda *args: {})

    def test_nonfinite_or_wrong_count_correctness_rejected(self):
        for rows in ([], [dict(first_ms=float('nan'))], [{}, {}]):
            with self.assertRaises(ValueError):
                r.valid_sample(dict(samples=rows))

    def test_capability_rehearsal_is_a_separate_excluded_population(self):
        output = self.root / 'rehearsal'
        result = r.execute(self.package, output, SyntheticBackend(), rehearsal=True)
        self.assertEqual(result['status'], 'synthetic-rehearsed')
        self.assertEqual(result['attempted'], 4)
        self.assertEqual(v.verify_execution(output)['outcome'], 'synthetic-rehearsed')
        self.assertTrue(all(cell['first_ms'] is None for cell in h.read(output / 'report.json')['populations'].values()))

    def test_outer_stage_drift_stops_before_next_invocation(self):
        class Drift(SyntheticBackend):
            def inventory(self):
                return {'current': 'changed' if self.calls else 'original'}
        output, result = self.execute(Drift())
        self.assertEqual(result['attempted'], 1)
        self.assertIn('outer identity drift', result['failure'])
        h.sealed(output)

    def test_source_drift_during_preparation_retains_blocked_package(self):
        source = Path(self.inputs['variants']['C']['harness']['path'])
        source.write_bytes(b'changed')
        output = self.root / 'input-drift'
        result = p.prepare(output)
        self.assertEqual(result['status'], 'blocked')
        self.assertIn('drift', result['failure'])
        h.sealed(output)

    def test_nested_manifest_sizes_and_duplicates_are_checked(self):
        root = self.root / 'source/C/runtime'
        manifest = h.read(root / 'manifest.json')
        for rows in ([dict(manifest['files'][0], size=5)], manifest['files'] * 2, []):
            h.write(root / 'manifest.json', dict(version=1, files=rows))
            with self.assertRaises(ValueError):
                p.e.payload(root, h.inventory(root))

    def test_staging_tree_keeps_modes_owners_selectors_and_manifest_bytes(self):
        base = self.root / 'outer'
        base.mkdir()
        (base / 'current').write_text('generation-id\n')
        (base / 'manifest.json').write_text('{}')
        first = p.e.tree(base)
        self.assertEqual(first['manifest.json']['bytes'], b'{}'.hex())
        self.assertEqual(first['current']['uid'], os.getuid())
        (base / 'current').chmod(0o600)
        self.assertNotEqual(first, p.e.tree(base))
        (base / 'escape').symlink_to(self.root / 'source/C')
        with self.assertRaisesRegex(ValueError, 'symlink escape'):
            p.e.tree(base)

    def test_real_perf_binary_fixture_has_independent_raw_attribution(self):
        root = dict(pid=10, start=100, namespace='desktop')
        bid = bytes.fromhex('ab'*20)
        def record(kind, body, misc=0):
            body += struct.pack('<IIQ', 10, 10, 1000)
            return struct.pack('<IHH', kind, misc, 8 + len(body)) + body
        def execution(pid):
            return record(3, struct.pack('<II', pid, pid) + b'harness\0', 1 << 13)
        def mapping(pid):
            body = struct.pack('<IIQQQ', pid, pid, 4096, 4096, 0)
            body += bytes([20, 0, 0, 0]) + bid + struct.pack('<II', 5, 2) + b'/usr/lib/lib.so\0'
            return record(10, body, 1 << 14)
        ns = struct.pack('<QQ', 1, 2) * 7
        chunks = [execution(10), mapping(10), record(7, struct.pack('<IIIIQ', 20, 10, 20, 10, 200)),
                  record(16, struct.pack('<IIQ', 20, 20, 7) + ns), execution(20), mapping(20),
                  record(4, struct.pack('<IIIIQ', 20, 10, 20, 10, 300)),
                  record(4, struct.pack('<IIIIQ', 10, 0, 10, 0, 400))]
        body = b''.join(chunks)
        header, attr = bytearray(104), bytearray(144)
        header[:8] = b'PERFILE2'
        struct.pack_into('<QQQQQ', header, 16, 144, 104, 144, 248, len(body))
        struct.pack_into('<IIQQQ', attr, 0, 1, 128, 9, 0, 263)
        struct.pack_into('<Q', attr, 40, sum(1 << bit for bit in (1, 5, 8, 9, 13, 18, 23, 24, 25, 28, 34)))
        struct.pack_into('<i', attr, 92, 1)
        raw = self.root / 'perf-binary.data'
        raw.write_bytes(header + attr + body)
        events = r.decode_perf(raw, root, lambda name, buildid, namespace:
                               dict(size=4, sha256=('a' if namespace == 'desktop' else 'b')*64, build_id=buildid))
        self.assertEqual(r.identities(events, root), v.check_events(events, root))
        v.check_raw_perf(raw, root, events)
        without_exec = b''.join(chunk for i, chunk in enumerate(chunks) if i != 4)
        alternate_header = bytearray(header)
        struct.pack_into('<Q', alternate_header, 48, len(without_exec))
        raw.write_bytes(alternate_header + attr + without_exec)
        inherited = r.decode_perf(raw, root, lambda name, buildid, namespace:
                                  dict(size=4, sha256='a'*64, build_id=buildid))
        v.check_raw_perf(raw, root, inherited)
        self.assertEqual(r.identities(inherited, root), v.check_events(inherited, root))
        raw.write_bytes(header + attr + body)
        altered = copy.deepcopy(events); altered[5]['namespace'] = 'wrong'
        with self.assertRaises(ValueError):
            v.check_raw_perf(raw, root, altered)
        struct.pack_into('<Q', attr, 8, 0)  # cpu-clock is forbidden.
        raw.write_bytes(header + attr + body)
        with self.assertRaisesRegex(ValueError, 'metadata-only'):
            v.check_raw_perf(raw, root, events)

    def binary_capture(self, chunks, sample_type=263):
        header, attr = bytearray(104), bytearray(160)
        header[:8] = b'PERFILE2'
        body = b''.join(chunks)
        struct.pack_into('<QQ', attr, 144, 264 + len(body), 8)
        struct.pack_into('<QQQQQ', header, 16, 160, 104, 160, 264, len(body))
        struct.pack_into('<IIQQQ', attr, 0, 1, 144, 9, 0, sample_type)
        struct.pack_into('<Q', attr, 40, sum(1 << bit for bit in (1, 5, 8, 9, 13, 18, 23, 24, 25, 28, 34)))
        struct.pack_into('<i', attr, 92, 1)
        path = self.root / 'generated.data'
        path.write_bytes(header + attr + body + struct.pack('<Q', 4605))
        return path

    @staticmethod
    def binary_record(kind, body=b'', misc=0, stamp=None):
        if stamp is not None:
            body += struct.pack('<IIQ', 10, 10, stamp)
        return struct.pack('<IHH', kind, misc, 8 + len(body)) + body

    def lifecycle_records(self):
        record = self.binary_record
        ns = struct.pack('<IIQ', 20, 20, 7) + struct.pack('<QQ', 1, 2) * 7
        return [record(7, struct.pack('<IIIIQ', 10, 0, 10, 0, 100), stamp=0),
                record(3, struct.pack('<II', 10, 10) + b'init\0', stamp=0),
                record(3, struct.pack('<II', 10, 10) + b'root\0', 1 << 13, 10),
                record(7, struct.pack('<IIIIQ', 20, 10, 20, 10, 123), stamp=20),
                record(16, ns, stamp=30),
                record(3, struct.pack('<II', 20, 20) + b'child\0', 1 << 13, 30),
                record(4, struct.pack('<IIIIQ', 20, 10, 20, 10, 456), stamp=40),
                record(4, struct.pack('<IIIIQ', 10, 0, 10, 0, 789), stamp=50),
                record(10, struct.pack('<IIQQQ', 10, 10, 4096, 4096, 0) +
                       bytes([20, 0, 0, 0]) + bytes.fromhex('ab'*20) +
                       struct.pack('<II', 5, 2) + b'/usr/lib/lib.so\0', 1 << 14, 15)]

    def assert_binary_agreement(self, chunks):
        raw = self.binary_capture(chunks)
        root = dict(pid=10, start=100, namespace='desktop')
        events = r.decode_perf(raw, root, lambda name, bid, ns: dict(build_id=bid, size=4, sha256='a'*64))
        v.check_raw_perf(raw, root, events)
        self.assertEqual(r.identities(events, root), v.check_events(events, root))
        return events

    def assert_binary_rejected(self, chunks, sample_type=263):
        root = dict(pid=10, start=100, namespace='desktop')
        valid = self.binary_capture(self.lifecycle_records())
        expected = r.decode_perf(valid, root, lambda name, bid, ns: dict(build_id=bid, size=4, sha256='a'*64))
        raw = self.binary_capture(chunks, sample_type)
        with self.assertRaises(ValueError):
            r.decode_perf(raw, root, lambda *args: {})
        with self.assertRaises(ValueError):
            v.check_raw_perf(raw, root, expected)

    def test_bookkeeping_layouts_and_cpu_buffer_order(self):
        record = self.binary_record
        metadata = [record(68), record(69, struct.pack('<Q', 1) + bytes(32)),
                    record(73, struct.pack('<Q', 1) + bytes(24)),
                    record(74, struct.pack('<HBBHH', 2, 0, 0, 0, 31)),
                    record(79, struct.pack('<QQQQQBB6x', 1, 2, 0, 0, 0, 1, 0)), record(82)]
        lifecycle = self.lifecycle_records()
        expected = self.assert_binary_agreement(lifecycle)
        # Physical buffers interleave; equal-time namespace/exec keep file-offset order.
        shuffled = [lifecycle[i] for i in (7, 3, 0, 1, 4, 5, 6, 2, 8)]
        self.assertEqual(self.assert_binary_agreement(metadata + shuffled), expected)
        self.assertEqual(expected[2]['start'], 123)  # Native fork time, not trailer time 20.
        self.assertEqual([x['kind'] for x in expected], ['exec', 'mapping', 'fork', 'namespace', 'exec', 'exit', 'exit'])
        for item in metadata:
            self.assertEqual(self.assert_binary_agreement([item] + lifecycle), expected)

    def test_bookkeeping_corruptions_and_unknown_variants(self):
        record = self.binary_record
        bad = [record(68, bytes(8)), record(82, bytes(8)), record(69), record(73),
               record(69, struct.pack('<Q', 2) + bytes(32)),
               record(73, struct.pack('<Q', 0) + bytes(24)),
               record(69, struct.pack('<Q', 1) + bytes(48)),
               record(74, bytes(8)), record(74, struct.pack('<HBBHH', 2, 2, 0, 0, 31)),
               record(74, struct.pack('<HBBHH', 2, 0, 1, 0, 31)),
               record(74, struct.pack('<HBBHH', 2, 0, 0, 31, 0)),
               record(74, bytes(16)), record(79, bytes(24)), record(79, bytes(48)),
               record(79, struct.pack('<QQQQQBB6x', 64, 2, 0, 0, 0, 1, 0)),
               record(79, struct.pack('<QQQQQBB6x', 1, 2, 0, 0, 0, 2, 0)),
               record(79, struct.pack('<QQQQQBB6s', 1, 2, 0, 0, 0, 1, 0, b'badpad')),
               record(78), record(80), record(999), b'\x00', struct.pack('<IHH', 68, 0, 100)]
        for item in bad:
            with self.subTest(item=item.hex()):
                self.assert_binary_rejected([item] + self.lifecycle_records())

    def test_cpu_event_update_is_bound_to_frozen_event(self):
        record = self.binary_record
        cpus = struct.pack('<HBBHH', 2, 0, 0, 0, 31)
        update = record(78, struct.pack('<QQ', 3, 4605) + cpus)
        expected = self.assert_binary_agreement(self.lifecycle_records())
        self.assertEqual(self.assert_binary_agreement([update] + self.lifecycle_records()), expected)
        for payload in (struct.pack('<QQ', 2, 4605) + cpus,
                        struct.pack('<QQ', 3, 9999) + cpus,
                        struct.pack('<QQ', 3, 4605) + bytes(8),
                        struct.pack('<QQHBBHH', 3, 4605, 2, 0, 1, 0, 31),
                        struct.pack('<QQHBBHH', 3, 4605, 2, 0, 0, 31, 0),
                        struct.pack('<QQ', 3, 4605) + cpus + bytes(8)):
            with self.subTest(payload=payload.hex()):
                self.assert_binary_rejected([record(78, payload)] + self.lifecycle_records())
        for location, size in ((0, 0), (1000000, 8), (264, 7)):
            raw = self.binary_capture([update] + self.lifecycle_records())
            data = bytearray(raw.read_bytes())
            struct.pack_into('<QQ', data, 104 + 144, location, size)
            raw.write_bytes(data)
            root = dict(pid=10, start=100, namespace='desktop')
            with self.assertRaises(ValueError):
                r.decode_perf(raw, root, lambda *args: {})
            with self.assertRaises(ValueError):
                v.check_raw_perf(raw, root, expected)

    def test_timestamp_layout_loss_and_attribution_rejections(self):
        rows = self.lifecycle_records()
        for samples in (0, 6, 7, 263 | (1 << 16)):
            self.assert_binary_rejected(rows, samples)
        no_trailer = self.binary_record(4, struct.pack('<IIIIQ', 10, 0, 10, 0, 789))
        self.assert_binary_rejected(rows[:7] + [no_trailer] + rows[8:])
        for kind in (2, 5, 6, 9, 13):
            self.assert_binary_rejected([self.binary_record(kind)] + rows)
        self.assert_binary_rejected(rows[:3] + rows[4:])  # Parentage cannot be inferred from time.
        raw = self.binary_capture(rows)
        value = bytearray(raw.read_bytes())
        struct.pack_into('<Q', value, 104 + 40, 0)  # Missing sample_id_all and required flags.
        raw.write_bytes(value)
        for reader in (lambda: r.decode_perf(raw, dict(pid=10, start=100, namespace='desktop'), lambda *args: {}),
                       lambda: v.check_raw_perf(raw, dict(pid=10, start=100, namespace='desktop'), [])):
            with self.assertRaises(ValueError):
                reader()

    def test_anonymous_binary_mappings_do_not_require_file_build_ids(self):
        for name in (b'//anon\0', b'[anon]\0'):
            with self.subTest(name=name):
                body = struct.pack('<IIQQQ', 10, 10, 4096, 4096, 0)
                body += bytes(24) + struct.pack('<II', 3, 0) + name
                rows = self.lifecycle_records() + [self.binary_record(10, body, misc=2, stamp=12)]
                events = self.assert_binary_agreement(rows)
                excluded = r.identities(events, dict(pid=10, start=100, namespace='desktop'))['exclusions']
                self.assertEqual(len(excluded), 1)
                self.assertEqual(excluded[0]['record']['path'], name[:-1].decode())
                self.assertNotIn('build_id', excluded[0]['record'])

    def test_file_backed_binary_mapping_still_requires_a_build_id(self):
        body = struct.pack('<IIQQQ', 10, 10, 4096, 4096, 0)
        body += bytes(24) + struct.pack('<II', 3, 0) + b'/usr/lib/test.so\0'
        self.assert_binary_rejected(self.lifecycle_records() + [self.binary_record(10, body, misc=2, stamp=12)])

    def test_elf_build_id_is_read_without_executing_an_elf(self):
        elf = bytearray(120)
        elf[:6] = b'\x7fELF\x02\x01'
        struct.pack_into('<Q', elf, 32, 64)
        struct.pack_into('<HH', elf, 54, 56, 1)
        note = struct.pack('<III', 4, 20, 3) + b'GNU\0' + bytes.fromhex('ab'*20)
        struct.pack_into('<IIQQQQ', elf, 64, 4, 0, 120, 0, 0, len(note))
        path = self.root / 'elf'
        path.write_bytes(elf + note)
        self.assertEqual(p.e.elf_id(path), 'ab'*20)

    def reseal(self, output):
        inventory = h.inventory(output)
        inventory.pop('seal.json', None)
        h.write(output / 'seal.json', inventory)


if __name__ == '__main__':
    unittest.main()
