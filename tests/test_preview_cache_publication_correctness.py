"""Correctness v2 synthetic regressions. Starting any process is forbidden."""
import shutil
from types import SimpleNamespace
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
DIRECTORY = Path(__file__).resolve().parents[1] / 'tooling/preview-cache-publication'
sys.path.insert(0, str(DIRECTORY))
import correctness as c
import qualify
import stage
v = c.e.load('synthetic_correctness_v2_verifier', DIRECTORY / 'offline/verify_correctness_v2.py')
h = c.h


class CorrectnessTests(unittest.TestCase):
    def setUp(self):
        guard = patch('subprocess.Popen', side_effect=AssertionError('process execution forbidden'))
        guard.start()
        self.addCleanup(guard.stop)
        self.temporary = tempfile.TemporaryDirectory(dir=c.e.ROOT / 'build')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.built = c.e.ROOT / 'build/preview-cache-publication-native-20261117-01'

    def xml(self, names=None):
        names = names or c.protocol()['publication']
        root = ET.Element('testsuites', tests=str(len(names)), failures='0', errors='0', disabled='0')
        suite = ET.SubElement(root, 'testsuite')
        for name in names:
            classname, name = name.split('.')
            ET.SubElement(suite, 'testcase', classname=classname, name=name, status='run', result='completed')
        path = self.root / 'tests.xml'
        ET.ElementTree(root).write(path)
        return path, root

    def validate_both(self, path, required):
        self.assertEqual(c.validate_xml(path, required), v.xml_cases(path, required))

    def rejected_both(self, path, required):
        for validate in (c.validate_xml, v.xml_cases):
            with self.assertRaises((ValueError, ET.ParseError)):
                validate(path, required)

    def test_complete_explicit_membership(self):
        path, _ = self.xml()
        self.validate_both(path, c.protocol()['publication'])
        c.validate_membership(DIRECTORY / 'native')

    def test_missing_duplicate_extra_disabled_and_skipped_required_cases(self):
        required = c.protocol()['publication']
        for names in (required[:-1], required + [required[0]], required + ['Other.Extra'],
                      ['Publication.DISABLED_Progressive'] + required[1:]):
            path, _ = self.xml(names)
            self.rejected_both(path, required)
        for kind in ('skipped', 'failure'):
            path, root = self.xml()
            ET.SubElement(root.find('.//testcase'), kind)
            ET.ElementTree(root).write(path)
            self.rejected_both(path, required)
        path, root = self.xml()
        root.find('.//testcase').set('status', 'notrun')
        ET.ElementTree(root).write(path)
        self.rejected_both(path, required)

    def test_malformed_xml_is_rejected(self):
        path = self.root / 'bad.xml'
        path.write_text('<testsuites>')
        self.rejected_both(path, c.protocol()['publication'])

    def test_original_completion_regression_and_observer_order(self):
        source = (DIRECTORY / 'native/main.cpp').read_text()
        gate = source[source.index('void commitGate('):source.index('TEST(Publication, Cancellation')]
        self.assertNotIn('PreviewServiceTestAccess::active', source)
        self.assertLess(gate.index('QObject::connect'), gate.index('select(service, oldPath)'))
        self.assertIn('return replacement;', gate)
        self.assertIn('service.sourcePixelSize(), QSize(80, 40)', gate)
        self.assertRegex(gate, r'service.previewErrorKind\(\),\s*PreviewService::PreviewErrorKind::None')
        for name in ('CancellationDuringCommitSuppressesOldApplication',
                     'SupersessionDuringCommitCompletesReplacement', 'TimeoutDuringCommitSuppressesOldApplication',
                     'ShutdownDuringCommitFinishesAsynchronously'):
            self.assertIn('Publication.' + name, c.protocol()['publication'])

    def test_async_shutdown_wait_and_barrier_lifetimes(self):
        source = (DIRECTORY / 'native/main.cpp').read_text()
        gate = source[source.index('void commitGate('):source.index('TEST(Publication, Cancellation')]
        self.assertLess(gate.index('QSemaphore resume'), gate.index('PreviewService service'))
        self.assertLess(gate.index('bool stale'), gate.index('PreviewService service'))
        self.assertLess(gate.index('QSignalSpy stopped'), gate.index('select(service, oldPath)'))
        self.assertIn('EXPECT_TRUE(stopped.isEmpty())', gate)
        self.assertIn('EXPECT_EQ(service.image(), accepted)', gate)
        self.assertIn('resume.release();\n    finish(service, stopped);', gate)
        self.assertIn('return !stopped.isEmpty();', source)

    def schedule(self):
        rows = qualify.schedule(self.built, self.root)
        h.write(self.root / 'schedule.json', rows)
        return rows

    def test_independent_schedule_and_environment_propagation(self):
        rows = self.schedule()
        self.assertEqual(rows, v.verify_schedule(self.root, self.built, c.protocol()))
        row = next(r for r in rows if r['name'] == 'early-protected-publication')
        self.assertEqual(row['environment']['PUBLICATION_RUNTIME'], str(stage.runtime_path(self.root, 'early')))
        self.assertNotEqual(row['environment']['PUBLICATION_RUNTIME'], str(self.built / 'early/runtime'))
        row['environment']['TMPDIR'] = '/tmp'
        h.write(self.root / 'schedule.json', rows)
        with self.assertRaisesRegex(ValueError, 'environment'):
            v.verify_schedule(self.root, self.built, c.protocol())

    def test_invocation_passes_frozen_environment_and_shared_cleanup_deadline(self):
        row = next(r for r in self.schedule() if r['name'] == 'control-mutable-publication')
        class Process:
            pid = 123456789
            def wait(self, timeout):
                return 0
        seen = {}
        def launch(argv, **kwargs):
            seen.update(kwargs)
            self.assertEqual(argv, row['argv'])
            return Process()
        def terminate(process, deadline):
            seen['cleanup_deadline'] = deadline
        clean = dict(isolated=True, exit=0, stdout='', stderr='', cgroups=[])
        with patch.object(qualify.subprocess, 'Popen', side_effect=launch), \
             patch.object(qualify, 'scopes', return_value=clean), \
             patch.object(qualify.e, 'load', return_value=SimpleNamespace(terminate=terminate)), \
             patch.object(qualify.os, 'killpg', side_effect=ProcessLookupError):
            qualify.invoke(row, self.root)
        for key, value in row['environment'].items():
            self.assertEqual(seen['env'][key], value)
        self.assertTrue(seen['start_new_session'])
        self.assertEqual(seen['cwd'], c.e.ROOT)
        record = h.read(self.root / 'commands' / (row['name'] + '-result.json'))
        self.assertTrue(record['cleanup'])
        self.assertLessEqual(record['cleanup_seconds'], 5)
        self.assertIn('cleanup_deadline', seen)

    def test_only_protected_fixture_and_staging_are_privileged(self):
        rows = self.schedule()
        for row in rows:
            if row['privileged']:
                self.assertTrue(row['name'].endswith(('-stage', '-unstage', '-protected-fixture')))
                self.assertEqual(row['argv'][:2], ['sudo', '-n'])
                if row['cases']:
                    self.assertEqual(row['cases'], c.protocol()['protected_fixture'])
                    for key in ('HOLONIGHT_CACHE_INVOCATION', 'XDG_CACHE_HOME', 'TMPDIR'):
                        self.assertIn(key + '=' + row['environment'][key], row['argv'])
            if row['workload']:
                self.assertFalse(row['privileged'])
                self.assertNotEqual(row['uid'], 0)
        row = next(r for r in rows if r['name'] == 'control-protected-publication')
        row.update(privileged=True, uid=0)
        h.write(self.root / 'schedule.json', rows)
        with self.assertRaises(ValueError):
            v.verify_schedule(self.root, self.built, c.protocol())

    def test_wildcard_missing_or_reordered_schedule_is_rejected(self):
        for mutation in ('wildcard', 'missing', 'reordered'):
            rows = self.schedule()
            if mutation == 'wildcard':
                row = next(r for r in rows if r['cases'])
                row['argv'] = [a if not a.startswith('--gtest_filter=') else '--gtest_filter=*' for a in row['argv']]
            elif mutation == 'missing':
                rows.pop()
            else:
                rows[0], rows[1] = rows[1], rows[0]
            h.write(self.root / 'schedule.json', rows)
            with self.assertRaises(ValueError):
                v.verify_schedule(self.root, self.built, c.protocol())

    def test_collision_overlap_and_symlink_escape_preserve_existing_data(self):
        sentinel = self.root / 'sentinel'
        sentinel.write_text('retained')
        with self.assertRaisesRegex(ValueError, 'collision'):
            h.fresh(self.root, [])
        self.assertEqual(sentinel.read_text(), 'retained')
        with self.assertRaisesRegex(ValueError, 'overlaps'):
            h.fresh(self.root / 'overlap', [self.root])
        link = self.root / 'link'
        link.symlink_to('/tmp', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'destination must be'):
            h.fresh(link / 'child', [])

    def test_required_prerequisite_drift_is_rejected(self):
        protocol = c.protocol()
        protocol['ordinary'] = protocol['ordinary'][1:]
        with patch.object(c, 'protocol', return_value=protocol):
            with self.assertRaisesRegex(ValueError, 'prerequisite membership'):
                c.validate_membership(DIRECTORY / 'native')

    def test_stopped_schedule_accounts_for_skipped_and_unexecuted_cases(self):
        rows = self.schedule()
        row = next(r for r in rows if r['cases'])
        path = Path(next(a.split('xml:', 1)[1] for a in row['argv'] if a.startswith('--gtest_output=xml:')))
        path.parent.mkdir(parents=True, exist_ok=True)
        fixture, root = self.xml(row['cases'])
        cases = root.findall('.//testcase')
        ET.SubElement(cases[0], 'failure')
        for case in cases[1:]:
            ET.SubElement(case, 'skipped')
        ET.ElementTree(root).write(path)
        accounting = qualify.case_accounting(rows, self.root)
        self.assertEqual(accounting[0]['attempted'], row['cases'][:1])
        self.assertEqual(accounting[0]['unexecuted'], row['cases'][1:])
        for record in accounting[1:]:
            self.assertEqual(record['unexecuted'], record['required'])
            self.assertFalse(record['attempted'])

    def test_resealed_protocol_tampering_is_not_trusted(self):
        h.write(self.root / 'assessment.json', dict(phase='correctness-v2', status='qualified',
            decision='Evidence insufficient', observations=0))
        protocol = c.protocol()
        protocol['ordinary'].pop(0)
        h.write(self.root / 'protocol-v2.json', protocol)
        h.write(self.root / 'seal.json', h.inventory(self.root))
        h.sealed(self.root)
        with self.assertRaisesRegex(ValueError, 'protocol drift'):
            v.verify(self.root)

    def blocked_record(self):
        rows = self.schedule()
        fake_built = self.root / 'provider'
        fake_built.mkdir()
        h.write(fake_built / 'seal.json', {})
        h.write(fake_built / 'package.json', dict(prepared=True))
        rows = qualify.schedule(fake_built, self.root)
        h.write(self.root / 'schedule.json', rows)
        h.write(self.root / 'built.json', dict(path=str(fake_built), seal=v.BUILT_SEAL, inventory={}))
        h.write(self.root / 'package.json', dict(prepared=True))
        shutil.copyfile(DIRECTORY / 'CORRECTNESS-v2.json', self.root / 'protocol-v2.json')
        shutil.copytree(DIRECTORY / 'native', self.root / 'native-source')
        h.write(self.root / 'native-inputs.json', h.inventory(self.root / 'native-source'))
        tools = c.tools()
        (self.root / 'tools').mkdir()
        for path in tools:
            shutil.copyfile(path, self.root / 'tools' / Path(path).name)
        h.write(self.root / 'tools.json', tools)
        h.write(self.root / 'integrity.json', dict(unchanged=True))
        h.write(self.root / 'case-accounting.json', qualify.case_accounting(rows, self.root))
        (self.root / 'commands').mkdir()
        h.write(self.root / 'commands/compiler-command.json', rows[0])
        h.write(self.root / 'commands/compiler-result.json', dict(start_ns=1, stop_ns=2,
            exit=1, failure='compiler unavailable', cleanup=True, cleanup_seconds=.001))
        (self.root / 'commands/compiler.stdout').write_text('')
        (self.root / 'commands/compiler.stderr').write_text('compiler unavailable')
        h.write(self.root / 'assessment.json', dict(phase='correctness-v2', status='blocked',
            decision='Evidence insufficient', observations=0, attempted=['compiler'], completed=[],
            unexecuted=[row['name'] for row in rows[1:]], native_correctness='unvalidated',
            cleanup=True, failure='compiler unavailable'))
        # The mocked prerequisite package lives outside the execution artifact inventory.
        provider = Path(self.temporary.name + '-provider')
        fake_built.rename(provider)
        self.addCleanup(shutil.rmtree, provider)
        rows = qualify.schedule(provider, self.root)
        h.write(self.root / 'schedule.json', rows)
        h.write(self.root / 'built.json', dict(path=str(provider), seal=v.BUILT_SEAL, inventory={}))
        h.write(self.root / 'commands/compiler-command.json', rows[0])
        h.write(self.root / 'seal.json', h.inventory(self.root))
        digest, sealed = h.digest, h.sealed
        self.enterContext(patch.object(h, 'digest', side_effect=lambda path:
            v.BUILT_SEAL if path == provider / 'seal.json' else digest(path)))
        self.enterContext(patch.object(h, 'sealed', side_effect=lambda path: {} if path == provider else sealed(path)))
        self.enterContext(patch.object(c.e, 'package', return_value=dict(prepared=True)))
        self.enterContext(patch.object(c.e, 'load', return_value=SimpleNamespace(verify=lambda path:
            dict(commands=27, failed_command=None))))
        return rows

    def test_independent_verifier_accepts_stopped_record_and_rejects_resealed_accounting(self):
        self.blocked_record()
        self.assertEqual(v.verify(self.root)['outcome'], 'blocked')
        assessment = h.read(self.root / 'assessment.json')
        assessment['unexecuted'].pop()
        h.write(self.root / 'assessment.json', assessment)
        inventory = h.inventory(self.root)
        inventory.pop('seal.json')
        h.write(self.root / 'seal.json', inventory)
        with self.assertRaisesRegex(ValueError, 'stopped schedule accounting'):
            v.verify(self.root)

    def test_resealed_source_snapshot_tampering_is_rejected(self):
        self.blocked_record()
        source = self.root / 'native-source/main.cpp'
        source.write_text(source.read_text().replace('return replacement;', 'return true;'))
        h.write(self.root / 'native-inputs.json', h.inventory(self.root / 'native-source'))
        inventory = h.inventory(self.root)
        inventory.pop('seal.json')
        h.write(self.root / 'seal.json', inventory)
        with self.assertRaisesRegex(ValueError, 'native snapshot drift'):
            v.verify(self.root)

    def test_offline_verifier_imports_neither_qualifier_nor_build_implementation(self):
        import ast
        tree = ast.parse((DIRECTORY / 'offline/verify_correctness_v2.py').read_text())
        imports = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertNotIn('qualify', imports)
        self.assertNotIn('run', imports)
        self.assertNotIn('correctness', imports)


if __name__ == '__main__':
    unittest.main()
