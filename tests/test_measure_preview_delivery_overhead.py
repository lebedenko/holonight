"""Deterministic checks for the fixed delivery overhead experiment."""
import copy
from contextlib import ExitStack
import shutil
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

m = load('measure_delivery_overhead', 'scripts/measure-preview-delivery-overhead.py')
f = load('historical_overhead_tests', 'tests/test_preview_tracing_overhead.py')


class MeasurementTests(unittest.TestCase):
    def rows(self):
        return [dict(invocation=r, samples=[f.sample(10000, 20000) if r['warmup'] else f.sample(10, 20) if r['mode'] == 'v3' else f.sample(5, 10)] * r['observations']) for r in m.prep.schedule()]

    def test_schedule_and_negative_distributions(self):
        rows = self.rows()
        self.assertEqual(len(rows), 264)
        self.assertEqual(sum(len(r['samples']) for r in rows), 2424)
        report = m.statistics_report(rows)
        self.assertEqual(len(report), 24)
        self.assertEqual(report[0]['statistics']['median'], dict(v3=10, v4=5, delta_ms=-5, delta_percent=-50))
        self.assertTrue(all(len(c['blocks']) == 10 for c in report))
        for bad in (rows[:-1], rows + rows[:1], rows[::-1]):
            with self.assertRaises(ValueError):
                m.statistics_report(bad)
        rows[8]['samples'] = []
        with self.assertRaises(ValueError):
            m.statistics_report(rows)

    def test_nearest_rank_and_zero(self):
        self.assertEqual(m.old.comparison(list(range(1, 101)), [0] * 100)['p95']['delta_ms'], -95)
        self.assertIsNone(m.old.comparison([0], [1])['median']['delta_percent'])

    def test_integrity_and_missing_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            (output / 'raw').write_text('original')
            m.seal(output)
            m.check_output(output)
            (output / 'raw').write_text('changed')
            with self.assertRaises(ValueError):
                m.check_output(output)
            with self.assertRaises((OSError, ValueError)):
                m.verify(output)

    def test_timeout_preserves_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'sample.json'
            result = m.gate.smoke.execute([sys.executable, '-c', 'import time;print("partial",flush=True);time.sleep(60)'], target, os.environ, {}, timeout=.1)
            self.assertTrue(result['timeout'])
            self.assertFalse(result['cleanup_verified'])
            self.assertIn('partial', target.with_suffix('.stdout').read_text())
            with self.assertRaises(ValueError):
                m.validate(target, m.prep.schedule()[0], result, os.getuid())

    def test_v4_count_required(self):
        for count in (1, 10):
            with self.assertRaises(ValueError):
                m.v4_gate(dict(issues=[], events=[dict(operation='endpoint_pixels')], spans=[]), 'A', count)

    def test_fixture_count_for_warmup_and_measured_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = root / 'fixtures'
            fixtures.mkdir()
            (fixtures / 'image.png').write_bytes(b'fixture')
            target = root / 'sample.json'
            work = root / 'sample.json.work-private'
            work.mkdir()
            (work / 'cache').mkdir()
            with patch.object(m.old, 'FIXTURE_ROOT', fixtures):
                for count in (1, 10):
                    for i in range(count * 8 + 8):
                        (work / f'{i}.png').write_bytes(b'fixture')
                    row = dict(fixture='image.png', observations=count)
                    m.validate_work(target, row, os.getuid())
                    (work / '0.png').write_bytes(b'tampered')
                    with self.assertRaises(ValueError):
                        m.validate_work(target, row, os.getuid())
                    (work / '0.png').write_bytes(b'fixture')
                    with self.assertRaises(ValueError):
                        m.validate_work(target, row, os.getuid() + 1)
                (work / '0.png').unlink()
                with self.assertRaises(ValueError):
                    m.validate_work(target, row, os.getuid())

    def test_first_failure_and_integrity_drift_stop_launches(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            commands = [dict(invocation=r, argv=['synthetic', str(output / f'{i}.json')]) for i, r in enumerate(m.prep.schedule()[:2])]
            for integrity_failure in (False, True):
                result = dict(invocations=[])
                def integrity():
                    if integrity_failure:
                        raise ValueError('integrity drift')
                with patch.object(m.gate, 'scope_snapshot', return_value=dict(isolated=True)), \
                     patch.object(m.gate.smoke, 'execute', return_value=dict(exit=7, timeout=False, cleanup_verified=True)) as execute, \
                     patch.object(m, 'validate', side_effect=ValueError('failed evidence')):
                    with self.assertRaises(ValueError):
                        m.run_commands(commands, output, result, 1000, {}, {}, integrity)
                    self.assertEqual(execute.call_count, 0 if integrity_failure else 1)

    def test_supplemental_mode_contamination(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'sample.json'
            row = m.prep.schedule()[0]
            m.write(target, dict(scenario='startup', fixture=str(m.old.FIXTURE_ROOT / row['fixture']), samples=[f.sample()]))
            target.with_suffix('.stderr').write_text('DELIVERY {}')
            target.with_suffix('.stdout').write_text('')
            with patch.object(m.old, 'validate_trace', return_value=dict(issues=[])):
                with self.assertRaisesRegex(ValueError, 'contamination'):
                    m.validate(target, row, dict(exit=0, timeout=False, cleanup_verified=True), os.getuid())

    def test_generalized_v4_gate_accepts_one_and_ten(self):
        fixture = load('generalized_delivery_fixture', 'tests/test_preview_delivery_smoke.py')
        for variant in 'ABCD':
            historical, values = fixture.combined(variant)
            template = fixture.s.trace_validation(fixture.trace(historical, values), [{}, {}, {}], '/raw', variant)
            for count in (1, 10):
                report = dict(issues=[], events=[], spans=[], handoffs=[])
                for observation in range(1, count + 1):
                    for group in ('events', 'spans', 'handoffs'):
                        for original in template[group]:
                            context = original.get('begin', original.get('identity', original))
                            if context.get('observation') != 1:
                                continue
                            def remap(value):
                                if isinstance(value, list):
                                    return [remap(v) for v in value]
                                if isinstance(value, dict):
                                    return {k: observation if k == 'observation' and v is not None else v + observation * 10000 if k == 'publication' and v is not None else remap(v) for k, v in value.items()}
                                return value
                            report[group].append(remap(copy.deepcopy(original)))
                m.v4_gate(report, variant, count)
                report['events'] = [e for e in report['events'] if e['operation'] != 'endpoint_metadata']
                with self.assertRaises(ValueError):
                    m.v4_gate(report, variant, count)

    def test_incomplete_report_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            execution = root / 'build/execution'
            execution.mkdir()
            m.write(execution / 'assessment.json', dict(status='blocked', failure='fixture provenance mismatch', invocations=[]))
            m.seal(execution)
            before = m.inventory(execution)
            with patch.object(m, 'ROOT', root), patch.object(m, 'verify'):
                self.assertEqual(m.report(root / 'prepared', execution, root / 'build/report'), 1)
            self.assertEqual(m.inventory(execution), before)
            report = m.read(root / 'build/report/assessment.json')
            self.assertEqual(report['unexecuted'], 264)
            self.assertFalse(report['statistics_available'])


    def test_destination_collisions_and_symlink_ancestors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            consumed = root / 'build/consumed'
            consumed.mkdir()
            (root / 'build/link').symlink_to(consumed, target_is_directory=True)
            with patch.object(m, 'ROOT', root):
                for output in (consumed, consumed / 'nested', root / 'build/link/new', root / 'build'):
                    with self.assertRaises(ValueError):
                        m.fresh(output, consumed)

    def test_malformed_reports_are_sealed_without_invented_counts(self):
        for rows in (None, 'bad', [None], [{'invocation': {}}], [{}] * 265):
            with self.subTest(rows=type(rows).__name__), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'build').mkdir()
                execution = root / 'build/execution'
                execution.mkdir()
                m.write(execution / 'assessment.json', dict(status='blocked', invocations=rows))
                m.seal(execution)
                before = m.inventory(execution)
                with patch.object(m, 'ROOT', root), patch.object(m, 'verify'):
                    self.assertEqual(m.report(root / 'prepared', execution, root / 'build/report'), 1)
                m.check_output(root / 'build/report')
                self.assertIsNone(m.read(root / 'build/report/assessment.json')['launched'])
                self.assertEqual(before, m.inventory(execution))

    def test_missing_report_evidence_is_sealed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            with patch.object(m, 'ROOT', root), patch.object(m, 'verify'):
                self.assertEqual(m.report(root / 'prepared', root / 'missing', root / 'build/report'), 1)
            m.check_output(root / 'build/report')

    def test_required_provider_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            required = [('build/holonight-images', []), ('build/holonight-thumbnails', ['Images']),
                        ('build/holonight-file-browser', ['Images', 'Thumbnails']),
                        ('reuse-harness', ['Images', 'Thumbnails', 'FileBrowser'])]
            for relative, names in required:
                directory = base / relative
                directory.mkdir(parents=True)
                (directory / 'CMakeCache.txt').write_text(''.join(f'Holonight{n}_DIR:PATH={base}/prefix/lib/cmake/Holonight{n}\n' for n in names))
            m.providers(base)
            cache = base / 'build/holonight-thumbnails/CMakeCache.txt'
            for invalid in ('', 'HolonightImages_DIR:PATH=/foreign'):
                cache.write_text(invalid)
                with self.assertRaises(ValueError):
                    m.providers(base)

    def raw_trace(self, variant, count, supplemental=True):
        fixture = load('counted_trace_fixture', 'tests/test_preview_delivery_smoke.py')
        historical, values = fixture.combined(variant)
        h = [e for e in historical if e['observation'] == 0]
        v = []
        for observation in range(1, count + 1):
            for source, target in ((historical, h), (values, v)):
                for original in source:
                    if original['observation'] != 1:
                        continue
                    event = dict(original)
                    for key in ('service', 'job', 'preparation', 'session', 'transaction', 'publication', 'span'):
                        if event.get(key):
                            event[key] += (observation - 1) * 10000
                    event['observation'] = observation
                    event['ns'] += (observation - 1) * 10000
                    target.append(event)
        return fixture.trace(h, v if supplemental else [])

    def test_real_trace_count_validation_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / 'image.png'
            fixture.write_bytes(b'fixture')
            with patch.object(m.old, 'FIXTURE_ROOT', root):
                for variant in 'ABCD':
                    for count in (1, 10):
                        for mode in ('v3', 'v4'):
                            target = root / f'{variant}-{mode}-{count}.json'
                            row = dict(variant=variant, mode=mode, observations=count, fixture=fixture.name)
                            m.write(target, dict(scenario='startup', fixture=str(fixture), samples=[f.sample()] * count))
                            target.with_suffix('.stdout').write_text('')
                            target.with_suffix('.stderr').write_text(self.raw_trace(variant, count, mode == 'v4'))
                            work = root / (target.name + '.work-private')
                            (work / 'cache').mkdir(parents=True)
                            for i in range(count * 8 + 8):
                                (work / f'{i}.png').write_bytes(b'fixture')
                            process = dict(exit=0, timeout=False, cleanup_verified=True)
                            m.validate(target, row, process, os.getuid())
                            before = m.inventory(root)
                            m.validate(target, row, process, os.getuid(), replay=True)
                            self.assertEqual(before, m.inventory(root))
                            m.write(target.with_suffix('.v3.json'), {})
                            with self.assertRaisesRegex(ValueError, 'replay mismatch'):
                                m.validate(target, row, process, os.getuid(), replay=True)


    def test_synthetic_build_execute_report_full_schedule(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            (root / 'build').mkdir()
            package = root / 'prepared'
            package.mkdir()
            m.write(package / 'protocol.json', dict(schedule=m.prep.schedule()))
            fixtures = root / 'fixtures'
            fixtures.mkdir()
            for name in m.old.FIXTURES:
                (fixtures / name).write_bytes(b'fixture')
            built, execution, report = [root / 'build' / n for n in ('native', 'execution', 'report')]
            runtime_root = root / 'run'
            runtime_root.mkdir()
            def bundle(base):
                helper = base / 'build/holonight-images/holonight-images-helper'
                helper.parent.mkdir(parents=True, exist_ok=True)
                helper.write_bytes(b'helper')
                for relative in ('runtime', 'prefix/libexec/holonight-images/runtime'):
                    directory = base / relative
                    payload = directory / 'usr/libexec/holonight-images-helper'
                    payload.parent.mkdir(parents=True, exist_ok=True)
                    payload.write_bytes(helper.read_bytes())
                    m.write(directory / 'manifest.json', dict(files=[dict(path='usr/libexec/holonight-images-helper', sha256=m.digest(payload), size=6, mode=0o644)]))
            def native(cmd, **kwargs):
                if '-B' in cmd:
                    directory = Path(cmd[cmd.index('-B') + 1])
                    directory.mkdir(parents=True, exist_ok=True)
                    base = directory.parent if directory.name == 'reuse-harness' else directory.parent.parent
                    names = {'holonight-images': [], 'holonight-thumbnails': ['Images'], 'holonight-file-browser': ['Images', 'Thumbnails'], 'reuse-harness': ['Images', 'Thumbnails', 'FileBrowser']}[directory.name]
                    (directory / 'CMakeCache.txt').write_text(''.join(f'Holonight{n}_DIR:PATH={base}/prefix/lib/cmake/Holonight{n}\n' for n in names))
                    if directory.name == 'holonight-images':
                        bundle(base)
                    if directory.name == 'reuse-harness':
                        (directory / 'preview-benchmark').write_bytes(b'harness')
                elif cmd[0] == 'nm':
                    kwargs['stdout'].write('StandbyTrace:: x ' + ('DeliveryTrace::' if '/v4/' in cmd[-1] else ''))
                elif '-c' in cmd:
                    Path(cmd[-1]).write_text('ok')
            traces = {(v, mode, count): self.raw_trace(v, count, mode == 'v4') for v in 'ABCD' for mode in ('v3', 'v4') for count in (1, 10)}
            def process(cmd, target, env, credentials):
                if 'install' in cmd:
                    destination = Path(cmd[cmd.index('--runtime') + 1])
                    source = Path(cmd[cmd.index('--source') + 1])
                    generation = 'a' * 64
                    shutil.copytree(source, destination / 'generations' / generation)
                    (destination / 'current').write_text(generation)
                    m.write(destination / 'ownership.json', [generation])
                else:
                    variant = Path(cmd[0]).parents[1].name
                    mode = Path(cmd[0]).parents[2].name
                    count = int(cmd[-2])
                    m.write(target, dict(scenario='startup', fixture=cmd[2], samples=[f.sample()] * count))
                    target.with_suffix('.stderr').write_text(traces[variant, mode, count])
                    target.with_suffix('.stdout').write_text('')
                    work = target.parent / (target.name + '.work-private')
                    (work / 'cache').mkdir(parents=True)
                    for i in range(count * 8 + 8):
                        (work / f'{i}{Path(cmd[2]).suffix}').write_bytes(b'fixture')
                return dict(exit=0, timeout=False, cleanup_verified=True)
            def observations(output, uid, gid):
                directory = output / 'observations'
                directory.mkdir()
                return directory
            for obj, name, value in [(m, 'ROOT', root), (m, 'RUNTIME_ROOT', runtime_root), (m.old, 'FIXTURE_ROOT', fixtures)]:
                stack.enter_context(patch.object(obj, name, value))
            stack.enter_context(patch.object(m, 'verify', return_value={}))
            stack.enter_context(patch.object(m, 'tools', return_value={}))
            stack.enter_context(patch.object(m, 'fixture_hashes', return_value={}))
            stack.enter_context(patch.object(m.subprocess, 'check_output', return_value='synthetic host'))
            stack.enter_context(patch.object(m.subprocess, 'run', side_effect=native))
            stack.enter_context(patch.object(m.os, 'geteuid', return_value=0))
            stack.enter_context(patch.object(m.gate, 'observation_directory', side_effect=observations))
            stack.enter_context(patch.object(m.gate, 'scope_snapshot', return_value=dict(isolated=True)))
            stack.enter_context(patch.object(m.gate, 'protected_inventory', side_effect=m.inventory))
            workloads = stack.enter_context(patch.object(m.gate.smoke, 'execute', side_effect=process))
            stack.enter_context(patch('builtins.print'))
            self.assertEqual(m.build(package, built), 0)
            self.assertEqual(m.execute(package, built, execution, os.getuid()), 0)
            assessment = m.read(execution / 'assessment.json')
            self.assertEqual(len(assessment['invocations']), 264)
            self.assertEqual(sum(len(r['samples']) for r in assessment['invocations']), 2424)
            self.assertEqual(workloads.call_count, 270)
            before = m.inventory(execution)
            self.assertEqual(m.report(package, execution, report), 0)
            m.check_output(report)
            self.assertEqual(before, m.inventory(execution))
            with self.assertRaisesRegex(ValueError, 'already started'):
                m.execute(package, built, root / 'build/reused', os.getuid())

    def test_final_checks_are_independent_and_keep_original_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            built = root / 'build/native'
            built.mkdir()
            m.write(built / 'assessment.json', dict(status='built'))
            m.write(built / 'tools.json', {})
            m.write(built / 'fixtures.json', {})
            m.seal(built)
            with patch.object(m, 'ROOT', root), patch.object(m.os, 'geteuid', return_value=0), \
                 patch.object(m, 'verify', side_effect=ValueError('input failure')), \
                 patch.object(m, 'built_integrity', side_effect=ValueError('artifact failure')), \
                 patch.object(m.gate, 'protected_inventory', side_effect=ValueError('runtime failure')), \
                 patch.object(m.gate, 'scope_snapshot', return_value=dict(isolated=True)) as scopes:
                output = root / 'build/execution'
                self.assertEqual(m.execute(root / 'prepared', built, output, os.getuid()), 1)
                assessment = m.read(output / 'assessment.json')
                self.assertEqual(assessment['failure'], 'input failure')
                self.assertEqual(set(assessment['final_checks']), {'inputs', 'artifacts', 'runtime', 'scopes'})
                self.assertTrue(assessment['final_checks']['scopes']['passed'])
                self.assertEqual(scopes.call_count, 1)
                m.check_output(output)


    def test_raw_trace_identity_and_transaction_failures_all_counts(self):
        import json
        for variant in 'ABCD':
            for count in (1, 10):
                raw = self.raw_trace(variant, count)
                lines = raw.splitlines()
                for failure in ('missing', 'identity', 'transaction'):
                    changed = []
                    for line in lines:
                        if line.startswith('DELIVERY '):
                            event = json.loads(line[len('DELIVERY '):])
                            if failure == 'missing' and event['operation'] == 'endpoint_pixels':
                                continue
                            if failure == 'identity' and event['operation'] == 'endpoint_metadata':
                                event['transaction'] += 999
                            if failure == 'transaction' and event['operation'] in ('reusable_completion_ack', 'oneshot_ack'):
                                event['outcome'] = 'failed'
                            line = 'DELIVERY ' + json.dumps(event)
                        changed.append(line)
                    report = m.gate.analyzer.analyze('\n'.join(changed), '/raw', variant, [f.sample()] * count)
                    with self.subTest(variant=variant, count=count, failure=failure), self.assertRaises(ValueError):
                        m.v4_gate(report, variant, count)


if __name__ == '__main__':
    unittest.main()
