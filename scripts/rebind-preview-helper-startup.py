#!/usr/bin/env python3
"""Create a fresh helper preparation with four explicitly revised host bindings."""
import argparse
import difflib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
p=module('host_rebind_preparation','prepare-preview-helper-startup.py')
c=module('host_rebind_checker','verify-preview-helper-startup-host.py')
o,require,read,write=p.o,p.require,p.read,p.write


def rebind(original,output):
    original,output=original.absolute(),output.absolute()
    o.fresh(output,original)
    result=dict(status='blocked',warning='UNCOMPILED, UNEXECUTED',launched_invocations=0)
    before=o.inventory(original); tracked={}
    try:
        c.seal(original)
        require(not (original/'host-rebind.json').exists(),'revision must reference the historical preparation')
        old=read(original/'integrity.json')
        changes={name:dict(old=value,new=o.digest(Path(name))) for name,value in old['consumed'].items()
                 if o.digest(Path(name))!=value}
        require(set(changes)==set(c.HOST_PATHS),'unexpected changed inputs; only four reviewed host paths may change')
        shutil.copytree(original,output,dirs_exist_ok=True)
        # The original seal is not the seal of this revision, even on failure.
        (output/'seal.json').unlink()
        tracked=dict(old['consumed'])
        for name,change in changes.items():tracked[name]=change['new']
        tools={str(path):o.digest(path) for path in (Path(__file__).resolve(),ROOT/'scripts/verify-preview-helper-startup-host.py')}
        tracked.update(tools)
        for name in tools:shutil.copy2(name,output/'tools'/Path(name).name)
        binding=dict(original=str(original),original_seal=o.digest(original/'seal.json'),
            original_verification_sha256=o.digest(original.parent/(original.name+'-independent.json')),changes=changes,tools=tools)
        write(output/'host-rebind.json',binding)
        prepared=Path(read(original/'inputs.json')['prepared'])
        for mode in ('baseline','instrumented'):
            for variant in ('A','C'):
                base=output/mode/variant; parent=prepared/'v4'/variant; differences=[]
                for group in p.GROUPS:
                    for path in sorted((base/group).rglob('*')):
                        if not path.is_file():continue
                        data=path.read_bytes().replace(str(original/mode/variant/'trace.h').encode(),str(base/'trace.h').encode())
                        path.write_bytes(data)
                        relative=path.relative_to(base); previous=(parent/relative).read_bytes()
                        if previous!=data:
                            differences.extend(difflib.unified_diff(previous.decode().splitlines(True),data.decode().splitlines(True),
                                fromfile=str(parent/relative),tofile=str(path)))
                (base/'overlay.diff').write_text(''.join(differences))
                write(base/'source-inventory.json',{group:o.inventory(base/group) for group in p.GROUPS})
        write(output/'probe-to-source.json',p.generated(output,prepared))
        checks={name:o.digest(Path(name))==sha for name,sha in tracked.items()}
        roots=dict(old['before'],**{str(original):before})
        checks.update({name:o.inventory(Path(name))==expected for name,expected in roots.items()})
        require(all(checks.values()),'input drift during host revision')
        write(output/'integrity.json',dict(consumed=tracked,before=roots,checks=checks,passed=True))
        result.update(status='prepared',host_revision=True)
        write(output/'assessment.json',result);o.seal(output)
        c.verify(output)
    except (OSError,ValueError,KeyError,TypeError) as error:
        result.update(status='blocked',failure=str(error))
    finally:
        require(o.inventory(original)==before,'historical package changed')
        write(output/'assessment.json',result)
        (output/'ASSESSMENT.md').write_text('# Explicit helper-startup host revision\n\n'+json.dumps(result,indent=2)+
            '\n\nOnly four host dependency bindings are revised. Historical evidence is unchanged. No optimization selected; qualification remains failed at 78/80 gates.\n')
        o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=rebind(args.original,args.output)
    print(json.dumps(result));sys.exit(result['status']!='prepared')
