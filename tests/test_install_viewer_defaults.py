"""User preference upgrades and installed desktop MIME discovery."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('viewer_defaults', ROOT / 'scripts/extend-viewer-defaults.py')
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)
ENTRY = ROOT / 'holonight-viewer/packaging/org.holonight.Viewer.desktop'
VIEWER = HELPER.VIEWER
OLD = '[Default Applications]\n' + ''.join(f'{mime}={VIEWER};\n' for mime in (*HELPER.BASE, 'image/bmp'))


class ViewerDefaults(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = self.root / 'config'
        self.config.mkdir()
        self.data = self.root / 'data'
        self.target = self.config / 'mimeapps.list'
        environment = patch.dict(os.environ, HOME=str(self.root), XDG_CONFIG_HOME=str(self.config),
                                 XDG_DATA_HOME=str(self.data), XDG_CURRENT_DESKTOP='HoloNight:Other')
        environment.start()
        self.addCleanup(environment.stop)

    def test_upgrade_preserves_content_mode_and_is_idempotent(self):
        self.target.write_text('# custom\n' + OLD + '\n[Other]\nkey=value\n')
        self.target.chmod(0o640)
        HELPER.extend(ENTRY)
        result = self.target.read_bytes()
        for mime in ('image/svg+xml', 'image/tiff'):
            self.assertIn(f'{mime}={VIEWER};'.encode(), result)
        self.assertIn(b'[Other]\nkey=value\n', result)
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o640)
        HELPER.extend(ENTRY)
        self.assertEqual(self.target.read_bytes(), result)

    def test_preserves_unrelated_line_endings(self):
        self.target.write_bytes(OLD.replace('\n', '\r\n').encode())
        HELPER.extend(ENTRY)
        self.assertIn(OLD.splitlines()[1].encode() + b'\r\n', self.target.read_bytes())

    def test_fresh_other_and_mixed_choices_unchanged(self):
        HELPER.extend(ENTRY)
        self.assertFalse(self.target.exists())
        for text in (OLD.replace(VIEWER, 'other.desktop'), OLD.replace('image/png='+VIEWER, 'image/png=other.desktop')):
            self.target.write_text(text)
            HELPER.extend(ENTRY)
            self.assertEqual(self.target.read_text(), text)

    def test_explicit_choices_and_removal_preserved(self):
        self.target.write_text(OLD + 'image/svg+xml=other.desktop;\n[Removed Associations]\nimage/tiff='+VIEWER+';\n')
        before = self.target.read_bytes()
        HELPER.extend(ENTRY)
        self.assertEqual(self.target.read_bytes(), before)

    def test_desktop_specific_and_legacy_choices(self):
        legacy = self.data / 'applications/defaults.list'
        legacy.parent.mkdir(parents=True)
        legacy.write_text(OLD)
        desktop = self.config / 'holonight-mimeapps.list'
        desktop.write_text('[Default Applications]\nimage/svg+xml=other.desktop;\n')
        HELPER.extend(ENTRY)
        self.assertNotIn('image/svg+xml', self.target.read_text())
        self.assertIn('image/tiff', self.target.read_text())
        self.assertEqual(legacy.read_text(), OLD)
        self.target.write_text(OLD)
        desktop.write_text('[Default Applications]\nimage/png=other.desktop;\n')
        HELPER.extend(ENTRY)
        self.assertEqual(self.target.read_text(), OLD)

    def test_default_xdg_paths_and_installed_format_extension(self):
        target = self.root / '.config/mimeapps.list'
        target.parent.mkdir()
        target.write_text(OLD)
        installed = self.root / 'viewer.desktop'
        installed.write_text(ENTRY.read_text().replace('image/tiff;', 'image/tiff;image/x-new-format;'))
        with patch.dict(os.environ, XDG_CONFIG_HOME='', XDG_DATA_HOME=''):
            HELPER.extend(installed)
        self.assertIn('image/x-new-format='+VIEWER, target.read_text())
        self.assertFalse(self.target.exists())

    def test_symlinked_preferences_preserve_link_and_destination_mode(self):
        actual = self.root / 'preferences'
        actual.write_text(OLD)
        actual.chmod(0o640)
        self.target.symlink_to(actual)
        HELPER.extend(ENTRY)
        self.assertTrue(self.target.is_symlink())
        self.assertIn('image/tiff', actual.read_text())
        self.assertEqual(actual.stat().st_mode & 0o777, 0o640)

    def test_atomic_write_failure_preserves_original(self):
        self.target.write_text(OLD)
        with patch.object(HELPER.os, 'replace', side_effect=PermissionError('fixture')):
            with self.assertRaises(PermissionError):
                HELPER.extend(ENTRY)
        self.assertEqual(self.target.read_text(), OLD)
        self.assertEqual(list(self.config.iterdir()), [self.target])

    @unittest.skipUnless(shutil.which('gio') and shutil.which('update-desktop-database'), 'GIO desktop tools unavailable')
    def test_isolated_installed_gio_discovery_for_every_format(self):
        applications = self.data / 'applications'
        applications.mkdir(parents=True)
        shutil.copy(ENTRY, applications / VIEWER)
        binary = self.root / 'bin'
        binary.mkdir()
        executable = binary / 'hn-viewer'
        executable.write_text('#!/bin/sh\nexit 0\n')
        executable.chmod(0o755)
        with patch.dict(os.environ, PATH=f'{binary}:{os.environ["PATH"]}',
                        XDG_DATA_DIRS=str(self.root / 'empty'), LC_ALL='C'):
            subprocess.run(['update-desktop-database', str(applications)], check=True)
            declared = HELPER.read(ENTRY).get('Desktop Entry', 'MimeType').strip(';').split(';')
            for mime in declared:
                result = subprocess.run(['gio', 'mime', mime], capture_output=True, text=True, check=True)
                self.assertIn(VIEWER, result.stdout.split('Registered applications:', 1)[1], mime)
            self.target.write_text(OLD)
            HELPER.extend(applications / VIEWER)
            for mime in declared:
                result = subprocess.run(['gio', 'mime', mime], capture_output=True, text=True, check=True)
                self.assertIn(VIEWER, result.stdout.splitlines()[0], mime)


class InstallerPreferenceBoundary(unittest.TestCase):
    def run_functions(self, body):
        source = (ROOT / 'scripts/install.sh').read_text().split('\npreflight\nnote "Preflight passed"')[0]
        with tempfile.TemporaryDirectory() as directory:
            scripts = Path(directory) / 'scripts'
            scripts.mkdir()
            shutil.copy(ROOT / 'scripts/install-dependencies.sh', scripts)
            functions = scripts / 'functions.sh'
            functions.write_text(source)
            return subprocess.run(['bash', '-eu', '-c', 'source "$1" --yes; ' + body,
                                   'fixture', str(functions)], capture_output=True, text=True)

    def test_staging_and_check_only_skip_user_helper(self):
        for body in ('TARGET_ROOT=/tmp/staging; extend_viewer_defaults',
                     'CHECK_ONLY=1; extend_viewer_defaults'):
            result = self.run_functions('python3() { return 99; }; ' + body)
            self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(os.geteuid() == 0, 'direct root boundary requires root')
    def test_direct_root_reports_skip(self):
        result = self.run_functions('python3() { return 99; }; extend_viewer_defaults')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('direct root', result.stdout)

    def test_desktop_cache_failure_stops_before_preferences(self):
        result = self.run_functions('as_root() { [[ "$1" != update-desktop-database ]]; }; '
                                    'refresh_system; echo unexpected')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('desktop database refresh failed', result.stderr)
        self.assertNotIn('unexpected', result.stdout)
