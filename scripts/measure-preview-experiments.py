#!/usr/bin/env python3
"""Run alternating fixed-baseline blocks; retain every sample, including failures."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import struct
import subprocess
import tempfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ('first', 'uncached', 'disk', 'memory', 'upgrade', 'burst', 'grid-decode')


def png(width, height, textured=False):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            rows.extend(((x * 17 + y * 31) & 255, (x * 73 ^ y * 19) & 255,
                         (x * y + x * 3 + y * 7) & 255) if textured else (255, 0, 0))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows, 6)) + chunk(b'IEND', b''))


def summary(records):
    result = {'samples': len(records),
              'failures': sum(not r['success'] for r in records),
              'invalid_success_observations': sum(r['success'] and (r['first_ms'] < 0 or r['final_ms'] < 0)
                                                  for r in records),
              'setup_failures': sum(not r['setup_success'] for r in records),
              'harness_timeouts': sum(r['harness_timeout'] for r in records),
              'superseded_selections': sum(r['superseded_selections'] for r in records)}
    result['reported_errors'] = {message: sum(r.get('error', '') == message for r in records)
                                 for message in sorted({r.get('error', '') for r in records}) if message}
    for key in ('first_ms', 'final_ms', 'wall_ms'):
        values = sorted(r[key] for r in records if r[key] >= 0)
        result[key] = {'observations': len(values), 'missing': len(records) - len(values),
                       'median': statistics.median(values) if values else None,
                       'p95': values[math.ceil(len(values) * .95) - 1] if values else None,
                       'maximum': max(values) if values else None}
    return result


def comparison(report):
    lines = ['# Fixed baseline comparison', '',
             'Each latency cell is median / p95 / maximum in milliseconds. Missing events and failures',
             'remain explicit in `summary.json`; these figures do not qualify any candidate experiment.', '',
             '| Scenario | A: original in-process | B: fixed current isolated | C: candidate | Change vs B | Change vs previous C |',
             '| --- | --- | --- | --- | --- | --- |']
    cases = sorted(name[2:] for name in report if name.startswith('A-'))
    for case in cases:
        cells = []
        for label in ('A', 'B'):
            result = report[label + '-' + case]
            times = []
            for key, title in (('first_ms', 'pixels'), ('final_ms', 'final')):
                values = result[key]
                times.append(title + ': ' + ' / '.join(
                    'missing' if values[stat] is None else f'{values[stat]:.2f}'
                    for stat in ('median', 'p95', 'maximum')))
            cells.append('; '.join(times) + f'; failures {result["failures"]}/{result["samples"]}'
                         + f'; setup failures {result["setup_failures"]}'
                         + f'; invalid observations {result["invalid_success_observations"]}')
        lines.append(f'| {case} | {cells[0]} | {cells[1]} | Not implemented | — | — |')
    lines += ['', 'No session, generation, or ready-worker optimization has been retained or rejected.',
              'The grid-decode case is a decoder check, not a scheduling-control measurement.',
              'See provenance.json and the harness README for remaining measurement limitations.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('--blocks', type=int, default=10)
    parser.add_argument('--per-block', type=int, default=10)
    parser.add_argument('--scenario', action='append', choices=SCENARIOS,
                        help='Restrict a fresh run to affected scenarios')
    parser.add_argument('--harness-directory', default='harness',
                        help='Use a separately built harness revision without overwriting old binaries')
    args = parser.parse_args()
    if args.blocks < 1 or args.per_block < 1:
        parser.error('positive block counts required')
    baseline = args.baseline.resolve()
    output = Path(tempfile.mkdtemp(prefix='measure-', dir=baseline))
    print(output, flush=True)
    for source, name in ((Path(__file__), 'runner.py'),
                         (ROOT / 'tooling/preview-benchmark/main.cpp', 'harness.cpp'),
                         (ROOT / 'tooling/preview-benchmark/CMakeLists.txt', 'CMakeLists.txt')):
        (output / name).write_bytes(source.read_bytes())
    fixtures = output / 'fixtures'
    fixtures.mkdir()
    for width, height, textured in ((160, 80, False), (1600, 1200, False), (3200, 2400, True)):
        (fixtures / f'{width}x{height}.png').write_bytes(png(width, height, textured))
    subprocess.run(['python3', str(baseline / 'B/source/holonight-images/tests/format-fixtures.py'),
                    str(fixtures / 'provider')], check=True)
    (fixtures / 'oriented.jpg').write_bytes((fixtures / 'provider/sample.jpg').read_bytes())
    inputs = sorted(fixtures.glob('*.png')) + [fixtures / 'oriented.jpg']
    provenance = {'fixtures': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                  'baseline_root': str(baseline), 'harness_directory': args.harness_directory,
                  'blocks': args.blocks, 'samples_per_block': args.per_block,
                  'scenarios': args.scenario or SCENARIOS,
                  'binaries': {label: hashlib.sha256((baseline / label / args.harness_directory / 'preview-benchmark').read_bytes())
                               .hexdigest() for label in ('A', 'B')},
                  'harness_source': hashlib.sha256((ROOT / 'tooling/preview-benchmark/main.cpp').read_bytes())
                                    .hexdigest(),
                  'qualifying_sample_count': args.blocks * args.per_block >= 100,
                  'limitations': ['grid-decode measures the decoder, not the grid scheduler',
                                  'getrusage child accounting is not aggregate cgroup memory',
                                  'superseded selections are issued requests, not verified cancellations',
                                  'worker readiness not applicable to A/B; candidate readiness unmeasured',
                                  'phase and cleanup attribution require separate diagnostic runs']}
    (output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    accumulated = {}
    for block in range(args.blocks):
        for label in (('A', 'B') if block % 2 == 0 else ('B', 'A')):
            for fixture in inputs:
                for scenario in args.scenario or SCENARIOS:
                    name = f'{label}-{fixture.name}-{scenario}'
                    target = output / f'{name}-{block:02}.json'
                    command = [str(baseline / label / args.harness_directory / 'preview-benchmark'),
                               str(baseline / label / 'prefix/libexec/holonight-images/runtime'),
                               str(fixture), scenario, str(args.per_block), str(target)]
                    with target.with_suffix('.log').open('x') as log:
                        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
                    if completed.returncode:
                        raise RuntimeError(f'benchmark exited {completed.returncode}: {target}')
                    data = json.loads(target.read_text())
                    accumulated.setdefault(name, []).extend(data['samples'])
            print(f'block {block + 1}/{args.blocks}: {label} complete', flush=True)
    report = {name: summary(records) for name, records in accumulated.items()}
    (output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    (output / 'comparison.md').write_text(comparison(report))
    print('Failures:', sum(r['failures'] for r in report.values()), flush=True)
    return int(any(r['failures'] or r['setup_failures'] or r['harness_timeouts']
                   or r['invalid_success_observations'] for r in report.values()))


if __name__ == '__main__':
    raise SystemExit(main())
