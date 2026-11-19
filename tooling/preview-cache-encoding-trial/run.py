#!/usr/bin/env python3
"""Prepare and run the single, private synchronous store investigation."""
import argparse
import difflib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import contract as c
h = c.h


def commands(output):
    prefix = c.historical.BUILT / 'common/prefix'
    return [
        ['cmake','-S',str(output/'native'),'-B',str(output/'native-build'),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(prefix)],
        ['cmake','--build',str(output/'native-build'),'--parallel','4'],
        ['ldd',str(output/'native-build/investigate')],
        [str(output/'native-build/investigate'),'mapping'],
        [str(output/'native-build/investigate'),str(output/'corpus'),str(output/'raw.json')]]


def command(output, index, argv, environment, timeout):
    """Persist failure and owned cleanup evidence before propagating any error."""
    launch = dict(argv=argv, cwd=str(output/'corpus'), environment=environment,
        timeout_seconds=timeout, start_new_session=True)
    h.write(output/f'command-{index}.json', launch)
    result = dict(exit=None, pid=None, start_ns=time.monotonic_ns(), stop_ns=None,
        failure=None, timed_out=False, cleanup=False, reaped=False,
        group_absent=False, cleanup_seconds=0.0, cleanup_failure=None)
    process = None
    try:
        with (output/f'{index}.stdout').open('x') as stdout, (output/f'{index}.stderr').open('x') as stderr:
            process = subprocess.Popen(argv, cwd=launch['cwd'], env=environment,
                stdout=stdout, stderr=stderr, start_new_session=True)
            result['pid'] = process.pid
            result['exit'] = process.wait(timeout=timeout)
            h.require(result['exit'] == 0, 'command failed: '+str(index))
    except (OSError,ValueError,subprocess.SubprocessError,KeyboardInterrupt) as error:
        result['failure'] = str(error) or type(error).__name__
        result['timed_out'] = isinstance(error, subprocess.TimeoutExpired)
    finally:
        cleanup_start = time.monotonic()
        try:
            if process is not None:
                cleanup = c.historical.e.load('encoding_owned_cleanup', c.ROOT/'scripts/run-preview-cpu-profile.py')
                cleanup.terminate(process, deadline=cleanup_start+5)
                result['exit'] = process.returncode
                result['reaped'] = process.returncode is not None
                try:
                    os.killpg(process.pid, 0)
                except ProcessLookupError:
                    result['group_absent'] = True
                h.require(result['reaped'] and result['group_absent'], 'process group survived or was not reaped')
            else:
                result['group_absent'] = True
            h.require(time.monotonic()-cleanup_start <= 5, 'cleanup deadline')
            result['cleanup'] = True
        except (OSError,ValueError,subprocess.SubprocessError,KeyboardInterrupt) as error:
            result['cleanup_failure'] = str(error) or type(error).__name__
        finally:
            result['cleanup_seconds'] = time.monotonic()-cleanup_start
            result['stop_ns'] = time.monotonic_ns()
            h.write(output/f'result-{index}.json', result)
    h.require(result['failure'] is None and result['cleanup'], result['failure'] or result['cleanup_failure'])
    return result


def investigate(output, source):
    h.require(output == c.OUTPUT and not os.path.lexists(output), 'fresh fixed investigation destination required')
    h.require(h.digest(source) == c.SOURCE_SHA, 'matching dependency source required')
    binding = c.prerequisite()
    output.mkdir()
    result = dict(status='stopped', decision='Evidence insufficient', completed=0, failure=None)
    identities = c.tools()
    h.write(output/'tools.json', identities)
    (output/'tools').mkdir()
    for name, digest in identities.items():
        shutil.copyfile(name, output/'tools'/c.historical.snapshot_name(name))
    h.write(output/'binding.json', binding)
    shutil.copyfile(source, output/'qpnghandler.cpp')
    shutil.copyfile('/usr/lib/qt6/sbom/qtbase-6.12.0.spdx', output/'qtbase.spdx')
    h.require('025bdad181de241e81bf853c8a2d7bf3d19261a9' in (output/'qtbase.spdx').read_text(), 'installed source revision')
    corpus = output/'corpus'
    corpus.mkdir()
    shutil.copyfile(binding['retained']['retained']['fixture']['path'], corpus/'textured.png')
    shutil.copyfile(binding['jpeg']['path'], corpus/'oriented.jpg')
    shutil.copytree(c.DIRECTORY/'native', output/'native')
    frozen = c.historical.Q/'C/source/holonight-thumbnails'
    for mode in c.MODES:
        dest = output/'sources'/mode
        shutil.copytree(frozen, dest)
        path = dest/'src/cache.cpp'
        before = path.read_text()
        after = c.transform(before,mode)
        path.write_text(after)
        (output/(mode+'.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True))))
        if mode != 'default':
            header=(dest/'include/holonight_thumbnails/cache.h').read_text()
            (dest/'store.h').write_text(header.replace('HolonightThumbnails','Store_'+mode))
    env = dict(PATH='/usr/bin:/bin', HOME=str(output/'home'), LANG='C.UTF-8', QT_QPA_PLATFORM='offscreen', XDG_CACHE_HOME=str(output/'cache'))
    (output/'home').mkdir()
    rows = commands(output)
    h.write(output/'schedule.json', rows)
    h.write(output/'environment.json',env)
    h.write(output/'limits.json',dict(command_seconds=list(c.COMMAND_TIMEOUTS),shared_cleanup_seconds=5))
    # Freeze complete inputs before compiling or collecting exploratory timings.
    h.write(output/'freeze.json', h.inventory(output))
    try:
        for index, argv in enumerate(rows):
            h.require(c.tools() == identities, 'tool drift')
            command_env = dict(env)
            if index == 3:
                command_env['LD_PRELOAD'] = str(output/'native-build/libmapping.so')
            command(output,index,argv,command_env,c.COMMAND_TIMEOUTS[index])
            result['completed'] += 1
            if index == 2:
                libraries = {}
                for line in (output/'2.stdout').read_text().splitlines():
                    for token in line.split():
                        if token.startswith('/') and Path(token).is_file():
                            path = Path(token).resolve()
                            libraries[str(path)] = h.digest(path)
                h.write(output/'libraries.json',libraries)
                h.write(output/'artifacts.json',{str(p):h.digest(p) for p in
                    [output/'native-build/investigate', output/'native-build/libmapping.so',
                     *(output/'native-build'/('libstore_'+mode+'.a') for mode in c.MODES)]})
            if index == 3:
                h.require((output/'3.stderr').read_text().splitlines() == ['PNG_LEVEL 1','PNG_LEVEL 0'], 'runtime compression mapping unresolved')
            print('command',index,'passed',flush=True)
        result.update(c.assess(h.read(output/'raw.json')),status='complete')
        h.require(all(h.digest(Path(p)) == digest for p,digest in h.read(output/'libraries.json').items()),'runtime library drift')
        h.require(c.prerequisite() == binding and c.tools() == identities,'input drift')
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError,KeyboardInterrupt) as error:
        result.update(status='stopped',decision='Evidence insufficient',failure=str(error) or type(error).__name__)
    h.write(output/'assessment.json',result)
    h.write(output/'seal.json',h.inventory(output))
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['investigate'])
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--qt-source',type=Path,required=True)
    args=parser.parse_args()
    result=investigate(args.output,args.qt_source)
    print(h.json.dumps(result,indent=2))
    sys.exit(result['status'] != 'complete')
