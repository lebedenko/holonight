#!/usr/bin/env python3
"""Build/run the reduced F05 lifecycle; --verify uses private headless Sway with no input."""
import argparse
import json
import os
import runpy
from pathlib import Path
import subprocess
import tempfile
import time


def build(source, work):
    flags = subprocess.check_output(['pkg-config', '--cflags', '--libs', 'Qt6Quick', 'Qt6Qml'], text=True).split()
    protocols = subprocess.check_output(['pkg-config', '--variable=pkgdatadir', 'wayland-protocols'], text=True).strip()
    subprocess.run(['wayland-scanner', 'client-header', f'{protocols}/stable/xdg-shell/xdg-shell.xml',
                    str(work / 'xdg-shell-client-protocol.h')], check=True)
    for name, target, extra in [('main.cpp', 'fixture', []),
                                ('observer.cpp', 'observer.so', ['-shared', '-I' + str(work), '-lwayland-client', '-ldl'])]:
        subprocess.run(['g++', '-std=c++23', '-fPIC', str(source / name), '-o', str(work / target), *flags, *extra], check=True)


def run_case(work, prefix, mode, env, smoke):
    case = work / mode
    case.mkdir()
    launch_env = dict(env)
    for name in ('LD_PRELOAD', 'QT_PLUGIN_PATH', 'QML_IMPORT_PATH', 'QML2_IMPORT_PATH',
                 'QT_QUICK_CONTROLS_CONF', 'QT_SCREEN_SCALE_FACTORS', 'WAYLAND_DEBUG', 'QT_LOGGING_RULES'):
        launch_env.pop(name, None)
    for name in ('XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME'):
        path = case / name
        path.mkdir()
        launch_env[name] = str(path)
    launch_env.update(QT_QPA_PLATFORM='wayland', QT_QUICK_CONTROLS_STYLE='Fusion', QT_SCALE_FACTOR='1.25',
                      QT_QPA_PLATFORMTHEME='holonight' if mode == 'theme' else '',
                      QT_PLUGIN_PATH=str(prefix / 'lib/qt6/plugins'),
                      QML_IMPORT_PATH=str(prefix / 'lib/qt6/qml'), LD_LIBRARY_PATH=str(prefix / 'lib'),
                      LD_PRELOAD=str(work / 'observer.so'))
    command = [str(work / 'fixture'), *(['--hn'] if mode == 'hn' else []), *(['--smoke'] if smoke else [])]
    with (case / 'events.log').open('w') as log:
        process = subprocess.Popen(command, env=launch_env, stdout=log, stderr=subprocess.STDOUT)
        maps = ''
        try:
            deadline = time.monotonic() + 5
            while process.poll() is None and time.monotonic() < deadline:
                maps = Path(f'/proc/{process.pid}/maps').read_text()
                if 'libQt6QuickControls2FusionStyle' in maps or time.monotonic() > deadline - 4:
                    break
                time.sleep(.05)
            (case / 'mappings.txt').write_text(maps)
            # Check loaded libraries/QML paths, not project-directory names.
            mapped = [line.split()[-1] for line in maps.splitlines() if len(line.split()) >= 6]
            hn = [p for p in mapped if 'holonight' in Path(p).name.lower() or '/qml/Holonight/' in p]
            if any(not p.startswith(str(prefix) + '/') for p in hn):
                raise RuntimeError(f'provider mapping escaped prefix: {hn}')
            if not any('/Fusion/' in p for p in mapped):
                raise RuntimeError('Fusion style plugin was not mapped')
            if mode == 'plain' and hn:
                raise RuntimeError(f'plain Qt loaded HoloNight: {hn}')
            if mode == 'theme' and not any('/platformthemes/' in p for p in hn):
                raise RuntimeError('HoloNight platform theme was not mapped')
            if mode == 'hn' and not hn:
                raise RuntimeError('HnApplicationWindow did not map its provider')
            if smoke:
                result = process.wait(timeout=10)
            else:
                print(f'{mode}: mappings verified; perform the reduced check, then use Quit fixture. Logs: {case}', flush=True)
                result = process.wait()
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    (case / 'outcome.json').write_text(json.dumps({'exit': result, 'pid': process.pid, 'mode': mode,
                                                 'command': command, 'holonightMappings': hn}, indent=2))
    if result != 0:
        raise RuntimeError(f'{mode}: process exit {result}')
    records = [json.loads(line.split('F05 ', 1)[1]) for line in (case / 'events.log').read_text().splitlines() if line.startswith('F05 ')]
    if smoke:
        windows = [r for r in records if r['kind'] == 'window']
        assert {'workspace', 'settings'} <= {r['name'] for r in windows}
        assert all(r['dpr'] == 1.25 for r in windows)
        assert any(r['kind'] == 'toplevel-configure' for r in records), 'toplevel observation missing'
        assert any(r['kind'] == 'seat-capabilities' for r in records), 'seat observation missing'
        assert any(r['framesSwapped'] > 0 for r in windows), 'no frameSwapped observations'
    print(f'{mode}: normal exit, mappings and metadata verified', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', required=True, type=Path)
    parser.add_argument('--mode', choices=['plain', 'theme', 'hn'], default='plain')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    work = Path(tempfile.mkdtemp(prefix='f05-reduced-'))
    print(f'F05 work: {work}', flush=True)
    build(Path(__file__).resolve().parent, work)
    env = dict(os.environ)
    if args.verify:
        # Reuse the established delivery/acceptance fixture, including an unrelated
        # key carrying text that must never appear in observer output.
        source = runpy.run_path(str(Path(__file__).resolve().parent.parent / 'verify-session-observer.py'))['SOURCE']
        privacy_source = work / 'privacy.cpp'
        privacy_source.write_text(source)
        flags = subprocess.check_output(['pkg-config', '--cflags', '--libs', 'Qt6Quick'], text=True).split()
        subprocess.run(['g++', '-std=c++23', '-fPIC', str(privacy_source), '-o', str(work / 'privacy'), *flags], check=True)
        result = subprocess.run([str(work / 'privacy')], env=dict(env, QT_QPA_PLATFORM='offscreen',
            QT_QPA_PLATFORMTHEME='', QT_QUICK_BACKEND='software', LD_PRELOAD=str(work / 'observer.so')),
            capture_output=True, text=True, timeout=10)
        output = result.stdout + result.stderr
        (work / 'privacy.log').write_text(output)
        assert result.returncode == 0 and 'OBSERVER_FIXTURE_OK' in output
        assert 'DO_NOT_RECORD_FORM_TEXT' not in output
        records = [json.loads(line[4:]) for line in output.splitlines() if line.startswith('F05 ')]
        assert [r['key'] for r in records if r['kind'] == 'navigation'] == ['Tab', 'Backtab']
        print('Navigation forwarding/acceptance and text exclusion: pass', flush=True)
    if not args.verify:
        run_case(work, args.prefix.resolve(), args.mode, env, False)
        return
    runtime = work / 'runtime'
    runtime.mkdir(mode=0o700)
    env.update(XDG_RUNTIME_DIR=str(runtime), WLR_BACKENDS='headless', WLR_RENDERER='pixman',
               WLR_LIBINPUT_NO_DEVICES='1', QT_QUICK_BACKEND='software')
    for name in ('DISPLAY', 'WAYLAND_DISPLAY', 'SWAYSOCK', 'HYPRLAND_INSTANCE_SIGNATURE'):
        env.pop(name, None)
    config = work / 'sway.conf'
    config.write_text('output HEADLESS-1 mode 1920x1080 scale 1\n')
    with (work / 'sway.log').open('w') as log:
        compositor = subprocess.Popen(['sway', '--config', str(config)], env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            sockets = []
            for _ in range(100):
                sockets = [p for p in runtime.glob('wayland-*') if p.is_socket()]
                if sockets or compositor.poll() is not None:
                    break
                time.sleep(.05)
            assert sockets, 'private compositor did not start'
            env['WAYLAND_DISPLAY'] = sockets[0].name
            for mode in ('plain', 'theme', 'hn'):
                run_case(work, args.prefix.resolve(), mode, env, True)
        finally:
            compositor.terminate()
            try:
                compositor.wait(timeout=5)
            except subprocess.TimeoutExpired:
                compositor.kill()
                compositor.wait()


if __name__ == '__main__':
    main()
