"""Keep installed providers ahead of the applications that consume them."""

import configparser
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from install_catalog import CATALOG


class InstallOrder(unittest.TestCase):
    def test_every_submodule_is_installed_exactly_once(self):
        config = configparser.ConfigParser()
        config.read(ROOT / ".gitmodules")
        self.assertCountEqual(list(CATALOG), [config[section]["path"] for section in config.sections()])

    def test_all_dependency_edges_precede_consumers(self):
        order = list(CATALOG)
        for consumer, component in CATALOG.items():
            for provider in component.dependencies:
                self.assertLess(order.index(provider), order.index(consumer))

    def test_system_services_provider_precedes_qt(self):
        order = list(CATALOG)
        self.assertLess(order.index("holonight-system-services"), order.index("holonight-qt"))

    def test_search_provider_precedes_files(self):
        order = list(CATALOG)
        self.assertLess(order.index("holonight-search"), order.index("holonight-files"))

    def test_thumbnail_provider_precedes_consumers(self):
        order = list(CATALOG)
        provider = order.index("holonight-thumbnails")
        self.assertLess(order.index("holonight-images"), provider)
        self.assertLess(provider, order.index("holonight-files"))
        self.assertLess(provider, order.index("holonight-viewer"))

    def test_filechooser_backend_follows_installed_providers(self):
        order = list(CATALOG)
        backend = order.index("xdg-desktop-portal-holonight")
        for provider in ("holonight-qt", "holonight-search", "holonight-file-browser"):
            self.assertLess(order.index(provider), backend)
