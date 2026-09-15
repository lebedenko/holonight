#!/usr/bin/env python3
"""Bounded headless startup/mapping comparison; no pointer, focus, or key automation."""
import argparse
import importlib.util
import json
import os
import signal
from pathlib import Path
import subprocess
import tempfile
import time


def stop(process):
    if process.poll() is None:
        process.terminate()
    try:
        return process.wait(timeout=5), False
    except subprocess.TimeoutExpired:
        process.kill()
        return process.wait(), True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kit', type=Path)
    parser.add_argument('logs', type=Path)
    args = parser.parse_args()
    kit = args.kit.resolve()
    prefix = kit / 'prefix'
    args.logs.mkdir(parents=True, exist_ok=True)
    args.logs = Path(tempfile.mkdtemp(prefix='attempt-', dir=args.logs))
    failures = []
    spec = importlib.util.spec_from_file_location('guided', kit / 'guided-app.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    with tempfile.TemporaryDirectory(prefix='u211-') as directory:
        root = Path(directory)
        runtime = root / 'runtime'
        runtime.mkdir(mode=0o700)
        env = dict(os.environ, XDG_RUNTIME_DIR=str(runtime), WLR_BACKENDS='headless',
                   WLR_RENDERER='pixman', WLR_LIBINPUT_NO_DEVICES='1')
        for key in ('DISPLAY', 'WAYLAND_DISPLAY', 'SWAYSOCK', 'HYPRLAND_INSTANCE_SIGNATURE',
                    'LD_PRELOAD', 'HOLONIGHT_RENDER_DIAGNOSTICS', 'HOLONIGHT_PALETTE_DIAGNOSTICS',
                    'HOLONIGHT_SESSION_DIAGNOSTICS', 'HOLONIGHT_SESSION_GEOMETRY'):
            env.pop(key, None)
        config = root / 'sway.conf'
        config.write_text('output HEADLESS-1 mode 1920x1080 scale 1\n')
        with (args.logs / 'sway.log').open('w') as log:
            compositor = subprocess.Popen(['sway', '--config', str(config)], env=env, stdout=log, stderr=subprocess.STDOUT)
            try:
                sockets = []
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    sockets = [path for path in runtime.glob('wayland-*') if path.is_socket()]
                    if sockets:
                        break
                    assert compositor.poll() is None, 'headless Sway failed'
                    time.sleep(.1)
                assert sockets, 'no Wayland socket'
                env.update(WAYLAND_DISPLAY=sockets[0].name, QT_QPA_PLATFORM='wayland', QT_QUICK_BACKEND='software',
                           LD_LIBRARY_PATH=str(prefix / 'lib'), QML_IMPORT_PATH=str(prefix / 'lib/qt6/qml'),
                           QT_PLUGIN_PATH=str(prefix / 'lib/qt6/plugins'), QT_QPA_PLATFORMTHEME='holonight',
                           QT_LOGGING_RULES='*.debug=false;*.info=true')
                for style in ('Holonight', 'Fusion'):
                    for scale in ('1', '1.25'):
                        for application, executable in (('shell', 'holonight-shell'), ('ai', 'holonight-chat')):
                            for observed in (True, False):
                                case = args.logs / f'{application}-{style}-{scale}-{observed}'
                                case.mkdir()
                                run_env = dict(env, QT_QUICK_CONTROLS_STYLE=style, QT_SCALE_FACTOR=scale,
                                               HOLONIGHT_APPEARANCE_FILE=str(case / 'appearance.toml'))
                                for key in ('XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME', 'XDG_CONFIG_DIRS'):
                                    path = case / key.lower()
                                    path.mkdir(mode=0o700)
                                    run_env[key] = str(path.resolve())
                                ai_config = Path(run_env['XDG_CONFIG_HOME']) / 'holonight-ai/config.json'
                                ai_config.parent.mkdir()
                                ai_config.write_text(json.dumps({'provider_instances': {'schema_version': 1,
                                    'instances': [{'id': name, 'type': name, 'name': name, 'enabled': False, 'settings': {}}
                                                  for name in ('ollama', 'openai', 'anthropic', 'google')], 'tombstones': []},
                                    'utility': {'chat_title_generation_enabled': False}}))
                                if observed:
                                    run_env.update(LD_PRELOAD=str(prefix / 'lib/session-diagnostics.so'),
                                                   HOLONIGHT_SESSION_DIAGNOSTICS='1')
                                    if application == 'shell':
                                        run_env.update(HOLONIGHT_SESSION_GEOMETRY='1', WAYLAND_DEBUG='1')
                                command = [str(prefix / 'bin' / executable)]
                                if application == 'shell':
                                    command += ['--debug', '--no-log-file']
                                with (case / 'launch.log').open('w') as output:
                                    child = subprocess.Popen(command, env=run_env, stdout=output, stderr=subprocess.STDOUT)
                                    try:
                                        time.sleep(3)
                                        assert child.poll() is None, f'premature exit: {case}'
                                        isolated = helper.collect(child.pid, case, prefix)
                                    finally:
                                        code, forced = stop(child)
                                text = (case / 'launch.log').read_text(errors='replace')
                                result = dict(isolated=isolated, exit=code, forced=forced,
                                              outcome=('forced cleanup' if forced else
                                                       'normal' if code == 0 else
                                                       'terminated' if code == -signal.SIGTERM else 'failed'),
                                              observations=helper.session_observations(text))
                                (case / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
                                # SIGTERM is the requested bounded stop. A different
                                # signal (especially SIGSEGV) is a failed run.
                                if not (isolated and not forced and code in (0, -signal.SIGTERM)):
                                    failures.append(case.name)
                                dprs = result['observations']['session_window_dpr']
                                assert (dprs and float(scale) in dprs.values()) if observed else not dprs
                                print(case.name, code, 'isolated', flush=True)
            finally:
                stop(compositor)
    assert not failures, f'Failed staged runs: {failures}; evidence: {args.logs}'


if __name__ == '__main__':
    main()
