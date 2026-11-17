#!/usr/bin/env python3
"""Offline verification of a blocked native attempt; imports no execution implementation."""
import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evidence as e

h = e.h


def verify(root):
    inventory = h.sealed(root)
    assessment = h.read(root / 'assessment.json')
    h.require(assessment['status'] == 'blocked' and assessment['decision'] == 'Evidence insufficient',
              'this verifier only accepts blocked attempts')
    h.require(assessment['attempted'] == 0 and assessment['unexecuted'] == e.historical.protocol()['schedule'] and
              assessment['staging'] == 'not attempted' and assessment['native_correctness'] == 'unvalidated',
              'blocked schedule or prerequisite accounting')
    h.require(h.read(root / 'protocol.json') == e.historical.protocol(), 'protocol mismatch')
    h.require(h.read(root / 'package.json') == e.package(), 'approved input binding mismatch')
    h.require(h.read(root / 'integrity.json') == dict(unchanged=True), 'input drift')
    tools = h.read(root / 'tools.json')
    # An ended attempt remains verifiable from its captured tooling. Later edits
    # cannot make it executable or change its blocked decision.
    h.require(set(tools) <= set(e.tools()) and
              {str(Path(__file__).parents[1] / n) for n in ('evidence.py', 'run.py', 'PROTOCOL.md')} <= set(tools),
              'tool snapshot membership')
    for path, digest in tools.items():
        h.require(h.digest(root / 'tools' / Path(path).name) == digest, 'tool snapshot mismatch')
    expected = ['compiler', 'cmake', 'dependencies']
    for arm in ('control', 'early'):
        for component in ('holonight-images', 'holonight-thumbnails', 'holonight-file-browser'):
            expected += [arm + '/' + component + '-configure', arm + '/' + component + '-compile']
            if component == 'holonight-images':
                expected += [arm + '/runtime']
            expected += [arm + '/' + component + '-install']
        expected += [arm + '/harness-configure', arm + '/harness-compile']
    actual = {name[:-len('-command.json')] for name in inventory if name.endswith('-command.json')}
    h.require(actual and actual == set(expected[:len(actual)]), 'commands are not the unretried build prefix')
    fixed = {'assessment.json', 'integrity.json', 'package.json', 'protocol.json', 'tools.json',
             'host.json', 'REPORT.md', 'seal.json'} | {'tools/' + Path(p).name for p in tools}
    records = {name + suffix for name in actual for suffix in
               ('-command.json', '-result.json', '.stdout', '.stderr')}
    for name in inventory:
        h.require(name in fixed | records or any(name.startswith(arm + '/' + group + '/')
            for arm in ('control', 'early') for group in ('build', 'prefix', 'runtime', 'harness-build')),
            'unexpected artifact membership')
    h.require(set(n[:-len('-result.json')] for n in inventory if n.endswith('-result.json')) == actual,
              'unpaired process result')
    failed = []
    previous = 0
    for name in expected[:len(actual)]:
        command = h.read(root / (name + '-command.json'))
        result = h.read(root / (name + '-result.json'))
        h.require(command['cwd'] == str(e.ROOT) and command['timeout_seconds'] == 600 and
                  command['environment']['QT_QPA_PLATFORM'] == 'offscreen' and
                  command['environment']['CMAKE_BUILD_PARALLEL_LEVEL'] == '4', 'command execution context')
        argv = command['argv']
        if '/' not in name:
            identity = {'compiler': ['c++', '--version'], 'cmake': ['cmake', '--version'],
                'dependencies': ['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp']}
            h.require(argv == identity[name], 'host identity command changed')
        else:
            arm, label = name.split('/')
            base = root / arm
            component, operation = label.rsplit('-', 1) if '-' in label else ('', label)
            if operation == 'configure' and component != 'harness':
                source = e.PACKAGE / arm / 'source' / component
                options = (['-DHOLONIGHT_IMAGES_ISOLATED=ON', '-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE=' + str(base / 'runtime')]
                    if component == 'holonight-images' else ['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON']
                    if component == 'holonight-thumbnails' else
                    ['-DBUILD_FILE_BROWSER_' + n + '=OFF' for n in ('QUICK', 'SEARCH', 'STORAGE', 'PREVIEW_QUICK', 'MARKDOWN')])
                expected_argv = ['cmake', '-S', str(source), '-B', str(base / 'build' / component), '-G', 'Ninja',
                    '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=OFF', '-DCMAKE_INSTALL_PREFIX=' + str(base / 'prefix'),
                    '-DCMAKE_PREFIX_PATH=' + str(base / 'prefix'), *options]
            elif operation == 'compile':
                directory = base / 'harness-build' if component == 'harness' else base / 'build' / component
                expected_argv = ['cmake', '--build', str(directory), '--parallel', '4']
            elif operation == 'install':
                expected_argv = ['cmake', '--install', str(base / 'build' / component)]
            elif label == 'runtime':
                expected_argv = [sys.executable, str(e.PACKAGE / arm / 'source/holonight-images/scripts/prepare-isolated-runtime.py'),
                    '--helper', str(base / 'build/holonight-images/holonight-images-helper'), '--plugins', '/usr/lib/qt6/plugins',
                    '--output', str(base / 'runtime')]
            elif label == 'harness-configure':
                expected_argv = ['cmake', '-S', str(e.PACKAGE / arm / 'harness-source'), '-B', str(base / 'harness-build'),
                    '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(base / 'prefix'),
                    '-DPREVIEW_REUSE_BENCHMARK=ON', '-DREUSABLE_VARIANT=ON']
            else:
                raise ValueError('unrecognized command')
            h.require(argv == expected_argv, 'native command changed')
        h.require(type(result['start_ns']) is int and type(result['stop_ns']) is int and
                  previous <= result['start_ns'] <= result['stop_ns'], 'process chronology')
        previous = result['stop_ns']
        for suffix in ('.stdout', '.stderr'):
            h.require(name + suffix in inventory, 'missing raw process output')
        if result['exit'] != 0 or result['failure'] is not None:
            failed.append(name)
    if failed:
        h.require(failed == [expected[len(actual) - 1]], 'first failure did not end build')
        last = h.read(root / (failed[0] + '-result.json'))
        h.require(bool(last['failure']) and bool(assessment.get('failure')), 'missing failure explanation')
    else:
        h.require(len(actual) == len(expected) and assessment.get('failure') ==
                  'native correctness gates not yet validated; execution prohibited', 'unsupported blocker')
    h.require(not any('harness.json' in n or 'observations.json' in n for n in inventory), 'unexpected observations')
    h.require(set(p.name for p in (root / 'tools').iterdir()) == {Path(p).name for p in tools}, 'snapshot membership')
    return dict(status='passed', outcome='blocked', decision='Evidence insufficient',
        evidence_seal=h.digest(root / 'seal.json'), failed_command=failed[0] if failed else None,
        commands=len(actual), observations=0, imports_runner=False,
        live_tools_unchanged=tools == e.tools(),
        verifier_sha256=h.digest(Path(__file__)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.evidence.absolute(), args.output.absolute()
    h.require(output == output.resolve() and not output.exists() and
              not output.is_relative_to(root) and not root.is_relative_to(output), 'verification collision/overlap')
    try:
        result = verify(root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = dict(status='failed', failure=str(error), decision='Evidence insufficient')
    h.write(output, result)
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
