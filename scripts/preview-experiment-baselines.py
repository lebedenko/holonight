#!/usr/bin/env python3
"""Freeze historical preview evidence and build fixed host-native Release baselines.

Never resumes or overwrites a run. All generated artifacts live in ignored build/.
The archived A source must match the selected revision, not just its preview file.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REVISIONS = {
    'holonight-images': 'c1f6da5',
    'holonight-thumbnails': '9462bac',
    'holonight-file-browser': '2f86c9b',
}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        name = str(path.relative_to(root))
        if path.is_symlink():
            result[name] = {'link': os.readlink(path)}
        elif path.is_file():
            result[name] = {'sha256': digest(path), 'bytes': path.stat().st_size,
                            'mode': path.stat().st_mode & 0o7777}
    return result


def capture(command, cwd=ROOT):
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def archive_source(repository, revision, destination):
    destination.mkdir(parents=True)
    with tempfile.TemporaryFile() as stream:
        subprocess.run(['git', 'archive', revision], cwd=ROOT / repository,
                       stdout=stream, check=True)
        stream.seek(0)
        with tarfile.open(fileobj=stream) as archive:
            archive.extractall(destination, filter='data')


def freeze(output):
    historical = output / 'historical'
    historical.mkdir()
    provenance = {'environment': {'platform': platform.platform(),
                                 'compiler': capture(['c++', '--version']),
                                 'cmake': capture(['cmake', '--version']),
                                 'dependencies': capture(['pkg-config', '--modversion',
                                                          'Qt6Core', 'libexif', 'libwebp'])},
                  'archives': {}, 'revisions': {}}
    for name in ('preview-baseline', 'preview-benchmark', 'warm-preview',
                 'isolated-prefix-relocated'):
        source = ROOT / 'build' / name
        records = inventory(source)
        if not records:
            raise RuntimeError(f'missing historical evidence: {source}')
        target = historical / (name + '.tar')
        with tarfile.open(target, 'x') as archive:
            archive.add(source, arcname=name)
        # Verify evidence was stable while being archived.
        if inventory(source) != records:
            raise RuntimeError(f'historical evidence changed during freeze: {source}')
        provenance['archives'][name] = {'path': str(target), 'sha256': digest(target),
                                        'source': str(source), 'inventory': records}
    for label, browser_revision in (('A', 'caec685'), ('B', REVISIONS['holonight-file-browser'])):
        provenance['revisions'][label] = {}
        for repository, revision in REVISIONS.items():
            if repository == 'holonight-file-browser':
                revision = browser_revision
            revision = capture(['git', 'rev-parse', revision], ROOT / repository)
            destination = output / label / 'source' / repository
            archive_source(repository, revision, destination)
            provenance['revisions'][label][repository] = revision
    archived = inventory(ROOT / 'build/preview-baseline/source')
    reproduced = inventory(output / 'A/source/holonight-file-browser')
    if archived != reproduced:
        differences = sorted(key for key in archived.keys() | reproduced.keys()
                             if archived.get(key) != reproduced.get(key))
        raise RuntimeError(f'archived A tree differs from revision: {differences}')
    (output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')


def build(output, label, jobs):
    base = output / label
    prefix = base / 'prefix'
    with (base / 'build.log').open('x') as log:
        def run(*command):
            log.write(json.dumps(command) + '\n')
            log.flush()
            subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)

        for repository in REVISIONS:
            source = base / 'source' / repository
            binary = base / 'build' / repository
            flags = []
            if repository == 'holonight-images':
                flags = ['-DHOLONIGHT_IMAGES_ISOLATED=ON',
                         f'-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE={base / "runtime"}']
            elif repository == 'holonight-thumbnails':
                flags = ['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON']
            else:
                flags = [f'-DBUILD_FILE_BROWSER_{component}=OFF' for component in
                         ('QUICK', 'SEARCH', 'STORAGE', 'PREVIEW_QUICK', 'MARKDOWN')]
            run('cmake', '-S', str(source), '-B', str(binary), '-G', 'Ninja',
                '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_CXX_COMPILER=/usr/bin/c++',
                '-DBUILD_TESTING=OFF', f'-DCMAKE_INSTALL_PREFIX={prefix}',
                f'-DCMAKE_PREFIX_PATH={prefix}', *flags)
            run('cmake', '--build', str(binary), '--parallel', str(jobs))
            if repository == 'holonight-images':
                qt_bin = capture(['pkg-config', '--variable=bindir', 'Qt6Core'])
                plugins = capture([str(Path(qt_bin) / 'qtpaths'), '--query', 'QT_INSTALL_PLUGINS'])
                run('python3', str(source / 'scripts/prepare-isolated-runtime.py'),
                    '--helper', str(binary / 'holonight-images-helper'),
                    '--plugins', plugins, '--output', str(base / 'runtime'))
            run('cmake', '--install', str(binary))
    (base / 'build-inventory.json').write_text(json.dumps(inventory(base), indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    output = Path(tempfile.mkdtemp(prefix='preview-experiments-', dir=ROOT / 'build'))
    print(output, flush=True)
    (output / 'baseline-builder.py').write_bytes(Path(__file__).read_bytes())
    try:
        freeze(output)
        for label in ('A', 'B'):
            print(f'Building {label}', flush=True)
            build(output, label, args.jobs)
    except Exception as error:
        (output / 'FAILED.txt').write_text(str(error) + '\n')
        raise


if __name__ == '__main__':
    main()
