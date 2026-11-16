"""Synthetic offline contract tests; process execution is forbidden."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


a = module('reconciliation_assessor_test', 'assess-preview-startup-reconciliation.py')
v = module('reconciliation_verifier_test', 'verify-preview-startup-reconciliation.py')


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.process = patch.object(subprocess, 'Popen', side_effect=AssertionError('process execution forbidden'))
        self.process.start()
        self.addCleanup(self.process.stop)
        self.value = dict(direction='mixed; inconclusive', below_threshold=8, positive_blocks=7, negative_blocks=1, zero_blocks=0)
        self.lives = [dict(validations=1, within_lifetime_repeated_bytes=0, generation_identity='unproven') for _ in range(52)]

    def test_deferred(self):
        v.check_decision(a.choose(self.value, self.lives), self.value, self.lives)

    def test_conflicting_evidence(self):
        self.value['below_threshold'] = 7
        with self.assertRaises(ValueError):
            a.choose(self.value, self.lives)

    def test_unjustified_caching(self):
        self.lives[0]['within_lifetime_repeated_bytes'] = 1
        with self.assertRaises(ValueError):
            a.choose(self.value, self.lives)

    def test_candidate_tampering(self):
        d = a.choose(self.value, self.lives)
        d['eligible'] = ['streaming']
        with self.assertRaises(ValueError):
            v.check_decision(d, self.value, self.lives)

    def test_gate_arithmetic_and_no_cross_population_subtraction(self):
        s = dict(gates=[dict(case='3200x2400.png/startup', event=e, passed=False) for e in ('first_ms', 'final_ms')] +
                 [dict(passed=True) for _ in range(78)], summary={'3200x2400.png/startup': {
                     arm: {e: dict(p95=n) for e in ('first_ms', 'final_ms')} for arm, n in [('A', 127.828), ('C', 142.332)]}})
        rows = a.gates(s)
        v.check_gates(rows, s)
        rows[0]['candidate_p95_ms'] -= 1.4
        with self.assertRaises(ValueError):
            v.check_gates(rows, s)

    def test_unavailable_is_not_zero(self):
        self.lives[0]['within_lifetime_repeated_bytes'] = None
        with self.assertRaises(ValueError):
            v.check_decision(a.choose(self.value, [dict(r, within_lifetime_repeated_bytes=0) for r in self.lives]), self.value, self.lives)

    def test_collision_overlap_seal_and_drift(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                a.h.fresh(root, [])
            with self.assertRaises(ValueError):
                a.h.fresh(root / 'nested', [root])
            p = root / 'data.json'
            a.h.write(p, {'population': 'setup'})
            before = a.h.inventory(root)
            a.h.write(root / 'seal.json', before)
            a.h.sealed(root)
            p.write_text('{}')
            with self.assertRaises(ValueError):
                a.h.sealed(root)
            self.assertFalse(a.h.recheck({}, {str(p): before['data.json']}))

    def test_population_separation(self):
        facts = dict(context=dict(distributions=[dict(population='setup', arm='profiled', endpoints_ns=None)]))
        rows = [dict(investigation=k, population=p, separate_populations=facts['context']['distributions'] if k == 'work' else None)
                for k, (_, p, _) in a.QUESTIONS.items()]
        v.check_populations(rows, facts)
        rows[0]['population'] = '600 pooled including warmups'
        with self.assertRaises(ValueError):
            v.check_populations(rows, facts)

    def test_source_and_dependency_identity_mismatch(self):
        with patch.object(a.b.h, 'digest', return_value='incompatible'), patch.object(a.b.b, 'bind', return_value=([], {}, {}, [], [])):
            with self.assertRaisesRegex(ValueError, 'identity drift'):
                a.b.bind()

    def test_blocked_preserved(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as tmp:
            out = Path(tmp) / 'partial'
            with patch.object(a.b, 'bind', side_effect=ValueError('incompatible dependency identity')):
                result = a.run(out)
            self.assertEqual(result['status'], 'blocked')
            a.h.sealed(out)
            self.assertEqual(v.verify(out)['outcome'], 'blocked')
