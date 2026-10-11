# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import external
import workflow


class ExternalDependencies(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dependency prefix with spaces ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = {'module': 'consumer', 'dependencies': [], 'external_dependencies':
                       [{'id': 'gtest', 'scope': ['test'], 'targets': ['GTest::gtest', 'GTest::gmock']}]}

    def installed_gtest(self, version='1.14.0', gmock=True):
        package = self.root / 'lib/cmake/GTest'
        package.mkdir(parents=True, exist_ok=True)
        config = 'add_library(GTest::gtest INTERFACE IMPORTED)\n'
        if gmock:
            config += 'add_library(GTest::gmock INTERFACE IMPORTED)\n'
        (package / 'GTestConfig.cmake').write_text(config)
        (package / 'GTestConfigVersion.cmake').write_text(
            f'set(PACKAGE_VERSION "{version}")\n'
            'if(PACKAGE_VERSION VERSION_LESS PACKAGE_FIND_VERSION)\n'
            '  set(PACKAGE_VERSION_COMPATIBLE FALSE)\n'
            'else()\n  set(PACKAGE_VERSION_COMPATIBLE TRUE)\nendif()\n')

    def test_installed_config_with_spaces_and_stable_evidence(self):
        self.installed_gtest()
        with patch.dict(os.environ, {'HOLONIGHT_EXTERNAL_PREFIX': str(self.root)}):
            first = external.check(self.config, ('test',))
            second = external.check(self.config, ('test',))
        self.assertEqual(first, second)
        self.assertIn('GTest_DIR=' + str(self.root / 'lib/cmake/GTest'), first['resolved'])

    def test_required_gmock_target_is_not_silently_skipped(self):
        self.installed_gtest(gmock=False)
        with patch.dict(os.environ, {'HOLONIGHT_EXTERNAL_PREFIX': str(self.root)}):
            with self.assertRaisesRegex(RuntimeError, 'consumer: installed GTest lacks GTest::gmock'):
                external.check(self.config, ('test',))

    def test_incompatible_installed_version_fails_without_acquisition(self):
        self.installed_gtest(version='1.13.0')
        # Disable the normal system installation so the incompatible prefix is the only candidate.
        original = external.probe_source
        def isolated(*args, **kwargs):
            return original(*args, **kwargs).replace('find_package(GTest',
                'set(CMAKE_FIND_USE_CMAKE_SYSTEM_PATH FALSE)\nset(CMAKE_FIND_USE_SYSTEM_ENVIRONMENT_PATH FALSE)\nfind_package(GTest')
        with patch.dict(os.environ, {'HOLONIGHT_EXTERNAL_PREFIX': str(self.root)}), patch.object(external, 'probe_source', isolated):
            with self.assertRaisesRegex(RuntimeError, '1.14'):
                external.check(self.config, ('test',))

    def test_production_profile_excludes_test_dependencies(self):
        configs = [json.loads(p.read_text()) for p in (external.BUNDLE / 'modules').glob('*.json')]
        names = external.package_names(configs, 'arch')
        self.assertIn('qmarkdown', names)
        self.assertIn('nlohmann-json', names)
        self.assertIn('polkit-qt6', names)
        self.assertIn('kconfig', names)
        for test_only in ('gtest', 'gtk3', 'gtk4', 'xorg-server-xvfb', 'bubblewrap', 'sway'):
            self.assertNotIn(test_only, names)
        source = external.probe_source(configs, ('build', 'tool', 'runtime'))
        self.assertIn('find_package(Qt6 ${Qt6_VERSION} EXACT REQUIRED', source)
        self.assertNotIn('find_package(GTest', source)

    def test_minimal_daemon_profile_has_no_gui_or_systemd(self):
        config = json.loads((external.BUNDLE / 'modules/holonightd.json').read_text())
        names = external.package_names([config], 'arch', features={'BUILD_SYSTEMD': False})
        self.assertNotIn('systemd', names)
        self.assertNotIn('qt6-base', names)
        self.assertNotIn('gtest', names)
        self.assertIn('nlohmann-json', names)
        self.assertIn('tomlplusplus', names)

    def test_unknown_declaration_and_feature_are_errors(self):
        with self.assertRaisesRegex(RuntimeError, 'unknown external dependency'):
            external.requirements({'module': 'consumer', 'external_dependencies': [{'id': 'unknown', 'scope': ['build']}]})
        with self.assertRaisesRegex(RuntimeError, 'undeclared feature'):
            external.requirements({'module': 'consumer', 'external_dependencies': [{'id': 'gtest', 'scope': ['test'], 'feature': 'BUILD_TESTS'}]})

    def test_configure_never_prepares_sources(self):
        with patch.object(workflow, 'ROOT', self.root), patch.object(workflow, 'prepare') as prepare, \
             patch.object(workflow, 'check_external', return_value={}), patch.object(workflow, 'refresh'), \
             patch.object(workflow, 'run') as run:
            workflow.configure(self.config, 'test')
        prepare.assert_not_called()
        self.assertEqual(run.call_count, 1)

    def test_internal_packages_cannot_resolve_from_external_prefix(self):
        self.installed_gtest()
        config = {'dependencies': [{'package': 'GTest'}]}
        with patch.dict(os.environ, {'HOLONIGHT_EXTERNAL_PREFIX': str(self.root)}):
            with self.assertRaisesRegex(RuntimeError, 'Missing GTest'):
                workflow.packages(config, self.root / 'internal')

    def test_unversioned_sources_have_content_signatures(self):
        checkout = self.root / 'checkout'
        checkout.mkdir()
        source = checkout / 'CMakeLists.txt'
        source.write_text('first')
        before = workflow.source_signature(checkout)
        source.write_text('second')
        self.assertNotEqual(before['content'], workflow.source_signature(checkout)['content'])

    def test_changed_provider_configuration_archives_incompatible_install_tree(self):
        source = self.root / 'source'
        source.mkdir()
        (source / 'CMakeLists.txt').write_text('project(provider)')
        prefix = self.root / 'build/deps/prefix'
        package = prefix / 'lib/cmake/Provider'
        package.mkdir(parents=True)
        (package / 'ProviderConfig.cmake').write_text('old')
        (self.root / 'build/deps/provider-state.json').write_text('{"old": true}')
        config = {'dependencies': [{'module': 'provider', 'package': 'Provider', 'source_variable': 'PROVIDER_SOURCE'}]}
        def install(args, **kwargs):
            if args[1] == '--install':
                package.mkdir(parents=True)
                (package / 'ProviderConfig.cmake').write_text('new')
        with patch.dict(os.environ, {'PROVIDER_SOURCE': str(source)}, clear=True), \
             patch.object(workflow, 'ROOT', self.root), patch.object(workflow, 'check_external', return_value={}), \
             patch.object(workflow, 'toolchain_signature', return_value={'compiler': 'new'}), \
             patch.object(workflow, 'run', side_effect=install) as run:
            workflow.prepare(config)
        self.assertEqual((self.root / 'build/deps.previous-1/prefix/lib/cmake/Provider/ProviderConfig.cmake').read_text(), 'old')
        self.assertEqual((package / 'ProviderConfig.cmake').read_text(), 'new')
        self.assertEqual(run.call_count, 3)

    def test_reuse_is_invalidated_by_compiler_qt_options_features_build_type_and_source(self):
        for changed in ('compiler', 'qt', 'options', 'features', 'build_type', 'source'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = root / 'source'
                source.mkdir()
                file = source / 'CMakeLists.txt'
                file.write_text('project(provider)')
                package = root / 'build/deps/prefix/lib/cmake/Provider'
                config = {'dependencies': [{'module': 'provider', 'package': 'Provider',
                                           'source_variable': 'PROVIDER_SOURCE'}], 'wayland': False}
                compiler = {'identity': 'first'}
                qt = {'resolved': ['Qt6_VERSION=6.11.0']}
                def install(args, **kwargs):
                    if args[1] == '--install':
                        package.mkdir(parents=True, exist_ok=True)
                        (package / 'ProviderConfig.cmake').write_text('installed')
                with patch.dict(os.environ, {'PROVIDER_SOURCE': str(source)}, clear=True), \
                     patch.object(workflow, 'ROOT', root), patch.object(workflow, 'check_external', side_effect=lambda *a, **kw: dict(qt)), \
                     patch.object(workflow, 'toolchain_signature', side_effect=lambda *a: dict(compiler)), \
                     patch.object(workflow, 'run', side_effect=install) as run:
                    workflow.prepare(config)
                    self.assertEqual(run.call_count, 3)
                    workflow.prepare(config)
                    self.assertEqual(run.call_count, 3, 'unchanged provider must be reused')
                    if changed == 'compiler':
                        compiler['identity'] = 'second'
                    elif changed == 'qt':
                        qt['resolved'] = ['Qt6_VERSION=6.12.0']
                    elif changed == 'options':
                        config['dependencies'][0]['options'] = ['-DBUILD_COMPONENT=OFF']
                    elif changed == 'features':
                        config['wayland'] = True
                    elif changed == 'build_type':
                        os.environ['HOLONIGHT_PROVIDER_BUILD_TYPE'] = 'Release'
                    else:
                        file.write_text('project(changed_provider)')
                    workflow.prepare(config)
                    self.assertEqual(run.call_count, 6)
                    self.assertTrue((root / 'build/deps.previous-1/prefix').exists())

    def test_external_sources_are_explicit_and_conflicts_fail_before_build(self):
        config = {'external_sources': [{'module': 'qmarkdown', 'source_variable': 'QMARKDOWN_SOURCE'}]}
        with patch.dict(os.environ, {}, clear=True), patch.object(workflow, 'run') as run:
            workflow.prepare_external(config)
            run.assert_not_called()
        with patch.dict(os.environ, {'QMARKDOWN_SOURCE': '/source', 'HOLONIGHT_EXTERNAL_PREFIX': '/installed'}):
            with self.assertRaisesRegex(RuntimeError, 'conflicting external providers'):
                workflow.prepare_external(config)

    def test_preset_and_explicit_feature_selection_reach_probe_and_cmake(self):
        config = {'module': 'consumer', 'dependencies': [], 'external_features': {'BUILD_SYSTEMD': True}}
        (self.root / 'CMakePresets.json').write_text(json.dumps({'configurePresets': [
            {'name': 'base', 'cacheVariables': {'BUILD_SYSTEMD': 'OFF'}},
            {'name': 'debug', 'inherits': 'base'}]}))
        with patch.object(workflow, 'ROOT', self.root), patch.dict(os.environ, {}, clear=True):
            self.assertEqual(workflow.selected_features(config, 'debug'), {'BUILD_SYSTEMD': False})
        with patch.object(workflow, 'ROOT', self.root), patch.dict(os.environ, {'HOLONIGHT_BUILD_FEATURES': 'BUILD_SYSTEMD=OFF'}), \
             patch.object(workflow, 'check_external', return_value={}) as check, \
             patch.object(workflow, 'toolchain_signature', return_value={}), patch.object(workflow, 'refresh'), \
             patch.object(workflow, 'run') as run:
            workflow.configure(config, 'debug')
            self.assertEqual(check.call_args.kwargs['features'], {'BUILD_SYSTEMD': False})
            self.assertIn('-DBUILD_SYSTEMD=OFF', run.call_args.args[0])

    def test_provider_preparation_only_passes_supported_component_switches(self):
        (self.root / 'CMakeLists.txt').write_text('option(BUILD_COMPOSITOR_WAYLAND "Wayland" ON)\ninclude(CTest)')
        options = workflow.provider_options(self.root, {'wayland': False})
        self.assertIn('-DBUILD_COMPOSITOR_WAYLAND=OFF', options)
        self.assertIn('-DBUILD_TESTING=OFF', options)
        self.assertNotIn('-DBUILD_DEMO=OFF', options)

    def test_duplicate_internal_installations_are_rejected(self):
        for directory in ['lib/cmake/Provider', 'lib64/cmake/Provider']:
            path = self.root / directory
            path.mkdir(parents=True)
            (path / 'ProviderConfig.cmake').write_text('')
        with self.assertRaisesRegex(RuntimeError, 'Conflicting Provider packages'):
            workflow.packages({'dependencies': [{'package': 'Provider'}]}, self.root)

    def test_cmake_rejects_external_internal_provider_and_replaces_stale_directory(self):
        internal = self.root / 'internal'
        outside = self.root / 'external'
        for prefix, value in [(internal, 'internal'), (outside, 'external')]:
            directory = prefix / 'lib/cmake/Provider'
            directory.mkdir(parents=True)
            (directory / 'ProviderConfig.cmake').write_text(f'set(SELECTED_PROVIDER {value})')
        source = self.root / 'consumer'
        source.mkdir()
        helper = external.BUNDLE / 'providers.cmake'
        (source / 'CMakeLists.txt').write_text(f'cmake_minimum_required(VERSION 3.25)\nproject(consumer)\n'
            f'include("{helper}")\nholonight_require_provider(Provider)\nfind_package(Provider CONFIG REQUIRED)\n'
            'file(WRITE "${CMAKE_BINARY_DIR}/selected" "${SELECTED_PROVIDER}")\n')
        args = ['cmake', '-S', str(source), '-B', str(source / 'build'), '-G', 'Ninja',
                '-DHOLONIGHT_DEPENDENCY_PREFIX=' + str(internal), '-DHOLONIGHT_EXTERNAL_PREFIX=' + str(outside),
                '-DProvider_DIR=' + str(outside / 'lib/cmake/Provider')]
        result = subprocess.run(args, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((source / 'build/selected').read_text(), 'internal')
        args[-3] = '-DHOLONIGHT_DEPENDENCY_PREFIX=' + str(self.root / 'missing')
        result = subprocess.run(args, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Missing Provider in approved internal provider prefixes', result.stderr)

    def test_changed_package_exports_are_recorded_even_at_same_version(self):
        self.installed_gtest()
        with patch.dict(os.environ, {'HOLONIGHT_EXTERNAL_PREFIX': str(self.root)}):
            before = external.check(self.config, ('test',))
            config = self.root / 'lib/cmake/GTest/GTestConfig.cmake'
            config.write_text(config.read_text() + 'set(ADDITIONAL_EXPORTED_OPTION ON)\n')
            after = external.check(self.config, ('test',))
        self.assertEqual(before['resolved'], after['resolved'])
        self.assertNotEqual(before['package_config_signatures'], after['package_config_signatures'])

    def test_core_only_profile_does_not_require_qml_or_svg_packages(self):
        config = json.loads((external.BUNDLE / 'modules/holonight-search.json').read_text())
        names = external.package_names([config], 'arch')
        self.assertIn('qt6-base', names)
        self.assertNotIn('qt6-declarative', names)
        self.assertNotIn('qt6-svg', names)

    def test_disabled_compositor_avoids_wayland_and_gui_discovery(self):
        config = json.loads((external.BUNDLE / 'modules/holonight-system-services.json').read_text())
        selected = external.requirements(config, features={'BUILD_COMPOSITOR': False})
        self.assertFalse(any(item['id'] == 'wayland' for item in selected))
        self.assertFalse(any('Gui' in item.get('components', []) for item in selected))

    def test_preset_compiler_and_qt_context_is_shared_with_prerequisite_probe(self):
        (self.root / 'CMakePresets.json').write_text(json.dumps({'configurePresets': [{
            'name': 'debug', 'cacheVariables': {'CMAKE_CXX_COMPILER': '/tools with spaces/clang++',
                                             'Qt6_DIR': '${sourceDir}/external/lib/cmake/Qt6',
                                             'CMAKE_CXX_FLAGS': {'type': 'STRING', 'value': '-march=x86-64'}}}]}))
        with patch.object(workflow, 'ROOT', self.root):
            context = workflow.build_context('debug')
        self.assertEqual(context['CMAKE_CXX_COMPILER'], '/tools with spaces/clang++')
        self.assertEqual(context['Qt6_DIR'], str(self.root / 'external/lib/cmake/Qt6'))
        self.assertEqual(context['CMAKE_CXX_FLAGS'], '-march=x86-64')

    def test_unused_external_source_override_is_not_prepared_in_minimal_profile(self):
        config = json.loads((external.BUNDLE / 'modules/holonight-files.json').read_text())
        with patch.dict(os.environ, {'QMARKDOWN_SOURCE': '/missing-source'}), patch.object(workflow, 'run') as run:
            workflow.prepare_external(config, features={'BUILD_FILES_APP': False})
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
