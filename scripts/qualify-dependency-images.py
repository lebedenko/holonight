#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run read-only image prerequisite and package probes offline; never build, pull or publish."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tooling'))
from external import probe_source


CONTAINER = r'''
import json, os
from pathlib import Path
import subprocess
kind = os.environ['PROFILE']
evidence = Path('/evidence')
source = Path('/tmp/probe')
source.mkdir()
(source / 'CMakeLists.txt').write_bytes(Path('/input/probe.cmake').read_bytes())
commands = {'packages': ['pacman', '-Q'], 'compiler': ['c++', '--version'],
            'cmake': ['cmake', '--version'], 'ninja': ['ninja', '--version']}
if kind == 'full': commands['qt'] = ['qmake6', '--version']
for name, command in commands.items():
    with (evidence / (name + '.txt')).open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
with (evidence / 'prerequisites.log').open('w') as log:
    subprocess.run(['cmake', '-S', str(source), '-B', str(source / 'build'), '-G', 'Ninja'],
                   stdout=log, stderr=subprocess.STDOUT, check=True)
(evidence / 'resolved.txt').write_bytes((source / 'build/resolved.txt').read_bytes())
if kind == 'daemon':
    assert not any(line.split()[0].startswith(('qt5-', 'qt6-', 'gtk3', 'gtk4'))
                   for line in (evidence / 'packages.txt').read_text().splitlines())
else:
    with (evidence / 'qmarkdown-ownership.txt').open('w') as log:
        subprocess.run(['pacman', '-Qo', '/usr/lib/libQMarkdown.so.1',
                        '/usr/lib/qt6/qml/QMarkdown/libQMarkdownPlugin.so',
                        '/usr/lib/qt6/qml/QMarkdown/qmldir', '/usr/lib/qt6/qml/QMarkdown/QMarkdown.qmltypes',
                        '/usr/share/licenses/QMarkdown/LICENSE', '/usr/share/licenses/QMarkdown/cmark/COPYING'],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    qml = source / 'probe.qml'
    qml.write_text('import QtQuick\nimport QMarkdown\nItem { width: 200; height: 100; '
                   'MarkdownView { id: view; width: 200; markdown: "# Installed package\\n`code`" } '
                   'Timer { interval: 100; running: true; onTriggered: Qt.exit(view.contentHeight > 0 ? 0 : 1) } }\n')
    runtime = Path('/tmp/runtime'); runtime.mkdir(mode=0o700)
    with (evidence / 'qmarkdown-runtime.log').open('w') as log:
        subprocess.run(['/usr/lib/qt6/bin/qml', str(qml)], timeout=20,
                       env=dict(os.environ, QT_QPA_PLATFORM='offscreen', QSG_RHI_BACKEND='software',
                                XDG_RUNTIME_DIR=str(runtime)), stdout=log, stderr=subprocess.STDOUT, check=True)
with (evidence / 'tooling-tests.log').open('w') as log:
    subprocess.run(['python3', '-m', 'unittest', 'discover', '-s', '/tooling', '-p', 'test_*.py', '-v'],
                   stdout=log, stderr=subprocess.STDOUT, check=True)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=['daemon', 'full'], required=True)
    parser.add_argument('--image', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    identity = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}', args.image], text=True).strip()
    configs = [json.loads(p.read_text()) for p in sorted((ROOT / 'tooling/modules').glob('*.json'))]
    if args.profile == 'daemon':
        configs = [c for c in configs if c['module'] == 'holonightd']
    features = {'BUILD_GTK_PROBES': True, 'BUILD_QT5_PROBES': True}
    probe = output / 'probe.cmake'
    probe.write_text(probe_source(configs, ('build', 'tool', 'test', 'runtime'), features))
    evidence = {'profile': args.profile, 'requested_image': args.image, 'image_id': identity,
                'network': 'none', 'features': features, 'repositories': [c['module'] for c in configs]}
    result = subprocess.run(['docker', 'run', '--rm', '--network', 'none',
                             '--mount', f'type=bind,src={probe},dst=/input/probe.cmake,readonly',
                             '--mount', f'type=bind,src={ROOT / "tooling"},dst=/tooling,readonly',
                             '--mount', f'type=bind,src={output},dst=/evidence',
                             '--env', f'PROFILE={args.profile}', '--entrypoint', 'python3', identity, '-c', CONTAINER])
    evidence['prerequisite_qualification'] = 'passed' if result.returncode == 0 else 'failed'
    evidence['repository_acceptance'] = 'pending adoption'
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(f'{args.profile}: {evidence["prerequisite_qualification"]}; evidence: {output}')
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
