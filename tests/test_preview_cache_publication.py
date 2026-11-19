"""Offline preparation and event-contract regressions. Process execution forbidden."""
import copy
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


p = load('cache_test_prepare', 'prepare-preview-cache-publication.py')
v = load('cache_test_verify', 'verify-preview-cache-publication.py')


def events(invocation, overlap=True):
    context = dict(invocation=str(invocation), service='service', request='request', worker='worker',
        preparation='preparation', transaction='1', source='verified-source', width=256, height=256,
        generation='1', original_decode=True, tier=256, outcome=0)
    times = dict(eligible=1, store_entry=3, store_return=8, enqueue=2 if overlap else 9,
                 accepted=4 if overlap else 10, adequate=5 if overlap else 11, final=12)
    return [dict(context, event=name, ns=time) for name, time in times.items()]


def population(overlap=True):
    return [dict(schedule=row, events=events(row['index'], overlap and row['arm'] == 'early'),
        correct_pixels=True, correct_metadata=True, cache_available_at_final=True,
        cleanup_passed=True, native_bindings_passed=True) for row in p.e.schedule()]


class CachePublicationTests(unittest.TestCase):
    def setUp(self):
        for name in ('Popen', 'run', 'check_output', 'check_call'):
            guard = patch.object(subprocess, name, side_effect=AssertionError('process execution forbidden'))
            guard.start()
            self.addCleanup(guard.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'build').mkdir()
        self.q = self.root / 'qualification'
        actual_q = p.e.Q
        for name in (p.e.SERVICE, p.e.RUNTIME):
            path = self.q / 'C/source' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((actual_q / 'C/source' / name).read_bytes())
        (self.q / 'C/source/extra.txt').write_text('unchanged source membership\n')
        (self.q / 'harness-source').mkdir()
        (self.q / 'harness-source/reuse.cpp').write_bytes((actual_q / 'harness-source/reuse.cpp').read_bytes())
        fixture = self.root / '3200x2400.png'
        fixture.write_bytes(b'synthetic fixture, never decoded')
        inputs = dict(source=p.h.inventory(self.q / 'C/source'), harness=p.h.inventory(self.q / 'harness-source'),
            fixture=dict(path=str(fixture), sha256=p.h.digest(fixture)),
            files={str(fixture): p.h.digest(fixture)}, inventories={str(self.q): p.h.inventory(self.q)})
        for module in (p, v):
            for owner, attr, value in [(module.e, 'ROOT', self.root), (module.e, 'Q', self.q),
                                       (module.h, 'ROOT', self.root)]:
                guard = patch.object(owner, attr, value)
                guard.start()
                self.addCleanup(guard.stop)
            guard = patch.object(module.e, 'retained', return_value=inputs)
            guard.start()
            self.addCleanup(guard.stop)
        # Snapshot real tools without following the synthetic ROOT into nonexistent scripts.
        tools = {str(ROOT / 'scripts' / name): p.h.digest(ROOT / 'scripts' / name) for name in
                 ('prepare-preview-cache-publication.py', 'verify-preview-cache-publication.py')}
        for module in (p, v):
            guard = patch.object(module.e, 'snapshots', return_value=tools)
            guard.start()
            self.addCleanup(guard.stop)
        self.output = self.root / 'build/preview-cache-publication-test'

    def prepare(self):
        self.assertEqual(p.prepare(self.output)['status'], 'prepared')
        self.assertEqual(v.verify(self.output)['outcome'], 'prepared')

    def reseal(self):
        inventory = p.h.inventory(self.output)
        inventory.pop('seal.json', None)
        p.h.write(self.output / 'seal.json', inventory)

    def test_protocol_schedule_and_roundtrip(self):
        self.assertEqual(p.e.protocol(), v.protocol())
        self.assertEqual(len(p.e.schedule()), 12)
        self.assertEqual(sum(r['warmup'] for r in p.e.schedule()), 2)
        self.prepare()

    def test_anchor_mismatch_seals_blocked_result(self):
        path = self.q / 'C/source' / p.e.SERVICE
        path.write_text(path.read_text().replace('struct PreviewResult {', 'struct Changed {'))
        # Capture the deliberate synthetic input before preparation.
        inputs = p.e.retained()
        inputs['source'] = p.h.inventory(self.q / 'C/source')
        inputs['inventories'] = {str(self.q): p.h.inventory(self.q)}
        self.assertEqual(p.prepare(self.output)['status'], 'blocked')
        self.assertEqual(v.verify(self.output)['outcome'], 'blocked')

    def test_resealed_source_and_duplicate_publication_rejected(self):
        self.prepare()
        path = self.output / 'early/source' / p.e.SERVICE
        original = path.read_text()
        for changed in (original + '\n// unrelated\n', original.replace('    publish(progressive);',
                                      '    publish(progressive);\n    publish(progressive);')):
            path.write_text(changed)
            self.reseal()
            with self.assertRaises(ValueError):
                v.verify(self.output)
        path.write_text(original)

    def test_inventory_and_package_membership_drift_rejected(self):
        self.prepare()
        path = self.output / 'early/source/extra.txt'
        path.write_text('changed')
        with self.assertRaises(ValueError):
            v.verify(self.output)
        self.reseal()
        with self.assertRaises(ValueError):
            v.verify(self.output)

    def test_resealed_protocol_and_zero_execution_tampering_rejected(self):
        self.prepare()
        for filename, key, value in [('protocol.json', 'retries', 1),
                                      ('assessment.json', 'executed_commands', ['build'])]:
            path = self.output / filename
            original = path.read_text()
            data = p.h.read(path)
            data[key] = value
            p.h.write(path, data)
            self.reseal()
            with self.assertRaises(ValueError):
                v.verify(self.output)
            path.write_text(original)
        self.reseal()

    def test_collision_overlap_and_symlink_rejected(self):
        self.prepare()
        with self.assertRaises(ValueError):
            p.prepare(self.output)
        with self.assertRaises(ValueError):
            p.prepare(self.q / 'nested')
        escape = self.root / 'build/preview-cache-publication-escape'
        escape.symlink_to(self.q, target_is_directory=True)
        with self.assertRaises(ValueError):
            p.prepare(escape)
        link = self.output / 'early/source/link'
        link.symlink_to(self.q / 'C/source/extra.txt')
        with self.assertRaises(ValueError):
            v.verify(self.output)

    def test_conflicting_binding_is_rejected(self):
        with self.assertRaises(ValueError):
            p.e.s.r.merge({'same': 'old'}, {'same': 'new'})

    def test_retained_discrepancy_seals_blocked_output(self):
        with patch.object(p.e, 'retained', side_effect=ValueError('consumed hash mismatch')):
            self.assertEqual(p.prepare(self.output)['status'], 'blocked')
        self.assertEqual(v.verify(self.output)['outcome'], 'blocked')
        (self.output / 'workload.json').write_text('{}')
        self.reseal()
        with self.assertRaises(ValueError):
            v.verify(self.output)

    def test_overlap_and_no_overlap(self):
        self.assertEqual(v.outcome(population()), 'overlap observed')
        self.assertEqual(v.outcome(population(False)), 'overlap not observed in this population')

    def test_interval_boundary_equality_is_not_support(self):
        for boundary in (3, 8):
            rows = population()
            for row in rows:
                if row['schedule']['arm'] == 'early':
                    for event in row['events']:
                        if event['event'] == 'accepted': event['ns'] = boundary
                        if event['event'] == 'adequate': event['ns'] = boundary
            self.assertEqual(v.outcome(rows), 'overlap not observed in this population')

    def test_invalid_identity_delivery_and_final_order(self):
        for key, value in [('request', 'wrong'), ('transaction', 'wrong'), ('preparation', ''),
                           ('cancelled', True), ('stale', True), ('ns', 0)]:
            rows = population()
            row = next(r for r in rows if not r['schedule']['warmup'] and r['schedule']['arm'] == 'early')
            event = next(e for e in row['events'] if e['event'] == ('final' if key == 'ns' else 'adequate'))
            event[key] = value
            self.assertEqual(v.outcome(rows), 'Evidence insufficient', key)

    def test_incomplete_schedule_correctness_cleanup_and_warmup_exclusion(self):
        self.assertEqual(v.outcome(population()[:-1]), 'Evidence insufficient')
        for key in ('correct_pixels', 'correct_metadata', 'cleanup_passed',
                    'cache_available_at_final', 'native_bindings_passed'):
            rows = population()
            rows[3][key] = False
            self.assertEqual(v.outcome(rows), 'Evidence insufficient')
        rows = population(False)
        rows[1]['events'] = events(1, True)
        self.assertEqual(v.outcome(rows), 'overlap not observed in this population')
        rows[2]['events'] = copy.deepcopy(rows[0]['events'])
        self.assertEqual(v.outcome(rows), 'Evidence insufficient')


if __name__ == '__main__':
    unittest.main()
