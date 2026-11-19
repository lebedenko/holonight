"""Frozen diagnostic persistence and independent reconstruction; real processes forbidden."""
import ast
from pathlib import Path
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zlib

sys.dont_write_bytecode = True
DIRECTORY = Path(__file__).resolve().parents[1] / 'tooling/preview-cache-publication'
sys.path.insert(0, str(DIRECTORY))
import execute as d

h, e, v = d.h, d.e, d.v


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(subprocess, 'Popen', side_effect=AssertionError('real process forbidden')))
        self.temporary = tempfile.TemporaryDirectory(dir=e.ROOT / 'build')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'attempt'
        self.built = e.ROOT / 'build/preview-cache-publication-native-20261117-01'
        self.correctness = e.ROOT / 'build/preview-cache-publication-correctness-20261118-04'

    def seal(self):
        values = h.inventory(self.root)
        values.pop('seal.json', None)
        h.write(self.root / 'seal.json', values)

    def schedule(self):
        self.root.mkdir(exist_ok=True)
        rows = d.schedule(self.built, self.root)
        h.write(self.root / 'schedule.json', rows)
        return rows

    def test_frozen_schedule_is_independently_reconstructed(self):
        rows = self.schedule()
        self.assertEqual(len(rows), 27)
        self.assertEqual(v.verify_schedule(self.root, self.built), rows)
        observations = [r for r in rows if r['workload']]
        self.assertEqual([r['observation'] for r in observations], e.historical.protocol()['schedule'])
        self.assertTrue(all(r['timeout_seconds'] == 30 and not r['privileged'] for r in observations))
        self.assertEqual(len({r['environment']['HOLONIGHT_CACHE_INVOCATION'] for r in observations}), 12)

    def test_privilege_timeout_order_and_launch_tampering_are_rejected(self):
        for kind in ('privilege', 'launch', 'order', 'timeout', 'invocation'):
            rows = self.schedule()
            workload = next(r for r in rows if r['workload'])
            if kind == 'privilege':
                workload.update(privileged=True, uid=0)
            elif kind == 'launch':
                workload['launch'] = dict(process_group=0)
            elif kind == 'order':
                rows[-6], rows[-5] = rows[-5], rows[-6]
            elif kind == 'timeout':
                workload['timeout_seconds'] = 600
            else:
                workloads = [r for r in rows if r['workload']]
                workloads[1]['environment']['HOLONIGHT_CACHE_INVOCATION'] = workload['environment']['HOLONIGHT_CACHE_INVOCATION']
            h.write(self.root / 'schedule.json', rows)
            with self.assertRaises(ValueError):
                v.verify_schedule(self.root, self.built)

    def test_source_overlay_preserves_frozen_workload(self):
        self.root.mkdir()
        d.prepare_sources(self.root)
        v.source_contract(self.root)
        source = self.root / 'native-source/control/main.cpp'
        source.write_text(source.read_text().replace('QThread::usleep(100)', 'QThread::usleep(200)'))
        with self.assertRaisesRegex(ValueError, 'workload changed'):
            v.source_contract(self.root)

    def test_blocked_correctness_cannot_authorize_execution(self):
        with self.assertRaisesRegex(ValueError, 'seal mismatch'):
            v.prerequisite(self.built, e.ROOT / 'build/preview-cache-publication-correctness-20261118-03')

    def test_missing_prerequisite_creates_no_attempt_or_authentication(self):
        with patch.object(d, 'validate_request'), patch.object(v, 'prerequisite', side_effect=ValueError('not qualified')), \
             patch.object(subprocess, 'run') as authenticate:
            with self.assertRaisesRegex(ValueError, 'not qualified'):
                d.execute(self.built, self.correctness, self.root, True)
        self.assertFalse(self.root.exists())
        authenticate.assert_not_called()

    def test_cancelled_authentication_creates_no_attempt(self):
        with patch.object(d, 'validate_request'), patch.object(v, 'prerequisite', return_value={}), \
             patch.object(sys.stdin, 'isatty', return_value=True), \
             patch.object(d.os, 'tcgetpgrp', return_value=os.getpgrp()), \
             patch.object(subprocess, 'run', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                d.execute(self.built, self.correctness, self.root, True)
        self.assertFalse(self.root.exists())

    def png(self, path, source, identity):
        def chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
        data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 256, 192, 8, 2, 0, 0, 0))
        for key, value in {'Thumb::URI': source.as_uri(), 'Thumb::MTime': identity.split(':')[3],
                           'Files::Revision': identity}.items():
            data += chunk(b'tEXt', (key + '\0' + value).encode())
        data += chunk(b'IDAT', zlib.compress((b'\0' + b'\0' * 256 * 3) * 192)) + chunk(b'IEND', b'')
        path.write_bytes(data)

    def produce(self, stop=None, mutation=None, supports=True, cleanup_failure=False, timeout=False):
        binding = dict(built=dict(path=str(self.built), seal=v.BUILT_SEAL, inventory={}),
            correctness=dict(path=str(self.correctness), seal=v.CORRECTNESS_SEAL, proof_sha256='synthetic'),
            package={}, fixture=dict(path=str(e.PACKAGE / '3200x2400.png'), sha256=v.protocol()['fixture_sha256']))
        self.enterContext(patch.object(v, 'prerequisite', return_value=binding))
        self.enterContext(patch.object(d, 'validate_request'))
        staged = set()
        original_lexists = os.path.lexists
        self.enterContext(patch.object(os.path, 'lexists', side_effect=lambda p: str(p) in staged or original_lexists(p)))
        clean = dict(isolated=True, exit=0, stdout='', stderr='', cgroups=[])
        def scopes(env, deadline):
            if cleanup_failure and (self.root / 'commands/observation-00-command.json').exists():
                return dict(clean, isolated=False, cgroups=['retained-synthetic-scope'])
            return clean
        self.enterContext(patch.object(d.qualify, 'scopes', side_effect=scopes))
        load = e.load
        self.enterContext(patch.object(e, 'load', side_effect=lambda name, path:
            SimpleNamespace(terminate=lambda *a, **k: None) if name == 'observation_cleanup' else load(name, path)))
        self.enterContext(patch.object(d.os, 'killpg', side_effect=ProcessLookupError))
        def launch(argv, **kwargs):
            name = Path(kwargs['stdout'].name).name.removesuffix('.stdout')
            row = h.read(self.root / 'commands' / (name + '-command.json'))
            fail = row['name'] in (stop or set())
            if not fail:
                self.artifacts(row, kwargs, staged, mutation, supports)
            else:
                kwargs['stderr'].write('synthetic command denial\n')
            class Process:
                pid = 123456789
                def wait(self, timeout):
                    self_timeout = 30 if row['workload'] else 600
                    assert timeout == self_timeout
                    if timed_out and row['workload']:
                        raise subprocess.TimeoutExpired(argv, timeout)
                    return 1 if fail else 0
            self.assertEqual(kwargs['env'], row['environment'])
            self.assertEqual({k: kwargs[k] for k in row['launch']}, row['launch'])
            return Process()
        timed_out = timeout
        with patch.object(subprocess, 'Popen', side_effect=launch):
            result = d.execute(self.built, self.correctness, self.root)
        return result

    def artifacts(self, row, kwargs, staged, mutation, supports):
        arm, name = row['arm'], row['name']
        if name.endswith('-configure'):
            base = self.root / arm / 'build'
            base.mkdir(parents=True)
            (base / 'CMakeCache.txt').write_text(''.join(k + '_DIR:PATH=' + str(self.built / arm / 'prefix/lib/cmake' / k) + '\n'
                for k in ('HolonightImages', 'HolonightThumbnails', 'HolonightFileBrowser')))
            (base / 'build.ninja').write_text('LINK_LIBRARIES = ' + ' '.join(str(self.built / arm / 'prefix/lib' / ('lib' + k + '.a')) for k in
                ('holonight_file_browser_preview', 'holonight_file_browser_core', 'holonight_thumbnails_isolated',
                 'holonight_images_isolated', 'holonight_images', 'holonight_thumbnails')) + '\n')
        elif name.endswith('-compile'):
            (self.root / arm / 'build/publication-observation').write_text('synthetic unexecutable artifact')
        elif name.endswith('-linkage'):
            kwargs['stdout'].write(str(Path(sys.executable).resolve()) + '\n')
        elif name.endswith('-stage'):
            runtime = v.protected_path(self.root, arm)
            staged.add(str(runtime))
            tree = {'generations/g/' + n: dict(uid=0, mode=0o644, sha256=sha)
                    for n, sha in h.inventory(self.built / arm / 'runtime').items()}
            h.write(self.root / (arm + '-staging.json'), dict(runtime=str(runtime), tree=tree,
                owner=dict(output=str(self.root), arm=arm, built=str(self.built), seal=v.BUILT_SEAL),
                generation='g', generation_identity=dict(device='10', inode='100')))
        elif name.endswith('-unstage'):
            staged.discard(str(v.protected_path(self.root, arm)))
            h.write(self.root / (arm + '-staging-cleanup.json'), dict(removed=True,
                owner=dict(output=str(self.root), arm=arm, built=str(self.built), seal=v.BUILT_SEAL)))
        elif row['workload']:
            base = self.root / name
            source = base / 'source/temporary/0.png'
            source.parent.mkdir(parents=True)
            shutil.copyfile(e.PACKAGE / '3200x2400.png', source)
            shutil.copyfile(source, base / 'source.png')
            info = source.stat()
            identity = ':'.join(str(v) for v in (info.st_dev, info.st_ino, info.st_size,
                info.st_mtime_ns // 10**9, info.st_mtime_ns % 10**9, info.st_ctime_ns // 10**9, info.st_ctime_ns % 10**9))
            self.png(base / 'cache.png', source, identity)
            lease = dict(target=str(v.protected_path(self.root, arm) / 'generations/g'), device='10', inode='100',
                         fdinfo='lock: 1: FLOCK ADVISORY READ 123 00:23:100 0 EOF\n')
            checks = dict(source_identity=identity, source_path=str(source), source_sha256=h.digest(source),
                cache_sha256=h.digest(base / 'cache.png'), cache_path=str(source.parent / 'cache/thumbnails/large/cache.png'),
                cache_available_at_final=True, cache_pixels_match=True, copied=True, check_ns='10',
                selected_generation='g', lease=lease)
            timing = [('eligible', 1), ('store_entry', 3), ('store_return', 8), ('enqueue', 9),
                      ('accepted', 9), ('adequate', 9), ('final', 10)] if arm == 'control' else [
                      ('eligible', 1), ('enqueue', 2), ('store_entry', 3), ('accepted', 4),
                      ('adequate', 5 if supports else 8), ('store_return', 8), ('final', 10)]
            common = dict(invocation=row['environment']['HOLONIGHT_CACHE_INVOCATION'], service='s', request='r',
                worker='w', preparation='p', transaction='1', source=identity, generation='1',
                width=256, height=256, original_decode=True, tier=256, outcome=0)
            events = [dict(common, event=k, ns=str(n)) for k, n in timing]
            if mutation == 'event' and name == 'observation-00':
                events[-1]['transaction'] = 'other'
            if mutation == 'cache' and name == 'observation-00':
                checks['cache_pixels_match'] = False
            if mutation == 'lease' and name == 'observation-00':
                checks['lease']['inode'] = '200'
            executable = (self.root / arm / 'build/publication-observation').resolve()
            mapped = str(Path(sys.executable).resolve())
            def mapping(path):
                info = Path(path).stat()
                return f'1-2 r-xp 0 {os.major(info.st_dev):x}:{os.minor(info.st_dev):x} {info.st_ino} {path}\n'
            data = dict(scenario='startup', fixture=str(self.root / 'fixture.png'), cleanup_failure=False,
                mapped_executable=str(executable), loaded_maps=mapping(executable) + mapping(mapped), samples=[dict(success=True, setup_success=True,
                    correct_pixels=True, correct_metadata=True, cleanup_failure=False, harness_timeout=False,
                    error='', superseded_selections=0, first_ms=1, final_ms=2, publication_checks=checks,
                    deliveries=[dict(event=k, selection=4, latency_ms=n) for k, n in [('pixels', 1), ('metadata', 2)]])])
            h.write(base / 'harness.json', data)
            kwargs['stderr'].write('\n'.join('CACHE_PUBLICATION ' + h.json.dumps(event) for event in events))

    def test_complete_supporting_record_uses_production_persistence(self):
        result = self.produce()
        self.assertEqual(result['status'], 'complete')
        proof = v.verify(self.root)
        self.assertEqual(proof['decision'], 'overlap observed')
        self.assertEqual((proof['observations'], proof['measured'], proof['supporting_early']), (12, 10, 5))
        self.assertTrue(proof['cleanup'])

    def test_valid_negative_population_is_sufficient(self):
        self.produce(supports=False)
        self.assertEqual(v.verify(self.root)['decision'], 'overlap not observed in this population')

    def test_authorization_denial_stops_before_any_workload(self):
        self.produce(stop={'authorization'})
        proof = v.verify(self.root)
        self.assertEqual(proof['failed_command'], 'authorization')
        self.assertEqual(proof['observations'], 0)

    def test_workload_failure_allows_only_owned_cleanup(self):
        self.produce(stop={'observation-02'})
        proof = v.verify(self.root)
        self.assertEqual(proof['observations'], 2)
        self.assertEqual(proof['decision'], 'Evidence insufficient')
        self.assertTrue(proof['cleanup'])
        self.assertFalse((self.root / 'commands/observation-03-command.json').exists())

    def test_expired_cleanup_authorization_retains_owned_staging(self):
        self.produce(stop={'observation-02', 'control-unstage-authorization'})
        proof = v.verify(self.root)
        self.assertFalse(proof['cleanup'])
        self.assertFalse((self.root / 'commands/control-unstage-command.json').exists())

    def test_malformed_events_block_even_when_process_exits_successfully(self):
        self.produce(mutation='event')
        self.assertEqual(v.verify(self.root)['failed_command'], 'observation-00')

    def test_unavailable_cache_at_final_blocks_diagnostic(self):
        self.produce(mutation='cache')
        self.assertEqual(v.verify(self.root)['failed_command'], 'observation-00')

    def test_missing_live_lease_blocks_diagnostic(self):
        self.produce(mutation='lease')
        self.assertEqual(v.verify(self.root)['failed_command'], 'observation-00')

    def test_scope_cleanup_failure_blocks_diagnostic(self):
        self.produce(cleanup_failure=True)
        proof = v.verify(self.root)
        self.assertFalse(proof['cleanup'])
        self.assertEqual(proof['decision'], 'Evidence insufficient')

    def test_resealed_false_decision_and_stopped_accounting_rejected(self):
        self.produce(stop={'observation-00'})
        assessment = h.read(self.root / 'assessment.json')
        assessment['decision'] = 'overlap observed'
        h.write(self.root / 'assessment.json', assessment)
        self.seal()
        with self.assertRaisesRegex(ValueError, 'false evidence decision'):
            v.verify(self.root)

    def test_resealed_unexpected_artifact_rejected(self):
        self.produce(stop={'authorization'})
        (self.root / 'surprise').write_text('unexpected')
        self.seal()
        with self.assertRaisesRegex(ValueError, 'artifact'):
            v.verify(self.root)

    def test_workload_timeout_stops_without_replacement(self):
        self.produce(timeout=True)
        proof = v.verify(self.root)
        self.assertEqual(proof['failed_command'], 'observation-00')
        self.assertEqual(proof['observations'], 0)
        self.assertFalse((self.root / 'commands/observation-01-command.json').exists())

    def test_event_parser_rejects_duplicate_keys_and_nonnumeric_timestamps(self):
        with self.assertRaisesRegex(ValueError, 'duplicate event field'):
            v.parse_events('CACHE_PUBLICATION {"event":"eligible","ns":"1","ns":"2"}')
        for stamp in ('-1', '1.0', '١', ''):
            with self.assertRaisesRegex(ValueError, 'nondecimal'):
                v.parse_events('CACHE_PUBLICATION ' + h.json.dumps(dict(event='eligible', ns=stamp)))

    def test_resealed_wrong_mapped_inode_is_rejected(self):
        self.produce()
        path = self.root / 'observation-00/harness.json'
        data = h.read(path)
        data['loaded_maps'] = data['loaded_maps'].replace(' r-xp 0 ', ' r-xp 0 ff:ff 0 ', 1)
        h.write(path, data)
        self.seal()
        with self.assertRaises((ValueError, IndexError)):
            v.verify(self.root)

    def test_destination_collision_overlap_and_escape_are_rejected(self):
        build = Path(self.temporary.name) / 'build'
        build.mkdir()
        output = build / d.OUTPUT_NAME
        with patch.object(e, 'ROOT', Path(self.temporary.name)):
            output.mkdir()
            with self.assertRaisesRegex(ValueError, 'collision'):
                d.validate_request(self.built, self.correctness, output)
            output.rmdir()
            with self.assertRaisesRegex(ValueError, 'overlapping'):
                d.validate_request(output / 'providers', self.correctness, output)
            output.symlink_to('/tmp/escaped-diagnostic')
            with self.assertRaisesRegex(ValueError, 'fresh diagnostic'):
                d.validate_request(self.built, self.correctness, output)

    def test_resealed_stopped_accounting_is_rejected(self):
        self.produce(stop={'observation-00'})
        assessment = h.read(self.root / 'assessment.json')
        assessment['unexecuted'].pop()
        h.write(self.root / 'assessment.json', assessment)
        self.seal()
        with self.assertRaisesRegex(ValueError, 'accounting'):
            v.verify(self.root)

    def test_verifier_imports_no_controller(self):
        tree = ast.parse((DIRECTORY / 'offline/verify_execution.py').read_text())
        imports = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        for name in ('execute', 'run', 'qualify', 'execution_stage'):
            self.assertNotIn(name, imports)


if __name__ == '__main__':
    unittest.main()
