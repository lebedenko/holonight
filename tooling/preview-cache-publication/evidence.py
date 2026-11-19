"""Read-only bindings shared with the independent execution verifier."""
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'build/preview-cache-publication-20261117-01'
SEAL = '7f8f076c9020bb7f7d399f0eaefe69ce032a9db4d255e57aff907d15a7e4ce6c'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


historical = load('publication_historical_verifier', ROOT / 'scripts/verify-preview-cache-publication.py')
h = historical.h


def package():
    h.require(h.digest(PACKAGE / 'seal.json') == SEAL, 'approved package seal mismatch')
    result = historical.verify(PACKAGE)
    record = PACKAGE.with_name(PACKAGE.name + '-independent.json')
    h.require(h.read(record) == result and result['status'] == 'passed' and
              result['outcome'] == 'prepared', 'independent preparation record mismatch')
    return dict(path=str(PACKAGE), seal=SEAL, independent_sha256=h.digest(record))


def tools():
    paths = list(Path(__file__).parent.glob('*.py')) + [Path(__file__).parent / 'PROTOCOL.md',
        ROOT / 'tests/test_preview_cache_publication_execution.py']
    return {str(p): h.digest(p) for p in sorted(paths)}


def parse_events(stderr):
    events = []
    for line in stderr.splitlines():
        if 'CACHE_PUBLICATION' not in line:
            continue
        h.require(line.startswith('CACHE_PUBLICATION '), 'malformed event prefix')
        def pairs(items):
            value = {}
            for key, item in items:
                h.require(key not in value, 'duplicate event field')
                value[key] = item
            return value
        row = h.json.loads(line[len('CACHE_PUBLICATION '):], object_pairs_hook=pairs)
        timestamp = row.get('ns')
        h.require(isinstance(timestamp, str) and timestamp.isascii() and timestamp.isdecimal(),
                  'timestamp must be decimal monotonic nanoseconds')
        row['ns'] = int(timestamp)
        events.append(row)
    historical.observation(events)
    return events
