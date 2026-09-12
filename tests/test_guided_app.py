"""Runtime mapping evidence must prove candidate isolation."""
import sys
sys.dont_write_bytecode = True

import importlib.util
from pathlib import Path
import unittest
import os
import signal
import subprocess
import tempfile
import time

SCRIPT = Path(__file__).resolve().parents[1] / "docs/initiatives/unified-qtquick-controls/guided-app.py"
spec = importlib.util.spec_from_file_location("guided_app", SCRIPT)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class RuntimeIsolation(unittest.TestCase):
    prefix = Path("/tmp/candidate")

    def evidence(self, style="Holonight", path="/tmp/candidate/lib"):
        return {"environment": {"LD_LIBRARY_PATH": path, "QT_QUICK_CONTROLS_STYLE": style}}

    def mappings(self):
        return ["0-1 r-xp 0 00:00 1 " + str(self.prefix / name) for name in (
            "lib/libholonight_config.so", "lib/qt6/qml/Holonight/Core/libholonight_core_qml.so",
            "lib/qt6/qml/Holonight/libholonight_qml.so")]

    def test_staged_paths_and_runtime_mappings_are_required(self):
        result = app.assess_isolation(self.evidence(), self.mappings(), self.prefix)
        self.assertEqual(result["status"], "verified")
        self.assertEqual(app.assess_isolation(self.evidence(), [], self.prefix)["status"], "incomplete")
        self.assertEqual(app.assess_isolation(self.evidence(path=None), self.mappings(), self.prefix)["status"],
                         "incomplete")

    def test_host_fallback_is_incomplete_even_with_staged_modules(self):
        maps = self.mappings() + ["0-1 r-xp 0 00:00 1 /usr/lib/libholonight_config.so"]
        self.assertEqual(app.assess_isolation(self.evidence(), maps, self.prefix)["status"], "incomplete")

    def test_similar_prefix_is_not_the_candidate(self):
        maps = [line.replace("/tmp/candidate/", "/tmp/candidate-old/") for line in self.mappings()]
        self.assertEqual(app.assess_isolation(self.evidence(), maps, self.prefix)["status"], "incomplete")

    def test_fusion_requires_core_and_config_but_not_holonight_style(self):
        self.assertEqual(app.assess_isolation(self.evidence("Fusion"), self.mappings()[:2], self.prefix)["status"],
                         "verified")
        self.assertEqual(app.assess_isolation(self.evidence("Fusion"), self.mappings()[1:2], self.prefix)["status"],
                         "incomplete")


class LauncherSupervisor(unittest.TestCase):
    def test_interrupt_allows_the_helper_to_finish_evidence(self):
        with tempfile.TemporaryDirectory(prefix="uqc-supervisor-") as directory:
            kit = Path(directory)
            launcher = Path(os.environ.get("UQC_LAUNCHER_HELPER", SCRIPT.with_name("launcher-test.py")))
            (kit / "launcher-test.py").write_bytes(launcher.read_bytes())
            (kit / "READY").write_text("test fixture")
            (kit / "guided-app.py").write_text(
                "import os, signal, sys, time\n"
                "from pathlib import Path\n"
                "kit = Path(__file__).parent\n"
                "def finish(*args):\n"
                "    (kit / 'finished').write_text('evidence saved')\n"
                "    sys.exit(0)\n"
                "signal.signal(signal.SIGINT, finish)\n"
                "(kit / 'started').write_text(str(os.getpid()))\n"
                "while True: time.sleep(0.05)\n")
            process = subprocess.Popen([sys.executable, str(kit / "launcher-test.py"), "run"],
                                       env=dict(os.environ, UQC_KIT=str(kit)),
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                deadline = time.monotonic() + 3
                while not (kit / "started").exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue((kit / "started").exists())
                process.send_signal(signal.SIGINT)
                process.wait(timeout=3)
                self.assertTrue((kit / "finished").exists(), "interrupt lost evidence finalization")
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=3)


if __name__ == "__main__":
    unittest.main()
