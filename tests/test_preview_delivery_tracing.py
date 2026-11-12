"""Deterministic v4 accounting and frozen-source preparation, never native execution."""
import ast
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


p = module('prepare_delivery', 'prepare-preview-delivery-tracing.py')
a = module('account_delivery', 'analyze-preview-delivery-tracing.py')
RETAINED = ROOT / 'build/preview-tracing-overhead-20261112'
PRIOR = ROOT / 'build/preview-delivery-gaps-v3-analysis-20261112-05'


def event(ns, operation, edge='point', span=None, **extra):
    return dict(dict(version=4, ns=ns, pid=1, tid=10, service=2, observation=3, job=4,
                     worker=5, preparation=6, generation=7, session=8, transaction=9,
                     publication=None, endpoint='unavailable', operation=operation,
                     edge=edge, span=span, outcome='unavailable'), **extra)


def span(start, stop, operation, number, **extra):
    return [event(start, operation, 'begin', number, **extra), event(stop, operation, 'end', number, **extra)]


def run(events, variant='A'):
    return a.analyze('\n'.join('DELIVERY ' + json.dumps(e) for e in events), '/synthetic.stderr', variant)


def delivery():
    fields = dict(publication=50, endpoint='final_result')
    values = span(10, 15, 'enqueue_call', 1, **fields)
    for start, stop, op, number in ((12, 30, 'callback_execution', 2), (13, 29, 'apply_result', 3), (16, 28, 'changed_emission', 4)):
        values += span(start, stop, op, number, tid=20, **fields)
    values += [event(14, 'result_decision', outcome='accepted', tid=20, **fields),
               event(17, 'harness_entry', tid=20, **fields), event(18, 'latency_capture', tid=20, **fields),
               event(19, 'endpoint_pixels', tid=20, **fields), event(20, 'endpoint_metadata', tid=20, **fields)]
    return values


class AccountingTests(unittest.TestCase):
    def test_all_four_lifecycle_paths_and_repeated_retirement(self):
        for variant in 'ABCD':
            values = span(1, 9, 'transaction_wrapper', 10)
            values += span(2, 3, 'reusable_completion_ack' if variant in 'CD' else 'oneshot_ack', 11)
            if variant in 'AB':
                values += span(4, 5, 'helper_exit', 12)
                values += span(6, 7, 'effective_cleanup', 13, outcome='verified')
            if variant == 'B':
                values += span(6, 8, 'retirement_call', 14, outcome='effective_retirement')
                values += span(9, 10, 'retirement_call', 15, outcome='already_retired')
            report = run(values, variant)
            self.assertEqual(report['status'], 'complete', report['issues'])
            self.assertEqual(report['cleanup_availability'], 'observed' if variant in 'AB' else 'unavailable')

    def test_cross_thread_handoff_overlap_and_dual_endpoints(self):
        report = run(delivery())
        self.assertEqual(report['status'], 'complete', report['issues'])
        row = report['handoffs'][0]
        self.assertEqual(row['enqueue_call_ns'], 5)
        self.assertEqual(row['enqueue_to_callback_elapsed_ns'], 2)
        self.assertEqual(row['callback_execution_ns'], 18)
        self.assertEqual([e['endpoint'] for e in row['endpoints']], ['pixels', 'metadata'])
        self.assertEqual(row['endpoints'][0]['record']['file'], '/synthetic.stderr')
        self.assertGreater(row['endpoints'][0]['record']['line'], 0)

    def test_nested_storage_metadata_skips_failures_and_inclusive_union(self):
        values = span(1, 20, 'store_raster', 1) + span(2, 18, 'thumbnail_store', 2, outcome='failure_checkpoint_1')
        values += span(3, 12, 'png_serialization', 3, outcome='failure')
        values += [event(20, 'store_raster', outcome='skipped'), event(21, 'memory_insert', outcome='skipped'), event(22, 'raster_exit', outcome='checkpoint_1')]
        report = run(values)
        self.assertEqual(report['status'], 'complete')
        self.assertEqual(report['categories']['storage']['union_ns'], [[1, 20]])
        self.assertEqual(sum(s['inclusive_ns'] for s in report['spans']), 44)
        self.assertEqual(report['categories']['metadata']['spans'], [])

    def test_cancellation_stale_timeout_rejections(self):
        for reason in ('cancelled', 'stale', 'timed_out'):
            values = [e for e in delivery() if e['operation'] not in ('changed_emission', 'harness_entry', 'latency_capture', 'endpoint_pixels', 'endpoint_metadata')]
            next(e for e in values if e['operation'] == 'result_decision')['outcome'] = reason
            self.assertEqual(run(values)['status'], 'complete')
            values += span(16, 28, 'changed_emission', 100, tid=20, publication=50, endpoint='final_result')
            self.assertEqual(run(values)['status'], 'blocked')

    def test_synchronous_apply_must_execute_on_callback_thread(self):
        values = delivery()
        for e in values:
            if e['operation'] == 'apply_result':
                e['tid'] = 30
        self.assertEqual(run(values)['status'], 'blocked')

    def test_generation_session_job_and_worker_isolation(self):
        for field in ('generation', 'session', 'transaction', 'job', 'worker', 'service', 'observation', 'preparation', 'endpoint'):
            values = delivery()
            values[-1][field] = 'pixel_result' if field == 'endpoint' else 100
            self.assertEqual(run(values)['status'], 'blocked', field)

    def test_missing_boundary_unavailable_duplicate_blocked_and_ordering(self):
        values = span(1, 2, 'metadata_format', 1)
        self.assertEqual(run(values[:1])['unavailable'][0]['reason'], 'missing_span_boundary')
        for bad in (values + values, list(reversed(span(3, 1, 'metadata_format', 2)))):
            self.assertEqual(run(bad)['status'], 'blocked')
        values = delivery()
        next(e for e in values if e['operation'] == 'harness_entry')['ns'] = 1
        self.assertEqual(run(values)['status'], 'blocked')

    def test_malformed_fields_unknowns_and_json_duplicates(self):
        for field, value in (('version', 3), ('pid', True), ('tid', 0), ('generation', 0), ('span', None), ('ns', -1)):
            value_event = span(1, 2, 'metadata_format', 1)[0]
            value_event[field] = value
            self.assertEqual(run([value_event])['status'], 'blocked', field)
        self.assertEqual(run([event(1, 'unknown', generation=None, session=None)])['status'], 'complete')
        self.assertEqual(a.analyze('DELIVERY {"version":4,"version":4}', '/raw', 'A')['status'], 'blocked')

    def test_job_cannot_cross_generations_and_unknown_endpoint_is_unavailable(self):
        values = delivery()
        values += [event(31, 'memory_insert', generation=99, outcome='skipped')]
        self.assertEqual(run(values)['status'], 'blocked')
        report = run([event(1, 'endpoint_pixels', publication=None)])
        self.assertEqual(report['unavailable'][0]['reason'], 'endpoint_identity_unavailable')

    def test_ambiguous_cleanup_and_invalid_outcomes(self):
        values = span(1, 2, 'effective_cleanup', 1, outcome='verified')
        self.assertEqual(run(values + span(3, 4, 'effective_cleanup', 2, outcome='verified'))['status'], 'blocked')
        self.assertEqual(run(span(1, 2, 'retirement_call', 3, outcome='verified'))['status'], 'blocked')

    def test_historical_parser_ignores_supplement_and_clipped_union(self):
        trace = dict(version=3, ns=1, pid=1, tid=10, request='diagnostic', object='0x0', slot=-1,
                     phase='decode_exchange_including_transport', edge='begin', service=2, observation=3, job=4, worker=5, preparation=0, role='demand')
        lines = ['TRACE ' + json.dumps(trace), 'TRACE ' + json.dumps(dict(trace, ns=5, edge='end'))]
        for phase, ns in (('pixels', 19), ('metadata', 20)):
            lines.append('TRACE ' + json.dumps(dict(trace, ns=ns, phase=phase, edge='point', tid=20)))
        lines += ['DELIVERY ' + json.dumps(dict(e, preparation=None)) for e in delivery() + span(2, 25, 'metadata_format', 60)]
        text = '\n'.join(lines)
        report = a.analyze(text, '/raw', 'A')
        self.assertEqual(report['status'], 'complete', report['issues'])
        self.assertEqual(len(report['historical']['events']), 4)
        self.assertEqual(report['windows'][0]['clipped_union_ns'], [[5, 19]])
        self.assertEqual(report['windows'][1]['union_ns'], 15)
        self.assertEqual(report['windows'][0]['boundary']['line'], 2)


@unittest.skipUnless(RETAINED.exists(), 'retained local package is unavailable')
class PreparationTests(unittest.TestCase):
    def test_all_variant_anchor_reviews_preserve_d_and_latency_order(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temporary:
            for variant in 'ABCD':
                base = Path(temporary) / variant
                for category in ('source', 'harness-source'):
                    shutil.copytree(RETAINED / (variant + 'T') / category, base / category)
                before = p.inventory(RETAINED / (variant + 'T') / 'source')
                anchors = p.patch(base, Path(temporary) / 'trace.h', variant)
                self.assertGreater(len(anchors), 25)
                self.assertEqual(before, p.inventory(RETAINED / (variant + 'T') / 'source'))
                if variant == 'D':
                    pool = 'holonight-file-browser/src/preview/session_pool.cpp'
                    self.assertEqual((base / 'source' / pool).read_text().splitlines()[1:], (RETAINED / 'DT/source' / pool).read_text().splitlines()[1:])
                harness = (base / 'harness-source/reuse.cpp').read_text()
                entry = harness.index('const auto delivery_entry')
                capture = harness.index('const auto latency', entry)
                emission = harness.index('DeliveryTrace::event', entry)
                self.assertLess(entry, capture)
                self.assertLess(capture, emission)

    def test_missing_and_duplicate_anchors_fail(self):
        for change in ('missing', 'duplicate'):
            with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temporary:
                base = Path(temporary)
                for category in ('source', 'harness-source'):
                    shutil.copytree(RETAINED / 'AT' / category, base / category)
                client = base / 'source/holonight-images/src/isolated/client.cpp'
                text = client.read_text()
                anchor = 'const SourceCoordinator& coordinate) const {'
                client.write_text(text.replace(anchor, 'changed') if change == 'missing' else text + '\n' + anchor)
                with self.assertRaisesRegex(ValueError, 'missing/duplicate anchor'):
                    p.patch(base, base / 'trace.h', 'A')

    def test_invalid_existing_destinations_and_hash_failures_preserved(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temporary:
            base = Path(temporary)
            for output in (RETAINED / 'out', PRIOR / 'out', ROOT / 'out', base):
                with self.assertRaises((ValueError, FileExistsError)):
                    p.prepare(RETAINED, PRIOR, output)
            prior = base / 'prior'
            prior.mkdir()
            evidence = base / 'evidence'
            evidence.write_text('unchanged')
            (prior / 'input-integrity.json').write_text(json.dumps(dict(unchanged=True, before={str(evidence): 'wrong'}, after={str(evidence): 'wrong'})))
            output = base / 'out'
            with patch('subprocess.Popen', side_effect=AssertionError('no subprocess authorized')), patch('os.system', side_effect=AssertionError('no shell authorized')):
                result = p.prepare(RETAINED, prior, output)
            self.assertEqual(result['status'], 'blocked')
            self.assertTrue(result['unchanged'])
            self.assertIn('integrity mismatch', result['issues'][0])
            self.assertTrue((output / 'manifest.json').exists())
            self.assertIn('UNCOMPILED', (output / 'README.md').read_text())

    def test_full_preparation_without_process_execution_and_unchanged_inputs(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temporary:
            output = Path(temporary) / 'output'
            with patch('subprocess.Popen', side_effect=AssertionError('no subprocess authorized')), patch('os.system', side_effect=AssertionError('no shell authorized')):
                result = p.prepare(RETAINED, PRIOR, output)
            self.assertEqual(result['status'], 'prepared', result['issues'])
            self.assertEqual(result['before'], result['after'])
            self.assertEqual(set(result['outputs']), set('ABCD'))
            for variant in 'ABCD':
                self.assertEqual(result['outputs'][variant], p.inventory(output / variant))
                self.assertTrue((output / variant / 'overlay.diff').stat().st_size)
                self.assertTrue(json.loads((output / variant / 'probe-to-source.json').read_text())['probes'])

    def test_preparation_has_no_execution_calls(self):
        tree = ast.parse(Path(p.__file__).read_text())
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any('subprocess' in ast.unparse(node) for node in imports))
        calls = [ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)]
        self.assertFalse(any(c in ('os.system', 'os.popen', 'exec', 'eval') or c.startswith('subprocess.') for c in calls))


if __name__ == '__main__':
    unittest.main()
