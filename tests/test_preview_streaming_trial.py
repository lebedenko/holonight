"""Trial arithmetic and integrity regressions; process execution is forbidden."""
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


runner = load('trial_test_runner', 'run-preview-streaming-trial.py')
verifier = load('trial_test_verifier', 'verify-preview-streaming-trial.py')
e, h = runner.e, runner.h


def observations(candidate=95, median_regression=False):
    rows = []
    for entry in runner.schedule():
        value = 100 if entry['arm'] == 'control' else candidate
        if entry['warmup']: value = 1000000
        if median_regression and entry['arm'] == 'control' and entry['observation'] < 6: value = 90
        rows.append(dict(schedule=entry, sample=dict(first_ms=value, final_ms=value + 10)))
    return rows


class TrialTests(unittest.TestCase):
    def setUp(self):
        for name in ('Popen', 'run', 'check_output', 'check_call'):
            guard = patch.object(subprocess, name, side_effect=AssertionError('process execution forbidden'))
            guard.start()
            self.addCleanup(guard.stop)

    def test_schedule_fresh_process_count_and_alternation(self):
        rows = runner.schedule()
        self.assertEqual(rows, verifier.schedule())
        self.assertEqual(len(rows), 202)
        self.assertTrue(all(r['count'] == 1 for r in rows))
        self.assertEqual(sum(r['warmup'] for r in rows), 2)
        for block in range(10):
            selected = [r for r in rows if r['block'] == block]
            arms = ['control', 'candidate'] if block % 2 == 0 else ['candidate', 'control']
            self.assertEqual([r['arm'] for r in selected], [arms[0]] * 10 + [arms[1]] * 10)

    def test_warmup_exclusion_quantiles_and_block_signs(self):
        rows = observations()
        summary = runner.summarize(rows, True)
        self.assertEqual(summary, verifier.statistics(rows, True))
        self.assertEqual(summary['populations']['control']['first_ms'], dict(count=100, median=100, p95=100))
        self.assertTrue(all(r['negative'] == 10 for r in summary['signs']))
        for row in rows:
            if not row['schedule']['warmup']:
                value = (row['schedule']['block'] * 10 + row['schedule']['observation'])
                row['sample'] = dict(first_ms=value, final_ms=value + 10)
        summary = runner.summarize(rows, True)
        self.assertEqual(summary, verifier.statistics(rows, True))
        self.assertEqual(summary['populations']['control']['first_ms'], dict(count=100, median=49.5, p95=94))
        self.assertTrue(all(r['zero'] == 10 for r in summary['signs']))

    def test_decision_boundaries_and_median_regression(self):
        for value, regression, decision in ((95, False, 'Recommend later production work'),
                (95.000001, False, 'Deferred'), (94, True, 'Deferred'), (100, False, 'Deferred')):
            with self.subTest(value=value, regression=regression):
                rows = observations(value, regression)
                summary = runner.summarize(rows, True)
                self.assertEqual(summary['decision'], decision)
                self.assertEqual(summary, verifier.statistics(rows, True))
        self.assertEqual(runner.summarize(observations()[:100], False)['decision'], 'Evidence insufficient')

    def test_both_endpoints_must_pass(self):
        rows = observations()
        for row in rows:
            if row['schedule']['arm'] == 'candidate': row['sample']['final_ms'] += 1
        self.assertEqual(runner.summarize(rows, True)['decision'], 'Deferred')

    def test_conflicting_bindings(self):
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            e.r.merge({'same': 'old'}, {'same': 'new'})

    def test_collision_and_overlap_do_not_modify_inputs(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temp:
            root = Path(temp)
            existing = root / 'existing'
            existing.mkdir()
            (existing / 'sentinel').write_text('preserved')
            with self.assertRaisesRegex(ValueError, 'collision'):
                h.fresh(existing, [])
            with self.assertRaisesRegex(ValueError, 'overlap'):
                h.fresh(existing / 'nested', [existing])
            self.assertEqual((existing / 'sentinel').read_text(), 'preserved')

    def test_protocol_tampering(self):
        verifier.check_protocol(runner.protocol())
        for key, value in (('recording', True), ('jobs', 8), ('workload_seconds', 31), ('shared_cleanup_seconds', 10)):
            protocol = copy.deepcopy(runner.protocol())
            protocol[key] = value
            with self.assertRaisesRegex(ValueError, 'protocol'):
                verifier.check_protocol(protocol)

    def test_resealed_tool_snapshot_tampering(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temp:
            root = Path(temp)
            (root / 'tools').mkdir()
            tool = root / 'tools/installer.py'
            tool.write_text('frozen installer')
            expected = {'/trusted/installer.py': h.digest(tool)}
            h.write(root / 'tools.json', expected)
            with patch.object(e, 'tools', return_value=expected):
                e.check_tools(root)
                tool.write_text('tampered installer')
                h.write(root / 'seal.json', h.inventory(root))
                h.sealed(root)
                with self.assertRaisesRegex(ValueError, 'snapshot drift'):
                    e.check_tools(root)

    def test_invalid_samples_rejected(self):
        valid = dict(samples=[dict(success=True, setup_success=True, correct_pixels=True,
                     correct_metadata=True, first_ms=1, final_ms=2)])
        self.assertEqual(e.sample(valid), valid['samples'][0])
        for key, value in (('correct_pixels', False), ('final_ms', float('nan')), ('first_ms', 3), ('cleanup_failure', True)):
            data = copy.deepcopy(valid)
            data['samples'][0][key] = value
            with self.assertRaises(ValueError): e.sample(data)

    def test_drift_and_resealed_source_tampering(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temp:
            root = Path(temp)
            origin, package = root / 'qualification', root / 'package'
            (origin / 'C/source').mkdir(parents=True)
            (origin / 'harness-source').mkdir()
            original = '  for (auto value : manifest["files"].toArray()) {\n!hash.addData(&file)\n'
            source = origin / 'C/source' / e.RELATIVE
            source.parent.mkdir(parents=True)
            source.write_text(original)
            (origin / 'harness-source/main.cpp').write_text('frozen harness')
            package.mkdir()
            (package / 'tools').mkdir()
            loop = (ROOT / 'tooling/preview-streaming-trial/hash-loop.inc').read_text()
            (package / 'tools/hash-loop.inc').write_text(loop)
            for arm in e.ARMS:
                import shutil
                shutil.copytree(origin / 'C/source', package / arm / 'source')
                shutil.copytree(origin / 'harness-source', package / arm / 'harness-source')
            candidate = package / 'candidate/source' / e.RELATIVE
            candidate.write_text(e.transformed(original, loop))
            import difflib
            (package / 'candidate.diff').write_text(''.join(difflib.unified_diff(
                original.splitlines(True), candidate.read_text().splitlines(True),
                fromfile='control/' + e.RELATIVE, tofile='candidate/' + e.RELATIVE)))
            (package / '3200x2400.png').write_bytes(b'fixture')
            inputs = dict(inventories={}, files={}, source=h.inventory(origin / 'C/source'),
                harness=h.inventory(origin / 'harness-source'), fixture=dict(sha256=h.digest(package / '3200x2400.png')))
            h.write(package / 'inputs.json', inputs)
            h.write(package / 'tools.json', {})
            h.write(package / 'assessment.json', dict(status='prepared'))
            def seal():
                if (package / 'seal.json').exists():
                    # Replace only this synthetic fixture's prior seal.
                    inventory = h.inventory(package)
                    inventory.pop('seal.json')
                else: inventory = h.inventory(package)
                h.write(package / 'seal.json', inventory)
            seal()
            with patch.object(e, 'Q', origin), patch.object(e, 'tools', return_value={}):
                e.check_package(package)
                candidate.write_text(candidate.read_text().replace('info.st_size', '0'))
                with self.assertRaisesRegex(ValueError, 'seal'): e.check_package(package)
                seal()
                with self.assertRaisesRegex(ValueError, 'transformation'): e.check_package(package)


if __name__ == '__main__':
    unittest.main()
