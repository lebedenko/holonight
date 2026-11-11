#!/usr/bin/env python3
"""Compare frozen A/B/C service timings; stop on every failed observation or cleanup."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ('first', 'disk', 'memory', 'burst')
LABELS = ('A', 'B', 'C')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_summary():
    spec = importlib.util.spec_from_file_location('baseline', ROOT / 'scripts/measure-preview-experiments.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.summary


def table(summary):
    lines = ['# Source transaction comparison', '',
             'Service delivery times in milliseconds; each latency cell is median / p95.',
             'These are not screen-presentation timings. Positive savings mean C is faster.', '',
             '| Fixture / scenario / event | A | B | C | ms saved vs B | % saved vs B | slowdown vs A |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    accepted = True
    for case in sorted({key[2:] for key in summary}):
        if any(label + '-' + case not in summary for label in LABELS):
            accepted = False
            continue
        for event in ('first_ms', 'final_ms'):
            rows = [summary[label + '-' + case] for label in LABELS]
            values = [row[event] for row in rows]
            if any(value['median'] is None for value in values):
                accepted = False
                continue
            a, b, c = (v['median'] for v in values)
            saved = b - c
            percent = saved / b * 100 if b else 0
            slowdown = (c / a - 1) * 100 if a else 0
            cells = [f'{v["median"]:.3f} / {v["p95"]:.3f}' for v in values]
            warm = case.endswith('-memory')
            percent_cell = '—' if warm else f'{percent:.1f}%'
            slowdown_cell = '—' if warm else f'{slowdown:+.1f}%'
            lines.append(f'| {case} / {event} | ' + ' | '.join(cells) +
                         f' | {saved:.3f} | {percent_cell} | {slowdown_cell} |')
            if case.endswith(('-first', '-disk')):
                accepted &= percent >= 30
            accepted &= values[2]['p95'] <= values[1]['p95']
            accepted &= all(row['samples'] == 100 and not any(row[k] for k in
                ('failures', 'setup_failures', 'harness_timeouts', 'invalid_success_observations')) for row in rows)
    lines += ['', 'Warm hits use absolute differences; percentages are omitted because these observations are sub-millisecond.',
              'Negative slowdown means faster than A. Strict acceptance still checks every p95, including warm hits.', '']
    return '\n'.join(lines), accepted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('fixtures', type=Path)
    parser.add_argument('--harness-directory', default='harness-qualified')
    args = parser.parse_args()
    package, fixtures = args.package.resolve(), args.fixtures.resolve()
    output = Path(tempfile.mkdtemp(prefix='measurement-', dir=package))
    print(output, flush=True)
    inputs = [fixtures / name for name in ('160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg')]
    (output / 'runner.py').write_bytes(Path(__file__).read_bytes())
    (output / 'harness.cpp').write_bytes((ROOT / 'tooling/preview-benchmark/main.cpp').read_bytes())
    (output / 'provenance.json').write_text(json.dumps({
        'fixtures': {str(p): digest(p) for p in inputs},
        'binaries': {label: digest(package / label / args.harness_directory / 'preview-benchmark') for label in LABELS},
        'scenarios': SCENARIOS, 'blocks': 10, 'per_block': 10,
        'harness_directory': args.harness_directory,
        'planned': 4800, 'warmups': 48, 'upgrade_checks': 36,
        'harness_sha256': digest(output / 'harness.cpp'),
        'limitations': ['service timings exclude screen presentation', 'host page cache is not flushed']
    }, indent=2) + '\n')
    summarize = load_summary()
    records = {}
    attempted = 0
    stop = None

    def run(label, fixture, scenario, count, name):
        nonlocal attempted, stop
        target = output / (name + '.json')
        command = [str(package / label / args.harness_directory / 'preview-benchmark'),
                   str(package / label / 'prefix/libexec/holonight-images/runtime'),
                   str(fixture), scenario, str(count), str(target)]
        with target.with_suffix('.log').open('x') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        data = json.loads(target.read_text()) if target.exists() else {}
        samples = data.get('samples', [])
        if name.startswith('qualifying-'):
            attempted += len(samples)
            records.setdefault(label + '-' + fixture.name + '-' + scenario, []).extend(
                r for r in samples if not r.get('incomplete'))
        failures = [r for r in samples if r.get('incomplete') or r.get('cleanup_failure') or
                    not r.get('success') or not r.get('setup_success') or r.get('harness_timeout') or
                    r.get('first_ms', -1) < 0 or r.get('final_ms', -1) < 0 or
                    not r.get('correct_pixels') or not r.get('correct_metadata')]
        if result.returncode or len(samples) != count or failures:
            stop = {'invocation': name, 'returncode': result.returncode, 'reported': len(samples),
                    'requested': count, 'failures': failures}
            return False
        return True

    try:
        # Separate warm-up observations never enter qualifying statistics.
        for label in LABELS:
            for fixture in inputs:
                for scenario in SCENARIOS:
                    if not run(label, fixture, scenario, 1, f'warmup-{label}-{fixture.name}-{scenario}'):
                        return 1
        for block in range(10):
            order = list(LABELS[block % 3:] + LABELS[:block % 3])
            if block % 2:
                order.reverse()
            for label in order:
                for fixture in inputs:
                    for scenario in SCENARIOS:
                        if not run(label, fixture, scenario, 10,
                                   f'qualifying-{block:02}-{label}-{fixture.name}-{scenario}'):
                            return 1
                print(f'block {block + 1}/10: {label} complete', flush=True)
        for label in LABELS:
            for fixture in inputs:
                if not run(label, fixture, 'upgrade', 3, f'upgrade-{label}-{fixture.name}'):
                    return 1
    except BaseException as error:
        stop = {'exception': type(error).__name__, 'message': str(error)}
        raise
    finally:
        summary = {key: summarize(value) for key, value in records.items()}
        markdown, accepted = table(summary)
        complete = stop is None and attempted == 4800
        report = {'planned': 4800, 'attempted': attempted,
                  'missing': 4800 - sum(len(r) for r in records.values()),
                  'stopped': stop, 'complete': complete,
                  'accepted': complete and accepted, 'summary': summary}
        (output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
        (output / 'comparison.md').write_text(markdown +
            f'\nComplete: {complete}. Performance acceptance: {complete and accepted}.\n')
        print('Complete:', complete, 'accepted:', complete and accepted, 'stopped:', stop, flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
