"""Browsing package ownership transfer uses the ordinary conservative installer."""
import test_install_ownership as ownership


class FileBrowserOwnership(ownership.ViewerOwnership):
    module = "holonight-file-browser"
    executable = "libholonight_file_browser_quick.so"
    binary_dir = "lib"
    desktop_path = "/usr/lib/qt6/qml/Holonight/FileBrowser/qmldir"
    auxiliary_path = "/usr/include/HolonightFileBrowser/directory_reader.h"

    def test_upgrade_transfers_files_package_ownership(self):
        self.make_manifest()
        old = (self.build / "manifest.tsv").read_text().replace(self.module, "holonight-files")
        state = self.target / "var/lib/holonight/source-install"
        state.mkdir(parents=True)
        (state / "manifest.tsv").write_text(old)
        for relative in self.payload:
            path = self.target / relative.lstrip("/")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"previous Files provider")
        result = self.run_functions("collision_check; copy_stage")
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = (state / "manifest.tsv").read_text()
        for relative in self.payload:
            row = next(line.split("\t") for line in manifest.splitlines() if line.endswith(relative))
            self.assertEqual(row[0], self.module)
            self.assertEqual((self.target / relative.lstrip("/")).read_bytes(), self.payload[relative])

    def test_duplicate_staged_owners_are_rejected(self):
        self.make_manifest()
        (self.build / "module-paths/holonight-files").write_text("\n".join(self.payload) + "\n")
        result = self.run_functions("make_manifest")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("multiple components install", result.stderr)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_cmake_manifest_records_overwritten_staging_paths(self):
        inventory = "\n".join(sorted(self.payload)) + "\n"
        (self.build / "before").write_text(inventory)
        (self.build / "after").write_text(inventory)
        module_build = self.build / "build" / self.module
        module_build.mkdir(parents=True)
        (module_build / "install_manifest.txt").write_text(inventory)
        result = self.run_functions(
            f'record_module_paths {self.module} "$BUILD_ROOT/before" "$BUILD_ROOT/after"'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.build / "module-paths" / self.module).read_text(), inventory)
