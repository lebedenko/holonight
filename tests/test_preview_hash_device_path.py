import copy
import importlib.util
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


a = module('device_audit_test', 'audit-preview-hash-device-path.py')
v = module('device_checker_test', 'verify-preview-hash-device-path.py')
h = module('device_fixture_test', 'verify-preview-hash-throughput.py')


def fixture(root):
    mapping = [dict(ordinal=0, path='empty', size=0, sha256='empty-digest'),
               dict(ordinal=1, path='payload', size=3, sha256='payload-digest')]
    schedule = h.expected_schedule()
    a.write(root / 'preregistration.json', dict(mapping=mapping, schedule=schedule))
    rows = [dict(type='identity')]
    for sweep in schedule:
        for f in mapping:
            # Unbalanced sweeps make accidental individual pairing easy to detect.
            ns = 20 + sweep['sweep'] * 3
            if sweep['case'] == 'qt_device':
                ns += -5 if f['ordinal'] == 0 else 11
            rows.append(dict(sweep, type='file', ordinal=f['ordinal'], bytes=f['size'], sha256=f['sha256'],
                             init_ns=1, update_ns=ns, final_ns=1))
        rows.append(dict(type='sweep_end', index=sweep['index'], elapsed_ns=1000))
    (root / 'native.stdout').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    a.write(root / 'summary.json', dict(ratios=[dict(block=b, numerator='qt_device', denominator='qt_file', ratio=52/58) for b in range(5)]))
    return mapping, rows


def identity_fixture(root):
    host = Path(sys.executable).resolve()
    prepared = root / 'prepared'
    prepared.mkdir()
    debug = dict(path=str(host), sha256=a.digest(host), build_id=v.build_id(host))
    a.write(prepared / 'symbols.json', {'libQt6Core.so.6': debug})
    a.seal(prepared)
    (root / 'BUILDINFO').write_text('pkgver = 6.12.0-5\n')
    (root / 'PKGINFO').write_text('pkgname = qt6-base\n')
    (root / 'libQt6Core.so').write_bytes(host.read_bytes())
    package = root / 'package.tar'
    with tarfile.open(package, 'w') as archive:
        for name, member in (('BUILDINFO', '.BUILDINFO'), ('PKGINFO', '.PKGINFO'), ('libQt6Core.so', 'usr/lib/libQt6Core.so.6.12.0')):
            archive.add(root / name, arcname=member)
    identity = dict(package=str(package), package_sha256=a.digest(package), host=str(host), host_sha256=a.digest(host),
                    build_id=debug['build_id'], debug=debug, symbols_manifest=str(prepared / 'symbols.json'),
                    symbols_manifest_sha256=a.digest(prepared / 'symbols.json'), prepared_seal=a.digest(prepared / 'seal.json'))
    a.write(root / 'identity.json', identity)
    return identity


class DevicePathTests(unittest.TestCase):
    def test_signed_block_means_reconcile_and_preserve_empty_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mapping, rows = fixture(root)
            result = a.accounting(rows, mapping)
            v.check_accounting(root, result)
            block = result[0]
            self.assertEqual(block['device_sum_ns'], 290)
            self.assertEqual(block['streaming_sum_ns'], 260)
            self.assertEqual(block['difference_mean_ms'], 6 / 1e6)
            self.assertEqual([f['difference_sum_ns'] for f in block['files']], [-25, 55])
            self.assertEqual(block['files'][0]['size'], 0)
            self.assertEqual(sum(f['difference_sum_ns'] for f in block['files']), 30)

    def test_missing_duplicate_ordinals_rejected_by_both_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mapping, rows = fixture(root)
            for bad in (rows[:16] + rows[17:], rows + [rows[16]]):
                with self.assertRaises(ValueError):
                    a.accounting(bad, mapping)
                (root / 'native.stdout').write_text(''.join(json.dumps(r) + '\n' for r in bad))
                with self.assertRaises((ValueError, StopIteration)):
                    v.check_accounting(root, a.accounting(rows, mapping))

    def test_accounting_tampering_rejected_after_resealing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mapping, rows = fixture(root)
            result = a.accounting(rows, mapping)
            result[0]['files'][0]['difference_mean_ms'] *= -1
            a.write(root / 'accounting.json', result)
            a.seal(root)
            v.sealed(root)
            with self.assertRaisesRegex(ValueError, 'accounting'):
                v.check_accounting(root, v.read(root / 'accounting.json'))

    def test_package_host_debug_identity_mismatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            identity = identity_fixture(root)
            v.check_identity(root)
            for key in ('package_sha256', 'host_sha256', 'build_id', 'symbols_manifest_sha256', 'prepared_seal'):
                changed = copy.deepcopy(identity)
                changed[key] = 'wrong'
                a.write(root / 'identity.json', changed)
                with self.assertRaises(ValueError):
                    v.check_identity(root)
            changed = copy.deepcopy(identity)
            changed['debug']['build_id'] = 'wrong'
            a.write(root / 'identity.json', changed)
            with self.assertRaisesRegex(ValueError, 'debug'):
                v.check_identity(root)

    def test_recipe_and_source_checksum_mismatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            recipe = "sha256sums=('" + 'a'*64 + "')\nprepare() {}\n"
            (root / 'PKGBUILD').write_text(recipe)
            (root / 'BUILDINFO').write_text('pkgbuild_sha256sum = ' + 'b'*64 + '\n')
            a.write(root / 'source-provenance.json', dict(status='exact', files={}))
            with self.assertRaisesRegex(ValueError, 'recipe'):
                v.check_sources(root)
            (root / 'BUILDINFO').write_text('pkgbuild_sha256sum = ' + a.digest(root / 'PKGBUILD') + '\n')
            (root / 'qtbase.tar').write_bytes(b'wrong source')
            a.write(root / 'source-provenance.json', dict(status='exact', archive_sha256='a'*64, archive_actual_sha256='a'*64, files={}))
            with self.assertRaisesRegex(ValueError, 'source archive'):
                v.check_sources(root)

    def test_missing_sources_require_explicit_limitation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a.write(root / 'source-provenance.json', dict(status='limited', limitation='Unavailable primary source'))
            v.check_sources(root)
            a.write(root / 'source-provenance.json', dict(status='limited', limitation=''))
            with self.assertRaisesRegex(ValueError, 'limitation'):
                v.check_sources(root)

    def test_citation_drift_even_after_resealing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'source').write_text('first\nsecond\n')
            citation = dict(file='source', sha256=a.digest(root / 'source'), start=1, end=2, text='first\nsecond')
            a.write(root / 'citations.json', [citation])
            v.check_citations(root)
            citation['start'] = 2
            a.write(root / 'citations.json', [citation])
            a.seal(root)
            v.sealed(root)
            with self.assertRaisesRegex(ValueError, 'citation drift'):
                v.check_citations(root)

    def test_collision_and_partial_failure_preserve_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / 'keep'
            marker.write_text('keep')
            with self.assertRaisesRegex(ValueError, 'collision'):
                a.run(root / 'missing', root / 'verification', root)
            self.assertEqual(marker.read_text(), 'keep')
            partial = root / 'partial'
            result = a.run(root / 'missing', root / 'verification', partial)
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(result['stage'], 'bindings')
            v.sealed(partial)

    def test_verification_binding_and_consumed_evidence_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / 'evidence'
            evidence.mkdir()
            dependency = root / 'dependency'
            dependency.write_text('original')
            a.write(evidence / 'inputs.json', dict(identities={str(dependency): a.digest(dependency)}))
            a.write(evidence / 'assessment.json', dict(status='complete'))
            a.seal(evidence)
            verification = root / 'independent.json'
            record = dict(status='passed', evidence_seal=a.digest(evidence / 'seal.json'), measured_sweeps=125,
                          warmup_sweeps=5, measured_rows=7500, warmup_rows=300)
            a.write(verification, record)
            v.bind(evidence, verification)
            dependency.write_text('drift')
            with self.assertRaisesRegex(ValueError, 'consumed identity drift'):
                v.bind(evidence, verification)
            record['evidence_seal'] = 'wrong'
            a.write(verification, record)
            with self.assertRaisesRegex(ValueError, 'binding'):
                v.bind(evidence, verification)


if __name__ == '__main__':
    unittest.main()
