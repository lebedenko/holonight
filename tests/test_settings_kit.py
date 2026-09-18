"""A Settings release needs fresh suites and an unchanged preparation inventory."""
import importlib.util
from pathlib import Path
import unittest
import hashlib
import subprocess
import tarfile
import tempfile

spec = importlib.util.spec_from_file_location("policy", Path(__file__).resolve().parents[1] /
    "docs/initiatives/unified-qtquick-controls/p03-kit/settings-policy.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class ReleaseRequirements(unittest.TestCase):
    def setUp(self):
        self.build = {f"{c}-{p}": {"code": 0} for c in policy.COMPONENTS
                      for p in ("configure", "build", "install")}
        self.checks = {name: {"code": 0} for name in policy.GATES}

    def test_complete_fresh_evidence_passes(self):
        policy.validate(self.build, self.checks, "qt 6.11\n", "qt 6.11\n")

    def test_inventory_drift_rejected_even_with_passing_suites(self):
        for current in ("qt 6.12\n", "qt 6.11\nnew-package 1\n", ""):
            with self.subTest(current=current), self.assertRaisesRegex(ValueError, "Package drift"):
                policy.validate(self.build, self.checks, "qt 6.11\n", current)

    def test_missing_and_failed_gates_block_release(self):
        for results in (self.build, self.checks):
            for name in tuple(results):
                with self.subTest(gate=name):
                    saved = results.pop(name)
                    with self.assertRaisesRegex(ValueError, name):
                        policy.validate(self.build, self.checks, "inventory", "inventory")
                    results[name] = {"code": 1}
                    with self.assertRaisesRegex(ValueError, name):
                        policy.validate(self.build, self.checks, "inventory", "inventory")
                    results[name] = saved

    def test_prior_or_focused_results_cannot_replace_full_suites(self):
        self.checks.pop("settings-full")
        self.checks["prior-settings-full"] = {"code": 0}
        with self.assertRaisesRegex(ValueError, "settings-full"):
            policy.validate(self.build, self.checks, "inventory", "inventory")


class AiReleaseRequirements(ReleaseRequirements):
    def setUp(self):
        self.build = {f"{c}-{p}": {"code": 0} for c in policy.AI_COMPONENTS
                      for p in ("configure", "build", "install")}
        self.checks = {name: {"code": 0} for name in policy.AI_GATES}

    def test_complete_fresh_evidence_passes(self):
        policy.validate(self.build, self.checks, "inventory", "inventory", "ai-scale1")

    def test_inventory_drift_rejected_even_with_passing_suites(self):
        with self.assertRaisesRegex(ValueError, "Package drift"):
            policy.validate(self.build, self.checks, "before", "after", "ai-scale1")

    def test_missing_and_failed_gates_block_release(self):
        for results in (self.build, self.checks):
            for name in tuple(results):
                with self.subTest(gate=name):
                    saved = results.pop(name)
                    with self.assertRaisesRegex(ValueError, name):
                        policy.validate(self.build, self.checks, "same", "same", "ai-scale1")
                    results[name] = {"code": 1}
                    with self.assertRaisesRegex(ValueError, name):
                        policy.validate(self.build, self.checks, "same", "same", "ai-scale1")
                    results[name] = saved

    def test_prior_or_focused_results_cannot_replace_full_suites(self):
        self.checks.pop("ai-full")
        self.checks["prior-ai-full"] = {"code": 0}
        with self.assertRaisesRegex(ValueError, "ai-full"):
            policy.validate(self.build, self.checks, "same", "same", "ai-scale1")

    def test_settings_evidence_cannot_release_ai(self):
        with self.assertRaises(ValueError):
            policy.validate(self.build, {name: {"code": 0} for name in policy.GATES},
                            "same", "same", "ai-scale1")


class AiRestoration(unittest.TestCase):
    def test_exact_prefix_hashes_and_overwrite_refusal(self):
        with tempfile.TemporaryDirectory(prefix="holonight-uqc201-ai-", dir="/tmp") as directory:
            kit = Path(directory)
            # TemporaryDirectory still owns this path after the restorer recreates it.
            kit.rmdir()
            with tempfile.TemporaryDirectory() as staging:
                source = Path(staging) / kit.name
                source.mkdir()
                payload = b"immutable payload\n"
                (source / "sample").write_bytes(payload)
                (source / "SHA256SUMS").write_text(hashlib.sha256(payload).hexdigest() + "  sample\n")
                (source / "READY").write_text("test release\n")
                archive = Path(staging) / (kit.name + ".tar.gz")
                with tarfile.open(archive, "w:gz") as saved:
                    saved.add(source, arcname=kit.name)
                command = ["python3", str(Path(__file__).resolve().parents[1] /
                    "docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py"), str(archive)]
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("guided-session.py sway", result.stdout)
                self.assertEqual((kit / "sample").read_bytes(), payload)
                self.assertTrue((kit / "READY").is_file())
                refused = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(refused.returncode, 2)
                self.assertIn("preserving existing", refused.stderr)
                self.assertEqual((kit / "sample").read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
