#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
exec python3 "$(dirname -- "$0")/source-install.py" uninstall "$@"
