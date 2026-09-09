"""Exercise installer preflight with isolated command/package/CMake boundaries."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "scripts/install-dependencies.sh"
COMMANDS = "git cmake ninja pkg-config sha256sum find sort awk install cp readlink getent pacman c++".split()
PACKAGES = """base-devel cmake ninja pkgconf qt6-base qt6-declarative qt6-svg layer-shell-qt
    tomlplusplus json-glib gtk3 gtk4 wayland wayland-protocols libpulse libsecret pacman sqlite systemd
    syntax-highlighting md4c greetd cage""".split()


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
        for name in ("mktemp", "rm", "cat"):
            (self.bin / name).symlink_to(shutil.which(name))
        for name in COMMANDS:
            self.command(name, 'printf "%s\\n" "$0 $*" >> "$LOG"\nexit 98\n')
        self.command("c++", 'cat >/dev/null\nexit "${COMPILER_STATUS:-0}"\n')
        self.command("pacman", '''
printf 'pacman %s\\n' "$*" >> "$LOG"
[[ "$1" = -T ]] || exit 98
shift
for package in "$@"; do
  if [[ "$package" = "${MISSING_PACKAGE:-}" ||
        ( "$package" = qt6-wayland && "${PACKAGING:-merged}" = merged ) ]]; then
    printf '%s\\n' "$package"
  fi
done
''')
        self.command("cmake", '''
printf 'cmake %s\\n' "$*" >> "$LOG"
[[ "$1" = -S && "$3" = -B && "$5" = -G && "$6" = Ninja && "$#" = 6 ]] || exit 98
[[ "$2" = "$TMPDIR"/holonight-qt-check.* && "$4" = "$2/build" ]] || exit 98
source_text="$(cat "$2/CMakeLists.txt")"
[[ "$source_text" = *'find_package(Qt6 6.11 REQUIRED COMPONENTS WaylandClient)'* ]] || exit 97
[[ "$source_text" = *'find_package(Qt6WaylandScannerTools 6.11 REQUIRED)'* ]] || exit 97
if [[ -n "${CMAKE_FAILURE:-}" ]]; then
  printf 'CMake Error: %s\\n' "$CMAKE_FAILURE" >&2
  exit 1
fi
printf 'Configure succeeded\\n'
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

    def test_merged_packaging_without_standalone_package(self):
        result = self.check(PACKAGING="merged")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Configure succeeded", result.stdout)

    def test_standalone_packaging(self):
        result = self.check(PACKAGING="standalone")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_capabilities_and_configuration_failures(self):
        for diagnostic in ("WaylandClient missing", "Qt6WaylandScannerTools missing",
                           "Qt6 version 6.10 incompatible with requested 6.11", "configuration failed"):
            with self.subTest(diagnostic=diagnostic):
                self.log.write_text("")
                result = self.check(CMAKE_FAILURE=diagnostic)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("CMake Error: " + diagnostic, result.stderr)
                self.assertIn("Qt >= 6.11", result.stderr)
                self.assertNotIn("qt6-wayland", result.stderr)

    def test_unrelated_missing_package(self):
        result = self.check(MISSING_PACKAGE="libsecret")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sudo pacman -S --needed libsecret", result.stderr)
        self.assertNotIn("cmake -S", self.log.read_text())

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
