"""Behavioral selection protocol regressions. Real processes are forbidden."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
DIRECTORY = Path(__file__).resolve().parents[1] / 'tooling/preview-cache-publication-trial'
# Other historical test modules use these generic module names; isolate import resolution.
previous = {name: sys.modules.pop(name) for name in ('correctness', 'qualify', 'stage') if name in sys.modules}
sys.path.insert(0, str(DIRECTORY))
spec = importlib.util.spec_from_file_location('publication_trial_controller', DIRECTORY / 'execute.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
sys.path.remove(str(DIRECTORY))
for name in ('correctness', 'qualify', 'stage'):
    sys.modules.pop(name, None)
sys.modules.update(previous)
t, v, h = d.t, d.v, d.h


class TrialTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(subprocess, 'Popen', side_effect=AssertionError('real process forbidden')))
        self.enterContext(patch.object(subprocess, 'run', side_effect=AssertionError('real process forbidden')))
        temporary = tempfile.TemporaryDirectory(dir=t.ROOT / 'build')
        self.addCleanup(temporary.cleanup)
        self.enterContext(patch('builtins.print'))
        self.parent = Path(temporary.name)
        self.root = self.parent / 'attempt'
        self.built = self.parent / 'built'
        self.correctness = self.parent / 'correctness'
        self.enterContext(patch.object(t, 'BUILT', self.built))
        self.enterContext(patch.object(t, 'EXECUTION', self.root))

    def rows(self, first=20, final=30, gain=5):
        return [dict(schedule=s, sample=dict(first_ms=first - (gain if s['arm'] == 'early' else 0),
            final_ms=final - (gain if s['arm'] == 'early' else 0))) for s in t.schedule()]

    def test_gate_includes_both_endpoints_and_exact_boundary(self):
        for gain, decision in [(5, 'Recommend'), (4.999999, 'Deferred'), (0, 'Deferred'), (-1, 'Deferred')]:
            rows = self.rows(gain=gain)
            self.assertEqual(t.statistics_for(rows, True)['decision'], decision)
            self.assertEqual(t.statistics_for(rows, True), v.summarize(rows, True))
        rows = self.rows()
        for r in rows:
            if r['schedule']['arm'] == 'early':
                r['sample']['final_ms'] = 30
        self.assertEqual(v.summarize(rows, True)['decision'], 'Deferred')

    def test_median_regression_disqualifies_good_p95(self):
        rows = self.rows(first=100, final=200, gain=10)
        for arm in t.ARMS:
            measured = [r for r in rows if r['schedule']['arm'] == arm and not r['schedule']['warmup']]
            for r in measured[:60]:
                r['sample'] = dict(first_ms=1 if arm == 'control' else 2, final_ms=101 if arm == 'control' else 102)
        self.assertEqual(v.summarize(rows, True)['decision'], 'Deferred')

    def test_warmups_excluded_and_nearest_rank_is_95(self):
        rows = self.rows()
        rows[0]['sample'] = dict(first_ms=20000, final_ms=30000)
        for arm in t.ARMS:
            measured = [r for r in rows if r['schedule']['arm'] == arm and not r['schedule']['warmup']]
            for i, r in enumerate(measured):
                r['sample'] = dict(first_ms=i + 1, final_ms=i + 101)
        result = v.summarize(rows, True)
        self.assertEqual(result['populations']['control']['first_ms'], dict(count=100, median=50.5, p95=95))
        self.assertEqual(result, t.statistics_for(rows, True))
        self.assertEqual(v.summarize(rows[:-1], True)['decision'], 'Evidence insufficient')
        self.assertEqual(v.summarize(rows, False)['decision'], 'Evidence insufficient')

    def test_malformed_samples_are_rejected(self):
        for value in (True, float('nan'), float('inf'), -1, '3', None, 30001):
            rows = self.rows()
            rows[2]['sample']['first_ms'] = value
            with self.assertRaises((ValueError, TypeError)):
                v.summarize(rows, True)
            with self.assertRaises((ValueError, TypeError)):
                t.statistics_for(rows, True)

    def test_full_schedule_and_resealed_tampering(self):
        self.root.mkdir()
        rows = d.schedule(self.built, self.root)
        h.write(self.root / 'schedule.json', rows)
        self.assertEqual(v.verify_schedule(self.root, self.built), rows)
        workloads = [r for r in rows if r['workload']]
        self.assertEqual(len(workloads), 202)
        for block in range(10):
            arms = [r['observation']['arm'] for r in workloads if r['observation']['block'] == block]
            self.assertEqual(arms, [a for a in (t.ARMS if block % 2 == 0 else t.ARMS[::-1]) for _ in range(10)])
        for key, value in [('timeout_seconds', 600), ('privileged', True), ('launch', dict(process_group=0))]:
            original = workloads[0][key]
            workloads[0][key] = value
            h.write(self.root / 'schedule.json', rows)
            h.write(self.root / 'seal.json', {'schedule.json': h.digest(self.root / 'schedule.json')})
            with self.assertRaises(ValueError):
                v.verify_schedule(self.root, self.built)
            workloads[0][key] = original

    def test_only_permitted_source_change_survives_reverse_validation(self):
        original = (t.Q / 'C/source' / t.SERVICE).read_text()
        candidate = t.transform(original)
        self.assertEqual(candidate.replace(t.AFTER, t.BEFORE).replace(t.NEW_TAIL, t.TAIL), original)
        self.assertNotIn('cachePublication', candidate)
        with self.assertRaises(ValueError):
            t.transform(candidate)
        # Complete source comparison catches an unrelated mutation after allowed edits reverse.
        tampered = candidate.replace('ThumbnailService::storeRaster', 'ThumbnailService::lookupRaster')
        self.assertNotEqual(tampered.replace(t.AFTER, t.BEFORE).replace(t.NEW_TAIL, t.TAIL), original)

    def test_correctness_preserves_all_130_checks_and_commands(self):
        self.root.mkdir()
        rows = d.qualify.schedule(self.built, self.root)
        h.write(self.root / 'schedule.json', rows)
        verifier = t.e.load('trial_correctness_schedule_test', DIRECTORY / 'offline/verify_correctness.py')
        self.assertEqual(verifier.verify_schedule(self.root, self.built, d.c.protocol()), rows)
        self.assertEqual(len(rows), 55)
        self.assertEqual(sum(len(row['cases']) for row in rows), 130)
        self.assertEqual(d.c.protocol()['ordinary'], h.read(t.HISTORICAL / 'CORRECTNESS-v4.json')['ordinary'])

    def synthetic(self, stop=None, timeout=False, cleanup_failure=False, mutation=None):
        self.built.mkdir()
        for arm in t.ARMS:
            binary = self.built / arm / 'harness-build/preview-benchmark'
            binary.parent.mkdir(parents=True)
            binary.write_text('unexecutable synthetic binary')
            runtime = self.built / arm / 'runtime'
            runtime.mkdir()
            (runtime / 'payload').write_text('identical synthetic payload')
        h.write(self.built / 'seal.json', h.inventory(self.built))
        binding = dict(historical=dict(diagnostic=dict(fixture=dict(sha256=h.digest(t.e.PACKAGE / '3200x2400.png')))),
            built=dict(path=str(self.built), seal=h.digest(self.built / 'seal.json')), correctness={})
        built_binding = dict(binding['built'], inventory=h.sealed(self.built))
        self.enterContext(patch.object(v, 'prerequisite', return_value=binding))
        self.enterContext(patch.object(d.c, 'built_binding', return_value=built_binding))
        self.enterContext(patch.object(d.c, 'tree', side_effect=lambda runtime: h.read(self.root / (str(runtime).split('-')[-1] + '-staging.json'))['tree']))
        self.enterContext(patch.object(d, 'validate_request'))
        clean = dict(isolated=True, exit=0, stdout='', stderr='', cgroups=[])
        calls = []
        def scopes(env, deadline):
            calls.append(env)
            return dict(clean, isolated=False) if cleanup_failure and len(calls) == 2 else clean
        self.enterContext(patch.object(d.qualify, 'scopes', side_effect=scopes))
        loader = t.e.load
        self.enterContext(patch.object(t.e, 'load', side_effect=lambda name, path:
            SimpleNamespace(terminate=lambda *a, **k: None) if name == 'observation_cleanup' else loader(name, path)))
        self.enterContext(patch.object(os, 'killpg', side_effect=ProcessLookupError))
        staged = set()
        lexists = os.path.lexists
        self.enterContext(patch.object(os.path, 'lexists', side_effect=lambda p: str(p) in staged or lexists(p)))
        executable = Path(sys.executable).resolve()
        self.enterContext(patch.object(v.support, 'linkage', return_value={str(executable): h.digest(executable)}))
        def mapping(path):
            info = path.stat()
            return f'1-2 r-xp 0 {os.major(info.st_dev):x}:{os.minor(info.st_dev):x} {info.st_ino} {path}\n'
        def launch(argv, **kwargs):
            name = Path(kwargs['stdout'].name).name.removesuffix('.stdout')
            row = h.read(self.root / 'commands' / (name + '-command.json'))
            arm = row['arm']
            if name not in (stop if isinstance(stop, set) else {stop}):
                if name.endswith('-stage'):
                    runtime = v.protected_path(self.root, arm)
                    staged.add(str(runtime))
                    tree = {'generations/g/' + n: dict(uid=0, mode=0o644, sha256=sha)
                        for n, sha in h.inventory(self.built / arm / 'runtime').items()}
                    tree['generations/g'] = dict(uid=0, mode=0o755, sha256=None)
                    h.write(self.root / (arm + '-staging.json'), dict(runtime=str(runtime), tree=tree,
                        owner=dict(output=str(self.root), arm=arm, **binding['built'])))
                    owner = h.read(self.root / (arm + '-staging.json'))['owner']
                    owner['built'] = owner.pop('path')
                    h.write(self.root / (arm + '-staging.json'), dict(runtime=str(runtime), tree=tree, owner=owner))
                elif name.endswith('-unstage'):
                    staged.discard(str(v.protected_path(self.root, arm)))
                    owner = h.read(self.root / (arm + '-staging.json'))['owner']
                    h.write(self.root / (arm + '-staging-cleanup.json'), dict(removed=True, owner=owner))
                elif row['workload']:
                    first, final = (20, 30) if arm == 'control' else (15, 25)
                    sample = dict(success=True, setup_success=True, correct_pixels=True, correct_metadata=True,
                        cleanup_failure=False, harness_timeout=False, error='', superseded_selections=0,
                        first_ms=first, final_ms=final,
                        deliveries=[dict(selection=4, event=k, latency_ms=n) for k, n in [('pixels', first), ('metadata', final)]])
                    if mutation and name == 'observation-02':
                        sample['first_ms'] = mutation
                    h.write(self.root / name / 'harness.json', dict(scenario='startup', fixture=str(self.root / 'fixture.png'),
                        cleanup_failure=False, samples=[sample]))
                    binary = Path(argv[0])
                    h.write(self.root / name / 'harness.json.loading.json', dict(executable=str(binary),
                        maps=mapping(binary) + mapping(executable), helper_mappings='unavailable: helper exited before post-timing capture'))
            class Process:
                pid = 987654321
                def wait(self, timeout):
                    assert timeout == (30 if row['workload'] else 600)
                    if timed_out and row['workload']:
                        raise subprocess.TimeoutExpired(argv, timeout)
                    return 1 if name in (stop if isinstance(stop, set) else {stop}) else 0
            return Process()
        timed_out = timeout
        with patch.object(subprocess, 'Popen', side_effect=launch):
            result = d.execute(self.built, self.correctness, self.root)
        return result

    def test_complete_trial_reconstructed_and_resealed_decision_rejected(self):
        result = self.synthetic()
        self.assertEqual(result['decision'], 'Recommend')
        self.assertEqual(v.verify(self.root)['measured'], 200)
        result['decision'] = 'Deferred'
        h.write(self.root / 'assessment.json', result)
        inventory = h.inventory(self.root)
        inventory.pop('seal.json')
        h.write(self.root / 'seal.json', inventory)
        with self.assertRaisesRegex(ValueError, 'decision mismatch'):
            v.verify(self.root)

    def test_authorization_loss_stops_before_staging(self):
        self.synthetic(stop='control-stage-authorization')
        proof = v.verify(self.root)
        self.assertEqual(proof['decision'], 'Evidence insufficient')
        self.assertEqual(proof['observations'], 0)
        self.assertFalse((self.root / 'commands/control-stage-command.json').exists())

    def test_timeout_stops_schedule_and_cleans_owned_staging(self):
        self.synthetic(timeout=True)
        proof = v.verify(self.root)
        self.assertEqual(proof['observations'], 0)
        self.assertTrue(proof['cleanup'])
        self.assertFalse((self.root / 'commands/observation-01-command.json').exists())

    def test_cleanup_failure_blocks_trial(self):
        self.synthetic(cleanup_failure=True)
        self.assertFalse(v.verify(self.root)['cleanup'])

    def test_cleanup_authorization_failure_never_retries_removal(self):
        self.synthetic(stop={'observation-02', 'control-unstage-authorization'})
        proof = v.verify(self.root)
        self.assertFalse(proof['cleanup'])
        self.assertEqual(proof['observations'], 2)
        self.assertFalse((self.root / 'commands/control-unstage-command.json').exists())

    def test_malformed_sample_stops_without_replacement(self):
        self.synthetic(mutation='malformed')
        proof = v.verify(self.root)
        self.assertEqual(proof['observations'], 2)
        self.assertFalse((self.root / 'commands/observation-03-command.json').exists())

    def test_missing_qualification_authenticates_nothing(self):
        with patch.object(d, 'validate_request'), patch.object(v, 'prerequisite', side_effect=ValueError('not qualified')):
            with self.assertRaisesRegex(ValueError, 'not qualified'):
                d.execute(self.built, self.correctness, self.root, True)
        self.assertFalse(self.root.exists())


if __name__ == '__main__':
    unittest.main()
