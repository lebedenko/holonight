#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Separate native sustained-navigation, scope-memory and helper-count evidence."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import pwd
import resource
import selectors
import shutil
import subprocess
import time
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('fixtures', Path(__file__).with_name('test-protected-sessions.py'))
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--helper', type=Path, required=True)
    parser.add_argument('--harness', type=Path, required=True)
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mutable', action='store_true', help='Exercise the legacy fully validated one-shot layout')
    parser.add_argument('--uid', type=int, default=int(os.environ.get('SUDO_UID', '-1')))
    args = parser.parse_args()
    if os.geteuid() != 0 or args.uid <= 0:
        parser.error('requires root and an ordinary invoking UID')
    account = pwd.getpwuid(args.uid)
    args.output.mkdir(exist_ok=False, parents=True)
    cgroups = Path(f'/sys/fs/cgroup/user.slice/user-{args.uid}.slice/user@{args.uid}.service')
    if not cgroups.is_dir():
        raise ValueError('native user cgroup hierarchy unavailable')

    def scopes():
        values = {}
        for path in cgroups.glob('**/holonight-images-*.scope'):
            try:
                values[str(path)] = int((path / 'memory.current').read_text())
            except FileNotFoundError:
                pass  # Verified disappearance can race the diagnostic sample.
        return values

    initial = set(scopes())
    with fixtures.protected_fixture() as root:
        root.chmod(0o755)
        runtime = root / 'runtime'
        if args.mutable:
            shutil.copytree(args.source.resolve(), runtime)
        else:
            fixtures.generations.run(SimpleNamespace(runtime=runtime, source=args.source.resolve(), helper=args.helper.resolve(),
                command='install', maintenance_migrate=False, ownership_manifest=None))
        env = dict(os.environ, HOME=account.pw_dir, USER=account.pw_name, LOGNAME=account.pw_name,
            XDG_RUNTIME_DIR=f'/run/user/{args.uid}', DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{args.uid}/bus',
            QT_QPA_PLATFORM='offscreen')
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        start = time.monotonic()
        phase, phase_start = 'construct', start
        events, snapshots = [], []
        observed = set()
        buffered = b''
        with (args.output / 'stderr.log').open('x') as log, (args.output / 'scopes.jsonl').open('x') as trace:
            process = subprocess.Popen([str(args.harness.resolve()), str(runtime), str(args.fixture.resolve())],
                stdout=subprocess.PIPE, stderr=log, env=env, user=args.uid, group=account.pw_gid,
                extra_groups=os.getgrouplist(account.pw_name, account.pw_gid))
            os.set_blocking(process.stdout.fileno(), False)
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)
            while process.poll() is None or time.monotonic() - phase_start < 1:
                for key, _ in selector.select(timeout=.01):
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    buffered += chunk
                    while b'\n' in buffered:
                        line, buffered = buffered.split(b'\n', 1)
                        event = json.loads(line)
                        phase = event['phase']
                        phase_start = time.monotonic()
                        events.append(dict(event, seconds=phase_start - start))
                now = time.monotonic()
                current = {path: memory for path, memory in scopes().items() if path not in initial}
                observed.update(current)
                row = dict(seconds=now - start, phase=phase, phase_seconds=now - phase_start,
                    helpers=len(current), memory_current=sum(current.values()), scopes=current)
                snapshots.append(row)
                trace.write(json.dumps(row) + '\n')
                if now - start > 150:
                    process.terminate()
                    process.wait(timeout=10)
                    raise RuntimeError('resource harness exceeded its 150-second diagnostic budget')
            status = process.wait()
            selector.close()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        failures = []
        if status or not events or events[-1]['phase'] != 'finished':
            failures.append('harness did not finish successfully')
        if any(row['helpers'] > 2 for row in snapshots):
            failures.append('two-helper bound exceeded')
        if not args.mutable and len(observed) < 10:
            failures.append('sustained demand did not exercise expected worker recycling')
        idle = [row for row in snapshots if row['phase'] == 'idle' and row['phase_seconds'] >= 1]
        expired = [row for row in idle if row['phase_seconds'] >= 32]
        hits = [row for row in snapshots if row['phase'] == 'memory-hit']
        if not idle or any(row['memory_current'] > 64 * 1024 * 1024 for row in idle):
            failures.append('64-MiB retained idle scope bound failed')
        if not expired or any(row['helpers'] for row in expired):
            failures.append('idle workers did not expire without replacement')
        if not hits or any(row['helpers'] for row in hits):
            failures.append('adequate memory hit prepared a worker')
        if snapshots[-1]['helpers']:
            failures.append('scopes remained after shutdown')
        if 'Preview runtime failure' in (args.output / 'stderr.log').read_text():
            failures.append('runtime or cleanup failure was reported')
        generations = [runtime] if args.mutable else list((runtime / 'generations').iterdir())
        storage = [{'id': path.name, 'files': sum(p.is_file() for p in path.rglob('*')),
                    'bytes': sum(p.stat().st_size for p in path.rglob('*') if p.is_file())} for path in generations]
        if len(storage) > 2 or any(row['files'] > 128 or row['bytes'] > 128 * 1024 * 1024 for row in storage):
            failures.append('generation storage bound exceeded')
        data = dict(failures=failures, events=events, observed_workers=len(observed), generations=storage,
            maximum_helpers=max(row['helpers'] for row in snapshots),
            maximum_scope_memory=max(row['memory_current'] for row in snapshots),
            maximum_idle_memory=max((row['memory_current'] for row in idle), default=None),
            cpu_user_seconds=after.ru_utime - before.ru_utime, cpu_system_seconds=after.ru_stime - before.ru_stime,
            process_maxrss_kib=after.ru_maxrss, wall_seconds=time.monotonic() - start,
            sampling='10-ms polling; transient peaks may fall between samples; memory.current is scope accounting')
        (args.output / 'summary.json').write_text(json.dumps(data, indent=2) + '\n')
        if failures:
            raise RuntimeError('; '.join(failures))
        if not args.mutable:
            fixtures.generations.run(SimpleNamespace(runtime=runtime, helper=args.helper.resolve(), command='remove',
                maintenance_migrate=False, ownership_manifest=None))
        print(json.dumps({key: value for key, value in data.items() if key != 'events'}), flush=True)


if __name__ == '__main__':
    main()
