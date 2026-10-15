#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
python3 scripts/build-ecosystem.py --tests --prefix /work/integration-prefix
