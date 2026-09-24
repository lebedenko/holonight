#!/usr/bin/env python3
"""Run the real Qt renderer against packaged themes in a disposable root."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / 'holonight-icons'


def main():
    with tempfile.TemporaryDirectory(prefix='holonight-staged-icons-') as temporary:
        destdir = Path(temporary)
        subprocess.run([sys.executable, str(ICONS / 'scripts/stage.py'), '--destdir', str(destdir)], check=True)
        themes = destdir / 'usr/share/icons'
        subprocess.run([sys.executable, str(ICONS / 'scripts/validate_icons.py'),
                        '--theme-root', str(themes)], check=True)
        # The renderer harness expects source fixtures adjacent to its theme root.
        # Expose them only in the disposable test root, outside installed payloads.
        for name in ('tests', 'metadata'):
            (themes.parent / name).symlink_to(ICONS / name, target_is_directory=True)
        subprocess.run([str(ICONS / 'build/rendering/render-check'), str(themes)], check=True,
                       env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen', 'QT_QPA_PLATFORMTHEME': ''})


if __name__ == '__main__':
    main()
