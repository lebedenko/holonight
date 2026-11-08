#!/usr/bin/env python3
"""Build fresh installed scheduler controls or diagnostic-only packages; never overwrite evidence."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OVERLAYS = ROOT / 'tooling/preview-benchmark/overlays'
spec = importlib.util.spec_from_file_location('baselines', ROOT / 'scripts/preview-experiment-baselines.py')
baselines = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baselines)


def apply_overlay(source, repository):
    patch = OVERLAYS / (repository + '.patch')
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=source, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=source, check=True)
    for line in patch.read_text().splitlines():
        if line.startswith('+++ b/'):
            target = source / line[6:]
            shutil.copyfile(OVERLAYS / 'telemetry.h', target.parent / 'preview_evidence.h')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=('scheduler', 'diagnostic'), required=True)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    output = Path(tempfile.mkdtemp(prefix='preview-' + args.kind + '-', dir=ROOT / 'build'))
    print(output, flush=True)
    shutil.copyfile(__file__, output / 'builder.py')
    shutil.copytree(OVERLAYS, output / 'overlays')
    provenance = {'kind': args.kind, 'qualifying_latency': False, 'revisions': {},
                  'overlays': baselines.inventory(OVERLAYS), 'commands': [],
                  'scheduler_threads': 2, 'thumbnail_box_pixels': 256,
                  'production_defaults_changed': False}
    def save():
        (output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    try:
        for label in ('D',) if args.kind == 'diagnostic' else ('A', 'B'):
            base = output / label
            revisions = dict(baselines.REVISIONS)
            if label == 'A':
                revisions['holonight-file-browser'] = 'caec685'
            if label == 'D':
                revisions['holonight-images'] = 'a772a67'
            provenance['revisions'][label] = {}
            for repo, rev in revisions.items():
                full = baselines.capture(['git', 'rev-parse', rev], ROOT / repo)
                provenance['revisions'][label][repo] = full
                source = base / 'source' / repo
                baselines.archive_source(repo, full, source)
                if label == 'D' and (OVERLAYS / (repo + '.patch')).exists():
                    apply_overlay(source, repo)
            harness_source = base / 'harness-source'
            shutil.copytree(ROOT / 'tooling/preview-benchmark', harness_source)
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
                      if label == 'D' else []))
                run('cmake', '--build', str(base / 'harness'), '--parallel', str(args.jobs))
            (base / 'inventory.json').write_text(json.dumps(baselines.inventory(base), indent=2) + '\n')
        save()
    except BaseException as error:
        provenance['failure'] = repr(error)
        save()
        raise


if __name__ == '__main__':
    main()
