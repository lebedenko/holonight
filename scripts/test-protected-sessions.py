#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run native tests as the invoking user against a disposable protected runtime."""
import argparse
import contextlib
import shutil
import importlib.util
import os
from pathlib import Path
import pwd
import subprocess
import tempfile
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('generations', Path(__file__).with_name('manage-images-generations.py'))
generations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generations)


@contextlib.contextmanager
def protected_fixture():
    root = Path(tempfile.mkdtemp(prefix='holonight-session-acceptance-', dir='/run'))
    try:
        yield root
    except BaseException:
        print(f'Native verification failed; protected fixture preserved: {root}', flush=True)
        raise
    else:
        shutil.rmtree(root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--helper', type=Path, required=True)
    parser.add_argument('--test', type=Path, required=True)
    parser.add_argument('--kind', choices=('production', 'fault', 'startup'), default='production')
    parser.add_argument('--uid', type=int, default=int(os.environ.get('SUDO_UID', '-1')))
    parser.add_argument('arguments', nargs='*')
    args = parser.parse_args()
    if os.geteuid() != 0 or args.uid <= 0:
        parser.error('requires root and an ordinary invoking UID')
    account = pwd.getpwuid(args.uid)
    with protected_fixture() as root:
        root.chmod(0o755)
        runtime = root / 'runtime'
        generations.run(SimpleNamespace(runtime=runtime, source=args.source.resolve(), helper=args.helper.resolve(),
                                        command='install', maintenance_migrate=False, ownership_manifest=None))
        env = dict(os.environ, HN_SESSION_RUNTIME=str(runtime), HN_BROWSER_SESSION_RUNTIME=str(runtime),
                   XDG_RUNTIME_DIR=f'/run/user/{args.uid}', DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{args.uid}/bus',
                   QT_QPA_PLATFORM='offscreen', HOME=account.pw_dir, USER=account.pw_name, LOGNAME=account.pw_name)
        for key in ('HN_SESSION_RUNTIME', 'HN_SESSION_FAULT_RUNTIME', 'HN_SESSION_STARTUP_RUNTIME'):
            env.pop(key, None)
        env[{'production': 'HN_SESSION_RUNTIME', 'fault': 'HN_SESSION_FAULT_RUNTIME',
             'startup': 'HN_SESSION_STARTUP_RUNTIME'}[args.kind]] = str(runtime)
        # Tests may write their own artifacts only as the ordinary invoking user.
        completed = subprocess.run([str(args.test.resolve()), *args.arguments], env=env, user=args.uid,
                                   group=account.pw_gid, extra_groups=os.getgrouplist(account.pw_name, account.pw_gid))
        if completed.returncode:
            raise RuntimeError(f'native test process exited {completed.returncode}')


if __name__ == '__main__':
    main()
