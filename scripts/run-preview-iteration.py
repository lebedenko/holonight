#!/usr/bin/env python3
"""Run corrected Experiment 0 passes sequentially; any failure gates all later passes."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def lifecycle_report(path, planned=1000):
    """Keep valid partial records and reject missing, malformed or failed output."""
    operations, summaries, errors = [], [], []
    try:
        lines = path.read_text().splitlines()
    except OSError as error:
        lines = []
        errors.append(str(error))
    for number, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError('record is not an object')
            if row.get('kind') == 'summary':
                if any(type(row.get(k)) is not int for k in ('cycles', 'operations', 'elapsed_ms')):
                    raise ValueError('invalid summary')
                summaries.append(row)
            else:
                if (any(type(row.get(k)) is not int for k in ('cycle', 'runtime', 'outcome')) or
                        row.get('operation') not in ('inspect', 'source-decode', 'cached-png-decode') or
                        not 0 <= row['cycle'] < planned):
                    raise ValueError('invalid operation')
                operations.append(row)
        except (ValueError, TypeError) as error:
            errors.append(f'line {number}: {error}')
    attempted = {r['cycle'] for r in operations}
    failed = {r['cycle'] for r in operations if r['runtime'] != 0 or r['outcome'] != 0}
    completed = 0
    for cycle in attempted:
        names = [r['operation'] for r in operations if r['cycle'] == cycle]
        if sorted(names) == sorted(('inspect', 'source-decode', 'cached-png-decode')) and cycle not in failed:
            completed += 1
    summary = summaries[0] if len(summaries) == 1 else None
    if summary is None or summary['operations'] != len(operations) or summary['cycles'] != completed:
        errors.append('missing or inconsistent lifecycle summary')
    capped = bool(summary and summary['elapsed_ms'] >= 600000 and completed < planned)
    if completed < planned and not capped:
        errors.append('incomplete lifecycle without cap evidence')
    return {'denominators': {'planned': planned, 'attempted': len(attempted),
            'completed': completed, 'failed': len(failed), 'excluded': 0,
            'unattempted': planned - len(attempted), 'missing': planned - completed,
            'missing_timed_observations': planned * 3 - len(operations),
            'failed_operations': sum(r['runtime'] != 0 or r['outcome'] != 0 for r in operations)},
            'cap_shortfall': planned - completed if capped else 0,
            'parse_errors': errors, 'failed': bool(failed or errors)}


def audit_package(package, baselines):
    records = {}
    provenance = json.loads((package / 'provenance.json').read_text())
    for label in provenance['variants']:
        base = package / label
        expected = json.loads((base / 'inventory.json').read_text())
        actual = baselines.inventory(base)
        mismatches = [name for name, value in expected.items() if actual.get(name) != value]
        extras = set(actual) - set(expected) - {'inventory.json'}
        unexpected = extras - {'harness/Testing/Temporary/CTestCostData.txt',
                               'harness/Testing/Temporary/LastTest.log'}
        if mismatches or unexpected:
            raise ValueError(f'{label} inventory mismatch: ' + json.dumps(
                {name: {'expected': expected[name], 'actual': actual.get(name)} for name in mismatches})
                + f', extra: {sorted(unexpected)}')
        for manifest in (base / 'prefix').rglob('manifest.json'):
            for row in json.loads(manifest.read_text())['files']:
                if baselines.digest(manifest.parent / row['path']) != row['sha256']:
                    raise ValueError(f'runtime manifest mismatch: {row["path"]}')
        records[label] = {'inventory_sha256': baselines.digest(base / 'inventory.json'),
                          'files_verified': len(expected), 'acceptance_logs': sorted(extras)}
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('scheduler', 'diagnostic', 'fixtures', 'probe'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    args.scheduler, args.diagnostic, args.fixtures, args.probe = (
        p.resolve() for p in (args.scheduler, args.diagnostic, args.fixtures, args.probe))
    output = Path(tempfile.mkdtemp(prefix='preview-iteration-', dir=ROOT / 'build'))
    print(output, flush=True)
    (output / 'runner.py').write_bytes(Path(__file__).read_bytes())
    planned = {'lifecycle_cycles': 1000, 'diagnostic': 280, 'resource': 84, 'scheduler': 600}
    report = {'passes': [], 'stopped': None, 'planned': planned,
              'unattempted': dict(planned),
              'denominators': {name: {'planned': count, 'attempted': 0, 'completed': 0,
                  'failed': 0, 'excluded': 0, 'unattempted': count,
                  'missing_timed_observations': 3000 if name == 'lifecycle_cycles' else count}
                  for name, count in planned.items()}}
    audit = {}
    def save():
        (output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    try:
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
        spec = importlib.util.spec_from_file_location('baselines', ROOT / 'scripts/preview-experiment-baselines.py')
        baselines = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baselines)
        audit['probe_sha256'] = baselines.digest(args.probe)
        for package in (args.scheduler, args.diagnostic):
            audit[str(package)] = audit_package(package, baselines)
        frozen = json.loads((args.fixtures.parent / 'provenance.json').read_text())
        expected_fixtures = frozen['fixtures']
        if set(expected_fixtures) != {'160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg'}:
            raise ValueError('frozen fixture inventory must identify all four inputs')
        for name, expected in expected_fixtures.items():
            path = args.fixtures / Path(name).name
            if baselines.digest(path) != expected:
                raise ValueError(f'fixture mismatch: {path}')
        (output / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n')
        workloads = {}
        for label in ('A', 'B2'):
            binary = args.scheduler / label / 'harness/preview-grid-control'
            workloads[label] = json.loads(subprocess.check_output([str(binary), '--describe-workload'], text=True))
            if not runner.validate_workload(workloads[label]):
                raise ValueError('scheduler preflight failed before lifecycle measurement')
        fixtures = [args.fixtures / n for n in ('160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg')]
        report = {'workloads': workloads, 'variants': ['A', 'B2', 'D2'], 'packages': [str(args.scheduler), str(args.diagnostic)],
                  'probe_sha256': baselines.digest(args.probe),
                  'fixtures': {str(p): baselines.digest(p) for p in fixtures},
                  'planned': {'lifecycle_cycles': 1000, 'diagnostic': 280, 'resource': 84, 'scheduler': 600},
                  'passes': [], 'stopped': None, 'denominators': report['denominators']}
        def save():
            (output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        audit['failure'] = str(error)
        (output / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n')
        report['stopped'] = 'preparation failed before measurement: ' + str(error)
        report['gated_passes'] = ['lifecycle', 'diagnostic', 'resource', 'scheduler']
        save()
        return 1
    commands = [('lifecycle', [str(args.probe), str(args.scheduler / 'B2/prefix/libexec/holonight-images/runtime'),
                              str(output / 'lifecycle.jsonl'), *map(str, fixtures)])]
    for kind, package in (('diagnostic', args.diagnostic), ('resource', args.diagnostic), ('scheduler', args.scheduler)):
        commands.append((kind, ['python3', str(ROOT / 'scripts/run-preview-evidence.py'), str(package),
                                str(args.fixtures), '--kind', kind]))
    for kind, command in commands:
        entry = {'kind': kind, 'command': command}
        report['passes'].append(entry)
        save()
        try:
            with (output / (kind + '.log')).open('x') as log:
                code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
        except OSError as error:
            entry['launch_error'] = str(error)
            code = 1
        entry['exit'] = code
        if kind == 'lifecycle':
            lifecycle = lifecycle_report(output / 'lifecycle.jsonl')
            entry.update(lifecycle)
            report['denominators']['lifecycle_cycles'] = lifecycle['denominators']
            if lifecycle['failed'] and code == 0:
                code = 1
            entry['effective_exit'] = code
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
