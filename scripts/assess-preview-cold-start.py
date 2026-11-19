#!/usr/bin/env python3
"""Select a next cold-start action from retained evidence; never execute workloads."""
import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('cold_predecode', Path(__file__).with_name('report-preview-predecode.py'))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
b, o = p.b, p.o
read, write, require = p.read, p.write, p.require

BLOCKS = {
    'owner_initialization': ('generation_validation', 'generation_acquisition', 'runtime_validation'),
    'helper_preparation': ('helper_prepare',),
    'inspection_decode': ('source_capture', 'inspect_exchange_including_transport', 'decode_exchange_including_transport'),
    'transaction_completion': ('oneshot_ack', 'helper_exit', 'reusable_completion_ack', 'effective_cleanup'),
    'thumbnail_storage': ('store_raster', 'store_raster_delegate', 'thumbnail_store', 'png_serialization', 'storage_commit'),
    'result_delivery': ('enqueue_call', 'callback_execution', 'apply_result', 'changed_emission', 'harness_execution', 'metadata_format', 'memory_insert'),
}


def rows(endpoints):
    """Keep endpoint-local inclusive spans and unions; never sum categories."""
    p.observations(endpoints)  # validates the two endpoint identities and predecode agreement
    seen, result = set(), []
    for row in endpoints:
        require(row['fixture']=='3200x2400.png' and not row.get('warmup',False)
                and row.get('mode','v4')=='v4', 'foreign population')
        key = row['invocation_index'], row['observation'], row['endpoint']
        require(key not in seen and row['variant'] in ('A', 'C'), 'duplicate/foreign endpoint')
        seen.add(key)
        left, right = row['trace_origin']['ns'], row['delivery']['ns']
        require(row['delivery']['observation'] == row['observation'], 'endpoint identity mismatch')
        spans = [dict(x, operation=x['phase']) for x in row['v3_timeline']
                 if x['role'] in ('demand', 'service_control')]
        spans += row['operations']
        blocks = {}
        for name, operations in BLOCKS.items():
            selected = [x for x in spans if x['operation'] in operations and x['start'] < right and x['stop'] > left]
            require(all(x['stop'] >= x['start'] for x in selected), 'reversed span')
            coverage = b.g.g.intervals(left, right, selected)
            blocks[name] = dict(spans=selected, **coverage,
                inclusive_ns=sum(min(right,x['stop'])-max(left,x['start']) for x in selected),
                availability='observed' if selected else 'unavailable; not zero')
        result.append(dict(population='matched-overhead/v4/3200x2400.png/measured',
            **{k:row[k] for k in ('variant','block','fixture','invocation_index','observation','endpoint','harness_latency_ns')},
            trace_origin=row['trace_origin'], delivery=row['delivery'], blocks=blocks,
            missing_evidence=row['unavailable'], coarse=row['coarse']))
    return result


def summarize(observations):
    groups = defaultdict(list)
    for row in observations:
        groups[row['population'],row['variant'],row['endpoint'],row['block']].append(row)
    result = []
    for (population,variant,endpoint,block), rs in sorted(groups.items(),key=lambda x:str(x[0])):
        result.append(dict(population=population,variant=variant,endpoint=endpoint,block=block,count=len(rs),
            blocks={name:dict(observed=sum(r['blocks'][name]['availability']=='observed' for r in rs),
                union_ns=b.stats([r['blocks'][name]['covered_ns'] for r in rs if r['blocks'][name]['spans']])
                if any(r['blocks'][name]['spans'] for r in rs) else None) for name in BLOCKS}))
    return result


def ranking(summary):
    # Descriptive priority only. Presence, source differences and tails cannot by
    # themselves identify removable work or an implementation with preserved contracts.
    return sorted(BLOCKS, key=lambda name:(-sum(c['blocks'][name]['union_ns']['median']
        for c in summary if c['variant']=='C' and c['blocks'][name]['union_ns']), name))


def run(qualification, startup, predecode, validation, hash_assessment, predecode_verification,
        validation_verification, hash_verification, output):
    inputs = [x.resolve() for x in (qualification,startup,predecode,validation,hash_assessment)]
    qualification,startup,predecode,validation,hash_assessment = inputs
    output = output.resolve()
    o.fresh(output,*inputs)
    tracked = {str(Path(__file__).resolve()):o.digest(Path(__file__)),
               str(Path(__file__).resolve().parents[1]/'tests/test_preview_cold_start.py'):
               o.digest(Path(__file__).resolve().parents[1]/'tests/test_preview_cold_start.py')}
    result = dict(status='blocked', outcome=None, new_measurements=False)
    def consume(path, expected=None):
        path = Path(path)
        actual = o.digest(path)
        require(expected is None or actual==expected, 'input identity mismatch: '+str(path))
        require(str(path) not in tracked or tracked[str(path)]==actual, 'input drift: '+str(path))
        tracked[str(path)] = actual
        if path.suffix=='.json': return read(path)
        data=path.read_bytes()
        try: return data.decode()
        except UnicodeDecodeError: return data
    def sealed(root):
        manifest = consume(root/'seal.json')
        o.check_output(root)
        for name, digest in manifest.items(): consume(root/name,digest)
        require(consume(root/'assessment.json')['status']=='complete', 'blocked input')
    try:
        for root in inputs[1:]: sealed(root)
        for root,verification,key in ((predecode,predecode_verification,'seal_sha256'),
                (validation,validation_verification,'audit_seal'),(hash_assessment,hash_verification,'assessment_seal')):
            record=consume(verification)
            require(record['status']=='passed' and record[key]==o.digest(root/'seal.json'), 'verification binding mismatch')
        # Bind evidence actually used, not unrelated scheduler pilot recordings or
        # mutable checkout tools incidentally inventoried by historical reporters.
        history = {}
        for root in (startup,predecode):
            integrity=consume(root/'integrity.json')
            require(integrity['passed'], 'failed retained integrity')
            history[str(root)] = integrity
        require(str(qualification) in history[str(predecode)]['before'] and
                str(startup) in history[str(predecode)]['before'], 'qualification/startup provenance mismatch')
        require(history[str(predecode)]['before'][str(startup)]==o.inventory(startup), 'startup inventory drift')
        freeze=consume(qualification/'freeze.json')
        require(all(consume(qualification/'post-run-identity-checks.json').values()), 'qualification identity failure')
        for variant,inv in freeze['source_inventories'].items():
            for name,digest in inv.items(): consume(qualification/variant/'source'/name,digest)
        old=history[str(predecode)]['before'][str(qualification)]
        qualification_text=consume(qualification/'ASSESSMENT.md',old['ASSESSMENT.md'])
        require('78 pass' in qualification_text and '142.340' in qualification_text and '140.619' in qualification_text,
                'qualification result mismatch')
        source=consume(predecode/'source-comparison.json')
        require(source['status']=='equivalent' and not source['differences'] and not source['reconstruction_residual'], 'A source relationship unavailable')
        prepared=Path(source['chain'][0]).parents[2]
        expected=history[str(predecode)]['consumed']
        origin_root=Path(source['chain'][2]).parents[1]
        def frozen(path,digest=None):
            if str(path) not in expected and path.is_relative_to(origin_root):
                seal_path=origin_root/'seal.json'
                manifest=consume(seal_path,expected[str(seal_path)])
                name=str(path.relative_to(origin_root))
                require(name in manifest, 'unsealed original source')
                expected[str(path)]=manifest[name]
            require(str(path) in expected, 'unrecorded frozen source: '+str(path))
            require(digest is None or digest==expected[str(path)], 'frozen identity mismatch')
            return consume(path,expected[str(path)])
        replayed=p.source_comparison(prepared,qualification,frozen)
        require(json.loads(json.dumps(replayed))==source, 'frozen source replay mismatch')
        # Both variants' source inventories must agree with the completed overhead
        # provenance before reviewing behavior. Preserve exact differences, including tracing.
        import difflib
        def source_text(path,digest):
            frozen(path,digest)
            return path.read_text()
        sources, diffs = {}, []
        for variant in ('A','C'):
            inv=frozen(prepared/'v4'/variant/'source-inventory.json')['source']
            sources[variant]={n:source_text(prepared/'v4'/variant/'source'/n,h) for n,h in inv.items()}
        for name in sorted(sources['A'].keys() | sources['C'].keys()):
            a,c=sources['A'].get(name,''),sources['C'].get(name,'')
            if a!=c: diffs.append(dict(file=name,diff=''.join(difflib.unified_diff(a.splitlines(True),c.splitlines(True),fromfile='A/'+name,tofile='C/'+name))))
        origin=Path(frozen(prepared/'manifest.json')['inputs']['v3'])
        preparation=frozen(origin/'preparation.json')
        require(preparation['equivalence']['C']['source']==[], 'C uninstrumented equivalence unavailable')
        cu=preparation['pairs']['CU']['source']
        require(cu==freeze['source_inventories']['C'], 'C qualification/source mismatch')
        for name,digest in cu.items(): frozen(origin/'CU/source'/name,digest)
        ct={name:source_text(origin/'CT/source'/name,digest).encode()
            for name,digest in preparation['pairs']['CT']['source'].items()}
        c3=frozen(prepared/'v3/C/source-inventory.json')['source']
        matched={name:source_text(prepared/'v3/C/source'/name,digest).encode() for name,digest in c3.items()}
        normalize=b.v3.overhead.normalized
        require({k:normalize(v) for k,v in ct.items()}=={k:normalize(v) for k,v in matched.items()}, 'C matched-v3 mismatch')
        anchors=frozen(prepared/'anchor-review.json')['C']
        replay=o.prep.replay({'source/'+k:v for k,v in ct.items()},[x for x in anchors if x['file'].startswith('source/')])
        require({k:normalize(v) for k,v in replay.items()}==
                {'source/'+k:normalize(v.encode()) for k,v in sources['C'].items()}, 'C v4 anchor mismatch')
        endpoints=consume(startup/'observations.json')
        require(endpoints==consume(predecode/'endpoint-mappings.json'), 'endpoint population mismatch')
        execution=Path(endpoints[0]['delivery']['file']).parent.parent
        overhead_assessment=frozen(execution/'assessment.json')
        require(overhead_assessment['status']=='complete', 'overhead comparison incomplete')
        require(frozen(execution/'statistics.json')==consume(startup/'matched-overhead-context.json'),
                'overhead statistics provenance mismatch')
        observed=rows(endpoints)
        require(len(observed)==400, 'retained population mismatch')
        for root in (startup,predecode):
            for item in consume(root/'raw-citations.json'):
                path=Path(item['file']); text=consume(path,item['sha256']).splitlines()
                if 'line' in item and 'text' in item: require(text[item['line']-1]==item['text'],'raw citation mismatch')
        # Independently verified validation and hashing remain separate populations.
        for root in (validation,hash_assessment):
            identity=consume(root/'inputs.json')
            for name,digest in identity.get('identities',{}).items(): consume(Path(name),digest)
        decision=consume(hash_assessment/'decision.json')
        require('defer' in decision['recommendation'], 'hash assessment changed')
        summary=summarize(observed)
        for name,value in [('observations',observed),('block-summaries',summary),('descriptive-ranking',ranking(summary)),
                ('selected-tails',b.selections(endpoints)),('source-differences',diffs),('source-relationship',source),
                ('raw-citations',consume(startup/'raw-citations.json')),('source-citations',consume(startup/'source-citations.json')),
                ('validation-context',consume(validation/'distributions.json')),('hash-decision',decision)]:
            write(output/(name+'.json'),value)
        (output/'qualification.md').write_text(qualification_text)
        (output/'REPORT.md').write_text(report_text(summary,observed))
        result.update(status='complete',outcome='Evidence insufficient',endpoints=len(observed))
    except (OSError,ValueError,KeyError,TypeError,IndexError,AttributeError) as error:
        result['failure']=str(error)
    finally:
        try:
            require(all(o.digest(Path(name))==digest for name,digest in tracked.items()),'consumed input drift')
        except (OSError,ValueError) as error: result.update(status='blocked',outcome=None,integrity_failure=str(error))
        if result['status']!='complete':
            (output/'REPORT.md').write_text('# Blocked cold-start assessment\n\n'+str(result)+'\nNo optimization selected.\n')
        write(output/'assessment.json',result)
        write(output/'integrity.json',dict(consumed=tracked,passed=result['status']=='complete'))
        (output/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
        o.seal(output)
    return result


def report_text(summary,observed):
    lines=['| Endpoint | Block | Work | A median ms | C median ms |',
           '|---|---:|---|---:|---:|']
    for c in summary:
        if c['variant']!='C': continue
        a=next(x for x in summary if x['variant']=='A' and x['endpoint']==c['endpoint'] and x['block']==c['block'])
        for name in BLOCKS:
            def cell(row):
                value=row['blocks'][name]['union_ns']
                return f"{value['median']/1e6:.3f}" if value else 'unavailable'
            lines.append(f"| {c['endpoint']} | {c['block']} | {name} | {cell(a)} | {cell(c)} |")
    table='\n'.join(lines)
    return '''# Remaining cold-start decision

Qualification remains failed: 78/80 gates pass. Large-PNG startup p95 fails for
pixels and metadata; metadata is 142.340 ms against 140.619 ms allowed
(A-fixed 127.835 ms). Thresholds and historical evidence are unchanged.

A-fixed source equivalence is replayed through the frozen private tracing chain.
Both A/C source inventories and literal source differences are retained before
behavior comparison. This establishes source relationships, not timing equivalence.

| Work | Frozen behavior and interpretation |
|---|---|
| Owner initialization | C constructs RuntimeOwner and validates its generation before demand; A validates within helper preparation. Validation is shared work with changed ordering. No repeated validation in an unchanged owner/generation lifetime is demonstrated. |
| Helper preparation | Both launch, discover/limit scopes, release the gate and await readiness. C additionally resolves a generation lease. Unmarked launch/readiness work remains inseparable from scheduling and blocking. |
| Inspection/decode | Both capture and inspect before decoding. Exchange spans include transport; no evidence isolates removable decode or transport work. |
| Transaction completion | A acknowledges and validates helper exit/cleanup; C acknowledges reusable completion and may retain the session. Missing C cleanup is not zero cost or a contract violation. |
| Thumbnail storage | Both run conditional raster storage, PNG serialization and commit. Nested store scopes are non-additive; branch skips remain explicit in retained endpoint evidence. |
| Result delivery | Both queue, apply and emit results; worker metadata may overlap callbacks. Enqueue-to-callback elapsed time is not pure queue residence. |

[Per-endpoint intervals](observations.json) and [per-block summaries](block-summaries.json)
retain inclusive spans, clipped unions, missing boundaries and concurrency for both
endpoints. The descriptive ranking uses summed C block median unions only as an
ordering device, never as elapsed cost or predicted savings. [Selected tails](selected-tails.json)
are selected within each original A/C traced run; their coarse intervals and full
operations remain available. The pre-decode assessment identifies validation as its
strongest measured group; the later validation population resolves read/hash work.
These populations cannot explain the separate qualification failure. No quantiles
are subtracted and no overhead correction is applied.

[Source differences](source-differences.json), [source relationship](source-relationship.json),
[source citations](source-citations.json) and [raw citations](raw-citations.json)
bind this review to frozen control flow and retained observations. Historical
reporter checkout-tool inventories and the unrelated B scheduler pilot are not
revalidated as consumed runtime evidence; no A/C scheduling attribution uses them.
Actual consumed files are listed and rehashed in integrity.json.

Hashing remains deferred under [its assessment](hash-decision.json): mixed block
directions and all differences below the 5 ms planning threshold do not establish
an upper bound. Initial standby deferral remains deferred under the failed D pilot;
this comparison adds no evidence to reverse that decision. Neither is ranked as a
supported implementation candidate.

The highest-priority unresolved remaining boundary is helper preparation after
lease/validation resolution and before readiness. Frozen source includes launcher
checks, process start, scope discovery/limit verification, gate release and readiness
receive. Its elapsed interval cannot distinguish running preparation work from
runnable delay, non-runnable waits or trace emission. The minimum discriminating
observation would split those existing substeps and correlate the same A/C
invocation, observation, worker and generation with scheduler/blocking boundaries.
It would need its own approved protocol. No experiment is prepared or executed.
No optimization is selected; production contracts, integrity checks, leases,
cleanup, APIs and installed packages remain unchanged.

''' + table + '\n\n**Evidence insufficient**\n'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('qualification','startup','predecode','validation','hash-assessment','predecode-verification',
                 'validation-verification','hash-verification','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    result=run(**vars(parser.parse_args()))
    print(result)
    sys.exit(result['status']!='complete')
