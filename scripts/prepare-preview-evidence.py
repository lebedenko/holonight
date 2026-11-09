#!/usr/bin/env python3
"""Build fresh installed scheduler controls or diagnostic-only packages; never overwrite evidence."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OVERLAYS = ROOT / 'tooling/preview-benchmark/overlays'
spec = importlib.util.spec_from_file_location('baselines', ROOT / 'scripts/preview-experiment-baselines.py')
baselines = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baselines)


def apply_patch(source, patch):
    # Archives live below the umbrella Git repository. Stop discovery at their
    # parent: otherwise git apply can silently skip diff --git paths as outside
    # the current repository subdirectory and still exit successfully.
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(source.resolve().parent))
    targets = [source / line[6:] for line in patch.read_text().splitlines() if line.startswith('+++ b/')]
    if not targets:
        raise ValueError('patch has no target files')
    before = {p: p.read_bytes() if p.exists() else None for p in targets}
    subprocess.run(['git', 'apply', '--check', str(patch.resolve())], cwd=source, env=env, check=True)
    subprocess.run(['git', 'apply', str(patch.resolve())], cwd=source, env=env, check=True)
    if any(not p.exists() or p.read_bytes() == before[p] for p in targets):
        raise ValueError('patch did not change every declared target')


def apply_overlay(source, repository):
    patch = OVERLAYS / (repository + '.patch')
    apply_patch(source, patch)
    for line in patch.read_text().splitlines():
        if line.startswith('+++ b/'):
            target = source / line[6:]
            shutil.copyfile(OVERLAYS / 'telemetry.h', target.parent / 'preview_evidence.h')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=('scheduler', 'diagnostic'), required=True)
    parser.add_argument('--variants', choices=('corrected', 'historical'), default='corrected')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    output = Path(tempfile.mkdtemp(prefix='preview-' + args.kind + '-', dir=ROOT / 'build'))
    print(output, flush=True)
    shutil.copyfile(__file__, output / 'builder.py')
    shutil.copytree(OVERLAYS, output / 'overlays')
    provenance = {'kind': args.kind, 'qualifying_latency': False, 'revisions': {},
                  'overlays': baselines.inventory(OVERLAYS), 'commands': [],
                  'scheduler_threads': 2, 'thumbnail_box_pixels': 256,
                  'production_defaults_changed': False, 'variants': {},
                  'environment': {'compiler': baselines.capture(['c++', '--version']),
                                  'qt': baselines.capture(['pkg-config', '--modversion', 'Qt6Core'])}}
    def save():
        (output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    try:
        corrected = args.variants == 'corrected'
        labels = (('D2',) if corrected else ('D',)) if args.kind == 'diagnostic' else (('A', 'B2') if corrected else ('A', 'B'))
        # Freeze every input before the first build, including the exact uncommitted correction.
        for label in labels:
            base = output / label
            revisions = dict(baselines.REVISIONS)
            if label == 'A':
                revisions['holonight-file-browser'] = 'caec685'
            if label == 'D':
                revisions['holonight-images'] = 'a772a67'
            if label in ('B2', 'D2'):
                revisions['holonight-images'] = 'HEAD'
            provenance['variants'][label] = {'role': 'diagnostic' if label in ('D', 'D2') else 'scheduler',
                                            'diagnostic': label in ('D', 'D2'),
                                            'corrected_cleanup': label in ('B2', 'D2'),
                                            'source_delta': {}}
            provenance['revisions'][label] = {}
            for repo, rev in revisions.items():
                full = baselines.capture(['git', 'rev-parse', rev], ROOT / repo)
                provenance['revisions'][label][repo] = full
                source = base / 'source' / repo
                baselines.archive_source(repo, full, source)
                if label in ('B2', 'D2') and repo == 'holonight-images':
                    files = ('src/isolated/cleanup.cpp', 'src/isolated/cleanup.h',
                             'src/isolated/runtime.cpp', 'tests/isolated_cleanup_test.cpp')
                    expected = {name: baselines.digest(ROOT / repo / name) for name in files}
                    delta = subprocess.check_output(['git', 'diff', '--binary', full, '--', *files], cwd=ROOT / repo)
                    patch = base / 'cleanup-correction.patch'
                    patch.write_bytes(delta)
                    if delta:
                        apply_patch(source, patch)
                    if {name: baselines.digest(source / name) for name in files} != expected:
                        raise ValueError('archived correction differs from requested source')
                    provenance['variants'][label]['correction_verified'] = True
                    provenance['variants'][label]['corrected_source_hashes'] = expected
                    provenance['variants'][label]['source_delta'][repo] = baselines.digest(patch)
                if label in ('D', 'D2') and (OVERLAYS / (repo + '.patch')).exists():
                    apply_overlay(source, repo)
            harness_source = base / 'harness-source'
            shutil.copytree(ROOT / 'tooling/preview-benchmark', harness_source)
            provenance['variants'][label]['source_inventory'] = baselines.inventory(base / 'source')
            provenance['variants'][label]['harness_inventory'] = baselines.inventory(harness_source)
        save()
        for label in labels:
            base = output / label
            revisions = provenance['revisions'][label]
            harness_source = base / 'harness-source'
            prefix = base / 'prefix'
            with (base / 'build.log').open('x') as log:
                def run(*command):
                    provenance['commands'].append(list(command))
                    save()
                    log.write(json.dumps(command) + '\n')
                    log.flush()
                    subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
                for repo in revisions:
                    source = base / 'source' / repo
                    binary = base / 'build' / repo
                    flags = []
                    if repo == 'holonight-images':
                        flags = ['-DHOLONIGHT_IMAGES_ISOLATED=ON',
                                 f'-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE={base / "runtime"}']
                    elif repo == 'holonight-thumbnails':
                        flags = ['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON']
                    else:
                        flags = [f'-DBUILD_FILE_BROWSER_{part}=OFF' for part in ('SEARCH', 'STORAGE', 'MARKDOWN')]
                    run('cmake', '-S', str(source), '-B', str(binary), '-G', 'Ninja',
                        '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_CXX_COMPILER=/usr/bin/c++',
                        '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON', '-DBUILD_TESTING=OFF',
                        f'-DCMAKE_INSTALL_PREFIX={prefix}', f'-DCMAKE_PREFIX_PATH={prefix}',
                        '-DHolonightQt_DIR=/usr/lib/cmake/HolonightQt', *flags)
                    run('cmake', '--build', str(binary), '--parallel', str(args.jobs))
                    if repo == 'holonight-images':
                        qt_bin = baselines.capture(['pkg-config', '--variable=bindir', 'Qt6Core'])
                        plugins = baselines.capture([str(Path(qt_bin) / 'qtpaths'), '--query', 'QT_INSTALL_PLUGINS'])
                        run('python3', str(source / 'scripts/prepare-isolated-runtime.py'),
                            '--helper', str(binary / 'holonight-images-helper'), '--plugins', plugins,
                            '--output', str(base / 'runtime'))
                    run('cmake', '--install', str(binary))
                run('cmake', '-S', str(harness_source), '-B', str(base / 'harness'),
                    '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_PREFIX_PATH={prefix}',
                    '-DBUILD_GRID_CONTROL=ON', '-DHolonightQt_DIR=/usr/lib/cmake/HolonightQt',
                    '-DISOLATED=' + ('OFF' if label == 'A' else 'ON'),
                    *([f'-DPREVIEW_DIAGNOSTIC_HEADER={base / "source/holonight-images/src/isolated/preview_evidence.h"}']
                      if label in ('D', 'D2') else []))
                run('cmake', '--build', str(base / 'harness'), '--parallel', str(args.jobs))
            (base / 'inventory.json').write_text(json.dumps(baselines.inventory(base), indent=2) + '\n')
        save()
    except BaseException as error:
        provenance['failure'] = repr(error)
        save()
        raise


if __name__ == '__main__':
    main()
