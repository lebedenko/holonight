"""Evidence accounting must not hide failed requests or missing observations."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import zlib


ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


measure = module('measure-preview-experiments')
baselines = module('preview-experiment-baselines')


class EvidenceAccounting(unittest.TestCase):
    def test_failed_requests_remain_in_denominator(self):
        records = [dict(success=True, setup_success=True, harness_timeout=False,
                        superseded_selections=20, first_ms=2, final_ms=4, wall_ms=5),
                   dict(success=False, setup_success=False, harness_timeout=True,
                        superseded_selections=20, first_ms=-1, final_ms=-1, wall_ms=10000,
                        error='deadline exceeded')]
        result = measure.summary(records)
        self.assertEqual(result['samples'], 2)
        self.assertEqual(result['failures'], 1)
        self.assertEqual(result['setup_failures'], 1)
        self.assertEqual(result['harness_timeouts'], 1)
        self.assertEqual(result['first_ms']['missing'], 1)
        self.assertEqual(result['final_ms']['observations'], 1)
        self.assertEqual(result['wall_ms']['maximum'], 10000)
        self.assertEqual(result['superseded_selections'], 40)
        self.assertEqual(result['reported_errors'], {'deadline exceeded': 1})

    def test_all_missing_pixels_have_no_latency_statistic(self):
        result = measure.summary([dict(success=False, setup_success=True, harness_timeout=False,
                                       superseded_selections=0, first_ms=-1, final_ms=8, wall_ms=9)])
        self.assertIsNone(result['first_ms']['median'])
        self.assertIsNone(result['first_ms']['p95'])
        self.assertIsNone(result['first_ms']['maximum'])
        self.assertEqual(result['final_ms']['median'], 8)

    def test_idle_pane_completion_without_upgraded_pixels_is_invalid(self):
        result = measure.summary([dict(success=True, setup_success=True, harness_timeout=False,
                                       superseded_selections=0, first_ms=-1, final_ms=.002, wall_ms=.003)])
        self.assertEqual(result['invalid_success_observations'], 1)
        self.assertEqual(result['first_ms']['missing'], 1)
        self.assertIsNone(result['first_ms']['median'])

    def test_p95_uses_nearest_rank_and_preserves_maximum(self):
        records = [dict(success=True, setup_success=True, harness_timeout=False,
                        superseded_selections=0, first_ms=i, final_ms=i, wall_ms=i) for i in range(1, 101)]
        result = measure.summary(records)
        self.assertEqual(result['first_ms']['median'], 50.5)
        self.assertEqual(result['first_ms']['p95'], 95)
        self.assertEqual(result['first_ms']['maximum'], 100)

    def test_inventory_detects_bytes_modes_and_symlink_replacement(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'artifact'
            path.write_bytes(b'one')
            before = baselines.inventory(root)
            path.write_bytes(b'two')
            self.assertNotEqual(before, baselines.inventory(root))
            before = baselines.inventory(root)
            path.chmod(0o700)
            self.assertNotEqual(before, baselines.inventory(root))
            before = baselines.inventory(root)
            path.unlink()
            path.symlink_to('missing')
            self.assertNotEqual(before, baselines.inventory(root))

    def test_fixture_is_valid_deterministic_rgb_png(self):
        data = measure.png(3, 2)
        self.assertEqual(data, measure.png(3, 2))
        self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
        offset = 8
        chunks = {}
        while offset < len(data):
            length = struct.unpack('>I', data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            payload = data[offset + 8:offset + 8 + length]
            crc = struct.unpack('>I', data[offset + 8 + length:offset + 12 + length])[0]
            self.assertEqual(crc, zlib.crc32(kind + payload))
            chunks[kind] = payload
            offset += 12 + length
        self.assertEqual(struct.unpack('>IIBBBBB', chunks[b'IHDR']), (3, 2, 8, 2, 0, 0, 0))
        self.assertEqual(zlib.decompress(chunks[b'IDAT']), (b'\0' + b'\xff\0\0' * 3) * 2)
        self.assertNotEqual(measure.png(3, 2), measure.png(3, 2, True))


accounting = module('preview-evidence-accounting')


class FrozenPatchApplication(unittest.TestCase):
    def test_git_diff_patch_changes_nested_archive(self):
        import subprocess
        prepare = module('prepare-preview-evidence')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            source = root / 'build/archive'
            (source / 'src').mkdir(parents=True)
            target = source / 'src/example.cpp'
            target.write_text('before\n')
            overlays = root / 'overlays'
            overlays.mkdir()
            (overlays / 'example.patch').write_text(
                'diff --git a/src/example.cpp b/src/example.cpp\n'
                '--- a/src/example.cpp\n+++ b/src/example.cpp\n'
                '@@ -1 +1 @@\n-before\n+after\n')
            (overlays / 'telemetry.h').write_text('// test\n')
            prepare.OVERLAYS = overlays
            prepare.apply_overlay(source, 'example')
            self.assertEqual(target.read_text(), 'after\n')
            self.assertFalse((root / 'src/example.cpp').exists())


class DiagnosticAccounting(unittest.TestCase):
    def test_missing_and_truncated_records_are_not_zero_durations(self):
        report = accounting.account('HN_DIAG {"event":"provider_begin","pid":7,"operation":"1"}\nHN_DIAG {')
        self.assertEqual(len(report['diagnostics']['malformed']), 1)
        self.assertTrue(report['diagnostics']['missing_flush'])
        operation = report['operations'][0]
        self.assertIsNone(operation['parent_unexplained_ns'])
        self.assertTrue(operation['phases']['capture']['missing'])
        self.assertTrue(operation['helper_telemetry_missing'])

    def test_nested_phases_use_interval_union_and_keep_helper_separate(self):
        import json
        rows = [dict(event='provider_call', begin_ns='10', end_ns='110'),
                dict(event='capture', begin_ns='20', end_ns='50'),
                dict(event='runtime_validation', begin_ns='30', end_ns='60'),
                dict(event='helper_telemetry', stderr='HN_DIAG {"event":"helper_provider_execution",'
                     '"begin_ns":"100000","end_ns":"900000"}', truncated=False)]
        report = accounting.account('\n'.join('HN_DIAG ' + json.dumps(dict(r, pid=7, operation='1', consumer='c'))
                                               for r in rows))
        self.assertEqual(report['operations'][0]['parent_unexplained_ns'], 60)
        self.assertEqual(report['operations'][0]['consumers'], ['c'])
        self.assertEqual(len(report['operations'][0]['helper_timelines']), 1)

    def test_same_operation_id_in_different_processes_does_not_merge(self):
        report = accounting.account('HN_DIAG {"event":"provider_begin","pid":1,"operation":"1"}\n'
                                    'HN_DIAG {"event":"provider_begin","pid":2,"operation":"1"}')
        self.assertEqual(len(report['operations']), 2)

    def test_failed_exit_preserves_partial_rows_and_cleanup_stop(self):
        import json
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'attempts.jsonl'
            result = accounting.preserve_attempt(output, 0, '{"sample":{"cleanup_failure":true}}\n{', '', 20)
            self.assertTrue(result['cleanup_failure'])
            self.assertTrue(result['incomplete'])
            self.assertEqual(len(result['samples']), 1)
            self.assertEqual(json.loads(output.read_text()), result)

    def test_runner_stops_after_cleanup_failure_without_next_invocation(self):
        import json
        import subprocess
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'provenance.json').write_text('{}')
            fixtures = root / 'fixtures'
            fixtures.mkdir()
            for name in ('160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg'):
                (fixtures / name).write_bytes(b'fixture')
            binary = root / 'A/harness/preview-grid-control'
            binary.parent.mkdir(parents=True)
            binary.write_text('#!/usr/bin/env python3\nimport sys, json\nfrom pathlib import Path\n'
                              'if sys.argv[1] == "--describe-workload":\n'
                              ' print(json.dumps({"fixtures": ["160x80.png", "1600x1200.png", "3200x2400.png", "oriented.jpg"] * 4, "scheduler_threads": 2, "box_pixels": 256})); sys.exit(0)\n'
                              'Path(sys.argv[5]).write_text(\'{"sample":{"cleanup_failure":true}}\\n\')\n'
                              'raise SystemExit(20)\n')
            binary.chmod(0o755)
            other = root / 'B/harness/preview-grid-control'
            other.parent.mkdir(parents=True)
            other.write_bytes(binary.read_bytes())
            other.chmod(0o755)
            completed = subprocess.run(['python3', str(ROOT / 'scripts/run-preview-evidence.py'),
                                        str(root), str(fixtures), '--kind', 'scheduler'],
                                       capture_output=True, text=True)
            self.assertEqual(completed.returncode, 20, completed.stderr)
            output = next(root.glob('scheduler-run-*'))
            provenance = json.loads((output / 'provenance.json').read_text())
            self.assertEqual(len(provenance['commands']), 1)
            self.assertEqual(provenance['completed_invocations'], 1)
            self.assertEqual(len((output / 'attempts.jsonl').read_text().splitlines()), 1)

    def test_malformed_shapes_are_retained_as_errors(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = accounting.preserve_attempt(Path(temporary) / 'attempts', 0,
                '[]\nnull\n3\n{"sample":null}\n{"setup":[]}\n{"success":true}', '', 0, 10)
        self.assertEqual(len(result['samples']), 1)
        self.assertEqual(len(result['parse_errors']), 5)
        self.assertTrue(result['incomplete'])

    def test_malformed_telemetry_cannot_crash_accounting(self):
        report = accounting.account('HN_DIAG {"event":"flush","records":[],"dropped":"x"}\n'
            'HN_DIAG {"event":"provider_call","operation":[]}\n'
            'HN_DIAG {"event":"helper_telemetry","operation":"1","stderr":null}')
        self.assertEqual(len(report['diagnostics']['malformed']), 3)

    def test_empty_helper_record_is_missing(self):
        report = accounting.account('HN_DIAG {"event":"helper_telemetry","operation":"1","stderr":""}')
        self.assertTrue(report['operations'][0]['helper_telemetry_missing'])

    def test_workload_preflight_rejects_homogeneous_and_wrong_settings(self):
        runner = module('run-preview-evidence')
        value = dict(fixtures=['160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg'] * 4,
                     scheduler_threads=2, box_pixels=256)
        self.assertTrue(runner.validate_workload(value))
        for key, invalid in [('fixtures', ['160x80.png'] * 16), ('scheduler_threads', 4), ('box_pixels', 128)]:
            self.assertFalse(runner.validate_workload(dict(value, **{key: invalid})))

    def test_variant_metadata_and_historical_fallback(self):
        runner = module('run-preview-evidence')
        self.assertEqual(runner.variants({}, 'scheduler'), ['A', 'B'])
        self.assertEqual(runner.variants({'variants': {'D2': {'role': 'diagnostic'}}}, 'resource'), ['D2'])
        with self.assertRaises(ValueError):
            runner.variants({'variants': {'D2': {'role': 'diagnostic'}}}, 'scheduler')

    def test_setup_failure_keeps_attempt_and_missing_measurement_separate(self):
        import json
        reporter = module('report-preview-evidence')
        names = ['160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg']
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'provenance.json').write_text(json.dumps(dict(kind='scheduler', stopped='cleanup failure',
                variants=['A', 'B2'], commands=[['/B2/harness/grid', 'runtime', 'fixtures', 'warm', '1', str(root / 'raw.json')]])))
            row = dict(fixture_cycle=names, scheduler_threads=2, box_pixels=256,
                       setup=dict(success=False, cleanup_failure=True,
                                  operations=[dict(source_fixture=n) for n in names * 4]))
            accounting.preserve_attempt(root / 'attempts.jsonl', 0, json.dumps(row), '', 20, 1)
            report = reporter.summarize(root)
            self.assertEqual(report['denominators']['attempted'], 1)
            self.assertEqual(report['denominators']['completed'], 0)
            self.assertEqual(report['denominators']['failed'], 1)
            self.assertEqual(report['denominators']['excluded'], 0)
            self.assertEqual(report['denominators']['missing'], 599)
            self.assertEqual(report['denominators']['missing_measurements'], 600)
            (root / 'EXCLUSION.json').write_text('{"reason":"wrong variant"}')
            self.assertEqual(reporter.summarize(root)['denominators']['excluded'], 1)

    def test_unverified_correction_metadata_is_rejected(self):
        runner = module('run-preview-evidence')
        with self.assertRaisesRegex(ValueError, 'verified patch'):
            runner.variants({'variants': {'B2': {'role': 'scheduler', 'corrected_cleanup': True}}}, 'scheduler')

    def test_iteration_failure_gates_all_later_passes(self):
        import json
        import subprocess
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for label, role in [('B2', 'scheduler'), ('D2', 'diagnostic')]:
                package = root / role
                package.mkdir()
                (package / 'provenance.json').write_text(json.dumps({
                    'variants': {label: dict(corrected_cleanup=True, correction_verified=True, diagnostic=label == 'D2', source_delta={})},
                    'revisions': {label: {}}}))
            for label in ('A', 'B2'):
                binary = root / 'scheduler' / label / 'harness/preview-grid-control'
                binary.parent.mkdir(parents=True)
                binary.write_text('#!/usr/bin/env python3\nimport json\nprint(json.dumps(dict('
                    'fixtures=["160x80.png","1600x1200.png","3200x2400.png","oriented.jpg"]*4, '
                    'scheduler_threads=2, box_pixels=256)))\n')
                binary.chmod(0o755)
            fixtures = root / 'fixtures'
            fixtures.mkdir()
            for name in ('160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg'):
                (fixtures / name).write_bytes(b'fixture')
            probe = root / 'probe'
            probe.write_text('#!/usr/bin/env python3\nimport sys, json\nfrom pathlib import Path\n'
                'Path(sys.argv[2]).write_text(json.dumps(dict(kind="diagnostic-only", cycle=0, '
                'operation="inspect", runtime=4, outcome=-1)) + "\\n")\nraise SystemExit(0)\n')
            probe.chmod(0o755)
            (root / 'provenance.json').write_text(json.dumps({'fixtures':
                {p.name: baselines.digest(p) for p in fixtures.iterdir()}}))
            for package, label in [('scheduler', 'B2'), ('diagnostic', 'D2')]:
                base = root / package / label
                base.mkdir(exist_ok=True)
                (base / 'inventory.json').write_text(json.dumps(baselines.inventory(base)))
            result = subprocess.run(['python3', str(ROOT / 'scripts/run-preview-iteration.py'),
                '--scheduler', str(root / 'scheduler'), '--diagnostic', str(root / 'diagnostic'),
                '--fixtures', str(fixtures), '--probe', str(probe)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((Path(result.stdout.splitlines()[0]) / 'summary.json').read_text())
            self.assertEqual(report['gated_passes'], ['diagnostic', 'resource', 'scheduler'])
            self.assertEqual(len(report['passes']), 1)
            self.assertEqual(report['passes'][0]['denominators']['missing'], 1000)
            (root / 'scheduler/B2/harness/preview-grid-control').write_bytes(b'changed')
            result = subprocess.run(['python3', str(ROOT / 'scripts/run-preview-iteration.py'),
                '--scheduler', str(root / 'scheduler'), '--diagnostic', str(root / 'diagnostic'),
                '--fixtures', str(fixtures), '--probe', str(probe)], capture_output=True, text=True)
            report = json.loads((Path(result.stdout.splitlines()[0]) / 'summary.json').read_text())
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report['passes'], [])
            self.assertEqual(report['gated_passes'], ['lifecycle', 'diagnostic', 'resource', 'scheduler'])
            self.assertIn('inventory mismatch', report['stopped'])

            # Independent fixture and correction changes must gate before native work.
            (root / 'scheduler/B2/harness/preview-grid-control').write_bytes(
                (root / 'scheduler/A/harness/preview-grid-control').read_bytes())
            (fixtures / '160x80.png').write_bytes(b'changed fixture')
            result = subprocess.run(result.args, capture_output=True, text=True)
            report = json.loads((Path(result.stdout.splitlines()[0]) / 'summary.json').read_text())
            self.assertEqual(report['passes'], [])
            self.assertIn('fixture mismatch', report['stopped'])
            (fixtures / '160x80.png').write_bytes(b'fixture')
            provenance_path = root / 'scheduler/provenance.json'
            metadata = json.loads(provenance_path.read_text())
            metadata['variants']['B2']['source_delta'] = {'changed': 'correction'}
            provenance_path.write_text(json.dumps(metadata))
            result = subprocess.run(result.args, capture_output=True, text=True)
            report = json.loads((Path(result.stdout.splitlines()[0]) / 'summary.json').read_text())
            self.assertEqual(report['passes'], [])
            self.assertIn('correction provenance mismatch', report['stopped'])


    def test_lifecycle_partial_and_failures(self):
        import json
        runner = module('run-preview-iteration')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'lifecycle.jsonl'
            self.assertTrue(runner.lifecycle_report(path)['failed'])
            rows = [dict(kind='diagnostic-only', cycle=0, operation=name, runtime=0, outcome=0)
                    for name in ('inspect', 'source-decode', 'cached-png-decode')]
            summary = dict(kind='summary', cycles=1, operations=3, elapsed_ms=10)
            def check():
                path.write_text(''.join(json.dumps(r) + '\n' for r in rows + [summary]))
                return runner.lifecycle_report(path, planned=2)
            self.assertTrue(check()['failed'])
            summary['elapsed_ms'] = 600001
            result = check()
            self.assertFalse(result['failed'])
            self.assertEqual(result['cap_shortfall'], 1)
            self.assertEqual(result['denominators']['unattempted'], 1)
            self.assertFalse(runner.lifecycle_report(path, planned=1)['failed'])
            for runtime, outcome in ((0, 1), (4, -1), (6, -1)):
                rows[0].update(runtime=runtime, outcome=outcome)
                result = check()
                self.assertTrue(result['failed'])
                self.assertEqual(result['denominators']['failed'], 1)
            path.write_text(json.dumps(rows[0]) + '\n{"kind":')
            result = runner.lifecycle_report(path)
            self.assertTrue(result['failed'])
            self.assertEqual(result['denominators']['attempted'], 1)
            self.assertEqual(result['denominators']['missing_timed_observations'], 2999)

    def test_artifact_inventory_mismatch_rejected(self):
        import json
        runner = module('run-preview-iteration')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'B2').mkdir()
            (root / 'provenance.json').write_text('{"variants":{"B2":{}}}')
            binary = root / 'B2/binary'
            binary.write_bytes(b'original')
            (root / 'B2/inventory.json').write_text(json.dumps(baselines.inventory(root / 'B2')))
            runner.audit_package(root, baselines)
            binary.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'inventory mismatch'):
                runner.audit_package(root, baselines)

    def test_overflow_and_silently_missing_records_remain_explicit(self):
        rows, diagnostic = accounting.telemetry('HN_DIAG {"event":"capture"}\n'
                                                'HN_DIAG {"event":"flush","records":2,"dropped":3}')
        self.assertEqual(diagnostic['dropped'], 3)
        self.assertEqual(diagnostic['record_count_mismatches'], [{'claimed': 2, 'observed': 1}])

    def test_missing_proc_observation_does_not_become_zero_memory(self):
        runner = module('run-preview-evidence')
        with tempfile.TemporaryDirectory() as temporary:
            observed = runner.observe(123, Path(temporary))
        self.assertFalse(observed['discovery_complete'])
        self.assertIsNone(observed['parent_rss_bytes'])
        self.assertIsNone(observed['concurrent_scope_bytes'])

    def test_homogeneous_batches_do_not_qualify_as_mixed_fixture_control(self):
        reporter = module('report-preview-evidence')
        names = ['160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg']
        row = {'fixture_cycle': names, 'scheduler_threads': 2, 'box_pixels': 256,
               'sample': {'operations': [{'source_fixture': name} for name in names * 4]}}
        self.assertTrue(reporter.mixed_fixture_batch(row))
        setup_only = dict(row, setup=row['sample'])
        del setup_only['sample']
        self.assertTrue(reporter.mixed_fixture_batch(setup_only))
        row['sample']['operations'][1]['source_fixture'] = names[0]
        self.assertFalse(reporter.mixed_fixture_batch(row))
        self.assertFalse(reporter.mixed_fixture_batch({'fixture': names[0], 'sample': {}}))


class CorrectedIterationGates(unittest.TestCase):
    def test_manifest_exception_is_prefix_only_and_read_only(self):
        import json
        runner = module('run-preview-iteration')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / 'B2'
            path = base / 'build/holonight-images/install_manifest.txt'
            path.parent.mkdir(parents=True)
            (root / 'provenance.json').write_text('{"variants":{"B2":{}}}')
            original = str(base / 'prefix')
            acceptance = root / 'acceptance'
            frozen = (original + '/lib/a\n' + original + '/include/b\n').encode()
            path.write_bytes(frozen)
            inventory = baselines.inventory(base)
            (base / 'inventory.json').write_text(json.dumps(inventory))
            changed = frozen.replace(original.encode(), str(acceptance).encode())
            path.write_bytes(changed)
            with self.assertRaises(ValueError):
                runner.audit_package(root, baselines)
            proof = runner.audit_package(root, baselines, acceptance)['B2']['metadata_exceptions']
            self.assertTrue(next(iter(proof.values()))['verified'])
            self.assertEqual(path.read_bytes(), changed)
            self.assertEqual(json.loads((base / 'inventory.json').read_text()), inventory)
            for invalid in (changed + b'added\n', changed.splitlines(keepends=True)[0],
                            b''.join(reversed(changed.splitlines(keepends=True))),
                            changed.replace(b'/lib/a', b'/lib/c'),
                            changed.replace(str(acceptance).encode(), str(acceptance).encode() + b'-other')):
                path.write_bytes(invalid)
                with self.assertRaises(ValueError):
                    runner.audit_package(root, baselines, acceptance)
            path.write_bytes(changed)
            path.chmod(0o600)
            with self.assertRaises(ValueError):
                runner.audit_package(root, baselines, acceptance)

    def test_cap_between_operations_preserves_partial_cycle(self):
        import json
        runner = module('run-preview-iteration')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'lifecycle'
            rows = [dict(cycle=0, operation='inspect', runtime=0, outcome=0),
                    dict(kind='summary', cycles=0, operations=1, elapsed_ms=600001)]
            path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            result = runner.lifecycle_report(path, 2)
            self.assertFalse(result['failed'])
            self.assertEqual(result['denominators']['partial_cycles'], 1)
            self.assertEqual(result['denominators']['successful'], 0)
            self.assertEqual(result['denominators']['missing_timed_observations'], 5)
            rows[0]['operation'] = 'cached-png-decode'
            path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            self.assertTrue(runner.lifecycle_report(path, 2)['failed'])

    def test_child_partial_and_missing_reports_gate_without_losing_ledger(self):
        import json
        runner = module('run-preview-iteration')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'summary.json'
            counts = dict(planned=280, requested=10, attempted=3, completed=2, failed=1,
                          excluded=0, unattempted=270, unreported_requested_slots=7,
                          missing_timed_observations=278)
            path.write_text(json.dumps(dict(denominators=counts, incomplete_invocations=1)))
            ledger, entry = {}, {}
            self.assertTrue(runner.import_child(path, 280, ledger, 'diagnostic', entry))
            self.assertEqual(ledger['diagnostic'], counts)
            for text in ('{', '{}', 'null'):
                path.write_text(text)
                self.assertTrue(runner.import_child(path, 280, ledger, 'diagnostic', {}))
                self.assertEqual(ledger['diagnostic'], counts)
            self.assertTrue(runner.import_child(path.parent / 'absent', 280, ledger, 'diagnostic', {}))

    def test_missing_child_summary_recovers_requested_and_observed_slots(self):
        import json
        runner = module('run-preview-iteration')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            command = ['/D2/harness/preview-benchmark', 'runtime', 'fixture', 'first', '10', str(root / 'raw.json')]
            (root / 'provenance.json').write_text(json.dumps(dict(kind='diagnostic', stopped='launch failed',
                variants=['D2'], commands=[command])))
            row = dict(success=False, setup_success=False, first_ms=-1, final_ms=-1)
            accounting.preserve_attempt(root / 'attempts.jsonl', 0, json.dumps(row), '', 1, 10)
            for malformed in (None, '{'):
                path = root / 'summary.json'
                if malformed is not None:
                    path.write_text(malformed)
                ledger, entry = {}, {}
                self.assertTrue(runner.import_child(path, 280, ledger, 'diagnostic', entry))
                counts = ledger['diagnostic']
                self.assertEqual(counts['requested'], 10)
                self.assertEqual(counts['attempted'], 1)
                self.assertEqual(counts['failed'], 1)
                self.assertEqual(counts['unattempted'], 270)
                self.assertEqual(counts['unreported_requested_slots'], 9)
                self.assertIn('report_error', entry)

    def test_warm_setup_and_timed_identity_are_independent(self):
        import copy
        reporter = module('report-preview-evidence')
        names = ['160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg']
        batch = dict(success=True, started=0, operations=[dict(source_fixture=n) for n in names * 4])
        row = dict(scheduler_threads=2, box_pixels=256, fixture_cycle=names,
                   setup=copy.deepcopy(batch), sample=copy.deepcopy(batch))
        self.assertTrue(reporter.valid_scheduler_batch(row, 'warm'))
        for field in ('setup', 'sample'):
            invalid = copy.deepcopy(row)
            invalid[field]['operations'][0]['source_fixture'] = 'other.png'
            self.assertFalse(reporter.valid_scheduler_batch(invalid, 'warm'))
        row['sample']['started'] = 1
        self.assertFalse(reporter.valid_scheduler_batch(row, 'warm'))


if __name__ == '__main__':
    unittest.main()
