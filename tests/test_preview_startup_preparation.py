"""Source-only overlay contract; never execute a compiler or measured program."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('prepare_startup', ROOT / 'scripts/prepare-preview-startup-tracing.py')
p = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p)


class PreparationTests(unittest.TestCase):
    def test_unique_anchor_refuses_missing_or_duplicate(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'source.cpp'
            for text in ('missing', 'anchor anchor'):
                path.write_text(text)
                with self.assertRaises(RuntimeError):
                    p.replace(path, 'anchor', 'trace')
                self.assertEqual(path.read_text(), text)

    def test_lambda_context_is_captured_at_scheduling_and_sync_callback_uses_execution_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'source.cpp'
            path.write_text('[this, job = std::move(job)] { executeJob(job); };\n'
                            '[this, index] { transactionStarted(index); };')
            p.capture(path, '[this, job = std::move(job)] {')
            text = path.read_text()
            self.assertIn('job = std::move(job), trace_context = StandbyTrace::current', text)
            self.assertIn('StandbyTrace::Bind trace_bind(trace_context);', text)
            self.assertIn('[this, index] { transactionStarted(index); }', text)

    def test_preparation_verifies_inputs_preserves_d_and_never_executes_subprocess(self):
        retained = ROOT / 'build/preview-standby-drbq1ofy'
        if not retained.exists():
            self.skipTest('retained private sources are unavailable')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            frozen = root / 'frozen'
            for label in 'ABCD':
                original = retained / 'diagnostic' / label
                base = frozen / 'diagnostic' / label
                base.mkdir(parents=True)
                for name in ('source', 'harness-source'):
                    shutil.copytree(original / name, base / name)
                shutil.copyfile(original / 'source-inventory.json', base / 'source-inventory.json')
            before = p.inventory(frozen)
            with patch.object(subprocess, 'Popen', side_effect=AssertionError('no subprocess allowed')):
                manifest = p.prepare(frozen, root / 'prepared', {'argv': ['synthetic']})
            self.assertEqual(before, p.inventory(frozen))
            self.assertEqual(manifest['before'], manifest['after'])
            self.assertIn('UNCOMPILED', manifest['status'])
            for label in 'ABCD':
                base = root / 'prepared' / label
                changed = [name for name, value in p.inventory(base / 'source').items()
                           if value != before[f'diagnostic/{label}/source/{name}']]
                self.assertTrue(changed)
                self.assertTrue(all(name.endswith('.cpp') and '/src/' in name for name in changed))
                service = (base / 'source/holonight-file-browser/src/preview/preview_service.cpp').read_text()
                self.assertIn('trace_context = StandbyTrace::current', service)
                self.assertIn('const auto publish = [this](const PreviewResult& result)', service)
                self.assertLess(service.index('if (!pending_job_ || stopping_)'),
                                service.index('demand_context.job = StandbyTrace::identity()'))
                self.assertIn('StandbyTrace::Bind lifetime_bind(StandbyTrace::lifetime(this));', service)
                self.assertNotIn('thread_identity', service)
                harness = (base / 'harness-source/reuse.cpp').read_text()
                self.assertLess(harness.index('"startup_origin"'), harness.index('    clock.start();', harness.index('"startup_origin"')))
                self.assertIn('"construction_outer", "begin"', harness)
                self.assertIn('"construction_complete", "point"', harness)
                self.assertTrue((base / 'overlay.diff').read_text())
            pool = (root / 'prepared/D/source/holonight-file-browser/src/preview/session_pool.cpp').read_text()
            self.assertIn('if (initial_window) { initial_active = true; return; }', pool)
            self.assertIn('setTransactionStartedCallback([this, index] { transactionStarted(index); });', pool)
            self.assertIn('preparation_context.job = trace_standby ? StandbyTrace::current.job : 0;', pool)
            self.assertIn('preparation_context.preparation = StandbyTrace::identity();', pool)
            self.assertIn('job_context.preparation = workers.at(index).trace_preparation;', pool)
            self.assertLess(pool.index('if (stopping || !pending)'), pool.index('StandbyTrace::Bind demand_bind'))
            self.assertIn('trace_standby ? "standby" : "demand"', pool)
            with self.assertRaises(FileExistsError):
                p.prepare(frozen, root / 'prepared', {})
            harness = frozen / 'diagnostic/A/harness-source/reuse.cpp'
            saved = harness.read_text()
            harness.write_text(saved + '\n// unreviewed\n')
            with self.assertRaisesRegex(ValueError, 'unreviewed frozen input'):
                p.prepare(frozen, root / 'unreviewed', {})
            self.assertFalse((root / 'unreviewed').exists())
            harness.write_text(saved)
            target = frozen / 'diagnostic/A/source/holonight-file-browser/src/preview/preview_service.cpp'
            target.write_text(target.read_text() + '\n// changed\n')
            with self.assertRaises(ValueError):
                p.prepare(frozen, root / 'rejected', {})
            self.assertFalse((root / 'rejected').exists())


if __name__ == '__main__':
    unittest.main()
