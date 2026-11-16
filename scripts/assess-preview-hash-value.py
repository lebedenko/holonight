#!/usr/bin/env python3
"""Assess retained buffered 64 KiB hashing evidence without running workloads."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hash_value_integrity', ROOT / 'scripts/verify-preview-hash-value.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def seal(output):
    write(output / 'seal.json', {str(p.relative_to(output)): v.digest(p)
                                for p in output.rglob('*') if p.is_file() and p.name != 'seal.json'})


def arithmetic(rows, mapping):
    cells = {}
    for row in rows:
        if row['type'] != 'file' or row['warmup'] or row['case'] not in ('device_buffered', 'stream_64k_buffered'):
            continue
        key = row['block'], row['case'], row['ordinal'], row['sweep']
        v.check(key not in cells, 'duplicate ordinal')
        v.check(type(row['update_ns']) is int and row['update_ns'] > 0, 'invalid timer')
        cells[key] = row['update_ns']
    v.check(len(cells) == 8*2*len(mapping)*3, 'missing/extra ordinals')
    blocks = []
    for block in range(8):
        contributions = []
        for file in mapping:
            totals = [sum(cells[block, case, file['ordinal'], sweep] for sweep in range(3))
                      for case in ('device_buffered', 'stream_64k_buffered')]
            a, b = totals
            contributions.append(dict(ordinal=file['ordinal'], size=file['size'], left_sum_ns=a,
                                      right_sum_ns=b, difference_sum_ns=a-b))
        a = sum(r['left_sum_ns'] for r in contributions)
        b = sum(r['right_sum_ns'] for r in contributions)
        blocks.append(dict(block=block, left_sum_ns=a, right_sum_ns=b, left_mean_ns=a/3,
                           right_mean_ns=b/3, difference_sum_ns=a-b, mean_difference_ns=(a-b)/3,
                           duration_ratio=a/b, contributions=contributions))
    return blocks


def recommendation(blocks):
    values = [b['mean_difference_ns'] for b in blocks]
    positive, negative = sum(x > 0 for x in values), sum(x < 0 for x in values)
    below, equal, above = (sum(test(x) for x in values) for test in
                          (lambda x: x < 5_000_000, lambda x: x == 5_000_000, lambda x: x > 5_000_000))
    return dict(threshold_ns=5_000_000, positive_blocks=positive, negative_blocks=negative,
                zero_blocks=8-positive-negative, direction='mixed; inconclusive' if positive and negative else
                'all positive' if positive == 8 else 'all negative' if negative == 8 else 'includes zero; inconclusive',
                below_threshold=below, equal_threshold=equal, above_threshold=above,
                recommendation='defer a private A/B experiment on current evidence' if below == 8 else
                'threshold reached in retained blocks; candidate experiment requires its own plan',
                future_5ms_savings_ruled_out=False)


def report(blocks, decision, context):
    lines = ['# Practical value of buffered 64 KiB hashing', '',
             'Planning threshold recorded before assessment: 5 ms per preview.',
             'New post hoc comparison: device buffered minus stream 64K buffered.',
             'Positive differences favor explicit streaming. Primary timer: read/update only.', '',
             '| Block | Device mean ms | Stream mean ms | Signed difference ms | Duration ratio |',
             '|---|---:|---:|---:|---:|']
    for b in blocks:
        lines.append(f"| {b['block']} | {b['left_mean_ns']/1e6:.6f} | {b['right_mean_ns']/1e6:.6f} | "
                     f"{b['mean_difference_ns']/1e6:+.6f} | {b['duration_ratio']:.8f} |")
    lines += ['', f"Direction: {decision['direction']}; positive {decision['positive_blocks']}, "
              f"negative {decision['negative_blocks']}, zero {decision['zero_blocks']}.",
              f"Threshold crossings: below {decision['below_threshold']}, equal {decision['equal_threshold']}, "
              f"above {decision['above_threshold']}.", '', decision['recommendation'] + '.', '',
              'Neither mixed directions nor this recommendation proves that a future implementation cannot save 5 ms.',
              'Standalone timings and historical preview latencies are separate populations. No endpoint subtraction,',
              'combined quantiles, exact critical-path savings, significance or upper bound is inferred.', '',
              '## Historical work context', '',
              '| Population | Arm | n | Validation median/p95 ms | Read/hash median/p95 ms | Pixels median/p95 ms | Metadata median/p95 ms |',
              '|---|---|---:|---:|---:|---:|---:|']
    for cell in context['distributions']:
        fields = [cell['timings'][k] for k in ('validation_ns', 'read_hash_ns')]
        fields += [cell['endpoints_ns'][k] for k in ('pixels', 'metadata')]
        values = ['unobserved' if f['count'] == 0 else f"{f['median']/1e6:.3f}/{f['p95']/1e6:.3f}" for f in fields]
        lines.append(f"| {cell['population']} | {cell['arm']} | {fields[0]['count']} | " + ' | '.join(values) + ' |')
    lines += ['', 'Full distributions and explicit execution/invocation/observation/service identities are in context.json.',
              'Setup endpoints are unobserved. Warm-ups and setup are excluded from measured distributions.',
              'Profiled and unprofiled populations remain separate. Only same-execution identities join endpoints.', '',
              '## Frozen source and lifecycle interpretation', '',
              'source-citations.json preserves the audit citations and hashes. generation.cpp:109–111 calls refresh()',
              'during RuntimeOwner construction; refresh():124–164 validates protected selection and nested runtime.',
              'verification.cpp:101 uses buffered QFile and hash.addData(&file) in read_hash.',
              'session_pool.cpp:595–601 and preview_service.cpp:842–851 expose explicit refresh paths.',
              'These are call paths, not evidence of redundant calls in one lifetime. lifetimes.json retains 52 distinct',
              'service constructions, each with one validation and zero demonstrated within-lifetime repeated bytes.',
              'Generation identity remains unproven; matching payload or object addresses do not establish it.', '',
              'Prior passing verifications are reused unchanged; seals, bindings, payload mapping, consumed identities,',
              'source citations and arithmetic are rechecked offline. No source reconstruction or workload is rerun.',
              'Any candidate implementation or private experiment requires its own plan.', '']
    return '\n'.join(lines)


def run(mechanism, mechanism_verification, work, work_verification, output):
    paths = [p.resolve() for p in (mechanism, mechanism_verification, work, work_verification)]
    output = output.resolve()
    v.check(not output.exists(), 'destination collision')
    for p in paths:
        v.check(not output.is_relative_to(p) and not p.is_relative_to(output), 'input/output overlap')
    output.mkdir(parents=True)
    result = dict(status='blocked', recommendation=None, new_measurements=False)
    try:
        write(output / 'protocol.json', dict(threshold_ns=5_000_000,
              comparison='device buffered minus stream 64K buffered', classification='new post hoc comparison', new_measurements=False))
        source = output / 'source'
        source.mkdir()
        tools = [Path(__file__).resolve(), ROOT / 'scripts/verify-preview-hash-value.py', ROOT / 'tests/test_preview_hash_value.py']
        for path in tools:
            shutil.copyfile(path, source / path.name)
        write(output / 'tool-identities.json', {str(p): v.digest(p) for p in tools})
        inputs = v.bindings(*paths)
        write(output / 'inputs.json', inputs)
        raw = [json.loads(line) for line in (paths[0] / 'native.stdout').read_text().splitlines()]
        blocks = arithmetic(raw, inputs['mapping'])
        v.check(blocks == v.comparison(paths[0], inputs['mapping']), 'independent arithmetic mismatch')
        write(output / 'arithmetic.json', blocks)
        context = v.context(paths[2])
        write(output / 'context.json', context)
        for name in ('source-citations.json', 'lifetimes.json'):
            shutil.copyfile(paths[2] / name, output / name)
        decision = recommendation(blocks)
        v.check(decision == v.decision(blocks), 'independent decision mismatch')
        # Repeat integrity checks before exposing a recommendation.
        v.check(v.bindings(*paths) == inputs, 'consumed input changed during assessment')
        write(output / 'decision.json', decision)
        (output / 'report.md').write_text(report(blocks, decision, context))
        result.update(status='complete', recommendation=decision['recommendation'])
    except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
        result.update(failure=str(error))
    write(output / 'assessment.json', result)
    seal(output)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('mechanism-evidence', 'mechanism-verification', 'verification-work-audit', 'work-verification', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    result = run(args.mechanism_evidence, args.mechanism_verification,
                 args.verification_work_audit, args.work_verification, args.output)
    print(result)
    sys.exit(result['status'] != 'complete')
