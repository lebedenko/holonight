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
MODES = ('default', 'adaptive')
IDS = tuple(f'{name}-{tier}' for name in ('textured', 'flat', 'alpha', 'oriented', 'two-color', 'gradient', 'panel') for tier in (128, 256, 512, 1024))
SOURCE = 'holonight-thumbnails/src/cache.cpp'
SOURCE_SHA = '7a352b8542df1fc7cc44f84a308035d8200fa660d2e11c7f5d93ffd7aa228852'
OUTPUT = ROOT / 'build/preview-cache-complexity-encoding-trial-20261119-02-investigation'
COMMAND_TIMEOUTS = (600, 600, 30, 30, 300, 300)


DETECTOR = r"""
static bool adaptiveNonuniform(const QImage& image, const std::atomic_bool& cancelled) {
  switch (image.format()) {
    case QImage::Format_RGB32:
    case QImage::Format_ARGB32:
    case QImage::Format_ARGB32_Premultiplied:
    case QImage::Format_RGBX8888:
    case QImage::Format_RGBA8888:
    case QImage::Format_RGBA8888_Premultiplied: break;
    default: return false;
  }
  if (image.width() < 2 || image.height() < 2) return false;
  const int nx = std::min(32, image.width()-1), ny = std::min(32, image.height()-1);
  int complex = 0;
  for (int j=0; j<ny; ++j) {
    if (cancelled.load()) return false;
    int y = 1 + ((2*j+1)*(image.height()-1))/(2*ny);
    const auto* row = reinterpret_cast<const quint32*>(image.constScanLine(y));
    const auto* upper = reinterpret_cast<const quint32*>(image.constScanLine(y-1));
    for (int i=0; i<nx; ++i) {
      int x = 1 + ((2*i+1)*(image.width()-1))/(2*nx);
      complex += row[x] != row[x-1] && row[x] != upper[x];
    }
  }
  return 4*complex >= nx*ny;
}
"""
ANCHOR = '  if (cancelled.load() || !tagged.save(&file, "PNG")) {'
WRITER = '''  const bool compress = request.kind == Kind::Raster && adaptiveNonuniform(image, cancelled);
  QImageWriter writer(&file, "PNG");
  if (compress) writer.setCompression(11);
  if (cancelled.load() || !(compress ? writer.write(tagged) : tagged.save(&file, "PNG"))) {'''


def transform(source, mode):
    h.require(mode in MODES, 'unsupported encoding')
    if mode == 'default': return source
    h.require(source.count(ANCHOR) == 1 and source.count('#include <QSaveFile>') == 1, 'source anchor drift')
    return source.replace('#include <QSaveFile>', '#include <QSaveFile>\n#include <QImageWriter>\n' + DETECTOR).replace(ANCHOR, WRITER)


def prerequisite():
    binding = historical.prerequisite()
    adaptive = ROOT/'build/preview-cache-adaptive-encoding-trial-20261119-01-investigation'
    proof_path = adaptive.with_name(adaptive.name+'-independent.json')
    h.require(h.digest(adaptive/'seal.json') == '77946b3adf2c93565d5ff8acc364c800d884ab88a1a71ff3a47ad2bf5cc79ce7', 'adaptive seal')
    h.sealed(adaptive)
    h.require(h.digest(proof_path) == '126513debeb20571d3fe58a9b5dd86153a25feea5cf5e452bd8553319a6144a5', 'adaptive proof')
    adaptive_proof = h.read(proof_path)
    h.require(adaptive_proof['status'] == 'passed' and adaptive_proof['decision'] == 'Deferred' and adaptive_proof['evidence_seal'] == h.digest(adaptive/'seal.json'), 'adaptive proof binding')
    encoding = ROOT / 'build/preview-cache-encoding-trial-20261118-02-investigation'
    proof = encoding.with_name(encoding.name + '-independent.json')
    h.require(h.digest(encoding/'seal.json') == '2c89ddd5215722f40beaa516d9573c114edaa9c591aabdcc1bf2f209cd4da28e', 'encoding seal changed')
    h.sealed(encoding)
    h.require(h.digest(proof) == 'db6eb58380fae376558c8762e0f6cc446eb4318f8bc29211a1d9ecd18c1ce31f', 'encoding proof changed')
    h.require(h.read(proof)['status'] == 'passed' and h.read(proof)['evidence_seal'] == h.digest(encoding/'seal.json') and h.read(proof)['decision'] == 'Deferred', 'encoding proof binding')
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
    return dict(adaptive=dict(path=str(adaptive),seal=h.digest(adaptive/'seal.json'),proof_sha256=h.digest(proof_path)), encoding=dict(path=str(encoding),seal=h.digest(encoding/'seal.json'),proof_sha256='db6eb58380fae376558c8762e0f6cc446eb4318f8bc29211a1d9ecd18c1ce31f'), retained=binding, early_trial=accepted, jpeg=dict(path=str(jpeg), sha256=h.digest(jpeg)))


def tools():
    # Include transitive historical helpers and fixture/test generators, not just entry points.
    paths = {p for p in DIRECTORY.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    for directory in ('scripts', 'tooling/preview-cache-publication', 'tooling/preview-cache-publication-trial'):
        paths.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.update((ROOT/'tests').glob('test_preview*.py'))
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
            expected.extend((identity, MODES[(block+offset)%2], False, block, i) for offset in range(2) for i in range(5))
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
    selected = 'adaptive' if eligible else None
    return dict(cells=cells, eligibility=reasons, selected=selected, decision='Deferred' if selected is None else 'Evidence insufficient')
