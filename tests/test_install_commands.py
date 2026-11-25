"""Replay installer failure diagnostics against disposable commands."""
import argparse
from contextlib import redirect_stderr
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location('installer', SCRIPTS / 'source-install.py')
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)

SCREENSHOT = 'holonight-screenshot'


class InstallerCommands(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.env = {**os.environ, 'PATH': str(self.bin), 'LOG': str(self.root / 'command.log')}
        self.env.pop('HOLONIGHT_EXTERNAL_PREFIX', None)
        env_patch = patch.dict(os.environ, self.env, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def command(self, name, body):
        path = self.bin / name
        path.write_text('#!/bin/sh\n' + body)
        path.chmod(0o755)

    def replay(self, operation, status):
        diagnostics = io.StringIO()
        with redirect_stderr(diagnostics), self.assertRaises(subprocess.CalledProcessError) as failure:
            operation()
        self.assertEqual(failure.exception.returncode, status)
        summary, command = diagnostics.getvalue().splitlines()
        self.assertIn(f'exit {status}', summary)
        original = (self.root / 'command.log').read_bytes()
        (self.root / 'command.log').write_bytes(b'')
        result = subprocess.run(['/bin/bash', '-c', command], cwd=self.root, timeout=5)
        self.assertEqual(result.returncode, status)
        self.assertEqual((self.root / 'command.log').read_bytes(), original)
        return original

    def screenshot_preflight(self, compiler='exit 0\n'):
        (self.root / SCREENSHOT / '.git').mkdir(parents=True)
        for tool in ('git', 'cmake', 'ninja', 'pkg-config'):
            self.command(tool, 'exit 98\n')
        self.command('pacman', """
printf '%s\\n' "$@" > "$LOG"
status=0
for package in "$@"; do
    case "$package" in
        qt6-wayland|"${MISSING_PACKAGE:-}") printf '%s\\n' "$package"; status=127 ;;
    esac
done
exit "$status"
""")
        self.command('c++', compiler)
        release = Path.read_text

        def read_text(path, *args, **kwargs):
            if path == Path('/etc/os-release'):
                return 'ID=arch\n'
            return release(path, *args, **kwargs)

        with patch.object(installer, 'ROOT', self.root), patch.object(Path, 'read_text', read_text):
            installer.preflight([SCREENSHOT], pinned=False)

    def test_screenshot_preflight_accepts_merged_qt_packaging(self):
        self.screenshot_preflight()
        packages = (self.root / 'command.log').read_text().splitlines()
        self.assertIn('qt6-base', packages)
        self.assertNotIn('qt6-wayland', packages)

    def test_missing_screenshot_package_blocks_preflight_and_command_replays(self):
        with patch.dict(os.environ, MISSING_PACKAGE='grim'):
            arguments = self.replay(self.screenshot_preflight, 127).decode().splitlines()
        self.assertEqual(arguments[0], '-T')
        self.assertIn('grim', arguments)

    def test_failed_command_preserves_spaces_quotes_and_glob(self):
        self.command('fixture', 'printf "%s\\n" "$@" > "$LOG"\nexit 7\n')
        (self.root / 'HoloNight_DIR').touch()
        argument = self.root / "it's a build path"
        self.assertEqual(
            self.replay(lambda: installer.run('fixture', argument, '*[Hh]olo*_DIR'), 7),
            f'{argument}\n*[Hh]olo*_DIR\n'.encode(),
        )

    def test_failed_staging_command_replays_destdir(self):
        self.command('cmake', """
if [ "$1" = --install ]; then
    printf '%s\\n' "$DESTDIR" "$@" > "$LOG"
    exit 8
fi
""")
        work = self.root / "stage with 'quotes'"
        with patch.object(installer, 'WORK', work), patch.object(installer, 'host_identity', return_value='host'), \
                patch.object(installer, 'source_identity', return_value={'dirty': False}):
            arguments = self.replay(
                lambda: installer.prepare([SCREENSHOT], argparse.Namespace(components=[SCREENSHOT])), 8,
            ).decode().splitlines()
        self.assertEqual(Path(arguments[0]).parent.parent, work)
        self.assertEqual(Path(arguments[0]).name, SCREENSHOT)
        self.assertEqual(arguments[1], '--install')

    def test_failed_compiler_probe_replays_source(self):
        captured = self.replay(
            lambda: self.screenshot_preflight('/bin/cat > "$LOG"\nexit 9\n'),
            9,
        )
        self.assertIn(b'#include <expected>\n', captured)
        self.assertIn(b'std::expected<int,int>', captured)
        self.assertTrue(captured.endswith(b'\n'))
