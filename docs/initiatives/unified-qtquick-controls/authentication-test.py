#!/usr/bin/env python3
"""User-operated Batch 2 authentication checkpoint; never manages existing agents."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

from session_identity import identity, output
from registration import registration_reply
from bounded_challenge import run_challenge

KIT = Path(__file__).resolve().parent


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def compatible():
    if not (KIT / 'READY').is_file():
        raise SystemExit('STOP: kit is not READY.')
    inventory = (KIT / 'PROVIDER.txt').read_text().splitlines()
    for package in ('qt6-base', 'qt6-declarative', 'hyprpolkitagent', 'hyprland'):
        if output('pacman', '-Q', package) not in inventory:
            raise SystemExit('STOP: package changed: ' + package)
    for line in (KIT / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = KIT / name
        if not path.resolve().is_relative_to(KIT) or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit('STOP: checksum mismatch: ' + name)


def new_run(base, sid, kind, style, scale):
    base.mkdir(mode=0o700, exist_ok=True)
    index = base / ('session-' + sid + '.jsonl')
    with index.open('a+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        records = [json.loads(line) for line in stream if line.strip()]
        number = len(records) + 1
        run = base / f'{sid}-{number:03}-{kind}-{style}-{scale}'
        run.mkdir(mode=0o700)
        record = dict(run=str(run), session=sid, kind=kind, style=style, scale=scale,
                      kit=str(KIT), date=datetime.datetime.now(datetime.timezone.utc).isoformat())
        stream.write(json.dumps(record) + '\n')
        stream.flush()
    return run, record


def latest_run(base, sid, style, scale):
    index = base / ('session-' + sid + '.jsonl')
    records = [json.loads(line) for line in index.read_text().splitlines()]
    matches = [record for record in records if record['kind'] == 'polkit'
               and record['style'] == style and record['scale'] == scale and record['kit'] == str(KIT)]
    if not matches:
        raise SystemExit('STOP: start the matching Polkit agent first.')
    run = Path(matches[-1]['run'])
    if run.parent != base or (run / 'session-id').read_text().strip() != sid:
        raise SystemExit('STOP: evidence session mismatch.')
    return run


def preflight(run, details):
    (run / 'identity.txt').write_text(details + '\n')
    commands = {
        'processes': ['ps', '-eo', 'uid,pid,ppid,cgroup,comm'],
        'user-services': ['systemctl', '--user', 'list-units', '--type=service', '--all', '--no-pager'],
        'registration-before': ['journalctl', '-b', '-u', 'polkit.service', '--no-pager'],
        'policy': ['pkaction', '--action-id', 'org.freedesktop.policykit.exec', '--verbose'],
        'outputs': ['hyprctl', 'monitors', '-j'],
    }
    for name, command in commands.items():
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15)
        (run / (name + '.txt')).write_text(result.stdout + '\ncommand_exit=' + str(result.returncode) + '\n')
    monitors = json.loads((run / 'outputs.txt').read_text().split('\ncommand_exit=')[0])
    if not monitors or any(monitor['scale'] != 1 for monitor in monitors):
        raise SystemExit('STOP: checkpoint requires output scale 1.')


def runtime_environment(run, style, scale):
    env = os.environ.copy()
    for key in ('QML2_IMPORT_PATH', 'QT_QUICK_CONTROLS_CONF', 'QT_QUICK_CONTROLS_FALLBACK_STYLE',
                'QT_QUICK_BACKEND', 'QT_SCALE_FACTOR_ROUNDING_POLICY', 'QT_SCREEN_SCALE_FACTORS'):
        env.pop(key, None)
    prefix = KIT / 'prefix'
    for key in ('XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME'):
        path = run / key.lower()
        path.mkdir(mode=0o700)
        env[key] = str(path)
    env.update(QT_QPA_PLATFORM='wayland', QT_QPA_PLATFORMTHEME='holonight',
               QT_QUICK_CONTROLS_STYLE=style, QT_SCALE_FACTOR=scale,
               QML_IMPORT_PATH=str(prefix / 'lib/qt6/qml'), QT_PLUGIN_PATH=str(prefix / 'lib/qt6/plugins'),
               LD_LIBRARY_PATH=str(prefix / 'lib'), LD_DEBUG='libs', QML_IMPORT_TRACE='1', QT_DEBUG_PLUGINS='1',
               QT_FORCE_STDERR_LOGGING='1', QT_LOGGING_RULES='*.debug=true;*.info=true', G_DBUS_DEBUG='message')
    return env


def verify_registration(run, sid):
    metadata = json.loads((run / 'process.json').read_text())
    if 'exit_status' in metadata:
        raise SystemExit('STOP: agent already exited.')
    ticks = Path('/proc', str(metadata['pid']), 'stat').read_text().rsplit(')', 1)[1].split()[19]
    if ticks != metadata['start_ticks']:
        raise SystemExit('STOP: recorded PID was reused.')
    registration = registration_reply((run / 'process.log').read_text(), sid)
    owner = output('busctl', '--system', 'call', 'org.freedesktop.DBus', '/org/freedesktop/DBus',
                   'org.freedesktop.DBus', 'GetNameOwner', 's', 'org.freedesktop.PolicyKit1').split('"')[1]
    pid = int(output('busctl', '--system', 'call', 'org.freedesktop.DBus', '/org/freedesktop/DBus',
                     'org.freedesktop.DBus', 'GetConnectionUnixProcessID', 's', registration['agent_bus']).split()[1])
    obj = output('busctl', '--system', 'call', 'org.freedesktop.login1', '/org/freedesktop/login1',
                 'org.freedesktop.login1.Manager', 'GetSessionByPID', 'u', str(pid)).split('"')[1]
    agent_sid = output('busctl', '--system', 'get-property', 'org.freedesktop.login1', obj,
                       'org.freedesktop.login1.Session', 'Id').split('"')[1]
    if owner != registration['authority'] or pid != metadata['pid'] or agent_sid != sid:
        raise SystemExit('STOP: authority/PID/session mismatch.')
    write_json(run / 'registration.json', registration)


def runtime_evidence(run, metadata):
    text = (run / 'process.log').read_text(errors='replace')
    modules = sorted(set(re.findall(r'calling init:\s+(/[^\n]+)', text)))
    owned = [path.strip() for path in modules if 'holonight' in Path(path.strip()).name.lower()]
    styles = re.findall(r'phase=selection configured=\s*"?([A-Za-z]+)', text)
    ratios = re.findall(r'phase=window devicePixelRatio=\s*([0-9.]+)', text)
    evidence = dict(actual_device_pixel_ratios=ratios, pid=metadata['pid'], requested_style=metadata['style'], requested_scale=metadata['scale'],
                    actual_styles=sorted(set(styles)), loaded_modules=owned,
                    mapping_source='PID-tagged dynamic loader initialization records; process is non-dumpable',
                    implementation=[line for line in text.splitlines() if 'phase=implementation' in line])
    required = {'libholonight_config.so', 'libholonight_core_qml.so', 'libholonight_controls_qml.so'}
    required.add('libholonight_qml.so' if metadata['style'] == 'Holonight' else 'libqtquickcontrols2fusionstyleplugin.so')
    evidence['missing_modules'] = sorted(required - {Path(path.strip()).name for path in modules})
    evidence['verified'] = (not evidence['missing_modules'] and ratios == [metadata['scale']] and set(styles) == {metadata['style']}
                            and all(Path(path).is_relative_to(KIT / 'prefix') for path in owned))
    write_json(run / 'runtime.json', evidence)


def stop_child(proc):
    proc.terminate()
    try:
        return proc.wait(timeout=5), 'terminated'
    except subprocess.TimeoutExpired:
        proc.kill()
        return proc.wait(), 'forced-kill'


def launch(run, metadata, env):
    kind = metadata['kind']
    executable = KIT / 'prefix' / ('libexec/holonight-polkit-agent' if kind == 'polkit'
                                  else 'bin/holonight-sudo-askpass')
    command = [str(executable)] + ([] if kind == 'polkit' else ['Batch 2 border inspection — cancel without credentials'])
    metadata.update(executable=str(executable), sha256=hashlib.sha256(executable.read_bytes()).hexdigest())
    with (run / 'process.log').open('w') as log:
        proc = subprocess.Popen(command, env=env, stdout=log if kind == 'polkit' else subprocess.PIPE, stderr=log, start_new_session=True)
        try:
            metadata['pid'] = proc.pid
            metadata['start_ticks'] = Path('/proc', str(proc.pid), 'stat').read_text().rsplit(')', 1)[1].split()[19]
            write_json(run / 'process.json', metadata)
            if kind == 'polkit':
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    if proc.poll() is not None:
                        raise RuntimeError('Agent exited before registration; inspect process.log.')
                    try:
                        verify_registration(run, metadata['session'])
                        break
                    except ValueError:
                        time.sleep(0.1)
                else:
                    raise RuntimeError('No verified registration reply before deadline.')
                print('Exclusive registration verified. In another kit terminal run the matching challenge command.', flush=True)
                print('After cancellation, Ctrl+C here stops only this test agent.', flush=True)
            else:
                print('Inspect unfocused borders and focused ring, then Cancel. Do not enter credentials.', flush=True)
            try:
                stdout, _ = proc.communicate(timeout=900 if kind == 'polkit' else 180)
                metadata.update(exit_status=proc.returncode, outcome='signal-exit' if proc.returncode < 0 else 'normal-exit',
                                stdout_bytes=len(stdout or b''))
            except (KeyboardInterrupt, subprocess.TimeoutExpired) as error:
                status, cleanup = stop_child(proc)
                metadata.update(exit_status=status, outcome='interrupted' if isinstance(error, KeyboardInterrupt) else 'timeout',
                                cleanup=cleanup)
        finally:
            if proc.poll() is None:
                status, cleanup = stop_child(proc)
                metadata.update(exit_status=status, outcome='launch-error', cleanup=cleanup)
            elif 'exit_status' not in metadata:
                metadata.update(exit_status=proc.returncode, outcome='launch-error')
            write_json(run / 'process.json', metadata)
            runtime_evidence(run, metadata)
    print('Recorded:', run, metadata['outcome'], metadata['exit_status'], flush=True)
    if kind == 'askpass':
        return int(metadata['outcome'] != 'normal-exit' or metadata['exit_status'] != 1
                   or metadata.get('stdout_bytes') != 0)
    return int(metadata['outcome'] not in ('normal-exit', 'interrupted') or metadata.get('cleanup') == 'forced-kill')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=('polkit', 'challenge', 'askpass'))
    parser.add_argument('--style', choices=('Holonight', 'Fusion'), default='Holonight')
    parser.add_argument('--scale', choices=('1', '1.25'), default='1.25')
    args = parser.parse_args()
    sid, details = identity()
    compatible()
    if os.environ.get('UQC_KIT') != str(KIT) or os.environ.get('XDG_CURRENT_DESKTOP') != 'Hyprland':
        raise SystemExit('STOP: use this kit’s fresh tux Hyprland session.')
    base = Path.home() / 'uqc-auth-evidence'
    if args.step == 'challenge':
        run = latest_run(base, sid, args.style, args.scale)
        if (run / 'challenge.txt').exists():
            raise SystemExit('STOP: preserve this challenge; start a fresh agent run for another attempt.')
        verify_registration(run, sid)
        print('Cancel the graphical prompt without credentials. Evidence:', run, flush=True)
        return run_challenge(run)
    run, metadata = new_run(base, sid, args.step, args.style, args.scale)
    (run / 'session-id').write_text(sid)
    preflight(run, details)
    print('Evidence:', run, '\nReview processes, user-services and registration-before files.', flush=True)
    if args.step == 'polkit' and input('Type ISOLATED after checking that no competing agent serves this login: ') != 'ISOLATED':
        raise SystemExit('Stopped without launching an agent.')
    return launch(run, metadata, runtime_environment(run, args.style, args.scale))


if __name__ == '__main__':
    raise SystemExit(main())
