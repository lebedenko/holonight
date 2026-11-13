"""Offline preparation contract tests using small, independent frozen packages."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('delivery_overhead', Path(__file__).resolve().parents[1] / 'scripts/prepare-preview-delivery-overhead.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'build').mkdir()
        (self.root / 'scripts').mkdir()
        (self.root / 'tests').mkdir()
        (self.root / '.gitignore').write_text('/build/\n')
        (self.root / 'tests/test_preview_delivery_overhead.py').write_text('# test tool\n')
        self.recipe = self.root / 'scripts/prepare-preview-delivery-tracing.py'
        self.recipe.write_text('HEADER = "\\n// supplemental\\n"\ndef patch(base, header, variant):\n    return []\n')
        self.v3, self.v4, self.out = [self.root / 'build' / n for n in ('old', 'new', 'output')]
        self.v3.mkdir(); self.v4.mkdir()
        self.header = b'  const char* role="setup";\n'
        (self.v3 / 'trace.h').write_bytes(self.header)
        (self.v4 / 'trace.h').write_bytes(self.header.replace(b'  const char* role="setup";', b'  const char* role="setup";\n  unsigned long long delivery_generation=0, delivery_session=0, delivery_transaction=0, delivery_publication=0;\n  const char* delivery_endpoint="unavailable";') + b'\n// supplemental\n')
        self.prep = {'pairs': {}, 'equivalence': {v: {g: [] for g in m.GROUPS} for v in 'ABCD'}}
        self.manifest = dict(status='prepared', unchanged=True, issues=[], before={str(self.recipe): m.digest(self.recipe)}, outputs={}, header_sha256=m.digest(self.v4 / 'trace.h'))
        self.manifest['after'] = dict(self.manifest['before'])
        m.write(self.v4 / 'anchor-review.json', {v: [] for v in 'ABCD'})
        for v in 'ABCD':
            for base in (self.v3 / (v + 'T'), self.v4 / v):
                for g in m.GROUPS:
                    (base / g).mkdir(parents=True)
                    (base / g / 'test.cpp').write_text('// frozen source\n')
            self.prep['pairs'][v + 'T'] = {g: m.inventory(self.v3 / (v + 'T') / g) for g in m.GROUPS}
            m.write(self.v4 / v / 'source-inventory.json', {g: m.inventory(self.v4 / v / g) for g in m.GROUPS})
            m.write(self.v4 / v / 'probe-to-source.json', dict(anchors=[], probes=[]))
        m.write(self.v3 / 'preparation.json', self.prep)
        m.write(self.v3 / 'seal.json', m.inventory(self.v3))
        for name in m.SUPPORT:
            base = self.root / 'build' / name
            base.mkdir()
            state = 'passed' if name == m.SUPPORT[0] else 'complete'
            m.write(base / ('status.json' if name == m.SUPPORT[-1] else 'assessment.json'), dict(status=state))
        self.refresh()
        self.addCleanup(patch.stopall)
        patch.object(m, 'ROOT', self.root).start()
        for name in ('Popen', 'run', 'call', 'check_call', 'check_output'):
            patch.object(subprocess, name, side_effect=AssertionError('process execution forbidden')).start()

    def refresh(self):
        for v in 'ABCD':
            self.manifest['outputs'][v] = m.inventory(self.v4 / v)
        m.write(self.v4 / 'manifest.json', self.manifest)
        review = self.root / 'build' / m.SUPPORT[-1]
        hashes = {str(self.v4): m.inventory(self.v4)}
        for name in m.SUPPORT[:2]:
            base = self.root / 'build' / name
            m.write(base / 'seal.json', {k: v for k, v in m.inventory(base).items() if k != 'seal.json'})
            hashes[str(base)] = m.inventory(base)
        m.write(review / 'integrity.json', dict(before=hashes, after=hashes, unchanged=True))
        for name in m.SUPPORT:
            base = self.root / 'build' / name
            m.write(base / 'seal.json', {k: v for k, v in m.inventory(base).items() if k != 'seal.json'})

    def run_prepare(self):
        return m.prepare(self.v3, self.v4, self.out)

    def assert_sealed(self):
        sealed = json.loads((self.out / 'seal.json').read_text())
        self.assertEqual(sealed, {k: v for k, v in m.inventory(self.out).items() if k != 'seal.json'})

    def test_accepts_eight_source_only_trees_and_seals_every_output(self):
        self.assertEqual(self.run_prepare()['status'], 'prepared')
        self.assert_sealed()
        for mode in ('v3', 'v4'):
            for v in 'ABCD':
                base = self.out / mode / v
                self.assertEqual((base / 'trace.h').read_bytes(), (self.v3 if mode == 'v3' else self.v4).joinpath('trace.h').read_bytes())
                self.assertEqual(set(p.name for p in base.iterdir()), {'trace.h', 'source', 'harness-source', 'source-inventory.json', 'probe-to-source.json'})

    def test_destination_rejections(self):
        for output in (self.v3, self.v3 / 'nested', self.root / 'outside', self.v4.parent):
            with self.subTest(output=output), self.assertRaises(ValueError):
                m.prepare(self.v3, self.v4, output)
        self.out.symlink_to(self.v3, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.run_prepare()

    def test_missing_and_tampered_inputs_leave_sealed_blocked_evidence(self):
        (self.v3 / 'trace.h').unlink()
        self.assertEqual(self.run_prepare()['status'], 'blocked')
        self.assert_sealed()

    def test_tampered_source(self):
        (self.v3 / 'AT/source/test.cpp').write_text('tampered')
        self.assertIn('inventory', self.run_prepare()['issues'][0])
        self.assert_sealed()

    def test_incomplete_inventory(self):
        self.prep['pairs']['AT']['source'] = {}
        m.write(self.v3 / 'preparation.json', self.prep)
        m.write(self.v3 / 'seal.json', {k: v for k, v in m.inventory(self.v3).items() if k != 'seal.json'})
        self.assertIn('inventory', self.run_prepare()['issues'][0])

    def test_header_recipe_error(self):
        (self.v4 / 'trace.h').write_text('wrong header')
        self.manifest['header_sha256'] = m.digest(self.v4 / 'trace.h')
        self.refresh()
        self.assertIn('header recipe', self.run_prepare()['issues'][0])

    def test_probe_error(self):
        m.write(self.v4 / 'A/probe-to-source.json', dict(anchors=[], probes=[dict(file='/outside', line=1, text='bad', sha256='bad')]))
        self.refresh()
        self.assertIn('probe map', self.run_prepare()['issues'][0])

    def test_missing_or_duplicate_anchors(self):
        for text in (b'absent', b'anchor anchor'):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'missing/duplicate'):
                m.replay({'source/a.cpp': text}, [dict(file='source/a.cpp', anchor='anchor', replacement='new', operation='test')])

    def test_replay_mismatch(self):
        (self.v4 / 'A/source/test.cpp').write_text('unauthorized source')
        m.write(self.v4 / 'A/source-inventory.json', {g: m.inventory(self.v4 / 'A' / g) for g in m.GROUPS})
        self.refresh()
        self.assertIn('replay mismatch', self.run_prepare()['issues'][0])

    def test_unauthorized_anchor_even_if_replay_matches(self):
        entry = dict(file='source/test.cpp', anchor='frozen', replacement='changed', operation='unauthorized')
        m.write(self.v4 / 'anchor-review.json', {v: [entry] if v == 'A' else [] for v in 'ABCD'})
        (self.v4 / 'A/source/test.cpp').write_text('// changed source\n')
        m.write(self.v4 / 'A/source-inventory.json', {g: m.inventory(self.v4 / 'A' / g) for g in m.GROUPS})
        m.write(self.v4 / 'A/probe-to-source.json', dict(anchors=[entry], probes=[]))
        self.refresh()
        self.assertIn('unauthorized source differences', self.run_prepare()['issues'][0])

    def test_input_drift_blocks_and_seals(self):
        original = m.shutil.copytree
        def drifting(*args, **kwargs):
            result = original(*args, **kwargs)
            (self.v3 / 'trace.h').write_bytes(self.header + b'// drift\n')
            return result
        with patch.object(m.shutil, 'copytree', side_effect=drifting):
            result = self.run_prepare()
        self.assertEqual(result['status'], 'blocked')
        self.assertIn('consumed inputs changed', result['issues'])
        self.assert_sealed()

    def test_support_seal_tampering(self):
        path = self.root / 'build' / m.SUPPORT[0] / 'assessment.json'
        path.write_text('{}')
        self.assertIn('integrity mismatch', self.run_prepare()['issues'][0])
        self.assert_sealed()

    def test_preparation_state_rejected(self):
        self.manifest['status'] = 'blocked'
        self.refresh()
        self.assertIn('preparation is blocked', self.run_prepare()['issues'][0])

    def test_missing_probe_inventory_entry(self):
        self.manifest['outputs']['A'].pop('probe-to-source.json')
        m.write(self.v4 / 'manifest.json', self.manifest)
        review = self.root / 'build' / m.SUPPORT[-1]
        integrity = json.loads((review / 'integrity.json').read_text())
        integrity['before'][str(self.v4)] = m.inventory(self.v4)
        integrity['after'] = integrity['before']
        m.write(review / 'integrity.json', integrity)
        m.write(review / 'seal.json', {k: v for k, v in m.inventory(review).items() if k != 'seal.json'})
        self.assertIn('output inventory mismatch', self.run_prepare()['issues'][0])

    def test_added_input_file_during_preparation_blocks(self):
        original = m.shutil.copytree
        def drifting(*args, **kwargs):
            result = original(*args, **kwargs)
            (self.v3 / 'AT/source/added.cpp').write_text('// drift')
            return result
        with patch.object(m.shutil, 'copytree', side_effect=drifting):
            result = self.run_prepare()
        self.assertTrue(any('input tree drift' in issue for issue in result['issues']))
        self.assert_sealed()

    def test_exact_schedule_counts_and_order(self):
        rows = m.schedule()
        self.assertEqual(len(rows), 264)
        self.assertEqual(sum(r['observations'] for r in rows if not r['warmup']), 2400)
        self.assertEqual(sum(r['observations'] for r in rows if r['warmup']), 24)
        for fixture_index, fixture in enumerate(('160x80.png', '3200x2400.png', 'oriented.jpg')):
            group = rows[fixture_index * 88:(fixture_index + 1) * 88]
            self.assertTrue(all(r['fixture'] == fixture for r in group))
            self.assertEqual([(r['variant'], r['mode']) for r in group[:8]], [(v, mode) for v in 'ABCD' for mode in ('v3', 'v4')])
            for block in range(10):
                rotation = block % 4
                variants = 'ABCD'[rotation:] + 'ABCD'[:rotation]
                modes = ('v3', 'v4') if block % 2 == 0 else ('v4', 'v3')
                actual = group[8 + block * 8:16 + block * 8]
                self.assertEqual([(r['variant'], r['mode']) for r in actual], [(v, mode) for v in variants for mode in modes])
                self.assertTrue(all(r['block'] == block and not r['warmup'] and r['observations'] == 10 for r in actual))


if __name__ == '__main__':
    unittest.main()
