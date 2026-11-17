"""Synthetic review contracts with process execution disabled."""
import copy
import importlib.util
import os
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


a = module('review_assessor_test', 'assess-preview-identity-review.py')
v = module('review_verifier_test', 'verify-preview-identity-review.py')
e = a.e
h = e.h


def observations():
    return [dict(schedule=s, sample=dict(first_ms=100000 if s['warmup'] else s['sample'] + 5 * s['block'],
        final_ms=200000 if s['warmup'] else s['sample'] + 5 * s['block'] + 10),
        authorization_seconds=99999, identities=None) for s in v.schedule()]


class ReviewTests(unittest.TestCase):
    def setUp(self):
        for target in ((subprocess, 'Popen'), (os, 'system'), (os, 'posix_spawn')):
            guard = patch.object(*target, side_effect=AssertionError('process execution forbidden'))
            guard.start()
            self.addCleanup(guard.stop)

    def test_populations_exclude_warmup_and_authorization(self):
        p, b, s = a.timing(observations())
        v.check_timing(observations(), p, b, s)
        self.assertEqual(len(p), 4)
        self.assertEqual(len(b), 20)
        self.assertEqual(p['C/captured']['first_ms'], dict(count=25, median=12, p95=23))
        self.assertTrue(all(r['zero'] == 5 for r in s))

    def test_block_directions_and_capture_separation(self):
        obs = observations()
        for row in obs:
            s = row['schedule']
            if s['variant'] == 'C' and not s['warmup']:
                delta = [1, -1, 0, 2, -2][s['block']] * (2 if s['captured'] else 1)
                for event in ('first_ms', 'final_ms'):
                    row['sample'][event] += delta
        p, b, s = a.timing(obs)
        v.check_timing(obs, p, b, s)
        self.assertTrue(all((r['positive'], r['negative'], r['zero']) == (2, 2, 1) for r in s))
        b[0]['C_minus_A_fixed_median'] *= -1
        with self.assertRaises(ValueError):
            v.check_timing(obs, p, b, s)

    def test_schedule_mixing(self):
        obs = observations()
        values = a.timing(obs)
        obs[0]['schedule']['warmup'] = False
        with self.assertRaises(ValueError):
            v.check_timing(obs, *values)

    def test_nearest_rank_is_not_interpolation(self):
        values = a.timing(observations())
        values[0]['C/captured']['first_ms']['p95'] = 22.8
        with self.assertRaises(ValueError):
            v.check_timing(observations(), *values)

    def test_content_identity_requires_digest(self):
        left = dict(size=10, build_id='same', sha256='a')
        right = dict(size=10, build_id='same', sha256='b')
        self.assertEqual(e.identity_status(left, right), 'different bytes')
        self.assertEqual(e.identity_status(left, dict(size=10, build_id='same')), 'unavailable')
        self.assertEqual(e.identity_status(left, dict(sha256='a')), 'exact content')

    def test_alias_ambiguity_is_explicit(self):
        rows = [dict(path='/usr/lib/libQt6Core.so.6', sha256='a'),
                dict(path='/other/libQt6Core.so.6.12.0', sha256='b')]
        self.assertEqual(e.correspond('/usr/lib/libQt6Core.so.6.12.0', rows)[1], 'ambiguous')
        self.assertEqual(e.correspond('/usr/lib/libQt6Core.so.6', rows)[1], 'exact path')
        self.assertEqual(e.correspond('/usr/lib/libQt6Core.so.6.12.0', rows[:1])[1], 'alias candidate')
        self.assertEqual(e.correspond('/usr/lib/absent.so', rows)[1], 'unavailable')

    def test_scope_and_per_observation_membership(self):
        identity = dict(size=10, sha256='a', build_id='id')
        ledgers = {'A-fixed': {'desktop:/lib/x.so': identity, 'sandbox:/lib/x.so': identity}, 'C': {}}
        obs = [dict(schedule=dict(variant='A-fixed', captured=True, invocation=1, warmup=True), identities=dict(
            mappings=[dict(scope='desktop', path='/lib/x.so', pid=1, start=2, namespace='n', event_index=1, **identity)])),
            dict(schedule=dict(variant='A-fixed', captured=True, invocation=5, warmup=False), identities=dict(mappings=[]))]
        rows = e.dependencies(obs, ledgers, [])
        self.assertEqual([len(r['observations']) for r in rows], [1, 0])
        self.assertEqual(rows[0]['observations'][0]['processes'][0]['pid'], 1)
        self.assertEqual(rows[0]['historical_correspondences'], [])

    def test_conflicting_bindings(self):
        with self.assertRaises(ValueError):
            e.merge({'file': 'a'}, {'file': 'b'})

    def test_all_proposals_require_existing_gaps(self):
        historical = dict(decision='Evidence insufficient', eligible=[], proposals=[dict(name=str(i),
            disposition='deferred', eligible=False, mechanism='unproven', applicability='partial',
            integrity='unproven', contradictory_evidence='unresolved') for i in range(3)])
        decision = a.decision(historical)
        v.check_decision(decision, historical)
        for key, value in [('eligible', ['streaming']), ('ranking', ['SHA-256']), ('experiment', 'new')]:
            altered = copy.deepcopy(decision)
            altered[key] = value
            with self.assertRaises(ValueError):
                v.check_decision(altered, historical)

    def test_collision_overlap_and_drift(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                h.fresh(root, [])
            with self.assertRaises(ValueError):
                h.fresh(root / 'child', [root])
            p = root / 'input'
            p.write_text('original')
            inventory = h.inventory(root)
            h.write(root / 'seal.json', inventory)
            h.sealed(root)
            p.write_text('changed')
            self.assertFalse(h.recheck({}, {str(p): inventory['input']}))
            with self.assertRaises(ValueError):
                h.sealed(root)

    def test_resealed_timing_tampering(self):
        # Independent arithmetic still rejects claims after a valid replacement seal.
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as tmp:
            root = Path(tmp)
            p, b, s = a.timing(observations())
            p['C/captured']['first_ms']['median'] = 500
            h.write(root / 'population-statistics.json', p)
            h.write(root / 'seal.json', h.inventory(root))
            h.sealed(root)
            with self.assertRaises(ValueError):
                v.check_timing(observations(), h.read(root / 'population-statistics.json'), b, s)

    def test_verification_must_bind_the_accepted_seal(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as tmp:
            root = Path(tmp) / 'evidence'
            root.mkdir()
            h.write(root / 'assessment.json', dict(status='complete'))
            h.write(root / 'seal.json', h.inventory(root))
            record = root.with_name(root.name + '-independent.json')
            h.write(record, dict(status='passed', outcome='complete', evidence_seal='foreign seal'))
            with self.assertRaises(ValueError):
                e.accepted(root, 'complete', 'evidence_seal')
            h.write(record, dict(status='passed', outcome='complete', evidence_seal=h.digest(root / 'seal.json')))
            e.accepted(root, 'complete', 'evidence_seal')

    def test_full_review_and_resealed_claim_rejection(self):
        from contextlib import ExitStack
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as tmp, ExitStack() as stack:
            root = Path(tmp)
            source = root / 'source'
            source.mkdir()
            obs = observations()
            for row in obs:
                if row['schedule']['captured']:
                    row['identities'] = dict(mappings=[])
            historical = dict(decision='Evidence insufficient', eligible=[], proposals=[dict(name=str(i),
                disposition='deferred', eligible=False, mechanism='unproven', applicability='partial',
                integrity='unproven', contradictory_evidence='unresolved') for i in range(3)])
            for name, value in [('observations', obs), ('ledgers', {'A-fixed': {}, 'C': {}}),
                    ('decision', historical), ('matrix', [])]:
                h.write(source / (name + '.json'), value)
            inputs = dict(inventories={str(source): h.inventory(source)}, files={})
            for evidence in (a.e, v.e):
                for name, value in [('EXECUTION', source), ('AUDIT', source), ('RECONCILIATION', source)]:
                    stack.enter_context(patch.object(evidence, name, value))
                stack.enter_context(patch.object(evidence, 'bind', return_value=inputs))
                stack.enter_context(patch.object(evidence, 'protected', return_value=[source]))
                stack.enter_context(patch.object(evidence, 'historical', return_value=[]))
            output = root / 'review'
            self.assertEqual(a.run(output)['status'], 'complete')
            self.assertEqual(v.verify(output)['status'], 'passed')
            decision = h.read(output / 'proposal-decisions.json')
            decision['proposals'][0]['review'] = 'Streaming is eligible'
            h.write(output / 'proposal-decisions.json', decision)
            seal = h.inventory(output)
            del seal['seal.json']
            h.write(output / 'seal.json', seal)
            h.sealed(output)
            with self.assertRaises(ValueError):
                v.verify(output)

    def test_verifier_import_boundary(self):
        text = (ROOT / 'scripts/verify-preview-identity-review.py').read_text()
        self.assertNotIn('assess-preview-identity-review.py', text)
        self.assertNotIn('run-preview-identity-baseline.py', text)


if __name__ == '__main__':
    unittest.main()
