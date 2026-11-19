#!/usr/bin/env python3
"""Independently validate the stopped native correctness attempt. Never imports a runner."""
import argparse
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evidence as e

h = e.h
spec = e.load('publication_blocked_build_verifier', Path(__file__).with_name('verify.py'))


def verify(root):
    inventory = h.sealed(root)
    assessment = h.read(root / 'assessment.json')
    h.require(assessment['status'] == 'blocked' and assessment['phase'] == 'correctness' and
              assessment['stage'] == 'correctness-control' and assessment['attempted'] == 0 and
              assessment['native_correctness'] == 'unvalidated' and assessment['staging'] == 'not attempted' and
              assessment['unexecuted'] == e.historical.protocol()['schedule'] and
              assessment['decision'] == 'Evidence insufficient', 'native blocked result accounting')
    binding = h.read(root / 'built.json')
    built = Path(binding['path'])
    h.require(h.digest(built / 'seal.json') == binding['seal'], 'consumed build seal mismatch')
    native_build = spec.verify(built)
    h.require(native_build['failed_command'] is None and native_build['commands'] == 27, 'incomplete provider build')
    h.require(h.read(root / 'package.json') == h.read(built / 'package.json'), 'approved package mismatch')
    h.require(h.read(root / 'protocol.json') == e.historical.protocol(), 'protocol mismatch')
    h.require(h.read(root / 'integrity.json') == dict(unchanged=True), 'input/tool drift')
    tools = h.read(root / 'tools.json')
    h.require(set(tools) <= set(e.tools()), 'unexpected snapshot tool')
    for path, digest in tools.items():
        h.require(h.digest(root / 'tools' / Path(path).name) == digest, 'snapshot tool mismatch')
    native_inputs = h.read(root / 'native-inputs.json')
    h.require(h.inventory(root / 'native-source') == native_inputs, 'native correctness source membership')
    base = root / 'control'
    commands = ['correctness-configure', 'correctness-compile', 'harness-linkage', 'helper-linkage', 'correctness-tests']
    raw = set()
    previous = 0
    for index, name in enumerate(commands):
        row = h.read(base / (name + '-command.json'))
        result = h.read(base / (name + '-result.json'))
        h.require(row['cwd'] == str(e.ROOT) and row['timeout_seconds'] == 600 and
                  row['environment']['QT_QPA_PLATFORM'] == 'offscreen' and
                  row['environment']['CMAKE_BUILD_PARALLEL_LEVEL'] == '4', 'native command context')
        prefix = built / 'control/prefix'
        expected = {
            'correctness-configure': ['cmake', '-S', str(root / 'native-source'), '-B', str(base / 'build'),
                '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(prefix),
                '-DFROZEN=' + str(e.PACKAGE / 'control/source'), '-DRUNTIME=' + str(built / 'control/runtime'),
                '-DFIXTURES=' + str(e.historical.e.Q / 'fixtures')],
            'correctness-compile': ['cmake', '--build', str(base / 'build'), '--parallel', '4'],
            'harness-linkage': ['ldd', str(built / 'control/harness-build/preview-benchmark')],
            'helper-linkage': ['ldd', str(built / 'control/build/holonight-images/holonight-images-helper')],
            'correctness-tests': [str(base / 'build/publication-correctness'),
                '--gtest_filter=Publication.*:IsolatedPreview.TargetChangeWhileCommittingDropsOldPixelsAndCache:'
                'IsolatedPreview.CancellationDuringCacheReadPreventsCommitAndLateDisplay:Cleanup.*:Verification.*:Generation.*',
                '--gtest_output=xml:' + str(base / 'native-tests.xml')],
        }
        h.require(row['argv'] == expected[name], 'native command mismatch')
        h.require(type(result['start_ns']) is int and type(result['stop_ns']) is int and
                  previous <= result['start_ns'] <= result['stop_ns'], 'native command chronology')
        previous = result['stop_ns']
        if index < len(commands) - 1:
            h.require(result['exit'] == 0 and result['failure'] is None, 'continued after native failure')
        else:
            h.require(result['exit'] == 1 and bool(result['failure']) and assessment['failure'] == result['failure'],
                      'native failure not reflected in decision')
        for suffix in ('-command.json', '-result.json', '.stdout', '.stderr'):
            raw.add('control/' + name + suffix)
            h.require('control/' + name + suffix in inventory, 'missing native raw record')
    environment = h.read(base / 'native-environment.json')
    h.require(environment['PUBLICATION_ARM'] == 'control' and bool(environment['HOLONIGHT_CACHE_INVOCATION']) and
              environment['XDG_CACHE_HOME'] == str(base / 'cache') and
              environment['TMPDIR'] == str(base / 'temporary-source'), 'native invocation environment mismatch')
    resolution = h.read(base / 'package-resolution.json')
    h.require(set(resolution) == {'HolonightImages_DIR', 'HolonightThumbnails_DIR', 'HolonightFileBrowser_DIR'} and
              all(Path(p).is_relative_to(built / 'control/prefix') for p in resolution.values()), 'installed provider binding')
    xml = ET.parse(base / 'native-tests.xml').getroot()
    cases = xml.findall('.//testcase')
    failures = [case for case in cases if case.find('failure') is not None]
    h.require(int(xml.attrib['tests']) == len(cases) == 21 and int(xml.attrib['failures']) == len(failures) == 1 and
              failures[0].attrib['classname'] == 'Publication' and failures[0].attrib['name'] ==
              'CommitBarrierRejectsCancelledSupersededTimedOutAndShutdownResults' and not xml.findall('.//skipped'),
              'raw native XML does not corroborate failure')
    stdout = (base / 'correctness-tests.stdout').read_text()
    h.require('[  FAILED  ] Publication.CommitBarrierRejectsCancelledSupersededTimedOutAndShutdownResults' in stdout and
              '[  PASSED  ] 20 tests.' in stdout, 'raw test log mismatch')
    h.require(h.read(root / 'correctness.json') == dict(passed=False, arms={}), 'native failure falsely accepted')
    fixed = {'assessment.json', 'integrity.json', 'REPORT.md', 'tools.json', 'package.json', 'protocol.json',
             'built.json', 'native-inputs.json', 'correctness.json', 'seal.json', 'control/native-environment.json',
             'control/native-tests.xml', 'control/package-resolution.json'}
    fixed |= {'tools/' + Path(path).name for path in tools}
    fixed |= {'native-source/' + name for name in native_inputs}
    h.require(all(name in fixed | raw or name.startswith(('control/build/', 'control/cache/',
              'control/temporary-source/')) for name in inventory), 'unexpected native attempt artifact')
    return dict(status='passed', outcome='blocked', decision='Evidence insufficient',
        evidence_seal=h.digest(root / 'seal.json'), native_tests=21, passed=20, failed=1,
        early_arm_unexecuted=True, observations=0, imports_runner=False,
        verifier_sha256=h.digest(Path(__file__)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.evidence.absolute(), args.output.absolute()
    h.require(output == output.resolve() and not output.exists() and not output.is_relative_to(root) and
              not root.is_relative_to(output), 'verification output collision/overlap')
    try:
        result = verify(root)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        result = dict(status='failed', decision='Evidence insufficient', failure=str(error))
    h.write(output, result)
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
