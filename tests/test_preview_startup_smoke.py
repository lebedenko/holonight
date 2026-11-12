"""Synthetic bounded-runner checks: never launch retained harnesses."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


s = load('startup_smoke', ROOT / 'scripts/run-preview-startup-smoke.py')
a = load('analysis_fixtures', ROOT / 'tests/test_preview_startup_analysis.py')


def trace():
    events = []
    for observation in range(4):
        raw = a.StartupAnalysisTests().v3()
        for e in raw:
            e.update(service=observation + 1, observation=observation,
                     ns=e['ns'] + observation * 100,
                     job=e['job'] + observation * 10 if e['job'] else 0,
                     preparation=e['preparation'] + observation * 10 if e['preparation'] else 0)
            if observation == 0:
                e['role'] = 'setup'
        if observation == 0:
            raw = [e for e in raw if e['phase'] not in ('pixels', 'metadata', 'pool_job', 'decode_exchange_including_transport', 'selected_worker', 'demand_dispatch')]
        for phase, ns, edge in (('service_destruction', 30, 'begin'), ('service_shutdown', 31, 'begin'),
                                ('service_shutdown', 32, 'end'), ('service_destruction', 33, 'end')):
            raw.append(dict(raw[0], phase=phase, ns=observation * 100 + ns, edge=edge, role='shutdown'))
        events.extend(raw)
    return events


def text(events):
    return '\n'.join('TRACE ' + json.dumps(e) for e in events)


class SmokeTests(unittest.TestCase):
    def test_three_observations_and_setup_shutdown(self):
        result = s.trace_validation(text(trace()), [{}, {}, {}], 'synthetic.log', 'C')
        self.assertEqual(result['issues'], [])
        self.assertEqual(len(result['lifecycles']), 4)
        self.assertEqual(sum(r['setup'] for r in result['lifecycles']), 1)
        self.assertTrue(all(r['valid'] for r in result['lifecycles']))

    def test_destructor_only_cleanup_completes_all_four_lifetimes(self):
        raw = [e for e in trace() if e['phase'] != 'service_shutdown']
        result = s.trace_validation(text(raw), [{}, {}, {}], 'destructor.log', 'C')
        self.assertEqual(result['issues'], [])
        self.assertEqual(len(result['lifecycles']), 4)
        self.assertTrue(all(l['valid'] and not l['shutdown'] for l in result['lifecycles']))

    def test_incomplete_or_invalid_cleanup_is_rejected(self):
        cases = ('missing_destruction_end', 'missing_shutdown_end', 'wrong_role',
                 'shutdown_after_destruction', 'foreign_destruction')
        for case in cases:
            with self.subTest(case=case):
                raw = trace()
                if case.startswith('missing_'):
                    phase = 'service_destruction' if case == 'missing_destruction_end' else 'service_shutdown'
                    raw = [e for e in raw if not (e['phase'] == phase and e['edge'] == 'end' and e['observation'] == 1)]
                else:
                    for e in raw:
                        if e['observation'] != 1:
                            continue
                        if case == 'wrong_role' and e['phase'] == 'service_shutdown':
                            e['role'] = 'demand'
                        if case == 'shutdown_after_destruction' and e['phase'] == 'service_shutdown':
                            e['ns'] += 10
                        if case == 'foreign_destruction' and e['phase'] == 'service_destruction':
                            e['service'] = 999
                self.assertTrue(s.trace_validation(text(raw), [{}, {}, {}], 'bad.log', 'C')['issues'])

    def test_malformed_incomplete_and_preparation_fail_closed(self):
        for phase in ('service_destruction', 'metadata', 'preparation_ready', 'construction_outer'):
            with self.subTest(phase=phase):
                raw = [e for e in trace() if e['phase'] != phase]
                self.assertTrue(s.trace_validation(text(raw), [{}, {}, {}], 'bad.log', 'C')['issues'])
        raw = trace()
        for e in raw:
            if e['phase'] == 'selected_worker':
                e['preparation'] = 999
        self.assertTrue(s.trace_validation(text(raw) + '\nTRACE {', [{}, {}, {}], 'bad.log', 'C')['issues'])

    def test_subprocess_exit_timeout_missing_json_preserve_streams(self):
        with tempfile.TemporaryDirectory() as directory:
            for index, code in enumerate(('print("partial"); raise SystemExit(7)', 'import time; print("partial", flush=True); time.sleep(60)')):
                target = Path(directory) / f'{index}.json'
                result = s.execute([sys.executable, '-c', code], target, os.environ, {}, timeout=.1)
                self.assertNotEqual(result['exit'], 0)
                self.assertEqual(result['timeout'], index == 1)
                self.assertIn('partial', target.with_suffix('.stdout').read_text())
                with self.assertRaisesRegex(RuntimeError, 'missing or invalid harness JSON'):
                    s.validate_invocation(target, 'C', result)
                self.assertTrue(target.with_suffix('.accounting.json').is_file())

    def test_valid_json_does_not_override_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'C.json'
            sample = dict(success=True, setup_success=True, correct_pixels=True, correct_metadata=True, first_ms=1, final_ms=2)
            target.write_text(json.dumps({'samples': [sample] * 3}))
            target.with_suffix('.stderr').write_text(text(trace()))
            target.with_suffix('.stdout').write_text('')
            with self.assertRaises(RuntimeError):
                s.validate_invocation(target, 'C', {'exit': 7, 'timeout': False})
            s.validate_invocation(target, 'C', {'exit': 0, 'timeout': False})

    def test_changed_or_missing_input_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'input').write_text('original')
            expected = {'input': s.digest(base / 'input')}
            s.verify_hashes(base, expected)
            (base / 'input').write_text('changed')
            with self.assertRaises(ValueError):
                s.verify_hashes(base, expected)
            with self.assertRaises(ValueError):
                s.verify_hashes(base, {'missing': 'hash'})

    def test_existing_output_and_marker_are_never_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'execution-started.json').write_text('{}')
            args = type('Args', (), dict(package=base, fixtures=base, output=base, uid=int(os.environ.get('SUDO_UID', '1000'))))()
            with patch.object(s.os, 'geteuid', return_value=0):
                with self.assertRaises(FileExistsError):
                    s.run(args)
            self.assertEqual((base / 'execution-started.json').read_text(), '{}')

    def test_failure_or_residual_scopes_stops_before_next_invocation(self):
        with tempfile.TemporaryDirectory() as directory:
            targets = [Path(directory) / f'{label}.json' for label in 'AB']
            commands = [['synthetic', str(t)] for t in targets]
            for residual in (False, True):
                result = {'invocations': []}
                snapshots = [{'isolated': True}, {'isolated': not residual}]
                with patch.object(s, 'scope_snapshot', side_effect=snapshots), \
                        patch.object(s, 'execute', return_value={'exit': 0, 'timeout': False}) as execute, \
                        patch.object(s, 'validate_invocation', side_effect=None if residual else RuntimeError('invalid trace')):
                    with self.assertRaises(RuntimeError):
                        s.run_commands(commands, result, os.getuid(), {}, {})
                    self.assertEqual(execute.call_count, 1)
                    self.assertEqual(len(result['invocations']), 1)

    def test_existing_helper_activity_blocks_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'A.json'
            result = {'invocations': []}
            with patch.object(s, 'scope_snapshot', return_value={'isolated': False}), \
                    patch.object(s, 'execute') as execute:
                with self.assertRaisesRegex(RuntimeError, 'helper activity'):
                    s.run_commands([['synthetic', str(target)]], result, 1000, {}, {})
                execute.assert_not_called()

    def test_shutdown_cannot_be_attributed_to_another_lifetime(self):
        raw = trace()
        for e in raw:
            if e['phase'] == 'service_shutdown' and e['observation'] == 1:
                e['service'] = 999
        result = s.trace_validation(text(raw), [{}, {}, {}], 'bad.log', 'C')
        self.assertIn('foreign_service_lifetime', {i['kind'] for i in result['issues']})
        self.assertTrue(result['issues'])

    @unittest.skipUnless(os.geteuid() == 0, 'requires privileged wrapper')
    def test_privileged_wrapper_output_is_writable_by_ordinary_user(self):
        import pwd
        uid = int(os.environ.get('SUDO_UID', '1000'))
        account = pwd.getpwuid(uid)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            base.chmod(0o755)
            target = s.observation_directory(base, uid, account.pw_gid)
            probe = target / 'probe'
            subprocess.run([sys.executable, '-c', 'import pathlib,sys; pathlib.Path(sys.argv[1]).write_text("ok")', str(probe)],
                           user=uid, group=account.pw_gid, extra_groups=[], check=True)
            self.assertEqual(probe.stat().st_uid, uid)


if __name__ == '__main__':
    unittest.main()
