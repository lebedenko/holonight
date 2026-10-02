# SPDX-License-Identifier: GPL-3.0-or-later
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import compilation
import workflow


class ToolingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='tooling paths with spaces ')
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.source = self.root / 'src/file.cpp'
        self.source.parent.mkdir()
        self.source.write_text('int main() {}')

    def database(self, directory, **extra):
        build = self.root / directory
        build.mkdir(parents=True)
        entry = dict(directory=str(build), file=str(self.source), arguments=['c++', '-c', str(self.source)], **extra)
        (build / 'compile_commands.json').write_text(json.dumps([entry]))
        return build

    def test_owned_test_precedes_debug_and_dependency(self):
        self.database('build/debug')
        self.database('build/deps/provider/test')
        self.database('build/test')
        entries, report = compilation.merge(self.root)
        self.assertEqual(len(entries), 1)
        self.assertEqual(report['origins'][str(self.source)], 'build/test/compile_commands.json')

    def test_invalid_and_stale(self):
        build = self.database('build/test')
        (build / 'compile_commands.json').write_text(json.dumps([{}, dict(directory='/missing', file='gone.cpp', command='c++')]))
        entries, report = compilation.merge(self.root)
        self.assertEqual(entries, [])
        self.assertEqual(report['invalid_entries'], 1)
        self.assertEqual(report['stale'], 1)

    def test_failed_refresh_preserves_database(self):
        previous = self.root / 'compile_commands.json'
        previous.write_text('[{"old": true}]')
        with patch.object(workflow, 'ROOT', self.root):
            with self.assertRaisesRegex(RuntimeError, 'preserved'):
                workflow.refresh({'cpp': True})
        self.assertEqual(previous.read_text(), '[{"old": true}]')

    def test_source_override_and_missing_source(self):
        checkout = self.root / 'provider checkout'
        checkout.mkdir()
        (checkout / 'CMakeLists.txt').write_text('project(test)')
        dep = {'module':'holonight-config', 'source_variable':'HOLONIGHT_CONFIG_SOURCE'}
        with patch.dict(os.environ, {'HOLONIGHT_CONFIG_SOURCE': str(checkout)}):
            self.assertEqual(workflow.dependency_source(dep), checkout)
        with patch.dict(os.environ, {'HOLONIGHT_CONFIG_SOURCE': str(self.root / 'absent')}):
            with self.assertRaisesRegex(RuntimeError, 'never downloaded'):
                workflow.dependency_source(dep)

    def test_explicit_prefix_does_not_build(self):
        location = self.root / 'prefix with spaces'
        package = location / 'lib/cmake/HoloNightConfig'
        package.mkdir(parents=True)
        (package / 'HoloNightConfigConfig.cmake').write_text('')
        config = {'dependencies':[{'module':'holonight-config', 'package':'HoloNightConfig','source_variable':'HOLONIGHT_CONFIG_SOURCE'}]}
        with patch.dict(os.environ, {'HOLONIGHT_DEPENDENCY_PREFIX':str(location)}), patch.object(workflow, 'run') as run:
            workflow.prepare(config)
            run.assert_not_called()
        with patch.dict(os.environ, {'HOLONIGHT_DEPENDENCY_PREFIX':str(self.root / 'missing')}):
            with self.assertRaisesRegex(RuntimeError, 'Missing HoloNightConfig'):
                workflow.prepare(config)

    def test_missing_qml_metadata(self):
        build = self.root / 'build/test'
        build.mkdir(parents=True)
        with patch.object(workflow, 'ROOT', self.root):
            with self.assertRaisesRegex(RuntimeError, 'No generated qmldir'):
                workflow.metadata({'qml_modules':['Example']}, 'test')
            (build / 'qmldir').write_text('module Example\ntypeinfo example.qmltypes\n')
            with self.assertRaisesRegex(RuntimeError, 'Missing or empty'):
                workflow.metadata({'qml_modules':['Example']}, 'test')

    def test_format_inventory_excludes_vendor_and_probes(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        for name in ['third_party/json.hpp', 'docs/probe.cpp', 'tooling/helper.cpp', 'include/public.h']:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('')
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        with patch.object(workflow, 'ROOT', self.root):
            self.assertEqual(set(workflow.owned_files({'.h', '.hpp', '.cpp'})),
                             {self.source, self.root / 'include/public.h'})

    def test_canonical_test_precedes_legacy_test(self):
        self.database('build-tests')
        self.database('build/test')
        _, report = compilation.merge(self.root)
        self.assertEqual(report['origins'][str(self.source)], 'build/test/compile_commands.json')

    def test_umbrella_owned_build_precedes_other_modules_dependency(self):
        owner = self.root / 'holonight-config'
        owner.mkdir()
        (owner / 'CMakeLists.txt').write_text('')
        self.source = owner / 'source.cpp'
        self.source.write_text('')
        self.database('holonight-consumer/build/deps/config/test')
        self.database('holonight-config/build/debug')
        _, report = compilation.merge(self.root)
        self.assertEqual(report['origins'][str(self.source)], 'holonight-config/build/debug/compile_commands.json')

    def test_drift_check_read_only(self):
        from sync import FILES
        module = self.root / 'standalone'
        (module / 'tooling').mkdir(parents=True)
        bundle = Path(__file__).resolve().parent
        for name in FILES:
            (module / 'tooling' / name).write_bytes((bundle / name).read_bytes())
        changed = module / 'tooling/VERSION'
        changed.write_text('drift\n')
        result = subprocess.run(['python3', str(bundle / 'sync.py'), '--check', '--module', str(module)], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(changed.read_text(), 'drift\n')


if __name__ == '__main__':
    unittest.main()
