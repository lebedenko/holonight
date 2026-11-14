#!/usr/bin/env python3
"""Interpret a sealed scheduler pilot using retained evidence only; never launch processes."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util
spec = importlib.util.spec_from_file_location('interpret_pilot', Path(__file__).with_name('run-preview-delivery-scheduler.py'))
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
g = r.module('interpret_gaps', 'analyze-preview-delivery-overhead-gaps.py')
o, a, n = r.o, r.a, r.n
require, read, write = o.require, o.read, o.write


def equal(left, right):
    return json.loads(json.dumps(left)) == right


def publication_rows(report, invocation):
    """One row per invocation-local publication, including both endpoint predicates."""
    require(not report['issues'] and report['assessment_available'], 'blocked endpoint accounting')
    result = []
    seen = set()
    for handoff in report['handoffs']:
        identity = handoff['identity']
        token = (identity['pid'], identity['publication'])
        require(token not in seen, 'duplicate publication')
        seen.add(token)
        spans = {}
        for operation in ('enqueue_call', 'callback_execution'):
            matches = [s for s in report['spans'] if s['operation'] == operation
                       and o.gate.analyzer.identity(s['begin']) == o.gate.analyzer.identity(identity)]
            require(len(matches) == 1, 'missing/duplicate publication span')
            spans[operation] = matches[0]
        invoke, callback = spans['enqueue_call'], spans['callback_execution']
        endpoints = []
        for window in report['windows']:
            e = window['delivery']
            if (e['pid'], e['publication']) != token:
                continue
            require(g.g.owns(identity, e), 'endpoint context mismatch')
            require(window['endpoint'] in ('pixels', 'metadata'), 'unknown endpoint')
            require(any(x['endpoint'] == window['endpoint'] and x['record'] == e
                        for x in handoff['endpoints']), 'endpoint handoff mismatch')
            endpoints.append(dict(endpoint=window['endpoint'], record=e))
        require(endpoints and len(endpoints) == len({e['endpoint'] for e in endpoints}), 'duplicate/missing publication endpoints')
        result.append(dict(invocation=invocation, identity=identity, observation=identity['observation'],
                           endpoints=endpoints, invoke_return=invoke['end'], callback_entry=callback['begin'],
                           invoke_return_to_callback_ns=callback['start']-invoke['stop']))
    require(sum(len(x['endpoints']) for x in result) == len(report['windows']), 'unowned endpoint')
    return result


def observations(rows, count):
    result = []
    for observation in range(1, count+1):
        selected = [r for r in rows if r['observation'] == observation]
        endpoints = [e['endpoint'] for r in selected for e in r['endpoints']]
        require(sorted(endpoints) == ['metadata', 'pixels'], 'incomplete observation endpoints')
        result.append(dict(observation=observation, publications=selected))
    require(len({r['observation'] for r in rows}) == count, 'unexpected observation')
    return result


def reconcile(row):
    signed = row['invoke_return_to_callback_ns']
    require(signed == row['invoke_return_to_dispatch_ns'] + row['dispatch_to_callback_ns'], 'signed interval mismatch')
    expected = {row['identity']['tid'], row['callback_entry']['tid']}
    require({t['tid'] for t in row['thread_accounting']} == expected, 'missing publication thread')
    for thread in row['thread_accounting']:
        require(thread['complete'] and sum(thread['totals'].values()) == max(0, signed), 'thread duration mismatch')
        for state in thread['totals']:
            require(sum(part['totals'][state] for part in thread['parts'].values()) == thread['totals'][state], 'dispatch split mismatch')
        require(sum(x['stop_ns']-x['start_ns'] for x in thread['intervals']) == max(0, signed), 'timeline duration mismatch')
        thread['roles'] = [name for name, tid in [('publisher', row['identity']['tid']), ('receiver', row['callback_entry']['tid'])] if tid == thread['tid']]


def summaries(datasets):
    result = []
    for dataset, rows in datasets.items():
        for endpoint in ('pixels', 'metadata', 'unique_publications'):
            selected = rows if endpoint == 'unique_publications' else [r for r in rows if any(e['endpoint'] == endpoint for e in r['endpoints'])]
            result.append(dict(dataset=dataset, endpoint=endpoint,
                               observations=len({r['observation_key'] for r in selected}),
                               unique_publications=len(selected), endpoint_count=sum(len(r['endpoints']) for r in selected) if endpoint == 'unique_publications' else len(selected),
                               **g.distribution([r['invoke_return_to_callback_ns'] for r in selected])))
    return result


def selections(rows):
    result = []
    for endpoint in ('pixels', 'metadata'):
        candidates = [r for r in rows if any(e['endpoint'] == endpoint for e in r['endpoints'])]
        maximum = max(r['invoke_return_to_callback_ns'] for r in candidates)
        result.extend(dict(endpoint=endpoint, publication=row) for row in candidates if row['invoke_return_to_callback_ns'] == maximum)
    return result


def raw_citations(value):
    """Verify exact raw file/line citations recursively, retaining original records."""
    refs = {}
    def visit(item):
        if isinstance(item, dict):
            if 'file' in item and 'line' in item:
                path = Path(item['file'])
                require(path.absolute() == path.resolve(), 'raw citation symlink')
                lines = path.read_text().splitlines()
                line = item['line']
                require(type(line) is int and 1 <= line <= len(lines), 'invalid raw citation')
                text = lines[line-1]
                if 'text' in item:
                    require(text == item['text'], 'raw citation text mismatch')
                elif 'operation' in item:
                    require(text.startswith('DELIVERY ') and all(json.loads(text[9:]).get(k) == v for k,v in item.items() if k not in ('file','line')), 'raw delivery mismatch')
                refs[str(path), line] = dict(file=str(path), line=line, text=text, sha256=o.digest(path))
            for child in item.values(): visit(child)
        elif isinstance(item, list):
            for child in item: visit(child)
    visit(value)
    return list(refs.values())


def replay_invocation(target, count, process=None):
    samples = read(target)['samples']
    require(len(samples) == count, 'sample count mismatch')
    process = read(target.with_suffix('.process.json')) if process is None else process
    require(process['exit'] == 0 and not process['timeout'] and process['cleanup_verified'], 'failed invocation')
    text = target.with_suffix('.stderr').read_text() + '\n' + target.with_suffix('.stdout').read_text()
    report = o.gate.analyzer.analyze(text, str(target.with_suffix('.stderr')), 'B', samples)
    require(report == read(target.with_suffix('.v4.json')), 'v4 replay mismatch')
    o.v4_gate(report, 'B', count)
    return report


def render(summary, rows, selected, diagnostics, uncaptured):
    lines = ['# Completed B / 160x80.png scheduler pilot', '',
             f"Ten captured observations ({sum(len(r['endpoints']) for r in rows)} endpoints, {len(rows)} unique publications) are separate from one uncaptured observation ({sum(len(r['endpoints']) for r in uncaptured)} endpoints, {len(uncaptured)} unique publications). Original blocked assessments are preserved in provenance.json.", '',
             'All values below are signed enqueue-return → callback-entry nanoseconds. Instrumentation differs between datasets; comparisons are descriptive. Nearest-rank p95 is the maximum for each ten-sample group.', '',
             '| Dataset | View | Observations | Publications | Min ns | Median ns | p95 ns | Max ns |',
             '|---|---|---:|---:|---:|---:|---:|---:|']
    for s in summary:
        lines.append(f"| {s['dataset']} | {s['endpoint']} | {s['observations']} | {s['count']} | {s['minimum_ns']} | {s['median_ns']} | {s['p95_ns']} | {s['maximum_ns']} |")
    lines += ['', '## Captured publications', '', '| Observation | Publication | Endpoint | Return → dispatch ns | Dispatch → callback ns | Return → callback ns |', '|---:|---:|---|---:|---:|---:|']
    for row in rows:
        lines.append(f"| {row['observation']} | {row['identity']['publication']} | {', '.join(e['endpoint'] for e in row['endpoints'])} | {row['invoke_return_to_dispatch_ns']} | {row['dispatch_to_callback_ns']} | {row['invoke_return_to_callback_ns']} |")
    lines += ['', '## Both-thread states for every captured publication', '', '| Observation | Publication | Thread | Role | Running ns | Runnable ns | Non-runnable ns | Unknown ns |', '|---:|---:|---:|---|---:|---:|---:|---:|']
    for row in rows:
        for t in row['thread_accounting']:
            v = t['totals']
            lines.append(f"| {row['observation']} | {row['identity']['publication']} | {t['tid']} | {', '.join(t['roles'])} | {v['running']} | {v['runnable']} | {v['non_runnable']} | {v['unknown']} |")
    lines += ['', '## Separate uncaptured observation', '', 'Scheduler states are unavailable for this invocation. It is excluded from captured and historical summaries.', '']
    for row in uncaptured:
        lines.append(f"- Publication {row['identity']['publication']} ({', '.join(e['endpoint'] for e in row['endpoints'])}): return → dispatch {row['invoke_return_to_dispatch_ns']} ns; dispatch → callback {row['dispatch_to_callback_ns']} ns; return → callback {row['invoke_return_to_callback_ns']} ns.")
    lines += ['', '## Largest endpoint windows (ties retained)', '']
    for item in selected:
        row = item['publication']
        lines.append(f"\n{item['endpoint']}: observation {row['observation']}, publication {row['identity']['publication']}, {row['invoke_return_to_callback_ns']} ns.\n")
        for thread in row['thread_accounting']:
            lines.append(f"- TID {thread['tid']} ({', '.join(thread['roles'])}): {thread['totals']}; dispatch split { {k:v['totals'] for k,v in thread['parts'].items()} }.")
    lines += ['', f'Scheduler diagnostics retained: {dict(Counter(diagnostics))}. All target windows have resolved task lifetimes, complete coverage, zero unknown time and reconciled dispatch splits. Unrelated incomplete initial history does not invalidate these windows; scheduler rules are unchanged.', '',
              f"The historical enqueue-return → callback-entry boundary pattern appears in this pilot: {sum(x['invoke_return_to_callback_ns'] > 0 for x in rows)} of {len(rows)} captured publication intervals are positive. No recurrence threshold or significance claim is introduced.", '',
              'See observations.json for all ten observations, uncaptured.json for the separate observation, publications.json for both-thread states and dispatch splits, selected-timelines.json for tied maxima and scheduler raw transitions, raw-citations.json for exact raw records, and source-citations.json for reconstructed frozen probes.', '',
              'Non-runnable time does not identify a blocking cause. Enqueue-return → callback-entry is not pure queue residence. Endpoint and thread views overlap and must not be summed. Incremental overhead is unmeasured; no overhead subtraction, performance qualification or C/D conclusion changes.', '',
              'Recommendation: another experiment is not justified solely to explain these sub-millisecond pilot windows. The retained scheduler states and exact boundaries answer this pilot’s accounting question. A separately approved matched experiment would be justified only if the aim is to explain the larger historical tail or quantify recurrence under comparable instrumentation; this ten-observation pilot cannot answer that question. No experiment was executed.']
    for endpoint in ('pixels', 'metadata'):
        pilot = next(s for s in summary if s['dataset'] == 'captured' and s['endpoint'] == endpoint)
        old = next(s for s in summary if s['dataset'] == 'historical' and s['endpoint'] == endpoint)
        lines.insert(-1, f"{endpoint}: pilot median {pilot['median_ns']} ns versus historical {old['median_ns']} ns; pilot maximum {pilot['maximum_ns']} ns versus historical {old['maximum_ns']} ns. These observed magnitudes do not establish a change in the underlying distribution.\n")
    return '\n'.join(lines)+'\n'


def report(execution, normalized, analysis, historical, output):
    inputs = [execution, normalized, analysis, historical]
    o.fresh(output, *inputs)
    before = {}; tracked = {}; result = dict(status='blocked')
    tool_hashes = {str(p):o.digest(p) for p in (r.ROOT/'scripts').glob('*.py')}
    try:
        require(all(p.absolute() == p.resolve() for p in inputs), 'symlink input refused')
        before = {str(p):o.inventory(p) for p in inputs}
        for p in inputs: o.check_output(p)
        for p in (normalized, analysis):
            require(read(p/'assessment.json')['status'] == 'complete', 'blocked corrected input')
            integrity = read(p/'integrity.json')
            require(all(c['passed'] for c in integrity['final_checks'].values()), 'failed corrected integrity')
            for name, digest in integrity['before'].items():
                require(o.digest(Path(name)) == digest, 'corrected consumed hash mismatch')
                tracked[name] = digest
        consumed = read(execution/'integrity.json')
        require(all(c['passed'] for c in consumed['final_checks'].values()), 'original integrity failed')
        for name, inventory in consumed['before'].items():
            path = Path(name)
            require(o.inventory(path) == inventory, 'execution consumed drift: '+name)
            o.check_output(path)
            tracked.update({str(path/k):v for k,v in inventory.items()})
        packages = [Path(name) for name in consumed['before'] if (Path(name)/'anchors.json').exists()]
        require(len(packages) == 1, 'ambiguous source preparation')
        package = packages[0]
        o.check_output(r.PREPARED)
        base_inventory = o.inventory(r.PREPARED)
        tracked.update({str(r.PREPARED/name):digest for name,digest in base_inventory.items()})
        r.p.verify_generated(package, r.PREPARED)
        source = read(package/'source-citations.json')
        source += g.citations(r.PREPARED)['B']
        for path in (package/'B').rglob('*'):
            if path.is_file() and path.suffix in ('.h', '.cpp'):
                lines = path.read_text().splitlines()
                for index, line in enumerate(lines):
                    if any(word in line for word in ('enqueue_call', 'callback_execution', 'endpoint_pixels', 'endpoint_metadata')):
                        source.append(dict(file=str(path), sha256=o.digest(path), line=index+1, text=line, excerpt='\n'.join(lines[max(0,index-4):index+5])))
        write(output/'source-citations.json', source)
        # Historical raw/source citations are checked against the gap package's
        # sealed consumed inventories, without inspecting a live managed runtime.
        historical_integrity = read(historical/'integrity.json')
        require(read(historical/'assessment.json')['status'] == 'complete' and all(c['passed'] for c in historical_integrity['final_checks'].values()), 'blocked historical package')
        historical_hashes = {str(Path(root)/name):digest for root, inv in historical_integrity['before'].items() for name,digest in inv.items()}
        capture = n.normalize((execution/'perf-export.stdout').read_text(), read(execution/'recording-metadata.json'), read(execution/'task-identities.json'), str(execution/'perf-export.stdout'))
        require(capture == read(normalized/'scheduler.json'), 'normalization replay mismatch')
        replay = a.account(read(execution/'accounting.json'), read(execution/'supplemental.json'), capture)
        require(equal(dict(replay, status='complete'), read(analysis/'assessment.json')) and replay['attribution_complete'], 'corrected analysis replay mismatch')
        captured_report = replay_invocation(execution/'observations/captured.json', 10)
        require(read(execution/'accounting.json')[0]['accounting'] == captured_report, 'captured accounting mismatch')
        require(r.supplemental(execution/'observations/captured.json', 'captured') == read(execution/'supplemental.json'), 'supplemental replay mismatch')
        rows = publication_rows(captured_report, 'captured')
        for row in rows:
            matches = [s for s in replay['rows'] if s['invocation'] == row['invocation'] and s['identity'] == row['identity']]
            require(len(matches) == 1, 'ambiguous scheduler publication')
            row.update(matches[0]); reconcile(row)
            row['observation_key'] = ('captured', row['observation'])
        original_analysis = read(execution/'analysis.json')
        for row in rows:
            previous = [v for v in original_analysis['rows'] if v['invocation'] == row['invocation'] and v['identity'] == row['identity']]
            require(len(previous) == 1 and all(previous[0][key] == row[key] for key in ('invoke_return_to_dispatch_ns', 'dispatch_to_callback_ns', 'invoke_return_to_callback_ns')), 'original signed boundaries changed')
        obs = observations(rows, 10)
        uncaptured_report = replay_invocation(execution/'observations/uncaptured.json', 1)
        uncaptured = publication_rows(uncaptured_report, 'uncaptured')
        uncaptured_links = a.account([dict(invocation='uncaptured', accounting=uncaptured_report, clock=read(execution/'observations/uncaptured.command.json')['clock'])], r.supplemental(execution/'observations/uncaptured.json', 'uncaptured'))
        require(not uncaptured_links['issues'], 'uncaptured linkage issues')
        for row in uncaptured:
            matches = [s for s in uncaptured_links['rows'] if s['identity'] == row['identity']]
            require(len(matches) == 1 and matches[0]['link_status'] == 'linked', 'uncaptured linkage failed')
            row.update(matches[0])
        observations(uncaptured, 1)
        history = []
        historical_rows = [x for x in read(historical/'endpoints.json') if x['variant'] == 'B' and x['fixture'] == '160x80.png']
        for index in sorted({x['invocation_index'] for x in historical_rows}):
            endpoints = [x for x in historical_rows if x['invocation_index'] == index]
            path = Path(endpoints[0]['delivery']['file'])
            target = path.with_suffix('.json')
            for f in (target, path, target.with_suffix('.stdout'), target.with_suffix('.v4.json'), target.parent.parent/'assessment.json'):
                require(str(f) in historical_hashes and o.digest(f) == historical_hashes[str(f)], 'historical consumed hash mismatch: '+str(f))
                tracked[str(f)] = historical_hashes[str(f)]
            entry = read(target.parent.parent/'assessment.json')['invocations'][index]
            rep = replay_invocation(target, 10, entry['process'])
            regenerated = g.endpoint_rows(rep, 'B', '160x80.png', 10)
            for saved in endpoints:
                require(any(all(saved[k] == row[k] for k in row) for row in regenerated), 'historical endpoint replay mismatch')
            hr = publication_rows(rep, str(index))
            observations(hr, 10)
            for row in hr: row['observation_key'] = (str(index), row['observation'])
            history.extend(hr)
        require(len(historical_rows) == 200 and len(history) > 0, 'historical B cell incomplete')
        summary = summaries(dict(captured=rows, historical=history))
        selected = selections(rows)
        for item in selected:
            row = item['publication']; left, right = row['invoke_return']['ns'], row['callback_entry']['ns']
            tids = {t['tid'] for t in row['thread_accounting']}
            # Include the establishing preceding transition and following transition
            # for each target task as well as every transition inside the window.
            keys = [t['key'] for t in capture['tasks'] if t['key'][0] == row['identity']['pid'] and t['key'][1] in tids and t['start_ns'] <= left <= right <= t['stop_ns']]
            transitions = []
            for key in keys:
                events = [e for e in capture['events'] if any(e.get(k) == key for k in ('prev','next','task'))]
                prior = [e for e in events if e['ns'] <= left]; later = [e for e in events if e['ns'] >= right]
                transitions += prior[-1:] + [e for e in events if left < e['ns'] < right] + later[:1]
            item['scheduler_transitions'] = transitions
        raw = raw_citations([rows, uncaptured, history, selected])
        tracked.update({citation['file']:citation['sha256'] for citation in source})
        for ref in raw:
            tracked[ref['file']] = ref['sha256']
        provenance = dict(original_assessment=read(execution/'assessment.json'), original_analysis_attribution_complete=original_analysis['attribution_complete'], corrected_normalization=read(normalized/'assessment.json'), corrected_analysis=dict(status='complete', attribution_complete=True), inputs={str(p):o.digest(p/'seal.json') for p in inputs}, source_preparation=str(package), historical_cited_hashes=historical_hashes)
        artifacts = {'publications.json':rows, 'observations.json':obs, 'uncaptured.json':uncaptured, 'historical-publications.json':history, 'summary.json':summary, 'selected-timelines.json':selected, 'raw-citations.json':raw, 'provenance.json':provenance, 'diagnostics.json':dict(normalizer=capture['diagnostics'], scheduler=replay['scheduler_issues'])}
        for name, value in artifacts.items(): write(output/name, value)
        (output/'REPORT.md').write_text(render(summary, rows, selected, replay['scheduler_issues'], uncaptured))
        result.update(status='complete', observations=10, endpoints=20, publications=len(rows), uncaptured_observations=1)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        result['failure'] = str(error)
    finally:
        try:
            require(all(o.inventory(p) == before.get(str(p)) for p in inputs), 'input drift')
            require(all(o.digest(Path(name)) == digest for name,digest in {**tracked, **tool_hashes}.items()), 'consumed input or tool drift')
        except (OSError, ValueError) as error:
            result.update(status='blocked', integrity_failure=str(error))
        if result['status'] != 'complete':
            (output/'REPORT.md').write_text('# Blocked offline interpretation\n\n'+result.get('failure', result.get('integrity_failure',''))+'\n\nNo partial results substitute for a verified report.\n')
        write(output/'integrity.json', dict(before=before, consumed=tracked, tools=tool_hashes, passed=result['status']=='complete'))
        write(output/'assessment.json', result)
        for path in (Path(__file__), Path(r.__file__), Path(a.__file__), Path(n.__file__)):
            (output/path.name).write_bytes(path.read_bytes())
        o.seal(output)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('execution', 'normalized', 'analysis', 'historical', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    result = report(args.execution, args.normalized, args.analysis, args.historical, args.output)
    print(json.dumps(result))
    sys.exit(result['status'] != 'complete')
