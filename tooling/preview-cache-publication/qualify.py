#!/usr/bin/env python3
"""Run installed native gates against retained successful provider compilations."""
import argparse
import os
from pathlib import Path
import shutil
import sys
import uuid
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
import evidence as e
import run

h = e.h


def qualify(built, output):
    def work(result):
        h.sealed(built)
        source_assessment = h.read(built / 'assessment.json')
        h.require(source_assessment['failure'] == 'native correctness gates not yet validated; execution prohibited',
                  'cannot resume a compilation or native correctness failure')
        commands = list(built.glob('*-result.json')) + list(built.glob('*/*-result.json'))
        h.require(len(commands) == 27 and all(h.read(p)['exit'] == 0 and h.read(p)['failure'] is None
                  for p in commands), 'provider compilation incomplete or failed')
        h.write(output / 'built.json', dict(path=str(built), seal=h.digest(built / 'seal.json')))
        native = Path(__file__).parent / 'native'
        inputs = h.inventory(native)
        shutil.copytree(native, output / 'native-source')
        h.write(output / 'native-inputs.json', inputs)
        h.write(output / 'correctness.json', dict(passed=False, arms={}))
        for arm in ('control', 'early'):
            result['stage'] = 'correctness-' + arm
            base = output / arm
            base.mkdir()
            runtime = built / arm / 'runtime'
            prefix = built / arm / 'prefix'
            run.command(['cmake', '-S', output / 'native-source', '-B', base / 'build', '-G', 'Ninja',
                '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(prefix),
                '-DFROZEN=' + str(e.PACKAGE / arm / 'source'), '-DRUNTIME=' + str(runtime),
                '-DFIXTURES=' + str(e.historical.e.Q / 'fixtures')], base, 'correctness-configure')
            run.command(['cmake', '--build', base / 'build', '--parallel', '4'], base, 'correctness-compile')
            cache = (base / 'build/CMakeCache.txt').read_text()
            resolution = {line.split(':', 1)[0]: line.split('=', 1)[1] for line in cache.splitlines()
                if line.startswith(('HolonightImages_DIR:', 'HolonightThumbnails_DIR:', 'HolonightFileBrowser_DIR:'))}
            h.require(len(resolution) == 3 and all(Path(p).is_relative_to(prefix) for p in resolution.values()),
                      'native gate must resolve installed arm providers')
            h.write(base / 'package-resolution.json', resolution)
            for name, relative in [('harness', 'harness-build/preview-benchmark'),
                                   ('helper', 'build/holonight-images/holonight-images-helper')]:
                path = built / arm / relative
                run.command(['ldd', path], base, name + '-linkage')
                h.require('not found' not in (base / (name + '-linkage.stdout')).read_text(), 'unresolved native dependency')
            environment = dict(HOLONIGHT_CACHE_INVOCATION=str(uuid.uuid4()), PUBLICATION_ARM=arm,
                XDG_CACHE_HOME=str(base / 'cache'), TMPDIR=str(base / 'temporary-source'))
            for key in ('XDG_CACHE_HOME', 'TMPDIR'):
                Path(environment[key]).mkdir(mode=0o700)
            h.write(base / 'native-environment.json', environment)
            previous = {key: os.environ.get(key) for key in environment}
            try:
                os.environ.update(environment)
                run.command([base / 'build/publication-correctness',
                    '--gtest_filter=Publication.*:IsolatedPreview.TargetChangeWhileCommittingDropsOldPixelsAndCache:'
                    'IsolatedPreview.CancellationDuringCacheReadPreventsCommitAndLateDisplay:Cleanup.*:Verification.*:Generation.*',
                    '--gtest_output=xml:' + str(base / 'native-tests.xml')], base, 'correctness-tests')
            finally:
                for key, value in previous.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
            try:
                xml = ET.parse(base / 'native-tests.xml').getroot()
            except ET.ParseError as error:
                raise ValueError('malformed native test XML') from error
            h.require(int(xml.attrib['tests']) > 0 and all(int(xml.attrib.get(k, '0')) == 0
                for k in ('failures', 'disabled', 'errors')) and not xml.findall('.//skipped'),
                'required native checks failed or skipped')
            correctness = h.read(output / 'correctness.json')
            correctness['arms'][arm] = dict(passed=True, tests=int(xml.attrib['tests']))
            h.write(output / 'correctness.json', correctness)
        h.require(h.inventory(native) == inputs, 'native gate source drift')
        raise ValueError('protected-session, generation, runtime verification and installed-consumer gates remain unvalidated')
    return run.action(output, 'correctness', work)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--built', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = qualify(args.built.absolute(), args.output.absolute())
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'qualified')
