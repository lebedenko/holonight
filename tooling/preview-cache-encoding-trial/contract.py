"""Read-only contracts for the PNG encoding investigation."""
import hashlib
import importlib.util
import math
from pathlib import Path
import statistics

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[1]
spec = importlib.util.spec_from_file_location('encoding_historical_contract', ROOT / 'tooling/preview-cache-publication-trial/contract.py')
historical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(historical)
h = historical.h
MODES = ('default', '11', '0')
IDS = tuple(f'{name}-{tier}' for name in ('textured', 'flat', 'alpha', 'oriented') for tier in (128, 256, 512, 1024))
SOURCE = 'holonight-thumbnails/src/cache.cpp'
SOURCE_SHA = '7a352b8542df1fc7cc44f84a308035d8200fa660d2e11c7f5d93ffd7aa228852'
STOPPED_OUTPUT = ROOT / 'build/preview-cache-encoding-trial-20261118-01-investigation'
OUTPUT = ROOT / 'build/preview-cache-encoding-trial-20261118-02-investigation'
COMMAND_TIMEOUTS = (600, 600, 30, 30, 300)


def transform(source, mode):
    h.require(mode in MODES, 'unsupported encoding')
    if mode == 'default':
        return source
    anchor = '  if (cancelled.load() || !tagged.save(&file, "PNG")) {'
    h.require(source.count(anchor) == 1 and source.count('#include <QSaveFile>') == 1, 'source anchor drift')
    return source.replace('#include <QSaveFile>', '#include <QSaveFile>\n#include <QImageWriter>').replace(anchor,
        '  QImageWriter writer(&file, "PNG");\n  writer.setCompression(' + mode + ');\n'
        '  if (cancelled.load() || !writer.write(tagged)) {')


def prerequisite():
    binding = historical.prerequisite()
    phases = [
        ('prepared','bb60fbfc7b5705410b447bd3419e82447d6e5e8618a09a10f47c1ff5cad00a2f'),
        ('built','59201a5ca7d50df6be49d69a8fc60cd8511911264795f71dfff9e3bfe73abced'),
        ('correctness','4bc7b4fdc018fe44c0c9ba0f53e1297a9633297d0a0982686079678587b2f5cf'),
        ('execution','f104bccb4ad1eab312d749943d237a55a49cf15f8512d5dfa0099c84bd4a5ed7')]
    proof_pins = ('8799b138a5fb7f4c47009585abb6640c32395bda8fd53ecaffe2b9f245844d65',
        'b1649cd3ff5cfc322af68c845595e0bd6281b397c8ae7a833da22ae502a0b25a',
        '8045eb11c085695c7256379f0612cbe4044f6408a1f9eef3115b93e855cd3497',
        'c3493ac211bf669199c03827063ba05e86db92978f3c8d0d43e480d183483ac3')
    accepted = []
    for phase, seal in phases:
        path = ROOT / ('build/preview-cache-publication-trial-20261118-01-' + phase)
        record = path.with_name(path.name + '-independent.json')
        h.require(h.digest(path / 'seal.json') == seal, 'early trial identity')
        h.sealed(path)
        h.require(h.digest(record) == proof_pins[len(accepted)], 'pinned independent record changed')
        proof = h.read(record)
        h.require(proof['status'] == 'passed' and proof['evidence_seal'] == seal, 'early trial independent binding')
        accepted.append(dict(path=str(path), seal=seal, proof_sha256=h.digest(record)))
    h.require(h.read(Path(accepted[-1]['path']) / 'assessment.json')['decision'] == 'Deferred', 'early trial decision')
    jpeg = historical.Q / 'A/build/holonight-images/tests/fixtures/sample.jpg'
    h.require(h.digest(jpeg) == 'febf46eb17d81b0105ed1e7237cf5a744407929bb333b25a9ee1e29ce877a1f4', 'retained JPEG identity')
    return dict(retained=binding, early_trial=accepted, jpeg=dict(path=str(jpeg), sha256=h.digest(jpeg)))


def tools():
    paths = [p for p in DIRECTORY.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT / 'tests/test_preview_cache_encoding_trial.py']
    paths += [ROOT / 'scripts/run-preview-cpu-profile.py']
    return {str(p): h.digest(p) for p in sorted(paths)}


def distribution(values):
    h.require(values and all(type(v) is int and v > 0 for v in values), 'invalid store timings')
    ordered = sorted(values)
    return dict(median=statistics.median(ordered), p95=ordered[math.ceil(.95 * len(ordered))-1])


def assess(raw):
    h.require(raw['qt'] == '6.12.0' and [r['id'] for r in raw['corpus']] == list(IDS), 'corpus identity')
    expected = []
    for identity in IDS:
        expected.extend((identity, m, True, -1, 0) for m in MODES)
        for block in range(6):
            expected.extend((identity, MODES[(block+offset)%3], False, block, i) for offset in range(3) for i in range(5))
    rows = raw['rows']
    h.require([(r['id'], r['mode'], r['warmup'], r['block'], r['observation']) for r in rows] == expected, 'store schedule mismatch')
    cells = {}
    for image in raw['corpus']:
        identity = image['id']
        cells[identity] = {}
        metadata = None
        for mode in MODES:
            samples = [r for r in rows if r['id'] == identity and r['mode'] == mode]
            for r in samples:
                h.require(type(r['bytes']) is int and r['bytes'] > 0 and type(r['warmup']) is bool, 'invalid store evidence')
                h.require(all(r[k] == image[k] for k in ('pixels','alpha','icc')), 'lossless/color preservation')
                h.require(r['metadata'] == samples[0]['metadata'] and r['bytes'] == samples[0]['bytes'] and r['sha256'] == samples[0]['sha256'], 'nonidentical encoding repetitions')
            texts = samples[0]['metadata']
            h.require(texts['Thumb::MTime'] == '1700000000' and texts['Thumb::Size'] == '1234567' and
                texts['X-HoloNight::MTimeMsec'] == '1700000000123' and texts['Files::Revision'] == 'encoding-trial-v1' and
                texts['X-HoloNight::OrientationPolicy'] == texts['Files::OrientationPolicy'] == 'applied-v1' and
                texts['Thumb::URI'].endswith('/source-' + identity.rsplit('-',1)[0]), 'cache metadata')
            metadata = texts if metadata is None else metadata
            h.require(metadata == texts, 'metadata differs between modes')
            cells[identity][mode] = dict(bytes=samples[0]['bytes'], **distribution([r['ns'] for r in samples if not r['warmup']]))
    eligible = []
    reasons = {}
    for mode in MODES[1:]:
        failures = [identity for identity in IDS if 4*cells[identity][mode]['bytes'] > 5*cells[identity]['default']['bytes']]
        primary = cells['textured-256']
        faster = all(primary[mode][k] < primary['default'][k] for k in ('median','p95'))
        reasons[mode] = dict(size_failures=failures, primary_faster=faster)
        if not failures and faster:
            eligible.append(mode)
    selected = min(eligible, key=lambda m: (cells['textured-256'][m]['p95'], cells['textured-256'][m]['median'], sum(cells[i][m]['bytes'] for i in IDS), 0 if m == '11' else 1)) if eligible else None
    return dict(cells=cells, eligibility=reasons, selected=selected, decision='Deferred' if selected is None else 'Evidence insufficient')
