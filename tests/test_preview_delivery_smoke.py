"""Synthetic bounded delivery runtime gate; no retained workloads are executed."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


s = load('delivery_smoke_test', ROOT / 'scripts/run-preview-delivery-smoke.py')
v3 = load('delivery_smoke_v3_fixture', ROOT / 'tests/test_preview_startup_smoke.py')
v4 = load('delivery_smoke_v4_fixture', ROOT / 'tests/test_preview_delivery_tracing.py')


def combined(variant='C'):
    historical = v3.trace()
    values = []
    for observation in (1, 2, 3):
        offset = observation * 1000
        reference = next(e for e in historical if e['observation'] == observation and e['phase'] == 'pixels')
        fields = {k: reference[k] for k in ('pid', 'service', 'observation', 'job', 'worker', 'preparation')}
        fields.update(session=observation * 10 + 8, transaction=observation * 10 + 9)
        for e in historical:
            if e['observation'] == observation:
                e['ns'] = offset + (e['ns'] % 100) * 10
                if e['phase'] in ('pixels', 'metadata'):
                    e['ns'] = offset + (490 if e['phase'] == 'pixels' else 491)
                if e['phase'] in ('service_destruction', 'service_shutdown'):
                    e['ns'] += 400
        supplemental = v4.delivery()
        for e in supplemental:
            e.update(fields)
            e['ns'] = offset + 300 + e['ns'] * 10
            e['span'] = e['span'] + observation * 100 if e['span'] else None
            e['publication'] += observation * 100
        required = [('reusable_completion_ack', 'acknowledged')] if variant in 'CD' else [('oneshot_ack', 'sent'), ('helper_exit', 'validated_exit'), ('effective_cleanup', 'verified')]
        for i, (op, outcome) in enumerate(required):
            for e in v4.span(offset + 180 + i * 10, offset + 185 + i * 10, op, observation * 100 + 20 + i, outcome=outcome):
                e.update(fields)
                supplemental.append(e)
        values.extend(supplemental)
    return historical, values


def trace(historical, values):
    return v3.text(historical) + '\n' + '\n'.join('DELIVERY ' + json.dumps(e) for e in values)


def sample():
    return dict(success=True, setup_success=True, correct_pixels=True, correct_metadata=True,
                first_ms=1, final_ms=2, deliveries=[dict(event='pixels', selection=4, latency_ms=1),
                                                    dict(event='metadata', selection=4, latency_ms=2)])


class DeliverySmokeTests(unittest.TestCase):
    def test_exact_schedule_bounds_and_order(self):
        commands = s.schedule(Path('/package'), Path('/runtime'), Path('/fixtures'), Path('/out'))
        self.assertEqual(len(commands), 12)
        self.assertEqual([Path(c[1]).name for c in commands], [v for v in 'ABCD' for _ in range(3)])
        self.assertEqual([Path(c[2]).name for c in commands], list(s.FIXTURES) * 4)
        self.assertTrue(all(c[3:5] == ['startup', '3'] for c in commands))
        self.assertEqual(sum(int(c[4]) for c in commands), 36)

    def test_valid_combined_trace_all_variants(self):
        for variant in 'ABCD':
            h, values = combined(variant)
            report = s.trace_validation(trace(h, values), [{}, {}, {}], '/original.stderr', variant)
            self.assertEqual(report['issues'], [])
            self.assertTrue(all(e['file'] == '/original.stderr' and e['line'] > 0 for e in report['events']))

    def test_missing_required_evidence_and_identity_conflicts(self):
        for operation in ('enqueue_call', 'callback_execution', 'apply_result', 'changed_emission', 'endpoint_pixels', 'result_decision', 'reusable_completion_ack'):
            h, values = combined()
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                s.trace_validation(trace(h, [e for e in values if e['operation'] != operation]), [{}, {}, {}], '/raw', 'C')
        for field in ('generation', 'transaction', 'session', 'job', 'worker', 'preparation'):
            h, values = combined()
            values[-1][field] = 999
            with self.subTest(field=field), self.assertRaises(ValueError):
                s.trace_validation(trace(h, values), [{}, {}, {}], '/raw', 'C')

    def test_duplicate_malformed_and_impossible_records(self):
        h, values = combined()
        for text in (trace(h, values + values[:1]), trace(h, values) + '\nDELIVERY {}', trace(h, [dict(e, ns=0) if e['operation'] == 'endpoint_pixels' else e for e in values])):
            with self.assertRaises(ValueError):
                s.trace_validation(text, [{}, {}, {}], '/raw', 'C')

    def test_missing_lifetime_and_preparation_fail(self):
        h, values = combined()
        for phase in ('service_destruction', 'selected_worker'):
            with self.assertRaises(ValueError):
                s.trace_validation(trace([e for e in h if e['phase'] != phase], values), [{}, {}, {}], '/raw', 'C')

    def test_content_exit_timeout_and_ownership(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'C-test.json'
            fixture = Path(temporary) / 'fixture.png'
            fixture.write_bytes(b'fixture')
            work = target.parent / (target.name + '.work-private')
            (work / 'cache').mkdir(parents=True)
            for index in range(32):
                (work / f'{index}.png').write_bytes(fixture.read_bytes())
            h, values = combined()
            target.with_suffix('.stderr').write_text(trace(h, values))
            process = dict(exit=0, timeout=False, cleanup_verified=True)
            original = dict(scenario='startup', fixture=str(fixture), samples=[sample() for _ in range(3)])
            target.write_text(json.dumps(original))
            s.validate_invocation(target, 'C', process, os.getuid(), fixture)
            for change in (dict(exit=1), dict(timeout=True), dict(cleanup_verified=False)):
                with self.assertRaises(ValueError):
                    s.validate_invocation(target, 'C', dict(process, **change), os.getuid(), fixture)
            with self.assertRaises(ValueError):
                s.validate_invocation(target, 'C', process, os.getuid() + 1, fixture)
            for key in ('correct_pixels', 'correct_metadata', 'setup_success'):
                data = copy.deepcopy(original)
                data['samples'][0][key] = False
                target.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    s.validate_invocation(target, 'C', process, os.getuid(), fixture)

    def test_stop_before_next_launch_on_process_or_scope_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            commands = s.schedule(Path('/pkg'), Path('/run'), Path('/fixtures'), Path(temporary))
            for snapshots, process in (([dict(isolated=False)], None),
                                       ([dict(isolated=True), dict(isolated=False)], dict(exit=1, timeout=False, cleanup_verified=True)),
                                       ([dict(isolated=True), dict(isolated=True)], dict(exit=-9, timeout=True, cleanup_verified=False))):
                with patch.object(s, 'scope_snapshot', side_effect=snapshots), patch.object(s.smoke, 'execute', return_value=process) as execute:
                    result = dict(invocations=[])
                    with self.assertRaises((ValueError, OSError)):
                        s.run_commands(commands, result, 1000, {}, {})
                    self.assertLessEqual(execute.call_count, 1)
                    self.assertTrue(all(r['status'] == 'failed' for r in result['invocations']))

    def test_residual_scopes_or_second_failure_stop_valid_schedule(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for fixture in s.FIXTURES:
                (base / fixture).write_bytes(b'fixture')
            commands = s.schedule(Path('/pkg'), Path('/run'), base, base)
            launched = []
            def execute(command, target, env, credentials):
                launched.append(command)
                variant = target.name[0]
                h, values = combined(variant)
                target.with_suffix('.stderr').write_text(trace(h, values))
                target.write_text(json.dumps(dict(scenario='startup', fixture=command[2], samples=[sample() for _ in range(3)])))
                work = target.parent / (target.name + '.work-private')
                (work / 'cache').mkdir(parents=True, exist_ok=True)
                for index in range(32):
                    (work / (str(index) + Path(command[2]).suffix)).write_bytes(b'fixture')
                return dict(exit=1 if len(launched) == 2 else 0, timeout=False, cleanup_verified=True)
            for residual in (True, False):
                launched.clear()
                snapshots = [dict(isolated=True), dict(isolated=not residual)] + [dict(isolated=True)] * 2
                with patch.object(s, 'scope_snapshot', side_effect=snapshots), patch.object(s.smoke, 'execute', side_effect=execute):
                    result = dict(invocations=[])
                    with self.assertRaisesRegex(ValueError, 'residual scopes' if residual else 'process failed'):
                        s.run_commands(commands, result, os.getuid(), {}, {})
                    self.assertEqual(len(launched), 1 if residual else 2)
                    self.assertEqual([r['status'] for r in result['invocations']], ['failed'] if residual else ['passed', 'failed'])

    def test_managed_generation_marker_resolves_exact_payload(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            package, runtime = base / 'package', base / 'runtime'
            for v in 'ABCD':
                source = package / v / 'runtime'
                source.mkdir(parents=True)
                (source / 'manifest.json').write_text('{}')
                if v == 'A':
                    payload = runtime / v
                    payload.mkdir(parents=True)
                else:
                    name = v.lower() * 64
                    payload = runtime / v / 'generations' / name
                    payload.mkdir(parents=True)
                    (runtime / v / 'current').write_text(name + '\n')
                    (runtime / v / 'ownership.json').write_text(json.dumps([name]))
                (payload / 'manifest.json').write_text('{}')
            s.staged_payloads(package, runtime)
            (runtime / 'B/current').write_text('../escape')
            with self.assertRaises(ValueError):
                s.staged_payloads(package, runtime)

    def test_reassessment_rejection_or_tampering_prevents_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            package, review = base / 'package', base / 'review'
            package.mkdir()
            review.mkdir()
            s.write(package / 'evidence-hashes.json', {})
            s.write(review / 'acceptance.json', dict(accepted=False, variants=dict.fromkeys('ABCD', False)))
            s.write(review / 'evidence-hashes.json', {'acceptance.json': s.digest(review / 'acceptance.json')})
            with patch.object(s.smoke, 'execute', side_effect=AssertionError('no workloads')):
                with self.assertRaisesRegex(ValueError, 'not accepted'):
                    s.preflight(package, review, base / 'prepared', base / 'fixtures')
                s.write(review / 'acceptance.json', dict(accepted=True, variants=dict.fromkeys('ABCD', True)))
                with self.assertRaisesRegex(ValueError, 'changed or missing'):
                    s.preflight(package, review, base / 'prepared', base / 'fixtures')

    def test_hash_tampering_and_destination_collision(self):
        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary) / 'input'
            p.write_text('original')
            expected = {p.name: s.digest(p)}
            p.write_text('tampered')
            with self.assertRaises(ValueError):
                s.smoke.verify_hashes(p.parent, expected)
        from types import SimpleNamespace
        base = ROOT / 'build'
        args = SimpleNamespace(package=base / 'pkg', reassessment=base / 'review', prepared=base / 'prep', fixtures=base / 'fixtures', output=base, uid=os.getuid() or 1000)
        with patch.object(s.os, 'geteuid', return_value=0), self.assertRaises(ValueError):
            s.run(args)
        with tempfile.TemporaryDirectory(dir=base) as existing:
            args.output = Path(existing)
            with patch.object(s.os, 'geteuid', return_value=0), self.assertRaises(FileExistsError):
                s.run(args)


if __name__ == '__main__':
    unittest.main()
