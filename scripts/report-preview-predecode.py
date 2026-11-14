#!/usr/bin/env python3
"""Drill into retained A/C pre-decode intervals; no processes or experiments."""
import argparse
from collections import defaultdict
import difflib
import importlib.util
from pathlib import Path
import re
import statistics
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('predecode_context', Path(__file__).with_name('report-preview-startup-bottlenecks.py'))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
o, require, read, write, stats = b.o, b.require, b.read, b.write, b.stats
PHASES = b.v3.a.PHASES
PARENTS = {'generation_validation': ('runtime_validation',),
           'helper_prepare': ('runtime_validation', 'generation_acquisition')}


def label(phases):
    return ' + '.join(sorted(phases)) or 'uncovered'


def analyze(part, variant):
    left, right = part['start_ns'], part['stop_ns']
    require(right > left, 'empty pre-decode interval')
    spans = part['spans']
    require(all(x['role'] in ('demand', 'service_control') for x in spans), 'foreign span role')
    require(all(x['start'] <= x['clipped_start'] < x['clipped_stop'] <= x['stop']
                and left <= x['clipped_start'] < x['clipped_stop'] <= right for x in spans), 'invalid clipped span')
    points = sorted({left, right, *(x[k] for x in spans for k in ('clipped_start', 'clipped_stop'))})
    segments, groups = [], defaultdict(int)
    for start, stop in zip(points, points[1:]):
        active = sorted({x['operation'] for x in spans if x['clipped_start'] <= start and x['clipped_stop'] >= stop})
        segments.append(dict(start_ns=start, stop_ns=stop, phases=active, label=label(active)))
        groups[label(active)] += stop-start
    duration = right-left
    require(sum(groups.values()) == duration, 'disjoint reconciliation failure')
    uncovered = groups.get('uncovered', 0)
    require(uncovered == part['uncovered_ns'] and duration-uncovered == part['covered_ns'], 'coverage reconciliation failure')
    phases = {}
    for name in sorted(set(PHASES) | {x['operation'] for x in spans}):
        selected = [x for x in spans if x['operation'] == name]
        coverage = b.g.g.intervals(left, right, selected)
        phases[name] = dict(availability='observed' if selected else
                           'absent_by_design' if variant == 'A' and name.startswith('generation_') else 'unavailable_in_predecode',
                           spans=selected, union=coverage['covered'],
                           union_ns=coverage['covered_ns'] if selected else None,
                           inclusive_ns=sum(x['clipped_stop']-x['clipped_start'] for x in selected) if selected else None)
    outside = {}
    # Subtract interval sets per observation, including only overlap inside each
    # parent. No assumption that different worker threads form a critical path.
    for parent, children in PARENTS.items():
        if phases[parent]['union_ns'] is None:
            outside[parent] = dict(children=children, duration_ns=None, intervals=[], availability=phases[parent]['availability'])
            continue
        pieces = []
        for start, stop in phases[parent]['union']:
            excluded = [dict(start=x['clipped_start'], stop=x['clipped_stop']) for x in spans if x['operation'] in children]
            pieces += b.g.g.intervals(start, stop, excluded)['uncovered']
        outside[parent] = dict(children=children, intervals=pieces, duration_ns=sum(y-x for x,y in pieces), availability='observed')
    return dict(start_ns=left, stop_ns=right, duration_ns=duration, spans=spans, segments=segments,
                groups_ns=dict(groups), phases=phases, parent_outside_nested=outside,
                covered_ns=duration-uncovered, uncovered_ns=uncovered,
                largest_uncovered_ns=max((s['stop_ns']-s['start_ns'] for s in segments if not s['phases']), default=0))


def observations(endpoints):
    grouped = defaultdict(list)
    for row in endpoints:
        grouped[row['invocation_index'], row['observation']].append(row)
    result = []
    for key, rows in sorted(grouped.items()):
        require(len(rows) == 2 and {r['endpoint'] for r in rows} == {'pixels', 'metadata'}, 'missing/duplicate endpoint')
        first, second = rows
        require(all(first[k] == second[k] for k in ('variant', 'block', 'fixture', 'trace_origin', 'decode_boundary')), 'endpoint ownership mismatch')
        require(all(first['delivery'][k] == second['delivery'][k] for k in ('pid', 'service', 'observation', 'job', 'worker')), 'endpoint identity mismatch')
        require({k:v for k,v in first['coarse']['pre_decode'].items() if k!='share'} ==
                {k:v for k,v in second['coarse']['pre_decode'].items() if k!='share'}, 'pre-decode endpoint mismatch')
        require(all(r['delivery']['observation'] == key[1] for r in rows), 'observation ownership mismatch')
        result.append(dict(invocation_index=key[0], observation=key[1], variant=first['variant'], block=first['block'],
                           fixture=first['fixture'], endpoints={r['endpoint']:dict(harness_latency_ns=r['harness_latency_ns'],
                           delivery=r['delivery'], trace_origin=r['trace_origin'], decode_boundary=r['decode_boundary'],
                           predecode_share_of_endpoint_window=r['coarse']['pre_decode'].get('share')) for r in rows},
                           **analyze(first['coarse']['pre_decode'], first['variant'])))
    return result


def summarize(rows):
    labels = sorted({name for r in rows for name in r['groups_ns']})
    groups = defaultdict(list)
    for row in rows:
        for block in ('pooled', row['block']):
            groups[row['variant'], block].append(row)
    result = []
    for (variant, block), rs in sorted(groups.items(), key=lambda x:str(x[0])):
        def available(values):
            values = [v for v in values if v is not None]
            return stats(values) if values else None
        result.append(dict(variant=variant, block=block, observations=len(rs), endpoint_mappings=2*len(rs),
            duration_ns=stats([r['duration_ns'] for r in rs]),
            uncovered_ns=stats([r['uncovered_ns'] for r in rs]),
            groups={name:dict(duration_ns=stats([r['groups_ns'].get(name,0) for r in rs]),
                               share=stats([r['groups_ns'].get(name,0)/r['duration_ns'] for r in rs])) for name in labels},
            phases={name:dict(availability_counts={status:sum(r['phases'][name]['availability']==status for r in rs)
                    for status in sorted({r['phases'][name]['availability'] for r in rs})},
                    **{metric:available([r['phases'][name][metric] for r in rs]) for metric in ('union_ns','inclusive_ns')}) for name in rs[0]['phases']},
            parent_outside_nested={name:available([r['parent_outside_nested'][name]['duration_ns'] for r in rs]) for name in PARENTS}))
    return result


def ranking(summary):
    pooled = {r['variant']:r for r in summary if r['block']=='pooled'}
    c = pooled['C']['groups']
    return dict(order=sorted(c, key=lambda n:(-c[n]['share']['median'], -c[n]['share']['p95'], n)),
                C=c, A=pooled['A']['groups'])


def selections(rows, harness):
    selected = defaultdict(list)
    for variant in ('A', 'C'):
        rs = [r for r in rows if r['variant']==variant]
        values = sorted((r['duration_ns'] for r in rs), reverse=True)
        cutoff, median = values[min(4,len(values)-1)], statistics.median(values)
        nearest = min(abs(v-median) for v in values)
        gap = max(r['largest_uncovered_ns'] for r in rs)
        for r in rs:
            reasons = selected[r['invocation_index'], r['observation']]
            if r['duration_ns'] >= cutoff: reasons.append('predecode_slowest_five_with_ties')
            if abs(r['duration_ns']-median) == nearest: reasons.append('predecode_nearest_median')
            if r['largest_uncovered_ns'] == gap: reasons.append('predecode_largest_uncovered')
    for r in harness:
        selected[r['invocation_index'], r['observation']] += [r['endpoint']+'_harness_'+reason for reason in r['selection_reasons']]
    return [dict(r, selection_reasons=sorted(set(selected[r['invocation_index'],r['observation']])))
            for r in rows if selected[r['invocation_index'],r['observation']]]


def selection_comparison(selected, labels):
    result = []
    for variant in ('A','C'):
        for reason in sorted({reason for r in selected if r['variant']==variant for reason in r['selection_reasons']}):
            rs = [r for r in selected if r['variant']==variant and reason in r['selection_reasons']]
            shares = {n:stats([r['groups_ns'].get(n,0)/r['duration_ns'] for r in rs]) for n in labels}
            result.append(dict(variant=variant, selection=reason, observations=len(rs), shares=shares,
                               order=sorted(labels,key=lambda n:(-shares[n]['median'],-shares[n]['p95'],n))))
    return result


# Exact private v3 source edits observed in the frozen, recorded A-tracing.diff.
# This allowlist deliberately does not match arbitrary StandbyTrace statements.
V3_PRIVATE_LINES = (
    'StandbyTrace::remember(this);',
    'StandbyTrace::Scope trace("service_construction", this, -1);',
    'StandbyTrace::Bind lifetime_bind(StandbyTrace::lifetime(this));',
    'StandbyTrace::forget(this);',
    'StandbyTrace::current.role = "shutdown";',
    'StandbyTrace::Scope destruction_trace("service_destruction", this);',
    'StandbyTrace::Bind trace_bind(trace_context);',
    'StandbyTrace::Scope shutdown_trace("service_shutdown", this);',
    'auto demand_context = StandbyTrace::lifetime(this);',
    'demand_context.job = StandbyTrace::identity();',
    'demand_context.worker = StandbyTrace::identity();',
    'demand_context.role = "demand";',
    'StandbyTrace::Bind demand_bind(demand_context);',
    'StandbyTrace::Scope dispatch_trace("demand_dispatch", this);',
    'StandbyTrace::Scope trace("source_capture", &device, -1);',
    'StandbyTrace::event("helper_prepare", "begin", &process);',
    'StandbyTrace::event("helper_ready", "point", &process);',
    'StandbyTrace::event("helper_prepare", "end", &process);',
    'StandbyTrace::Scope trace(command.operation == Operation::Decode ? "decode_exchange_including_transport" : "inspect_exchange_including_transport", &process);',
    'StandbyTrace::Scope trace("cleanup", &process);',
    'StandbyTrace::Scope trace("runtime_validation", &root, -1);',
)


def reconstruct_v3(data):
    text = data.decode()
    text = text.replace(', trace_context = StandbyTrace::current', '')
    text = text.replace('          QMetaObject::invokeMethod(this, [this, result] {\n'
                        '          StandbyTrace::Bind trace_bind(trace_context); applyResult(result); }, Qt::QueuedConnection);',
                        '          QMetaObject::invokeMethod(this, [this, result] { applyResult(result); }, Qt::QueuedConnection);')
    lines = []
    for line in text.splitlines(True):
        if line.strip() in V3_PRIVATE_LINES or re.fullmatch(r'#include "[^"\n]*/trace.h"\n', line):
            continue
        lines.append(line)
    return ''.join(lines).encode()


def source_comparison(prepared, qualification, consume):
    """Replay recorded literal anchors only, never historical Python functions."""
    manifest = consume(prepared/'manifest.json')
    require(manifest['status']=='prepared' and not manifest['issues'], 'blocked preparation')
    origin = Path(manifest['inputs']['v3'])
    recorded = consume(prepared/'input-integrity.json')
    require(recorded['unchanged'] and recorded['before']==recorded['after'], 'preparation input drift')
    require(str(origin/'seal.json') in recorded['before'], 'unbound v3 seal')
    seal = consume(origin/'seal.json', recorded['before'][str(origin/'seal.json')])
    def frozen(path):
        name = str(path.relative_to(origin))
        require(name in seal, 'unsealed provenance file: '+name)
        return consume(path, seal[name])
    prep = frozen(origin/'preparation.json')
    require(prep['retained_unchanged'] and prep['equivalence']['A']['source']==[], 'v3 source equivalence blocked')
    trees = {}
    for mode in ('AU','AT'):
        inv = prep['pairs'][mode]['source']
        require(o.inventory(origin/mode/'source')==inv, 'provenance source inventory mismatch')
        trees[mode] = {name:(frozen(origin/mode/'source'/name), (origin/mode/'source'/name).read_bytes())[1] for name in inv}
    # Verify the recorded U -> T diff exactly, including hunk context. Keeping it
    # as data avoids importing or executing the old instrumentation recipes.
    diff = []
    for group in ('source','harness-source'):
        for name, digest in prep['pairs']['AU'][group].items():
            left, right = origin/'AU'/group/name, origin/'AT'/group/name
            frozen(left); frozen(right)
            if left.read_bytes()!=right.read_bytes():
                diff.extend(difflib.unified_diff(left.read_text().splitlines(True),right.read_text().splitlines(True),fromfile=str(left),tofile=str(right)))
    recorded_diff = frozen(origin/'A-tracing.diff')
    require(recorded_diff == ''.join(diff), 'v3 tracing diff mismatch')
    # The frozen matched v3 source must equal AT except the documented private
    # trace include path; no whitespace or production statements are normalized.
    matched = {}
    for mode in ('v3','v4'):
        inv = consume(prepared/mode/'A/source-inventory.json')['source']
        require(o.inventory(prepared/mode/'A/source')==inv, 'matched source inventory mismatch')
        matched[mode] = {name:(consume(prepared/mode/'A/source'/name,digest), (prepared/mode/'A/source'/name).read_bytes())[1] for name,digest in inv.items()}
    normalize = b.v3.overhead.normalized
    require({k:normalize(v) for k,v in trees['AT'].items()}=={k:normalize(v) for k,v in matched['v3'].items()}, 'AT to matched-v3 mismatch')
    anchors = consume(prepared/'anchor-review.json')['A']
    files = {'source/'+k:v for k,v in trees['AT'].items()}
    # Source anchors are applied literally with unique occurrence checks.
    replayed = o.prep.replay(files,[x for x in anchors if x['file'].startswith('source/')])
    require({k:normalize(v) for k,v in replayed.items()}=={'source/'+k:normalize(v) for k,v in matched['v4'].items()}, 'v4 source anchor mismatch')
    freeze = consume(qualification/'freeze.json')['source_inventories']['A']
    differences = []
    for name in sorted(trees['AU'].keys() | freeze.keys()):
        left = trees['AU'].get(name)
        right = None
        if name in freeze:
            consume(qualification/'A/source'/name,freeze[name]); right=(qualification/'A/source'/name).read_bytes()
        if left != right:
            differences.append(dict(file=name, diff=''.join(difflib.unified_diff(
                (left or b'').decode().splitlines(True),(right or b'').decode().splitlines(True),fromfile='AU/'+name,tofile='qualification-A/'+name))))
    reconstructed = {name:reconstruct_v3(data) for name,data in trees['AT'].items()}
    residual = []
    for name in sorted(reconstructed.keys() | trees['AU'].keys()):
        left, right = reconstructed.get(name,b''), trees['AU'].get(name,b'')
        if left != right:
            residual.append(dict(file=name,diff=''.join(difflib.unified_diff(left.decode().splitlines(True),right.decode().splitlines(True),fromfile='reconstructed/'+name,tofile='AU/'+name))))
    equivalent = not differences and not residual
    return dict(status='equivalent' if equivalent else 'unavailable', uninstrumented_inventory_equal=not differences,
                reconstruction_residual=residual, allowed_private_lines=V3_PRIVATE_LINES,
                uninstrumented_files=len(freeze), differences=differences,
                chain=[str(prepared/'v4/A/source'),str(prepared/'v3/A/source'),str(origin/'AT/source'),str(origin/'AU/source'),str(qualification/'A/source')],
                matched_v4_literal_anchor_replay=True, matched_v3_to_AT_private_include_only=True,
                v3_recorded_diff_exact=True, v3_tracing_diff=recorded_diff,
                anchors=anchors,
                limitation=('Frozen traced-A production source reconstructs exactly to AU using only the enumerated private tracing/include edits, and AU matches qualification A-fixed exactly. This proves source equivalence under documented tracing transformations, not timing or binary equivalence.' if equivalent else 'Source equivalence unavailable: residual reconstruction or qualification differences are retained exactly; runs remain distinct.') + ' No historical recipe was executed.')


def source_boundaries(prepared, consume):
    citations = []
    files = ('holonight-file-browser/src/preview/preview_service.cpp',
             'holonight-file-browser/src/preview/session_pool.cpp',
             'holonight-images/src/isolated/generation.cpp',
             'holonight-images/src/isolated/verification.cpp',
             'holonight-images/src/isolated/runtime.cpp',
             'holonight-images/src/isolated/client.cpp',
             'holonight-images/src/isolated/capture.cpp')
    tokens = ('StandbyTrace::', 'RuntimeOwner', 'refresh(', 'verifyProtectedRuntime(', 'verifyRuntime(',
              'QCryptographicHash', 'hash.addData', 'parseControl(', 'manifest.readAll(', 'selector(',
              'SessionPool', 'target.session->prepare', 'execution.prepare(', 'state_->launch(',
              'process.start(', 'waitForStarted(', 'groupOf(', 'receive(', 'capture(',
              'Operation::Inspect', 'Operation::Decode', 'exchange(', 'applyResult(')
    for variant in ('A','C'):
        inv = consume(prepared/'v3'/variant/'source-inventory.json')['source']
        for name in files:
            if name not in inv: continue
            path = prepared/'v3'/variant/'source'/name
            consume(path,inv[name])
            lines = path.read_text().splitlines()
            selected = {i for n,line in enumerate(lines) if any(token in line for token in tokens)
                        for i in range(max(0,n-2),min(len(lines),n+4))}
            citations.append(dict(variant=variant,file=str(path),sha256=inv[name],
                                  excerpts=[dict(line=i+1,text=lines[i]) for i in sorted(selected)]))
    return citations


def boundary_report(citations):
    lines = ['# Frozen pre-decode boundaries and intervening calls', '',
             'C: PreviewService constructs PreviewSessionPool, whose state constructs RuntimeOwner. '
             'RuntimeOwner construction calls refresh(); generation_validation scopes refresh(), including '
             'protected-chain checks, selector/descriptor acquisition, verifyRuntime(), manifest parsing/hash '
             'and final identity checks. runtime_validation scopes verifyRuntime(): manifest parsing, '
             'file attributes, per-file SHA-256 and inventory traversal. Its duration is nested inside generation validation.', '',
             'C: demand preparation passes a generation lease through the pool/session to Execution::prepare() '
             'and State::launch(). helper_prepare scopes launch(), including lease resolution, launcher checks, '
             'systemd-run start, scope discovery/limits, gate release and readiness receive. It excludes the earlier '
             'generation validation in these observations. Source capture and inspect exchange are separate measured spans; '
             'client transaction code connects capture/inspection to decode exchange, whose entry ends pre-decode.', '',
             'A: helper_prepare begins before verifyRuntime() and ends after helper readiness; runtime validation '
             'is nested inside helper preparation. A has no generation validation/acquisition by design. '
             'service_construction measures the constructor body; full construction boundaries remain in endpoint '
             'mappings and are not added as overlapping operation coverage.', '',
             'These frozen call sequences identify what lies between probes. They assign no duration to individual '
             'unmarked calls, hashing, launcher operations, scheduling or blocking. Cross-thread overlap alone '
             'does not establish dependency or critical-path attribution.', '']
    for item in citations:
        lines += [f"## {item['variant']}: {item['file']}", '', f"SHA-256: {item['sha256']}", '', '```cpp']
        lines += [f"{x['line']}: {x['text']}" for x in item['excerpts']]
        lines += ['```', '']
    return '\n'.join(lines)


def report(startup, qualification, output):
    startup, qualification, output = (p.absolute() for p in (startup, qualification, output))
    inputs = (startup, qualification)
    o.fresh(output,*inputs)
    before, tracked, result = {}, {}, dict(status='blocked')
    def consume(path, expected=None):
        actual=o.digest(path)
        require(expected is None or actual==expected, 'consumed hash mismatch: '+str(path))
        tracked[str(path)]=actual
        if path.suffix=='.json': return read(path)
        if path.suffix in ('.cpp','.h','.diff','.py'): return path.read_text()
        return path.read_bytes()
    try:
        before={str(p):o.inventory(p) for p in inputs}
        tracked[str(Path(__file__).resolve())]=o.digest(Path(__file__))
        test=Path(__file__).resolve().parents[1]/'tests/test_preview_predecode.py'
        tracked[str(test)]=o.digest(test)
        o.check_output(startup)
        require(read(startup/'assessment.json')['status']=='complete', 'blocked startup input')
        integrity=consume(startup/'integrity.json')
        require(integrity['passed'], 'startup integrity failed')
        for name,digest in integrity['consumed'].items():
            require(o.digest(Path(name))==digest, 'startup consumed drift: '+name)
            tracked[name]=digest
        roots=[Path(p) for p in integrity['before']]
        require(all(o.inventory(p)==integrity['before'][str(p)] for p in roots), 'startup provenance input drift')
        require(qualification in roots, 'qualification provenance mismatch')
        deliveries=[p for p in roots if (p/'endpoints.json').exists()]
        schedulers=[p for p in roots if (p/'summary.json').exists() and p not in deliveries]
        require(len(deliveries)==len(schedulers)==1,'ambiguous replay provenance')
        # This path replays only the same 20 v4 invocations and reuses validated
        # overhead summaries. It never invokes a workload or historical recipe.
        replay=output/'replay'
        replay_result=b.report(deliveries[0],schedulers[0],qualification,replay)
        require(replay_result['status']=='complete', 'startup replay blocked: '+str(replay_result))
        endpoints=consume(startup/'observations.json')
        require(endpoints==read(replay/'observations.json'), 'startup replay mismatch')
        tracked.update(read(replay/'integrity.json')['consumed'])
        rows=observations(endpoints)
        require(len(rows)==200 and len(endpoints)==400 and len({r['invocation_index'] for r in rows})==20, 'selected corpus mismatch')
        require(all(sum(r['variant']==v for r in rows)==100 for v in ('A','C')), 'variant corpus mismatch')
        delivery_integrity=consume(deliveries[0]/'integrity.json')
        prepared=[Path(p) for p in delivery_integrity['before'] if (Path(p)/'v4/A/probe-to-source.json').exists()]
        require(len(prepared)==1,'ambiguous source provenance')
        expected={str(Path(root)/name):digest for root,inv in delivery_integrity['before'].items() for name,digest in inv.items()}
        def bound_consume(path, digest=None):
            if path.is_relative_to(prepared[0]):
                require(str(path) in expected, 'unrecorded preparation input: '+str(path))
                require(digest is None or digest==expected[str(path)], 'preparation provenance mismatch')
                digest=expected[str(path)]
            return consume(path,digest)
        source=source_comparison(prepared[0],qualification,bound_consume)
        boundaries=source_boundaries(prepared[0],bound_consume)
        write(output/'source-boundaries.json',boundaries)
        (output/'source-boundaries.md').write_text(boundary_report(boundaries))
        summary=summarize(rows); ranks=ranking(summary)
        selected=selections(rows,consume(startup/'selected-timelines.json'))
        comparisons=selection_comparison(selected,ranks['order'])
        for name,value in [('observations',rows),('endpoint-mappings',endpoints),('distributions',summary),('rankings',ranks),
                           ('selected-timelines',selected),('selection-comparison',comparisons),('source-comparison',source),
                           ('source-citations',consume(startup/'source-citations.json')),('raw-citations',consume(startup/'raw-citations.json'))]:
            write(output/(name+'.json'),value)
        lines=['# Retained pre-decode drill-down','',
               'Complete: 20 measured v4 invocations; 200 invocation-local observations; 400 endpoint mappings. Durations are nanoseconds. Pixel and metadata pre-decode intervals and spans agree exactly before deduplication. Both original harness latencies and endpoint references remain preserved.', '',
               '| Disjoint phase set | C median share | C p95 share | C median ns | C p95 ns | A median ns |',
               '|---|---:|---:|---:|---:|---:|']
        for name in ranks['order']:
            c,a=ranks['C'][name],ranks['A'][name]
            lines.append(f"| {name} | {c['share']['median']:.6f} | {c['share']['p95']:.6f} | {c['duration_ns']['median']} | {c['duration_ns']['p95']} | {a['duration_ns']['median']} |")
        pooled={r['variant']:r for r in summary if r['block']=='pooled'}
        lines += ['', '| Inclusive phase union | C median ns | C p95 ns | A median ns | A p95 ns |',
                  '|---|---:|---:|---:|---:|']
        for name in sorted(pooled['C']['phases']):
            def cell(variant, metric):
                phase=pooled[variant]['phases'][name]
                value=phase['union_ns']
                return str(value[metric]) if value else str(phase['availability_counts'])
            lines.append(f"| {name} | {cell('C','median')} | {cell('C','p95')} | {cell('A','median')} | {cell('A','p95')} |")
        lines += ['', '| Parent outside nested spans | C median ns | C p95 ns | A median ns | A p95 ns |',
                  '|---|---:|---:|---:|---:|']
        for name in PARENTS:
            def cell(variant, metric):
                value=pooled[variant]['parent_outside_nested'][name]
                return str(value[metric]) if value else 'unavailable / absent by design'
            lines.append(f"| {name} | {cell('C','median')} | {cell('C','p95')} | {cell('A','median')} | {cell('A','p95')} |")
        lines += ['', 'Every boundary splits the interval into disjoint active-phase sets, including uncovered time. Each group uses zero for otherwise valid observations without that group. Inclusive phase unions/spans are retained separately and are non-additive. Parent time outside nested validation/acquisition is calculated by interval subtraction per observation, then summarized. Missing phases remain unavailable; A generation phases are absent by design.', '',
                  '| Selection | Variant | Count | Dominant group by median share |', '|---|---|---:|---|']
        for c in comparisons:
            lines.append(f"| {c['selection']} | {c['variant']} | {c['observations']} | {c['order'][0]} |")
        c_selections=[c for c in comparisons if c['variant']=='C']
        dominant=ranks['order'][0]
        agreement=all(c['order'][0]==dominant for c in c_selections)
        lines += ['', f"C's dominant group is {dominant}. All retained C selection classes agree with the pooled median priority: {agreement}. Selection distributions are descriptive and overlapping, not independent samples.", '',
                  'Source comparison: '+source['limitation'], '',
                  'The source citations map probes to frozen functions; source-comparison.json retains the complete recorded U/T diff and literal v3→v4 anchors. These establish measured boundary locations, not durations of intervening uninstrumented calls. See source-boundaries.md for the call chain.', '',
                  'Recommendation: the narrowest next investigation is the runtime-validation portion of generation validation, supported by its pooled median and selected tail priority. A future separately approved measurement would need begin/end boundaries for protected-tree traversal, manifest reading/parsing, file-attribute checks, file reads/hash computation and final inventory traversal. Matched A/C scheduler switch/wakeup and blocking evidence over those boundaries would distinguish running validation work from runnable delay and non-runnable waits. The secondary helper-preparation hypothesis needs boundaries for launcher checks/start, scope discovery/limit verification, gate release and readiness receive; inspect transport needs separate write/read boundaries. These boundaries would separate hypotheses; no duration is assigned to any uninstrumented call, hashing, launcher operation or scheduling.', '',
                  'These are retained elapsed measurements, not causes of the separate failed qualification or predicted savings. Source equivalence under private tracing changes does not establish run, runtime or binary equivalence. Overhead is not subtracted; no experiment, qualification rerun or D reassessment was performed.', '',
                  'Artifacts: [observations](observations.json), [endpoint mappings](endpoint-mappings.json), [pooled/per-block distributions](distributions.json), [rankings](rankings.json), [selected timelines](selected-timelines.json), [selection comparisons](selection-comparison.json), [source comparison](source-comparison.json), [source citations](source-citations.json), [raw citations](raw-citations.json), [offline replay](replay/REPORT.md). Distributions include counts, minimum, median, nearest-rank p95 and maximum.']
        (output/'REPORT.md').write_text('\n'.join(lines)+'\n')
        result.update(status='complete',observations=len(rows),endpoint_mappings=len(endpoints),invocations=20)
    except (OSError,ValueError,KeyError,TypeError,IndexError,StopIteration) as error:
        result['failure']=str(error)
    finally:
        try:
            require(all(o.inventory(p)==before.get(str(p)) for p in inputs), 'input drift')
            require(all(o.digest(Path(p))==h for p,h in tracked.items()), 'consumed input drift')
        except (OSError,ValueError) as error:
            result.update(status='blocked',integrity_failure=str(error))
        if result['status']!='complete':
            (output/'REPORT.md').write_text('# Blocked pre-decode assessment\n\n'+str(result)+'\n\nPartial rankings are not verified conclusions.\n')
            # No provisional ranking file can be mistaken for verified output.
            if (output/'rankings.json').exists(): write(output/'rankings.json',dict(status='blocked'))
        write(output/'assessment.json',result)
        write(output/'integrity.json',dict(before=before,consumed=tracked,passed=result['status']=='complete'))
        (output/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
        o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('startup','qualification','output'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    result=report(args.startup,args.qualification,args.output)
    print(result)
    sys.exit(result['status']!='complete')
