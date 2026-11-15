import copy
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


a = module('test_work_audit', 'audit-preview-verification-work.py')
i = module('test_work_independent', 'verify-preview-verification-work.py')


def events(service=20, observation=1, offset=0):
    result = []
    counter = 0
    clock = offset
    def span(operation, parent, validation, ordinal=-1, children=()):
        nonlocal counter, clock
        counter += 1
        identity = counter
        validation = identity if operation in ('generation', 'runtime') else validation
        event = dict(version=1, pid=10, tid=11, service=service, observation=observation,
                     job=None, worker=None, preparation=None, validation=validation, span=identity,
                     parent=parent, ordinal=ordinal, operation=operation)
        result.append(dict(event, ns=clock, edge='begin', outcome='unavailable'))
        clock += 1
        for child in children:
            if isinstance(child, tuple):
                name, index, nested = child
                span(name, identity, validation, index, nested)
            else:
                span(child, identity, validation)
        result.append(dict(event, ns=clock, edge='end', outcome='returned'))
        clock += 1
    file_ops = ('record_prepare', 'attributes', 'file_open', 'read_hash', 'digest_compare')
    runtime = ('initial_path_manifest', ('manifest_parse', -1, ('manifest_read',)), 'manifest_policy',
               ('file', 0, tuple((name, 0, ()) for name in file_ops)),
               ('file', 1, tuple((name, 1, ()) for name in file_ops)), 'required_files', 'inventory')
    span('generation', 0, 0, children=('protected_base', 'selector_descriptors', 'protected_generation',
         ('nested_runtime', -1, (('runtime', -1, runtime),)), 'generation_manifest_open_read',
         'generation_manifest_parse_policy', 'generation_manifest_digest', 'generation_final_identity'))
    return result


def fixture(root):
    execution = root / 'sample-execution'
    report = root / 'sample-analysis'
    package = root / 'cpu-package'
    built = root / 'built'
    source = root / 'source-package'
    for p in (execution / 'observations', report, package, built / 'validation/C/runtime', source):
        p.mkdir(parents=True)
    mapping = []
    for ordinal, data in enumerate((b'abc', b'')):
        path = built / f'validation/C/runtime/usr/{ordinal}'
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(data)
        mapping.append(dict(ordinal=ordinal, path=f'usr/{ordinal}', size=len(data), sha256=i.digest(path)))
    a.write(built / 'validation/C/runtime/manifest.json', dict(files=[{k: v for k, v in r.items() if k != 'ordinal'} for r in mapping]))
    a.write(built / 'validation/C/manifest-ordinals.json', mapping)
    inventory = {}
    for name in ('holonight-images/src/isolated/generation.cpp', 'holonight-images/src/isolated/verification.cpp',
                 'holonight-images/src/isolated/runtime.cpp', 'holonight-images/src/isolated/helper.cpp',
                 'holonight-file-browser/src/preview/session_pool.cpp',
                 'holonight-file-browser/src/preview/preview_service.cpp'):
        path = source / 'validation/C/source' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('// RuntimeOwner refresh() verifyRuntime()\n')
        inventory[name] = i.digest(path)
    a.write(source / 'validation/C/source-inventory.json', dict(source=inventory))
    for p in (source, built):
        a.o.seal(p)
    a.write(package / 'inputs.json', dict(built=str(built), package=str(source), mapping=mapping,
            seals={str(p): i.digest(p / 'seal.json') for p in (source, built)}))
    a.o.seal(package)
    commands, invocations, report_rows = [], [], []
    for index in range(10):
        warmup = index < 2
        count = 1 if warmup else 5
        arm = ('unprofiled', 'profiled')[index % 2]
        block = None if warmup else (index-2)//2
        invocation = dict(warmup=warmup, observations=count, arm=arm, block=block)
        target = execution / 'observations' / f'{index:03}.json'
        entry = dict(invocation=invocation, argv=[str(target)])
        commands.append(entry)
        invocations.append(dict(index=index, status='passed', entry=entry))
        records, life, unassigned = [], [], []
        for obs in range(count+1):
            observation = obs or None
            start = obs*1000
            for phase, left, right in (('service_construction', start, start+1),
                                       ('generation_validation', start+2, start+200)):
                pair = []
                for edge, ns in (('begin', left), ('end', right)):
                    event = dict(pid=10, tid=11, service=20+obs, observation=obs, phase=phase, edge=edge, ns=ns)
                    records.append('TRACE ' + json.dumps(event))
                    pair.append(dict(event, file=str(target), line=len(records)))
                span = dict(phase=phase, start=left, stop=right, begin=pair[0], end=pair[1])
                (unassigned if obs == 0 else life).append(span)
            raw = events(20+obs, observation, start+3)
            # Span IDs are process-local, not per validation.
            for event in raw:
                for key in ('span', 'validation'):
                    event[key] += obs*100
                if event['parent']:
                    event['parent'] += obs*100
                records.append('VALIDATION ' + json.dumps(event))
        target.with_suffix('.stderr').write_text('\n'.join(records)+'\n')
        target.with_suffix('.stdout').write_text('')
        raw = a.v.spans(a.v.records(target))
        observations, setup = [], []
        for obs in range(count+1):
            spans = [s for s in raw if s['begin']['service'] == 20+obs]
            root_span = next(s for s in spans if s['parent'] == 0)
            part = dict(spans=spans, duration_ns=root_span['stop']-root_span['start'], files=a.v.mapped_files(spans, mapping))
            saved = dict(observation=obs or None, validation=part,
                         endpoints={key: dict(harness_latency_ns=ns) for key, ns in (('pixels', 300), ('metadata', 400))})
            (observations if obs else setup).append(saved)
            if obs and not warmup:
                report_rows.append(dict(invocation=index, observation=obs, arm=arm, block=block, validation_ns=part['duration_ns'],
                                        pixel_ns=300, metadata_ns=400))
        a.write(target.with_suffix('.cpu-observations.json'), observations)
        a.write(target.with_suffix('.validation-setup.json'), setup)
        a.write(target.with_suffix('.v3.json'), dict(unassigned=unassigned,
            accounting=[dict(sample=obs-1, timeline=[x for x in life if x['begin']['observation'] == obs])
                        for obs in range(1, count+1)]))
    a.write(execution / 'preregistration.json', dict(package=str(package), package_seal=i.digest(package / 'seal.json'), commands=commands))
    a.write(execution / 'assessment.json', dict(status='complete', invocations=invocations))
    a.o.seal(execution)
    a.write(report / 'assessment.json', dict(status='complete', observations=40, warmups=2))
    a.write(report / 'observations.json', report_rows)
    a.write(report / 'tails.json', {arm: {field: [dict(invocation=r['invocation'], observation=r['observation'], value=r[field])
            for r in report_rows if r['arm'] == arm] for field in ('validation_ns', 'pixel_ns', 'metadata_ns')}
            for arm in ('unprofiled', 'profiled')})
    a.o.seal(report)
    for suffix in ('-independent.json', '-final-verification.json'):
        a.write(root / ('sample'+suffix), dict(status='passed', experiment_status='complete',
                execution_seal=i.digest(execution / 'seal.json'), package_seal=i.digest(package / 'seal.json'),
                invocations=10, measured_observations=40, warmup_observations=2))
    return execution, report


class VerificationWorkTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name in ('subprocess.Popen', 'subprocess.run', 'subprocess.check_output', 'os.system', 'os.popen', 'os.fork', 'os.posix_spawn'):
            self.stack.enter_context(patch(name, side_effect=AssertionError('offline only: launch forbidden')))
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory(dir=ROOT / 'build')))

    def test_nested_passes_zero_bytes_and_separate_populations(self):
        execution, report = fixture(self.root)
        output = self.root / 'audit'
        result = a.audit(execution, report, output)
        self.assertEqual(result['status'], 'complete', result)
        rows = a.read(output / 'accounting.json')
        self.assertEqual(len(rows), 52)
        self.assertEqual(sum(r['inferred_bytes'] for r in rows if r['population'] == 'measured'), 120)
        self.assertTrue(all(len(r['files']) == 2 and r['files'][1]['bytes_per_second'] == 0 for r in rows))
        self.assertEqual(result['service_lifetimes'], 52)
        self.assertEqual(i.verify(output)['status'], 'passed')
        # Tampering remains detectable after the output is resealed.
        rows[0]['inferred_bytes'] += 1
        a.write(output / 'accounting.json', rows)
        a.o.seal(output)
        with self.assertRaisesRegex(ValueError, 'accounting mismatch'):
            i.verify(output)

    def test_collisions_preserve_existing_output(self):
        output = self.root / 'audit'
        output.mkdir()
        (output / 'sentinel').write_text('keep')
        with self.assertRaises(ValueError):
            a.audit(self.root / 'execution', self.root / 'report', output)
        self.assertEqual((output / 'sentinel').read_text(), 'keep')

    def test_tampered_seal_manifest_source_and_verification_block(self):
        for kind in ('seal', 'manifest', 'source', 'verification'):
            with self.subTest(kind=kind):
                root = self.root / kind
                root.mkdir()
                execution, report = fixture(root)
                if kind == 'seal':
                    (execution / 'assessment.json').write_text('{}')
                elif kind == 'manifest':
                    (root / 'built/validation/C/runtime/usr/0').write_bytes(b'changed')
                elif kind == 'source':
                    next((root / 'source-package').rglob('generation.cpp')).write_text('changed')
                    a.o.seal(root / 'source-package')
                else:
                    a.write(root / 'sample-independent.json', dict(status='failed'))
                result = a.audit(execution, report, root / 'audit')
                self.assertEqual(result['status'], 'blocked')
                a.o.check_output(root / 'audit')

    def test_missing_duplicate_exception_and_nonpositive_spans_rejected(self):
        mapping = [dict(ordinal=n, path=str(n), size=0, sha256='0'*64) for n in range(2)]
        for kind in ('missing', 'duplicate', 'ordinal', 'zero', 'negative', 'exception'):
            with self.subTest(kind=kind):
                raw = events()
                if kind == 'missing':
                    raw.pop()
                if kind == 'duplicate':
                    raw.insert(1, copy.deepcopy(raw[0]))
                if kind == 'ordinal':
                    for row in raw:
                        if row['ordinal'] == 1:
                            row['ordinal'] = 0
                if kind in ('zero', 'negative'):
                    for index, row in enumerate(raw):
                        if row['operation'] == 'read_hash' and row['edge'] == 'end':
                            row['ns'] = raw[index-1]['ns'] - (kind == 'negative')
                if kind == 'exception':
                    raw[-1]['outcome'] = 'exception'
                with self.assertRaises(ValueError):
                    spans = a.v.spans(raw)
                    root = next(s for s in spans if s['parent'] == 0)
                    part = dict(spans=spans, files=a.v.mapped_files(spans, mapping), duration_ns=root['stop']-root['start'])
                    a.accounting(part, mapping)

    def test_p95_ties_and_summed_throughput(self):
        self.assertEqual(a.distribution([1]*18+[2, 2])['p95'], 2)
        rows = [dict(population='measured', arm='profiled', block=0, validation_ns=10,
                     read_hash_ns=duration, residual_validation_ns=10-duration, inferred_bytes=size, bytes_per_second=size*1e9/duration,
                     files=[dict(ordinal=0, read_hash_ns=duration, inferred_bytes=size, bytes_per_second=size*1e9/duration)])
                for size, duration in ((10, 2), (10, 8))]
        pooled = a.summarize(rows)[0]['pooled']
        self.assertEqual(pooled['bytes_per_second'], 2e9)

    def test_explicit_refresh_without_lifecycle_identity_blocks(self):
        execution, report = fixture(self.root)
        target = execution / 'observations/002.json'
        # A second refresh in the same service must never be labelled another
        # construction or silently assigned to the nearest observation.
        raw = events(service=21, observation=1, offset=9000)
        for event in raw:
            for key in ('span', 'validation'):
                event[key] += 9000
            if event['parent']:
                event['parent'] += 9000
        with target.with_suffix('.stderr').open('a') as stream:
            for event in raw:
                stream.write('VALIDATION ' + json.dumps(event) + '\n')
        a.o.seal(execution)
        for suffix in ('-independent.json', '-final-verification.json'):
            path = self.root / ('sample'+suffix)
            record = a.read(path)
            record['execution_seal'] = i.digest(execution / 'seal.json')
            a.write(path, record)
        result = a.audit(execution, report, self.root / 'audit')
        self.assertEqual(result['status'], 'blocked')
        self.assertIn('unexplained validation roots', result['failure'])

    def test_unclassified_lifecycle_rejected(self):
        root = dict(start=5, stop=10, begin=dict(pid=1, tid=1, service=1, observation=1))
        with self.assertRaisesRegex(ValueError, 'unclassified'):
            a.lifecycle_binding(root, dict(accounting=[dict(sample=0, timeline=[])]), 1, False)


if __name__ == '__main__':
    unittest.main()
