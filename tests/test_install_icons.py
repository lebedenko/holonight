"""Exercise the real icons staging and umbrella lifecycle in disposable roots."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVISION = "1" * 40


class IconsInstallation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.target = self.root / "target"
        self.target.mkdir()
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in ("install-dependencies.sh", "prune-icons.py"):
            shutil.copy(ROOT / "scripts" / name, scripts)
        source, separator, _ = (ROOT / "scripts/install.sh").read_text().partition(
            '\npreflight\nnote "Preflight passed"')
        self.assertTrue(separator)
        self.functions = scripts / "functions.sh"
        self.functions.write_text(source)
        icons = self.root / "holonight-icons"
        icons.mkdir()
        for name in ("scripts", "icons", "metadata", "LICENSES"):
            shutil.copytree(ROOT / "holonight-icons" / name, icons / name, symlinks=True,
                            ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("REUSE.toml", "THIRD_PARTY_NOTICES.md"):
            shutil.copy(ROOT / "holonight-icons" / name, icons)
        self.commands = self.root / "commands"
        self.commands.mkdir()
        self.command("git", f"printf '%s\\n' '{REVISION}'\n")
        # External cache tool boundary: cache bytes must enter the manifest.
        self.command("gtk-update-icon-cache", '''
printf '%s\\n' "$4" >> "$CACHE_LOG"
printf 'fixture icon cache for %s\\n' "$4" > "$4/icon-theme.cache"
''')
        for name in ("sudo", "kbuildsycoca6", "ldconfig", "systemctl"):
            self.command(name, 'printf "unexpected host command\\n" >&2\nexit 99\n')
        self.env = dict(os.environ, PATH=f"{self.commands}:{os.environ['PATH']}",
                        CACHE_LOG=str(self.root / "cache.log"), XDG_DATA_HOME=str(self.root / "user-data"))
        self.build = self.root / ".source-install"
        self.stage = self.build / "stage"
        self.stage.mkdir(parents=True)
        self.manifest = self.target / "var/lib/holonight/source-install/manifest.tsv"

    def command(self, name, body):
        path = self.commands / name
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(0o755)

    def run_functions(self, command):
        return subprocess.run(
            ["bash", "-eu", "-c", 'source "$1" --root "$2"; ' + command,
             "fixture", str(self.functions), str(self.target)],
            env=self.env, text=True, capture_output=True, timeout=120)

    def prepare(self):
        result = self.run_functions('''
find "$BUILD_ROOT/stage" -mindepth 1 -printf '/%P\\n' | sort > "$BUILD_ROOT/before"
stage_icons
find "$BUILD_ROOT/stage" -mindepth 1 -printf '/%P\\n' | sort > "$BUILD_ROOT/after"
record_module_paths holonight-icons "$BUILD_ROOT/before" "$BUILD_ROOT/after"
make_manifest
''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def install(self):
        result = self.run_functions("collision_check; copy_stage")
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def uninstall(self):
        result = subprocess.run(
            ["bash", str(ROOT / "scripts/uninstall.sh"), "--yes", "--root", str(self.target)],
            env=self.env, text=True, capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_complete_payload_caches_repeat_install_and_uninstall(self):
        self.prepare()
        self.install()
        rows = {r[5]: r for line in self.manifest.read_text().splitlines() if (r := line.split("\t"))}
        for theme in ("HoloNight", "HoloNight-Dark"):
            for relative in (f"/usr/share/icons/{theme}/index.theme",
                             f"/usr/share/icons/{theme}/icon-theme.cache",
                             f"/usr/share/icons/{theme}/places/20"):
                self.assertEqual(rows[relative][:2], ["holonight-icons", REVISION])
            cache = f"/usr/share/icons/{theme}/icon-theme.cache"
            self.assertEqual(rows[cache][4], hashlib.sha256((self.target / cache.lstrip('/')).read_bytes()).hexdigest())
            alias = self.target / f"usr/share/icons/{theme}/places/20"
            self.assertTrue(alias.is_symlink())
            self.assertEqual(os.readlink(alias), "24")
        self.assertIn("/usr/share/holonight-icons/scripts/recolor.py", rows)
        self.assertEqual((self.root / "cache.log").read_text().splitlines(),
                         [str(base / f"usr/share/icons/{name}") for base in (self.stage, self.target)
                          for name in ("HoloNight", "HoloNight-Dark")])
        before = self.manifest.read_bytes()
        self.install()
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertFalse((self.root / "user-data").exists())
        self.uninstall()
        self.assertFalse((self.target / "usr/share/icons/HoloNight").exists())
        self.assertFalse((self.target / "usr/share/icons/HoloNight-Dark").exists())
        self.assertFalse((self.target / "usr/share/holonight-icons").exists())

    def test_legacy_upgrade_preserves_modified_and_unowned_paths(self):
        self.prepare()
        legacy = self.target / "usr/share/icons/HoloNight/scalable/places"
        legacy.mkdir(parents=True)
        rows = []
        for name in ("removed.svg", "modified.svg"):
            path = legacy / name
            path.write_bytes(b"original")
            rows.append(["holonight-icons", "0" * 40, "f", "644", hashlib.sha256(b"original").hexdigest(),
                         "/" + str(path.relative_to(self.target))])
        alias = legacy / "alias.svg"
        alias.symlink_to("removed.svg")
        rows.append(["holonight-icons", "0" * 40, "l", "-", hashlib.sha256(b"removed.svg").hexdigest(),
                     "/" + str(alias.relative_to(self.target))])
        for directory in (legacy.parent, legacy):
            rows.append(["holonight-icons", "0" * 40, "d", "755", "-",
                         "/" + str(directory.relative_to(self.target))])
        empty = legacy.parent / "empty"
        empty.mkdir()
        rows.append(["holonight-icons", "0" * 40, "d", "755", "-",
                     "/" + str(empty.relative_to(self.target))])
        (legacy / "modified.svg").write_bytes(b"custom")
        (legacy / "unowned.svg").write_bytes(b"unowned")
        # Earlier installers refreshed this cache without recording ownership.
        old_cache = legacy.parent.parent / "icon-theme.cache"
        old_cache.write_bytes(b"unowned legacy cache")
        index = legacy.parent.parent / "index.theme"
        index.write_bytes(b"old theme")
        rows.append(["holonight-icons", "0" * 40, "f", "644", hashlib.sha256(b"old theme").hexdigest(),
                     "/" + str(index.relative_to(self.target))])
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_text("".join("\t".join(row) + "\n" for row in rows))
        result = self.install()
        self.assertIn("preserved modified", result.stderr)
        self.assertFalse((legacy / "removed.svg").exists())
        self.assertFalse(alias.is_symlink())
        self.assertFalse(empty.exists())
        self.assertEqual((legacy / "modified.svg").read_bytes(), b"custom")
        self.assertEqual((legacy / "unowned.svg").read_bytes(), b"unowned")
        self.assertIn("modified.svg", self.manifest.read_text())
        self.assertNotIn("removed.svg", self.manifest.read_text())
        self.assertNotIn("unowned.svg", self.manifest.read_text())
        self.assertEqual(old_cache.read_bytes(), b"unowned legacy cache")
        self.assertNotIn("/HoloNight/icon-theme.cache", self.manifest.read_text())
        self.uninstall()
        self.assertEqual((legacy / "modified.svg").read_bytes(), b"custom")
        self.assertEqual((legacy / "unowned.svg").read_bytes(), b"unowned")
        self.assertEqual(old_cache.read_bytes(), b"unowned legacy cache")

    def test_unowned_collision_and_symlinked_parent_abort_before_copy(self):
        self.prepare()
        theme = self.target / "usr/share/icons/HoloNight"
        theme.mkdir(parents=True)
        collision = theme / "index.theme"
        collision.write_text("unowned")
        result = self.run_functions("collision_check; copy_stage")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not owned", result.stderr)
        self.assertEqual(collision.read_text(), "unowned")
        self.assertFalse((theme.parent / "HoloNight-Dark").exists())
        collision.unlink()
        theme.rmdir()
        outside = self.root / "outside"
        outside.mkdir()
        theme.symlink_to(outside, target_is_directory=True)
        result = self.run_functions("collision_check; copy_stage")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_cache_failure_prevents_deployment(self):
        self.command("gtk-update-icon-cache", "exit 7\n")
        result = self.run_functions("stage_icons; make_manifest; collision_check; copy_stage")
        self.assertEqual(result.returncode, 7)
        self.assertEqual(list(self.target.iterdir()), [])

    @unittest.skipUnless(shutil.which("gtk-update-icon-cache"), "GTK cache utility unavailable")
    def test_real_cache_tool_accepts_both_generated_themes(self):
        cache_tool = shutil.which("gtk-update-icon-cache")
        # Invoke the installed executable directly, bypassing the test PATH fixture.
        result = self.run_functions('python3 "$REPO_ROOT/holonight-icons/scripts/stage.py" --destdir "$BUILD_ROOT/stage"')
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("HoloNight", "HoloNight-Dark"):
            theme = self.stage / "usr/share/icons" / name
            result = subprocess.run([cache_tool, "-q", "-t", "-f", str(theme)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((theme / "icon-theme.cache").is_file())
            result = subprocess.run([cache_tool, "--validate", str(theme)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


class ObsoleteIconSafety(unittest.TestCase):
    def test_pruning_and_uninstall_do_not_follow_replaced_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target"
            icons = target / "usr/share/icons/HoloNight"
            icons.mkdir(parents=True)
            outside = root / "outside"
            outside.mkdir()
            (outside / "old.svg").write_bytes(b"original")
            (icons / "scalable").symlink_to(outside, target_is_directory=True)
            manifest = target / "var/lib/holonight/source-install/manifest.tsv"
            manifest.parent.mkdir(parents=True)
            row = "\t".join(["holonight-icons", REVISION, "f", "644", hashlib.sha256(b"original").hexdigest(),
                             "/usr/share/icons/HoloNight/scalable/old.svg"]) + "\n"
            manifest.write_text(row)
            new = root / "new.tsv"
            new.write_text("")
            result = subprocess.run(["python3", str(ROOT / "scripts/prune-icons.py"), "--root", str(target),
                                     "--old-manifest", str(manifest), "--new-manifest", str(new)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, row)
            result = subprocess.run(["bash", str(ROOT / "scripts/uninstall.sh"), "--yes", "--root", str(target)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("symlinked parent", result.stderr)
            self.assertEqual((outside / "old.svg").read_bytes(), b"original")

    def test_pruning_is_restricted_to_obsolete_icons_owned_payloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = []
            for owner, relative in (("holonight-viewer", "/usr/share/icons/HoloNight/other.svg"),
                                    ("holonight-icons", "/usr/share/icons/hicolor/other.svg"),
                                    ("holonight-icons", "/usr/share/icons/HoloNight/current.svg")):
                path = root / relative.lstrip("/")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"original")
                rows.append("\t".join([owner, REVISION, "f", "644", hashlib.sha256(b"original").hexdigest(), relative]))
            old, new = root / "old.tsv", root / "new.tsv"
            old.write_text("\n".join(rows) + "\n")
            new.write_text(rows[-1] + "\n")
            result = subprocess.run(["python3", str(ROOT / "scripts/prune-icons.py"), "--root", str(root),
                                     "--old-manifest", str(old), "--new-manifest", str(new)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            for row in rows:
                self.assertEqual((root / row.split("\t")[-1].lstrip("/")).read_bytes(), b"original")
