"""Version 4 correctness contracts. This module never starts processes."""
from pathlib import Path
import re
import stat
import xml.etree.ElementTree as ET
import contract as t
e = t.e

h = e.h
DIRECTORY = Path(__file__).resolve().parent


def protocol():
    return h.read(DIRECTORY / 'CORRECTNESS.json')


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
        frozen = t.PREPARED / arm / 'source'
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


def prepared_binding():
    return dict(path=str(t.PREPARED), seal=h.digest(t.PREPARED / 'seal.json'))


def built_binding(built):
    verifier = e.load('trial_build_verifier', DIRECTORY / 'offline/verify.py')
    record = verifier.verify(built)
    h.require(record['status'] == 'passed' and record['outcome'] == 'built', 'verified build required')
    return dict(path=str(built), seal=h.digest(built / 'seal.json'), inventory=h.sealed(built))


def tree(root):
    result = {}
    for path in [root, *sorted(root.rglob('*'))]:
        info = path.lstat()
        h.require(not path.is_symlink() and (path.is_file() or path.is_dir()), 'unsafe staging member')
        result[str(path.relative_to(root))] = dict(uid=info.st_uid, gid=info.st_gid,
            mode=stat.S_IMODE(info.st_mode), sha256=h.digest(path) if path.is_file() else None)
    return result


def tools():
    # Qualifier retains a collision-free hierarchical snapshot, via unique hashed names.
    return t.tools()


def generator():
    paths = [t.PREPARED / arm / 'source/holonight-images/tests/format-fixtures.py' for arm in protocol()['arms']]
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
