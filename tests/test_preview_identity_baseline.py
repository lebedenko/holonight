"""Offline protocol regressions. Every real process execution API is disabled."""
import copy
import importlib.util
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch

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
        header = bytearray(104)
        header[:8] = b'PERFILE2'
        struct.pack_into('<QQ', header, 40, 104, 8)
        raw.write_bytes(header + struct.pack('<IHH', 2, 0, 8))
        with self.assertRaisesRegex(ValueError, 'capture loss'):
            r.decode_perf(raw, capture()[0], lambda *args: {})
        raw.write_bytes(header)
        with self.assertRaisesRegex(ValueError, 'truncated'):
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
        struct.pack_into('<IIQQQ', attr, 0, 1, 128, 9, 0, 0)
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
