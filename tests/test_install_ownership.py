"""Exercise application payload ownership using the real installer functions in disposable roots."""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_REVISION = "1" * 40


class ViewerOwnership(unittest.TestCase):
    module = "holonight-viewer"
    executable = "hn-viewer"
    app_id = "org.holonight.Viewer"
    binary_dir = "bin"
    entry_dir = "share/applications"
    entry_suffix = ".desktop"
    auxiliary_path = None

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.target = self.root / "target"
        self.target.mkdir()
        scripts = self.root / "scripts"
        scripts.mkdir()
        shutil.copy(ROOT / "scripts/install-dependencies.sh", scripts)
        shutil.copy(ROOT / "scripts/prune-icons.py", scripts)
        # Load the production functions without running preflight/build/host installation.
        source = (ROOT / "scripts/install.sh").read_text()
        functions, separator, _ = source.partition('\npreflight\nnote "Preflight passed"')
        self.assertTrue(separator, "installer entrypoint changed")
        self.functions = scripts / "installer-functions.sh"
        self.functions.write_text(functions)
        self.commands = self.root / "commands"
        self.commands.mkdir()
        # Git is the only mocked boundary: the disposable fixture has no real checkouts.
        git = self.commands / "git"
        git.write_text("#!/bin/sh\nprintf '%s\\n' '" + FIXTURE_REVISION + "'\n")
        git.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.commands) + ":" + os.environ["PATH"])
        self.build = self.root / ".source-install"
        self.stage = self.build / "stage"
        self.payload = {
            f"/usr/{self.binary_dir}/{self.executable}": b"viewer executable\n",
            f"/usr/{self.entry_dir}/{self.app_id}{self.entry_suffix}": b"viewer desktop entry\n",
            (self.auxiliary_path or f"/usr/share/icons/hicolor/scalable/apps/{self.app_id}.svg"): b"viewer icon\n",
        }
        for relative, data in self.payload.items():
            path = self.stage / relative.lstrip("/")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (self.build / "module-paths").mkdir()
        (self.build / "before").write_text("")
        (self.build / "after").write_text("".join(path + "\n" for path in sorted(self.payload)))

    def run_functions(self, commands):
        return subprocess.run(
            ["bash", "-eu", "-c", 'source "$1" --root "$2"; ' + commands,
             "fixture", str(self.functions), str(self.target)],
            env=self.env, text=True, capture_output=True, timeout=20,
        )

    def make_manifest(self):
        result = self.run_functions(
            f'record_module_paths {self.module} "$BUILD_ROOT/before" "$BUILD_ROOT/after"; make_manifest'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return (self.build / "manifest.tsv").read_text()

    def test_payload_records_owner_revision_and_hash(self):
        manifest = self.make_manifest()
        entries = {fields[5]: fields for line in manifest.splitlines() if (fields := line.split("\t"))}
        for relative, data in self.payload.items():
            with self.subTest(path=relative):
                fields = entries[relative]
                self.assertEqual(fields[:3], [self.module, FIXTURE_REVISION, "f"])
                self.assertEqual(fields[4], hashlib.sha256(data).hexdigest())

    def test_unowned_legacy_install_is_rejected_without_changes(self):
        self.make_manifest()
        existing = self.target / f"usr/{self.binary_dir}/{self.executable}"
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"legacy or package-owned executable")
        result = self.run_functions("collision_check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not owned by an earlier umbrella installation", result.stderr)
        self.assertEqual(existing.read_bytes(), b"legacy or package-owned executable")
        self.assertFalse((self.target / "usr/share").exists())

    def test_uninstall_removes_owned_payload_and_preserves_modified_files(self):
        self.make_manifest()
        result = self.run_functions("collision_check; copy_stage")
        self.assertEqual(result.returncode, 0, result.stderr)
        desktop = self.target / f"usr/{self.entry_dir}/{self.app_id}{self.entry_suffix}"
        desktop.write_bytes(b"user modified desktop entry")
        unrelated = self.target / "usr/bin/other-app"
        unrelated.parent.mkdir(parents=True, exist_ok=True)
        unrelated.write_bytes(b"unrelated")
        result = subprocess.run(
            ["bash", str(ROOT / "scripts/uninstall.sh"), "--yes", "--root", str(self.target)],
            text=True, capture_output=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preserved modified path", result.stderr)
        self.assertEqual(desktop.read_bytes(), b"user modified desktop entry")
        self.assertEqual(unrelated.read_bytes(), b"unrelated")
        self.assertFalse((self.target / f"usr/{self.binary_dir}/{self.executable}").exists())
        self.assertFalse((self.target / (self.auxiliary_path or f"/usr/share/icons/hicolor/scalable/apps/{self.app_id}.svg").lstrip("/")).exists())

    def migration_fixture(self, package_owned=False):
        self.make_manifest()
        existing = self.target / f"usr/{self.binary_dir}/{self.executable}"
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"legacy executable")
        pacman = self.commands / "pacman"
        pacman.write_text(
            '#!/bin/sh\ncase "$3" in\n-Q) exit 0;;\n-Qo) exit '
            + ("0" if package_owned else "1") + ';;\nesac\nexit 2\n'
        )
        pacman.chmod(0o755)
        return existing

    def test_migration_backs_up_and_records_ownership(self):
        existing = self.migration_fixture()
        result = self.run_functions("ADOPT_EXISTING=1; collision_check; copy_stage")
        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list((self.target / "var/backups").glob("holonight-source-migration.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / f"usr/{self.binary_dir}/{self.executable}").read_bytes(), b"legacy executable")
        self.assertEqual(existing.read_bytes(), self.payload[f"/usr/{self.binary_dir}/{self.executable}"])
        result = self.run_functions("collision_check")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_migration_rejects_package_owned_files_before_copy(self):
        existing = self.migration_fixture(package_owned=True)
        result = self.run_functions("ADOPT_EXISTING=1; collision_check; copy_stage")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is package-owned", result.stderr)
        self.assertEqual(existing.read_bytes(), b"legacy executable")
        self.assertFalse((self.target / "var").exists())

    def test_migration_rejects_unreadable_package_database(self):
        existing = self.migration_fixture()
        (self.commands / "pacman").write_text("#!/bin/sh\nexit 1\n")
        result = self.run_functions("ADOPT_EXISTING=1; collision_check; copy_stage")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot read the package database", result.stderr)
        self.assertEqual(existing.read_bytes(), b"legacy executable")


class FilesOwnership(ViewerOwnership):
    module = "holonight-files"
    executable = "hn-files"
    app_id = "org.holonight.Files"


class FileChooserOwnership(ViewerOwnership):
    module = "xdg-desktop-portal-holonight"
    executable = "xdg-desktop-portal-holonight"
    app_id = "org.freedesktop.impl.portal.desktop.holonight_filechooser"
    binary_dir = "libexec"
    entry_dir = "share/dbus-1/services"
    entry_suffix = ".service"
    auxiliary_path = "/usr/share/xdg-desktop-portal/portals/holonight-filechooser.portal"


if __name__ == "__main__":
    unittest.main()
