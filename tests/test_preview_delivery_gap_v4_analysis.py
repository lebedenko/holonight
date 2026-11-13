import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('audit',Path(__file__).resolve().parents[1]/'scripts/analyze-preview-delivery-gaps-v4.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class IntervalTests(unittest.TestCase):
    def test_overlap_clipping_and_complement(self):
        r=a.intervals(5,20,[dict(start=0,stop=8),dict(start=7,stop=10),dict(start=15,stop=30)])
        self.assertEqual(r['covered'],[[5,10],[15,20]])
        self.assertEqual(r['uncovered'],[[10,15]])
        self.assertEqual(r['covered_ns']+r['uncovered_ns'],15)
    def test_empty_and_zero_window(self):
        self.assertEqual(a.intervals(0,5,[])['uncovered'],[[0,5]])
        self.assertEqual(a.intervals(5,5,[])['uncovered'],[])

import copy
import tempfile
from unittest.mock import patch


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=a.s.ROOT / 'build')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.runtime = self.base / 'runtime'; self.runtime.mkdir()
        self.prepared = self.base / 'prepared'; self.prepared.mkdir()
        self.output = self.base / 'output'
        self.reports = []
        invocations = []
        for index in range(12):
            variant = 'ABCD'[index // 3]
            target = self.runtime / f'{variant}-{a.s.FIXTURES[index % 3]}.json'
            a.s.write(target, dict(samples=[]))
            target.with_suffix('.stderr').write_text('synthetic')
            report = dict(windows=[], handoffs=[], spans=[], events=[], unavailable=[])
            for observation in range(3):
                e = dict(pid=index+1, service=1, observation=observation+1, job=1, worker=1,
                         generation=1, preparation=None, session=1, transaction=1,
                         publication=observation+1, tid=20, file='/raw.stderr', line=12)
                report['handoffs'].append(dict(pid=e['pid'], publication=e['publication'], identity=e.copy()))
                for endpoint in ('pixels', 'metadata'):
                    report['windows'].append(dict(delivery=e.copy(), start_ns=10, stop_ns=30,
                                                  endpoint=endpoint, boundary=dict(file='/raw.stderr', line=1), categories={}))
            self.reports.append(report)
            a.s.write(target.with_suffix('.accounting.json'), report)
            invocations.append(dict(command=['harness', 'fixture', 'mode', 'startup', '3', str(target)], status='passed'))
        a.s.write(self.runtime / 'assessment.json', dict(status='passed', passed_observations=36,
                  invocations=invocations, cleanup_verified=True, runtime_integrity=True, retained_integrity=True))
        self.seal_runtime()
        (self.prepared / 'trace.h').write_text('header')
        for variant in 'ABCD':
            root = self.prepared / variant; root.mkdir()
            source = root / 'source.cpp'; source.write_text('probe\n')
            a.s.write(root / 'probe-to-source.json', dict(probes=[dict(file=str(source),
                      sha256=a.s.digest(source), line=1, text='probe')]))
        self.manifest = dict(status='prepared', unchanged=True, issues=[], before={}, after={},
                             header_sha256=a.s.digest(self.prepared / 'trace.h'))
        self.seal_prepared()
        self.execution = patch('subprocess.Popen', side_effect=AssertionError('process execution forbidden'))
        self.execution.start(); self.addCleanup(self.execution.stop)
        shell = patch('os.system', side_effect=AssertionError('shell execution forbidden'))
        shell.start(); self.addCleanup(shell.stop)

    def seal_runtime(self):
        seal = self.runtime / 'seal.json'
        a.s.write(seal, {k:v for k,v in a.s.inventory(self.runtime).items() if k != 'seal.json'})

    def seal_prepared(self):
        self.manifest['outputs'] = {v:a.s.inventory(self.prepared / v) for v in 'ABCD'}
        a.s.write(self.prepared / 'manifest.json', self.manifest)

    def run_audit(self, reports=None):
        with patch.object(a.s, 'trace_validation', side_effect=reports or copy.deepcopy(self.reports)):
            return a.audit(self.runtime, self.prepared, self.output)

    def assert_blocked(self, reports=None):
        result = self.run_audit(reports)
        self.assertEqual(result['status'], 'blocked', result)
        self.assertTrue((self.output / 'ASSESSMENT.md').exists())
        a.s.smoke.verify_hashes(self.output, a.s.read(self.output / 'seal.json'))
        return result

    def test_complete_schedule_and_raw_references(self):
        self.assertEqual(self.run_audit()['endpoints'], 72)
        rows = a.s.read(self.output / 'endpoints.json')
        self.assertEqual(len({(r['delivery']['pid'], r['delivery']['publication'], r['endpoint']) for r in rows}), 72)
        self.assertEqual(rows[0]['delivery']['file'], '/raw.stderr')
        self.assertEqual(rows[0]['boundary']['line'], 1)

    def test_invalid_destination_writes_nothing(self):
        self.output.mkdir()
        with self.assertRaises(ValueError): self.run_audit()
        self.assertEqual(list(self.output.iterdir()), [])
        self.output = self.runtime / 'nested'
        with self.assertRaises(ValueError): self.run_audit()
        self.assertFalse(self.output.exists())

    def test_manifest_rejections(self):
        for field, value in [('status','blocked'), ('unchanged',False), ('issues',['issue']), ('after',{'changed':'hash'})]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.manifest)
                self.manifest[field] = value; self.seal_prepared()
                self.output = self.base / field
                self.assert_blocked()
                self.manifest = original

    def test_tampered_runtime(self):
        (self.runtime / 'assessment.json').write_text('{}')
        self.assert_blocked()

    def test_tampered_header_and_inventory(self):
        (self.prepared / 'trace.h').write_text('changed')
        self.assert_blocked()
        (self.prepared / 'trace.h').write_text('header')
        (self.prepared / 'A/source.cpp').write_text('changed')
        self.output = self.base / 'inventory'
        self.assert_blocked()

    def test_malformed_probes(self):
        path = self.prepared / 'A/probe-to-source.json'
        original = a.s.read(path)
        for field, values in [('line',[0,-1,2,True,'1',None]), ('text',['wrong']),
                              ('sha256',['wrong']), ('file',[str(self.prepared / 'A/../trace.h')])]:
            for value in values:
                probe = copy.deepcopy(original); probe['probes'][0][field] = value
                a.s.write(path, probe); self.seal_prepared()
                self.output = self.base / f'probe-{field}-{value}'.replace('/', '_')
                self.assert_blocked()

    def test_replay_mismatch_retains_prior_output(self):
        reports = copy.deepcopy(self.reports); reports[1]['unavailable'] = ['changed']
        self.assert_blocked(reports)
        self.assertTrue(list(self.output.glob('*.accounting.json')))

    def test_missing_duplicate_and_malformed_windows_and_handoffs(self):
        for key, value in [('windows',[]), ('windows',[{}]*6), ('windows',None), ('windows',self.reports[0]['windows'][:5] + [self.reports[0]['windows'][0]]),
                           ('handoffs',[]), ('handoffs',self.reports[0]['handoffs']*2)]:
            report = copy.deepcopy(self.reports[0]); report[key] = value
            # Use the scheduled first file, independent of directory iteration order.
            target = self.runtime / f'A-{a.s.FIXTURES[0]}.accounting.json'
            a.s.write(target, report); self.seal_runtime()
            reports = [report, *copy.deepcopy(self.reports[1:])]
            self.output = self.base / f'malformed-{key}-{len(list(self.base.iterdir()))}'
            self.assert_blocked(reports)

    def test_integrity_change_during_replay(self):
        def replay(*args):
            (self.runtime / 'new-evidence').write_text('changed')
            return copy.deepcopy(self.reports.pop(0))
        with patch.object(a.s, 'trace_validation', side_effect=replay):
            result = a.audit(self.runtime, self.prepared, self.output)
        self.assertEqual(result['failure'], 'inputs changed')
        self.assertTrue((self.output / 'endpoints.json').exists())
        a.s.smoke.verify_hashes(self.output, a.s.read(self.output / 'seal.json'))

    def test_identity_selection_envelopes_cleanup_and_cross_thread_overlap(self):
        report = copy.deepcopy(self.reports[0]); e = report['windows'][0]['delivery']
        def span(operation, **changes):
            begin = dict(e, **changes)
            return dict(operation=operation, begin=begin, end=dict(begin, line=13), start=5, stop=25)
        good = span('memory_insert', tid=99)
        wrapper = span('transaction_wrapper', session=None, transaction=None)
        cleanup = span('effective_cleanup', transaction=None)
        report['spans'] = [good, wrapper, cleanup]
        for field in a.IDENTITY + a.CONTEXT:
            report['spans'].append(span('storage_commit', **{field:999}))
        report['unavailable'] = [cleanup]
        rows = a.endpoint_rows(report, 'A', 'fixture')
        self.assertEqual(rows[0]['operations'], [good, wrapper])
        self.assertEqual(rows[0]['specific']['covered'], [[10,25]])
        self.assertEqual(rows[0]['unavailable'], [cleanup])
        self.assertEqual(rows[1]['operations'], [good, wrapper])
        report['spans'] = [wrapper]
        self.assertEqual(a.endpoint_rows(report,'A','fixture')[0]['specific']['covered_ns'],0)

    def test_adjacent_nested_outside_and_touching_intervals(self):
        spans = [dict(start=x,stop=y) for x,y in [(0,10),(10,15),(12,14),(15,20),(20,30),(-5,0),(40,50)]]
        self.assertEqual(a.intervals(10,20,spans), dict(covered=[[10,20]],uncovered=[],covered_ns=10,uncovered_ns=0))
