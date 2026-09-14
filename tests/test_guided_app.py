"""Runtime mapping evidence must prove candidate isolation."""
import sys
sys.dont_write_bytecode = True

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import hashlib
import json
import os
import signal
import subprocess
import tempfile
import time

SCRIPT = Path(__file__).resolve().parents[1] / "docs/initiatives/unified-qtquick-controls/guided-app.py"
spec = importlib.util.spec_from_file_location("guided_app", SCRIPT)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class RenderingObservations(unittest.TestCase):
    def test_only_actual_window_records_establish_dpr(self):
        self.assertIsNone(app.render_observations('QT_SCALE_FACTOR=1.25')['actual_window_dpr'])
        text = '\n'.join([
            'HN_RENDER invalid',
            'HN_RENDER {"id":"window", "activeFocusItem":"button", "dpr":1.5, "phase":"state"}',
            'HN_RENDER {"id":"popup", "dpr":1.25, "phase":"state"}',
            'HN_RENDER {"id":"button", "phase":"space-before-release"}',
        ])
        self.assertEqual(app.render_observations(text),
                         {'actual_window_dpr': {'window': 1.5}, 'space_observations': 1})


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

    def test_foreign_fusion_requires_its_style_and_config_without_unused_core(self):
        evidence = dict(self.evidence("Fusion"), executable="/usr/bin/haruna")
        maps = self.mappings()[:1] + ["0-1 r-xp 0 00:00 1 /usr/lib/qt6/qml/QtQuick/Controls/Fusion/libqtquickcontrols2fusionstyleplugin.so"]
        self.assertEqual(app.assess_isolation(evidence, maps, self.prefix)["status"], "verified")
        self.assertEqual(app.assess_isolation(evidence, maps[:1], self.prefix)["status"], "incomplete")
        evidence["executable"] = "/tmp/candidate/bin/holonight-settings"
        self.assertEqual(app.assess_isolation(evidence, maps, self.prefix)["status"], "incomplete")


class LauncherSupervisor(unittest.TestCase):
    def test_batch3_index_retains_process_failure_and_log_hash(self):
        with tempfile.TemporaryDirectory(prefix="uqc-batch3-index-") as directory:
            run = Path(directory)
            child = Mock(pid=12345)
            child.poll.return_value = None
            child.wait.return_value = -6
            env = dict(UQC_SESSION_RUN=str(run), UQC_PREFIX="/tmp/candidate",
                       UQC_KIT="/tmp/kit", WAYLAND_DISPLAY="test-only",
                       QT_LOGGING_RULES="*.debug=false", HOLONIGHT_RENDER_DIAGNOSTICS="1",
                       LD_PRELOAD="/tmp/old-observer.so")
            argv = [str(SCRIPT), "haruna", "--style", "Fusion", "--scale", "1.25", "--index", "batch3"]
            with patch.dict(os.environ, env), patch.object(sys, "argv", argv), \
                    patch.object(app.os, "getuid", return_value=1001), \
                    patch.object(app.subprocess, "Popen", return_value=child), \
                    patch.object(app.time, "sleep"), patch.object(app, "collect", return_value=True):
                self.assertEqual(app.main(), -6)
                launched_env = app.subprocess.Popen.call_args.kwargs["env"]
                self.assertNotIn("LD_PRELOAD", launched_env)
                self.assertNotIn("HOLONIGHT_RENDER_DIAGNOSTICS", launched_env)
            records = [json.loads(line) for line in (run / "batch3-index.jsonl").read_text().splitlines()]
            self.assertEqual([record["status"] for record in records], ["running", "finished"])
            self.assertIsNone(records[0]["process_exit"])
            self.assertEqual(records[1]["process_exit"], -6)
            self.assertEqual(records[1]["requested_scale"], "1.25")
            self.assertEqual(records[1]["qt_logging_rules"], "*.debug=false")
            self.assertEqual(records[1]["log_sha256"], hashlib.sha256(b"").hexdigest())
            self.assertEqual(Path(records[1]["run"]).joinpath("exit.txt").read_text(), "-6\n")

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
