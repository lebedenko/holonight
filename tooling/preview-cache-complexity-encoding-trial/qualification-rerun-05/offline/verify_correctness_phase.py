#!/usr/bin/env python3
"""Independent writable-provider correctness schedule. No controllers imported."""
import argparse
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import contract as t
h=t.h
base=t.e.load('directional_correctness_base',t.DIRECTORY/'offline/verify_correctness.py')
original_expected=base.expected_schedule


def expected_schedule(root,built,protocol):
    rows=[]
    for wanted in original_expected(root,built,protocol):
        if wanted['name'].endswith('-ctest'):
            arm=wanted['arm']
            component=wanted['name'][len(arm)+1:-6]
            native=root/arm/'build/providers'/component
            prefix=built/arm/'prefix'
            protected=base.protected_path(root,arm)
            options=['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON','-DHOLONIGHT_THUMBNAILS_TEST_RUNTIME='+str(protected)] if component=='holonight-thumbnails' else [
                '-DHOLONIGHT_FILE_BROWSER_TEST_RUNTIME='+str(built/arm/'runtime'),'-DHOLONIGHT_FILE_BROWSER_TEST_FIXTURES='+str(root/'fixtures'),
                *['-DBUILD_FILE_BROWSER_'+name+'=OFF' for name in ('QUICK','SEARCH','STORAGE','PREVIEW_QUICK','MARKDOWN')]]
            for suffix,argv in [('configure',['cmake','-S',t.PREPARED/arm/'source'/component,'-B',native,'-G','Ninja',
                '-DCMAKE_BUILD_TYPE=Release','-DBUILD_TESTING=ON','-DCMAKE_PREFIX_PATH='+str(prefix),*options]),
                ('compile',['cmake','--build',native,'--parallel','4'])]:
                rows.append(dict(wanted,name=arm+'-'+component+'-'+suffix,argv=list(map(str,argv)),workload=False))
            wanted['argv'][wanted['argv'].index('--test-dir')+1]=str(native)
        rows.append(wanted)
    template=next(row for row in rows if row['name']=='control-store-checks')
    reverse=root/'store-shared/reverse'
    for name,argv,workload in (
        ('cross-directory',['cmake','-E','make_directory',reverse],False),
        ('cross-copy',['cmake','-E','copy',root/'store-shared/candidate-raster.png',reverse/'control-raster.png'],False),
        ('cross-control-read',[root/'control/build/store-checks',reverse,'candidate',root/'control/private/cross-control-read/result.json'],True)):
        rows.append(dict(template,name=name,argv=list(map(str,argv)),workload=workload))
    return rows


base.expected_schedule=expected_schedule


def verify(root):
    result=base.verify(root)
    result['phase_verifier_sha256']=h.digest(Path(__file__))
    if result['outcome']=='qualified':
        h.require(result['completed_commands']==72, 'complete writable provider schedule required')
        h.require(h.read(root/'control/private/cross-control-read/result.json')['cross_arm_readability'], 'reverse installed readability')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    h.require(not args.output.exists() and not args.output.is_relative_to(args.evidence),'proof collision')
    try: result=verify(args.evidence.absolute())
    except (OSError,ValueError,KeyError,TypeError,ET.ParseError) as error:
        result=dict(status='failed',decision='Evidence insufficient',failure=str(error))
    h.write(args.output,result)
    print(h.json.dumps(result,indent=2))
    sys.exit(result['status']!='passed')
