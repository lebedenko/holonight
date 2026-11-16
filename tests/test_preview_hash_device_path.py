import copy
import importlib.util
import json
import os
import subprocess
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


a = module('device_audit_test', 'audit-preview-hash-device-path.py')
v = module('device_checker_test', 'verify-preview-hash-device-path.py')
h = module('device_fixture_test', 'verify-preview-hash-throughput.py')


def fixture(root):
    mapping = [dict(ordinal=0, path='empty', size=0, sha256='empty-digest'),
               dict(ordinal=1, path='payload', size=3, sha256='payload-digest')]
    schedule = h.expected_schedule()
    a.write(root / 'preregistration.json', dict(mapping=mapping, schedule=schedule))
    rows = [dict(type='identity')]
    for sweep in schedule:
        for f in mapping:
            # Unbalanced sweeps make accidental individual pairing easy to detect.
            ns = 20 + sweep['sweep'] * 3
            if sweep['case'] == 'qt_device':
                ns += -5 if f['ordinal'] == 0 else 11
            rows.append(dict(sweep, type='file', ordinal=f['ordinal'], bytes=f['size'], sha256=f['sha256'],
                             init_ns=1, update_ns=ns, final_ns=1))
        rows.append(dict(type='sweep_end', index=sweep['index'], elapsed_ns=1000))
    (root / 'native.stdout').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    a.write(root / 'summary.json', dict(ratios=[dict(block=b, numerator='qt_device', denominator='qt_file', ratio=52/58) for b in range(5)]))
    return mapping, rows


def identity_fixture(root):
    host = Path(sys.executable).resolve()
    prepared = root / 'prepared'
    prepared.mkdir()
    debug = dict(path=str(host), sha256=a.digest(host), build_id=v.build_id(host))
    a.write(prepared / 'symbols.json', {'libQt6Core.so.6': debug})
    a.seal(prepared)
    (root / 'BUILDINFO').write_text('pkgver = 6.12.0-5\n')
    (root / 'PKGINFO').write_text('pkgname = qt6-base\n')
    (root / 'libQt6Core.so').write_bytes(host.read_bytes())
    package = root / 'package.tar'
    with tarfile.open(package, 'w') as archive:
        for name, member in (('BUILDINFO', '.BUILDINFO'), ('PKGINFO', '.PKGINFO'), ('libQt6Core.so', 'usr/lib/libQt6Core.so.6.12.0')):
            archive.add(root / name, arcname=member)
    identity = dict(package=str(package), package_sha256=a.digest(package), host=str(host), host_sha256=a.digest(host),
                    build_id=debug['build_id'], debug=debug, symbols_manifest=str(prepared / 'symbols.json'),
                    symbols_manifest_sha256=a.digest(prepared / 'symbols.json'), prepared_seal=a.digest(prepared / 'seal.json'))
    a.write(root / 'identity.json', identity)
    return identity


def preparation_fixture(root, conflict=False):
    repo = root / 'repo'
    repo.mkdir()
    def git(*args):
        return subprocess.check_output(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                                       '-C', str(repo), *args], stderr=subprocess.PIPE).decode().strip()
    git('init')
    path = repo / 'mkspecs/common/gcc-base.conf'
    path.parent.mkdir(parents=True)
    old = ['QMAKE_CFLAGS_DEPS          += -M', 'QMAKE_CFLAGS_WARN_ON       += -Wall -Wextra',
           'QMAKE_CFLAGS_WARN_OFF      += -w', 'release', 'release_debug', 'debug',
           'shlib', 'static', 'QMAKE_CFLAGS_APP           += changed']
    path.write_text(''.join('prefix %d\n' % i for i in range(39)) + '\n'.join(old) + '\n')
    (repo / 'rename').write_text('one\ntwo\nthree\nfour\n')
    (repo / 'delete').write_text('delete\n')
    (repo / 'ordered').write_text('base\n')
    git('add', '.'); git('commit', '-qm', 'base')
    tag = git('rev-parse', 'HEAD')
    (root / 'qtbase.tar').write_bytes(subprocess.check_output(['git', '-C', str(repo), 'archive', '--format=tar', tag]))
    # The first reviewed hunk differs only in its final context line.
    patch = 'diff --git a/mkspecs/common/gcc-base.conf b/mkspecs/common/gcc-base.conf\n--- a/mkspecs/common/gcc-base.conf\n+++ b/mkspecs/common/gcc-base.conf\n@@ -40,9 +40,9 @@\n'
    patch += ''.join((' ' + line + '\n') for line in old[:3])
    patch += '-release\n-release_debug\n-debug\n+new_release\n+new_release_debug\n+new_debug\n'
    patch += ' shlib\n static\n QMAKE_CFLAGS_APP           += original\n'
    (root / 'qt6-base-cflags.patch').write_text(patch)
    commits = []
    git('mv', 'rename', 'renamed')
    git('commit', '-qm', 'rename only'); commits.append(git('rev-parse', 'HEAD'))
    git('mv', 'renamed', 'edited')
    (repo / 'edited').write_text('one\ntwo\nthree\nchanged\n')
    (repo / 'edited').chmod(0o755)
    (repo / 'delete').unlink()
    (repo / 'added').write_text('added\n')
    (repo / 'ordered').write_text('second\n')
    git('add', '-A'); git('commit', '-qm', 'edit mode add delete'); commits.append(git('rev-parse', 'HEAD'))
    (repo / 'ordered').write_text('third\n')
    git('add', '.'); git('commit', '-qm', 'ordered'); commits.append(git('rev-parse', 'HEAD'))
    if conflict:
        git('checkout', '--detach', tag)
        (repo / 'ordered').write_text('conflict\n')
        git('add', '.'); git('commit', '-qm', 'conflict'); commits.append(git('rev-parse', 'HEAD'))
    (root / 'BUILDINFO').write_text('installed = git-' + subprocess.check_output(['git', '--version']).decode().split()[-1] +
                                   '-1-x86_64\ninstalled = patch-' + subprocess.check_output(['patch', '--version']).decode().splitlines()[0].split()[-1] + '-1-x86_64\n')
    return repo, tag, commits


class DevicePathTests(unittest.TestCase):
    def test_recipe_preparation_replays_git_semantics_and_rejects_resealed_drift(self):
        for conflict in (False, True):
            with self.subTest(conflict=conflict), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                repo, tag, commits = preparation_fixture(root, conflict)
                with tempfile.TemporaryDirectory() as work:
                    result = a.prepare(root, repo, tag, ['qt6-base-cflags.patch'], commits, Path(work))
                    self.assertEqual(result['passed'], not conflict)
                    self.assertEqual(len(result['operations']), 1 + len(commits))
                    tree = Path(work) / 'work'
                    self.assertEqual((tree / 'edited').read_text(), 'one\ntwo\nthree\nchanged\n')
                    self.assertTrue((tree / 'edited').stat().st_mode & 0o111)
                    self.assertFalse((tree / 'delete').exists())
                    self.assertEqual((tree / 'added').read_text(), 'added\n')
                    self.assertIn('QMAKE_CFLAGS_APP           += changed', (tree / 'mkspecs/common/gcc-base.conf').read_text())
                    names = ['edited', 'rename', 'renamed', 'delete', 'added', 'ordered', 'mkspecs/common/gcc-base.conf']
                    names += ['mkspecs/common/gcc-base.conf' + suffix for suffix in ('.orig', '.rej')
                              if (tree / ('mkspecs/common/gcc-base.conf' + suffix)).is_file()]
                    source = root / 'source'
                    source.mkdir()
                    import shutil
                    for name in names:
                        if (tree / name).is_file():
                            (source / name).parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(tree / name, source / name)
                provenance = dict(qt_cache='repo', qt_commit=tag, source_names=names,
                                  files={n: a.digest(source / n) if (source / n).is_file() else None for n in names},
                                  reconstructed=not conflict, status='limited' if conflict else 'exact', limitation=result['limitation'])
                a.write(root / 'preparation.json', result)
                v.replay_preparation(root, provenance, ['qt6-base-cflags.patch'], commits)
                for field in ('returncode', 'stdout', 'before', 'after'):
                    changed = copy.deepcopy(result)
                    changed['operations'][0][field] = 'tampered'
                    a.write(root / 'preparation.json', changed)
                    a.seal(root); v.sealed(root)
                    with self.assertRaisesRegex(ValueError, 'operation result'):
                        v.replay_preparation(root, provenance, ['qt6-base-cflags.patch'], commits)
                a.write(root / 'preparation.json', result)
                (source / 'added').write_text('tampered')
                a.seal(root)
                with self.assertRaisesRegex(ValueError, 'retained prepared source'):
                    v.replay_preparation(root, provenance, ['qt6-base-cflags.patch'], commits)

    def test_reviewed_fuzz_requires_unique_preimage_and_preserves_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, tag, commits = preparation_fixture(root)
            name = 'mkspecs/common/gcc-base.conf'
            before = (repo / name).read_bytes()
            patch = (root / 'qt6-base-cflags.patch').read_text()
            expected = a.expected_patch({name: before}, patch)[name]
            self.assertIn(b'QMAKE_CFLAGS_APP           += changed', expected)
            self.assertNotIn(b'QMAKE_CFLAGS_APP           += original', expected)
            with self.assertRaisesRegex(ValueError, 'ambiguous'):
                a.expected_patch({name: before + before}, patch)
            with self.assertRaises(ValueError):
                a.expected_patch({name: before.replace(b'shlib', b'unexpected')}, patch)
            args = ['patch', '--fuzz=0', '--batch', '--forward', '-p1', '-d', str(repo), '-i', str(root / 'qt6-base-cflags.patch')]
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)

    def test_patch_failure_and_unexpected_fuzz_retain_replayable_partial_results(self):
        for mode in ('failure', 'unexpected-fuzz', 'unintended-edit', 'ambiguous'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                repo, tag, commits = preparation_fixture(root)
                patch = root / 'qt6-base-cflags.patch'
                text = patch.read_text()
                if mode == 'failure':
                    text = text.replace('-release\n', '-missing\n')
                elif mode == 'unintended-edit':
                    text = text.replace(' QMAKE_CFLAGS_WARN_OFF      += -w', ' wrong context')
                elif mode == 'ambiguous':
                    # A second identical preimage is rejected, even if GNU patch chooses one.
                    path = repo / 'mkspecs/common/gcc-base.conf'
                    path.write_bytes(path.read_bytes() * 2)
                    subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
                    subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', '-C', str(repo), 'commit', '-qm', 'duplicate'], check=True)
                    tag = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD']).decode().strip()
                    (root / 'qtbase.tar').write_bytes(subprocess.check_output(['git', '-C', str(repo), 'archive', '--format=tar', tag]))
                patch.write_text(text)
                name = patch.name
                if mode == 'unexpected-fuzz':
                    name = 'other.patch'
                    (root / name).write_text(text)
                with tempfile.TemporaryDirectory() as work:
                    result = a.prepare(root, repo, tag, [name], [], Path(work))
                    self.assertFalse(result['passed'])
                    self.assertTrue(result['limitation'])
                    self.assertEqual(len(result['operations']), 1)
                    source = root / 'source/mkspecs/common'
                    source.mkdir(parents=True)
                    import shutil
                    names = []
                    for file in (Path(work) / 'work/mkspecs/common').iterdir():
                        shutil.copy2(file, source / file.name)
                        names.append('mkspecs/common/' + file.name)
                provenance = dict(qt_cache='repo', qt_commit=tag, source_names=names,
                                  files={n: a.digest(root / 'source' / n) for n in names},
                                  reconstructed=False, status='limited', limitation=result['limitation'])
                a.write(root / 'preparation.json', result)
                a.seal(root); v.sealed(root)
                v.replay_preparation(root, provenance, [name], [])

    def test_reconstruction_policy_cannot_be_resealed_or_downgraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for policy, retained in [('unknown', False), (None, True), ('recipe-prepare-v1', False)]:
                a.write(root / 'source-provenance.json', dict(status='limited', limitation='test', reconstruction_policy=policy))
                if retained:
                    a.write(root / 'preparation.json', {})
                elif (root / 'preparation.json').exists():
                    (root / 'preparation.json').unlink()
                a.seal(root)
                with self.assertRaisesRegex(ValueError, 'policy'):
                    v.check_sources(root)

    def test_git_export_attributes_and_configuration_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / 'repo'
            repo.mkdir()
            def git(*args, env=None):
                return subprocess.check_output(['git', '-C', str(repo), *args], env=env, stderr=subprocess.PIPE)
            git('init')
            (repo / '.gitattributes').write_text('hidden export-ignore\nversion export-subst\n')
            (repo / 'hidden').write_text('retained input')
            (repo / 'version').write_text('$Format:%H$\n')
            git('add', '.')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'fixture')
            before = git('rev-parse', 'HEAD')
            ordinary = git('archive', '--format=tar', 'HEAD')
            (repo / '.git/info/attributes').write_text('* -export-subst -export-ignore\n')
            sanitized = git('archive', '--format=tar', 'HEAD')
            self.assertNotEqual(ordinary, sanitized)
            self.assertEqual(before, git('rev-parse', 'HEAD'))
            self.assertEqual((repo / 'version').read_text(), '$Format:%H$\n')
            config = root / 'global'
            config.write_text('[tar]\n    umask = 0000\n')
            polluted = dict(os.environ, GIT_CONFIG_GLOBAL=str(config), GIT_CONFIG_SYSTEM='/dev/null', GIT_CONFIG_COUNT='0')
            self.assertNotEqual(sanitized, git('archive', '--format=tar', 'HEAD', env=polluted))
            isolated = dict(polluted, GIT_CONFIG_GLOBAL='/dev/null')
            self.assertEqual(sanitized, git('archive', '--format=tar', 'HEAD', env=isolated))
            for data, hidden, version in ((ordinary, False, before.strip().decode()), (sanitized, True, '$Format:%H$')):
                import io
                with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                    self.assertEqual('hidden' in archive.getnames(), hidden)
                    self.assertEqual(archive.extractfile('version').read().decode().strip(), version)

    def test_policy_attributes_and_member_tampering_after_resealing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            qt = root / 'qt'
            (qt / 'info').mkdir(parents=True)
            (qt / 'info/attributes').write_text('* -export-subst -export-ignore\n')
            (root / 'BUILDINFO').write_text('installed = pacman-1.0-1-x86_64\n')
            (root / 'pacman-PKGINFO').write_text('pkgname = pacman\npkgver = 1.0-1\n')
            (root / 'makepkg-git.sh').write_text('export GIT_CONFIG_GLOBAL=/dev/null\n')
            (root / 'makepkg-gitconfig').write_text('')
            package = root / 'pacman.tar'
            members = {'.PKGINFO': 'pacman-PKGINFO', 'usr/share/makepkg/source/git.sh': 'makepkg-git.sh'}
            with tarfile.open(package, 'w') as archive:
                for member, name in members.items():
                    archive.add(root / name, arcname=member)
            policy = dict(version='makepkg-git-v1', package=str(package), package_sha256=a.digest(package),
                          installed='pacman-1.0-1-x86_64', config_present=False,
                          config_sha256=a.digest(root / 'makepkg-gitconfig'),
                          members={member: dict(file=name, sha256=a.digest(root / name)) for member, name in members.items()})
            a.write(root / 'archive-policy.json', policy)
            with tempfile.TemporaryDirectory() as replay:
                v.policy_environment(root, qt, Path(replay))
            for path in (qt / 'info/attributes', root / 'makepkg-git.sh', root / 'makepkg-gitconfig'):
                original = path.read_bytes()
                path.write_text('tampered')
                a.seal(root)
                v.sealed(root)
                with tempfile.TemporaryDirectory() as replay, self.assertRaises(ValueError):
                    v.policy_environment(root, qt, Path(replay))
                path.write_bytes(original)
            policy['version'] = 'unknown'
            a.write(root / 'archive-policy.json', policy)
            a.seal(root)
            with tempfile.TemporaryDirectory() as replay, self.assertRaisesRegex(ValueError, 'policy'):
                v.policy_environment(root, qt, Path(replay))

    def test_prior_binding_and_paired_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audit = root / 'prior'
            audit.mkdir()
            a.write(audit / 'assessment.json', dict(status='complete'))
            a.seal(audit)
            verification = root / 'passed.json'
            a.write(verification, dict(status='passed', audit_seal=a.digest(audit / 'seal.json')))
            v.check_prior(audit, verification)
            (audit / 'assessment.json').write_text('{}')
            a.seal(audit)
            with self.assertRaisesRegex(ValueError, 'binding'):
                v.check_prior(audit, verification)

    def test_patch_without_fuzz_additions_deletions_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'old').write_text('old\n')
            patch = root / 'change.patch'
            patch.write_text('--- a/old\n+++ /dev/null\n@@ -1 +0,0 @@\n-old\n--- /dev/null\n+++ b/new\n@@ -0,0 +1 @@\n+new\n')
            args = ['patch', '--fuzz=0', '--batch', '--forward', '-p1', '-d', root, '-i', patch]
            a.command(args, root / 'application')
            self.assertFalse((root / 'old').exists())
            self.assertEqual((root / 'new').read_text(), 'new\n')
            with self.assertRaises(ValueError):
                a.command(args, root / 'failed-application')

    def test_signed_block_means_reconcile_and_preserve_empty_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mapping, rows = fixture(root)
            result = a.accounting(rows, mapping)
            v.check_accounting(root, result)
            block = result[0]
            self.assertEqual(block['device_sum_ns'], 290)
            self.assertEqual(block['streaming_sum_ns'], 260)
            self.assertEqual(block['difference_mean_ms'], 6 / 1e6)
            self.assertEqual([f['difference_sum_ns'] for f in block['files']], [-25, 55])
            self.assertEqual(block['files'][0]['size'], 0)
            self.assertEqual(sum(f['difference_sum_ns'] for f in block['files']), 30)

    def test_missing_duplicate_ordinals_rejected_by_both_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mapping, rows = fixture(root)
            for bad in (rows[:16] + rows[17:], rows + [rows[16]]):
                with self.assertRaises(ValueError):
                    a.accounting(bad, mapping)
                (root / 'native.stdout').write_text(''.join(json.dumps(r) + '\n' for r in bad))
                with self.assertRaises((ValueError, StopIteration)):
                    v.check_accounting(root, a.accounting(rows, mapping))

    def test_accounting_tampering_rejected_after_resealing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mapping, rows = fixture(root)
            result = a.accounting(rows, mapping)
            result[0]['files'][0]['difference_mean_ms'] *= -1
            a.write(root / 'accounting.json', result)
            a.seal(root)
            v.sealed(root)
            with self.assertRaisesRegex(ValueError, 'accounting'):
                v.check_accounting(root, v.read(root / 'accounting.json'))

    def test_package_host_debug_identity_mismatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            identity = identity_fixture(root)
            v.check_identity(root)
            for key in ('package_sha256', 'host_sha256', 'build_id', 'symbols_manifest_sha256', 'prepared_seal'):
                changed = copy.deepcopy(identity)
                changed[key] = 'wrong'
                a.write(root / 'identity.json', changed)
                with self.assertRaises(ValueError):
                    v.check_identity(root)
            changed = copy.deepcopy(identity)
            changed['debug']['build_id'] = 'wrong'
            a.write(root / 'identity.json', changed)
            with self.assertRaisesRegex(ValueError, 'debug'):
                v.check_identity(root)

    def test_recipe_and_source_checksum_mismatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            recipe = "sha256sums=('" + 'a'*64 + "')\nprepare() {}\n"
            (root / 'PKGBUILD').write_text(recipe)
            (root / 'BUILDINFO').write_text('pkgbuild_sha256sum = ' + 'b'*64 + '\n')
            a.write(root / 'source-provenance.json', dict(status='exact', files={}))
            with self.assertRaisesRegex(ValueError, 'recipe'):
                v.check_sources(root)
            (root / 'BUILDINFO').write_text('pkgbuild_sha256sum = ' + a.digest(root / 'PKGBUILD') + '\n')
            (root / 'qtbase.tar').write_bytes(b'wrong source')
            a.write(root / 'source-provenance.json', dict(status='exact', archive_sha256='a'*64, archive_actual_sha256='a'*64, files={}))
            a.seal(root)
            v.sealed(root)
            with self.assertRaisesRegex(ValueError, 'source archive'):
                v.check_sources(root)

    def test_missing_sources_require_explicit_limitation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a.write(root / 'source-provenance.json', dict(status='limited', limitation='Unavailable primary source'))
            v.check_sources(root)
            a.write(root / 'source-provenance.json', dict(status='limited', limitation=''))
            with self.assertRaisesRegex(ValueError, 'limitation'):
                v.check_sources(root)

    def test_citation_drift_even_after_resealing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'source').write_text('first\nsecond\n')
            citation = dict(file='source', sha256=a.digest(root / 'source'), start=1, end=2, text='first\nsecond')
            a.write(root / 'citations.json', [citation])
            v.check_citations(root)
            citation['start'] = 2
            a.write(root / 'citations.json', [citation])
            a.seal(root)
            v.sealed(root)
            with self.assertRaisesRegex(ValueError, 'citation drift'):
                v.check_citations(root)

    def test_collision_and_partial_failure_preserve_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / 'keep'
            marker.write_text('keep')
            with self.assertRaisesRegex(ValueError, 'collision'):
                a.run(root / 'missing', root / 'verification', root)
            self.assertEqual(marker.read_text(), 'keep')
            partial = root / 'partial'
            result = a.run(root / 'missing', root / 'verification', partial)
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(result['stage'], 'bindings')
            v.sealed(partial)

    def test_verification_binding_and_consumed_evidence_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / 'evidence'
            evidence.mkdir()
            dependency = root / 'dependency'
            dependency.write_text('original')
            a.write(evidence / 'inputs.json', dict(identities={str(dependency): a.digest(dependency)}))
            a.write(evidence / 'assessment.json', dict(status='complete'))
            a.seal(evidence)
            verification = root / 'independent.json'
            record = dict(status='passed', evidence_seal=a.digest(evidence / 'seal.json'), measured_sweeps=125,
                          warmup_sweeps=5, measured_rows=7500, warmup_rows=300)
            a.write(verification, record)
            v.bind(evidence, verification)
            dependency.write_text('drift')
            with self.assertRaisesRegex(ValueError, 'consumed identity drift'):
                v.bind(evidence, verification)
            record['evidence_seal'] = 'wrong'
            a.write(verification, record)
            with self.assertRaisesRegex(ValueError, 'binding'):
                v.bind(evidence, verification)


if __name__ == '__main__':
    unittest.main()
