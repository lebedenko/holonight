#!/usr/bin/env python3
"""Desktop-only, gated userspace sampling of the unchanged C validation harness."""
import argparse
import importlib.util
import json
import os
import re
from pathlib import Path
import select
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


p = module('cpu_preparation', 'prepare-preview-cpu-profile.py')
v, o, require, read, write = p.v, p.o, p.require, p.read, p.write
r = v.r


def record_argv(path, pid, control, ack):
    return ['perf', 'record', '--event', 'cpu-clock:u', '--freq', '999', '--strict-freq',
            '--call-graph', 'dwarf,16384', '--user-callchains', '--clockid', 'mono', '--mmap-pages', '256',
            '--no-buildid-cache', '--timestamp', '--period', '--pid', str(pid),
            '--delay', '-1', '--control', f'fd:{control},{ack}', '--output', str(path)]


def offline_env():
    env, credentials = r.session()
    require(not credentials and os.geteuid() == 1000, 'recorder and readers require desktop ownership')
    return dict(env, DEBUGINFOD_URLS='', DEBUGINFOD_PROGRESS='0', PERF_BUILDID_DIR='/dev/null')


def gate(fd, ready, argv):
    require(os.geteuid() == 1000, 'execution gate requires desktop ownership')
    os.write(ready, b'ready\n')
    os.close(ready)
    require(os.read(fd, 1) == b'G', 'execution gate not released')
    os.close(fd)
    os.execvpe(argv[0], argv, os.environ)


def wait_ready(fd, process, deadline, now=time.monotonic, readable=select.select, receive=os.read):
    data = b''
    while b'\n' not in data:
        require(process.poll() is None, 'gate exited before readiness')
        remaining = min(5, deadline - now())
        require(remaining > 0 and readable([fd], [], [], remaining)[0], 'gate readiness timeout')
        chunk = receive(fd, 64)
        require(bool(chunk), 'gate readiness EOF')
        data += chunk
        require(len(data) <= 6, 'malformed gate readiness')
    require(data == b'ready\n', 'malformed gate readiness')


def terminate(process, now=time.monotonic, deadline=None):
    """Bound group termination and reaping to one five-second deadline."""
    deadline = now() + 5 if deadline is None else deadline
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=max(0, deadline - now() - 1))
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=max(0, deadline - now()))
    require(now() <= deadline, 'gate cleanup budget exceeded')


def stop_recorder(process, deadline, ready=False, now=time.monotonic, kill_group=os.killpg):
    """Share the workload's termination deadline, including forced cleanup."""
    result = dict(passed=False, reaped=False, forced=False, sigint_sent=False)
    if process.poll() is None:
        process.send_signal(signal.SIGINT)
        result['sigint_sent'] = True
    try:
        code = process.wait(timeout=max(0, deadline-now()-1))
    except subprocess.TimeoutExpired:
        result['forced'] = True
        kill_group(process.pid, signal.SIGKILL)
        code = process.wait(timeout=max(0, deadline-now()))
    result.update(reaped=True, exit=code)
    result['passed'] = not result['forced'] and now() <= deadline and (code == 0 or
                      (ready and result['sigint_sent'] and code == -signal.SIGINT))
    return result


def identity(pid):
    root = Path('/proc') / str(pid)
    return dict(pid=pid, stat=(root / 'stat').read_text(), status=(root / 'status').read_text(),
                cmdline=(root / 'cmdline').read_bytes().hex(),
                namespaces={path.name: os.readlink(path) for path in (root / 'ns').iterdir()})


def acknowledge(fd, recorder, directory, deadline, now=time.monotonic,
                readable=select.select, receive=os.read):
    data = b''
    try:
        while b'\n' not in data:
            require(recorder.poll() is None, 'recorder exited before acknowledgement')
            remaining = deadline - now()
            require(remaining > 0 and readable([fd], [], [], remaining)[0], 'recorder readiness timeout')
            chunk = receive(fd, 64)
            data += chunk
            require(chunk and len(data) <= 5, 'recorder readiness failed')
        require(data in (b'ack\n', b'ack\n\0') and recorder.poll() is None, 'recorder readiness failed')
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            write(directory / 'recorder-ack.json', dict(hex=data.hex(), ns=time.monotonic_ns()))
        except Exception:
            if not active_error:
                raise


def cleanup_all(process, recorder, descriptors, deadline, ready=False):
    """Every cleanup is attempted, even after a different cleanup fails."""
    outcomes = {}
    for name, child, action in (
            ('gate', process, lambda: terminate(process, deadline=deadline)),
            ('recorder', recorder, lambda: stop_recorder(recorder, deadline, ready=ready))):
        try:
            value = action() if child is not None else None
            outcomes[name] = dict(reaped=child is None or child.poll() is not None, result=value)
        except Exception as error:
            outcomes[name] = dict(reaped=child is None or child.poll() is not None, error=str(error))
    outcomes['descriptors'] = []
    for fd in descriptors:
        if fd is not None:
            try:
                os.close(fd)
                outcomes['descriptors'].append(dict(fd=fd, closed=True))
            except OSError as error:
                outcomes['descriptors'].append(dict(fd=fd, closed=False, error=str(error)))
    outcomes['passed'] = (all(outcomes[name]['reaped'] and 'error' not in outcomes[name] and
                              not (outcomes[name].get('result') or {}).get('forced', False)
                              for name in ('gate', 'recorder')) and
                          all(row['closed'] for row in outcomes['descriptors']))
    return outcomes


def workload(argv, target, profiled, recorder_command=record_argv):
    """Attach while blocked, acknowledge perf, then exec without changing PID."""
    require(os.geteuid() == 1000, 'no privileged recorder fallback')
    start = time.monotonic()
    deadline = start + 30
    release_r = release_w = ready_r = ready_w = ctl_r = ctl_w = ack_r = ack_w = None
    process = recorder = None
    cleanup = None
    timed_out = False
    cleanup_deadline = None
    env = offline_env()
    failure = None
    released = acknowledged = False
    directory = target.parent / (target.stem + '-recording')
    directory.mkdir()
    try:
        release_r, release_w = os.pipe()
        ready_r, ready_w = os.pipe()
        ctl_r, ctl_w = os.pipe()
        ack_r, ack_w = os.pipe()
        with target.with_suffix('.stdout').open('x') as stdout, target.with_suffix('.stderr').open('x') as stderr:
            gate_command = [sys.executable, '-B', str(Path(__file__).resolve()), 'gate',
                            '--fd', str(release_r), '--ready', str(ready_w), '--', *argv]
            process = subprocess.Popen(gate_command, env=env, pass_fds=(release_r, ready_w),
                                       stdout=stdout, stderr=stderr, start_new_session=True)
            os.close(release_r); release_r = None
            os.close(ready_w); ready_w = None
            wait_ready(ready_r, process, deadline)
            write(directory / 'gate.json', dict(identity=identity(process.pid), pid=process.pid, uid=os.geteuid(), argv=argv,
                  stat=Path(f'/proc/{process.pid}/stat').read_text(), ready_ns=time.monotonic_ns()))
            if profiled:
                command = recorder_command(directory / 'perf.data', process.pid, ctl_r, ack_w)
                write(directory / 'record-command.json', command)
                with (directory / 'recorder.stdout').open('x') as rout, (directory / 'recorder.stderr').open('x') as rerr:
                    recorder = subprocess.Popen(command, env=env, pass_fds=(ctl_r, ack_w),
                                                stdout=rout, stderr=rerr, start_new_session=True)
                write(directory / 'recorder-identity.json', identity(recorder.pid))
                os.close(ctl_r); ctl_r = None
                os.close(ack_w); ack_w = None
                os.write(ctl_w, b'enable\n')
                acknowledge(ack_r, recorder, directory, min(deadline, time.monotonic() + 5))
                acknowledged = True
            require(time.monotonic() < deadline, 'readiness exhausted session budget')
            write(directory / 'release.json', dict(pid=process.pid, ns=time.monotonic_ns(), profiled=profiled))
            os.write(release_w, b'G')
            released = True
            os.close(release_w); release_w = None
            try:
                code = process.wait(timeout=max(0, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                timed_out = True
                cleanup_deadline = deadline + 5
                terminate(process, deadline=cleanup_deadline)
                code = process.returncode
            require(not timed_out and time.monotonic() <= deadline, 'workload session timeout')
            if recorder:
                cleanup_deadline = time.monotonic() + 5
                cleanup = stop_recorder(recorder, cleanup_deadline, ready=True)
                write(directory / 'recorder-shutdown.json', cleanup)
                require(cleanup['passed'], 'recorder shutdown failed')
            result = dict(exit=code, timeout=timed_out, cleanup_verified=True,
                          pid=process.pid, start_ns=int(start * 1e9), stop_ns=time.monotonic_ns())
            write(target.with_suffix('.process.json'), result)
            require(code == 0, 'workload execution failed')
            return result
    except Exception as error:
        failure = dict(type=type(error).__name__, message=str(error), errno=getattr(error, 'errno', None))
        stderr_path = directory / 'recorder.stderr'
        try:
            failure['recorder_stderr'] = stderr_path.read_text() if stderr_path.exists() else ''
        except OSError as evidence_error:
            failure['stderr_read_failure'] = str(evidence_error)
        raise
    finally:
        if cleanup_deadline is None:
            cleanup_deadline = min(deadline, time.monotonic()) + 5
        outcomes = cleanup_all(process, recorder if cleanup is None else None,
                               (release_r, release_w, ready_r, ready_w, ctl_r, ctl_w, ack_r, ack_w),
                               cleanup_deadline, ready=acknowledged)
        if failure is not None and (directory / 'recorder.stderr').exists():
            try:
                failure['recorder_stderr'] = (directory / 'recorder.stderr').read_text()
            except OSError as evidence_error:
                failure['stderr_read_failure'] = str(evidence_error)
        partial = dict(timeout=timed_out, cleanup=cleanup,
              cleanup_outcomes=outcomes, first_failure=failure, released=released,
              acknowledged=acknowledged, cleanup_deadline=cleanup_deadline,
              gate_reaped=process is None or process.poll() is not None, stop_ns=time.monotonic_ns())
        try:
            write(directory / 'partial.json', partial)
        except Exception:
            if failure is None:
                raise
        if failure is None:
            require(outcomes['passed'], 'process/descriptor cleanup failed')


def export(target, symfs):
    directory = target.parent / (target.stem + '-recording')
    env = offline_env()
    header = r.command(['perf', 'report', '--header-only', '--stdio', '-i', str(directory / 'perf.data')],
                       directory, 'header', env=env)
    r.clock_header(header)
    require('cpu-clock:u' in header, 'wrong recorded event')
    r.command(['perf', 'script', '--ns', '--show-task-events', '--show-lost-events', '--no-inline',
               '--symfs', str(symfs), '-F', 'comm,pid,tid,time,period,event,ip,sym,symoff,dso',
               '-i', str(directory / 'perf.data')], directory, 'export', env=env)
    text = (directory / 'export.stdout').read_text()
    require(not any(word in text.upper() for word in ('PERF_RECORD_LOST', 'PERF_RECORD_THROTTLE')),
            'capture loss/throttling')
    require(not any(word in (directory / 'recorder.stderr').read_text().lower() for word in
                    ('lost chunks', 'lost samples', 'failed', 'error:')), 'recorder capture failure')
    return text


def mirror_helper(package, root):
    """Expose the frozen helper at its workload namespace path for offline readers."""
    identity = read(package / 'inputs.json')['binaries']['helper']
    source = Path(identity['path'])
    require(o.digest(source) == identity['sha256'] and p.build_id(source) == identity['build_id'],
            'frozen helper identity drift')
    target = root / 'usr/libexec/holonight-images-helper'
    require(copy_ordinary(source, target) == identity['sha256'], 'helper mirror identity drift')


def symfs(package, output):
    """Private mirror: no writes to the system or earlier evidence/cache."""
    root = output / 'symfs'
    root.mkdir()
    for name, identity in read(package / 'inputs.json')['dependencies'].items():
        for path in (Path('/usr/lib') / name, Path(identity['host'])):
            target = root / str(path).lstrip('/')
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copyfile(identity['payload'], target)
        symbol = read(package / 'symbols.json')[name]
        target = root / 'usr/lib/debug/.build-id' / symbol['build_id'][:2] / (symbol['build_id'][2:] + '.debug')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(symbol['path'], target)
    mirror_helper(package, root)
    # Unstripped private binaries/providers retain their original DWARF sections.
    base = p.BUILT / 'validation/C'
    for path in [base / 'reuse-harness/preview-benchmark', base / 'build/holonight-images/holonight-images-helper',
                 *list((base / 'prefix/lib').glob('*.so*'))]:
        target = root / str(path).lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(path.resolve(), target)
    return root


def commands(output, runtime):
    return [dict(invocation=dict(row, variant='C', mode='validation', fixture='3200x2400.png', captured=False),
                 argv=[str(p.BUILT / 'validation/C/reuse-harness/preview-benchmark'), str(runtime / 'validation/C'),
                       str(o.old.FIXTURE_ROOT / '3200x2400.png'), 'startup', str(row['observations']),
                       str(output / 'observations' / f'{index:03}.json')])
            for index, row in enumerate(p.schedule())]


def run_schedule(entries, result, integrity, launch, account, save):
    require([dict((k, e['invocation'][k]) for k in ('arm', 'block', 'warmup', 'observations')) for e in entries] ==
            p.schedule(), 'schedule drift')
    for index, entry in enumerate(entries):
        integrity()
        row = dict(index=index, status='failed', entry=entry)
        result['invocations'].append(row)
        result.update(launched_invocations=index + 1, unexecuted_invocations=9 - index)
        save()
        process = launch(index, entry)
        values = account(index, entry, process)
        require(len(values) == entry['invocation']['observations'], 'observation accounting mismatch')
        integrity()
        row.update(status='passed', process=process)
        key = 'warmup_observations' if entry['invocation']['warmup'] else 'measured_observations'
        result[key] += len(values)
        save()
    require(result['measured_observations'] == 40 and result['warmup_observations'] == 2, 'final counts mismatch')


RECOVERY = ROOT / 'build/preview-cpu-replay-20261115-02'
RECOVERY_FINAL = ROOT / 'build/preview-cpu-replay-20261115-02-final-independent.json'


def preflight_execution(package, output):
    """Read-only admission; no destination reservation, staging or workload."""
    context = replay_environment()
    environment = offline_env()
    require(not output.exists() and not output.is_symlink() and output.parent.is_dir() and
            os.access(output.parent, os.W_OK), 'execution destination unavailable')
    runtime = Path('/run') / ('holonight-validation-' + output.name)
    require(not runtime.exists() and not runtime.is_symlink(), 'runtime collision')
    for tool in ('perf', 'readelf'):
        require(shutil.which(tool) is not None, 'missing reader: ' + tool)
    verifier = module('cpu_execution_preflight', 'verify-preview-cpu-profile.py')
    verifier.seal(package)
    require(read(package / 'assessment.json')['status'] == 'prepared', 'symbol preparation blocked')
    require(read(package / 'protocol.json') == p.protocol(), 'prepared protocol drift')
    require(p.frozen_inputs() == read(package / 'inputs.json'), 'frozen preparation drift')
    for symbol in read(package / 'symbols.json').values():
        require(o.digest(Path(symbol['path'])) == symbol['sha256'] and
                p.build_id(Path(symbol['path'])) == symbol['build_id'], 'debug identity drift')
    final = read(RECOVERY_FINAL)
    verifier.seal(RECOVERY)
    require(final['status'] == 'passed' and final['replay'] == 'complete' and
            final['replay_seal'] == o.digest(RECOVERY / 'seal.json'), 'recovery acceptance drift')
    consumed = list(dict.fromkeys([package, RECOVERY, *replay_inputs(Path(read(RECOVERY / 'preregistration.json')['source']))]))
    previous = ROOT / 'build/preview-cpu-profile-20261115-02-execution'
    if previous.exists():
        consumed.extend([previous, ROOT / 'build/preview-cpu-profile-20261115-02-analysis'])
    runtimes = {str(path): o.gate.protected_inventory(path) for path in
                sorted(Path('/run').glob('holonight-validation-preview-cpu-profile-*-execution/validation/C'))}
    seals = {}
    for source in consumed:
        verifier.seal(source)
        seals[str(source)] = o.digest(source / 'seal.json')
    installer = r.INSTALLER
    hashes = read(Path(read(p.PACKAGE / 'provenance.json')['prepared']) / 'input-integrity.json')['before']
    for name in ('manage-images-generations.py', 'install_state.py'):
        require(o.digest(installer / name) == hashes[str(installer / name)], 'installer identity drift')
    return dict(status='passed', context=context, environment=environment, runtime=str(runtime),
                historical_seals=seals, historical_runtimes=runtimes, recovery=str(RECOVERY), recovery_final=str(RECOVERY_FINAL),
                recovery_final_sha256=o.digest(RECOVERY_FINAL))


def execute(package, output):
    preflight = preflight_execution(package, output)
    o.fresh(output, package, p.BUILT, p.PACKAGE)
    result = dict(status='blocked', invocations=[], launched_invocations=0, unexecuted_invocations=10,
                  measured_observations=0, warmup_observations=0, stage='provenance')
    try:
        o.check_output(package)
        require(read(package / 'assessment.json')['status'] == 'prepared', 'symbol preparation blocked')
        frozen = read(package / 'inputs.json')
        require(p.frozen_inputs() == frozen, 'frozen preparation drift')
        tools = {str(path): o.digest(path) for path in [Path(__file__).resolve(),
                 ROOT / 'scripts/prepare-preview-cpu-profile.py', ROOT / 'scripts/report-preview-cpu-profile.py',
                 ROOT / 'scripts/verify-preview-cpu-profile.py']}
        write(output / 'tool-identities.json', tools)
        snapshots = output / 'tools'; snapshots.mkdir()
        for name in tools:
            shutil.copyfile(name, snapshots / Path(name).name)
        targets = output / 'observations'; targets.mkdir()
        runtime = Path('/run') / ('holonight-validation-' + output.name)
        require(not runtime.exists() and not runtime.is_symlink(), 'runtime collision')
        entries = commands(output, runtime)
        mirror = symfs(package, output)
        installer = r.INSTALLER / 'manage-images-generations.py'
        snapshots = read(Path(read(p.PACKAGE / 'provenance.json')['prepared']) / 'input-integrity.json')['before']
        installer_hashes = {str(r.INSTALLER / name): snapshots[str(r.INSTALLER / name)] for name in
                            ('manage-images-generations.py', 'install_state.py')}
        request = dict(mode='validation', variant='C', built=str(p.BUILT), built_seal=o.digest(p.BUILT / 'seal.json'),
                       execution=str(output), installer=str(installer), installer_sha256=o.digest(installer),
                       installer_hashes=installer_hashes)
        write(output / 'stage-request.json', request)
        stage = [sys.executable, '-B', str(ROOT / 'scripts/run-preview-validation.py'), 'stage',
                 '--request', str(output / 'stage-request.json'), '--output', str(runtime / 'validation/C')]
        clock = dict(name='CLOCK_MONOTONIC', provenance=dict(
                     boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                     host=Path('/etc/machine-id').read_text().strip()))
        write(output / 'preregistration.json', dict(execution_version=2, preflight=preflight, protocol=p.protocol(), commands=entries, staging=['sudo', '-A', *stage],
              stage_request=request, package=str(package), package_seal=o.digest(package / 'seal.json'),
              symbols=read(package / 'symbols.json'), environment=offline_env(), clock=clock,
              recorder_template=record_argv(Path('perf.data'), '<gate-pid>', '<control-fd>', '<ack-fd>')))
        r.isolated(targets / 'initial.json')
        result['stage'] = 'staging'
        r.command(['sudo', '-A', *stage], output, 'staging', timeout=600)
        protected = o.staged(p.BUILT / 'validation', runtime / 'validation', 'C')
        write(output / 'protected-runtime.json', protected)

        def integrity():
            require(replay_environment() == preflight['context'], 'host/runtime context drift')
            for path, inventory in preflight.get('historical_runtimes', {}).items():
                require(o.gate.protected_inventory(Path(path)) == inventory, 'historical runtime drift')
            for source, digest in preflight['historical_seals'].items():
                o.check_output(Path(source))
                require(o.digest(Path(source) / 'seal.json') == digest, 'historical seal drift')
            require(o.digest(RECOVERY_FINAL) == preflight['recovery_final_sha256'], 'recovery acceptance drift')
            o.check_output(package)
            require(p.frozen_inputs() == frozen, 'input drift')
            require(o.gate.protected_inventory(runtime / 'validation/C') == protected, 'protected runtime drift')
            require(clock['provenance']['boot_id'] == Path('/proc/sys/kernel/random/boot_id').read_text().strip(), 'boot drift')
            for name, digest in {**tools, **installer_hashes}.items():
                require(o.digest(Path(name)) == digest, 'tool/installer drift')

        # A synthetic process creates a worker thread and a descendant after exec.
        # Its markers bind exported sample timestamps and exec PID to this gate.
        rehearsal = output / 'rehearsal.json'
        synthetic = [sys.executable, '-B', str(Path(__file__).resolve()), 'synthetic']
        integrity()
        result['stage'] = 'rehearsal-recording'
        workload(synthetic, rehearsal, True)
        result['stage'] = 'rehearsal-mirror'
        complete_mirror(output / 'rehearsal-recording', mirror, output / 'rehearsal-recording')
        result['stage'] = 'rehearsal-export'
        text = export(rehearsal, mirror)
        reporter = module('cpu_reporter', 'report-preview-cpu-profile.py')
        result['stage'] = 'rehearsal-validation'
        reporter.rehearsal(rehearsal, text)
        integrity()

        def launch(index, entry):
            target = Path(entry['argv'][-1])
            r.isolated(target)
            result['stage'] = 'workload'
            return workload(entry['argv'], target, entry['invocation']['arm'] == 'profiled')

        def account(index, entry, process):
            target = Path(entry['argv'][-1])
            values = o.validate(target, dict(entry['invocation'], mode='v4'), process, 1000)
            r.isolated(target.with_name(target.stem + '-after.json'))
            observations, endpoints = reporter.validation.invocation(entry, index, p.BUILT, output)
            if entry['invocation']['arm'] == 'profiled':
                result['stage'] = 'mapping'
                complete_mirror(target.parent / (target.stem + '-recording'), mirror,
                                target.parent / (target.stem + '-recording'))
                result['stage'] = 'export'
                text = export(target, mirror)
                result['stage'] = 'accounting'
                reporter.account(target, text, observations)
            write(target.with_suffix('.cpu-observations.json'), observations)
            return values

        run_schedule(entries, result, integrity, launch, account, lambda: write(output / 'progress.json', result))
        integrity()
        result.update(status='complete', stage='complete')
    except v.ERRORS as error:
        result.update(failure=str(error), failure_stage=result['stage'])
    finally:
        try:
            r.isolated(output / 'final.json')
            r.residuals(output)
        except v.ERRORS as error:
            result.update(status='blocked', cleanup_failure=str(error))
        if (output / 'symfs').exists():
            write(output / 'symbol-mirror.json', o.inventory(output / 'symfs'))
        write(output / 'assessment.json', result)
        (output / 'ASSESSMENT.md').write_text('CPU experiment: ' + result['status'] + '\nStage: ' +
            result['stage'] + '\n' + result.get('failure', '') + '\nUnexecuted invocations: ' +
            str(result['unexecuted_invocations']) + '\n')
        o.seal(output)
    return result


DIAGNOSTIC_CASES = [dict(mode=mode, settings=settings) for mode in ('launched', 'attached')
                    for settings in ('minimal', 'full')]
TRACE_SYSCALLS = 'perf_event_open,mmap,munmap,ioctl,read,write,poll,ppoll,close,fcntl,prctl'


def diagnostic_command(path, pid=None, control=None, ack=None, settings='full', traced=True):
    if settings == 'full':
        command = record_argv(path, pid, control, ack)
        command.remove('--user-callchains')  # Reproduce the original approved options.
        if pid is None:
            # Launch mode needs neither a target PID nor a delayed enable exchange.
            command = command[:command.index('--pid')] + ['--output', str(path)]
    else:
        command = ['perf', 'record', '--event', 'cpu-clock:u', '--output', str(path)]
        if pid is not None:
            command += ['--pid', str(pid), '--delay', '-1', '--control', f'fd:{control},{ack}']
    command.insert(2, '-vv')
    if traced:
        command = ['strace', '-f', '-ttt', '-T', '-s', '256', '-e', 'trace=' + TRACE_SYSCALLS,
                   '-o', str(path.parent / 'syscalls.log'), *command]
    return command


def diagnostic_context():
    import resource
    paths = ('/proc/sys/kernel/perf_event_paranoid', '/proc/sys/kernel/perf_event_mlock_kb',
             '/proc/sys/kernel/perf_event_max_sample_rate', '/sys/kernel/security/lsm',
             '/sys/kernel/security/lockdown', '/proc/self/attr/current', '/proc/self/cgroup')
    context = dict(identity=identity(os.getpid()), uid=os.getuid(), euid=os.geteuid(),
                   gid=os.getgid(), groups=os.getgroups(), kernel=list(os.uname()),
                   parent=identity(os.getppid()), environment={k: os.environ.get(k) for k in
                   ('XDG_SESSION_ID', 'XDG_SESSION_TYPE', 'XDG_RUNTIME_DIR', 'DISPLAY', 'WAYLAND_DISPLAY')},
                   limits={name: list(resource.getrlimit(getattr(resource, name))) for name in
                           ('RLIMIT_NOFILE', 'RLIMIT_MEMLOCK', 'RLIMIT_CPU', 'RLIMIT_AS')}, security={})
    for name in paths:
        try:
            context['security'][name] = Path(name).read_text()
        except OSError as error:
            context['security'][name] = dict(error=str(error), errno=error.errno)
    for tool in ('perf', 'strace'):
        path = Path(shutil.which(tool) or '/missing')
        context[tool] = dict(path=str(path), sha256=o.digest(path),
                             version=subprocess.check_output([tool, '--version'], text=True).strip())
    return context


def diagnostic_launched(target, settings):
    directory = target.parent / (target.stem + '-recording'); directory.mkdir()
    command = diagnostic_command(directory / 'perf.data', settings=settings)
    command += ['--', sys.executable, '-B', str(Path(__file__).resolve()), 'synthetic']
    write(directory / 'record-command.json', command)
    start = time.monotonic(); deadline = start + 30
    process = None; failure = None
    try:
        with (directory / 'recorder.stdout').open('x') as out, (directory / 'recorder.stderr').open('x') as err:
            process = subprocess.Popen(command, env=offline_env(), stdout=out, stderr=err, start_new_session=True)
            write(directory / 'recorder-identity.json', identity(process.pid))
            code = process.wait(timeout=max(0, deadline-time.monotonic()))
            require(code == 0, 'perf-launched recording failed: exit ' + str(code))
    except Exception as error:
        failure = dict(type=type(error).__name__, message=str(error), errno=getattr(error, 'errno', None))
        raise
    finally:
        cleanup_deadline = min(deadline, time.monotonic()) + 5
        outcomes = cleanup_all(process, None, (), cleanup_deadline)
        write(directory / 'partial.json', dict(first_failure=failure, cleanup_outcomes=outcomes,
              released=False, acknowledged=False, cleanup_deadline=cleanup_deadline, stop_ns=time.monotonic_ns()))
        if failure is None:
            require(outcomes['passed'], 'launched cleanup failed')


def diagnose(output):
    """Synthetic-only: deliberately does not call execute, staging or commands."""
    require(os.geteuid() == 1000, 'diagnostics require desktop user; no privileged fallback')
    stopped = ROOT / 'build/preview-cpu-profile-20261115-01-execution'
    package = ROOT / 'build/preview-cpu-profile-20261115-02-prepared'
    o.fresh(output, stopped, package, p.BUILT, p.PACKAGE)
    result = dict(status='blocked', cases=[], launched_invocations=0, unexecuted_invocations=10,
                  confirmation='not run: no demonstrated recorder repair')
    protected = None
    def integrity():
        # The ordinary-file mirror, original launch snapshots and stopped evidence
        # are checked in place, never repaired or resealed by this entrypoint.
        o.check_output(stopped); o.check_output(package)
        runtime = Path('/run/holonight-validation-' + stopped.name) / 'validation/C'
        return dict(stopped=o.digest(stopped / 'seal.json'), package=o.digest(package / 'seal.json'),
                    runtime=o.gate.protected_inventory(runtime))
    try:
        protected = integrity()
        write(output / 'preserved-before.json', protected)
        write(output / 'context.json', diagnostic_context())
        write(output / 'preregistration.json', dict(cases=DIAGNOSTIC_CASES, timeout_seconds=30,
              termination_grace_seconds=5, retries=0, synthetic_only=True,
              earlier_permission_check=dict(status='unverified', command=None, context=None),
              full_template=diagnostic_command(Path('perf.data'), '<pid>', '<control>', '<ack>', traced=False),
              trace_syscalls=TRACE_SYSCALLS))
        snapshots = output / 'tools'; snapshots.mkdir()
        for name in ('run-preview-cpu-profile.py', 'verify-preview-cpu-profile.py'):
            shutil.copyfile(ROOT / 'scripts' / name, snapshots / name)
        for index, case in enumerate(DIAGNOSTIC_CASES):
            require(integrity() == protected, 'protected input drift')
            row = dict(index=index, **case, status='passed')
            target = output / f'{index:02}-{case["mode"]}-{case["settings"]}.json'
            try:
                if case['mode'] == 'attached':
                    def command(path, pid, control, ack):
                        return diagnostic_command(path, pid, control, ack, settings=case['settings'])
                    workload([sys.executable, '-B', str(Path(__file__).resolve()), 'synthetic'],
                             target, True, recorder_command=command)
                else:
                    diagnostic_launched(target, case['settings'])
            except Exception as error:
                row.update(status='failed', failure=str(error))
            directory = target.parent / (target.stem + '-recording')
            partial = read(directory / 'partial.json')
            require(partial['cleanup_outcomes']['passed'], 'diagnostic cleanup failure')
            trace = (directory / 'syscalls.log').read_text()
            result['cases'].append(row)
            row['event_open_lines'] = [line for line in trace.splitlines() if 'perf_event_open(' in line]
            require(row['event_open_lines'], 'missing event-opening evidence')
            if row['status'] == 'failed':
                require(any('= -1 E' in line and 'PERF_COUNT_SW_CPU_CLOCK' in line and
                            ('sample_freq=' in line or 'sample_period=' in line) and
                            'PERF_SAMPLE_IP' in line for line in row['event_open_lines']),
                        'failure not explained by event-opening denial; stop')
            write(output / 'progress.json', result)
            require(integrity() == protected, 'protected input drift')
        result['cause'] = ('See perf_event_open attributes and errno in each syscall log. '
                           'No host policy, capability or privileged fallback was attempted.')
        result['status'] = 'diagnosed'
    except Exception as error:
        result['failure'] = str(error)
    finally:
        if protected is not None:
            try:
                after = integrity()
                write(output / 'preserved-after.json', after)
                require(after == protected, 'protected input drift')
            except Exception as error:
                result.update(status='blocked', integrity_failure=str(error))
        write(output / 'assessment.json', result)
        o.seal(output)
    return result


def confirm(output, diagnostic):
    """One untraced synthetic rehearsal after an evidence-supported repair."""
    require(os.geteuid() == 1000, 'confirmation requires desktop user')
    verifier = module('cpu_confirmation_verifier', 'verify-preview-cpu-profile.py')
    verifier.verify_diagnostic(diagnostic)
    package = ROOT / 'build/preview-cpu-profile-20261115-02-prepared'
    stopped = ROOT / 'build/preview-cpu-profile-20261115-01-execution'
    o.fresh(output, package, stopped, diagnostic)
    result = dict(status='blocked', launched_invocations=0, unexecuted_invocations=10, attempts=1)
    before = None
    stage = 'source'
    def integrity():
        o.check_output(stopped); o.check_output(package); o.check_output(diagnostic)
        return dict(stopped=o.digest(stopped / 'seal.json'), package=o.digest(package / 'seal.json'),
                    diagnostic=o.digest(diagnostic / 'seal.json'), runtime=o.gate.protected_inventory(
                        Path('/run/holonight-validation-' + stopped.name) / 'validation/C'))
    try:
        before = integrity()
        write(output / 'preserved-before.json', before)
        write(output / 'preregistration.json', dict(attempts=1, retries=0, synthetic_only=True,
              traced=False, diagnostic=str(diagnostic), diagnostic_seal=o.digest(diagnostic / 'seal.json'),
              repair='--user-callchains excludes unintended kernel callchains; DWARF settings unchanged'))
        write(output / 'context.json', diagnostic_context())
        snapshots = output / 'tools'; snapshots.mkdir()
        for name in ('run-preview-cpu-profile.py', 'verify-preview-cpu-profile.py'):
            shutil.copyfile(ROOT / 'scripts' / name, snapshots / name)
        stage = 'mirror'
        mirror = symfs(package, output)
        target = output / 'rehearsal.json'
        stage = 'recording'
        workload([sys.executable, '-B', str(Path(__file__).resolve()), 'synthetic'], target, True)
        stage = 'mirror'
        complete_mirror(output / 'rehearsal-recording', mirror, output)
        write(output / 'symbol-mirror.json', o.inventory(mirror))
        stage = 'export'
        text = export(target, mirror)
        stage = 'rehearsal'
        reporter = module('cpu_confirmation_reporter', 'report-preview-cpu-profile.py')
        reporter.rehearsal(target, text)
        require(o.inventory(mirror) == read(output / 'symbol-mirror.json'), 'symbol mirror drift')
        for row in read(output / 'mirror-sources.json'):
            require(o.digest(Path(row['source'])) == row['sha256'], 'source export drift')
        result['status'] = 'complete'
    except Exception as error:
        result.update(failure=str(error), failure_stage=stage)
        partial = output / 'rehearsal-recording/partial.json'
        if partial.is_file():
            result['workload_failure'] = read(partial)['first_failure']
    finally:
        if before is not None:
            try:
                after = integrity()
                write(output / 'preserved-after.json', after)
                require(after == before, 'protected input drift')
            except Exception as error:
                result.update(status='blocked', integrity_failure=str(error))
        write(output / 'assessment.json', result)
        o.seal(output)
    return result


def mapped_elfs(text, mirror=None):
    """Read identities from MMAP2, never infer dependencies from today's loader."""
    mappings = {}
    excluded = []
    for line in text.splitlines():
        if 'PERF_RECORD_MMAP2 ' not in line:
            continue
        match = re.search(r'\]: [rwxps-]+ (.+)$', line)
        require(match is not None, 'unparsed MMAP2 record')
        path = match[1]
        if path.startswith('[') or path.startswith('//anon'):
            excluded.append(line)
            continue
        require(path.startswith('/') and '..' not in Path(path).parts, 'unsafe mapped path')
        candidate = mirror / path.lstrip('/') if mirror is not None else Path(path)
        candidate = candidate if candidate.is_file() else Path(path).resolve(strict=True)
        with candidate.open('rb') as stream:
            elf = stream.read(4) == b'\x7fELF'
        if not elf:
            excluded.append(dict(record=line, source=str(candidate), sha256=o.digest(candidate),
                                 reason='non-ELF file contents'))
            continue
        identity = re.search(r'<([0-9a-f]+)>', line)
        require(identity is not None and set(identity[1]) != {'0'}, 'missing mapped build ID: ' + path)
        require(path not in mappings or mappings[path] == identity[1], 'conflicting mapped build IDs: ' + path)
        mappings[path] = identity[1]
    require(bool(mappings), 'no recorded ELF mappings')
    return dict(files=mappings, excluded=excluded)


def copy_ordinary(source, target):
    require(not target.exists() and not target.is_symlink(), 'symbol destination collision: ' + str(target))
    before = o.digest(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    require(not any(parent.is_symlink() for parent in (target.parent, *target.parents)), 'linked destination')
    with source.open('rb') as src, target.open('xb') as dst:
        shutil.copyfileobj(src, dst)
    require(o.digest(source) == before == o.digest(target), 'symbol source changed while copying')
    return before


def complete_mirror(recording, mirror, evidence):
    raw = r.command(['perf', 'script', '-D', '-i', str(recording / 'perf.data')],
                    evidence, 'mappings', env=offline_env())
    mappings = mapped_elfs(raw, mirror)
    write(evidence / 'mapped-elfs.json', mappings)
    rows = []
    for path, identity in mappings['files'].items():
        target = mirror / path.lstrip('/')
        frozen = target.exists()
        source = target if frozen else Path(path).resolve(strict=True)
        require(source.is_file() and not source.is_symlink(), 'unavailable ELF: ' + path)
        before = o.digest(source)
        require(p.build_id(source) == identity, 'mapped build ID mismatch: ' + path)
        if not frozen:
            require(copy_ordinary(source, target) == before, 'source changed before copy')
        require(o.digest(source) == before == o.digest(target), 'mapped ELF changed')
        rows.append(dict(recorded_path=path, source=str(source), build_id=identity,
                         sha256=before, frozen=frozen))
    write(evidence / 'mirror-sources.json', rows)
    return rows


RUNTIME = Path('/run/holonight-validation-preview-cpu-profile-20261115-01-execution/validation/C')


def replay_environment():
    require(os.geteuid() == os.getuid() == 1000, 'replay requires desktop UID 1000')
    require(Path('/proc/self/uid_map').read_text().split() == ['0', '0', '4294967295'],
            'host user namespace mismatch')
    references = [path for path in Path('/proc').iterdir() if path.name.isdigit() and
                  path.stat().st_uid == 1000 and (path / 'comm').read_text().strip() == 'Hyprland']
    require(len(references) == 1, 'desktop compositor unavailable')
    namespaces = {}
    for name in ('user', 'mnt', 'pid'):
        current = os.readlink('/proc/self/ns/' + name)
        require(current == os.readlink(references[0] / 'ns' / name), 'host namespace mismatch: ' + name)
        namespaces[name] = current
    return dict(uid=os.getuid(), namespaces=namespaces, runtime=o.gate.protected_inventory(RUNTIME))


def replay_inputs(source):
    registration = read(source / 'preregistration.json')
    return [source, Path(registration['diagnostic']),
            ROOT / 'build/preview-cpu-profile-20261115-01-execution',
            ROOT / 'build/preview-cpu-profile-20261115-02-prepared', p.BUILT, p.PACKAGE,
            ROOT / 'build/preview-cpu-replay-20261115-01']


def preflight_confirmation(source, output=None):
    context = replay_environment()
    env = offline_env()
    verifier = module('cpu_preflight_verifier', 'verify-preview-cpu-profile.py')
    for path in replay_inputs(source):
        verifier.seal(path)
    verifier.verify_confirmation(source)
    for tool in ('perf', 'readelf'):
        require(shutil.which(tool) is not None, 'missing reader: ' + tool)
    if output is not None:
        require(not output.exists() and not output.is_symlink() and output.parent.is_dir() and
                os.access(output.parent, os.W_OK), 'replay destination unavailable')
    perf = source / 'rehearsal-recording/perf.data'
    before = o.digest(perf)
    raw = subprocess.check_output(['perf', 'script', '-D', '-i', str(perf)], text=True, env=env)
    mappings = mapped_elfs(raw, source / 'symfs')
    identities = {}
    for path, identity in mappings['files'].items():
        frozen = source / 'symfs' / path.lstrip('/')
        candidate = frozen if frozen.is_file() else Path(path).resolve(strict=True)
        require(p.build_id(candidate) == identity, 'mapped build ID mismatch: ' + path)
        identities[path] = dict(source=str(candidate), sha256=o.digest(candidate), build_id=identity)
    require(o.digest(perf) == before, 'recording changed during preflight')
    return dict(status='passed', context=context, perf_sha256=before, mappings=mappings, identities=identities)


def replay_confirmation(source, output):
    """Offline-only recovery: no staging, workload or recorder entrypoints."""
    verifier = module('cpu_replay_verifier', 'verify-preview-cpu-profile.py')
    preflight = preflight_confirmation(source, output)
    o.fresh(output, source)
    result = dict(status='blocked', attempts=1, recording_attempts=0, retries=0,
                  launched_invocations=0, unexecuted_invocations=10)
    before = None
    stage = 'source'
    consumed = replay_inputs(source)
    runtime = RUNTIME
    def integrity():
        for path in consumed:
            verifier.seal(path)
        return dict(seals={str(path): o.digest(path / 'seal.json') for path in consumed},
                    runtime=o.gate.protected_inventory(runtime), source=o.inventory(source))
    try:
        tools = output / 'tools'; tools.mkdir()
        for name in ('run-preview-cpu-profile.py', 'verify-preview-cpu-profile.py',
                     'prepare-preview-cpu-profile.py', 'report-preview-cpu-profile.py'):
            copy_ordinary(ROOT / 'scripts' / name, tools / name)
        write(output / 'preregistration.json', dict(source=str(source), source_seal=o.digest(source / 'seal.json'),
              preflight=preflight, consumed_inputs=[str(path) for path in consumed],
              attempts=1, recording_attempts=0, retries=0, offline_only=True,
              perf_data=str(source / 'rehearsal-recording/perf.data'),
              perf_sha256=o.digest(source / 'rehearsal-recording/perf.data'),
              environment=offline_env(), tool_identities=o.inventory(tools),
              commands=[['perf', 'script', '-D', '-i', str(source / 'rehearsal-recording/perf.data')],
                        ['perf', 'report', '--header-only', '--stdio', '-i', str(source / 'rehearsal-recording/perf.data')],
                        ['perf', 'script', '--ns', '--show-task-events', '--show-lost-events', '--no-inline',
                         '--symfs', str(output / 'symfs'), '-F', 'comm,pid,tid,time,period,event,ip,sym,symoff,dso',
                         '-i', str(source / 'rehearsal-recording/perf.data')]]))
        before = integrity()
        write(output / 'preserved-before.json', before)
        verifier.verify_confirmation(source)
        stage = 'mirror'
        mirror = output / 'symfs'; mirror.mkdir()
        for path in (source / 'symfs').rglob('*'):
            require(not path.is_symlink(), 'linked frozen mirror')
            if path.is_file():
                copy_ordinary(path, mirror / path.relative_to(source / 'symfs'))
        complete_mirror(source / 'rehearsal-recording', mirror, output)
        write(output / 'symbol-mirror.json', o.inventory(mirror))
        for suffix in ('.stdout', '.process.json'):
            copy_ordinary(source / ('rehearsal' + suffix), output / ('rehearsal' + suffix))
        directory = output / 'rehearsal-recording'; directory.mkdir()
        for name in ('gate.json', 'release.json', 'recorder-ack.json', 'partial.json',
                     'recorder-shutdown.json', 'record-command.json', 'recorder.stderr'):
            copy_ordinary(source / 'rehearsal-recording' / name, directory / name)
        stage = 'export'
        registration = read(output / 'preregistration.json')
        for command, name in zip(registration['commands'][1:], ('header', 'export')):
            r.command(command, directory, name, env=offline_env())
        stage = 'rehearsal'
        reporter = module('cpu_replay_reporter', 'report-preview-cpu-profile.py')
        reporter.rehearsal(output / 'rehearsal.json', (directory / 'export.stdout').read_text())
        verifier.confirmation_stacks(source, output)
        require(o.inventory(mirror) == read(output / 'symbol-mirror.json'), 'mirror export drift')
        for row in read(output / 'mirror-sources.json'):
            require(o.digest(Path(row['source'])) == row['sha256'], 'source export drift')
        result['status'] = 'complete'
    except Exception as error:
        result.update(failure=str(error), failure_stage=stage)
        partial = output / 'rehearsal-recording/partial.json'
        if partial.is_file():
            result['workload_failure'] = read(partial)['first_failure']
    finally:
        if before is not None:
            try:
                after = integrity()
                write(output / 'preserved-after.json', after)
                require(after == before, 'protected evidence drift')
            except Exception as error:
                result.update(status='blocked', integrity_failure=str(error))
        write(output / 'assessment.json', result)
        o.seal(output)
    return result


def synthetic():
    import threading
    def busy():
        begin = time.monotonic_ns()
        print(json.dumps(dict(pid=os.getpid(), tid=threading.get_native_id(), start_ns=begin)), flush=True)
        value = 1
        while time.monotonic_ns() - begin < 150_000_000:
            value = (value * 17 + 1) % 999983
        print(json.dumps(dict(pid=os.getpid(), tid=threading.get_native_id(), stop_ns=time.monotonic_ns())), flush=True)
    child = os.fork()
    if child == 0:
        busy(); os._exit(0)
    thread = threading.Thread(target=busy)
    thread.start(); busy(); thread.join()
    _, status = os.waitpid(child, 0)
    require(status == 0, 'synthetic descendant failed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    g = subs.add_parser('gate')
    g.add_argument('--fd', type=int, required=True); g.add_argument('--ready', type=int, required=True)
    g.add_argument('argv', nargs=argparse.REMAINDER)
    subs.add_parser('synthetic')
    d = subs.add_parser('diagnose')
    d.add_argument('--output', type=Path, required=True)
    c = subs.add_parser('confirm')
    c.add_argument('--output', type=Path, required=True)
    c.add_argument('--diagnostic', type=Path, required=True)
    preflight = subs.add_parser('preflight-confirmation')
    preflight.add_argument('--confirmation', type=Path, required=True)
    preflight.add_argument('--output', type=Path)
    replay = subs.add_parser('replay-confirmation')
    replay.add_argument('--confirmation', type=Path, required=True)
    replay.add_argument('--output', type=Path, required=True)
    pre = subs.add_parser('preflight-execution')
    pre.add_argument('--package', type=Path, required=True)
    pre.add_argument('--output', type=Path, required=True)
    e = subs.add_parser('execute')
    e.add_argument('--package', type=Path, required=True); e.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.action == 'gate':
        gate(args.fd, args.ready, args.argv[1:] if args.argv[:1] == ['--'] else args.argv)
    elif args.action == 'preflight-execution':
        result = preflight_execution(args.package.absolute(), args.output.absolute())
        print(dict(status=result['status'], context=result['context']['namespaces'], runtime=result['runtime']))
    elif args.action == 'synthetic':
        synthetic()
    elif args.action == 'diagnose':
        result = diagnose(args.output.absolute())
        print({k: val for k, val in result.items() if k != 'cases'})
        sys.exit(result['status'] != 'diagnosed')
    elif args.action == 'preflight-confirmation':
        result = preflight_confirmation(args.confirmation.absolute(), args.output.absolute() if args.output else None)
        print(dict(status=result['status'], mapped_elfs=len(result['mappings']['files']),
                   excluded_mappings=len(result['mappings']['excluded'])))
    elif args.action == 'replay-confirmation':
        result = replay_confirmation(args.confirmation.absolute(), args.output.absolute())
        print(result)
        sys.exit(result['status'] != 'complete')
    elif args.action == 'confirm':
        result = confirm(args.output.absolute(), args.diagnostic.absolute())
        print(result)
        sys.exit(result['status'] != 'complete')
    else:
        result = execute(args.package.absolute(), args.output.absolute())
        print({k: val for k, val in result.items() if k != 'invocations'})
        sys.exit(result['status'] != 'complete')
