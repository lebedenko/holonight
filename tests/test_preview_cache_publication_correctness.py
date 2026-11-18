"""Correctness v4 synthetic regressions. Starting any process is forbidden."""
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
v = c.e.load('synthetic_correctness_v4_verifier', DIRECTORY / 'offline/verify_correctness_v4.py')
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
                self.assertTrue(row['name'].endswith(('-stage', '-unstage', '-protected-fixture', '-authorization')) or row['name'] == 'authorization')
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
            with self.assertRaisesRegex(ValueError, 'prerequisite'):
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
        self.assertEqual(accounting[0]['skipped'], row['cases'][1:])
        for record in accounting[1:]:
            self.assertEqual(record['unexecuted'], record['required'])
            self.assertFalse(record['attempted'])

    def test_resealed_protocol_tampering_is_not_trusted(self):
        h.write(self.root / 'assessment.json', dict(phase='correctness-v4', status='qualified',
            decision='Evidence insufficient', observations=0))
        protocol = c.protocol()
        protocol['ordinary'].pop(0)
        h.write(self.root / 'protocol-v4.json', protocol)
        h.write(self.root / 'seal.json', h.inventory(self.root))
        h.sealed(self.root)
        with self.assertRaisesRegex(ValueError, 'protocol drift'):
            v.verify(self.root)

    def production_record(self, stop='compiler', cleanup=True, invalid_xml=False, invalid_fixture=False, preparation_failure=False, cleanup_denied=False, authenticate=False):
        output = self.root / 'preview-cache-publication-correctness-20261118-04'
        binding = dict(path=str(self.built), seal=v.BUILT_SEAL, inventory={})
        package = h.read(self.built / 'package.json')
        self.enterContext(patch.object(c, 'built_binding', side_effect=ValueError('provider unavailable') if preparation_failure else None,
                                      return_value=binding))
        digest, sealed, load = h.digest, h.sealed, c.e.load
        self.enterContext(patch.object(h, 'digest', side_effect=lambda path:
            ('invalid' if preparation_failure else v.BUILT_SEAL) if path == self.built / 'seal.json' else digest(path)))
        self.enterContext(patch.object(h, 'sealed', side_effect=lambda path: {} if path == self.built else sealed(path)))
        self.enterContext(patch.object(c.e, 'package', return_value=package))
        self.enterContext(patch.object(c.e, 'load', side_effect=lambda name, path:
            SimpleNamespace(verify=lambda path: dict(commands=27, failed_command=None))
            if name == 'independent_native_build_verifier' else load(name, path)))
        staging = set()
        real_lexists = os.path.lexists
        self.enterContext(patch.object(qualify.os.path, 'lexists', side_effect=lambda path:
            str(path) in staging or real_lexists(path)))
        production_invoke = qualify.invoke
        def invoke(row, root):
            if row['argv'] == ['sudo', '-n', '-v']:
                class Process:
                    pid = 123456789
                    def wait(self, timeout):
                        return 1 if row['name'] == stop or (cleanup_denied and row['name'] == 'control-unstage-authorization') else 0
                def launch(argv, **kwargs):
                    kwargs['stderr'].write('authorization denied' if row['name'] == stop or cleanup_denied else '')
                    return Process()
                with patch.object(qualify.subprocess, 'Popen', side_effect=launch), \
                     patch.object(qualify.time, 'monotonic_ns', side_effect=[row['index'] * 2 + 1, row['index'] * 2 + 2]), \
                     patch.object(qualify.e, 'load', return_value=SimpleNamespace(terminate=lambda *a, **k: None)), \
                     patch.object(qualify.os, 'killpg', side_effect=ProcessLookupError):
                    return production_invoke(row, root)
            target = root / 'commands'
            target.mkdir(exist_ok=True)
            h.write(target / (row['name'] + '-command.json'), row)
            failure = row['name'] == stop and not invalid_xml
            h.write(target / (row['name'] + '-result.json'), dict(start_ns=row['index'] * 2 + 1,
                stop_ns=row['index'] * 2 + 2, exit=1 if failure else 0,
                failure='synthetic failure' if failure else None, cleanup=cleanup if failure else True,
                cleanup_seconds=.001))
            (target / (row['name'] + '.stdout')).write_text(
                '[  PASSED  ] ' + str(len(row['cases'])) + ' tests' if row['cases'] else
                str(Path(sys.executable).resolve()) if row['name'].endswith('-linkage') else '')
            (target / (row['name'] + '.stderr')).write_text('synthetic failure' if failure else '')
            if failure:
                raise ValueError('synthetic failure')
            if row['name'] == 'fixtures':
                self.generate(root / 'fixtures')
                if invalid_fixture:
                    (root / 'fixtures/sample.jpg').unlink()
            if row['name'].endswith('-configure'):
                cache = root / row['arm'] / 'build/CMakeCache.txt'
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(''.join(name + '_DIR:PATH=' + str(self.built / row['arm'] / 'prefix/lib/cmake' / name) + '\n'
                    for name in ('HolonightImages', 'HolonightThumbnails', 'HolonightFileBrowser')))
            if row['cases']:
                path, xml = self.xml(row['cases'])
                if invalid_xml and row['name'] == stop:
                    xml.findall('.//testcase')[0].set('result', 'suppressed')
                path = Path(next(arg.split('xml:', 1)[1] for arg in row['argv'] if arg.startswith('--gtest_output=xml:')))
                path.parent.mkdir(parents=True, exist_ok=True)
                ET.ElementTree(xml).write(path)
                # xml() is only an in-memory factory here; its scratch file is not evidence.
                (self.root / 'tests.xml').unlink()
            if row['workload']:
                clean = dict(isolated=True, exit=0, stdout='', stderr='', cgroups=[])
                for phase in ('before', 'after'):
                    h.write(target / (row['name'] + '-scopes-' + phase + '.json'), clean)
            if row['name'].endswith('-stage'):
                arm = row['arm']
                staging.add(str(stage.runtime_path(root, arm)))
                tree = {'generations/synthetic': dict(uid=0, mode=0o755, sha256=None)}
                for name, sha in h.inventory(self.built / arm / 'runtime').items():
                    tree['generations/synthetic/' + name] = dict(uid=0, mode=0o644, sha256=sha)
                h.write(root / (arm + '-staging.json'), dict(tree=tree, owner=dict(output=str(root), arm=arm,
                    built=str(self.built), seal=v.BUILT_SEAL),
                    runtime=str(stage.runtime_path(root, arm))))
            if row['name'].endswith('-unstage'):
                arm = row['arm']
                staging.discard(str(stage.runtime_path(root, arm)))
                h.write(root / (arm + '-staging-cleanup.json'), dict(removed=True,
                    owner=dict(output=str(root), arm=arm, built=str(self.built), seal=v.BUILT_SEAL)))

        with patch.object(qualify, 'validate_request'), patch.object(qualify, 'invoke', side_effect=invoke), \
             patch.object(qualify.sys.stdin, 'isatty', return_value=True), \
             patch.object(qualify.os, 'tcgetpgrp', return_value=os.getpgrp()), \
             patch.object(qualify.subprocess, 'run') as authentication:
            qualify.qualify(self.built, output, authenticate=authenticate)
        if authenticate:
            authentication.assert_called_once_with(['sudo', '-v'], check=True)
        self.root = output
        return h.read(output / 'schedule.json')

    def generate(self, destination):
        import runpy
        with patch('ctypes.util.find_library', return_value='libwebp.so.7'), \
             patch.object(sys, 'argv', [str(c.generator()), str(destination)]):
            runpy.run_path(str(c.generator()), run_name='__main__')

    def blocked_record(self):
        return self.production_record()

    def test_provider_preparation_failure_has_no_executed_commands(self):
        self.production_record(preparation_failure=True)
        proof = v.verify(self.root)
        self.assertEqual(proof['outcome'], 'blocked')
        self.assertTrue(proof['preparation_failure'])
        self.assertEqual(proof['completed_commands'], 0)
        self.assertFalse((self.root / 'commands').exists())

    def test_successful_generator_with_missing_fixture_is_blocked(self):
        self.production_record(invalid_fixture=True)
        proof = v.verify(self.root)
        self.assertEqual(proof['outcome'], 'blocked')
        self.assertEqual(proof['failed_command'], 'fixtures')
        self.assertNotIn('sample.jpg', h.read(self.root / 'fixtures.json'))

    def test_failed_staging_removal_is_not_cleanup_success(self):
        self.production_record(stop='control-unstage')
        proof = v.verify(self.root)
        self.assertEqual(proof['outcome'], 'blocked')
        self.assertFalse(h.read(self.root / 'assessment.json')['cleanup'])

    def test_fully_qualified_record_uses_production_persistence(self):
        self.production_record(stop=None)
        self.assertEqual(v.verify(self.root)['outcome'], 'qualified')

    def test_compilation_failure_record_is_verifiable(self):
        self.production_record(stop='control-compile')
        self.assertEqual(v.verify(self.root)['failed_command'], 'control-compile')

    def test_test_failure_record_is_verifiable(self):
        self.production_record(stop='control-runtime-verification')
        self.assertEqual(v.verify(self.root)['failed_command'], 'control-runtime-verification')

    def test_successful_process_with_invalid_xml_is_blocked(self):
        self.production_record(stop='control-runtime-verification', invalid_xml=True)
        self.assertEqual(v.verify(self.root)['outcome'], 'blocked')

    def test_protocol_copy_preserves_frozen_bytes(self):
        self.production_record()
        self.assertEqual((self.root / 'protocol-v4.json').read_bytes(),
                         (DIRECTORY / 'CORRECTNESS-v4.json').read_bytes())
        self.assertEqual(h.digest(self.root / 'protocol-v4.json'), v.PROTOCOL_SHA256)
        self.assertEqual(v.verify(self.root)['outcome'], 'blocked')

    def test_preparation_and_cleanup_failures_are_retained(self):
        self.production_record(stop='fixtures', cleanup=False)
        self.assertEqual(v.verify(self.root)['outcome'], 'blocked')
        self.assertFalse(h.read(self.root / 'assessment.json')['cleanup'])

    def test_fixture_inventory_rejects_missing_modified_and_symlinked(self):
        self.production_record()
        sample = self.root / 'fixtures/sample.png'
        original = sample.read_bytes()
        for mutation in ('missing', 'modified', 'symlink'):
            with self.subTest(mutation=mutation):
                sample.unlink()
                if mutation == 'modified':
                    sample.write_bytes(b'changed')
                elif mutation == 'symlink':
                    sample.symlink_to(self.root / 'fixtures/sample.jpg')
                if mutation != 'symlink':
                    h.write(self.root / 'fixtures.json', h.inventory(self.root / 'fixtures'))
                    inventory = h.inventory(self.root)
                    inventory.pop('seal.json')
                    h.write(self.root / 'seal.json', inventory)
                with self.assertRaises(ValueError):
                    v.verify(self.root)
                if sample.is_symlink() or sample.exists():
                    sample.unlink()
                sample.write_bytes(original)

    def test_frozen_generator_orientation_and_metadata_transformation(self):
        self.generate(self.root / 'fixtures')
        self.assertTrue(c.fixtures(self.root / 'fixtures'))
        jpeg = (self.root / 'fixtures/sample.jpg').read_bytes()
        old = bytes.fromhex('ffe1002245786966000049492a0008000000010012010300010000000600000000000000')
        self.assertIn(old, jpeg)
        source = (DIRECTORY / 'native/main.cpp').read_text()
        import re
        literals = [''.join(re.findall(r'"([0-9a-f]+)"', value)) for value in
                    re.findall(r'QByteArray::fromHex\((.*?)\);', source, re.S)]
        self.assertIn(bytes.fromhex(literals[0]), jpeg)
        self.assertNotEqual(jpeg.replace(bytes.fromhex(literals[0]), bytes.fromhex(literals[1])), jpeg)

    def test_fixture_binding_and_prerequisite_order(self):
        rows = self.schedule()
        names = [row['name'] for row in rows]
        for arm in ('control', 'early'):
            ordered = [arm + '-' + name for name in ('runtime-verification', 'generation-ownership',
                'cleanup', 'scheduling', 'pool-lifecycle', 'preview')]
            self.assertEqual(sorted(ordered, key=names.index), ordered)
        row = next(row for row in rows if row['name'] == 'control-configure')
        row['argv'][-1] = '-DFIXTURES=/historical/fixtures'
        h.write(self.root / 'schedule.json', rows)
        with self.assertRaises(ValueError):
            v.verify_schedule(self.root, self.built, c.protocol())

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



    def test_successful_terminal_authentication_preserves_production_record(self):
        self.production_record(authenticate=True)
        self.assertEqual(v.verify(self.root)['outcome'], 'blocked')
        self.assertIn('authorization', h.read(self.root / 'assessment.json')['completed'])

    def test_denied_terminal_authentication_creates_no_attempt(self):
        output = self.root / 'denied'
        with patch.object(qualify, 'validate_request'), \
             patch.object(qualify.sys.stdin, 'isatty', return_value=True), \
             patch.object(qualify.os, 'tcgetpgrp', return_value=os.getpgrp()), \
             patch.object(qualify.subprocess, 'run', side_effect=qualify.subprocess.CalledProcessError(1, ['sudo', '-v'])):
            with self.assertRaises(qualify.subprocess.CalledProcessError):
                qualify.qualify(self.built, output, authenticate=True)
        self.assertFalse(output.exists())

    def test_owned_cleanup_after_stopped_schedule_is_verifiable(self):
        self.production_record(stop='control-protected-fixture-authorization')
        self.assertEqual(v.verify(self.root)['failed_command'], 'control-protected-fixture-authorization')
        self.assertTrue(h.read(self.root / 'assessment.json')['cleanup'])
        self.assertTrue((self.root / 'control-staging-cleanup.json').exists())

    def test_cleanup_authorization_loss_after_workload_failure_retains_staging(self):
        self.production_record(stop='control-protected-publication', cleanup_denied=True)
        self.assertEqual(v.verify(self.root)['failed_command'], 'control-protected-publication')
        self.assertFalse(h.read(self.root / 'assessment.json')['cleanup'])
        self.assertFalse((self.root / 'commands/control-unstage-command.json').exists())

    def test_request_rejects_collision_overlap_and_symlink_before_prompt(self):
        (self.root / 'build').mkdir()
        output = self.root / 'build/preview-cache-publication-correctness-20261118-04'
        with patch.object(qualify.e, 'ROOT', self.root):
            output.mkdir()
            with self.assertRaisesRegex(ValueError, 'collision'):
                qualify.validate_request(self.built, output)
            output.rmdir()
            with self.assertRaisesRegex(ValueError, 'overlaps'):
                qualify.validate_request(output / 'provider', output)
            output.symlink_to(self.root / 'elsewhere')
            with self.assertRaisesRegex(ValueError, 'approved attempt'):
                qualify.validate_request(self.built, output)

    def test_staging_installer_loads_without_repository_on_import_path(self):
        # sudo runs stage.py directly; neither the repository nor scripts is on sys.path.
        paths = [p for p in sys.path if p and Path(p).resolve() not in
                 (c.e.ROOT, c.e.ROOT / 'scripts')]
        with patch.object(sys, 'path', paths), patch.dict(sys.modules):
            for name in list(sys.modules):
                if name == 'install_state' or name == 'scripts' or name.startswith('scripts.'):
                    del sys.modules[name]
            before = list(sys.path)
            installer = stage.load_installer()
            self.assertTrue(callable(installer.run))
            self.assertTrue(callable(installer.remove_tree))
            self.assertEqual(Path(sys.modules['install_state'].__file__).resolve(),
                             c.e.ROOT / 'scripts/install_state.py')
            self.assertEqual(sys.path, before)

    def test_staging_rejects_historical_and_escaped_destinations(self):
        with patch.object(stage.os, 'geteuid', return_value=0):
            for output in (c.e.ROOT / 'build/preview-cache-publication-correctness-20261118-02',
                           c.e.ROOT / 'build/preview-cache-publication-correctness-20261118-03',
                           self.root / 'preview-cache-publication-correctness-20261118-04'):
                with self.assertRaisesRegex(ValueError, 'unsafe staging'):
                    stage.worker(output, 'control')

    def test_desktop_identity_rejected_before_authentication(self):
        with patch.object(qualify.os, 'getuid', return_value=0), \
             patch.object(qualify.subprocess, 'run') as prompt:
            with self.assertRaisesRegex(ValueError, 'desktop user'):
                qualify.qualify(self.built, c.e.ROOT / 'build/preview-cache-publication-correctness-20261118-04', True)
        prompt.assert_not_called()

    def test_authentication_interruption_creates_no_attempt(self):
        output = self.root / 'interrupted'
        with patch.object(qualify, 'validate_request'), \
             patch.object(qualify.sys.stdin, 'isatty', return_value=True), \
             patch.object(qualify.os, 'tcgetpgrp', return_value=os.getpgrp()), \
             patch.object(qualify.subprocess, 'run', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                qualify.qualify(self.built, output, authenticate=True)
        self.assertFalse(output.exists())

    def test_destination_rejected_before_authentication(self):
        with patch.object(qualify.subprocess, 'run') as prompt:
            with self.assertRaisesRegex(ValueError, 'approved attempt'):
                qualify.qualify(self.built, self.root / 'wrong', authenticate=True)
        prompt.assert_not_called()

    def test_authorization_denial_is_independently_verifiable(self):
        self.production_record(stop='authorization')
        proof = v.verify(self.root)
        self.assertEqual(proof['failed_command'], 'authorization')
        self.assertFalse((self.root / 'fixtures').exists())
        self.assertIn('authorization denied', (self.root / 'commands/authorization.stderr').read_text())

    def test_authorization_loss_prevents_protected_work(self):
        self.production_record(stop='control-stage-authorization')
        self.assertEqual(v.verify(self.root)['failed_command'], 'control-stage-authorization')
        self.assertFalse((self.root / 'commands/control-stage-command.json').exists())

    def test_authorization_loss_prevents_cleanup(self):
        self.production_record(stop='control-unstage-authorization')
        self.assertEqual(v.verify(self.root)['failed_command'], 'control-unstage-authorization')
        self.assertFalse((self.root / 'commands/control-unstage-command.json').exists())
        self.assertFalse(h.read(self.root / 'assessment.json')['cleanup'])
        self.assertIn('retained', h.read(self.root / 'assessment.json')['cleanup_failure'])

    def test_privileged_launch_retains_session_and_separates_group(self):
        row = self.schedule()[0]
        class Process:
            pid = 123456789
            def wait(self, timeout):
                return 0
        with patch.object(qualify.subprocess, 'Popen', return_value=Process()) as launch, \
             patch.object(qualify.e, 'load', return_value=SimpleNamespace(terminate=lambda *a, **k: None)), \
             patch.object(qualify.os, 'killpg', side_effect=ProcessLookupError):
            qualify.invoke(row, self.root)
        self.assertEqual(launch.call_args.kwargs['process_group'], 0)
        self.assertNotIn('start_new_session', launch.call_args.kwargs)
        row['launch'] = dict(start_new_session=True)
        h.write(self.root / 'schedule.json', [row, *self.schedule()[1:]])
        with self.assertRaisesRegex(ValueError, 'launch policy'):
            v.verify_schedule(self.root, self.built, c.protocol())

    def test_offline_verifier_imports_neither_qualifier_nor_build_implementation(self):
        import ast
        tree = ast.parse((DIRECTORY / 'offline/verify_correctness_v4.py').read_text())
        imports = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertNotIn('qualify', imports)
        self.assertNotIn('run', imports)
        self.assertNotIn('correctness', imports)


if __name__ == '__main__':
    unittest.main()
