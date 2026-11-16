#!/usr/bin/env python3
"""Independent stdlib-only evidence verification; imports no runner or reporter."""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def require(condition,message):
    if not condition: raise ValueError(message)
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())
def inventory(root):
    require(root.is_dir() and root==root.resolve(),'invalid evidence directory')
    result={}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(),'evidence symlink')
        if path.is_file(): result[str(path.relative_to(root))]=digest(path)
    return result

def seal(root):
    require(inventory(root)==dict(read(root/'seal.json'),**{'seal.json':digest(root/'seal.json')}),'seal mismatch')

def protocol():
    combinations=[(variant,arm) for arm in ('baseline','instrumented','captured') for variant in ('A','C')]
    rows=[]
    for block in (None,*range(5)):
        order=combinations if block is None else combinations[block:]+combinations[:block]
        if block is not None and block%2: order=order[::-1]
        rows.extend(dict(variant=v,arm=a,block=block,warmup=block is None,observations=1 if block is None else 5,
                         fixture='3200x2400.png') for v,a in order)
    return rows

def distribution(values):
    values=sorted(values)
    require(values and all(math.isfinite(x) for x in values),'invalid distribution')
    return dict(count=len(values),minimum=values[0],median=statistics.median(values),p95=values[math.ceil(.95*len(values))-1],maximum=values[-1])

def union(parts):
    result=[]
    for left,right in sorted((l,r) for l,r in parts if l<r):
        if result and left<=result[-1][1]: result[-1][1]=max(right,result[-1][1])
        else: result.append([left,right])
    return result

def raw_bindings(account):
    stacks=defaultdict(list)
    for event in account['records']:
        ref=event['raw']; text=Path(ref['file']).read_text().splitlines()[ref['line']-1]
        require(text==ref['text'] and text.startswith('HELPER_STARTUP '),'raw helper citation mismatch')
        original=json.loads(text[15:])
        for key in ('ns','service','observation','job','worker','preparation','request_generation','span','parent'):
            if isinstance(original[key],str): original[key]=int(original[key])
        require(original=={k:v for k,v in event.items() if k!='raw'},'raw helper record mismatch')
        require(event['invocation']==account['population']['invocation'],'invocation identity mismatch')
        stack=stacks[event['pid'],event['tid']]
        if event['edge']=='begin':
            require(event['parent']==(stack[-1]['span'] if stack else None),'independent thread nesting mismatch')
            require(event['outcome']=='unavailable','independent entry outcome mismatch');stack.append(event)
        else:
            require(stack and stack[-1]['span']==event['span'],'independent boundary mismatch')
            begin=stack.pop()
            require(event['outcome'] in ('returned','exception') and event['ns']>=begin['ns'] and
                    all(event[k]==begin[k] for k in original if k not in ('ns','edge','outcome')),'independent exit identity mismatch')
    require(not any(stacks.values()),'independent unclosed boundary')
    for span in account['spans']:
        require(span['source_citations'],'independent source probe unavailable')
        for citation in span['source_citations']:
            path=Path(citation['file'])
            require(digest(path)==citation['sha256'] and path.read_text().splitlines()[citation['line']-1]==citation['text'] and
                    '"'+span['operation']+'"' in citation['text'],'independent operation source mismatch')
    for window in account['windows']:
        binding=window['lifecycle_binding']; legacy=binding['legacy']; event=window['begin']
        require(all(legacy[edge].get(k)==(event[k] or 0) for edge in ('begin','end') for k in
                    ('pid','tid','service','observation','job','worker','preparation')),'independent lifecycle identity mismatch')
        require(binding['supplemental_after_legacy_ns']==max(0,window['end']['ns']-legacy['stop']),
                'independent lifecycle interval relationship mismatch')
        for edge in ('begin','end'):
            ref=legacy[edge]; path=Path(ref['file']).with_suffix('.stderr')
            line=path.read_text().splitlines()[ref['line']-1]
            require(line.startswith('TRACE ') and json.loads(line[6:])=={k:v for k,v in ref.items() if k not in ('file','line')},
                    'independent legacy raw citation mismatch')


def arithmetic(account):
    raw_bindings(account)
    spans=account['spans']
    for span in spans:
        start,stop=span['start'],span['stop']
        require(stop-start==span['inclusive_ns'],'inclusive interval mismatch')
        children=[s for s in spans if s['pid']==span['pid'] and s['parent']==span['span']]
        coverage=union((max(start,s['start']),min(stop,s['stop'])) for s in children)
        require(coverage==span['child_union'],'child union mismatch')
        cursor=start; exclusive=[]
        for left,right in coverage:
            if cursor<left: exclusive.append([cursor,left])
            cursor=right
        if cursor<stop: exclusive.append([cursor,stop])
        require(exclusive==span['exclusive_intervals'] and sum(r-l for l,r in exclusive)==span['exclusive_ns'],'exclusive interval mismatch')
        sched=span['scheduler']
        if sched['available']:
            intervals=sched['intervals']; cursor=start; totals=defaultdict(int)
            for interval in intervals:
                require(interval['start_ns']==cursor and cursor<interval['stop_ns']<=stop,'scheduler interval gap/overlap')
                totals[interval['state']]+=interval['stop_ns']-cursor; cursor=interval['stop_ns']
            require(cursor==stop and all(totals[state]==value for state,value in sched['totals'].items()) and
                    totals['unknown']==0 and sum(totals.values())==stop-start,'scheduler reconciliation mismatch')
    for window in account['windows']:
        start,stop=window['begin']['ns'],window['end']['ns']
        merged=union((max(start,s['start']),min(stop,s['stop'])) for s in window['spans'])
        require(merged==window['clipped_union'] and sum(r-l for l,r in merged)==window['covered_ns'],'preparation union mismatch')
        require(window['lifecycle_binding']['classification'] in ('setup','demand','standby') and
                window['lifecycle_binding']['runtime_generation'] is None,'lifecycle classification mismatch')

def verify(evidence):
    seal(evidence); assessment=read(evidence/'assessment.json'); integrity=read(evidence/'integrity.json')
    require(integrity['passed'] and all(integrity['checks'].values()),'input/tool integrity failed')
    for name,expected in integrity['before'].items():
        require(inventory(Path(name))==expected,'consumed inventory drift: '+name)
        seal(Path(name))
    for name,expected in integrity['tools'].items():
        require(digest(evidence/'tools'/Path(name).name)==expected,'tool snapshot drift')
    # The existing independent static checker imports no recipe or execution code.
    packages=[Path(name) for name in integrity['before'] if (Path(name)/'probe-to-source.json').exists()]
    require(len(packages)==1,'missing/ambiguous preparation')
    file='verify-preview-helper-startup-host.py' if (packages[0]/'host-rebind.json').exists() else 'verify-preview-helper-startup.py'
    spec=importlib.util.spec_from_file_location('static_helper_verification',ROOT/'scripts'/file)
    checker=importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)
    packages=[Path(name) for name in integrity['before'] if (Path(name)/'probe-to-source.json').exists()]
    require(len(packages)==1,'missing/ambiguous preparation')
    package=packages[0]; checked=checker.verify(package)
    require(read(package.parent/(package.name+'-independent.json'))==checked,'independent preparation binding mismatch')
    require(read(package/'protocol.json')['schedule']==protocol(),'schedule mismatch')
    launched=assessment['launched']
    require(0<=launched<=36 and read(evidence/'unexecuted-schedule.json')==protocol()[launched:],'unexecuted schedule mismatch')
    require(assessment['unexecuted']==36-launched,'remaining invocation mismatch')
    for index,saved in enumerate(assessment['invocations']):
        require(saved['index']==index and saved['entry']['invocation']==protocol()[index],'executed schedule mismatch')
    require(len(assessment['invocations'])==launched,'invocation ledger mismatch')
    for name in ('preflight-final-checks.json','execution-final-checks.json'):
        if (evidence/name).exists(): require(all(c['passed'] for c in read(evidence/name).values()),'final cleanup failed')
    if (evidence/'partial-accounting.json').exists():
        for account in read(evidence/'partial-accounting.json'): arithmetic(account)
    if (evidence/'endpoints.json').exists():
        endpoints=read(evidence/'endpoints.json'); accounts=read(evidence/'accounting.json')
        measured=[e for e in endpoints if not e['warmup']]
        require(len(measured)==300 and len(endpoints)==312 and len(accounts)==36,'report populations mismatch')
        grouped=defaultdict(list)
        for endpoint in measured:
            sample=accounts[endpoint['invocation_index']]['original_samples'][endpoint['observation']-1]
            require(endpoint['harness_latency_ns']==sample['first_ms' if endpoint['endpoint']=='pixels' else 'final_ms']*1e6,'endpoint latency mismatch')
            for block in ('pooled',endpoint['block']):
                grouped[endpoint['variant'],endpoint['arm'],endpoint['endpoint'],block].append(endpoint['harness_latency_ns'])
        summary=read(evidence/'distributions.json')
        require(len(summary)==len(grouped),'distribution population mismatch')
        for cell in summary:
            require(cell['latency_ns']==distribution(grouped[cell['variant'],cell['arm'],cell['endpoint'],cell['block']]),'distribution mismatch')
        for effect in read(evidence/'effects.json'):
            values=[]
            for block in range(5):
                cell={c['arm']:c['latency_ns']['median'] for c in summary if
                      (c['variant'],c['endpoint'],c['block'])==(effect['variant'],effect['endpoint'],block)}
                values.append(cell[effect['right']]-cell[effect['left']])
            require(effect['signed_block_median_difference_ns']==(statistics.median(values) if effect['block']=='block_medians' else values[effect['block']]),'block median difference mismatch')
        for account in accounts: arithmetic(account)
    if assessment['status']=='blocked':
        require(assessment.get('failure') or assessment.get('integrity_failure'),'blocked result lacks reason')
        if launched==0:
            require(not (evidence/'observations').exists() and not any(evidence.glob('*/A/build')),'blocked preflight launched work')
    return dict(status='passed',outcome=assessment['status'],evidence_seal=digest(evidence/'seal.json'),
                launched=launched,unexecuted=36-launched,imports_runner=False,imports_reporter=False,
                verifier_sha256=digest(Path(__file__)),
                original_launched=assessment.get('original_launched',launched),
                original_unexecuted=assessment.get('original_unexecuted',36-launched))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('evidence',type=Path)
    args=parser.parse_args()
    try: print(json.dumps(verify(args.evidence.absolute()),indent=2))
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps(dict(status='blocked',failure=str(error)),indent=2));sys.exit(1)
