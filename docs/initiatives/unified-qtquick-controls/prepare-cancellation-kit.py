#!/usr/bin/env python3
"""Prepare A03-only helpers in a fresh staged prefix; verify before adding READY."""
import argparse
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kit', type=Path)
    args = parser.parse_args()
    kit = args.kit.resolve()
    if kit.parent != Path('/tmp') or not kit.name.startswith('holonight-uqc205-'):
        parser.error('expected a fresh /tmp/holonight-uqc205-* directory')
    if (kit / 'READY').exists() or (kit / 'owned-auth').exists():
        parser.error('preserve existing kits; prepare a fresh directory')
    docs = Path(__file__).resolve().parent
    root = docs.parents[2]
    source = root / 'holonight-qt/docs/sdd/unified-qtquick-controls/audit/auth-test'
    owned = kit / 'owned-auth'
    owned.mkdir(parents=True)
    kit.chmod(0o755)
    for name in ('auth-test.py', 'registration.py'):
        shutil.copy2(source / name, owned / name)
    subprocess.run(['patch', '--batch', '--fuzz=0', '-p0', '-i', str(docs / 'owned-auth.patch')],
                   cwd=owned, check=True)
    helper = owned / 'auth-test.py'
    text = helper.read_text().replace('from registration import registration_reply',
                                      'from registration import registration_reply\nfrom bounded_challenge import run_challenge')
    text = text.replace("        if output('pacman', '-Q', 'hyprpolkitagent') != 'hyprpolkitagent 0.1.3-10':\n"
                        "            raise SystemExit('STOP: agent version changed; review toolkit/contract first.')\n", '')
    text = text.replace("'QT_QPA_PLATFORM', 'QT_QUICK_BACKEND']:",
                        "'QT_QPA_PLATFORM', 'QT_QUICK_BACKEND', 'QT_QUICK_CONTROLS_STYLE', 'QT_SCALE_FACTOR']:")
    text = text.replace("env.update(QT_QPA_PLATFORM='wayland',", "env.update(QT_SCALE_FACTOR='1.25', QT_QPA_PLATFORM='wayland',")
    text = text.replace('metadata = dict(session=sid,', "metadata = dict(requested_style='default', requested_scale='1.25', session=sid,")
    marker = "        result = subprocess.run(['pkexec', '--disable-internal-agent', '/usr/bin/true'],"
    if text.count(marker) != 1:
        raise SystemExit('challenge helper changed; review before preparing')
    text = text[:text.index(marker)] + '        raise SystemExit(run_challenge(run))\n'
    helper.write_text(text)
    shutil.copy2(root / 'holonight-shell/docs/sdd/unified-qtquick-controls/fixtures/bounded_challenge.py', owned)
    shutil.copy2(docs / 'guided-session.py', kit)
    shutil.copy2(source / 'terminal.sh', kit)
    terminal = f'/bin/sh {kit}/terminal.sh'
    (kit / 'sway.conf').write_text(
        f'set $mod Mod4\noutput * scale 1\nexec {terminal}\n'
        f'bindsym $mod+Return exec {terminal}\n'
        'bindsym $mod+Shift+e exit\nbindsym $mod+q kill\n')
    versions = subprocess.check_output(['pacman', '-Q', 'qt6-base', 'qt6-declarative', 'hyprpolkitagent'], text=True)
    pins = subprocess.check_output(['git', 'submodule', 'status'], cwd=root, text=True)
    (kit / 'PROVIDER.txt').write_text(versions + pins)
    shutil.copy2(docs / 'CANCELLATION.md', kit / 'README.md')
    print('Helpers prepared, awaiting installed verification:', kit)


if __name__ == '__main__':
    main()
