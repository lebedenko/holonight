"""Read-only trial contracts; no subprocess imports or workload launch capability."""
import importlib.util
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[2]
HISTORICAL = ROOT / 'tooling/preview-cache-publication'
sys.path.insert(0, str(HISTORICAL))
import evidence as e
sys.path.remove(str(HISTORICAL))
h = e.h
Q = ROOT / 'build/preview-corrected-qjln5jn4'
SERVICE = 'holonight-thumbnails/src/cache.cpp'
ARMS = ('control', 'candidate')
PREPARED = ROOT / 'build/preview-cache-complexity-encoding-trial-20261119-02-prepared'
BUILT = ROOT / 'build/preview-cache-complexity-encoding-trial-20261119-02-built'
CORRECTNESS = ROOT / 'build/preview-cache-complexity-encoding-trial-20261119-04-correctness'
EXECUTION = ROOT / 'build/preview-cache-complexity-encoding-trial-20261119-04-execution'
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


directional = e.load('directional_qualified_contract', DIRECTORY.parent/'contract.py')


def transform(text):
    return directional.transform(text, 'adaptive')


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


INVESTIGATION_SEAL = '3b320920e297cbb184f7b4acde04c83f45e0f63f92ae8c82dfc87d76563f0373'
INVESTIGATION_PROOF = '7a13e7afdf091f47c392d4954c02149aee29ea4ef5325e6165e36f5b983a2ac1'


def prerequisite():
    root = directional.OUTPUT
    record = root.with_name(root.name+'-independent.json')
    h.require(h.digest(root/'seal.json') == INVESTIGATION_SEAL and h.digest(record) == INVESTIGATION_PROOF, 'qualified investigation identity')
    # The independent investigation module uses its own contract, isolated from this phase.
    previous = sys.modules.get('contract')
    sys.modules['contract'] = directional
    try:
        verifier = e.load('directional_investigation_verifier', DIRECTORY.parent/'offline/verify.py')
        proof = verifier.verify(root)
    finally:
        if previous is None: sys.modules.pop('contract', None)
        else: sys.modules['contract'] = previous
    h.require(h.read(record) == proof and proof['status'] == 'passed' and proof['selected'] == 'adaptive' and
              proof['stores'] == 1736 and proof['measured_stores'] == 1680 and proof['cleanup'], 'independently verified eligibility required')
    binding = directional.prerequisite()
    return dict(investigation=dict(path=str(root),seal=INVESTIGATION_SEAL,proof_sha256=INVESTIGATION_PROOF),
                provenance=binding, retained=binding['retained']['retained'], diagnostic=binding['retained']['diagnostic'])


def phase_proof(path, outcome):
    verifier_name = 'verify_correctness.py' if outcome == 'qualified' else 'verify.py'
    verifier = e.load('directional_phase_proof', DIRECTORY/'offline'/verifier_name)
    proof = verifier.verify(path)
    record = path.with_name(path.name+'-independent.json')
    h.require(proof['status'] == 'passed' and proof['outcome'] == outcome and h.read(record) == proof,
              'missing, failed or unverified prerequisite phase')
    return proof


def tool_paths():
    paths = set(DIRECTORY.rglob('*.py')) | set((DIRECTORY / 'native').glob('*')) | {DIRECTORY / 'PROTOCOL.md', DIRECTORY / 'CORRECTNESS.json'}
    paths |= {ROOT / 'tests/test_preview_cache_publication_trial.py'}
    paths |= set(HISTORICAL.glob('*.py')) | set((HISTORICAL / 'offline').glob('*.py'))
    paths |= set((ROOT / 'scripts').glob('*.py'))
    paths |= set(Path(name) for name in directional.tools())
    paths |= {ROOT/'tests/test_preview_cache_directional_qualification.py'}
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
    recommend = valid and all(populations['control'][ev]['p95'] - populations['candidate'][ev]['p95'] >= 5 and
        populations['candidate'][ev]['median'] <= populations['control'][ev]['median'] for ev in ('first_ms', 'final_ms'))
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
