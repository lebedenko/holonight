#!/usr/bin/env python3
"""Run corrected Experiment 0 passes sequentially; a cleanup failure gates all later passes."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('scheduler', 'diagnostic', 'fixtures', 'probe'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    args.scheduler, args.diagnostic, args.fixtures, args.probe = (
        p.resolve() for p in (args.scheduler, args.diagnostic, args.fixtures, args.probe))
    scheduler = json.loads((args.scheduler / 'provenance.json').read_text())
    diagnostic = json.loads((args.diagnostic / 'provenance.json').read_text())
    b2, d2 = scheduler['variants']['B2'], diagnostic['variants']['D2']
    if (not b2.get('correction_verified') or not d2.get('correction_verified') or
            not b2['corrected_cleanup'] or not d2['corrected_cleanup'] or b2['diagnostic'] or
            not d2['diagnostic'] or b2['source_delta'] != d2['source_delta'] or
            scheduler['revisions']['B2'] != diagnostic['revisions']['D2']):
        raise ValueError('B2/D2 correction provenance mismatch')
    spec = importlib.util.spec_from_file_location('runner', ROOT / 'scripts/run-preview-evidence.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    workloads = {}
    for label in ('A', 'B2'):
        binary = args.scheduler / label / 'harness/preview-grid-control'
        workloads[label] = json.loads(subprocess.check_output([str(binary), '--describe-workload'], text=True))
        if not runner.validate_workload(workloads[label]):
            raise ValueError('scheduler preflight failed before lifecycle measurement')
    output = Path(tempfile.mkdtemp(prefix='preview-iteration-', dir=ROOT / 'build'))
    print(output, flush=True)
    (output / 'runner.py').write_bytes(Path(__file__).read_bytes())
    spec = importlib.util.spec_from_file_location('baselines', ROOT / 'scripts/preview-experiment-baselines.py')
    baselines = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baselines)
    fixtures = [args.fixtures / n for n in ('160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg')]
    report = {'workloads': workloads, 'variants': ['A', 'B2', 'D2'], 'packages': [str(args.scheduler), str(args.diagnostic)],
              'probe_sha256': baselines.digest(args.probe),
              'fixtures': {str(p): baselines.digest(p) for p in fixtures},
              'planned': {'lifecycle_cycles': 1000, 'diagnostic': 280, 'resource': 84, 'scheduler': 600},
              'passes': [], 'stopped': None}
    def save():
        (output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    commands = [('lifecycle', [str(args.probe), str(args.scheduler / 'B2/prefix/libexec/holonight-images/runtime'),
                              str(output / 'lifecycle.jsonl'), *map(str, fixtures)])]
    for kind, package in (('diagnostic', args.diagnostic), ('resource', args.diagnostic), ('scheduler', args.scheduler)):
        commands.append((kind, ['python3', str(ROOT / 'scripts/run-preview-evidence.py'), str(package),
                                str(args.fixtures), '--kind', kind]))
    for kind, command in commands:
        entry = {'kind': kind, 'command': command}
        report['passes'].append(entry)
        save()
        with (output / (kind + '.log')).open('x') as log:
            code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
        entry['exit'] = code
        if kind == 'lifecycle':
            rows = [json.loads(line) for line in (output / 'lifecycle.jsonl').read_text().splitlines()]
            operations = [r for r in rows if r['kind'] != 'summary']
            complete = sum(r['operation'] == 'cached-png-decode' for r in operations)
            entry['denominators'] = {'planned': 1000, 'attempted': len({r['cycle'] for r in operations}),
                                     'completed': complete, 'missing': 1000 - complete,
                                     'failed': len({r['cycle'] for r in operations if r['runtime'] != 0 or r['outcome'] != 0}),
                                     'excluded': 0, 'failed_operations': sum(r['runtime'] != 0 or r['outcome'] != 0 for r in operations)}
        save()
        print(kind, code, flush=True)
        if code:
            report['stopped'] = kind + ' failed; no retry or later native measurement'
            report['gated_passes'] = [name for name, _ in commands[len(report['passes']):]]
            save()
            return code
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
