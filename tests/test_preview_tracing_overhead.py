"""Synthetic protocol checks; never execute retained provider workloads."""
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
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

m = load('overhead', ROOT / 'scripts/measure-preview-tracing-overhead.py')
f = load('smoke_fixtures', ROOT / 'tests/test_preview_startup_smoke.py')


def sample(first=1, final=2):
    return dict(success=True, setup_success=True, correct_pixels=True, correct_metadata=True,
                first_ms=first, final_ms=final,
                deliveries=[dict(selection=4, event='pixels', latency_ms=first), dict(selection=4, event='metadata', latency_ms=final)])


class OverheadTests(unittest.TestCase):
    def test_fixed_schedule_counts_and_order(self):
        rows = m.schedule()
        self.assertEqual(len(rows), 264)
        self.assertEqual(sum(r['count'] for r in rows if not r['warmup']), 2400)
        self.assertEqual(sum(r['count'] for r in rows if r['warmup']), 24)
        for fixture in m.FIXTURES:
            selected = [r for r in rows if r['fixture'] == fixture]
            self.assertEqual([r['variant'] + r['mode'] for r in selected[:8]], ['AU', 'AT', 'BU', 'BT', 'CU', 'CT', 'DU', 'DT'])
            self.assertEqual([r['variant'] + r['mode'] for r in selected[16:24]], ['BT', 'BU', 'CT', 'CU', 'DT', 'DU', 'AT', 'AU'])
            for v in 'ABCD':
                for mode in 'UT':
                    self.assertEqual(sum(r['count'] for r in selected if not r['warmup'] and r['variant'] == v and r['mode'] == mode), 100)

    def test_warmups_excluded_and_negative_overhead_retained(self):
        rows = [dict(invocation=r, samples=[sample(10000, 10001) if r['warmup'] else sample(10, 20) if r['mode'] == 'U' else sample(5, 10)] * r['count']) for r in m.schedule()]
        report = m.statistics_report(rows)
        self.assertEqual(len(report), 24)
        self.assertEqual(report[0]['statistics']['median'], dict(U=10, T=5, delta_ms=-5, delta_percent=-50))
        self.assertEqual(len(report[0]['blocks']), 10)
        for bad in (rows[:-1], list(reversed(rows))):
            with self.assertRaises(ValueError):
                m.statistics_report(bad)
        rows[8]['samples'] = []
        with self.assertRaises(ValueError):
            m.statistics_report(rows)

    def test_nearest_rank_zero_baseline_and_invalid_statistics(self):
        result = m.comparison(list(range(1, 101)), [2 * x for x in range(1, 101)])
        self.assertEqual(result['p95'], dict(U=95, T=190, delta_ms=95, delta_percent=100))
        self.assertEqual(m.comparison([0], [2])['median']['delta_percent'], None)
        for values in ([], [-1], [float('nan')], [float('inf')], [True], ['1']):
            with self.assertRaises(ValueError):
                m.comparison(values, [1])

    def test_trace_lifecycles_setup_and_mode_validation(self):
        trace = f.trace()
        self.assertEqual(m.validate_trace(f.text(trace), [sample()] * 3, 'synthetic', 'C')['issues'], [])
        for phase in ('service_destruction', 'metadata', 'preparation_ready'):
            self.assertTrue(m.validate_trace(f.text([e for e in trace if e['phase'] != phase]), [sample()] * 3, 'bad', 'C')['issues'])
        self.assertTrue(m.validate_trace('', [sample()], 'missing', 'A')['issues'])
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'test.json'
            target.write_text(json.dumps(dict(scenario='startup', fixture=str(m.FIXTURE_ROOT / m.FIXTURES[0]), samples=[sample()])))
            target.with_suffix('.stderr').write_text(f.text(trace))
            target.with_suffix('.stdout').write_text('')
            with self.assertRaisesRegex(ValueError, 'trace validation'):
                m.validate(target, dict(mode='U', count=1, fixture=m.FIXTURES[0], variant='A'), dict(exit=0, timeout=False, cleanup_verified=True), os.getuid())

    def test_timeout_preserves_streams_and_cleanup_is_unverified(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'test.json'
            result = m.smoke.execute([sys.executable, '-c', 'import time;print("partial",flush=True);time.sleep(60)'], target, os.environ, {}, timeout=.1)
            self.assertTrue(result['timeout'])
            self.assertFalse(result['cleanup_verified'])
            self.assertIn('partial', target.with_suffix('.stdout').read_text())

    def test_first_failure_stops_before_next_command(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d)
            commands = [dict(invocation=r, argv=['synthetic', str(output / f"{r['index']}.json")]) for r in m.schedule()[:2]]
            result = dict(invocations=[])
            with patch.object(m.smoke, 'scope_snapshot', return_value=dict(isolated=True)), \
                 patch.object(m.smoke, 'execute', return_value=dict(exit=7, timeout=False, cleanup_verified=True)) as execute:
                with self.assertRaises(OSError):
                    m.run_invocations(commands, output, result, 1000, {}, {})
                self.assertEqual(execute.call_count, 1)
                self.assertEqual(len(result['invocations']), 1)
                self.assertEqual(result['first_failing_command'], commands[0])

    def test_seal_detects_changed_artifact_and_tool(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d)
            artifact = output / 'binary'
            artifact.write_text('frozen')
            m.write(output / 'preparation.json', dict(tools={str(artifact): m.digest(artifact)}))
            m.write(output / 'seal.json', m.inventory(output))
            m.check_seal(output)
            artifact.write_text('changed')
            with self.assertRaises(ValueError):
                m.check_seal(output)

    def test_only_package_local_trace_includes_are_normalized(self):
        self.assertEqual(m.normalized(b'#include "/a/trace.h"'), m.normalized(b'#include "/b/trace.h"'))
        self.assertNotEqual(m.normalized(b'int x=1;'), m.normalized(b'int x=2;'))

    @unittest.skipUnless(os.geteuid() == 0, 'requires privileged wrapper')
    def test_ordinary_user_ownership_and_private_fixture_validation(self):
        import pwd
        uid = int(os.environ.get('SUDO_UID', '1000'))
        account = pwd.getpwuid(uid)
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            base.chmod(0o755)
            output = m.smoke.observation_directory(base, uid, account.pw_gid)
            target = output / 'test.json'
            fixture = m.FIXTURES[0]
            data = dict(scenario='startup', fixture=str(m.FIXTURE_ROOT / fixture), samples=[sample()])
            target.write_text(json.dumps(data))
            target.with_suffix('.stderr').write_text('')
            target.with_suffix('.stdout').write_text('')
            work = output / (target.name + '.work-test')
            work.mkdir()
            (work / 'cache').mkdir()
            import shutil
            for i in range(16):
                shutil.copyfile(m.FIXTURE_ROOT / fixture, work / f'{i}.png')
            for p in [target, work, *work.rglob('*')]:
                os.chown(p, uid, account.pw_gid)
            invocation = dict(mode='U', count=1, fixture=fixture, variant='A')
            process = dict(exit=0, timeout=False, cleanup_verified=True)
            self.assertEqual(m.validate(target, invocation, process, uid), [sample()])
            os.chown(target, 0, 0)
            with self.assertRaisesRegex(ValueError, 'ownership'):
                m.validate(target, invocation, process, uid)
            os.chown(target, uid, account.pw_gid)
            (work / '1.png').write_text('corrupt')
            with self.assertRaisesRegex(ValueError, 'provenance'):
                m.validate(target, invocation, process, uid)


if __name__ == '__main__':
    unittest.main()
