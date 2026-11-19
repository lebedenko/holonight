#!/usr/bin/env python3
"""Independent static verification of an explicit helper-startup host revision."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())
def require(condition,message):
    if not condition: raise ValueError(message)
def inventory(root):
    require(root.is_dir(),'missing tree')
    result={}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(),'symlink')
        if path.is_file(): result[str(path.relative_to(root))]=digest(path)
    return result

def seal(root):
    expected=read(root/'seal.json')
    require(inventory(root)==dict(expected,**{'seal.json':digest(root/'seal.json')}),'seal mismatch')


HOST_PATHS=('/etc/ld.so.cache','/usr/lib/ld-linux-x86-64.so.2','/usr/lib/libc.so.6','/usr/lib/libm.so.6')


def host_binding(root):
    binding=read(root/'host-rebind.json'); original=Path(binding['original'])
    require(original==original.resolve() and not root.is_relative_to(original) and not original.is_relative_to(root),
            'overlapping host revision')
    seal(original)
    require(digest(original/'seal.json')==binding['original_seal'],'original preparation seal mismatch')
    record=read(original.parent/(original.name+'-independent.json'))
    require(record['status']=='passed' and record['preparation_seal']==binding['original_seal'] and
            digest(original.parent/(original.name+'-independent.json'))==binding['original_verification_sha256'],
            'original independent binding mismatch')
    old=read(original/'integrity.json'); current=read(root/'integrity.json')
    require(old['passed'] and all(old['checks'].values()),'original preparation integrity blocked')
    require(set(binding['changes'])==set(HOST_PATHS),'unexpected host revision paths')
    expected=dict(old['consumed'])
    for name,change in binding['changes'].items():
        require(set(change)=={'old','new'} and change['old']==expected[name] and change['new']!=change['old'],
                'invalid host revision mapping')
        require(digest(Path(name))==change['new'],'revised host input drift: '+name)
        expected[name]=change['new']
    for name,sha in binding['tools'].items():
        require(Path(name).name in ('rebind-preview-helper-startup.py','verify-preview-helper-startup-host.py') and
                Path(name).parent==Path(__file__).resolve().parent,'unexpected revision tool')
        require(digest(Path(name))==sha and digest(root/'tools'/Path(name).name)==sha,'revision tool drift')
        expected[name]=sha
    require(len(binding['tools'])==2 and current['consumed']==expected,'revision consumed inventory mismatch')
    require(current['before']==dict(old['before'],**{str(original):inventory(original)}),'revision source inventory mismatch')
    for name in ('protocol.json','anchors.json','inputs.json','provenance.json','fixtures.json','source-comparison.json'):
        require((root/name).read_bytes()==(original/name).read_bytes(),'revision changed frozen '+name)
    return binding


def verify(root):
    seal(root)
    binding=host_binding(root)
    require(read(root/'assessment.json')['status']=='prepared','blocked preparation')
    integrity=read(root/'integrity.json'); require(integrity['passed'] and all(integrity['checks'].values()),'blocked integrity')
    for name,value in integrity['consumed'].items(): require(digest(Path(name))==value,'consumed input drift: '+name)
    for name,expected in integrity['before'].items(): require(inventory(Path(name))==expected,'input inventory drift')
    inputs=read(root/'inputs.json'); prepared=Path(inputs['prepared']); evidence=Path(inputs['evidence'])
    seal(evidence); seal(prepared)
    record=read(Path(inputs['verification']))
    require(record['status']=='passed' and record['assessment_seal']==digest(evidence/'seal.json'),'verification mismatch')
    for name,value in read(evidence/'integrity.json')['consumed'].items():
        path=Path(name)
        if not path.is_absolute(): path=Path(__file__).resolve().parents[1]/path
        effective=binding['changes'][str(path)]['new'] if str(path) in binding['changes'] else value
        if str(path) in binding['changes']: require(binding['changes'][str(path)]['old']==value,'historical host identity mismatch')
        require(integrity['consumed'].get(str(path))==effective and digest(path)==effective,'cold-start binding drift: '+name)
    recipe=ast.parse((root/'tools/prepare-preview-helper-startup.py').read_text())
    headers=[node.value for node in recipe.body if isinstance(node,ast.Assign) and
             any(isinstance(t,ast.Name) and t.id=='HEADER' for t in node.targets)]
    require(len(headers)==1,'header snapshot missing'); header=ast.literal_eval(headers[0]).encode()
    anchors=read(root/'anchors.json'); maps=[]; trees=0
    for mode in ('baseline','instrumented'):
        for variant in ('A','C'):
            target=root/mode/variant; original=prepared/'v4'/variant
            require((target/'trace.h').read_bytes()==(original/'trace.h').read_bytes()+
                    (header if mode=='instrumented' else b''),'header bytes mismatch')
            expected_diffs=[]
            for group in ('source','harness-source'):
                require(read(target/'source-inventory.json')[group]==inventory(target/group),'inventory mismatch')
                require(set(inventory(original/group))==set(inventory(target/group)),'source set mismatch')
                for relative in inventory(original/group):
                    name=group+'/'+relative; old=(original/name).read_bytes(); actual=(target/name).read_bytes()
                    expected=old.replace(str(original/'trace.h').encode(),str(target/'trace.h').encode())
                    edits=[a for a in anchors if a['mode']==mode and a['variant']==variant and a['file']==name]
                    for edit in edits:
                        a,b=edit['anchor'].encode(),edit['replacement'].encode()
                        require(expected.count(a)==1,'missing/duplicate forward anchor'); expected=expected.replace(a,b,1)
                    require(actual==expected,'overlay mismatch')
                    reverse=actual
                    for edit in reversed(edits):
                        a,b=edit['anchor'].encode(),edit['replacement'].encode()
                        require(reverse.count(b)==1,'missing/duplicate reverse anchor'); reverse=reverse.replace(b,a,1)
                    reverse=reverse.replace(str(target/'trace.h').encode(),str(original/'trace.h').encode())
                    require(reverse==old,'exact reverse reconstruction failed')
                    if old!=actual:
                        expected_diffs.extend(difflib.unified_diff(old.decode().splitlines(True),actual.decode().splitlines(True),
                                             fromfile=str(original/name),tofile=str(target/name)))
                    if (target/name).suffix=='.cpp':
                        for line,text in enumerate(actual.decode().splitlines(),1):
                            if any(t in text for t in ('HelperStartupTrace::','StandbyTrace::','DeliveryTrace::')):
                                maps.append(dict(file=str(target/name),sha256=digest(target/name),line=line,text=text))
            require((target/'overlay.diff').read_text()==''.join(expected_diffs),'diff mismatch')
            if mode=='instrumented':
                text=(target/'source/holonight-images/src/isolated/runtime.cpp').read_text()
                markers=['helper_resolution.finish();','helper_launchers.finish();','helper_command.finish();',
                         'HelperStartupTrace::measure("process_start"','HelperStartupTrace::measure("wait_for_started"',
                         'helper_discovery.finish();','helper_limits.finish();','process.write("G", 1)',
                         'helper_gate.finish();','HelperStartupTrace::Scope helper_marker',
                         'HelperStartupTrace::Scope helper_final','helper_root.finish();']
                positions=[text.index(m) for m in markers]; require(positions==sorted(positions),'security/lifecycle probe ordering')
                require(('session_readiness_payload_receive' in text)==(variant=='C'),'A/C readiness mismatch')
            trees+=1
    require(maps==read(root/'probe-to-source.json'),'probe citations mismatch')
    schedule=read(root/'protocol.json')['schedule']
    require(len(schedule)==36 and sum(r['observations'] for r in schedule if not r['warmup'])==150 and
            sum(r['warmup'] for r in schedule)==6,'protocol population mismatch')
    return dict(status='passed',preparation_seal=digest(root/'seal.json'),trees=trees,citations=len(maps),
                imports_preparer=False,compiled=False,executed=False,host_revision=True,
                original_preparation_seal=binding['original_seal'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('prepared',type=Path)
    args=parser.parse_args()
    try: print(json.dumps(verify(args.prepared.absolute()),indent=2))
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps(dict(status='blocked',failure=str(error)),indent=2)); raise SystemExit(1)
