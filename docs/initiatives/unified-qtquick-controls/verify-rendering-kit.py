#!/usr/bin/env python3
"""Check staged loading and runtime-selected origins with bounded private launches."""
import argparse
import hashlib
import importlib.util
import sys
sys.dont_write_bytecode = True
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kit', type=Path)
    parser.add_argument('--logs', type=Path, required=True)
    parser.add_argument("--diagnostics", action="store_true")
    parser.add_argument('--dropdown-only', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("render_collector", Path(__file__).with_name("guided-app.py"))
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    prefix = args.kit.resolve() / 'prefix'
    args.logs.mkdir(parents=True, exist_ok=True)
    for style in ('Holonight', 'Fusion'):
        for scale in (('1',) if args.dropdown_only else ('1', '1.25')):
            for app in (('neochat', 'tokodon', 'haruna') if args.dropdown_only else ('haruna', 'neochat', 'tokodon', 'settings', 'ai')):
                destination = args.logs / f'{app}-{style}-{scale}'
                destination.mkdir(exist_ok=True)
                binary = prefix / 'bin' / {'ai': 'holonight-chat', 'settings': 'holonight-settings'}[app] if app in ('ai', 'settings') else Path('/usr/bin') / app
                with tempfile.TemporaryDirectory(prefix='uqc207-runtime-') as temporary:
                    profile_root = Path(temporary)
                    env = dict(os.environ, HOME=temporary, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
                        QT_QPA_PLATFORMTHEME='holonight', QT_STYLE_OVERRIDE='', QT_QUICK_CONTROLS_STYLE=style,
                        QT_SCALE_FACTOR=scale, QT_FORCE_STDERR_LOGGING='1', QML_IMPORT_TRACE='1',
                        QT_LOGGING_RULES='qt.quick.viewport.debug=true',
                        QT_PLUGIN_PATH=str(prefix / 'lib/qt6/plugins'), QML_IMPORT_PATH=str(prefix / 'lib/qt6/qml'),
                        LD_LIBRARY_PATH=str(prefix / 'lib'), LD_DEBUG='libs',
                        XDG_DATA_DIRS=str(prefix / 'share') + ':/usr/share', HOLONIGHT_APPEARANCE_FILE=str(profile_root / 'appearance.toml'))
                    for key in ('XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME', 'XDG_CONFIG_DIRS'):
                        path = profile_root / key
                        path.mkdir(mode=0o700)
                        env[key] = str(path)
                    if args.diagnostics:
                        env['HOLONIGHT_RENDER_DIAGNOSTICS'] = '1'
                        env['LD_PRELOAD'] = str(prefix / 'lib/render-diagnostics.so')
                    log_path = destination / 'launch.log'
                    mappings = ''
                    premature_exit = False
                    forced_kill = False
                    started = time.monotonic()
                    with log_path.open('w') as log:
                        child = subprocess.Popen([str(binary)], env=env, stdout=log, stderr=subprocess.STDOUT)
                        try:
                            child.wait(timeout=3)
                            premature_exit = True
                        except subprocess.TimeoutExpired:
                            mappings = Path(f'/proc/{child.pid}/maps').read_text()
                        finally:
                            if child.poll() is None:
                                child.terminate()
                            try:
                                child.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                forced_kill = True
                                child.kill()
                                child.wait()
                    (destination / 'maps').write_text(mappings)
                    paths = sorted({line.split(None, 5)[5] for line in mappings.splitlines()
                                    if len(line.split(None, 5)) == 6 and '.so' in line})
                    owned = [path for path in paths if 'holonight' in Path(path).name.lower()]
                    errors = [path for path in owned if not Path(path).resolve().is_relative_to(prefix)]
                    if premature_exit:
                        errors.append('process exited before runtime inspection')
                    if forced_kill:
                        errors.append('process required killing after termination deadline')
                    required = ['libholonight_config.so']
                    if style == 'Holonight':
                        required += ['libholonight_qml.so', 'libholonight_core_qml.so']
                    if app in ('ai', 'settings'):
                        required += ['libholonight_controls_qml.so', 'libholonight_core_qml.so']
                    errors += ['missing ' + name for name in required if not any(Path(path).name == name for path in owned)]
                    text = log_path.read_text()
                    marker = 'qrc:/qt/qml/Holonight/' if style == 'Holonight' else 'qrc:/qt-project.org/imports/QtQuick/Controls/Fusion/'
                    if marker not in text:
                        errors.append('missing runtime-selected control origin')
                    result = dict(pid=child.pid, executable=str(binary), executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                        requested_style=style, requested_scale=scale, elapsed=time.monotonic()-started,
                        process_exit=child.returncode, premature_exit=premature_exit, forced_kill=forced_kill,
                        reason='early exit' if premature_exit else 'terminated after bounded inspection',
                        modules=owned, origin_marker=marker, errors=errors,
                        log_sha256=hashlib.sha256(log_path.read_bytes()).hexdigest(), **collector.render_observations(text))
                    (destination / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
                    if errors:
                        raise RuntimeError(f'{app}/{style}/{scale}: {errors}')
                    print('PASS staged loading/origins', app, style, scale, flush=True)


if __name__ == '__main__':
    main()
