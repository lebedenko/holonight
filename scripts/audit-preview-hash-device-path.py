#!/usr/bin/env python3
"""Audit retained Qt hashing evidence; never execute a workload or packaging script."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

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


def command(args, output=None, env=None):
    result = subprocess.run([str(a) for a in args], capture_output=True, timeout=180, env=env)
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
        raise ValueError('retained local repository required; network acquisition disabled')
    require(command(['git', '-C', path, 'remote', 'get-url', 'origin']).decode().strip() == url,
            'source repository URL mismatch')


def archive_policy(root, qt, buildinfo):
    installed = re.search(r'^installed = (pacman-[^\n]+)$', buildinfo, re.M).group(1)
    package = Path('/var/cache/pacman/pkg') / (installed + '.pkg.tar.zst')
    members = command(['bsdtar', '-tf', package]).decode().splitlines()
    retained = {}
    for member, name in (('.PKGINFO', 'pacman-PKGINFO'),
                         ('usr/share/makepkg/source/git.sh', 'makepkg-git.sh')):
        command(['bsdtar', '-xOf', package, member], root / name)
        retained[member] = dict(file=name, sha256=digest(root / name))
    config = 'etc/makepkg.d/gitconfig'
    if config in members:
        command(['bsdtar', '-xOf', package, config], root / 'makepkg-gitconfig')
    else:
        (root / 'makepkg-gitconfig').write_text('')
    helper = (root / 'makepkg-git.sh').read_text()
    require('export GIT_CONFIG_GLOBAL=/dev/null' in helper and
            '* -export-subst -export-ignore' in helper, 'unsupported makepkg helper')
    gitdir = Path(command(['git', '-C', qt, 'rev-parse', '--absolute-git-dir']).decode().strip())
    (gitdir / 'info').mkdir(exist_ok=True)
    (gitdir / 'info/attributes').write_text('* -export-subst -export-ignore\n')
    policy = dict(version='makepkg-git-v1', package=str(package), package_sha256=digest(package),
                  installed=installed, members=retained, config_present=config in members,
                  config_sha256=digest(root / 'makepkg-gitconfig'))
    write(root / 'archive-policy.json', policy)
    return dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null',
                GIT_CONFIG_SYSTEM=str((root / 'makepkg-gitconfig').resolve()), GIT_CONFIG_COUNT='0')


def expected_patch(before, patch):
    """Check every hunk, allowing only the recipe's reviewed context difference."""
    expected = dict(before)
    sections = re.split(r'^diff --git ', patch, flags=re.M)[1:]
    for section in sections:
        name = re.search(r'^--- a/(.+)$', section, re.M).group(1)
        original = expected[name].decode().splitlines(keepends=True)
        for header, body in re.findall(r'^@@ ([^\n]+)@@[^\n]*\n(.*?)(?=^@@ |\Z)', section, re.M | re.S):
            lines = [line for line in body.splitlines(keepends=True) if line[:1] in (' ', '+', '-')]
            old = [line[1:] for line in lines if line[0] != '+']
            new = [line[1:] for line in lines if line[0] != '-']
            special = name == 'mkspecs/common/gcc-base.conf' and header.startswith('-40,9 ')
            candidates = []
            for pos in range(len(original) - len(old) + 1):
                candidate = original[pos:pos + len(old)]
                if candidate == old or (special and candidate[:-1] == old[:-1]
                        and candidate[-1].startswith('QMAKE_CFLAGS_APP ')):
                    candidates.append(pos)
            require(len(candidates) == 1, 'ambiguous or unintended patch placement')
            pos = candidates[0]
            if special:
                require(old[-1].startswith('QMAKE_CFLAGS_APP '), 'unexpected fuzz context')
                new[-1] = original[pos + len(old) - 1]
            original[pos:pos + len(old)] = new
        expected[name] = ''.join(original).encode()
    return expected


def prepare(root, qt, tag, patches, commits, temporary):
    environment = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    environment.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_SYSTEM='/dev/null',
                       GIT_CONFIG_COUNT='0', LC_ALL='C', GIT_TERMINAL_PROMPT='0')
    work = temporary / 'work'
    git = ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgSign=false',
           '-c', 'user.name=Audit', '-c', 'user.email=audit@example.invalid', '-C', str(work)]
    command(['git', 'init', '--quiet', '--template=', work], env=environment)
    gitdir = qt / '.git' if (qt / '.git').is_dir() else qt
    require(not (gitdir / 'objects/info/alternates').exists(), 'external object store unsupported')
    shutil.copytree(gitdir / 'objects', work / '.git/objects', dirs_exist_ok=True)
    if (gitdir / 'shallow').exists():
        shutil.copyfile(gitdir / 'shallow', work / '.git/shallow')
    revision = command(['git', '-C', qt, 'rev-parse', tag + '^{commit}'], env=environment).decode().strip()
    command(git + ['checkout', '--quiet', '--detach', revision], env=environment)
    tools = {}
    buildinfo = (root / 'BUILDINFO').read_text()
    for tool in ('git', 'patch'):
        executable = Path(shutil.which(tool)).resolve()
        version = command([executable, '--version'], env=environment).decode().splitlines()[0]
        installed = re.search(r'^installed = (' + tool + r'-([^\n]+))$', buildinfo, re.M)
        require(installed and version.split()[-1] == installed.group(2).rsplit('-', 2)[0], 'preparation tool version mismatch')
        tools[tool] = dict(path=str(executable), sha256=digest(executable), version=version, installed=installed.group(1))
    # Compare all archive entries, including executable bits and symbolic links.
    with tarfile.open(root / 'qtbase.tar') as archive:
        for member in archive:
            path = work / member.name
            require(not Path(member.name).is_absolute() and '..' not in Path(member.name).parts, 'unsafe archive path')
            if member.isfile():
                require(path.is_file() and path.read_bytes() == archive.extractfile(member).read()
                        and bool(path.stat().st_mode & 0o111) == bool(member.mode & 0o111), 'starting archive content mismatch')
            elif member.issym():
                require(path.is_symlink() and os.readlink(path) == member.linkname, 'starting symlink mismatch')
    tracked = set()
    for name in patches:
        tracked.update(re.findall(r'^(?:\+\+\+ b/|--- a/)(.+)$', (root / name).read_text(), re.M))
    for commit in commits:
        tracked.update(command(git + ['diff', '--no-renames', '--name-only', '-z', commit + '^', commit], env=environment).decode().strip('\0').split('\0'))
    tracked.discard('')
    def state():
        diff = command(git + ['diff', '--binary', '--no-ext-diff', '--no-textconv', 'HEAD'], env=environment)
        index = command(git + ['diff', '--cached', '--binary', '--no-ext-diff', '--no-textconv'], env=environment)
        return dict(worktree_sha256=hashlib.sha256(diff).hexdigest(), index_sha256=hashlib.sha256(index).hexdigest(),
                    files={n: dict(sha256=digest(work / n), executable=bool((work / n).stat().st_mode & 0o111))
                           if (work / n).is_file() else None for n in sorted(tracked | {n + suffix for n in tracked for suffix in ('.orig', '.rej')
                                              if (work / (n + suffix)).is_file()})})
    operations = []
    limitation = None
    for kind, target in [('patch', p) for p in patches] + [('cherry-pick', c) for c in commits]:
        before = state()
        intended = None
        validation_error = None
        if kind == 'patch':
            patch = (root / target).read_text()
            names = re.findall(r'^--- a/(.+)$', patch, re.M)
            try:
                intended = expected_patch({n: (work / n).read_bytes() for n in names}, patch)
            except (ValueError, KeyError, OSError) as error:
                validation_error = str(error)
        args = (['patch', '--batch', '--forward', '-p1', '-i', str((root / target).resolve())]
                if kind == 'patch' else git + ['cherry-pick', '-n', target])
        result = subprocess.run(args, cwd=work, env=environment, capture_output=True, timeout=180)
        stdout, stderr = result.stdout.decode(), result.stderr.decode()
        normalized = ['patch', '--batch', '--forward', '-p1', '-i', target] if kind == 'patch' else ['git', 'cherry-pick', '-n', target]
        operation = dict(argv=normalized, returncode=result.returncode, stdout=stdout, stderr=stderr, before=before, after=state())
        operations.append(operation)
        if result.returncode:
            limitation = kind + ' failed: ' + target
        elif kind == 'patch':
            fuzz = re.findall(r'Hunk #(\d+) succeeded at (\d+) with fuzz (\d+)', stdout)
            if fuzz != ([('1', '40', '1')] if target == 'qt6-base-cflags.patch' else []):
                limitation = 'unexpected fuzz: ' + target
            if validation_error:
                limitation = 'patch preimage validation failed: ' + target
            elif any((work / n).read_bytes() != data for n, data in intended.items()):
                limitation = 'unintended patch edits: ' + target
        if limitation:
            break
    return dict(policy='recipe-prepare-v1', tools=tools, operations=operations,
                passed=limitation is None, limitation=limitation)


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
    environment = archive_policy(root, qt, buildinfo)
    args = ['git', '-c', 'core.abbrev=no', '-C', qt, 'archive', '--format', 'tar', 'v6.12.0']
    write(root / 'archive-command.json', dict(argv=[str(a) for a in args], environment={k: environment[k] for k in ('GIT_CONFIG_GLOBAL', 'GIT_CONFIG_SYSTEM', 'GIT_CONFIG_COUNT')}))
    command(args, root / 'qtbase.tar', env=environment)
    archive_matches = digest(root / 'qtbase.tar') == checksums[0]
    for commit in commits:
        try:
            command(['git', '-C', qt, 'cat-file', '-e', commit + '^'])
        except ValueError:
            raise ValueError('missing retained cherry-pick parent: ' + commit)
        name = commit + '.patch'
        command(['git', '-C', qt, 'diff', '--no-ext-diff', '--no-textconv', commit + '^', commit], root / name)
        patches.append(name)
    # Keep content-addressed Git objects so independent checking never needs /tmp caches.
    for cache, name in ((packaging, 'packaging-proof'), (qt, 'qt-proof')):
        target = root / name
        shutil.copytree(cache / '.git' if (cache / '.git').is_dir() else cache, target)
        command(['git', '--git-dir=' + str(target), 'config', 'core.bare', 'true'])
    provenance = dict(archive_policy='makepkg-git-v1', status='exact' if archive_matches else 'limited',
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
    provenance['reconstruction_policy'] = 'recipe-prepare-v1'
    provenance['source_names'] = sorted(set(SOURCES) | {
        name for patch in patches for name in re.findall(r'^(?:\+\+\+ b/|--- a/)(.+)$', (root / patch).read_text(), re.M)})
    for commit in commits:
        provenance['source_names'] = sorted(set(provenance['source_names']) | set(command(
            ['git', '-C', qt, 'diff', '--no-renames', '--name-only', '-z', commit + '^', commit]).decode().strip('\0').split('\0')))
    with tempfile.TemporaryDirectory() as temporary:
        preparation = prepare(root, qt, tag, patches[:2], commits, Path(temporary))
        write(root / 'preparation.json', preparation)
        names = provenance['source_names']
        provenance['source_names'] = sorted(set(names) | {n + suffix for n in names for suffix in ('.orig', '.rej')
            if (Path(temporary) / 'work' / (n + suffix)).is_file()})
        source = root / 'source'
        source.mkdir()
        for name in provenance['source_names']:
            path = Path(temporary) / 'work' / name
            if path.is_file():
                target = source / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
        provenance.update(files={n: digest(source / n) if (source / n).exists() else None
                                 for n in provenance['source_names']},
                          reconstructed=preparation['passed'],
                          status='exact' if preparation['passed'] else 'limited',
                          limitation=preparation['limitation'])
    return provenance


def citations(root):
    selectors = {
        'src/corelib/tools/qcryptographichash.cpp': [r'bool QCryptographicHash::addData\(QIODevice', r'bool QCryptographicHashPrivate::addData\(QIODevice'],
        'src/corelib/io/qiodevice.cpp': [r'qint64 QIODevicePrivate::read\(', r'qint64 QIODevice::read\(char'],
        'src/corelib/io/qfiledevice.cpp': [r'qint64 QFileDevice::readData\(', r'bool QFileDevice::atEnd\('],
        'src/corelib/io/qfsfileengine.cpp': [r'qint64 QFSFileEngine::read\(', r'qint64 QFSFileEnginePrivate::readFdFh\('],
        'src/corelib/io/qfsfileengine_unix.cpp': [r'qint64 QFSFileEnginePrivate::nativeRead\('],
        'src/corelib/tools/qringbuffer.cpp': [r'qint64 QRingBuffer::read\('],
    }
    result = []
    for name, patterns in selectors.items():
        path = root / 'source' / name
        text = path.read_text()
        for pattern in patterns:
            matches = list(re.finditer(pattern, text))
            require(len(matches) == 1, 'ambiguous/missing citation function: ' + pattern)
            start = text.count('\n', 0, matches[0].start()) + 1
            opening = text.index('{', matches[0].end())
            depth = 1
            closing = opening
            while depth:
                closing += 1
                depth += (text[closing] == '{') - (text[closing] == '}')
            end = text.count('\n', 0, closing) + 1
            result.append(dict(file='source/' + name, sha256=digest(path), start=start, end=end,
                               selector=pattern, text='\n'.join(text.splitlines()[start-1:end])))
    for name in ('src/corelib/io/qiodevice_p.h', 'harness.cpp'):
        path = root / 'source' / name
        lines = path.read_text().splitlines()
        result.append(dict(file='source/' + name, sha256=digest(path), start=1, end=len(lines), text='\n'.join(lines)))
    for name in ('makepkg-git.sh', 'pacman-PKGINFO', 'makepkg-gitconfig'):
        path = root / name
        lines = path.read_text().splitlines()
        if lines:
            result.append(dict(file=name, sha256=digest(path), start=1, end=len(lines), text='\n'.join(lines)))
    return result


def run(evidence, verification, output, packaging=None, qt=None, prior_audit=None, prior_verification=None):
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
        require((prior_audit is None) == (prior_verification is None), 'paired prior audit options required')
        if prior_audit is not None:
            checker.check_prior(prior_audit, prior_verification)
            write(output / 'prior.json', dict(audit=str(prior_audit), verification=str(prior_verification),
                                             audit_seal=digest(prior_audit / 'seal.json'),
                                             verification_sha256=digest(prior_verification)))
            for name in ('packaging', 'qt'):
                isolated = output / (name + '-repo')
                shutil.copytree(prior_audit / (name + '-proof'), isolated)
                if name == 'packaging':
                    packaging = isolated
                else:
                    qt = isolated
        if prior_audit is None:
            for name, supplied in (('packaging', packaging), ('qt', qt)):
                if supplied is not None:
                    isolated = output / (name + '-repo')
                    shutil.copytree(supplied / '.git' if (supplied / '.git').is_dir() else supplied, isolated)
                    command(['git', '--git-dir=' + str(isolated), 'config', 'core.bare', 'true'])
                    if name == 'packaging':
                        packaging = isolated
                    else:
                        qt = isolated
        try:
            provenance = acquire(output, packaging or output / 'packaging-repo', qt or output / 'qt-repo', (output / 'BUILDINFO').read_text())
        except (ValueError, OSError, subprocess.SubprocessError) as error:
            provenance = dict(archive_policy='makepkg-git-v1', status='limited', limitation=str(error), packaging_url=PACKAGING_URL, qt_url=QT_URL)
        write(output / 'source-provenance.json', provenance)
        (output / 'source').mkdir(exist_ok=True)
        harness = evidence / 'source/main.cpp'
        shutil.copyfile(harness, output / 'source/harness.cpp')
        write(output / 'citations.json', citations(output) if provenance['status'] == 'exact' else [
            dict(file='source/harness.cpp', sha256=digest(output / 'source/harness.cpp'), start=1, end=110,
                 text='\n'.join(harness.read_text().splitlines()[:110]))])
        if (output / 'archive-policy.json').exists() and provenance['status'] != 'exact':
            retained = read(output / 'citations.json')
            for name in ('makepkg-git.sh', 'pacman-PKGINFO'):
                path = output / name
                lines = path.read_text().splitlines()
                retained.append(dict(file=name, sha256=digest(path), start=1, end=len(lines), text='\n'.join(lines)))
            write(output / 'citations.json', retained)
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
        if provenance['status'] == 'exact':
            report += ['', 'Verified recipe-prepared source trace (inclusive function ranges are in citations.json):',
                       '- QCryptographicHash::addData forwards to its private routine, which reads 1024-byte chunks, updates on positive reads and returns device->atEnd(). This corroborates the matched 0x400 request and positive-read loop in disassembly.',
                       '- QIODevicePrivate::read first consumes the ring buffer. With buffering enabled and no transaction/peek retention, requests below readBufferChunkSize refill the ring buffer; requests at least that size can read directly into the caller buffer. The default chunk is 16384 bytes. QRingBuffer::read copies with memcpy, consistent with retained disassembly.',
                       '- QFileDevice::readData checks flushing, delegates to the engine, propagates errors and invalidates cached size after short reads. QFileDevice::atEnd checks buffered data and engine/size state.',
                       '- QFSFileEngine::read delegates to nativeRead. On Unix, nativeRead handles sequential FILE streams specially and otherwise delegates to readFdFh, whose FILE/fd branches use fread/read with EINTR and error handling. These branches corroborate the matched binary calls; they do not identify runtime branch selection.',
                       'Exact source means verified recipe-prepared contents of retained files. It does not prove reproducible compilation, syscall counts, branch selection or elapsed-cost attribution.']
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
    parser.add_argument('--prior-audit', type=Path)
    parser.add_argument('--prior-verification', type=Path)
    args = parser.parse_args()
    result = run(args.evidence.resolve(), args.verification.resolve(), args.output.resolve(), args.packaging_cache, args.qt_cache, args.prior_audit.resolve() if args.prior_audit else None, args.prior_verification.resolve() if args.prior_verification else None)
    print(json.dumps(result, sort_keys=True))
    sys.exit(result['status'] != 'complete')
