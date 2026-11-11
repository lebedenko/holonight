"""Performance acceptance must retain failures and tail regressions."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('transactions', ROOT / 'scripts/measure-preview-transactions.py')
transactions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transactions)


class Acceptance(unittest.TestCase):
    @staticmethod
    def summaries(candidate=60, candidate_p95=80):
        summary = {}
        for label, median, p95 in [('A', 10, 15), ('B', 100, 120), ('C', candidate, candidate_p95)]:
            summary[label + '-fixture-first'] = {
                'samples': 100, 'failures': 0, 'setup_failures': 0,
                'harness_timeouts': 0, 'invalid_success_observations': 0,
                'first_ms': {'median': median, 'p95': p95},
                'final_ms': {'median': median + 1, 'p95': p95 + 1},
            }
        return summary

    def test_reports_milliseconds_percent_and_remaining_slowdown(self):
        table, accepted = transactions.table(self.summaries())
        self.assertTrue(accepted)
        self.assertIn('60.000 / 80.000', table)
        self.assertIn('40.000 | 40.0% | +500.0%', table)

    def test_tail_regression_rejects_median_gain(self):
        self.assertFalse(transactions.table(self.summaries(candidate_p95=121))[1])

    def test_missing_failure_and_insufficient_gain_reject(self):
        for key in ('failures', 'setup_failures', 'harness_timeouts', 'invalid_success_observations'):
            summary = self.summaries()
            summary['C-fixture-first'][key] = 1
            self.assertFalse(transactions.table(summary)[1])
        self.assertFalse(transactions.table(self.summaries(candidate=71))[1])
        summary = self.summaries()
        del summary['B-fixture-first']
        self.assertFalse(transactions.table(summary)[1])


if __name__ == '__main__':
    unittest.main()
