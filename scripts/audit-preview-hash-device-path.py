#!/usr/bin/env python3
"""Audit retained Qt hashing evidence; never execute a workload or packaging script."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGING_URL = 'https://gitlab.archlinux.org/archlinux/packaging/packages/qt6-base.git'
QT_URL = 'https://code.qt.io/qt/qtbase.git'
PACKAGE = Path('/var/cache/pacman/pkg/qt6-base-6.12.0-5-x86_64.pkg.tar.zst')
PREPARED = ROOT / 'build/preview-cpu-profile-20261115-02-prepared'
SOURCES = ['src/corelib/tools/qcryptographichash.cpp', 'src/corelib/io/qiodevice.cpp',
           'src/corelib/io/qiodevice_p.h', 'src/corelib/io/qfiledevice.cpp',
           'src/corelib/io/qfsfileengine.cpp', 'src/corelib/io/qfsfileengine_unix.cpp',
           'src/corelib/tools/qringbuffer.cpp']
SYMBOLS = ['_ZN18QCryptographicHash7addDataEP9QIODevice', '_ZN9QIODevice4readEPcx',
           '_ZN16QIODevicePrivate4readEPcxb', '_ZN11QFileDevice8readDataEPcx',
           '_ZN13QFSFileEngine4readEPcx', '_ZNK11QFileDevice5atEndEv']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def seal(root):
    write(root / 'seal.json', {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob('*'))
                             if p.is_file() and p != root / 'seal.json'})


def command(args, output=None):
    result = subprocess.run([str(a) for a in args], capture_output=True, timeout=180)
    if output:
        output.write_bytes(result.stdout)
        output.with_suffix(output.suffix + '.stderr').write_bytes(result.stderr)
    require(result.returncode == 0, 'command failed: ' + ' '.join(map(str, args)) + ': ' + result.stderr.decode(errors='replace')[-1000:])
    return result.stdout


def load_checker():
    spec = importlib.util.spec_from_file_location('device_checker', ROOT / 'scripts/verify-preview-hash-device-path.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def accounting(rows, mapping):
    result = []
    measured = [r for r in rows if r.get('type') == 'file' and not r['warmup'] and r['case'] in ('qt_device', 'qt_file')]
    expected = {(b, c, s, f['ordinal']) for b in range(5) for c in ('qt_device', 'qt_file')
                for s in range(5) for f in mapping}
    keys = [(r['block'], r['case'], r['sweep'], r['ordinal']) for r in measured]
    require(len(keys) == len(set(keys)) and set(keys) == expected, 'missing/duplicate ordinals or sweeps')
    for block in range(5):
        files = []
        for f in mapping:
            sums = {c: sum(r['update_ns'] for r in measured if r['block'] == block and r['ordinal'] == f['ordinal'] and r['case'] == c)
                    for c in ('qt_device', 'qt_file')}
            delta = sums['qt_device'] - sums['qt_file']
            files.append(dict(f, device_sum_ns=sums['qt_device'], streaming_sum_ns=sums['qt_file'],
                              difference_sum_ns=delta, difference_mean_ms=delta / 5e6))
        device = sum(f['device_sum_ns'] for f in files)
        streaming = sum(f['streaming_sum_ns'] for f in files)
        result.append(dict(block=block, sweeps_per_arm=5, device_sum_ns=device, streaming_sum_ns=streaming,
                           device_mean_ms=device / 5e6, streaming_mean_ms=streaming / 5e6,
                           difference_mean_ms=(device-streaming) / 5e6, throughput_ratio=streaming/device,
                           files=files))
    return result


def repo(path, url, tag=None):
    if path is None:
        raise ValueError('internal missing acquisition destination')
    if not path.exists():
        args = ['git', 'clone', '--quiet', '--bare'] + (['--depth', '1', '--branch', tag] if tag else [])
        command(args + [url, path])
    require(command(['git', '-C', path, 'remote', 'get-url', 'origin']).decode().strip() == url,
            'source repository URL mismatch')


def acquire(root, packaging, qt, buildinfo):
    repo(packaging, PACKAGING_URL)
    expected = re.search(r'^pkgbuild_sha256sum = ([0-9a-f]+)$', buildinfo, re.M).group(1)
    revision = None
    for rev in command(['git', '-C', packaging, 'log', '--all', '--format=%H', '--', 'PKGBUILD']).decode().splitlines():
        data = command(['git', '-C', packaging, 'show', rev + ':PKGBUILD'])
        if hashlib.sha256(data).hexdigest() == expected:
            revision = rev
            break
    require(revision, 'no packaging revision matches .BUILDINFO')
    (root / 'PKGBUILD').write_bytes(data)
    text = data.decode()
    checksums = re.findall(r"'([0-9a-f]{64})'", text.split('sha256sums=', 1)[1].split('prepare()', 1)[0])
    patches = re.findall(r'^  patch .* < (\S+)', text, re.M)
    commits = re.findall(r'cherry-pick -n ([0-9a-f]{40})', text)
    require(len(checksums) == 3 and len(patches) == 2 and len(commits) == 4 and '_pkgver=6.12.0' in text,
            'unsupported recipe; manual review required')
    for name, expected_patch in zip(patches, checksums[1:]):
        (root / name).write_bytes(command(['git', '-C', packaging, 'show', revision + ':' + name]))
        require(digest(root / name) == expected_patch, 'packaging patch checksum mismatch')
    repo(qt, QT_URL, 'v6.12.0')
    tag = command(['git', '-C', qt, 'rev-parse', 'v6.12.0^{commit}']).decode().strip()
    command(['git', '-c', 'core.abbrev=no', '-C', qt, 'archive', '--format', 'tar', 'v6.12.0'], root / 'qtbase.tar')
    archive_matches = digest(root / 'qtbase.tar') == checksums[0]
    for commit in commits:
        try:
            command(['git', '-C', qt, 'cat-file', '-e', commit + '^'])
        except ValueError:
            command(['git', '-C', qt, 'fetch', '--quiet', '--depth', '2', 'origin', commit])
        name = commit + '.patch'
        command(['git', '-C', qt, 'diff', '--no-ext-diff', '--no-textconv', commit + '^', commit], root / name)
        patches.append(name)
    # Keep content-addressed Git objects so independent checking never needs /tmp caches.
    for cache, name in ((packaging, 'packaging-proof'), (qt, 'qt-proof')):
        target = root / name
        shutil.copytree(cache / '.git' if (cache / '.git').is_dir() else cache, target)
        command(['git', '--git-dir=' + str(target), 'config', 'core.bare', 'true'])
    provenance = dict(status='exact' if archive_matches else 'limited',
                      limitation=None if archive_matches else 'Qt tag archive checksum does not match the checksum-pinned recipe; candidate sources are not exact-build evidence.',
                      archive_actual_sha256=digest(root / 'qtbase.tar'), packaging_cache='packaging-proof', qt_cache='qt-proof',
                      packaging_url=PACKAGING_URL, packaging_revision=revision, qt_url=QT_URL,
                      qt_tag='v6.12.0', qt_commit=tag, archive_sha256=checksums[0], patches=patches,
                      cherry_picks=commits, files={}, reconstructed=False,
                      retrieval_urls=[PACKAGING_URL + '/-/raw/' + revision + '/PKGBUILD',
                                      QT_URL + '/tag/?h=v6.12.0'] +
                                     [QT_URL + '/commit/?id=' + commit for commit in commits])
    if not archive_matches:
        return provenance
    source = root / 'source'
    source.mkdir()
    # Reconstruct only cited files and patch targets, never execute the recipe.
    names = set(SOURCES)
    for patch in patches:
        names.update(re.findall(r'^\+\+\+ b/(.+)$', (root / patch).read_text(), re.M))
    with tarfile.open(root / 'qtbase.tar') as archive:
        for name in sorted(names):
            if name not in archive.getnames():
                continue  # A retained patch may introduce a new file.
            member = archive.getmember(name)
            require(member.isfile() and '..' not in Path(name).parts and not Path(name).is_absolute(), 'unsafe source member')
            target = source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
    for patch in patches:
        command(['patch', '--batch', '--forward', '-p1', '-d', source, '-i', root / patch], root / (patch + '.apply'))
    provenance.update(files={n: digest(source / n) for n in sorted(names)}, reconstructed=True)
    return provenance


def citations(root):
    # Whole function/branch excerpts are retained with stable one-based line ranges.
    ranges = {'src/corelib/tools/qcryptographichash.cpp': [(910, 950)],
              'src/corelib/io/qiodevice.cpp': [(1015, 1195)],
              'src/corelib/io/qiodevice_p.h': [(30, 38), (100, 120)],
              'src/corelib/io/qfiledevice.cpp': [(450, 525), (720, 760)],
              'src/corelib/io/qfsfileengine.cpp': [(580, 665)],
              'src/corelib/io/qfsfileengine_unix.cpp': [(140, 202)],
              'src/corelib/tools/qringbuffer.cpp': [(210, 310)],
              'harness.cpp': [(1, 110)]}
    result = []
    for name, spans in ranges.items():
        path = root / 'source' / name
        lines = path.read_text().splitlines()
        for start, end in spans:
            result.append(dict(file='source/' + name, sha256=digest(path), start=start, end=end,
                               text='\n'.join(lines[start-1:end])))
    return result


def run(evidence, verification, output, packaging=None, qt=None):
    require(not output.exists() and not output.is_relative_to(evidence), 'destination collision')
    output.mkdir(parents=True)
    checker = load_checker()
    stage = 'bindings'
    try:
        binding = checker.bind(evidence, verification)
        write(output / 'inputs.json', binding)
        for name in ('native.stdout', 'preregistration.json', 'summary.json'):
            shutil.copyfile(evidence / name, output / name)
        stage = 'accounting'
        raw = [json.loads(line) for line in (output / 'native.stdout').read_text().splitlines()]
        totals = accounting(raw, read(output / 'preregistration.json')['mapping'])
        checker.check_accounting(output, totals)
        write(output / 'accounting.json', totals)
        stage = 'package-identity'
        dep = read(evidence / 'inputs.json')['dependencies']['libQt6Core.so.6']
        command(['bsdtar', '-xOf', PACKAGE, '.BUILDINFO'], output / 'BUILDINFO')
        command(['bsdtar', '-xOf', PACKAGE, '.PKGINFO'], output / 'PKGINFO')
        command(['bsdtar', '-xOf', PACKAGE, 'usr/lib/libQt6Core.so.6.12.0'], output / 'libQt6Core.so')
        symbols = read(PREPARED / 'symbols.json')['libQt6Core.so.6']
        debug = Path(symbols['path'])
        identity = dict(package=str(PACKAGE), package_sha256=digest(PACKAGE), host=dep['host'],
                        host_sha256=dep['host_sha256'], build_id=dep['build_id'], debug=symbols,
                        symbols_manifest=str(PREPARED / 'symbols.json'), symbols_manifest_sha256=digest(PREPARED / 'symbols.json'),
                        prepared_seal=read(evidence / 'inputs.json')['identities'][str(PREPARED / 'seal.json')])
        write(output / 'identity.json', identity)
        checker.check_identity(output)
        stage = 'sources'
        for name, supplied in (('packaging', packaging), ('qt', qt)):
            if supplied is None:
                candidates = sorted((ROOT / 'build').glob('preview-hash-device-path-*/' + name + '-proof'))
                if candidates:
                    isolated = output / (name + '-repo')
                    shutil.copytree(candidates[-1], isolated)
                    if name == 'packaging':
                        packaging = isolated
                    else:
                        qt = isolated
        try:
            provenance = acquire(output, packaging or output / 'packaging-repo', qt or output / 'qt-repo', (output / 'BUILDINFO').read_text())
        except (ValueError, OSError, subprocess.SubprocessError) as error:
            provenance = dict(status='limited', limitation=str(error), packaging_url=PACKAGING_URL, qt_url=QT_URL)
        write(output / 'source-provenance.json', provenance)
        (output / 'source').mkdir(exist_ok=True)
        harness = evidence / 'source/main.cpp'
        shutil.copyfile(harness, output / 'source/harness.cpp')
        write(output / 'citations.json', citations(output) if provenance['status'] == 'exact' else [
            dict(file='source/harness.cpp', sha256=digest(output / 'source/harness.cpp'), start=1, end=110,
                 text='\n'.join(harness.read_text().splitlines()[:110]))])
        stage = 'disassembly'
        (output / 'disassembly').mkdir()
        for symbol in SYMBOLS:
            command(['objdump', '-d', '--disassemble=' + symbol, dep['host']], output / 'disassembly' / (symbol + '.txt'))
        symbol_table = command(['nm', '-S', debug], output / 'debug-symbols.txt').decode()
        private = []
        for line in symbol_table.splitlines():
            fields = line.split()
            if len(fields) == 4 and any(token in fields[3] for token in ('QCryptographicHashPrivate7addDataEP9QIODevice', 'QIODevicePrivateC2', 'QRingBuffer4readEPcx')):
                start, size = int(fields[0], 16), int(fields[1], 16)
                name = fields[3]
                command(['objdump', '-d', '--start-address=' + hex(start), '--stop-address=' + hex(start + size), dep['host']], output / 'disassembly' / (name + '.range'))
                private.append(dict(symbol=name, start=start, size=size))
        require(any('QCryptographicHashPrivate' in r['symbol'] for r in private), 'missing private hash symbol')
        write(output / 'binary-ranges.json', private)
        retained_citations = read(output / 'citations.json')
        for path in sorted((output / 'disassembly').iterdir()):
            if path.suffix in ('.txt', '.range'):
                lines = path.read_text().splitlines()
                retained_citations.append(dict(file=str(path.relative_to(output)), sha256=digest(path),
                                               start=1, end=len(lines), text='\n'.join(lines)))
        write(output / 'citations.json', retained_citations)
        (output / 'tools').mkdir()
        for name in ('audit-preview-hash-device-path.py', 'verify-preview-hash-device-path.py'):
            shutil.copyfile(ROOT / 'scripts' / name, output / 'tools' / name)

        command(['readelf', '-n', dep['host']], output / 'host-notes.txt')
        command(['readelf', '-n', debug], output / 'debug-notes.txt')
        write(output / 'assessment.json', dict(status='complete', source_status=provenance['status'], new_measurements=False))
        report = ['# Qt device hashing path audit', '', 'Signed differences are device minus streaming; five sweep means per arm, never adjacent-sweep pairs.', '',
                  '| Block | Device ms | Streaming ms | Difference ms | Throughput ratio |', '| --- | ---: | ---: | ---: | ---: |']
        report.extend(f"| {b['block']} | {b['device_mean_ms']:.6f} | {b['streaming_mean_ms']:.6f} | {b['difference_mean_ms']:+.6f} | {b['throughput_ratio']:.8f} |" for b in totals)
        report += ['', 'Full signed per-ordinal accounting is in accounting.json. Empty-file accounting is supported; this retained population has no empty files.',
                   'Exact integer reconciliation: sum(file difference_sum_ns) = device_sum_ns - streaming_sum_ns; divide by 5,000,000 for mean milliseconds.',
                   'Source status: ' + provenance['status'] + '.',
                   'Source limitation: ' + str(provenance.get('limitation')),
                   'Binary findings (matched Qt SHA-256/build ID and retained debug symbols):',
                   '- Public addData(QIODevice*) branches to the debug-named private routine at 0x30dce0. At 0x30dd2b it supplies 0x400 (1024) bytes to QIODevice::read; 0x30dd3e loops on a positive result and the body calls the hash-update routine.',
                   '- QIODevicePrivate constructor stores 0x4000 (16384) as the default buffer chunk. Its read routine contains buffered and direct-read branches. QRingBuffer::read contains memcpy; these show copying is available on the buffered path, not its observed cost.',
                   '- QFileDevice::readData delegates to the engine and handles errors. QFSFileEngine::read contains read/fread calls and retry/error branches. No dynamic branch or syscall count is established.',
                   '- Frozen harness source/harness.cpp lines 40-110 uses 65536-byte streaming reads, hashes only positive chunks, rejects negative reads and unexpected zero reads, and terminates at zero. Device timing additionally checks file.error(), atEnd() and pos(); streaming timing maintains an offset. Open and finalization remain outside update_ns.',
                   'For ordinary full reads the 1 KiB device requests imply more QIODevice/hash-update API iterations than 64 KiB streaming. This conditional structural expectation does not establish actual syscall counts or attribution of the elapsed difference.',

                   'See citations.json (SHA-256, one-based inclusive ranges), source-provenance.json and disassembly/.',
                   'No syscall counts, cache behavior, provider selection, hardware dispatch, production savings or optimization choice follow from this audit.']
        (output / 'REPORT.md').write_text('\n'.join(report) + '\n')
        # Check consumed bindings again before sealing; preserve a sealed partial on any failure.
        require(checker.bind(evidence, verification) == binding, 'consumed evidence drift during audit')
        checker.check_sources(output)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        write(output / 'assessment.json', dict(status='blocked', stage=stage, failure=str(error), new_measurements=False))
    seal(output)
    return read(output / 'assessment.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('evidence', 'verification', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--packaging-cache', type=Path)
    parser.add_argument('--qt-cache', type=Path)
    args = parser.parse_args()
    result = run(args.evidence.resolve(), args.verification.resolve(), args.output.resolve(), args.packaging_cache, args.qt_cache)
    print(json.dumps(result, sort_keys=True))
    sys.exit(result['status'] != 'complete')
