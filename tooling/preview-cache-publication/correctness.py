"""Version 3 correctness contracts. This module never starts processes."""
import os
from pathlib import Path
import re
import stat
import xml.etree.ElementTree as ET
import evidence as e

h = e.h
DIRECTORY = Path(__file__).resolve().parent
BUILT_SEAL = 'd2e45f0c05b464e1c22de87145f35160ac038ff482a0cc72ca04d6f1396b2d7a'


def protocol():
    return h.read(DIRECTORY / 'CORRECTNESS-v3.json')


def validate_xml(path, required):
    try:
        xml = ET.parse(path).getroot()
    except ET.ParseError as error:
        raise ValueError('malformed correctness XML') from error
    cases = xml.findall('.//testcase')
    names = [c.attrib['classname'] + '.' + c.attrib['name'] for c in cases]
    h.require(len(names) == len(set(names)) and set(names) == set(required) and
              len(names) == len(required) == int(xml.attrib['tests']), 'required test membership mismatch')
    h.require(all(not any('DISABLED_' in part for part in name.split('.')) for name in names),
              'disabled required case')
    h.require(all(int(xml.attrib.get(k, '0')) == 0 for k in ('failures', 'errors', 'disabled')) and
              not xml.findall('.//skipped') and not xml.findall('.//failure') and
              all(c.attrib.get('status') == 'run' and c.attrib.get('result') == 'completed' for c in cases),
              'required correctness case failed, disabled or skipped')
    return names


def source_cases(path, suites):
    return [suite + '.' + name for suite, name in re.findall(
        r'TEST(?:_F)?\(\s*(\w+)\s*,\s*(\w+)\s*\)', path.read_text()) if suite in suites]


def validate_membership(native):
    p = protocol()
    suites = [('runtime-verification', ('RuntimeVerification',)), ('generation-ownership', ('GenerationOwner',)),
              ('cleanup', ('Cleanup',)), ('scheduling', ('PreviewScheduling',)),
              ('pool-lifecycle', ('PoolLifecycle',)), ('preview', ('IsolatedPreview', 'WarmPreview'))]
    h.require(p['prerequisites'] == [dict(label=label, cases=[n for n in p['ordinary']
              if n.split('.')[0] in members]) for label, members in suites], 'prerequisite order changed')
    for arm in p['arms']:
        frozen = e.PACKAGE / arm / 'source'
        ordinary = []
        for relative, suites in (
            ('holonight-images/tests/isolated_verification_test.cpp', ['RuntimeVerification']),
            ('holonight-images/tests/isolated_generation_test.cpp', ['GenerationOwner']),
            ('holonight-images/tests/isolated_cleanup_test.cpp', ['Cleanup']),
            ('holonight-file-browser/tests/session_pool_test.cpp', ['PreviewScheduling', 'PoolLifecycle']),
            ('holonight-file-browser/tests/isolated_preview_test.cpp', ['IsolatedPreview'])):
            ordinary += source_cases(frozen / relative, suites)
        selected = ['WarmPreview.' + name for name in (
            'RevisitPreservesOrientedDimensionsMetadataAndProgressivePixelsWithoutRuntime',
            'DiskHitKeepsSourceExifOrientationAndNotificationOrder',
            'ChangedRemovedAndUnreadableSourcesCannotReusePixels',
            'MutationAtMemoryCheckpointInvalidatesMemoryAndDiskCandidate')]
        h.require(set(selected) <= set(source_cases(frozen / 'holonight-file-browser/tests/isolated_preview_test.cpp',
                  ['WarmPreview'])), 'missing frozen Preview case')
        h.require(p['ordinary'] == ordinary + selected, 'prerequisite membership changed')
        h.require(p['protected_fixture'] == source_cases(frozen / 'holonight-images/tests/isolated_generation_test.cpp',
                  ['ProtectedGeneration']), 'protected fixture membership changed')
        h.require(p['session'] == source_cases(frozen / 'holonight-images/tests/isolated_session_test.cpp',
                  ['NativeSession']), 'session membership changed')
    h.require(p['publication'] == source_cases(native / 'main.cpp', ['Publication']), 'publication membership changed')
    for key in ('ordinary', 'protected_fixture', 'publication', 'session', 'protected_preview'):
        names = p[key]
        h.require(names and len(names) == len(set(names)) and
                  all(not any(c in name for c in '*?:') and 'DISABLED_' not in name for name in names),
                  'non-explicit required cases')


def built_binding(built):
    h.require(built == built.resolve() and h.digest(built / 'seal.json') == BUILT_SEAL, 'pinned build seal mismatch')
    verifier = e.load('correctness_build_verifier', DIRECTORY / 'offline/verify.py')
    record = verifier.verify(built)
    h.require(record['commands'] == 27 and record['failed_command'] is None, 'incomplete native compilation')
    inventory = h.sealed(built)
    for arm in ('control', 'early'):
        runtime = built / arm / 'runtime'
        manifest = h.read(runtime / 'manifest.json')
        for row in manifest['files']:
            path = runtime / row['path']
            h.require(path.resolve().is_relative_to(runtime) and path.is_file() and
                      h.digest(path) == row['sha256'] and path.stat().st_size == row['size'] and
                      stat.S_IMODE(path.stat().st_mode) == row['mode'], 'runtime manifest payload mismatch')
        helper = runtime / 'usr/libexec/holonight-images-helper'
        h.require(h.digest(helper) == h.digest(built / arm / 'build/holonight-images/holonight-images-helper'),
                  'runtime helper mismatch')
    return dict(path=str(built), seal=BUILT_SEAL, inventory=inventory)


def tree(root):
    result = {}
    for path in [root, *sorted(root.rglob('*'))]:
        info = path.lstat()
        h.require(not path.is_symlink() and (path.is_file() or path.is_dir()), 'unsafe staging member')
        result[str(path.relative_to(root))] = dict(uid=info.st_uid, gid=info.st_gid,
            mode=stat.S_IMODE(info.st_mode), sha256=h.digest(path) if path.is_file() else None)
    return result


def tools():
    paths = [*DIRECTORY.glob('*.py'), *DIRECTORY.glob('CORRECTNESS*'),
             DIRECTORY / 'offline/verify_correctness_v2.py',
             e.ROOT / 'tests/test_preview_cache_publication_correctness.py',
             e.ROOT / 'scripts/manage-images-generations.py', e.ROOT / 'scripts/install_state.py',
             e.ROOT / 'scripts/run-preview-cpu-profile.py', e.ROOT / 'scripts/run-preview-startup-smoke.py']
    # Retain the local dependencies of the historical verifier and cleanup primitive too.
    paths += list((e.ROOT / 'scripts').glob('*.py'))
    paths += list((DIRECTORY / 'offline').glob('*.py'))
    return {str(p): h.digest(p) for p in sorted(set(paths))}


def generator():
    paths = [e.PACKAGE / arm / 'source/holonight-images/tests/format-fixtures.py' for arm in protocol()['arms']]
    h.require(paths[0].read_bytes() == paths[1].read_bytes(), 'fixture generator arm mismatch')
    h.require(h.digest(paths[0]) == protocol()['fixture_generator_sha256'], 'fixture generator protocol mismatch')
    return paths[0]


def fixtures(root):
    h.require(root.is_dir() and not root.is_symlink(), 'missing or unsafe fixtures')
    for path in root.rglob('*'):
        h.require(not path.is_symlink() and path.is_file(), 'unsafe fixture member')
    inventory = h.inventory(root)
    h.require(all('sample.' + ext in inventory for ext in ('png', 'jpg', 'bmp', 'tif', 'webp', 'gif')),
              'missing required fixture')
    h.require(inventory == protocol()['fixtures'], 'fixture content mismatch')
    return inventory
