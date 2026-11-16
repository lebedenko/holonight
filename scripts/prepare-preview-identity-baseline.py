#!/usr/bin/env python3
"""Freeze a fresh startup baseline; never import or call execution entrypoints."""
import argparse
import importlib.util
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('identity_boundary', Path(__file__).with_name('preview-identity-evidence.py'))
e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e)
h = e.h
COMBINATIONS = [('A-fixed', False), ('A-fixed', True), ('C', False), ('C', True)]


def schedule():
    rows = []
    def append(variant, captured, block, sample):
        rows.append(dict(invocation=len(rows), variant=variant, captured=captured, block=block,
                         sample=sample, warmup=block is None, count=1))
    for variant, captured in COMBINATIONS:
        append(variant, captured, None, 0)
    for block in range(5):
        order = COMBINATIONS[block % 4:] + COMBINATIONS[:block % 4]
        if block % 2:
            order = list(reversed(order))
        for variant, captured in order:
            for sample in range(5):
                append(variant, captured, block, sample)
    return rows


def protocol():
    return dict(version=1, schedule=schedule(), measured=100, warmups=4, timeout_seconds=30,
                cleanup_seconds=5, retries=0, event='dummy:u', no_samples=True, clock='mono',
                inheritance=True, buildid_mmap=True, namespaces=True, task=True,
                buildid_cache=False, symbol_downloads=False, cpu_samples=False, callstacks=False,
                scheduler_events=False, offscreen=True, cache_flush=False, affinity=False,
                artificial_load=False, qualification='78/80 unchanged',
                mapping_scope='captured executions only', installer_scope='new staging only; no historical attestation',
                acceptance='prepared; execution capability unvalidated')


def prepare(output):
    h.fresh(output, e.protected_inputs())
    result = dict(status='blocked', capability='unvalidated', workloads=0, builds=0, staging=0, recordings=0)
    inputs, tools = None, {}
    try:
        tools = e.snapshots()
        (output / 'tools').mkdir()
        for name in tools:
            shutil.copy2(name, output / 'tools' / Path(name).name)
        inputs = e.retained()
        h.write(output / 'inputs.json', inputs)
        h.write(output / 'protocol.json', protocol())
        for variant, value in inputs['variants'].items():
            destination = output / 'frozen' / variant
            destination.mkdir(parents=True)
            shutil.copy2(value['harness']['path'], destination / 'preview-benchmark')
            shutil.copytree(value['runtime'], destination / 'runtime')
            h.require(h.inventory(destination / 'runtime') == value['inventory'], 'copy membership drift')
        shutil.copy2(inputs['fixture']['path'], output / 'frozen/3200x2400.png')
        h.require(h.recheck(inputs['inventories'], dict(inputs['files'], **tools)), 'preparation input/tool drift')
        result['status'] = 'prepared'
    except (OSError, ValueError, KeyError, TypeError) as error:
        result['failure'] = str(error)
    finally:
        if inputs is not None:
            try:
                h.require(h.recheck(inputs['inventories'], dict(inputs['files'], **tools)), 'final input/tool drift')
            except (OSError, ValueError) as error:
                result.update(status='blocked', failure=str(error))
        h.write(output / 'assessment.json', result)
        (output / 'REPORT.md').write_text(
            '# Identity-bound startup baseline preparation\n\n' + result['status'] +
            '; execution capability unvalidated.\n\nZero builds, staging operations, workloads or recordings launched. '
            'New installer identity does not attest historical execution. Qualification remains 78/80; '
            'no optimization selected. Mapping evidence will apply only to captured executions.\n\n' +
            result.get('failure', 'A later authorized capability rehearsal is required before real observations.') + '\n')
        h.write(output / 'tools.json', tools)
        h.write(output / 'seal.json', h.inventory(output))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.output.absolute())
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'prepared')
