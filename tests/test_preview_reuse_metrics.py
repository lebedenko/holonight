"""Qualification must reject incomplete, contradictory or out-of-budget observations."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from contextlib import ExitStack, redirect_stdout
from io import StringIO
import json
import tempfile
from types import SimpleNamespace

SPEC = importlib.util.spec_from_file_location('reuse_metrics', Path(__file__).resolve().parents[1] /
                                            'scripts/measure-preview-reuse.py')
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)


def observation(first=1.0, final=1.1):
    return dict(success=True, setup_success=True, correct_pixels=True, correct_metadata=True,
                first_ms=first, final_ms=final, cleanup_failure=False, harness_timeout=False)


def records():
    return {(label, fixture, scenario): [observation() for _ in range(100)]
            for label in metrics.LABELS for fixture in metrics.FIXTURES for scenario in metrics.SCENARIOS}


class ReuseQualification(unittest.TestCase):
    def test_missing_samples_cannot_qualify(self):
        data = records()
        data[('C', metrics.FIXTURES[0], 'memory')].pop()
        result = metrics.assess(data, metrics.SCENARIOS, 100)
        self.assertFalse(result['latency_targets_met'])
        self.assertEqual(result['summary'][metrics.FIXTURES[0] + '/memory']['C']['missing'], 1)

    def test_memory_gate_uses_absolute_median_and_p95_regression(self):
        data = records()
        data[('C', metrics.FIXTURES[0], 'memory')] = [observation(1.201, 1.301) for _ in range(100)]
        self.assertFalse(metrics.assess(data, metrics.SCENARIOS, 100)['latency_targets_met'])

    def test_source_texture_exception_never_exempts_disk_hits(self):
        data = records()
        fixture = '3200x2400.png'
        data[('C', fixture, 'ready')] = [observation(100, 101) for _ in range(100)]
        self.assertTrue(metrics.assess(data, metrics.SCENARIOS, 100)['latency_targets_met'])
        data[('C', fixture, 'disk')] = [observation(51, 52) for _ in range(100)]
        self.assertFalse(metrics.assess(data, metrics.SCENARIOS, 100)['latency_targets_met'])

    def test_contradictory_success_and_notification_order_are_rejected(self):
        for change in ({'correct_pixels': False}, {'correct_metadata': False}, {'cleanup_failure': True},
                       {'harness_timeout': True}, {'first_ms': 2, 'final_ms': 1}, {'first_ms': float('inf')}):
            with self.subTest(change=change):
                row = observation()
                row.update(change)
                self.assertFalse(metrics.valid_observation(row))

    def test_invalid_or_excess_distributions_are_not_reported(self):
        for change in ({'cleanup_failure': True}, {'first_ms': True},
                       {'first_ms': -1}, {'final_ms': float('nan')}, {'setup_success': False}):
            with self.subTest(change=change):
                data = records()
                data[('A', metrics.FIXTURES[0], 'ready')][0].update(change)
                result = metrics.assess(data, metrics.SCENARIOS, 100)
                self.assertFalse(result['latency_targets_met'])
                self.assertIsNone(result['summary'][metrics.FIXTURES[0] + '/ready']['A']['first_ms'])
        data = records()
        data[('C', metrics.FIXTURES[0], 'ready')].append(observation())
        result = metrics.assess(data, metrics.SCENARIOS, 100)
        self.assertFalse(result['latency_targets_met'])
        self.assertEqual(result['summary'][metrics.FIXTURES[0] + '/ready']['C']['excess'], 1)
        self.assertIsNone(result['summary'][metrics.FIXTURES[0] + '/ready']['C']['first_ms'])

    def test_failed_warmup_invalidates_otherwise_complete_measurement(self):
        result = metrics.assess(records(), metrics.SCENARIOS, 100, ['warmup failed'])
        self.assertFalse(result['latency_targets_met'])
        self.assertEqual(metrics.assessment_exit_status(result), 1)
        self.assertIsNone(result['summary'][metrics.FIXTURES[0] + '/ready']['A']['first_ms'])

    def test_numerical_failure_has_failing_exit_status(self):
        data = records()
        data[('C', metrics.FIXTURES[0], 'disk')] = [observation(31, 32) for _ in range(100)]
        self.assertEqual(metrics.assessment_exit_status(metrics.assess(data, metrics.SCENARIOS, 100)), 1)
        self.assertEqual(metrics.assessment_exit_status(metrics.assess(records(), metrics.SCENARIOS, 100)), 0)

    def test_corrected_reference_is_explicit_in_report(self):
        result = metrics.assess(records(), metrics.SCENARIOS, 100, reference='A-fixed')
        self.assertIn('A-fixed', metrics.report(result))
        self.assertIn('original A remains failed', metrics.report(result))
        self.assertEqual(result['reference'], 'A-fixed')

    def test_numerical_failure_preserves_runtime_fixture(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package, fixtures = root / 'package', root / 'fixtures'
            package.mkdir()
            fixtures.mkdir()
            (fixtures / 'tiny.png').write_bytes(b'fixture')
            for label in metrics.LABELS:
                binary = package / label / 'reuse-harness/preview-benchmark'
                binary.parent.mkdir(parents=True)
                binary.write_bytes(label.encode())
            (package / 'A/runtime').mkdir()
            (package / 'harness-inventory-final.json').write_text('{}')
            (package / 'freeze.json').write_text('{}')
            make_directory = tempfile.mkdtemp

            def disposable_directory(**kwargs):
                if kwargs.get('dir') == '/run':
                    kwargs['dir'] = root
                return make_directory(**kwargs)

            def generation(arguments):
                self.assertEqual(arguments.command, 'install', 'failed fixture must not be removed')
                arguments.runtime.mkdir()

            def harness(command, **kwargs):
                rows = [observation(31, 32) for _ in range(int(command[-2]))]
                Path(command[-1]).write_text(json.dumps({'samples': rows}))
                return SimpleNamespace(returncode=0)

            account = SimpleNamespace(pw_gid=1000, pw_dir=str(root), pw_name='test')
            with ExitStack() as stack, redirect_stdout(StringIO()):
                for target, value in (('SCENARIOS', ('disk',)), ('FIXTURES', ('tiny.png',))):
                    stack.enter_context(patch.object(metrics, target, value))
                stack.enter_context(patch('sys.argv', ['measure', str(package), str(fixtures), '--uid', '1000']))
                stack.enter_context(patch.object(metrics.os, 'geteuid', return_value=0))
                stack.enter_context(patch.object(metrics.os, 'chown'))
                stack.enter_context(patch.object(metrics.os, 'getgrouplist', return_value=[1000]))
                stack.enter_context(patch.object(metrics.pwd, 'getpwuid', return_value=account))
                stack.enter_context(patch.object(metrics.tempfile, 'mkdtemp', side_effect=disposable_directory))
                stack.enter_context(patch.object(metrics.generations, 'run', side_effect=generation))
                stack.enter_context(patch.object(metrics.subprocess, 'run', side_effect=harness))
                self.assertEqual(metrics.main(), 1)
            output, = package.glob('reuse-measurement-*')
            result = json.loads((output / 'summary.json').read_text())
            self.assertTrue(Path(result['preserved_runtime_root']).is_dir())
            self.assertIsNone(result['failure'])
            self.assertTrue(any(not gate['passed'] for gate in result['gates']))
            self.assertIsNotNone(result['summary']['tiny.png/disk']['C']['first_ms'])
            self.assertEqual(sum(map(len, result['raw_observations'].values())), 300)

    def test_smoke_results_cannot_establish_qualification(self):
        data = {key: value[:1] for key, value in records().items()}
        self.assertFalse(metrics.assess(data, metrics.SCENARIOS, 1)['latency_targets_met'])


if __name__ == '__main__':
    unittest.main()
