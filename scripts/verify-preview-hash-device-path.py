#!/usr/bin/env python3
"""Independent stdlib-only device-path audit checker; does not import the auditor."""
import argparse
from fractions import Fraction
import hashlib
import json
import os
import shutil
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile


def check(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            check(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def sealed(root):
    actual = {}
    for path in root.rglob('*'):
        check(not path.is_symlink(), 'symlink in evidence')
        if path.is_file() and path != root / 'seal.json':
            actual[str(path.relative_to(root))] = digest(path)
    check(actual == read(root / 'seal.json'), 'seal mismatch: ' + str(root))


def build_id(path):
    result = subprocess.check_output(['readelf', '-n', str(path)], text=True, timeout=30)
    ids = re.findall(r'Build ID: ([0-9a-f]+)', result)
    check(len(ids) == 1, 'missing/ambiguous build ID')
    return ids[0]


def bind(evidence, verification):
    sealed(evidence)
    passed = read(verification)
    check(passed['status'] == 'passed' and passed['evidence_seal'] == digest(evidence / 'seal.json') and
          (passed['measured_sweeps'], passed['warmup_sweeps'], passed['measured_rows'], passed['warmup_rows']) ==
          (125, 5, 7500, 300), 'independent verification binding mismatch')
    assessment = read(evidence / 'assessment.json')
    check(assessment['status'] == 'complete', 'incomplete diagnostic')
    identities = dict(read(evidence / 'inputs.json')['identities'])
    identities[str(evidence / 'seal.json')] = digest(evidence / 'seal.json')
    identities[str(verification)] = digest(verification)
    for name, expected in identities.items():
        path = Path(name)
        check(digest(path) == expected, 'consumed identity drift: ' + name)
        if path.name == 'seal.json':
            sealed(path.parent)
    return dict(evidence=str(evidence), verification=str(verification), identities=identities)


def check_accounting(root, saved):
    registration = read(root / 'preregistration.json')
    mapping = registration['mapping']
    check([f['ordinal'] for f in mapping] == list(range(len(mapping))), 'mapping ordinals')
    # Replay every raw row in fixed registered order, independently of auditor grouping.
    schedule = registration['schedule']
    cases = ('qt_device', 'qt_file', 'evp_file', 'qt_memory', 'evp_memory')
    expected_schedule = [dict(case=c, block=None, warmup=True, sweep=0) for c in cases]
    for block in range(5):
        for case in cases[block:] + cases[:block]:
            expected_schedule += [dict(case=case, block=block, warmup=False, sweep=s) for s in range(5)]
    check(schedule == [dict(index=i, **s) for i, s in enumerate(expected_schedule)], 'schedule drift')
    lines = iter((root / 'native.stdout').read_text().splitlines())
    check(json.loads(next(lines))['type'] == 'identity', 'missing native identity')
    sums = {(b, c, f['ordinal']): 0 for b in range(5) for c in cases[:2] for f in mapping}
    for sweep in schedule:
        duration = 0
        for f in mapping:
            row = json.loads(next(lines))
            check(row['type'] == 'file' and all(row[k] == value for k, value in sweep.items()) and
                  (row['ordinal'], row['bytes'], row['sha256']) == (f['ordinal'], f['size'], f['sha256']),
                  'missing/duplicate ordinal or raw schedule drift')
            check(all(type(row[k]) is int and row[k] > 0 for k in ('init_ns', 'update_ns', 'final_ns')), 'invalid raw duration')
            duration += sum(row[k] for k in ('init_ns', 'update_ns', 'final_ns'))
            if not sweep['warmup'] and sweep['case'] in cases[:2]:
                sums[sweep['block'], sweep['case'], f['ordinal']] += row['update_ns']
        end = json.loads(next(lines))
        check(end['type'] == 'sweep_end' and end['index'] == sweep['index'] and
              duration <= end['elapsed_ns'] <= 30000000000, 'sweep completion drift')
    check(next(lines, None) is None, 'extra raw rows')
    check(len(saved) == 5, 'accounting blocks')
    summary = read(root / 'summary.json')
    for b, block in enumerate(saved):
        check(block['block'] == b and block['sweeps_per_arm'] == 5 and len(block['files']) == len(mapping), 'block shape')
        device = streaming = contributions = 0
        for f, actual in zip(mapping, block['files']):
            d, s = (sums[b, c, f['ordinal']] for c in cases[:2])
            check(actual == dict(f, device_sum_ns=d, streaming_sum_ns=s, difference_sum_ns=d-s,
                                 difference_mean_ms=float(Fraction(d-s, 5000000))), 'per-file accounting mismatch')
            device += d
            streaming += s
            contributions += actual['difference_sum_ns']
        expected = dict(block=b, sweeps_per_arm=5, device_sum_ns=device, streaming_sum_ns=streaming,
                        device_mean_ms=float(Fraction(device, 5000000)), streaming_mean_ms=float(Fraction(streaming, 5000000)),
                        difference_mean_ms=float(Fraction(device-streaming, 5000000)),
                        throughput_ratio=float(Fraction(streaming, device)), files=block['files'])
        check(block == expected and contributions == device-streaming, 'block arithmetic/reconciliation mismatch')
        old = next(r for r in summary['ratios'] if r['block'] == b and r['numerator'] == 'qt_device' and r['denominator'] == 'qt_file')
        check(abs(old['ratio'] - block['throughput_ratio']) < 1e-15, 'retained throughput ratio drift')


def check_identity(root):
    identity = read(root / 'identity.json')
    check(digest(Path(identity['package'])) == identity['package_sha256'], 'package identity mismatch')
    check(digest(root / 'libQt6Core.so') == digest(Path(identity['host'])) == identity['host_sha256'], 'package/host mismatch')
    check(build_id(root / 'libQt6Core.so') == build_id(Path(identity['host'])) == identity['build_id'], 'package build ID mismatch')
    # Re-extract metadata and Qt bytes independently; a resealed substituted member must fail.
    for member, name in (('.BUILDINFO', 'BUILDINFO'), ('.PKGINFO', 'PKGINFO'), ('usr/lib/libQt6Core.so.6.12.0', 'libQt6Core.so')):
        data = subprocess.check_output(['bsdtar', '-xOf', identity['package'], member], timeout=60)
        check(data == (root / name).read_bytes(), 'package member mismatch: ' + member)
    check('pkgver = 6.12.0-5\n' in (root / 'BUILDINFO').read_text(), 'wrong package version')
    manifest = Path(identity['symbols_manifest'])
    check(digest(manifest) == identity['symbols_manifest_sha256'], 'debug manifest mismatch')
    check(read(manifest)['libQt6Core.so.6'] == identity['debug'], 'debug provenance mismatch')
    prepared = manifest.parent
    check(digest(prepared / 'seal.json') == identity['prepared_seal'], 'debug prepared binding mismatch')
    sealed(prepared)
    debug = identity['debug']
    check(digest(Path(debug['path'])) == debug['sha256'] and build_id(Path(debug['path'])) ==
          debug['build_id'] == identity['build_id'], 'debug identity mismatch')


def check_citations(root):
    for citation in read(root / 'citations.json'):
        path = root / citation['file']
        check(path.resolve().is_relative_to(root.resolve()), 'citation path escape')
        lines = path.read_text().splitlines()
        start, end = citation['start'], citation['end']
        check(digest(path) == citation['sha256'] and 1 <= start <= end <= len(lines) and
              '\n'.join(lines[start-1:end]) == citation['text'], 'citation drift')


def check_prior(audit, verification):
    sealed(audit)
    passed = read(verification)
    check(passed['status'] == 'passed' and passed['audit_seal'] == digest(audit / 'seal.json'),
          'prior verification binding mismatch')
    check(read(audit / 'assessment.json')['status'] == 'complete', 'incomplete prior audit')


def policy_environment(root, qt, directory):
    policy = read(root / 'archive-policy.json')
    check(policy['version'] == 'makepkg-git-v1', 'unsupported archive policy')
    installed = re.search(r'^installed = (pacman-[^\n]+)$', (root / 'BUILDINFO').read_text(), re.M).group(1)
    package = Path(policy['package'])
    check(policy['installed'] == installed and digest(package) == policy['package_sha256'], 'pacman binding mismatch')
    info = subprocess.check_output(['bsdtar', '-xOf', package, '.PKGINFO']).decode()
    check('pkgname = pacman\n' in info and
          'pkgver = ' + installed[len('pacman-'):].rsplit('-', 1)[0] + '\n' in info, 'pacman version mismatch')
    check(set(policy['members']) == {'.PKGINFO', 'usr/share/makepkg/source/git.sh'}, 'missing makepkg members')
    for member, retained in policy['members'].items():
        data = subprocess.check_output(['bsdtar', '-xOf', package, member])
        check(data == (root / retained['file']).read_bytes() and digest(root / retained['file']) == retained['sha256'], 'makepkg member mismatch')
    members = subprocess.check_output(['bsdtar', '-tf', package]).decode().splitlines()
    present = 'etc/makepkg.d/gitconfig' in members
    check(present == policy['config_present'], 'makepkg config presence mismatch')
    config = subprocess.check_output(['bsdtar', '-xOf', package, 'etc/makepkg.d/gitconfig']) if present else b''
    check(config == (root / 'makepkg-gitconfig').read_bytes() and
          digest(root / 'makepkg-gitconfig') == policy['config_sha256'], 'makepkg config mismatch')
    check((qt / 'info/attributes').read_text() == '* -export-subst -export-ignore\n', 'archive attributes mismatch')
    isolated = directory / 'qt'
    shutil.copytree(qt, isolated)
    (isolated / 'info/attributes').write_text('* -export-subst -export-ignore\n')
    return isolated, dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null',
                          GIT_CONFIG_SYSTEM=str((root / 'makepkg-gitconfig').resolve()), GIT_CONFIG_COUNT='0')


def replay_preparation(root, provenance, package_patches, commits):
    retained = read(root / 'preparation.json')
    check(retained['policy'] == 'recipe-prepare-v1', 'preparation policy mismatch')
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_SYSTEM='/dev/null',
               GIT_CONFIG_COUNT='0', LC_ALL='C', GIT_TERMINAL_PROMPT='0')
    tools = {}
    for name in ('git', 'patch'):
        executable = Path(shutil.which(name)).resolve()
        version = subprocess.check_output([executable, '--version'], env=env, text=True).splitlines()[0]
        installed = re.search(r'^installed = (' + name + r'-([^\n]+))$', (root / 'BUILDINFO').read_text(), re.M)
        check(installed and installed.group(2).rsplit('-', 2)[0] == version.split()[-1], 'tool/buildinfo mismatch')
        tools[name] = dict(path=str(executable), sha256=digest(executable), version=version, installed=installed.group(1))
    check(tools == retained['tools'], 'preparation tool identity drift')
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary) / 'tree'
        subprocess.run(['git', 'init', '--quiet', '--template=', str(work)], env=env, check=True, capture_output=True)
        objects = root / provenance['qt_cache']
        if (objects / '.git').is_dir():
            objects = objects / '.git'
        check(not (objects / 'objects/info/alternates').exists(), 'external object store unsupported')
        shutil.copytree(objects / 'objects', work / '.git/objects', dirs_exist_ok=True)
        if (objects / 'shallow').exists():
            shutil.copyfile(objects / 'shallow', work / '.git/shallow')
        prefix = ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgSign=false',
                  '-c', 'user.name=Audit', '-c', 'user.email=audit@example.invalid', '-C', str(work)]
        def git(*args):
            return subprocess.check_output(prefix + list(args), env=env, stderr=subprocess.PIPE)
        git('checkout', '--quiet', '--detach', provenance['qt_commit'])
        with tarfile.open(root / 'qtbase.tar') as archive:
            for member in archive:
                check(not Path(member.name).is_absolute() and '..' not in Path(member.name).parts, 'unsafe archive path')
                path = work / member.name
                if member.isfile():
                    check(path.read_bytes() == archive.extractfile(member).read(), 'initial archive bytes mismatch')
                    check(bool(path.stat().st_mode & 0o111) == bool(member.mode & 0o111), 'initial archive mode mismatch')
                if member.issym():
                    check(path.is_symlink() and os.readlink(path) == member.linkname, 'initial archive link mismatch')
        paths = set()
        for patch in package_patches:
            paths.update(re.findall(r'^(?:\+\+\+ b/|--- a/)(.+)$', (root / patch).read_text(), re.M))
        for commit in commits:
            paths.update(git('diff', '--no-renames', '--name-only', '-z', commit + '^', commit).decode().strip('\0').split('\0'))
        paths.discard('')
        def snapshot():
            return dict(worktree_sha256=hashlib.sha256(git('diff', '--binary', '--no-ext-diff', '--no-textconv', 'HEAD')).hexdigest(),
                        index_sha256=hashlib.sha256(git('diff', '--cached', '--binary', '--no-ext-diff', '--no-textconv')).hexdigest(),
                        files={name: dict(sha256=digest(work / name), executable=bool((work / name).stat().st_mode & 0o111))
                               if (work / name).is_file() else None for name in sorted(paths | {name + suffix for name in paths for suffix in ('.orig', '.rej')
                                                  if (work / (name + suffix)).is_file()})})
        operations = []
        failure = None
        for kind, target in [('patch', name) for name in package_patches] + [('cherry-pick', commit) for commit in commits]:
            before = snapshot()
            expected_files = {}
            if kind == 'patch':
                validation_error = None
                try:
                    # Independently derive whole-file expectations from unique hunk preimages.
                    patch_text = (root / target).read_text()
                    filename = None
                    lines = patch_text.splitlines(keepends=True)
                    i = 0
                    while i < len(lines):
                        line = lines[i]
                        if line.startswith('--- a/'):
                            filename = line[6:].strip()
                            expected_files[filename] = (work / filename).read_text()
                        if line.startswith('@@ '):
                            hunk_header = line
                            hunk = []
                            i += 1
                            while i < len(lines) and lines[i][:1] in (' ', '-', '+') and not lines[i].startswith('--- a/'):
                                hunk.append(lines[i]); i += 1
                            old = ''.join(x[1:] for x in hunk if x[0] != '+')
                            new = ''.join(x[1:] for x in hunk if x[0] != '-')
                            text = expected_files[filename]
                            if filename == 'mkspecs/common/gcc-base.conf' and hunk_header.startswith('@@ -40,9 '):
                                old_lines = old.splitlines(keepends=True)
                                check(old_lines[-1].startswith('QMAKE_CFLAGS_APP '), 'unreviewed fuzz context')
                                stem = ''.join(old_lines[:-1])
                                check(text.count(stem) == 1, 'ambiguous fuzz placement')
                                pos = text.index(stem) + len(stem)
                                context = text[pos:text.index('\n', pos) + 1]
                                check(context.startswith('QMAKE_CFLAGS_APP '), 'unexpected fuzz context')
                                old = stem + context
                                new = ''.join(new.splitlines(keepends=True)[:-1]) + context
                            check(text.count(old) == 1, 'ambiguous patch preimage')
                            expected_files[filename] = text.replace(old, new, 1)
                            continue
                        i += 1
                except (ValueError, KeyError, OSError) as error:
                    validation_error = str(error)
                args = ['patch', '--batch', '--forward', '-p1', '-i', str((root / target).resolve())]
                argv = ['patch', '--batch', '--forward', '-p1', '-i', target]
            else:
                args = prefix + ['cherry-pick', '-n', target]
                argv = ['git', 'cherry-pick', '-n', target]
            result = subprocess.run(args, cwd=work, env=env, capture_output=True, timeout=180)
            stdout = result.stdout.decode()
            operations.append(dict(argv=argv, returncode=result.returncode, stdout=stdout,
                                   stderr=result.stderr.decode(), before=before, after=snapshot()))
            if result.returncode:
                failure = kind + ' failed: ' + target
            elif kind == 'patch':
                expected_fuzz = [('1', '40', '1')] if target == 'qt6-base-cflags.patch' else []
                if re.findall(r'Hunk #(\d+) succeeded at (\d+) with fuzz (\d+)', stdout) != expected_fuzz:
                    failure = 'unexpected fuzz: ' + target
                if validation_error:
                    failure = 'patch preimage validation failed: ' + target
                elif any((work / name).read_text() != text for name, text in expected_files.items()):
                    failure = 'unintended patch edits: ' + target
            if failure:
                break
        check(operations == retained['operations'], 'preparation operation result mismatch')
        check(retained['passed'] == (failure is None) and retained['limitation'] == failure, 'preparation outcome mismatch')
        check(provenance['reconstructed'] == retained['passed'] and provenance['limitation'] == failure
              and provenance['status'] == ('exact' if failure is None else 'limited'), 'preparation source status mismatch')
        for name in paths:
            for suffix in ('.orig', '.rej'):
                if (work / (name + suffix)).is_file():
                    check(name + suffix in provenance['source_names'], 'missing patch artifact')
        for name in provenance['source_names']:
            source, kept = work / name, root / 'source' / name
            actual = digest(source) if source.is_file() else None
            check(provenance['files'][name] == actual, 'prepared source hash mismatch')
            check((digest(kept) if kept.is_file() else None) == actual, 'retained prepared source mismatch')
            if source.is_file():
                check(bool(source.stat().st_mode & 0o111) == bool(kept.stat().st_mode & 0o111), 'retained source mode mismatch')
        inventory = {str(p.relative_to(root / 'source')) for p in (root / 'source').rglob('*') if p.is_file()}
        check(inventory - {'harness.cpp'} == {n for n, value in provenance['files'].items() if value is not None}, 'prepared source inventory drift')


def check_sources(root):
    provenance = read(root / 'source-provenance.json')
    check(provenance['status'] in ('exact', 'limited'), 'invalid source status')
    reconstruction = provenance.get('reconstruction_policy')
    check(reconstruction in (None, 'recipe-prepare-v1'), 'unsupported reconstruction policy')
    check((root / 'preparation.json').exists() == (reconstruction == 'recipe-prepare-v1'), 'inconsistent reconstruction policy metadata')
    check(reconstruction is None or provenance.get('archive_policy') == 'makepkg-git-v1', 'inconsistent reconstruction archive policy')
    if provenance['status'] == 'limited':
        check(bool(provenance['limitation']), 'missing source limitation')
        if 'files' not in provenance:
            check(not (root / 'archive-policy.json').exists(), 'missing archive provenance')
            return
    recipe = (root / 'PKGBUILD').read_text()
    expected = re.search(r'^pkgbuild_sha256sum = ([0-9a-f]+)$', (root / 'BUILDINFO').read_text(), re.M).group(1)
    check(digest(root / 'PKGBUILD') == expected, 'recipe mismatch')
    checksums = re.findall(r"'([0-9a-f]{64})'", recipe.split('sha256sums=', 1)[1].split('prepare()', 1)[0])
    check(checksums[0] == provenance['archive_sha256'] and digest(root / 'qtbase.tar') == provenance['archive_actual_sha256'], 'source archive mismatch')
    check(provenance['status'] != 'exact' or digest(root / 'qtbase.tar') == checksums[0], 'source status mismatch')
    packaging = str(root / provenance['packaging_cache'])
    qt = str(root / provenance['qt_cache'])
    check(subprocess.check_output(['git', '-C', packaging, 'show', provenance['packaging_revision'] + ':PKGBUILD'], timeout=30) == (root / 'PKGBUILD').read_bytes(), 'packaging revision mismatch')
    check(subprocess.check_output(['git', '-C', qt, 'rev-parse', provenance['qt_tag'] + '^{commit}'], text=True, timeout=30).strip() == provenance['qt_commit'], 'Qt revision mismatch')
    policy = provenance.get('archive_policy', 'git-attributes-v0')
    check(not (root / 'archive-policy.json').exists() or policy == 'makepkg-git-v1', 'archive policy downgrade')
    check(policy in ('git-attributes-v0', 'makepkg-git-v1'), 'unsupported archive policy')
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryFile() as archived:
        environment = None
        if policy == 'makepkg-git-v1':
            qt, environment = policy_environment(root, Path(qt), Path(tmp))
        subprocess.run(['git', '-c', 'core.abbrev=no', '-C', qt, 'archive', '--format', 'tar', provenance['qt_tag']],
                       stdout=archived, stderr=subprocess.PIPE, timeout=180, check=True, env=environment)
        archived.seek(0)
        check(hashlib.file_digest(archived, 'sha256').hexdigest() == provenance['archive_actual_sha256'], 'Git archive provenance mismatch')
    qt = str(root / provenance['qt_cache'])
    package_patches = re.findall(r'^  patch .* < (\S+)', recipe, re.M)
    commits = re.findall(r'cherry-pick -n ([0-9a-f]{40})', recipe)
    check(commits == provenance['cherry_picks'] and provenance['patches'] == package_patches + [c + '.patch' for c in commits], 'patch order drift')
    for name, expected in zip(package_patches, checksums[1:]):
        check(digest(root / name) == expected, 'package patch mismatch')
    for commit in commits:
        check(subprocess.check_output(['git', '-C', qt, 'diff', '--no-ext-diff', '--no-textconv', commit + '^', commit], timeout=30) == (root / (commit + '.patch')).read_bytes(), 'Qt patch revision mismatch')
    if reconstruction == 'recipe-prepare-v1':
        required = {'src/corelib/tools/qcryptographichash.cpp', 'src/corelib/io/qiodevice.cpp',
                    'src/corelib/io/qiodevice_p.h', 'src/corelib/io/qfiledevice.cpp',
                    'src/corelib/io/qfsfileengine.cpp', 'src/corelib/io/qfsfileengine_unix.cpp',
                    'src/corelib/tools/qringbuffer.cpp'}
        for patch in provenance['patches']:
            required.update(re.findall(r'^(?:\+\+\+ b/|--- a/)(.+)$', (root / patch).read_text(), re.M))
        for commit in commits:
            required.update(subprocess.check_output(['git', '-C', qt, 'diff', '--no-renames', '--name-only', '-z', commit + '^', commit]).decode().strip('\0').split('\0'))
        optional = {name + suffix for name in required for suffix in ('.orig', '.rej')}
        names = set(provenance['source_names'])
        check(required <= names <= required | optional and names == set(provenance['files']), 'prepared source inventory mismatch')
        replay_preparation(root, provenance, package_patches, commits)
        return
    if not provenance['reconstructed'] and 'failed_patch' not in provenance:
        check(provenance['status'] == 'limited' and not provenance['files'], 'missing source reconstruction')
        return
    if policy == 'makepkg-git-v1':
        required = {'src/corelib/tools/qcryptographichash.cpp', 'src/corelib/io/qiodevice.cpp',
                    'src/corelib/io/qiodevice_p.h', 'src/corelib/io/qfiledevice.cpp',
                    'src/corelib/io/qfsfileengine.cpp', 'src/corelib/io/qfsfileengine_unix.cpp',
                    'src/corelib/tools/qringbuffer.cpp'}
        for patch in provenance['patches']:
            required.update(re.findall(r'^(?:\+\+\+ b/|--- a/)(.+)$', (root / patch).read_text(), re.M))
        check(set(provenance.get('source_names', provenance['files'])) == required, 'source inventory mismatch')
    # Reconstruct selected source independently from checksum-bound archive and retained patches.
    with tempfile.TemporaryDirectory() as tmp, tarfile.open(root / 'qtbase.tar') as archive:
        directory = Path(tmp)
        for name in provenance.get('source_names', provenance['files']):
            check(not Path(name).is_absolute() and '..' not in Path(name).parts, 'source path escape')
            if name not in archive.getnames():
                continue  # A retained patch may introduce a new file.
            member = archive.getmember(name)
            check(member.isfile(), 'nonregular source')
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
        for name in provenance['patches']:
            applied = subprocess.run(['patch'] + (['--fuzz=0'] if policy == 'makepkg-git-v1' else []) + ['--batch', '--forward', '-p1', '-d', str(directory), '-i', str((root / name).resolve())],
                           check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            if applied.returncode:
                check(provenance.get('failed_patch') == name and provenance['status'] == 'limited' and not provenance['reconstructed'], 'unexpected patch failure')
                check(applied.stdout == (root / (name + '.apply')).read_bytes() and applied.stderr == (root / (name + '.apply.stderr')).read_bytes(), 'patch result mismatch')
                partial = {str(p.relative_to(directory)): digest(p) for p in directory.rglob('*') if p.is_file()}
                check(partial == provenance['partial_files'], 'partial source reconstruction mismatch')
                actual = {str(p.relative_to(root / 'source')): digest(p) for p in (root / 'source').rglob('*') if p.is_file() and p != root / 'source/harness.cpp'}
                check(actual == partial, 'retained partial source mismatch')
                return
        check('failed_patch' not in provenance, 'unreproduced patch failure')
        for name, expected in provenance['files'].items():
            if expected is None:
                check(not (directory / name).exists() and not (root / 'source' / name).exists(), 'deleted source mismatch')
            else:
                check(digest(directory / name) == expected == digest(root / 'source' / name), 'source reconstruction mismatch')


def verify(root):
    sealed(root)
    check(read(root / 'assessment.json')['status'] == 'complete', 'partial audit; no complete findings')
    if (root / 'prior.json').exists():
        prior = read(root / 'prior.json')
        check_prior(Path(prior['audit']), Path(prior['verification']))
        check(digest(Path(prior['audit']) / 'seal.json') == prior['audit_seal'] and digest(Path(prior['verification'])) == prior['verification_sha256'], 'prior drift')
    inputs = read(root / 'inputs.json')
    check(bind(Path(inputs['evidence']), Path(inputs['verification'])) == inputs, 'input bindings drift')
    original = Path(inputs['evidence'])
    for name in ('native.stdout', 'preregistration.json', 'summary.json'):
        check(digest(root / name) == digest(original / name), 'raw snapshot drift')
    check(digest(root / 'source/harness.cpp') == digest(original / 'source/main.cpp'), 'harness drift')
    check_accounting(root, read(root / 'accounting.json'))
    check_identity(root)
    identity = read(root / 'identity.json')
    dep = read(original / 'inputs.json')['dependencies']['libQt6Core.so.6']
    check(identity['host'] == dep['host'] and identity['host_sha256'] == dep['host_sha256'] and
          identity['build_id'] == dep['build_id'], 'diagnostic Qt identity binding mismatch')
    prepared = Path(identity['symbols_manifest']).parent
    check(inputs['identities'][str(prepared / 'seal.json')] == identity['prepared_seal'], 'diagnostic debug binding mismatch')
    check_sources(root)
    check_citations(root)
    cited = {c['file'] for c in read(root / 'citations.json')}
    check('source/harness.cpp' in cited and all(str(p.relative_to(root)) in cited for p in (root / 'disassembly').iterdir() if p.suffix in ('.txt', '.range')), 'missing citations')
    identity = read(root / 'identity.json')
    expected_symbols = {'_ZN18QCryptographicHash7addDataEP9QIODevice', '_ZN9QIODevice4readEPcx',
                        '_ZN16QIODevicePrivate4readEPcxb', '_ZN11QFileDevice8readDataEPcx',
                        '_ZN13QFSFileEngine4readEPcx', '_ZNK11QFileDevice5atEndEv'}
    check({p.stem for p in (root / 'disassembly').glob('*.txt')} == expected_symbols, 'missing disassembly')
    for path in (root / 'disassembly').glob('*.txt'):
        symbol = path.stem
        actual = subprocess.check_output(['objdump', '-d', '--disassemble=' + symbol, identity['host']], timeout=30)
        check(actual == path.read_bytes() and ('<' + symbol + '@@').encode() in actual, 'disassembly drift/empty symbol')
    symbols = subprocess.check_output(['nm', '-S', identity['debug']['path']], timeout=30)
    check(symbols == (root / 'debug-symbols.txt').read_bytes(), 'debug symbol table drift')
    ranges = read(root / 'binary-ranges.json')
    check(any('QCryptographicHashPrivate' in r['symbol'] for r in ranges), 'missing private hash range')
    for item in ranges:
        expected_line = f"{item['start']:016x} {item['size']:016x} ".encode()
        check(any(line.startswith(expected_line) and line.endswith(item['symbol'].encode()) for line in symbols.splitlines()), 'private symbol binding mismatch')
        actual = subprocess.check_output(['objdump', '-d', '--start-address=' + hex(item['start']), '--stop-address=' + hex(item['start'] + item['size']), identity['host']], timeout=30)
        check(actual == (root / 'disassembly' / (item['symbol'] + '.range')).read_bytes(), 'private disassembly drift')
    sealed(root)
    return dict(status='passed', audit_seal=digest(root / 'seal.json'), source_status=read(root / 'source-provenance.json')['status'],
                blocks=5, ordinals=len(read(root / 'preregistration.json')['mapping']), imports_auditor=False, new_measurements=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    check(not args.output.exists() and not args.output.resolve().is_relative_to(args.evidence.resolve()), 'destination collision')
    try:
        result = verify(args.evidence.resolve())
    except (ValueError, OSError, KeyError, TypeError, IndexError, StopIteration, subprocess.SubprocessError) as error:
        result = dict(status='failed', failure=str(error))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(result)
    sys.exit(result['status'] != 'passed')
