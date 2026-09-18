"""A Settings release needs fresh suites and an unchanged preparation inventory."""
import importlib.util
from pathlib import Path
import unittest

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


if __name__ == "__main__":
    unittest.main()
