from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


p = module('test_cpu_prepare', 'prepare-preview-cpu-profile.py')
r = module('test_cpu_runner', 'run-preview-cpu-profile.py')
a = module('test_cpu_report', 'report-preview-cpu-profile.py')
independent = module('test_cpu_independent', 'verify-preview-cpu-profile.py')


class CPUProfileTests(unittest.TestCase):
    def setUp(self):
        for method in ('Popen', 'run', 'check_output'):
            guard = patch('subprocess.' + method, side_effect=AssertionError('process launch forbidden'))
            guard.start(); self.addCleanup(guard.stop)
        self.index = {'libcrypto.so.4': {'sha256_block_data_order': [100]},
                      'libc.so.6': {'__memcpy_avx_unaligned': [50], '__write': [30]},
                      'libQt6Core.so.6': {'QIODevice::read(char*, long long)': [80]},
                      'preview-benchmark': {'ValidationTrace::Scope::event(char const*, char const*) const': [200]}}

    def frame(self, symbol='sha256_block_data_order+0x1', dso='/usr/lib/libcrypto.so.4'):
        return dict(symbol=symbol, dso=dso, ip='abcd', line=1)

    def test_mmap_identities_exclusions_and_conflicts(self):
        line = 'PERF_RECORD_MMAP2 1/1: [0x10(0x20) @ 0 <abcd>]: r-xp /usr/bin/python\n'
        with patch.object(Path, 'open', unittest.mock.mock_open(read_data=b'\x7fELF')):
            parsed = r.mapped_elfs(line + 'PERF_RECORD_MMAP2 1/1: [0x10(0x20) @ 0]: rw-p [heap]\n')
        self.assertEqual(parsed['files'], {'/usr/bin/python': 'abcd'})
        self.assertEqual(len(parsed['excluded']), 1)
        for bad in (line.replace('<abcd>', ''), line + line.replace('abcd', 'ffff'),
                    line.replace('/usr/bin/python', '/usr/../python')):
            with patch.object(Path, 'open', unittest.mock.mock_open(read_data=b'\x7fELF')):
                with self.assertRaises(ValueError):
                    r.mapped_elfs(bad)

    def test_raw_reader_normalizes_only_ephemeral_vdso_annotation(self):
        left = ' ...... dso: /tmp/perf-vdso.so-Ab1234\nMMAP /tmp/perf-vdso.so-Ab1234'
        right = left.replace('Ab1234', 'Cd5678', 1)
        self.assertEqual(independent.stable_raw_dump(left), independent.stable_raw_dump(right))
        self.assertNotEqual(independent.stable_raw_dump(left),
                            independent.stable_raw_dump(right.replace('MMAP', 'CHANGED')))

    def test_non_elf_mapping_is_hashed_without_build_identity(self):
        with tempfile.TemporaryDirectory() as name:
            data = Path(name) / 'locale'; data.write_bytes(b'data')
            elf = Path(name) / 'elf'; elf.write_bytes(b'\x7fELF')
            line = 'PERF_RECORD_MMAP2 1/1: [0x10(0x20) @ 0]: r--p '
            raw = line + str(data) + '\n' + line.replace('@ 0]', '@ 0 <abcd>]') + str(elf)
            result = r.mapped_elfs(raw)
            self.assertEqual(result['excluded'][0]['sha256'], r.o.digest(data))
            self.assertEqual(result['files'], {str(elf): 'abcd'})
            with self.assertRaisesRegex(ValueError, 'missing mapped build ID'):
                r.mapped_elfs(line + str(elf))

    def test_namespace_mismatch_precedes_runtime_access(self):
        with patch.object(r.os, 'getuid', return_value=1000), patch.object(r.os, 'geteuid', return_value=1000), \
             patch.object(Path, 'read_text', return_value='1000 0 1'), \
             patch.object(r.o.gate, 'protected_inventory') as inventory:
            with self.assertRaisesRegex(ValueError, 'namespace mismatch'):
                r.replay_environment()
            inventory.assert_not_called()

    def test_ordinary_copy_rejects_overwrite_symlink_and_changed_source(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); source = root / 'source'; source.write_bytes(b'frozen')
            link = root / 'link'; link.symlink_to(source)
            target = root / 'target'
            r.copy_ordinary(link, target)
            self.assertFalse(target.is_symlink())
            self.assertEqual(target.read_bytes(), b'frozen')
            with self.assertRaisesRegex(ValueError, 'collision'):
                r.copy_ordinary(source, target)
            with patch.object(r.o, 'digest', side_effect=['before', 'after']):
                with self.assertRaisesRegex(ValueError, 'changed'):
                    r.copy_ordinary(source, root / 'changed')
            directory = root / 'linked'; directory.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'linked destination'):
                r.copy_ordinary(source, directory / 'new')

    def test_namespace_helper_mirror_uses_frozen_binary_and_rejects_drift(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); package = root / 'package'; package.mkdir()
            source = root / 'native-helper'; source.write_bytes(b'\x7fELFfrozen-helper')
            identity = dict(path=str(source), sha256=r.o.digest(source), build_id='abcd')
            p.write(package / 'inputs.json', dict(binaries=dict(helper=identity)))
            mirror = root / 'symfs'; mirror.mkdir()
            with patch.object(r.p, 'build_id', return_value='abcd'):
                r.mirror_helper(package, mirror)
                target = mirror / 'usr/libexec/holonight-images-helper'
                self.assertFalse(target.is_symlink())
                self.assertEqual(target.read_bytes(), source.read_bytes())
                raw = 'PERF_RECORD_MMAP2 1/1: [0x10(0x20) @ 0 <abcd>]: r-xp /usr/libexec/holonight-images-helper'
                self.assertEqual(r.mapped_elfs(raw, mirror)['files'], {'/usr/libexec/holonight-images-helper': 'abcd'})
                source.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'helper identity drift'):
                    r.mirror_helper(package, root / 'other')
            source.write_bytes(b'\x7fELFfrozen-helper')
            with patch.object(r.p, 'build_id', return_value='ffff'):
                with self.assertRaisesRegex(ValueError, 'helper identity drift'):
                    r.mirror_helper(package, root / 'other')

    def test_complete_mirror_requires_matching_identity_and_preserves_frozen_file(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); mirror = root / 'symfs'; mirror.mkdir()
            source = root / 'host'; source.write_bytes(b'\x7fELF')
            evidence = root / 'evidence'; evidence.mkdir()
            raw = 'PERF_RECORD_MMAP2 1/1: [0x10(0x20) @ 0 <abcd>]: r-xp ' + str(source) + '\n'
            with patch.object(r.r, 'command', return_value=raw), patch.object(r, 'offline_env', return_value={}), \
                 patch.object(r.p, 'build_id', return_value='abcd'):
                rows = r.complete_mirror(root, mirror, evidence)
            self.assertFalse(rows[0]['frozen'])
            self.assertEqual((mirror / str(source).lstrip('/')).read_bytes(), b'\x7fELF')
            evidence2 = root / 'evidence2'; evidence2.mkdir()
            with patch.object(r.r, 'command', return_value=raw), patch.object(r, 'offline_env', return_value={}), \
                 patch.object(r.p, 'build_id', return_value='ffff'):
                with self.assertRaisesRegex(ValueError, 'build ID mismatch'):
                    r.complete_mirror(root, mirror, evidence2)
            self.assertEqual((mirror / str(source).lstrip('/')).read_bytes(), b'\x7fELF')

    def test_replay_source_failure_seals_without_launch_or_recording(self):
        with tempfile.TemporaryDirectory() as name:
            output = Path(name) / 'replay'
            source = Path(name) / 'source'
            (source / 'rehearsal-recording').mkdir(parents=True)
            (source / 'seal.json').write_text('{}')
            (source / 'rehearsal-recording/perf.data').write_bytes(b'fixture')
            with patch.object(r, 'preflight_confirmation', return_value={}), \
                 patch.object(r, 'replay_inputs', return_value=[]), \
                 patch.object(r, 'replay_environment', return_value={}), \
                 patch.object(r, 'offline_env', return_value={}), \
                 patch.object(r.o, 'fresh', side_effect=lambda path, *args: path.mkdir()), \
                 patch.object(r, 'workload', side_effect=AssertionError('workload forbidden')), \
                 patch.object(r, 'execute', side_effect=AssertionError('staging forbidden')), \
                 patch.object(r, 'symfs', side_effect=AssertionError('live preparation forbidden')), \
                 patch.object(r, 'module', return_value=independent), \
                 patch.object(r.o.gate, 'protected_inventory', side_effect=ValueError('source changed')):
                result = r.replay_confirmation(Path(name) / 'source', output)
            self.assertEqual(result['failure_stage'], 'source')
            self.assertEqual(result['recording_attempts'], 0)
            independent.seal(output)
            with self.assertRaisesRegex(ValueError, 'replay failed at source: source changed'):
                independent.verify_replay(output)

    def test_offline_replay_success_never_records_or_launches_workload(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); source = root / 'source'; output = root / 'replay'
            recording = source / 'rehearsal-recording'; recording.mkdir(parents=True)
            (source / 'symfs').mkdir()
            for file in ('perf.data', 'gate.json', 'release.json', 'recorder-ack.json', 'partial.json',
                         'recorder-shutdown.json', 'record-command.json', 'recorder.stderr'):
                (recording / file).write_text('{}')
            for suffix in ('.stdout', '.process.json'):
                (source / ('rehearsal' + suffix)).write_text('{}')
            (source / 'seal.json').write_text('{}')
            def reader(command, directory, label, **kwargs):
                (directory / (label + '.stdout')).write_text('fixture export')
            with patch.object(r, 'preflight_confirmation', return_value={}), \
                 patch.object(r, 'replay_inputs', return_value=[]), \
                 patch.object(r.o, 'fresh', side_effect=lambda path, *args: path.mkdir()), \
                 patch.object(r.o.gate, 'protected_inventory', return_value={}), \
                 patch.object(independent, 'verify_confirmation', return_value={}), \
                 patch.object(independent, 'confirmation_stacks', return_value={}), \
                 patch.object(r, 'complete_mirror', side_effect=lambda rec, mirror, evidence: p.write(evidence / 'mirror-sources.json', [])), \
                 patch.object(r, 'offline_env', return_value={}), \
                 patch.object(r.r, 'command', side_effect=reader), \
                 patch.object(a, 'rehearsal') as rehearsal, \
                 patch.object(r, 'module', side_effect=lambda name, file: a if 'reporter' in name else independent), \
                 patch.object(r, 'workload', side_effect=AssertionError('workload forbidden')), \
                 patch.object(r, 'execute', side_effect=AssertionError('harness forbidden')), \
                 patch.object(r, 'record_argv', side_effect=AssertionError('recording forbidden')):
                result = r.replay_confirmation(source, output)
            self.assertEqual(result['status'], 'complete')
            rehearsal.assert_called_once()
            independent.seal(output)
            self.assertEqual(p.read(output / 'preserved-before.json'), p.read(output / 'preserved-after.json'))

    def test_independent_marker_intervals_require_all_three_stacks(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); directory = root / 'rehearsal-recording'; directory.mkdir()
            p.write(directory / 'partial.json', dict(stop_ns=30))
            p.write(directory / 'gate.json', dict(pid=1)); p.write(directory / 'release.json', dict(ns=0))
            p.write(directory / 'export.command.json', dict(exit=0, argv=['perf', 'script', '--ns', '--show-task-events', '--show-lost-events',
                    '--no-inline', '--symfs', str(root / 'symfs'), '-F',
                    'comm,pid,tid,time,period,event,ip,sym,symoff,dso', '-i', str(directory / 'perf.data')]))
            (directory / 'header.stdout').write_text('clockid: 1\n')
            p.write(root / 'seal.json', {})
            markers = [dict(pid=pid, tid=tid, **{field: ns}) for pid, tid in ((1, 1), (1, 2), (3, 3))
                       for field, ns in (('start_ns', 10), ('stop_ns', 20))]
            (root / 'rehearsal.stdout').write_text('\n'.join(json.dumps(m) for m in markers))
            blocks = ['x %s/%s 0.000000015: 1 cpu-clock:u: ab fn (/elf)\n ab fn (/elf)\n cd caller (/elf)\n\n' % key
                      for key in ((1, 1), (1, 2), (3, 3))]
            with patch.object(independent, 'validate_capture'):
                (directory / 'export.stdout').write_text(''.join(blocks))
                self.assertEqual(len(independent.confirmation_stacks(root, root)['tasks']), 3)
                for bad in (''.join(blocks[:2]), ''.join(blocks).replace('000000015', '000000020'),
                            ''.join(blocks) + 'PERF_RECORD_LOST', ''.join(blocks) + 'PERF_RECORD_THROTTLE'):
                    (directory / 'export.stdout').write_text(bad)
                    with self.assertRaises(ValueError):
                        independent.confirmation_stacks(root, root)

    def test_confirmation_failure_stages_preserve_workload_error(self):
        for failing in ('recording', 'mirror', 'export', 'rehearsal'):
            with self.subTest(stage=failing), tempfile.TemporaryDirectory() as name:
                root = Path(name); output = root / 'confirmation'
                def fresh(path, *args): path.mkdir()
                def workload(argv, target, profiled):
                    directory = target.parent / 'rehearsal-recording'; directory.mkdir()
                    p.write(directory / 'partial.json', dict(first_failure={'message': 'recording failed'}
                            if failing == 'recording' else None))
                    if failing == 'recording': raise ValueError('recording failed')
                def complete(*args):
                    if failing == 'mirror': raise ValueError('mirror failed')
                def export(*args):
                    if failing == 'export': raise ValueError('export failed')
                    return ''
                class Verifier:
                    def verify_diagnostic(self, path): pass
                class Reporter:
                    def rehearsal(self, *args): raise ValueError('rehearsal failed')
                def module(name, filename): return Verifier() if 'verifier' in name else Reporter()
                with patch.object(r.o, 'fresh', side_effect=fresh), patch.object(r.o, 'check_output'), \
                     patch.object(r.o, 'digest', return_value='identity'), \
                     patch.object(r.o.gate, 'protected_inventory', return_value={}), \
                     patch.object(r, 'module', side_effect=module), patch.object(r, 'diagnostic_context', return_value={}), \
                     patch.object(r, 'symfs', return_value=root), patch.object(r, 'workload', side_effect=workload), \
                     patch.object(r, 'complete_mirror', side_effect=complete), patch.object(r, 'export', side_effect=export):
                    result = r.confirm(output, root)
                self.assertEqual(result['failure_stage'], failing)
                self.assertEqual(result['workload_failure'], {'message': 'recording failed'} if failing == 'recording' else None)

    def test_legacy_blocked_error_must_be_reproduced(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); directory = root / 'rehearsal-recording'; directory.mkdir()
            p.write(root / 'assessment.json', dict(status='blocked', attempts=1, launched_invocations=0,
                    unexecuted_invocations=10, failure='inheritance/timestamp/stack rehearsal failed'))
            p.write(root / 'preregistration.json', dict(synthetic_only=True, traced=False, retries=0,
                    diagnostic=str(root), diagnostic_seal='identity'))
            for file in ('preserved-before.json', 'preserved-after.json', 'symbol-mirror.json'):
                p.write(root / file, {})
            p.write(directory / 'partial.json', dict(first_failure=None))
            p.write(directory / 'export.command.json', dict(exit=0))
            with patch.object(independent, 'seal'), patch.object(independent, 'verify_diagnostic'), \
                 patch.object(independent, 'digest', return_value='identity'), \
                 patch.object(independent, 'validate_capture'), patch.object(independent, 'confirmation_stacks') as stacks:
                with self.assertRaisesRegex(ValueError, 'not reproduced'):
                    independent.verify_confirmation(root)
                stacks.side_effect = ValueError('inherited stack samples missing')
                self.assertTrue(independent.verify_confirmation(root)['failure_reproduced'])
                stacks.side_effect = ValueError('capture loss')
                with self.assertRaisesRegex(ValueError, 'mismatch'):
                    independent.verify_confirmation(root)

    def test_verifier_cli_writes_exclusive_structured_failure(self):
        import runpy
        with tempfile.TemporaryDirectory() as name:
            output = Path(name) / 'failure.json'
            argv = ['verify-preview-cpu-profile.py', '--replay', str(Path(name) / 'missing'), '--output', str(output)]
            with patch('sys.argv', argv), patch('builtins.print'):
                with self.assertRaises(SystemExit) as caught:
                    runpy.run_path(str(ROOT / 'scripts/verify-preview-cpu-profile.py'), run_name='__main__')
            self.assertEqual(caught.exception.code, 1)
            result = p.read(output)
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['error']['type'], 'FileNotFoundError')
            before = output.read_bytes()
            with patch('sys.argv', argv):
                with self.assertRaises(FileExistsError):
                    runpy.run_path(str(ROOT / 'scripts/verify-preview-cpu-profile.py'), run_name='__main__')
            self.assertEqual(output.read_bytes(), before)

    def test_acknowledgement_retains_partial_bytes_and_recorder_exit(self):
        class Recorder:
            def __init__(self): self.codes = iter([None, None, 1])
            def poll(self): return next(self.codes)
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            chunks = iter([b'a', b'ck'])
            with self.assertRaisesRegex(ValueError, 'exited'):
                r.acknowledge(3, Recorder(), root, 5, now=lambda: 1,
                              readable=lambda *args: ([3], [], []), receive=lambda *args: next(chunks))
            self.assertEqual(p.read(root / 'recorder-ack.json')['hex'], b'ack'.hex())

    def test_fragmented_acknowledgement_is_accepted(self):
        class Recorder:
            def poll(self): return None
        with tempfile.TemporaryDirectory() as name:
            chunks = iter([b'a', b'ck\n\0'])
            r.acknowledge(3, Recorder(), Path(name), 5, now=lambda: 1,
                          readable=lambda *args: ([3], [], []), receive=lambda *args: next(chunks))
            self.assertEqual(p.read(Path(name) / 'recorder-ack.json')['hex'], '61636b0a00')

    def test_cleanup_attempts_both_groups_and_all_descriptors_after_failure(self):
        class Child:
            def poll(self): return 1
        closed = []
        with patch.object(r, 'terminate', side_effect=OSError(1, 'gate cleanup denied')) as gate, \
             patch.object(r, 'stop_recorder', return_value={'reaped': True}) as recorder, \
             patch.object(r.os, 'close', side_effect=lambda fd: closed.append(fd)):
            result = r.cleanup_all(Child(), Child(), (3, None, 4), 35)
        self.assertFalse(result['passed'])
        self.assertIn('gate cleanup denied', result['gate']['error'])
        self.assertTrue(result['recorder']['reaped'])
        self.assertEqual(closed, [3, 4])
        self.assertEqual(gate.call_args.kwargs['deadline'], 35)
        self.assertEqual(recorder.call_args.args[1], 35)

    def test_failed_attachment_preserves_errno_stderr_and_never_releases_gate(self):
        class Child:
            pid = 123
            def poll(self): return None
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); target = root / 'case.json'
            error = OSError(13, 'event denied')
            original_read = Path.read_text
            def proc_read(path, *args, **kwargs):
                return 'stat' if str(path).startswith('/proc/') else original_read(path, *args, **kwargs)
            def fail(*args):
                (root / 'case-recording/recorder.stderr').write_text('perf_event_open: EACCES')
                raise error
            with patch.object(r.os, 'pipe', side_effect=[(10, 11), (12, 13), (14, 15), (16, 17)]), \
                 patch.object(r.os, 'close'), patch.object(r.os, 'write') as send, \
                 patch.object(r.subprocess, 'Popen', return_value=Child()), \
                 patch.object(r, 'offline_env', return_value={}), patch.object(r, 'wait_ready'), \
                 patch.object(r, 'identity', return_value={}), \
                 patch.object(r.Path, 'read_text', proc_read), \
                 patch.object(r, 'acknowledge', side_effect=fail), \
                 patch.object(r, 'cleanup_all', return_value={'passed': False}):
                # Avoid a real /proc PID dependency while retaining real evidence writes.
                with self.assertRaises(OSError) as caught:
                    r.workload(['synthetic'], target, True, recorder_identity=lambda pid: dict(pid=pid, scoped=True))
            self.assertIs(caught.exception, error)
            self.assertEqual(p.read(root / 'case-recording/recorder-identity.json'), dict(pid=123, scoped=True))
            self.assertEqual(p.read(root / 'case-recording/gate.json')['identity'], {})
            partial = json.loads((root / 'case-recording/partial.json').read_text())
            self.assertEqual(partial['first_failure']['errno'], 13)
            self.assertEqual(partial['first_failure']['recorder_stderr'], 'perf_event_open: EACCES')
            self.assertFalse(partial['released']); self.assertFalse(partial['acknowledged'])
            self.assertNotIn(b'G', [call.args[1] for call in send.call_args_list])
            p.o.seal(root); independent.seal(root)

    def test_diagnostic_cannot_stage_or_schedule_and_seals_partial_failure(self):
        with tempfile.TemporaryDirectory() as name:
            output = Path(name) / 'diagnostic'
            with patch.object(r.o, 'fresh', side_effect=lambda path, *args: path.mkdir()), \
                 patch.object(r.o, 'check_output', side_effect=ValueError('integrity failure')), \
                 patch.object(r, 'execute', side_effect=AssertionError('experiment forbidden')), \
                 patch.object(r, 'commands', side_effect=AssertionError('schedule forbidden')), \
                 patch.object(r, 'run_schedule', side_effect=AssertionError('schedule forbidden')), \
                 patch.object(r.r, 'command', side_effect=AssertionError('staging forbidden')):
                result = r.diagnose(output)
            self.assertEqual(result['launched_invocations'], 0)
            self.assertEqual(result['unexecuted_invocations'], 10)
            self.assertEqual(result['failure'], 'integrity failure')
            independent.seal(output)

    def test_complete_diagnostic_path_has_no_staging_or_harness_calls(self):
        launched = []
        with tempfile.TemporaryDirectory() as name:
            output = Path(name) / 'diagnostic'
            original_digest = r.o.digest
            def digest(path):
                return original_digest(path) if path.is_relative_to(output) else 'frozen-identity'
            def recording(target):
                directory = target.parent / (target.stem + '-recording'); directory.mkdir()
                launched.append(target.stem)
                p.write(directory / 'partial.json', {'cleanup_outcomes': {'passed': True}})
                (directory / 'syscalls.log').write_text('perf_event_open(cpu-clock) = 5\n')
            def attached(argv, target, profiled, recorder_command):
                self.assertEqual(argv[-1], 'synthetic')
                self.assertTrue(profiled)
                recording(target)
            with patch.object(r.o, 'fresh', side_effect=lambda path, *args: path.mkdir()), \
                 patch.object(r.o, 'check_output'), patch.object(r.o, 'digest', side_effect=digest), \
                 patch.object(r.o.gate, 'protected_inventory', return_value={}), \
                 patch.object(r, 'diagnostic_context', return_value={}), \
                 patch.object(r, 'diagnostic_launched', side_effect=lambda target, settings: recording(target)), \
                 patch.object(r, 'workload', side_effect=attached), \
                 patch.object(r, 'execute', side_effect=AssertionError('experiment forbidden')), \
                 patch.object(r, 'commands', side_effect=AssertionError('harness commands forbidden')), \
                 patch.object(r, 'run_schedule', side_effect=AssertionError('schedule forbidden')), \
                 patch.object(r.r, 'command', side_effect=AssertionError('staging forbidden')):
                result = r.diagnose(output)
            self.assertEqual(result['status'], 'diagnosed')
            self.assertEqual(len(launched), 4)
            self.assertEqual(result['launched_invocations'], 0)
            self.assertEqual(result['unexecuted_invocations'], 10)
            p.o.seal(output); independent.seal(output)

    def test_pipe_setup_failure_closes_already_created_descriptors(self):
        closed = []
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            with patch.object(r, 'offline_env', return_value={}), \
                 patch.object(r.os, 'pipe', side_effect=[(10, 11), OSError(24, 'descriptor limit')]), \
                 patch.object(r.os, 'close', side_effect=closed.append):
                with self.assertRaisesRegex(OSError, 'descriptor limit'):
                    r.workload(['synthetic'], root / 'case.json', True)
            self.assertEqual(closed, [10, 11])
            evidence = p.read(root / 'case-recording/partial.json')
            self.assertEqual(evidence['first_failure']['errno'], 24)
            self.assertTrue(evidence['cleanup_outcomes']['passed'])
            self.assertFalse(evidence['released'])

    def test_descriptor_failure_does_not_skip_remaining_descriptors(self):
        closed = []
        def close(fd):
            closed.append(fd)
            if fd == 3: raise OSError(9, 'bad descriptor')
        with patch.object(r.os, 'close', side_effect=close):
            evidence = r.cleanup_all(None, None, (3, 4), 35)
        self.assertEqual(closed, [3, 4])
        self.assertFalse(evidence['passed'])
        self.assertTrue(evidence['descriptors'][1]['closed'])

    def test_forced_recorder_cleanup_stops_diagnostics(self):
        class Child:
            def poll(self): return 1
        with patch.object(r, 'stop_recorder', return_value=dict(reaped=True, forced=True)):
            evidence = r.cleanup_all(None, Child(), (), 35)
        self.assertFalse(evidence['passed'])

    def test_diagnostic_commands_only_change_registered_comparison_options(self):
        for case in r.DIAGNOSTIC_CASES:
            attached = case['mode'] == 'attached'
            command = r.diagnostic_command(Path('perf.data'), 123 if attached else None,
                                           4, 7, settings=case['settings'])
            perf = command[command.index('perf'):]
            self.assertEqual(perf[:3], ['perf', 'record', '-vv'])
            self.assertEqual('--pid' in perf, attached)
            self.assertEqual('--control' in perf, attached)
            self.assertEqual('--delay' in perf, attached)
            self.assertNotIn('sudo', command)
            if case['settings'] == 'full':
                self.assertIn('dwarf,16384', command)
                self.assertIn('--strict-freq', command)

    def test_fixed_budget_and_alternating_schedule(self):
        rows = p.schedule()
        self.assertEqual(len(rows), 10)
        self.assertEqual([r['arm'] for r in rows[:2]], ['unprofiled', 'profiled'])
        self.assertEqual(sum(r['observations'] for r in rows if r['warmup']), 2)
        for arm in ('profiled', 'unprofiled'):
            self.assertEqual(sum(r['observations'] for r in rows if not r['warmup'] and r['arm'] == arm), 20)
        for block in range(4):
            self.assertEqual([r['arm'] for r in rows if r['block'] == block],
                             ['unprofiled', 'profiled'] if block % 2 == 0 else ['profiled', 'unprofiled'])

    def test_task_scoped_recording_preserves_inheritance(self):
        argv = r.record_argv(Path('perf.data'), 123, 4, 7)
        self.assertEqual(argv[argv.index('--pid')+1], '123')
        for forbidden in ('--all-cpus', '--no-inherit', 'sudo', 'sched:sched_switch'):
            self.assertNotIn(forbidden, argv)
        self.assertIn('cpu-clock:u', argv); self.assertIn('dwarf,16384', argv)
        self.assertIn('--strict-freq', argv)
        self.assertIn('--user-callchains', argv)

    def test_self_categories_are_exclusive_and_inclusive_logging_is_demonstrated(self):
        self.assertEqual(a.classify([self.frame()], self.index), a.CATEGORIES[0])
        copy = self.frame('__memcpy_avx_unaligned+0x10', '/usr/lib/libc.so.6')
        io = self.frame('QIODevice::read(char*, long long)+0x4', '/usr/lib/libQt6Core.so.6')
        logging = self.frame('ValidationTrace::Scope::event(char const*, char const*) const+0x1', 'preview-benchmark')
        write = self.frame('__write+0x2', '/usr/lib/libc.so.6')
        self.assertEqual(a.classify([copy, io], self.index), a.CATEGORIES[2])
        self.assertEqual(a.classify([io], self.index), a.CATEGORIES[1])
        self.assertEqual(a.classify([write], self.index), a.CATEGORIES[-1])
        self.assertEqual(a.classify([write, logging], self.index), a.CATEGORIES[3])

    def test_nearest_exported_symbol_and_unknown_leaf_remain_unresolved(self):
        self.assertIsNone(a.resolved(self.frame('sha256_block_data_order+0x64'), self.index))
        self.assertEqual(a.classify([self.frame('[unknown]'), self.frame()], self.index), a.CATEGORIES[-1])
        self.assertIsNone(a.resolved(self.frame(dso='foreign-lib.so'), self.index))

    def test_half_open_boundaries_pid_tid_and_separate_setup_ownership(self):
        samples = [dict(pid=1, tid=2, ns=ns, period=period, line=i, frames=[self.frame()], truncated=False)
                   for i, (ns, period) in enumerate(((9, 1), (10, 2), (19, 3), (20, 4)))]
        samples.append(dict(samples[1], tid=3))
        windows = [dict(pid=1, tid=2, start=9, stop=10, observation=None, setup=True),
                   dict(pid=1, tid=2, start=10, stop=20, observation=1, setup=False)]
        rows = a.attribute(samples, windows, self.index)
        self.assertEqual([r['sample_count'] for r in rows], [1, 2])
        self.assertEqual(rows[1]['recorded_period'], 5)
        self.assertIsNone(rows[0]['window']['observation'])
        self.assertEqual(rows, json.loads(json.dumps(rows)))

    def test_count_and_period_weighting_and_unavailable_zero_sample_windows(self):
        frames = [self.frame(), self.frame('[unknown]')]
        samples = [dict(pid=1, tid=1, ns=10+i, period=weight, line=i, frames=[frame], truncated=i == 1)
                   for i, (weight, frame) in enumerate(zip((1, 9), frames))]
        rows = a.attribute(samples, [dict(pid=1, tid=1, start=0, stop=20), dict(pid=1, tid=1, start=30, stop=40)], self.index)
        self.assertEqual(rows[0]['count_shares'][a.CATEGORIES[0]], .5)
        self.assertEqual(rows[0]['period_shares'][a.CATEGORIES[0]], .1)
        self.assertEqual(rows[0]['unresolved_frames'], 1)
        self.assertEqual(rows[0]['truncated_stacks'], 1)
        self.assertIsNone(rows[1]['count_shares']); self.assertIsNone(rows[1]['period_shares'])

    def test_quantiles_and_all_tail_cutoff_ties(self):
        rows = [dict(invocation=0, observation=i, value=min(i, 18)) for i in range(20)]
        self.assertEqual(a.distribution([r['value'] for r in rows]),
                         dict(count=20, minimum=0, median=9.5, p95=18, maximum=18))
        self.assertEqual([r['observation'] for r in a.tails(rows, 'value')], [18, 19])

    def test_parser_retains_addresses_tasks_periods_and_rejects_loss(self):
        text = ('x 12/13 1.000000001: PERF_RECORD_COMM exec: x:12/12\n'
                'x 12/13 1.000000002: 99 cpu-clock:u: abcd sha256_block_data_order+0x1 (/usr/lib/libcrypto.so.4)\n'
                '        abcd sha256_block_data_order+0x1 (/usr/lib/libcrypto.so.4)\n\n')
        parsed = a.parse(text)
        self.assertEqual(parsed['samples'][0]['ns'], 1000000002)
        self.assertEqual(parsed['samples'][0]['period'], 99)
        self.assertEqual(len(parsed['tasks']), 1)
        self.assertEqual(parsed['samples'][0]['frames'][0]['ip'], 'abcd')
        with self.assertRaisesRegex(ValueError, 'loss'):
            a.parse(text + 'PERF_RECORD_LOST 1\n')
        with self.assertRaisesRegex(ValueError, 'unparsed'):
            a.parse('corrupt export\n')

    def test_failed_accounting_stops_schedule_without_retry(self):
        entries = r.commands(Path('/tmp/output'), Path('/run/fresh'))
        result = dict(invocations=[], measured_observations=0, warmup_observations=0)
        launched = []
        def launch(i, entry): launched.append(i); return {}
        def account(i, entry, process): raise ValueError('sealed failure')
        with self.assertRaisesRegex(ValueError, 'sealed failure'):
            r.run_schedule(entries, result, lambda: None, launch, account, lambda: None)
        self.assertEqual(launched, [0])
        self.assertEqual(result['unexecuted_invocations'], 9)
        self.assertEqual(result['invocations'][0]['status'], 'failed')

    def test_gate_readiness_handles_eof_deadline_and_exact_protocol(self):
        class Process:
            def poll(self): return None
        r.wait_ready(3, Process(), 30, now=lambda: 1, readable=lambda *args: ([3], [], []), receive=lambda *args: b'ready\n')
        for data in (b'', b'wrong\n', b'ready\nextra'):
            with self.assertRaises(ValueError):
                r.wait_ready(3, Process(), 30, now=lambda: 1, readable=lambda *args: ([3], [], []), receive=lambda *args: data)
        with self.assertRaisesRegex(ValueError, 'timeout'):
            r.wait_ready(3, Process(), 1, now=lambda: 2)

    def test_recorder_shutdown_reaps_and_has_one_deadline(self):
        class Recorder:
            pid = 999
            def __init__(self): self.signals = []; self.code = None
            def poll(self): return self.code
            def send_signal(self, sig): self.signals.append(sig)
            def wait(self, timeout): self.code = 0; return 0
        recorder = Recorder()
        with patch.object(r.r.time, 'monotonic', side_effect=[0, 0, 1]):
            result = r.r.shutdown(recorder, ready=True)
        self.assertTrue(result['passed']); self.assertTrue(result['reaped'])
        self.assertEqual(len(recorder.signals), 1)

    def test_recorder_forced_cleanup_uses_remaining_shared_deadline(self):
        class Recorder:
            pid = 999
            def __init__(self): self.timeouts = []
            def poll(self): return None
            def send_signal(self, sig): self.signal = sig
            def wait(self, timeout):
                self.timeouts.append(timeout)
                if len(self.timeouts) == 1: raise subprocess.TimeoutExpired('perf', timeout)
                return -9
        recorder = Recorder(); killed = []
        ticks = iter([31, 34, 34.5])
        result = r.stop_recorder(recorder, 35, ready=True, now=lambda: next(ticks),
                                 kill_group=lambda *args: killed.append(args))
        self.assertEqual(recorder.timeouts, [3, 1])
        self.assertEqual(killed, [(999, 9)])
        self.assertTrue(result['forced']); self.assertTrue(result['reaped']); self.assertFalse(result['passed'])

    def test_missing_symbols_seals_failure_and_starts_no_workload(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'preparation'
            def fresh(path, *args): path.mkdir()
            with patch.object(p.o, 'fresh', side_effect=fresh), patch.object(p, 'frozen_inputs',
                    return_value={'dependencies': {}}), patch.dict(p.os.environ, {'DEBUGINFOD_URLS': ''}):
                result = p.prepare(target)
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(result['launched_invocations'], 0)
            p.o.check_output(target)

    def test_mismatched_debug_build_id_stops_before_using_symbols(self):
        with patch.object(p, 'build_id', side_effect=['aaaa', 'bbbb']):
            with self.assertRaisesRegex(ValueError, 'build ID mismatch'):
                p.validate_symbols(Path('binary'), Path('wrong.debug'))

    def test_sized_symbol_lookup_rejects_zero_size_and_cross_library_names(self):
        output = '0000 000a t sha256_block_data_order\n0010 0000 t unknown_extent\n'
        index = a.symbol_index({'libcrypto.so.4': {'path': 'private.debug'}}, run=lambda *args, **kwargs: output)
        self.assertEqual(a.resolved(self.frame('sha256_block_data_order+0x9'), index), 'sha256_block_data_order')
        self.assertIsNone(a.resolved(self.frame('sha256_block_data_order+0xa'), index))
        self.assertIsNone(a.resolved(self.frame('unknown_extent'), index))

    def test_unknown_or_depth_limited_stacks_are_retained(self):
        text = ('x 12/13 1.0: 1 cpu-clock:u: abcd [unknown] ([unknown])\n' +
                ' abcd [unknown] ([unknown])\n'*127 + '\n')
        capture = a.parse(text)
        self.assertTrue(capture['samples'][0]['truncated'])
        self.assertEqual(len(capture['samples'][0]['frames']), 127)
        result = a.attribute(capture['samples'], [dict(pid=12, tid=13, start=0, stop=2*10**9)], self.index)[0]
        self.assertEqual(result['counts']['other/unresolved'], 1)
        self.assertEqual(result['unresolved_frames'], 127)

    def test_setup_window_has_no_observation_and_overlapping_ownership_is_rejected(self):
        span = dict(operation='read_hash', start=10, stop=20, begin=dict(pid=1, tid=2, service=9))
        file = dict(path='usr/lib/libicudata.so.78', ordinal=7, operations=[span])
        setup = [dict(service=9, validation=dict(files=[file]))]
        rows = a.windows([], setup)
        self.assertIsNone(rows[0]['observation']); self.assertTrue(rows[0]['setup'])
        observation = dict(observation=1, validation=dict(files=[file]))
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            a.windows([observation], setup)

    def test_independent_seal_replay_detects_tampered_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'assessment.json').write_text('{"status":"blocked"}\n')
            p.o.seal(root)
            independent.seal(root)
            (root/'assessment.json').write_text('{"status":"complete"}\n')
            with self.assertRaisesRegex(ValueError, 'seal mismatch'):
                independent.seal(root)

    def test_independent_mapping_replay_rejects_identity_and_exclusion_tampering(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); mirror = root / 'symfs'; mirror.mkdir()
            recording = root / 'recording'; recording.mkdir()
            source = root / 'elf'; source.write_bytes(b'\x7fELFbody')
            data = root / 'locale'; data.write_bytes(b'data')
            raw = ('PERF_RECORD_MMAP2 1/1: [0x10(0x20) @ 0 <abcd>]: r-xp ' + str(source) + '\n' +
                   'PERF_RECORD_MMAP2 1/1: [0x40(0x20) @ 0]: r--p ' + str(data) + '\n')
            def reader(command, target, label, **kwargs):
                result = raw if label == 'mappings' else 'fixture'
                p.write(target / (label + '.command.json'), dict(argv=command, exit=0))
                (target / (label + '.stdout')).write_text(result)
                return result
            with patch.object(r.r, 'command', side_effect=reader), patch.object(r, 'offline_env', return_value={}), \
                 patch.object(r.p, 'build_id', return_value='abcd'):
                r.complete_mirror(recording, mirror, recording)
            perf = recording / 'perf.data'
            commands = {
                'header': ['perf', 'report', '--header-only', '--stdio', '-i', str(perf)],
                'export': ['perf', 'script', '--ns', '--show-task-events', '--show-lost-events', '--no-inline',
                           '--symfs', str(mirror), '-F', 'comm,pid,tid,time,period,event,ip,sym,symoff,dso', '-i', str(perf)]}
            for label, command in commands.items(): reader(command, recording, label)
            def reproduce(command, **kwargs):
                if command[0] == 'readelf': return 'Build ID: abcd'
                return raw if '-D' in command else 'fixture'
            with patch.object(independent.subprocess, 'check_output', side_effect=reproduce):
                independent.verify_recording_mirror(recording, mirror)
                inventory = p.read(recording / 'mapped-elfs.json')
                inventory['files'][str(source)] = 'ffff'
                p.write(recording / 'mapped-elfs.json', inventory)
                with self.assertRaisesRegex(ValueError, 'mapping inventory drift'):
                    independent.verify_recording_mirror(recording, mirror)
                inventory['files'][str(source)] = 'abcd'
                p.write(recording / 'mapped-elfs.json', inventory)
                data.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'mapping inventory drift'):
                    independent.verify_recording_mirror(recording, mirror)

    def test_actual_capture_settings_and_acknowledgement_tampering(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); directory = root / 'rehearsal-recording'; directory.mkdir()
            command = r.record_argv(directory / 'perf.data', 123, 4, 5)
            p.write(directory / 'record-command.json', command)
            p.write(directory / 'gate.json', dict(pid=123, uid=1000, identity=dict(pid=123)))
            p.write(directory / 'release.json', dict(pid=123, ns=20))
            p.write(directory / 'recorder-ack.json', dict(hex='61636b0a', ns=10))
            p.write(directory / 'partial.json', dict(acknowledged=True, released=True,
                cleanup_outcomes=dict(passed=True), cleanup=dict(passed=True), stop_ns=30,
                cleanup_deadline=1, first_failure=None))
            p.write(root / 'rehearsal.process.json', dict(exit=0, timeout=False, cleanup_verified=True))
            p.write(directory / 'recorder-shutdown.json', dict(passed=True))
            (directory / 'recorder.stderr').write_text('')
            independent.validate_capture(root)
            for option, value in (('--freq', '998'), ('--call-graph', 'fp'), ('--clockid', 'realtime')):
                changed = command.copy(); changed[changed.index(option)+1] = value
                p.write(directory / 'record-command.json', changed)
                with self.assertRaisesRegex(ValueError, 'settings drift'):
                    independent.validate_capture(root)
            p.write(directory / 'record-command.json', command + ['--no-inherit'])
            with self.assertRaisesRegex(ValueError, 'command drift'):
                independent.validate_capture(root)
            p.write(directory / 'record-command.json', command)
            p.write(directory / 'recorder-ack.json', dict(hex='61636b0a', ns=21))
            with self.assertRaisesRegex(ValueError, 'acknowledgement'):
                independent.validate_capture(root)

    def test_execution_preflight_namespace_and_destination_reject_without_writes(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); output = root / 'execution'
            with patch.object(r, 'replay_environment', side_effect=ValueError('host namespace mismatch')):
                with self.assertRaisesRegex(ValueError, 'namespace'):
                    r.preflight_execution(root, output)
            self.assertFalse(output.exists())
            output.mkdir()
            with patch.object(r, 'replay_environment', return_value={}), patch.object(r, 'offline_env', return_value={}):
                with self.assertRaisesRegex(ValueError, 'destination unavailable'):
                    r.preflight_execution(root, output)
            self.assertEqual(list(output.iterdir()), [])

    def test_complete_execution_fixture_mirrors_before_exports_and_reports(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); output = root / 'execution'; package = root / 'package'; package.mkdir()
            prepared = root / 'prepared'; prepared.mkdir()
            p.write(package / 'inputs.json', {})
            p.write(package / 'assessment.json', dict(status='prepared'))
            p.write(package / 'symbols.json', {})
            p.write(package / 'seal.json', {})
            p.write(prepared / 'provenance.json', dict(prepared=str(prepared)))
            installer_hashes = {str(r.r.INSTALLER / n): 'hash' for n in ('manage-images-generations.py', 'install_state.py')}
            p.write(prepared / 'input-integrity.json', dict(before=installer_hashes))
            context = dict(namespaces={}, runtime={})
            preflight = dict(context=context, historical_seals={}, recovery_final_sha256='hash')
            mirrored = []; exported = []
            def mirror(package, output):
                target = output / 'symfs'; target.mkdir(); return target
            def workload(argv, target, profiled):
                directory = target.parent / (target.stem + '-recording'); directory.mkdir()
                return dict(exit=0, timeout=False, cleanup_verified=True)
            def complete(recording, mirror, evidence): mirrored.append(recording)
            def export(target, mirror):
                recording = target.parent / (target.stem + '-recording')
                self.assertIn(recording, mirrored); exported.append(recording)
                return ''
            def invocation(entry, index, built, output):
                return ([dict(observation=n+1, validation=dict(duration_ns=50, files=[]),
                              endpoints={k: dict(harness_latency_ns=100+n) for k in ('pixels', 'metadata')})
                         for n in range(entry['invocation']['observations'])], [])
            def account(target, text, observations): p.write(target.with_suffix('.cpu.json'), dict(files=[]))
            guards = [patch.object(r, 'preflight_execution', return_value=preflight),
                 patch.object(r.o, 'fresh', side_effect=lambda path, *args: path.mkdir()),
                 patch.object(r.o, 'check_output'), patch.object(r.o, 'digest', return_value='hash'),
                 patch.object(r.p, 'frozen_inputs', return_value={}), patch.object(r.p, 'PACKAGE', prepared),
                 patch.object(r, 'symfs', side_effect=mirror), patch.object(r, 'offline_env', return_value={}),
                 patch.object(r.r, 'command'), patch.object(r.r, 'isolated'), patch.object(r.r, 'residuals'),
                 patch.object(r.o, 'staged', return_value={}), patch.object(r.o.gate, 'protected_inventory', return_value={}),
                 patch.object(r, 'replay_environment', return_value=context), patch.object(r, 'workload', side_effect=workload),
                 patch.object(r, 'complete_mirror', side_effect=complete), patch.object(r, 'export', side_effect=export),
                 patch.object(r.o, 'validate', side_effect=lambda target, invocation, *args: [None]*invocation['observations']),
                 patch.object(a, 'rehearsal'), patch.object(a.validation, 'invocation', side_effect=invocation),
                 patch.object(a, 'account', side_effect=account),
                 patch.object(r, 'module', side_effect=lambda name, file: a if file == 'report-preview-cpu-profile.py' else None)]
            with ExitStack() as stack:
                for guard in guards: stack.enter_context(guard)
                result = r.execute(package, output)
            self.assertEqual(result['status'], 'complete', result)
            self.assertEqual((result['launched_invocations'], result['measured_observations'], result['warmup_observations']), (10, 40, 2))
            self.assertEqual(len(exported), 6)
            report = root / 'report'
            with patch.object(a.o, 'fresh', side_effect=lambda path, *args: path.mkdir()):
                self.assertEqual(a.report(output, report)['status'], 'complete')
            replayed = [(row['index'], row['entry']['invocation'], obs) for row in result['invocations']
                        for obs in p.read(Path(row['entry']['argv'][-1]).with_suffix('.cpu-observations.json'))]
            independent.verify_report(report, result, replayed)

    def test_json_report_distributions_and_independent_tie_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); execution = root/'execution'; execution.mkdir()
            observations_dir = execution/'observations'; observations_dir.mkdir()
            invocations = []
            replayed = []
            for index, invocation in enumerate(p.schedule()):
                target = observations_dir/f'{index:03}.json'
                entry = dict(index=index, status='passed', entry=dict(invocation=invocation, argv=[str(target)]))
                invocations.append(entry)
                observations = [dict(observation=n+1, validation=dict(duration_ns=50_000_000, files=[]),
                    endpoints={name: dict(harness_latency_ns=(140+n)*1_000_000) for name in ('pixels', 'metadata')})
                    for n in range(invocation['observations'])]
                p.write(target.with_suffix('.cpu-observations.json'), observations)
                if invocation['arm'] == 'profiled':
                    p.write(target.with_suffix('.cpu.json'), dict(files=[]))
                replayed.extend((index, invocation, obs) for obs in observations)
            assessment = dict(status='complete', invocations=invocations)
            p.write(execution/'assessment.json', assessment); p.o.seal(execution)
            output = root/'report'
            with patch.object(a.o, 'fresh', side_effect=lambda path, *args: path.mkdir()):
                result = a.report(execution, output)
            self.assertEqual(result['status'], 'complete')
            independent.verify_report(output, assessment, replayed)
            summaries = p.read(output/'summary.json')
            profiled = next(s for s in summaries if s['arm']=='profiled' and s['block']=='pooled')
            self.assertEqual(profiled['timings']['validation_ns']['count'], 20)
            self.assertEqual(profiled['category_count_shares'][a.CATEGORIES[0]], {'count': 0})


if __name__ == '__main__':
    unittest.main()
