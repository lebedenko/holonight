"""Keep installed providers ahead of the applications that consume them."""

from pathlib import Path
import re
import unittest


INSTALLER = Path(__file__).resolve().parents[1] / "scripts/install.sh"


class InstallOrder(unittest.TestCase):
    def test_search_provider_precedes_files(self):
        script = INSTALLER.read_text()
        modules = re.search(r"^readonly MODULES=\(([^)]*)\)$", script, re.MULTILINE)
        self.assertIsNotNone(modules)
        order = modules.group(1).split()
        self.assertLess(order.index("holonight-search"), order.index("holonight-files"))

    def test_thumbnail_provider_precedes_consumers(self):
        script = INSTALLER.read_text()
        modules = re.search(r"^readonly MODULES=\(([^)]*)\)$", script, re.MULTILINE)
        self.assertIsNotNone(modules)
        order = modules.group(1).split()
        provider = order.index("holonight-thumbnails")
        self.assertLess(order.index("holonight-images"), provider)
        self.assertLess(provider, order.index("holonight-files"))
        self.assertLess(provider, order.index("holonight-viewer"))
