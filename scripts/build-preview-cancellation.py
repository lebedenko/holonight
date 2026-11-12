#!/usr/bin/env python3
"""Build prepared diagnostic copies sequentially against private installed providers."""
import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
import subprocess

spec = importlib.util.spec_from_file_location('prepare_cancellation', Path(__file__).with_name('prepare-preview-cancellation.py'))
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)
smoke = prepare.smoke


def verify_inputs(package, manifest):
    if (package / 'execution-started.json').exists():
        raise ValueError('execution already started; rebuilding or sealing prohibited')
    smoke.verify_hashes(prepare.ROOT, manifest['tool_inputs'])
    smoke.verify_hashes(package, manifest['private_inputs'])
    for label in 'CD':
        for group, key in (('source', 'sources'), ('harness-source', 'harness_sources')):
            if smoke.inventory(package / label / group) != manifest[key][label]:
                raise ValueError('prepared input changed: ' + label + '/' + group)


def verify_without_helpers(package):
    commands = []

    def run(command, name, timeout=30):
        commands.append(command)
        smoke.write(package / 'verification-commands.json', commands)
        with (package / name).open('x') as stream:
            subprocess.run(command, cwd=prepare.ROOT, stdout=stream, stderr=subprocess.STDOUT,
                           check=True, timeout=timeout)

    run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p',
         'test_preview_cancellation.py', '-v'], 'python-tests.log')
    flags_command = ['pkg-config', '--cflags', '--libs', 'Qt6Core']
    run(flags_command, 'qt-core-resolution.log')
    flags = (package / 'qt-core-resolution.log').read_text().split()
    run(['c++', '-std=c++23', '-fPIC', '-I' + str(package),
         str(package / 'C/harness-source/barrier_test.cpp'), '-o', str(package / 'barrier-test'),
         *flags, '-pthread'], 'barrier-build.log')
    for mode in ('result-status', 'release', 'watchdog', 'supervisor', 'supervisor-timeout'):
        run([str(package / 'barrier-test'), mode], 'test-' + mode + '.log', timeout=5)
    smoke.write(package / 'verification.json', {
        'passed': True, 'python': 'python-tests.log',
        'native_without_helpers': ['result-status', 'release', 'watchdog', 'supervisor', 'supervisor-timeout']})


def seal(package, manifest):
    verify_inputs(package, manifest)
    checks = json.loads((package / 'verification.json').read_text())
    if checks.get('passed') is not True:
        raise ValueError('focused verification required before sealing')
    review = {'trace_header_unchanged': smoke.digest(package / 'trace.h') == smoke.digest(smoke.REVIEW / 'trace.h'),
              'overlays': ['C/overlay.diff', 'D/overlay.diff'],
              'success_predicate': 'runtime success, raster success, no preview error; independent of image payload',
              'delivery_join': 'publication -> application attempt -> acceptance, matching context/selection/payload/status',
              'reference': 'Independent in-process pixels, oriented dimensions and full formatted EXIF',
              'verification': checks, 'runtime_started': False}
    if not review['trace_header_unchanged']:
        raise ValueError('v3 tracing header changed')
    smoke.write(package / 'review.json', review)
    identities = dict(manifest['tool_inputs'])
    names = ('trace.h', 'diagnostic.h', 'preparation.json', 'artifacts.json', 'build-commands.json',
             'build-integrity.json', 'verification-commands.json', 'verification.json', 'environment.json',
             'python-tests.log', 'qt-core-resolution.log', 'barrier-build.log', 'barrier-test', 'review.json')
    for name in names:
        identities[name] = smoke.digest(package / name)
    for path in package.glob('test-*.log'):
        identities[path.name] = smoke.digest(path)
    smoke.write(package / 'tool-identities.json', identities)


def build(package):
    package = package.resolve()
    manifest = json.loads((package / 'preparation.json').read_text())
    previous = Path(manifest['input'])
    verify_inputs(package, manifest)
    before = smoke.preflight(previous, Path(manifest['fixtures']))
    verify_without_helpers(package)
    smoke.write(package / 'environment.json', {
        'host': list(os.uname()), 'cwd': str(prepare.ROOT),
        'environment': {key: value for key, value in os.environ.items()
                        if key.startswith(('QT_', 'LD_', 'CMAKE', 'PKG_CONFIG')) or
                        key in ('PATH', 'CXX', 'CC', 'CFLAGS', 'CXXFLAGS', 'LDFLAGS')},
        'parallel_jobs': 4, 'build_order': ['C', 'D']})
    commands = []
    artifacts = {}
    for label in 'CD':
        base = package / label
        if smoke.inventory(base / 'source') != manifest['sources'][label]:
            raise ValueError('overlay changed since preparation')
        saved = json.loads((previous / 'commands.json').read_text())
        selected = [row['argv'] for row in saved if any(str(previous / label) + '/' in part for part in row['argv']) and
                    not any('reuse-harness' in part or 'harness-source' in part for part in row['argv'])]
        selected = [[part.replace(str(previous / label), str(base)) for part in command] for command in selected]
        selected += [['cmake', '-S', str(base / 'harness-source'), '-B', str(base / 'harness-build'), '-G', 'Ninja',
                      '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(base / 'prefix')],
                     ['cmake', '--build', str(base / 'harness-build'), '--parallel', '4', '--verbose']]
        for index, command in enumerate(selected):
            commands.append(command)
            smoke.write(package / 'build-commands.json', commands)
            with (base / f'build-{index:02}.log').open('x') as stream:
                subprocess.run(command, cwd=prepare.ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
        for name, command in [('harness', ['ldd', str(base / 'harness-build/preview-cancellation')]),
                              ('helper', ['ldd', str(base / 'build/holonight-images/holonight-images-helper')])]:
            with (base / (name + '-dependencies.log')).open('x') as stream:
                subprocess.run(command, cwd=prepare.ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
        artifacts[label] = {group: smoke.inventory(base / group) for group in ('source', 'prefix', 'runtime', 'harness-source', 'harness-build')}
        # CMake caches record the installed provider resolution.
        artifacts[label]['build'] = {'holonight-images/holonight-images-helper': smoke.digest(base / 'build/holonight-images/holonight-images-helper')}
    smoke.write(package / 'artifacts.json', artifacts)
    after = smoke.preflight(previous, Path(manifest['fixtures']))
    if before != after:
        raise ValueError('retained input changed during build')
    smoke.write(package / 'build-integrity.json', {'unchanged': True, 'inputs': after})
    seal(package, manifest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    build(parser.parse_args().package)
