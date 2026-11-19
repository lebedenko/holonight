#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
python3 scripts/test-quality.py
python3 scripts/check-quality-copies.py
bash -n scripts/install.sh scripts/install-dependencies.sh scripts/uninstall.sh
mkdir -p build
python3 -m unittest discover -s tests -p 'test_*.py' -v
reuse lint
