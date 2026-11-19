"""Synthetic C audit contracts. Workloads/process execution are forbidden."""
import copy
import difflib
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


a = module('applicability_auditor_test', 'audit-preview-startup-applicability.py')
v = module('applicability_verifier_test', 'verify-preview-startup-applicability.py')


class ApplicabilityTests(unittest.TestCase):
    def setUp(self):
        for owner, name in [(subprocess, 'Popen'), (os, 'system'), (os, 'posix_spawn'), (os, 'fork'), (os, 'execve')]:
            blocker = patch.object(owner, name, side_effect=AssertionError('process execution forbidden'))
            blocker.start(); self.addCleanup(blocker.stop)
        tmp = tempfile.TemporaryDirectory(dir=ROOT / 'build')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.facts = dict(value=dict(direction='mixed; inconclusive', positive_blocks=7, negative_blocks=1,
                                    zero_blocks=0, below_threshold=8),
                          work=[dict(validations=1, within_lifetime_repeated_bytes=0, generation_identity='unproven') for _ in range(52)])
        self.raw = {'qualification-C': {'usr/lib/lib.so': dict(size=4, sha256='a'*64)},
                    'validation-C': {'usr/lib/lib.so': dict(size=4, sha256='b'*64)}}

    def sources(self):
        names = ['qualification-C', 'CU', 'CT', 'v3-C', 'v4-C', 'baseline-C', 'validation-C']
        stages = []
        for index, name in enumerate(names):
            base = self.root / name
            base.mkdir()
            file = base / 'code.cpp'
            file.write_text('int value = 1;\n' + ('// recorded C tracing\n' if index >= 2 else '') +
                            ('// recorded C delivery\n' if index >= 4 else '') +
                            ('// recorded C validation\n' if index >= 6 else ''))
            harness = base / 'harness.cpp'
            harness.write_text('start();\n' + ('// C harness tracing\n' if index >= 2 else ''))
            stages.append((name, {'source/code.cpp': file, 'harness-source/reuse.cpp': harness}))
        p, q = stages[1][1]['source/code.cpp'], stages[2][1]['source/code.cpp']
        recorded = ''.join(difflib.unified_diff(p.read_text().splitlines(keepends=True), q.read_text().splitlines(keepends=True), fromfile=str(p), tofile=str(q)))
        hp, hq = stages[1][1]['harness-source/reuse.cpp'], stages[2][1]['harness-source/reuse.cpp']
        recorded += ''.join(difflib.unified_diff(hp.read_text().splitlines(keepends=True), hq.read_text().splitlines(keepends=True), fromfile=str(hp), tofile=str(hq)))
        delivery = [dict(file='source/code.cpp', anchor='// recorded C tracing', replacement='// recorded C tracing\n// recorded C delivery')]
        validation = [dict(file='source/code.cpp', variant='C', mode='validation', anchor='// recorded C delivery', replacement='// recorded C delivery\n// recorded C validation')]
        return stages, delivery, validation, recorded

    def test_recorded_c_replay_and_independent_reverse(self):
        inputs = self.sources()
        rows = a.source_rows(*inputs)
        v.check_sources(rows, *inputs)
        self.assertEqual(rows[-1]['status'], 'compatible under recorded transformations')
        self.assertEqual(rows[0]['status'], 'exact identity')

    def test_unexplained_source_edit_is_not_stripped(self):
        stages, *rest = self.sources()
        stages[-1][1]['source/code.cpp'].write_text('int value = 2;\n// recorded C tracing\n// recorded C delivery\n// recorded C validation\n')
        with self.assertRaisesRegex(ValueError, 'unexplained C source edit'):
            a.source_rows(stages, *rest)

    def test_a_sources_cannot_substitute_for_c(self):
        stages, *rest = self.sources()
        stages[0] = ('qualification-A', stages[0][1])
        with self.assertRaisesRegex(ValueError, 'A-to-C'):
            a.source_rows(stages, *rest)
        with self.assertRaisesRegex(ValueError, 'A-to-C'):
            v.check_sources([], stages, *rest)

    def test_extra_patch_and_resealed_source_claim_rejected(self):
        inputs = self.sources()
        rows = a.source_rows(*inputs)
        with self.assertRaisesRegex(ValueError, 'patch mismatch'):
            v.check_sources(rows, *inputs[:-1], inputs[-1] + 'unrecorded\n')
        rows[-1]['expected_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'derivation'):
            v.check_sources(rows, *inputs)

    def test_same_size_different_digest_is_different(self):
        rows = a.payload_rows(self.raw)
        v.check_payloads(rows, self.raw)
        self.assertEqual(rows[0]['status'], 'different')

    def test_unavailable_is_not_zero_or_equal(self):
        self.raw['validation-C'] = {}
        rows = a.payload_rows(self.raw)
        self.assertEqual(rows[0]['status'], 'unavailable')
        rows[0]['status'] = 'exact identity'
        with self.assertRaises(ValueError):
            v.check_payloads(rows, self.raw)

    def test_manifest_duplicate_missing_and_outer_scope(self):
        p = self.root / 'runtime'
        (p / 'usr/lib').mkdir(parents=True)
        data = p / 'usr/lib/lib.so'; data.write_bytes(b'abcd')
        entry = dict(path='usr/lib/lib.so', size=4, sha256=a.h.digest(data))
        manifest = p / 'manifest.json'
        def save(entries):
            a.h.write(manifest, dict(version=1, sessionProtocol=1, files=entries))
        save([entry]); self.assertEqual(len(a.b.manifest(manifest)), 1)
        for entries in ([entry, entry], [], [dict(entry, path='generations/id/usr/lib/lib.so')], [dict(entry, path='usr/lib/missing.so')]):
            save(entries)
            with self.assertRaises((ValueError, OSError)):
                a.b.manifest(manifest)
        save([entry]); (p / 'usr/lib/unlisted.so').write_bytes(b'x')
        with self.assertRaisesRegex(ValueError, 'unlisted'):
            a.b.manifest(manifest)

    def test_manifest_comparison_membership(self):
        rows = a.payload_rows(self.raw)
        for mutated in ([], rows + rows):
            with self.assertRaisesRegex(ValueError, 'duplicate/missing'):
                v.check_payloads(mutated, self.raw)

    def test_outer_inventory_cannot_be_nested_manifest(self):
        outer = self.root / 'outer.json'
        a.h.write(outer, {'generations/id/usr/lib/lib.so': dict(sha256='a'*64)})
        with self.assertRaisesRegex(ValueError, 'schema'):
            a.b.manifest(outer)

    def test_matching_payloads_do_not_select_streaming(self):
        self.raw['validation-C'] = copy.deepcopy(self.raw['qualification-C'])
        matrix = a.applicability([], a.payload_rows(self.raw))
        result = a.decision(matrix, self.facts)
        v.check_decision(result, matrix, self.facts)
        self.assertEqual(result['eligible'], [])
        self.assertEqual(matrix[1]['status'], 'exact identity')

    def test_unjustified_timing_reuse_and_candidate_claims(self):
        matrix = a.applicability([], a.payload_rows(self.raw))
        result = a.decision(matrix, self.facts)
        v.check_decision(result, matrix, self.facts)
        for mutate in (lambda d: d['transfers'].update(durations=True), lambda d: d['transfers'].update(p95_subtraction=True),
                       lambda d: d['transfers'].update(sample_percentages=True), lambda d: d.update(eligible=['streaming']),
                       lambda d: d.update(saving_ms=3), lambda d: d['proposals'][1].update(eligible=True),
                       lambda d: d['proposals'][0].update(integrity='Verified saving of 6 ms with skipped checks'),
                       lambda d: d.update(reused='Subtract 3 ms of diagnostics from qualification')):
            changed = copy.deepcopy(result); mutate(changed)
            with self.assertRaises(ValueError):
                v.check_decision(changed, matrix, self.facts)
        self.facts['work'][0]['within_lifetime_repeated_bytes'] = None
        with self.assertRaises(ValueError):
            v.check_decision(result, matrix, self.facts)

    def test_mixed_streaming_contradiction_preserved(self):
        self.facts['value']['negative_blocks'] = 0
        with self.assertRaises(ValueError):
            a.decision([], self.facts)

    def test_resealed_manifest_tampering_fails_semantic_verification(self):
        out = self.root / 'sealed'; out.mkdir()
        rows = a.payload_rows(self.raw)
        rows[0]['status'] = 'exact identity'
        a.h.write(out / 'payloads.json', rows)
        a.h.write(out / 'seal.json', a.h.inventory(out))
        a.h.sealed(out)
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            v.check_payloads(a.h.read(out / 'payloads.json'), self.raw)

    def test_matrix_count_and_unavailable_loading(self):
        rows = a.payload_rows(self.raw)
        matrix = a.applicability([], rows)
        v.check_matrix(matrix, rows)
        matrix[3]['status'] = 'exact identity'
        with self.assertRaises(ValueError):
            v.check_matrix(matrix, rows)

    def test_collision_overlap_drift_and_blocked_seal(self):
        with self.assertRaisesRegex(ValueError, 'collision'):
            a.run(self.root)
        with self.assertRaisesRegex(ValueError, 'overlaps'):
            a.h.fresh(self.root / 'overlap', [self.root])
        out = self.root / 'blocked'
        with patch.object(a.b, 'bind', side_effect=ValueError('missing required retained input')):
            self.assertEqual(a.run(out)['status'], 'blocked')
        self.assertEqual(v.verify(out)['outcome'], 'blocked')
        p = out / 'assessment.json'; p.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'seal/inventory'):
            a.h.sealed(out)
        self.assertFalse(a.h.recheck({}, {str(p): '0'*64}))

    def test_drift_preserves_blocked_partial(self):
        out = self.root / 'drift'
        with patch.object(a.b, 'bind', side_effect=ValueError('stop')), patch.object(a.h, 'recheck', return_value=False):
            result = a.run(out)
        self.assertEqual(result['failure'], 'input/tool drift')
        a.h.sealed(out)
        with self.assertRaisesRegex(ValueError, 'drift'):
            v.verify(out)

    def test_population_mixing_is_rejected_by_exact_retained_membership(self):
        retained = [dict(population='measured', arm='profiled', count=20), dict(population='warmup', count=2)]
        mixed = [dict(population='measured', arm='profiled', count=22)]
        v.check_populations(retained, retained)
        with self.assertRaisesRegex(ValueError, 'population mixing'):
            v.check_populations(mixed, retained)
        matrix = a.applicability([], a.payload_rows(self.raw))
        value = a.decision(matrix, self.facts)
        value['populations'] = 'measured plus warmups'
        with self.assertRaises(ValueError):
            v.check_decision(value, matrix, self.facts)

    def test_qualification_arithmetic_cannot_subtract_diagnostics(self):
        summary = dict(gates=[dict(case='3200x2400.png/startup', event=e, passed=False) for e in ('first_ms', 'final_ms')] +
                       [dict(passed=True) for _ in range(78)], summary={'3200x2400.png/startup': {
                           arm: {e: dict(p95=n) for e in ('first_ms', 'final_ms')} for arm, n in [('A', 127.828), ('C', 142.332)]}})
        with patch.object(a.h, 'read', return_value=summary):
            rows = a.gates()
        with patch.object(v.h, 'read', return_value=summary):
            v.check_gates(rows)
            rows[0]['candidate_p95_ms'] -= 1.4
            with self.assertRaisesRegex(ValueError, 'arithmetic/subtraction'):
                v.check_gates(rows)

    def test_outer_comparison_cannot_invent_sizes(self):
        records = dict(cpu_protected={'current': dict(sha256='c'*64),
                       'generations/id/manifest.json': dict(sha256='d'*64),
                       'generations/id/usr/lib/lib.so': dict(sha256='b'*64)},
                       mechanism_inputs=dict(dependencies={}), mechanism_mappings={})
        rows = a.mapping_rows(self.raw, records)
        self.assertEqual(len(rows), 1)
        v.check_mappings(rows, self.raw, records)
        rows[0]['recorded_size'] = 4
        with self.assertRaisesRegex(ValueError, 'outer/nested'):
            v.check_mappings(rows, self.raw, records)
