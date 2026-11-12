"""Qualification must reject incomplete, contradictory or out-of-budget observations."""
import importlib.util
from pathlib import Path
import unittest

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

    def test_smoke_results_cannot_establish_qualification(self):
        data = {key: value[:1] for key, value in records().items()}
        self.assertFalse(metrics.assess(data, metrics.SCENARIOS, 1)['latency_targets_met'])


if __name__ == '__main__':
    unittest.main()
