"""Exercise installer preflight with isolated command/package/CMake boundaries."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "scripts/install-dependencies.sh"
COMMANDS = "git cmake ninja pkg-config sha256sum find sort awk install cp readlink getent pacman c++ python3 wayland-scanner update-desktop-database".split()
PROFILE = HELPER.parent / 'install-profile.sh'
PACKAGES = [line.strip() for line in PROFILE.read_text().splitlines()[2:-1]]



class DependencyChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.probes = self.root / "probes"
        self.probes.mkdir()
        self.log = self.root / "commands"
        self.env = {"PATH": str(self.bin), "TMPDIR": str(self.probes), "LOG": str(self.log)}
        for name in ("mktemp", "rm", "cat", "cp", "dirname"):
            (self.bin / name).symlink_to(shutil.which(name))
        for name in COMMANDS:
            if name in {'cp', 'dirname'}:
                continue
            self.command(name, 'printf "%s\\n" "$0 $*" >> "$LOG"\nexit 98\n')
        self.command("c++", 'cat >/dev/null\nexit "${COMPILER_STATUS:-0}"\n')
        self.command("pacman", '''
printf 'pacman %s\\n' "$*" >> "$LOG"
[[ "$1" = -T ]] || exit 98
shift
if [[ -n "${PACMAN_FAILURE:-}" ]]; then
  printf 'error: package database unavailable\\n' >&2
  exit "$PACMAN_FAILURE"
fi
status=0
for package in "$@"; do
  if [[ " ${MISSING_PACKAGE:-} " = *" $package "* ||
        ( "$package" = qt6-wayland && "${PACKAGING:-merged}" = merged ) ]]; then
    printf '%s\\n' "$package"
    status=127
  fi
done
exit "$status"
''')

    def command(self, name, body):
        path = self.bin / name
        path.write_text("#!/bin/bash\n" + body)
        path.chmod(0o755)

    def check(self, **environment):
        result = subprocess.run(
            ["/bin/bash", "-eu", "-c", 'source "$1"; check_install_dependencies', "fixture", str(HELPER)],
            env=self.env | environment, cwd=self.root, text=True, capture_output=True, timeout=20,
        )
        self.assertEqual(list(self.probes.iterdir()), [], "probe leaked temporary files")
        self.assertEqual({p.name for p in self.root.iterdir()}, {"bin", "probes", "commands"})
        commands = self.log.read_text().splitlines()
        self.assertEqual(commands[0].split(), ["pacman", "-T", *PACKAGES])
        self.assertTrue(all(line.startswith(("pacman -T ", "cmake -S ")) for line in commands), commands)
        return result

    def test_managed_profile_requires_uwsm(self):
        result = self.check(MISSING_PACKAGE="uwsm")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sudo pacman -S --needed uwsm", result.stderr)

    def test_merged_packaging_without_standalone_package(self):
        result = self.check(PACKAGING="merged")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("cmake -S", self.log.read_text())

    def test_standalone_packaging(self):
        result = self.check(PACKAGING="standalone")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unrelated_missing_package(self):
        result = self.check(MISSING_PACKAGE="libsecret")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sudo pacman -S --needed libsecret", result.stderr)
        self.assertNotIn("cmake -S", self.log.read_text())

    def test_missing_storage_runtime(self):
        result = self.check(MISSING_PACKAGE="udisks2")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sudo pacman -S --needed udisks2", result.stderr)
        self.assertNotIn("cmake -S", self.log.read_text())

    def test_package_database_failure_stops_preflight(self):
        result = self.check(PACMAN_FAILURE="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("package database unavailable", result.stderr)
        self.assertIn("pacman dependency check failed (exit 1)", result.stderr)
        self.assertNotIn("cmake -S", self.log.read_text())

    def test_missing_viewer_dependencies(self):
        for package in ("libwebp", "libexif", "qt6-imageformats", "python"):
            with self.subTest(package=package):
                self.log.write_text("")
                result = self.check(MISSING_PACKAGE=package)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("sudo pacman -S --needed " + package, result.stderr)
                self.assertNotIn("cmake -S", self.log.read_text())

    def test_optional_icon_themes_do_not_block_installation(self):
        for missing in ("papirus-icon-theme", "breeze-icons", "papirus-icon-theme breeze-icons"):
            with self.subTest(missing=missing):
                self.log.write_text("")
                result = self.check(MISSING_PACKAGE=missing)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("cmake -S", self.log.read_text())

    def test_icons_require_hicolor_fallback(self):
        result = self.check(MISSING_PACKAGE="hicolor-icon-theme")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sudo pacman -S --needed hicolor-icon-theme", result.stderr)

    def test_unrelated_missing_command(self):
        (self.bin / "git").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing required commands: git", result.stderr)

    def test_missing_package_manager(self):
        (self.bin / "pacman").unlink()
        result = subprocess.run(
            ["/bin/bash", "-eu", "-c", 'source "$1"; check_install_dependencies', "fixture", str(HELPER)],
            env=self.env, cwd=self.root, text=True, capture_output=True, timeout=20,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing required commands: pacman", result.stderr)
        self.assertFalse(self.log.exists())
        self.assertEqual(list(self.probes.iterdir()), [])

    def test_incompatible_compiler(self):
        result = self.check(COMPILER_STATUS="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required C++23 support", result.stderr)

    def test_missing_compiler(self):
        (self.bin / "c++").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("C++23 compiler", result.stderr)


if __name__ == "__main__":
    unittest.main()
