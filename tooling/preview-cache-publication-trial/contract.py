"""Read-only trial contracts; no subprocess imports or workload launch capability."""
import importlib.util
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[1]
HISTORICAL = ROOT / 'tooling/preview-cache-publication'
sys.path.insert(0, str(HISTORICAL))
import evidence as e
sys.path.remove(str(HISTORICAL))
h = e.h
Q = ROOT / 'build/preview-corrected-qjln5jn4'
SERVICE = 'holonight-file-browser/src/preview/preview_service.cpp'
ARMS = ('control', 'early')
PREPARED = ROOT / 'build/preview-cache-publication-trial-20261118-01-prepared'
BUILT = ROOT / 'build/preview-cache-publication-trial-20261118-01-built'
CORRECTNESS = ROOT / 'build/preview-cache-publication-trial-20261118-01-correctness'
EXECUTION = ROOT / 'build/preview-cache-publication-trial-20261118-01-execution'
BEFORE = '''  if (decodedSource && tier && result.raster_outcome == HolonightImages::Outcome::Success &&
      unchangedSource(file, identity)) {
    ThumbnailService::storeRaster(file, path, identity, *tier, needed, result.image, *cancel, stage, nativePath);
  }'''
AFTER = '''  bool pixelsPublished = false;
  if (decodedSource && tier && result.raster_outcome == HolonightImages::Outcome::Success &&
      unchangedSource(file, identity)) {
    auto progressive = result;
    progressive.final = false;
    if (cancel->load()) {
      return result;
    }
    publish(progressive);
    pixelsPublished = true;
    ThumbnailService::storeRaster(file, path, identity, *tier, needed, result.image, *cancel, stage, nativePath);
  }'''
TAIL = '  publish(result);\n  result.final = true;\n  result.image = {};  // EXIF'
NEW_TAIL = '  if (!pixelsPublished) {\n    publish(result);\n  }\n  result.final = true;\n  result.image = {};  // EXIF'
# This snapshot runs strictly after all endpoint timing and service shutdown.
IDENTITY_BEFORE = '  rusage parent{}, children{};'
IDENTITY_AFTER = '''  QFile maps("/proc/self/maps");
  QFile executable("/proc/self/exe");
  QFile identity(QString::fromLocal8Bit(argv[5]) + ".loading.json");
  if (!maps.open(QIODevice::ReadOnly) || !executable.open(QIODevice::ReadOnly) ||
      !identity.open(QIODevice::WriteOnly | QIODevice::NewOnly)) {
    return 21;
  }
  const auto identityBytes = QJsonDocument(QJsonObject{
      {"maps", QString::fromUtf8(maps.readAll())},
      {"executable", QFileInfo(executable).symLinkTarget()},
      {"helper_mappings", "unavailable: helper exited before post-timing capture"}}).toJson();
  if (identity.write(identityBytes) != identityBytes.size() || !identity.flush()) {
    return 22;
  }
  rusage parent{}, children{};'''


def transform(text):
    h.require(text.count(BEFORE) == text.count(TAIL) == 1, 'publication anchor drift')
    return text.replace(BEFORE, AFTER).replace(TAIL, NEW_TAIL)


def harness(text):
    h.require(text.count(IDENTITY_BEFORE) == 1, 'post-timing identity anchor drift')
    return text.replace(IDENTITY_BEFORE, IDENTITY_AFTER)


def schedule():
    rows = [dict(arm=a, warmup=True, block=None, observation=0, count=1) for a in ARMS]
    for block in range(10):
        for arm in ARMS if block % 2 == 0 else ARMS[::-1]:
            rows.extend(dict(arm=arm, warmup=False, block=block, observation=i, count=1) for i in range(10))
    return [dict(index=i, **row) for i, row in enumerate(rows)]


def protocol():
    return dict(version=1, schedule=schedule(), processes=202, measured_per_arm=100,
        warmups_per_arm=1, scenario='startup', requested_size=[256, 256], jobs=4,
        build_type='Release', workload_seconds=30, shared_cleanup_seconds=5,
        retries=0, probes=False, tracing=False, profiling=False, cache_inspection=False,
        offscreen=True, private_source=True, private_cache=True, cache_flushing=False,
        affinity_changes=False, artificial_load=False,
        rule='Both p95 gains >= 5 ms; neither median regresses; unrounded whole populations.',
        qualification='78/80 unchanged')


def prerequisite():
    # Reuse the exact accepted independent records; do not rerun historical investigations.
    pins = [
        ('preview-cache-publication-execution-20261118-01',
         '8374318bc42744e59fbca4df4247785d5a40370ade9b96bd00e86b2de4974dcd',
         '23b27913354a03fd9e754d980f72069484cf2a1008d8f30154ed9555558975b2'),
        ('preview-cache-publication-correctness-20261118-04',
         '86ffc201c84924df0d06c2aa7a20a33bfa687bd079ba92befc65198b1c6f5727',
         'bcfdef06d56e1685cd247aa1ccaffd07cad7565dddb5f71dfa5d60c9d10f874a'),
        ('preview-cache-publication-native-20261117-01',
         'd2e45f0c05b464e1c22de87145f35160ac038ff482a0cc72ca04d6f1396b2d7a',
         '2f479d9b8cf6e14ab12a8fd6ad5bf2863daff921b3b9a57ad5d509d05d409ec9'),
        ('preview-cache-publication-20261117-01',
         '7f8f076c9020bb7f7d399f0eaefe69ce032a9db4d255e57aff907d15a7e4ce6c',
         '4ebf800404c87d0d8560a0e06386ea4de35f9064f593b64895848b4a827b8236')]
    accepted = []
    for name, seal, proof_hash in pins:
        root = ROOT / 'build' / name
        record = root.with_name(name + '-independent.json')
        h.require(h.digest(root / 'seal.json') == seal and h.digest(record) == proof_hash,
                  'accepted prerequisite identity changed')
        h.sealed(root)
        proof = h.read(record)
        h.require(proof['status'] == 'passed' and proof.get('evidence_seal', proof.get('preparation_seal')) == seal,
                  'accepted prerequisite proof binding')
        accepted.append(dict(path=str(root), seal=seal, independent_sha256=proof_hash))
    overlap, correctness, built, package = [Path(row['path']) for row in accepted]
    h.require(h.read(overlap / 'assessment.json')['decision'] == 'overlap observed' and
              h.read(correctness.with_name(correctness.name + '-independent.json'))['required_cases_passed'] == 130,
              'accepted overlap and correctness required')
    h.require(h.read(correctness / 'request.json')['built'] == str(built) and
              h.read(overlap / 'request.json') == dict(built=str(built), correctness=str(correctness)),
              'accepted artifact chain mismatch')
    inputs = h.read(package / 'inputs.json')
    h.require(h.inventory(Q / 'C/source') == inputs['source'] and
              h.inventory(Q / 'harness-source') == inputs['harness'], 'frozen C source provenance mismatch')
    fixture = package / '3200x2400.png'
    h.require(h.digest(fixture) == inputs['fixture']['sha256'], 'retained fixture mismatch')
    return dict(accepted=accepted, overlap=accepted[0],
        diagnostic=dict(fixture=dict(path=str(fixture), sha256=h.digest(fixture))),
        retained=dict(source=inputs['source'], harness=inputs['harness'],
                      fixture=dict(path=str(fixture), sha256=h.digest(fixture))))


def tool_paths():
    paths = set(DIRECTORY.rglob('*.py')) | set((DIRECTORY / 'native').glob('*')) | {DIRECTORY / 'PROTOCOL.md', DIRECTORY / 'CORRECTNESS.json'}
    paths |= {ROOT / 'tests/test_preview_cache_publication_trial.py'}
    paths |= set(HISTORICAL.glob('*.py')) | set((HISTORICAL / 'offline').glob('*.py'))
    paths |= set((ROOT / 'scripts').glob('*.py'))
    return sorted(paths)


def tools():
    return {str(p): h.digest(p) for p in tool_paths()}


def sample(value):
    h.require(value['scenario'] == 'startup' and len(value['samples']) == 1 and
              value['cleanup_failure'] is False, 'invalid benchmark envelope')
    row = value['samples'][0]
    h.require(all(row[k] is True for k in ('success', 'setup_success', 'correct_pixels', 'correct_metadata')) and
              all(row[k] is False for k in ('cleanup_failure', 'harness_timeout')) and not row['error'] and
              row['superseded_selections'] == 0, 'failed benchmark sample')
    first, final = row['first_ms'], row['final_ms']
    h.require(all(type(v) in (int, float) and math.isfinite(v) for v in (first, final)) and
              0 <= first <= final <= 30000, 'malformed endpoint timing')
    h.require(row['deliveries'] == [dict(selection=4, event=event, latency_ms=latency)
              for event, latency in [('pixels', first), ('metadata', final)]], 'endpoint deliveries mismatch')
    return row


def statistics_for(rows, complete):
    h.require([r['schedule'] for r in rows] == schedule()[:len(rows)], 'observation schedule mismatch')
    for row in rows:
        # Validate numeric data even for partial trials.
        for key in ('first_ms', 'final_ms'):
            v = row['sample'][key]
            h.require(type(v) in (int, float) and math.isfinite(v) and v >= 0, 'invalid sample')
        h.require(row['sample']['first_ms'] <= row['sample']['final_ms'] <= 30000, 'invalid sample ordering')
    measured = [r for r in rows if not r['schedule']['warmup']]
    def distribution(values):
        values = sorted(values)
        return dict(count=len(values), median=statistics.median(values),
                    p95=values[math.ceil(.95 * len(values)) - 1]) if values else None
    populations = {arm: {event: distribution([r['sample'][event] for r in measured
        if r['schedule']['arm'] == arm]) for event in ('first_ms', 'final_ms')} for arm in ARMS}
    blocks = []
    for block in range(10):
        for event in ('first_ms', 'final_ms'):
            cells = [[r['sample'][event] for r in measured if r['schedule']['arm'] == arm and
                      r['schedule']['block'] == block] for arm in ARMS]
            if all(len(c) == 10 for c in cells):
                cells = [distribution(c) for c in cells]
                blocks.append(dict(block=block, event=event,
                    **{k: cells[1][k] - cells[0][k] for k in ('median', 'p95')}))
    valid = complete and len(rows) == 202
    recommend = valid and all(populations['control'][ev]['p95'] - populations['early'][ev]['p95'] >= 5 and
        populations['early'][ev]['median'] <= populations['control'][ev]['median'] for ev in ('first_ms', 'final_ms'))
    return dict(populations=populations, blocks=blocks,
        decision=('Recommend' if recommend else 'Deferred') if valid else 'Evidence insufficient')


def snapshot_name(path):
    import hashlib
    return hashlib.sha256(str(path).encode()).hexdigest() + '-' + Path(path).name


def environment():
    import os
    import pwd
    uid = os.getuid()
    return dict(PATH='/usr/bin:/bin', HOME=pwd.getpwuid(uid).pw_dir, LANG='C.UTF-8',
        QT_QPA_PLATFORM='offscreen', CMAKE_BUILD_PARALLEL_LEVEL='4',
        XDG_RUNTIME_DIR='/run/user/' + str(uid),
        DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/' + str(uid) + '/bus')
