#!/usr/bin/env python3
"""Correctness interface with writable provider test trees, preserving sealed build inputs."""
import argparse
import copy
from pathlib import Path
import sys
import uuid
import qualify as base

c, h = base.c, base.h
original_schedule = base.schedule


def schedule(built, output):
    rows=[]
    for row in original_schedule(built,output):
        if row['name'].endswith('-ctest'):
            arm=row['arm']
            component=row['name'][len(arm)+1:-len('-ctest')]
            source=c.t.PREPARED/arm/'source'/component
            native=output/arm/'build/providers'/component
            protected=base.stage.runtime_path(output,arm)
            prefix=built/arm/'prefix'
            options=['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON','-DHOLONIGHT_THUMBNAILS_TEST_RUNTIME='+str(protected)] if component=='holonight-thumbnails' else [
                '-DHOLONIGHT_FILE_BROWSER_TEST_RUNTIME='+str(built/arm/'runtime'),'-DHOLONIGHT_FILE_BROWSER_TEST_FIXTURES='+str(output/'fixtures'),
                *['-DBUILD_FILE_BROWSER_'+name+'=OFF' for name in ('QUICK','SEARCH','STORAGE','PREVIEW_QUICK','MARKDOWN')]]
            for suffix,argv in (('configure',['cmake','-S',source,'-B',native,'-G','Ninja','-DCMAKE_BUILD_TYPE=Release',
                    '-DBUILD_TESTING=ON','-DCMAKE_PREFIX_PATH='+str(prefix),*options]),
                    ('compile',['cmake','--build',native,'--parallel','4'])):
                extra=copy.deepcopy(row)
                extra.update(name=arm+'-'+component+'-'+suffix,argv=[str(arg) for arg in argv],workload=False)
                env=extra['environment']
                env.update(HOLONIGHT_CACHE_INVOCATION=str(uuid.uuid4()),XDG_CACHE_HOME=str(output/arm/'private'/extra['name']/'cache'),
                    TMPDIR=str(output/arm/'private'/extra['name']/'source'))
                rows.append(extra)
            row['argv'][row['argv'].index('--test-dir')+1]=str(native)
        rows.append(row)
    # Read candidate PNGs with the control-linked installed store consumer as well.
    template=next(row for row in rows if row['name']=='control-store-checks')
    reverse=output/'store-shared/reverse'
    for name,argv,workload in (
        ('cross-directory',['cmake','-E','make_directory',reverse],False),
        ('cross-copy',['cmake','-E','copy',output/'store-shared/candidate-raster.png',reverse/'control-raster.png'],False),
        ('cross-control-read',[output/'control/build/store-checks',reverse,'candidate',output/'control/private/cross-control-read/result.json'],True)):
        row=copy.deepcopy(template)
        row.update(name=name,argv=[str(arg) for arg in argv],workload=workload)
        row['environment'].update(HOLONIGHT_CACHE_INVOCATION=str(uuid.uuid4()),XDG_CACHE_HOME=str(output/'control/private'/name/'cache'),
            TMPDIR=str(output/'control/private'/name/'source'))
        rows.append(row)
    for index,row in enumerate(rows): row['index']=index
    return rows


base.schedule=schedule
qualify=base.qualify

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--built',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    authentication=parser.add_mutually_exclusive_group()
    authentication.add_argument('--authenticate',action='store_true')
    authentication.add_argument('--askpass',action='store_true')
    args=parser.parse_args()
    try:
        if args.askpass:
            c.t.prerequisite()
            c.t.phase_proof(args.built.absolute(),'built')
            base.validate_request(args.built.absolute(),args.output.absolute())
            # Keep authentication and noninteractive sudo commands under the same parent.
            base.subprocess.run(['sudo','-A','-v'],check=True)
        result=qualify(args.built.absolute(),args.output.absolute(),args.authenticate)
    except base.ERRORS as error:
        print('No attempt created: '+str(error),file=sys.stderr)
        sys.exit(1)
    print(h.json.dumps(result,indent=2))
    sys.exit(result['status']!='qualified')
