#!/usr/bin/env python3
"""Inspect four isolated staged greeter demos without desktop input."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kit', type=Path)
    parser.add_argument('logs', type=Path)
    args = parser.parse_args()
    kit = args.kit.resolve()
    prefix = kit / 'prefix'
    args.logs.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('guided', kit / 'guided-app.py')
    guided = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guided)
    for style in ('Holonight', 'Fusion'):
        for scale in ('1', '1.25'):
            case = args.logs / f'{style}-{scale}'
            case.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='uqc212-demo-') as directory:
                root = Path(directory)
                env = dict(PATH=os.defpath, LANG='C.UTF-8', HOME=str(root),
                           QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
                           QT_QPA_PLATFORMTHEME='', QT_QUICK_CONTROLS_STYLE=style,
                           QT_SCALE_FACTOR=scale, QT_FORCE_STDERR_LOGGING='1',
                           QML_IMPORT_TRACE='1', QT_DEBUG_PLUGINS='1',
                           QML_IMPORT_PATH=str(prefix / 'lib/qt6/qml'),
                           LD_LIBRARY_PATH=str(prefix / 'lib'),
                           LD_PRELOAD=str(prefix / 'lib/render-diagnostics.so'),
                           HOLONIGHT_RENDER_DIAGNOSTICS='1',
                           DBUS_SESSION_BUS_ADDRESS=f'unix:path={root}/no-bus',
                           DBUS_SYSTEM_BUS_ADDRESS=f'unix:path={root}/no-system',
                           GREETD_SOCK=str(root / 'no-greetd'))
                for key in ('XDG_CONFIG_HOME', 'XDG_CONFIG_DIRS', 'XDG_DATA_HOME',
                            'XDG_DATA_DIRS', 'XDG_STATE_HOME', 'XDG_CACHE_HOME', 'XDG_RUNTIME_DIR'):
                    path = root / key
                    path.mkdir(mode=0o700)
                    env[key] = str(path)
                command = [str(prefix / 'bin/holonight-greeter'), '--demo',
                           '--config', str(root / 'demo.toml'), '--state', str(root / 'state.json')]
                log_path = case / 'runtime.log'
                with log_path.open('w') as log:
                    process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
                    try:
                        deadline = time.monotonic() + 8
                        while time.monotonic() < deadline:
                            assert process.poll() is None, f'Premature exit: {process.returncode}'
                            observations = guided.render_observations(log_path.read_text())
                            if observations['actual_window_dpr']:
                                break
                            time.sleep(0.05)
                        assert guided.collect(process.pid, case, prefix), 'Outside-prefix module'
                        assert observations['actual_window_dpr'], 'Missing actual DPR'
                        assert all(value == float(scale) for value in observations['actual_window_dpr'].values())
                        (case / 'render.json').write_text(json.dumps(observations, indent=2) + '\n')
                    finally:
                        process.terminate()
                        try:
                            code = process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                            raise AssertionError('Forced cleanup required')
                        (case / 'outcome.json').write_text(json.dumps(dict(
                            returncode=code, outcome='terminated by verification')) + '\n')
                text = log_path.read_text()
                assert 'qml-loaded' in text
                for component in ('TextField', 'Button', 'ComboBox'):
                    assert f'/{style}/{component}.qml' in text, component
                maps = next(case.glob('pid-*.maps')).read_text()
                assert str(prefix / 'lib/qt6/qml/Holonight/Controls/libholonight_controls_qml.so') in maps
                print(f'PASS {style} {scale}: staged origins, actual DPR, mappings and reaped exit', flush=True)


if __name__ == '__main__':
    main()
