#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
bash -n scripts/install.sh scripts/install-dependencies.sh scripts/uninstall.sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
reuse lint
