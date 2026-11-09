#!/usr/bin/env python3
"""Run separate diagnostic, resource, or scheduler evidence without touching frozen A/B results."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

accounting = module('preview-evidence-accounting')
baselines = module('preview-experiment-baselines')
measure = module('measure-preview-experiments')


def read(path):
    try:
        return path.read_text()
    except OSError:
        return None


def observe(pid, proc_root=Path('/proc')):
    status = read(proc_root / str(pid) / 'status')
    rss = None
    if status:
        for line in status.splitlines():
            if line.startswith('VmRSS:'):
                rss = int(line.split()[1]) * 1024
    discovery_complete = status is not None
    pending = [pid]
    seen = set()
    groups = set()
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        tasks = list((proc_root / str(current) / 'task').glob('*'))
        discovery_complete = discovery_complete and bool(tasks)
        for task in tasks:
            children = read(task / 'children')
            discovery_complete = discovery_complete and children is not None
            if children:
                pending.extend(int(child) for child in children.split())
        membership = read(proc_root / str(current) / 'cgroup')
        discovery_complete = discovery_complete and membership is not None
        if membership:
            for line in membership.splitlines():
                if line.startswith('0::') and 'holonight-images-' in line:
                    groups.add('/sys/fs/cgroup' + line[3:])
    values = {group: read(Path(group) / 'memory.current') for group in groups}
    numeric = {group: int(value) if value and value.strip().isdigit() else None for group, value in values.items()}
    concurrent = sum(numeric.values()) if discovery_complete and all(v is not None for v in numeric.values()) else None
    return {'monotonic_ns': time.monotonic_ns(), 'parent_rss_bytes': rss,
            'scope_memory_current': numeric, 'concurrent_scope_bytes': concurrent,
            'concurrent_parent_plus_scope_bytes': rss + concurrent if rss is not None and concurrent is not None else None,
            'discovery_complete': discovery_complete, 'scope_count': len(groups), 'descendant_count': len(seen) - 1}


def run_process(command, log, resource_file=None):
    with log.open('x') as stream:
        process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
        if resource_file is None:
            return process.wait()
        with resource_file.open('x') as samples:
            while process.poll() is None:
                start = time.monotonic()
                samples.write(json.dumps(observe(process.pid)) + '\n')
                samples.flush()
                time.sleep(max(0, .010 - (time.monotonic() - start)))
        return process.wait()


def variants(provenance, kind):
    metadata = provenance.get('variants', {})
    if metadata:
        for value in metadata.values():
            if value.get('corrected_cleanup') and not value.get('correction_verified'):
                raise ValueError('corrected package lacks verified patch application')
        labels = [name for name, value in metadata.items()
                  if value['role'] == ('scheduler' if kind == 'scheduler' else 'diagnostic')]
        if len(labels) != (2 if kind == 'scheduler' else 1):
            raise ValueError('package variants do not match requested pass')
        return labels
    return ['A', 'B'] if kind == 'scheduler' else ['D']


def validate_workload(value):
    return (isinstance(value, dict) and value.get('fixtures') ==
            ['160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg'] * 4
            and value.get('scheduler_threads') == 2 and value.get('box_pixels') == 256)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packages', type=Path)
    parser.add_argument('fixtures', type=Path)
    parser.add_argument('--kind', required=True, choices=('diagnostic', 'resource', 'scheduler'))
    args = parser.parse_args()
    packages, fixtures = args.packages.resolve(), args.fixtures.resolve()
    package_provenance = json.loads((packages / 'provenance.json').read_text())
    labels = variants(package_provenance, args.kind)
    inputs = [fixtures / name for name in ('160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg')]
    fixture_hashes = {str(p): baselines.digest(p) for p in inputs}
    output = Path(tempfile.mkdtemp(prefix=args.kind + '-run-', dir=packages))
    print(output, flush=True)
    repetitions = {'diagnostic': 10, 'resource': 3, 'scheduler': 100}[args.kind]
    provenance = {'kind': args.kind, 'qualifying_latency': False, 'fixtures': fixture_hashes,
                  'repetitions': repetitions, 'resource_interval_ms': 10 if args.kind == 'resource' else None,
                  'package_provenance_sha256': baselines.digest(packages / 'provenance.json'),
                  'commands': [], 'binaries': {}, 'stopped': None,
                  'variants': labels, 'variant_metadata': package_provenance.get('variants', {}),
                  'planned_samples': 600 if args.kind == 'scheduler' else 28 * repetitions}
    for source in (Path(__file__), ROOT / 'scripts/preview-evidence-accounting.py'):
        (output / source.name).write_bytes(source.read_bytes())
    def save():
        (output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    if args.kind == 'scheduler':
        for label in labels:
            binary = packages / label / 'harness/preview-grid-control'
            described = json.loads(subprocess.check_output([str(binary), '--describe-workload'], text=True))
            if not validate_workload(described):
                raise ValueError('non-mixed or incorrectly configured scheduler workload')
        provenance['workload_validated'] = True
    attempt = 0
    if args.kind == 'scheduler':
        # 100 attempts/workload/baseline; every batch cycles all four fixtures four times.
        schedule = ((label, workload, fixtures, 1)
                    for block in range(10)
                    for label in (labels if block % 2 == 0 else reversed(labels))
                    for workload in ('cold', 'warm', 'cancel')
                    for index in range(block * 10, block * 10 + 10))
    else:
        schedule = ((labels[0], scenario, fixture, repetitions)
                    for fixture in inputs for scenario in measure.SCENARIOS)
    try:
        for label, scenario, fixture, count in schedule:
            base = packages / label
            binary = base / 'harness' / ('preview-grid-control' if args.kind == 'scheduler' else 'preview-benchmark')
            provenance['binaries'][str(binary)] = baselines.digest(binary)
            target = output / f'{attempt:04}-{label}-{scenario}-{fixture.name}.json'
            command = [str(binary), str(base / 'prefix/libexec/holonight-images/runtime'), str(fixture),
                       scenario, str(count), str(target)]
            provenance['commands'].append(command)
            save()
            code = run_process(command, target.with_suffix('.log'),
                               target.with_suffix('.resources.jsonl') if args.kind == 'resource' else None)
            raw = read(target) or ''
            if args.kind != 'scheduler' and raw:
                # Preserve complete service samples even on a nonzero harness exit.
                try:
                    raw = '\n'.join(json.dumps(r) for r in json.loads(raw)['samples'])
                except (ValueError, KeyError, TypeError):
                    pass
            result = accounting.preserve_attempt(output / 'attempts.jsonl', attempt, raw,
                                                  read(target.with_suffix('.log')) or '', code, count)
            result['expected_samples'] = count
            (target.with_suffix('.accounting.json')).write_text(json.dumps(result, indent=2) + '\n')
            print(f'{attempt}: {label} {scenario} {fixture.name}: exit {code}', flush=True)
            attempt += 1
            if result['cleanup_failure']:
                provenance['stopped'] = 'unexplained cleanup failure; no retry or manager cleanup'
                return 20
            if code or result['incomplete']:
                provenance['stopped'] = 'incomplete harness attempt'
                return 1
    finally:
        provenance['completed_invocations'] = attempt
        save()
        subprocess.run(['python3', str(ROOT / 'scripts/report-preview-evidence.py'), str(output)], check=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
