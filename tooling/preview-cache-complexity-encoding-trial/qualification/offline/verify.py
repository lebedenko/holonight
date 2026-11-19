#!/usr/bin/env python3
"""Independent offline preparation/build verifier. No controller imports."""
import argparse
import difflib
import os
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import contract as t
h = t.h
DETECTOR = '\nstatic bool adaptiveNonuniform(const QImage& image, const std::atomic_bool& cancelled) {\n  switch (image.format()) {\n    case QImage::Format_RGB32:\n    case QImage::Format_ARGB32:\n    case QImage::Format_ARGB32_Premultiplied:\n    case QImage::Format_RGBX8888:\n    case QImage::Format_RGBA8888:\n    case QImage::Format_RGBA8888_Premultiplied: break;\n    default: return false;\n  }\n  if (image.width() < 2 || image.height() < 2) return false;\n  const int nx = std::min(32, image.width()-1), ny = std::min(32, image.height()-1);\n  int complex = 0;\n  for (int j=0; j<ny; ++j) {\n    if (cancelled.load()) return false;\n    int y = 1 + ((2*j+1)*(image.height()-1))/(2*ny);\n    const auto* row = reinterpret_cast<const quint32*>(image.constScanLine(y));\n    const auto* upper = reinterpret_cast<const quint32*>(image.constScanLine(y-1));\n    for (int i=0; i<nx; ++i) {\n      int x = 1 + ((2*i+1)*(image.width()-1))/(2*nx);\n      complex += row[x] != row[x-1] && row[x] != upper[x];\n    }\n  }\n  return 4*complex >= nx*ny;\n}\n'
ANCHOR = '  if (cancelled.load() || !tagged.save(&file, "PNG")) {'
WRITER = '  const bool compress = request.kind == Kind::Raster && adaptiveNonuniform(image, cancelled);\n  QImageWriter writer(&file, "PNG");\n  if (compress) writer.setCompression(11);\n  if (cancelled.load() || !(compress ? writer.write(tagged) : tagged.save(&file, "PNG"))) {'


def tools(root):
    recorded = h.read(root / 'tools.json')
    h.require(all(h.digest(Path(path)) == digest for path,digest in recorded.items()), 'captured phase tool drift')
    for path, digest in recorded.items():
        h.require(h.digest(root / 'tools' / t.snapshot_name(path)) == digest, 'snapshot mismatch')
    h.require(h.read(root / 'integrity.json') == dict(unchanged=True), 'input integrity failed')
    return {'tools/' + t.snapshot_name(path) for path in recorded}


def source_contract(root):
    binding = h.read(root / 'binding.json')
    h.require(binding == t.prerequisite(), 'retained provenance mismatch')
    retained = binding['retained']
    h.require(h.read(root / 'protocol.json') == t.protocol(), 'protocol drift')
    h.require(h.digest(root / '3200x2400.png') == retained['fixture']['sha256'], 'fixture drift')
    for arm in ('control', 'candidate'):
        for group, source, membership in [('source', t.Q / 'C/source', retained['source']),
                                         ('harness-source', t.Q / 'harness-source', retained['harness'])]:
            actual = h.inventory(root / arm / group)
            h.require(set(actual) == set(membership), 'source membership drift')
            for name in actual:
                data = (root / arm / group / name).read_text() if name.endswith('.cpp') else None
                if group == 'source' and arm == 'candidate' and name == t.SERVICE:
                    h.require(data.count(WRITER) == 1 and data.count(DETECTOR) == 1, 'candidate encoding restrictions')
                    data = data.replace('#include <QSaveFile>\n#include <QImageWriter>\n'+DETECTOR,'#include <QSaveFile>').replace(WRITER,ANCHOR)
                    h.require(data.encode() == (source/name).read_bytes(), 'unexplained provider edit')
                elif group == 'harness-source' and name == 'reuse.cpp':
                    h.require(data.count(t.IDENTITY_AFTER) == 1, 'post-timing snapshot missing')
                    data = data.replace(t.IDENTITY_AFTER, t.IDENTITY_BEFORE)
                    h.require(data.encode() == (source / name).read_bytes(), 'timed harness changed')
                else:
                    h.require(actual[name] == membership[name], 'unexpected source edit: ' + name)
    before = (root / 'control/source' / t.SERVICE).read_text()
    after = (root / 'candidate/source' / t.SERVICE).read_text()
    patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
        fromfile='control/' + t.SERVICE, tofile='candidate/' + t.SERVICE))
    h.require((root / 'candidate.diff').read_text() == patch, 'candidate patch mismatch')


def linkage(path):
    text = path.read_text()
    h.require('not found' not in text, 'unresolved host dependency')
    identities = {}
    for line in text.splitlines():
        parts = line.split()
        name = parts[2] if len(parts) > 2 and parts[1] == '=>' else parts[0] if parts else ''
        if name.startswith('/'):
            resolved = Path(name).resolve()
            identities[str(resolved)] = h.digest(resolved)
    h.require(identities, 'no linked dependencies')
    return identities


def mapped(data, binary, linked):
    h.require(data['executable'] == str(binary.resolve()) and data['helper_mappings'] ==
              'unavailable: helper exited before post-timing capture', 'loading executable/helper identity')
    images = {}
    for line in data['maps'].splitlines():
        parts = line.split(maxsplit=5)
        if len(parts) == 6 and parts[5].startswith('/'):
            h.require(not parts[5].endswith(' (deleted)'), 'deleted loaded image')
            path = Path(parts[5]).resolve()
            info = path.stat()
            device = parts[3].split(':')
            h.require(info.st_ino == int(parts[4]) and os.major(info.st_dev) == int(device[0], 16) and
                      os.minor(info.st_dev) == int(device[1], 16), 'loaded inode/device mismatch')
            images[str(path)] = h.digest(path)
    h.require(str(binary.resolve()) in images and all(images.get(p) == digest for p, digest in linked.items()),
              'loaded dependency mismatch')
    return images


def verify(root):
    inventory = h.sealed(root)
    snapshots = tools(root)
    assessment = h.read(root / 'assessment.json')
    h.require(assessment['status'] in ('prepared', 'built', 'blocked') and
              assessment['decision'] == 'Evidence insufficient', 'invalid preparation/build outcome')
    fixed = {'assessment.json', 'integrity.json', 'tools.json', 'REPORT.md', 'seal.json'} | snapshots
    if root == t.PREPARED:
        h.require(assessment['attempted'] == assessment['completed'] == [], 'preparation launched commands')
        source_contract(root)
        fixed |= {'binding.json', 'protocol.json', '3200x2400.png', 'candidate.diff'}
        h.require(all(name in fixed or any(name.startswith(a + '/' + g + '/') for a in t.ARMS
            for g in ('source', 'harness-source')) for name in inventory), 'unexpected preparation artifact')
    else:
        h.require(root == t.BUILT, 'fixed build root required')
        h.require(verify(t.PREPARED)['outcome'] == 'prepared', 'preparation prerequisite')
        h.require(h.read(root / 'package.json') == dict(path=str(t.PREPARED),
            seal=h.digest(t.PREPARED / 'seal.json')), 'prepared binding')
        rows = h.read(root / 'schedule.json')
        h.require(rows == expected_build_commands(t.PREPARED, root), 'build command reconstruction mismatch')
        names = [r['name'] for r in rows]
        attempted, completed = assessment['attempted'], assessment['completed']
        h.require(attempted == names[:len(attempted)] and completed == attempted[:len(completed)] and
                  len(attempted) - len(completed) in (0, 1), 'stopped build accounting')
        actual = {p.removeprefix('commands/').removesuffix('-command.json') for p in inventory
                  if p.startswith('commands/') and p.endswith('-command.json')}
        h.require(actual == set(attempted), 'unexpected build command')
        previous = 0
        for row in rows[:len(attempted)]:
            name = row['name']
            h.require(h.read(root / 'commands' / (name + '-command.json')) == row, 'build launch drift')
            result = h.read(root / 'commands' / (name + '-result.json'))
            h.require(previous <= result['start_ns'] <= result['stop_ns'], 'build chronology')
            previous = result['stop_ns']
            if name in completed:
                h.require(result['exit'] == 0 and result['failure'] is None and result['cleanup'] and
                          0 <= result['cleanup_seconds'] <= 5, 'failed completed build')
            else:
                h.require(result['failure'], 'unexplained stopped build')
        if assessment['status'] == 'built':
            h.require(completed == names, 'incomplete build')
            common = h.inventory(root / 'common/prefix')
            runtime = h.inventory(root / 'common/runtime')
            for arm in t.ARMS:
                h.require(h.inventory(root / arm / 'runtime') == runtime, 'runtime differs between arms')
                prefix = h.inventory(root / arm / 'prefix')
                h.require(all(prefix.get(n) == digest for n, digest in common.items()), 'common installed package drift')
                cache = (root / arm / 'harness-build/CMakeCache.txt').read_text()
                resolution = {line.split(':')[0]: line.split('=', 1)[1] for line in cache.splitlines()
                    if line.startswith(('HolonightImages_DIR:', 'HolonightThumbnails_DIR:', 'HolonightFileBrowser_DIR:'))}
                h.require(len(resolution) == 3 and all(Path(p).is_relative_to(root / arm / 'prefix')
                    for p in resolution.values()), 'installed provider resolution')
                linkage(root / 'commands' / (arm + '-linkage.stdout'))
        fixed |= {'package.json', 'environment.json', 'schedule.json'}
        h.require(all(name in fixed or name.startswith(('common/', 'control/', 'candidate/', 'commands/'))
                      for name in inventory), 'unexpected build artifact')
    return dict(status='passed', outcome=assessment['status'], decision='Evidence insufficient',
        evidence_seal=h.digest(root / 'seal.json'), imports_runner=False,
        verifier_sha256=h.digest(Path(__file__)))


def expected_build_commands(package, output):
    rows = []
    def add(name, argv):
        rows.append(dict(name=name, argv=[str(v) for v in argv], environment=t.environment(),
            timeout_seconds=30 if name.endswith('-linkage') or name in ('compiler','cmake','dependencies') else 600, cwd=str(t.ROOT), launch=dict(start_new_session=True)))
    add('compiler', ['c++', '--version'])
    add('cmake', ['cmake', '--version'])
    add('dependencies', ['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp'])
    # Compile Images and Thumbnails once. Install their identical package bytes into each arm.
    common = output / 'common'
    for component in ('holonight-images',):
        source = package / 'control/source' / component
        native = common / 'build' / component
        options = ['-DHOLONIGHT_IMAGES_ISOLATED=ON', '-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE=' + str(common / 'runtime')] if component == 'holonight-images' else ['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON']
        add(component + '-configure', ['cmake', '-S', source, '-B', native, '-G', 'Ninja',
            '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=OFF', '-DCMAKE_INSTALL_PREFIX=' + str(common / 'prefix'),
            '-DCMAKE_PREFIX_PATH=' + str(common / 'prefix'), *options])
        add(component + '-compile', ['cmake', '--build', native, '--parallel', '4'])
        if component == 'holonight-images':
            add('runtime', [sys.executable, source / 'scripts/prepare-isolated-runtime.py', '--helper',
                native / 'holonight-images-helper', '--plugins', '/usr/lib/qt6/plugins', '--output', common / 'runtime'])
        add(component + '-install', ['cmake', '--install', native])
    for arm in t.ARMS:
        base = output / arm
        protected = Path('/run') / ('holonight-directional-' + __import__('hashlib').sha256(str(t.CORRECTNESS).encode()).hexdigest()[:20] + '-' + arm)
        prefix = base / 'prefix'
        thumb = base / 'build/holonight-thumbnails'
        add(arm + '-thumbnails-configure', ['cmake','-S',package / arm / 'source/holonight-thumbnails','-B',thumb,'-G','Ninja',
            '-DCMAKE_BUILD_TYPE=Release','-DBUILD_TESTING=ON','-DHOLONIGHT_THUMBNAILS_ISOLATED=ON',
            '-DCMAKE_INSTALL_PREFIX='+str(prefix),'-DCMAKE_PREFIX_PATH='+str(prefix),
            '-DHOLONIGHT_THUMBNAILS_TEST_RUNTIME='+str(protected)])
        add(arm + '-thumbnails-compile', ['cmake','--build',thumb,'--parallel','4'])
        add(arm + '-thumbnails-install', ['cmake','--install',thumb])
        source = package / arm / 'source/holonight-file-browser'
        native = base / 'build/holonight-file-browser'
        prefix = base / 'prefix'
        add(arm + '-browser-configure', ['cmake', '-S', source, '-B', native, '-G', 'Ninja',
            '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=ON', '-DCMAKE_INSTALL_PREFIX=' + str(prefix),
            '-DHOLONIGHT_FILE_BROWSER_TEST_RUNTIME='+str(protected),
            '-DHOLONIGHT_FILE_BROWSER_TEST_FIXTURES='+str(t.CORRECTNESS/'fixtures'),
            '-DCMAKE_PREFIX_PATH=' + str(prefix),
            *['-DBUILD_FILE_BROWSER_' + n + '=OFF' for n in ('QUICK', 'SEARCH', 'STORAGE', 'PREVIEW_QUICK', 'MARKDOWN')]])
        add(arm + '-browser-compile', ['cmake', '--build', native, '--parallel', '4'])
        add(arm + '-browser-install', ['cmake', '--install', native])
        add(arm + '-harness-configure', ['cmake', '-S', package / arm / 'harness-source', '-B', base / 'harness-build',
            '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(prefix),
            '-DPREVIEW_REUSE_BENCHMARK=ON', '-DREUSABLE_VARIANT=ON'])
        add(arm + '-harness-compile', ['cmake', '--build', base / 'harness-build', '--parallel', '4'])
        add(arm + '-linkage', ['ldd', base / 'harness-build/preview-benchmark'])
    return rows



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.evidence.absolute(), args.output.absolute()
    h.require(not output.exists() and not output.is_relative_to(root) and not root.is_relative_to(output), 'verification collision')
    try:
        result = verify(root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = dict(status='failed', decision='Evidence insufficient', failure=str(error))
    h.write(output, result)
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
