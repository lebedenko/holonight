#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Privileged disposable generation lifecycle tests; never deploy to the host."""
import argparse
from contextlib import redirect_stdout
import io
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('generations', Path(__file__).with_name('manage-images-generations.py'))
generations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generations)


def exercise(helper):
    if os.geteuid() != 0:
        raise ValueError('requires root for protected fixture ancestors')
    with tempfile.TemporaryDirectory(prefix='holonight-generations-', dir='/run') as temporary:
        root = Path(temporary)
        root.chmod(0o755)
        source = root / 'source'
        source.mkdir(mode=0o755)
        inventory = []
        for name in ('usr/libexec/holonight-images-helper', 'usr/lib/qt6/plugins/imageformats/libqgif.so',
                     'usr/lib/qt6/plugins/imageformats/libqjpeg.so', 'usr/lib/qt6/plugins/imageformats/libqtiff.so',
                     'usr/lib/qt6/plugins/imageformats/libqwebp.so'):
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'inert fixture')
            path.chmod(0o644)
            inventory.append(dict(path=name, mode=0o644, size=13,
                                  sha256=hashlib.sha256(b'inert fixture').hexdigest()))
        manifest = source / 'manifest.json'
        def version(number):
            # Different exact manifest bytes produce distinct generation IDs.
            manifest.write_text(json.dumps(dict(version=1, files=inventory), indent=number))
            manifest.chmod(0o644)
        version(1)
        # Hold an ordinary user's writable inode before privileged publication.
        for path in source.rglob('*'):
            if path.is_file():
                os.chown(path, 65534, 65534)
        payload = source / inventory[0]['path']
        old_descriptor = payload.open('r+b')
        runtime = root / 'runtime'
        args = SimpleNamespace(runtime=runtime, source=source, helper=helper, command='install',
                               generation=None, maintenance_migrate=False, ownership_manifest=None)
        generations.run(args)
        first = (runtime / 'current').read_text().strip()
        first_path = runtime / 'generations' / first
        assert generations.identity(manifest.read_bytes()) == first
        with generations.lease(first_path):
            version(2)
            generations.run(args)
            second = (runtime / 'current').read_text().strip()
            assert first != second
            version(3)
            try:
                generations.run(args)
            except BlockingIOError:
                pass
            else:
                raise AssertionError('third generation bypassed retired shared lease')
            assert (runtime / 'current').read_text().strip() == second
            assert len(list((runtime / 'generations').iterdir())) == 2
            args.command, args.generation = 'rollback', first
            generations.run(args)
            assert (runtime / 'current').read_text().strip() == first
            args.command, args.generation = 'rollback', second
            generations.run(args)
            args.command = 'install'
        generations.run(args)
        third = (runtime / 'current').read_text().strip()
        assert not first_path.exists()
        assert third != second
        generations.run(args)  # Idempotent installation keeps rollback generation.
        assert len(list((runtime / 'generations').iterdir())) == 2
        selected = runtime / 'generations' / third
        # Neither a held writable alias nor reopening it through proc can
        # modify a published fresh inode. Source ownership must remain unchanged.
        published = selected / inventory[0]['path']
        assert payload.stat().st_uid == 65534 and published.stat().st_uid == 0
        assert (payload.stat().st_dev, payload.stat().st_ino) != (published.stat().st_dev, published.stat().st_ino)
        old_descriptor.write(b'changed bytes')
        old_descriptor.flush()
        assert published.read_bytes() == b'inert fixture'
        proc_write = ('import os,sys; fd=os.open("/proc/self/fd/"+sys.argv[1],os.O_WRONLY); '
                      'os.pwrite(fd,b"proc mutation",0); os.close(fd)')
        result = subprocess.run(['/usr/bin/python3', '-c', proc_write, str(old_descriptor.fileno())],
                                user=65534, group=65534, extra_groups=[],
                                pass_fds=(old_descriptor.fileno(),), capture_output=True)
        assert result.returncode == 0, result.stderr
        assert published.read_bytes() == b'inert fixture'
        old_descriptor.close()
        payload.write_bytes(b'inert fixture')
        # Ordinary-user writes and chmod fail on the protected installed inode.
        attempt = 'from pathlib import Path; import sys; Path(sys.argv[1]).write_bytes(b"changed")'
        result = subprocess.run(['/usr/bin/python3', '-c', attempt, str(selected / 'manifest.json')],
                                user=65534, group=65534, extra_groups=[], capture_output=True)
        assert result.returncode != 0
        # A child process lease is released on process exit.
        child = subprocess.Popen(['/usr/bin/python3', '-c',
            'import os,fcntl,sys; fd=os.open(sys.argv[1],os.O_RDONLY); fcntl.flock(fd,fcntl.LOCK_SH); print("ready",flush=True); sys.stdin.read()',
            str(selected)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        assert child.stdout.readline().strip() == 'ready'
        args.command = 'remove'
        try:
            generations.run(args)
        except BlockingIOError:
            pass
        else:
            raise AssertionError('busy uninstall succeeded')
        assert (runtime / 'current').exists()
        child.communicate('finish', timeout=5)
        assert child.returncode == 0
        injected = selected / 'unowned'
        injected.write_bytes(b'unowned')
        try:
            generations.run(args)
        except subprocess.CalledProcessError:
            pass
        else:
            raise AssertionError('unowned resource was removed')
        assert injected.exists()
        injected.unlink()
        generations.run(args)
        assert not (runtime / 'current').exists()
        assert not list((runtime / 'generations').iterdir())
        # A new legacy fixture must fail closed until explicitly authorized and
        # ownership-validated maintenance conversion is requested.
        legacy = root / 'legacy'
        legacy.mkdir(mode=0o755)
        generations.copy_tree(source, legacy)
        rows = []
        for path in (legacy, *legacy.rglob('*')):
            relative = '/usr/libexec/holonight-images/runtime' + str(path)[len(str(legacy)):]
            directory = path.is_dir()
            rows.append('\t'.join(['holonight-images', 'fixture', 'd' if directory else 'f',
                                   format(path.stat().st_mode & 0o7777, 'o'),
                                   '-' if directory else hashlib.sha256(path.read_bytes()).hexdigest(), relative]))
        ownership = root / 'manifest.tsv'
        ownership.write_text('\n'.join(rows) + '\n')
        args.runtime, args.command = legacy, 'install'
        args.check = True
        try:
            generations.run(args)
        except ValueError:
            pass
        else:
            raise AssertionError('implicit legacy conversion succeeded')
        args.check = False
        args.maintenance_migrate, args.ownership_manifest = True, ownership
        generations.run(args)
        assert (legacy / 'current').is_file()
        installed_rows = io.StringIO()
        with redirect_stdout(installed_rows):
            generations.inventory(legacy, 'fixture')
        ownership.write_text(installed_rows.getvalue())
        args.command = 'remove'
        generations.run(args)
    print('generation lifecycle: fresh copies, two-generation bound, busy upgrades/removal, rollback, ownership, process exit and maintenance migration passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--helper', type=Path, required=True)
    args = parser.parse_args()
    exercise(args.helper.resolve(strict=True))
