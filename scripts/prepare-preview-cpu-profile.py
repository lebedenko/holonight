#!/usr/bin/env python3
"""Prepare the fixed C userspace attribution experiment without launching previews."""
import argparse
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cpu_validation', ROOT / 'scripts/run-preview-validation.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
o, require, read, write = v.o, v.require, v.read, v.write
BUILT = ROOT / 'build/preview-validation-20261115-04-built'
PACKAGE = ROOT / 'build/preview-validation-20261115-04-prepared'
FINAL = ROOT / 'build/preview-validation-20261115-04-final-verification.json'
LIBRARIES = ('libQt6Core.so.6', 'libcrypto.so.4', 'libc.so.6')


def schedule():
    rows = [dict(arm=arm, block=None, warmup=True, observations=1) for arm in ('unprofiled', 'profiled')]
    for block in range(4):
        arms = ('unprofiled', 'profiled') if block % 2 == 0 else ('profiled', 'unprofiled')
        rows.extend(dict(arm=arm, block=block, warmup=False, observations=5) for arm in arms)
    return rows


def protocol():
    return dict(schedule=schedule(), invocations=10, measured_observations=40, warmup_observations=2,
                timeout_seconds=30, termination_grace_seconds=5, retries=0,
                event='cpu-clock:u', frequency=999, strict_frequency=True, inheritance=True,
                call_graph='dwarf,16384', clock='CLOCK_MONOTONIC', mmap_pages=256,
                all_cpus=False, privileged_recorder=False, automatic_symbol_downloads=False)


def build_id(path, run=subprocess.check_output):
    notes = run(['readelf', '-n', str(path)], text=True)
    matches = re.findall(r'Build ID: ([0-9a-f]+)', notes)
    require(len(matches) == 1, 'missing/ambiguous ELF build ID: ' + str(path))
    return matches[0]


def validate_symbols(binary, symbols):
    require(build_id(binary) == build_id(symbols), 'debug build ID mismatch: ' + str(binary))
    sections = subprocess.check_output(['readelf', '-SW', str(symbols)], text=True)
    require('.debug_info' in sections and '.debug_line' in sections and '.symtab' in sections,
            'required debug sections missing: ' + str(symbols))


def frozen_inputs():
    final = read(FINAL)
    require(final['status'] == 'passed' and final['independent_verification'] == 'passed', 'attempt-04 not accepted')
    for name, digest in final['input_seals'].items():
        require(o.digest(Path(name) / 'seal.json') == digest, 'attempt-04 seal identity drift: ' + name)
    # Validate the consumed native artifacts and source provenance, reusing the
    # completed native build/linkage checks rather than rebuilding for profiling.
    v.check_package(PACKAGE)
    o.check_output(BUILT)
    require(read(BUILT / 'assessment.json')['status'] == 'built', 'native build blocked')
    require(read(BUILT / 'integrity.json')['before'][str(PACKAGE)] == o.inventory(PACKAGE), 'native source provenance drift')
    base = BUILT / 'validation/C'
    binaries = {}
    for label in ('harness', 'helper'):
        saved = read(base / (label + '-identity.json'))
        binary = Path(saved['path'])
        require(o.digest(binary) == saved['sha256'] and 'not found' not in saved['linkage'], 'native identity/linkage drift')
        binaries[label] = dict(path=str(binary), sha256=o.digest(binary), build_id=build_id(binary))
    manifest = read(base / 'runtime/manifest.json')
    mapping = v.ordinal_mapping(manifest)
    require(mapping == read(base / 'manifest-ordinals.json'), 'manifest mapping drift')
    for row in mapping:
        require(o.digest(base / 'runtime' / row['path']) == row['sha256'] and
                (base / 'runtime' / row['path']).stat().st_size == row['size'], 'payload drift: ' + row['path'])
    for name, digest in read(PACKAGE / 'fixtures.json').items():
        require(o.digest(Path(name)) == digest, 'fixture drift')
    dependencies = {}
    for name in LIBRARIES:
        payload = base / 'runtime/usr/lib' / name
        host = Path('/usr/lib') / name
        dependencies[name] = dict(payload=str(payload), payload_sha256=o.digest(payload),
                                  host=str(host.resolve()), host_sha256=o.digest(host),
                                  build_id=build_id(payload), host_build_id=build_id(host))
    return dict(built=str(BUILT), package=str(PACKAGE), final_sha256=o.digest(FINAL),
                seals=final['input_seals'], binaries=binaries, dependencies=dependencies,
                mapping=mapping, fixtures=read(PACKAGE / 'fixtures.json'),
                package_resolution=read(base / 'package-resolution.json'))


def prepare(output):
    require(os.geteuid() != 0, 'preparation must run as desktop user')
    o.fresh(output, BUILT, PACKAGE)
    result = dict(status='blocked', stage='provenance', launched_invocations=0, measured_observations=0,
                  unexecuted_invocations=10)
    inputs = None
    try:
        write(output / 'protocol.json', protocol())
        inputs = frozen_inputs()
        write(output / 'inputs.json', inputs)
        result['stage'] = 'symbols'
        cache = output / 'symbols'
        cache.mkdir()
        env = dict(os.environ, DEBUGINFOD_CACHE_PATH=str(cache / 'downloads'), DEBUGINFOD_TIMEOUT='45',
                   DEBUGINFOD_PROGRESS='0')
        require(bool(env.get('DEBUGINFOD_URLS', '').strip()), 'DEBUGINFOD_URLS unavailable')
        write(output / 'symbol-environment.json', {k: env[k] for k in
              ('DEBUGINFOD_CACHE_PATH', 'DEBUGINFOD_URLS', 'DEBUGINFOD_TIMEOUT')})
        symbols = {}
        for name, identity in inputs['dependencies'].items():
            argv = ['debuginfod-find', 'debuginfo', identity['build_id']]
            write(output / (name + '-download-command.json'), argv)
            with (output / (name + '-download.stdout')).open('x') as stdout, \
                    (output / (name + '-download.stderr')).open('x') as stderr:
                process = subprocess.run(argv, env=env, stdout=stdout, stderr=stderr, timeout=60)
            require(process.returncode == 0, 'required symbols unavailable: ' + name)
            downloaded = Path((output / (name + '-download.stdout')).read_text().strip())
            require(downloaded.is_file() and downloaded.resolve().is_relative_to(cache.resolve()), 'debug cache escape')
            validate_symbols(Path(identity['payload']), downloaded)
            target = cache / '.build-id' / identity['build_id'][:2] / (identity['build_id'][2:] + '.debug')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(downloaded, target)
            symbols[name] = dict(path=str(target), sha256=o.digest(target), build_id=build_id(target))
            write(output / 'symbols.json', symbols)
        require(frozen_inputs() == inputs, 'input drift during symbol preparation')
        result.update(status='prepared', stage='complete')
    except v.ERRORS as error:
        result['failure'] = str(error)
    finally:
        write(output / 'assessment.json', result)
        (output / 'ASSESSMENT.md').write_text('# C userspace profile preparation\n\nStatus: ' + result['status'] +
            '\n\n' + result.get('failure', '') + '\n\nNo previews, staging, rehearsal or measurements launched.\n')
        o.seal(output)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.output.absolute())
    print(result)
    sys.exit(result['status'] != 'prepared')
