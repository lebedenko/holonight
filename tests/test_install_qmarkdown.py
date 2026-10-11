"""Installed external QMarkdown remains outside umbrella ownership."""
from pathlib import Path
import subprocess
import unittest
import test_install_dependencies as preflight
import test_install_ownership as ownership
ROOT = ownership.ROOT


class QMarkdownPreflight(unittest.TestCase):
    def setUp(self):
        self.fixture = preflight.DependencyChecks()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()

    def test_missing_system_package_fails_before_configuration(self):
        result = self.fixture.check(MISSING_PACKAGE='qmarkdown')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('sudo pacman -S --needed qmarkdown', result.stderr)
        self.assertNotIn('cmake -S', self.fixture.log.read_text())

    def test_shared_library_and_metadata_failures_are_actionable(self):
        for diagnostic in ('Files requires installed shared QMarkdown 1.x',
                           'Installed QMarkdown is missing QML metadata: QMarkdown.qmltypes'):
            self.fixture.log.write_text('')
            result = self.fixture.check(CMAKE_FAILURE=diagnostic)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(diagnostic, result.stderr)
            self.assertIn('installed shared QMarkdown', result.stderr)


class QMarkdownOwnership(unittest.TestCase):
    def setUp(self):
        self.fixture = ownership.FilesOwnership()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()

    def test_system_package_survives_umbrella_install_and_uninstall(self):
        package_files = ['usr/lib/libQMarkdown.so.1', 'usr/lib/cmake/QMarkdown/QMarkdownConfig.cmake',
                         'usr/lib/qt6/qml/QMarkdown/qmldir', 'usr/lib/qt6/qml/QMarkdown/QMarkdown.qmltypes',
                         'usr/lib/qt6/qml/QMarkdown/libQMarkdownPlugin.so', 'usr/share/licenses/QMarkdown/LICENSE']
        for name in package_files:
            path = self.fixture.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'package-owned')
        manifest = self.fixture.make_manifest()
        self.assertNotIn('QMarkdown', manifest)
        result = self.fixture.run_functions('collision_check; copy_stage')
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(['bash', str(ROOT / 'scripts/uninstall.sh'), '--yes', '--root', str(self.fixture.target)],
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in package_files:
            self.assertEqual((self.fixture.target / name).read_bytes(), b'package-owned')

    def test_installer_has_no_external_acquisition_or_staging(self):
        script = (ROOT / 'scripts/install.sh').read_text()
        self.assertNotIn('stage_qmarkdown', script)
        self.assertNotIn('git -C "$source" fetch', script)
        self.assertNotIn('QMARKDOWN_SOURCE', script)
